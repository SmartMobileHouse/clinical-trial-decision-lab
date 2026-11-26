"""Generate the synthetic benchmark splits, deterministically.

    triallab data generate        # rewrites data/synthetic/v1/ from fixed seeds
    triallab data verify          # regenerates in memory and compares with the files

Three splits with separate seeds and separate fictional studies:
- dev          for wording and adapter development; may be inspected freely
- calibration  for fitting decision thresholds; never used for reported scores
- test         frozen; the only split used for reported results

Each split holds 50% routine, 25% issue and 25% ambiguous cases. These shares
are design targets. They say nothing about how often such issues occur in real
trials.
"""

from __future__ import annotations

import hashlib
import json
import random
from dataclasses import dataclass
from pathlib import Path

from triallab.config import DATA
from triallab.core.provenance import file_hash, read_jsonl
from triallab.reference.adjudicate import adjudicate
from triallab.schema import Case, CaseTruth
from triallab.synthetic.library import StudyDesign, build_study
from triallab.synthetic.scenarios import SCENARIOS, Draft, Scenario

GENERATOR_VERSION = "1"
DATASET_NAME = "synthetic-v1"
DATASET_DIR = DATA / "synthetic" / "v1"
SPLITS: dict[str, tuple[int, int]] = {"dev": (1101, 80), "calibration": (2202, 120), "test": (3303, 400)}
CATEGORY_SHARE = {"routine": 0.50, "issue": 0.25, "ambiguous": 0.25}
STUDIES_PER_SPLIT = 8


class GenerationError(RuntimeError):
    """A generated case does not contain exactly the findings its scenario declared."""


@dataclass(frozen=True)
class GeneratedCase:
    case: Case
    truth: CaseTruth


def scenario_counts(size: int) -> dict[str, int]:
    """Cases per scenario for a split of `size`, by largest remainder within each category."""
    counts: dict[str, int] = {}
    for category, share in CATEGORY_SHARE.items():
        target = round(size * share)
        members = [s for s in SCENARIOS if s.category == category]
        total = sum(s.count for s in members)
        exact = {s.name: s.count * target / total for s in members}
        floors = {name: int(value) for name, value in exact.items()}
        left = target - sum(floors.values())
        by_remainder = sorted(members, key=lambda s: (-(exact[s.name] - floors[s.name]), s.name))
        for s in by_remainder[:left]:
            floors[s.name] += 1
        counts.update(floors)
    return counts


def _seed(*parts: object) -> int:
    text = ":".join(str(p) for p in ("triallab", GENERATOR_VERSION, *parts))
    return int.from_bytes(hashlib.sha256(text.encode()).digest()[:8], "big")


def _fits(study: StudyDesign, scenario: Scenario) -> bool:
    have = {
        "amendment": study.amended_parameter is not None,
        "icf2": study.icf2_date is not None,
        "reconsent": study.reconsent_required,
        "overlap": study.has_overlap,
    }
    return all(have[need] for need in scenario.needs)


def generate_split(split: str) -> list[GeneratedCase]:
    seed, size = SPLITS[split]
    studies = [build_study(random.Random(_seed(split, seed, "study", i)), i) for i in range(STUDIES_PER_SPLIT)]
    plan = [s for s in SCENARIOS for _ in range(scenario_counts(size)[s.name])]
    random.Random(_seed(split, seed, "order")).shuffle(plan)
    ids = random.Random(_seed(split, seed, "participants")).sample(range(100_000, 1_000_000), len(plan))
    out = []
    for i, scenario in enumerate(plan, 1):
        case_seed = _seed(split, seed, "case", i)
        rng = random.Random(case_seed)
        study = rng.choice([s for s in studies if _fits(s, scenario)])
        phase = scenario.phase if scenario.phase != "any" else rng.choice(("early", "late"))
        site = {"west": study.sites[0], "east": study.sites[2]}.get(scenario.site)
        draft = Draft.compliant(rng, study, f"P-{ids[i - 1]}", phase, site)
        scenario.build(draft, rng)
        packet, meanings = draft.finish()
        reference = adjudicate(packet, meanings)
        declared = sorted({f.key() for f in draft.declared})
        derived = sorted({f.key() for f in reference.findings})
        case_id = f"SYN-{split[0].upper()}-{i:04d}"
        if declared != derived:
            raise GenerationError(f"{case_id} ({scenario.name}): declared {declared}, adjudicated {derived}")
        truth = CaseTruth(
            case_id=case_id, split=split, seed=case_seed, generator_version=GENERATOR_VERSION,
            scenario=scenario.name, category=scenario.category, tags=draft.tags,
            declared_findings=draft.declared, note_meanings=meanings, reference=reference,
        )  # fmt: skip
        out.append(GeneratedCase(Case(case_id=case_id, packet=packet), truth))
    return out


def _lines(rows: list[dict]) -> str:
    return "".join(json.dumps(r, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n" for r in rows)


def render_split(split: str) -> dict[str, str]:
    """File name -> exact file contents for one split."""
    generated = generate_split(split)
    return {
        f"{split}.cases.jsonl": _lines([g.case.model_dump(mode="json") for g in generated]),
        f"{split}.reference.jsonl": _lines([g.truth.model_dump(mode="json") for g in generated]),
    }


def write_dataset(directory: Path = DATASET_DIR) -> dict:
    directory.mkdir(parents=True, exist_ok=True)
    files: dict[str, str] = {}
    for split in SPLITS:
        for name, text in render_split(split).items():
            (directory / name).write_text(text)
            files[name] = hashlib.sha256(text.encode()).hexdigest()
    manifest = {
        "dataset": DATASET_NAME,
        "generator_version": GENERATOR_VERSION,
        "origin": "Generated by this project from fixed seeds. Fictional; no real participant, site, sponsor or study.",
        "license": "MIT",
        "splits": {
            split: {"seed": seed, "cases": size, "scenario_counts": scenario_counts(size)}
            for split, (seed, size) in SPLITS.items()
        },
        "files_sha256": files,
    }
    (directory / "MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def verify_dataset(directory: Path = DATASET_DIR) -> list[str]:
    """Regenerate every split and report files that differ from what is on disk."""
    problems = []
    manifest_path = directory / "MANIFEST.json"
    recorded = json.loads(manifest_path.read_text())["files_sha256"] if manifest_path.is_file() else {}
    for split in SPLITS:
        for name, text in render_split(split).items():
            path = directory / name
            expected = hashlib.sha256(text.encode()).hexdigest()
            if not path.is_file():
                problems.append(f"{name}: missing")
            elif file_hash(path) != expected:
                problems.append(f"{name}: differs from a fresh generation")
            elif recorded.get(name) != expected:
                problems.append(f"{name}: MANIFEST.json fingerprint is out of date")
    return problems


def load_cases(split: str, directory: Path = DATASET_DIR) -> list[Case]:
    return [Case.model_validate(row) for row in read_jsonl(directory / f"{split}.cases.jsonl")]


def load_truth(split: str, directory: Path = DATASET_DIR) -> dict[str, CaseTruth]:
    rows = [CaseTruth.model_validate(row) for row in read_jsonl(directory / f"{split}.reference.jsonl")]
    return {row.case_id: row for row in rows}
