"""Metric correctness on small hand-computed examples."""

from __future__ import annotations

import numpy as np
import pytest

from triallab.evaluate.decision import (
    ReferenceCase,
    SystemAnswer,
    build_table,
    finding_metrics,
    headline,
    triage_metrics,
)
from triallab.evaluate.probability import brier, expected_calibration_error, probability_metrics
from triallab.evaluate.statistics import answer_stability, mcnemar_exact, paired_bootstrap
from triallab.reference.derive import TRIAGE_QUESTIONS, consistent, decision_from_answers

NO = dict.fromkeys(TRIAGE_QUESTIONS, False)


def ans(**yes: bool) -> dict[str, bool]:
    return {**NO, **yes}


ELIG_ISSUE = ans(eligibility_issue=True, review_needed=True, review_expedited=True)
CONSENT_MISSING = ans(consent_insufficient=True, review_needed=True)
CONSENT_CONFLICT = ans(consent_conflicting=True, review_needed=True)

REFERENCE = [
    ReferenceCase("c1", NO, "routine"),
    ReferenceCase("c2", NO, "routine"),
    ReferenceCase(
        "c3", ELIG_ISSUE, "issue", evidence_refs=frozenset({"ASM-1"}), valid_refs=frozenset({"ASM-1", "ASM-2"})
    ),
    ReferenceCase("c4", CONSENT_MISSING, "ambiguous"),
    ReferenceCase("c5", CONSENT_CONFLICT, "ambiguous", tags=("text_dependent",)),
]


def system(answers: list[dict[str, bool] | None]) -> dict[str, SystemAnswer]:
    return {r.case_id: SystemAnswer(a) for r, a in zip(REFERENCE, answers, strict=True)}


def test_derivation_precedence_issue_over_conflict_over_missing() -> None:
    both = ans(eligibility_issue=True, eligibility_conflicting=True, eligibility_insufficient=True)
    assert decision_from_answers(both).eligibility_outcome == "potential_issue"
    assert (
        decision_from_answers(ans(consent_conflicting=True, consent_insufficient=True)).consent_outcome
        == "conflicting_evidence"
    )
    assert decision_from_answers(NO).review_priority == "routine"
    assert decision_from_answers(CONSENT_MISSING).missing_evidence is True


def test_consistency_rules() -> None:
    assert consistent(NO) and consistent(ELIG_ISSUE)
    assert not consistent(ans(review_expedited=True))  # expedited without review needed
    assert not consistent(ans(eligibility_issue=True))  # a reason without review needed
    assert not consistent(ans(review_needed=True))  # review needed without a reason


def test_perfect_answers_score_perfectly() -> None:
    m = triage_metrics(REFERENCE, system([r.answers for r in REFERENCE]))
    assert m["case_accuracy"] == 1.0 and m["eligibility_macro_f1"] == 1.0 and m["consent_macro_f1"] == 1.0
    assert m["critical_recall"] == 1.0 and m["missed_issues"] == 0 and m["false_positives_per_100"] == 0.0
    assert m["priority"]["exact_agreement"] == 1.0 and m["priority"]["weighted_kappa"] == pytest.approx(1.0)
    assert m["abstention"]["precision"] == 1.0 and m["abstention"]["recall"] == 1.0
    assert m["unsupported_finding_rate"] == 0.0 and m["consistency_rate"] == 1.0


def test_hand_computed_errors() -> None:
    answers = [
        ELIG_ISSUE,  # c1 routine -> a false alarm and an unsupported finding
        NO,  # c2 right
        NO,  # c3 missed critical issue
        CONSENT_MISSING,  # c4 right
        None,  # c5 no response
    ]
    m = triage_metrics(REFERENCE, system(answers))
    assert m["coverage"] == 0.8
    assert m["case_accuracy"] == pytest.approx(2 / 5)
    assert m["issue_detection"] == {
        "tp": 0,
        "fp": 1,
        "fn": 1,
        "precision": 0.0,
        "recall": 0.0,
        "f1": 0.0,
        "issue_cases": 1,
    }
    assert m["missed_issues"] == 1 and m["critical"]["missed"] == 1 and m["critical_recall"] == 0.0
    assert m["review"]["unnecessary_reviews"] == 1 and m["false_positives_per_100"] == pytest.approx(20.0)
    assert m["unsupported_findings"] == 1 and m["unsupported_finding_rate"] == 1.0
    assert m["abstention"]["tp"] == 1 and m["abstention"]["fn"] == 1  # c5's conflict was not answered
    assert m["domains"]["consent"]["per_class"]["conflicting_evidence"]["recall"] == 0.0
    assert m["strata"]["evidence:text_dependent"] == {"cases": 1, "case_accuracy": 0.0, "flagged_rate": 0.0}
    assert m["case_correct"] == [False, True, False, True, False]


def test_review_budget_ranks_by_probability_then_by_fixed_tie_break() -> None:
    answers = {
        r.case_id: SystemAnswer(r.answers, {"review_needed": p, "review_expedited": p})
        for r, p in zip(REFERENCE, (0.1, 0.2, 0.9, 0.6, 0.5), strict=True)
    }
    budget = triage_metrics(REFERENCE, answers)["review_budget"]
    assert budget["10pct"]["reviewed_cases"] == 1 and budget["10pct"]["critical_recall"] == 1.0
    assert budget["25pct"]["reviewed_cases"] == 2 and budget["25pct"]["review_needed_precision"] == 1.0
    again = triage_metrics(REFERENCE, answers)["review_budget"]
    assert again == budget


def test_evidence_citations_are_checked_against_the_packet() -> None:
    answers = system([r.answers for r in REFERENCE])
    answers["c3"] = SystemAnswer(ELIG_ISSUE, None, ("ASM-1", "ASM-99"))
    evidence = triage_metrics(REFERENCE, answers)["evidence"]
    assert evidence["cites_evidence"] and evidence["citation_validity"] == 0.5 and evidence["evidence_overlap"] == 1.0


def test_headline_on_resample_matches_direct_computation() -> None:
    table = build_table(REFERENCE, system([r.answers for r in REFERENCE]))
    assert headline(table, np.array([0, 0, 2, 2, 3]))["case_accuracy"] == 1.0


def test_bootstrap_is_deterministic_and_paired() -> None:
    perfect = build_table(REFERENCE, system([r.answers for r in REFERENCE]))
    silent = build_table(REFERENCE, system([NO] * 5))
    strata = [r.category for r in REFERENCE]
    first = paired_bootstrap({"a": perfect, "b": silent}, strata, reference="a", resamples=50, seed=3)
    second = paired_bootstrap({"a": perfect, "b": silent}, strata, reference="a", resamples=50, seed=3)
    assert first == second
    intervals, differences = first
    assert intervals["a"]["case_accuracy"].low == intervals["a"]["case_accuracy"].high == 1.0
    assert differences["b"]["case_accuracy"].high < 0  # stratified: every redraw keeps the three non-routine cases


def test_mcnemar_exact() -> None:
    assert mcnemar_exact([True, True, False], [True, True, False])["p_value"] == 1.0
    result = mcnemar_exact([True] * 8 + [False] * 2, [False] * 8 + [False] * 2)
    assert result["only_first_correct"] == 8 and result["only_second_correct"] == 0
    assert result["p_value"] == pytest.approx(2 * 0.5**8)


def test_probability_metrics_only_when_probabilities_exist() -> None:
    assert probability_metrics(REFERENCE, system([r.answers for r in REFERENCE])) is None
    p = np.array([0.9, 0.1, 0.8, 0.2])
    y = np.array([1.0, 0.0, 1.0, 0.0])
    assert brier(p, y) == pytest.approx((0.01 + 0.01 + 0.04 + 0.04) / 4)
    assert expected_calibration_error(p, y) == pytest.approx(0.15)
    perfect = {r.case_id: SystemAnswer(r.answers, {q: float(v) for q, v in r.answers.items()}) for r in REFERENCE}
    result = probability_metrics(REFERENCE, perfect)
    assert result is not None and result["pooled"]["brier"] == 0.0 and result["pooled"]["n"] == 40


def test_answer_stability() -> None:
    assert answer_stability([{"c1": NO}]) is None
    result = answer_stability([{"c1": NO, "c2": NO}, {"c1": NO, "c2": ELIG_ISSUE}])
    assert result == {"repeats": 2, "compared_cases": 2, "cases_with_changed_answers": 1, "changed_rate": 0.5}


def test_finding_track_metrics() -> None:
    reference = [
        ReferenceCase("r1", {"eligibility_issue": True, "consent_issue": False}),
        ReferenceCase("r2", {"eligibility_issue": False, "consent_issue": True}),
        ReferenceCase("r3", {"eligibility_issue": False, "consent_issue": False}),
    ]
    answers = {
        "r1": SystemAnswer({"eligibility_issue": True, "consent_issue": False}),
        "r2": SystemAnswer({"eligibility_issue": True, "consent_issue": True}),
    }
    m = finding_metrics(reference, answers)
    assert m["coverage"] == pytest.approx(2 / 3)
    assert m["questions"]["eligibility_issue"]["precision"] == 0.5 and m["questions"]["consent_issue"]["f1"] == 1.0
    assert m["case_correct"] == [True, False, False]
