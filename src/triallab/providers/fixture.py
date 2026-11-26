"""Dry-run transport: provider-shaped fixture responses, no network, no keys.

`--dry-run` swaps the HTTP transport for this one. Every adapter still builds
its real request and parses a response in its provider's shape, so request
building, parsing, accounting and resume are exercised end to end.

The answers are derived from a hash of the request. They are NOT model output,
measure nothing, and are excluded from every report and export.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

import httpx


def _unit(seed: str) -> float:
    return int.from_bytes(hashlib.sha256(seed.encode()).digest()[:8], "big") / 2**64


def _usage(body: dict[str, Any], output: int = 0) -> dict[str, int]:
    return {"input_tokens": len(json.dumps(body)) // 3, "output_tokens": output}


def fixture_response(request: httpx.Request) -> httpx.Response:
    body = json.loads(request.content)
    seed = hashlib.sha256(request.content).hexdigest()
    url = str(request.url)
    if "state" in body:  # System One
        answers = {q: {"type": "noul", "noul": round(_unit(f"{seed}:{q}"), 4)} for q in body["questions"]}
        result: dict[str, Any] = {"model": body.get("model"), "answers": answers, "usage": _usage(body)}
        if "/ai/run/" in url:
            result = {"result": result, "success": True, "errors": [], "messages": []}
        return httpx.Response(200, json=result, headers={"x-request-id": f"dryrun-{seed[:12]}"})
    if isinstance(body.get("questions"), list):  # OpenAI Decisions
        answers_list = [
            {"type": "predicate", "name": q["name"], "probability": round(_unit(f"{seed}:{q['name']}"), 4)}
            for q in body["questions"]
        ]
        return httpx.Response(200, json={"model": body["model"], "answers": answers_list, "usage": _usage(body)})
    if "text" in body:  # OpenAI Responses
        ids = body["text"]["format"]["schema"]["properties"]["answers"]["required"]
        reply = json.dumps({"answers": {q: _unit(f"{seed}:{q}") >= 0.5 for q in ids}, "evidence_refs": []})
        message = {"type": "message", "content": [{"type": "output_text", "text": reply}]}
        return httpx.Response(
            200, json={"model": body["model"], "status": "completed", "output": [message], "usage": _usage(body, 40)}
        )
    if "format" in body and "messages" in body:  # Ollama chat
        ids = body["format"]["properties"]["answers"]["required"]
        reply = json.dumps({"answers": {q: _unit(f"{seed}:{q}") >= 0.5 for q in ids}, "evidence_refs": []})
        return httpx.Response(
            200,
            json={"model": body["model"], "message": {"role": "assistant", "content": reply}, "done_reason": "stop"},
        )
    if "messages" in body:  # Anthropic Messages
        ids = body["output_config"]["format"]["schema"]["properties"]["answers"]["required"]
        reply = json.dumps({"answers": {q: _unit(f"{seed}:{q}") >= 0.5 for q in ids}, "evidence_refs": []})
        return httpx.Response(
            200,
            json={
                "model": body["model"], "stop_reason": "end_turn",
                "content": [{"type": "text", "text": reply}], "usage": _usage(body, 40),
            },
        )  # fmt: skip
    return httpx.Response(400, json={"error": "fixture transport does not recognise this request"})


def fixture_transport() -> httpx.MockTransport:
    return httpx.MockTransport(fixture_response)
