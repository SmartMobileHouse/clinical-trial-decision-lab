> Appendix B: research notes on sources 6 to 10 (OpenRBQM / gsm, CDISC CORE, sdtmchecks, CTAS, Project Data Sphere). Unedited working notes, kept as supporting evidence for docs/DATA-LICENSING-AUDIT.md.
> Verification date: 2026-11-16. Quotes were collected by automated fetching; some passed through a summarising fetch tool or a reader proxy and may be clipped. Re-read every clause at its source before sign-off.
> Not legal advice. Local paths, individual warning-letter URLs, personal names of letter recipients and FDA staff, and email addresses were removed.

# Licensing / data-rights research — batch B (sources 6–10)

- Verification date for every determination below: **2026-11-16**.
- Method: primary sources fetched live on the verification date via the GitHub REST API (`gh api`), `raw.githubusercontent.com`, PyPI/CRAN metadata APIs, and direct HTTP fetches of publisher pages/PDFs. Quotes are verbatim from the fetched files. Nothing below relies on memory.
- Classification vocabulary: ALLOWED / PROHIBITED / UNCLEAR / REQUIRES PERMISSION.
- Restriction categories used in explanations: **[C]** copyright/license, **[P]** privacy, **[T]** contractual / terms-of-use, **[S]** scientific limitation.
- "COULD NOT VERIFY" marks anything that could not be fetched or confirmed. Uncertainty is never treated as permission.
- This is a factual licensing survey, not legal advice. Items marked UNCLEAR / REQUIRES PERMISSION need counsel or the rights holder.

## 0. Executive table

| # | Source | SPDX | Copyright holder (as stated) | Version / commit inspected | Overall verdict | Most restrictive finding |
|---|---|---|---|---|---|---|
| 6 | OpenRBQM / gsm family | Apache-2.0 (workr dependency: MIT) | "Gilead Sciences" (DESCRIPTION `cph`; LICENSE.md appendix in some repos) | see §6.1 table | ALLOWED as optional external R tool; vendoring allowed under Apache-2.0 conditions | `clindata` sample data is described both as "Synthetic" and as "anonymized clinical trial data" -> do not redistribute it (UNCLEAR); consent mapping depends on a package (`gsm.endpoints`) that is not publicly findable |
| 7 | CDISC CORE engine + CDISC Open Rules | MIT (engine and both rule repos) | "cdisc" (engine, cdisc-open-rules); "verisian" (core-contributor) | see §7.1 | ALLOWED as optional external tool; rule YAML is MIT; Library-derived cache and CDISC standards text are NOT cleared | CDISC Library EULA: COULD NOT VERIFY. CDISC standards documents: internal-organization-only licence, no derivative works, no web posting. CDISC name/logo: approval required |
| 8 | pharmaverse sdtmchecks | Apache-2.0 | "F. Hoffmann-La Roche AG" | devel `fb35f8b3` (1.0.0.01); CRAN 1.0.0 | ALLOWED | None material. No IE/eligibility checks exist; only one consent-related check |
| 9 | IMPALA CTAS | MIT (R "MIT + file LICENSE") | "Bayer" / "Bayer Pharmaceuticals" | main `94c9f061` (0.4.0) | ALLOWED; optional future experiment only | GPL dependencies (lme4, merTools, dbscan) - do not bundle; two PHUSE PDFs in the repo have no stated licence |
| 10 | Project Data Sphere | n/a (contract) | Data Providers retain ownership | "Cancer Research Platform Agreement (v. May 13, 2020)" | Future source only; record-level publication and third-party/AI-API processing PROHIBITED | Purpose limited to cancer research; no disclosure of Data to any non-authorized third party; no publication of Data on a website |

---

## 6. OpenRBQM / Good Statistical Monitoring ({gsm} family)

### 6.1 Repositories, versions, licences (all fetched 2026-11-16)

Important structural fact: the packages do **not** live in the `OpenRBQM` GitHub org. `https://github.com/Gilead-BioStats/gsm` redirects to `Gilead-Public/gsm`; `Gilead-BioStats/gsm.core` and `Gilead-BioStats/gsm.kri` now carry the description "Moved to Gilead-Public/gsm.core — this repo only hosts a docs redirect". `OpenRBQM/gsm.core`, `gsm.kri`, `gsm.mapping`, `gsm.reporting`, `gsm.app` return HTTP 404.

| Repo | Default branch / HEAD commit (date) | Latest release tag (tag commit) | DESCRIPTION `License:` | GitHub-detected SPDX | Copyright statement found |
|---|---|---|---|---|---|
| Gilead-Public/gsm.core | dev `29f1f82bb25fddc11b71ddb9ec5203d4bcc6c6f1` (2026-11-16) | v1.3.2, 2026-11-02 (`78aadcd0…`) | `Apache License (>= 2)` | Apache-2.0 | LICENSE.md appendix: "Copyright 2024 Gilead Sciences"; DESCRIPTION `person("Gilead Sciences", role = "cph")` |
| Gilead-Public/gsm.kri | dev `6e32207b504b38b0d9c21675f82f0c7e30054cc9` (2026-11-10) | v1.8.0, 2026-11-02 (`f47fb930…`) | `Apache License (>= 2)` | Apache-2.0 | DESCRIPTION cph "Gilead Sciences"; LICENSE.md appendix is the unfilled template "Copyright [yyyy] [name of copyright owner]" |
| Gilead-Public/gsm.mapping | dev `f0d698561d44c4c80bd4b786add145358478e2b8` (2026-11-04) | v1.2.0, 2026-11-02 (`3f4728e6…`) | `Apache License (>= 2)` | Apache-2.0 | DESCRIPTION cph "Gilead Sciences"; LICENSE.md template unfilled |
| Gilead-Public/gsm.reporting | dev `c33bceb984f986879b2715833254e138e4f858a0` (2026-11-04) | v1.1.8, 2026-11-02 (`dd4e683a…`) | `Apache License (>= 2)` | Apache-2.0 | DESCRIPTION cph "Gilead Sciences"; LICENSE.md template unfilled |
| Gilead-Public/gsm.datasim | dev `37df8fad37b5b4976b26e0ee42ca40601d1a5e08` (2026-11-13) | v2.1.0, 2026-11-02 | `Apache License (>= 2)` | Apache-2.0 | "Copyright 2024 Gilead Sciences"; DESCRIPTION cph |
| Gilead-Public/gsm.qtl | dev `7417fc43d7b706fc875306e81990c235dd47b1d0` (2026-10-13) | v1.4.0, 2026-09-09 | `Apache License (>= 2)` | Apache-2.0 | No `cph` in DESCRIPTION; LICENSE.md template unfilled -> holder not stated |
| Gilead-Public/gsm.viz (JS) | dev `9bd54d5c52eb00370ee64204a0128c55732906d1` | v2.4.1, 2026-08-07 | n/a (LICENSE file) | Apache-2.0 | template unfilled |
| Gilead-Public/gsm.vizr | main | 0.1.0 (DESCRIPTION) | `Apache License (>= 2)` | Apache-2.0 | not inspected further |
| Gilead-Public/gsm (legacy monolith) | dev `c3e704e4416a8938611f5a2912db4b0359579f07` (2026-07-28) | v2.2.5, 2026-07-27 | `Apache License (>= 2)` | Apache-2.0 | "Copyright 2024 Gilead Sciences" |
| Gilead-BioStats/gsm.app | dev `b4ef087642b23e9ab2ea6585717db352a602ee95` (2026-04-28) | v2.6.1, 2025-09-24 | `Apache License (>= 2)` | Apache-2.0 | "Copyright 2024 Gilead Sciences" in LICENSE.md; no cph in DESCRIPTION |
| Gilead-BioStats/clindata (sample data) | main `f3b2f798fe53b2e79eb00c6bf2a2e115cee90d6d` (2025-03-18) | v1.0.5, 2024-02-13 | `Apache License (>= 2)` | Apache-2.0 | "Copyright 2023 Gilead Sciences" |
| OpenRBQM/gsm.pd | main `77bfb763703f28b8c23e5d683b6db8439f93647f` (2025-02-26) | none (0.0.0.9000) | `Apache License (>= 2)` | Apache-2.0 | no cph; template unfilled |
| OpenRBQM/openrbqm (meta-package) | dev `d74de823386501a6926dca4f0fb2d23d35f41dcc` (2025-10-27) | none (0.0.1) | `Apache License (>= 2)` | Apache-2.0 | template unfilled; stale Remotes pointing at Gilead-BioStats |
| Gilead-Public/workr (hard dependency of gsm.kri, gsm.mapping) | dev | not checked | `MIT + file LICENSE` | NOASSERTION (because of R-style stub) | LICENSE: "YEAR: 2026 / COPYRIGHT HOLDER: Workr Maintainer"; LICENSE.md "Copyright (c) 2026 Workr Maintainer" |
| OpenRBQM/OpenRBQM.github.io (website) | main | n/a | n/a | MIT | page footer: "© 2024–2026 OpenRBQM · Released under the MIT License" |

- **NOTICE files:** none. Root listings of every repo above were fetched; no `NOTICE` / `NOTICE.md` exists in any of them.
- **CRAN:** `gsm`, `gsm.core`, `gsm.kri`, `gsm.mapping`, `gsm.reporting`, `gsm.datasim`, `workr`, `clindata` all return HTTP 404 on `cran.r-project.org/web/packages/<pkg>/index.html` -> GitHub-only installation (`pak::pak("Gilead-Public/gsm.kri@*release")` per README).
- **OpenRBQM site** (https://openrbqm.github.io/): "Open-source software for risk-based quality management (RBQM) in clinical trials — a PHUSE pre-competitive collaboration."

### 6.2 Governing provisions (quoted from `Gilead-Public/gsm.core` LICENSE.md at commit `29f1f82b`; the 194-line LICENSE.md is byte-identical apart from the appendix copyright line across gsm.kri / gsm.mapping / gsm.reporting — md5 `f4eda510…` vs `4bc34975…`)

- **P6-A (Apache-2.0 §2, copyright grant):** "each Contributor hereby grants to You a perpetual, worldwide, non-exclusive, no-charge, royalty-free, irrevocable copyright license to reproduce, prepare Derivative Works of, publicly display, publicly perform, sublicense, and distribute the Work and such Derivative Works in Source or Object form."
- **P6-B (§4, redistribution conditions):** "(a) You must give any other recipients of the Work or Derivative Works a copy of this License; and (b) You must cause any modified files to carry prominent notices stating that You changed the files; and (c) You must retain, in the Source form of any Derivative Works that You distribute, all copyright, patent, trademark, and attribution notices from the Source form of the Work … (d) If the Work includes a "NOTICE" text file as part of its distribution, then any Derivative Works that You distribute must include a readable copy of the attribution notices contained within such NOTICE file".
- **P6-C (§6, trademarks):** "This License does not grant permission to use the trade names, trademarks, service marks, or product names of the Licensor, except as required for reasonable and customary use in describing the origin of the Work and reproducing the content of the NOTICE file."
- **P6-D (clindata provenance conflict):** `Gilead-BioStats/clindata` DESCRIPTION: "Synthetic Clinical Data for testing and development." README.md: "A repository of various anonymized clinical trial data for use in open source testing and development."
- Source URLs: https://github.com/Gilead-Public/gsm.core/blob/29f1f82bb25fddc11b71ddb9ec5203d4bcc6c6f1/LICENSE.md ; https://github.com/Gilead-Public/gsm.kri/blob/6e32207b504b38b0d9c21675f82f0c7e30054cc9/LICENSE.md ; https://github.com/Gilead-BioStats/clindata/blob/f3b2f798fe53b2e79eb00c6bf2a2e115cee90d6d/README.md

### 6.3 KRIs that exist (gsm.kri `inst/workflow/2_metrics/` at `6e32207b`) and their input domains

Each `kriNNNN.yaml` (site level) has a `couNNNN.yaml` country-level twin. Fields below are copied from the YAML `meta:` and `spec:` blocks.

| ID | Metric | Numerator / Denominator | Required mapped domains |
|---|---|---|---|
| kri0001 | Adverse Event Rate | Adverse Events / Days on Study | Mapped_AE, Mapped_SUBJ |
| kri0002 | Serious Adverse Event Rate | Serious Adverse Events / Days on Study | Mapped_AE, Mapped_SUBJ |
| **kri0003** | **Non-Important Protocol Deviation Rate** | Non-Important Protocol Deviations / Days on Study | Mapped_PD, Mapped_SUBJ |
| **kri0004** | **Important Protocol Deviation Rate** | Important Protocol Deviations / Days on Study | Mapped_PD, Mapped_SUBJ |
| kri0005 | Grade 3+ Lab Abnormality Rate | Grade 3+ Abnormal Labs Samples / Total Lab Samples | Mapped_LB, Mapped_SUBJ |
| kri0006 | Study Discontinuation Rate | Subjects Discontinued - Study / Enrolled Subjects | Mapped_STUDCOMP, Mapped_SUBJ |
| kri0007 | Treatment Discontinuation Rate | Subjects Discontinued - Treatment / Enrolled Subjects | Mapped_SDRGCOMP, Mapped_SUBJ |
| kri0007-2 | Premature Treatment Discontinuation Rate | … / Enrolled & Dosed Subjects | Mapped_SUBJ |
| kri0008 | Query Rate | Queries / Total Data Points | Mapped_QUERY, Mapped_DATACHG, Mapped_SUBJ |
| kri0009 | Delayed Query Resolution Rate | Queries Open > 30 Days / Total Queries | Mapped_QUERY, Mapped_SUBJ |
| kri0010 | Delayed Data Entry Rate | Data Pages Entered > 10 Days / Total Data Pages | Mapped_DATAENT, Mapped_SUBJ |
| kri0011 | Data Change Rate | Data Points with 1+ Change / Total Data Points | Mapped_DATACHG, Mapped_SUBJ |
| **kri0012** | **Screen Failure Rate** | Screen Failures / Screened Subjects | **Mapped_ENROLL** only (`subjectid`, `invid`, `enrollyn`); numerator = `enrollyn = 'N'` |
| kri0013 | PK Collection Compliance Rate | PK Samples Collected / Expected | Mapped_PK, Mapped_SUBJ |
| **kri0014** | **Ineligibility** | Number of subjects ineligible / Number of subjects enrolled | **Mapped_EXCLUSION** (`subjid`, `subjectid`, `Source`, `studyid`, `invid`, `country`, `eligibility_criteria`, `ie_violation`); numerator = `Source != 'Neither'`; YAML comment: "Red flag when there are 3 or more possibly ineligible participants" |
| kri0015 / pat0015 | Premature Death Rate (site / subject) | Deaths in First 90 Days / Enrolled Subjects | Mapped_Death, Mapped_SUBJ |
| kri0019 | IP Non-Starter Rate | IP Non-Starters / Enrolled Subjects | Mapped_IPNS |
| kri0020a–f | Repeat Measure (Weight, HR, SBP, DBP, RR, Temp) | identical-value windows / evaluable windows | Mapped_VS, Mapped_SUBJ |
| srs0001 | Site Risk Score | Weight / Maximum Weights | (derived from other KRIs) |

Reports in `inst/workflow/4_modules/`: `report_eligibility.yaml` ("CTQ Eligibility Report", consumes `Mapped_EXCLUSION` and metric `Analysis_qtl0001` from **gsm.qtl**), `report_ipmonitoring`, `report_kri_country`, `report_kri_site`, `report_prematuredeath`.

Mapping specs (gsm.mapping `inst/workflow/1_mappings/` at `f0d69856`) relevant to our synthetic schema:

- `ENROLL.yaml` — Raw_ENROLL: `studyid, invid, country, subjid, subjectid, enrollyn, enroll_dt (Date)`.
- `IE.yaml` — Raw_IE: `studyid, subjid, tiver, ietest, ietestcd, ieorres, iecat`. Logic: `ietestcd ILIKE '%EXC%'` -> EX, `'%INC%'` -> IN; violation when EX & `ieorres = 'Yes'` or IN & `ieorres = 'No'`; only violation rows kept.
- `EXCLUSION.yaml` — "Combining IE and PD data to create QTL participant level dataset"; needs Mapped_IE, Mapped_ENROLL, Mapped_PD (`dvdecod IN ('Exclusion Criteria', 'Inclusion Criteria')`).
- `PD.yaml` — Raw_PD: `studyid, subjid (source subjectenrollmentnumber), deemedimportant, dvdecod (source crocategory), dvterm (source description), dvdtm (source deviationdate)`.
- `SUBJ.yaml` — Raw_SUBJ: `studyid, invid, country, subjid, subject_nsv, enrollyn, timeonstudy, firstparticipantdate, firstdosedate, timeontreatment, …` (many `drv_*` derived columns); keeps `enrollyn == 'Y'`.
- `SITE.yaml` — Raw_SITE: `studyid (protocol), invid (pi_number), InvestigatorFirstName, InvestigatorLastName, site_status, City, State, Country, site_active_dt`.
- `Consents.yaml` — Raw_Consents: `studyid, subjid, cons_dt, constype, conscat`; filters `constype = 'WITHDRAWAL OF CONSENT' AND conscat = 'MAIN STUDY CONSENT'`, then calls `gsm.endpoints::complete_consents`. **No repository named `gsm.endpoints` exists in Gilead-Public, Gilead-BioStats or OpenRBQM (all 404; GitHub repo search returned nothing) -> COULD NOT VERIFY that this step is runnable from public code.**
- **There is no informed-consent KRI in gsm.kri** (no metric YAML references `Mapped_Consents`). Consent appears only as the withdrawal-of-consent mapping above.

Compatibility with synthetic subjects/sites/enrollment/consent/eligibility data: kri0012 (needs only ENROLL) and kri0014 (needs IE + ENROLL + PD) can be fed with small renamed tables; kri0003/0004 additionally need `timeonstudy` in SUBJ. **[S]** These are site-level statistical outlier flags (Normal Approximation / adjusted z-score with accrual thresholds, e.g. kri0012 `AccrualThreshold: 3`), not per-subject eligibility or consent-issue triage; they need many sites and subjects to be meaningful.

### 6.4 Practicality from a Python 3.12 / uv project

R only (`Depends: R (>= 4.0)` or `R (>= 4.1.0)`). No Python bindings, no documented CLI. Invocation would be `Rscript script.R` via `subprocess`, exchanging CSV/Parquet. Friction: not on CRAN (GitHub install via `pak`, `Remotes:` to dev branches), a dependency chain gsm.kri -> gsm.core + gsm.vizr + workr + rmarkdown/gt/DT/htmlwidgets, gsm.mapping -> duckdb/DBI/dbplyr. Feasible as an **optional** external step behind a feature flag with pinned release tags; not suitable as a required dependency. Not executed here (no R run performed) -> runtime behaviour COULD NOT VERIFY.

### 6.5 Use matrix — gsm family ("records" = bundled workflow YAML, example outputs, simulated data in gsm.datasim; clindata treated separately)

| Use | Classification | Provision | Explanation | Artifacts | Confidence / open questions |
|---|---|---|---|---|---|
| (a) commercial-company research use | ALLOWED | P6-A | [C] Apache-2.0 has no field-of-use limit. | all gsm.* packages | high |
| (b) internal processing | ALLOWED | P6-A | [C] Reproduction and use granted. | all | high |
| (c) processing through external AI APIs | ALLOWED (gsm.* code/YAML/simulated data); UNCLEAR (clindata records) | P6-A; P6-D | [C] Reproduction/sublicensing permitted, no confidentiality terms. [P] clindata is called "anonymized clinical trial data" in its README, so its privacy status is unresolved. | code, YAML; clindata `data/`, `data-raw/` | high / low for clindata |
| (d) publishing aggregate benchmark metrics | ALLOWED | P6-A | [C] Licence does not reach outputs computed on our own data. | our outputs | high |
| (e) publishing charts/visualizations | ALLOWED | P6-A, P6-B | [C] Own charts free; if gsm.viz/gsm.kri HTML widgets (bundled JS) are redistributed inside a published report, that is distribution of Apache-2.0 code -> keep licence/notice. | reports embedding `inst/htmlwidgets/lib` | medium |
| (f) publishing transformed or reconstructed records | ALLOWED (gsm.datasim simulated data, YAML); UNCLEAR (clindata) | P6-A, P6-B(b); P6-D | [C] Derivative works permitted with change notices. [P] clindata provenance conflict. | `gsm.datasim/data-raw/simulated_data/**`; clindata | medium |
| (g) publishing per-case inputs and model predictions | ALLOWED | P6-A | Inputs are our own synthetic data; licence imposes nothing on them. | ours | high |
| (h) publishing cached API responses | ALLOWED (not applicable) | — | The tools expose no API and no remote service. | — | high |
| (i) publishing prompts or quoted source text | ALLOWED | P6-A, P6-B | [C] Quoting KRI definitions / YAML is reproduction of an Apache-2.0 work: attribute and keep the licence reference. | metric YAML `meta:` text | high |
| (j) publishing trained models or derived artifacts | ALLOWED | P6-A | [C] Derivative works expressly licensed. | — | medium (models are not addressed by name) |
| (k) redistributing original records | ALLOWED (gsm.*); UNCLEAR (clindata) | P6-B; P6-D | [C] With licence copy and retained notices. [P] clindata as above. | YAML, simulated parquet; clindata | high / low |
| (l) redistributing modified records | ALLOWED (gsm.*); UNCLEAR (clindata) | P6-B(b) | [C] Must mark modified files. | same | high / low |
| (m) including files inside an MIT repository | ALLOWED with conditions | P6-B | [C] Copied files remain Apache-2.0; they cannot be relicensed as MIT. Ship the Apache-2.0 text, keep notices, mark changes, and scope the repo's MIT statement to our own code (e.g. `third_party/gsm/LICENSE`). | any vendored file | high |
| (n) attribution and NOTICE requirements | ALLOWED (obligations apply) | P6-B(a)(c)(d) | No NOTICE file exists in any inspected repo, so (d) is currently empty; (a) and (c) still apply on redistribution. Mere invocation needs no attribution, but cite the packages. | — | high |
| (o) share-alike requirements | ALLOWED (none) | Apache-2.0 §4 final paragraph: "may provide additional or different license terms" for modifications | No copyleft. | — | high |
| (p) privacy, data protection, contractual restrictions | ALLOWED (code); UNCLEAR (clindata) | P6-C; P6-D | [T] No terms of use beyond the licence. Trademark: no right to use "Gilead"/"OpenRBQM"/"PHUSE" names beyond describing origin. [P] clindata unresolved. | — | medium |

Software-specific answers:
1. **Invoke as optional external dependency:** ALLOWED (P6-A). Practical only as an optional Rscript step.
2. **Vendor/copy its code:** ALLOWED under P6-B (licence copy, change notices, retained notices); files stay Apache-2.0.
3. **Publish outputs produced on our own synthetic data:** ALLOWED. If the HTML report bundles gsm JS/CSS, treat it as redistribution (P6-B).

Unresolved for source 6: (i) copyright holder is not stated in the LICENSE.md of gsm.kri/gsm.mapping/gsm.reporting/gsm.qtl/gsm.pd (template placeholder), though three of them list "Gilead Sciences" as `cph`; (ii) `workr` copyright holder is the literal string "Workr Maintainer"; (iii) `gsm.endpoints` not public; (iv) clindata synthetic-vs-anonymized conflict; (v) the 18+ transitive R dependencies of the gsm stack were not individually licence-audited.

---

## 7. CDISC CORE (CDISC Open Rules Engine) and rule libraries

### 7.1 What was inspected

| Artifact | Location | Version / commit | Licence file | Copyright line |
|---|---|---|---|---|
| CORE "pandas" engine | https://github.com/cdisc-org/cdisc-rules-engine | main `42028faf090c59bfdfba974779f64be2448bf5bb` (2026-11-09); release **v1.0.0** 2026-11-03 (tag `f3282a0d…`); `version.py`: `__version__ = "1.0.0"` | `LICENSE` — MIT (GitHub SPDX: MIT) | "Copyright (c) 2022 cdisc" |
| PyPI `cdisc-rules-engine` | https://pypi.org/pypi/cdisc-rules-engine/json | 1.0.0, uploaded 2026-11-03 (`cdisc_rules_engine-1.0.0-135-py3-none-any.whl`, 303,987 bytes) | `License: MIT`; wheel contains `dist-info/licenses/LICENSE` | author "cdisc-org" |
| CORE "SQL" engine (Verisian fork) | https://github.com/verisianHQ/cdisc-rules-engine | main `a8c00fc5dff065836e8e5211773ffa1ed0b4b0de` (2026-11-16); release **v1.0.0** 2026-11-03 (tag `4a734105…`) | `LICENSE` — MIT | "Copyright (c) 2022 cdisc"; pyproject authors "Verisian" |
| Rules (TIG/USDM/SEND; SDTM in `Deprecated/`) | https://github.com/cdisc-org/cdisc-open-rules | main `1881cb9a1f9a38b6cafc785eca5169b240981f66` (2026-11-12); no releases | `LICENSE` — MIT | "Copyright (c) 2026 cdisc" |
| Rules (SDTMIG 3.2/3.3/3.4 + FDA Business Rules) | https://github.com/cdisc-org/core-contributor (fork of verisianHQ/core-contributor) | main `94963e01df448f05bdbbc43a482661d4f30f7dac` (2026-11-06); no releases | `LICENSE` — MIT | "Copyright (c) 2025 verisian" |
| Library client | https://github.com/cdisc-org/cdisc-library-client | main `419d013f440716bf34c2480811f123dfbdecca2d` | MIT (GitHub SPDX) | not opened |

No `NOTICE` file in the engine repo (HTTP 404 at the inspected commit).

**The engine is split in two as of the verification date.** cdisc-org README (commit `42028faf`): "At present, rule validation is split across two engines while work is underway to merge the SQL fork back into this repository." Table in the same README: "SDTM or FDA Business Rules -> The refactored SQL Engine — verisianHQ/cdisc-rules-engine … Rules: cdisc-org/core-contributor"; "TIG, USDM, or SEND -> The CDISC Engine (this repository) … Rules: cdisc-org/cdisc-open-rules". The cdisc-open-rules README adds: "Currently, SDTM-only rules are housed in the Deprecated/ dir. … These rules may work, but their execution and data has not been fully validated".

Naming inconsistency to be aware of: https://www.cdisc.org/core/cdisc-open-rules calls the pandas engine "CORE V0.17.1" and the SQL engine "CORE V1.0, released 3 November 2026", while the cdisc-org repo itself also carries a `v1.0.0` release dated 2026-11-03 and PyPI serves 1.0.0. Which label CDISC intends for the pandas engine: UNCLEAR.

### 7.2 Governing provisions

- **P7-A (MIT, engine; https://github.com/cdisc-org/cdisc-rules-engine/blob/42028faf090c59bfdfba974779f64be2448bf5bb/LICENSE):** "Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software … subject to the following conditions: The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software."
- **P7-B (MIT, rule repositories):** same MIT text in `cdisc-org/cdisc-open-rules/LICENSE` ("Copyright (c) 2026 cdisc") and `cdisc-org/core-contributor/LICENSE` ("Copyright (c) 2025 verisian"). **The rule content is MIT in these repositories — not CC-BY-4.0; no CC licence was found anywhere.** No per-rule licence field exists in the rule YAML that was opened.
- **P7-C (CDISC web statement; https://www.cdisc.org/core/cdisc-open-rules):** "Provided as open source with the permissive MIT license"; "Available to users for free"; FAQ: "Yes. CORE is open source under the MIT License and registered with the CDISC Open-Source Alliance (COSA). CDISC does not offer CORE as a commercial product." Also: "CDISC Open Rules are released as packages by standard and standard version, and are published in CDISC Library."
- **P7-D (CDISC standards documents — "Terms and Conditions", https://www.cdisc.org/terms-and-conditions, "Copyright (c) 2014, CDISC All rights reserved."):** "User agrees to limit access to this download for use within your organization only." "You are hereby granted a nonexclusive, worldwide, perpetual, compensation-free, non- transferable, non-sublicensable license to reproduce, publish, display, and use this standard solely within Your Organization for the purpose of promoting the standard." "For the avoidance of doubt, the foregoing license grant does not include the right to (i) translate or create derivative works of the Material, or (ii) internally or externally copy, distribute, or post to a Web page." Scope stated on the page: "CDISC standards in document format".
- **P7-E (CDISC Policy 003 — Intellectual Property, v3, approved 21 August 2024; https://www.cdisc.org/sites/default/files/2024-08/CDISC%20Policy%20003%20-%20Intellectual%20Property%202024%20FINAL.pdf):** §4.1 "CDISC shall own the copyright in Final Standards"; §4.2 CDISC grants "a nonexclusive, compensation-free, non-transferable, non-sublicensable, worldwide, perpetual, copyright license to reproduce, publish, display, perform, and distribute the Final Standard pursuant to the license terms provided on CDISC website for each format of the Final Standard offered by CDISC"; §2.5 "'Final Standard' means any CDISC standard, in any version and in any format"; §9.1 "No Other Licenses."
- **P7-F (CDISC brand; "2025 CDISC Communications Policy for External Stakeholders", §2; https://www.cdisc.org/sites/default/files/2025-11/CDISC%20Communications%20Policy%202025%20%281%29.pdf):** "External use of the CDISC Brand including the CDISC logo, CDISC elements, and the word "CDISC" or images, must be approved by the CDISC Communications Team. Use of the CDISC logo, CDISC elements, and word "CDISC" are protected by U.S. Trademark Law and should not be used by an external party without the express consent and guidance of CDISC Communications. Reproduction of any logos or symbols is prohibited without the approval of CDISC Communications. For licensing information, please contact [email removed]"
- **P7-G (API key / cache; engine docs at commit `42028faf`, `docs/faq.md` and `docs/cli-reference.md`):** "An API key is required for controlled terminology and library metadata. **Rules are accessible without a key.** Running `update-cache` without a key will still populate conformance rules." `docs/PYPI.md`: "Installing the package alone is not enough to run validations. You also need: 1. **The rules cache** — download the contents of `resources/cache/` from the repository … 2. **A CDISC Library API key** — required for controlled terminology and library metadata." Also: "This installs the engine underlying the CLI and executable, but **does not include `core.py`** or the CLI entrypoints."
- **P7-H (CDISC Library access; https://www.cdisc.org/cdisc-library):** "CDISC Library is available to all employees of our Member Organizations as well as non-members." "an API Key (found on the API Management Developer Portal) is required to access the API."

**CDISC Library EULA / API terms of use: COULD NOT VERIFY.** Attempts: `cdisc.org/cdisc-library/eula`, `/eula`, `/cdisc-library-eula`, `/cdisc-library/terms`, `/cdisc-library/api-eula`, `/cdisc-library/license`, `/legal`, `/terms`, `/terms-use` (all HTTP 404); `wiki.cdisc.org/display/LIBSUPRT/Getting+Started…` (HTTP 403); `api.developer.library.cdisc.org` sign-in/sign-up pages (no terms text exposed without login); the Data Standards Browser JS bundle (no "EULA"/"terms of use" strings); two web searches. The only evidence that a EULA exists is a CDISC slide deck (https://www.cdisc.org/sites/default/files/2022-11/2022-US-Interchange-Sam%20Hume.pdf): "Updated Library EULA" and "New EULA makes it easier for open-source software developers" — which says nothing about what is permitted. The EULA is presumably shown at cdiscID / API-key sign-up. **Until someone reads it, commercial use of the API, caching, and redistribution of Library content (controlled terminology, standards metadata, rule packages as served by the API) must be treated as not cleared.**

**A standalone CDISC trademark policy page: COULD NOT VERIFY** (`/trademarks`, `/trademark-policy`, `/about/trademarks` all 404). P7-F is the only primary brand statement found.

### 7.3 Is rule content bundled?

- **PyPI wheel: no.** The 1.0.0 wheel was downloaded and listed: 273 entries; the only `resources/` files are `resources/schema/USDM.yaml`, `resources/schema/dataset-ndjson-schema.json`, `resources/schema/dataset.schema.json`. No `.pkl` cache, no rules. `MANIFEST.in` confirms (`include resources/schema/…`, `recursive-include resources/jsonata`).
- **Git repository: yes.** `resources/cache/` at commit `42028faf` holds 223 files, 501,458,129 bytes: `rules.pkl` (2.47 MB), `rules_dictionary.pkl`, `standards_details.pkl` (23 MB), `standards_models.pkl` (6.6 MB), `variables_metadata.pkl` (13.8 MB), `variable_codelist_maps.pkl`, `usdm-3-0-schema.pkl`, `usdm-4-0-schema.pkl`, plus ~215 controlled-terminology packages (`sdtmct-*.pkl`, `adamct-*.pkl`, `cdashct-*.pkl`, …). The Verisian fork's `resources/cache` is 221 files / 585,926,638 bytes; its README: "The rules, controlled terminology and other standards metadata come with the repository".
- **Release executables: yes.** `docs/quick-start.md`: "Executable releases ship with a pre-populated cache".
- These cache files sit in MIT-licensed repositories published by CDISC itself, but they are serialised CDISC Library content (standards metadata and controlled terminology). Whether the repo's MIT licence is intended to cover that content, or whether the Library EULA / P7-D govern it, is **UNCLEAR**. The `.pkl` files were not unpickled (untrusted pickle), so their exact content was not examined.
- Rule YAML files embed verbatim excerpts of CDISC standards under `Cited Guidance:` (example, `core-contributor/sdtm_rules/CORE-000001/CG0176,TIG0405.….yml`: "Cited Guidance: The intent of the domain model is to collect responses to only those criteria that the subject did not meet, and not the responses to all criteria. / Document: IG v3.4 / Item: Assumption 1 / Section: '6.3.4'"). CDISC publishes these excerpts itself under MIT in the rule repos; copying a rule file therefore rests on P7-B. Copying further SDTMIG text directly from the standard documents rests on P7-D and is not covered.

### 7.4 Python / offline / dataset-format facts

- **Python:** `pyproject.toml` (both engines): `requires-python = ">=3.12, <3.13"`. PyPI metadata: `Requires-Python: <3.13,>=3.12`. FAQ: "Python 3.12 is required. Other versions are not supported". Compatible with a Python 3.12 uv project; **incompatible with 3.13+**.
- **Dependency pins that can collide with our project (cdisc-org pyproject at `42028faf`):** `pandas >=3.0.0`, `numpy >=1.26.0`, `dask[dataframe,array] >=2025.4.0`, `jsonpath-ng >=1.8.0,<1.11`, `pyinstaller >=6.11.0` (listed as a runtime dependency), `redis >=4.5.0`, `setuptools >=75.6.0`. The Verisian fork's `requirements.txt` instead pins `pandas==2.1.4`, `numpy~=1.26.0`, `dask==2024.6.0`, and adds `psycopg2-binary==2.9.10`, `pgserver==0.1.4`, `pyarrow==24.0.0`. The two engines cannot share one environment. Recommendation: run either engine in its own isolated environment (separate `uv` environment / `uv tool` / downloaded executable) and call it by subprocess; do not add it to the main dependency set.
- **Dependency licences (PyPI metadata, fetched 2026-11-16; latest-version metadata, not the exact resolved versions):** business-rules-enhanced MIT; cachetools MIT; cdisc-library-client (PyPI licence field empty; GitHub repo MIT); click BSD-3-Clause; dask BSD-3-Clause; fastparquet Apache-2.0; importlib-metadata Apache-2.0; jsonata-python Apache-2.0; jsonpath-ng Apache-2.0; jsonschema MIT; lxml BSD-3-Clause; numpy "BSD-3-Clause AND 0BSD AND MIT AND Zlib AND CC0-1.0"; odmlib MIT; openpyxl MIT; pandas BSD-3-Clause; psutil BSD-3-Clause; **pyinstaller "GPLv2-or-later with a special exception which allows to use PyInstaller…"**; pympler Apache-2.0; pyreadstat Apache-2.0; python-dotenv BSD-3-Clause; pytz MIT; pyyaml MIT; redis MIT; requests Apache-2.0; setuptools MIT; titlecase MIT. Verisian fork extras: **psycopg2-binary "LGPL with exceptions"**; pgserver (PyPI licence field empty; GitHub `orm011/pgserver` detected Apache-2.0; it bundles PostgreSQL binaries — their licence was not checked); pyarrow Apache-2.0. Implication: nothing here restricts *invoking* the tool; GPL/LGPL components matter only if we redistribute a bundle containing them (we should not). Transitive dependencies were not audited.
- **Formats:** cdisc.org FAQ: "For data validation, CORE V1.0 accepts SAS V5 XPT and define.xml. CORE V0.17.1 accepts SAS V5 XPT and define.xml, Dataset-JSON, Dataset-NDJSON, USDM JSON, Excel, and CSV. Both versions produce reports in Excel and JSON, and CORE V0.17.1 also produces them in CSV." Verisian README: "The engine validates XPT and SAS7BDAT files …; files in other formats, such as Dataset-JSON, are skipped with a warning."
- **Offline:** yes in principle once a cache is present on disk (cache ships in the repo and executables; `-ca/--cache` flag; `-lr/--local-rules` runs local YAML/JSON rules; custom-rule commands "don't need a CDISC Library API key"). `update-cache` contacts `api.library.cdisc.org:443`. The SQL engine needs PostgreSQL but self-provisions: "when the engine finds no `DATABASE_*` settings … it creates a temporary database for each run and deletes it at the end" (via `pgserver`). Warning quoted from the same README for the Docker option: "it **deletes the tables in that database's `public` schema**".
- **Could it validate small synthetic DM/DS/IE datasets?** Plausibly yes, by two routes, **neither executed here (COULD NOT VERIFY at runtime)**: (1) SQL engine v1.0.0 from a source clone with XPT inputs (`python core.py validate -s sdtmig -v 3-4 -d path/to/datasets`) — the route CDISC designates for SDTM; (2) pandas engine with Dataset-JSON/CSV/XLSX inputs, but SDTM-only rules for that engine are in `Deprecated/` and "not fully validated". Whether the pandas engine's shipped `rules.pkl` still contains SDTMIG rules: COULD NOT VERIFY.
- **Relevant rule content (GitHub code search on `verisianHQ/core-contributor`, `path:sdtm_rules`):** 8 rule files mention `RFICDTC` (e.g. CORE-000086 CG0075, CORE-000363 CG0068, CORE-000370 CG0143, CORE-000658 FB3412, CORE-000713 FB3411, CORE-002087 FB3414, CORE-002115 FB1113, CORE-002121 CG0011); 7 mention "INFORMED CONSENT"; 12 mention `IETESTCD` (e.g. CORE-000001 CG0176, CORE-000011 CG0175, CORE-000025 CG0177, CORE-000228 CG0179, CORE-000145 CG0255, CORE-000146 CG0256, CORE-002110 CG0254, CORE-002112 CG0253); 22 mention "SCREEN FAILURE". **[S]** These are standards-conformance rules (is the dataset structured per SDTMIG / FDA business rules), not checks that a subject was actually eligible or validly consented; they complement but do not constitute enrollment/consent issue triage. Synthetic "SDTM-like" data that is not strictly SDTMIG-conformant will raise many unrelated findings.

### 7.5 Use matrix — CDISC CORE ("records" = rule YAML + test data in the MIT repos, and separately the Library-derived cache / standards text)

| Use | Classification | Provision | Explanation | Artifacts | Confidence / open questions |
|---|---|---|---|---|---|
| (a) commercial-company research use | ALLOWED (engine, rule repos); UNCLEAR (CDISC Library API under a key) | P7-A, P7-B, P7-C; EULA unverified | [C] MIT, "Available to users for free". [T] API-key use is governed by an unread EULA. | engine, rule YAML; API | high / low |
| (b) internal processing | ALLOWED | P7-A, P7-B; P7-D permits use "solely within Your Organization" | [C] Internal use is covered by every instrument read. | all | high |
| (c) processing through external AI APIs | ALLOWED (our data, engine output, MIT rule YAML); UNCLEAR (cache `.pkl` content, API responses); REQUIRES PERMISSION (CDISC standards document text) | P7-B; EULA unverified; P7-D | [C] MIT rule text may be copied to third parties. [T] Library content terms unread. [C] Standards documents are licensed for use "solely within Your Organization" and exclude copying/distribution. | rule YAML; `resources/cache/*`; SDTMIG PDFs/HTML | medium |
| (d) publishing aggregate benchmark metrics | ALLOWED | P7-A | Counts of findings on our own data are our own output. | ours | high |
| (e) publishing charts/visualizations | ALLOWED; REQUIRES PERMISSION if the CDISC/CORE logo is shown | P7-A; P7-F | [T] Logo/brand use needs CDISC Communications approval. | charts; `docs/CORE_logo_sm.png`, `resources/assets/*` | high |
| (f) publishing transformed or reconstructed records | ALLOWED (rule YAML/test data from the MIT repos, with MIT notice); UNCLEAR (cache/Library content); PROHIBITED without permission (derivatives of standards documents) | P7-B; EULA unverified; P7-D "(i) translate or create derivative works of the Material" | As stated. | as above | medium |
| (g) publishing per-case inputs and model predictions | ALLOWED | P7-A, P7-B | Inputs are ours. Engine reports reproduce rule IDs/messages/descriptions originating in MIT rule files — keep the MIT notice if rule text is reproduced at scale. | CORE report JSON/XLSX on our data | medium (assumes report text comes only from the MIT rule files) |
| (h) publishing cached API responses | UNCLEAR — treat as not permitted | EULA COULD NOT VERIFY; P7-D by analogy | [T] The Library API terms were not obtainable. Do not commit `resources/cache/*.pkl`, CT packages, or raw Library API JSON to our repo. | `resources/cache/**`, any `api.library.cdisc.org` response | low — must read the EULA or ask CDISC |
| (i) publishing prompts or quoted source text | ALLOWED (text from MIT rule files, with attribution); REQUIRES PERMISSION (text taken from CDISC standards documents) | P7-B; P7-D | [C] The page-level licence for standards excludes distribution and web posting; any reliance on quotation exceptions is a legal judgment outside the licence. | rule `Cited Guidance`, descriptions; SDTMIG text | medium |
| (j) publishing trained models or derived artifacts | ALLOWED (derived from MIT code/rules or our data); UNCLEAR (derived from Library content or standards documents) | P7-A/B; P7-D; EULA unverified | As stated. | — | low-medium |
| (k) redistributing original records | ALLOWED (rule YAML + test data from the MIT repos, with notice); UNCLEAR (cache/Library content) | P7-B; EULA unverified | [C] MIT requires the copyright + permission notice. | `cdisc-open-rules/Published/**`, `core-contributor/sdtm_rules/**` | medium — test-data XLSX files were not opened; their provenance was not checked |
| (l) redistributing modified records | ALLOWED (MIT repos); UNCLEAR (cache/Library content) | P7-B | Modified copies must not be presented as official CDISC rules (see P7-F). | same | medium |
| (m) including files inside an MIT repository | ALLOWED (engine code, rule YAML — same licence; keep CDISC/Verisian copyright notices); UNCLEAR (cache); REQUIRES PERMISSION (logo) | P7-A, P7-B; P7-F | MIT-to-MIT is compatible but the original notice must travel with the copied files. | — | high / low |
| (n) attribution and NOTICE requirements | ALLOWED (obligations apply) | MIT: "The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software." | No NOTICE file. Needed only if we copy code/rules; invocation alone triggers nothing. | — | high |
| (o) share-alike requirements | ALLOWED (none) | MIT | No copyleft in the engine or rule repos. (pyinstaller GPL / psycopg2 LGPL are dependencies we would not redistribute.) | — | high |
| (p) privacy, data protection, contractual restrictions | UNCLEAR (Library EULA); REQUIRES PERMISSION (CDISC name/logo in branding) | EULA unverified; P7-F | [P] No personal data in the tool or rules; the engine runs locally, so our data is not sent to CDISC during `validate` (not verified by network trace). [T] API key is tied to a cdiscID account. Brand: do not name the benchmark with "CDISC"/"CORE", use no logo, claim no certification or endorsement; factual references ("validated with CDISC CORE v1.0.0") are the minimum necessary use — the policy text itself asks for consent even for the word "CDISC", so confirm with [email removed] if the name is used prominently. | — | low-medium |

Software-specific answers:
1. **Invoke as optional external dependency:** ALLOWED (MIT). Use an isolated environment or the release executable. Prefer the route that needs **no API key** (shipped cache / rules-only update) so that the unverified EULA is not triggered.
2. **Vendor/copy its code:** ALLOWED for engine source and rule YAML with the MIT notice. Do **not** vendor `resources/cache`, CT packages, or logos.
3. **Publish outputs on our own synthetic data:** ALLOWED.

Unresolved for source 7: CDISC Library EULA text; whether MIT covers the repo-hosted cache; standalone trademark policy; which engine/version CDISC will designate once the fork is merged back; runtime behaviour on our data; licences of pgserver's bundled PostgreSQL binaries and of transitive dependencies; provenance of rule test data.

---

## 8. pharmaverse sdtmchecks

### 8.1 Facts

- Repo: https://github.com/pharmaverse/sdtmchecks — default branch `devel`, HEAD `fb35f8b33adc3548c2b1531fab1f65a7e8360492` (2024-12-14), DESCRIPTION `Version: 1.0.0.01`. `main` branch `cb2e726027f2c2fcb5916bfe7a5546410199c9ad` (2024-09-05), `Version: 1.0.0`. Latest GitHub *release* object is v0.1.11 (2024-05-22) — stale relative to CRAN.
- CRAN: `sdtmchecks` 1.0.0, published 2024-07-12, `License: Apache License (>= 2)`. No commits since 2024-12-14 (maintenance appears slow).
- Licence: `LICENSE.md` = Apache License 2.0 (no plain `LICENSE`, no `NOTICE` — both 404). GitHub SPDX: Apache-2.0. Appendix line: "Copyright 2024 F. Hoffmann-La Roche AG".
- Copyright holder: DESCRIPTION `person(given="F. Hoffmann-La Roche AG", role = c("cph", "fnd"))`; maintainer Will Harris (gene.com address, i.e. Genentech/Roche).
- R dependency: `Imports: dplyr (>= 1.1.1), tidyselect, openxlsx` (CRAN metadata: all three "MIT + file LICENSE"). Suggests knitr, rmarkdown, testthat, DT. A minimum R version is not declared in DESCRIPTION.
- Bundled data: only `data/sdtmchecksmeta.RData` (12,995 bytes; "A dataset containing the SDTM checks in the package" — one row per check: check, category, priority, domains, titles…) and `data/nickname.RData` (71 bytes). **No patient-level or sample clinical data is bundled.** Rights: same Apache-2.0 as the package.
- Provisions: identical Apache-2.0 text to P6-A / P6-B / P6-C (source: https://github.com/pharmaverse/sdtmchecks/blob/fb35f8b33adc3548c2b1531fab1f65a7e8360492/LICENSE.md).

### 8.2 Real function names (from `R/` at `fb35f8b3`) relevant to DM / DS / IE / consent / eligibility / enrollment

- **IE: none.** There is no `check_ie_*` function in the package. No inclusion/exclusion-criteria check exists.
- **Consent:** `check_ts_sstdtc_ds_consent` — "Check for missing SSTDTC (Study Start Date) in TS; if it's present, check that the date matches the earliest informed consent among any subject enrolled in the study." Inputs: TS (`TSPARMCD, TSPARM, TSVAL`), DS (`DSCAT, DSSCAT, DSDECOD, DSSTDTC`). This is the only consent-related check, and it is a study-level date consistency check.
- **Eligibility (name only):** `check_sc_dm_eligcrit` — "Check SC Eye Meeting Eligibility Criteria assignments among DM patients" (ophthalmology study-eye selection: SC.SCTESTCD = "ELIGEYE"); not protocol I/E eligibility.
- **DM:** `check_dm_actarm_arm`, `check_dm_ae_ds_death`, `check_dm_age_missing` ("missing AGE, AGE<18 or AGE>90"), `check_dm_armcd`, `check_dm_dthfl_dthdtc`, `check_dm_usubjid_ae_usubjid`, `check_dm_usubjid_dup`.
- **DS:** `check_ds_ae_discon`, `check_ds_dsdecod_death`, `check_ds_dsdecod_dsstdtc`, `check_ds_dsscat` ("more than one study discontinuation records"), `check_ds_dsterm_death_due_to`, `check_ds_duplicate_randomization` ("duplicate randomization records for a patient"), `check_ds_ex_after_discon`, `check_ds_multdeath_dsstdtc`, `check_ds_sc_strat` ("randomized patients are missing stratification factor data").
- **Protocol deviations (DV):** `check_dv_ae_aedecod_covid`, `check_dv_covid` (COVID-19-specific only).
- Cross-domain involving DM/DS: `check_ae_aeacnoth_ds_disctx`, `check_ae_aeacn_ds_disctx_covid`, `check_ae_aeacnoth_ds_stddisc_covid`, `check_ae_aedthdtc_ds_death`, `check_ae_death_ds_discon`, `check_ae_ds_partial_death_dates`, `check_ae_withdr_ds_discon`, `check_dd_ae_aedthdtc_ds_dsstdtc`, `check_ss_ssdtc_alive_dm`, `check_ss_ssdtc_dead_ds`.
- Runners: `run_all_checks`, `run_check`. Total exported check files: ~110 (AE, CE, CM, DD, DM, DS, DV, EC, EG, EX, LB, MH, MI, OE, PR, QS, RS, SC, SS, TR, TS, TU, VS).
- **[S]** Coverage for our topic is thin: one consent-date check, a duplicate-randomization check, basic DM sanity checks. The package is oriented to oncology/ophthalmology analysis-readiness.

### 8.3 Use matrix — sdtmchecks ("records" = `sdtmchecksmeta` metadata table and package docs)

| Use | Classification | Provision | Explanation | Confidence |
|---|---|---|---|---|
| (a) commercial-company research use | ALLOWED | Apache-2.0 §2 (P6-A text) | [C] No field-of-use limit. | high |
| (b) internal processing | ALLOWED | §2 | — | high |
| (c) processing through external AI APIs | ALLOWED | §2 | [C] Code and metadata may be reproduced; no patient data is bundled, so no [P] issue. | high |
| (d) publishing aggregate benchmark metrics | ALLOWED | §2 | Output on our own data. | high |
| (e) publishing charts/visualizations | ALLOWED | §2 | — | high |
| (f) publishing transformed or reconstructed records | ALLOWED | §2, §4(b) | Metadata table may be transformed; mark changes. | high |
| (g) publishing per-case inputs and model predictions | ALLOWED | §2 | Our data; check messages originate from Apache-2.0 code. | high |
| (h) publishing cached API responses | ALLOWED (not applicable) | — | No API. | high |
| (i) publishing prompts or quoted source text | ALLOWED | §2, §4 | Quote roxygen descriptions with attribution. | high |
| (j) publishing trained models or derived artifacts | ALLOWED | §2 | — | medium |
| (k) redistributing original records | ALLOWED | §4(a)(c) | Include licence, keep notices. | high |
| (l) redistributing modified records | ALLOWED | §4(b) | Mark modifications. | high |
| (m) including files inside an MIT repository | ALLOWED with conditions | §4 | Files remain Apache-2.0; ship licence text; state changes. Re-implementing a check's *logic* in Python from the documentation is not copying the R code, but a line-by-line port is a derivative work -> treat as Apache-2.0. | high |
| (n) attribution and NOTICE requirements | ALLOWED (obligations apply) | §4(a)(c)(d) | No NOTICE file exists. | high |
| (o) share-alike requirements | ALLOWED (none) | §4 final paragraph | — | high |
| (p) privacy, data protection, contractual restrictions | ALLOWED | §6 (P6-C text) | No terms of use, no personal data. No right to use Roche/Genentech/pharmaverse marks beyond describing origin. | high |

Software-specific: (1) invoke as optional external dependency — ALLOWED; easiest of the R tools (on CRAN: `install.packages("sdtmchecks")`, three light dependencies; call `Rscript` with data frames read from CSV/XPT). (2) vendor/copy — ALLOWED under Apache-2.0 §4. (3) publish outputs on our synthetic data — ALLOWED.

Unresolved: none material. Minimum R version not declared; runtime not executed here.

---

## 9. IMPALA Clinical Timeseries Anomaly Spotter (CTAS)

(The README title is "Clinical Timeseries Anomaly Spotter (CTAS)".)

### 9.1 Facts

- Repo: https://github.com/IMPALA-Consortium/ctas — main `94c9f061225e30a5ab0145a25991b068bd4e649f` (2026-10-19). DESCRIPTION `Version: 0.4.0`; tags v0.4.0 (`355a0141…`), v0.3.0, v0.2.1, v0.2.0; the GitHub "latest release" object is v0.3.0 (2024-12-12). Not on CRAN (404).
- Licence: DESCRIPTION `License: MIT + file LICENSE`. `LICENSE` (R stub): "YEAR: 2024 / COPYRIGHT HOLDER: Bayer". `LICENSE.md`: "MIT License / Copyright (c) 2024 Bayer" followed by the standard MIT text. GitHub API reports `NOASSERTION` only because the root `LICENSE` is the two-line R stub. SPDX: **MIT**.
- Copyright holder: "Bayer" (LICENSE) / `person("Bayer Pharmaceuticals", role = "cph")` (DESCRIPTION). Authors: Pekka Tiikkainen (bayer.com), Björn Koneswarakantha (roche.com). No NOTICE file.
- What it does (README): "CTAS is an R package for identifying outliers and anomalies in clinical trial time series. Its main focus is on flagging sites with one or more study parameters whose profiles differ from those of the other sites. However, also anomalies for individual subjects can be identified". "data preparation step is intentionally out-of-scope for the package". Main function `process_a_study(data, subjects, parameters, custom_timeseries, custom_reference_groups, …)`; inputs are long-format numeric results per subject x timepoint x parameter plus a subjects table (`subject_id, site, country, region`).
- Bundled data: `data/ctas_data.rda` (41,027 bytes), documented in `R/data.R` as "Simulated input data to pass to process_a_study"; generated by `data-raw/ctas_data.R` (`set.seed(1)`, `rpois`-based synthetic regions/countries/sites/subjects). No real patient data. Covered by the package MIT licence.
- Also in the repo root: `CTAS Phuse EU Connect paper.pdf` and `CTAS Phuse EU Connect presentation.pdf`. No licence statement specific to these PDFs was found; whether the MIT licence is meant to cover them (and whether PHUSE holds rights) is UNCLEAR. The PDFs were not opened.
- Dependencies: `Depends: dplyr, R (>= 3.5.0)`; `Imports: dbscan, rlang, stringr, tidyr, lme4, merTools`. CRAN metadata: **lme4 "GPL (>= 2)", merTools "GPL (>= 2)", dbscan "GPL (>= 3)"**; dplyr MIT. Invoking CTAS in a separate R process does not affect our MIT repo; bundling CTAS together with these libraries would be GPL-governed distribution.
- Provision **P9-A** (https://github.com/IMPALA-Consortium/ctas/blob/94c9f061225e30a5ab0145a25991b068bd4e649f/LICENSE.md): "Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software … The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software."

### 9.2 Suitability

**[S]** CTAS needs repeated numeric measurements over time per subject (labs, vitals) across several sites. It has no concept of enrollment, screening, eligibility criteria, consent or protocol deviations. It does not match a subjects/sites/enrollment/consent/eligibility dataset unless we also synthesise longitudinal numeric series. **Conclusion: suitable only as an optional future experiment**, not for the core benchmark. Licence-wise there is no obstacle.

### 9.3 Use matrix — CTAS ("records" = `ctas_data` simulated dataset)

| Use | Classification | Provision | Explanation | Confidence |
|---|---|---|---|---|
| (a) commercial-company research use | ALLOWED | P9-A | [C] "without restriction". | high |
| (b) internal processing | ALLOWED | P9-A | — | high |
| (c) processing through external AI APIs | ALLOWED | P9-A | Simulated data and code only; no [P] issue. | high |
| (d) publishing aggregate benchmark metrics | ALLOWED | P9-A | — | high |
| (e) publishing charts/visualizations | ALLOWED | P9-A | — | high |
| (f) publishing transformed or reconstructed records | ALLOWED | P9-A | "modify, merge, publish". | high |
| (g) publishing per-case inputs and model predictions | ALLOWED | P9-A | Our data. | high |
| (h) publishing cached API responses | ALLOWED (not applicable) | — | No API. | high |
| (i) publishing prompts or quoted source text | ALLOWED (README/code); UNCLEAR (text from the two PHUSE PDFs) | P9-A | PDFs carry no stated licence. | high / low |
| (j) publishing trained models or derived artifacts | ALLOWED | P9-A | — | medium |
| (k) redistributing original records | ALLOWED (with MIT notice); UNCLEAR (PHUSE PDFs) | P9-A | — | high / low |
| (l) redistributing modified records | ALLOWED | P9-A | — | high |
| (m) including files inside an MIT repository | ALLOWED | P9-A | Same licence; keep "Copyright (c) 2024 Bayer" notice with copied files. Do not include the PDFs. | high |
| (n) attribution and NOTICE requirements | ALLOWED (obligation: keep copyright + permission notice in copies) | P9-A | No NOTICE file. | high |
| (o) share-alike requirements | ALLOWED (none for CTAS itself) | P9-A | GPL applies to lme4/merTools/dbscan if we redistribute them — we should not. | high |
| (p) privacy, data protection, contractual restrictions | ALLOWED | P9-A | No terms of use, no personal data. No right to use Bayer/IMPALA names for endorsement (MIT grants no trademark rights). | high |

Software-specific: (1) invoke as optional external dependency — ALLOWED (GitHub install only; Rscript subprocess). (2) vendor/copy — ALLOWED with MIT notice. (3) publish outputs on our synthetic data — ALLOWED.

---

## 10. Project Data Sphere (PDS) — potential FUTURE source only

### 10.1 Documents obtained

- `https://www.projectdatasphere.org/` 301-redirects to `https://data.projectdatasphere.org/` (a JavaScript single-page app). Its bundle (`/static/js/main.7743efb9.js`, fetched 2026-11-16) lists the Resources documents: "PDS Platform Use Agreement" -> `/documents/resources_data_user_agreement.pdf`; "PDS Data Sharing Agreement" -> `/documents/resources_data_sharing_agreement.pdf`.
- **User agreement:** https://data.projectdatasphere.org/documents/resources_data_user_agreement.pdf — 12 pages, PDF created 2020-05-14, headed "**Cancer Research Platform Agreement (v. May 13, 2020)**" (md5 `ca8e174eb151cce78b25cf552b05841f`). The site FAQ calls it the "Online Services User Agreement": "All new users enter into an Online Services User Agreement with PDS. Additionally, all data providers enter into a Data Sharing Agreement for each data provision." **Whether the click-through text shown at registration today is identical to this posted PDF: COULD NOT VERIFY** (registration not performed).
- **Data Sharing Agreement** (provider-side; 19 pages, PDF created 2020-12-15, md5 `1a13d72e521aec740de165b831d1c09e`) — binds data providers, not users; it embeds the user agreement as an exhibit. Skimmed only.
- Site FAQ (from the same bundle): "This platform is available to anyone who applies for access."; "Typically, new user requests are approved within 24hrs. … All user requests are approved once verified that the user isn't subject to certain geographical or limited regulatory restrictions."; "Once registered, you will have access to all data on the platform with exception of data provided by the National CancerInstitute (NCI). … This approval process goes through the NCI."; "Once your new user request is approved you will have access to the platform for one year."; "Will users be required to submit research results? No! However, PDS encourages users to publish … Users are required to acknowledge Project Data Sphere in their publications or presentat[ions]".
- Website Terms of Use (public portions, from the bundle): "Project Data Sphere invites you to view, use and download a single copy of the publicly accessible portions of this website for your informational, non-commercial use." and "Except for your informational, personal, non-commercial use as authorized above, you may not modify, reproduce or distribute any content that is accessible on this website without written authorization by Project Data Sphere."

### 10.2 Governing provisions (verbatim from the Cancer Research Platform Agreement v. May 13, 2020)

- **P10-A (I, eligibility/purpose):** "Access to the Platform will be provided to bona fide researchers who submit a completed online application and agree to the terms … upon receiving access authorization from Project Data Sphere". "the term "research" means "one or more systematic investigations, each including research development, testing and evaluation, and designed to develop or contribute to generalizable knowledge.""
- **P10-B (III.A(i), licence):** "a non-exclusive, revocable, limited, non-transferable, non-sublicensable license to use the Platform only for purposes of accessing and using Data for one or more systematic investigations that you conduct, including research, development, testing and evaluation designed to develop or contribute to generalizable knowledge **in the field of cancer research** (the "Purpose")".
- **P10-C (III.A(ii), supplemental terms):** "You are expressly prohibited from copying … any Data that is identified to you as non-downloadable." Data "(including but not necessarily limited to data made available through the Platform by the National Cancer Institute) is subject to additional terms … ("Supplemental Terms")".
- **P10-D (III.B(i), re-identification):** "You may not use the Platform or any component thereof, either alone or in concert with any other information, to identify or contact individuals whose protected information may have been instrumental in developing the Data."
- **P10-E (III.B(ii), third parties / publication of Data):** "the Platform is for your personal use and … except as permitted by Articles IV, VII and VIII, you are prohibited from disclosing any portion of the Data available through the Platform to, or otherwise sharing any portion of the Data with, any third party. You may not publish the Data in any news release, article, manuscript, blog, website or any other release except as permitted by Article IV, Article VII and Article VIII. If disclosure of any Data is necessary for completion of your research, you may disclose such Data to a third party only after that third party has submitted a completed online application to be an Authorized User …, has agreed to the terms, covenants and conditions in this Agreement, and has received access authorization from Project Data Sphere."
- **P10-F (III.B(iii)–(vi), compliance/security):** compliance with "all data protection laws and regulations applicable to protected health information or other personally identifiable information"; "You are responsible for obtaining review and approval of research … by an Ethics Committee or Institutional Review Board, if and as required"; "You shall keep the Data in secure storage"; "promptly report to Project Data Sphere any unauthorized Data sharing, breach of Data security, inadvertent Data release … within 24 hours".
- **P10-G (III.C(i)–(ii), individual access):** "Only you may access the Platform. You shall not allow any other person to have access to the Platform or your password." "You shall not: use the Platform for any purpose other than the Purpose".
- **P10-H (V.A, ownership):** "each Data Provider retains ownership of, and all intellectual property rights in, the Data … you acquire no rights in the Data other than those limited rights set forth in this Agreement."
- **P10-I (VI.A, patents):** "you will not seek … patent protection in any jurisdiction for any research procedure or research design that results from your use of the Data"; non-assertion against Data Providers; licence-back to the trial's pharmaceutical "Collaborator" for inventions.
- **P10-J (VII, publications):** "You are encouraged to publish any results of your research in any peer-reviewed publication, and to report the results of your research in any presentation, provided that your publication or presentation does not disclose any Data or User Contributions other than Data or User Contributions that are reasonably necessary to publish or report your research results. You agree to include the following acknowledgment …: "This [publication or presentation, as applicable] is based on research using information obtained from www.projectdatasphere.org, which is maintained by Project Data Sphere. Neither Project Data Sphere nor the owner(s) of any information from the web site have contributed to, approved or are in any way responsible for the contents of this [publication or presentation].""
- **P10-K (VIII, confidentiality):** "the Data is nonpublic information that is proprietary to the Data Providers … you shall: (i) maintain the Data in strict confidence: (ii) not, directly or indirectly, disclose, or permit the disclosure of, the Data other than in accordance with Section III.B(2), Article VII or this Article VIII; and (iii) not use the Data for any purpose other than the Purpose."
- **P10-L (X, XII, term/destruction):** agreement "shall expire one (1) year after" the effective date unless renewed; on termination for breach "you shall promptly destroy all copies of the Data"; Data Providers may have Data removed.
- **P10-M (XVIII, publicity) and VI.B:** "The words "Project Data Sphere" and the following Project Data Sphere logo are registered trademarks"; "Except for the attribution required by Article VII, neither party will use any trademark, service mark, trade name, or other name or logo of the other party … for promotional or advertising purposes … without permission".
- **P10-N (II, XIII–XIV, enforcement):** Data licensors are third-party beneficiaries with the right to enforce; injunctive relief; user indemnity.

### 10.3 Use matrix — Project Data Sphere

| Use | Classification | Provision | Explanation | Confidence / open questions |
|---|---|---|---|---|
| (a) commercial-company research use | REQUIRES PERMISSION | P10-A, P10-B; FAQ "available to anyone who applies" | [T] No clause in the user agreement excludes commercial entities, but access needs an approved application per individual, and the licensed Purpose is confined to generalizable knowledge "in the field of cancer research". A general clinical-trial eligibility/consent triage benchmark is not obviously cancer research — the application must describe the research and PDS must authorize it. The patent covenants (P10-I) bind a commercial user. | medium — whether our purpose qualifies must be asked of PDS |
| (b) internal processing | REQUIRES PERMISSION | P10-G, P10-E | [T] Access is personal: every colleague who touches Data must be an individually Authorized User. Secure storage, 24-hour incident reporting, one-year term. | high |
| (c) processing through external AI APIs | PROHIBITED | P10-E, P10-K | [T] Sending Data to an external model provider is disclosure to a third party that is not an Authorized User; Data must be held "in strict confidence". Only self-hosted/local processing by Authorized Users fits the agreement. | high |
| (d) publishing aggregate benchmark metrics | ALLOWED (with mandatory acknowledgment) | P10-J | [T] Results publication is encouraged provided no Data is disclosed beyond what is "reasonably necessary". Aggregate metrics disclose no Data. Small-cell aggregates could still enable identification -> see P10-D. | medium-high (wording targets "peer-reviewed publication" and "presentation"; a public report/GitHub README is not expressly named) |
| (e) publishing charts/visualizations | ALLOWED (aggregate charts, with acknowledgment); PROHIBITED (per-subject plots/listings beyond what is reasonably necessary) | P10-J, P10-E | As (d). | medium |
| (f) publishing transformed or reconstructed records | PROHIBITED | P10-E, P10-K | [T] "any portion of the Data" may not be published on a website or other release; transformed or reconstructed records remain Data-derived disclosure. | high (whether fully synthetic data *statistically modelled* on PDS data counts as "Data" is not addressed -> UNCLEAR, ask PDS) |
| (g) publishing per-case inputs and model predictions | PROHIBITED | P10-E | Per-case inputs are Data. Predictions keyed to real subject records disclose record-level information. | high |
| (h) publishing cached API responses | PROHIBITED | P10-E, P10-K | Cached LLM requests/responses would contain Data (and such API calls are themselves barred under (c)). | high |
| (i) publishing prompts or quoted source text | PROHIBITED (anything containing Data); UNCLEAR (dataset descriptor/data-dictionary text) | P10-E; website Terms of Use quote in §10.1 | Website content may not be reproduced beyond "informational, personal, non-commercial use" without written authorization. | medium |
| (j) publishing trained models or derived artifacts | UNCLEAR | P10-E, P10-I, P10-K | [T] Not addressed. A model trained on Data can memorise records (disclosure risk) and is "intellectual property resulting from your use of the Data" for P10-I purposes. Treat as needing written clarification from PDS. | low |
| (k) redistributing original records | PROHIBITED | P10-E, P10-H, P10-K | Non-sublicensable licence; confidentiality; providers keep all rights. | high |
| (l) redistributing modified records | PROHIBITED | same | — | high |
| (m) including files inside an MIT repository | PROHIBITED | P10-E, P10-H | An MIT grant over Data would be an unauthorized sublicence and public disclosure. | high |
| (n) attribution and NOTICE requirements | ALLOWED (obligation: verbatim acknowledgment in every publication/presentation of results) | P10-J; P10-M | No use of the "Project Data Sphere" name/logo for promotion beyond the required acknowledgment. | high |
| (o) share-alike requirements | ALLOWED (no share-alike); note IP covenants | P10-I | Not copyleft, but patent non-assertion and licence-back obligations attach to results. | high |
| (p) privacy, data protection, contractual restrictions | PROHIBITED (re-identification / contacting individuals); other duties apply | P10-D, P10-F, P10-C, P10-L, P10-N | [P] De-identified patient-level data; the agreement itself warns the Platform "may include … protected health information". [T] IRB/ethics responsibility on the user, data-protection-law compliance, secure storage, 24h breach notice, destruction on termination, NCI Supplemental Terms for NCI data, sanctions warranty, third-party-beneficiary enforcement, indemnity, North Carolina law. | high |

**[S] Scientific limitations (as far as verified):** the platform and licence are scoped to oncology ("completed studies in the field of cancer research"). Whether available datasets contain screening, I/E-criterion and informed-consent records suitable for eligibility/consent triage was not checked — dataset contents sit behind registration: COULD NOT VERIFY.

**Bottom line for source 10:** not usable for any artifact in a public MIT repository; not usable with external AI APIs. If ever used, only by individually authorized staff, on local/self-hosted infrastructure, for a cancer-research purpose approved in the application, publishing aggregates only with the Article VII acknowledgment.

---

## 11. Cross-cutting notes for integration decisions

1. **Nothing from sources 6–9 needs to be copied into our repository.** All four tools can be optional, externally installed, invoked by subprocess on our own synthetic data; publishing the resulting metrics/charts/per-case outputs is ALLOWED in each case.
2. **If we do vendor anything:** Apache-2.0 material (gsm, sdtmchecks) must stay Apache-2.0 with licence text and change notices; MIT material (CORE engine, rule YAML, CTAS) must keep its original copyright + permission notice. A `THIRD_PARTY_LICENSES`/`NOTICE` file in our repo is advisable even though none of the upstreams ships a NOTICE file.
3. **Do not commit:** CORE `resources/cache/*.pkl` or any CDISC Library API output; CDISC standards text beyond what is already inside MIT rule files; CDISC/CORE logos; `clindata` records; the CTAS PHUSE PDFs; anything from Project Data Sphere.
4. **Python 3.12 / uv fit:** only CORE is Python (`>=3.12,<3.13`), with heavy and conflicting pins (`pandas>=3.0.0` in the PyPI package vs `pandas==2.1.4` in the SQL fork) -> isolate it. The other three are R (two GitHub-only, sdtmchecks on CRAN).
5. **Topic fit [S]:** gsm kri0012 (Screen Failure Rate), kri0014 (Ineligibility) and kri0003/kri0004 (protocol deviation rates) are the closest matches but are site-level aggregates; CORE has SDTM conformance rules touching RFICDTC / IE / screen failure; sdtmchecks has one consent-date check and no IE checks; CTAS and PDS do not fit the core task.

## 12. Consolidated list of items that COULD NOT be verified

- CDISC Library EULA / API terms of use (commercial use, caching, redistribution) — text not obtainable without account sign-up.
- A standalone CDISC trademark policy page (only the 2025 Communications Policy §2 was found).
- Whether the MIT licence of the CORE repositories is intended to cover the Library-derived cache files; contents of the `.pkl` cache (not unpickled).
- Which CORE engine/version label CDISC intends for the pandas engine (cdisc.org says "V0.17.1"; the repo and PyPI say 1.0.0), and whether its cache still carries SDTMIG rules.
- Runtime behaviour of any tool on our data (no tool was installed or executed; read-only research).
- Provenance/licence of CORE rule test-data XLSX files and of the two PHUSE PDFs in the CTAS repo.
- `gsm.endpoints` (required by the gsm.mapping `Consents` workflow) — no public repository found.
- Whether `clindata` is synthetic or anonymized real data (the package contradicts itself).
- Copyright holder for gsm.qtl, gsm.pd, gsm.app (no `cph`; LICENSE template unfilled in two of them) and the identity behind "Workr Maintainer".
- Whether the PDS click-through agreement at registration matches the posted May 13, 2020 PDF; NCI Supplemental Terms text; contents of PDS datasets.
- Licences of transitive dependencies (R and Python) and of PostgreSQL binaries bundled by `pgserver`.
