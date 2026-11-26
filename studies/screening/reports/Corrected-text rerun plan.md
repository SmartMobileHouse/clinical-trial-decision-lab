# Corrected-text rerun: plan

Written on 26 November 2026, before any model is called on the corrected text. This is an after-the-fact check. It is not
confirmatory. The locked run of 25 November 2026 stays the confirmatory result and its files are not changed.

## Why

The locked run removed markup from titles and abstracts with a rule that treats every "less than" sign as the start of a tag.
In text such as "p < 0.001" the rule deleted everything from that sign to the end of the next real tag. We found this on
26 November 2026 while preparing a worked example.

- 325 of the 1,210 abstracts lost text (26.9%). The median loss is 332 characters, 16.7% of the complete abstract.
- No title was changed.
- All 79 reviews have at least one affected abstract: 169 included papers and 156 excluded papers.
- Every system received the same shortened text for the same paper. The classifiers' training text was cleaned with the same rule.

## The question

Do the six answers of the locked run hold when every system reads the complete abstracts?

## What stays exactly as in the locked run

- The same 1,210 papers, the same 79 reviews, the same labels, in the same order.
- The same question file (`questions.json`), the same request formats and the same runners.
- The same five hosted models and settings: `pplx-decider-v1.3`, `nimble-v4.1-max`, `google/gemini-decision-1` through OpenRouter,
  `gpt-6-luna` (reasoning effort none, probability output), `claude-haiku-5-5` (thinking disabled, probability output).
- The same measure (balanced accuracy averaged equally over reviews), the same 0.5 cut-off, the same five-point margin,
  the same seed (20261122) and 10,000 resamples of whole reviews, the same two frozen cut-offs of the automatic rule.
- A missing or invalid answer counts as wrong. Each call is scheduled once; the runners' own retry rules are unchanged.

## What changes

1. **The text.** Markup is removed by stripping only the tag names that occur in the source (`h4`, `i`, `b`, `sup`, `sub`, `br`,
   and the close relatives `u`, `em`, `strong`, `p`). Everything else is kept, including "<" and ">" signs. The script is
   `screening-check/trialpanorama/final-corrected/build_corrected_sample.py`. It first checks that today's source text, cleaned
   with the old rule, equals the text the locked run used, for every paper.
2. **The trained classifiers.** They are refitted on the same training rows with correctly cleaned text, using the settings chosen
   before the locked run. No settings are selected again. Training rows whose source text can no longer be fetched keep their old text
   and are counted.
3. **Two calculation points already corrected after the locked run** are used from the start: 10,000 resamples for questions 4 and 5,
   and no rank correlations.

## What will be reported

- All six questions on the corrected text, beside the locked results, whatever the outcome.
- For question 1, whether the lower end of the 95% range of "Decider minus GPT-6 Luna" is above -5 points on the corrected text.
  If it is not, the report will say that the narrow pass did not hold with complete abstracts.
- How many answers changed between the two texts, for each system, separately for the 325 corrected abstracts and the 885 unchanged ones.
  The unchanged ones show how much answers move with no change to the input.
- The same results restricted to the 325 corrected abstracts and to the 885 unchanged ones (descriptive).

## Limits known in advance

- The models may have changed since 25 November 2026. Differences between the two runs mix the effect of the text with any such change.
  The 885 unchanged abstracts give a measure of that.
- This check was decided after the locked results were known.
- Trial linkage is not repaired here; the earlier sensitivity analysis covers it.

## Cost

One pass of five hosted models and a repeat pass of the three decision models. Expected about $0.55. Hard cap for the whole rerun: $3.
