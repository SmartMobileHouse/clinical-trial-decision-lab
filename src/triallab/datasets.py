"""Load a benchmark dataset: tasks for the systems, reference rows for scoring, and its rights.

Two tracks, never mixed:
- `synthetic`   the bundled fictional operational cases (question set `triage`)
- `regulatory`  descriptions of publicly documented regulatory findings (question set `finding`).
                These files are NOT part of this repository; they are read from the folder
                named by TRIALLAB_RESTRICTED_DATA.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, ValidationError, model_validator

from triallab.config import CONFIGS, REPO_ROOT
from triallab.core.provenance import file_hash, read_jsonl
from triallab.evaluate.decision import ReferenceCase
from triallab.providers.base import Task
from triallab.questions import QuestionSet, load_question_set
from triallab.schema import Case, CaseTruth

RESTRICTED_ENV = "TRIALLAB_RESTRICTED_DATA"
RENDER_VERSION = "1"  # bump if what is sent for a case changes


class DatasetError(ValueError):
    """A dataset config or file is missing or invalid. The message says how to fix it."""


class DatasetSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    track: Literal["synthetic", "regulatory"]
    question_set: str
    source_id: str  # entry in data/source-manifest.json
    location: Literal["repository", "restricted"]
    path: str  # folder, relative to the repository or to the restricted data folder
    splits: list[str]
    reported_split: str
    external_processing_allowed: bool = False  # safe default: local only
    publication_allowed: bool = False  # processing permission never grants publication rights
    publication_note: str = ""
    license_note: str = ""

    @model_validator(mode="after")
    def _note(self) -> DatasetSpec:
        if self.publication_allowed and not self.publication_note.strip():
            raise ValueError("publication_allowed requires a publication_note recording the rights basis")
        if self.reported_split not in self.splits:
            raise ValueError("reported_split must be one of splits")
        return self


@dataclass(frozen=True)
class Dataset:
    spec: DatasetSpec
    split: str
    questions: QuestionSet
    tasks: list[Task]
    reference: list[ReferenceCase]
    files_sha256: dict[str, str]


def payload_hash(state: dict[str, Any]) -> str:
    text = json.dumps(state, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def load_spec(name_or_path: str) -> DatasetSpec:
    path = Path(name_or_path)
    if not path.is_file():
        path = CONFIGS / "datasets" / f"{name_or_path}.yaml"
    if not path.is_file():
        raise DatasetError(f"dataset config not found: {name_or_path} (looked in configs/datasets/)")
    try:
        return DatasetSpec.model_validate(yaml.safe_load(path.read_text()))
    except (yaml.YAMLError, ValidationError) as exc:
        raise DatasetError(f"{path} is invalid: {exc}") from exc


def dataset_dir(spec: DatasetSpec) -> Path:
    if spec.location == "repository":
        return REPO_ROOT / spec.path
    root = os.environ.get(RESTRICTED_ENV, "").strip()
    if not root:
        raise DatasetError(
            f"{spec.name} is not distributed with this repository. Set {RESTRICTED_ENV} to the folder that holds it."
        )
    return Path(root).expanduser() / spec.path


def _packet_refs(packet: dict[str, Any]) -> frozenset[str]:
    refs = {c["ref"] for c in packet["protocol"]["criteria"]} | {
        c["ref"] for c in packet["protocol"]["consent_versions"]
    }
    for key in ("assessments", "consents", "events", "notes"):
        refs |= {item["ref"] for item in packet["record"][key]}
    return frozenset(refs)


def load_dataset(name_or_path: str, split: str | None = None) -> Dataset:
    spec = load_spec(name_or_path)
    split = split or spec.reported_split
    if split not in spec.splits:
        raise DatasetError(f"{spec.name} has no split {split!r}; choose from {', '.join(spec.splits)}")
    folder = dataset_dir(spec)
    questions = load_question_set(spec.question_set)
    cases_path, reference_path = folder / f"{split}.cases.jsonl", folder / f"{split}.reference.jsonl"
    for path in (cases_path, reference_path):
        if not path.is_file():
            raise DatasetError(f"{spec.name}: missing file {path.name} in the dataset folder")
    files = {cases_path.name: file_hash(cases_path), reference_path.name: file_hash(reference_path)}
    tasks: list[Task] = []
    reference: list[ReferenceCase] = []
    if spec.track == "synthetic":
        cases = [Case.model_validate(row) for row in read_jsonl(cases_path)]
        truth = {t.case_id: t for t in (CaseTruth.model_validate(row) for row in read_jsonl(reference_path))}
        for case in cases:
            state = case.packet.model_dump(mode="json")
            tasks.append(Task(case.case_id, state, payload_hash(state), questions))
            t = truth[case.case_id]
            reference.append(
                ReferenceCase(
                    case_id=case.case_id,
                    answers=t.reference.answers,
                    category=t.category,
                    scenario=t.scenario,
                    tags=tuple(t.tags),
                    evidence_refs=frozenset(r for f in t.reference.findings for r in f.evidence_refs),
                    valid_refs=_packet_refs(state),
                )  # fmt: skip
            )
    else:
        rows = {row["case_id"]: row for row in read_jsonl(reference_path)}
        for row in read_jsonl(cases_path):
            state = {"document_type": "description of an inspection observation", "finding_text": row["finding_text"]}
            tasks.append(Task(row["case_id"], state, payload_hash(state), questions))
            ref = rows[row["case_id"]]
            reference.append(
                ReferenceCase(
                    case_id=row["case_id"],
                    answers={q: bool(ref["answers"][q]) for q in questions.ids},
                    category=ref.get("category", ""),
                    scenario=ref.get("issue_category", ""),
                )  # fmt: skip
            )
    if [t.case_id for t in tasks] != [r.case_id for r in reference]:
        raise DatasetError(f"{spec.name}: cases and reference rows are not aligned")
    return Dataset(spec, split, questions, tasks, reference, files)
