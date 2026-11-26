# Local quality gate. Run `make check` before every push; CI runs the same target.
# The repo may live on an external volume: uv cannot hardlink across disks, so copy.
export UV_LINK_MODE := copy
.PHONY: help install check lint format typecheck test data licenses secrets preflight release-check doctor demo pii

help:  ## List targets
	@grep -E '^[a-z-]+:.*##' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  make %-14s %s\n", $$1, $$2}'

install:  ## Install pinned dependencies from uv.lock
	uv sync --frozen

check: lint typecheck test data licenses secrets preflight  ## Everything below, in order
	@echo "make check: all passed (publication approvals are checked separately by make release-check)"

lint:  ## Ruff lint + format check
	uv run ruff check .
	uv run ruff format --check .

format:  ## Auto-fix lint and formatting
	uv run ruff check --fix .
	uv run ruff format .

typecheck:  ## mypy on src/
	uv run mypy

test:  ## Offline tests (live tests are excluded by default)
	uv run pytest

data:  ## Dataset reproducibility and ground-truth integrity
	uv run triallab data verify

licenses:  ## Screen installed license metadata (redistribution still requires review)
	uv run pip-licenses --partial-match --fail-on="GPL;AGPL;SSPL;Commons Clause;UNKNOWN" > /dev/null
	@echo "licenses: metadata screen passed; review distribution notices separately"

secrets:  ## Scan git history and staged changes for secrets (needs `brew install gitleaks`)
	@command -v gitleaks >/dev/null || { echo "gitleaks missing: brew install gitleaks"; exit 1; }
	gitleaks git --no-banner --redact --log-opts=--all .
	gitleaks git --no-banner --redact --pre-commit --staged .
	gitleaks dir --no-banner --redact src tests configs data docs scripts

preflight:  ## Automated publication checks (rights, provenance, restricted files, notices, sensitive data)
	uv run triallab preflight --technical

pii:  ## Presidio scan of every publishable file for personal data (first run downloads Presidio and a language model)
	uv run --no-project --python 3.12 --with presidio-analyzer==2.2.366 \
	  --with "en-core-web-lg @ https://github.com/explosion/spacy-models/releases/download/en_core_web_lg-3.8.0/en_core_web_lg-3.8.0-py3-none-any.whl" \
	  python scripts/presidio_scan.py

release-check:  ## Full publication preflight, including recorded human approvals. Fails until they exist.
	uv run triallab preflight

doctor:  ## Check local setup
	uv run triallab doctor

demo:  ## Offline demo: rules on the synthetic test set, a dry run of two adapters, an HTML summary (no keys)
	uv run triallab demo
