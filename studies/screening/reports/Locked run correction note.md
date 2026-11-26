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
