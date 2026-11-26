"""Data contracts: the case packet every system sees, and the hidden reference record.

A *case packet* is one synthetic participant record plus the protocol excerpt
needed to review it. It is the only thing a model, rule or baseline may read.
The *case truth* (scenario, findings, reference answers) is stored in a separate
file and is never part of any request.

Every item a reviewer could cite carries a short `ref` (for example `ASM-2`),
so findings can point at their evidence.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

PACKET_VERSION = "1"

Domain = Literal["eligibility", "consent"]
FindingKind = Literal["issue", "missing", "conflict"]
Outcome = Literal["no_issue", "potential_issue", "insufficient_evidence", "conflicting_evidence"]
Priority = Literal["routine", "standard", "expedited"]
Category = Literal["routine", "issue", "ambiguous"]

OUTCOMES: tuple[Outcome, ...] = ("no_issue", "potential_issue", "insufficient_evidence", "conflicting_evidence")
PRIORITIES: tuple[Priority, ...] = ("routine", "standard", "expedited")


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------- protocol


class ProtocolVersion(_Strict):
    version: str
    effective_date: str  # YYYY-MM-DD; applies to enrollments on or after this date
    summary_of_changes: str | None = None


class EligibleRange(_Strict):
    """A participant is eligible on this criterion when min <= value <= max (both inclusive)."""

    minimum: float | None = None
    maximum: float | None = None


class Criterion(_Strict):
    ref: str
    kind: Literal["inclusion", "exclusion"]
    text: str
    parameter: str
    unit: str  # the protocol unit for this parameter
    eligible_if: EligibleRange
    applies_from_version: str
    applies_until_version: str | None = None  # superseded from this version on (exclusive)


class UnitConversion(_Strict):
    """protocol_unit_value = value * factor + offset"""

    unit: str
    factor: float
    offset: float = 0.0


class ConsentVersion(_Strict):
    ref: str
    version: str
    irb_approval_date: str
    site_effective_date: str  # the version to be used for signatures on or after this date
    reconsent_required: bool = False  # ongoing participants must sign this version


class Protocol(_Strict):
    study_id: str
    versions: list[ProtocolVersion]
    criteria: list[Criterion]
    accepted_units: dict[str, list[UnitConversion]] = Field(default_factory=dict)  # parameter -> other units
    screening_window_days: int
    retest_policy: str
    consent_policy: str
    consent_versions: list[ConsentVersion]


# ------------------------------------------------------------------ record


class Assessment(_Strict):
    ref: str
    parameter: str
    value: float | None
    unit: str | None
    collected_date: str  # YYYY-MM-DD
    source: Literal["site", "central_lab"] = "site"


class ConsentRecord(_Strict):
    ref: str
    icf_version: str
    participant_signed: str | None  # date (YYYY-MM-DD) or date-time with UTC offset; None = not recorded
    investigator_signed: str | None
    document_on_file: bool
    verification_status: Literal["verified", "pending", "not_available"]


class Event(_Strict):
    ref: str
    type: Literal["study_procedure", "enrollment", "randomization", "study_visit", "screen_failure"]
    occurred: str  # date-time with UTC offset
    description: str


class Note(_Strict):
    ref: str
    date: str
    author_role: str
    text: str


class ParticipantRecord(_Strict):
    participant_id: str
    site_id: str
    assessments: list[Assessment]
    consents: list[ConsentRecord]
    events: list[Event]
    notes: list[Note] = Field(default_factory=list)


class CasePacket(_Strict):
    """Everything a system may see for one case."""

    packet_version: str = PACKET_VERSION
    protocol: Protocol
    record: ParticipantRecord


# ------------------------------------------------------------------- truth


class Finding(_Strict):
    domain: Domain
    kind: FindingKind
    code: str
    evidence_refs: list[str] = Field(default_factory=list)

    def key(self) -> tuple[str, str, str]:
        return (self.domain, self.kind, self.code)


class NoteMeaning(_Strict):
    """The structured meaning of a free-text note. Hidden from every evaluated system.

    The generator writes the note text from this meaning, so the reference
    labels never depend on anyone (human or model) reading the text.
    """

    note_ref: str
    type: Literal[
        "irrelevant",
        "repeat_assessment",
        "void_assessment",
        "procedure_before_consent",
        "consent_time_clarified",
        "contradicts_assessment",
    ]
    target_ref: str | None = None
    parameter: str | None = None
    value: float | None = None
    unit: str | None = None
    date: str | None = None
    occurred: str | None = None


class Reference(_Strict):
    answers: dict[str, bool]
    eligibility_outcome: Outcome
    consent_outcome: Outcome
    missing_evidence: bool
    conflicting_evidence: bool
    review_priority: Priority
    findings: list[Finding]


class CaseTruth(_Strict):
    case_id: str
    split: str
    seed: int
    generator_version: str
    scenario: str
    category: Category
    tags: list[str]
    declared_findings: list[Finding]  # what the scenario was built to contain
    note_meanings: list[NoteMeaning]
    reference: Reference  # derived independently by the reference adjudicator


class Case(_Strict):
    case_id: str
    packet: CasePacket
