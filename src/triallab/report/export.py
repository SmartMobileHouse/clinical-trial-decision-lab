"""`triallab export-report-data`: a public-safe evidence bundle for the report system.

Writes one JSON file with every number a published report may use. Publishing
tools read this file; they never read run folders.

Gates, each independent of the others:
- the dataset must be approved for publication (never inferred from processing permission);
- a remote system's results are included only when they are real measurements (not a dry
  run) AND the model's publication is approved in the registry; otherwise the system is
  listed with a status such as "not run" and no numbers;
- a track whose dataset is not approved is listed as withheld, with no numbers.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from triallab import __version__
from triallab.benchmark.replay import load_run, replay_run
from triallab.config import OUTPUTS
from triallab.core.provenance import read_jsonl
from triallab.providers.registry import LOCAL_SYSTEMS
from triallab.providers.spec import load_registry

SCHEMA = "smh-research-data/1"
NOT_RUN = "not run"
WITHHELD = "withheld"
LOCAL_LABELS = {
    "rules": "Deterministic protocol rules",
    "keyword": "Keyword rules",
    "flag_all": "Flag every case (anchor)",
    "flag_none": "Flag no case (anchor)",
}


class ReportError(RuntimeError):
    """A run folder is missing, unusable or not approved for publication."""


class RestrictedDatasetError(ReportError):
    """Publication rights have not been established for a dataset's artifacts."""


def require_publication(manifest: dict[str, Any], run_id: str) -> None:
    ds = manifest.get("dataset", {})
    if ds.get("publication_allowed") is True and str(ds.get("publication_note", "")).strip():
        return
    raise RestrictedDatasetError(
        f"{run_id} uses dataset {ds.get('name')!r}, whose results are not approved for publication "
        "(publication_allowed and a publication_note are required; local only until rights are reviewed)"
    )


def _system(name: str, entry: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    out = {
        "label": config.get("label") or LOCAL_LABELS.get(name, name),
        "execution": entry["execution"],
        "model_requested": entry.get("model_requested"),
        "models_reported": entry.get("models_reported", []),
        "versions": entry.get("models_reported") or [entry.get("model_requested")],
        "status": entry["status"],
        "coverage": entry["coverage"],
        "statuses": entry["statuses"],
    }
    if entry["status"] != "ok":
        out["reason"] = entry.get("reason", "")
        return out
    for key in ("quality", "probability", "performance", "ranges_95", "difference_vs_reference_95",
                "paired_vs_reference", "stability"):  # fmt: skip
        if key in entry:
            out[key] = entry[key]
    return out


def _experiment(run_id: str, outputs: Path) -> dict[str, Any]:
    out, manifest, metrics = load_run(run_id, outputs)
    require_publication(manifest, run_id)
    _, _, differences = replay_run(run_id, outputs)
    if differences:
        raise ReportError(f"{run_id}: saved statistics do not match a replay ({', '.join(differences)})")
    registry = load_registry()
    configs = manifest["identity"]["system_configs"]
    systems: dict[str, Any] = {}
    included: list[str] = []
    for name, entry in metrics["systems"].items():
        if name == "mock":
            continue
        if name in LOCAL_SYSTEMS:
            systems[name] = _system(name, entry, configs.get(name, {}))
            included.append(name)
            continue
        spec = registry.get(name)
        if not entry.get("measurement"):
            systems[name] = {
                "label": spec.label,
                "status": NOT_RUN,
                "reason": "only a dry run with fixture responses exists",
            }
        elif not spec.publishable:
            systems[name] = {
                "label": spec.label,
                "status": WITHHELD,
                "reason": "publication of this model's results is not approved",
            }
        else:
            systems[name] = _system(name, entry, configs.get(name, {}))
            included.append(name)
    for spec in registry.models:  # every registered model appears, so a missing result is visible as such
        if spec.id not in systems:
            reason = spec.disabled_reason if not spec.enabled else "paid API run not executed yet"
            systems[spec.id] = {"label": spec.label, "status": NOT_RUN, "reason": reason}
    ds = manifest["dataset"]
    verification = None
    if ds["track"] == "synthetic":
        predictions = [
            {
                k: row[k]
                for k in ("case_id", "provider", "answers", "probabilities", "evidence_refs", "status", "payload_hash")
            }
            for row in read_jsonl(out / "predictions.jsonl")
            if row["provider"] in included
        ]
        verification = {
            "scope": "saved final answers for the bundled fictional dataset; enough to recompute every quality metric",
            "reference": [{"case_id": r["case_id"], "answers": r["answers"], "category": r["category"],
                           "scenario": r["scenario"], "tags": r["tags"]} for r in read_jsonl(out / "reference.jsonl")],
            "predictions": predictions,
        }  # fmt: skip
    return {
        "run_id": run_id,
        "started_utc": manifest["started_utc"],
        "completed_utc": manifest.get("completed_utc"),
        "track": ds["track"],
        "dataset": {
            "name": ds["name"],
            "split": ds["split"],
            "rows": metrics["scored_cases"],
            "license_note": ds["license_note"],
            "files_sha256": ds["files_sha256"],
            "external_processing_allowed": ds["external_processing_allowed"],
            "publication_allowed": True,
            "publication_note": ds["publication_note"],
        },
        "scored_cases": metrics["scored_cases"],
        "composition": metrics["composition"],
        "reference_system": metrics["reference_system"],
        "bootstrap": metrics["bootstrap"],
        "versions": manifest["versions"],
        "questions": manifest["identity"]["questions"],
        "models": systems,
        "measured_systems": included,
        "provenance": {
            "git": manifest["sessions"][-1].get("git"),
            "identity_sha256": manifest["identity_sha256"],
            "source_sha256": manifest["identity"]["source_sha256"],
            "model_registry_sha256": manifest["identity"]["model_registry_sha256"],
            "artifacts_sha256": manifest.get("artifacts_sha256", {}),
            "run_options": {
                k: manifest["run"][k]
                for k in ("systems", "scored_cases", "dry_run", "concurrency", "rate_per_s", "repeats", "max_cost_usd")
            },
            "limitation": "Metadata does not freeze provider-side behaviour or authenticate provider execution.",
        },  # fmt: skip
        "verification": verification,
    }


def model_register() -> list[dict[str, Any]]:
    return [
        {
            "id": m.id, "label": m.label, "provider": m.provider, "family": m.family, "model": m.model,
            "execution": m.execution, "gateway": m.gateway, "enabled": m.enabled, "disabled_reason": m.disabled_reason,
            "interface_status": m.interface_status, "version_pinning": m.version_pinning,
            "max_context_tokens": m.max_context_tokens, "reports_probabilities": m.reports_probabilities,
            "price_input_per_m_usd": m.price.input, "price_output_per_m_usd": m.price.output,
            "price_source": m.price.source, "price_retrieved": m.price.retrieved,
            "terms_benchmark_publication": m.terms.benchmark_publication,
            "terms_output_publication": m.terms.output_publication, "publication_approved": m.publication.approved,
        }
        for m in load_registry().models
    ]  # fmt: skip


def export_report_data(run_ids: list[str], out_file: Path, outputs: Path | None = None) -> Path:
    outputs = outputs or OUTPUTS
    experiments: dict[str, Any] = {}
    for run_id in run_ids:
        experiment = _experiment(run_id, outputs)  # raises on unapproved datasets
        key = experiment["dataset"]["name"].replace("-", "_") + "_" + experiment["dataset"]["split"]
        if key in experiments:
            raise ReportError(f"two runs for the same dataset split ({key}); export one of them")
        experiments[key] = experiment
    bundle = {
        "schema": SCHEMA,
        "generated_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "generator": {"tool": "triallab", "version": __version__},
        "experiments": experiments,
        "tracks": {
            "synthetic": {
                "status": "included" if any(e["track"] == "synthetic" for e in experiments.values()) else NOT_RUN
            },
            "regulatory": {
                "status": WITHHELD,
                "reason": "The regulatory-finding dataset and its results are local only until the privacy review "
                "and owner approval recorded in docs/RELEASE-APPROVAL.md are complete.",
            },
        },
        "model_register": model_register(),
    }
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(json.dumps(bundle, indent=2, allow_nan=False) + "\n")
    return out_file
