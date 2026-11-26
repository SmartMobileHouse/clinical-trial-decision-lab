"""The common contract every evaluated system follows.

A system gets a Task (one case packet plus the frozen question set) and returns
a Prediction: a yes/no answer per question, or a clear failure status, plus
latency, tokens and cost. Provider differences stay inside each adapter.

Adapted from Fraud Decision Lab v0.2.0 (`fraudlab/providers/base.py`): the single
fraud score became a set of answers, and probabilities are kept only when a
provider actually reports them.
"""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from typing import Any, Literal

from triallab.questions import QuestionSet

Status = Literal["ok", "error", "timeout", "refusal", "invalid", "rate_limited", "not_run", "permission_blocked"]
Execution = Literal["local", "native", "gateway", "dry_run", "mock"]
DECISION_THRESHOLD = 0.5  # fixed before any model was run: probability of "yes" at or above this is a "yes"


@dataclass(frozen=True)
class Task:
    """Everything a system may see for one case. Identical for every system."""

    case_id: str  # for our records only; adapters must never send it
    state: dict[str, Any]
    payload_hash: str
    questions: QuestionSet


@dataclass(frozen=True)
class Prediction:
    case_id: str
    provider: str
    model_requested: str
    model_reported: str | None
    answers: dict[str, bool] | None  # question id -> yes/no; None when the call failed
    probabilities: dict[str, float] | None  # only when the provider reports probabilities; never invented
    evidence_refs: list[str] | None  # refs the system cited, when it can cite any
    status: Status
    execution: Execution
    attempts: int
    latency_ms: float | None  # last attempt only
    total_latency_ms: float | None  # all attempts, including retry waits
    input_tokens: int | None
    output_tokens: int | None
    cost_usd: float | None
    cost_source: Literal["reported", "usage_calculated", "estimated", "none"]
    request_id: str | None
    payload_hash: str
    error: str | None = None  # short, sanitised; never contains keys
    raw_answer: str | None = None  # original answer with credential redaction and a 4,000-character limit
    attempt_details: str | None = None  # JSON metadata for every HTTP attempt; never bodies or headers
    cost_unknown_attempts: int = 0
    cached_input_tokens: int | None = None

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Price:
    input_per_m: float
    output_per_m: float
    cached_input_per_m: float | None
    source: str
    retrieved: str = ""

    def cost(self, input_tokens: int, output_tokens: int, cached_tokens: int = 0) -> float:
        cached = min(cached_tokens, input_tokens) if self.cached_input_per_m is not None else 0
        return (
            (input_tokens - cached) * self.input_per_m
            + cached * (self.cached_input_per_m or 0.0)
            + output_tokens * self.output_per_m
        ) / 1_000_000


class MissingCredentials(RuntimeError):
    """A live provider was requested but its keys are not set."""


class DecisionProvider(ABC):
    """Base class for every system: rules, mock and provider adapters."""

    name: str
    model: str
    execution: Execution = "native"
    reports_probabilities: bool = False
    required_env: tuple[str, ...] = ()

    def credentials(self) -> dict[str, str]:
        missing = [k for k in self.required_env if not os.environ.get(k, "").strip()]
        if missing:
            raise MissingCredentials(f"{self.name}: missing {', '.join(missing)} (see .env.example)")
        return {k: os.environ[k].strip() for k in self.required_env}

    @abstractmethod
    async def evaluate(self, task: Task) -> Prediction:
        """Answer one task. Must never raise for provider-side problems: return a failure status instead."""


def blank_prediction(
    task: Task, provider: str, model: str, status: Status, error: str, execution: Execution
) -> Prediction:
    """A prediction for a case that was not answered (blocked, not run, adapter failure)."""
    return Prediction(
        case_id=task.case_id, provider=provider, model_requested=model, model_reported=None, answers=None,
        probabilities=None, evidence_refs=None, status=status, execution=execution, attempts=0, latency_ms=None,
        total_latency_ms=None, input_tokens=None, output_tokens=None, cost_usd=None, cost_source="none",
        request_id=None, payload_hash=task.payload_hash, error=error,
    )  # fmt: skip
