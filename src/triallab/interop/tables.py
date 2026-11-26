"""Export the synthetic cases as tables that clinical data tools can read.

These tools answer different questions from the triage benchmark, so their
output is never ranked against a decision model:

- CDISC CORE and pharmaverse sdtmchecks check the structure and consistency of
  SDTM-shaped tables (here: minimal DM and DS).
- OpenRBQM / Good Statistical Monitoring computes site-level risk indicators
  (here: the inputs for a screen-failure-rate indicator).

The export is implemented and tested. Running those tools is optional, needs
software that is not bundled with this project, and has not been done by us.
See docs/CLINICAL-TOOLS.md.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from triallab.clinical.rules import first_procedure, signed_consents
from triallab.schema import Case

DM_COLUMNS = ("STUDYID", "DOMAIN", "USUBJID", "SUBJID", "SITEID", "RFICDTC", "AGE", "AGEU")
DS_COLUMNS = ("STUDYID", "DOMAIN", "USUBJID", "DSSEQ", "DSTERM", "DSDECOD", "DSCAT", "DSSTDTC")
ENROLL_COLUMNS = ("studyid", "invid", "subjid", "enrollyn", "sfreason")
DISPOSITION = {
    "enrollment": ("ENROLLED", "PROTOCOL MILESTONE"),
    "randomization": ("RANDOMIZED", "PROTOCOL MILESTONE"),
    "screen_failure": ("SCREEN FAILURE", "DISPOSITION EVENT"),
}


def dm_rows(cases: list[Case]) -> list[dict[str, Any]]:
    rows = []
    for case in cases:
        protocol, record = case.packet.protocol, case.packet.record
        signed = signed_consents(record)
        age = next((a.value for a in record.assessments if a.parameter == "age"), None)
        rows.append({
            "STUDYID": protocol.study_id, "DOMAIN": "DM", "USUBJID": f"{protocol.study_id}-{record.participant_id}",
            "SUBJID": record.participant_id, "SITEID": record.site_id,
            "RFICDTC": signed[0].participant_signed if signed else "", "AGE": "" if age is None else int(age),
            "AGEU": "" if age is None else "YEARS",
        })  # fmt: skip
    return rows


def ds_rows(cases: list[Case]) -> list[dict[str, Any]]:
    rows = []
    for case in cases:
        protocol, record = case.packet.protocol, case.packet.record
        usubjid = f"{protocol.study_id}-{record.participant_id}"
        entries = [
            ("INFORMED CONSENT OBTAINED", "PROTOCOL MILESTONE", c.participant_signed) for c in signed_consents(record)
        ]
        entries += [(*DISPOSITION[e.type], e.occurred) for e in record.events if e.type in DISPOSITION]
        for seq, (decod, category, when) in enumerate(sorted(entries, key=lambda x: str(x[2])), 1):
            rows.append({"STUDYID": protocol.study_id, "DOMAIN": "DS", "USUBJID": usubjid, "DSSEQ": seq,
                         "DSTERM": decod.title(), "DSDECOD": decod, "DSCAT": category, "DSSTDTC": when})  # fmt: skip
    return rows


def enroll_rows(cases: list[Case]) -> list[dict[str, Any]]:
    """One row per screened participant, in the shape risk-based monitoring tools use for screen-failure rates."""
    rows = []
    for case in cases:
        record = case.packet.record
        if first_procedure(record) is None:
            continue
        types = {e.type for e in record.events}
        enrolled = "enrollment" in types
        rows.append({"studyid": case.packet.protocol.study_id, "invid": record.site_id, "subjid": record.participant_id,
                     "enrollyn": "Y" if enrolled else "N",
                     "sfreason": "" if enrolled else "Inclusion/Exclusion Criteria"})  # fmt: skip
    return rows


def write_tables(cases: list[Case], out_dir: Path) -> dict[str, int]:
    out_dir.mkdir(parents=True, exist_ok=True)
    tables = {"dm.csv": (DM_COLUMNS, dm_rows(cases)), "ds.csv": (DS_COLUMNS, ds_rows(cases)),
              "enroll.csv": (ENROLL_COLUMNS, enroll_rows(cases))}  # fmt: skip
    for name, (columns, rows) in tables.items():
        with (out_dir / name).open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(columns))
            writer.writeheader()
            writer.writerows(rows)
    return {name: len(rows) for name, (_, rows) in tables.items()}
