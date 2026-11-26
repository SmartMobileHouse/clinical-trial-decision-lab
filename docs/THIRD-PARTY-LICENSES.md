# Third-party licences

Verification date: **2026-11-16**.

This page lists every third-party item this project touches and the rights we recorded for it. The MIT licence in [LICENSE](../LICENSE) covers this project's original software and original synthetic data only. Third-party material keeps its own terms.

This is a record of what was read, not legal advice. Short notices for redistribution are in [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md).

## 1. Python packages

The exact versions are pinned in `uv.lock`. The table below is the output of `uv run pip-licenses --format=markdown --with-urls` in the project environment on the verification date. It covers runtime and development packages together, including transitive ones.

Direct runtime dependencies (declared in `pyproject.toml`): httpx, Jinja2, numpy, pydantic, python-dotenv, PyYAML, typer.

Direct development dependencies: mypy, pip-licenses, pytest, pytest-asyncio, respx, ruff, types-PyYAML. They are used to test and check the project and are not needed to run it.

| Name                        | Version         | License                                            | URL                                                                   |
|-----------------------------|-----------------|----------------------------------------------------|-----------------------------------------------------------------------|
| Jinja2                      | 3.1.6           | BSD License                                        | https://github.com/pallets/jinja/                                     |
| MarkupSafe                  | 3.0.4           | BSD-3-Clause                                       | https://github.com/pallets/markupsafe/                                |
| PyYAML                      | 6.0.3           | MIT License                                        | https://pyyaml.org/                                                   |
| Pygments                    | 2.21.0          | BSD-2-Clause                                       | https://pygments.org                                                  |
| annotated-doc               | 0.0.5           | MIT                                                | https://github.com/fastapi/annotated-doc                              |
| annotated-types             | 0.8.0           | MIT                                                | https://github.com/annotated-types/annotated-types                    |
| anyio                       | 4.16.0          | MIT                                                | https://anyio.readthedocs.io/en/stable/versionhistory.html            |
| ast_serialize               | 0.13.1          | MIT                                                | https://github.com/mypyc/ast_serialize                                |
| certifi                     | 2026.10.23      | Mozilla Public License 2.0 (MPL 2.0)               | https://github.com/certifi/python-certifi                             |
| h11                         | 0.16.0          | MIT License                                        | https://github.com/python-hyper/h11                                   |
| httpcore                    | 1.0.9           | BSD-3-Clause                                       | https://www.encode.io/httpcore/                                       |
| httpx                       | 0.28.1          | BSD License                                        | https://github.com/encode/httpx                                       |
| idna                        | 3.20            | BSD-3-Clause                                       | https://github.com/kjd/idna                                           |
| iniconfig                   | 2.3.1           | MIT                                                | https://github.com/pytest-dev/iniconfig                               |
| librt                       | 0.16.0          | MIT                                                | https://github.com/mypyc/librt                                        |
| markdown-it-py              | 4.2.0           | MIT License                                        | https://github.com/executablebooks/markdown-it-py                     |
| mdurl                       | 0.1.2           | MIT License                                        | https://github.com/executablebooks/mdurl                              |
| mypy                        | 2.4.1           | MIT                                                | https://www.mypy-lang.org/                                            |
| mypy_extensions             | 1.2.0           | MIT                                                | https://github.com/python/mypy_extensions                             |
| numpy                       | 2.5.4           | BSD-3-Clause AND 0BSD AND MIT AND Zlib AND CC0-1.0 | https://numpy.org                                                     |
| packaging                   | 26.3            | Apache-2.0 OR BSD-2-Clause                         | https://github.com/pypa/packaging                                     |
| pathspec                    | 1.1.1           | Mozilla Public License 2.0 (MPL 2.0)               | https://python-path-specification.readthedocs.io/en/latest/index.html |
| pluggy                      | 1.7.0           | MIT License                                        | https://github.com/pytest-dev/pluggy                                  |
| pydantic                    | 2.14.3          | MIT                                                | https://github.com/pydantic/pydantic                                  |
| pydantic_core               | 2.50.4          | MIT                                                | https://github.com/pydantic                                           |
| pytest                      | 9.2.0           | MIT                                                | https://docs.pytest.org/en/latest/                                    |
| pytest-asyncio              | 1.4.1.post1     | Apache-2.0                                         | https://github.com/pytest-dev/pytest-asyncio                          |
| python-dotenv               | 1.2.4           | BSD-3-Clause                                       | https://github.com/theskumar/python-dotenv                            |
| respx                       | 0.23.1          | BSD License                                        | https://lundberg.github.io/respx/                                     |
| rich                        | 15.0.0          | MIT License                                        | https://github.com/Textualize/rich                                    |
| ruff                        | 0.17.4          | MIT                                                | https://docs.astral.sh/ruff                                           |
| shellingham                 | 1.5.4           | ISC License (ISCL)                                 | https://github.com/sarugaku/shellingham                               |
| typer                       | 0.28.0          | MIT                                                | https://github.com/fastapi/typer                                      |
| types-PyYAML                | 6.0.12.20261103 | Apache-2.0                                         | https://github.com/python/typeshed                                    |
| typing-inspection           | 0.4.5           | MIT                                                | https://github.com/pydantic/typing-inspection                         |
| typing_extensions           | 4.16.0          | PSF-2.0                                            | https://github.com/python/typing_extensions                           |

Notes:

- This is a **metadata screen**. It reports what each package declares about itself. It does not prove legal compatibility and it is not a complete notice inventory. `make licenses` fails the build when a package declares GPL, AGPL, SSPL, Commons Clause or no licence.
- All listed licences are permissive (MIT, BSD, Apache-2.0, ISC, PSF-2.0, 0BSD, Zlib, CC0-1.0) except two packages under the Mozilla Public License 2.0: `certifi` (runtime, via httpx) and `pathspec` (development only, via mypy). MPL-2.0 is a file-level licence. Using these packages unmodified alongside MIT code is compatible; if a file of theirs were ever modified and distributed, that file would stay under MPL-2.0 with its source available.
- `numpy` declares several licences because it bundles components under each.
- This project does not redistribute these packages. Anyone who builds a container image or other bundle that includes them must keep each package's licence and notice files.

## 2. Code reused from Fraud Decision Lab

| Item | Detail |
|---|---|
| Source | https://github.com/SmartMobileHouse/fraud-decision-lab, v0.2.0, commit b03029d |
| Licence | MIT |
| Copyright holder | Smart Mobile House (the same holder as this project) |
| What was reused | Shared HTTP layer, spending guard, call ledger, provenance helpers and option validation, copied into `src/triallab/core/`; provider contract and adapters adapted in `src/triallab/providers/`; project templates |
| Obligation | Keep the MIT notice. Each copied module names its origin in its header. |

Details: [FRAUD-LAB-REUSE-AUDIT.md](FRAUD-LAB-REUSE-AUDIT.md).

## 3. Optional external tools

None of these is bundled with this project. None is a dependency. **None has been executed by this project.** Each could be run separately by a user on data exported from the lab. Details and quoted provisions: [DATA-LICENSING-AUDIT.md](DATA-LICENSING-AUDIT.md).

| Tool | Version inspected | Licence | Copyright holder | Status here | Note |
|---|---|---|---|---|---|
| OpenRBQM / Good Statistical Monitoring (gsm.core, gsm.kri, gsm.mapping, gsm.reporting) | gsm.core v1.3.2, gsm.kri v1.8.0, gsm.mapping v1.2.0, gsm.reporting v1.1.8 | Apache-2.0 | Gilead Sciences | Not bundled, not a dependency, not executed | R packages. Site-level indicators; no informed-consent indicator. |
| Gilead gsm.datasim | v2.1.0, commit 29fc61c1 | Apache-2.0 | Gilead Sciences | Not bundled, not a dependency, not executed | R package. Evaluated as the data generator and not adopted: its eligibility results are random and its consent fields are constants. |
| CDISC CORE (rules engine and open rules) | engine v1.0.0; rule repositories at the commits named in the audit | MIT for the engine and rule repositories; CDISC Library content under terms we could not obtain | CDISC; Verisian for one rule repository | Not bundled, not a dependency, not executed | Never publish cached CDISC Library content or API responses. Use of the CDISC name or logo in branding needs approval. |
| pharmaverse sdtmchecks | CRAN 1.0.0 | Apache-2.0 | F. Hoffmann-La Roche AG | Not bundled, not a dependency, not executed | R package. No eligibility-criteria checks; one consent-date check. |
| IMPALA Clinical Trial Anomaly Spotter (CTAS) | v0.4.0 | MIT; imports packages under GPL licences | Bayer | Not bundled, not a dependency, not executed | Possible future experiment only. Never bundle, because of its GPL dependencies. |

## 4. Data sources

| Source | Licence or terms | In the repository | Summary |
|---|---|---|---|
| Synthetic cases v1 (this project) | MIT | Yes | Original fictional data. Every use allowed. |
| FDA warning letters | U.S. Government work; public domain in the United States | No | Free to use on copyright grounds. Letters name individuals, so per-case material stays private until a privacy review. |
| ClinicalTrials.gov | Custom terms and conditions | No | Not used. Attribution, processing date and modification log required; not under MIT. |
| AACT | Not verified | No | Not used. Terms could not be read. |
| CDISC SDTM/ADaM Pilot 01 | README terms of use; no licence file | No | Not used. Terms forbid modifying the data. |
| PHUSE phuse-scripts and safetyData | MIT stated; upstream CDISC terms unresolved | No | Not used. |
| Gilead clindata | Apache-2.0; privacy status unclear | No | Not used. Do not redistribute. |
| Project Data Sphere | Cancer Research Platform Agreement (2020-05-13) | No | Not used. Future source only; needs permission. |

Full register: [DATA-SOURCE-REGISTER.md](DATA-SOURCE-REGISTER.md) and `data/source-manifest.json`.

## 5. Model providers and gateways

Hosted models are services, not redistributed material. Their terms govern what we may run and publish. No provider has been called by this project.

| Provider | Product | Our reading: publish benchmark results |
|---|---|---|
| TypeSafe | Jev | UNCLEAR |
| OpenAI | Decisions, Responses | ALLOWED |
| Cloudflare | Clef, Clef-flash (weights Apache-2.0) | ALLOWED, with full replication information |
| Perplexity | Decider | REQUIRES PERMISSION |
| Bespoke Labs | Nimble (weights CC BY-NC 4.0: no commercial self-hosting) | UNCLEAR |
| Liquid AI | D1 Ultra (open d1 weights under a revenue-threshold licence) | UNCLEAR |
| Morph | reflex | UNCLEAR |
| Microsoft | Decision 1 (Preview) | ALLOWED, with conditions |
| Convai Innovations | Laya (weights Apache-2.0) | ALLOWED |
| Anthropic | Claude | ALLOWED |
| Opper, Runware | Gateways | UNCLEAR; upstream terms assumed to apply |

Per-model detail: [MODEL-REGISTER.md](MODEL-REGISTER.md). Quoted clauses: [DATA-LICENSING-AUDIT.md](DATA-LICENSING-AUDIT.md), section 12.

## 6. Trademarks

Provider, product and organisation names belong to their owners. They are used here only to describe what was assessed. This project is not affiliated with or endorsed by any of them.
