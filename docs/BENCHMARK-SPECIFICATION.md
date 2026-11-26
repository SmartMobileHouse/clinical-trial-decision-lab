# Benchmark specification

Clinical Trial Decision Lab, study 1: **Enrollment Eligibility and Informed Consent Issue Triage**.
Specification version 1, frozen on 2026-11-16, before any model was run. Question wording,
reference-label rules, metrics and the test set must not change after model results are seen. Any
change needs a new version number and new predictions.

## 1. Research question

> Can specialized AI decision models identify potential clinical trial enrollment and
> informed-consent problems more effectively and efficiently than deterministic clinical rules and
> general-purpose LLMs?

What is compared: decision models (models that take a record plus yes/no questions and return a
probability per question), a deterministic rules baseline, and general LLMs forced into structured
output.

What would count as evidence: on a frozen test set with independently derived reference labels, a
paired difference between systems whose 95% range excludes zero, reported next to cost and latency.

What this study cannot establish: performance in real clinical operations, clinical validity, or
regulatory correctness. This is research into decision support. No system here makes clinical or
regulatory decisions, and none recommends treatment changes or patient-safety actions.

No hypothesis about which system wins was registered.

## 2. Two tracks, never combined

| | Track A: regulatory findings | Track B: synthetic operational cases |
|---|---|---|
| Material | Descriptions of findings in public FDA warning letters | Fictional protocols and participant records |
| Task | Retrospective classification of a documented finding | Triage of a participant record against its protocol |
| Evidence class | Real, public, already-adjudicated allegations; possibly in model training data | Synthetic; reproducible; never seen by any model before release |
| Question set | `finding` (2 questions) | `triage` (8 questions) |
| Reference labels | Provisional: assigned by the researcher from FDA's wording | Deterministic: rules over objective facts, two derivations that must agree |
| Status in v0.1.0 | Built and run locally; **not distributed, results withheld** | Bundled; frozen; rules baseline measured |

Scores from the two tracks are never merged into one headline number.

## 3. Track B input: the case packet

A case packet is everything a system may see. Schema: `src/triallab/schema.py` (`CasePacket`).

```
packet_version
protocol
  study_id
  versions[]            version, effective_date, summary_of_changes
  criteria[]            ref, kind (inclusion|exclusion), text, parameter, unit,
                        eligible_if {minimum, maximum}  (both inclusive),
                        applies_from_version, applies_until_version
  accepted_units{}      parameter -> [{unit, factor, offset}]   protocol_value = value * factor + offset
  screening_window_days
  retest_policy         text
  consent_policy        text
  consent_versions[]    ref, version, irb_approval_date, site_effective_date, reconsent_required
record
  participant_id, site_id          synthetic identifiers
  assessments[]         ref, parameter, value, unit, collected_date, source
  consents[]            ref, icf_version, participant_signed, investigator_signed,
                        document_on_file, verification_status
  events[]              ref, type (study_procedure|enrollment|randomization|study_visit|screen_failure),
                        occurred (date-time with UTC offset), description
  notes[]               ref, date, author_role, text
```

Every citable item has a short `ref` (for example `ASM-2`). A packet is about 4,400 characters
(roughly 1,500 tokens); the longest is under 5,300 characters.

**Allowed evidence.** Only the packet. No outside knowledge of units, protocols or regulations is
needed: limits are stated, conversions are listed, and policies are written in the packet. A system
must not assume facts that are not in the packet.

**Never sent:** the case identifier, the scenario, tags, the hidden meaning of notes, reference
labels.

## 4. Questions and output

Every system answers the same frozen yes/no questions (`configs/questions-v1.json`). Decision models
return a probability of "yes" per question; rules and LLMs return true or false. A probability at or
above 0.5 counts as "yes". The 0.5 threshold was fixed in advance.

| Question id | Yes means |
|---|---|
| `eligibility_issue` | The record documents that an enrolled participant did not meet an eligibility requirement |
| `eligibility_insufficient` | Evidence needed to confirm an eligibility criterion is missing or unusable |
| `eligibility_conflicting` | Records about an eligibility criterion contradict each other and nothing resolves it |
| `consent_issue` | The record documents an informed-consent compliance problem |
| `consent_insufficient` | Consent documentation needed to decide is missing or unusable |
| `consent_conflicting` | Consent records contradict each other and nothing resolves it |
| `review_needed` | The case should be queued for human review beyond routine monitoring |
| `review_expedited` | The case should receive expedited human review |

LLMs additionally return `evidence_refs`: the refs that support any "yes". Decision models cannot
cite evidence; no citation metric is computed for them.

### The four decision outputs

They are derived from the answers by `src/triallab/reference/derive.py`. The same function is used
for the reference and for every system.

1. **Eligibility outcome** and 2. **Consent outcome**, each one of:

   | Outcome | Derived when |
   |---|---|
   | `potential_issue` | `<domain>_issue` is yes |
   | `conflicting_evidence` | else `<domain>_conflicting` is yes |
   | `insufficient_evidence` | else `<domain>_insufficient` is yes |
   | `no_issue` | otherwise |

   Precedence: a documented issue outranks a contradiction, which outranks missing evidence.

3. **Missing or conflicting evidence**: `missing_evidence` is yes when either `_insufficient` answer
   is yes; `conflicting_evidence` when either `_conflicting` answer is yes.

4. **Review priority**: `expedited` when `review_expedited` is yes; else `standard` when
   `review_needed` is yes; else `routine`.

## 5. Reference-label rules (Track B)

Reference labels come from deterministic logic over objective facts. No language model takes part.

**Step 1: facts.** The generator builds a compliant record, then a scenario changes it in one
defined way. Where the deciding fact is written in a free-text note, the generator first records the
fact as structured data (the hidden *note meaning*) and then writes the sentence from it.

**Step 2: rules.** The reference adjudicator (`src/triallab/reference/adjudicate.py`) applies the
note meanings to the record and runs eight protocol rules (`src/triallab/clinical/rules.py`):

| Rule | Finding codes |
|---|---|
| Eligibility thresholds | `criterion_not_met` (issue) |
| Missing eligibility tests | `required_assessment_missing`, `result_unusable` (missing) |
| Screening and enrollment timing | `assessment_outside_window`, `assessment_after_enrollment` (issue) |
| Consent completion | `consent_record_missing`, `consent_unverified` (missing); `consent_signature_incomplete` (issue) |
| Consent version applicability | `consent_version_not_current` (issue) |
| Consent timing | `consent_after_procedure` (issue); `consent_order_undetermined` (missing) |
| Re-consent evidence | `reconsent_record_missing` (missing) |
| Inconsistent documentation | `conflicting_results`, `consent_timestamp_conflict`, `note_contradicts_record` (conflict) |

Fixed conventions:

- Eligibility findings concern enrolled participants only. A failing result for a participant who
  was correctly not enrolled is not an issue.
- The most recent result collected on or before the enrollment date governs a criterion. Limits are
  inclusive. Results on the first day of the screening window are inside it.
- A result is usable only with a value and a unit that is the protocol unit or a listed conversion.
- Criteria apply according to the protocol version in effect on the enrollment date.
- Consent must precede the first study-specific procedure. Moments with a UTC offset are compared as
  instants. When a date has no time and falls on the same day as the procedure, the order cannot be
  determined.
- The consent version must be the one in effect at the site on the signing date.
- **Absence of documentation is never treated as proof that consent did not occur.** A missing
  consent record is `insufficient_evidence`, not `potential_issue`.

**Step 3: independent check.** The scenario declares the findings it intended. For every case the
declared findings must equal the adjudicated findings. Generation stops otherwise, and the test
suite repeats the check on the committed files. Each label therefore has two derivations: by
construction and by rule.

**Review-priority criteria.** `expedited` when any finding is `criterion_not_met`,
`consent_after_procedure` or `consent_record_missing`. `standard` for any other finding. `routine`
when there is none.

## 6. Missing data and abstention

- Missing or unusable evidence in the packet has its own outcome (`insufficient_evidence`).
  Contradictions have their own outcome (`conflicting_evidence`). Saying so is the correct answer,
  not a failure.
- **Model abstention** means answering one of these two outcomes. Abstention quality is measured as
  precision and recall against the cases whose reference outcome is one of the two, plus the
  over-abstention rate on determinate cases.
- A system that returns no usable answer (API error, timeout, refusal, invalid or incomplete
  output) is scored as wrong for every class and as not flagging the case. Invalid output is never
  repaired. Coverage is reported separately.
- An input that exceeds a model's context is refused before sending and recorded as invalid.
  Evidence is never truncated silently.

## 7. Dataset design (Track B)

| Split | Cases | Seed | Use |
|---|---|---|---|
| `dev` | 80 | 1101 | Wording and adapter development. May be inspected freely |
| `calibration` | 120 | 2202 | Reserved for fitting decision thresholds in a secondary analysis. Never used for reported scores. Threshold fitting is not implemented in v0.1.0 |
| `test` | 400 | 3303 | Frozen. The only split used for reported results |

Splits use different seeds and different fictional studies, sites and participants. Nothing is
trained on any split: decision models and LLMs are used zero-shot.

Each split holds 50% routine, 25% issue and 25% ambiguous cases. **These shares are design targets.
They are not estimates of how often such issues occur in real trials.**

The 36 scenarios of the test split (`src/triallab/synthetic/scenarios.py`):

| Category | Scenario | Cases |
|---|---|---|
| routine | plain compliant | 86 |
| routine | value exactly at a limit, or results on the first day of the window | 14 |
| routine | failing result, participant correctly not enrolled | 12 |
| routine | failing result, passing repeat before enrollment | 12 |
| routine | accepted alternative unit that converts to an eligible value | 12 |
| routine | value meets the amended limit, enrolled after the amendment | 10 |
| routine | required re-consent done | 10 |
| routine | consent and procedure on the same day, consent first | 10 |
| routine | procedure time in UTC reads earlier but happened later | 8 |
| routine | passing repeat documented only in a note* | 10 |
| routine | contradictory results, a note voids the wrong one* | 8 |
| routine | consent date without time, a note records the order* | 8 |
| issue | criterion not met | 10 |
| issue | one measurement step outside a limit | 10 |
| issue | alternative unit that converts to an ineligible value | 10 |
| issue | value meets only the amended limit, enrolled before the amendment | 8 |
| issue | fails a stricter overlapping criterion | 8 |
| issue | results outside the screening window | 8 |
| issue | required result only after enrollment | 6 |
| issue | consent after the first procedure | 12 |
| issue | superseded consent version | 8 |
| issue | investigator signature missing | 6 |
| issue | a note documents a procedure before consent* | 8 |
| issue | procedure time in UTC reads later but happened earlier | 4 |
| issue | eligibility and consent issue together | 2 |
| ambiguous | required assessment missing | 10 |
| ambiguous | unit missing | 10 |
| ambiguous | unit not listed in the protocol | 6 |
| ambiguous | contradictory same-day results | 12 |
| ambiguous | no consent record | 12 |
| ambiguous | consent form unverified or not on file | 10 |
| ambiguous | consent and procedure on the same date, no time | 10 |
| ambiguous | two consent records with contradicting times | 10 |
| ambiguous | re-consent documentation absent | 8 |
| ambiguous | a note contradicts a structured result* | 8 |
| ambiguous | missing unit and undetermined consent order together | 4 |

\* Text-dependent: the deciding fact is written only in a free-text note (42 of 400 cases).

Distractor notes with no bearing on the answer, some using the words "consent" and "eligibility",
are added to cases of every kind.

**Inclusion and exclusion.** Every generated case is included. There is no post-hoc removal of
cases. A case is excluded only if generation fails its integrity check, which stops the build.

## 8. Track A: regulatory findings

- **Source.** FDA warning letters to clinical investigators, sponsors, sponsor-investigators and
  review boards, published on fda.gov. Each case is one finding from one letter.
- **Input.** A short neutral description of the finding in the researcher's own words. Regulation
  citations, study names, recipient names and the charge wording are removed, so the text does not
  state its own label.
- **Questions.** Does the observation concern enrollment eligibility? Does it concern informed
  consent? Contrast findings (for example drug accountability or dosing errors) answer no to both.
- **Reference.** FDA's stated finding, categorised by the researcher. **Provisional**: no qualified
  clinical-compliance expert has reviewed the labels. A warning letter states allegations at a point
  in time; it is not a final adjudication, and later correspondence can change the status.
- **Leakage.** The final classification is never in the input. No candidate model's output was used
  as a label. Public letters may be in model training data, so this track measures retrospective
  classification, not prospective detection.
- **Record per case** (kept in a private register): FDA source URL, document date, retrieval date,
  the finding, evidence available in the letter, issue category, label provenance, later status,
  publication rights, suitability.
- **Metrics.** Per question: precision, recall, F1 and accuracy; share of cases with both answers
  right. With about 50 cases the ranges are wide.
- **Baseline.** A transparent keyword matcher. If it scores high, the task is mostly vocabulary
  matching and model scores must be read in that light.

## 9. Systems

- **Deterministic rules** (`rules`): the eight rules on structured fields. They do not read note
  text. See limitation 1 in section 12.
- **Anchors**: `flag_all` and `flag_none` bound the review-load metrics. They are not systems.
- **Decision models and LLMs**: as listed in `configs/models.yaml`. Every model receives the same
  packet and the same question text. Only the serialization differs: System One `state` and
  `questions`; OpenAI Decisions `input_json` and predicates; LLMs get the questions as instructions
  and the packet as JSON, with a strict output schema.
- **Gateways**: a model reached through a gateway is a separate system. Its latency includes gateway
  processing and is never attributed to the underlying model.
- Clinical data tools (CDISC CORE, sdtmchecks, OpenRBQM) answer different questions and are not
  ranked against these systems. See `docs/CLINICAL-TOOLS.md`.

## 10. Metrics

Implemented in `src/triallab/evaluate/`. Definitions are fixed (evaluation version 1).

**Decision quality**

| Metric | Definition |
|---|---|
| Critical-case recall | Share of cases with reference priority `expedited` that the system flags for any review |
| Issue precision and recall | A case is positive when either domain outcome is `potential_issue` |
| Macro-F1 | Per domain, mean F1 over the outcome classes present in the reference |
| Accuracy | Per domain; and case accuracy: both domain outcomes right. Class balance is a design choice, so accuracy alone says little |
| False positives per 100 cases | Cases with reference priority `routine` that the system flags, per 100 cases |
| Missed issues | Cases with a documented issue that the system never queues for review |
| Precision and recall at a fixed review budget | Top 10% and top 25% of the system's ranking, against critical cases |
| Abstention quality | Precision, recall and over-abstention rate, per (case, domain) |
| Unsupported finding rate | Share of the system's `potential_issue` calls where the reference is `no_issue` or `insufficient_evidence` |
| Evidence consistency | Share of answer sets that are logically consistent (expedited implies review; any reason implies review; review implies a reason). For systems that cite refs: share of cited refs that exist, and share of flagged cases whose cited refs overlap the reference evidence |
| Review-priority agreement | Exact agreement and linear-weighted kappa over three levels |

Review-budget ranking uses p(`review_needed`) + p(`review_expedited`) when a system reports
probabilities, otherwise its priority level. Ties are broken by a fixed hash of the case identifier.

**Probability quality**, only for systems that report probabilities: Brier score, expected
calibration error with ten equal-width bins, and the reliability table. Reported probabilities are
not assumed to be calibrated. No probability is invented for a system that returns only yes or no.

**Performance**: p50 and p95 end-to-end latency; throughput under the run's concurrency and rate;
API failure rate; retry rate; schema-failure rate; refusal rate; tokens; cost per 1,000 cases; cost
per correctly detected issue. Cost is provider-reported token usage times the list price in the
registry. It is marked as measured only when every call reported usage; otherwise the estimated
part is shown separately. It is never an invoice.

## 11. Statistical methodology

- **Frozen test set** with deterministic seeds; fingerprints of inputs, questions, registry and code
  are bound to every run.
- **Uncertainty**: paired bootstrap, 1,000 resamples, stratified by scenario category, percentile
  95% ranges for the headline metrics and for each system's difference from the rules baseline.
- **Paired comparison**: exact two-sided McNemar test on case accuracy against the rules baseline.
- **Thresholds**: 0.5 for the primary analysis. Thresholds fitted on the calibration split would be
  a secondary analysis, labelled as such. That analysis is not implemented in v0.1.0.
- **Repeated runs**: `--repeats` re-asks each case; the share of cases whose answers changed is
  reported. Ranges do not include this variability.
- **Timeouts and missing responses**: retried up to twice by the shared HTTP layer; a case with no
  usable final answer counts against the system.
- **Snapshots**: model identifiers, reported model names, prices and run dates are stored per run.
- **Batching**: one case per request with all its questions. A provider-side batch experiment, if
  ever run, is reported separately and never mixed into the latency comparison.
- **Stratified reporting**: results are shown by category and separately for structured and
  text-dependent cases.
- Raw results (`attempts.jsonl`, `predictions.jsonl`) are stored apart from statistics
  (`metrics.json`). `triallab replay` recomputes every statistic from the raw files and must match.

## 12. Limitations

See `docs/LIMITATIONS.md` for the full list. The three that most affect interpretation:

1. **The rules baseline shares the reference logic for structured evidence.** It agrees with the
   reference on every case decided by structured fields, by construction, and can be wrong only on
   text-dependent cases. A model can at best tie the rules on structured cases. The overall gap
   between models and rules therefore depends on the designed share of text-dependent cases. Always
   read the two strata separately.
2. **Synthetic data.** Records are simpler and cleaner than real source documents, and the case mix
   is designed. Results do not transfer to real trials.
3. **No expert validation.** Reference rules encode the stated protocol and consent policies of
   fictional studies. Track A labels are provisional.
