"""Offline integrity checks for the archived screening study (studies/screening)."""

import hashlib
import json
from collections import defaultdict
from pathlib import Path

import pytest

STUDY = Path(__file__).resolve().parents[2] / "studies" / "screening"
TP = STUDY / "experiment" / "screening" / "tp"
FINAL = STUDY / "screening-check" / "trialpanorama" / "final"

# Not redistributed: it holds paper titles and abstracts.
NOT_IN_REPOSITORY = {"screening-check/trialpanorama/final/sample.jsonl"}

# Per-paper answers of the hosted models are raw provider outputs. They stay out of the repository until
# publication rights are recorded for each provider, so only the locally trained classifiers are recomputed.
SYSTEMS = {
    "logistic": "final-classic-logistic.jsonl",
    "xgboost": "final-classic-xgboost.jsonl",
}


def _labels() -> dict[str, tuple[str, int]]:
    out = {}
    for line in (FINAL / "sample-ids.jsonl").read_text().splitlines():
        r = json.loads(line)
        out[f"{r['review']}|{r['pmid']}"] = (r["review"], int(r["label"]))
    return out


def _probabilities(path: str) -> dict[str, float]:
    return {p["case_id"]: p["p"] for p in map(json.loads, (TP / path).read_text().splitlines())}


def test_frozen_files_match_their_fingerprints() -> None:
    freeze = json.loads((FINAL / "freeze.json").read_text())
    checked = 0
    for name, expected in freeze["files"].items():
        if name in NOT_IN_REPOSITORY:
            continue
        assert hashlib.sha256((STUDY / name).read_bytes()).hexdigest() == expected, name
        checked += 1
    assert checked == len(freeze["files"]) - len(NOT_IN_REPOSITORY)


def test_sample_ids_match_the_manifest() -> None:
    manifest = json.loads((FINAL / "sample-manifest.json").read_text())
    labels = _labels()
    assert len(labels) == manifest["records"]
    assert sum(label for _, label in labels.values()) == manifest["included"]
    assert len({review for review, _ in labels.values()}) == manifest["families_qualifying"]


def test_no_abstract_text_is_stored() -> None:
    for line in (FINAL / "sample-ids.jsonl").read_text().splitlines():
        assert set(json.loads(line)) == {"review", "pmid", "pmcid", "doi", "licence", "label", "year"}


@pytest.mark.parametrize("system", sorted(SYSTEMS))
def test_balanced_accuracy_reproduces_from_saved_predictions(system: str) -> None:
    labels = _labels()
    probabilities = _probabilities(SYSTEMS[system])
    assert set(probabilities) == set(labels)
    by_review: dict[str, dict[int, list[bool]]] = defaultdict(lambda: {0: [], 1: []})
    for case_id, (review, label) in labels.items():
        by_review[review][label].append((probabilities[case_id] >= 0.5) == bool(label))
    per_review = [(sum(v[1]) / len(v[1]) + sum(v[0]) / len(v[0])) / 2 for v in by_review.values()]
    recomputed = sum(per_review) / len(per_review)
    reported = json.loads((TP / "final-results.json").read_text())["systems"][system]["balanced_accuracy"]
    assert recomputed == pytest.approx(reported, abs=1e-9)


CORRECTED = STUDY / "screening-check" / "trialpanorama" / "final-corrected"


def test_corrected_rerun_files_match_their_fingerprints() -> None:
    freeze = json.loads((CORRECTED / "freeze.json").read_text())
    missing = {"screening-check/trialpanorama/final-corrected/sample.jsonl"}  # holds titles and abstracts
    for name, expected in freeze["files"].items():
        if name not in missing:
            assert hashlib.sha256((STUDY / name).read_bytes()).hexdigest() == expected, name
    added = freeze["added_before_results_were_read"]
    assert hashlib.sha256((STUDY / added["file"]).read_bytes()).hexdigest() == added["sha256"]
    assert all(freeze["unchanged_since_locked_freeze"].values())


def test_corrected_sample_manifest_is_consistent() -> None:
    manifest = json.loads((CORRECTED / "manifest.json").read_text())
    changed = json.loads((CORRECTED / "changed.json").read_text())
    labels = _labels()
    assert manifest["records"] == len(labels) and manifest["labels_identical"] and manifest["titles_changed"] == 0
    assert manifest["abstracts_changed"] == len(changed) == sum(manifest["changed_by_label"].values())
    assert {f"{c['review']}|{c['pmid']}" for c in changed} <= set(labels)
    by_label = [labels[f"{c['review']}|{c['pmid']}"][1] for c in changed]
    assert sum(by_label) == manifest["changed_by_label"]["included"]


@pytest.mark.parametrize("system", sorted(SYSTEMS))
def test_corrected_rerun_accuracy_reproduces_from_saved_predictions(system: str) -> None:
    labels = _labels()
    probabilities = _probabilities(SYSTEMS[system].replace("final-", "corrected-"))
    assert set(probabilities) == set(labels)
    by_review: dict[str, dict[int, list[bool]]] = defaultdict(lambda: {0: [], 1: []})
    for case_id, (review, label) in labels.items():
        by_review[review][label].append((probabilities[case_id] >= 0.5) == bool(label))
    per_review = [(sum(v[1]) / len(v[1]) + sum(v[0]) / len(v[0])) / 2 for v in by_review.values()]
    reported = json.loads((TP / "corrected-results.json").read_text())["systems"][system]["balanced_accuracy"]
    assert sum(per_review) / len(per_review) == pytest.approx(reported, abs=1e-9)


def test_no_raw_provider_output_is_stored() -> None:
    assert not [p.name for p in STUDY.rglob("*.jsonl") if p.name in ("predictions.jsonl", "attempts.jsonl")]
    assert not list(TP.glob("final-pass*")) and not list(TP.glob("corrected-pass*"))
