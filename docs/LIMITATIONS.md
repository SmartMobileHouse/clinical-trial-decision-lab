# Limitations

Read these before quoting any result.

## What the benchmark cannot show

1. **Not real clinical operations.** Track B is synthetic. Records are short, clean and structured;
   real source documents are long, scanned, inconsistent and multilingual. Results do not predict
   performance at a site, a sponsor or a CRO.
2. **Not prevalence.** Half of the cases are routine, a quarter contain an issue and a quarter are
   ambiguous because that mix was designed. Real issue rates are different and unknown here.
   Precision, false positives per 100 cases and accuracy all depend on this mix.
3. **Not clinical validation.** Reference labels follow the written policies of fictional studies,
   applied by deterministic rules. No clinical, regulatory or data-management expert has reviewed
   the rules, the scenarios or the labels.
4. **Not a regulatory determination.** No output of any system here is an official finding. Track A
   labels restate allegations in FDA letters; they are provisional and may have been superseded by
   later correspondence.
5. **Not a product evaluation.** A system that scores well here is not shown to be fit for use in a
   trial. The lab does not recommend treatment changes or patient-safety actions and must not be
   used to make decisions about people.

## The rules baseline

6. **It shares the reference logic.** The rules baseline and the reference adjudicator run the same
   eight rules. The baseline lacks only the meaning of free-text notes. So it is right on every
   structured case and wrong on every text-dependent case, by construction. It is an upper bound
   for structured-only rules, more complete than rules a study team would write before seeing the
   data. A model cannot beat it on structured cases; it can only tie.
7. **The headline gap is designed.** 42 of 400 test cases are text-dependent. Change that share and
   the overall difference between models and rules changes with it. Compare strata, not totals.

## The dataset

8. **Templates.** Notes come from a small set of sentence templates. A model may learn the
   templates rather than read the content. Wording variety is limited.
9. **One finding per case, mostly.** Only six test cases combine findings.
10. **Simplified rules of practice.** One permitted retest, inclusive limits, a single screening
    window, date-only assessments, one site clock per site. Real protocols have exceptions,
    waivers, central eligibility review and local regulations.
11. **Narrow scope.** Eleven screening parameters, two consent form versions, one amendment. No
    vulnerable populations, legally authorised representatives, assent, translated forms,
    electronic consent audit trails or remote consent.
12. **English only.**

## Track A

13. **Small and selected.** About fifty descriptions from letters that FDA chose to issue and
    publish, found by keyword search, dated 2021 to 2026. Not a sample of inspections.
14. **Summaries, not source text.** Systems see the researcher's description, not the letter. The
    description may make the task easier or harder than the original.
15. **Probably seen in training.** Public letters may be in model training data.
16. **Vocabulary shortcut.** A keyword matcher is right on most descriptions. High scores on this
    track mostly show vocabulary matching.
17. **Withheld.** The dataset and its results are not published in v0.1.0, so the track cannot be
    reproduced by others yet.

## Models and measurement

18. **Nothing was run.** No decision model or LLM has been executed by this project. Adapters are
    verified against documentation and fixture responses only. Multi-question requests have not
    been sent to any provider.
19. **Zero-shot only.** No examples, no fine-tuning, no prompt tuning per model. One wording for all.
20. **Fixed threshold.** A probability of 0.5 or more is "yes". Providers' probabilities may not be
    calibrated for this task; a different threshold could change the ranking.
21. **Question format favours some systems.** Eight separate yes/no questions suit decision models.
    An LLM allowed to reason freely, or given the task as one structured question, might do better.
    LLMs run with reasoning turned off or low.
22. **No version pinning for several models.** See `docs/MODEL-REGISTER.md`.
23. **Cost is computed, not billed.** Token usage times list price. Providers that bill the record
    once per question cost more than a single-question estimate suggests.
24. **Latency is ours.** End-to-end from one machine and network, including retries. Gateway
    latency includes the gateway.
25. **Uncertainty is partial.** Bootstrap ranges treat cases as independent although cases share
    eight fictional studies per split. They exclude run-to-run variation and provider changes.
26. **Citations for LLMs only.** Decision models return no evidence, so "unsupported finding" is
    measured at the label level for every system and at the citation level only for LLMs.

## Clinical data tools

27. **Not executed.** CDISC CORE, sdtmchecks and OpenRBQM were assessed and an export was written,
    but none was run. No statement is made about what they find on this data.

## Legal

28. **Open questions.** Several provider terms and the privacy position of Track A are unresolved.
    Nothing in this repository is legal advice. See `docs/RELEASE-APPROVAL.md`.
