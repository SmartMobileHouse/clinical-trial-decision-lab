# CLAUDE.md — working rules for this repository

Clinical Trial Decision Lab benchmarks AI decision models, deterministic rules and structured-output
LLMs for triage of enrollment-eligibility and informed-consent issues. Python 3.12, uv, Typer,
httpx, pydantic. MIT licensed. It reuses Fraud Decision Lab's infrastructure and conventions.

## Commands

```bash
uv sync --frozen           # install exactly what uv.lock pins
uv run triallab doctor     # offline setup check
make check                 # ruff, mypy, pytest, dataset verification, licences, gitleaks, technical preflight
make format                # auto-fix lint/format
make demo                  # offline demo
make release-check         # full publication preflight; fails until approvals are recorded
```

## Hard rules

- **Never invent numbers.** Results, metrics and costs come only from real runs with a run ID.
  Missing results are shown as `not run`, `withheld`, `permission_blocked` or `failed`, never as
  placeholder numbers. Dry-run and mock answers are never measurements.
- **Research, not clinical advice.** No output is a regulatory determination. Never recommend
  treatment changes or patient-safety actions. Never claim clinically validated accuracy.
- **Absence of documentation is not proof.** A missing consent record is insufficient evidence,
  never a potential issue.
- **No language model writes ground truth.** Reference labels come from deterministic rules over
  recorded facts, and every case must match its scenario's declared findings.
- **Frozen specification.** Questions, reference rules, scenarios, metrics and the test split do
  not change after model results are seen. Changes need a new version and new predictions.
- **Offline by default.** No code path may call a provider without `--allow-external-requests`.
  Tests never reach the network; paid-API tests are marked `live` and excluded by default.
- **Never commit or print secrets or restricted data.** `.env`, `outputs/`, raw provider traces,
  third-party records, regulatory letters, their URLs and any names of individuals stay out of git
  and out of its history. Report secrets by name and length only.
- **Two tracks, never mixed.** Synthetic and regulatory-finding results are reported separately.
- **Rights are separate decisions.** Processing permission, publication permission for a dataset
  and publication approval for a model are three different flags. Never infer one from another.
  Uncertainty is not permission.
- **Same evidence for every system.** Models receive the same packet and question text through
  their own request formats. Never truncate evidence. Never repair invalid output.
- **MIT covers original work only.** Third-party material keeps its terms and notices.
- **Verify provider APIs and terms against current official sources** before changing an adapter or
  a registry entry. Record source and date.
- **No publishing without approval.** Do not push to a public remote, publish or deploy until
  `docs/RELEASE-APPROVAL.md` records an explicit approval.

## Conventions

- Conventional Commits: `feat`, `fix`, `docs`, `test`, `refactor`, `build`, `chore`. Branches are
  named `type/slug`.
- Keep commit authorship as configured in the repo; add AI assistance only as a `Co-Authored-By`
  trailer.
- Short, plain sentences in docs and issues. Explain project terms on first use.
- Files copied from Fraud Decision Lab name their origin; keep them close to the originals.
