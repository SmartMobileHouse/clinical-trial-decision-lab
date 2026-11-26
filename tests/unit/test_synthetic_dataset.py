"""Dataset reproducibility and ground-truth integrity."""

from __future__ import annotations

import asyncio
import json
from collections import Counter

import pytest

from triallab.baselines.systems import RulesProvider
from triallab.datasets import load_dataset
from triallab.reference.adjudicate import adjudicate
from triallab.reference.derive import EXPEDITED_CODES, answers_from_findings, decision_from_answers
from triallab.synthetic.generate import (
    DATASET_DIR,
    SPLITS,
    generate_split,
    load_cases,
    load_truth,
    scenario_counts,
    verify_dataset,
)
from triallab.synthetic.scenarios import SCENARIOS


def test_committed_files_match_a_fresh_generation() -> None:
    assert verify_dataset() == []


def test_test_split_has_the_designed_composition() -> None:
    truth = load_truth("test")
    assert Counter(t.category for t in truth.values()) == {"routine": 200, "issue": 100, "ambiguous": 100}
    assert Counter(t.scenario for t in truth.values()) == {s.name: s.count for s in SCENARIOS}
    assert sum(s.count for s in SCENARIOS) == 400


@pytest.mark.parametrize("split", list(SPLITS))
def test_split_sizes_and_shares(split: str) -> None:
    size = SPLITS[split][1]
    counts = scenario_counts(size)
    by_category = Counter()
    for scenario in SCENARIOS:
        by_category[scenario.category] += counts[scenario.name]
    assert by_category == {"routine": size // 2, "issue": size // 4, "ambiguous": size // 4}


@pytest.mark.parametrize("split", list(SPLITS))
def test_every_label_has_two_derivations_that_agree(split: str) -> None:
    """Scenario declaration (by construction) == adjudicator (by derivation), re-checked on the saved files."""
    truth = load_truth(split)
    for case in load_cases(split):
        t = truth[case.case_id]
        again = adjudicate(case.packet, t.note_meanings)
        assert {f.key() for f in again.findings} == {f.key() for f in t.declared_findings}, case.case_id
        assert again.answers == t.reference.answers == answers_from_findings(again.findings)
        decision = decision_from_answers(again.answers)
        assert decision.review_priority == t.reference.review_priority
        expedited = any(f.code in EXPEDITED_CODES for f in again.findings)
        assert (decision.review_priority == "expedited") == expedited


def test_routine_cases_have_no_findings_and_others_have_some() -> None:
    for t in load_truth("test").values():
        assert (t.category == "routine") == (not t.reference.findings), t.case_id


def test_packets_never_contain_the_answer() -> None:
    forbidden = {s.name for s in SCENARIOS} | {"scenario", "category", "tags", "declared_findings", "note_meanings",
                                              "reference", "review_priority", "text_dependent", "suspicious_but_correct"}  # fmt: skip
    text = (DATASET_DIR / "test.cases.jsonl").read_text()
    for word in forbidden:
        assert f'"{word}"' not in text, word
    ds = load_dataset("synthetic-v1")
    assert all(set(task.state) == {"packet_version", "protocol", "record"} for task in ds.tasks)


def test_splits_share_no_study_participant_or_case() -> None:
    studies, participants, ids = [], [], []
    for split in SPLITS:
        cases = load_cases(split)
        studies.append({c.packet.protocol.study_id for c in cases})
        participants.append({c.packet.record.participant_id for c in cases})
        ids.append({c.case_id for c in cases})
    for group in (studies, participants, ids):
        assert not (group[0] & group[1]) and not (group[0] & group[2]) and not (group[1] & group[2])


def test_generation_is_deterministic() -> None:
    first = [g.case.model_dump() for g in generate_split("dev")]
    second = [g.case.model_dump() for g in generate_split("dev")]
    assert first == second


def test_rules_baseline_differs_from_reference_only_on_text_dependent_cases() -> None:
    """The rules read structured fields only, so they can be wrong only where a note decides the case."""
    ds = load_dataset("synthetic-v1")
    rules = RulesProvider()
    wrong_structured, wrong_text, text_cases = 0, 0, 0
    for task, ref in zip(ds.tasks, ds.reference, strict=True):
        answers = asyncio.run(rules.evaluate(task)).answers
        text = "text_dependent" in ref.tags
        text_cases += text
        if answers != ref.answers:
            wrong_text += text
            wrong_structured += not text
    assert wrong_structured == 0
    assert wrong_text == text_cases == 42  # every text-dependent case defeats structured-only rules, by design


def test_no_personal_identifiers_in_the_dataset() -> None:
    for line in (DATASET_DIR / "test.cases.jsonl").read_text().splitlines():
        record = json.loads(line)["packet"]["record"]
        assert record["participant_id"].startswith("P-") and record["site_id"].startswith("SITE-")
        assert set(record) == {"participant_id", "site_id", "assessments", "consents", "events", "notes"}
