"""From findings to yes/no answers, and from yes/no answers to the four decision outputs.

The same functions are applied to the reference and to every system's answers,
so a label can never mean one thing for the reference and another for a model.

Outcome per domain, by precedence: a documented issue outranks a contradiction,
which outranks missing evidence:

    potential_issue > conflicting_evidence > insufficient_evidence > no_issue
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from triallab.schema import Finding, Outcome, Priority

TRIAGE_QUESTIONS = (
    "eligibility_issue",
    "eligibility_insufficient",
    "eligibility_conflicting",
    "consent_issue",
    "consent_insufficient",
    "consent_conflicting",
    "review_needed",
    "review_expedited",
)

# Finding codes that call for expedited human review. Everything else is standard.
EXPEDITED_CODES = frozenset({"criterion_not_met", "consent_after_procedure", "consent_record_missing"})

_KIND_SUFFIX = {"issue": "issue", "missing": "insufficient", "conflict": "conflicting"}


def answers_from_findings(findings: Iterable[Finding]) -> dict[str, bool]:
    findings = list(findings)
    answers = dict.fromkeys(TRIAGE_QUESTIONS, False)
    for finding in findings:
        answers[f"{finding.domain}_{_KIND_SUFFIX[finding.kind]}"] = True
    answers["review_needed"] = bool(findings)
    answers["review_expedited"] = any(f.code in EXPEDITED_CODES for f in findings)
    return answers


@dataclass(frozen=True)
class Decision:
    """The four decision outputs for one case."""

    eligibility_outcome: Outcome
    consent_outcome: Outcome
    missing_evidence: bool
    conflicting_evidence: bool
    review_priority: Priority


def _outcome(answers: Mapping[str, bool], domain: str) -> Outcome:
    if answers.get(f"{domain}_issue"):
        return "potential_issue"
    if answers.get(f"{domain}_conflicting"):
        return "conflicting_evidence"
    if answers.get(f"{domain}_insufficient"):
        return "insufficient_evidence"
    return "no_issue"


def decision_from_answers(answers: Mapping[str, bool]) -> Decision:
    priority: Priority = "routine"
    if answers.get("review_expedited"):
        priority = "expedited"
    elif answers.get("review_needed"):
        priority = "standard"
    return Decision(
        eligibility_outcome=_outcome(answers, "eligibility"),
        consent_outcome=_outcome(answers, "consent"),
        missing_evidence=bool(answers.get("eligibility_insufficient") or answers.get("consent_insufficient")),
        conflicting_evidence=bool(answers.get("eligibility_conflicting") or answers.get("consent_conflicting")),
        review_priority=priority,
    )


def consistent(answers: Mapping[str, bool]) -> bool:
    """Do the answers agree with each other?

    - expedited review implies review is needed;
    - any issue, missing-evidence or conflict answer implies review is needed;
    - review needed implies at least one stated reason.
    """
    reasons = any(answers.get(q) for q in TRIAGE_QUESTIONS[:6])
    needed, expedited = bool(answers.get("review_needed")), bool(answers.get("review_expedited"))
    return (not expedited or needed) and (not reasons or needed) and (not needed or reasons)
