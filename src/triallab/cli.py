"""Command-line interface: `triallab <command>`.

Commands: `doctor`, `version`, `demo`, `data ...`, `models`, `run`, `replay`,
`export-report-data`, `report`, `preflight`.
"""

from __future__ import annotations

import json
import os
import stat
from pathlib import Path

import typer

from triallab import __version__
from triallab.benchmark.replay import ReplayError, replay_run
from triallab.benchmark.runner import RunOptions, RunRefused, format_run_table, run_benchmark
from triallab.config import ENV_FILE, OUTPUTS, load_env, secret_status
from triallab.datasets import RESTRICTED_ENV, DatasetError, load_dataset
from triallab.evaluate.statistics import DEFAULT_RESAMPLES
from triallab.providers.base import MissingCredentials
from triallab.providers.registry import OFFLINE_SYSTEMS
from triallab.providers.spec import RegistryError, load_registry

app = typer.Typer(
    help="Clinical Trial Decision Lab — benchmark AI decision models against rules and LLMs "
    "for enrollment-eligibility and informed-consent issue triage. Research only; not a clinical tool.",
    no_args_is_help=True,
    add_completion=False,
)
data_app = typer.Typer(help="Generate and verify the bundled synthetic dataset.", no_args_is_help=True)
app.add_typer(data_app, name="data")
OK, WARN, FAIL = "ok  ", "warn", "FAIL"


def _line(status: str, label: str, detail: str = "") -> None:
    typer.echo(f"  [{status}] {label}" + (f" — {detail}" if detail else ""))


def _fail(message: str) -> None:
    typer.echo(f"Refused: {message}", err=True)
    raise typer.Exit(1)


@data_app.command("generate")
def data_generate() -> None:
    """Rewrite data/synthetic/v1/ from the fixed seeds."""
    from triallab.synthetic.generate import DATASET_DIR, write_dataset

    manifest = write_dataset()
    for split, info in manifest["splits"].items():
        typer.echo(f"  {split:<12}{info['cases']:>4} cases (seed {info['seed']})")
    typer.echo(f"Written to {DATASET_DIR}")


@data_app.command("verify")
def data_verify() -> None:
    """Regenerate every split in memory and compare with the committed files."""
    from triallab.synthetic.generate import verify_dataset

    problems = verify_dataset()
    if problems:
        for problem in problems:
            typer.echo(f"  [{FAIL}] {problem}")
        raise typer.Exit(1)
    typer.echo(
        "Synthetic dataset matches a fresh generation, and every case's declared findings match the adjudicator."
    )


@data_app.command("export-tables")
def data_export_tables(
    split: str = typer.Option("test", help="Dataset split to export"),
    out: Path = typer.Option(Path("outputs/tables"), help="Folder for dm.csv, ds.csv and enroll.csv"),
) -> None:
    """Write SDTM-shaped and monitoring-shaped tables for optional external clinical tools."""
    from triallab.interop.tables import write_tables
    from triallab.synthetic.generate import load_cases

    for name, rows in write_tables(load_cases(split), out).items():
        typer.echo(f"  {name:<12}{rows:>5} rows")
    typer.echo(f"Written to {out}. These tools are optional and not bundled; see docs/CLINICAL-TOOLS.md.")


@app.command()
def models() -> None:
    """List the model registry: what is enabled, how it was verified, and what may be published."""
    try:
        registry = load_registry()
    except RegistryError as exc:
        _fail(str(exc))
    typer.echo(f"{'id':<20}{'enabled':<9}{'execution':<10}{'interface':<24}{'publish results':<28}model")
    for m in registry.models:
        publish = "approved" if m.publishable else f"no ({m.terms.benchmark_publication.lower()})"
        enabled = "yes" if m.enabled else "no"
        typer.echo(f"{m.id:<20}{enabled:<9}{m.execution:<10}{m.interface_status:<24}{publish:<28}{m.model}")
    typer.echo(f"\nLocal systems (no keys, no cost): {', '.join(OFFLINE_SYSTEMS)}")
    typer.echo("No model has been executed by this project unless a run folder says so. See docs/MODEL-REGISTER.md.")


@app.command()
def run(
    dataset: str = typer.Option("synthetic-v1", "--dataset", "-d", help="Dataset name or config path"),
    systems: str = typer.Option("rules,flag_all,flag_none", "--systems", "-s", help="Comma-separated systems"),
    split: str | None = typer.Option(None, help="Dataset split (default: the reported split)"),
    dry_run: bool = typer.Option(False, help="Use fixture responses: no network, no keys, not a measurement"),
    allow_external_requests: bool = typer.Option(False, help="Required for live providers (paid API calls)"),
    max_cost_usd: float | None = typer.Option(None, help="Estimated spending guard (not a provider billing limit)"),
    max_cases: int | None = typer.Option(None, min=1, help="Run only a seeded sample of the cases"),
    categories: str | None = typer.Option(None, help="Comma-separated scenario categories to run"),
    repeats: int = typer.Option(1, min=1, max=5, help="Repeat each case for remote systems (answer stability)"),
    concurrency: int = typer.Option(4, min=1, max=64, help="Calls in flight per provider"),
    rate: float = typer.Option(2.0, min=0.1, help="Max new calls per second per provider"),
    resamples: int = typer.Option(DEFAULT_RESAMPLES, min=1, help="Bootstrap resamples"),
    resume: str | None = typer.Option(None, help="Run ID to resume (skips cases already answered)"),
) -> None:
    """Answer a dataset split with the chosen systems and save raw results and statistics."""
    try:
        ds = load_dataset(dataset, split)
        out, metrics = run_benchmark(
            ds,
            RunOptions(
                systems=[s.strip() for s in systems.split(",") if s.strip()],
                allow_external_requests=allow_external_requests,
                dry_run=dry_run,
                max_cost_usd=max_cost_usd,
                max_cases=max_cases,
                categories=[c.strip() for c in categories.split(",")] if categories else None,
                repeats=repeats,
                concurrency=concurrency,
                rate_per_s=rate,
                resamples=resamples,
                resume_run_id=resume,
                progress=typer.echo,
            ),  # fmt: skip
        )
    except (DatasetError, RegistryError, RunRefused, MissingCredentials) as exc:
        _fail(str(exc))
    typer.echo(f"{ds.spec.name} / {ds.split}: {metrics['scored_cases']:,} cases")
    typer.echo(format_run_table(metrics))
    if dry_run:
        typer.echo("Dry run: remote answers came from fixtures. They are not model output and are never reported.")
    typer.echo(f"Run ID: {out.name}  (folder: outputs/{out.name})")


@app.command()
def replay(run_id: str = typer.Option(..., "--run-id", help="Folder name under outputs/")) -> None:
    """Recompute a run's statistics from its raw files and compare with what was saved."""
    try:
        _, again, differences = replay_run(run_id)
    except ReplayError as exc:
        _fail(str(exc))
    typer.echo(format_run_table(again))
    if differences:
        typer.echo(f"MISMATCH in: {', '.join(differences)}", err=True)
        raise typer.Exit(1)
    typer.echo("Replay matches the saved statistics exactly.")


@app.command("export-report-data")
def export_report_data_cmd(
    run_id: list[str] = typer.Option(..., "--run-id", help="Run folder(s) under outputs/; repeat for several"),
    out: Path = typer.Option(Path("outputs/report-data.json"), help="Where to write the JSON evidence bundle"),
) -> None:
    """Write the public-safe evidence bundle that the report system reads."""
    from triallab.report.export import ReportError, export_report_data

    try:
        path = export_report_data(run_id, out)
    except (ReportError, ReplayError) as exc:
        _fail(str(exc))
    typer.echo(f"Evidence bundle written to {path}")


@app.command()
def report(
    run_id: list[str] = typer.Option(..., "--run-id", help="Run folder(s) under outputs/; repeat for several"),
    out: Path = typer.Option(Path("outputs/report.html"), help="Where to write the HTML file"),
) -> None:
    """Build a plain, self-contained HTML summary from finished runs."""
    from triallab.report.export import ReportError
    from triallab.report.render import build_report

    try:
        path = build_report(run_id, out)
    except (ReportError, ReplayError) as exc:
        _fail(str(exc))
    typer.echo(f"Report written to {path}")


@app.command()
def preflight(
    technical: bool = typer.Option(False, help="Run only the automated checks (used by `make check` and CI)"),
) -> None:
    """Publication preflight: rights, provenance, restricted files, notices, sensitive data, artifacts, approvals."""
    from triallab.preflight.checks import run_preflight

    results = run_preflight(technical_only=technical)
    failed = [r for r in results if not r.passed]
    for result in results:
        _line(OK if result.passed else FAIL, result.name, result.detail)
    if failed:
        pending = sum(r.kind == "approval" for r in failed)
        typer.echo(
            f"\npreflight: {len(failed)} check(s) failed ({pending} pending approval). Publication stays blocked."
        )
        raise typer.Exit(1)
    if technical:
        typer.echo(
            "\npreflight: automated checks passed. Approvals are checked by `triallab preflight` without --technical."
        )
    else:
        typer.echo("\npreflight: all checks passed, including recorded approvals.")


@app.command()
def demo() -> None:
    """One command, offline: rules and anchors on the synthetic test set, a dry run of two adapters, and a report."""
    from triallab.demo import run_demo

    run_dir, report_path = run_demo(progress=typer.echo)
    typer.echo(f"Run folder: outputs/{run_dir.name}")
    typer.echo(f"Report:     {report_path}")


@app.command()
def version() -> None:
    typer.echo(__version__)


@app.command()
def doctor() -> None:
    """Check the local setup. Prints no secrets."""
    from triallab.synthetic.generate import verify_dataset

    typer.echo(f"triallab {__version__}")
    typer.echo("Setup")
    env_loaded = load_env()
    if env_loaded:
        mode = stat.S_IMODE(ENV_FILE.stat().st_mode)
        _line(
            OK if mode & 0o077 == 0 else WARN,
            ".env found",
            f"permissions {mode:o}" + ("" if mode & 0o077 == 0 else "; run chmod 600 .env"),
        )
    else:
        _line(OK, "no .env", "fine for offline use; live runs need one (see .env.example)")
    try:
        registry = load_registry()
        _line(OK, "model registry", f"{len(registry.models)} models, {len(registry.enabled)} enabled")
    except RegistryError as exc:
        _line(FAIL, "model registry", str(exc))
        raise typer.Exit(1) from exc
    problems = verify_dataset()
    _line(
        FAIL if problems else OK, "synthetic dataset", "; ".join(problems) if problems else "matches a fresh generation"
    )
    restricted = os.environ.get(RESTRICTED_ENV, "").strip()
    _line(
        OK,
        "regulatory-finding dataset",
        "configured" if restricted else f"not configured ({RESTRICTED_ENV} unset); optional",
    )
    typer.echo("Credentials for live runs (name and length only)")
    for name in sorted({env for m in registry.enabled for env in m.required_env}):
        s = secret_status(name)
        _line(OK if s.is_set else WARN, name, f"set, {s.length} characters" if s.is_set else "not set")
    OUTPUTS.mkdir(exist_ok=True)
    if problems:
        raise typer.Exit(1)
    typer.echo(json.dumps({"offline_ready": True}))
