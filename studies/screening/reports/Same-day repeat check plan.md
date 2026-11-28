# Same-day repeat check for the two general models: plan

Written on 28 November 2026, before any request of this check is sent. After the fact and descriptive. It tests a point
raised by a reader of the day-apart comparison: without a same-day repeat, a 9.3% change between two days cannot be
called day-to-day change.

## Question

When GPT-6 Luna and Claude Haiku 5.5 receive the same frozen request twice within minutes, how often does the
include-or-exclude answer change? How does that compare with the change between days?

## What is sent

The corrected sample of the rerun (`final-corrected/sample.jsonl`, 1,210 papers), the same question file and the same
runner (`run_llm_probability.py`) as on 25 and 26 November. Two full passes, A then B, started one after the other on
28 November. No decision models: they already have a same-day repeat on both earlier days.

## What will be reported, whatever the outcome

For each of the two models, the share of papers whose answer differs (0.5 cut-off), with the count, for:

1. **Within a day:** pass A against pass B (1,210 identical requests, minutes apart).
2. **Across days, identical requests:** 26 November against pass A (1,210 identical requests, two days apart).
3. **Across days, earlier pair:** 25 against 26 November, on the 885 papers whose text did not change (already measured).
4. The same three comparisons restricted to those 885 papers, so that all figures share one set of papers.

For each comparison: how many changes moved toward the reviewers' label and how many away, the share of identical
probabilities, and the mean absolute change in probability. Ranges are from 10,000 resamples of whole reviews, seed 20261122.
Accuracy of each pass is reported beside it.

## Reading rule, fixed now

If the within-day share of changed answers is close to the across-day share (its range overlaps it), the earlier
difference between days is ordinary run-to-run variation and will be described that way. If the across-day share is
clearly higher, that is evidence of a change between days, cause unknown.

## Limits known in advance

Two passes on one day from one location. A missing or invalid answer counts as a changed answer and is reported.
Returned model versions are not logged by this runner. Expected cost about $0.50; hard cap $1.50.
