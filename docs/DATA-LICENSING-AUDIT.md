# Data licensing audit

Verification date: **2026-11-16**. Scope: Clinical Trial Decision Lab v0.1.0.

This is our reading of each source's published terms on the verification date. **It is not legal advice and it does not give legal clearance.** Where terms are ambiguous we say so, exclude the source from the public release, and list the question for specialist review in [section 16](#16-items-needing-specialist-legal-review).

## 1. Purpose and method

Smart Mobile House is a commercial company based in the EU. It publishes research on its website and releases code on GitHub under the MIT licence. This audit records what each candidate data source, tool and model provider allows us to use, process, publish and redistribute.

Method:

- Every source was re-checked from its primary location on the verification date: licence files, terms pages, repository `LICENSE`, `DESCRIPTION` and `README` files, and publisher documentation. Earlier conclusions were not reused.
- No account was created and no data was uploaded to any service. No tool was installed or run.
- Every determination names its provision. The provision tables give the URL and a quoted excerpt.
- The full working notes are kept as appendices: [A (data sources)](research/appendix-a-data-sources.md), [B (tools and future sources)](research/appendix-b-tools-and-future-sources.md), [C (model providers)](research/appendix-c-model-providers.md).

**Quote fidelity.** Quotes for data sources and tools were taken from fetched text. Quotes for model providers (section 12) came through a fetch tool that summarises pages with a small model, and OpenAI's policies came through a public reader proxy after a direct fetch was refused. Short quotes may be clipped. **Re-read every clause at its source before anyone signs off a publication.**

## 2. How to read this audit

Classifications, used exactly:

| Classification | Meaning |
|---|---|
| ALLOWED | The terms we read permit this use. Conditions, if any, are stated. |
| PROHIBITED | The terms we read forbid this use. |
| UNCLEAR | The terms are silent, contradictory or could not be read. Not treated as permission. |
| REQUIRES PERMISSION | The use needs the rights holder's agreement first. |

Restriction types are kept apart, because they are solved by different people:

| Tag | Type | Example |
|---|---|---|
| [C] | Copyright or licence | A licence forbids modified copies. |
| [P] | Privacy and data protection | A public document names a living person. |
| [T] | Contractual or terms of use | A provider's terms limit where outputs may be shown. |
| [S] | Scientific limitation | A dataset is not comprehensive or lacks needed fields. |

The sixteen uses assessed for every source:

(a) commercial-company research use; (b) internal processing; (c) processing through external AI APIs; (d) publishing aggregate benchmark metrics; (e) publishing charts and visualizations; (f) publishing transformed or reconstructed records; (g) publishing per-case inputs and model predictions; (h) publishing cached API responses; (i) publishing prompts or quoted source text; (j) publishing trained models or derived artifacts; (k) redistributing original records; (l) redistributing modified records; (m) including files inside an MIT repository; (n) attribution and NOTICE requirements; (o) share-alike requirements; (p) privacy, data protection and contractual restrictions.

For (n) and (o) the cell states the obligation rather than a permission.

## 3. Release decision summary

| # | Source | Used in v0.1.0 | In the repository | Verdict | Blocker or condition |
|---|---|---|---|---|---|
| – | Original synthetic cases (this project) | Yes, synthetic track | Yes | ALLOWED for every use | None. MIT. |
| 1 | FDA warning letters | Yes, regulatory-finding track, privately | **No** | ALLOWED on copyright; UNCLEAR on privacy | Letters name individuals. Per-case material, letter URLs and letter numbers stay out until a privacy review and an owner decision. |
| 2a | ClinicalTrials.gov | No | No | ALLOWED with conditions | Not under MIT; attribution, processing date and modification log needed. Future source. |
| 2b | AACT | No | No | UNCLEAR | Terms are behind a login and were not read. Excluded. |
| 3 | CDISC SDTM/ADaM Pilot 01 | No | No | PROHIBITED for modified or MIT-licensed publication | Terms forbid modifying the data. Never copy into this repository. |
| 4 | PHUSE phuse-scripts, safetyData | No | No | UNCLEAR for the CDISC-derived data | A downstream MIT label does not override upstream CDISC terms. Excluded. |
| 5 | Gilead gsm.datasim | Evaluated, not used | No | ALLOWED | Not adopted for scientific reasons ([S]), not legal ones. |
| 5 | Gilead clindata | No | No | UNCLEAR on privacy | Described as both "synthetic" and "anonymized". Do not redistribute. |
| 6 | OpenRBQM / gsm packages | No (optional external tool) | No | ALLOWED to invoke | Not bundled, not a dependency, not executed. |
| 7 | CDISC CORE | No (optional external tool) | No | ALLOWED to invoke; cache content UNCLEAR | CDISC Library terms not obtained; never publish cached Library content. |
| 8 | pharmaverse sdtmchecks | No (optional external tool) | No | ALLOWED | Thin coverage for this topic ([S]). |
| 9 | IMPALA CTAS | No (future experiment) | No | ALLOWED to invoke | GPL dependencies; never bundle. |
| 10 | Project Data Sphere | No (future source) | No | REQUIRES PERMISSION; most publication uses PROHIBITED | Individual access, cancer research purpose only, no external AI APIs. |

Only one data source is distributed with this repository: the project's own synthetic cases.

## 4. Source 1: FDA inspection findings and warning letters

**Inspected:** fda.gov policy and listing pages below, with their "content current as of" dates; two sample warning letters. Rights holder: none for U.S. Government works. Applicable artifacts for every row: warning-letter pages, close-out and response letters, Form 483 material, inspection database exports.

### Provisions

| ID | Source URL | Quoted excerpt |
|---|---|---|
| F1 | https://www.fda.gov/about-fda/about-website/website-policies (content current as of 01/19/2024) | "Unless otherwise noted, the contents of the FDA website (www.fda.gov) — both text and graphics — are not copyrighted. They are in the public domain and may be republished, reprinted and otherwise used freely by anyone without the need to obtain permission from FDA. Credit to the U.S. Food and Drug Administration as the source is appreciated but not required." |
| F2 | same page | "FDA strongly recommends that the copied item lists the date that the material was copied and provides a link back to its source on the FDA website." |
| F3 | https://www.law.cornell.edu/uscode/text/17/105 | "Copyright protection under this title is not available for any work of the United States Government" |
| F4 | https://www.fda.gov/about-fda/website-policies/fda-name-and-logo-policy (08/31/2023) | "The FDA Mark must not be used: … By any third party, unless specifically authorized by the FDA in writing … To indicate or imply endorsement by the FDA." |
| F6 | https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/compliance-actions-and-activities/warning-letters | "Matters described in FDA warning letters may have been subject to subsequent interaction between FDA and the letter recipient that may have changed the regulatory status of issues discussed in the letter." |
| F7 | https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/warning-letters/about-warning-and-close-out-letters (03/20/2024) | "This procedure applies to Warning Letters issued on or after September 1, 2009." … "If the Warning Letter contains violations that by their nature are not correctable, then no close-out letter will issue." |
| F8 | Two sample warning letters (URLs kept in the private register) | Observed: the recipient is a named individual; the FDA field investigator is named; protocol, drug and sponsor are redacted "(b)(4)"; subject identifiers and some dates are redacted "(b)(6)". |
| F10 | https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/inspection-classification-database | "This database does not represent a comprehensive listing of all conducted inspections and should not be used as a source to compile official data." |
| G1 | GDPR Art. 6(1)(f), read from the unofficial mirror https://gdpr-info.eu/art-6-gdpr/ | "processing is necessary for the purposes of the legitimate interests pursued by the controller or by a third party, except where such interests are overridden by the interests or fundamental rights and freedoms of the data subject" |
| G2 | GDPR Art. 10, https://gdpr-info.eu/art-10-gdpr/ | "Processing of personal data relating to criminal convictions and offences or related security measures … shall be carried out only under the control of official authority or when the processing is authorised by Union or Member State law" |

### Analysis

- [C] FDA-authored text is not copyrighted in the United States (F1, F3). Two limits. "Unless otherwise noted" means material FDA did not write, such as quoted correspondence or attachments, is not covered. Section 105 is U.S. law; FDA does not expressly waive foreign copyright, so confidence for EU publication is medium.
- [P] Warning letters to clinical investigators name a living person and allege violations by that person. They also name FDA staff. For an EU publisher this is personal data. The "(b)(6)" redactions protect trial subjects, not the investigator. Whether these findings fall under Art. 10 ("offences") is not settled by what we read.
- [P] A letter number or a letter URL resolves to the named page. Publishing either is publishing an indirect identifier.
- [S] A warning letter states FDA's observations at a point in time. It may have been answered or closed out later (F6, F7). FDA's inspection databases are not comprehensive (F10). Public letters may also be in model training data.

### Matrix

| Use | Classification | Provisions | Explanation; confidence; open questions |
|---|---|---|---|
| (a) Commercial research use | ALLOWED | F1, F3 | "Used freely by anyone"; no non-commercial limit. High. |
| (b) Internal processing | ALLOWED | F1, G1 | No copyright bar. Processing named letters is still GDPR processing; record a legitimate-interest assessment. High [C], medium [P]. |
| (c) External AI APIs | ALLOWED [C]; UNCLEAR [P] if names are kept | F1, G1 | Sending named individuals' data to a processor needs a data processing agreement and a transfer mechanism. De-named descriptions avoid most of this. |
| (d) Aggregate metrics | ALLOWED | F1 | Aggregates hold neither protected expression nor personal data. High. |
| (e) Charts | ALLOWED | F1, F4 | No FDA logo; no implied endorsement. High. |
| (f) Transformed or reconstructed records | ALLOWED [C]; UNCLEAR [P] while a person is identifiable | F1, F2, F6, G1, G2 | State that records are modified; keep copy date. A record that resolves to a named person remains personal data. Medium. |
| (g) Per-case inputs and predictions | ALLOWED [C]; UNCLEAR [P] while a person is identifiable | F1, G1, G2 | A model prediction about an identifiable person adds a new, possibly wrong, statement about that person. Medium. |
| (h) Cached API responses | ALLOWED for cached fda.gov pages; UNCLEAR for FDA Data Dashboard API output | F1 | The dashboard API needs registration whose terms we did not see. |
| (i) Prompts or quoted source text | ALLOWED [C]; UNCLEAR [P] if names are quoted | F1 | FDA-authored text may be quoted. Third-party material inside letters is not covered. |
| (j) Trained models or derived artifacts | ALLOWED | F1, F3 | Models can memorise names; train only on de-named text. Medium [P]. |
| (k) Redistributing original records | ALLOWED [C]; UNCLEAR [P] | F1, F2, F8, G1, G2 | FDA prefers linking. Mirroring republishes personal data from the EU. Low to medium [P]. |
| (l) Redistributing modified records | ALLOWED with names removed and changes stated | F1, F2 | Do not present altered text as FDA's wording. High. |
| (m) Inside an MIT repository | ALLOWED, but not as MIT-licensed material | F1, F3 | Public-domain text cannot be licensed by us; mark it as outside the MIT grant. Medium. |
| (n) Attribution and NOTICE | Not required; recommended | F1, F2, F4 | Name the U.S. Food and Drug Administration in plain text, give the copy date, state non-endorsement. |
| (o) Share-alike | None | F1 | No downstream conditions. |
| (p) Privacy, data protection, contractual | UNCLEAR | F8, G1, G2, F6 | Named investigators and FDA staff; Art. 10 question open; accuracy duty implies tracking response and close-out status. No contractual terms on fda.gov content. Counsel needed. |

### Decision for this project

The regulatory-finding dataset is kept **outside this repository and its Git history**. Its descriptions were written without names. Nothing per-case is published: no descriptions, no letter URLs, no letter numbers, no predictions. External API processing is switched off until the owner decides. Aggregate metrics are permitted on copyright grounds but are also withheld until the owner approves. See [DATA-SOURCE-REGISTER.md](DATA-SOURCE-REGISTER.md).

## 5. Source 2: ClinicalTrials.gov and AACT

### 5.1 ClinicalTrials.gov

**Inspected:** Terms and Conditions at https://clinicaltrials.gov/about-site/terms-conditions (the starting URL `/terms-conditions` serves the same page). Page metadata gave a last-modified date of 2023-01-31. API version 2.0.5. The text was extracted from the site's own script bundle because the page renders in the browser; re-confirm it in a browser. Rights holder: U.S. Government (NLM/NIH) for the database; third parties for some content. Applicable artifacts: registry records, API responses, uploaded study documents.

| ID | Quoted excerpt (all from the URL above) |
|---|---|
| C1 | "These Terms and Conditions apply to all data obtained from ClinicalTrials.gov, independent of format and method of acquisition." |
| C2 | "ClinicalTrials.gov data are available to all requesters, both within and outside the United States, at no charge." |
| C3 | "In any publication or distribution of these data, you should: Attribute the source of the data as ClinicalTrials.gov / Update the data such that they are current at all times / Clearly display the date the data were processed by ClinicalTrials.gov / State any modifications made to the content of the data, along with a complete description of the modifications" |
| C4 | "You shall not assert any proprietary rights to any portion of the database, or represent the database or any part thereof to anyone as other than a United States Government database." |
| C5 | "You shall not use any email addresses extracted from our database for marketing or other promotional purposes." |
| C6 | "The ClinicalTrials.gov data carry an international copyright outside the United States and its Territories or Possessions. Some ClinicalTrials.gov data may be subject to the copyright of third parties; you should consult these entities for any additional terms of use." |
| C7 | "These terms and conditions are in effect as long as the user retains any of the data obtained from ClinicalTrials.gov." |

| Use | Classification | Provisions | Explanation; confidence; open questions |
|---|---|---|---|
| (a) Commercial research use | ALLOWED | C1, C2 | High. |
| (b) Internal processing | ALLOWED | C1, C2 | High. |
| (c) External AI APIs | ALLOWED | C1–C5 | No bar found; strip contact data first. Medium-high. |
| (d) Aggregate metrics | ALLOWED | C3 | Attribute the source and show the processing date. High. |
| (e) Charts | ALLOWED | C3, C4 | High. |
| (f) Transformed or reconstructed records | ALLOWED with conditions | C3, C4 | Describe every modification. "Current at all times" cannot be met by a frozen snapshot. Medium. |
| (g) Per-case inputs and predictions | ALLOWED with conditions | C3, C6 | Third-party copyright may apply to free text. Medium. |
| (h) Cached API responses | ALLOWED with conditions for registry responses | C1, C3 | No separate API terms were found. Medium. |
| (i) Prompts or quoted source text | ALLOWED for structured fields and short quotations; UNCLEAR for bulk sponsor free text | C3, C6 | Medium to low. |
| (j) Trained models or derived artifacts | UNCLEAR | C3, C4, C6 | Terms are silent on models. Medium-low. |
| (k) Redistributing original records | ALLOWED with conditions for registry records; UNCLEAR for uploaded protocol and consent documents | C2, C3, C6 | Uploaded documents may be third-party copyright. |
| (l) Redistributing modified records | ALLOWED with conditions | C3 | Modification log required. Medium. |
| (m) Inside an MIT repository | PROHIBITED as MIT-licensed content; possible only as a separate carve-out | C4, C6 | We may not assert rights over the data, and an international copyright is asserted. Medium. |
| (n) Attribution and NOTICE | Required in substance | C3, C4 | "should" attribute, date and describe changes. |
| (o) Share-alike | None, but the terms persist while data is retained | C7 | |
| (p) Privacy, data protection, contractual | UNCLEAR [P]; contractual limits as listed | C5, C1 | Records contain contact names and addresses. |

**Decision:** not used in v0.1.0. A possible future source, in a directory outside the MIT grant.

### 5.2 AACT (Aggregate Analysis of ClinicalTrials.gov, CTTI)

**Inspected:** https://aact.ctti-clinicaltrials.org/ (landing and sign-up pages only). Every other path redirected to a login form. Rights holder per footer: Clinical Trials Transformation Initiative. **The terms of use could not be read.**

| ID | Source URL | Quoted excerpt |
|---|---|---|
| A1 | https://aact.ctti-clinicaltrials.org/landing | "AACT is a public relational database with all protocol and results data for every study on ClinicalTrials.gov" … "Create an account to connect to the cloud database" |
| A2 | https://ctti-clinicaltrials.org/citation-policy/ | "We do ask that you acknowledge CTTI as the source whenever using or referencing our materials in any format… This applies to both original and derivative works." |

| Use | Classification | Explanation; confidence |
|---|---|---|
| (a) Commercial research use | UNCLEAR | A1 says "public" and "open", but the governing terms were not read. The source manifest records UNCLEAR. |
| (b) Internal processing | UNCLEAR | As (a). |
| (c) External AI APIs | UNCLEAR | No visible terms. Low. |
| (d) Aggregate metrics | UNCLEAR | Likely allowed with acknowledgement (A2, C3), but unverified. |
| (e) Charts | UNCLEAR | As (d). |
| (f) Transformed or reconstructed records | UNCLEAR | Low. |
| (g) Per-case inputs and predictions | UNCLEAR | Low. |
| (h) Cached API responses | UNCLEAR | Low. |
| (i) Prompts or quoted source text | UNCLEAR | C6 also applies to the underlying data. |
| (j) Trained models or derived artifacts | UNCLEAR | Silent. |
| (k) Redistributing original records | UNCLEAR | Footer asserts "© 2026 Clinical Trials Transformation Initiative". |
| (l) Redistributing modified records | UNCLEAR | As (k). |
| (m) Inside an MIT repository | PROHIBITED until terms are read | As (k); C4 applies to the underlying data. |
| (n) Attribution and NOTICE | Required in substance | A2 and C3. |
| (o) Share-alike | UNCLEAR | Not visible. |
| (p) Privacy, data protection, contractual | UNCLEAR | An account is needed for access; its terms are unseen. |

**Decision:** excluded until its terms are read and recorded.

## 6. Source 3: CDISC SDTM/ADaM Pilot 01

**Inspected:** https://github.com/cdisc-org/sdtm-adam-pilot-project, branch `master`, commit `667511d4b183871d74392ba691c935c38d431d39` (2024-12-20). **There is no licence file.** The governing text is the README "Terms of Use", present since the first commit (2019-05-23). Rights holder: CDISC; the data was provided by Eli Lilly and Company. Applicable artifacts: all SDTM and ADaM datasets and documents in that repository.

| ID | Source URL | Quoted excerpt |
|---|---|---|
| D1 | https://github.com/cdisc-org/sdtm-adam-pilot-project/blob/master/README.md | "By downloading / using this data, you agree to the Terms of use." |
| D2 | same, "Terms of Use" | "You shall not (and will not allow or assist any third party to), under any circumstances: (i) mislead, confuse, or cause misapprehension or confusion among users of the data as to the features, functionality, origin, capabilities, or other aspects of the data, (b) disassemble, reverse engineer, decompile, modify, or alter any part of the Data; (c) use the Data in any manner or for any purpose that violates any law or regulation, (d) use the Data in order to compete with CDISC, (e) sublicense or distribute the data for a fee, or (f) sublicense or distribute the data without an attribution back to CDISC." |
| D3 | Pilot project report in the same repository, section 2.2.1 | "Eli Lilly and Company (the Legacy Sponsor) provided the legacy data used in CDISCPILOT01 for the purposes of this pilot project. De-identification of the data and redaction of documents occurred prior to release to the pilot project team." |
| D5 | https://www.cdisc.org/terms-and-conditions (covers standards documents, not the pilot data) | "…license to reproduce, publish, display, and use this standard solely within Your Organization…" |

Analysis: [C]/[T] the terms forbid modifying or altering "any part of the Data" (D2(b)). [P] the data is de-identified real trial data, not synthetic (D3). [S] it has no eligibility (IE) or protocol deviation (DV) datasets, so it offers little for this benchmark.

| Use | Classification | Provisions | Explanation; confidence; open questions |
|---|---|---|---|
| (a) Commercial research use | ALLOWED | D1, D2(d) | Provided we do not compete with CDISC. Medium. |
| (b) Internal processing | ALLOWED for read-only analysis; UNCLEAR for altered copies | D2(b) | Medium to low. |
| (c) External AI APIs | UNCLEAR | D2, D3 | De-identified real data; terms silent on third-party processing. Low. |
| (d) Aggregate metrics | ALLOWED | D2(i), D2(f) | With attribution to CDISC. Medium-high. |
| (e) Charts | ALLOWED | as (d) | Medium. |
| (f) Transformed or reconstructed records | PROHIBITED | D2(b) | High. |
| (g) Per-case inputs and predictions | PROHIBITED where rows are re-serialised or altered; UNCLEAR for verbatim rows | D2(b), D2(f) | Medium-high. |
| (h) Cached API responses | UNCLEAR | D2(b) | Low. |
| (i) Prompts or quoted source text | UNCLEAR | D2(b) | Low. |
| (j) Trained models or derived artifacts | UNCLEAR | D2(b), D2(d) | Low. |
| (k) Redistributing original records | REQUIRES PERMISSION to be safe | D2(e), D2(f) | Unmodified, free, attributed redistribution is allowed only by inference. Ask CDISC. |
| (l) Redistributing modified records | PROHIBITED | D2(b) | High. |
| (m) Inside an MIT repository | PROHIBITED | D2(b), D2(e) | MIT grants modify and sell rights that CDISC withholds. High. |
| (n) Attribution and NOTICE | Required | D2(f), D2(i) | Attribution back to CDISC. |
| (o) Share-alike | No copyleft, but restrictions must flow down | D2 | Medium. |
| (p) Privacy, data protection, contractual | UNCLEAR [P]; binding browse-wrap terms [T] | D1, D3 | Medium. |

**Decision:** not used. Never to be copied into this repository.

## 7. Source 4: PHUSE clinical datasets and safetyData

**Inspected:** https://github.com/phuse-org/phuse-scripts, commit `398a6d33ced9359ffb58c46650a6d488811176b1` (2025-08-25); https://github.com/SafetyGraphics/safetyData, commit `afb971624c210db0b6103c2927ac4148fd97f88b`, release v1.0.0. Applicable artifacts: the CDISC-derived datasets under `data/adam/` and `data/sdtm/` in phuse-scripts, and everything in safetyData.

| ID | Source | Quoted excerpt |
|---|---|---|
| P1 | https://github.com/phuse-org/phuse-scripts/blob/master/LICENSE.md | MIT permission text. **It has no copyright line and names no holder.** |
| P3 | `data/adam/README.md` in phuse-scripts | "`cdisc` - Modified & augmented version of `cdiscpilot01`" … "`cdiscpilot01` - original CDISC Pilot data, published by CDISC in 2013" |
| S3 | `README.md` in safetyData | "PHUSE released the data under the permissive MIT license, so reuse with attribution is encouraged." |
| S4 | `data-raw/sdtm/README.md` in safetyData | Names the phuse-scripts `cdiscpilot01` folder as the original data and the PHUSE licence as the original licence. |

**Can the PHUSE MIT licence override CDISC's rights?** We found no evidence that it can. A licence conveys only rights the licensor holds, and nothing shows CDISC or the data provider authorised relicensing. The MIT text covers "software and associated documentation files". The licence file names no copyright holder. CDISC's current terms forbid modification, while PHUSE distributes modified versions. safetyData's MIT claim rests only on PHUSE's. We therefore treat PHUSE's own scripts as MIT, and every CDISC-derived dataset as governed by section 6.

| Use | Classification | Explanation; confidence |
|---|---|---|
| (a) Commercial research use | UNCLEAR | MIT and D1 both seem to permit, but the provenance is unresolved. The manifest records UNCLEAR. |
| (b) Internal processing | UNCLEAR | As (a); D2(b) caveat for altered copies. |
| (c) External AI APIs | UNCLEAR | Upstream D2 and D3 concerns. Low. |
| (d) Aggregate metrics | UNCLEAR | Likely allowed with attribution to PHUSE and CDISC; not relied on. |
| (e) Charts | UNCLEAR | As (d). |
| (f) Transformed or reconstructed records | REQUIRES PERMISSION from CDISC | MIT says yes; upstream D2(b) says no. Low. |
| (g) Per-case inputs and predictions | PROHIBITED until CDISC confirms | As (f). |
| (h) Cached API responses | UNCLEAR | As (f). |
| (i) Prompts or quoted source text | UNCLEAR | As (f). |
| (j) Trained models or derived artifacts | UNCLEAR | As section 6 (j). |
| (k) Redistributing original records | REQUIRES PERMISSION to be safe | Unmodified upstream files with both notices might satisfy both sets of terms. Medium-low. |
| (l) Redistributing modified records | REQUIRES PERMISSION | Conflict as (f). |
| (m) Inside an MIT repository | PROHIBITED until the upstream question is resolved | The MIT label is an unverified claim for this data. |
| (n) Attribution and NOTICE | Required | MIT notice (there is no copyright line to reproduce; cite repository and commit) and CDISC attribution. |
| (o) Share-alike | None in MIT; D2 flows down upstream | |
| (p) Privacy, data protection, contractual | UNCLEAR | Same de-identified real patient data as section 6. |

**Decision:** not used.

## 8. Source 5: Gilead gsm.datasim and related GSM data packages

**Inspected:** https://github.com/Gilead-Public/gsm.datasim, release v2.1.0 (2026-11-02), commit `29fc61c1ca83ceaf38c4c2ba54613872aa5a1d66`; development branch at `37df8fad37b5b4976b26e0ee42ca40601d1a5e08`. The package is not in the OpenRBQM GitHub organisation. Licence: Apache-2.0, "Copyright 2024 Gilead Sciences". No NOTICE file. Also https://github.com/Gilead-BioStats/clindata, v1.0.5, commit `f3b2f798fe53b2e79eb00c6bf2a2e115cee90d6d`, Apache-2.0, "Copyright 2023 Gilead Sciences".

| ID | Source | Quoted excerpt |
|---|---|---|
| G-1 | https://github.com/Gilead-Public/gsm.datasim/blob/dev/LICENSE.md | "Copyright 2024 Gilead Sciences / Licensed under the Apache License, Version 2.0" |
| G-2 | `DESCRIPTION` | "Generates synthetic clinical trial data for testing and development of clinical monitoring applications." |
| G-4 | Apache-2.0 section 4 | Redistribution requires a copy of the licence, marking of modified files and retention of notices. |
| K1 | clindata `README.md` | "A repository of various anonymized clinical trial data for use in open source testing and development." |
| K2 | clindata `DESCRIPTION` | "Synthetic Clinical Data for testing and development" |

### 8.1 gsm.datasim (code, bundled simulated data, and output you generate)

| Use | Classification | Explanation; confidence |
|---|---|---|
| (a) Commercial research use | ALLOWED | Apache-2.0. High. |
| (b) Internal processing | ALLOWED | High. |
| (c) External AI APIs | ALLOWED | Data is synthetic. High. |
| (d) Aggregate metrics | ALLOWED | High. |
| (e) Charts | ALLOWED | High. |
| (f) Transformed or reconstructed records | ALLOWED | Derivative works permitted. High. |
| (g) Per-case inputs and predictions | ALLOWED | High. |
| (h) Cached API responses | ALLOWED | High. |
| (i) Prompts or quoted source text | ALLOWED | Quoted package text stays Apache-2.0. High. |
| (j) Trained models or derived artifacts | ALLOWED | High. |
| (k) Redistributing original records | ALLOWED with Apache section 4 conditions | Include the licence and copyright notice. High. |
| (l) Redistributing modified records | ALLOWED with section 4 conditions | State that files were changed. High. |
| (m) Inside an MIT repository | ALLOWED | Copied Gilead files stay Apache-2.0; output you generate is yours. High. |
| (n) Attribution and NOTICE | Required for copied Apache material; none for self-generated output | Good practice: cite the generator version. |
| (o) Share-alike | None | Permissive licence. |
| (p) Privacy, data protection, contractual | ALLOWED | No personal data found in the source; placeholder names only. |

**Scientific fit [S].** The package is written in R. It generates sites, subjects, enrolment, eligibility rows, consent rows and deviations. But its eligibility results are a random "Yes" or "No" on randomly chosen criterion codes with no criterion text, and its consent rows are constants (type "WITHDRAWAL OF CONSENT", one date). It has no consent form versions, signature times, thresholds or protocol amendments. It therefore cannot produce cases with independently verifiable eligibility and consent labels.

**Decision:** evaluated as the generator and not adopted, for scientific reasons and because this project is Python only. The licence was not the obstacle. No gsm.datasim code or data is in this repository.

### 8.2 clindata

| Use | Classification | Explanation; confidence |
|---|---|---|
| (a) Commercial research use | ALLOWED | Apache-2.0. High. |
| (b) Internal processing | ALLOWED [C]; UNCLEAR [P] | Real-versus-synthetic status is unresolved (K1 against K2). |
| (c) External AI APIs | UNCLEAR | As (b). Low-medium. |
| (d) Aggregate metrics | ALLOWED | High. |
| (e) Charts | ALLOWED | High. |
| (f) Transformed or reconstructed records | ALLOWED [C]; UNCLEAR [P] | Medium. |
| (g) Per-case inputs and predictions | ALLOWED [C]; UNCLEAR [P] | Medium. |
| (h) Cached API responses | ALLOWED [C]; UNCLEAR [P] | Medium. |
| (i) Prompts or quoted source text | ALLOWED [C]; UNCLEAR [P] | Medium. |
| (j) Trained models or derived artifacts | ALLOWED [C]; UNCLEAR [P] | Medium. |
| (k) Redistributing original records | ALLOWED [C] with Apache section 4; UNCLEAR [P] | Medium. |
| (l) Redistributing modified records | ALLOWED [C]; UNCLEAR [P] | Mark changes. |
| (m) Inside an MIT repository | UNCLEAR | Licence allows (files stay Apache-2.0); privacy status does not. |
| (n) Attribution and NOTICE | Required | Apache-2.0 copy and copyright notice. |
| (o) Share-alike | None | |
| (p) Privacy, data protection, contractual | UNCLEAR | Ask the maintainers whether the records are synthetic. |

**Decision:** not used; do not redistribute.

## 9. Source 6: OpenRBQM / Good Statistical Monitoring

**Inspected:** the packages now live at https://github.com/Gilead-Public (the `OpenRBQM/gsm.*` addresses return "not found"): gsm.core v1.3.2 (commit `29f1f82bb25fddc11b71ddb9ec5203d4bcc6c6f1`), gsm.kri v1.8.0 (`6e32207b504b38b0d9c21675f82f0c7e30054cc9`), gsm.mapping v1.2.0, gsm.reporting v1.1.8. Licence: Apache-2.0, copyright holder Gilead Sciences. No NOTICE files. Not on CRAN.

| ID | Source | Quoted excerpt |
|---|---|---|
| P6-A | Apache-2.0 section 2, https://github.com/Gilead-Public/gsm.core/blob/29f1f82bb25fddc11b71ddb9ec5203d4bcc6c6f1/LICENSE.md | "each Contributor hereby grants to You a perpetual, worldwide, non-exclusive, no-charge, royalty-free, irrevocable copyright license to reproduce, prepare Derivative Works of, publicly display, publicly perform, sublicense, and distribute the Work" |
| P6-B | section 4, same file | "You must give any other recipients of the Work or Derivative Works a copy of this License; and … You must cause any modified files to carry prominent notices stating that You changed the files" |
| P6-C | section 6, same file | "This License does not grant permission to use the trade names, trademarks, service marks, or product names of the Licensor" |

For this software tool, "records" means bundled workflow files and example outputs. Separately: (1) invoking it as an optional external tool is ALLOWED; (2) copying its code is ALLOWED with Apache section 4 conditions; (3) publishing outputs it produces on our own synthetic data is ALLOWED.

| Use | Classification | Explanation; confidence |
|---|---|---|
| (a) Commercial research use | ALLOWED | High. |
| (b) Internal processing | ALLOWED | High. |
| (c) External AI APIs | ALLOWED | For gsm code, workflow files and simulated data. High. |
| (d) Aggregate metrics | ALLOWED | High. |
| (e) Charts | ALLOWED | Do not use Gilead or OpenRBQM marks as branding (P6-C). Medium. |
| (f) Transformed or reconstructed records | ALLOWED | Medium. |
| (g) Per-case inputs and predictions | ALLOWED | High. |
| (h) Cached API responses | ALLOWED | Not applicable to a local tool. |
| (i) Prompts or quoted source text | ALLOWED | High. |
| (j) Trained models or derived artifacts | ALLOWED | Models are not named in the licence. Medium. |
| (k) Redistributing original records | ALLOWED | With section 4 conditions. High. |
| (l) Redistributing modified records | ALLOWED | Mark changes. High. |
| (m) Inside an MIT repository | ALLOWED with conditions | Copied files stay Apache-2.0 with notices. High. |
| (n) Attribution and NOTICE | Required when code is copied | No upstream NOTICE file exists. |
| (o) Share-alike | None | |
| (p) Privacy, data protection, contractual | ALLOWED | No personal data in the code. The clindata sample data is treated separately in section 8.2. |

**Scientific fit [S].** The indicators are site-level statistical flags, not per-participant triage. Relevant ones: screen failure rate (kri0012), ineligibility (kri0014) and protocol deviation rates (kri0003, kri0004). There is no informed-consent indicator. The consent mapping needs a package (`gsm.endpoints`) that we could not find publicly.

**Decision:** optional external tool. Not bundled, not a dependency, not executed. If ever run, its results are reported separately from triage scores.

## 10. Source 7: CDISC CORE and its rule libraries

**Inspected:** https://github.com/cdisc-org/cdisc-rules-engine, release v1.0.0 (2026-11-03), commit `42028faf090c59bfdfba974779f64be2448bf5bb`, MIT, "Copyright (c) 2022 cdisc"; PyPI `cdisc-rules-engine` 1.0.0; rule repositories https://github.com/cdisc-org/cdisc-open-rules (commit `1881cb9a1f9a38b6cafc785eca5169b240981f66`, MIT) and https://github.com/cdisc-org/core-contributor (commit `94963e01df448f05bdbbc43a482661d4f30f7dac`, MIT, "Copyright (c) 2025 verisian"). The engine is currently split in two: SDTM rules run on a separate fork, https://github.com/verisianHQ/cdisc-rules-engine, which accepts XPT and SAS7BDAT files only.

| ID | Source | Quoted excerpt |
|---|---|---|
| P7-A | https://github.com/cdisc-org/cdisc-rules-engine/blob/42028faf090c59bfdfba974779f64be2448bf5bb/LICENSE | MIT permission text. |
| P7-C | https://www.cdisc.org/core/cdisc-open-rules | "Provided as open source with the permissive MIT license" |
| P7-D | https://www.cdisc.org/terms-and-conditions (standards documents) | "User agrees to limit access to this download for use within your organization only." |
| P7-F | CDISC Communications Policy 2025, section 2 (cdisc.org) | "External use of the CDISC Brand including the CDISC logo, CDISC elements, and the word "CDISC" or images, must be approved by the CDISC Communications Team." |
| P7-G | Engine documentation at the inspected commit | "An API key is required for controlled terminology and library metadata. Rules are accessible without a key." |

The engine and the rule repositories are MIT, not CC-BY. **The CDISC Library licence text could not be obtained.** For this tool: (1) invoking it is ALLOWED; (2) copying engine code is ALLOWED with the MIT notice; (3) publishing its output on our own synthetic data is ALLOWED when the report text comes only from the MIT rule files.

| Use | Classification | Explanation; confidence |
|---|---|---|
| (a) Commercial research use | ALLOWED for the engine and rule repositories; UNCLEAR for the CDISC Library API | High / low. |
| (b) Internal processing | ALLOWED | High. |
| (c) External AI APIs | ALLOWED for our data, engine output and MIT rule files; UNCLEAR for cache content; REQUIRES PERMISSION for standards documents | Medium. |
| (d) Aggregate metrics | ALLOWED | High. |
| (e) Charts | ALLOWED; REQUIRES PERMISSION if a CDISC or CORE logo is shown | P7-F. |
| (f) Transformed or reconstructed records | ALLOWED for MIT rule files and test data; UNCLEAR for cache or Library content | Medium. |
| (g) Per-case inputs and predictions | ALLOWED | Assumes report text comes only from MIT rule files. Medium. |
| (h) Cached API responses | UNCLEAR; treated as not permitted | Read the Library terms or ask CDISC. Low. |
| (i) Prompts or quoted source text | ALLOWED for MIT rule text; REQUIRES PERMISSION for standards document text | P7-D. Medium. |
| (j) Trained models or derived artifacts | ALLOWED from MIT code and our data; UNCLEAR from Library content | Low-medium. |
| (k) Redistributing original records | ALLOWED for MIT rule files with notice; UNCLEAR for cache content | Rule test-data files were not opened. Medium. |
| (l) Redistributing modified records | ALLOWED for the MIT repositories; UNCLEAR for cache content | Medium. |
| (m) Inside an MIT repository | ALLOWED for engine code and rule files with their notices; UNCLEAR for cache; REQUIRES PERMISSION for logos | The manifest records PROHIBITED for this project: nothing from CORE is to be bundled. |
| (n) Attribution and NOTICE | Required when copied | Keep the CDISC and Verisian copyright lines. |
| (o) Share-alike | None | |
| (p) Privacy, data protection, contractual | UNCLEAR (Library terms); REQUIRES PERMISSION (CDISC name or logo in branding) | The engine runs locally, so our data stays with us. |

**Decision:** optional external tool. Not bundled, not a dependency, not executed. Cached Library content and API responses must never be published. Its two engines pin conflicting dependencies, so it would need its own environment.

## 11. Sources 8, 9 and 10

### 11.1 Source 8: pharmaverse sdtmchecks

**Inspected:** https://github.com/pharmaverse/sdtmchecks, commit `fb35f8b33adc3548c2b1531fab1f65a7e8360492`; CRAN 1.0.0 (2024-07-12). Apache-2.0, "Copyright 2024 F. Hoffmann-La Roche AG". No NOTICE file. Provisions: the same Apache-2.0 text as P6-A to P6-C, at https://github.com/pharmaverse/sdtmchecks/blob/fb35f8b33adc3548c2b1531fab1f65a7e8360492/LICENSE.md. Bundled data is a metadata table of checks only; no patient data.

| Use | Classification | Use | Classification |
|---|---|---|---|
| (a) Commercial research use | ALLOWED | (i) Prompts or quoted source text | ALLOWED |
| (b) Internal processing | ALLOWED | (j) Trained models or derived artifacts | ALLOWED |
| (c) External AI APIs | ALLOWED | (k) Redistributing original records | ALLOWED |
| (d) Aggregate metrics | ALLOWED | (l) Redistributing modified records | ALLOWED |
| (e) Charts | ALLOWED | (m) Inside an MIT repository | ALLOWED with conditions (copied files stay Apache-2.0) |
| (f) Transformed or reconstructed records | ALLOWED | (n) Attribution and NOTICE | Required when code is copied |
| (g) Per-case inputs and predictions | ALLOWED | (o) Share-alike | None |
| (h) Cached API responses | ALLOWED (not applicable) | (p) Privacy, data protection, contractual | ALLOWED |

Confidence is high throughout, medium for (j). Invoking it, copying it with notices, and publishing its outputs on our synthetic data are all ALLOWED.

**Scientific fit [S].** There is no inclusion or exclusion criteria check (no `check_ie_*` function). The only consent-related check is `check_ts_sstdtc_ds_consent`, a study-level date check. `check_ds_duplicate_randomization` and the `check_dm_*` checks are loosely relevant.

**Decision:** optional external tool. Not bundled, not a dependency, not executed.

### 11.2 Source 9: IMPALA Clinical Trial Anomaly Spotter (CTAS)

**Inspected:** https://github.com/IMPALA-Consortium/ctas, commit `94c9f061225e30a5ab0145a25991b068bd4e649f` (2026-10-19), version 0.4.0. MIT, "Copyright (c) 2024 Bayer" (https://github.com/IMPALA-Consortium/ctas/blob/94c9f061225e30a5ab0145a25991b068bd4e649f/LICENSE.md). Bundled data is simulated. It imports lme4, merTools and dbscan, which CRAN lists under GPL licences. Two PHUSE conference PDFs in the repository carry no licence statement.

| Use | Classification | Use | Classification |
|---|---|---|---|
| (a) Commercial research use | ALLOWED | (i) Prompts or quoted source text | ALLOWED for README and code; UNCLEAR for the two PDFs |
| (b) Internal processing | ALLOWED | (j) Trained models or derived artifacts | ALLOWED |
| (c) External AI APIs | ALLOWED | (k) Redistributing original records | ALLOWED with MIT notice; UNCLEAR for the PDFs. Manifest records UNCLEAR. |
| (d) Aggregate metrics | ALLOWED | (l) Redistributing modified records | ALLOWED |
| (e) Charts | ALLOWED | (m) Inside an MIT repository | PROHIBITED for this project: bundling it with its GPL dependencies would be GPL-governed distribution |
| (f) Transformed or reconstructed records | ALLOWED | (n) Attribution and NOTICE | Keep the copyright and permission notice in copies |
| (g) Per-case inputs and predictions | ALLOWED | (o) Share-alike | None for CTAS itself; GPL for its dependencies |
| (h) Cached API responses | ALLOWED (not applicable) | (p) Privacy, data protection, contractual | ALLOWED |

**Scientific fit [S].** It needs longitudinal numeric series per site and parameter. Our cases are single participant records.

**Decision:** possible future experiment only. Never bundle.

### 11.3 Source 10: Project Data Sphere

**Inspected:** https://data.projectdatasphere.org/ and the user agreement at https://data.projectdatasphere.org/documents/resources_data_user_agreement.pdf, headed "Cancer Research Platform Agreement (v. May 13, 2020)". Access needs registration and approval. Rights holders: Project Data Sphere and the data providers.

| ID | Quoted excerpt (user agreement) |
|---|---|
| P10-B | "a non-exclusive, revocable, limited, non-transferable, non-sublicensable license to use the Platform only for purposes of accessing and using Data for one or more systematic investigations … in the field of cancer research" |
| P10-D | "You may not use the Platform or any component thereof, either alone or in concert with any other information, to identify or contact individuals" |
| P10-E | "you are prohibited from disclosing any portion of the Data available through the Platform to, or otherwise sharing any portion of the Data with, any third party." |
| P10-G | "Only you may access the Platform. You shall not allow any other person to have access to the Platform or your password." |
| P10-J | "You are encouraged to publish any results of your research in any peer-reviewed publication … provided that your publication or presentation does not disclose any Data … other than Data … that are reasonably necessary to publish or report your research results." |

| Use | Classification | Explanation; confidence |
|---|---|---|
| (a) Commercial research use | REQUIRES PERMISSION | Purpose is limited to cancer research; ask whether ours qualifies. Medium. |
| (b) Internal processing | REQUIRES PERMISSION | Access is per approved individual (P10-G). High. |
| (c) External AI APIs | PROHIBITED | P10-E. High. |
| (d) Aggregate metrics | ALLOWED with the mandatory acknowledgement | P10-J. Medium-high. |
| (e) Charts | ALLOWED for aggregate charts; PROHIBITED for per-subject plots beyond what is reasonably necessary | Medium. |
| (f) Transformed or reconstructed records | PROHIBITED | High. |
| (g) Per-case inputs and predictions | PROHIBITED | High. |
| (h) Cached API responses | PROHIBITED | High. |
| (i) Prompts or quoted source text | PROHIBITED for anything containing Data; UNCLEAR for data dictionary text | Medium. |
| (j) Trained models or derived artifacts | UNCLEAR | Low. |
| (k) Redistributing original records | PROHIBITED | High. |
| (l) Redistributing modified records | PROHIBITED | High. |
| (m) Inside an MIT repository | PROHIBITED | High. |
| (n) Attribution and NOTICE | Mandatory acknowledgement in every publication of results | High. |
| (o) Share-alike | None; intellectual property covenants apply | |
| (p) Privacy, data protection, contractual | PROHIBITED to re-identify or contact individuals; security, ethics review and one-year term duties apply | High. |

**Decision:** possible future source only. Not used.

## 12. Hosted model APIs and gateways

These are provider terms [T], not data licences. Sources and quotes are in [Appendix C](research/appendix-c-model-providers.md). The quote-fidelity caveat in section 1 applies to every row.

Our use: a commercial EU company publishing benchmark scores, per-case model outputs, latency and cost; synthetic data plus de-named descriptions of public FDA text; no real patient data; no decisions about people.

| Provider | Terms read | (a) Commercial use | (b) Publish outputs | (c) Publish benchmarks | (d) Clinical-compliance research benchmark |
|---|---|---|---|---|---|
| TypeSafe (Jev) | https://typesafe.ai/legal/mca | ALLOWED | ALLOWED. "TypeSafe hereby assigns to Customer all of its right, title, and interest, if any, in the Output." | UNCLEAR. No benchmark clause. Confidentiality covers "other non-public information with respect to the Services"; "Nothing in this Agreement grants either Party the right to use the name, brand, or logo of the other Party." | ALLOWED. No medical restriction found. |
| OpenAI (Decisions, Responses) | https://openai.com/policies/services-agreement/ and https://openai.com/policies/usage-policies/ | ALLOWED | ALLOWED. Customer "owns all Output". | ALLOWED. "You may use OpenAI models for research, software development, model evaluation and benchmarking". Limits: no public statement about the relationship or use of name or logo without permission; outputs must not train competing models. | ALLOWED with care. The policy bars "automation of high-stakes actions in sensitive areas without human review". |
| Cloudflare (Clef, Clef-flash) | https://www.cloudflare.com/terms/ | ALLOWED | ALLOWED. "you retain all applicable intellectual property or other proprietary rights in Inputs and Outputs." | ALLOWED with a condition. "You are permitted to perform benchmark tests of our Services." Published results must come with "all information necessary to replicate such benchmark tests." | ALLOWED. No protected health information. |
| Perplexity (Decider) | https://www.perplexity.ai/hub/legal/perplexity-api-terms-of-service and https://www.perplexity.ai/hub/legal/aup | ALLOWED, narrow licence | REQUIRES PERMISSION. Customer "owns all Output", but display is limited to "solely within the Customer Applications". | REQUIRES PERMISSION. No clause; the usage policy bars products "competitive with, similar to, or that would otherwise be a substitute". | ALLOWED for research. |
| Bespoke Labs (Nimble API) | No public terms page found | UNCLEAR | UNCLEAR | UNCLEAR | UNCLEAR |
| Liquid AI (D1 Ultra API) | https://www.liquid.ai/terms-conditions | ALLOWED. "for your internal business purposes" | ALLOWED. "own the outputs" | UNCLEAR. Main terms are silent. | ALLOWED for research. |
| Morph (reflex) | https://morphllm.com/privacy/tos | ALLOWED | ALLOWED. "You own the output generated from your inputs." | UNCLEAR. Subscription terms restrict "benchmark farming" and evaluating competing models; reach for metered API use is not clear. | ALLOWED. |
| Microsoft (Decision 1, Preview) | https://www.microsoft.com/licensing/terms/product/ForOnlineServices/all | ALLOWED | ALLOWED. "Output Content is Customer Data." | ALLOWED with conditions. Disclosing benchmarks requires giving, on request, "all information necessary to replicate such Benchmark"; using the service waives our own anti-benchmark terms if we offer a competing product. | ALLOWED as decision support with human review. |
| Convai Laya (open weights) | https://huggingface.co/convaiinnovations/laya | ALLOWED (Apache-2.0) | ALLOWED | ALLOWED | ALLOWED |
| Anthropic (Claude) | https://www.anthropic.com/legal/commercial-terms | ALLOWED | ALLOWED. Customer "owns its Outputs". | ALLOWED. No benchmarking clause; may not "access the Services to build a competing product or service". | ALLOWED for research. |
| Opper (gateway) | https://opper.ai/terms-of-service | ALLOWED | UNCLEAR. Output ownership is not addressed; upstream terms are assumed to apply. | UNCLEAR for this project. No clause found; we would have no direct contract with the upstream provider. | Not addressed. |
| Runware (gateway) | https://runware.ai/terms | ALLOWED | ALLOWED. "you own your Outputs." | UNCLEAR for this project. No clause; "Where there is a conflict between these Terms and a Model Licence, the Model Licence governs", and the Jev model licence was not shown. | Not addressed. |

**Data handling [P]/[T].**

- TypeSafe, OpenAI, Cloudflare, Perplexity, Morph, Microsoft and Anthropic state that customer inputs are not used to train models by default. Retention differs; see Appendix C.
- **Liquid AI:** "Liquid may save prompts and outputs and use them to improve our models and services" on standard endpoints. Sending the frozen test set there would expose it to training. The model stays disabled until a zero-retention endpoint is confirmed.
- No provider's terms block a synthetic, non-patient research benchmark. The restrictions target automated decisions about people without human review.

**Open-weight licences [C].**

- Bespoke Labs `Nimble-v4-max` weights: **CC BY-NC 4.0**. A commercial company must not self-host them. Use the paid API only, after reading its terms.
- Liquid AI open `d1` weights: LFM Open License v1.0, "Free if your annual revenue is under $10 million USD". Above that a commercial licence is needed. D1 Ultra itself has no downloadable weights.
- Cloudflare Clef and Convai Laya weights: Apache-2.0.

**Version drift since the Fraud Decision Lab check of 2026-11-06.** No change to the four existing endpoints or prices. OpenAI Decisions is now generally available and can return a `refusal` answer. Perplexity Decider 1.2 and Nimble v4 Max are superseded by Decider 1.3 and Nimble v4.1 Max; the `-latest` aliases moved, so explicit identifiers are pinned.

## 13. What was decided for this project

These decisions match `data/source-manifest.json` and `configs/models.yaml`.

**Data sources.**

| Source id | In repository | External API processing | Publish aggregates | Publish per-case records | Redistribute | In MIT repository |
|---|---|---|---|---|---|---|
| triallab-synthetic-v1 | Yes | ALLOWED | ALLOWED | ALLOWED | ALLOWED | ALLOWED |
| fraud-decision-lab (code) | Yes | ALLOWED | ALLOWED | ALLOWED | ALLOWED | ALLOWED |
| fda-warning-letters | No | UNCLEAR | ALLOWED | UNCLEAR | UNCLEAR | UNCLEAR |
| clinicaltrials-gov | No | ALLOWED | ALLOWED | UNCLEAR | UNCLEAR | PROHIBITED |
| aact | No | UNCLEAR | UNCLEAR | UNCLEAR | UNCLEAR | PROHIBITED |
| cdisc-pilot-01 | No | UNCLEAR | ALLOWED | PROHIBITED | REQUIRES PERMISSION | PROHIBITED |
| phuse-scripts | No | UNCLEAR | UNCLEAR | PROHIBITED | REQUIRES PERMISSION | PROHIBITED |
| gsm-datasim | No | ALLOWED | ALLOWED | ALLOWED | ALLOWED | ALLOWED |
| openrbqm-gsm | No | ALLOWED | ALLOWED | ALLOWED | ALLOWED | ALLOWED |
| cdisc-core | No | ALLOWED | ALLOWED | UNCLEAR | UNCLEAR | PROHIBITED |
| sdtmchecks | No | ALLOWED | ALLOWED | ALLOWED | ALLOWED | ALLOWED |
| ctas | No | ALLOWED | ALLOWED | ALLOWED | UNCLEAR | PROHIBITED |
| project-data-sphere | No | PROHIBITED | ALLOWED | PROHIBITED | PROHIBITED | PROHIBITED |

- The synthetic dataset config sets `external_processing_allowed: true` and `publication_allowed: true`.
- The regulatory-finding dataset config sets both to `false`. The runner records every case as `permission_blocked` for remote models, whatever flags are given.
- MIT applies to original software and original synthetic data only. Third-party material keeps its own terms.

**Models.** Running a model and publishing its results are separate decisions. `publication.approved` is `false` for every model in the registry today, so no model result can be exported.

| Model id | Enabled | Benchmark publication (our reading) | Reason when disabled or blocked |
|---|---|---|---|
| jev | Yes | UNCLEAR | Ask TypeSafe in writing. |
| openai_decisions, llm_openai | Yes | ALLOWED | Owner approval still needed. |
| clef, clef_flash | Yes | ALLOWED | Publish full replication information. |
| pplx_decider, pplx_decider_flash | Yes | REQUIRES PERMISSION | Written permission before publishing. |
| nimble | **No** | UNCLEAR | API terms are not public; read and archive them at sign-up before any call. |
| liquid_d1_ultra | **No** | UNCLEAR | Standard endpoints may train on prompts. |
| morph_reflex | Yes | UNCLEAR | Ask Morph; use metered API access only. |
| microsoft_decision | **No** | ALLOWED | Response fields could not be validated from the documentation. |
| convai_laya | **No** | ALLOWED | No vendor-hosted API; context too small for one case. |
| llm_anthropic | Yes | ALLOWED | Owner approval still needed. |
| jev_via_opper, jev_via_runware | Yes | UNCLEAR | Upstream TypeSafe terms assumed to apply. |

No paid API call has been made by this project.

## 14. Limits of this audit

- Licence terms [C], privacy [P], provider terms [T] and scientific limits [S] are different questions. A source can pass one and fail another. FDA text is the clearest case: free on copyright, open on privacy.
- A passing publication preflight is necessary for release, not sufficient. It checks that decisions are recorded; it does not check that they are right.
- Terms change. Every row is tied to the verification date.

## 15. Could not verify

1. AACT terms of use (behind a login; no account was created).
2. The official EUR-Lex text of the GDPR articles quoted (an unofficial mirror was read).
3. ClinicalTrials.gov API-specific terms; and the Terms and Conditions were extracted from a script bundle, not seen rendered.
4. FDA Data Dashboard API terms; FDA clinical investigator inspection list and bioresearch monitoring programme pages.
5. The terms under which PHUSE first obtained the CDISC pilot data, and whether CDISC ever authorised MIT relicensing.
6. Whether clindata records are synthetic or anonymised real data.
7. Contents and record counts of the CDISC pilot datasets (files were listed, not opened).
8. Runtime behaviour of gsm.datasim, gsm, CDISC CORE, sdtmchecks and CTAS (nothing was installed or run).
9. The CDISC Library licence and API terms; a standalone CDISC trademark policy; whether MIT covers the CORE cache files.
10. The `gsm.endpoints` package needed by the gsm consent mapping.
11. Whether the Project Data Sphere click-through agreement matches the posted document; its supplemental terms; what its datasets contain.
12. Bespoke Labs hosted API terms.
13. Microsoft Decision 1 literal response field names; batch endpoints for any decision model; most numeric rate limits.
14. The Jev model licence shown by Runware; whether Runware enables long context.
15. Licences of transitive dependencies of the optional R tools.
16. The exact wording of every provider clause quoted in section 12 (see the quote-fidelity caveat).

## 16. Items needing specialist legal review

1. **FDA letters and GDPR.** Is there a lawful basis to publish material that resolves to named investigators (names, letter numbers or letter URLs)? Does Art. 10 apply to regulatory findings? What Art. 14 notice position is needed? What does Polish law implementing Arts. 85 and 89 add?
2. **De-named descriptions.** Are our de-named finding descriptions, published without any letter reference, outside personal data? If so, may they be sent to external model APIs and published per case?
3. **Foreign copyright in U.S. Government works** used by an EU publisher.
4. **TypeSafe.** Is measured performance "non-public information with respect to the Services"? May Jev be named in public results?
5. **Perplexity.** Written permission to publish per-case outputs and comparative results outside a "Customer Application".
6. **Morph.** Does the "benchmark farming" restriction reach metered API benchmarking?
7. **Liquid AI.** Benchmark publication, and a zero-retention endpoint for D1 Ultra.
8. **Bespoke Labs.** Read the API terms at sign-up before any call.
9. **Microsoft.** Accept the reciprocal benchmarking waiver knowingly; Preview terms.
10. **OpenAI.** Does naming OpenAI in a results table fall under the no-publicity clause? Published per-case outputs could be used by others to train models; consider a notice.
11. **Gateways.** With Opper or Runware we have no direct contract with the upstream provider. Which terms govern publication?
12. **"Competing product" clauses** (TypeSafe, Perplexity, Anthropic, Microsoft, OpenAI). Do they apply if Smart Mobile House ever builds or sells a decision model?
13. **CDISC.** If the pilot data is ever wanted: written permission for any modified or redistributed form. Approval for any use of the CDISC name beyond plain description.
14. **ClinicalTrials.gov.** How to meet "current at all times" with a frozen snapshot, if it is ever used.

Until these are answered, the affected sources and model results stay out of the public release.
