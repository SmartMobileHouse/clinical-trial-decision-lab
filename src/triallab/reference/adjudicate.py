"""The reference adjudicator: how reference labels are established.

Reference labels come from deterministic logic over objective facts, never from
a language model. The adjudicator:

1. takes the case packet and the hidden structured meaning of each free-text
   note (written by the generator before the text was rendered);
2. applies those meanings to the record (a documented repeat result becomes a
   result, a voided entry is removed, and so on);
3. runs the same eight protocol rules a study team would configure.

The scenario that built a case also declares which findings it intended. The
test suite requires the adjudicator's findings to equal that declaration for
every case, so each label has two independent derivations that must agree.
"""

from __future__ import annotations

from triallab.clinical.rules import enrollment_event, evaluate_rules
from triallab.reference.derive import answers_from_findings, decision_from_answers
from triallab.schema import Assessment, CasePacket, Event, Finding, NoteMeaning, ParticipantRecord, Reference


def evidence_view(record: ParticipantRecord, meanings: list[NoteMeaning]) -> ParticipantRecord:
    """The record as a reviewer who understood every note would read it."""
    view = record.model_copy(deep=True)
    for meaning in meanings:
        if meaning.type == "repeat_assessment":
            view.assessments.append(
                Assessment(
                    ref=meaning.note_ref,
                    parameter=meaning.parameter or "",
                    value=meaning.value,
                    unit=meaning.unit,
                    collected_date=meaning.date or "",
                )
            )
        elif meaning.type == "void_assessment":
            view.assessments = [a for a in view.assessments if a.ref != meaning.target_ref]
        elif meaning.type == "procedure_before_consent":
            view.events.append(
                Event(
                    ref=meaning.note_ref,
                    type="study_procedure",
                    occurred=meaning.occurred or "",
                    description="procedure documented in a note",
                )
            )
        elif meaning.type == "consent_time_clarified":
            for consent in view.consents:
                if consent.ref == meaning.target_ref:
                    consent.participant_signed = meaning.occurred
    return view


def adjudicate(packet: CasePacket, meanings: list[NoteMeaning]) -> Reference:
    view = evidence_view(packet.record, meanings)
    findings = evaluate_rules(packet.protocol, view)
    enrolled = enrollment_event(view) is not None
    for meaning in meanings:
        if meaning.type == "contradicts_assessment" and enrolled:
            refs = sorted({meaning.note_ref, *([meaning.target_ref] if meaning.target_ref else [])})
            findings.append(
                Finding(domain="eligibility", kind="conflict", code="note_contradicts_record", evidence_refs=refs)
            )
    answers = answers_from_findings(findings)
    decision = decision_from_answers(answers)
    return Reference(
        answers=answers,
        eligibility_outcome=decision.eligibility_outcome,
        consent_outcome=decision.consent_outcome,
        missing_evidence=decision.missing_evidence,
        conflicting_evidence=decision.conflicting_evidence,
        review_priority=decision.review_priority,
        findings=findings,
    )
