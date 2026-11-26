"""Build systems by name, and estimate what a call may cost."""

from __future__ import annotations

import httpx

from triallab.baselines.systems import ConstantProvider, KeywordProvider, MockProvider, RulesProvider
from triallab.providers.adapters import ADAPTERS, ConfiguredProvider
from triallab.providers.base import DecisionProvider, Task
from triallab.providers.common import estimate_tokens
from triallab.providers.spec import Registry

LOCAL_SYSTEMS = ("rules", "keyword", "flag_all", "flag_none")
OFFLINE_SYSTEMS = (*LOCAL_SYSTEMS, "mock")


def make_local(name: str) -> DecisionProvider:
    if name == "rules":
        return RulesProvider()
    if name == "keyword":
        return KeywordProvider()
    if name in ("flag_all", "flag_none"):
        return ConstantProvider(flag=name == "flag_all")
    if name == "mock":
        return MockProvider()
    raise ValueError(f"unknown local system {name!r}")


def make_remote(name: str, registry: Registry, client: httpx.AsyncClient, dry_run: bool = False) -> ConfiguredProvider:
    spec = registry.get(name)
    return ADAPTERS[spec.kind](spec, client, dry_run=dry_run)


def worst_case_cost(provider: DecisionProvider, task: Task, attempts: int = 3) -> float:
    """Conservative token-based estimate for reservations; not a guaranteed billing upper bound.

    Some decision models bill the state once per question, so the estimate multiplies by the question count.
    """
    if not isinstance(provider, ConfiguredProvider) or provider.dry_run:
        return 0.0
    per_question = estimate_tokens({"state": task.state, "context": task.questions.context})
    input_tokens = int(per_question * 1.5 + 400) * len(task.questions.questions)
    output_tokens = getattr(provider, "max_output_tokens", 64)
    return attempts * provider.price.cost(input_tokens, output_tokens)
