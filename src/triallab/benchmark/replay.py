"""`triallab replay`: recompute a finished run's statistics from its raw files.

No system is called. The result must match the saved metrics.json exactly; any
difference is reported. Adapted from Fraud Decision Lab's `benchmark/replay.py`.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from triallab.benchmark.runner import compute_metrics, reference_from_row
from triallab.config import OUTPUTS
from triallab.core.ledger import Ledger
from triallab.core.provenance import file_hash, read_jsonl
from triallab.providers.base import Prediction


class ReplayError(RuntimeError):
    """The run folder is missing files or cannot be replayed."""


def load_run(run_id: str, outputs: Path | None = None) -> tuple[Path, dict[str, Any], dict[str, Any]]:
    out = (outputs or OUTPUTS) / run_id
    needed = ["metrics.json", "predictions.jsonl", "reference.jsonl", "manifest.json"]
    missing = [n for n in needed if not (out / n).is_file()]
    if missing:
        raise ReplayError(f"{out} is missing {', '.join(missing)}")
    manifest = json.loads((out / "manifest.json").read_text())
    if manifest.get("kind") != "run" or manifest.get("status") != "complete":
        raise ReplayError("only completed runs made by `triallab run` can be replayed")
    return out, manifest, json.loads((out / "metrics.json").read_text())


def replay_run(run_id: str, outputs: Path | None = None) -> tuple[dict[str, Any], dict[str, Any], list[str]]:
    out, manifest, saved = load_run(run_id, outputs)
    reference = [reference_from_row(row) for row in read_jsonl(out / "reference.jsonl")]
    by_system: dict[str, list[Prediction]] = {name: [] for name in manifest["run"]["systems"]}
    for row in read_jsonl(out / "predictions.jsonl"):
        if row["provider"] not in by_system:
            raise ReplayError(f"predictions contain a system that is not in the manifest: {row['provider']}")
        by_system[row["provider"]].append(Prediction(**row))
    ids = {r.case_id for r in reference}
    for name, preds in by_system.items():
        base = [p.case_id for p in preds if p.case_id in ids]
        if len(base) != len(set(base)) or set(base) != ids:
            raise ReplayError(f"predictions for {name} do not cover each reference case exactly once")
    again = compute_metrics(
        track=saved["track"], reference=reference, predictions=by_system, seed=saved["bootstrap"]["seed"],
        resamples=saved["bootstrap"]["resamples"], accounting=Ledger(out / "attempts.jsonl").summary().by_provider,
        timing=manifest["run"]["timing"], configs=manifest["identity"]["system_configs"],
    )  # fmt: skip
    differences = []
    hashes = manifest.get("artifacts_sha256", {})
    if any(not (out / name).is_file() or file_hash(out / name) != digest for name, digest in hashes.items()):
        differences.append("artifact fingerprints")
    accounting = Ledger(out / "attempts.jsonl").summary()
    budget = saved.get("budget", {})
    if not math.isclose(accounting.spent_usd, budget.get("spent_usd", 0.0), rel_tol=1e-12, abs_tol=1e-12):
        differences.append("budget accounting")
    for key in ("eval_version", "track", "scored_cases", "composition", "reference_system", "bootstrap", "systems"):
        if json.loads(json.dumps(again[key])) != saved[key]:
            differences.append(key)
    return saved, again, differences
