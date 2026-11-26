"""`triallab demo`: the one-command offline tour.

Runs the deterministic rules and the two anchors on the frozen synthetic test
set, shows that two provider adapters build and parse requests against fixture
responses, and writes the plain HTML summary. No API keys, no downloads, no network.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from triallab.benchmark.runner import RunOptions, format_run_table, run_benchmark
from triallab.config import OUTPUTS
from triallab.datasets import load_dataset
from triallab.report.render import build_report


def run_demo(
    outputs: Path | None = None, resamples: int = 1_000, progress: Callable[[str], None] | None = None
) -> tuple[Path, Path]:
    outputs = outputs or OUTPUTS
    say = progress or (lambda _: None)
    ds = load_dataset("synthetic-v1")
    say(f"1/3 Rules and anchors on {len(ds.tasks)} synthetic test cases (offline)")
    run_dir, metrics = run_benchmark(
        ds, RunOptions(systems=["rules", "flag_all", "flag_none"], resamples=resamples), outputs=outputs
    )
    say(format_run_table(metrics))
    say("2/3 Dry run of two provider adapters on 20 cases (fixture responses; not a measurement)")
    _, dry = run_benchmark(
        ds, RunOptions(systems=["jev", "llm_openai"], dry_run=True, max_cases=20, resamples=50), outputs=outputs
    )
    for name, entry in dry["systems"].items():
        say(f"  {name}: request built and response parsed for {entry['statuses'].get('ok', 0)} of 20 cases")
    say("3/3 Plain HTML summary")
    report = build_report([run_dir.name], outputs / "demo-report.html", outputs=outputs)
    return run_dir, report
