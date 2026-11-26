"""Provider adapters against mocked HTTP: request shape, parsing, failures. Never the network."""

from __future__ import annotations

import json

import httpx
import pytest
import respx

from triallab.datasets import payload_hash
from triallab.providers.adapters import ADAPTERS, llm_schema, parse_llm_reply
from triallab.providers.base import MissingCredentials, Task
from triallab.providers.fixture import fixture_transport
from triallab.providers.registry import make_remote, worst_case_cost
from triallab.providers.spec import RegistryError, load_registry
from triallab.questions import load_question_set

QUESTIONS = load_question_set("triage")
STATE = {"packet_version": "1", "protocol": {"study_id": "STUDY-X"}, "record": {"participant_id": "P-1"}}
TASK = Task("SYN-X-0001", STATE, payload_hash(STATE), QUESTIONS)
REGISTRY = load_registry()


@pytest.fixture(autouse=True)
def _keys(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in ("TYPESAFE_API_KEY", "OPENAI_API_KEY", "CLOUDFLARE_API_TOKEN", "ANTHROPIC_API_KEY"):
        monkeypatch.setenv(name, "test-secret-value")
    monkeypatch.setenv("CLOUDFLARE_ACCOUNT_ID", "acct123")


def noul(p: float) -> dict:
    return {"type": "noul", "noul": p}


@respx.mock
async def test_system_one_request_and_response() -> None:
    route = respx.post("https://api.typesafe.ai/v1/systemone").mock(
        return_value=httpx.Response(
            200,
            json={
                "model": "jev-1.14.0",
                "answers": {q: noul(0.9 if q == "consent_issue" else 0.1) for q in QUESTIONS.ids},
                "usage": {"input_tokens": 1000, "output_tokens": 8},
            },
        )  # fmt: skip
    )
    async with httpx.AsyncClient() as client:
        pred = await make_remote("jev", REGISTRY, client).evaluate(TASK)
    body = json.loads(route.calls[0].request.content)
    assert body["model"] == "jev-1.14.0" and body["state"] == STATE
    assert set(body["questions"]) == set(QUESTIONS.ids)
    assert "SYN-X-0001" not in route.calls[0].request.content.decode()  # the case id is never sent
    assert body["questions"]["consent_issue"]["criteria"]["true"]
    assert pred.status == "ok" and pred.execution == "native"
    assert pred.answers["consent_issue"] is True and pred.answers["eligibility_issue"] is False
    assert pred.probabilities["consent_issue"] == 0.9
    assert pred.cost_usd == pytest.approx(1000 * 0.042 / 1e6) and pred.cost_source == "usage_calculated"


@respx.mock
async def test_threshold_is_inclusive_at_one_half() -> None:
    respx.post("https://api.typesafe.ai/v1/systemone").mock(
        return_value=httpx.Response(200, json={"answers": {q: noul(0.5) for q in QUESTIONS.ids}})
    )
    async with httpx.AsyncClient() as client:
        pred = await make_remote("jev", REGISTRY, client).evaluate(TASK)
    assert all(pred.answers.values()) and pred.cost_usd is None and pred.cost_unknown_attempts == 1


@respx.mock
async def test_cloudflare_envelope_and_account_in_url() -> None:
    route = respx.post("https://api.cloudflare.com/client/v4/accounts/acct123/ai/run/@cf/cloudflare/clef").mock(
        return_value=httpx.Response(
            200, json={"result": {"answers": {q: noul(0.2) for q in QUESTIONS.ids}}, "success": True}
        )
    )
    async with httpx.AsyncClient() as client:
        pred = await make_remote("clef", REGISTRY, client).evaluate(TASK)
    assert json.loads(route.calls[0].request.content)["model"] == "clef"
    assert pred.status == "ok" and not any(pred.answers.values())


@respx.mock
async def test_missing_or_invalid_probability_is_invalid_not_repaired() -> None:
    answers = {q: noul(0.2) for q in QUESTIONS.ids}
    answers["review_needed"] = {"type": "noul", "noul": 1.7}
    respx.post("https://api.typesafe.ai/v1/systemone").mock(return_value=httpx.Response(200, json={"answers": answers}))
    async with httpx.AsyncClient() as client:
        pred = await make_remote("jev", REGISTRY, client).evaluate(TASK)
    assert pred.status == "invalid" and pred.answers is None and "review_needed" in pred.error


async def test_oversized_input_is_refused_before_sending() -> None:
    big = Task("SYN-X-0002", {"blob": "x" * 400_000}, "h", QUESTIONS)
    async with httpx.AsyncClient() as client:
        pred = await make_remote("clef_flash", REGISTRY, client).evaluate(big)  # no route mocked: a send would fail
    assert pred.status == "invalid" and pred.attempts == 0 and "not sent" in pred.error


@respx.mock
async def test_http_failures_become_statuses() -> None:
    respx.post("https://api.typesafe.ai/v1/systemone").mock(return_value=httpx.Response(401, json={"error": "no"}))
    async with httpx.AsyncClient() as client:
        pred = await make_remote("jev", REGISTRY, client).evaluate(TASK)
    assert pred.status == "error" and pred.answers is None and "test-secret-value" not in json.dumps(pred.as_dict())


@respx.mock
async def test_openai_decisions_request_response_and_refusal() -> None:
    ok = [{"type": "predicate", "name": q, "probability": 0.8} for q in QUESTIONS.ids]
    route = respx.post("https://api.openai.com/v1/decisions").mock(
        return_value=httpx.Response(
            200, json={"model": "gpt-6-luna", "answers": ok, "usage": {"input_tokens": 10, "output_tokens": 0}}
        )
    )
    async with httpx.AsyncClient() as client:
        provider = make_remote("openai_decisions", REGISTRY, client)
        pred = await provider.evaluate(TASK)
        body = json.loads(route.calls[0].request.content)
        assert body["input"][0]["content"][1] == {"type": "input_json", "data": STATE}
        assert [q["name"] for q in body["questions"]] == list(QUESTIONS.ids)
        assert pred.status == "ok" and all(pred.answers.values())
        refused = [*ok[:-1], {"type": "refusal", "name": QUESTIONS.ids[-1]}]
        route.mock(return_value=httpx.Response(200, json={"answers": refused}))
        assert (await provider.evaluate(TASK)).status == "refusal"


@respx.mock
async def test_openai_llm_strict_json() -> None:
    reply = json.dumps(
        {"answers": dict.fromkeys(QUESTIONS.ids, False) | {"consent_issue": True}, "evidence_refs": ["CNS-1"]}
    )
    route = respx.post("https://api.openai.com/v1/responses").mock(
        return_value=httpx.Response(
            200,
            json={
                "model": "gpt-6-luna",
                "status": "completed",
                "usage": {"input_tokens": 900, "output_tokens": 50},
                "output": [{"type": "message", "content": [{"type": "output_text", "text": reply}]}],
            },
        )  # fmt: skip
    )
    async with httpx.AsyncClient() as client:
        pred = await make_remote("llm_openai", REGISTRY, client).evaluate(TASK)
    body = json.loads(route.calls[0].request.content)
    assert body["text"]["format"]["strict"] is True and body["store"] is False
    assert "probab" not in json.dumps(body["text"]["format"]["schema"])  # no probabilities are requested from an LLM
    assert pred.status == "ok" and pred.probabilities is None and pred.evidence_refs == ["CNS-1"]
    assert pred.cost_usd == pytest.approx((900 * 0.10 + 50 * 0.50) / 1e6)


@respx.mock
async def test_anthropic_llm_request_and_refusal() -> None:
    reply = json.dumps({"answers": dict.fromkeys(QUESTIONS.ids, False), "evidence_refs": []})
    route = respx.post("https://api.anthropic.com/v1/messages").mock(
        return_value=httpx.Response(
            200,
            json={
                "model": "claude-haiku-5-5",
                "stop_reason": "end_turn",
                "content": [{"type": "text", "text": reply}],
                "usage": {"input_tokens": 800, "output_tokens": 40},
            },
        )  # fmt: skip
    )
    async with httpx.AsyncClient() as client:
        provider = make_remote("llm_anthropic", REGISTRY, client)
        pred = await provider.evaluate(TASK)
        request = route.calls[0].request
        body = json.loads(request.content)
        assert (
            request.headers["x-api-key"] == "test-secret-value" and request.headers["anthropic-version"] == "2026-10-21"
        )
        assert body["model"] == "claude-haiku-5-5" and body["output_config"]["format"]["type"] == "json_schema"
        assert "temperature" not in body and body["thinking"] == {"type": "disabled"}
        assert pred.status == "ok" and not any(pred.answers.values())
        route.mock(return_value=httpx.Response(200, json={"stop_reason": "refusal", "content": []}))
        assert (await provider.evaluate(TASK)).status == "refusal"
        route.mock(
            return_value=httpx.Response(
                200, json={"stop_reason": "max_tokens", "content": [{"type": "text", "text": "{"}]}
            )
        )
        assert (await provider.evaluate(TASK)).status == "invalid"


def test_llm_reply_parsing_is_strict() -> None:
    ids = ("a", "b")
    assert parse_llm_reply('{"answers": {"a": true, "b": false}, "evidence_refs": []}', ids) == (
        {"a": True, "b": False},
        [],
    )
    assert isinstance(parse_llm_reply("not json", ids), str)
    assert isinstance(parse_llm_reply('{"answers": {"a": "yes", "b": false}, "evidence_refs": []}', ids), str)
    assert isinstance(parse_llm_reply('{"answers": {"a": true}, "evidence_refs": []}', ids), str)
    assert llm_schema(ids)["properties"]["answers"]["required"] == ["a", "b"]


async def test_missing_credentials_are_reported_by_name_only(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TYPESAFE_API_KEY")
    async with httpx.AsyncClient() as client:
        with pytest.raises(MissingCredentials, match="TYPESAFE_API_KEY"):
            await make_remote("jev", REGISTRY, client).evaluate(TASK)


async def test_every_enabled_model_parses_its_fixture_response_without_keys(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in (
        "TYPESAFE_API_KEY",
        "OPENAI_API_KEY",
        "CLOUDFLARE_API_TOKEN",
        "CLOUDFLARE_ACCOUNT_ID",
        "ANTHROPIC_API_KEY",
    ):
        monkeypatch.delenv(name, raising=False)
    async with httpx.AsyncClient(transport=fixture_transport()) as client:
        for spec in REGISTRY.enabled:
            provider = make_remote(spec.id, REGISTRY, client, dry_run=True)
            pred = await provider.evaluate(TASK)
            assert pred.status == "ok" and pred.execution == "dry_run", spec.id
            assert set(pred.answers) == set(QUESTIONS.ids)
            assert pred.cost_usd in (None, 0.0)  # fixture token counts never become a cost
            assert worst_case_cost(provider, TASK) == 0.0


def test_registry_rules() -> None:
    assert {m.kind for m in REGISTRY.models} <= set(ADAPTERS)
    # Owner approvals of 2026-11-26 cover the five hosted models of the screening study, and no other model.
    assert {m.id for m in REGISTRY.models if m.publishable} == {
        "pplx_decider_v13",
        "nimble",
        "llm_openai",
        "llm_anthropic",
        "or_gemini_decision_1",
    }
    for m in REGISTRY.models:
        assert m.enabled or m.disabled_reason
        assert not (m.enabled and m.interface_status == "not_verified")
        assert m.price.source.startswith("https://") and m.terms.source.startswith("https://")
    gateways = [m for m in REGISTRY.models if m.execution == "gateway"]
    # Jev is the only model measured both directly and through gateways; other gateway entries have no counterpart.
    assert gateways and all(m.native_counterpart in ("jev", None) for m in gateways)
    with pytest.raises(RegistryError):
        REGISTRY.get("no_such_model")
