# Fraud Decision Lab reuse audit

Audit date: 2026-11-16. Audited: Fraud Decision Lab v0.2.0 (single commit `b03029d`, public, MIT),
about 4,400 lines of source and 2,500 lines of tests. Its own gate (`make check`: lint, types, 192
tests, licence screen, secret scan) passed before this project started and passes unchanged now.

This audit was written before any architecture work. It records what exists, what was reused, what
should become a shared module, and what had to be clinical-specific.

## Decision: a separate repository that copies the shared code

Fraud Decision Lab was **not modified**. Clinical Trial Decision Lab is a separate repository with
the same conventions (Python 3.12, uv, Typer, httpx, pydantic, ruff, mypy, pytest, respx, `make
check`, the same issue and pull-request templates). Generic modules were copied with a provenance
note in each file.

Why not a shared package now:

- Every fraud run records a fingerprint of the `fraudlab` source tree. Moving modules out would
  change that fingerprint and make existing runs impossible to resume. Preserving reproducibility
  was a requirement.
- `fraudlab` is an application, not a library: several modules find configs through the repository
  root and would break when installed as a dependency.
- The fraud repository is public and its working copy pushes straight to it. A refactor there is a
  public release of its own and deserves its own review.

Extraction is the right next step and is listed below as REFACTOR INTO SHARED MODULE. The copies
were kept close to the originals so that the extraction is mechanical.

## Classification

Classes: **REUSE UNCHANGED**, **EXTEND**, **REFACTOR INTO SHARED MODULE**, **CLINICAL-SPECIFIC
IMPLEMENTATION**, **DO NOT REUSE**. Effort is engineering time for the work done here; "shared"
effort is the later extraction.

### 1. Repository structure and architecture

| Component | Fraud Decision Lab | Class | What happened here | Effort | Risk |
|---|---|---|---|---|---|
| Layout (`src/`, `tests/unit`, `configs/`, `data/`, `scripts/`, `outputs/` ignored) | Same | REUSE UNCHANGED | Same layout | none | none |
| Tooling (uv lock, ruff rules, mypy, pytest markers, Makefile gate) | `pyproject.toml`, `Makefile` | REUSE UNCHANGED | Copied; XGBoost, scikit-learn, pandas and pyarrow dropped | 0.5 h | low |
| `CLAUDE.md` hard rules (no invented numbers, offline by default, dataset rights) | Same | EXTEND | Kept, plus clinical rules (no clinical advice, absence of documents is not proof) | 0.5 h | low |
| Settings and secret status (`config.py`) | Name and length only | REUSE UNCHANGED | Copied, paths adjusted | 0.2 h | low |

### 2. Model provider integrations and adapters

| Component | Fraud Decision Lab | Class | What happened here | Effort | Risk |
|---|---|---|---|---|---|
| Shared HTTP layer (`providers/http.py`): per-attempt timing, retries on 429/5xx/529/timeouts, Retry-After, credential redaction | 190 lines | REUSE UNCHANGED → REFACTOR INTO SHARED MODULE | Copied verbatim to `core/http.py` with its tests | 0.2 h | low |
| Provider contract (`providers/base.py`: Task, Prediction, Price, DecisionProvider) | One fraud score per case | EXTEND | A set of yes/no answers; probabilities only when reported; evidence refs; execution route | 2 h | medium: the Prediction shape differs, so the two labs cannot yet share it |
| Prediction builder and usage accounting (`providers/common.py`) | Per-attempt cost history | EXTEND | Copied; score replaced by answers | 1 h | low |
| System One adapter (Jev, Clef, Clef-flash) | One question, hard-coded classes | EXTEND | One generic adapter, many questions per request, driven by the registry | 3 h | medium: multi-question requests are documented but not yet executed |
| OpenAI Decisions adapter | One predicate | EXTEND | Many predicates; refusal answers handled | 1.5 h | medium, same reason |
| OpenAI structured-output LLM adapter | One-number schema | EXTEND | Answers schema with evidence refs | 1.5 h | low |
| Anthropic structured-output adapter | none | CLINICAL-SPECIFIC IMPLEMENTATION (generic) | New adapter over the shared HTTP layer | 1.5 h | medium: verified from documentation only |
| Mock provider | Hash-based score | EXTEND | Hash-based answers and probabilities | 0.3 h | none |
| Probe (`probe.py`: a few live calls per provider) | 168 lines | DO NOT REUSE (yet) | Replaced by `--dry-run`; a live probe belongs with the first approved paid run | none | none |

### 3. Model registry, versions, configuration, credentials

| Component | Fraud Decision Lab | Class | What happened here | Effort | Risk |
|---|---|---|---|---|---|
| Registry | A Python dict of five classes; model ids as class attributes | REFACTOR INTO SHARED MODULE | `configs/models.yaml`: fifteen entries with endpoint, route, context, price, terms, interface status, enabled flag, publication approval | 3 h | low |
| Price snapshot (`configs/prices-*.yaml`) | Separate dated file | EXTEND | Folded into the registry with source and retrieval date; the registry fingerprint is bound to each run | 0.5 h | low |
| Credentials (`.env`, `PROVIDER_ENV`) | Four variables | EXTEND | Derived from the registry; nine variables | 0.3 h | low |

### 4. Decision request schemas and response normalisation

| Component | Fraud Decision Lab | Class | What happened here | Effort | Risk |
|---|---|---|---|---|---|
| Question file (`configs/questions-v1.json`) | One fraud question | EXTEND | Two frozen question sets: eight triage questions, two finding questions | 2 h | high: wording is frozen before any model run and cannot be tuned afterwards |
| Payload rendering and hash (`datasets/payload.py`) | One tabular row | CLINICAL-SPECIFIC IMPLEMENTATION | A nested case packet; same hash idea | 1 h | low |
| Probability validation, never repairing invalid output | Yes | REUSE UNCHANGED | Copied | none | none |
| Normalisation to decision labels | none (ranking only) | CLINICAL-SPECIFIC IMPLEMENTATION | `reference/derive.py`, applied identically to reference and systems | 2 h | medium |

### 5. Dataset loading and generation

| Component | Fraud Decision Lab | Class | What happened here | Effort | Risk |
|---|---|---|---|---|---|
| Dataset config with separate `external_processing_allowed` and `publication_allowed` | Yes | REUSE UNCHANGED (concept) | Same two flags, same safe defaults, same note requirement | 0.5 h | low |
| Tabular loader, time split, leakage correlation check | pandas | DO NOT REUSE | Cases are nested records; leakage is checked structurally (no label fields in packets) | none | none |
| Synthetic generator | Transactions with a hidden risk score | CLINICAL-SPECIFIC IMPLEMENTATION | Protocols, records, 36 scenarios, hidden note meanings, reference adjudicator | 14 h | high: this is the scientific core |
| Bundled dataset with a fingerprint test | Parquet | REUSE UNCHANGED (concept) | JSON Lines, regenerated and compared in tests and in `make check` | 1 h | low |

### 6. Evaluation metrics and statistics

| Component | Fraud Decision Lab | Class | What happened here | Effort | Risk |
|---|---|---|---|---|---|
| Ranking metrics (PR-AUC, recall at top 1% and 5%) | `evaluate/metrics.py` | DO NOT REUSE | Not appropriate: the task is categorical triage, not rare-event ranking | none | none |
| Failed calls count against the system; coverage reported | Yes | REUSE UNCHANGED (convention) | Same | none | none |
| Fixed hash tie-break for rankings | Yes | REUSE UNCHANGED | Copied for the review-budget metric | 0.2 h | none |
| Paired, stratified, percentile bootstrap with differences against a reference | `evaluate/bootstrap.py` | EXTEND | Same method; strata are scenario categories; reference is the rules baseline | 2 h | low |
| Decision quality, abstention, evidence, calibration, McNemar, stability | none | CLINICAL-SPECIFIC IMPLEMENTATION | `evaluate/decision.py`, `probability.py`, `statistics.py` | 8 h | medium |

### 7. Latency, throughput, tokens and cost

| Component | Fraud Decision Lab | Class | What happened here | Effort | Risk |
|---|---|---|---|---|---|
| Spending guard (`benchmark/budget.py`) | Reservations, unknown-cost handling | REUSE UNCHANGED → REFACTOR INTO SHARED MODULE | Copied verbatim with tests | 0.1 h | none |
| Append-only call ledger (`benchmark/ledger.py`) | Start and finish records, per-provider accounting | REUSE UNCHANGED → REFACTOR INTO SHARED MODULE | Copied; only the import of Prediction changed | 0.2 h | low |
| Worst-case cost estimate | Per case | EXTEND | Multiplied by the number of questions, because some providers bill the state per question | 0.3 h | medium |
| Open-loop load test (`benchmark/loadtest.py`) | 263 lines | DO NOT REUSE in v0.1.0 | Controlled concurrency and rate are run options; a separate load test is future work | none | low |

### 8. Experiment orchestration and reproducibility

| Component | Fraud Decision Lab | Class | What happened here | Effort | Risk |
|---|---|---|---|---|---|
| Runner: immutable run identity, run lock, sessions, resume, rate limit | `benchmark/runner.py` | EXTEND | Same structure; adds dry run, repeats, category filter; drops XGBoost | 6 h | medium |
| Provenance helpers (`benchmark/provenance.py`) | Hashes, atomic writes | REUSE UNCHANGED → REFACTOR INTO SHARED MODULE | Copied; parquet helpers replaced by JSON Lines | 0.3 h | none |
| Replay | Recompute and compare | EXTEND | Same contract for the new metrics | 1 h | low |
| Option validation | Yes | REUSE UNCHANGED | Copied verbatim | none | none |

### 9. Tests, CI and quality gates

| Component | Fraud Decision Lab | Class | What happened here | Effort | Risk |
|---|---|---|---|---|---|
| Network guard for tests, `live` marker | `tests/conftest.py` | REUSE UNCHANGED | Copied | none | none |
| Repository hygiene tests | Forbidden paths, size limit, private-path leak | EXTEND | Copied; restricted-data folder added | 0.2 h | none |
| HTTP, budget and ledger tests | 3 files | REUSE UNCHANGED | Copied with imports changed | 0.3 h | none |
| `make check` (ruff, mypy, pytest, pip-licenses, gitleaks) | Local gate only; no hosted CI by decision | EXTEND | Same gate plus dataset verification and the publication preflight; a CI workflow runs the same target | 1.5 h | low: the workflow has not run on a hosted runner yet |

### 10. Report generation, charts, tables, exports

| Component | Fraud Decision Lab | Class | What happened here | Effort | Risk |
|---|---|---|---|---|---|
| Evidence bundle export (`report/export.py`, schema `smh-research-data/1`) | Public-safe JSON for the report system | EXTEND | Same schema name and envelope; clinical content; per-model publication gate | 3 h | low |
| Publication gate (`report/publication.py`) | Dataset flag | EXTEND | Dataset flag, model approval, measured-only | 1 h | low |
| Built-in HTML report with Plotly | 550 lines plus a 530-line template | DO NOT REUSE | The published report is built by the separate report system; a small plain summary reuses the neutral colour tokens only. Plotly is not a dependency of this project | 2 h | low |

### 11. Public website and research page

| Component | Fraud Decision Lab | Class | What happened here | Effort | Risk |
|---|---|---|---|---|---|
| Research report system (separate private project: report definition plus evidence bundle to HTML and PDF) | First report is Fraud Decision Lab | REUSE UNCHANGED | A new report definition consumes this lab's evidence bundle. The fraud report and page are untouched | 4 h | low |

### 12. Licensing, documentation and publication checks

| Component | Fraud Decision Lab | Class | What happened here | Effort | Risk |
|---|---|---|---|---|---|
| `LICENSE`, `CONTRIBUTING.md`, `SECURITY.md`, issue and PR templates, `CODEOWNERS` | Yes | REUSE UNCHANGED / EXTEND | Copied and adapted | 1 h | none |
| `DATA_LICENSES.md` | One page for three datasets | CLINICAL-SPECIFIC IMPLEMENTATION | A full audit, a source register and a machine-readable manifest | 10 h | high: several legal questions stay open |
| Source-only release script and history check | `scripts/` | DO NOT REUSE | Not needed: this repository starts with a clean history. Replaced by a preflight that also inspects history | 4 h | low |
| Dependency licence screen and secret scan | Makefile | REUSE UNCHANGED | Same commands | none | none |

## Shared module proposal

A later `decisionlab-core` package would hold, unchanged in behaviour: the HTTP layer, the spending
guard, the call ledger, provenance helpers, option validation, the registry schema, the dry-run
transport and the publication gate. Preconditions: a generic Prediction (answers as a mapping, with
the fraud score as one answer), a new fraud release that states the source-fingerprint change, and
replay of every published fraud run before and after. Estimated effort: 2 to 3 days including the
fraud release. Until then the two copies must be kept in step by hand; each copied file names its
origin.

## What was verified about preservation

- No file in the Fraud Decision Lab working copy differs from its commit (`git status` is empty).
- Its gate passed before and after this work: 192 tests, lint, types, licence screen, secret scan.
- During setup a mistaken command briefly created untracked copies inside that working copy. They
  were removed at once; nothing was committed and no tracked file changed.
