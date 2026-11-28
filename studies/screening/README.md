# Screening study: the locked run of 25 November 2026

This folder holds the study behind the report *Clinical Trial Decision Lab: Where AI Decision Models
Earn Their Place in Clinical-Trial Evidence Work, and Where They Do Not*.

**The task.** A systematic review considered a paper. Given the review's title and the paper's title
and abstract, predict whether the review included the paper or excluded it. 1,210 papers from 79
reviews, half included.

**The systems.** Three decision models (Perplexity Decider 1.3, Bespoke Nimble 4.1, Google Gemini
Decision 1), two general models asked for a probability (GPT-6 Luna, Claude Haiku 5.5) and two trained
classifiers (XGBoost, logistic regression).

This is research. It is not a clinical or regulatory tool.

## The folder keeps the original layout

The scripts find their inputs relative to their own location, and the plan, sample, prompt, runners
and analysis script were fingerprinted before the run. The files are therefore byte-identical copies
in their original relative paths. Do not reformat or move them: the fingerprints in
`screening-check/trialpanorama/final/freeze.json` would stop matching.

| Path | What it is |
|---|---|
| `reports/Locked run plan.md` | The plan, frozen on 22 November 2026 |
| `reports/Locked run results.txt`, `.json` | The original output of the locked analysis |
| `reports/Locked run correction note.md` | Departures from the plan found afterwards, and their effect |
| `reports/Locked run sensitivity checks.txt`, `.json` | The post-hoc checks |
| `reports/Corrected-text rerun plan.md`, `results.txt`, `.json`, `comparison.json` | The rerun of 26 November 2026 with the deleted passages restored: its plan, results and comparison with the locked run |
| `screening-check/trialpanorama/final-corrected/` | Builder of the corrected sample, its manifest, the list of repaired papers and the rerun's fingerprints |
| `experiment/screening/tp/corrected_text_*.py`, `corrected-*` | The rerun's analysis scripts, aggregate results and the classifiers' per-paper predictions |
| `reports/Same-day repeat check plan.md`, `results.json`; `experiment/screening/tp/same_day_repeat_analysis.py`, `same_day_repeat_addendum.py` | A check of 28 November 2026: the two general models asked the same frozen requests twice within the hour |
| `experiment/screening/tp/info_work_saved.py`, `info-work-saved.json`, and the `_addendum` pair | Exploratory: in the small title-versus-rules test, how much of the rejected pile each decision model could remove at a pooled 5% or 10% loss, with the cut-off chosen on the same data. The addendum shows how unevenly that loss falls on single reviews |
| `abstract-check/fetch_raw.py` | Script that downloads raw titles and abstracts from Europe PMC by identifier |
| `screening-check/trialpanorama/final/` | Sample builder, record fetcher, fingerprints, sample manifest, review list, `sample-ids.jsonl` |
| `screening-check/trialpanorama/classic-final/selection.json` | Chosen settings of the trained classifiers |
| `experiment/screening/tp/questions.json` | The frozen question |
| `experiment/screening/tp/run*.py` | Runners for the hosted models |
| `experiment/screening/tp/classic_final.py` | Training and prediction for the trained classifiers |
| `experiment/screening/tp/final-classic-*.jsonl`, `final-sensitivity-classic-*.jsonl` | Per-paper predictions of the trained classifiers |
| `experiment/screening/tp/final_analysis.py` | The locked analysis (unchanged) |
| `experiment/screening/tp/final_sensitivity.py` | Post-hoc checks (written after the run; exploratory) |
| `experiment/export_report_data.py` | Builds the report's evidence file from the saved results |
| `experiment/screening/tp/*-scores.json`, `prompt-comparison.json`, `experiment/screening/pilot-scores.json`, `experiment/scores-human-checked-regenerated.json`, `review/` | Aggregate results of the exploratory pilots |

The same identifiers and labels are on Hugging Face as a loadable dataset:
[smartmobilehouse/clinical-trial-decision-lab-screening](https://huggingface.co/datasets/smartmobilehouse/clinical-trial-decision-lab-screening).

## What is not here

- **Abstracts and paper titles.** `sample.jsonl` is not redistributed. `sample-ids.jsonl` lists each
  paper's review, PubMed id, PMC id, DOI, licence, label and year. The abstracts can be fetched again
  from Europe PMC by identifier, under their own licences.
- **Per-paper answers of the hosted models** (`final-pass1-*`, `final-pass2-*`). They are raw provider
  outputs. This repository does not store them until publication rights are recorded for each
  provider. They are available from the authors on request, subject to each provider's terms. Aggregate results for every system are in `final-results.json`.
- **Training data and fitted models** of the trained classifiers. `classic_final.py` rebuilds them
  from the TrialPanorama benchmark and Europe PMC.
- **The benchmark's source files.** The random draw of the sample cannot be rebuilt without them.
- **Pilot predictions.** Only aggregate pilot scores are included.

## Checking the results without calling any service

`tests/unit/test_screening_study.py` runs offline as part of `make check`. It verifies the
fingerprints of the frozen files that are present, and recomputes the balanced accuracy of the two
trained classifiers from their saved predictions and `sample-ids.jsonl`, comparing it with
`final-results.json`, and does the same for the rerun against `corrected-results.json`. The hosted models' figures cannot be recomputed from this folder alone.

## Re-running the analysis

1. Rebuild `screening-check/trialpanorama/final/sample.jsonl` with `fetch_records.py` and
   `build_sample.py`. Its SHA-256 must equal the value in `freeze.json`.
2. Place the hosted models' prediction files in `experiment/screening/tp/final-pass1-*` and
   `final-pass2-*` (from the authors, or from a fresh paid run).
3. From this folder, with numpy, scipy, scikit-learn and xgboost installed:

```bash
python experiment/screening/tp/final_analysis.py      # locked analysis
python experiment/screening/tp/final_sensitivity.py   # post-hoc checks (needs the classifier training data)
python experiment/export_report_data.py report-data.json
```

A fresh prediction run calls live services whose models may have changed, and costs money. The
runners import this repository's `triallab` package and need API keys in `.env`.

## The cleaning error and the rerun

On 26 November 2026 we found that the step removing markup had deleted passages from 325 of the 1,210 abstracts
(26.9%) in the locked run: it treated every "less than" sign, as in "p < 0.001", as the start of a tag. Every system
received the same damaged text for the same paper.

We corrected the cleaning, fingerprinted a plan, and ran all five hosted models again and refitted the classifiers.
The outcome of every decision rule was unchanged: Decider minus GPT-6 Luna was -0.80 points (-3.64 to +2.02). The
rerun was decided after the locked results were known, so it is a check, not a confirmatory test. Details and limits
are in section 8 of `reports/Locked run correction note.md`.

To rebuild the corrected sample, fetch the raw text with `abstract-check/fetch_raw.py` and run
`screening-check/trialpanorama/final-corrected/build_corrected_sample.py`; its SHA-256 must equal the value in
`final-corrected/manifest.json`.

## Known limits

Read `reports/Locked run correction note.md`. In short: a cleaning error deleted passages from a quarter of
the abstracts (rerun with the passages restored: same outcomes); reports of the same trial were not linked as
planned; two ranges were first computed with too few resamples; logs lack returned model identifiers
for the general models and caching details; the planned calibration analysis was not done. The software versions used at run time were not recorded.

## Rights

Study membership labels come from the TrialPanorama benchmark (Apache-2.0), drawn from the reference
lists of published systematic reviews. Review titles are bibliographic references. Independent
research; not affiliated with or endorsed by any provider, Cochrane or the TrialPanorama authors.
