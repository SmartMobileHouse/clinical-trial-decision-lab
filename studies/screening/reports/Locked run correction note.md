# Locked run: correction note

Date: 2026-11-25. Written after the locked results were seen and after an independent review ("Locked run results review by GPT.md").

The locked analysis script and its output ("Locked run results.txt" and ".json") are unchanged. Everything below is a post-hoc correction or an exploratory sensitivity check, produced by `experiment/screening/tp/final_sensitivity.py`. Full output: "Locked run sensitivity checks.txt".

## 1. Departure from the plan: linked reports of the same trial

The plan said linked reports of the same trial would be allocated to one review family and removed from baseline training data. This step was not implemented.

Found afterwards, using trial registration numbers printed in titles and abstracts:

| Where | What was found |
|---|---|
| Inside the sample | 6 registration numbers join 16 records across 9 review families (79 families become 73 clusters) |
| Classic baseline training data | 11 of 5,067 training rows share a registration number with 7 sample records |
| Pilots | 8 registration numbers are shared with 11 sample records |

This linkage is partial. Only 531 of the 1,210 sample records print a registration number, so other shared trials may remain undetected.

Effect, checked by resampling linked families together and refitting the classic baselines without the 11 linked rows (same frozen settings, no new model selection):

| Result | As locked | After the fix |
|---|---|---|
| Question 1, Decider minus GPT | −2.01 (−4.96 to +0.80) | −2.01 (−4.85 to +0.67): still passes |
| Question 1, also dropping the 11 pilot-linked records | n/a | −1.84 (−4.68 to +0.82): still passes |
| XGBoost balanced accuracy | 60.4% | 59.6% |
| Logistic regression balanced accuracy | 54.8% | 55.4% |
| Question 3, Decider minus XGBoost | +0.5 (−3.2 to +4.3) | +1.3 (−2.4 to +5.0): still not met |
| Question 3, Decider minus logistic | +6.1 (2.9 to 9.3) | +5.5 (2.2 to 8.9) |

No verdict changes. The statement "the classic baseline shared no study, review or review title with the sample" must read: no shared paper, review or review title was found; shared underlying trials were found and their removal changes XGBoost by under one point.

Refit check: XGBoost refitted on the unchanged training data reproduces the frozen predictions exactly; logistic regression reproduces them to within 0.005.

## 2. Questions 4 and 5 used 2,000 resamples instead of the planned 10,000

| Figure | Locked output | With 10,000 |
|---|---|---|
| Q4 Decider repeat classification | 99.3% (98.8 to 99.8) | 99.3% (98.8 to 99.8) |
| Q5 automatic exclude, 65/91 = 71.4% | 62.6 to 80.2 | 62.4 to 80.5 |
| Q5 automatic include, 151/201 = 75.1% | 68.5 to 81.3 | 68.6 to 81.7 |

## 3. Rank correlations ignored ties (exploratory review-difficulty figures)

| Decider accuracy against | Locked output | Corrected |
|---|---|---|
| Records sampled per review | +0.08 | +0.08 |
| Review year | −0.04 | −0.14 |
| Length of review title | −0.23 | −0.22 |

All remain weak.

## 4. Logging and cost

- Recorded spend: $0.497 ($0.370 first pass, $0.128 repeat pass), plus three failed Nimble calls with unknown charges. The earlier "about $0.53" is withdrawn.
- General-model logs omit returned model identifiers and caching details; Gemini logs omit caching details. This falls short of the plan and cannot be recovered for this run.
- Question 2 is unaffected: both Decider and GPT succeeded on every first attempt.

## 5. Wording corrections

| Earlier wording | Corrected wording |
|---|---|
| The task is barely doable | Six systems scored about 60 to 63%, which is 10 to 13 points above chance, with substantial error remaining |
| XGBoost matches the decision models | XGBoost had similar yes/no accuracy here; equality was not established, and it ranks studies less well (AUC 0.63 against 0.69) |
| Automatic decisions are not supported | The one frozen rule tested does not justify unattended decisions (26 of 91 automatic exclusions were in fact included papers); other rules and real workloads are untested |
| Nothing changed after seeing results | File hashes and request logs are consistent with the declared freeze; no evidence of outcome-driven changes was found |

## 6. Omitted from the first summary: probability quality

Brier score, lower is better. Always answering 0.5 scores 0.250.

| System | Brier |
|---|---|
| XGBoost | 0.240 |
| Nimble 4.1 | 0.242 |
| Logistic regression | 0.252 |
| Gemini Decision 1 | 0.281 |
| Claude Haiku 5.5 | 0.289 |
| Decider 1.3 | 0.293 |
| GPT-6 Luna | 0.318 |

Four of the five hosted systems give probabilities that score worse than a constant 0.5. Their probabilities are useful for ordering but should not be read as calibrated chances.

## 7. Not repaired

- The sample was not redrawn. Doing so would lose its locked status.
- The reviewer could not rebuild the random draw or certify every family decision, because the bundle it received lacked the source membership lists and candidate metadata.

## 8. Cleaning error: passages deleted from abstracts (found 26 November 2026)

Found by us while preparing a worked example, after the two independent reviews, which were not given the raw text.

**The fault.** Markup was removed from titles and abstracts with the rule `<[^>]+>`. That rule treats every "less than" sign as the start of a tag. In text such as "p < 0.001" it deleted everything from that sign to the end of the next real tag.

**How much.** We fetched the raw text again and confirmed that the old rule reproduces the text used in the locked run for all 1,210 papers.

- 325 of 1,210 abstracts lost text (26.9%). The median loss is 332 characters, 16.7% of the complete abstract.
- No title was changed.
- All 79 reviews are affected: 169 included papers and 156 excluded papers.
- Every system received the same shortened text for the same paper. The classifiers' training text had the same fault (1,382 of 5,067 training rows).
- The pilots used the same rule. They were not rerun.

**The repair.** The corrected rule strips only the tag names that occur in the source text and keeps everything else. We wrote a plan (`Corrected-text rerun plan.md`), fingerprinted it with the corrected sample and the scripts (2026-11-26T16:13:48+0100), and then ran all five hosted models again (two passes for the decision models) and refitted the two classifiers on corrected text with their original settings. Same papers, labels, question, request formats, measure, margin, seed and resamples.

This rerun was decided after the locked results were known. It is a check, not a confirmatory test. The locked run remains the confirmatory result.

**Result: the outcome of every decision rule was unchanged.**

| Question | Locked run | Complete abstracts |
|---|---|---|
| 1. Decider minus GPT-6 Luna (pass mark: lower end above -5.00) | -2.01 (-4.96 to +0.80), passed | -0.80 (-3.64 to +2.02), passed |
| 2. Cost ratio, Decider to GPT-6 Luna (at most 0.2) | 0.176, met | 0.178, met |
| 3. Decider minus XGBoost | +0.48 (-3.17 to +4.27), not met | +1.09 (-2.51 to +4.80), not met |
| 3. Decider minus logistic regression | +6.11 (+2.86 to +9.30) | +5.01 (+1.45 to +8.52) |
| 4. Decider repeats its answer | 99.3% | 100.0% |
| 5. Automatic exclusions correct | 65 of 91 | 66 of 92 |
| 5. Automatic inclusions correct | 151 of 201 | 151 of 202 |

| System | Balanced accuracy, locked run | Balanced accuracy, complete abstracts | Answers changed, corrected abstracts | Answers changed, unchanged abstracts |
|---|---|---|---|---|
| GPT-6 Luna | 62.9% (60.0% to 65.9%) | 61.9% (58.6% to 65.1%) | 25 of 325 (7.7%) | 82 of 885 (9.3%) |
| Decider 1.3 | 60.9% (57.9% to 63.9%) | 61.1% (58.1% to 64.0%) | 9 of 325 (2.8%) | 4 of 885 (0.5%) |
| Gemini Decision 1 | 60.7% (58.1% to 63.3%) | 60.6% (58.0% to 63.2%) | 15 of 325 (4.6%) | 0 of 885 (0.0%) |
| Nimble 4.1 | 61.2% (58.2% to 64.1%) | 60.2% (57.3% to 63.1%) | 18 of 325 (5.5%) | 0 of 885 (0.0%) |
| Claude Haiku 5.5 | 59.9% (56.9% to 62.9%) | 60.0% (56.9% to 63.0%) | 44 of 325 (13.5%) | 37 of 885 (4.2%) |
| XGBoost | 60.4% (57.7% to 63.2%) | 60.0% (57.1% to 62.9%) | 57 of 325 (17.5%) | 134 of 885 (15.1%) |
| Logistic regression | 54.8% (52.3% to 57.3%) | 56.0% (53.3% to 58.7%) | 27 of 325 (8.3%) | 43 of 885 (4.9%) |

**What else it shows.**

- Scores showed no consistent change: between the two runs they moved by -1.05 to +1.26 points. These changes mix the restored text with run-to-run variation and, for the classifiers, refitting, so they do not measure the effect of the missing passages.
- On the 325 repaired abstracts alone, counting papers equally, Decider was behind GPT-6 Luna in both runs: -5.45 points in the locked run and -5.87 (-10.05 to -1.59) in the rerun. On the unchanged abstracts the gap was -1.24 and +0.56. These subgroup figures are descriptive, not the pre-declared measure.
- On the 885 abstracts whose text did not change, the hosted models received identical requests a day apart. GPT-6 Luna changed its include-or-exclude answer on 9.3% and Claude Haiku on 4.2%; Decider on 0.5%, Nimble and Gemini Decision on none. This shows disagreement between these two runs. We cannot tell whether the general models vary from call to call or were changed by their providers between the two days, and it says nothing about longer periods. The classifiers' answers moved because they were refitted.

**Independent check.** A separate AI model (GPT-6.1 Sol, highest reasoning setting) recalculated the defect and the rerun from the raw text and both sets of answers with its own code. It reproduced the counts above and all 327 numbers in the two rerun result files, and confirmed that the analysis script differs from the locked one only in the four declared ways. Its further points are included here.

**Limits.**

- The heading "QUESTION 1 (confirmatory)" in `Corrected-text rerun results.txt` is copied from the locked script. In the rerun that question is an after-the-fact check.
- The confidence-quarter figures of GPT-6 Luna and Claude Haiku, in both runs, depend on the order of tied probabilities, because these models give rounded probabilities. We no longer quote them.
- Superscripts and subscripts are flattened in 40 abstracts (for example "HbA 1c"). That was also true in the locked run. "Restored" means the source abstracts with the deleted passages put back, not copies checked against the original publications.
- The plan, the corrected sample and the analysis script were fingerprinted before the first request on the corrected text. The comparison script was added at 2026-11-26T16:33:27+0100, after the answers had been collected; by our own record no corrected result had been computed by then. There is no independent witness to that order.
- A repeat rate of 100% in the rerun does not guarantee future requests.
- The models may have changed between 25 and 26 November. The rerun does not repair trial linkage (section 1). Recorded API spend for the rerun: $0.52.

Files: `Corrected-text rerun plan.md`, `Corrected-text rerun results.txt` and `.json`, `Corrected-text rerun comparison.json`; scripts `corrected_text_analysis.py`, `corrected_text_classic.py`, `corrected_text_compare.py`; corrected sample builder `final-corrected/build_corrected_sample.py`.

## 9. Same-day repeat check for the two general models (28 November 2026)

Section 8 reported that on 885 identical requests sent a day apart, GPT-6 Luna changed 9.3% of its include-or-exclude answers and Claude Haiku 4.2%, and said we could not tell whether the models vary from call to call or had been changed between the two days. A reader pointed out that this needs a same-day repeat, and a count of which way the answers moved. We ran that check.

**What was done.** A plan was written and fingerprinted first (2026-11-28T15:55:17+0100; `Same-day repeat check plan.md`). The same 1,210 frozen requests of the rerun were then sent to the two general models twice, one pass after the other (the passes started 40 minutes apart). Same question file and runner.

**Result.** Share of include-or-exclude answers that differ, on the 885 papers whose requests were identical on all three days:

| Compared | GPT-6 Luna | Claude Haiku 5.5 |
|---|---|---|
| Twice within the hour, 28 November | 7.0% (62 of 885) | 4.5% (40 of 885) |
| 25 against 26 November | 9.3% (82 of 885) | 4.2% (37 of 885) |
| 26 against 28 November | 6.6% (58 of 885) | 5.2% (46 of 885) |
| 25 against 28 November | 7.2% (64 of 885) | 5.1% (45 of 885) |

On all 1,210 papers the within-the-hour figures are 7.4% (90 of 1210) for GPT-6 Luna (range 5.7% to 9.4%) and 4.5% (54 of 1210) for Claude Haiku (3.3% to 5.7%).

**Reading, by the rule fixed in the plan.** The within-the-hour share overlaps the across-day shares for both models. The differences between days reported in section 8 are therefore ordinary run-to-run variation, not evidence that the models changed between days. Both models ran with reasoning switched off and a strict output format.

**Direction.** In the within-the-hour repeat, GPT-6 Luna's changed answers moved toward the reviewers' label 26 times and away 35 times; for Claude Haiku the figures were 21 and 19. There is no direction, and accuracy did not move (62.2% and 61.2% for GPT-6 Luna; 61.1% and 61.3% for Claude Haiku, counting papers equally).

**What stands.** The decision models changed 0.5% or fewer of their answers across days and none in the rerun's same-day repeat. They are far more repeatable than the two general models on this task. Repeatable is not the same as right: they repeat the same answers at about 61% accuracy.

**Limits.** One day, two passes, one location. One GPT-6 Luna answer in each pass was invalid and is counted as a changed answer, as planned. Decided after the earlier results were known. Recorded API spend: $0.50.

Files: `Same-day repeat check plan.md`, `Same-day repeat check results.json`; script `same_day_repeat_analysis.py`.
