"""The runner end to end, offline: local systems, dry runs, gates, resume and replay."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from triallab.benchmark.replay import ReplayError, replay_run
from triallab.benchmark.runner import RunOptions, RunRefused, format_run_table, run_benchmark
from triallab.core.provenance import read_jsonl
from triallab.datasets import DatasetError, load_dataset


@pytest.fixture(scope="module")
def dataset():
    return load_dataset("synthetic-v1")


def test_offline_run_writes_raw_and_processed_files_and_replays_exactly(dataset, tmp_path: Path) -> None:
    out, metrics = run_benchmark(
        dataset, RunOptions(systems=["rules", "flag_all", "flag_none", "mock"], resamples=30), outputs=tmp_path
    )
    assert {p.name for p in out.iterdir()} >= {"manifest.json", "metrics.json", "predictions.jsonl", "reference.jsonl"}
    assert metrics["scored_cases"] == 400 and metrics["reference_system"] == "rules"
    rules = metrics["systems"]["rules"]
    assert rules["measurement"] is True and rules["coverage"] == 1.0
    assert rules["quality"]["strata"]["evidence:structured"]["case_accuracy"] == 1.0
    assert rules["performance"]["cost"]["basis"] == "local, no API cost"
    assert metrics["systems"]["mock"]["measurement"] is False
    assert metrics["systems"]["flag_none"]["quality"]["critical_recall"] == 0.0
    assert metrics["systems"]["flag_all"]["quality"]["critical_recall"] == 1.0
    assert "difference_vs_reference_95" in metrics["systems"]["flag_all"]
    assert metrics["systems"]["flag_all"]["paired_vs_reference"]["second"] == "rules"
    saved, again, differences = replay_run(out.name, outputs=tmp_path)
    assert differences == [] and "rules" in format_run_table(again)
    manifest = json.loads((out / "manifest.json").read_text())
    assert manifest["status"] == "complete" and manifest["identity"]["questions"]["version"] == "v1"


def test_replay_detects_tampering(dataset, tmp_path: Path) -> None:
    out, _ = run_benchmark(dataset, RunOptions(systems=["rules"], max_cases=30, resamples=10), outputs=tmp_path)
    rows = read_jsonl(out / "predictions.jsonl")
    rows[0]["answers"]["eligibility_issue"] = not rows[0]["answers"]["eligibility_issue"]
    (out / "predictions.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
    _, _, differences = replay_run(out.name, outputs=tmp_path)
    assert "artifact fingerprints" in differences and "systems" in differences
    with pytest.raises(ReplayError):
        replay_run("no-such-run", outputs=tmp_path)


def test_live_runs_need_explicit_flags_and_keys(dataset, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("triallab.benchmark.runner.load_env", lambda: False)
    monkeypatch.delenv("TYPESAFE_API_KEY", raising=False)
    with pytest.raises(RunRefused, match="allow-external-requests"):
        run_benchmark(dataset, RunOptions(systems=["jev"]), outputs=tmp_path)
    with pytest.raises(RunRefused, match="max-cost-usd"):
        run_benchmark(dataset, RunOptions(systems=["jev"], allow_external_requests=True), outputs=tmp_path)
    with pytest.raises(RunRefused, match="TYPESAFE_API_KEY"):
        run_benchmark(
            dataset,
            RunOptions(systems=["jev"], allow_external_requests=True, max_cost_usd=1.0, max_cases=2),
            outputs=tmp_path,
        )
    with pytest.raises(RunRefused, match="disabled"):
        run_benchmark(dataset, RunOptions(systems=["nimble"], dry_run=True), outputs=tmp_path)
    with pytest.raises(RunRefused, match="unknown"):
        run_benchmark(dataset, RunOptions(systems=["gpt-9"]), outputs=tmp_path)


def test_dry_run_exercises_adapters_and_is_never_a_measurement(dataset, tmp_path: Path) -> None:
    out, metrics = run_benchmark(
        dataset,
        RunOptions(
            systems=["rules", "jev", "llm_anthropic", "jev_via_opper"],
            dry_run=True,
            max_cases=12,
            repeats=2,
            resamples=10,
        ),
        outputs=tmp_path,
    )
    assert "dryrun" in out.name
    for name in ("jev", "llm_anthropic", "jev_via_opper"):
        entry = metrics["systems"][name]
        assert entry["execution"] == "dry_run" and entry["measurement"] is False and entry["coverage"] == 1.0
        assert entry["performance"]["cost"]["total_usd"] == 0.0
        assert entry["stability"]["repeats"] == 2 and entry["stability"]["changed_rate"] == 0.0
    assert metrics["systems"]["jev"]["probability"] is not None
    assert metrics["systems"]["llm_anthropic"]["probability"] is None  # an LLM's yes/no gets no invented probabilities
    assert len(read_jsonl(out / "predictions.jsonl")) == 12 + 3 * 24
    assert replay_run(out.name, outputs=tmp_path)[2] == []


def test_selective_execution_by_category(dataset, tmp_path: Path) -> None:
    _, metrics = run_benchmark(
        dataset, RunOptions(systems=["rules"], categories=["issue"], resamples=10), outputs=tmp_path
    )
    assert metrics["scored_cases"] == 100 and metrics["composition"]["by_category"] == {"issue": 100}
    with pytest.raises(RunRefused, match="unknown scenario category"):
        run_benchmark(dataset, RunOptions(systems=["rules"], categories=["nope"]), outputs=tmp_path)


def test_resume_reuses_answers_and_refuses_changed_inputs(dataset, tmp_path: Path) -> None:
    opts = RunOptions(systems=["jev"], dry_run=True, max_cases=8, resamples=10)
    out, first = run_benchmark(dataset, opts, outputs=tmp_path)
    attempts = len((out / "attempts.jsonl").read_text().splitlines())
    _, second = run_benchmark(
        dataset,
        RunOptions(systems=["jev"], dry_run=True, max_cases=8, resamples=10, resume_run_id=out.name),
        outputs=tmp_path,
    )
    assert len((out / "attempts.jsonl").read_text().splitlines()) == attempts  # nothing was sent again
    assert second["systems"]["jev"]["quality"] == first["systems"]["jev"]["quality"]
    with pytest.raises(RunRefused, match="differ"):
        run_benchmark(
            dataset,
            RunOptions(systems=["jev"], dry_run=True, max_cases=9, resamples=10, resume_run_id=out.name),
            outputs=tmp_path,
        )


def _regulatory_folder(tmp_path: Path) -> Path:
    folder = tmp_path / "restricted" / "fda-findings-v1"
    folder.mkdir(parents=True)
    cases = [
        {
            "case_id": "REG-001",
            "finding_text": "Fictional test text: a subject was enrolled without meeting inclusion criteria.",
        },
        {"case_id": "REG-002", "finding_text": "Fictional test text: the consent form was signed after the procedure."},
        {"case_id": "REG-003", "finding_text": "Fictional test text: drug accountability records were incomplete."},
    ]
    answers = [(True, False, "eligibility"), (False, True, "consent"), (False, False, "contrast")]
    reference = [
        {
            "case_id": c["case_id"],
            "answers": {"eligibility_issue": e, "consent_issue": k},
            "category": g,
            "issue_category": g,
        }
        for c, (e, k, g) in zip(cases, answers, strict=True)
    ]
    (folder / "test.cases.jsonl").write_text("".join(json.dumps(r) + "\n" for r in cases))
    (folder / "test.reference.jsonl").write_text("".join(json.dumps(r) + "\n" for r in reference))
    return folder.parent


def test_restricted_dataset_is_never_sent_to_a_provider(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TRIALLAB_RESTRICTED_DATA", raising=False)
    with pytest.raises(DatasetError, match="not distributed"):
        load_dataset("fda-findings-v1")
    monkeypatch.setenv("TRIALLAB_RESTRICTED_DATA", str(_regulatory_folder(tmp_path)))
    ds = load_dataset("fda-findings-v1")
    assert ds.spec.external_processing_allowed is False and ds.spec.publication_allowed is False
    assert all(set(t.state) == {"document_type", "finding_text"} for t in ds.tasks)
    _, metrics = run_benchmark(
        ds, RunOptions(systems=["keyword", "jev"], allow_external_requests=True, max_cost_usd=5.0, resamples=10),
        outputs=tmp_path / "out",
    )  # fmt: skip
    assert metrics["track"] == "regulatory" and metrics["reference_system"] == "keyword"
    assert metrics["systems"]["jev"]["status"] == "permission_blocked" and metrics["systems"]["jev"]["coverage"] == 0.0
    assert metrics["systems"]["keyword"]["quality"]["case_accuracy"] == 1.0
