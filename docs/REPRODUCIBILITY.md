# Reproducibility

Everything in this file runs offline, without API keys, on Python 3.12 (macOS or Linux).

## Set up

```bash
git clone https://github.com/SmartMobileHouse/clinical-trial-decision-lab
cd clinical-trial-decision-lab
uv sync --frozen          # exactly the versions in uv.lock
uv run triallab doctor    # checks the setup; prints no secrets
```

## One-command demo

```bash
make demo
```

It runs the deterministic rules and the two anchors on the 400 synthetic test cases, shows two
provider adapters building and parsing requests against fixture responses, and writes
`outputs/demo-report.html`.

## Reproduce the synthetic dataset

```bash
uv run triallab data verify      # regenerates every split in memory and compares with data/synthetic/v1/
uv run triallab data generate    # rewrites the files from the fixed seeds
```

Generation uses only the Python standard-library random generator with fixed seeds, so files are
identical across machines. Fingerprints are in `data/synthetic/v1/MANIFEST.json` and
`data/source-manifest.json`. `make check` fails if the files differ from a fresh generation or if
any case's declared findings differ from the reference adjudicator.

## Reproduce the rules baseline

```bash
uv run triallab run --dataset synthetic-v1 --systems rules,flag_all,flag_none
uv run triallab replay --run-id <run id printed above>
```

The quality numbers of these local systems are deterministic. Expected values on the frozen test
split (dataset generator 1, rules version 1, evaluation version 1):

| System | Case accuracy | Critical cases flagged | Issue precision | Issue recall | Issues never queued | Unneeded reviews per 100 |
|---|---|---|---|---|---|---|
| `rules` | 89.5% | 90.5% | 90.2% | 92.0% | 8 | 6.5 |
| `flag_all` | 50.0% | 100.0% | n/a | 0.0% | 0 | 50.0 |
| `flag_none` | 50.0% | 0.0% | n/a | 0.0% | 100 | 0.0 |

The rules are right on all 358 structured cases and wrong on all 42 text-dependent cases, by
design. Latency of local systems depends on the machine and is not listed here.

## Dry run of the provider adapters

```bash
uv run triallab run --systems rules,jev,openai_decisions,clef,llm_openai,llm_anthropic --dry-run --max-cases 40
```

A dry run needs no keys and makes no network call. Its remote answers come from fixtures, are marked
"not a measurement" and are excluded from every report and export.

## Paid API runs

Not executed for v0.1.0. Before any paid run: read `docs/RELEASE-APPROVAL.md`, confirm the
provider's terms in `docs/DATA-LICENSING-AUDIT.md`, and set a provider-side spending limit.

```bash
cp .env.example .env && chmod 600 .env        # fill in only the providers you will run
uv run triallab models                        # what is enabled and what may be published

# Smoke run: 20 cases
uv run triallab run --systems rules,jev,openai_decisions --max-cases 20 \
  --allow-external-requests --max-cost-usd 1.00

# Full run on the frozen test split, two repeats for answer stability
uv run triallab run --systems rules,jev,openai_decisions,clef,clef_flash,llm_openai,llm_anthropic \
  --repeats 2 --concurrency 4 --rate 2 --allow-external-requests --max-cost-usd 10.00

# Native versus gateway, same cases
uv run triallab run --systems jev,jev_via_opper,jev_via_runware --max-cases 100 \
  --allow-external-requests --max-cost-usd 2.00

uv run triallab run --resume <run id> ...     # continue an interrupted run; answered cases are not sent again
```

`--max-cost-usd` is an estimate-based guard, not a provider billing cap.

## From a run to a report

```bash
uv run triallab export-report-data --run-id <run id> --out outputs/report-data.json
uv run triallab report --run-id <run id> --out outputs/report.html
```

The export refuses datasets that are not approved for publication. It includes a remote model's
numbers only when they are real measurements and the model's publication is approved in the
registry. The published research report is built from `report-data.json` by Smart Mobile House's
report system.

## The regulatory-finding track

Its dataset is not distributed. With access to it:

```bash
export TRIALLAB_RESTRICTED_DATA=/path/to/private/folder     # outside this repository
uv run triallab run --dataset fda-findings-v1 --systems keyword
```

Remote systems are blocked on this dataset by its configuration.

## Quality gate

```bash
make check           # lint, types, tests, dataset verification, licence screen, secret scan, technical preflight
make release-check   # full publication preflight; fails until approvals are recorded
```

## Known limits of reproduction

- Hosted models change. Several providers offer no pinned version; a later run of the same
  identifier may differ. Each run records the date and the model name each response reported.
- Replay recomputes statistics from saved answers. It does not prove that a provider produced them
  and does not verify charges.
- Latency depends on the network path, the machine, the time of day and the provider's load.
- Bootstrap ranges are reproducible for a given seed and resample count.
