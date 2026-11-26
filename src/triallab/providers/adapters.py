"""Provider adapters, one per request format. Which models exist is decided by configs/models.yaml.

Formats:
- `system_one`         state + questions, answers as probabilities (TypeSafe Jev, Cloudflare Clef and others)
- `openai_decisions`   OpenAI's /v1/decisions predicate questions
- `openai_responses`   a general LLM forced into strict JSON (OpenAI Responses API)
- `anthropic_messages` a general LLM forced into strict JSON (Anthropic Messages API)

Every adapter sends the same facts: the frozen question set and the case packet.
Only the serialization differs. Nothing is ever truncated: an input that does
not fit a model's context is refused before sending and recorded as `invalid`.

The System One and OpenAI adapters are adapted from Fraud Decision Lab v0.2.0
(`fraudlab/providers/system_one.py`, `fraudlab/providers/openai.py`). All calls go
through the shared HTTP layer so latency and retries are measured the same way;
that is why the Anthropic adapter uses plain HTTP rather than the vendor SDK.
"""

from __future__ import annotations

import json
import os
from typing import Any

import httpx

from triallab.core.http import post_json
from triallab.providers.base import MissingCredentials, Prediction, Price, Task
from triallab.providers.common import (
    HttpProvider,
    answers_from_probabilities,
    estimate_tokens,
    status_for_http_failure,
    valid_probability,
)
from triallab.providers.spec import ModelSpec
from triallab.questions import Question

DRY_RUN_SECRET = "dry-run-placeholder"  # noqa: S105 - not a credential; used only with the fixture transport


def question_instructions(context: str, question: Question) -> str:
    return f"{context}\n\nQuestion: {question.text}"


class ConfiguredProvider(HttpProvider):
    """An HTTP adapter whose model, endpoint, credentials and price come from the model registry."""

    def __init__(self, spec: ModelSpec, client: httpx.AsyncClient, dry_run: bool = False) -> None:
        price = Price(
            input_per_m=spec.price.input, output_per_m=spec.price.output,
            cached_input_per_m=spec.price.cached_input, source=spec.price.source, retrieved=spec.price.retrieved,
        )  # fmt: skip
        if dry_run:  # fixture token counts must never turn into a cost figure
            price = Price(0.0, 0.0, None, "dry run: no provider was called")
        super().__init__(client, price, timeout_s=spec.timeout_s)
        self.spec = spec
        self.name = spec.id
        self.model = spec.model
        self.dry_run = dry_run
        self.execution = "dry_run" if dry_run else spec.execution
        self.reports_probabilities = spec.reports_probabilities
        self.required_env = tuple(spec.required_env)
        self.max_context_tokens = spec.max_context_tokens

    def _env(self, name: str) -> str:
        if self.dry_run:
            return DRY_RUN_SECRET
        value = os.environ.get(name, "").strip()
        if not value:
            raise MissingCredentials(f"{self.name}: missing {name} (see .env.example)")
        return value

    def endpoint(self) -> str:
        url = self.spec.endpoint
        for name in self.spec.endpoint_env:
            placeholder = "{" + name + "}"
            value = "https://dry-run.invalid" if self.dry_run and url.startswith(placeholder) else self._env(name)
            url = url.replace(placeholder, value)
        return url

    def headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json", **self.spec.extra_headers}
        if self.spec.auth_env:
            key = self._env(self.spec.auth_env)
            headers[self.spec.auth_header] = f"{self.spec.auth_scheme} {key}" if self.spec.auth_scheme else key
        return headers

    def body(self, task: Task) -> dict[str, Any]:
        raise NotImplementedError

    def too_long(self, task: Task, body: dict[str, Any]) -> Prediction | None:
        if self.max_context_tokens and estimate_tokens(body) > 0.9 * self.max_context_tokens:
            return self._result(
                task, None, "invalid",
                error=f"input too long for {self.model} ({self.max_context_tokens:,}-token context); not sent",
            )  # fmt: skip
        return None

    async def call(self, body: dict[str, Any]):
        return await post_json(
            self.client, self.endpoint(), self.headers(), body, timeout_s=self.timeout_s, max_retries=self.max_retries
        )


class SystemOneProvider(ConfiguredProvider):
    def body(self, task: Task) -> dict[str, Any]:
        qs = task.questions
        return {
            "model": self.spec.body_model or self.spec.model,
            "state": task.state,  # the case itself; never the case ID or any label
            "questions": {
                q.id: {
                    "type": "noul",
                    "instructions": question_instructions(qs.context, q),
                    "criteria": {"true": q.criteria_true, "false": q.criteria_false},
                }
                for q in qs.questions
            },
        }

    def unwrap(self, body: Any) -> Any:
        # Cloudflare REST wraps the answer: {"result": {...}, "success": true, ...}. Bare shape also accepted.
        if self.spec.unwrap == "cloudflare" and isinstance(body, dict) and "answers" not in body:
            return body.get("result") if isinstance(body.get("result"), dict) else body
        return body

    async def evaluate(self, task: Task) -> Prediction:
        body = self.body(task)
        if (refused := self.too_long(task, body)) is not None:
            return refused
        outcome = await self.call(body)
        if outcome.error or outcome.status_code != 200:
            return self._result(task, outcome, status_for_http_failure(outcome))
        data = self.unwrap(outcome.body)
        if not isinstance(data, dict):
            return self._result(task, outcome, "invalid", error="response is not a JSON object", raw_answer=data)
        usage = data.get("usage") if isinstance(data.get("usage"), dict) else None
        reported = data.get("model") if isinstance(data.get("model"), str) else None
        raw = data.get("answers")
        answers: dict[str, Any] = raw if isinstance(raw, dict) else {}
        probabilities: dict[str, float] = {}
        for qid in task.questions.ids:
            item = answers.get(qid)
            answer: dict[str, Any] = item if isinstance(item, dict) else {}
            p = valid_probability(answer.get("noul"))
            if p is None:
                return self._result(
                    task, outcome, "invalid", usage=usage, model_reported=reported,
                    error=f"answer for {qid} missing or not a probability in [0, 1]", raw_answer=answers or data,
                )  # fmt: skip
            probabilities[qid] = p
        return self._result(
            task, outcome, "ok", answers=answers_from_probabilities(probabilities), probabilities=probabilities,
            usage=usage, model_reported=reported, raw_answer=answers,
        )  # fmt: skip


class OpenAIDecisionsProvider(ConfiguredProvider):
    def body(self, task: Task) -> dict[str, Any]:
        qs = task.questions
        return {
            "model": self.spec.model,
            "input": [
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": qs.context},
                        {"type": "input_json", "data": task.state},
                    ],
                }
            ],
            "questions": [
                {
                    "type": "predicate",
                    "name": q.id,
                    "instructions": f"{q.text}\nAnswer yes if: {q.criteria_true}\nAnswer no if: {q.criteria_false}",
                }
                for q in qs.questions
            ],
        }

    async def evaluate(self, task: Task) -> Prediction:
        outcome = await self.call(self.body(task))
        if outcome.error or outcome.status_code != 200:
            return self._result(task, outcome, status_for_http_failure(outcome))
        data = outcome.body if isinstance(outcome.body, dict) else {}
        usage = data.get("usage") if isinstance(data.get("usage"), dict) else None
        reported = data.get("model") if isinstance(data.get("model"), str) else None
        listed = [a for a in data.get("answers") or [] if isinstance(a, dict)]
        by_name = {a.get("name"): a for a in listed}
        extra: dict[str, Any] = {"usage": usage, "model_reported": reported, "raw_answer": listed or data}
        if any(a.get("type") == "refusal" for a in listed):
            return self._result(task, outcome, "refusal", error="model refused at least one question", **extra)
        probabilities: dict[str, float] = {}
        for qid in task.questions.ids:
            answer = by_name.get(qid) or {}
            p = valid_probability(answer.get("probability"))
            if answer.get("type") != "predicate" or p is None:
                return self._result(
                    task, outcome, "invalid", error=f"answer for {qid} missing or not a probability in [0, 1]", **extra
                )
            probabilities[qid] = p
        return self._result(
            task, outcome, "ok", answers=answers_from_probabilities(probabilities), probabilities=probabilities, **extra
        )


def llm_schema(question_ids: tuple[str, ...]) -> dict[str, Any]:
    """Strict JSON: one boolean per question plus the refs the model relied on. No probabilities are requested."""
    return {
        "type": "object",
        "properties": {
            "answers": {
                "type": "object",
                "properties": {q: {"type": "boolean"} for q in question_ids},
                "required": list(question_ids),
                "additionalProperties": False,
            },
            "evidence_refs": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Refs of the record items that support any yes answer; empty when all answers are no.",
            },
        },
        "required": ["answers", "evidence_refs"],
        "additionalProperties": False,
    }


def llm_instructions(task: Task) -> str:
    qs = task.questions
    lines = [qs.context, "", "Answer every question with true (yes) or false (no)."]
    for q in qs.questions:
        lines += ["", f"{q.id}: {q.text}", f"  true if: {q.criteria_true}", f"  false if: {q.criteria_false}"]
    lines += ["", "List in evidence_refs the refs of the items that support any true answer."]
    return "\n".join(lines)


def parse_llm_reply(reply: str, question_ids: tuple[str, ...]) -> tuple[dict[str, bool], list[str]] | str:
    """The answers and cited refs, or a short reason why the reply is unusable. Invalid output is never repaired."""
    try:
        parsed = json.loads(reply)
    except ValueError:
        return "reply is not valid JSON"
    answers = parsed.get("answers") if isinstance(parsed, dict) else None
    if not isinstance(answers, dict) or any(not isinstance(answers.get(q), bool) for q in question_ids):
        return "answers missing or not boolean for every question"
    refs = parsed.get("evidence_refs")
    if not isinstance(refs, list) or any(not isinstance(r, str) for r in refs):
        return "evidence_refs missing or not a list of strings"
    return {q: answers[q] for q in question_ids}, refs


class _LLMProvider(ConfiguredProvider):
    max_output_tokens = 600

    def _finish(self, task: Task, outcome: Any, reply: str, **extra: Any) -> Prediction:
        parsed = parse_llm_reply(reply, task.questions.ids)
        if isinstance(parsed, str):
            return self._result(task, outcome, "invalid", error=parsed, raw_answer=reply, **extra)
        answers, refs = parsed
        return self._result(task, outcome, "ok", answers=answers, evidence_refs=refs, raw_answer=reply, **extra)


class OpenAIResponsesProvider(_LLMProvider):
    def body(self, task: Task) -> dict[str, Any]:
        return {
            "model": self.spec.model,
            "instructions": llm_instructions(task),
            "input": [{"role": "user", "content": json.dumps({"case": task.state}, ensure_ascii=False)}],
            "reasoning": {"effort": self.spec.parameters.get("reasoning_effort", "none")},
            "max_output_tokens": self.max_output_tokens,
            "store": False,
            "text": {
                "format": {
                    "type": "json_schema", "name": "triage_answers", "strict": True,
                    "schema": llm_schema(task.questions.ids),
                }
            },
        }  # fmt: skip

    async def evaluate(self, task: Task) -> Prediction:
        outcome = await self.call(self.body(task))
        if outcome.error or outcome.status_code != 200:
            return self._result(task, outcome, status_for_http_failure(outcome))
        data = outcome.body if isinstance(outcome.body, dict) else {}
        extra: dict[str, Any] = {
            "usage": data.get("usage") if isinstance(data.get("usage"), dict) else None,
            "model_reported": data.get("model") if isinstance(data.get("model"), str) else None,
        }
        if data.get("status") not in (None, "completed"):
            reason = (data.get("incomplete_details") or {}).get("reason", data.get("status"))
            return self._result(
                task,
                outcome,
                "invalid",
                error=f"response not completed: {reason}",
                raw_answer=data.get("output"),
                **extra,
            )
        texts, refusal = [], None
        for item in data.get("output") or []:
            if not isinstance(item, dict) or item.get("type") != "message":
                continue
            for part in item.get("content") or []:
                if part.get("type") == "refusal":
                    refusal = part.get("refusal") or "refused"
                elif part.get("type") == "output_text":
                    texts.append(part.get("text", ""))
        if refusal is not None:
            return self._result(task, outcome, "refusal", error="model refused", raw_answer=refusal, **extra)
        return self._finish(task, outcome, "".join(texts), **extra)


class AnthropicMessagesProvider(_LLMProvider):
    def body(self, task: Task) -> dict[str, Any]:
        return {
            "model": self.spec.model,
            "max_tokens": self.max_output_tokens,
            "system": llm_instructions(task),
            "messages": [{"role": "user", "content": json.dumps({"case": task.state}, ensure_ascii=False)}],
            "thinking": {"type": "disabled"},  # a plain classification call, like reasoning effort "none" above
            "output_config": {
                "effort": self.spec.parameters.get("effort", "low"),
                "format": {"type": "json_schema", "schema": llm_schema(task.questions.ids)},
            },
        }

    async def evaluate(self, task: Task) -> Prediction:
        outcome = await self.call(self.body(task))
        if outcome.error or outcome.status_code != 200:
            return self._result(task, outcome, status_for_http_failure(outcome))
        data = outcome.body if isinstance(outcome.body, dict) else {}
        extra: dict[str, Any] = {
            "usage": data.get("usage") if isinstance(data.get("usage"), dict) else None,
            "model_reported": data.get("model") if isinstance(data.get("model"), str) else None,
        }
        content = [b for b in data.get("content") or [] if isinstance(b, dict)]
        reply = "".join(b.get("text", "") for b in content if b.get("type") == "text")
        stop = data.get("stop_reason")
        if stop == "refusal":
            return self._result(task, outcome, "refusal", error="model refused", raw_answer=reply or None, **extra)
        if stop not in (None, "end_turn"):
            return self._result(
                task, outcome, "invalid", error=f"response stopped early: {stop}", raw_answer=reply, **extra
            )
        return self._finish(task, outcome, reply, **extra)


class OllamaChatProvider(_LLMProvider):
    """An open-weight general LLM served by a local Ollama instance, forced into the answers schema.

    The context length is set explicitly: Ollama otherwise cuts long prompts to its default without saying so.
    """

    def body(self, task: Task) -> dict[str, Any]:
        return {
            "model": self.spec.model,
            "messages": [
                {"role": "system", "content": llm_instructions(task)},
                {"role": "user", "content": json.dumps({"case": task.state}, ensure_ascii=False)},
            ],
            "format": llm_schema(task.questions.ids),
            "stream": False,
            "think": bool(self.spec.parameters.get("think", False)),
            "options": {
                "temperature": self.spec.parameters.get("temperature", 0),
                "num_predict": self.max_output_tokens,
                "num_ctx": self.spec.max_context_tokens,
            },
        }

    async def evaluate(self, task: Task) -> Prediction:
        body = self.body(task)
        if (refused := self.too_long(task, body)) is not None:
            return refused
        outcome = await self.call(body)
        if outcome.error or outcome.status_code != 200:
            return self._result(task, outcome, status_for_http_failure(outcome))
        data = outcome.body if isinstance(outcome.body, dict) else {}
        raw = data.get("message")
        message: dict[str, Any] = raw if isinstance(raw, dict) else {}
        extra: dict[str, Any] = {"model_reported": data.get("model") if isinstance(data.get("model"), str) else None}
        if data.get("done_reason") not in (None, "stop"):
            return self._result(
                task, outcome, "invalid", error=f"response stopped early: {data.get('done_reason')}",
                raw_answer=message.get("content"), **extra,
            )  # fmt: skip
        return self._finish(task, outcome, str(message.get("content") or ""), **extra)


ADAPTERS: dict[str, type[ConfiguredProvider]] = {
    "system_one": SystemOneProvider,
    "openai_decisions": OpenAIDecisionsProvider,
    "openai_responses": OpenAIResponsesProvider,
    "anthropic_messages": AnthropicMessagesProvider,
    "ollama_chat": OllamaChatProvider,
}
