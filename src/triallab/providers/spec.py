"""The model registry: one YAML file lists every model, how to call it, what it costs and what we may publish.

Adding or disabling a model is a change to configs/models.yaml only; benchmark
logic never names a model.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from triallab.config import MODEL_REGISTRY

Rights = Literal["ALLOWED", "PROHIBITED", "UNCLEAR", "REQUIRES PERMISSION"]


class RegistryError(ValueError):
    """The model registry is missing or invalid. The message says how to fix it."""


class PriceSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")
    input: float = Field(ge=0)  # USD per 1M input tokens
    output: float = Field(ge=0)
    cached_input: float | None = None
    source: str
    retrieved: str  # date the price page was read


class TermsSpec(BaseModel):
    """Our reading of the provider's terms on the verification date. Not legal advice."""

    model_config = ConfigDict(extra="forbid")
    commercial_use: Rights
    output_publication: Rights
    benchmark_publication: Rights
    source: str
    verified: str
    note: str = ""


class PublicationSpec(BaseModel):
    """An owner decision, separate from our reading of the terms."""

    model_config = ConfigDict(extra="forbid")
    approved: bool = False
    basis: str = ""

    @model_validator(mode="after")
    def _approval_needs_basis(self) -> PublicationSpec:
        if self.approved and not self.basis.strip():
            raise ValueError("publication.approved requires a basis recording who approved it and why")
        return self


class ModelSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(pattern=r"^[a-z0-9_]+$")
    label: str
    kind: Literal["system_one", "openai_decisions", "openai_responses", "anthropic_messages", "ollama_chat"]
    family: Literal["decision_model", "general_llm"]
    provider: str
    model: str  # exact identifier requested
    body_model: str | None = None  # value of "model" in the request body when it differs
    version_pinning: str  # how exactly the identifier pins a version
    endpoint: str
    endpoint_env: list[str] = Field(default_factory=list)  # {NAME} placeholders filled from the environment
    auth_env: str = ""  # empty: no credential is sent (a self-hosted model on this machine)
    auth_header: str = "Authorization"
    auth_scheme: str = "Bearer"
    extra_headers: dict[str, str] = Field(default_factory=dict)
    unwrap: Literal["none", "cloudflare"] = "none"
    execution: Literal["native", "gateway"] = "native"
    gateway: str | None = None
    native_counterpart: str | None = None  # registry id of the same model called directly
    max_context_tokens: int | None = None
    reports_probabilities: bool
    batching: str = "one case per request; all questions of the case in that request"
    timeout_s: float = 60.0
    parameters: dict[str, Any] = Field(default_factory=dict)
    enabled: bool
    disabled_reason: str = ""
    interface_status: Literal["executed_in_fraud_lab", "verified_from_docs", "not_verified"]
    interface_note: str = ""
    price: PriceSpec
    terms: TermsSpec
    publication: PublicationSpec = Field(default_factory=PublicationSpec)

    @model_validator(mode="after")
    def _checks(self) -> ModelSpec:
        if not self.enabled and not self.disabled_reason.strip():
            raise ValueError(f"{self.id}: a disabled model needs a disabled_reason")
        if self.enabled and self.interface_status == "not_verified":
            raise ValueError(f"{self.id}: a model whose interface is not verified cannot be enabled")
        if self.execution == "gateway" and not self.gateway:
            raise ValueError(f"{self.id}: gateway execution needs a gateway name")
        for name in self.endpoint_env:
            if "{" + name + "}" not in self.endpoint:
                raise ValueError(f"{self.id}: endpoint_env {name} is not used in the endpoint")
        return self

    @property
    def required_env(self) -> list[str]:
        return [name for name in dict.fromkeys([self.auth_env, *self.endpoint_env]) if name]

    @property
    def publishable(self) -> bool:
        """Results may be published only with an owner approval on top of terms that allow it."""
        return self.publication.approved and "PROHIBITED" not in (
            self.terms.output_publication,
            self.terms.benchmark_publication,
        )


class Registry(BaseModel):
    model_config = ConfigDict(extra="forbid")
    verified: str
    models: list[ModelSpec]

    @model_validator(mode="after")
    def _unique(self) -> Registry:
        ids = [m.id for m in self.models]
        if len(set(ids)) != len(ids):
            raise ValueError("model ids must be unique")
        for m in self.models:
            if m.native_counterpart and m.native_counterpart not in ids:
                raise ValueError(f"{m.id}: native_counterpart {m.native_counterpart!r} is not in the registry")
        return self

    def get(self, model_id: str) -> ModelSpec:
        for m in self.models:
            if m.id == model_id:
                return m
        raise RegistryError(f"unknown model {model_id!r}; see configs/models.yaml")

    @property
    def enabled(self) -> list[ModelSpec]:
        return [m for m in self.models if m.enabled]


def load_registry(path: Path = MODEL_REGISTRY) -> Registry:
    if not path.is_file():
        raise RegistryError(f"model registry not found: {path}")
    try:
        return Registry.model_validate(yaml.safe_load(path.read_text()))
    except (yaml.YAMLError, ValidationError) as exc:
        raise RegistryError(f"{path} is invalid: {exc}") from exc
