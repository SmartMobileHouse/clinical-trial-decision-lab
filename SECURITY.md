# Security policy

## Reporting a vulnerability

Please **do not open a public issue** for security or privacy problems. Report them privately
through GitHub: **Security → Report a vulnerability** on this repository, when private vulnerability
reporting is enabled. If that option is unavailable, contact Smart Mobile House privately through
its website and ask for a secure reporting channel before sending sensitive details. Include a
sanitised reproduction and expected impact. We aim to reply within 5 working days.

## What counts

- A way for secrets (API keys in `.env`) to appear in logs, reports, outputs or run folders.
- A way for a dataset marked `external_processing_allowed: false` to be sent to a provider.
- A code path that calls a paid provider without `--allow-external-requests`, or bypasses the
  spending guard.
- A way for dry-run fixture answers to appear as measured results.
- A way for unapproved data, names of individuals or unapproved model results to reach a report,
  an export or the repository, or for the publication preflight to pass when it should fail.
- Personal or sensitive information found anywhere in this repository or its history.

## How the project protects you

- Offline defaults. Live calls need explicit flags, keys and a spending estimate. The estimate is
  not a provider billing cap.
- `.env` is gitignored. Credential checks report names and lengths only. Response text kept in run
  folders is redacted for known credentials, but run folders are still private until reviewed.
- Tests block network connections.
- Publication permission is separate from processing permission, per dataset and per model.
- `make check` runs a secret scan, a licence metadata screen and the technical preflight. None of
  these is a vulnerability scan or a legal review.

## Scope and misuse

This is a research benchmark on synthetic data. It is not connected to clinical systems and must
not be used to make decisions about trial participants. Case text can contain prompt injection;
robustness against manipulated records has not been tested. Do not send real participant data to
any provider through this tool.
