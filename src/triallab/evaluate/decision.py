"""Decision-quality metrics (EVAL_VERSION 1).

Conventions, fixed so every system is scored the same way:
- A system answers each frozen yes/no question. The four decision outputs are
  derived from those answers by `triallab.reference.derive`, exactly as for the
  reference.
- A case with no usable answer (failed call, timeout, refusal, invalid output)
  counts against the system: its outcome is `no_response`, which matches no
  class, and the case is treated as not flagged for review. Coverage reports
  how many cases were answered.
- "Critical" cases are those whose reference priority is `expedited`.
- "Flagged" means the system asked for any review beyond routine monitoring.
- Review-budget ranking uses p(review_needed) + p(review_expedited) when the
  system reports probabilities, otherwise its priority level (0, 1 or 2). Ties
  are broken by a fixed hash of (seed, case_id), never by row order.
"""

from __future__ import annotations

import hashlib
import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from triallab.reference.derive import consistent, decision_from_answers
from triallab.schema import OUTCOMES, PRIORITIES

EVAL_VERSION = "1"
NO_RESPONSE = "no_response"
REVIEW_BUDGETS = (0.10, 0.25)
DOMAINS = ("eligibility", "consent")
HEADLINE = (
    "case_accuracy",
    "eligibility_macro_f1",
    "consent_macro_f1",
    "critical_recall",
    "issue_recall",
    "issue_precision",
    "false_positives_per_100",
)


@dataclass(frozen=True)
class ReferenceCase:
    case_id: str
    answers: dict[str, bool]
    category: str = ""
    scenario: str = ""
    tags: tuple[str, ...] = ()
    evidence_refs: frozenset[str] = frozenset()
    valid_refs: frozenset[str] = frozenset()


@dataclass(frozen=True)
class SystemAnswer:
    """What one system said about one case; `answers` is None when it gave no usable answer."""

    answers: dict[str, bool] | None
    probabilities: dict[str, float] | None = None
    evidence_refs: tuple[str, ...] | None = None


@dataclass
class CaseTable:
    """Per-case arrays for one system, aligned with the reference order."""

    ids: list[str]
    ref_outcome: dict[str, np.ndarray] = field(default_factory=dict)  # domain -> class index
    pred_outcome: dict[str, np.ndarray] = field(default_factory=dict)  # domain -> class index, -1 = no response
    ref_priority: np.ndarray = field(default_factory=lambda: np.zeros(0, dtype=int))
    pred_priority: np.ndarray = field(default_factory=lambda: np.zeros(0, dtype=int))  # -1 = no response
    answered: np.ndarray = field(default_factory=lambda: np.zeros(0, dtype=bool))
    score: np.ndarray = field(default_factory=lambda: np.zeros(0))


def tie_break_keys(case_ids: Sequence[str], seed: int) -> np.ndarray:
    """A fixed pseudo-random number per case, used only to order equal scores."""
    return np.array(
        [int.from_bytes(hashlib.sha256(f"{seed}:{c}".encode()).digest()[:8], "big") for c in case_ids],
        dtype=np.uint64,
    )


def build_table(reference: Sequence[ReferenceCase], answers: Mapping[str, SystemAnswer]) -> CaseTable:
    n = len(reference)
    table = CaseTable(ids=[r.case_id for r in reference])
    table.ref_outcome = {d: np.zeros(n, dtype=int) for d in DOMAINS}
    table.pred_outcome = {d: np.full(n, -1, dtype=int) for d in DOMAINS}
    table.ref_priority = np.zeros(n, dtype=int)
    table.pred_priority = np.full(n, -1, dtype=int)
    table.answered = np.zeros(n, dtype=bool)
    table.score = np.full(n, -1.0)
    for i, ref in enumerate(reference):
        truth = decision_from_answers(ref.answers)
        table.ref_outcome["eligibility"][i] = OUTCOMES.index(truth.eligibility_outcome)
        table.ref_outcome["consent"][i] = OUTCOMES.index(truth.consent_outcome)
        table.ref_priority[i] = PRIORITIES.index(truth.review_priority)
        given = answers.get(ref.case_id)
        if given is None or given.answers is None:
            continue
        said = decision_from_answers(given.answers)
        table.answered[i] = True
        table.pred_outcome["eligibility"][i] = OUTCOMES.index(said.eligibility_outcome)
        table.pred_outcome["consent"][i] = OUTCOMES.index(said.consent_outcome)
        table.pred_priority[i] = PRIORITIES.index(said.review_priority)
        p = given.probabilities
        if p is not None and "review_needed" in p and "review_expedited" in p:
            table.score[i] = p["review_needed"] + p["review_expedited"]
        else:
            table.score[i] = float(table.pred_priority[i])
    return table


def _ratio(numerator: Any, denominator: Any) -> float | None:
    return float(numerator / denominator) if denominator else None


def _f1(precision: float | None, recall: float | None) -> float | None:
    if precision is None or recall is None:
        return None
    return 0.0 if precision + recall == 0 else 2 * precision * recall / (precision + recall)


def binary(ref: np.ndarray, pred: np.ndarray) -> dict[str, Any]:
    tp, fp, fn = int((ref & pred).sum()), int((~ref & pred).sum()), int((ref & ~pred).sum())
    precision, recall = _ratio(tp, tp + fp), _ratio(tp, tp + fn)
    return {"tp": tp, "fp": fp, "fn": fn, "precision": precision, "recall": recall, "f1": _f1(precision, recall)}


def macro_f1(ref: np.ndarray, pred: np.ndarray, classes: int) -> float:
    """Mean F1 over the classes that occur in the reference. A class never predicted scores 0."""
    scores = []
    for c in range(classes):
        if not (ref == c).any():
            continue
        scores.append(binary(ref == c, pred == c)["f1"] or 0.0)
    return float(np.mean(scores)) if scores else 0.0


def weighted_kappa(ref: np.ndarray, pred: np.ndarray, levels: int) -> float | None:
    """Linear-weighted Cohen's kappa on answered cases; None when it is undefined."""
    mask = pred >= 0
    if mask.sum() == 0:
        return None
    r, p = ref[mask], pred[mask]
    observed = np.zeros((levels, levels))
    for a, b in zip(r, p, strict=True):
        observed[a, b] += 1
    observed /= observed.sum()
    expected = np.outer(observed.sum(axis=1), observed.sum(axis=0))
    weights = np.abs(np.subtract.outer(np.arange(levels), np.arange(levels))) / (levels - 1)
    denominator = (weights * expected).sum()
    return None if denominator == 0 else float(1 - (weights * observed).sum() / denominator)


def headline(table: CaseTable, idx: np.ndarray | None = None) -> dict[str, float]:
    """The pre-specified headline metrics, optionally on a resample. Undefined ratios are reported as NaN."""
    take = (lambda a: a) if idx is None else (lambda a: a[idx])
    re, pe = take(table.ref_outcome["eligibility"]), take(table.pred_outcome["eligibility"])
    rc, pc = take(table.ref_outcome["consent"]), take(table.pred_outcome["consent"])
    rp, pp = take(table.ref_priority), take(table.pred_priority)
    issue = OUTCOMES.index("potential_issue")
    ref_issue, pred_issue = (re == issue) | (rc == issue), (pe == issue) | (pc == issue)
    flagged = pp >= 1
    critical = rp == 2
    stats = binary(ref_issue, pred_issue)

    def value(x: float | None) -> float:
        return float("nan") if x is None else x

    return {
        "case_accuracy": float(((re == pe) & (rc == pc)).mean()),
        "eligibility_macro_f1": macro_f1(re, pe, len(OUTCOMES)),
        "consent_macro_f1": macro_f1(rc, pc, len(OUTCOMES)),
        "critical_recall": value(_ratio((critical & flagged).sum(), critical.sum())),
        "issue_recall": value(stats["recall"]),
        "issue_precision": value(stats["precision"]),
        "false_positives_per_100": float(100 * ((rp == 0) & flagged).sum() / len(rp)),
    }


def review_budget(table: CaseTable, seed: int) -> dict[str, dict[str, Any]]:
    """Precision and recall for critical cases when only the top share of the ranking is reviewed."""
    n = len(table.ids)
    order = np.lexsort((tie_break_keys(table.ids, seed), -table.score))
    critical, needed = table.ref_priority == 2, table.ref_priority >= 1
    out = {}
    for budget in REVIEW_BUDGETS:
        k = math.ceil(budget * n)
        top = order[:k]
        out[f"{round(budget * 100)}pct"] = {
            "reviewed_cases": k,
            "critical_precision": _ratio(critical[top].sum(), k),
            "critical_recall": _ratio(critical[top].sum(), critical.sum()),
            "review_needed_precision": _ratio(needed[top].sum(), k),
            "review_needed_recall": _ratio(needed[top].sum(), needed.sum()),
        }
    return out


def triage_metrics(
    reference: Sequence[ReferenceCase], answers: Mapping[str, SystemAnswer], seed: int = 42
) -> dict[str, Any]:
    table = build_table(reference, answers)
    n = len(reference)
    issue, none = OUTCOMES.index("potential_issue"), OUTCOMES.index("no_issue")
    insufficient, conflicting = OUTCOMES.index("insufficient_evidence"), OUTCOMES.index("conflicting_evidence")
    out: dict[str, Any] = {"n": n, "coverage": float(table.answered.mean()), **headline(table)}
    out = {k: (None if isinstance(v, float) and math.isnan(v) else v) for k, v in out.items()}

    domains = {}
    for d in DOMAINS:
        ref, pred = table.ref_outcome[d], table.pred_outcome[d]
        domains[d] = {
            "accuracy": float((ref == pred).mean()),
            "macro_f1": macro_f1(ref, pred, len(OUTCOMES)),
            "per_class": {
                name: {**binary(ref == c, pred == c), "support": int((ref == c).sum())}
                for c, name in enumerate(OUTCOMES)
            },
        }
    out["domains"] = domains

    ref_any_issue = (table.ref_outcome["eligibility"] == issue) | (table.ref_outcome["consent"] == issue)
    pred_any_issue = (table.pred_outcome["eligibility"] == issue) | (table.pred_outcome["consent"] == issue)
    flagged = table.pred_priority >= 1
    needs_review = table.ref_priority >= 1
    critical = table.ref_priority == 2
    out["issue_detection"] = {**binary(ref_any_issue, pred_any_issue), "issue_cases": int(ref_any_issue.sum())}
    out["missed_issues"] = int((ref_any_issue & ~flagged).sum())  # documented issues never queued for review
    out["critical"] = {
        "cases": int(critical.sum()),
        "flagged_recall": _ratio((critical & flagged).sum(), critical.sum()),
        "expedited_recall": _ratio((critical & (table.pred_priority == 2)).sum(), critical.sum()),
        "missed": int((critical & ~flagged).sum()),
    }
    out["review"] = {
        **binary(needs_review, flagged),
        "flagged_cases": int(flagged.sum()),
        "unnecessary_reviews": int((~needs_review & flagged).sum()),
        "false_positives_per_100": float(100 * (~needs_review & flagged).sum() / n),
    }
    out["priority"] = {
        "exact_agreement": float((table.ref_priority == table.pred_priority).mean()),
        "weighted_kappa": weighted_kappa(table.ref_priority, table.pred_priority, len(PRIORITIES)),
    }
    out["review_budget"] = review_budget(table, seed)

    # Abstention and unsupported findings are counted per (case, domain) instance.
    ref_all = np.concatenate([table.ref_outcome[d] for d in DOMAINS])
    pred_all = np.concatenate([table.pred_outcome[d] for d in DOMAINS])
    ref_open = (ref_all == insufficient) | (ref_all == conflicting)
    pred_open = (pred_all == insufficient) | (pred_all == conflicting)
    abstention = binary(ref_open, pred_open)
    determinate = ~ref_open
    abstention["over_abstention_rate"] = _ratio((determinate & pred_open).sum(), determinate.sum())
    out["abstention"] = abstention
    said_issue = pred_all == issue
    unsupported = said_issue & ((ref_all == none) | (ref_all == insufficient))
    out["unsupported_finding_rate"] = _ratio(unsupported.sum(), said_issue.sum())
    out["unsupported_findings"] = int(unsupported.sum())

    flags = {}
    for name, suffix in (("missing_evidence", "insufficient"), ("conflicting_evidence", "conflicting")):
        ref_flag = np.array([any(r.answers.get(f"{d}_{suffix}") for d in DOMAINS) for r in reference])
        pred_flag = np.array(
            [
                bool(a and a.answers and any(a.answers.get(f"{d}_{suffix}") for d in DOMAINS))
                for a in (answers.get(r.case_id) for r in reference)
            ]
        )
        flags[name] = binary(ref_flag, pred_flag)
    out["evidence_flags"] = flags

    given = [(r, answers.get(r.case_id)) for r in reference]
    answered = [(r, a) for r, a in given if a is not None and a.answers is not None]
    out["consistency_rate"] = _ratio(sum(consistent(a.answers or {}) for _, a in answered), len(answered))
    cited = [(r, a) for r, a in answered if a.evidence_refs is not None]
    if cited:
        all_refs = [ref for _, a in cited for ref in (a.evidence_refs or ())]
        valid = sum(ref in r.valid_refs for r, a in cited for ref in (a.evidence_refs or ()))
        with_finding = [(r, a) for r, a in cited if r.evidence_refs and any((a.answers or {}).values())]
        overlap = sum(bool(set(a.evidence_refs or ()) & r.evidence_refs) for r, a in with_finding)
        out["evidence"] = {
            "cites_evidence": True,
            "cited_refs": len(all_refs),
            "citation_validity": _ratio(valid, len(all_refs)),
            "evidence_overlap": _ratio(overlap, len(with_finding)),
        }
    else:
        out["evidence"] = {"cites_evidence": False}

    case_correct = (table.ref_outcome["eligibility"] == table.pred_outcome["eligibility"]) & (
        table.ref_outcome["consent"] == table.pred_outcome["consent"]
    )
    strata: dict[str, dict[str, Any]] = {}
    groups = {
        "category:routine": [r.category == "routine" for r in reference],
        "category:issue": [r.category == "issue" for r in reference],
        "category:ambiguous": [r.category == "ambiguous" for r in reference],
        "evidence:structured": ["text_dependent" not in r.tags for r in reference],
        "evidence:text_dependent": ["text_dependent" in r.tags for r in reference],
    }
    for name, members in groups.items():
        mask = np.array(members, dtype=bool)
        if mask.any():
            strata[name] = {
                "cases": int(mask.sum()),
                "case_accuracy": float(case_correct[mask].mean()),
                "flagged_rate": float(flagged[mask].mean()),
            }
    out["strata"] = strata
    out["case_correct"] = [bool(v) for v in case_correct]
    return out


def finding_metrics(reference: Sequence[ReferenceCase], answers: Mapping[str, SystemAnswer]) -> dict[str, Any]:
    """Regulatory-finding track: two independent yes/no classifications per description."""
    n = len(reference)
    questions = sorted({q for r in reference for q in r.answers})
    answered = np.array([(a := answers.get(r.case_id)) is not None and a.answers is not None for r in reference])
    out: dict[str, Any] = {"n": n, "coverage": float(answered.mean()) if n else 0.0, "questions": {}}
    all_right = np.ones(n, dtype=bool)
    for q in questions:
        ref = np.array([bool(r.answers.get(q)) for r in reference])
        pred = np.array(
            [bool(a and a.answers and a.answers.get(q)) for a in (answers.get(r.case_id) for r in reference)]
        )
        right = (ref == pred) & answered
        all_right &= right
        out["questions"][q] = {
            **binary(ref, pred & answered),
            "accuracy": float(right.mean()),
            "positives": int(ref.sum()),
        }
    out["case_accuracy"] = float(all_right.mean()) if n else None
    out["case_correct"] = [bool(v) for v in all_right]
    return out
