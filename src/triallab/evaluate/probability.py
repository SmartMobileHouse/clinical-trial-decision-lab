"""Probability quality, only for systems that report probabilities.

A probability is whatever a provider returned for "yes". It is not assumed to be
calibrated; these metrics measure whether it is. Systems that return only
yes/no get no probability metrics: none are invented for them.

- Brier score: mean squared difference between the probability and the 0/1 reference.
- Expected calibration error (ECE): cases are sorted into 10 equal-width
  probability bins; ECE is the case-weighted mean gap between the average
  probability and the observed share of "yes" in each bin.
- Reliability table: the per-bin numbers behind a reliability diagram.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import numpy as np

from triallab.evaluate.decision import ReferenceCase, SystemAnswer

BINS = 10


def brier(probabilities: np.ndarray, outcomes: np.ndarray) -> float:
    return float(np.mean((probabilities - outcomes) ** 2))


def reliability(probabilities: np.ndarray, outcomes: np.ndarray, bins: int = BINS) -> list[dict[str, Any]]:
    index = np.minimum((probabilities * bins).astype(int), bins - 1)
    table = []
    for b in range(bins):
        mask = index == b
        table.append(
            {
                "bin_low": b / bins,
                "bin_high": (b + 1) / bins,
                "count": int(mask.sum()),
                "mean_probability": float(probabilities[mask].mean()) if mask.any() else None,
                "observed_rate": float(outcomes[mask].mean()) if mask.any() else None,
            }
        )
    return table


def expected_calibration_error(probabilities: np.ndarray, outcomes: np.ndarray, bins: int = BINS) -> float:
    total = len(probabilities)
    return float(
        sum(
            row["count"] / total * abs(row["mean_probability"] - row["observed_rate"])
            for row in reliability(probabilities, outcomes, bins)
            if row["count"]
        )
    )


def probability_metrics(
    reference: Sequence[ReferenceCase], answers: Mapping[str, SystemAnswer]
) -> dict[str, Any] | None:
    """Per question and pooled over questions; None when the system reports no probabilities."""
    per_question: dict[str, tuple[list[float], list[float]]] = {}
    for ref in reference:
        given = answers.get(ref.case_id)
        if given is None or given.probabilities is None:
            continue
        for q, truth in ref.answers.items():
            if q in given.probabilities:
                ps, ys = per_question.setdefault(q, ([], []))
                ps.append(given.probabilities[q])
                ys.append(float(truth))
    if not per_question:
        return None
    out: dict[str, Any] = {"questions": {}}
    all_p: list[float] = []
    all_y: list[float] = []
    for q, (ps, ys) in per_question.items():
        p, y = np.array(ps), np.array(ys)
        out["questions"][q] = {"n": len(p), "brier": brier(p, y), "ece": expected_calibration_error(p, y)}
        all_p += ps
        all_y += ys
    p, y = np.array(all_p), np.array(all_y)
    out["pooled"] = {"n": len(p), "brier": brier(p, y), "ece": expected_calibration_error(p, y)}
    out["reliability"] = reliability(p, y)
    out["note"] = "Provider-reported probabilities, not assumed calibrated. Pooled over all questions and cases."
    return out
