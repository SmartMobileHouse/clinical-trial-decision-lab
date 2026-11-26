"""`triallab run`: answer one dataset split with any mix of systems and save everything.

Systems: local ones (`rules`, `keyword`, `flag_all`, `flag_none`, `mock`) and the
models enabled in configs/models.yaml.

Safety (same model as Fraud Decision Lab's runner, from which this is adapted):
- live providers need --allow-external-requests, --max-cost-usd and keys;
- `--dry-run` uses fixture responses and needs none of them; its answers are not measurements;
- a dataset with external_processing_allowed: false is never sent: every case is
  recorded as permission_blocked, whatever the flags say;
- an estimated spending guard, and a call log that reuses compatible successful answers on resume.

Raw results (attempts.jsonl, predictions.jsonl) are kept separate from processed
statistics (metrics.json). `triallab replay` recomputes the statistics from the raw files.
"""

from __future__ import annotations

import asyncio
import hashlib
import platform
import subprocess
import time
from collections import Counter
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx
import numpy as np

from triallab import __version__
from triallab.clinical.rules import RULES_VERSION
from triallab.config import MODEL_REGISTRY, OUTPUTS, REPO_ROOT, load_env
from triallab.core.budget import Budget
from triallab.core.ledger import Ledger, prediction_costs
from triallab.core.provenance import atomic_json, atomic_jsonl, file_hash, json_hash, run_lock, source_hash
from triallab.core.validation import finite_number, positive_integer, validate_names
from triallab.datasets import RENDER_VERSION, Dataset
from triallab.evaluate.decision import (
    EVAL_VERSION,
    ReferenceCase,
    SystemAnswer,
    build_table,
    finding_metrics,
    triage_metrics,
)
from triallab.evaluate.probability import probability_metrics
from triallab.evaluate.statistics import DEFAULT_RESAMPLES, answer_stability, mcnemar_exact, paired_bootstrap
from triallab.providers.adapters import ConfiguredProvider
from triallab.providers.base import DecisionProvider, MissingCredentials, Prediction, Task, blank_prediction
from triallab.providers.fixture import fixture_transport
from triallab.providers.registry import OFFLINE_SYSTEMS, make_local, make_remote, worst_case_cost
from triallab.providers.spec import Registry, load_registry
from triallab.questions import QUESTIONS_PATH

REFERENCE_SYSTEM = {"synthetic": "rules", "regulatory": "keyword"}
REPEAT_MARK = "#r"


class RunRefused(RuntimeError):
    """The run was not allowed to start. The message says why and how to fix it."""


@dataclass
class RunOptions:
    systems: list[str]
    allow_external_requests: bool = False
    dry_run: bool = False
    max_cost_usd: float | None = None
    concurrency: int = 4  # calls in flight per provider
    rate_per_s: float = 2.0  # max new calls per second per provider
    max_cases: int | None = None  # a seeded sample (smoke runs)
    categories: list[str] | None = None  # run only these scenario categories
    repeats: int = 1  # remote systems only: repeat every case to measure answer stability
    resamples: int = DEFAULT_RESAMPLES
    seed: int = 42
    resume_run_id: str | None = None
    progress: Callable[[str], None] | None = None


@dataclass
class _RateLimiter:
    rate_per_s: float
    _next: float = 0.0
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock)

    async def wait(self) -> None:
        async with self._lock:
            now = time.monotonic()
            start = max(now, self._next)
            self._next = start + 1.0 / self.rate_per_s
        if start > now:
            await asyncio.sleep(start - now)


def git_state() -> dict[str, Any]:
    def git(*args: str) -> str:
        try:
            return subprocess.run(  # noqa: S603
                ["git", *args],  # noqa: S607 - git from PATH is intended
                cwd=REPO_ROOT, capture_output=True, text=True, check=False,
            ).stdout.strip()  # fmt: skip
        except OSError:
            return ""

    return {"commit": git("rev-parse", "HEAD") or None, "uncommitted_changes": bool(git("status", "--porcelain"))}


def _validate(opts: RunOptions, registry: Registry) -> None:
    try:
        validate_names(opts.systems, (*OFFLINE_SYSTEMS, *[m.id for m in registry.models]))
        for name, value in (
            ("resamples", opts.resamples),
            ("concurrency", opts.concurrency),
            ("repeats", opts.repeats),
        ):
            positive_integer(value, name)
        if opts.concurrency > 64:
            raise ValueError("concurrency must be <= 64")
        if opts.repeats > 5:
            raise ValueError("repeats must be <= 5")
        finite_number(opts.rate_per_s, "rate", positive=True)
        if opts.max_cost_usd is not None:
            finite_number(opts.max_cost_usd, "max-cost-usd")
        if opts.max_cases is not None:
            positive_integer(opts.max_cases, "max-cases")
        if opts.resume_run_id and (
            opts.resume_run_id in (".", "..") or Path(opts.resume_run_id).name != opts.resume_run_id
        ):
            raise ValueError("resume must be a run folder name, not a path")
    except ValueError as exc:
        raise RunRefused(str(exc)) from exc
    for name in opts.systems:
        if name in OFFLINE_SYSTEMS:
            continue
        spec = registry.get(name)
        if not spec.enabled:
            raise RunRefused(f"{name} is disabled in configs/models.yaml: {spec.disabled_reason}")


def _select(ds: Dataset, opts: RunOptions) -> tuple[list[Task], list[ReferenceCase]]:
    pairs = list(zip(ds.tasks, ds.reference, strict=True))
    if opts.categories:
        known = {r.category for r in ds.reference}
        unknown = [c for c in opts.categories if c not in known]
        if unknown:
            raise RunRefused(f"unknown scenario category: {', '.join(unknown)}; choose from {', '.join(sorted(known))}")
        pairs = [p for p in pairs if p[1].category in opts.categories]
    if opts.max_cases is not None and opts.max_cases < len(pairs):
        keep = np.sort(np.random.default_rng(opts.seed).choice(len(pairs), size=opts.max_cases, replace=False))
        pairs = [pairs[int(i)] for i in keep]
    if not pairs:
        raise RunRefused("no cases selected")
    return [p[0] for p in pairs], [p[1] for p in pairs]


def _system_config(name: str, registry: Registry, opts: RunOptions) -> dict[str, Any]:
    if name in OFFLINE_SYSTEMS:
        local = make_local(name)
        return {"model_requested": local.model, "kind": "local", "execution": local.execution}
    spec = registry.get(name)
    return {
        "model_requested": spec.model,
        "label": spec.label,
        "provider": spec.provider,
        "kind": spec.kind,
        "family": spec.family,
        "endpoint": spec.endpoint,  # placeholders such as {CLOUDFLARE_ACCOUNT_ID} are never filled in here
        "execution": "dry_run" if opts.dry_run else spec.execution,
        "gateway": spec.gateway,
        "native_counterpart": spec.native_counterpart,
        "version_pinning": spec.version_pinning,
        "max_context_tokens": spec.max_context_tokens,
        "reports_probabilities": spec.reports_probabilities,
        "batching": spec.batching,
        "timeout_s": spec.timeout_s,
        "max_retries": 2,
        "parameters": spec.parameters,
        "interface_status": spec.interface_status,
        "price": spec.price.model_dump(),
        "terms": spec.terms.model_dump(),
        "publication_approved": spec.publication.approved,
        "sampling": "provider defaults except explicitly recorded parameters",
    }


async def _run_remote(
    provider: DecisionProvider, tasks: list[Task], budget: Budget, ledger: Ledger,
    done: dict[tuple[str, str], Prediction], opts: RunOptions,
) -> list[Prediction]:  # fmt: skip
    semaphore = asyncio.Semaphore(opts.concurrency)
    limiter = _RateLimiter(opts.rate_per_s)
    finished = 0

    async def one(task: Task) -> Prediction:
        nonlocal finished
        previous = done.get((provider.name, task.case_id))
        if previous is not None:
            if previous.payload_hash != task.payload_hash or previous.model_requested != provider.model:
                raise RunRefused("resume refused: a saved payload or model differs")
            return previous
        reserve = worst_case_cost(provider, task)
        async with semaphore:
            if not await budget.reserve(reserve):
                return blank_prediction(
                    task, provider.name, provider.model, "not_run", "budget exhausted", provider.execution
                )
            if isinstance(provider, ConfiguredProvider) and not provider.dry_run:
                await limiter.wait()
            attempt_id = ledger.start(provider.name, task.case_id, reserve)
            try:
                pred = await provider.evaluate(task)
            except MissingCredentials:
                raise
            except Exception as exc:  # an adapter bug must not stop the run or leak details
                pred = blank_prediction(
                    task,
                    provider.name,
                    provider.model,
                    "error",
                    f"adapter error: {type(exc).__name__}",
                    provider.execution,
                )
                pred = Prediction(**{**pred.as_dict(), "attempts": 1})
            ledger.finish(attempt_id, pred)
            known, estimated = prediction_costs(pred, reserve)
            await budget.settle(reserve, known, estimated_usd=estimated)
        finished += 1
        if opts.progress and finished % 100 == 0:
            opts.progress(
                f"  {provider.name}: {finished:,}/{len(tasks):,} done, accounted ${budget.state.spent_usd:.4f}"
            )
        return pred

    return list(await asyncio.gather(*(one(t) for t in tasks)))


def _repeat_tasks(tasks: list[Task], repeats: int) -> list[Task]:
    out = list(tasks)
    for k in range(1, repeats):
        out += [Task(f"{t.case_id}{REPEAT_MARK}{k}", t.state, t.payload_hash, t.questions) for t in tasks]
    return out


def run_benchmark(ds: Dataset, opts: RunOptions, outputs: Path | None = None) -> tuple[Path, dict[str, Any]]:
    registry = load_registry()
    _validate(opts, registry)
    outputs = outputs or OUTPUTS
    load_env()
    remote = [s for s in opts.systems if s not in OFFLINE_SYSTEMS]
    sendable = ds.spec.external_processing_allowed or opts.dry_run
    live = bool(remote) and sendable and not opts.dry_run
    if live and not opts.allow_external_requests:
        raise RunRefused("live providers need --allow-external-requests (or use --dry-run for fixture responses)")
    if live and opts.max_cost_usd is None:
        raise RunRefused("live providers need --max-cost-usd")
    tasks, reference = _select(ds, opts)
    ids = [t.case_id for t in tasks]
    identity = {
        "schema": 1,
        "dataset": ds.spec.model_dump(mode="json"),
        "split": ds.split,
        "input_files_sha256": ds.files_sha256,
        "case_ids_sha256": hashlib.sha256("\n".join(ids).encode()).hexdigest(),
        "payloads_sha256": json_hash([t.payload_hash for t in tasks]),
        "reference_sha256": json_hash([r.answers for r in reference]),
        "questions": {"version": ds.questions.version, "set": ds.questions.name, "sha256": file_hash(QUESTIONS_PATH)},
        "system_configs": {name: _system_config(name, registry, opts) for name in opts.systems},
        "model_registry_sha256": file_hash(MODEL_REGISTRY),
        "source_sha256": source_hash(),
        "dry_run": opts.dry_run,
        "categories": opts.categories,
        "max_cases": opts.max_cases,
        "repeats": opts.repeats,
        "resamples": opts.resamples,
        "seed": opts.seed,
    }
    identity_digest = json_hash(identity)
    if opts.resume_run_id:
        out = outputs / opts.resume_run_id
        if not out.is_dir():
            raise RunRefused(f"no run to resume: {out}")
    else:
        stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        out = outputs / f"{stamp}-{ds.spec.name}-{ds.split}-{'dryrun' if opts.dry_run else 'run'}"
        try:
            out.mkdir(parents=True, exist_ok=False)
        except FileExistsError as exc:
            raise RunRefused("a run with this timestamp already exists; wait a second or resume it") from exc
    try:
        with run_lock(out):
            return _execute(ds, opts, registry, out, identity, identity_digest, tasks, reference, sendable)
    except ValueError as exc:
        raise RunRefused(str(exc)) from exc


def _execute(
    ds: Dataset, opts: RunOptions, registry: Registry, out: Path, identity: dict[str, Any], identity_digest: str,
    tasks: list[Task], reference: list[ReferenceCase], sendable: bool,
) -> tuple[Path, dict[str, Any]]:  # fmt: skip
    started = datetime.now(UTC).isoformat(timespec="microseconds")
    manifest_path = out / "manifest.json"
    if opts.resume_run_id:
        if not manifest_path.is_file():
            raise RunRefused("resume refused: the run has no manifest")
        import json

        manifest = json.loads(manifest_path.read_text())
        if manifest.get("identity_sha256") != identity_digest:
            raise RunRefused("resume refused: inputs, reference, questions, models, code or options differ")
    else:
        manifest = {
            "run_id": out.name,
            "kind": "run",
            "started_utc": started,
            "versions": {
                "triallab": __version__, "eval": EVAL_VERSION, "rules": RULES_VERSION, "render": RENDER_VERSION,
                "questions": ds.questions.version, "python": platform.python_version(),
                "platform": f"{platform.system()} {platform.machine()}",
            },
            "dataset": {**ds.spec.model_dump(mode="json"), "split": ds.split, "files_sha256": ds.files_sha256},
            "identity": identity,
            "identity_sha256": identity_digest,
            "sessions": [],
            "run": {
                "systems": opts.systems, "scored_cases": len(tasks), "dry_run": opts.dry_run,
                "concurrency": opts.concurrency, "rate_per_s": opts.rate_per_s, "repeats": opts.repeats,
                "allow_external_requests": opts.allow_external_requests, "max_cost_usd": opts.max_cost_usd,
                "timing": {},
            },
        }  # fmt: skip
    ledger = Ledger(out / "attempts.jsonl")
    past = ledger.summary()
    if opts.max_cost_usd is not None and past.spent_usd > opts.max_cost_usd:
        raise RunRefused("resume budget is below the amount already accounted; increase it before resuming")
    budget = Budget(opts.max_cost_usd or 0.0, past.spent_usd, past.estimated_usd)
    session = {"started_utc": started, "git": git_state(), "status": "running"}
    manifest["sessions"].append(session)
    manifest["status"] = "running"
    atomic_json(manifest_path, manifest)
    predictions: dict[str, list[Prediction]] = {}
    timing: dict[str, dict[str, float]] = manifest["run"]["timing"]

    async def everything() -> None:
        for name in opts.systems:
            if name not in OFFLINE_SYSTEMS:
                continue
            local = make_local(name)
            t0 = time.perf_counter()
            predictions[name] = [await local.evaluate(t) for t in tasks]
            timing[name] = {"wall_seconds": time.perf_counter() - t0}
        remote = [s for s in opts.systems if s not in OFFLINE_SYSTEMS]
        if not remote:
            return
        pool = max(10, len(remote) * opts.concurrency + 10)
        client = httpx.AsyncClient(
            transport=fixture_transport() if opts.dry_run else None,
            limits=httpx.Limits(max_connections=pool, max_keepalive_connections=pool),
        )
        async with client:
            to_run: list[ConfiguredProvider] = []
            for name in remote:
                provider = make_remote(name, registry, client, dry_run=opts.dry_run)
                if not sendable:
                    predictions[name] = [
                        blank_prediction(
                            t, name, provider.model, "permission_blocked",
                            "dataset is local only (external_processing_allowed: false)", provider.execution,
                        )
                        for t in tasks
                    ]  # fmt: skip
                    continue
                if not opts.dry_run:
                    try:
                        provider.credentials()
                    except MissingCredentials as exc:
                        raise RunRefused(str(exc)) from exc
                to_run.append(provider)
            if opts.progress and to_run and not opts.dry_run:
                estimate = sum(worst_case_cost(p, t) for p in to_run for t in tasks) * opts.repeats
                opts.progress(
                    f"conservative cost estimate ${estimate:.4f}; guard ${opts.max_cost_usd:.2f}; "
                    "token and billing uncertainty can exceed estimates"
                )

            async def timed(provider: ConfiguredProvider) -> list[Prediction]:
                t0 = time.perf_counter()
                result = await _run_remote(
                    provider, _repeat_tasks(tasks, opts.repeats), budget, ledger, past.completed, opts
                )
                previous = timing.get(provider.name, {}).get("wall_seconds", 0.0)
                timing[provider.name] = {"wall_seconds": previous + time.perf_counter() - t0}
                return result

            results = await asyncio.gather(*[timed(p) for p in to_run])
            predictions.update({p.name: preds for p, preds in zip(to_run, results, strict=True)})

    try:
        asyncio.run(everything())
        ordered = {name: predictions[name] for name in opts.systems}
        accounting = ledger.summary().by_provider
        metrics = compute_metrics(
            track=ds.spec.track, reference=reference, predictions=ordered, seed=opts.seed, resamples=opts.resamples,
            accounting=accounting, timing=timing, configs=manifest["identity"]["system_configs"],
        )  # fmt: skip
        metrics.update(run_id=out.name, dataset=ds.spec.name, split=ds.split, budget=asdict(budget.state))
        metrics["budget"]["overrun_usd"] = budget.state.overrun_usd
        atomic_jsonl(out / "predictions.jsonl", [p.as_dict() for preds in ordered.values() for p in preds])
        atomic_jsonl(out / "reference.jsonl", [reference_row(r) for r in reference])
        atomic_json(out / "metrics.json", metrics)
        session.update(status="complete", completed_utc=datetime.now(UTC).isoformat(timespec="microseconds"))
        manifest.update(status="complete", completed_utc=session["completed_utc"])
        manifest["artifacts_sha256"] = {
            name: file_hash(out / name)
            for name in ("metrics.json", "predictions.jsonl", "reference.jsonl", "attempts.jsonl")
            if (out / name).is_file()
        }
        atomic_json(manifest_path, manifest)
        return out, metrics
    except BaseException as exc:
        session.update(status="interrupted", error_type=type(exc).__name__)
        manifest["status"] = "interrupted"
        atomic_json(manifest_path, manifest)
        raise


def reference_row(ref: ReferenceCase) -> dict[str, Any]:
    return {
        "case_id": ref.case_id, "answers": ref.answers, "category": ref.category, "scenario": ref.scenario,
        "tags": list(ref.tags), "evidence_refs": sorted(ref.evidence_refs), "valid_refs": sorted(ref.valid_refs),
    }  # fmt: skip


def reference_from_row(row: dict[str, Any]) -> ReferenceCase:
    return ReferenceCase(
        case_id=row["case_id"], answers=row["answers"], category=row["category"], scenario=row["scenario"],
        tags=tuple(row["tags"]), evidence_refs=frozenset(row["evidence_refs"]), valid_refs=frozenset(row["valid_refs"]),
    )  # fmt: skip


def _percentile(values: list[float], q: float) -> float | None:
    return float(np.percentile(values, q)) if values else None


def _performance(
    name: str, preds: list[Prediction], n: int, accounting: dict[str, Any] | None, wall: float | None,
    detected_issues: int | None,
) -> dict[str, Any]:  # fmt: skip
    statuses = Counter(p.status for p in preds)
    ok = [p for p in preds if p.status == "ok"]
    attempted = [p for p in preds if p.attempts > 0]
    latencies = [p.total_latency_ms for p in ok if p.total_latency_ms is not None]
    local = all(p.execution == "local" for p in preds)
    acct = accounting or {}
    known = float(acct.get("known_cost_usd", sum(p.cost_usd or 0.0 for p in preds)))
    estimated = float(acct.get("estimated_cost_usd", 0.0))
    cost = known + estimated
    complete = bool(acct.get("cost_evidence_complete", local))
    return {
        "latency_ms": {
            "p50": _percentile(latencies, 50),
            "p95": _percentile(latencies, 95),
            "answered": len(latencies),
        },
        "latency_scope": (
            "local computation" if local else "end to end from this machine, including network and any gateway"
        ),
        "throughput_cases_per_s": (len(ok) / wall) if wall else None,
        "wall_seconds": wall,
        "failure_rate": (n - len(ok)) / n,
        "api_failure_rate": sum(statuses[s] for s in ("error", "timeout", "rate_limited")) / n,
        "retry_rate": (sum(p.attempts > 1 for p in attempted) / len(attempted)) if attempted else None,
        "schema_failure_rate": statuses["invalid"] / n,
        "refusal_rate": statuses["refusal"] / n,
        "tokens": {
            "input": acct.get("input_tokens", sum(p.input_tokens or 0 for p in preds)),
            "output": acct.get("output_tokens", sum(p.output_tokens or 0 for p in preds)),
            "cached_input": acct.get("cached_input_tokens"),
            "complete": bool(acct.get("token_usage_complete", local)),
        },
        "cost": {
            "known_usd": known,
            "estimated_usd": estimated,
            "total_usd": cost,
            "per_1000_cases_usd": cost / n * 1000,
            "per_detected_issue_usd": (cost / detected_issues) if detected_issues else None,
            "evidence_complete": complete,
            "basis": "local, no API cost" if local else (
                "measured: provider-reported token usage x list prices in the registry; not an invoice"
                if complete else "partly estimated: some calls reported no usage and are counted at their reservation"
            ),
        },
        "http_statuses": acct.get("http_statuses", {}),
    }  # fmt: skip


def compute_metrics(
    *, track: str, reference: list[ReferenceCase], predictions: dict[str, list[Prediction]], seed: int,
    resamples: int, accounting: dict[str, dict[str, Any]], timing: dict[str, dict[str, float]],
    configs: dict[str, dict[str, Any]],
) -> dict[str, Any]:  # fmt: skip
    """Processed statistics from raw predictions. Used by both `run` and `replay`."""
    n = len(reference)
    ids = {r.case_id for r in reference}
    systems: dict[str, dict[str, Any]] = {}
    tables = {}
    correct: dict[str, list[bool]] = {}
    for name, preds in predictions.items():
        base = {p.case_id: p for p in preds if p.case_id in ids}
        answers = {
            cid: SystemAnswer(
                p.answers, p.probabilities, tuple(p.evidence_refs) if p.evidence_refs is not None else None
            )
            for cid, p in base.items()
        }
        statuses = dict(Counter(p.status for p in base.values()))
        execution = next(iter(base.values())).execution if base else "local"
        entry: dict[str, Any] = {
            "execution": execution,
            "measurement": execution not in ("dry_run", "mock"),
            "model_requested": configs.get(name, {}).get("model_requested"),
            "models_reported": sorted({p.model_reported for p in base.values() if p.model_reported}),
            "statuses": statuses,
            "coverage": statuses.get("ok", 0) / n,
        }
        if statuses.get("ok", 0) == 0:
            entry["status"] = max(statuses, key=lambda s: statuses[s]) if statuses else "not_run"
            entry["reason"] = next((p.error for p in base.values() if p.error), "")
            systems[name] = entry
            continue
        quality = (
            triage_metrics(reference, answers, seed) if track == "synthetic" else finding_metrics(reference, answers)
        )
        correct[name] = quality.pop("case_correct")
        detected = quality.get("issue_detection", {}).get("tp") if track == "synthetic" else None
        entry.update(
            status="ok",
            quality=quality,
            probability=probability_metrics(reference, answers),
            performance=_performance(
                name, list(base.values()), n, accounting.get(name), timing.get(name, {}).get("wall_seconds"), detected
            ),
        )
        repeats: dict[int, dict[str, dict[str, bool] | None]] = {0: {c: p.answers for c, p in base.items()}}
        for p in preds:
            if REPEAT_MARK in p.case_id:
                cid, k = p.case_id.split(REPEAT_MARK)
                repeats.setdefault(int(k), {})[cid] = p.answers
        entry["stability"] = answer_stability([repeats[k] for k in sorted(repeats)])
        if track == "synthetic":
            tables[name] = build_table(reference, answers)
        systems[name] = entry
    reference_system = REFERENCE_SYSTEM[track] if REFERENCE_SYSTEM[track] in correct else None
    bootstrap: dict[str, Any] = {"resamples": resamples, "seed": seed}
    if tables:
        intervals, differences = paired_bootstrap(
            tables, [r.category for r in reference], reference_system, resamples, seed
        )
        bootstrap["method"] = "paired, stratified by scenario category, percentile"
        for name in tables:
            systems[name]["ranges_95"] = {m: asdict(i) for m, i in intervals[name].items()}
            if name in differences:
                systems[name]["difference_vs_reference_95"] = {m: asdict(i) for m, i in differences[name].items()}
    if reference_system:
        for name, right in correct.items():
            if name != reference_system:
                systems[name]["paired_vs_reference"] = {
                    "test": "McNemar exact, two-sided, on whether both domain outcomes are right",
                    "first": name, "second": reference_system, **mcnemar_exact(right, correct[reference_system]),
                }  # fmt: skip
    return {
        "eval_version": EVAL_VERSION,
        "track": track,
        "scored_cases": n,
        "composition": {
            "by_category": dict(Counter(r.category for r in reference)),
            "by_scenario": dict(Counter(r.scenario for r in reference)),
            "text_dependent": sum("text_dependent" in r.tags for r in reference),
        },
        "reference_system": reference_system,
        "bootstrap": bootstrap,
        "systems": systems,
    }


def _pct(value: float | None) -> str:
    return "    -" if value is None else f"{value:>5.1%}"


def format_run_table(metrics: dict[str, Any]) -> str:
    if metrics["track"] == "regulatory":
        lines = [f"{'system':<20}{'status':<20}{'cover':>7}{'elig F1':>9}{'consent F1':>12}{'both right':>12}"]
        for name, m in metrics["systems"].items():
            if m["status"] != "ok":
                lines.append(f"{name:<20}{m['status']:<20}{m['coverage']:>7.1%}  {m.get('reason', '')}")
                continue
            q = m["quality"]
            note = "" if m["measurement"] else "  (fixture answers; not a measurement)"
            lines.append(
                f"{name:<20}{'ok':<20}{m['coverage']:>7.1%}{_pct(q['questions']['eligibility_issue']['f1']):>9}"
                f"{_pct(q['questions']['consent_issue']['f1']):>12}{_pct(q['case_accuracy']):>12}{note}"
            )
        return "\n".join(lines)
    lines = [
        f"{'system':<20}{'status':<20}{'cover':>7}{'case acc':>9}{'crit rec':>9}{'issue P':>8}{'issue R':>8}"
        f"{'missed':>7}{'FP/100':>7}{'p95 ms':>9}{'$/1k':>9}"
    ]
    for name, m in metrics["systems"].items():
        if m["status"] != "ok":
            lines.append(f"{name:<20}{m['status']:<20}{m['coverage']:>7.1%}  {m.get('reason', '')}")
            continue
        q, perf = m["quality"], m["performance"]
        p95 = perf["latency_ms"]["p95"]
        note = "" if m["measurement"] else "  (fixture answers; not a measurement)"
        lines.append(
            f"{name:<20}{'ok':<20}{m['coverage']:>7.1%}{_pct(q['case_accuracy']):>9}{_pct(q['critical_recall']):>9}"
            f"{_pct(q['issue_precision']):>8}{_pct(q['issue_recall']):>8}{q['missed_issues']:>7}"
            f"{q['false_positives_per_100']:>7.1f}{(f'{p95:.1f}' if p95 is not None else '-'):>9}"
            f"{perf['cost']['per_1000_cases_usd']:>9.4f}{note}"
        )
    return "\n".join(lines)
