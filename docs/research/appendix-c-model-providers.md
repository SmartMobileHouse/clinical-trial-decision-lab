> Appendix C: research notes on decision-model providers, gateways and their terms. Unedited working notes, kept as supporting evidence for docs/DATA-LICENSING-AUDIT.md.
> Verification date: 2026-11-16. Quotes were collected by automated fetching; some passed through a summarising fetch tool or a reader proxy and may be clipped. Re-read every clause at its source before sign-off.
> Not legal advice. Local paths, individual warning-letter URLs, personal names of letter recipients and FDA staff, and email addresses were removed.

# Decision-model providers: interfaces, pricing, terms

Verification date: 2026-11-16. Read-only web research; no API was called, no account created, no data sent to providers.

## How to read this file

- Every fact below was read from a page fetched in this session. Source URLs are given inline.
- **Quote fidelity caveat.** Pages were read through a fetch tool that summarises with a small model. Text in quotation marks is what the tool returned as a quote; it is short and may be clipped. Before relying on any clause legally, open the URL and confirm the wording. The OpenAI Services Agreement and Usage Policies are the exception: openai.com returned HTTP 403 to direct fetches, so they were read as raw text through the public reader proxy `r.jina.ai` (only the public URL was sent). Those quotes are copied from the raw text, but came through an intermediary.
- Example bodies marked "illustrative" were rewritten by the fetch tool rather than copied; field names are from the docs, values are not. Take the exact JSON from the cited URL before coding against it.
- Classification legend for terms: ALLOWED / PROHIBITED / UNCLEAR / REQUIRES PERMISSION.
- This is not legal advice.

## 1. Drift versus the 2026-11-06 adapter assumptions

| Adapter | Status | Drift |
|---|---|---|
| TypeSafe Jev | No drift on endpoint, model, alias, price | `jev-latest` and `jev-preview` both point to `jev-1.14.0`. Nothing newer. Limits are stated as "64k per request / 32k per question" (we assumed only the 32,768 per-question figure). New since our note or not captured: `choice`, `score`, `box` types; long-context header raising both limits to 262k. |
| OpenAI Decisions | No drift on endpoint, model, price | API is now GA; questions per request raised to 400 (200 in beta). Answers may come back as `type: "refusal"` — the adapter must handle this instead of reading `answers[0].probability` blindly. Usage Policies revision effective 2026-11-20 (four days from now). |
| OpenAI Responses (gpt-6-luna) | No drift | $0.10 in / $0.01 cached / $0.50 out confirmed. Prompts over 272K input tokens are billed 2x input, 1.5x output. |
| Cloudflare Clef / Clef-flash | No drift on endpoint, price, context | Body requires a `model` field with value `"clef"` or `"clef-flash"` (selector, in addition to the URL). Max 64 questions per request. `state` is silently truncated to fit the context — a benchmark-validity risk. Both models are open weights (Apache 2.0). A third model `clef-omni` appears in Opper's catalogue; not checked on Cloudflare. |

Drift on the models we were asked to add:

- **Perplexity Decider 1.2 is no longer the latest.** `pplx-decider-v1.3` and `pplx-decider-flash-v1.3` launched in November 2026 and the `-latest` aliases now point to them. v1.2 models are still callable by name.
- **Nimble v4 Max is no longer the latest.** `nimble-v4.1-max` is the default; `nimble-latest` moved to it on 2026-11-05. `nimble-v4-max` still works.
- **Liquid D1 Ultra**: Liquid's pricing page now also lists `d1.2` and `d1.2-ultra` (Liquid Console only). They are absent from the docs pages, so their interface is not verified.
- **Morph reflex**: launch name was `d3-ultra`; still accepted as a model id.
- **Microsoft Decision 1**: still in Preview.

## 2. Per-model table

Prices are USD per 1M input tokens; all listed decision models charge nothing for output.

| # | Model | Exists | Model id to pin | Endpoint | Auth | System One format | Context | Price in | Interface verified |
|---|---|---|---|---|---|---|---|---|---|
| 1 | TypeSafe Jev 1.14 | Yes | `jev-1.14.0` (alias `jev-latest`) | `POST https://api.typesafe.ai/v1/systemone` | `Authorization: Bearer` | Native | 64k request / 32k per question; 262k with header | $0.042 | Yes |
| 2 | OpenAI Decisions | Yes (GA) | `gpt-6-luna` (no snapshots listed) | `POST https://api.openai.com/v1/decisions` | Bearer | No (own format) | Model: 1,050,000; decisions-specific limit not stated | $0.10 ($0.01 cached) | Yes |
| 3 | Cloudflare Clef | Yes | `@cf/cloudflare/clef` | `POST https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/@cf/cloudflare/clef` | Bearer API token | Yes (+ `model` selector) | 65,536 | $0.24 | Yes |
| 4 | Cloudflare Clef-flash | Yes | `@cf/cloudflare/clef-flash` | same pattern, `.../clef-flash` | Bearer API token | Yes | 24,576 | $0.038 | Yes |
| 5 | Perplexity Decider 1.2 | Yes (superseded by 1.3) | `pplx-decider-v1.2` | `POST https://api.perplexity.ai/v1/decisions` | Bearer (`x-api-key` rejected) | Yes | under 256K input tokens | $0.02 | Yes |
| 6 | Perplexity Decider Flash 1.2 | Yes (superseded by 1.3) | `pplx-decider-flash-v1.2` | same | Bearer | Yes | under 256K | $0.01 | Yes |
| 7 | Nimble v4 Max (Bespoke Labs) | Yes (superseded by v4.1) | `nimble-v4-max` | `POST https://api.bespokelabs.ai/v1/systemone` | Bearer, `BESPOKE_API_KEY` | Yes | 256k per question incl. state | $0.04 | Yes (schema); terms NOT found |
| 8 | Liquid AI D1 Ultra | Yes | `d1-ultra` (`d1-ultra:latest` is a moving alias) | `POST https://api.liquid.ai/decisions/v1/systemone` | Bearer, `LIQUID_API_KEY` | Yes | 32,768 tokens and 250 KB text | $0.042 | Yes |
| 9 | Morph reflex | Yes | `reflex` (no version; `d3-ultra` legacy) | `POST https://api.morphllm.com/v1/systemone` | Bearer `sk-...` | Yes | 65,536 | $0.042 ($0.002 cached) | Yes |
| 10 | Microsoft Decision 1 | Yes (Preview) | `Microsoft-Decision-1` version `1`; request `model` = your deployment name | `POST <foundry-resource-endpoint>/providers/microsoft/v1/systemone` | Entra ID Bearer or `api-key` header | Yes | 32,768 | $0.042 | Yes |
| 11 | Convai Laya | Yes, open weights only; no vendor-hosted API | `convaiinnovations/laya` (+ `multilingual`, `typed-decisions` subfolders) | self-host `laya-serve`: `POST /v1/systemone` on port 8000; or via gateways | none unless `LAYA_API_KEY` set | Yes | 512 (root), 1024 (typed-decisions), up to 8,192 (multilingual) | free self-hosted | Partly (no full response JSON in card) |
| 12a | OpenAI structured output | Yes | `gpt-6-luna` | `POST /v1/responses` | Bearer | n/a | 1,050,000 | $0.10 in / $0.50 out | Pricing and support verified; body not re-fetched |
| 12b | Anthropic structured output | Yes | `claude-haiku-5-5` (cheapest), `claude-sonnet-5-5`, `claude-opus-5-5`, `claude-fable-5-2` | `POST https://api.anthropic.com/v1/messages` | `x-api-key`, `anthropic-version: 2026-10-21` | n/a | 1M | Haiku 5.5: $0.10 in / $0.50 out up to 100k-token prompts | Yes |
| 13 | Opper gateway | Yes | see section 4 | `POST https://api.opper.ai/v3/compat/v1/systemone` and `/v3/compat/decisions` | Bearer project key | Both formats | per model | catalogue price | Yes |
| 14 | Runware gateway | Yes | `typesafe:jev@1.14`, `typesafe:jev@1`, `runware:laya@1` | `POST https://api.runware.ai/v1/decisions` | Bearer | TypeSafe format | per model | Jev $0.042, Laya $0.020 | Yes |

### Capability matrix

| Model | Multi-question per request | Categorical | Ordinal score | Abstention / unknown | Explanations / evidence | Probabilities |
|---|---|---|---|---|---|---|
| Jev 1.14 | Yes (max not stated) | `choice`, 1-255 options | `score`, 1-10 levels | No dedicated type; add an option yourself | None | noul prob; per-option probs + `confidence` |
| OpenAI Decisions | 1-400 | `choice` | `score`, 2-10 levels | `refusal` answer type exists; trigger conditions not documented | None | `probability`; `probabilities` + `confidence` |
| Clef / Clef-flash | 1-64 | `choice` | `score` | No | None | Yes |
| Perplexity v1.2 | Yes; **flash-v1.2 answers each question separately and bills `state` per question**; v1.2 questions see each other ("Grouping can help or hurt") | `choice`, 1-255 | `score`, 1-10 | No | `locate` spans (v1.3 only); `search_results` with `mode: "web_grounding"` | Yes |
| Nimble v4-max | 1-64 | `choice`, 2-255 | `score`, 2-255 | No | None | Yes |
| D1 Ultra | up to 128; each question billed as its own prompt | `choice`, 2-255 | `score`, 2-10 | No | None | Yes; noul also returns `confidence` |
| Morph reflex | Yes (max not stated) | `choice` | `score`, 2-10 | No | `diagnostics` (`label_mass`, `argmax_is_label`) only | Yes; noul also returns `probabilities` and `confidence` |
| Microsoft Decision 1 | Yes | `choice` | `score` | No type; docs advise: "Include an abstention option, such as `cannot tell`" | None ("doesn't generate ... written rationale") | Yes per docs prose; the one sample response shows only `choice` |
| Laya | Yes | `choice` (weak above ~20 options) | `score` (weakest primitive) | No | None | Yes, but card says models "ship over-confident" |

No decision model returns explanations. Abstention must be modelled as an extra `choice` option everywhere except OpenAI, which can return a `refusal`.

## 3. Per-model detail and example bodies

### 3.1 TypeSafe Jev 1.14

Sources: https://docs.typesafe.ai/api/system-one , https://docs.typesafe.ai/models.md , https://docs.typesafe.ai/changelog.md , https://docs.typesafe.ai/api/errors.md , https://docs.typesafe.ai/sdk/python/api/retries.md

- Models: `jev-1.14.0` (available from 2026-10-14), `jev-1.13.0`. Aliases `jev-latest` and `jev-preview` both point to `jev-1.14.0`. Response `model` "May differ from the alias supplied in the request." Pin `jev-1.14.0`.
- Headers: `TypeSafe-Danger-Zone-Long-Context: true` raises both limits to 262k (same price, documented as slower and less accurate). `TypeSafe-Danger-Zone-Images: true` needed for images and `box`.
- Limits: body 32 MiB; 64 nesting levels; gzip/zstd accepted. Max questions per request: not stated.
- Rate limits: per organization, numbers not published.
- Errors: 400 (`max_tokens_exceeded` when over context), 401, 413, 415, 422, 429, 529. Retry 429 and 529 with exponential backoff.
- SDK retry defaults: 2 retries, 0.5 s initial backoff doubling to max 5 s, retries 408/429/5xx, honours `Retry-After`, 30 s total budget.
- Batching: no batch endpoint; multiple questions per request.
- Data: Privacy Policy — "We will not train or fine tune any artificial intelligence or machine learning models on your prompts or other Input." ZDR "for enterprise customers" (https://docs.typesafe.ai/legal.md). DPA has no fixed retention period.

Request (from docs):
```json
{
  "model": "jev-latest",
  "state": "I was charged twice for my subscription this month. Please refund the extra charge.",
  "questions": {
    "billing": { "type": "noul", "instructions": "Is this message about billing?" }
  }
}
```
Response (from docs):
```json
{
  "model": "jev-latest",
  "answers": { "billing": { "type": "noul", "noul": 0.98 } },
  "usage": { "input_tokens": 120, "output_tokens": 12 }
}
```

### 3.2 OpenAI Decisions / gpt-6-luna

Sources: https://developers.openai.com/api/docs/guides/decisions , https://developers.openai.com/api/docs/pricing , https://developers.openai.com/api/docs/models/gpt-6-luna , https://developers.openai.com/api/docs/guides/your-data

- `gpt-6-luna` is "the only currently supported model". No dated snapshot is listed, so strict version pinning is not available.
- Input: string or message array. JSON goes in a user-message part `{"type": "input_json", "data": {...}}`. Question types `predicate`, `choice` (`choices` with `value`/`description`), `score` (`levels` with `label`/`description`).
- 1-400 questions per request. Prompt caching needs a 1,024-token prefix.
- Pricing: $0.10 uncached input, cached discounted, output not charged; "Regional processing premiums and long-context multipliers apply."
- Rate limits (model page): Build 5,000 RPM / 2M TPM; Launch 10,000 / 10M; Grow 30,000 / 180M. Whether these apply unchanged to `/v1/decisions`: not stated.
- Batch: `v1/batch` is supported for the model, but the decisions guide does not mention batch, and the model page does not list Decisions as an endpoint. Batch for `/v1/decisions`: COULD NOT VERIFY.
- Data: `/v1/decisions` row — not used for training; abuse-monitoring retention 30 days; ZDR eligible "with limitations". EU regional processing supported (premium applies).
- The guide shows only an "illustrative response excerpt"; full response envelope (`id`, `usage`) was not shown.

Request (abbreviated, from docs):
```json
{
  "model": "gpt-6-luna",
  "input": "I was charged twice for my order.",
  "questions": [
    {
      "type": "choice",
      "name": "department",
      "instructions": "Which department should handle this complaint?",
      "choices": [
        { "value": "billing", "description": "Payments, invoices, and refunds." },
        { "value": "other", "description": "Requests outside these categories." }
      ]
    }
  ]
}
```
Response excerpts (from docs):
```json
{ "answers": [ { "type": "predicate", "name": "visible_damage", "probability": 0.92 } ] }
```
```json
{
  "answers": [
    {
      "type": "choice", "name": "department", "choice": "billing",
      "probabilities": [ { "value": "billing", "probability": 0.95 }, { "value": "other", "probability": 0.05 } ],
      "confidence": 0.93
    }
  ]
}
```

### 3.3 / 3.4 Cloudflare Clef and Clef-flash

Sources: https://developers.cloudflare.com/workers-ai/models/clef/ , https://developers.cloudflare.com/workers-ai/models/clef-flash/ , https://developers.cloudflare.com/workers-ai/platform/pricing/ , https://developers.cloudflare.com/workers-ai/platform/limits/ , https://developers.cloudflare.com/workers-ai/platform/data-usage/

- Pricing rows: "@cf/cloudflare/clef | $0.240 per M input tokens | 21818 neurons per M input tokens"; "@cf/cloudflare/clef-flash | $0.038 per M input tokens | 3455 neurons per M input tokens". Free allocation 10,000 neurons/day.
- 1-64 questions; question ids max 100 chars from letters, digits, `_`, `.`, `-`. Types `noul`, `choice`, `score`. Optional `images` (max 4).
- Context 65,536 (clef), 24,576 (clef-flash). If questions plus media exceed it the request fails; otherwise **`state` is truncated to fit**.
- Rate limits: the limits page lists per-task limits and does not mention Clef. COULD NOT VERIFY a Clef-specific limit.
- Batch API exists for Workers AI but the page names no models. Clef batch support: COULD NOT VERIFY.
- No version pinning mechanism documented for the hosted model.
- Weights: `Cloudflare/clef` and `Cloudflare/clef-flash` on Hugging Face under Apache 2.0 (the LICENSE appendix carries an "Alibaba Cloud" copyright line).
- Data: "Cloudflare does not use Customer Content processed by Workers AI to train AI models."; "does not retain inputs or outputs after they are no longer needed".

Request (from clef-flash docs page):
```json
{
  "model": "clef-flash",
  "state": "Checkout has been failing for every customer for the last hour.",
  "questions": {
    "urgent": { "type": "noul", "instructions": "Is this support request urgent?" },
    "team": {
      "type": "choice",
      "instructions": "Which team should handle this request?",
      "criteria": {
        "billing": "Payments, invoices, and refunds",
        "technical": "Outages, errors, and configuration",
        "sales": "Plans and upgrades"
      }
    },
    "severity": {
      "type": "score",
      "instructions": "How severe is the customer impact?",
      "criteria": ["No impact", "Minor", "Major", "Critical"]
    }
  }
}
```
Response: the page documents `model`, `answers` (keyed by question id) and `usage`, with comments that `answers.urgent` is the probability, `answers.team` the "chosen team with per-option probabilities", `answers.severity` a "probability-weighted score (0 = lowest level)". A literal response JSON, and whether it is wrapped in Cloudflare's usual `{"result": ..., "success": ...}` REST envelope, was not captured — check the page before changing the adapter.

### 3.5 / 3.6 Perplexity Decider 1.2 and Decider Flash 1.2

Sources: https://docs.perplexity.ai/docs/decisions/quickstart , https://docs.perplexity.ai/api-reference/decisions-post.md , https://docs.perplexity.ai/docs/getting-started/pricing.md , https://docs.perplexity.ai/docs/resources/changelog.md

- Models: `pplx-decider-v1.3` (27B, alias `pplx-decider-latest`), `pplx-decider-flash-v1.3` (4B, alias `pplx-decider-flash-latest`), `pplx-decider-v1.2` (27B, no alias), `pplx-decider-flash-v1.2` (4B, no alias). `pplx-decider-v1.1-27b` and `pplx-decider-v1-27b` silently map to v1.2. The response `model` field echoes the name sent, so it cannot be used to detect remapping.
- Unknown top-level fields return 400. `x-api-key` returns 401. Trailing slash returns 404.
- Optional `mode: "web_grounding"` ($0.001 per search/fetch) — leave off for a closed benchmark.
- If `state` is a single URL the API fetches the page under web grounding; not relevant without that mode.
- Limits: under 256K input tokens; body 32 MiB; 255 options; 10 score levels.
- Rate limits: 10 requests/s per organization across models; v1.2 15M TPM / 900M TPH; flash-v1.2 4M TPM / 240M TPH. 429 carries `Retry-After`.
- Timeouts: 504 after about a minute; examples use a 30 s client timeout.
- Determinism: identical requests "may differ in the second decimal place".
- No batch endpoint. Data retention: not stated in the docs.
- Third-party reports say earlier Decider versions had open weights; this was NOT confirmed from a Perplexity source. Treat weight availability and licence as COULD NOT VERIFY.

Request (from docs, abbreviated there):
```json
{
  "model": "pplx-decider-latest",
  "state": {
    "title": "Battery died after two weeks",
    "review": "The headphones sound great, but the battery stopped charging after two weeks."
  },
  "questions": {
    "defect": { "type": "noul", "instructions": "Does the review report a product defect?" },
    "sentiment": {
      "type": "choice",
      "instructions": "What is the overall sentiment of the review?",
      "criteria": { "positive": "Mostly satisfied", "mixed": "Praise and complaints in one review", "negative": "Mostly dissatisfied" }
    }
  }
}
```
Response (from docs):
```json
{
  "model": "pplx-decider-latest",
  "answers": {
    "defect": { "type": "noul", "noul": 0.9424522889347015 },
    "sentiment": {
      "type": "choice", "choice": "mixed", "confidence": 0.9255246944002182,
      "probabilities": { "positive": 0.0206, "mixed": 0.9503, "negative": 0.0290 }
    }
  },
  "usage": { "input_tokens": 367, "output_tokens": 3 }
}
```
For our benchmark send `"model": "pplx-decider-v1.2"` / `"pplx-decider-flash-v1.2"` explicitly, and consider adding the v1.3 pair.

### 3.7 Nimble v4 Max (Bespoke Labs)

Sources: https://docs.bespokelabs.ai/api-reference/systemone.md , https://docs.bespokelabs.ai/nimble/pricing , https://docs.bespokelabs.ai/nimble/limits-and-errors.md , https://docs.bespokelabs.ai/nimble/overview.md , https://docs.bespokelabs.ai/nimble/quickstart.md , https://huggingface.co/bespokelabs/Nimble-v4-max , https://github.com/bespokelabsai/nimble

- Model ids: `nimble-v4.1-max` (default), `nimble-v4-max` (previous, still works), `nimble-latest` (moved to v4.1 on 2026-11-05), `nimble-v4` (deprecated, redirects to `nimble-v4-max`), `nimble-v3` (deprecated).
- Endpoint also reachable at `/v1/nimble/systemone`. Env var `BESPOKE_API_KEY`.
- Limits: body 1 MiB; 1-64 questions; 256k prompt tokens per question including state; "Nimble never cuts a prompt."
- Concurrency: 4 concurrent requests per organization until first credit purchase, then 100. The $1 sign-up credit does not count as a purchase.
- Errors: 401, 402 (no credit), 413, 422 (do not retry unchanged), 429 and 503 (honour `Retry-After`), 502, 504 (reduce questions/state), 529 (retry after ~1 s with backoff). "You are not charged for a request that gets an error."
- Price: $0.04 / 1M input, prepaid credit, output free.
- Weights: `bespokelabs/Nimble-v4-max` on Hugging Face is **CC BY-NC 4.0** — "so it may not be used for commercial purposes". Tags `v4.0` and `v4.1`. Base model Qwen/Qwen3.8-27B (Apache 2.0). Older 9B models are separate repos.
- Discrepancy: GitHub README mentions an 8,192-token limit (that refers to the 9B demo), while the hosted API docs say 256k.
- Data retention / training: not stated anywhere found.

Request (illustrative; field names from https://docs.bespokelabs.ai/api-reference/systemone.md):
```json
{
  "model": "nimble-v4-max",
  "state": "The package arrived with a cracked screen.",
  "questions": {
    "is_damaged": { "type": "noul", "instructions": "Is the item damaged?" }
  }
}
```
Response (illustrative):
```json
{
  "model": "nimble-v4-max",
  "answers": { "is_damaged": { "type": "noul", "noul": 0.97 } },
  "usage": { "input_tokens": 210, "output_tokens": 5 }
}
```

### 3.8 Liquid AI D1 Ultra

Sources: https://www.liquid.ai/blog/d1-ultra , https://docs.liquid.ai/api/reference/decision-models/make-decisions.md , https://docs.liquid.ai/api/guides/decisions.md , https://docs.liquid.ai/api/reference/rate-limits.md , https://docs.liquid.ai/api/guides/your-data.md , https://liquid.ai/pricing , https://docs.liquid.ai/lfm/help/model-license.md

- Released 2026-10-15 (per search snippet of the blog). Hosted only. Pin `d1-ultra`; `d1-ultra:latest` moves.
- Pricing page lists `d1-ultra` $0.042, `d1.1` $0.02, `d1.2` $0.02, `d1.2-ultra` $0.042. `d1.2` / `d1.2-ultra` are not in the docs: interface COULD NOT VERIFY.
- Limits: 128 questions; 250 KB text; 32,768 tokens for `d1-ultra` (65,536 for `d1`/`d1.1`); body 4.5 MB; over-limit returns 422.
- Billing inconsistency between Liquid pages: blog says "Each question is billed as its own prompt"; the API reference says state and images "count once, plus each question's own tokens". Measure `usage.input_tokens` (and `usage.cost`) before publishing cost numbers.
- The API does not accept zstd-compressed bodies (relevant if the TypeSafe SDK is reused).
- Rate limits: per organization per model, values only in Liquid Console. 429 has `Retry-After` and `x-ratelimit-*`.
- Data: "Liquid may save prompts and outputs and use them to improve our models and services." on standard endpoints. ZDR endpoints exist; whether `d1-ultra` has one: COULD NOT VERIFY.
- Open weights (`d1-2B`, `d1-omni-2B`, `d1-omni-600M`) are under the LFM Open License v1.0 — a revenue-threshold licence (see 5.8). D1 Ultra itself has no downloadable weights.

Request (illustrative; fields from the make-decisions reference):
```json
{
  "model": "d1-ultra",
  "state": "Customer reports payouts failing for three days.",
  "questions": {
    "is_urgent": { "type": "noul", "instructions": "Is this urgent?" }
  }
}
```
Response shape (documented fields; no literal JSON on the page): `model`, `answers.<id>` with `type`, `noul`, `confidence` (noul); `choice`, `probabilities`, `confidence` (choice); `score`, `legend`, `probabilities`, `confidence` (score); `usage.input_tokens`, `usage.output_tokens` (always 0), `usage.cost`.

### 3.9 Morph reflex

Sources: https://docs.morphllm.com/api-reference/endpoint/systemone , https://docs.morphllm.com/models/reflex , https://www.morphllm.com/api/models/json?prices=list , https://www.morphllm.com/zdr

- Model id `reflex`; no versioned id, so no pinning. Catalogue: context 65,536, $0.042 input, $0.002 cached, datacenters US, quantization bf16. (A search snippet quoting $0.01 cached is stale or wrong.)
- Extra top-level fields: `images` (max 16), `instructions` (context before the questions).
- Errors: 400, 401, 404 (unknown model), 422, 429, 503 ("Retry with exponential backoff"). `x-request-id` on every response.
- Rate limit numbers: not published. Base model: not stated officially.
- Do not confuse with Morph's older classifier product at `/v1/reflex/predict`.

Request (from docs, abridged there):
```json
{
  "model": "reflex",
  "state": "Stripe connection has failed for three days and sales are being lost.",
  "questions": {
    "is_urgent": { "type": "noul", "instructions": "The message conveys urgency or time sensitivity." }
  }
}
```
Response (from docs, abridged there):
```json
{
  "id": "dec-6f1c0b9e2a7d4c3e",
  "object": "structured_decision",
  "created": 1793577600,
  "model": "reflex",
  "answers": {
    "is_urgent": { "type": "noul", "noul": 0.97, "probabilities": { "yes": 0.97, "no": 0.03 }, "confidence": 0.96 }
  },
  "usage": { "input_tokens": 312, "output_tokens": 0, "input_tokens_details": { "cached_tokens": 256 } }
}
```

### 3.10 Microsoft Decision 1

Sources: https://learn.microsoft.com/en-us/azure/foundry/foundry-models/how-to/use-foundry-models-microsoft-decision , https://ai.azure.com/catalog/models/Microsoft-Decision-1 , https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/introducing-microsoft-decision-1-in-microsoft-foundry-for-decision-and-classific/4562742 , https://commandline.microsoft.com/microsoft-decision-1-model-foundry/

- Catalogue: "Lifecycle: Preview", version 1, text only, 32,768-token context, built on Qwen3.5-9B.
- Requires an Azure subscription and a Foundry deployment. Deployment types `GlobalStandard` and `DataZoneStandard` (US and EU data zones, both $0.042 input, output N/A).
- "The request's `model` value is your deployment name, not the underlying model name."
- Auth: Entra ID token for `https://cognitiveservices.azure.com` as Bearer, or `api-key: <key>` header.
- No api-version query parameter appears in the documented URL.
- Errors: 400, 401, 403, 404, 422, 429 ("Retry with exponential backoff, or request more quota"). Sample code uses a 60 s timeout. Quota numbers not stated.
- Catalogue lists as out of scope: "Sole automated decision-making in consequential areas such as credit, employment, housing, insurance, education, healthcare, or legal rights".

Request (from Learn):
```json
{
  "model": "<deployment-name>",
  "state": "The API returns 500 on every call.",
  "questions": {
    "team": {
      "type": "choice",
      "instructions": "Which team should handle this ticket?",
      "criteria": {
        "billing": "Charges, invoices, and refunds",
        "engineering": "Bugs, errors, and outages",
        "support": "How-to and account questions"
      }
    }
  }
}
```
Response: Learn says `noul` returns "A probability from 0 through 1", `choice` "One selected option and the probability for each option", plus deployed model name and token usage. The only literal sample (tech community blog) is `{"answers": {"team": {"type": "choice", "choice": "billing"}}}`. The exact probability field names (`noul`, `probabilities`) are inferred from the System One convention and were NOT shown literally — confirm with one live call before trusting the adapter.

### 3.11 Convai Laya

Sources: https://huggingface.co/convaiinnovations/laya , https://vercel.com/ai-gateway/models/laya , https://runware.ai/blog/jev-laya-and-the-emerging-role-of-decision-models

- Apache 2.0 open weights; encoder models (ModernBERT-large 421M; mmBERT-base 322M). `pip install laya`, `laya-serve` exposes `POST /v1/systemone` on `0.0.0.0:8000`, unauthenticated unless `LAYA_API_KEY` is set.
- No vendor-hosted API on the model card. Hosted routes seen: Runware `runware:laya@1` ($0.020), Opper `berget/convaiinnovations/laya` ($0.05, context 512), Vercel AI Gateway via Boundless ($0.0105, context 8,192 — not otherwise checked).
- Model card warnings: "Laya is a fast base to specialise, not a zero-shot decision engine."; models ship over-confident; root checkpoint English only; 512-token context on the root checkpoint.
- A 512-1024-token context will not fit FDA warning-letter text without chunking. A zero-shot result would mostly measure that limit; state it if Laya is included.

Request (from model card):
```json
{
  "state": {"document": "I was charged twice. Please fix this ASAP."},
  "questions": {"billing": {"type": "noul", "instructions": "Is this ticket about billing?"}}
}
```
Response: answers under `answers.<question>` with `choice` / `score` / `noul`, plus `routing` metadata. No literal JSON on the card.

### 3.12 Structured-output general LLMs

**OpenAI** — `gpt-6-luna` via `POST /v1/responses`: Responses supported, structured outputs supported, $0.10 in / $0.01 cached / $0.50 out, batch 50% off, context 1,050,000, max output 128,000. The `text.format` strict `json_schema` body was not re-fetched this session (https://developers.openai.com/api/docs/models/gpt-6-luna , https://developers.openai.com/api/docs/pricing).

**Anthropic** — sources https://platform.claude.com/docs/en/about-claude/models/overview , https://platform.claude.com/docs/en/build-with-claude/structured-outputs , https://platform.claude.com/docs/en/about-claude/pricing , https://platform.claude.com/docs/en/manage-claude/api-and-data-retention

| Model | API id | Input / output per MTok | Context | Max output |
|---|---|---|---|---|
| Claude Fable 5.2 | `claude-fable-5-2` | $8 / $40 | 1M | 128K |
| Claude Opus 5.5 | `claude-opus-5-5` | $4 / $20 | 1M | 128K |
| Claude Sonnet 5.5 | `claude-sonnet-5-5` | $2 / $10 | 1M | 128K |
| Claude Haiku 5.5 | `claude-haiku-5-5` | $0.10 / $0.50 for prompts up to 100,000 tokens; $0.50 / $2.50 above | 1M | 128K |

- "Every Claude model ID is a pinned snapshot". Batch API 50% off. Haiku 5.5 cache read $0.01.
- Structured outputs: `output_config.format` = `{"type": "json_schema", "schema": {...}}`; no beta header in the examples. `additionalProperties` must be `false`; numeric `minimum`/`maximum` are not supported, so a probability in [0,1] cannot be enforced by schema — validate client-side.
- Thinking is adaptive on current models, which affects latency and output-token cost comparisons.
- Data: "Retained data is never used for model training without your express permission."; conversation content "is not retained by default" except Covered Models (30 days); ZDR by arrangement.
- Haiku 5.5 is price-matched to gpt-6-luna and is the natural like-for-like candidate.

Request (from docs, shortened schema):
```json
{
  "model": "claude-opus-5-5",
  "max_tokens": 1024,
  "messages": [ { "role": "user", "content": "Extract the key information from this email: ..." } ],
  "output_config": {
    "format": {
      "type": "json_schema",
      "schema": {
        "type": "object",
        "properties": { "name": {"type": "string"}, "demo_requested": {"type": "boolean"} },
        "required": ["name", "demo_requested"],
        "additionalProperties": false
      }
    }
  }
}
```
Response: the text content block holds JSON matching the schema, e.g. `{"name": "John Smith", "demo_requested": true}`.

## 4. Gateways

### 4.1 Opper

Sources: https://docs.opper.ai/build/gateway/decision-models.md , https://opper.ai/models/decision-models.md , https://docs.opper.ai/overview/gateway.md , https://opper.ai/terms-of-service , https://opper.ai/data-processing-agreement

- Endpoints: `POST https://api.opper.ai/v3/compat/v1/systemone` (TypeSafe format) and `POST https://api.opper.ai/v3/compat/decisions` (OpenAI format). Bearer project key. Discovery: `GET https://api.opper.ai/v3/models?type=evaluation`.
- Proxies all of our targets. Catalogue ids and prices (input $/1M, as displayed, rounded to cents):

| Model | Opper id | Host / region | Price | Context |
|---|---|---|---|---|
| Jev 1.14 | `typesafe/jev-1.14.0` | TypeSafe, US | $0.04 | 64K |
| GPT-6 Luna Decisions | `openai/gpt-6-luna-decisions` | OpenAI, US | $0.10 | n/a |
| Clef | `cloudflare:global/clef`, `melious/clef` (Finland), `sference/clef` (EU) | | $0.24 / $0.22 / $0.24 | 16K |
| Clef-flash | `cloudflare:global/clef-flash`, `berget/Cloudflare/clef-flash` (Sweden), `melious/clef-flash`, `regolo/clef-flash` (Italy) | | $0.04 / $0.05 / $0.03 / $0.17 | 16K |
| Perplexity Decider 1.2 | `perplexity/pplx-decider-v1.2` | Perplexity | $0.02 | 262K |
| Perplexity Decider Flash 1.2 | `perplexity/pplx-decider-flash-v1.2` | Perplexity | $0.01 | 262K |
| Nimble v4 Max | `bespoke/nimble-v4-max` | Bespoke Labs | $0.04 | 256K |
| D1 Ultra | `liquid/d1-ultra` | Liquid, US | $0.04 | 33K |
| reflex | `morph/reflex` | Morph, US | $0.04 | 66K |
| Microsoft Decision 1 | `azure:eu/microsoft-decision-1`, `azure:global/microsoft-decision-1` | Azure | $0.04 | 33K |
| Laya | `berget/convaiinnovations/laya` | Berget, Sweden | $0.05 | 512 |

- Opper lists Clef at 16K context versus Cloudflare's own 65,536 / 24,576 — a real difference that would change results on long inputs.
- Other decision models in the catalogue we were not asked about: Gemini Decision 1, Clef-omni, Aplomb 1, Metis, REAX 1.3, Eevo-1, Blink, Mammoth 1, Rune.
- Markup: no statement. "Billing uses the catalog input and output token prices of the endpoint that answered". Most rows equal upstream list price after rounding. Cost per call is returned in `X-Opper-Cost`.
- Pool names (`clef`, `jev-1.14.0`, `gpt-6-luna-decisions`) may route across endpoints; full catalogue ids never fail over. Use full ids for a benchmark.
- Timeouts 60 s (120 s for Opper-hosted); one automatic retry on 429/502/503/504/timeout.
- Residency: "EU gateway hosting does not make every provider EU-hosted." DPA: gateway runs in AWS Stockholm; model inference is not restricted to the EEA by default.

### 4.2 Runware

Sources: https://runware.ai/docs/platform/compatible-apis , https://runware.ai/blog/jev-laya-and-the-emerging-role-of-decision-models , https://runware.ai/terms

- Endpoint `POST https://api.runware.ai/v1/decisions`, TypeSafe format, Bearer Runware key. TypeSafe SDKs work with base URL `https://api.runware.ai`; `model` must be set on every request.
- Models: `typesafe:jev@1.14` (Jev 1.14), `typesafe:jev@1` (Jev 1.13), `runware:laya@1`. None of the other decision models.
- Prices: Jev $0.042 (no markup versus TypeSafe), Laya $0.020.
- Limits and rate limits: not stated in the decisions section.
- The blog gives Jev 1.14 a 262,144-token window; TypeSafe documents 64k/32k by default with 262k only under the long-context header. Whether Runware sets that header: COULD NOT VERIFY.

## 5. Terms

Our use: commercial EU company, public publication of benchmark scores, per-case model outputs, latency and cost; synthetic clinical-trial data plus public FDA warning-letter text; no real patient data; research benchmark, no decisions about people.

### Summary matrix

| Provider | (a) Commercial use | (b) Publish outputs | (c) Publish benchmarks | (d) Clinical-compliance research benchmark |
|---|---|---|---|---|
| TypeSafe | ALLOWED | ALLOWED (ownership assigned) | UNCLEAR — no benchmark clause, but confidentiality covers "non-public information with respect to the Services" and no name/logo right | ALLOWED (no medical restriction found) |
| OpenAI | ALLOWED | ALLOWED | ALLOWED for benchmarking itself; naming OpenAI in "public statement about its relationship" restricted (s.10) | ALLOWED with care — human-review rule targets high-stakes automation |
| Cloudflare | ALLOWED | ALLOWED | ALLOWED WITH CONDITION — must publish everything needed to replicate | ALLOWED; no PHI |
| Perplexity | ALLOWED but narrow licence | UNCLEAR — Customer "owns all Output" yet display limited to "solely within the Customer Applications" | UNCLEAR — no clause; AUP bars competitive/similar products | ALLOWED for research; AUP limits automated decisions about individuals |
| Bespoke (Nimble API) | UNCLEAR — no terms found | UNCLEAR | UNCLEAR | UNCLEAR |
| Bespoke (Nimble-v4-max weights) | PROHIBITED (CC BY-NC 4.0) | n/a | n/a | n/a |
| Liquid (API) | ALLOWED ("internal business purposes") | ALLOWED (owns outputs) | UNCLEAR — main terms silent; other Liquid product terms require consent | ALLOWED for research; human review for significant decisions |
| Liquid (open d1 weights) | ALLOWED under $10M annual revenue; otherwise REQUIRES PERMISSION | n/a | n/a | n/a |
| Morph | ALLOWED | ALLOWED (owns output) | UNCLEAR — "benchmark farming" and evaluating competing models restricted for Subscriptions | ALLOWED (no medical clause) |
| Microsoft | ALLOWED | ALLOWED (Output Content is Customer Data) | ALLOWED WITH CONDITIONS — replication info on request; reciprocal benchmark waiver if we offer a competing product; Preview status | ALLOWED for decision support; catalogue excludes sole automated healthcare decisions |
| Convai Laya | ALLOWED (Apache 2.0) | ALLOWED | ALLOWED | ALLOWED |
| Anthropic | ALLOWED | ALLOWED | ALLOWED (no clause) — UNCLEAR only as to "competing product" reading | ALLOWED; high-risk rules apply to advice/decisions for individuals |
| Opper | ALLOWED | UNCLEAR on outputs (terms silent); upstream terms govern | ALLOWED (no clause) | Not addressed |
| Runware | ALLOWED (explicit) | ALLOWED | ALLOWED (no clause); Model Licence governs on conflict | Not addressed |

### 5.1 TypeSafe

Master Customer Agreement https://typesafe.ai/legal/mca (last updated Sep 23, 2026); AUP https://typesafe.ai/legal/acceptable-use-policy ; DPA https://typesafe.ai/legal/data-processing ; Privacy https://typesafe.ai/legal/privacy-policy

- (a) ALLOWED. s.2.1 "TypeSafe grants to Customer a limited, non-exclusive, non-transferable, non-sublicensable license during the Term."; s.2.2 includes "the right to include the API into one or more software applications developed and operated by Customer." Confidence: medium-high.
- (b) ALLOWED. s.4.2 "TypeSafe does not claim ownership of Input and TypeSafe disclaims ownership of Output." and "TypeSafe hereby assigns to Customer all of its right, title, and interest, if any, in the Output." Confidence: high.
- (c) UNCLEAR, leaning allowed. No benchmarking clause found. Risks: s.14.1 "Confidential Information includes the Access Credentials, Documentation, Customer's Fees and all pricing information." and "other non-public information with respect to the Services"; s.16.4 "Nothing in this Agreement grants either Party the right to use the name, brand, or logo of the other Party."; s.2.3(b) bars using the Services or Output to "develop (or to facilitate the development of) a similar or competing product or service." Publishing public list prices is not disclosing confidential pricing; negotiated prices would be. Confidence: medium.
- (d) ALLOWED. No medical/high-risk restriction in MCA or AUP. s.9.3 "CUSTOMER IS RESPONSIBLE FOR INDEPENDENTLY EVALUATING THE OUTPUT."
- (e) No training on Input (Privacy Policy; MCA s.4.1 "without Customer's prior consent"). s.4.3 "TypeSafe may Process Telemetry without restriction". DPA uses EU SCCs; retention "as long as necessary"; ZDR for enterprise only. Hosting region not stated (Opper lists the route as US).
- Open questions: if we sell or ship our own decision model, does s.2.3(b) reach a benchmark that helps position it? Is measured latency/accuracy "non-public information with respect to the Services"? Ask TypeSafe in writing.

### 5.2 OpenAI

Services Agreement https://openai.com/policies/services-agreement/ (Effective January 1, 2026); Usage Policies https://openai.com/policies/usage-policies/ (Effective November 20, 2026); data controls https://developers.openai.com/api/docs/guides/your-data . Read via reader proxy.

- (a) ALLOWED. Agreement is for "customers who are businesses and developers". Confidence: high.
- (b) ALLOWED. s.4.1 "Customer: (a) retains all ownership rights in Input; and (b) owns all Output. OpenAI hereby assigns to Customer all OpenAI's right, title, and interest, if any, in and to Output." Confidence: high.
- (c) ALLOWED. No benchmark restriction in s.3.3. Usage Policies: "You may use OpenAI models for research, software development, model evaluation and benchmarking, and product development, within these boundaries." Boundaries: s.3.3(e) "except for a Permitted Exception, use Output to develop artificial intelligence models that compete with OpenAI's products and services"; Usage Policies bar using outputs to supply "labels, scores, rankings, preferences, rewards, or corrections" as training signals for substitute models, and "They also apply when outputs from product use or evaluation are later used or supplied for those training purposes." Also s.10: neither party will "make any public statement about its relationship with the other Party or this Agreement" or use the other's name or logo "on their websites, media, or marketing materials" without written permission. Confidence: high on benchmarking; medium on how s.10 applies to naming OpenAI in a results table.
- (d) ALLOWED for a research benchmark. Usage Policies prohibit "automation of high-stakes actions in sensitive areas without human review" in areas including "medical" and "legal", and "building or offering AI tools that provide others with tailored advice that requires a license, without appropriate involvement by a licensed professional." Our benchmark automates no action. s.5.4 bars PHI without the Healthcare Addendum — not triggered by synthetic data.
- (e) s.4.2 "OpenAI will not use Customer Content to develop or improve the Services, unless Customer explicitly agrees". `/v1/decisions`: 30-day abuse-monitoring retention, ZDR eligible with limitations, EU regional processing available at a premium.
- Open questions: published per-case OpenAI outputs become public data that others could use for training; we are restricted from using them that way. Consider a notice in the dataset licence. If our company trains decision models, keep OpenAI outputs out of any training or data-selection pipeline.

### 5.3 Cloudflare (Clef, Clef-flash)

Self-Serve Subscription Agreement https://www.cloudflare.com/terms/ (Last Updated September 12, 2025); Developer Platform service-specific terms https://www.cloudflare.com/service-specific-terms-developer-platform/ (Workers AI section updated September 28, 2026); https://developers.cloudflare.com/workers-ai/platform/data-usage/ ; weights licence https://huggingface.co/Cloudflare/clef/blob/main/LICENSE

- (a) ALLOWED. No commercial-use limit; s.2.2.1(a) only bars reselling access. Confidence: high.
- (b) ALLOWED. "you retain all applicable intellectual property or other proprietary rights in Inputs and Outputs." Confidence: high.
- (c) ALLOWED WITH CONDITION. s.2.2.2 "You are permitted to perform benchmark tests of our Services." If results are published we must make available "all information necessary to replicate such benchmark tests." Our open-source MIT harness plus published synthetic data and configs should satisfy this; include model ids, dates, prompts, parameters. Confidence: high.
- (d) ALLOWED. No high-risk clause; s.2.2.1(i) restricts "protected health information" without written consent — not triggered.
- (e) "Unless otherwise agreed, Cloudflare does not use any Customer Content to train generative AI tools."; zero data retention commitment for standard inference. Models are "Third-Party Products" possibly "subject to additional terms" — for Clef the model licence is Apache 2.0.
- (f) Weights Apache 2.0: commercial use allowed, no benchmark or revenue clause.
- Open question: if Workers AI Clef were labelled beta, s.5 "Beta Services are intended for testing purposes only" would apply; the model pages did not show a beta label.

### 5.4 Perplexity

API Terms of Service https://www.perplexity.ai/hub/legal/perplexity-api-terms-of-service (Last updated January 23, 2026); AUP https://www.perplexity.ai/hub/legal/aup (Last updated July 8th, 2025)

- (a) ALLOWED but narrow. s.2.1 use is "on a non-exclusive, non-sublicensable and non-transferable basis", tied to Customer Applications. Confidence: medium.
- (b) UNCLEAR. s.2.3.1 Customer "owns all Output" and Perplexity "asserts no ownership rights in any Output", but s.2.1 limits display of Output to "solely within the Customer Applications". Whether a public GitHub dump of per-case answers is display "within the Customer Applications" is not settled by the text. Decider output is numeric probabilities, which lowers practical risk, but the clause is not content-specific. Confidence: low-medium.
- (c) UNCLEAR. No benchmark clause. s.2.5 lets Perplexity terminate an application that is "competitive with Perplexity"; AUP s.3.5 prohibits to "Create or make available any products or services competitive with, similar to, or that would otherwise be a substitute". A public comparative benchmark by a company in the decision-model space could be argued either way. Confidence: low-medium.
- (d) ALLOWED for research. AUP s.2.5 prohibits to "Make automated decisions about individuals that materially impact them"; s.2.4 restricts professional services "without appropriate professional oversight". ToS s.6.2 bars PHI without a BAA.
- (e) s.2.3.3 "Perplexity shall not use (or authorize third parties to use) Customer Content to train". Retention period not stated; DPA referenced in s.6.1.
- The API ToS predates the Decisions API (October 2026); no decision-specific terms were found.
- Recommendation: REQUEST WRITTEN PERMISSION before publishing per-case outputs and comparative results.

### 5.5 Bespoke Labs (Nimble)

- Hosted API terms: COULD NOT VERIFY. Tried https://www.bespokelabs.ai/terms (404), https://www.bespokelabs.ai/terms-of-service (404), https://console.bespokelabs.ai/terms (404), web search, and the docs index https://docs.bespokelabs.ai/llms.txt (no legal page). Only https://www.bespokelabs.ai/privacy-policy surfaced, and it states it does not cover processing within Nimble. Terms are presumably shown at console sign-up, which we did not do.
- (a)-(e) for the API: UNCLEAR. Read the console terms at sign-up before any call, and capture a copy.
- (f) Weights `bespokelabs/Nimble-v4-max`: CC BY-NC 4.0, "so it may not be used for commercial purposes" (https://huggingface.co/bespokelabs/Nimble-v4-max). As a commercial company we must not self-host these weights for the benchmark. Use the paid API only, subject to its terms. Confidence: high.

### 5.6 Liquid AI

Terms https://www.liquid.ai/terms-conditions (Last updated SEP 30, 2026; covers "Liquid Console, Liquid AI's hosted APIs and models"); https://docs.liquid.ai/api/guides/your-data.md ; LFM licence https://docs.liquid.ai/lfm/help/model-license.md , full text https://www.liquid.ai/lfm-license

- (a) ALLOWED. s.4 "you may access and use the Services for your internal business purposes." A public benchmark is arguably within internal purposes plus publication of our own outputs; "internal" is the word to watch. Confidence: medium.
- (b) ALLOWED. s.6 "you retain your rights in submitted materials and own the outputs." Confidence: medium-high.
- (c) UNCLEAR. Main terms are silent. s.7 bars to "use the Services or outputs to develop, train, fine-tune, or improve other AI models". Separate Liquid product terms (ShieldFlow, Pipette) reportedly restrict building a benchmark or comparative analysis for publication without consent — seen only in a search summary, not fetched, and they do not govern the API. That shows Liquid's stance, so ask. Confidence: low-medium.
- (d) ALLOWED for research. s.2 "You must not use the Services or outputs to make decisions that have a legal or similarly significant effect" on a person without human review.
- (e) **Standard endpoints: "Liquid may save prompts and outputs and use them to improve our models and services."** s.6 grants a "license to use Your Content to develop and improve Liquid AI's models". Our benchmark cases would be exposed to training unless a ZDR endpoint is used — this can contaminate future benchmark runs. Region and DPA not stated.
- (f) Open d1 weights (not D1 Ultra): LFM Open License v1.0 — "Free if your annual revenue is under $10 million USD"; above that a commercial licence is required. Revenue counted across the corporate group. REVENUE-THRESHOLD LICENCE.

### 5.7 Morph

Terms https://morphllm.com/privacy/tos (Version 4.3, Last Updated November 10, 2026); ZDR https://www.morphllm.com/zdr

- (a) ALLOWED. s.18.3 "Use Services only for legitimate business purposes." Confidence: medium.
- (b) ALLOWED. s.6.3 "Ownership: You own the output generated from your inputs." Confidence: high.
- (c) UNCLEAR, leaning allowed for pay-as-you-go API use. s.7.7.3 bars using a Subscription to generate "datasets or outputs for training, distilling, or evaluating competing models" and lists "benchmark farming" among restricted high-volume workloads. Those sit in the subscription-plan section; whether they reach metered API use, and whether benchmarking Reflex itself counts, is not clear from the excerpt. No rule on publishing results. Confidence: medium-low. Do not run the benchmark on a flat-rate subscription.
- (d) ALLOWED. No medical clause; s.9.3 "Services do not constitute professional advice of any kind."
- (e) s.5 "We do not use your code or content to train our models, on any tier."; retained up to 30 days; ZDR "on enterprise tiers only" after an addendum. Datacenters US. DPA and EU handling: not stated.

### 5.8 Microsoft

Product Terms, Online Services https://www.microsoft.com/licensing/terms/product/ForOnlineServices/all ; Preview supplemental terms https://azure.microsoft.com/support/legal/preview-supplemental-terms/ ; data https://learn.microsoft.com/en-us/azure/foundry/responsible-ai/openai/data-privacy

- (a) ALLOWED. Standard Azure commercial service. Confidence: high.
- (b) ALLOWED. "Output Content is Customer Data. Microsoft does not own Customer's Output Content." Confidence: high.
- (c) ALLOWED WITH CONDITIONS. Competitive Benchmarking clause: "If Customer offers a product or service competitive to an Online Service," then "by using the Online Service, Customer waives any restrictions on competitive use and benchmark testing" in its own product terms; and if Customer "discloses, directly or through third parties, any benchmarks or comparative tests or evaluations" it must provide on request "all information necessary to replicate such Benchmark". The tool also reported that Microsoft may ask for access to our competing product to run its own benchmarks. If our company offers a competing decision model, using Azure waives our own anti-benchmark terms. Confidence: medium-high (clause was returned in fragments — read it in full).
- Preview caveat: model is "Lifecycle: Preview". Product Terms: "PREVIEWS ARE PROVIDED "AS-IS," "WITH ALL FAULTS," AND "AS AVAILABLE,"" and "Certain Previews are subject to supplemental preview terms". Supplemental terms say generative AI previews "are not intended to be used in production or in a live operating environment." The confidentiality/no-publish language applies to "Early Access Previews" under NDA; Decision-1 is a public preview, so it should not apply. Label results as preview.
- (d) ALLOWED as decision support. Learn: for consequential decisions including healthcare "use the model for decision support with meaningful human review. Don't use it as the sole decision-maker." Product Terms high-risk clause concerns uses where interruption could cause death or injury; "at its own risk".
- (e) Prompts and completions "are NOT used to train any generative AI foundation models without your permission or instruction." EU DataZone keeps processing in EU member states. Microsoft DPA at https://aka.ms/DPA. Preview models "may employ different privacy practices".
- Also: restriction on using a generative AI service "to generate Output Content for the express purpose of creating synthetic training data" for competing systems.

### 5.9 Convai Laya

- (a)-(d) ALLOWED. Apache 2.0 weights (https://huggingface.co/convaiinnovations/laya); no use, benchmark or field-of-use restrictions. Confidence: high for self-hosting.
- (e) Self-hosted: no data leaves our machine. Through a gateway, that gateway's terms apply.

### 5.10 Anthropic

Commercial Terms https://www.anthropic.com/legal/commercial-terms ; Usage Policy https://www.anthropic.com/legal/aup (effective Nov 12, 2026)

- (a) ALLOWED. A.1 "Anthropic gives Customer permission to use the Services, including to power products and services".
- (b) ALLOWED. s.B Customer "owns its Outputs".
- (c) ALLOWED — no benchmarking clause. D.4: may not "access the Services to build a competing product or service" or use them "to train competing AI models or resell the Services". Confidence: medium-high.
- (d) ALLOWED for research. High-risk rules (healthcare, legal) require that "A qualified person must meaningfully review a High-risk AI Recommendation" and AI disclosure; they target advice and decisions delivered to individuals, not a synthetic benchmark.
- (e) "Anthropic may not train models on Customer Content from Services."; prompts and outputs not retained by default except Covered Models (30 days); ZDR by arrangement.

### 5.11 Opper

Terms https://opper.ai/terms-of-service (2026-07-07, Swedish law); DPA https://opper.ai/data-processing-agreement (2026-09-23)

- (a) ALLOWED. s.5.1 "non-exclusive, non-transferable right to access and use the Platform and the Services".
- (b) UNCLEAR. s.8.2 Customer "exclusively owns and reserves all right, title, and interest" in Customer Data; output ownership not addressed.
- (c) ALLOWED — no benchmarking or publication restriction found. Pass-through of upstream provider terms is not addressed in the excerpted text; assume upstream terms still bind use of each model, but note we would have no direct contract with the upstream provider.
- (d) Not addressed.
- (e) EU company, GDPR DPA, gateway in AWS Stockholm; deletion 30 days after termination; model inference not EEA-restricted by default; training use not addressed.

### 5.12 Runware

Terms https://runware.ai/terms (Last updated: 29 September 2026)

- (a) ALLOWED. s.10 "You may use the Services for lawful commercial purposes, including generating Outputs for commercial use."
- (b) ALLOWED. s.2 "As between you and Runware, you own your Outputs." and "Runware asserts no ownership of, and claims no intellectual property rights in, your Outputs."
- (c) ALLOWED — no benchmarking clause. But s.2 "Each Model is made available subject to its applicable licence terms" and "Where there is a conflict between these Terms and a Model Licence, the Model Licence governs." The Jev Model Licence/Model Rules were not shown on the Runware model page: COULD NOT VERIFY what they say. Note s.2 also bars republishing Runware "Content or Marks" (their site content, not our outputs).
- (d) No clause; s.1 "The Services are not tailored to comply with industry-specific regulations".
- (e) s.4 "Runware will use your Customer Material solely to provide, secure and support the Services for you."; outputs not retained long-term; site claims EU and US data residency.

## 6. Unresolved questions and recommended actions

1. **Bespoke Labs API terms** — not public. Read and archive at sign-up; do not call the API before that. Never self-host `Nimble-v4-max` weights commercially.
2. **Perplexity** — ask for written confirmation that per-case outputs and comparative results may be published outside a "Customer Application".
3. **TypeSafe** — ask whether measured performance is treated as confidential and whether naming Jev in public results is acceptable; check s.2.3(b) if we build our own decision model.
4. **Liquid** — ask about benchmark publication; ask for a ZDR endpoint for `d1-ultra`, since standard endpoints may train on our cases. Resolve the per-question billing inconsistency by measurement.
5. **Morph** — confirm that metered API benchmarking is outside the s.7.7.3 "benchmark farming" restriction.
6. **Microsoft** — accept the reciprocal benchmarking waiver knowingly; label Decision-1 as Preview; confirm response field names with one live call.
7. **OpenAI** — s.10 publicity: factual naming in a results table is common practice but the clause is broad; avoid logos and any implication of partnership. Handle `refusal` answers. Re-read Usage Policies after 2026-11-20.
8. **Cloudflare** — publish full replication information (already our model). Note `state` truncation; log token counts so truncated cases can be flagged.
9. **Version choices** — decide whether to benchmark the versions named in the brief (Decider 1.2, Nimble v4 Max) or the current defaults (Decider 1.3, Nimble v4.1 Max), or both. Pin explicit ids either way; never use `-latest` aliases.
10. **No explicit pin available** for `gpt-6-luna`, `reflex`, hosted Clef, and Microsoft-Decision-1 beyond version "1": record the run date and response `model` field per call.
11. **Not verified**: batch endpoints for any decision model; Clef rate limits; TypeSafe, Liquid, Morph numeric rate limits; Perplexity decider weight licence; Runware Jev Model Rules; `d1.2` / `d1.2-ultra` interface; Cloudflare REST response envelope for Clef.
12. All "verbatim" quotes should be re-read at source by whoever signs off the publication.
