> Appendix A: research notes on data sources 1 to 5 (FDA, ClinicalTrials.gov and AACT, CDISC Pilot 01, PHUSE and safetyData, gsm.datasim and clindata). Unedited working notes, kept as supporting evidence for docs/DATA-LICENSING-AUDIT.md.
> Verification date: 2026-11-16. Quotes were collected by automated fetching; some passed through a summarising fetch tool or a reader proxy and may be clipped. Re-read every clause at its source before sign-off.
> Not legal advice. Local paths, individual warning-letter URLs, personal names of letter recipients and FDA staff, and email addresses were removed.

# Licensing / data-rights research — batch A

- Verification date for every determination below: **2026-11-16** (all sources fetched on this date unless stated).
- Publisher profile assumed: Polish/EU commercial company; MIT-licensed public benchmark repository + public research report.
- Vocabulary: ALLOWED / PROHIBITED / UNCLEAR / REQUIRES PERMISSION.
- Restriction types are tagged: **[C]** copyright/licence, **[P]** privacy/data protection, **[T]** contractual/terms of use, **[S]** scientific limitation.
- Method: primary sources fetched with `gh api` (authenticated) and `curl`; quotes are verbatim from the fetched text. Raw captures were kept in a private working folder and are not part of this repository.
- This is research, not legal advice. The GDPR analysis in particular is my assessment of fetched statutory text, not a regulator's or counsel's position; items marked "counsel" need a lawyer's sign-off.
- Where a cell has two classifications (e.g. "ALLOWED [C] / UNCLEAR [P]"), the more restrictive one governs unless the stated condition is met.

## 0. Summary of things I COULD NOT VERIFY

| # | Item | Why |
|---|---|---|
| CNV-1 | AACT terms of use / licence | aact.ctti-clinicaltrials.org has been redesigned; only `/landing` and `/sign_up` are public, every other path tried (`/terms`, `/terms_and_conditions`, `/download`, `/data_dictionary`, `/points_to_consider`, `/faq`, `/learn_more`, `/credits`, `/privacy`) returned 404 or redirected to the login form. I did not create an account (would require submitting personal data). `gh api repos/ctti-clinicaltrials/aact` returned 404. The Wayback Machine was "Temporarily Offline". |
| CNV-2 | Official EUR-Lex text of GDPR | eur-lex.europa.eu returned HTTP 202 (bot wall) to both curl and WebFetch. Articles 6(1)(f), 10 and 14(5)(b) are quoted from the unofficial mirror gdpr-info.eu; re-check against EUR-Lex before citing in the audit. |
| CNV-3 | ClinicalTrials.gov API-specific terms (rate limits, key requirements) | The site is a JavaScript app; I extracted the Terms and Conditions text from its script bundle but found no separate API terms text. The T&C themselves say they apply "independent of format and method of acquisition". |
| CNV-4 | FDA Data Dashboard API terms | The API page says credentials are required via "OII Unified Logon"; any terms shown during that registration were not visible to me. |
| CNV-5 | FDA CLIIL (Clinical Investigator Inspection List) and BIMO programme pages | Both URLs I tried returned 404; not investigated further. Form 483 specifics verified only via the "Inspection Observations" page, not the Electronic Reading Room. |
| CNV-6 | Terms under which PHUSE originally obtained the CDISC pilot data (2013-2016) and whether CDISC ever authorised MIT relicensing | No document in either repo records such a grant. The cdisc.org pilot page (`/sdtmadam-pilot-project`) returned 403. |
| CNV-7 | Whether `clindata` records are fully synthetic or anonymised real trial data | The repo's README and DESCRIPTION contradict each other (see 5b). I did not open the data files. |
| CNV-8 | Record counts and exact contents of the CDISC datasets (e.g. number of subjects, screen failures) | I listed files but did not open the .xpt data. |
| CNV-9 | Whether gsm.datasim's IE label functions behave as intended | Read from source only; code was not executed (see 5a [S]). |

---

## 1. FDA inspection findings and warning letters

**Inspected:** fda.gov pages listed below ("Content current as of" dates quoted per page). **Copyright holder:** none for US Government works (public domain in the US). **SPDX:** none applicable (not a licence; closest descriptive tag is "public domain / US Government work").

### 1.1 Provisions

| ID | Source URL | Verbatim excerpt |
|---|---|---|
| F1 | https://www.fda.gov/about-fda/about-website/website-policies (section "Linking to or Copying Information on the FDA Website"; "Content current as of: 01/19/2024") | "Unless otherwise noted, the contents of the FDA website (www.fda.gov) — both text and graphics — are not copyrighted. They are in the public domain and may be republished, reprinted and otherwise used freely by anyone without the need to obtain permission from FDA. Credit to the U.S. Food and Drug Administration as the source is appreciated but not required." |
| F2 | same page | "FDA's preference is that people link to the material on the FDA site (rather than copying it to their personal websites) because the agency continuously updates the information on the website as better information becomes available." … "If a person, nonetheless, decides to copy content or images, FDA strongly recommends that the copied item lists the date that the material was copied and provides a link back to its source on the FDA website." |
| F3 | https://www.law.cornell.edu/uscode/text/17/105 (17 U.S.C. §105(a)) | "Copyright protection under this title is not available for any work of the United States Government, but the United States Government is not precluded from receiving and holding copyrights transferred to it by assignment, bequest, or otherwise." |
| F4 | https://www.fda.gov/about-fda/website-policies/fda-name-and-logo-policy ("Content current as of: 08/31/2023") | "The “FDA” name, an initialism for the U.S. Food and Drug Administration, and corresponding logos are trademarks and service marks (hereinafter, “FDA Marks”) specifically for the official use of the U.S. Food and Drug Administration and not for use by the private sector or on private sector materials, unless specifically authorized, in writing, by the FDA." … "The FDA Mark must not be used: … By any third party, unless specifically authorized by the FDA in writing … In association or in connection with any third-party product or service. … To indicate or imply endorsement by the FDA." … "Unauthorized use of the FDA Marks may violate federal law and subject those responsible to civil and/or criminal liability." |
| F5 | same page (last paragraph) | "…the FDA must only be identified by either its full legal name (“Food & Drug Administration” or “Food and Drug Administration” with or without the “U.S.”) or its FDA initialism and only in ordinary text with the same size and font lettering as all other nonbranded wording in the communication." (Stated for those who "conduct business with or before the FDA"; a safe model for plain-text references.) |
| F6 | https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/compliance-actions-and-activities/warning-letters | "Matters described in FDA warning letters may have been subject to subsequent interaction between FDA and the letter recipient that may have changed the regulatory status of issues discussed in the letter." The page's table has filters "Letters with Response or Closeout", "Response Letters", "Closeout Letters". |
| F7 | https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/warning-letters/about-warning-and-close-out-letters ("Content current as of: 03/20/2024") | "FDA may issue a Warning Letter close-out letter ("close-out letter") once the Agency has completed an evaluation of corrective actions undertaken by a firm in response to a Warning Letter." … "This procedure applies to Warning Letters issued on or after September 1, 2009." … "If the Warning Letter contains violations that by their nature are not correctable, then no close-out letter will issue." Also: "Some of the letters have been redacted or edited to remove confidential information." (said of drug marketing letters). |
| F8 | Two sample warning letters (URLs kept in the private register) | Observed directly: recipient is a named individual ("Dear Dr. [named investigator]:"); the FDA field investigator is named ("Investigator [named FDA investigator], representing FDA"); protocol, drug and sponsor are redacted "(b)(4)" (8 and 7 occurrences); subject identifiers and some dates are redacted "(b)(6)" (7 and 4 occurrences), e.g. "Subject (b)(6) was enrolled in Protocol (b)(4) without confirming…". |
| F9 | https://www.foia.gov/faq.html | "Exemption 4: Trade secrets or commercial or financial information that is confidential or privileged." "Exemption 6: Information that, if disclosed, would invade another individual’s personal privacy." |
| F10 | https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/inspection-classification-database | "This database does not represent a comprehensive listing of all conducted inspections and should not be used as a source to compile official data." … "Some inspection data may not be posted until a final enforcement action is taken. Descriptions of posted inspection citations may not necessarily represent citations on the final classification letters." |
| F11 | https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/inspection-references/inspection-observations | "These spreadsheets are not a comprehensive listing of all inspectional observations…" … "Not all Form FDA 483s are generated by these tools as some 483s are manually prepared." … observations are listed "when, in an investigator’s judgment, the observed conditions or practices indicate that an FDA-regulated product may be in violation of FDA’s requirements." |
| F12 | https://datadashboard.fda.gov/oii/api/index.htm | "To obtain the credentials necessary to use the API, please submit authorization key requests using the online OII Unified Logon application." |
| G1 | GDPR Art. 6(1)(f) — https://gdpr-info.eu/art-6-gdpr/ (unofficial mirror, see CNV-2) | "processing is necessary for the purposes of the legitimate interests pursued by the controller or by a third party, except where such interests are overridden by the interests or fundamental rights and freedoms of the data subject which require protection of personal data…" |
| G2 | GDPR Art. 10 — https://gdpr-info.eu/art-10-gdpr/ | "Processing of personal data relating to criminal convictions and offences or related security measures based on Article 6 (1) shall be carried out only under the control of official authority or when the processing is authorised by Union or Member State law providing for appropriate safeguards for the rights and freedoms of data subjects." |
| G3 | GDPR Art. 14(5)(b) — https://gdpr-info.eu/art-14-gdpr/ | "the provision of such information proves impossible or would involve a disproportionate effort, in particular for processing for archiving purposes in the public interest, scientific or historical research purposes or statistical purposes, subject to the conditions and safeguards referred to in Article 89 (1)… In such cases the controller shall take appropriate measures to protect the data subject’s rights and freedoms and legitimate interests, including making the information publicly available;" |

### 1.2 Analysis notes

- **[C]** FDA-authored text is not copyrighted in the US (F1, F3). Two limits: (i) "Unless otherwise noted" (F1) — FDA's policy page contains no further wording on third-party content, so anything inside a letter or 483 that FDA did not author (quoted firm correspondence, embedded labels/images, attachments) is not covered by the public-domain statement; (ii) §105 is US law; FDA's own statement "used freely by anyone" is not territorially limited, but FDA does not expressly waive foreign copyright (contrast ClinicalTrials.gov, which expressly asserts it, see 2a). Confidence for EU publication is therefore medium, not high.
- **[P]** Warning letters to clinical investigators name a living individual and allege regulatory violations by that person; they also name FDA employees. For an EU controller this is personal data (GDPR applies to the publisher by establishment). Redactions "(b)(6)" protect trial subjects, not the investigator. Whether FDA regulatory findings fall under Art. 10 ("offences") is not settled by the text I fetched — UNCLEAR, counsel. A lawful basis (likely Art. 6(1)(f), G1) plus an Art. 14 position (G3) would be needed to republish names; removing names/addresses/licence numbers and FDA staff names before publication avoids most of this. Polish law implementing Art. 85/89 was not researched.
- **[P] US side:** FDA itself publishes the names; no US statute I fetched restricts republication of public federal records. Residual risk is defamation/false-light if a letter is presented without its later status (F6, F7) — hence keep issue date, retrieval date, link, and response/close-out status.
- **[S]** Warning letters are allegations at a point in time and may have been superseded (F6); close-outs exist only for letters from 2009-09-01 and not for non-correctable violations (F7); inspection databases and 483 spreadsheets are explicitly non-comprehensive (F10, F11); (b)(4) redaction removes protocol/sponsor/drug, so letters cannot be reliably linked to ClinicalTrials.gov records.

### 1.3 Matrix — FDA

Applicable artifacts for all rows: warning-letter HTML pages, close-out/response letters, Form 483 PDFs/spreadsheets, Inspection Classification Database / Data Dashboard exports.

| Use | Classification | Provisions | Explanation | Confidence / unresolved |
|---|---|---|---|---|
| (a) Commercial research use | ALLOWED | F1, F3 | "used freely by anyone without the need to obtain permission"; no non-commercial limit. | High |
| (b) Internal processing | ALLOWED [C] / ALLOWED [P] with a documented lawful basis | F1, G1 | No copyright bar. Internal processing of named letters is still GDPR processing; record a legitimate-interest assessment. | High [C]; medium [P] |
| (c) Processing through external AI APIs | ALLOWED [C] / UNCLEAR [P] if names retained | F1, G1 | No copyright or terms bar. Sending named individuals' data to a processor needs a DPA and, if outside the EEA, a transfer mechanism; strip names first to avoid this. | High [C]; medium [P] |
| (d) Publishing aggregate metrics | ALLOWED | F1 | Aggregates contain neither protected expression nor personal data. | High |
| (e) Publishing charts | ALLOWED | F1, F4 | Same; do not use the FDA logo or imply endorsement. | High |
| (f) Publishing transformed/reconstructed records | ALLOWED [C] / UNCLEAR [P] if individuals identifiable | F1, F2, F6, G1, G2 | Free to adapt; state that records are modified, give copy date and link. A reconstructed record that still identifies the investigator (name, or letter ID that resolves to the name) remains personal data. | High [C]; medium [P]. Unresolved: is a letter reference number an indirect identifier you are willing to publish? (It resolves to the named page.) |
| (g) Publishing per-case inputs and predictions | ALLOWED [C] / UNCLEAR [P] if individuals identifiable | F1, G1, G2 | As (f). A model "prediction" about a named investigator's conduct adds a new, possibly inaccurate statement about a person — avoid attaching predictions to identifiable individuals. | Medium |
| (h) Publishing cached API responses | ALLOWED for cached fda.gov pages [C]; UNCLEAR for Data Dashboard API output [T] | F1, F12, CNV-4 | Web content is public domain. Dashboard API requires registration whose terms I could not see. | High / low |
| (i) Publishing prompts or quoted source text | ALLOWED [C] / UNCLEAR [P] if names quoted | F1, "Unless otherwise noted" | FDA-authored text may be quoted at any length. Third-party material embedded in letters is not covered. | High [C] for FDA-authored text; medium overall |
| (j) Publishing trained models / derived artifacts | ALLOWED | F1, F3 | No restriction on derivatives. Models can memorise names; train on de-named text. | High [C]; medium [P] |
| (k) Redistributing original records | ALLOWED [C] / UNCLEAR [P] (names of investigators and FDA staff are in the originals) | F1, F2, F8, G1–G3 | Permitted by FDA; FDA prefers linking and "strongly recommends" copy date + link back. Verbatim mirroring republishes personal data from the EU. | High [C]; low-medium [P]; counsel |
| (l) Redistributing modified records | ALLOWED (with names removed and modifications stated) | F1, F2 | No integrity requirement, but do not present altered text as FDA's wording. | High |
| (m) Including files inside an MIT repository | ALLOWED, but not as MIT-licensed material | F1, F3 | Public-domain text cannot be "licensed" by the publisher; mark the data directory as US Government work / public domain, outside the MIT grant. | Medium (foreign-copyright point above) |
| (n) Attribution / NOTICE | Not required; recommended | F1, F2, F4, F5 | "Credit … is appreciated but not required." Recommended: source = U.S. Food and Drug Administration (plain text), URL, date copied, statement of non-endorsement. No logo. | High |
| (o) Share-alike | None | F1 | No downstream conditions. | High |
| (p) Privacy / data protection / contractual | UNCLEAR | F8, G1–G3, F6 | Named investigators + FDA employees = personal data under GDPR; Art. 10 applicability unresolved; Art. 14 notice position needed; accuracy duty implies tracking close-out/response status. No contractual terms on fda.gov content. | Medium; counsel |

---

## 2a. ClinicalTrials.gov

**Inspected:** Terms and Conditions at https://clinicaltrials.gov/about-site/terms-conditions (the old `/terms-conditions` URL serves the same app; HTTP 200). Page metadata in the site bundle: `lastModDate: 2023-01-31`. API: `https://clinicaltrials.gov/api/v2/version` returned `"apiVersion" : "2.0.5", "dataTimestamp" : "2026-11-16T10:00:05"`. **Rights holder:** US Government (NLM/NIH) for the database; third parties (sponsors) for some content. **SPDX:** none (custom terms).

Extraction note: the page is rendered client-side; the text below was extracted from the string literals of the site's own script chunk (`chunk-D_cHimam2.js`) served by clinicaltrials.gov on 2026-11-16. Wording is verbatim; visual layout was not seen. Re-confirm in a browser before the audit is finalised.

### Provisions

| ID | Verbatim excerpt (https://clinicaltrials.gov/about-site/terms-conditions) |
|---|---|
| C1 | "The following Terms and Conditions apply for use of ClinicalTrials.gov data. Downloading ClinicalTrials.gov data indicates your acceptance of the following Terms and Conditions. These Terms and Conditions apply to all data obtained from ClinicalTrials.gov, independent of format and method of acquisition." |
| C2 | "ClinicalTrials.gov data are available to all requesters, both within and outside the United States, at no charge." |
| C3 | "In any publication or distribution of these data, you should: Attribute the source of the data as ClinicalTrials.gov / Update the data such that they are current at all times / Clearly display the date the data were processed by ClinicalTrials.gov / State any modifications made to the content of the data, along with a complete description of the modifications" |
| C4 | "You shall not assert any proprietary rights to any portion of the database, or represent the database or any part thereof to anyone as other than a United States Government database." |
| C5 | "You shall not use any email addresses extracted from our database for marketing or other promotional purposes." |
| C6 | "The ClinicalTrials.gov data carry an international copyright outside the United States and its Territories or Possessions. Some ClinicalTrials.gov data may be subject to the copyright of third parties; you should consult these entities for any additional terms of use." |
| C7 | "These terms and conditions are in effect as long as the user retains any of the data obtained from ClinicalTrials.gov." |
| C8 | "ClinicalTrials.gov is updated daily. You should check ClinicalTrials.gov frequently for updated information." |
| C9 | Warranty: "Neither the United States Government … make any warranties, expressed or implied, with respect to data contained in the database, and, furthermore, assume no liability for any party's use…" |

### Analysis notes

- **[C]/[T]** For an EU publisher C6 matters: the US Government asserts copyright outside the US, so the T&C are the operative permission. They contemplate "publication or distribution" (C3) but contain no express licence grant, no statement on derivative works, and no open licence. Modification is permitted if described (C3, 4th bullet).
- **[T]** C3 uses "should"; C4/C5 use "shall not". "Update the data such that they are current at all times" cannot be met by a frozen benchmark snapshot — mitigate by displaying the processing date (`dataTimestamp`), shipping a refresh script, and stating the snapshot is not current. Whether that satisfies NLM is unresolved.
- **[C] third parties (C6):** free-text fields (eligibility criteria, descriptions) are sponsor-written; uploaded study documents ("Study Protocol, Statistical Analysis Plan, and Informed Consent Form" — string found in the site bundle) are sponsor-authored PDFs. NLM gives no licence for these.
- **[P]** Records contain names, phone numbers and emails of investigators, study officials and contacts — personal data under GDPR.
- **[S]** Registry entries are sponsor-submitted, not verified by NLM (C9), change daily (C8); eligibility text is unstructured; no enrolment-level or consent-process operational data.

### Matrix — ClinicalTrials.gov

Artifacts: API v2 JSON/CSV, bulk downloads, study-record fields; separately, uploaded protocol/SAP/ICF PDFs.

| Use | Classification | Provisions | Explanation | Confidence / unresolved |
|---|---|---|---|---|
| (a) Commercial research use | ALLOWED | C1, C2 | "available to all requesters … at no charge"; no non-commercial limit. | High |
| (b) Internal processing | ALLOWED | C1, C2 | No restriction on internal use. | High |
| (c) External AI APIs | ALLOWED | C1–C5 | Not restricted; drop contact names/emails before sending [P]. | Medium-high |
| (d) Aggregate metrics | ALLOWED | C3 | Attribute ClinicalTrials.gov and show data date. | High |
| (e) Charts | ALLOWED | C3, C4 | Same; do not present as your proprietary database. | High |
| (f) Transformed / reconstructed records | ALLOWED with conditions | C3 (4th bullet), C4 | Must "State any modifications … along with a complete description". | Medium. Unresolved: "current at all times". |
| (g) Per-case inputs and predictions | ALLOWED with conditions | C3, C6 | Inputs derived from registry fields need attribution, date, modification statement. Long verbatim sponsor text carries the C6 third-party caveat. | Medium |
| (h) Cached API responses | ALLOWED with conditions for registry responses; n/a for LLM responses except where they reproduce data | C1, C3 | Cached ClinicalTrials.gov API payloads are "distribution of these data". | Medium; CNV-3 |
| (i) Prompts / quoted source text | ALLOWED for structured fields and short quotations; UNCLEAR for bulk verbatim sponsor free text | C3, C6 | NLM flags third-party copyright without identifying which data. | Medium / low |
| (j) Trained models / derived artifacts | UNCLEAR (leaning allowed) | C3, C4, C6 | Terms are silent on derivatives other than modified data; nothing prohibits it; do not claim proprietary rights in the underlying data. | Medium-low |
| (k) Redistributing original records | ALLOWED with conditions for registry records; UNCLEAR for uploaded protocol/SAP/ICF documents | C2, C3, C6 | Distribution is contemplated; four "should" conditions apply. Sponsor documents: link, do not mirror. | Medium / low |
| (l) Redistributing modified records | ALLOWED with conditions | C3 | Complete description of modifications required. | Medium |
| (m) Inside an MIT repository | ALLOWED only as a carve-out, not under MIT | C4, C6 | Applying MIT to the data would be "assert[ing] proprietary rights" and misdescribing a US Government database; add a data NOTICE and exclude the directory from the MIT grant. | Medium |
| (n) Attribution / NOTICE | Required in substance ("should") | C3, C4 | Source = ClinicalTrials.gov; processing date; modification log; statement that it is a US Government database. | High |
| (o) Share-alike | None, but terms persist while data is retained | C7 | No copyleft; advisable to pass the T&C through to downstream users. | Medium |
| (p) Privacy / contractual | UNCLEAR [P]; contractual limits as listed | C5, C1 | Contact personal data → GDPR; emails must not be used for marketing; acceptance by download (C1). Remove contact fields from published artifacts. | Medium |

## 2b. AACT (CTTI)

**Inspected:** https://aact.ctti-clinicaltrials.org/ → redirects to `/landing` (HTTP 200); `/sign_up` (HTTP 200). **Rights holder:** footer "© 2026 Clinical Trials Transformation Initiative · A project of CTTI. Data derived from ClinicalTrials.gov." **SPDX:** none found. **Terms: COULD NOT VERIFY (CNV-1).**

| ID | Source | Verbatim excerpt |
|---|---|---|
| A1 | https://aact.ctti-clinicaltrials.org/landing | "AACT is a public relational database with all protocol and results data for every study on ClinicalTrials.gov — refreshed daily, and ready to query in the cloud or download in full." / "Open — Query in the cloud or download the full database. No proprietary software." / "Create an account to connect to the cloud database with your own credentials, download full snapshots…" |
| A2 | https://ctti-clinicaltrials.org/citation-policy/ | "We do ask that you acknowledge CTTI as the source whenever using or referencing our materials in any format… This applies to both original and derivative works." "Please acknowledge the "Clinical Trials Transformation Initiative."" |
| A3 | GitHub org `ctti-clinicaltrials` | Public repos visible: `aact-proj` (MIT, pushed 2022-12-14), `aact-sup` (MIT), `PROPHETIC` (MIT), `aact-web` and `aact-docker-db` (no licence). `ctti-clinicaltrials/aact` → 404. These are code repos; none states a licence for the database content. |

The sign-up form (first name, last name, email, password) shows no terms text in the fetched HTML. Underlying data remain subject to ClinicalTrials.gov T&C (C1: "independent of format and method of acquisition").

| Use | Classification | Explanation | Confidence |
|---|---|---|---|
| (a) Commercial research use | ALLOWED | A1 "public", "Open"; no restriction visible; CT.gov C2. | Medium (terms behind login unseen) |
| (b) Internal processing | ALLOWED | As (a). | Medium |
| (c) External AI APIs | UNCLEAR | No visible terms; CT.gov layer allows. | Low |
| (d) Aggregate metrics | ALLOWED | Acknowledge CTTI (A2) and ClinicalTrials.gov with data date (C3). | Medium |
| (e) Charts | ALLOWED | As (d). | Medium |
| (f) Transformed records | UNCLEAR | AACT-specific terms unseen; CT.gov layer requires modification statement. | Low |
| (g) Per-case inputs/predictions | UNCLEAR | As (f). | Low |
| (h) Cached API responses | UNCLEAR | As (f). | Low |
| (i) Prompts / quoted text | UNCLEAR | As (f) plus C6. | Low |
| (j) Trained models | UNCLEAR | Silent. | Low |
| (k) Redistributing original records (AACT snapshots/tables) | UNCLEAR | Database is "© 2026 CTTI"; no redistribution licence found; EU sui generis database right not addressed anywhere. | Low |
| (l) Redistributing modified records | UNCLEAR | As (k). | Low |
| (m) Inside an MIT repo | UNCLEAR | As (k); CT.gov C4 also applies. | Low |
| (n) Attribution | Required in substance | A2 + C3. | Medium |
| (o) Share-alike | UNCLEAR | Not visible. | Low |
| (p) Privacy / contractual | UNCLEAR | Account required for access (personal data given to CTTI/Duke); account terms unseen; same contact personal data as CT.gov. | Low |

**Recommendation:** take registry data directly from the ClinicalTrials.gov API (terms verified), use AACT at most as an internal convenience, and do not redistribute AACT tables until CTTI's terms are read from inside an account or confirmed in writing.

---

## 3. CDISC SDTM/ADaM Pilot 01 (CDISCPILOT01)

**Inspected:** https://github.com/cdisc-org/sdtm-adam-pilot-project , branch `master`, commit `667511d4b183871d74392ba691c935c38d431d39` (2024-12-20, "Merge pull request #1 from cdisc-org/add_dataset-jsonv1.1"); no releases/tags. **No LICENSE file exists**; GitHub API `license: null`. Governing text is the README "Terms of Use" (present since the initial commit `2f1a3eb6`, 2019-05-23) and the identical PDF `CDISC.Pilot Project Data.Website Disclaimer.v1.pdf`. **Rights holder:** CDISC (terms issuer); underlying data provided by Eli Lilly and Company. **SPDX:** none (`LicenseRef-CDISC-Pilot-Terms` would be an appropriate local identifier).

### Provisions

| ID | Source | Verbatim excerpt |
|---|---|---|
| D1 | https://github.com/cdisc-org/sdtm-adam-pilot-project/blob/master/README.md | "This website provides clinical test data for informational purposes and the convenience of the public. … The data has been analyzed, cleansed, and aggregated where appropriate to facilitate use and discussion in research. By downloading / using this data, you agree to the Terms of use." |
| D2 | same, "Terms of Use" | "You shall not (and will not allow or assist any third party to), under any circumstances: (i) mislead, confuse, or cause misapprehension or confusion among users of the data as to the features, functionality, origin, capabilities, or other aspects of the data, (b) disassemble, reverse engineer, decompile, modify, or alter any part of the Data; (c) use the Data in any manner or for any purpose that violates any law or regulation, (d) use the Data in order to compete with CDISC, (e) sublicense or distribute the data for a fee, or (f) sublicense or distribute the data without an attribution back to CDISC." |
| D3 | `sdtmadampilotprojectreport.pdf` in the repo, §2.2.1 | "Eli Lilly and Company (the Legacy Sponsor) provided the legacy data used in CDISCPILOT01 for the purposes of this pilot project. De-identification of the data and redaction of documents occurred prior to release to the pilot project team. De-identification included changing dates of data elements while maintaining all chronological relationships and sequences within the data elements for each subject…" Abstract: "provided by Eli Lilly and Company from a phase II clinical trial." |
| D4 | same report | "To protect the copyright and licensing agreement of MedDRA non-informative terms masked the actual values of HLGT and HLT (e.g. HLGT_0152, HLT_0617). The pilot project team also chose to mask the AE verbatim text…" |
| D5 | https://www.cdisc.org/terms-and-conditions (covers "CDISC standards in document format", not the pilot data) | "Copyright (c) 2014, CDISC All rights reserved." … "…license to reproduce, publish, display, and use this standard solely within Your Organization for the purpose of promoting the standard. For the avoidance of doubt, the foregoing license grant does not include the right to (i) translate or create derivative works of the Material, or (ii) internally or externally copy, distribute, or post to a Web page." |
| D6 | CDISC Policy 003 – Intellectual Property (https://www.cdisc.org/sites/default/files/2024-08/CDISC%20Policy%20003%20-%20Intellectual%20Property%202024%20FINAL.pdf, linked from https://www.cdisc.org/about/bylaws) | §4.1 "CDISC shall own the copyright in Final Standards…". The policy addresses standards, contributions and patents; I found nothing in it addressing test/pilot datasets. |

### Analysis notes

- **[C]/[T]** The data is **real, de-identified patient-level trial data, not synthetic** (D3). There is no open licence. D2(b) forbids modifying or altering "any part of the Data" "under any circumstances" and is not limited to distribution. D2(e)/(f) restrict distribution "for a fee" and "without an attribution back to CDISC"; permission to redistribute unmodified, free, attributed copies is therefore an inference from those clauses, not an express grant.
- D2 also binds the user not to "allow or assist any third party" — an MIT licence, which lets recipients modify and sell, would do exactly that.
- **Third-party content:** MedDRA coding (D4: only HLGT/HLT masked) and questionnaire content (QS/ADQS datasets: ADAS-Cog, CIBIC, NPI-X per file names `adqsadas`, `adqscibc`, `adqsnpix`) may carry third-party rights not cleared by CDISC's terms. Repo also holds a redacted CSR/protocol and CRF PDFs.
- **[P]** De-identified in 2006 with date shifting; whether that meets GDPR anonymisation is not established by any source — UNCLEAR. Trial subjects were not recruited for this benchmark.
- **[S]** Files present: SDTM `ae cm dm ds ex lb mh qs relrec sc se suppae suppdm suppds supplb sv ta te ti ts tv vs`; **no `ie` (inclusion/exclusion) and no `dv` (protocol deviation) dataset**, and nothing on consent process beyond what `ds`/`dm` hold. One phase II study; weak fit for eligibility/consent triage.

### Matrix — CDISC Pilot 01

Artifacts: everything under `updated-pilot-submission-package/` (.xpt, Dataset-JSON, define.xml, CSR/CRF PDFs), `reference-ranges/`.

| Use | Classification | Provisions | Explanation | Confidence / unresolved |
|---|---|---|---|---|
| (a) Commercial research use | ALLOWED | D1, D2(d) | Offered to "the public" for "use and discussion in research"; no non-commercial clause; must not be used "to compete with CDISC". | Medium |
| (b) Internal processing | ALLOWED for read-only analysis; UNCLEAR for creating altered copies | D2(b) | "modify, or alter any part of the Data" is not limited to distribution; format conversion/derivation is arguably caught. | Medium / low |
| (c) External AI APIs | UNCLEAR | D2, D3 | Not addressed; sending records to a vendor is disclosure of de-identified patient-level data to a third party you must not "allow or assist" to breach the terms. | Low |
| (d) Aggregate metrics | ALLOWED | D2(i),(f) | Results are not "the Data"; attribute CDISC and do not misdescribe origin. | Medium-high |
| (e) Charts | ALLOWED | as (d) | Aggregate charts only; patient-level plots approach redistribution. | Medium |
| (f) Transformed / reconstructed records | PROHIBITED | D2(b) | Direct conflict with "modify, or alter any part of the Data". | High |
| (g) Per-case inputs and predictions | PROHIBITED where inputs are re-serialised/altered records; UNCLEAR for verbatim unaltered rows | D2(b),(f) | Benchmark inputs are normally transformed records. | Medium-high |
| (h) Cached API responses | UNCLEAR | D2(b) | Model outputs that restate or alter records are altered data in substance. | Low |
| (i) Prompts / quoted source text | UNCLEAR | D2(b), D4 | Prompts embedding records = altered presentation; CSR/protocol/CRF text has no licence beyond D2. | Low |
| (j) Trained models / derived artifacts | UNCLEAR | D2(b),(d) | Silent; training does not alter the data, but "reverse engineer"/"compete with CDISC" wording and patient-level origin leave doubt. | Low |
| (k) Redistributing original records | ALLOWED with conditions (unmodified, free of charge, attribution to CDISC, terms passed on) — by inference only | D2(e),(f) | No express redistribution grant. | Medium-low; ask CDISC to confirm |
| (l) Redistributing modified records | PROHIBITED | D2(b) | As (f). | High |
| (m) Including files in an MIT repository | PROHIBITED as MIT-licensed content | D2(b),(e) | MIT grants modify/sell rights CDISC withholds. Unmodified copies in a clearly separate, non-MIT directory with the terms would fall under (k). Safer: fetch-at-runtime script pinned to commit `667511d4`. | High for the MIT conflict |
| (n) Attribution / NOTICE | Required | D2(f), D2(i) | "attribution back to CDISC"; do not confuse users about origin; reproduce the Terms of Use. | High |
| (o) Share-alike | No copyleft, but restrictions must flow down | D2 preamble | "will not allow or assist any third party to". | Medium |
| (p) Privacy / contractual | UNCLEAR [P]; binding browse-wrap [T] | D1, D3 | De-identified real patients; acceptance "By downloading / using". | Medium |

**To unblock (f), (g), (l), (m):** written permission from CDISC (and clarity on Lilly's position) — i.e. REQUIRES PERMISSION in practice.

---

## 4a. PHUSE `phuse-scripts`

**Inspected:** https://github.com/phuse-org/phuse-scripts , branch `master`, commit `398a6d33ced9359ffb58c46650a6d488811176b1` (2025-08-25); no releases. GitHub API licence: `MIT`. `LICENSE.md` was created 2016-05-24 (commit `ebbd52ee`). **Copyright holder: none stated** — `LICENSE.md` contains only the MIT permission and warranty paragraphs, with no "Copyright (c) <year> <holder>" line. **SPDX:** MIT (as detected), with a missing copyright notice.

| ID | Source | Verbatim excerpt |
|---|---|---|
| P1 | https://github.com/phuse-org/phuse-scripts/blob/master/LICENSE.md | Starts directly: "Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction…" (no copyright line). |
| P2 | `data/adam/cdisc/README.md` | "### 2021-12 UPDATE: While CDISC no longer publish the original pilot projects, below, other sources remain…" / "CDISC originally published these data in a pilot electronic submission package… Complete CDISC pilot package is available to CDISC members" |
| P3 | `data/adam/README.md` | "`cdisc` - Modified & augmented version of `cdiscpilot01`" … "`cdiscpilot01` - original CDISC Pilot data, published by CDISC in 2013" … "`cdisc-split` - 2-study version of `cdiscpilot01`…" … "`TDF_ADaM_v1.0` - Update fromo Test Data Factory team" |
| P4 | `data/sdtm/README.md` | "cdiscpilot01 is the original pilot datatsets from CDISC" / "cdiscpilot_update1 (updated_cdiscpilot) is the first update by Test Data Factory team…" |
| P5 | `data/sdtm/TDF_SDTM_v1.0/TDF_SDTM_ReadMe.docx` (Nov 2018) | "The PhUSE organization initiated the Test Data Factory (TDF) project to create CDISC-compliant test datasets and make these test datasets publicly available." … "the team decided to use the existing SDTM and ADaM datasets of the CDISCPILOT02 study from 2013 as a starting point" |
| P6 | `data/Tabulations/SDTM - Statin Test Data v0/data readme.txt` | "By Jeno Pizarro, IBM Corporation … Peter Glass, IBM Corporation" / "Proper use - Any updates and enhancements should be made into a new version." |

### Can the MIT licence override CDISC's rights? — assessment

No evidence that it can. (1) A licence only conveys rights the licensor holds; nothing in the repo shows CDISC or Eli Lilly assigned or licensed the pilot data to PHUSE for relicensing (CNV-6). (2) The MIT text licenses "this software and associated documentation files"; applying it to third-party clinical datasets is at best ambiguous. (3) The licence file names no copyright holder at all. (4) CDISC's own current terms (D2) forbid modification, while PHUSE distributes modified versions (P3–P5). The CDISC GitHub terms date from 2019-05-23 and PHUSE's copies predate that (2013–2018), so PHUSE may have received the data under different, unknown terms — but that would not transfer to a new user who is on notice of D2 today. (5) Long-standing public tolerance by CDISC is not a licence. Conclusion: treat PHUSE-original scripts as MIT; treat every CDISC-derived dataset in `data/` as governed by section 3, with the PHUSE MIT statement as an unverified claim.

The `data/send/` tree additionally contains material from other contributors (e.g. files named for Covance, JnJ, Sanofi, Ultragenyx study reports) — out of scope, provenance not examined, do not assume MIT covers it.

**[S]** `data/sdtm/cdiscpilot01`, `updated_cdiscpilot`, `TDF_SDTM_v1.0` contain `dm`, `ds`, `sv` but no `ie`/`dv` files (tree listing). Same single study as section 3.

### Matrix — phuse-scripts (CDISC-derived data: `data/adam/*`, `data/sdtm/*`)

| Use | Classification | Explanation | Confidence |
|---|---|---|---|
| (a) Commercial research use | ALLOWED | MIT (P1) and CDISC D1 both permit. | Medium-high |
| (b) Internal processing | ALLOWED | As (a); D2(b) caveat on altered copies. | Medium |
| (c) External AI APIs | UNCLEAR | Upstream D2/D3 concerns. | Low |
| (d) Aggregate metrics | ALLOWED | Attribute PHUSE and CDISC. | Medium-high |
| (e) Charts | ALLOWED | As (d). | Medium |
| (f) Transformed records | UNCLEAR — REQUIRES PERMISSION from CDISC to be safe | MIT says yes; upstream D2(b) says no; MIT grantor's authority unverified. | Low |
| (g) Per-case inputs/predictions | UNCLEAR | As (f). | Low |
| (h) Cached API responses | UNCLEAR | As (f). | Low |
| (i) Prompts / quoted text | UNCLEAR | As (f). | Low |
| (j) Trained models | UNCLEAR | As section 3 (j). | Low |
| (k) Redistributing original records | ALLOWED with conditions (unmodified upstream files, free, attribution to CDISC and PHUSE, both notices) | Satisfies both MIT and D2(e)/(f). Applies to `cdiscpilot01` folders only; the TDF/`cdisc`/`cdisc-split` sets are already modified. | Medium-low |
| (l) Redistributing modified records (incl. PHUSE's TDF versions) | UNCLEAR | Conflict as (f). | Low |
| (m) Inside an MIT repo | UNCLEAR | Facially MIT-compatible, but the provenance defect means your MIT repo would repeat an unverified grant. | Low |
| (n) Attribution | Required | MIT notice must be kept (note: there is no copyright line to reproduce — cite repo + commit); CDISC attribution per D2(f). | High |
| (o) Share-alike | None in MIT; D2 flow-down upstream | | Medium |
| (p) Privacy / contractual | UNCLEAR | Same de-identified real patient data as section 3. | Medium |

PHUSE-authored scripts (non-data): ALLOWED for all uses under MIT with notice retention — not otherwise relevant to this benchmark.

## 4b. `SafetyGraphics/safetyData`

**Inspected:** https://github.com/SafetyGraphics/safetyData , branch `main`, commit `afb971624c210db0b6103c2927ac4148fd97f88b` (2022-04-26); release `v1.0.0` (2021-05-04); CRAN shows Version 1.0.0, Published 2021-01-19, "License: MIT + file LICENSE". GitHub API reports `NOASSERTION` because `LICENSE` is the two-line CRAN stub. **Copyright holder:** "safetyData authors" (2020); DESCRIPTION authors Jeremy Wildfire [aut, cre], Renan Escalante Chong [aut]. **SPDX:** MIT. No commits since April 2022.

| ID | Source | Verbatim excerpt |
|---|---|---|
| S1 | `LICENSE.md` | "# MIT License / Copyright (c) 2020 safetyData authors" |
| S2 | `DESCRIPTION` | "License: MIT + file LICENSE" |
| S3 | `README.md` | "The package reformats PHUSE's sample ADaM and SDTM datasets as an R package…" / "PHUSE released the data under the permissive MIT license, so reuse with attribution is encouraged." |
| S4 | `data-raw/sdtm/README.md` | "Original data … phuse-scripts/blob/master/data/sdtm/cdiscpilot01/" / "Original License … phuse-scripts/blob/master/LICENSE.md" / "Converted domain level data from from xpt to csv" |

Assessment: the package's MIT claim rests entirely on PHUSE's (S3), which rests on nothing verifiable (4a). The data is CDISCPILOT01 converted to `.rda`/`.csv` (S4) — i.e. already a format-altered copy. Files: `data/adam_*.rda` (10), `data/sdtm_*.rda` (22: ae cm dm ds ex lb mh qs relrec sc se suppae suppdm suppds supplb sv ta te ti ts tv vs), `data-raw/`. No `ie`/`dv`.

**Matrix — safetyData:** identical to 4a for every use (a)–(p), with these differences: (k) "original records" here are already reformatted from CDISC's files, so classification is **UNCLEAR** rather than ALLOWED; (n) attribution must include "Copyright (c) 2020 safetyData authors" + MIT text, plus PHUSE and CDISC. Confidence low for all publication/redistribution uses.

---

## 5a. Gilead `gsm.datasim` (and `gsm.core`, `gsm`, `gsm.mapping`)

**Location:** https://github.com/Gilead-Public/gsm.datasim (`Gilead-BioStats/gsm.datasim` redirects there). **Not in the OpenRBQM org**: `OpenRBQM/gsm.datasim`, `OpenRBQM/gsm.core`, `OpenRBQM/clindata` → 404; that org's 9 public repos are `OpenRBQM.github.io`, `gsm.digitpref`, `cluster`, `gsm.ae`, `gsm.query`, `openrbqm`, `openRBQM-workshop`, `gsm.pd`, `openRBQM-workshop-EU25`, and `openrbqm`'s README links to the Gilead-BioStats URLs.

| Package | Repo | Inspected | Licence (file / DESCRIPTION) | Copyright holder | Status |
|---|---|---|---|---|---|
| gsm.datasim | Gilead-Public/gsm.datasim | default branch `dev` @ `37df8fad37b5b4976b26e0ee42ca40601d1a5e08` (2026-11-13), Version 2.1.0.9000; latest release `v2.1.0` (2026-11-02) = commit `29fc61c1ca83ceaf38c4c2ba54613872aa5a1d66` | `LICENSE.md` Apache License 2.0; "License: Apache License (>= 2)"; SPDX Apache-2.0 | "Copyright 2024 Gilead Sciences"; `person("Gilead Sciences", role = "cph")` | Active (pushed 2026-11-16) |
| gsm.core | Gilead-Public/gsm.core | `dev` @ `29f1f82bb25fddc11b71ddb9ec5203d4bcc6c6f1` (2026-11-16), 1.3.2.9000; release `v1.3.2` (2026-11-02) | Apache-2.0 | "Copyright 2024 Gilead Sciences" | Active |
| gsm | Gilead-Public/gsm | `dev` @ `c3e704e4416a8938611f5a2912db4b0359579f07` (2026-07-28), 2.2.5; release `v2.2.5` (2026-07-27) | Apache-2.0 | "Copyright 2024 Gilead Sciences" | gsm.core README: "`{gsm}`, which has been deprecated as of March 2025" |
| gsm.mapping | Gilead-Public/gsm.mapping | `dev`, 1.2.0.9000; release `v1.2.0` (2026-11-02) | Apache-2.0 | Gilead Sciences (cph) | Active |
| workr (hard dependency) | Gilead-Public/workr | 1.1.1; release `v1.1.1` (2026-10-20) | "MIT + file LICENSE"; LICENSE stub "YEAR: 2026 / COPYRIGHT HOLDER: Workr Maintainer"; GitHub `NOASSERTION` | DESCRIPTION `person("Gilead", role = "cph")` | Active |

None of these is on CRAN (index pages return 404); install from GitHub (`pak::pak("Gilead-Public/gsm.datasim@*release")` per README). No `NOTICE` file in the gsm.datasim root.

### Provisions

| ID | Source | Verbatim excerpt |
|---|---|---|
| G-1 | https://github.com/Gilead-Public/gsm.datasim/blob/dev/LICENSE.md | "Apache License … Version 2.0, January 2004" … "Copyright 2024 Gilead Sciences / Licensed under the Apache License, Version 2.0 (the "License")…" |
| G-2 | `DESCRIPTION` | "Description: Generates synthetic clinical trial data for testing and development of clinical monitoring applications. Produces configurable multi-snapshot longitudinal datasets across SDTM-style and custom domains…" / "License: Apache License (>= 2)" |
| G-3 | `NEWS.md` (v2.0.0) | "**New domains:** added `Raw_VISIT`, `Raw_Death` …, `Raw_Consents`, `Raw_Baseline`, `Raw_Randomization`, `Raw_OverallResponse`, and `Raw_GENERAL`, plus gradual enrollment simulation…" Also: "**Replacing `clindata` with `gsm.datasim`:** The object `gsm.core::lSource` was created using `gsm.datasim`…" |
| G-4 | Apache-2.0 §4 (in LICENSE.md) | Redistribution of the Work or Derivative Works requires giving recipients a copy of the licence, marking modified files, and retaining copyright/attribution notices. |

### What gsm.datasim generates (from source, not executed)

- **Language / runtime:** R (>= 4.1.0). **Imports:** arrow, cachem, cli, digest, dplyr, fs, glue, jsonlite, lifecycle, logger, lubridate, magrittr, purrr, R6, rlang, stringr, tictoc, utils, workr (>= 1.1.0), yaml. **Suggests:** gsm.core, gsm.kri, gsm.mapping, gsm.qtl, gsm.reporting, knitr, rmarkdown, testthat, withr. Generators are written against `gsm.mapping` YAML specs (e.g. "Generate Raw IE based on `IE.yaml` from `gsm.mapping`").
- **Generator files (`R/Raw_*.R`):** AE, AntiCancer, Baseline, Consents, DATACHG, DATAENT, Death, ENROLL, GENERAL, IE, LB, OverallResponse, PD, PK, QUERY, Randomization, SDRGCOMP, SITE, STUDCOMP, STUDY, SUBJ, VISIT, VS, gilda_STUDY. Output via `export_study_data()` as CSV or Parquet; multi-snapshot longitudinal studies; site-level outlier/"hotspot" injection (`outlier_intensity`, `risk_profile`).
- **Subjects/sites/enrolment:** `Raw_SITE` (invid, country/state/city, site status, placeholder investigator names sampled from "John/Joanne/Fred" × "Doe/Deer/Smith"); `Raw_SUBJ` (subjid, site link, enrollyn, enrolldt, timeonstudy, age, sex, race, first dose, IP non-starter and premature-discontinuation fields); `Raw_ENROLL` (subjid, invid, country, enrollyn, subjectid).
- **Eligibility (`Raw_IE`):** columns studyid, subjid, tiver, ietestcd, ietest, ieorres, iecat. `ietestcd` is sampled at random from `incl1..incl10, excl1..excl10`; `ieorres` is a random "Yes"/"No"; `tiver` is constant "A1". No criterion text and no link to subject characteristics.
- **Consent (`Raw_Consents`):** subjid, studyid, cons_dt, constype, conscat; `constype` is constant "WITHDRAWAL OF CONSENT", `conscat` constant "MAIN STUDY CONSENT", `cons_dt` = start date. No ICF versions, signature dates, re-consent or process timing.
- **Protocol deviations (`Raw_PD`):** `dvdecod` sampled from "Informed Consent", "Missing Data", "Study Procedures", "Inclusion Criteria", "Exclusion Criteria" (base probabilities 0.3/0.3/0.3/0.05/0.05 with site hotspots on the two I/E categories); `dvterm` constant "Inclusion/Exclusion description"; `deemedimportant` random Yes/No.

**[S] Judgement:** it can generate the operational skeleton (studies, sites, subjects, enrolment status/dates, I/E rows, consent-withdrawal rows, categorised deviations, queries, data-entry lag) with site-level anomaly injection, but eligibility and consent content is random or constant placeholder — there is no ground truth for "is this an eligibility/consent issue" beyond the PD category label. A benchmark would need its own semantic layer on top. Possible defect (CNV-9): `ietest()`/`iecat()` test for upper-case `"^INC"`/`"INC"` while codes are generated in lower case (`incl1`), so `iecat` may come out as "Exclusion" for every row — verify by running.

**Provenance check:** GitHub code search of gsm.datasim for "cdisc", "phuse", "safetyData" returned no hits; "clindata" appears only in NEWS.md/AGENTS.md prose. Generators use `sample()` over hard-coded vocabularies. (Code search covers the default branch only.)

### Matrix — gsm.datasim (code, bundled sample data in `data-raw/simulated_data/`, `inst/`, and output you generate)

| Use | Classification | Explanation | Confidence |
|---|---|---|---|
| (a) Commercial research use | ALLOWED | Apache-2.0 grants use to anyone, commercial included. | High |
| (b) Internal processing | ALLOWED | Same. | High |
| (c) External AI APIs | ALLOWED | No restriction; data is synthetic. | High |
| (d) Aggregate metrics | ALLOWED | | High |
| (e) Charts | ALLOWED | | High |
| (f) Transformed / reconstructed records | ALLOWED | Derivative works permitted (§2); output of running the generator is your own data. | High |
| (g) Per-case inputs and predictions | ALLOWED | | High |
| (h) Cached API responses | ALLOWED | | High |
| (i) Prompts / quoted source text | ALLOWED | Quoted package code/docs stay Apache-2.0 (keep notice). | High |
| (j) Trained models / derived artifacts | ALLOWED | | High |
| (k) Redistributing original records (repo's bundled parquet/CSV) | ALLOWED with Apache §4 conditions | Include licence copy and "Copyright 2024 Gilead Sciences". | High |
| (l) Redistributing modified records | ALLOWED with §4 conditions | State that files were changed. | High |
| (m) Inside an MIT repository | ALLOWED | Self-generated output can be released under MIT/any terms (the licence does not claim program output; medium-high confidence on that point). Any copied Gilead files (code, bundled data, YAML specs from gsm.mapping) remain Apache-2.0 and need a `LICENSE-APACHE`/third-party notice — they do not become MIT. | High / medium-high |
| (n) Attribution / NOTICE | Required for copied Apache material; none for self-generated output | No upstream NOTICE file exists. Good practice: cite gsm.datasim v2.1.0 (commit `29fc61c1`) as the generator. | High |
| (o) Share-alike | None | Apache-2.0 is permissive. | High |
| (p) Privacy / contractual | ALLOWED (no personal data found in source) | Synthetic; investigator names are generic placeholders. No terms beyond the licence. | High for generated data |

`gsm.core`, `gsm`, `gsm.mapping` (Apache-2.0, Gilead Sciences): same matrix. `workr` is MIT with an inconsistent holder line ("Workr Maintainer" vs cph "Gilead") — low risk, note in third-party notices.

## 5b. Gilead `clindata`

**Inspected:** https://github.com/Gilead-BioStats/clindata (not moved), branch `main` @ `f3b2f798fe53b2e79eb00c6bf2a2e115cee90d6d` (2025-03-18); Version 1.0.5; release `v1.0.5` (2024-02-13). Licence: Apache-2.0 (`LICENSE.md`, "Copyright 2023 Gilead Sciences"; DESCRIPTION "License: Apache License (>= 2)", `person(given = "Gilead Sciences", role = "cph")`). Effectively superseded (G-3: "Replacing `clindata` with `gsm.datasim`"); no release since Feb 2024.

| ID | Source | Verbatim excerpt |
|---|---|---|
| K1 | `README.md` | "A repository of various anonymized clinical trial data for use in open source testing and development." … includes "participant demographics", "I/E criteria", "study metadata" |
| K2 | `DESCRIPTION` | "Title: Synthetic Clinical Data for testing and development" / "Description: Synthetic Clinical Data for testing and development. Raw form data to start…" |
| K3 | `data-raw/rawplus/dm_metadata.json` | Column list includes `"brthdat": ["string", "Date of Birth"]`, `"subjinit_nsv": ["string", "SUBJECT INITIALS"]`, `"invid": ["string", "Investigator ID"]` |
| K4 | `data-raw/rawplus.R` | `library(rbmPipe)` / `datasets <- rawplus_1_import()` — base tables come from a pipeline not in the repo; consent, IE and enrol tables are patched in as "temporary fix" (`rawplus_consent.rda`, `rawplus_ie.rda`; screen-failure reasons sampled with `sample(c('Inclusion/Exclusion Criteria','Withdrawal of Consent','Medical Issue'), …)`). |

- **CDISC/PHUSE embedding:** GitHub code search of clindata for "cdisc" and "safetyData" returned no hits, and the schema (Rave-style "rawplus"/EDC/CTMS columns) is unlike CDISCPILOT01. I found no evidence that clindata embeds CDISC/PHUSE data, but I did not inspect the binary data, so this is "no evidence found", not "verified absent".
- **[P] Provenance conflict (CNV-7):** K1 says "anonymized clinical trial data"; K2 says "Synthetic". If any table is anonymised real Gilead trial data, GDPR anonymisation adequacy is unknown; the schema has date-of-birth and subject-initials columns (K3; whether populated not checked).
- Contents relevant to this project: `rawplus_ie`, `rawplus_consent`, `rawplus_enroll`, `rawplus_dm`, `ctms_protdev` (deviation date, category, deemedimportant), `ctms_site`, `ctms_study`, `edc_queries`, etc.

### Matrix — clindata

| Use | Classification | Explanation | Confidence |
|---|---|---|---|
| (a) Commercial research use | ALLOWED | Apache-2.0. | High |
| (b) Internal processing | ALLOWED | Apache-2.0. | High [C]; medium [P] |
| (c) External AI APIs | UNCLEAR | Licence allows; real-vs-synthetic status unresolved. | Low-medium |
| (d) Aggregate metrics | ALLOWED | | High |
| (e) Charts | ALLOWED | | High |
| (f) Transformed records | ALLOWED [C] / UNCLEAR [P] | Apache permits derivatives; K1/K2 conflict. | Medium |
| (g) Per-case inputs/predictions | ALLOWED [C] / UNCLEAR [P] | As (f). | Medium |
| (h) Cached API responses | ALLOWED [C] / UNCLEAR [P] | As (f). | Medium |
| (i) Prompts / quoted text | ALLOWED [C] / UNCLEAR [P] | As (f). | Medium |
| (j) Trained models | ALLOWED [C] / UNCLEAR [P] | As (f). | Medium |
| (k) Redistributing original records | ALLOWED [C] with Apache §4 / UNCLEAR [P] | Gilead already publishes them; you would become an independent EU controller if they are personal data. | Medium |
| (l) Redistributing modified records | ALLOWED [C] / UNCLEAR [P] | Mark changes. | Medium |
| (m) Inside an MIT repo | ALLOWED [C] (files stay Apache-2.0) / UNCLEAR [P] | | Medium |
| (n) Attribution | Required | Apache-2.0 copy + "Copyright 2023 Gilead Sciences"; no NOTICE file listed in the repo root. | High |
| (o) Share-alike | None | | High |
| (p) Privacy / contractual | UNCLEAR | CNV-7. Ask the maintainers (repo issue) whether any table derives from real participants, or avoid clindata and use gsm.datasim. | Low |

---

## 6. Cross-source observations for the audit

1. Only **gsm.datasim output** is cleanly publishable inside an MIT repository for all sixteen uses.
2. **FDA text** is free of copyright restriction in the US and FDA says it may be "used freely by anyone", but the publishable form for an EU company is the de-named one; keep issue date, retrieval date, URL and close-out/response status with every record.
3. **ClinicalTrials.gov** data can be published with attribution, processing date and a modification log, in a directory excluded from the MIT grant; do not mirror uploaded sponsor documents; strip contact data.
4. **CDISC pilot data (direct, via PHUSE, or via safetyData)** must not be published in modified form or under MIT without CDISC's written permission; the PHUSE/safetyData MIT labels do not cure this. It also lacks IE/DV domains, so the licensing cost buys little scientific value for this benchmark.
5. **AACT** and **clindata** each have one unresolved blocking question (terms; real-vs-synthetic provenance).
