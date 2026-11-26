# Locked run plan: hard include-or-exclude decisions

Status: **approved by the owner and frozen on 2026-11-22**, after an independent review (see "Locked run plan review by GPT.md"). Any later change is recorded in the change log at the bottom, with a date and a reason.

## 1. Purpose

One locked confirmatory comparison will test Decider 1.3 against probability-output GPT-6 Luna on review families excluded from the two screening pilots. All pilot results are development results. The pilots contain 30 distinct review PMIDs and 29 normalised-title families; their explicit union is excluded.

Some candidate families previously contributed to automated training and cross-validation of the classic baselines. This exposure is disclosed. The classic comparison is secondary, and its final model selection and fitting exclude reserved evaluation families and overlapping records.

Decider 1.3 was chosen as the primary decision model using the pilot results. That is acceptable for a test of a named model on independent families. It does not support a claim about decision models as a class.

## 2. The task

A systematic review of clinical interventions considered a paper. Did the review list it as included or as excluded? "Excluded" means the reviewers assessed it and rejected it.

- The system sees: the review's title, and the paper's title and abstract.
- The correct answer: the review's own lists of included and excluded studies (TrialPanorama `study_screening`).
- What this is: predicting published review membership from a title and an abstract, with limited information. It is not the reviewers' real job, which uses the full paper and the review's eligibility criteria.

## 3. Sample

Source: TrialPanorama `study_screening`. A record is usable if its article licence is CC0, CC BY, CC BY-SA or CC BY-ND and its abstract has at least 200 characters.

**Review families.** Families are initially identified by lowercasing review titles, replacing runs outside `[a-z0-9]` with one space, and trimming whitespace. Related titles and renamed editions are audited using review metadata before study texts are inspected. The final family mapping is archived. The newest edition is selected by publication date, with review PMID breaking ties, before study availability is assessed.

**Clinical intervention reviews only.** Reviews are classified from review titles alone. Diagnostic, qualitative, prognostic, prevalence, scoping, overview, research-methods and population-policy reviews are excluded. Ambiguous titles are excluded with a recorded reason. This title-based classification does not establish that every included paper reports a clinical trial.

**Plan-like records.** Removed from both labels using the case-insensitive expression `protocol|study design|design of|rationale|trial design`, applied to the paper's title. This is a reproducible title filter, not a complete classification of protocols.

**Allocation.** Records carrying both labels within the selected review are excluded as ambiguous. Pilot records are removed. Families are processed in a seeded random order. After removing records already selected for a retained family, a family qualifies only if at least six usable records remain in each label. Draw `k` records randomly from each label, where `k = min(10, usable included, usable excluded)`. Discarded families reserve no records. Seed: 20261122.

**Duplicates.** PMID and DOI duplicates are collapsed. Known linked reports of the same trial are allocated to one family where identifiers permit. The prediction unit remains the paper record; incomplete linkage is reported.

**Expected size.** The candidate metadata contain 136 title-flagged families with at least 6+6 records, 65 with 8+8, and 41 with 10+10, before remaining exclusions. These are upper bounds; several title flags are known to be wrong. A realistic expectation is 100 to 120 families. All qualifying families are used and the final flow of families and records is reported. A shortfall does not permit changing the margin, eligibility rules or analysis.

## 4. Systems

| Role | System | Fixed setting |
|---|---|---|
| Primary decision model | Perplexity Decider 1.3 | `pplx-decider-v1.3`, called directly |
| Second decision model | Bespoke Nimble 4.1 | `nimble-v4.1-max`, called directly |
| Third decision model | Google Gemini Decision 1 | `google/gemini-decision-1` through OpenRouter |
| Primary general model | GPT-6 Luna, asked for a probability | `gpt-6-luna`, reasoning effort none, output `{"probability": number}`, as in `run_llm_probability.py` |
| Second general model | Claude Haiku 5.5, asked for a probability | `claude-haiku-5-5`, thinking disabled, effort low, same output format |
| Classic baselines | Logistic regression and XGBoost | See below |
| Floor | Keyword overlap between review title and paper | As in the pilot |

**Prompt.** The "detailed" question file `questions.json`, unchanged, for every hosted system. It is retained for a single consistent comparison; it is not claimed to be optimal. The general models receive the same context and question with an instruction to return a probability; this compares deployable configurations given the same information and does not isolate an advantage of any model architecture.

**Classic baselines.** Logistic regression and XGBoost use the existing declared feature and parameter search space. Before repeating model selection, all candidate review families are removed from baseline development data, together with overlapping paper and known trial records. Cross-validation keeps review families together and prevents shared records crossing folds. Features, IDF values and scaling are fitted within training folds. Settings are selected by equal-family balanced accuracy, with the existing AUC tie-break rule, and then frozen. Training counts and prior automated exposure are reported.

Not in this run: the other model configurations tested in the pilot, other prompt styles, ensembles, cascades, and the fuller-criteria condition.

## 5. Why the fuller-criteria condition is not in this run

Giving the model the review's objectives and selection criteria helped in the pilot. Those texts are Cochrane's. Only 11 reviews carry a licence that lets us use them, and all 11 were used in the pilot. So this run is title-only, and the criteria result stays exploratory. Fuller-information performance and actual screening usefulness remain unanswered by this run.

## 6. Questions, measures and decision rules

The primary measure is equal-family balanced accuracy: calculate accuracy separately for included and excluded records within each family, average those two values, and then average families equally. Both label-specific accuracies and record-weighted accuracy are reported as supporting results.

The first scheduled prediction pass is used for all performance results. Every scheduled record remains in the accuracy denominator; missing or invalid answers count as wrong. A valid probability must be a finite numeric value from 0 to 1. Predict "include" when `p >= 0.5`.

Paired percentile intervals use 10,000 resamples of whole review families, with seed 20261122. The same sampled families are used for all systems in each resample, and the stated statistic is recalculated. Only question 1 is confirmatory. Other intervals are nominal secondary intervals.

| # | Question | Decision or reporting rule |
|---|---|---|
| 1 | Is Decider within five percentage points of probability-output GPT? | Confirmatory success requires the lower endpoint of the two-sided 95% interval for Decider minus GPT to exceed −0.05. The margin accepts up to 50 additional wrong labels per 1,000 balanced records; it is not a screening-safety margin. Failure to establish non-inferiority is inconclusive unless the interval lies wholly below −0.05. |
| 2 | Does Decider cost at most one fifth as much? | Compare one production pass per system, including retries and charges for invalid answers, divided by all scheduled records. Report repeat-pass spending separately. Archive prices and their date. |
| 3 | Does Decider outperform both classic baselines? | Report paired differences against logistic regression and XGBoost separately. The secondary benchmark criterion is met only if both 95% lower endpoints exceed zero. |
| 4 | Do Decider's classifications repeat? | Report the proportion of all scheduled records receiving two valid, identical classifications. Invalid or missing responses count as disagreements. At least 98% meets the descriptive sample benchmark; report a family-cluster interval without claiming a population guarantee. |
| 5 | What reliability and coverage does a fixed automatic-decision rule achieve? | Report include and exclude branches separately, with correct/total counts, coverage, contributing families and uncertainty. No pass/fail claim about the availability of automatic decisions is made. |
| 6 | How much does performance vary between reviews and between models? | Report observed review variation, estimated underlying variation after allowing for within-review sampling noise, and paired model gaps. This is exploratory and has no pass mark. |

For question 5, the following Decider rule is frozen from the original 400-record pilot: automatically exclude when `p <= 0.019619440825558058`; automatically include when `p >= 0.96434342645985`; otherwise defer. These cut-offs select the lowest and highest 40 pilot scores respectively. Pilot reliability was 28/40 for exclusions and 35/40 for inclusions; these are not 95%-qualified thresholds.

Empty branches have undefined reliability and zero coverage. Family-bootstrap intervals are reported where estimable, together with counts and any sparse-data or boundary limitations. No result from this rule establishes that other rules cannot work or that deployment reliability is 95%.

Secondary descriptive analyses comprise the other named systems, equal-family within-review AUC, calibration and Brier score on valid outputs with response coverage, confidence-based error identification, and model disagreement. Review-difficulty associations are exploratory. No threshold, calibration or prompt is fitted to final-run outcomes.

## 7. What is frozen, and how the run is carried out

Models, model versions, the prompt, the sample rules, the cut-offs, the questions and their decision rules do not change after predictions are collected.

The sample manifest, family mapping, dataset revision, code commit, full prompt and settings hashes, model identifiers, baseline-selection procedure and analysis are frozen before model predictions are collected.

Repeat passes use separate output directories and fresh requests, bypassing local prediction caches. At most four transport attempts are permitted for transient failures, with no answer-dependent retrying. Every attempt is logged, including timestamps, requested and returned model identifiers, token usage, caching information where exposed, and known or estimated charges. The aggregate spending cap is enforced across runners.

If a system cannot run, it is reported as unavailable and affected comparisons as unassessed. It is not replaced, the better repeat pass is never selected, and no rule is altered after inspecting outcomes.

## 8. Reporting

All six questions are reported, including unsuccessful and unassessed outcomes. Question 1 is identified as the sole confirmatory test and all other analyses are labelled secondary or descriptive. The report states that the sample is balanced within families, restricted by open availability and title-based eligibility rules, and labelled from published membership lists. It does not estimate deployment reliability, workload savings, or performance with full eligibility criteria.

Results from the pilots are labelled exploratory.

## 9. Budget

API spending is capped at $25 (approved 2026-11-22). Expected: under $3, including the repeat pass.

## 10. Known limits accepted in advance

- Abstracts only; reviewers used full papers and the review's eligibility criteria.
- Open-licence papers only, which skews towards newer studies and towards reviews with substantial open-access material.
- Balanced included and excluded records, so reliability figures do not transfer to real workloads.
- Review families are grouped by title; renamed editions may slip through, and PMID or DOI de-duplication misses some linked reports.
- "New to this project" does not establish that a paper or review was absent from a provider's training data.
- "OpenAI Decisions" is not used: it is GPT-6 Luna behind a different endpoint.
- Provider terms on publishing benchmark results are unclear for Perplexity and unknown for Bespoke.

## Change log

- 2026-11-22: first draft revised after the independent review, before any final-run data was opened. Changes: one confirmatory question only; balanced accuracy as the primary measure; equal numbers of each label per family; question 3 requires superiority over both classic baselines; question 5 changed from a pass/fail claim to a report of a fixed rule; question 6 made descriptive; classic-baseline selection repeated without candidate families; logging, retry and cost rules added. The five-point margin was kept by the owner's decision, with its meaning stated.
