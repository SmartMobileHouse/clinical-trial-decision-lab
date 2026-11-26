# Release approval

Status on 2026-11-26: **Approved by the owner for release 0.1.0. Not yet committed, pushed or published.**

Nothing has been pushed to a public remote, published or deployed. This file is the checklist for
Smart Mobile House. A release needs every blocker below closed, the approvals recorded in
`data/source-manifest.json`, and `make release-check` passing. Passing checks is necessary, not
sufficient: they do not give legal clearance.

## Release 0.1.0: scope and sign-off

Prepared on 2026-11-26. The owner instructed that the three entries below be recorded in
`data/source-manifest.json` on that date. The per-model publication flags for the five tested
models were set in `configs/models.yaml` on the same date, on the owner's instruction.

**What would be published**

- The software, the synthetic dataset and the documentation.
- The screening study in `studies/screening/`: frozen plan, sample identifiers, runners, locked
  analysis, post-hoc checks, aggregate results for seven systems, the trained classifiers' per-paper
  predictions, aggregate scores of the exploratory pilots.
- The report on the Smart Mobile House website (reviewed as draft 0.2, published as version 1.0).

**What stays out**

- Paper titles and abstracts.
- The hosted models' per-paper answers (owner decision of 2026-11-26: held back, available on request).
- Track A (regulatory findings): every record, register and result.
- Run folders, raw provider traces, `.env`.

### The three entries the release check needs

`make release-check` fails on exactly these three. Each needs a name and a date from the owner.

| Entry in `data/source-manifest.json` | What signing it states | Prepared evidence | Open point for the owner |
|---|---|---|---|
| `reviews.sensitive_data` | A person looked at every tracked file for personal or sensitive information | Automated scan passes (153 files, no hits). The screening study holds identifiers and scores only; a test asserts that no abstract text is stored. Review titles and PubMed ids are bibliographic. | Owner decision of 2026-11-26: a Microsoft Presidio scan (`make pii`) replaces the human review. Result: 155 files, no unreviewed finding. Seven names of real people are kept on purpose as public authorship credits. The scan is evidence, not proof: no person read every file, and the restricted-register name scan was not run. |
| `reviews.legal` | The items marked UNCLEAR or REQUIRES PERMISSION that affect this release were reviewed | See the table of items below | No specialist lawyer has reviewed them. The owner decided on 2026-11-26 not to seek a lawyer's view for this release. Signing this entry would record an owner risk decision, not specialist advice; say so in the `scope` text. |
| `release` | The owner approves publishing version 0.1.0 | `make check` passes | Sign last, after the commit exists, and record the commit in the approval table at the end of this file. |

Wording template (the recorded entries are in the manifest):

```json
"reviews": {
  "sensitive_data": {"status": "approved", "reviewer": "<owner name>", "date": "<date>",
    "scope": "Human review of every tracked file for personal or sensitive information, on top of the automated scan."},
  "legal": {"status": "approved", "reviewer": "<owner name>", "date": "<date>",
    "scope": "Owner risk decision without specialist legal review. Items reviewed: provider terms for the five tested models, open-licence abstracts, review titles, CC BY Cochrane reviews in one pilot. Track A stays unpublished."},
  "clinical_expert": {"status": "pending"}
},
"release": {"version": "0.1.0", "approved": true, "approved_by": "<owner name>", "date": "<date>"}
```

### Legal items that affect this release

| Item | Our reading | Status |
|---|---|---|
| Abstracts sent to providers | Only abstracts under CC0, CC BY, CC BY-SA or CC BY-ND were sent, in every sample (checked 2026-11-26). Classifier training data was filtered the same way and never left the machine. | No open question |
| Abstracts in the repository | None | No open question |
| Study membership labels | TrialPanorama benchmark, Apache-2.0 | No open question; attribution is in the report and the study README |
| Review titles | Bibliographic references to published reviews | Owner accepted on 2026-11-26 |
| Review criteria text | One exploratory pilot used 11 Cochrane reviews that carry a CC BY licence. Cochrane's website terms forbid AI use in general; we read the article's own licence as governing. No such text is quoted or stored here. | Owner risk; not reviewed by a lawyer |
| Perplexity (Decider 1.3) | Our registry records benchmark publication as REQUIRES PERMISSION. No written permission exists. | Owner decided to publish aggregate results. Raw outputs stay out. |
| Bespoke Labs (Nimble 4.1) | Terms not public, UNCLEAR. The model was called in the locked run. The terms shown at sign-up were not kept (owner, 2026-11-26). No terms page was found on 2026-11-26. | Owner decision of 2026-11-26: publish, and state in the report and README that no published terms were found on that date |
| Google Gemini Decision 1 through OpenRouter | Registry entry added 2026-11-26. Commercial use allowed; publication of outputs and of test results not addressed by either set of terms (UNCLEAR). Google forbids using the service to develop competing models. | Owner risk; no restriction found, no express permission |
| OpenAI (GPT-6 Luna) | Allowed; publicity clause limits use of name and logo | Plain naming only, no logo, no implied partnership |
| Anthropic (Claude Haiku 5.5) | Allowed; no benchmarking clause | No open question |
| Track A, GDPR and regulatory letters | Unresolved | Not part of this release |

### Per-model publication flags (B4)

The report shows results for five hosted models. Their flags are set in `configs/models.yaml` with the
basis recorded there (aggregate results only, raw outputs withheld); every other model stays unapproved.
The wording first proposed was:

| Registry id | Proposed `publication` entry |
|---|---|
| `pplx_decider_v13` | `{approved: true, basis: "Owner decision <date>: aggregate results only, published without written permission; terms record REQUIRES PERMISSION. Raw outputs withheld."}` |
| `nimble` | `{approved: true, basis: "Owner decision <date>: aggregate results only; hosted API terms not public. Raw outputs withheld."}` after the terms point above is closed |
| `llm_openai` | `{approved: true, basis: "Owner decision <date>: OpenAI Services Agreement read 2026-11-16; aggregate results; no logo."}` |
| `llm_anthropic` | `{approved: true, basis: "Owner decision <date>: Anthropic terms read 2026-11-16; aggregate results."}` |
| `or_gemini_decision_1` | `{approved: true, basis: "Owner decision <date>: aggregate results only; OpenRouter and Google terms read 2026-11-26, no benchmarking clause found. Raw outputs withheld."}` |

These flags do not gate the current release check, because no per-paper provider output and no
evidence bundle is stored in this repository. They should still be set before the report goes out,
so the registry matches what was published.

### Other gaps found while preparing this

- **Source register.** Closed on 2026-11-26: TrialPanorama, Europe PMC and SYNERGY were added to
  `data/source-manifest.json`, ClinicalTrials.gov was corrected from "not used", and notices were added
  to `THIRD_PARTY_NOTICES.md`. Two terms pages could not be re-read that day (Europe PMC, ClinicalTrials.gov).
- **This document's older sections** below were written for the synthetic benchmark and Track A. B6
  is now closed for the screening study (a paid run exists). B5 and B7 do not apply to the screening
  study; they still apply to the synthetic benchmark and Track A.
- **CI (B8)** has never run on a hosted runner; it can only run once the repository exists.
- **Uncommitted work.** The study folder, the new test, the README, the logo, `CITATION.cff` and an
  older change to `configs/models.yaml` (which the frozen run depends on) are not committed.

## How approval is recorded

`data/source-manifest.json` holds three reviews and the release decision:

```json
"reviews": {
  "sensitive_data":  {"status": "approved", "reviewer": "<name>", "date": "<date>"},
  "legal":           {"status": "approved", "reviewer": "<name>", "date": "<date>"},
  "clinical_expert": {"status": "pending"}
},
"release": {"version": "0.1.0", "approved": true, "approved_by": "<name>", "date": "<date>"}
```

Per model, publication of results is approved in `configs/models.yaml`:

```yaml
publication: {approved: true, basis: "<who approved, when, on what written basis>"}
```

`make release-check` fails while the sensitive-data review, the legal review or the release decision
is pending. The clinical expert review does not block a release of code and synthetic data; it
blocks any claim of validated accuracy.

## Release blockers

| # | Blocker | Why it blocks | Owner action |
|---|---|---|---|
| B1 | Human review for personal or sensitive information not recorded | Required before any publication; the automated scan is not enough | Review every tracked file; record the review |
| B2 | Specialist legal review of open questions not recorded | Several determinations are UNCLEAR or REQUIRES PERMISSION | Review section "Items needing specialist legal review" of `docs/DATA-LICENSING-AUDIT.md`; record the outcome |
| B3 | Release decision not recorded | No publication without an explicit approval step | Approve in the manifest |
| B4 | No model's results are approved for publication | Every model has `publication.approved: false` | Decide per provider after B2; see the table below |
| B5 | Track A (regulatory findings) privacy position unresolved | Source letters name individuals; an EU publisher needs a lawful basis | Decide: keep private, or publish de-named aggregates only, or publish cases after counsel review |
| B6 | No paid API run exists | The research question cannot be answered without model results | Approve a budget and run; see `docs/REPRODUCIBILITY.md` |
| B7 | Reference labels not reviewed by a qualified expert | Without it no claim of clinically validated accuracy may be made | Commission a review, or publish with the "not expert-validated" statement |
| B8 | CI workflow never executed on a hosted runner | The gate has only run locally | Run it once in the destination repository before release |

B1 to B3 block any public release, including a code-only one. B4 to B7 block publishing model
results or the research report. B8 should be closed before the repository is made public.

## Provider decisions needed (B4)

| Provider | Our reading of benchmark publication | Suggested action |
|---|---|---|
| OpenAI | Allowed; publicity clause limits use of name and logo | Approve; no logo, no implied partnership; keep outputs out of any model training |
| Cloudflare | Allowed if replication information is published | Approve; the open repository satisfies the condition |
| Anthropic | Allowed; no benchmarking clause | Approve |
| TypeSafe | Unclear; confidentiality wording | Ask in writing, or decide on the basis of the Fraud Decision Lab precedent |
| Morph | Unclear; "benchmark farming" wording for subscriptions | Ask in writing; use metered API only |
| Perplexity | Requires permission | Get written permission before publishing any result |
| Opper, Runware (gateways) | Unclear; upstream terms apply | Follow the upstream provider's answer |
| Bespoke Labs | Terms not public | Read and archive terms at sign-up before any call |
| Liquid AI | Unclear; standard endpoints may train on inputs | Use only a zero-retention endpoint; ask about publication |
| Microsoft | Allowed with conditions; Preview | Confirm the response format with one live call; accept the reciprocal benchmarking clause knowingly |

## Data decisions

| Item | Decision recorded | Open |
|---|---|---|
| Synthetic dataset v1 | Approved for every use; original work, MIT | none |
| Track A descriptions, register, results | Local only; outside the repository and its history | B5 |
| Sending Track A descriptions to model providers | Not allowed (`external_processing_allowed: false`) | Owner decision after B5 |
| CDISC pilot data, PHUSE and safetyData copies | Not used; never to be copied in | none |
| ClinicalTrials.gov, AACT, Project Data Sphere | Not used | Re-audit before any future use |
| OpenRBQM, CDISC CORE, sdtmchecks, anomaly spotter | Optional external tools; not bundled | none |

## Release checklist

Technical

- [ ] `make check` passes on a clean clone.
- [ ] `uv run triallab data verify` passes.
- [ ] The CI workflow has passed in the destination repository.
- [ ] `git log --all --name-only` shows no data, outputs or private files, now or earlier.
- [ ] No run folder, raw provider trace or cached response is tracked.

Rights and privacy

- [ ] B1, B2 and B3 recorded in the manifest; `make release-check` passes.
- [ ] `THIRD_PARTY_NOTICES.md` and `docs/THIRD-PARTY-LICENSES.md` match `uv.lock`.
- [ ] Every model whose results appear has `publication.approved: true` with a written basis.
- [ ] Quoted provider terms were re-read at source on the release date.
- [ ] No name, letter number or letter URL from Track A appears anywhere in the repository or report.

Research claims

- [ ] Every number in the report comes from the evidence bundle of a named run.
- [ ] Models without results show "not run" or "withheld", never a number.
- [ ] Synthetic and regulatory results are in separate sections and never combined.
- [ ] The report states that data is synthetic, that the case mix is designed, that labels are not
      expert-validated, and that the rules baseline shares the reference logic.
- [ ] Model identifiers, run dates, sample sizes and prices with their dates are shown.

Destination

- [ ] Private vulnerability reporting, secret scanning and push protection enabled.
- [ ] Default branch protected; workflow token read-only.
- [ ] Repository and report links resolve.
- [ ] The explicit approval to publish is recorded here: approver, date, commit.

## Approval record

| Date | Version | Commit | Approved by | Scope |
|---|---|---|---|---|
| 2026-11-26 | 0.1.0 | the initial public commit | Jerzy Pietruszewski | Software, synthetic data, screening study (aggregate results, no raw provider outputs, no abstracts), report version 1.0 (reviewed as draft 0.2). Sensitive-data review by Presidio scan; legal entry is an owner risk decision. |
