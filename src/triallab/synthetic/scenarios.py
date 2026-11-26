"""Scenarios: how each synthetic case is built and what it is meant to contain.

A case starts as a fully compliant participant record (`Draft.compliant`). A
scenario then changes it in one defined way and declares the findings that the
change creates. Declared findings are checked against the independent reference
adjudicator for every generated case.

Categories:
- routine   : compliant records, including ones that look suspicious but are correct
- issue     : a documented eligibility or consent problem
- ambiguous : missing, unusable or contradictory evidence

Tags mark what makes a case hard: `boundary`, `unit`, `amendment`, `overlap`,
`timezone`, `suspicious_but_correct`, `multi_finding`, and `text_dependent`
(the deciding fact is written only in a free-text note).
"""

from __future__ import annotations

import random
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, time, timedelta, timezone

from triallab.clinical.rules import applicable_criteria
from triallab.schema import (
    Assessment,
    CasePacket,
    ConsentRecord,
    Criterion,
    Event,
    Finding,
    Note,
    NoteMeaning,
    ParticipantRecord,
)
from triallab.synthetic.library import OVERLAP_MAX, OVERLAP_PARAMETER, ParamSpec, Site, StudyDesign

DISTRACTOR_NOTES = (
    "Participant rescheduled the visit because of travel; no protocol impact.",
    "Courier pickup for central lab samples was delayed by one day; samples remained within stability.",
    "Source documents scanned and filed in the investigator site file.",
    "Back-up coordinator covered this visit while the lead coordinator was on leave.",
    "Storage temperature log for the investigational product reviewed; no excursions.",
    "Participant received a copy of the signed consent form.",
    "Eligibility checklist reviewed and signed by the investigator before enrollment.",
    "Monitor confirmed that the delegation log is current.",
    "Participant asked about visit reimbursement; question passed to the study coordinator.",
    "Lab kit lot number recorded; kit within expiry date.",
)


def _tz(offset: str) -> timezone:
    sign = -1 if offset[0] == "-" else 1
    hours, minutes = int(offset[1:3]), int(offset[4:6])
    return timezone(sign * timedelta(hours=hours, minutes=minutes))


@dataclass
class DAssessment:
    parameter: str
    value: float | None
    unit: str | None
    day: date
    source: str = "site"


@dataclass
class DConsent:
    version: str
    participant_signed: datetime | date | None
    investigator_signed: datetime | date | None
    on_file: bool = True
    status: str = "verified"


@dataclass
class DEvent:
    type: str
    at: datetime
    description: str


@dataclass
class DNote:
    day: date
    role: str
    text: Callable[[dict[int, str]], str]  # receives {id(object): ref} once refs are assigned
    meaning: str = "irrelevant"
    target: object | None = None
    parameter: str | None = None
    value: float | None = None
    unit: str | None = None
    on: date | None = None
    occurred: datetime | None = None


def _fixed(text: str) -> Callable[[dict[int, str]], str]:
    """A note whose text does not mention any other item."""
    return lambda refs: text


def _iso(moment: datetime | date | None) -> str | None:
    if moment is None:
        return None
    if isinstance(moment, datetime):
        return moment.isoformat(timespec="minutes")
    return moment.isoformat()


@dataclass
class Draft:
    study: StudyDesign
    site: Site
    participant_id: str
    assessments: list[DAssessment] = field(default_factory=list)
    consents: list[DConsent] = field(default_factory=list)
    events: list[DEvent] = field(default_factory=list)
    notes: list[DNote] = field(default_factory=list)
    declared: list[Finding] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)

    # ------------------------------------------------------------ lookups

    def event(self, kind: str) -> DEvent:
        return next(e for e in self.events if e.type == kind)

    def has_event(self, kind: str) -> bool:
        return any(e.type == kind for e in self.events)

    @property
    def screening(self) -> DEvent:
        return self.event("study_procedure")

    @property
    def enrollment(self) -> DEvent:
        return self.event("enrollment")

    @property
    def consent(self) -> DConsent:
        return self.consents[0]

    def criteria(self) -> list[Criterion]:
        return applicable_criteria(self.study.protocol, self.enrollment.at.date())

    def limits(self, parameter: str) -> tuple[float | None, float | None]:
        """The combined eligible range for a parameter across the applicable criteria."""
        low: float | None = None
        high: float | None = None
        for criterion in self.criteria():
            if criterion.parameter != parameter:
                continue
            r = criterion.eligible_if
            low = r.minimum if low is None else (max(low, r.minimum) if r.minimum is not None else low)
            high = r.maximum if high is None else (min(high, r.maximum) if r.maximum is not None else high)
        return low, high

    def parameters(self) -> list[str]:
        return list(dict.fromkeys(c.parameter for c in self.criteria()))

    def assessment(self, parameter: str) -> DAssessment:
        return next(a for a in self.assessments if a.parameter == parameter)

    def spec(self, parameter: str) -> ParamSpec:
        return self.study.specs[parameter]

    def declare(self, domain: str, kind: str, code: str) -> None:
        self.declared.append(Finding(domain=domain, kind=kind, code=code))

    def tag(self, *tags: str) -> None:
        self.tags.extend(t for t in tags if t not in self.tags)

    # ------------------------------------------------------------- values

    def _grid(self, spec: ParamSpec, low: float, high: float) -> list[float]:
        first, last = round(low / spec.step), round(high / spec.step)
        return [round(i * spec.step, spec.decimals) for i in range(first, last + 1)]

    def passing(self, rng: random.Random, parameter: str, margin: int = 2) -> float:
        spec = self.spec(parameter)
        low, high = self.limits(parameter)
        lo = max(low if low is not None else spec.plausible[0], spec.plausible[0])
        hi = min(high if high is not None else spec.plausible[1], spec.plausible[1])
        pad = margin * spec.step
        return rng.choice(self._grid(spec, lo + (pad if low is not None else 0), hi - (pad if high is not None else 0)))

    def failing(self, rng: random.Random, parameter: str, steps: tuple[int, int] = (2, 12)) -> float:
        spec = self.spec(parameter)
        low, high = self.limits(parameter)
        options: list[float] = []
        if high is not None:
            top = min(spec.plausible[1], high + steps[1] * spec.step)
            options += self._grid(spec, high + steps[0] * spec.step, top)
        if low is not None:
            bottom = max(spec.plausible[0], low - steps[1] * spec.step)
            options += self._grid(spec, bottom, low - steps[0] * spec.step)
        return rng.choice(options)

    def in_alt_unit(self, parameter: str, value: float) -> tuple[float, str]:
        spec = self.spec(parameter)
        conversion = spec.alt_units[0]
        return round((value - conversion.offset) / conversion.factor, spec.alt_decimals), conversion.unit

    def simple_parameters(self, rng: random.Random, *, alt_unit: bool = False) -> str:
        """A parameter governed by exactly one applicable criterion (never the overlapping one)."""
        counts: dict[str, int] = {}
        for criterion in self.criteria():
            counts[criterion.parameter] = counts.get(criterion.parameter, 0) + 1
        names = [p for p, n in counts.items() if n == 1 and p != "age" and (not alt_unit or self.spec(p).alt_units)]
        return rng.choice(names)

    # ----------------------------------------------------------- timeline

    def shift_after_screening(self, delta: timedelta) -> None:
        """Move enrollment and everything after it."""
        for event in self.events:
            if event.type in ("enrollment", "randomization", "study_visit"):
                event.at += delta

    def set_consent_time(self, moment: datetime | date) -> None:
        self.consent.participant_signed = moment
        if isinstance(moment, datetime):
            self.consent.investigator_signed = moment + timedelta(minutes=10)
        else:
            self.consent.investigator_signed = moment

    def add_note(self, note: DNote) -> None:
        self.notes.append(note)

    # -------------------------------------------------------------- build

    @classmethod
    def compliant(
        cls, rng: random.Random, study: StudyDesign, participant_id: str, phase: str, site: Site | None = None
    ) -> Draft:
        """A complete, consistent, compliant participant record.

        phase "early": the whole timeline precedes any amendment or new consent version.
        phase "late" : the whole timeline follows them.
        phase "bridge": consent precedes the second consent version and a visit follows it.
        """
        site = site or rng.choice(study.sites)
        zone = _tz(site.utc_offset)
        draft = cls(study=study, site=site, participant_id=participant_id)
        if phase == "early":
            consent_day = study.start + timedelta(days=rng.randrange(20, 111))
        elif phase == "late":
            consent_day = study.start + timedelta(days=rng.randrange(200, 301))
        else:
            consent_day = study.start + timedelta(days=rng.randrange(120, 141))
        consent_at = datetime.combine(consent_day, time(rng.randrange(8, 15), rng.randrange(0, 60)), zone)
        if rng.random() < 0.5:
            screening_at = consent_at + timedelta(minutes=rng.randrange(20, 181))
        else:
            screening_day = consent_day + timedelta(days=rng.randrange(1, 4))
            screening_at = datetime.combine(screening_day, time(rng.randrange(8, 12), rng.randrange(0, 60)), zone)
        window = study.protocol.screening_window_days
        enrollment_day = screening_at.date() + timedelta(days=rng.randrange(4, window - 2))
        enrollment_at = datetime.combine(enrollment_day, time(rng.randrange(9, 16), rng.randrange(0, 60)), zone)

        version = "1.0"
        if study.icf2_date is not None and consent_day >= study.icf2_date:
            version = "2.0"
        draft.consents.append(DConsent(version, consent_at, consent_at + timedelta(minutes=rng.randrange(5, 31))))
        draft.events.append(DEvent("study_procedure", screening_at, "Screening visit: vital signs, ECG and blood draw"))
        draft.events.append(DEvent("enrollment", enrollment_at, "Participant enrolled"))
        if rng.random() < 0.8:
            at = enrollment_at + timedelta(minutes=rng.randrange(30, 181))
            draft.events.append(DEvent("randomization", at, "Participant randomized"))
        if phase == "bridge":
            assert study.icf2_date is not None
            visit_day = study.icf2_date + timedelta(days=rng.randrange(5, 31))
            visit_at = datetime.combine(visit_day, time(rng.randrange(9, 15), rng.randrange(0, 60)), zone)
            draft.events.append(DEvent("study_visit", visit_at, "Scheduled study visit"))
        elif rng.random() < 0.3:
            visit_at = enrollment_at + timedelta(days=rng.randrange(7, 15))
            draft.events.append(DEvent("study_visit", visit_at, "Scheduled study visit"))

        for parameter in draft.parameters():
            spec = draft.spec(parameter)
            day = screening_at.date() + timedelta(days=1 if rng.random() < 0.2 else 0)
            source = "central_lab" if spec.alt_units and rng.random() < 0.5 else "site"
            draft.assessments.append(DAssessment(parameter, draft.passing(rng, parameter), spec.unit, day, source))

        for _ in range(rng.choice((0, 0, 1, 1, 2))):
            text = rng.choice(DISTRACTOR_NOTES)
            day = screening_at.date() + timedelta(days=rng.randrange(0, 4))
            role = rng.choice(("site coordinator", "monitor", "investigator"))
            draft.notes.append(DNote(day, role, _fixed(text)))
        return draft

    def finish(self) -> tuple[CasePacket, list[NoteMeaning]]:
        """Assign refs in chronological order and render the packet and the hidden note meanings."""
        refs: dict[int, str] = {}
        assessments = sorted(self.assessments, key=lambda a: (a.day, a.parameter, a.source))
        consents = sorted(self.consents, key=lambda c: (_iso(c.participant_signed) or "", c.version))
        events = sorted(self.events, key=lambda e: e.at)
        notes = sorted(self.notes, key=lambda n: n.day)
        for prefix, items in (("ASM", assessments), ("CNS", consents), ("EVT", events), ("NOTE", notes)):
            for i, item in enumerate(items, 1):
                refs[id(item)] = f"{prefix}-{i}"
        record = ParticipantRecord(
            participant_id=self.participant_id,
            site_id=self.site.site_id,
            assessments=[
                Assessment(
                    ref=refs[id(a)],
                    parameter=a.parameter,
                    value=a.value,
                    unit=a.unit,
                    collected_date=a.day.isoformat(),
                    source=a.source,
                )
                for a in assessments
            ],  # fmt: skip
            consents=[
                ConsentRecord(
                    ref=refs[id(c)],
                    icf_version=c.version,
                    participant_signed=_iso(c.participant_signed),
                    investigator_signed=_iso(c.investigator_signed),
                    document_on_file=c.on_file,
                    verification_status=c.status,
                )
                for c in consents
            ],  # fmt: skip
            events=[
                Event(ref=refs[id(e)], type=e.type, occurred=_iso(e.at) or "", description=e.description)
                for e in events
            ],
            notes=[Note(ref=refs[id(n)], date=n.day.isoformat(), author_role=n.role, text=n.text(refs)) for n in notes],
        )
        meanings = [
            NoteMeaning(
                note_ref=refs[id(n)],
                type=n.meaning,
                target_ref=refs[id(n.target)] if n.target is not None else None,
                parameter=n.parameter,
                value=n.value,
                unit=n.unit,
                date=n.on.isoformat() if n.on else None,
                occurred=_iso(n.occurred),
            )  # fmt: skip
            for n in notes
        ]
        return CasePacket(protocol=self.study.protocol, record=record), meanings


# ---------------------------------------------------------------- scenarios

Builder = Callable[[Draft, random.Random], None]


@dataclass(frozen=True)
class Scenario:
    name: str
    category: str
    count: int  # cases in the 400-case test design
    build: Builder
    phase: str = "any"  # "any", "early", "late", "bridge"
    needs: tuple[str, ...] = ()  # "amendment", "icf2", "reconsent", "overlap"
    site: str = "any"  # "any", "west", "east"
    summary: str = ""


def _fmt(d: Draft, parameter: str, value: float) -> str:
    return f"{value:.{d.spec(parameter).decimals}f}"


# -- routine ---------------------------------------------------------------


def plain_compliant(d: Draft, rng: random.Random) -> None:
    pass


def boundary_at_limit(d: Draft, rng: random.Random) -> None:
    d.tag("boundary", "suspicious_but_correct")
    if rng.random() < 0.6:
        parameter = d.simple_parameters(rng)
        low, high = d.limits(parameter)
        d.assessment(parameter).value = rng.choice([v for v in (low, high) if v is not None])
    else:  # governing results collected exactly on the first day of the screening window
        window = timedelta(days=d.study.protocol.screening_window_days)
        earliest = min(a.day for a in d.assessments)
        for a in d.assessments:
            a.day = earliest
        zone = d.enrollment.at.tzinfo
        target = datetime.combine(earliest + window, d.enrollment.at.time(), zone)
        d.shift_after_screening(target - d.enrollment.at)


def screen_failure_not_enrolled(d: Draft, rng: random.Random) -> None:
    d.tag("suspicious_but_correct")
    parameter = d.simple_parameters(rng)
    d.assessment(parameter).value = d.failing(rng, parameter)
    at = d.screening.at + timedelta(days=rng.randrange(2, 5))
    d.events = [e for e in d.events if e.type == "study_procedure"]
    d.events.append(DEvent("screen_failure", at, "Screen failure recorded: eligibility criteria not met"))


def retest_in_window(d: Draft, rng: random.Random) -> None:
    d.tag("suspicious_but_correct")
    parameter = d.simple_parameters(rng)
    first = d.assessment(parameter)
    repeat_day = first.day + timedelta(days=rng.randrange(1, 4))
    d.assessments.append(DAssessment(parameter, d.passing(rng, parameter), first.unit, repeat_day, first.source))
    first.value = d.failing(rng, parameter)


def alternate_unit_in_range(d: Draft, rng: random.Random) -> None:
    d.tag("unit", "suspicious_but_correct")
    parameter = d.simple_parameters(rng, alt_unit=True)
    a = d.assessment(parameter)
    a.value, a.unit = d.in_alt_unit(parameter, d.passing(rng, parameter, margin=3))
    a.source = "central_lab"


def _between_amendment_limits(d: Draft, rng: random.Random) -> tuple[str, float]:
    """A value that meets the amended limit but not the original one."""
    parameter = d.study.amended_parameter
    assert parameter is not None
    spec = d.spec(parameter)
    old = next(c for c in d.study.protocol.criteria if c.parameter == parameter and c.applies_until_version)
    new = next(c for c in d.study.protocol.criteria if c.parameter == parameter and c.applies_from_version == "2.0")
    if old.eligible_if.maximum != new.eligible_if.maximum:
        assert old.eligible_if.maximum is not None and new.eligible_if.maximum is not None
        grid = d._grid(spec, old.eligible_if.maximum + spec.step, new.eligible_if.maximum)
    else:
        assert old.eligible_if.minimum is not None and new.eligible_if.minimum is not None
        grid = d._grid(spec, new.eligible_if.minimum, old.eligible_if.minimum - spec.step)
    return parameter, rng.choice(grid)


def amendment_enrolled_after(d: Draft, rng: random.Random) -> None:
    d.tag("amendment", "suspicious_but_correct")
    parameter, value = _between_amendment_limits(d, rng)
    d.assessment(parameter).value = value


def reconsent_done(d: Draft, rng: random.Random) -> None:
    d.tag("suspicious_but_correct")
    visit = d.event("study_visit")
    signed = visit.at - timedelta(minutes=rng.randrange(15, 61))
    d.consents.append(DConsent("2.0", signed, signed + timedelta(minutes=10)))


def same_day_consent_first(d: Draft, rng: random.Random) -> None:
    d.tag("suspicious_but_correct")
    d.set_consent_time(d.screening.at - timedelta(minutes=rng.randrange(10, 41)))


def timezone_consent_first(d: Draft, rng: random.Random) -> None:
    """The procedure is logged in UTC: its clock time reads earlier than consent, but it happened later."""
    d.tag("timezone", "suspicious_but_correct")
    zone = d.consent.participant_signed.tzinfo  # type: ignore[union-attr]
    hours = int(d.site.utc_offset[1:3])
    day = d.screening.at.date()
    consent_at = datetime.combine(day, time(hours + rng.randrange(0, 3), rng.randrange(0, 60)), zone)
    d.set_consent_time(consent_at)
    procedure_at = (consent_at + timedelta(minutes=rng.randrange(20, 61))).astimezone(UTC)
    d.screening.at = procedure_at
    d.screening.description = "Screening ECG upload (time recorded by the central system in UTC)"


def note_documents_retest(d: Draft, rng: random.Random) -> None:
    d.tag("text_dependent", "suspicious_but_correct")
    parameter = d.simple_parameters(rng)
    a = d.assessment(parameter)
    spec = d.spec(parameter)
    passing = d.passing(rng, parameter)
    a.value = d.failing(rng, parameter)
    repeat_day = a.day + timedelta(days=rng.randrange(1, 4))
    text = rng.choice((
        "Repeat {label} collected on {day}: {value} {unit}. Result filed in source; EDC entry pending.",
        "{label} was repeated on {day} per the retest policy. Repeat result {value} {unit}, documented in the source worksheet only.",  # noqa: E501
        "Retest performed {day}: {label} {value} {unit}. Lab report on file at site, not yet entered in EDC.",
    )).format(label=spec.label, day=repeat_day.isoformat(), value=_fmt(d, parameter, passing), unit=spec.unit)  # fmt: skip  # noqa: E501
    d.add_note(DNote(repeat_day, "site coordinator", _fixed(text), meaning="repeat_assessment",
                     parameter=parameter, value=passing, unit=spec.unit, on=repeat_day))  # fmt: skip


def note_resolves_duplicate(d: Draft, rng: random.Random) -> None:
    d.tag("text_dependent", "suspicious_but_correct")
    parameter = d.simple_parameters(rng)
    good = d.assessment(parameter)
    bad = DAssessment(parameter, d.failing(rng, parameter), good.unit, good.day, "site")
    good.source = "central_lab"
    d.assessments.append(bad)
    template = rng.choice((
        "Entry {bad} was a transcription error and has been voided after source verification; {good} is the correct result.",  # noqa: E501
        "Source data verification: {bad} does not match the lab report and is void. {good} matches the source.",
    ))  # fmt: skip
    d.add_note(DNote(good.day + timedelta(days=1), "monitor",
                     lambda refs: template.format(bad=refs[id(bad)], good=refs[id(good)]),
                     meaning="void_assessment", target=bad))  # fmt: skip


def note_clarifies_consent_time(d: Draft, rng: random.Random) -> None:
    d.tag("text_dependent", "suspicious_but_correct")
    zone = d.screening.at.tzinfo
    day = d.screening.at.date()
    d.screening.at = datetime.combine(day, time(rng.randrange(10, 13), rng.randrange(0, 60)), zone)
    signed_at = d.screening.at - timedelta(minutes=rng.randrange(25, 91))
    d.set_consent_time(day)
    consent = d.consent
    text = rng.choice((
        "Consent process note: the participant signed the consent form at {t} on {day}, before the screening procedures started.",  # noqa: E501
        "Per the consent process documentation, ICF signature time was {t} on {day}; screening procedures began afterwards.",  # noqa: E501
    )).format(t=signed_at.strftime("%H:%M"), day=day.isoformat())  # fmt: skip
    d.add_note(DNote(day, "site coordinator", _fixed(text), meaning="consent_time_clarified",
                     target=consent, occurred=signed_at))  # fmt: skip


# -- issue -----------------------------------------------------------------


def criterion_not_met(d: Draft, rng: random.Random) -> None:
    parameter = d.simple_parameters(rng)
    d.assessment(parameter).value = d.failing(rng, parameter)
    d.declare("eligibility", "issue", "criterion_not_met")


def criterion_just_outside(d: Draft, rng: random.Random) -> None:
    d.tag("boundary")
    parameter = d.simple_parameters(rng)
    d.assessment(parameter).value = d.failing(rng, parameter, steps=(1, 1))
    d.declare("eligibility", "issue", "criterion_not_met")


def criterion_not_met_in_alt_unit(d: Draft, rng: random.Random) -> None:
    d.tag("unit")
    parameter = d.simple_parameters(rng, alt_unit=True)
    a = d.assessment(parameter)
    a.value, a.unit = d.in_alt_unit(parameter, d.failing(rng, parameter, steps=(3, 12)))
    a.source = "central_lab"
    d.declare("eligibility", "issue", "criterion_not_met")


def amendment_enrolled_before(d: Draft, rng: random.Random) -> None:
    d.tag("amendment")
    parameter, value = _between_amendment_limits(d, rng)
    d.assessment(parameter).value = value
    d.declare("eligibility", "issue", "criterion_not_met")


def overlapping_criteria(d: Draft, rng: random.Random) -> None:
    d.tag("overlap")
    spec = d.spec(OVERLAP_PARAMETER)
    wide = next(c for c in d.criteria() if c.parameter == OVERLAP_PARAMETER and c.eligible_if.maximum != OVERLAP_MAX)
    assert wide.eligible_if.maximum is not None
    d.assessment(OVERLAP_PARAMETER).value = rng.choice(
        d._grid(spec, OVERLAP_MAX + 2 * spec.step, wide.eligible_if.maximum - 2 * spec.step)
    )
    d.declare("eligibility", "issue", "criterion_not_met")


def assessment_outside_window(d: Draft, rng: random.Random) -> None:
    window = timedelta(days=d.study.protocol.screening_window_days + rng.randrange(1, 11))
    latest = max(a.day for a in d.assessments)
    zone = d.enrollment.at.tzinfo
    target = datetime.combine(latest + window, d.enrollment.at.time(), zone)
    d.shift_after_screening(target - d.enrollment.at)
    d.declare("eligibility", "issue", "assessment_outside_window")


def assessment_after_enrollment(d: Draft, rng: random.Random) -> None:
    parameter = d.simple_parameters(rng)
    d.assessment(parameter).day = d.enrollment.at.date() + timedelta(days=rng.randrange(1, 4))
    d.declare("eligibility", "issue", "assessment_after_enrollment")


def consent_after_procedure(d: Draft, rng: random.Random) -> None:
    if rng.random() < 0.5:
        d.set_consent_time(d.screening.at + timedelta(minutes=rng.randrange(30, 301)))
    else:
        d.set_consent_time(d.screening.at + timedelta(days=rng.randrange(1, 3), minutes=rng.randrange(0, 120)))
    d.declare("consent", "issue", "consent_after_procedure")


def consent_superseded_version(d: Draft, rng: random.Random) -> None:
    d.consent.version = "1.0"
    d.declare("consent", "issue", "consent_version_not_current")


def consent_signature_incomplete(d: Draft, rng: random.Random) -> None:
    d.consent.investigator_signed = None
    d.declare("consent", "issue", "consent_signature_incomplete")


def note_reveals_procedure(d: Draft, rng: random.Random) -> None:
    d.tag("text_dependent")
    signed = d.consent.participant_signed
    assert isinstance(signed, datetime)
    performed = signed - timedelta(minutes=rng.randrange(20, 91))
    text = rng.choice((
        "Monitoring visit note: source shows the screening ECG was recorded at {t} on {day}, before the consent form was signed.",  # noqa: E501
        "Source review: fasting blood sample for the study was drawn at {t} on {day}; the consent form was signed later that day.",  # noqa: E501
    )).format(t=performed.strftime("%H:%M"), day=performed.date().isoformat())  # fmt: skip
    d.add_note(DNote(d.enrollment.at.date(), "monitor", _fixed(text),
                     meaning="procedure_before_consent", occurred=performed))  # fmt: skip
    d.declare("consent", "issue", "consent_after_procedure")


def timezone_consent_after(d: Draft, rng: random.Random) -> None:
    """The procedure is logged in UTC: its clock time reads later than consent, but it happened earlier."""
    d.tag("timezone")
    zone = d.consent.participant_signed.tzinfo  # type: ignore[union-attr]
    day = d.screening.at.date()
    consent_at = datetime.combine(day, time(rng.randrange(8, 11), rng.randrange(0, 60)), zone)
    d.set_consent_time(consent_at)
    d.screening.at = (consent_at - timedelta(minutes=rng.randrange(15, 46))).astimezone(UTC)
    d.screening.description = "Screening ECG upload (time recorded by the central system in UTC)"
    d.declare("consent", "issue", "consent_after_procedure")


def double_issue(d: Draft, rng: random.Random) -> None:
    d.tag("multi_finding")
    criterion_not_met(d, rng)
    consent_after_procedure(d, rng)


# -- ambiguous -------------------------------------------------------------


def assessment_missing(d: Draft, rng: random.Random) -> None:
    parameter = d.simple_parameters(rng)
    d.assessments.remove(d.assessment(parameter))
    d.declare("eligibility", "missing", "required_assessment_missing")


def unit_missing(d: Draft, rng: random.Random) -> None:
    d.tag("unit")
    parameter = d.simple_parameters(rng, alt_unit=True)
    d.assessment(parameter).unit = None
    d.declare("eligibility", "missing", "result_unusable")


def unit_unlisted(d: Draft, rng: random.Random) -> None:
    d.tag("unit")
    parameter = d.simple_parameters(rng, alt_unit=True)
    d.assessment(parameter).unit = d.spec(parameter).unlisted_unit
    d.declare("eligibility", "missing", "result_unusable")


def conflicting_results(d: Draft, rng: random.Random) -> None:
    parameter = d.simple_parameters(rng)
    good = d.assessment(parameter)
    good.source = "central_lab"
    d.assessments.append(DAssessment(parameter, d.failing(rng, parameter), good.unit, good.day, "site"))
    d.declare("eligibility", "conflict", "conflicting_results")


def consent_record_missing(d: Draft, rng: random.Random) -> None:
    d.consents.clear()
    d.declare("consent", "missing", "consent_record_missing")


def consent_unverified(d: Draft, rng: random.Random) -> None:
    if rng.random() < 0.5:
        d.consent.on_file, d.consent.status = False, "not_available"
    else:
        d.consent.status = "pending"
    d.declare("consent", "missing", "consent_unverified")


def consent_same_day_no_time(d: Draft, rng: random.Random) -> None:
    d.set_consent_time(d.screening.at.date())
    d.declare("consent", "missing", "consent_order_undetermined")


def consent_timestamp_conflict(d: Draft, rng: random.Random) -> None:
    later = d.screening.at + timedelta(minutes=rng.randrange(60, 301))
    d.consents.append(DConsent(d.consent.version, later, later + timedelta(minutes=10)))
    d.declare("consent", "conflict", "consent_timestamp_conflict")


def reconsent_missing(d: Draft, rng: random.Random) -> None:
    d.declare("consent", "missing", "reconsent_record_missing")


def note_contradicts_assessment(d: Draft, rng: random.Random) -> None:
    d.tag("text_dependent")
    parameter = d.simple_parameters(rng)
    a = d.assessment(parameter)
    spec = d.spec(parameter)
    other = _fmt(d, parameter, d.failing(rng, parameter))
    template = rng.choice((
        "Source worksheet for {label} reads {other} {unit}, but entry {ref} shows a different value. Discrepancy not yet resolved.",  # noqa: E501
        "Query open: the lab printout lists {label} as {other} {unit}; this does not match {ref}. Awaiting site response.",  # noqa: E501
    ))  # fmt: skip
    d.add_note(DNote(a.day + timedelta(days=2), "monitor",
                     lambda refs: template.format(label=spec.label, other=other, unit=spec.unit, ref=refs[id(a)]),
                     meaning="contradicts_assessment", target=a, parameter=parameter))  # fmt: skip
    d.declare("eligibility", "conflict", "note_contradicts_record")


def mixed_missing(d: Draft, rng: random.Random) -> None:
    d.tag("multi_finding")
    unit_missing(d, rng)
    consent_same_day_no_time(d, rng)


SCENARIOS: tuple[Scenario, ...] = (
    Scenario("plain_compliant", "routine", 86, plain_compliant, summary="Complete, consistent, compliant record."),
    Scenario("boundary_at_limit", "routine", 14, boundary_at_limit, phase="early",
             summary="A value exactly at an inclusive limit, or results on the first day of the screening window."),
    Scenario("screen_failure_not_enrolled", "routine", 12, screen_failure_not_enrolled,
             summary="A failing result for a participant who was correctly not enrolled."),
    Scenario("retest_in_window", "routine", 12, retest_in_window,
             summary="A failing result followed by a passing repeat before enrollment."),
    Scenario("alternate_unit_in_range", "routine", 12, alternate_unit_in_range,
             summary="A result in an accepted alternative unit that converts to an eligible value."),
    Scenario("amendment_enrolled_after", "routine", 10, amendment_enrolled_after, phase="late", needs=("amendment",),
             summary="A value that meets the amended limit, enrolled after the amendment took effect."),
    Scenario("reconsent_done", "routine", 10, reconsent_done, phase="bridge", needs=("reconsent",),
             summary="Two consent records: the original version and a required re-consent."),
    Scenario("same_day_consent_first", "routine", 10, same_day_consent_first,
             summary="Consent and first procedure on the same day, consent first by minutes."),
    Scenario("timezone_consent_first", "routine", 8, timezone_consent_first, site="east",
             summary="Procedure time recorded in UTC reads earlier than consent but happened later."),
    Scenario("note_documents_retest", "routine", 10, note_documents_retest,
             summary="A failing structured result; the passing repeat is documented only in a note."),
    Scenario("note_resolves_duplicate", "routine", 8, note_resolves_duplicate,
             summary="Two contradictory same-day results; a note voids the wrong one."),
    Scenario("note_clarifies_consent_time", "routine", 8, note_clarifies_consent_time,
             summary="Consent date without a time; a note records that signing preceded the procedure."),
    Scenario("criterion_not_met", "issue", 10, criterion_not_met,
             summary="Governing result outside a criterion limit; participant enrolled."),
    Scenario("criterion_just_outside", "issue", 10, criterion_just_outside,
             summary="Governing result one measurement step outside a limit."),
    Scenario("criterion_not_met_in_alt_unit", "issue", 10, criterion_not_met_in_alt_unit,
             summary="A result in an accepted alternative unit that converts to an ineligible value."),
    Scenario("amendment_enrolled_before", "issue", 8, amendment_enrolled_before, phase="early", needs=("amendment",),
             summary="A value that meets only the amended limit, enrolled before the amendment took effect."),
    Scenario("overlapping_criteria", "issue", 8, overlapping_criteria, needs=("overlap",),
             summary="A value inside one criterion's range but outside a stricter overlapping criterion."),
    Scenario("assessment_outside_window", "issue", 8, assessment_outside_window, phase="early",
             summary="Governing results collected earlier than the screening window allows."),
    Scenario("assessment_after_enrollment", "issue", 6, assessment_after_enrollment,
             summary="A required result collected only after enrollment."),
    Scenario("consent_after_procedure", "issue", 12, consent_after_procedure,
             summary="Consent signed after the first study-specific procedure."),
    Scenario("consent_superseded_version", "issue", 8, consent_superseded_version, phase="late", needs=("icf2",),
             summary="Consent signed on a superseded form version."),
    Scenario("consent_signature_incomplete", "issue", 6, consent_signature_incomplete,
             summary="Verified consent form on file without the investigator signature."),
    Scenario("note_reveals_procedure", "issue", 8, note_reveals_procedure,
             summary="Structured record looks compliant; a note documents a procedure before consent."),
    Scenario("timezone_consent_after", "issue", 4, timezone_consent_after, site="west",
             summary="Procedure time recorded in UTC reads later than consent but happened earlier."),
    Scenario("double_issue", "issue", 2, double_issue,
             summary="An eligibility limit not met and consent after the first procedure."),
    Scenario("assessment_missing", "ambiguous", 10, assessment_missing,
             summary="No result for a required assessment."),
    Scenario("unit_missing", "ambiguous", 10, unit_missing, summary="A result recorded without a unit."),
    Scenario("unit_unlisted", "ambiguous", 6, unit_unlisted,
             summary="A result in a unit the protocol does not list."),
    Scenario("conflicting_results", "ambiguous", 12, conflicting_results,
             summary="Two same-day results, one eligible and one not, with nothing to resolve them."),
    Scenario("consent_record_missing", "ambiguous", 12, consent_record_missing,
             summary="Study activity with no consent record. Not proof that consent did not occur."),
    Scenario("consent_unverified", "ambiguous", 10, consent_unverified,
             summary="Consent form not on file, or verification pending."),
    Scenario("consent_same_day_no_time", "ambiguous", 10, consent_same_day_no_time,
             summary="Consent and first procedure on the same date; no signing time recorded."),
    Scenario("consent_timestamp_conflict", "ambiguous", 10, consent_timestamp_conflict,
             summary="Two records of the same consent, one before and one after the first procedure."),
    Scenario("reconsent_missing", "ambiguous", 8, reconsent_missing, phase="bridge", needs=("reconsent",),
             summary="Required re-consent documentation absent after a later visit."),
    Scenario("note_contradicts_assessment", "ambiguous", 8, note_contradicts_assessment,
             summary="A note reports a source value that contradicts the structured result."),
    Scenario("mixed_missing", "ambiguous", 4, mixed_missing,
             summary="A result without a unit, and consent timing that cannot be ordered."),
)  # fmt: skip
SCENARIO_BY_NAME = {s.name: s for s in SCENARIOS}
