# Model register

Verification date: **2026-11-16**. This page mirrors `configs/models.yaml`, the machine-readable registry. If the two ever differ, the registry is right.

## Read this first

- **No model has been executed by Clinical Trial Decision Lab.** No paid API call has been made. Every result for a hosted model is pending.
- `executed_in_fraud_lab` means that Fraud Decision Lab ran this request format against the live API on 2026-11-06, with **one fraud question per request**. This project sends eight questions per request. That follows each provider's documented format but has not been run.
- `verified_from_docs` means the request and response shapes were read from the provider's official documentation on the verification date. Nothing was executed.
- `not_verified` models cannot be enabled.
- A dry run (`--dry-run`) checks that our request builder and parser agree with the documented shape, using fixture responses. It measures nothing.
- Prices are list prices in USD per 1 million tokens, read on the date shown. They are not invoices.
- The terms columns are our reading of published terms. They are not legal advice. See [DATA-LICENSING-AUDIT.md](DATA-LICENSING-AUDIT.md), section 12.
- Publishing a model's results needs an owner approval in the registry (`publication.approved`) on top of terms that allow it. It is `false` for every model today.

## Shared behaviour for every hosted model

| Topic | Behaviour |
|---|---|
| Request batching | One case per request. All questions of the case go in that request. No batch endpoint is used. |
| Timeout | 60 seconds per attempt. |
| Retries | Up to 2 retries on HTTP 429, 500, 502, 503, 504, 529 and on timeouts or network errors. Jittered exponential backoff; a `Retry-After` header is honoured, capped at 20 seconds. Never retried: 400, 401, 403, 404, 413, 415, 422. |
| Gateway retries | Opper also retries once on its own side. Gateway timing therefore includes gateway processing and is reported separately from the native route. |
| Latency | End to end from the calling machine: network, any gateway, and the model. Reported as such. |
| Token usage | Read from each response's `usage` block when the provider reports one. A call without usage is counted at its cost reservation and marked as estimated. |
| Context limits | An input above 90% of a model's context is refused before sending and recorded as `invalid`. Evidence is never truncated. |
| Sampling | Provider defaults, except parameters listed per model. |
| Secrets | Read from the environment only. Never written to run files. |
| Probabilities | Kept only when the provider returns them. A yes/no is the probability at or above 0.5, fixed before any run. General LLMs return yes/no only; no probability is invented for them. |

## Overview

| Id | Model | Identifier | Route | Enabled | Interface status | Input price | Publish benchmarks (our reading) |
|---|---|---|---|---|---|---|---|
| `jev` | TypeSafe Jev 1.14 | `jev-1.14.0` | native | yes | executed_in_fraud_lab | $0.042 | UNCLEAR |
| `openai_decisions` | OpenAI Decisions (GPT-6 Luna) | `gpt-6-luna` | native | yes | executed_in_fraud_lab | $0.1 | ALLOWED |
| `clef` | Cloudflare Clef | `@cf/cloudflare/clef` | native | yes | executed_in_fraud_lab | $0.24 | ALLOWED |
| `clef_flash` | Cloudflare Clef-flash | `@cf/cloudflare/clef-flash` | native | yes | executed_in_fraud_lab | $0.038 | ALLOWED |
| `pplx_decider` | Perplexity Decider 1.2 | `pplx-decider-v1.2` | native | yes | verified_from_docs | $0.02 | REQUIRES PERMISSION |
| `pplx_decider_flash` | Perplexity Decider Flash 1.2 | `pplx-decider-flash-v1.2` | native | yes | verified_from_docs | $0.01 | REQUIRES PERMISSION |
| `nimble` | Bespoke Labs Nimble v4 Max | `nimble-v4-max` | native | **no** | verified_from_docs | $0.04 | UNCLEAR |
| `liquid_d1_ultra` | Liquid AI D1 Ultra | `d1-ultra` | native | **no** | verified_from_docs | $0.042 | UNCLEAR |
| `morph_reflex` | Morph reflex | `reflex` | native | yes | verified_from_docs | $0.042 | UNCLEAR |
| `microsoft_decision` | Microsoft Decision 1 (Preview) | `Microsoft-Decision-1` | native | **no** | not_verified | $0.042 | ALLOWED |
| `convai_laya` | Convai Laya | `convaiinnovations/laya` | native | **no** | not_verified | $0.0 | ALLOWED |
| `llm_openai` | Structured-output LLM (GPT-6 Luna) | `gpt-6-luna` | native | yes | executed_in_fraud_lab | $0.1 | ALLOWED |
| `llm_anthropic` | Structured-output LLM (Claude Haiku 5.5) | `claude-haiku-5-5` | native | yes | verified_from_docs | $0.1 | ALLOWED |
| `jev_via_opper` | TypeSafe Jev 1.14 via Opper | `typesafe/jev-1.14.0` | gateway (Opper) | yes | verified_from_docs | $0.042 | UNCLEAR |
| `jev_via_runware` | TypeSafe Jev 1.14 via Runware | `typesafe:jev@1.14` | gateway (Runware) | yes | verified_from_docs | $0.042 | UNCLEAR |

## Models

### TypeSafe Jev 1.14 (`jev`)

| Field | Value |
|---|---|
| Exact identifier | `jev-1.14.0` |
| Version pinning | Explicit version id. The aliases jev-latest and jev-preview move. |
| Provider | TypeSafe |
| Family | decision model |
| Endpoint | `https://api.typesafe.ai/v1/systemone` |
| Execution | native (direct provider API) |
| Authentication | `Authorization` header with `Bearer` scheme, key from `TYPESAFE_API_KEY` |
| Extra headers | none |
| Input and output format | System One: one JSON state plus named yes/no questions (`noul`); answer is a probability of yes per question |
| Multi-question | All questions of a case in one request |
| Reports probabilities | yes |
| Maximum context | 32,768 tokens |
| Batching | one case per request; all questions of the case in that request |
| Timeout and retries | 60 s per attempt; shared retry policy above |
| Configuration parameters | none beyond the request format |
| Price per 1M tokens | $0.042 input, $0.0 output |
| Pricing source | https://docs.typesafe.ai/models.md |
| Price verified | 2026-11-16 |
| Token usage | input and output tokens as reported by the provider, when reported |
| Commercial use | ALLOWED |
| Output publication | ALLOWED |
| Benchmark publication | UNCLEAR |
| Terms source | https://typesafe.ai/legal/mca |
| Terms verified | 2026-11-16 |
| Terms note | No benchmark clause. Confidentiality covers non-public information about the Services; no right to use name or logo. Ask TypeSafe in writing. |
| Publication approved by owner | no |
| Enabled | yes |
| Interface status | executed_in_fraud_lab |
| Interface note | Single-question requests were executed. Eight questions in one request follow the documented format but were not executed. |

### OpenAI Decisions (GPT-6 Luna) (`openai_decisions`)

| Field | Value |
|---|---|
| Exact identifier | `gpt-6-luna` |
| Version pinning | No dated snapshot is offered. The run date and the model field of each response are recorded. |
| Provider | OpenAI |
| Family | decision model |
| Endpoint | `https://api.openai.com/v1/decisions` |
| Execution | native (direct provider API) |
| Authentication | `Authorization` header with `Bearer` scheme, key from `OPENAI_API_KEY` |
| Extra headers | none |
| Input and output format | OpenAI Decisions: message input with a JSON part plus `predicate` questions; answer is a probability per question |
| Multi-question | All questions of a case in one request |
| Reports probabilities | yes |
| Maximum context | not limited by this registry (see provider documentation) |
| Batching | one case per request; all questions of the case in that request |
| Timeout and retries | 60 s per attempt; shared retry policy above |
| Configuration parameters | none beyond the request format |
| Price per 1M tokens | $0.1 input, $0.0 output, $0.01 cached input |
| Pricing source | https://developers.openai.com/api/docs/guides/decisions |
| Price verified | 2026-11-16 |
| Token usage | input and output tokens as reported by the provider, when reported |
| Commercial use | ALLOWED |
| Output publication | ALLOWED |
| Benchmark publication | ALLOWED |
| Terms source | https://openai.com/policies/services-agreement/ |
| Terms verified | 2026-11-16 |
| Terms note | Usage Policies allow model evaluation and benchmarking. Section 10 restricts public statements about the relationship and use of name or logo. Outputs must not train competing models. |
| Publication approved by owner | no |
| Enabled | yes |
| Interface status | executed_in_fraud_lab |
| Interface note | Single-question requests were executed. Refusal answers are handled per the current guide. |

### Cloudflare Clef (`clef`)

| Field | Value |
|---|---|
| Exact identifier | `@cf/cloudflare/clef`; request body uses `clef` |
| Version pinning | No version pinning is documented for the hosted model. The run date is recorded. |
| Provider | Cloudflare Workers AI |
| Family | decision model |
| Endpoint | `https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/ai/run/@cf/cloudflare/clef` (placeholders filled from `CLOUDFLARE_ACCOUNT_ID`) |
| Execution | native (direct provider API) |
| Authentication | `Authorization` header with `Bearer` scheme, key from `CLOUDFLARE_API_TOKEN` |
| Extra headers | none |
| Input and output format | System One: one JSON state plus named yes/no questions (`noul`); answer is a probability of yes per question |
| Multi-question | All questions of a case in one request |
| Reports probabilities | yes |
| Maximum context | 65,536 tokens |
| Batching | one case per request; all questions of the case in that request |
| Timeout and retries | 60 s per attempt; shared retry policy above |
| Configuration parameters | none beyond the request format |
| Price per 1M tokens | $0.24 input, $0.0 output |
| Pricing source | https://developers.cloudflare.com/workers-ai/platform/pricing/ |
| Price verified | 2026-11-16 |
| Token usage | input and output tokens as reported by the provider, when reported |
| Commercial use | ALLOWED |
| Output publication | ALLOWED |
| Benchmark publication | ALLOWED |
| Terms source | https://www.cloudflare.com/terms/ |
| Terms verified | 2026-11-16 |
| Terms note | Section 2.2.2 permits benchmark tests; published results must come with all information necessary to replicate them. |
| Publication approved by owner | no |
| Enabled | yes |
| Interface status | executed_in_fraud_lab |
| Interface note | Single-question requests were executed. The REST result envelope was observed in that run, not in the docs. |

### Cloudflare Clef-flash (`clef_flash`)

| Field | Value |
|---|---|
| Exact identifier | `@cf/cloudflare/clef-flash`; request body uses `clef-flash` |
| Version pinning | No version pinning is documented for the hosted model. The run date is recorded. |
| Provider | Cloudflare Workers AI |
| Family | decision model |
| Endpoint | `https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/ai/run/@cf/cloudflare/clef-flash` (placeholders filled from `CLOUDFLARE_ACCOUNT_ID`) |
| Execution | native (direct provider API) |
| Authentication | `Authorization` header with `Bearer` scheme, key from `CLOUDFLARE_API_TOKEN` |
| Extra headers | none |
| Input and output format | System One: one JSON state plus named yes/no questions (`noul`); answer is a probability of yes per question |
| Multi-question | All questions of a case in one request |
| Reports probabilities | yes |
| Maximum context | 24,576 tokens |
| Batching | one case per request; all questions of the case in that request |
| Timeout and retries | 60 s per attempt; shared retry policy above |
| Configuration parameters | none beyond the request format |
| Price per 1M tokens | $0.038 input, $0.0 output |
| Pricing source | https://developers.cloudflare.com/workers-ai/platform/pricing/ |
| Price verified | 2026-11-16 |
| Token usage | input and output tokens as reported by the provider, when reported |
| Commercial use | ALLOWED |
| Output publication | ALLOWED |
| Benchmark publication | ALLOWED |
| Terms source | https://www.cloudflare.com/terms/ |
| Terms verified | 2026-11-16 |
| Terms note | Same terms as Clef. |
| Publication approved by owner | no |
| Enabled | yes |
| Interface status | executed_in_fraud_lab |
| Interface note | Single-question requests were executed. |

### Perplexity Decider 1.2 (`pplx_decider`)

| Field | Value |
|---|---|
| Exact identifier | `pplx-decider-v1.2` |
| Version pinning | Explicit version id. Superseded by v1.3; the -latest alias moves and is not used. |
| Provider | Perplexity |
| Family | decision model |
| Endpoint | `https://api.perplexity.ai/v1/decisions` |
| Execution | native (direct provider API) |
| Authentication | `Authorization` header with `Bearer` scheme, key from `PERPLEXITY_API_KEY` |
| Extra headers | none |
| Input and output format | System One: one JSON state plus named yes/no questions (`noul`); answer is a probability of yes per question |
| Multi-question | All questions of a case in one request |
| Reports probabilities | yes |
| Maximum context | 256,000 tokens |
| Batching | one case per request; all questions of the case in that request |
| Timeout and retries | 60 s per attempt; shared retry policy above |
| Configuration parameters | none beyond the request format |
| Price per 1M tokens | $0.02 input, $0.0 output |
| Pricing source | https://docs.perplexity.ai/docs/getting-started/pricing.md |
| Price verified | 2026-11-16 |
| Token usage | input and output tokens as reported by the provider, when reported |
| Commercial use | ALLOWED |
| Output publication | REQUIRES PERMISSION |
| Benchmark publication | REQUIRES PERMISSION |
| Terms source | https://www.perplexity.ai/hub/legal/perplexity-api-terms-of-service |
| Terms verified | 2026-11-16 |
| Terms note | Output display is limited to Customer Applications; the usage policy bars competitive or similar products. Get written permission before publishing. |
| Publication approved by owner | no |
| Enabled | yes |
| Interface status | verified_from_docs |
| Interface note | Never executed by us. Web grounding mode is left off. |

### Perplexity Decider Flash 1.2 (`pplx_decider_flash`)

| Field | Value |
|---|---|
| Exact identifier | `pplx-decider-flash-v1.2` |
| Version pinning | Explicit version id. Superseded by v1.3. |
| Provider | Perplexity |
| Family | decision model |
| Endpoint | `https://api.perplexity.ai/v1/decisions` |
| Execution | native (direct provider API) |
| Authentication | `Authorization` header with `Bearer` scheme, key from `PERPLEXITY_API_KEY` |
| Extra headers | none |
| Input and output format | System One: one JSON state plus named yes/no questions (`noul`); answer is a probability of yes per question |
| Multi-question | All questions of a case in one request |
| Reports probabilities | yes |
| Maximum context | 256,000 tokens |
| Batching | one case per request; the provider answers each question separately and bills the state per question |
| Timeout and retries | 60 s per attempt; shared retry policy above |
| Configuration parameters | none beyond the request format |
| Price per 1M tokens | $0.01 input, $0.0 output |
| Pricing source | https://docs.perplexity.ai/docs/getting-started/pricing.md |
| Price verified | 2026-11-16 |
| Token usage | input and output tokens as reported by the provider, when reported |
| Commercial use | ALLOWED |
| Output publication | REQUIRES PERMISSION |
| Benchmark publication | REQUIRES PERMISSION |
| Terms source | https://www.perplexity.ai/hub/legal/perplexity-api-terms-of-service |
| Terms verified | 2026-11-16 |
| Terms note | Same terms as Decider 1.2. |
| Publication approved by owner | no |
| Enabled | yes |
| Interface status | verified_from_docs |
| Interface note | Never executed by us. |

### Bespoke Labs Nimble v4 Max (`nimble`)

| Field | Value |
|---|---|
| Exact identifier | `nimble-v4-max` |
| Version pinning | Explicit version id. Superseded by nimble-v4.1-max; nimble-latest moves. |
| Provider | Bespoke Labs |
| Family | decision model |
| Endpoint | `https://api.bespokelabs.ai/v1/systemone` |
| Execution | native (direct provider API) |
| Authentication | `Authorization` header with `Bearer` scheme, key from `BESPOKE_API_KEY` |
| Extra headers | none |
| Input and output format | System One: one JSON state plus named yes/no questions (`noul`); answer is a probability of yes per question |
| Multi-question | All questions of a case in one request |
| Reports probabilities | yes |
| Maximum context | 256,000 tokens |
| Batching | one case per request; all questions of the case in that request |
| Timeout and retries | 60 s per attempt; shared retry policy above |
| Configuration parameters | none beyond the request format |
| Price per 1M tokens | $0.04 input, $0.0 output |
| Pricing source | https://docs.bespokelabs.ai/nimble/pricing |
| Price verified | 2026-11-16 |
| Token usage | input and output tokens as reported by the provider, when reported |
| Commercial use | UNCLEAR |
| Output publication | UNCLEAR |
| Benchmark publication | UNCLEAR |
| Terms source | https://docs.bespokelabs.ai/nimble/overview.md |
| Terms verified | 2026-11-16 |
| Terms note | No terms of service page was found. |
| Publication approved by owner | no |
| Enabled | no: The hosted API terms are not public. Read and archive them at sign-up before any call. The open weights are CC BY-NC 4.0 and must not be self-hosted by a commercial company. |
| Interface status | verified_from_docs |
| Interface note | none |

### Liquid AI D1 Ultra (`liquid_d1_ultra`)

| Field | Value |
|---|---|
| Exact identifier | `d1-ultra` |
| Version pinning | Model id without a version; d1-ultra:latest is a moving alias. |
| Provider | Liquid AI |
| Family | decision model |
| Endpoint | `https://api.liquid.ai/decisions/v1/systemone` |
| Execution | native (direct provider API) |
| Authentication | `Authorization` header with `Bearer` scheme, key from `LIQUID_API_KEY` |
| Extra headers | none |
| Input and output format | System One: one JSON state plus named yes/no questions (`noul`); answer is a probability of yes per question |
| Multi-question | All questions of a case in one request |
| Reports probabilities | yes |
| Maximum context | 32,768 tokens |
| Batching | one case per request; all questions of the case in that request |
| Timeout and retries | 60 s per attempt; shared retry policy above |
| Configuration parameters | none beyond the request format |
| Price per 1M tokens | $0.042 input, $0.0 output |
| Pricing source | https://liquid.ai/pricing |
| Price verified | 2026-11-16 |
| Token usage | input and output tokens as reported by the provider, when reported |
| Commercial use | ALLOWED |
| Output publication | ALLOWED |
| Benchmark publication | UNCLEAR |
| Terms source | https://www.liquid.ai/terms-conditions |
| Terms verified | 2026-11-16 |
| Terms note | Use is for internal business purposes; the terms are silent on publishing benchmarks. Ask Liquid. |
| Publication approved by owner | no |
| Enabled | no: Standard endpoints may store prompts and use them to improve models, which would expose the frozen test set to training. Enable only on a zero-retention endpoint. |
| Interface status | verified_from_docs |
| Interface note | Liquid's pages disagree on whether the state is billed once or per question; measure before reporting cost. |

### Morph reflex (`morph_reflex`)

| Field | Value |
|---|---|
| Exact identifier | `reflex` |
| Version pinning | No versioned id exists. The run date is recorded. |
| Provider | Morph |
| Family | decision model |
| Endpoint | `https://api.morphllm.com/v1/systemone` |
| Execution | native (direct provider API) |
| Authentication | `Authorization` header with `Bearer` scheme, key from `MORPH_API_KEY` |
| Extra headers | none |
| Input and output format | System One: one JSON state plus named yes/no questions (`noul`); answer is a probability of yes per question |
| Multi-question | All questions of a case in one request |
| Reports probabilities | yes |
| Maximum context | 65,536 tokens |
| Batching | one case per request; all questions of the case in that request |
| Timeout and retries | 60 s per attempt; shared retry policy above |
| Configuration parameters | none beyond the request format |
| Price per 1M tokens | $0.042 input, $0.0 output, $0.002 cached input |
| Pricing source | https://www.morphllm.com/api/models/json?prices=list |
| Price verified | 2026-11-16 |
| Token usage | input and output tokens as reported by the provider, when reported |
| Commercial use | ALLOWED |
| Output publication | ALLOWED |
| Benchmark publication | UNCLEAR |
| Terms source | https://morphllm.com/privacy/tos |
| Terms verified | 2026-11-16 |
| Terms note | Subscription terms restrict 'benchmark farming' and evaluating competing models; reach for metered API use is unclear. Ask Morph. |
| Publication approved by owner | no |
| Enabled | yes |
| Interface status | verified_from_docs |
| Interface note | Never executed by us. Use metered API access, not a flat-rate subscription. |

### Microsoft Decision 1 (Preview) (`microsoft_decision`)

| Field | Value |
|---|---|
| Exact identifier | `Microsoft-Decision-1`; request body uses `<your-deployment-name>` |
| Version pinning | Model version 1 behind a customer deployment name; Preview. |
| Provider | Microsoft Foundry |
| Family | decision model |
| Endpoint | `{AZURE_FOUNDRY_ENDPOINT}/providers/microsoft/v1/systemone` (placeholders filled from `AZURE_FOUNDRY_ENDPOINT`) |
| Execution | native (direct provider API) |
| Authentication | `api-key` header, key from `AZURE_FOUNDRY_API_KEY` |
| Extra headers | none |
| Input and output format | System One: one JSON state plus named yes/no questions (`noul`); answer is a probability of yes per question |
| Multi-question | All questions of a case in one request |
| Reports probabilities | yes |
| Maximum context | 32,768 tokens |
| Batching | one case per request; all questions of the case in that request |
| Timeout and retries | 60 s per attempt; shared retry policy above |
| Configuration parameters | none beyond the request format |
| Price per 1M tokens | $0.042 input, $0.0 output |
| Pricing source | https://ai.azure.com/catalog/models/Microsoft-Decision-1 |
| Price verified | 2026-11-16 |
| Token usage | input and output tokens as reported by the provider, when reported |
| Commercial use | ALLOWED |
| Output publication | ALLOWED |
| Benchmark publication | ALLOWED |
| Terms source | https://www.microsoft.com/licensing/terms/product/ForOnlineServices/all |
| Terms verified | 2026-11-16 |
| Terms note | Benchmark disclosure requires replication information on request, and waives our own anti-benchmark terms if we offer a competing product. Preview service. |
| Publication approved by owner | no |
| Enabled | no: The documentation shows no literal response with probability fields, so the parser cannot be validated without a live call. Needs an Azure deployment name in body_model. |
| Interface status | not_verified |
| Interface note | none |

### Convai Laya (`convai_laya`)

| Field | Value |
|---|---|
| Exact identifier | `convaiinnovations/laya` |
| Version pinning | Open weights; pin a repository revision when self-hosting. |
| Provider | Convai Innovations (self-hosted) |
| Family | decision model |
| Endpoint | `{LAYA_BASE_URL}/v1/systemone` (placeholders filled from `LAYA_BASE_URL`) |
| Execution | native (direct provider API) |
| Authentication | `Authorization` header with `Bearer` scheme, key from `LAYA_API_KEY` |
| Extra headers | none |
| Input and output format | System One: one JSON state plus named yes/no questions (`noul`); answer is a probability of yes per question |
| Multi-question | All questions of a case in one request |
| Reports probabilities | yes |
| Maximum context | 1,024 tokens |
| Batching | one case per request; all questions of the case in that request |
| Timeout and retries | 60 s per attempt; shared retry policy above |
| Configuration parameters | none beyond the request format |
| Price per 1M tokens | $0.0 input, $0.0 output |
| Pricing source | https://huggingface.co/convaiinnovations/laya |
| Price verified | 2026-11-16 |
| Token usage | input and output tokens as reported by the provider, when reported |
| Commercial use | ALLOWED |
| Output publication | ALLOWED |
| Benchmark publication | ALLOWED |
| Terms source | https://huggingface.co/convaiinnovations/laya |
| Terms verified | 2026-11-16 |
| Terms note | Apache-2.0 weights. |
| Publication approved by owner | no |
| Enabled | no: No vendor-hosted API. The context is 512 to 1,024 tokens, far below one case packet, and evidence is never truncated. |
| Interface status | not_verified |
| Interface note | none |

### Structured-output LLM (GPT-6 Luna) (`llm_openai`)

| Field | Value |
|---|---|
| Exact identifier | `gpt-6-luna` |
| Version pinning | No dated snapshot is offered. The run date and reported model are recorded. |
| Provider | OpenAI |
| Family | general llm |
| Endpoint | `https://api.openai.com/v1/responses` |
| Execution | native (direct provider API) |
| Authentication | `Authorization` header with `Bearer` scheme, key from `OPENAI_API_KEY` |
| Extra headers | none |
| Input and output format | OpenAI Responses with a strict JSON schema: one boolean per question plus cited refs |
| Multi-question | All questions of a case in one request |
| Reports probabilities | no (yes/no only) |
| Maximum context | not limited by this registry (see provider documentation) |
| Batching | one case per request; all questions of the case in that request |
| Timeout and retries | 60 s per attempt; shared retry policy above |
| Configuration parameters | `reasoning_effort: none`, `max_output_tokens: 600` |
| Price per 1M tokens | $0.1 input, $0.5 output, $0.01 cached input |
| Pricing source | https://developers.openai.com/api/docs/pricing |
| Price verified | 2026-11-16 |
| Token usage | input and output tokens as reported by the provider, when reported |
| Commercial use | ALLOWED |
| Output publication | ALLOWED |
| Benchmark publication | ALLOWED |
| Terms source | https://openai.com/policies/services-agreement/ |
| Terms verified | 2026-11-16 |
| Terms note | Same terms as OpenAI Decisions. |
| Publication approved by owner | no |
| Enabled | yes |
| Interface status | executed_in_fraud_lab |
| Interface note | Executed with a one-number schema. The answers schema used here was not executed. |

### Structured-output LLM (Claude Haiku 5.5) (`llm_anthropic`)

| Field | Value |
|---|---|
| Exact identifier | `claude-haiku-5-5` |
| Version pinning | The model id is a pinned snapshot. |
| Provider | Anthropic |
| Family | general llm |
| Endpoint | `https://api.anthropic.com/v1/messages` |
| Execution | native (direct provider API) |
| Authentication | `x-api-key` header, key from `ANTHROPIC_API_KEY` |
| Extra headers | `anthropic-version: 2026-10-21` |
| Input and output format | Anthropic Messages with `output_config.format` JSON schema: one boolean per question plus cited refs |
| Multi-question | All questions of a case in one request |
| Reports probabilities | no (yes/no only) |
| Maximum context | not limited by this registry (see provider documentation) |
| Batching | one case per request; all questions of the case in that request |
| Timeout and retries | 60 s per attempt; shared retry policy above |
| Configuration parameters | `effort: low`, `thinking: disabled`, `max_tokens: 600` |
| Price per 1M tokens | $0.1 input, $0.5 output, $0.01 cached input |
| Pricing source | https://platform.claude.com/docs/en/about-claude/pricing |
| Price verified | 2026-11-16 |
| Token usage | input and output tokens as reported by the provider, when reported |
| Commercial use | ALLOWED |
| Output publication | ALLOWED |
| Benchmark publication | ALLOWED |
| Terms source | https://www.anthropic.com/legal/commercial-terms |
| Terms verified | 2026-11-16 |
| Terms note | No benchmarking clause. The services may not be used to build a competing product or train competing models. |
| Publication approved by owner | no |
| Enabled | yes |
| Interface status | verified_from_docs |
| Interface note | Never executed by us. Uses output_config.format with a JSON schema. |

### TypeSafe Jev 1.14 via Opper (`jev_via_opper`)

| Field | Value |
|---|---|
| Exact identifier | `typesafe/jev-1.14.0` |
| Version pinning | Full catalogue id, which never fails over to another endpoint. |
| Provider | TypeSafe |
| Family | decision model |
| Endpoint | `https://api.opper.ai/v3/compat/v1/systemone` |
| Execution | gateway via Opper (native counterpart: `jev`) |
| Authentication | `Authorization` header with `Bearer` scheme, key from `OPPER_API_KEY` |
| Extra headers | none |
| Input and output format | System One: one JSON state plus named yes/no questions (`noul`); answer is a probability of yes per question |
| Multi-question | All questions of a case in one request |
| Reports probabilities | yes |
| Maximum context | 32,768 tokens |
| Batching | one case per request; all questions of the case in that request |
| Timeout and retries | 60 s per attempt; shared retry policy above |
| Configuration parameters | none beyond the request format |
| Price per 1M tokens | $0.042 input, $0.0 output |
| Pricing source | https://opper.ai/models/decision-models.md |
| Price verified | 2026-11-16 |
| Token usage | input and output tokens as reported by the provider, when reported |
| Commercial use | ALLOWED |
| Output publication | UNCLEAR |
| Benchmark publication | UNCLEAR |
| Terms source | https://opper.ai/terms-of-service |
| Terms verified | 2026-11-16 |
| Terms note | Opper's terms do not address output ownership; upstream TypeSafe terms are assumed to apply. Catalogue price is shown rounded to cents. |
| Publication approved by owner | no |
| Enabled | yes |
| Interface status | verified_from_docs |
| Interface note | Never executed by us. The gateway retries once on its own; its timing includes gateway processing. |

### TypeSafe Jev 1.14 via Runware (`jev_via_runware`)

| Field | Value |
|---|---|
| Exact identifier | `typesafe:jev@1.14` |
| Version pinning | Explicit version in the gateway model id. |
| Provider | TypeSafe |
| Family | decision model |
| Endpoint | `https://api.runware.ai/v1/decisions` |
| Execution | gateway via Runware (native counterpart: `jev`) |
| Authentication | `Authorization` header with `Bearer` scheme, key from `RUNWARE_API_KEY` |
| Extra headers | none |
| Input and output format | System One: one JSON state plus named yes/no questions (`noul`); answer is a probability of yes per question |
| Multi-question | All questions of a case in one request |
| Reports probabilities | yes |
| Maximum context | 32,768 tokens |
| Batching | one case per request; all questions of the case in that request |
| Timeout and retries | 60 s per attempt; shared retry policy above |
| Configuration parameters | none beyond the request format |
| Price per 1M tokens | $0.042 input, $0.0 output |
| Pricing source | https://runware.ai/blog/jev-laya-and-the-emerging-role-of-decision-models |
| Price verified | 2026-11-16 |
| Token usage | input and output tokens as reported by the provider, when reported |
| Commercial use | ALLOWED |
| Output publication | ALLOWED |
| Benchmark publication | UNCLEAR |
| Terms source | https://runware.ai/terms |
| Terms verified | 2026-11-16 |
| Terms note | Model licence terms govern on conflict and were not shown for Jev; upstream TypeSafe terms are assumed to apply. |
| Publication approved by owner | no |
| Enabled | yes |
| Interface status | verified_from_docs |
| Interface note | Never executed by us. Whether the gateway enables long context is not documented. |

## Local systems

These need no keys and cost nothing. They are not in the registry file because they call no provider.

| Id | What it is |
|---|---|
| `rules` | The eight deterministic protocol rules on the structured record. Never reads note text. |
| `keyword` | A transparent keyword matcher for the regulatory-finding track. |
| `flag_all`, `flag_none` | Anchors: the result of flagging every case, or none. Not systems. |
| `mock` | Hash-based fake answers for tests. Never a measurement. |

## Drift noted on the verification date

Compared with the Fraud Decision Lab check of 2026-11-06:

- TypeSafe Jev, OpenAI Decisions, OpenAI Responses, Cloudflare Clef and Clef-flash: no change to endpoint, identifier or price.
- OpenAI Decisions is now generally available and accepts up to 400 questions per request. Answers can come back as a `refusal`; the adapter records that as a refusal, not as a score.
- Cloudflare Clef requires a `model` selector in the request body, accepts at most 64 questions, and truncates an over-long `state` silently. We refuse to send such inputs instead.
- Perplexity Decider 1.2 is no longer the latest: Decider 1.3 launched in November 2026 and the `-latest` aliases now point to it. Version 1.2 is still callable by name and is what the registry pins.
- Nimble v4 Max is no longer the latest: `nimble-v4.1-max` is the default and `nimble-latest` moved to it on 2026-11-05. `nimble-v4-max` still works.
- Liquid lists newer `d1.2` models on its pricing page only; their interface is not documented and not verified.
- Microsoft Decision 1 is still in Preview.

## Not verified

- Batch endpoints for any decision model.
- Most numeric rate limits.
- The literal response field names of Microsoft Decision 1.
- Whether Liquid bills the state once or once per question.
- The Cloudflare REST response envelope for Clef, beyond what Fraud Decision Lab observed in its own run.
- The Jev model licence shown by Runware, and whether Runware enables long context.

Full notes and sources: [research/appendix-c-model-providers.md](research/appendix-c-model-providers.md).

## Addendum of 2026-11-26: models of the screening study

`configs/models.yaml` remains the authoritative record. The tables above were not regenerated.

| Registry id | Change | Terms reading |
|---|---|---|
| `or_gemini_decision_1` | New entry. Google Gemini Decision 1 through OpenRouter, called only by the screening study's own runner. $0.10 per 1M input tokens, read 2026-11-26. | Commercial use ALLOWED; output and benchmark publication UNCLEAR. OpenRouter defers output rights to the model's own terms. Google's API terms do not address publishing test results and forbid using the service to develop competing models. |
| `nimble` | Identifier is `nimble-v4.1-max`. Called in the locked screening run of 2026-11-25. | Still UNCLEAR. No terms page was found on 2026-11-26 (two URLs returned 404; the documentation site has no terms link). The terms shown at sign-up were not kept. |

The pages were read through a summarising fetch tool, not as raw text. Re-read them at source on the release date.
