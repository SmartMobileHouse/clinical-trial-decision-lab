"""Building blocks for fictional study protocols: criteria, units, sites.

Everything here is invented for this benchmark. Parameters are generic
screening measurements; thresholds are picked from small fixed option lists.
No real protocol, sponsor, product, site or participant is represented.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from datetime import date, timedelta

from triallab.schema import ConsentVersion, Criterion, EligibleRange, Protocol, ProtocolVersion, UnitConversion


@dataclass(frozen=True)
class ParamSpec:
    parameter: str
    label: str
    unit: str
    step: float
    decimals: int
    kind: str  # "inclusion" or "exclusion"
    text: str  # uses {min} and {max}
    plausible: tuple[float, float]
    min_options: tuple[float, ...] = ()
    max_options: tuple[float, ...] = ()
    alt_units: tuple[UnitConversion, ...] = ()
    alt_decimals: int = 0
    unlisted_unit: str | None = None  # a real unit the protocol does not list (for "unknown unit" cases)


LIBRARY: dict[str, ParamSpec] = {
    p.parameter: p
    for p in (
        ParamSpec("age", "Age", "years", 1, 0, "inclusion", "Age {min} to {max} years inclusive at screening",
                  (18, 82), min_options=(18,), max_options=(65, 70, 75)),
        ParamSpec("egfr", "eGFR", "mL/min/1.73m2", 1, 0, "inclusion", "eGFR of at least {min} mL/min/1.73m2",
                  (20, 120), min_options=(30, 45, 60)),
        ParamSpec("alt", "ALT", "x ULN", 0.1, 1, "exclusion", "ALT greater than {max} x ULN (site ULN is 40 U/L)",
                  (0.3, 5.0), max_options=(2.0, 2.5, 3.0),
                  alt_units=(UnitConversion(unit="U/L", factor=0.025),), alt_decimals=0, unlisted_unit="ukat/L"),
        ParamSpec("hemoglobin", "Hemoglobin", "g/dL", 0.1, 1, "inclusion", "Hemoglobin of at least {min} g/dL",
                  (7.0, 16.5), min_options=(9.0, 10.0),
                  alt_units=(UnitConversion(unit="g/L", factor=0.1),), alt_decimals=0, unlisted_unit="mmol/L"),
        ParamSpec("platelets", "Platelet count", "10^9/L", 1, 0, "inclusion",
                  "Platelet count of at least {min} x 10^9/L", (40, 400), min_options=(75, 100),
                  alt_units=(UnitConversion(unit="/uL", factor=0.001),), alt_decimals=0,
                  unlisted_unit="% of baseline"),
        ParamSpec("hba1c", "HbA1c", "%", 0.1, 1, "inclusion", "HbA1c between {min}% and {max}% inclusive",
                  (5.0, 12.5), min_options=(6.5, 7.0), max_options=(10.0, 10.5),
                  alt_units=(UnitConversion(unit="mmol/mol", factor=0.09148, offset=2.152),), alt_decimals=0,
                  unlisted_unit="eAG mg/dL"),
        ParamSpec("bmi", "BMI", "kg/m2", 0.1, 1, "inclusion", "BMI between {min} and {max} kg/m2 inclusive",
                  (16.0, 45.0), min_options=(18.5,), max_options=(35.0, 40.0)),
        ParamSpec("sbp", "Systolic blood pressure", "mmHg", 1, 0, "exclusion",
                  "Systolic blood pressure above {max} mmHg", (95, 185), max_options=(150, 160)),
        ParamSpec("qtcf", "QTcF", "ms", 1, 0, "exclusion", "QTcF above {max} ms", (370, 500),
                  max_options=(450, 470)),
        ParamSpec("creatinine", "Serum creatinine", "mg/dL", 0.1, 1, "exclusion",
                  "Serum creatinine above {max} mg/dL", (0.5, 3.0), max_options=(1.5, 2.0),
                  alt_units=(UnitConversion(unit="umol/L", factor=0.011312),), alt_decimals=0,
                  unlisted_unit="mmol/L"),
        ParamSpec("washout", "Days since last investigational product", "days", 1, 0, "inclusion",
                  "At least {min} days since the last dose of any other investigational product", (5, 400),
                  min_options=(28, 30)),
    )
}  # fmt: skip
ALT_UNIT_PARAMS = tuple(p for p, spec in LIBRARY.items() if spec.alt_units)
OVERLAP_PARAMETER = "bmi"
OVERLAP_MAX = 32.0

RETEST_POLICY = (
    "A screening assessment may be repeated once. The most recent result collected on or before the "
    "enrollment date governs eligibility. All governing results must be collected within the screening window."
)
CONSENT_POLICY = (
    "Written informed consent must be obtained on the consent form version in effect at the site on the "
    "signing date, signed by the participant and the investigator, before any study-specific procedure. "
    "When a new version requires re-consent, ongoing participants sign it at their next visit."
)

# Three sites per protocol: one west of UTC, one near UTC, one far east.
WEST_OFFSETS = ("-08:00", "-05:00", "-03:00")
NEAR_OFFSETS = ("+00:00", "+01:00", "+02:00")
EAST_OFFSETS = ("+08:00", "+09:00")


@dataclass(frozen=True)
class Site:
    site_id: str
    utc_offset: str


@dataclass(frozen=True)
class StudyDesign:
    """A fictional protocol plus the facts scenarios need to build cases on it."""

    protocol: Protocol
    start: date  # effective date of protocol version 1.0
    sites: tuple[Site, ...]
    amended_parameter: str | None = None
    amendment_date: date | None = None
    icf2_date: date | None = None
    reconsent_required: bool = False
    has_overlap: bool = False
    specs: dict[str, ParamSpec] = field(default_factory=dict)


def _fmt(value: float, decimals: int) -> str:
    return f"{value:.{decimals}f}"


def _criterion(ref: str, spec: ParamSpec, low: float | None, high: float | None, start: str, end: str | None):
    text = spec.text.format(
        min=_fmt(low, spec.decimals) if low is not None else "",
        max=_fmt(high, spec.decimals) if high is not None else "",
    )
    prefix = "Inclusion: " if spec.kind == "inclusion" else "Exclusion: "
    return Criterion(
        ref=ref, kind=spec.kind, text=prefix + text, parameter=spec.parameter, unit=spec.unit,
        eligible_if=EligibleRange(minimum=low, maximum=high), applies_from_version=start, applies_until_version=end,
    )  # fmt: skip


def build_study(rng: random.Random, index: int) -> StudyDesign:
    """One fictional study. `index` fixes which design features it has, so every scenario finds a home.

    index 0, 2, 4, 6: a protocol amendment relaxes one limit
    index 0, 1, 4, 5: a second consent form version exists (re-consent required for 0 and 1)
    index 4..7:      two criteria overlap on the same parameter
    """
    amended = index % 2 == 0
    icf2 = (index // 2) % 2 == 0
    reconsent = icf2 and index < 2
    overlap = index >= 4

    with_alt = rng.sample(ALT_UNIT_PARAMS, 2)
    forced = ["age", *with_alt] + ([OVERLAP_PARAMETER] if overlap else [])
    others = [p for p in LIBRARY if p not in forced]
    chosen = forced + rng.sample(others, 6 - len(forced))
    chosen.sort(key=list(LIBRARY).index)

    start = date(2024, 1, 1) + timedelta(days=rng.randrange(0, 300))
    amendable = [
        p
        for p in chosen
        if p != "age"
        and not (overlap and p == OVERLAP_PARAMETER)
        and max(len(LIBRARY[p].min_options), len(LIBRARY[p].max_options)) > 1
    ]
    amended_parameter = rng.choice(amendable) if amended else None

    criteria: list[Criterion] = []
    number = 0
    for parameter in chosen:
        spec = LIBRARY[parameter]
        number += 1
        if parameter == amended_parameter:
            # Version 1.0 uses the strictest limit, version 2.0 the most relaxed one.
            old: tuple[float | None, float | None]
            new: tuple[float | None, float | None]
            if len(spec.max_options) > 1:
                low = spec.min_options[-1] if spec.min_options else None
                old, new = (low, spec.max_options[0]), (low, spec.max_options[-1])
            else:
                high = spec.max_options[0] if spec.max_options else None
                old, new = (spec.min_options[-1], high), (spec.min_options[0], high)
            criteria.append(_criterion(f"CRIT-{number:02d}", spec, old[0], old[1], "1.0", "2.0"))
            criteria.append(_criterion(f"CRIT-{number:02d}A", spec, new[0], new[1], "2.0", None))
        else:
            low = rng.choice(spec.min_options) if spec.min_options else None
            high = rng.choice(spec.max_options) if spec.max_options else None
            criteria.append(_criterion(f"CRIT-{number:02d}", spec, low, high, "1.0", None))
    if overlap:
        number += 1
        criteria.append(
            Criterion(
                ref=f"CRIT-{number:02d}",
                kind="exclusion",
                parameter=OVERLAP_PARAMETER,
                unit="kg/m2",
                text=f"Exclusion: BMI above {OVERLAP_MAX:.1f} kg/m2 (procedural sedation risk)",
                eligible_if=EligibleRange(maximum=OVERLAP_MAX),
                applies_from_version="1.0",
            )  # fmt: skip
        )

    versions = [ProtocolVersion(version="1.0", effective_date=start.isoformat())]
    amendment_date = None
    if amended_parameter:
        amendment_date = start + timedelta(days=180)
        spec = LIBRARY[amended_parameter]
        before = next(c for c in criteria if c.parameter == amended_parameter and c.applies_until_version == "2.0")
        after = next(c for c in criteria if c.parameter == amended_parameter and c.applies_from_version == "2.0")
        changed = "maximum" if before.eligible_if.maximum != after.eligible_if.maximum else "minimum"
        versions.append(
            ProtocolVersion(
                version="2.0",
                effective_date=amendment_date.isoformat(),
                summary_of_changes=(
                    f"Amendment 1: {spec.label} {changed} limit changed from "
                    f"{_fmt(getattr(before.eligible_if, changed), spec.decimals)} to "
                    f"{_fmt(getattr(after.eligible_if, changed), spec.decimals)} {spec.unit}. "
                    "Applies to participants enrolled on or after the effective date."
                ),
            )
        )

    consent_versions = [
        ConsentVersion(
            ref="ICFV-1",
            version="1.0",
            irb_approval_date=(start - timedelta(days=30)).isoformat(),
            site_effective_date=(start - timedelta(days=14)).isoformat(),
        )  # fmt: skip
    ]
    icf2_date = None
    if icf2:
        icf2_date = start + timedelta(days=185)
        consent_versions.append(
            ConsentVersion(
                ref="ICFV-2",
                version="2.0",
                irb_approval_date=(start + timedelta(days=170)).isoformat(),
                site_effective_date=icf2_date.isoformat(),
                reconsent_required=reconsent,
            )  # fmt: skip
        )

    study_id = "STUDY-" + "".join(rng.choice("ABCDEFGHJKLMNPQRSTUVWXYZ23456789") for _ in range(4))
    numbers = rng.sample(range(10, 100), 3)
    sites = (
        Site(f"SITE-{numbers[0]}", rng.choice(WEST_OFFSETS)),
        Site(f"SITE-{numbers[1]}", rng.choice(NEAR_OFFSETS)),
        Site(f"SITE-{numbers[2]}", rng.choice(EAST_OFFSETS)),
    )
    protocol = Protocol(
        study_id=study_id,
        versions=versions,
        criteria=criteria,
        accepted_units={p: list(LIBRARY[p].alt_units) for p in chosen if LIBRARY[p].alt_units},
        screening_window_days=rng.choice((21, 28, 35)),
        retest_policy=RETEST_POLICY,
        consent_policy=CONSENT_POLICY,
        consent_versions=consent_versions,
    )
    return StudyDesign(
        protocol=protocol, start=start, sites=sites, amended_parameter=amended_parameter,
        amendment_date=amendment_date, icf2_date=icf2_date, reconsent_required=reconsent, has_overlap=overlap,
        specs={p: LIBRARY[p] for p in chosen},
    )  # fmt: skip
