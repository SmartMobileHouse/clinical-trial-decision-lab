"""Evidence export and the plain report: publication gates and no invented numbers."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from test_runner import _regulatory_folder
from typer.testing import CliRunner

from triallab.benchmark.runner import RunOptions, run_benchmark
from triallab.cli import app
from triallab.datasets import load_dataset
from triallab.demo import run_demo
from triallab.report.export import NOT_RUN, RestrictedDatasetError, export_report_data
from triallab.report.render import build_report


def test_bundle_contains_measured_local_systems_and_no_dry_run_numbers(tmp_path: Path) -> None:
    ds = load_dataset("synthetic-v1")
    out, _ = run_benchmark(
        ds,
        RunOptions(systems=["rules", "flag_all", "flag_none", "mock", "jev"], dry_run=True, resamples=20),
        outputs=tmp_path,
    )
    bundle = json.loads(export_report_data([out.name], tmp_path / "bundle.json", outputs=tmp_path).read_text())
    exp = bundle["experiments"]["synthetic_v1_test"]
    assert bundle["schema"] == "smh-research-data/1" and exp["dataset"]["external_processing_allowed"] is True
    assert exp["measured_systems"] == ["rules", "flag_all", "flag_none"] and "mock" not in exp["models"]
    assert exp["models"]["rules"]["status"] == "ok" and "quality" in exp["models"]["rules"]
    jev = exp["models"]["jev"]
    assert jev["status"] == NOT_RUN and "quality" not in jev and "performance" not in jev
    assert exp["models"]["nimble"]["status"] == NOT_RUN and "terms" in exp["models"]["nimble"]["reason"]
    assert bundle["tracks"]["regulatory"]["status"] == "withheld"
    providers = {p["provider"] for p in exp["verification"]["predictions"]}
    assert providers == {"rules", "flag_all", "flag_none"}  # no fixture answers leave the run folder
    assert len(exp["verification"]["reference"]) == 400
    assert len(bundle["model_register"]) == 19


def test_unapproved_dataset_is_refused_before_anything_is_written(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("TRIALLAB_RESTRICTED_DATA", str(_regulatory_folder(tmp_path)))
    out, _ = run_benchmark(
        load_dataset("fda-findings-v1"), RunOptions(systems=["keyword"], resamples=10), outputs=tmp_path
    )
    target = tmp_path / "bundle.json"
    with pytest.raises(RestrictedDatasetError, match="not approved for publication"):
        export_report_data([out.name], target, outputs=tmp_path)
    with pytest.raises(RestrictedDatasetError):
        build_report([out.name], tmp_path / "report.html", outputs=tmp_path)
    assert not target.exists() and not (tmp_path / "report.html").exists()


def test_demo_builds_a_report_with_statuses_not_placeholder_numbers(tmp_path: Path) -> None:
    run_dir, report = run_demo(outputs=tmp_path, resamples=20)
    html = report.read_text()
    assert run_dir.name in html and "Deterministic protocol rules" in html
    assert "not run" in html and "paid API run not executed yet" in html
    assert "Withheld" in html and "REG-" not in html and "http://" not in html.replace("http://www.w3.org", "")


def test_cli_smoke(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    runner = CliRunner()
    assert runner.invoke(app, ["version"]).exit_code == 0
    listing = runner.invoke(app, ["models"])
    assert listing.exit_code == 0 and "jev-1.14.0" in listing.output
    assert runner.invoke(app, ["data", "verify"]).exit_code == 0
    refused = runner.invoke(app, ["run", "-s", "jev"])
    assert refused.exit_code == 1 and "Refused" in refused.output
    monkeypatch.setenv("TYPESAFE_API_KEY", "secret-value-123456")
    doctor = runner.invoke(app, ["doctor"])
    assert doctor.exit_code == 0 and "secret-value-123456" not in doctor.output and "19 characters" in doctor.output
