"""Tables for optional external clinical tools."""

from __future__ import annotations

import csv
from pathlib import Path

from triallab.interop.tables import DM_COLUMNS, write_tables
from triallab.synthetic.generate import load_cases, load_truth


def test_tables_are_consistent_with_the_cases(tmp_path: Path) -> None:
    cases = load_cases("test")
    truth = load_truth("test")
    counts = write_tables(cases, tmp_path)
    assert counts["dm.csv"] == 400 and counts["enroll.csv"] == 400
    dm = list(csv.DictReader((tmp_path / "dm.csv").open()))
    assert tuple(dm[0]) == DM_COLUMNS and len({row["USUBJID"] for row in dm}) == 400
    no_consent = sum(row["RFICDTC"] == "" for row in dm)
    assert no_consent == sum(t.scenario == "consent_record_missing" for t in truth.values())
    enroll = list(csv.DictReader((tmp_path / "enroll.csv").open()))
    assert sum(row["enrollyn"] == "N" for row in enroll) == sum(
        t.scenario == "screen_failure_not_enrolled" for t in truth.values()
    )
    ds = list(csv.DictReader((tmp_path / "ds.csv").open()))
    assert {row["DSDECOD"] for row in ds} == {"INFORMED CONSENT OBTAINED", "ENROLLED", "RANDOMIZED", "SCREEN FAILURE"}
    text = (tmp_path / "dm.csv").read_text() + (tmp_path / "ds.csv").read_text()
    assert "scenario" not in text and "reference" not in text  # no labels leak into the tables
