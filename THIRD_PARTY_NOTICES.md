# Third-party notices

Clinical Trial Decision Lab is released under the MIT licence (see [LICENSE](LICENSE)), copyright Smart Mobile House.

**The MIT licence covers this project's original software and its original synthetic data only.** It does not license any third-party dataset, document, tool, model or service. Third-party material keeps its own terms and attribution. Full records: [docs/THIRD-PARTY-LICENSES.md](docs/THIRD-PARTY-LICENSES.md) and [docs/DATA-LICENSING-AUDIT.md](docs/DATA-LICENSING-AUDIT.md).

## Code reused from Fraud Decision Lab

Parts of `src/triallab/core/` and `src/triallab/providers/` were copied or adapted from Fraud Decision Lab v0.2.0 (https://github.com/SmartMobileHouse/fraud-decision-lab), copyright (c) 2026 Smart Mobile House, MIT licence. Each copied module names its origin in its header.

## U.S. Food and Drug Administration

The regulatory-finding track uses descriptions of findings stated in warning letters published by the U.S. Food and Drug Administration on fda.gov. Those letters are works of the United States Government and are in the public domain in the United States. They are not covered by this project's MIT licence, and no letter text or per-case material is distributed with this repository.

Letters were retrieved on 2026-11-16. A warning letter states the agency's observations on its date and may have been answered or closed out since.

This project is not affiliated with, authorised by or endorsed by the U.S. Food and Drug Administration. The agency's name appears in plain text only, to identify the source. Its logo and marks are not used. Labels produced by this project or by any model are not regulatory determinations.

## Data sources of the screening study

The screening study in `studies/screening/` uses these sources. None of their text is redistributed here.

- **TrialPanorama.** Review-to-paper membership labels come from the TrialPanorama benchmark (https://huggingface.co/datasets/TrialPanorama/TrialPanorama-benchmark), Apache-2.0, drawn from the reference lists of published systematic reviews. This repository holds identifiers, labels and review titles derived from it.
- **Europe PMC.** Paper titles, abstracts and licence fields were retrieved from Europe PMC (https://europepmc.org/). Only abstracts under CC0, CC BY, CC BY-SA or CC BY-ND were used. Each abstract belongs to its authors and publisher and stays under its own licence; none is stored here.
- **SYNERGY.** Labels for one exploratory pilot come from the SYNERGY dataset by ASReview (https://github.com/asreview/synergy-dataset), CC0 1.0.
- **ClinicalTrials.gov.** One exploratory pilot used registry records from ClinicalTrials.gov (https://clinicaltrials.gov/), retrieved on 2026-11-17. The records were processed by simple rules and AI models; the labels stored here are ours, not the registry's. The data may have changed since.

This project is not affiliated with or endorsed by the TrialPanorama authors, Europe PMC, ASReview, Cochrane or the U.S. National Library of Medicine.

## Python packages used at run time

This project does not redistribute these packages. They are installed from the versions pinned in `uv.lock`. If you redistribute them, for example in a container image, keep each package's own licence and notice files.

| Package | Licence |
|---|---|
| httpx | BSD-3-Clause |
| jinja2 | BSD-3-Clause |
| numpy | BSD-3-Clause, with bundled components under 0BSD, MIT, Zlib and CC0-1.0 |
| pydantic | MIT |
| python-dotenv | BSD-3-Clause |
| pyyaml | MIT |
| typer | MIT |

Transitive packages include `certifi` under the Mozilla Public License 2.0, used unmodified. The complete list with versions is in [docs/THIRD-PARTY-LICENSES.md](docs/THIRD-PARTY-LICENSES.md).

## Tools that are not included

OpenRBQM / Good Statistical Monitoring and gsm.datasim (Gilead Sciences, Apache-2.0), CDISC CORE (CDISC, MIT), pharmaverse sdtmchecks (F. Hoffmann-La Roche AG, Apache-2.0) and the IMPALA Clinical Trial Anomaly Spotter (Bayer, MIT) were assessed. None of their code or data is included in this repository.

## Trademarks

Smart Mobile House is a trademark of Smart Mobile House and is not licensed under MIT.

TypeSafe, Jev, OpenAI, GPT, Cloudflare, Clef, Perplexity, Bespoke Labs, Nimble, Liquid AI, Morph, Microsoft, Convai, Laya, Anthropic, Claude, Opper, Runware, CDISC, PHUSE, Gilead, OpenRBQM, Roche, Bayer, ClinicalTrials.gov and Project Data Sphere are names or marks of their owners. They are used only to identify what was assessed or compared. This project is independent and is not affiliated with or endorsed by any of them.
