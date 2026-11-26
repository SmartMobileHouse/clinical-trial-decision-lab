# Contributing to clinical-trial-decision-lab

Read [`README.md`](README.md) and [`CLAUDE.md`](CLAUDE.md) first. The hard rules in `CLAUDE.md`
apply to every change.

## Prerequisites

| Tool | Why | Install (macOS) |
|---|---|---|
| `uv` | Python 3.12 and pinned dependencies from `uv.lock` | `brew install uv` |
| `make` | Runs the local checks | Xcode Command Line Tools |
| `gitleaks` | Secret scan in `make check` | `brew install gitleaks` |

## Workflow

```bash
uv sync --frozen
git switch -c feat/short-slug
# ... make your change, with tests ...
make format
make check          # must pass before every push; CI runs the same target
```

- **Conventional Commits:** `feat`, `fix`, `docs`, `test`, `refactor`, `build`, `chore`. Branches
  are named `type/slug`.
- **Tests** must not reach the network. A test that calls a real paid API is marked
  `@pytest.mark.live` and never runs by default.
- **Frozen things.** The question file, the reference rules, the scenario list, the metrics and the
  test split are frozen for specification version 1. Changing any of them needs a new version, a
  note in `docs/BENCHMARK-SPECIFICATION.md`, and new predictions. Never change them because of
  model results.
- **Dataset.** After any change to the generator run `uv run triallab data generate`, update the
  checksums in `data/source-manifest.json`, and explain the change. `make check` fails otherwise.
- **Models.** Add or change a model in `configs/models.yaml` only. Check the provider's current
  official API documentation and terms first, and record the source and date. A model whose
  interface was not verified cannot be enabled.
- **Data.** Never add third-party records, regulatory letters, names, run folders or provider
  responses. Add every new data file to `data/source-manifest.json` with its source.
- **Dependencies.** Review licence and notices, including transitive ones, and update
  `THIRD_PARTY_NOTICES.md` and `docs/THIRD-PARTY-LICENSES.md`. `make licenses` screens metadata; it
  does not prove compatibility.
- **Release.** Use [`docs/RELEASE-APPROVAL.md`](docs/RELEASE-APPROVAL.md). Passing checks does not
  approve publication.

## Contributors

Human and AI contributions are both welcome and both reviewed by a human maintainer. Commits keep
the maintainer's authorship; AI assistance is recorded with a `Co-Authored-By` trailer.

## Issues and pull requests

Use the issue forms (task, bug, tracking, decision) and the pull request template. Keep pull
requests small; a task holds at most 3 of them.
