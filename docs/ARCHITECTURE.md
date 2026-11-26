# Architecture

Clinical Trial Decision Lab is a Python 3.12 command-line project. It reuses the benchmark
infrastructure of Fraud Decision Lab (see `docs/FRAUD-LAB-REUSE-AUDIT.md`) and adds the clinical
task on top.

```
configs/questions-v1.json ─┐
configs/models.yaml ───────┤
data/synthetic/v1/*.jsonl ─┼─▶ triallab run ─▶ outputs/<run>/  attempts.jsonl   raw call log
restricted folder (Track A)┘                                   predictions.jsonl raw answers
                                                               reference.jsonl   labels used
                                                               metrics.json      statistics
                                                               manifest.json     identity, versions
                              triallab replay ─▶ recomputes metrics.json from the raw files
                              triallab export-report-data ─▶ evidence bundle (public-safe JSON)
                              triallab report ─▶ plain HTML summary
data/source-manifest.json ─▶ triallab preflight ─▶ pass / fail before any publication
```

## Packages

| Package | Role |
|---|---|
| `triallab.schema` | The case packet (what systems see) and the case truth (hidden reference record) |
| `triallab.questions` | Loads the frozen question sets |
| `triallab.clinical.rules` | Eight protocol rules, each a plain function |
| `triallab.reference` | `adjudicate`: reference labels from facts and rules. `derive`: answers to decision outputs |
| `triallab.synthetic` | Fictional study designs, 36 scenarios, deterministic generation and verification |
| `triallab.datasets` | Loads a dataset split with its rights flags; builds tasks and reference rows |
| `triallab.providers` | The system contract, the model registry, four request-format adapters, the dry-run transport |
| `triallab.baselines` | Rules baseline, keyword baseline, anchors, mock |
| `triallab.core` | HTTP layer, spending guard, call ledger, provenance, validation (copied from Fraud Decision Lab) |
| `triallab.benchmark` | Runner and replay |
| `triallab.evaluate` | Decision quality, probability quality, bootstrap, McNemar, stability |
| `triallab.report` | Evidence export and the plain HTML summary |
| `triallab.interop` | Tables for optional external clinical tools |
| `triallab.preflight` | Publication checks |

## One contract for every system

```
Task        case_id (never sent), state (the packet), payload_hash, questions
Prediction  answers {question: bool} | None, probabilities {question: float} | None,
            evidence_refs | None, status, execution (local|native|gateway|dry_run|mock),
            attempts, latency, tokens, cost, cost_source, request_id, error, raw_answer
```

A system is anything with `async evaluate(task) -> Prediction`. Rules, anchors, the mock and every
provider adapter implement it. Benchmark code never names a model.

## Adding or disabling a model

Edit `configs/models.yaml` only.

- A model with an existing request format (`system_one`, `openai_decisions`, `openai_responses`,
  `anthropic_messages`) needs one registry entry: identifier, endpoint, credential variable,
  context size, price with source and date, terms, interface status.
- `enabled: false` with a `disabled_reason` removes a model from runs. A model whose interface is
  `not_verified` cannot be enabled.
- A new request format needs one adapter class in `providers/adapters.py` and its entry in
  `ADAPTERS`.
- A gateway route is its own entry with `execution: gateway` and a `native_counterpart`.

## Safety properties

| Property | Where it is enforced |
|---|---|
| Offline by default; live calls need `--allow-external-requests`, `--max-cost-usd` and keys | `benchmark/runner.py` |
| A dataset with `external_processing_allowed: false` is never sent | `benchmark/runner.py` records `permission_blocked` |
| Tests cannot reach the network | `tests/conftest.py` |
| Dry-run answers are never reported | `execution: dry_run` sets `measurement: false`; `report/export.py` drops the numbers |
| Fixture token counts never become a cost | `providers/adapters.py` zeroes the price in a dry run |
| Evidence is never truncated | Adapters refuse inputs above 90% of the model context |
| Invalid output is never repaired | Adapters return `invalid` |
| Results are published only for approved datasets and approved models | `report/export.py`, `preflight/checks.py` |
| Secrets appear by name and length only | `config.py`, `core/http.py` redaction |

## Run identity and resume

Each run stores a fingerprint of: the dataset config and files, case identifiers, payloads,
reference answers, the question file, every system's configuration, the model registry, the source
tree with the lock file, and the run options. Resume is refused when any of these differ. The call
ledger is written before and after every call, so an interrupted run never loses or double-counts a
call.

## What is not here

- No training and no fine-tuning.
- No hosted service, no database, no user interface.
- No R code. Optional clinical tools are run by the user, outside this project.
