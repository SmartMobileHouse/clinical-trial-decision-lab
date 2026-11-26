"""Uncertainty and paired comparisons.

Paired bootstrap (method reused from Fraud Decision Lab's `evaluate/bootstrap.py`):
the scored cases are redrawn with replacement, keeping the number of cases in
each stratum fixed, and every headline metric is recomputed for every system on
the SAME redraw. The middle 95% of those values is the range. Because all
systems share each redraw, the range for "system minus reference" shows whether
a difference could be luck.

Caveats: redrawing cases treats them as independent, although cases of one
fictional study share a protocol; ranges condition on the saved answers and say
nothing about provider rerun variability or about real trials.

McNemar's exact test compares two systems case by case: among the cases where
exactly one of them is right, is one right more often than a coin flip?
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np

from triallab.evaluate.decision import HEADLINE, CaseTable, headline

DEFAULT_RESAMPLES = 1_000


@dataclass(frozen=True)
class Interval:
    low: float | None
    high: float | None


def _ranges(values: np.ndarray) -> dict[str, Interval]:
    out = {}
    for i, name in enumerate(HEADLINE):
        column = values[:, i]
        column = column[~np.isnan(column)]
        if len(column) == 0:
            out[name] = Interval(None, None)
        else:
            low, high = np.percentile(column, [2.5, 97.5])
            out[name] = Interval(float(low), float(high))
    return out


def paired_bootstrap(
    tables: dict[str, CaseTable],
    strata: Sequence[str],
    reference: str | None = None,
    resamples: int = DEFAULT_RESAMPLES,
    seed: int = 42,
) -> tuple[dict[str, dict[str, Interval]], dict[str, dict[str, Interval]]]:
    """95% ranges per system and metric, and ranges of (system - reference)."""
    labels = np.asarray(strata)
    groups = [np.flatnonzero(labels == g) for g in sorted(set(strata))]
    rng = np.random.default_rng(seed)
    values = {name: np.empty((resamples, len(HEADLINE))) for name in tables}
    for b in range(resamples):
        idx = np.concatenate([rng.choice(g, len(g)) for g in groups])
        for name, table in tables.items():
            result = headline(table, idx)
            values[name][b] = [result[m] for m in HEADLINE]
    intervals = {name: _ranges(v) for name, v in values.items()}
    differences = {}
    if reference is not None and reference in values:
        differences = {name: _ranges(v - values[reference]) for name, v in values.items() if name != reference}
    return intervals, differences


def mcnemar_exact(first_correct: Sequence[bool], second_correct: Sequence[bool]) -> dict[str, float | int]:
    """Two-sided exact McNemar test on paired right/wrong outcomes."""
    a, b = np.asarray(first_correct, dtype=bool), np.asarray(second_correct, dtype=bool)
    if len(a) != len(b):
        raise ValueError("paired outcomes must have the same length")
    only_first, only_second = int((a & ~b).sum()), int((~a & b).sum())
    n = only_first + only_second
    if n == 0:
        return {"only_first_correct": 0, "only_second_correct": 0, "p_value": 1.0}
    k = min(only_first, only_second)
    tail = sum(math.comb(n, i) for i in range(k + 1)) / 2**n
    return {"only_first_correct": only_first, "only_second_correct": only_second, "p_value": min(1.0, 2 * tail)}


def answer_stability(runs: Sequence[dict[str, dict[str, bool] | None]]) -> dict[str, float | int] | None:
    """Across repeated runs of one system: how often did any answer to a case change?"""
    if len(runs) < 2:
        return None
    cases = [c for c in runs[0] if all(r.get(c) is not None for r in runs)]
    if not cases:
        return {"repeats": len(runs), "compared_cases": 0}
    changed = sum(any(r[c] != runs[0][c] for r in runs[1:]) for c in cases)
    return {"repeats": len(runs), "compared_cases": len(cases), "cases_with_changed_answers": changed,
            "changed_rate": changed / len(cases)}  # fmt: skip
