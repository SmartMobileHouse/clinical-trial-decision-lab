"""Protocol-aware deterministic rules for eligibility and informed-consent review.

Eight transparent rules, each a plain function of (protocol, participant record)
that returns findings. They read structured fields only; they never read the
free text of notes. Each rule can be called and tested on its own.

| Rule | What it checks |
|---|---|
| eligibility_thresholds        | governing result outside a criterion limit for an enrolled participant |
| missing_eligibility_tests     | required assessment absent, or its result unusable (no value, no or unknown unit) |
| screening_enrollment_timing   | governing result outside the screening window, or obtained only after enrollment |
| consent_completion            | no consent record, unverified or unavailable form, missing investigator signature |
| consent_version_applicability | signed version was not the version in effect on the signing date |
| consent_timing                | consent signed after the first study-specific procedure, or order cannot be told |
| reconsent_evidence            | required re-consent documentation absent |
| inconsistent_documentation    | same-day results or consent records that support different conclusions |

Finding kinds: `issue` (documented evidence of a problem), `missing` (evidence
needed to decide is absent or unusable) and `conflict` (records contradict each
other). A missing consent record is `missing`, never `issue`: absent
documentation is not proof that consent did not occur.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime
from typing import Literal

from triallab.schema import (
    Assessment,
    ConsentRecord,
    ConsentVersion,
    Criterion,
    Event,
    Finding,
    ParticipantRecord,
    Protocol,
)

RULES_VERSION = "1"
PROCEDURE_EVENTS = ("study_procedure", "enrollment", "randomization", "study_visit")
COMPARE_DECIMALS = 6  # values are compared after rounding, so unit conversion noise cannot flip a limit


# ------------------------------------------------------------------- time


@dataclass(frozen=True)
class When:
    """A recorded moment: always a calendar date, and an exact instant when a time and offset were recorded."""

    day: date
    instant: datetime | None


def parse_when(text: str) -> When:
    if "T" in text:
        moment = datetime.fromisoformat(text)
        if moment.tzinfo is not None:
            return When(moment.date(), moment)
        return When(moment.date(), None)  # a time without an offset cannot be ordered across systems
    return When(date.fromisoformat(text), None)


def order(first: When, second: When) -> Literal["before", "after", "undetermined"]:
    """Is `first` before or after `second`? Exact instants win; otherwise calendar dates decide."""
    if first.instant is not None and second.instant is not None:
        return "before" if first.instant <= second.instant else "after"
    if first.day < second.day:
        return "before"
    if first.day > second.day:
        return "after"
    return "undetermined"


# ------------------------------------------------------------ eligibility


def enrollment_event(record: ParticipantRecord) -> Event | None:
    events = [e for e in record.events if e.type == "enrollment"]
    return min(events, key=lambda e: parse_when(e.occurred).instant or datetime.max) if events else None


def protocol_version_index(protocol: Protocol, on: date) -> int:
    """Index of the protocol version in effect on a date (the first version before any effective date)."""
    index = 0
    for i, version in enumerate(protocol.versions):
        if date.fromisoformat(version.effective_date) <= on:
            index = i
    return index


def applicable_criteria(protocol: Protocol, on: date) -> list[Criterion]:
    names = [v.version for v in protocol.versions]
    current = protocol_version_index(protocol, on)
    out = []
    for criterion in protocol.criteria:
        start = names.index(criterion.applies_from_version)
        end = names.index(criterion.applies_until_version) if criterion.applies_until_version else len(names)
        if start <= current < end:
            out.append(criterion)
    return out


def to_protocol_unit(protocol: Protocol, criterion: Criterion, assessment: Assessment) -> float | None:
    """The result in the protocol unit, or None when the value or unit cannot be used."""
    if assessment.value is None or assessment.unit is None:
        return None
    if assessment.unit == criterion.unit:
        return assessment.value
    for conversion in protocol.accepted_units.get(criterion.parameter, []):
        if conversion.unit == assessment.unit:
            return assessment.value * conversion.factor + conversion.offset
    return None


def within_limits(criterion: Criterion, value: float) -> bool:
    value = round(value, COMPARE_DECIMALS)
    low, high = criterion.eligible_if.minimum, criterion.eligible_if.maximum
    return (low is None or value >= low) and (high is None or value <= high)


EvidenceStatus = Literal["absent", "only_after_enrollment", "unusable", "conflict", "fail", "pass"]


@dataclass(frozen=True)
class CriterionEvidence:
    criterion: Criterion
    status: EvidenceStatus
    refs: tuple[str, ...]
    governing_day: date | None = None


def criterion_evidence(
    protocol: Protocol, record: ParticipantRecord, criterion: Criterion, enrolled_on: date
) -> CriterionEvidence:
    """Resolve what the record says about one criterion.

    The most recent result collected on or before the enrollment date governs
    (the protocol's retest policy). Several results on that same date must agree.
    """
    mine = [a for a in record.assessments if a.parameter == criterion.parameter]
    before = [a for a in mine if date.fromisoformat(a.collected_date) <= enrolled_on]
    if not before:
        if mine:
            return CriterionEvidence(criterion, "only_after_enrollment", tuple(a.ref for a in mine))
        return CriterionEvidence(criterion, "absent", ())
    governing_day = max(date.fromisoformat(a.collected_date) for a in before)
    governing = [a for a in before if date.fromisoformat(a.collected_date) == governing_day]
    refs = tuple(a.ref for a in governing)
    values = [to_protocol_unit(protocol, criterion, a) for a in governing]
    usable = [v for v in values if v is not None]
    if not usable:
        return CriterionEvidence(criterion, "unusable", refs, governing_day)
    verdicts = {within_limits(criterion, v) for v in usable}
    if len(verdicts) > 1:
        return CriterionEvidence(criterion, "conflict", refs, governing_day)
    return CriterionEvidence(criterion, "pass" if verdicts.pop() else "fail", refs, governing_day)


def _eligibility_evidence(protocol: Protocol, record: ParticipantRecord) -> tuple[Event, list[CriterionEvidence]]:
    """Evidence per applicable criterion; empty when the participant was not enrolled."""
    enrolled = enrollment_event(record)
    if enrolled is None:
        raise _NotEnrolled
    enrolled_on = parse_when(enrolled.occurred).day
    return enrolled, [
        criterion_evidence(protocol, record, c, enrolled_on) for c in applicable_criteria(protocol, enrolled_on)
    ]


class _NotEnrolled(Exception):
    """Eligibility findings concern enrolled participants only (a screen failure is not an issue)."""


def _finding(domain: str, kind: str, code: str, refs: tuple[str, ...] | list[str]) -> Finding:
    return Finding(domain=domain, kind=kind, code=code, evidence_refs=sorted(set(refs)))


def rule_eligibility_thresholds(protocol: Protocol, record: ParticipantRecord) -> list[Finding]:
    try:
        enrolled, evidence = _eligibility_evidence(protocol, record)
    except _NotEnrolled:
        return []
    return [
        _finding("eligibility", "issue", "criterion_not_met", (*e.refs, e.criterion.ref, enrolled.ref))
        for e in evidence
        if e.status == "fail"
    ]


def rule_missing_eligibility_tests(protocol: Protocol, record: ParticipantRecord) -> list[Finding]:
    try:
        enrolled, evidence = _eligibility_evidence(protocol, record)
    except _NotEnrolled:
        return []
    out = []
    for e in evidence:
        if e.status == "absent":
            out.append(
                _finding("eligibility", "missing", "required_assessment_missing", (e.criterion.ref, enrolled.ref))
            )
        elif e.status == "unusable":
            out.append(_finding("eligibility", "missing", "result_unusable", (*e.refs, e.criterion.ref)))
    return out


def rule_screening_enrollment_timing(protocol: Protocol, record: ParticipantRecord) -> list[Finding]:
    try:
        enrolled, evidence = _eligibility_evidence(protocol, record)
    except _NotEnrolled:
        return []
    enrolled_on = parse_when(enrolled.occurred).day
    out = []
    for e in evidence:
        refs = (*e.refs, e.criterion.ref, enrolled.ref)
        if e.status == "only_after_enrollment":
            out.append(_finding("eligibility", "issue", "assessment_after_enrollment", refs))
        elif (
            e.status == "pass"
            and e.governing_day is not None
            and (enrolled_on - e.governing_day).days > protocol.screening_window_days
        ):
            out.append(_finding("eligibility", "issue", "assessment_outside_window", refs))
    return out


# ---------------------------------------------------------------- consent


def first_procedure(record: ParticipantRecord) -> Event | None:
    events = [e for e in record.events if e.type in PROCEDURE_EVENTS]
    return min(events, key=lambda e: parse_when(e.occurred).instant or datetime.max) if events else None


def signed_consents(record: ParticipantRecord) -> list[ConsentRecord]:
    signed = [c for c in record.consents if c.participant_signed is not None]
    return sorted(signed, key=lambda c: _sort_key(parse_when(c.participant_signed or "")))


def _sort_key(when: When) -> tuple[date, float]:
    return (when.day, when.instant.timestamp() if when.instant else 0.0)


def consent_version_in_effect(protocol: Protocol, on: date) -> ConsentVersion | None:
    current = None
    for version in protocol.consent_versions:
        if date.fromisoformat(version.site_effective_date) <= on:
            current = version
    return current


def initial_consents(record: ParticipantRecord) -> list[ConsentRecord]:
    """Signed records of the version the participant signed first."""
    signed = signed_consents(record)
    return [c for c in signed if c.icf_version == signed[0].icf_version] if signed else []


def _initial_orders(record: ParticipantRecord) -> tuple[Event, list[ConsentRecord], set[str]] | None:
    procedure = first_procedure(record)
    initial = initial_consents(record)
    if procedure is None or not initial:
        return None
    at = parse_when(procedure.occurred)
    return procedure, initial, {order(parse_when(c.participant_signed or ""), at) for c in initial}


def rule_consent_completion(protocol: Protocol, record: ParticipantRecord) -> list[Finding]:
    if not record.consents:
        procedure = first_procedure(record)
        if procedure is None:
            return []
        return [_finding("consent", "missing", "consent_record_missing", (procedure.ref,))]
    signed = signed_consents(record)
    if not signed:
        return [_finding("consent", "missing", "consent_unverified", [c.ref for c in record.consents])]
    out = []
    for consent in signed:
        if not consent.document_on_file or consent.verification_status != "verified":
            out.append(_finding("consent", "missing", "consent_unverified", (consent.ref,)))
        elif consent.investigator_signed is None:
            out.append(_finding("consent", "issue", "consent_signature_incomplete", (consent.ref,)))
    return out


def rule_consent_version_applicability(protocol: Protocol, record: ParticipantRecord) -> list[Finding]:
    out = []
    for consent in signed_consents(record):
        current = consent_version_in_effect(protocol, parse_when(consent.participant_signed or "").day)
        if current is None or current.version != consent.icf_version:
            refs = [consent.ref] + ([current.ref] if current else [])
            out.append(_finding("consent", "issue", "consent_version_not_current", refs))
    return out


def rule_consent_timing(protocol: Protocol, record: ParticipantRecord) -> list[Finding]:
    resolved = _initial_orders(record)
    if resolved is None:
        return []
    procedure, initial, orders = resolved
    refs = (*[c.ref for c in initial], procedure.ref)
    if orders == {"after"}:
        return [_finding("consent", "issue", "consent_after_procedure", refs)]
    if orders == {"undetermined"}:
        return [_finding("consent", "missing", "consent_order_undetermined", refs)]
    return []


def rule_reconsent_evidence(protocol: Protocol, record: ParticipantRecord) -> list[Finding]:
    signed = signed_consents(record)
    if not signed:
        return []
    first_signed = parse_when(signed[0].participant_signed or "").day
    out = []
    for version in protocol.consent_versions[1:]:
        effective = date.fromisoformat(version.site_effective_date)
        if not version.reconsent_required or first_signed >= effective:
            continue
        later = [e for e in record.events if parse_when(e.occurred).day > effective]
        if later and not any(c.icf_version == version.version for c in signed):
            out.append(
                _finding("consent", "missing", "reconsent_record_missing", (version.ref, *[e.ref for e in later]))
            )
    return out


def rule_inconsistent_documentation(protocol: Protocol, record: ParticipantRecord) -> list[Finding]:
    out = []
    try:
        _, evidence = _eligibility_evidence(protocol, record)
    except _NotEnrolled:
        evidence = []
    for e in evidence:
        if e.status == "conflict":
            out.append(_finding("eligibility", "conflict", "conflicting_results", (*e.refs, e.criterion.ref)))
    resolved = _initial_orders(record)
    if resolved is not None:
        procedure, initial, orders = resolved
        if len(orders) > 1:
            refs = (*[c.ref for c in initial], procedure.ref)
            out.append(_finding("consent", "conflict", "consent_timestamp_conflict", refs))
    return out


Rule = Callable[[Protocol, ParticipantRecord], list[Finding]]

RULES: dict[str, Rule] = {
    "eligibility_thresholds": rule_eligibility_thresholds,
    "missing_eligibility_tests": rule_missing_eligibility_tests,
    "screening_enrollment_timing": rule_screening_enrollment_timing,
    "consent_completion": rule_consent_completion,
    "consent_version_applicability": rule_consent_version_applicability,
    "consent_timing": rule_consent_timing,
    "reconsent_evidence": rule_reconsent_evidence,
    "inconsistent_documentation": rule_inconsistent_documentation,
}


def evaluate_rules(protocol: Protocol, record: ParticipantRecord) -> list[Finding]:
    """Run every rule and return the distinct findings in a stable order."""
    found: dict[tuple[str, str, str, tuple[str, ...]], Finding] = {}
    for rule in RULES.values():
        for finding in rule(protocol, record):
            found[(*finding.key(), tuple(finding.evidence_refs))] = finding
    return [found[key] for key in sorted(found)]


def fired_rules(protocol: Protocol, record: ParticipantRecord) -> dict[str, list[Finding]]:
    """Which rule produced which findings (for explanations and the report)."""
    return {name: findings for name, rule in RULES.items() if (findings := rule(protocol, record))}
