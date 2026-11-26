# Clinical validation and monitoring tools

Status on 2026-11-16: **assessed; export implemented and tested; none of the tools executed.**

These tools are used in clinical data management. They answer different questions from the triage
benchmark, so their output is never ranked against a decision model or the rules baseline.

| Tool | What it answers | Comparable to triage answers? | Status here |
|---|---|---|---|
| CDISC CORE | Do SDTM datasets conform to CDISC conformance rules? | No. Structural conformance of datasets | Not run |
| pharmaverse sdtmchecks | Are there common data-quality problems in SDTM domains? | No. Dataset-level listings | Not run |
| OpenRBQM / Good Statistical Monitoring | Which sites are statistical outliers on key risk indicators? | No. Site-level aggregates | Not run |
| IMPALA Clinical Trial Anomaly Spotter | Which sites have anomalous time series? | No | Future experiment only |
| CluePoints, Medidata Clinical Data Studio | Commercial central monitoring | Unknown without access | Industry reference only; not tested |

## Why none was executed

- **R is not part of this project.** OpenRBQM, sdtmchecks and the anomaly spotter are R packages.
  The project is Python only by convention, and no R runtime was available. The OpenRBQM packages
  are not on CRAN and bring a large dependency tree.
- **CDISC CORE is split.** Its SDTM rules currently run on a separate engine that reads XPT or
  SAS7BDAT files, and the Python package ships no rules cache. Rules come from the CDISC Library,
  whose licence text could not be obtained. Cached Library content must not be published.
- **Thin coverage.** sdtmchecks has no eligibility-criteria checks and one consent-date check.
  OpenRBQM has a screen-failure indicator and an ineligibility indicator but no consent indicator.
- **gsm.datasim** was assessed as a generator and not adopted: its eligibility results are random
  and its consent fields are constants, so it cannot express protocol limits, consent versions or
  timing. Its licence (Apache-2.0) would have allowed use.

## What is implemented

```bash
uv run triallab data export-tables --split test --out outputs/tables
```

| File | Shape | For |
|---|---|---|
| `dm.csv` | Minimal SDTM DM: STUDYID, DOMAIN, USUBJID, SUBJID, SITEID, RFICDTC, AGE, AGEU | CDISC CORE, sdtmchecks |
| `ds.csv` | Minimal SDTM DS: informed consent, enrollment, randomization and screen-failure milestones | CDISC CORE, sdtmchecks (`check_ts_sstdtc_ds_consent`, `check_ds_duplicate_randomization`) |
| `enroll.csv` | One row per screened participant: study, site, enrolled yes or no, reason | OpenRBQM screen-failure indicator |

These are minimal tables, not complete SDTM. Conversion to XPT or Dataset-JSON, required by CDISC
CORE, is left to the user's own tooling.

## If you run them

- Install the tools yourself and keep them, their rule caches and their sample data out of this
  repository.
- Report their output in its own section, with tool name, version and rule-set version.
- Do not compute triage metrics from their output unless a mapping to the eight questions is
  defined and published first.
- Synthetic sites here have about 17 participants each in the test split. Site-level statistics on
  that are illustrative only.

Rights for each tool are in `docs/DATA-LICENSING-AUDIT.md`.
