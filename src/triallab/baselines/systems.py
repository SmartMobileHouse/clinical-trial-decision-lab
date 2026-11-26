"""Local systems: the deterministic rules baseline, two anchors and the offline mock.

- `rules`       the eight protocol rules on the structured record (never reads note text)
- `flag_all`    answers "review needed" for every case; `flag_none` never does. Anchors, not systems.
- `keyword`     a transparent keyword matcher for the regulatory-finding track
- `mock`        hash-based fake answers for tests; never a measurement
"""

from __future__ import annotations

import hashlib
import re
import time

from triallab.clinical.rules import RULES_VERSION, evaluate_rules
from triallab.providers.base import DecisionProvider, Prediction, Task
from triallab.reference.derive import answers_from_findings
from triallab.schema import CasePacket


def _local(task: Task, name: str, model: str, answers: dict[str, bool] | None, started: float, **extra) -> Prediction:
    elapsed = (time.perf_counter() - started) * 1000
    return Prediction(
        case_id=task.case_id, provider=name, model_requested=model, model_reported=model, answers=answers,
        probabilities=None, evidence_refs=extra.get("evidence_refs"), status="ok" if answers is not None else "not_run",
        execution=extra.get("execution", "local"), attempts=0, latency_ms=elapsed, total_latency_ms=elapsed,
        input_tokens=None, output_tokens=None, cost_usd=0.0, cost_source="none", request_id=None,
        payload_hash=task.payload_hash, error=extra.get("error"),
    )  # fmt: skip


class RulesProvider(DecisionProvider):
    name = "rules"
    model = f"rules-v{RULES_VERSION}"
    execution = "local"

    async def evaluate(self, task: Task) -> Prediction:
        started = time.perf_counter()
        if task.questions.name != "triage":
            return _local(task, self.name, self.model, None, started, error="protocol rules need a case packet")
        packet = CasePacket.model_validate(task.state)
        findings = evaluate_rules(packet.protocol, packet.record)
        refs = sorted({r for f in findings for r in f.evidence_refs})
        return _local(task, self.name, self.model, answers_from_findings(findings), started, evidence_refs=refs)


ELIGIBILITY_WORDS = re.compile(
    r"inclusion|exclusion|eligib|did not meet|not meet the|enrolled .{0,40}criteri|randomi[sz]ed .{0,60}criteri", re.I
)
CONSENT_WORDS = re.compile(
    r"informed consent|consent form|consent document|reconsent|re-consent|\bICF\b|\bconsent", re.I
)


class KeywordProvider(DecisionProvider):
    """Finding track only: says yes when the text contains eligibility or consent vocabulary."""

    name = "keyword"
    model = "keyword-v1"
    execution = "local"

    async def evaluate(self, task: Task) -> Prediction:
        started = time.perf_counter()
        if task.questions.name != "finding":
            return _local(task, self.name, self.model, None, started, error="keyword rules need a finding text")
        text = str(task.state.get("finding_text", ""))
        answers = {
            "eligibility_issue": bool(ELIGIBILITY_WORDS.search(text)),
            "consent_issue": bool(CONSENT_WORDS.search(text)),
        }
        return _local(task, self.name, self.model, answers, started)


class ConstantProvider(DecisionProvider):
    """An anchor: the result of flagging every case, or none."""

    execution = "local"

    def __init__(self, flag: bool) -> None:
        self.flag = flag
        self.name = "flag_all" if flag else "flag_none"
        self.model = self.name

    async def evaluate(self, task: Task) -> Prediction:
        started = time.perf_counter()
        answers = dict.fromkeys(task.questions.ids, False)
        if self.flag and "review_needed" in answers:
            answers["review_needed"] = True
        elif self.flag:
            answers = dict.fromkeys(task.questions.ids, True)
        return _local(task, self.name, self.model, answers, started)


class MockProvider(DecisionProvider):
    """Deterministic fake answers for tests. Its numbers are NOT a measurement of any real model."""

    name = "mock"
    model = "mock-1"
    execution = "mock"
    reports_probabilities = True

    def __init__(self, seed: int = 0, fail_every: int = 0) -> None:
        self.seed = seed
        self.fail_every = fail_every
        self._calls = 0

    async def evaluate(self, task: Task) -> Prediction:
        self._calls += 1
        failed = bool(self.fail_every and self._calls % self.fail_every == 0)
        probabilities = {}
        for q in task.questions.ids:
            digest = hashlib.sha256(f"{self.seed}:{task.payload_hash}:{q}".encode()).digest()
            probabilities[q] = int.from_bytes(digest[:8], "big") / 2**64
        return Prediction(
            case_id=task.case_id, provider=self.name, model_requested=self.model, model_reported=self.model,
            answers=None if failed else {q: p >= 0.5 for q, p in probabilities.items()},
            probabilities=None if failed else probabilities, evidence_refs=None,
            status="error" if failed else "ok", execution="mock", attempts=1, latency_ms=0.0, total_latency_ms=0.0,
            input_tokens=0, output_tokens=0, cost_usd=0.0, cost_source="none", request_id=None,
            payload_hash=task.payload_hash, error="simulated failure" if failed else None,
        )  # fmt: skip
