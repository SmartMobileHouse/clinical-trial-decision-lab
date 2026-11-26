"""Publication preflight: automated checks that must pass before anything is made public.

Two kinds of check:
- `automated`  facts a program can verify about the repository;
- `approval`   decisions only a person can make, recorded in data/source-manifest.json.

`triallab preflight` runs both and fails while any approval is pending.
`triallab preflight --technical` (used by `make check` and CI) runs the automated ones.

The preflight fails when:
1. a data source's rights are unknown, or a source inside the repository is not cleared;
2. an external source lacks provenance;
3. a restricted file is tracked by Git, now or anywhere in history;
4. a required attribution or notice is missing;
5. personal or sensitive information is detected, or its review is not recorded;
6. a data artifact lacks a traceable source and an approved publication status;
7. API outputs are stored without confirmed publication rights;
8. a generated report references unapproved data.

Passing the preflight is necessary for a release, not sufficient: it does not give legal clearance.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from triallab.config import REPO_ROOT
from triallab.core.provenance import file_hash
from triallab.providers.registry import OFFLINE_SYSTEMS
from triallab.providers.spec import RegistryError, load_registry

VOCABULARY = ("ALLOWED", "PROHIBITED", "UNCLEAR", "REQUIRES PERMISSION")
DECISIONS = (
    "commercial_research_use",
    "internal_processing",
    "external_api_processing",
    "publish_aggregate_metrics",
    "publish_per_case_records",
    "redistribute_records",
    "include_in_mit_repository",
)
SOURCE_FIELDS = ("id", "name", "origin", "source_version", "license", "rights_holder", "verification_date", "decisions")
FORBIDDEN_PREFIXES = ("data/external/", "data/restricted/", "data/processed/", "outputs/", "private/")
FORBIDDEN_NAMES = (".env", "CLAUDE.local.md", "register.jsonl")
FORBIDDEN_SUFFIXES = (".xpt", ".sas7bdat", ".parquet", ".rds", ".rda", ".sqlite", ".db")
RUN_ARTIFACT_NAMES = ("predictions.jsonl", "attempts.jsonl")
MAX_TRACKED_BYTES = 5_000_000
REQUIRED_FILES = ("LICENSE", "THIRD_PARTY_NOTICES.md", "docs/THIRD-PARTY-LICENSES.md", "docs/DATA-LICENSING-AUDIT.md",
                  "docs/DATA-SOURCE-REGISTER.md", "docs/RELEASE-APPROVAL.md", "data/source-manifest.json")  # fmt: skip
RESTRICTED_DATASETS = ("fda-findings-v1", "real-findings-v2", "ohrp-findings")
TEXT_SUFFIXES = (".py", ".md", ".json", ".jsonl", ".yaml", ".yml", ".toml", ".txt", ".html", ".j2", ".cff", ".cfg", "")
ALLOWED_EMAIL_DOMAINS = ("anthropic.com", "example.com", "example.invalid", "users.noreply.github.com")
SENSITIVE_PATTERNS = {
    "email address": re.compile(r"\b[A-Za-z0-9._%+-]+@([A-Za-z0-9-]+\.[A-Za-z.]{2,})\b"),
    "US social security number": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "phone number": re.compile(r"(?<![\w.-])\+?\d{1,3}[ -]\(?\d{3}\)?[ -]\d{3}[ -]\d{4}\b"),
    "date of birth field": re.compile(r"\b(date[ _]of[ _]birth|birth[ _]?date|dob)\b\s*[:=]", re.I),
    "FDA warning-letter URL": re.compile(r"fda\.gov/[^\s\"')]*warning-letters/[a-z0-9-]+-\d{6,}"),
}
RESTRICTED_ENV = "TRIALLAB_RESTRICTED_DATA"
# The scanner's own patterns and its test fixtures are the only files allowed to contain look-alikes.
SCAN_EXEMPT = ("uv.lock", "src/triallab/preflight/checks.py", "tests/unit/test_preflight.py")
GENERIC_NAME_WORDS = frozenset(
    [
        "quality",
        "community",
        "committee",
        "independent",
        "ethics",
        "human",
        "subjects",
        "protection",
        "program",
        "programs",
        "investigator",
        "sponsor",
        "inc",
        "llc",
        "corp",
        "corporation",
        "company",
        "medical",
        "research",
        "institute",
        "institutional",
        "review",
        "board",
        "health",
        "products",
        "clinical",
        "university",
        "center",
        "centre",
        "hospital",
        "study",
        "group",
        "services",
        "associates",
        "pharmaceuticals",
        "pharma",
        "united",
        "american",
        "national",
        "international",
        "behavioral",
        "technology",
        "massachusetts",
        "therapeutics",
        "sciences",
        "science",
        "labs",
        "laboratories",
        "foundation",
        "college",
        "school",
        "department",
        "division",
        "office",
        "system",
        "systems",
        "care",
        "partners",
        "global",
        "biotech",
        "bio",
    ]
)


@dataclass(frozen=True)
class CheckResult:
    name: str
    passed: bool
    detail: str = ""
    kind: str = "automated"


def _git(root: Path, *args: str) -> str | None:
    try:
        result = subprocess.run(  # noqa: S603
            ["git", *args],  # noqa: S607 - git from PATH is intended
            cwd=root, capture_output=True, text=True, check=False,
        )  # fmt: skip
    except OSError:
        return None
    return result.stdout if result.returncode == 0 else None


def tracked_files(root: Path) -> list[str] | None:
    """Files Git tracks or would add (not ignored). None when this is not a Git checkout."""
    out = _git(root, "ls-files", "--cached", "--others", "--exclude-standard")
    return None if out is None else [line for line in out.splitlines() if line and (root / line).is_file()]


def history_paths(root: Path) -> list[str]:
    out = _git(root, "log", "--all", "--pretty=format:", "--name-only", "--diff-filter=A")
    return sorted({line for line in (out or "").splitlines() if line})


def load_manifest(root: Path) -> dict[str, Any]:
    return json.loads((root / "data" / "source-manifest.json").read_text())


def _is_restricted(path: str) -> bool:
    p = Path(path)
    return (
        path.startswith(FORBIDDEN_PREFIXES)
        or p.name in FORBIDDEN_NAMES
        or p.suffix.lower() in FORBIDDEN_SUFFIXES
        or (path.startswith("data/") and any(name in path for name in RESTRICTED_DATASETS))
    )


def _listing(items: list[str], limit: int = 5) -> str:
    return "; ".join(items[:limit]) + (f"; and {len(items) - limit} more" if len(items) > limit else "")


# ------------------------------------------------------------------ checks


def check_source_rights(root: Path, files: list[str]) -> CheckResult:
    name = "1. data source rights are known"
    problems = []
    for source in load_manifest(root)["sources"]:
        sid = source.get("id", "?")
        decisions = source.get("decisions", {})
        for key in DECISIONS:
            if decisions.get(key) not in VOCABULARY:
                problems.append(f"{sid}: decision {key} is missing or not one of the four classifications")
        if not str(source.get("license", "")).strip():
            problems.append(f"{sid}: licence not recorded")
        if source.get("included_in_repository"):
            for key in ("redistribute_records", "include_in_mit_repository", "publish_per_case_records"):
                if decisions.get(key) != "ALLOWED":
                    problems.append(f"{sid}: is inside the repository but {key} is {decisions.get(key)}")
    return CheckResult(
        name, not problems, _listing(problems) or "every source has a licence and seven classified decisions"
    )


def check_provenance(root: Path, files: list[str]) -> CheckResult:
    name = "2. external sources have provenance"
    problems = []
    for source in load_manifest(root)["sources"]:
        missing = [f for f in SOURCE_FIELDS if not source.get(f)]
        if missing:
            problems.append(f"{source.get('id', '?')}: missing {', '.join(missing)}")
        if source.get("included_in_repository") and not source.get("acquisition_date"):
            problems.append(f"{source.get('id', '?')}: no acquisition date")
    return CheckResult(name, not problems, _listing(problems) or "origin, version, licence, holder and dates recorded")


def check_restricted_files(root: Path, files: list[str]) -> CheckResult:
    name = "3. no restricted file is tracked by Git or present in its history"
    bad = [f for f in files if _is_restricted(f)]
    big = [f for f in files if (root / f).stat().st_size > MAX_TRACKED_BYTES]
    past = [f for f in history_paths(root) if _is_restricted(f)]
    problems = (
        [f"tracked: {f}" for f in bad] + [f"larger than 5 MB: {f}" for f in big] + [f"in history: {f}" for f in past]
    )
    return CheckResult(name, not problems, _listing(problems) or f"{len(files)} files checked, history clean")


def check_notices(root: Path, files: list[str]) -> CheckResult:
    name = "4. required attributions and notices are present"
    problems = [f"missing file: {f}" for f in REQUIRED_FILES if not (root / f).is_file()]
    notices_path = root / "THIRD_PARTY_NOTICES.md"
    notices = notices_path.read_text() if notices_path.is_file() else ""
    for source in load_manifest(root)["sources"]:
        if source.get("notice_required") and str(source.get("notice_token")) not in notices:
            problems.append(f"THIRD_PARTY_NOTICES.md does not mention {source.get('notice_token')!r}")
    pyproject = (root / "pyproject.toml").read_text() if (root / "pyproject.toml").is_file() else ""
    block = re.search(r"^dependencies = \[(.*?)^\]", pyproject, re.S | re.M)
    for dependency in re.findall(r'"([A-Za-z0-9_.-]+)', block.group(1) if block else ""):
        if dependency.lower() not in notices.lower():
            problems.append(f"THIRD_PARTY_NOTICES.md does not list the dependency {dependency}")
    return CheckResult(name, not problems, _listing(problems) or "licence, notices and every direct dependency listed")


def restricted_name_tokens() -> set[str] | None:
    """Distinctive words from recipient names in the private register; None when it is not available."""
    root = os.environ.get(RESTRICTED_ENV, "").strip()
    register = Path(root).expanduser() / "fda-findings-v1" / "register.jsonl" if root else None
    if register is None or not register.is_file():
        return None
    tokens: set[str] = set()
    for line in register.read_text().splitlines():
        if not line.strip():
            continue
        for word in re.findall(r"[A-Za-z][A-Za-z'-]{4,}", json.loads(line).get("recipient_name_as_published", "")):
            if word.lower() not in GENERIC_NAME_WORDS:
                tokens.add(word.lower())
    return tokens


def scan_sensitive(root: Path, files: list[str], name_tokens: set[str] | None) -> list[str]:
    hits = []
    names = re.compile(r"\b(" + "|".join(sorted(map(re.escape, name_tokens))) + r")\b", re.I) if name_tokens else None
    for f in files:
        path = root / f
        if path.suffix.lower() not in TEXT_SUFFIXES or path.stat().st_size > 2_000_000 or f in SCAN_EXEMPT:
            continue
        text = path.read_text(errors="ignore")
        for label, pattern in SENSITIVE_PATTERNS.items():
            for match in pattern.finditer(text):
                if label == "email address" and match.group(1).lower().endswith(ALLOWED_EMAIL_DOMAINS):
                    continue
                hits.append(f"{f}: {label}")
                break
        if names is not None and (found := names.search(text)):
            hits.append(f"{f}: a name from the restricted register ({found.group(0)[:3]}…)")
    return hits


def check_sensitive_scan(root: Path, files: list[str]) -> CheckResult:
    name = "5a. automated scan finds no personal or sensitive information"
    tokens = restricted_name_tokens()
    hits = scan_sensitive(root, files, tokens)
    scope = "patterns and restricted-register names" if tokens is not None else (
        f"patterns only; restricted-register name scan skipped because {RESTRICTED_ENV} is not set"
    )  # fmt: skip
    return CheckResult(name, not hits, _listing(hits) or f"no hits ({scope})")


def check_artifacts(root: Path, files: list[str]) -> CheckResult:
    name = "6. every data artifact has a source and an approved publication status"
    manifest = load_manifest(root)
    sources = {s["id"] for s in manifest["sources"]}
    listed = {a["path"]: a for a in manifest.get("artifacts", [])}
    problems = []
    for f in files:
        if not f.startswith("data/") or f == "data/source-manifest.json":
            continue
        entry = listed.get(f)
        if entry is None:
            problems.append(f"{f}: not listed in the source manifest")
        elif entry.get("source_id") not in sources:
            problems.append(f"{f}: unknown source {entry.get('source_id')!r}")
        elif entry.get("publication_status") != "approved":
            problems.append(f"{f}: publication status is {entry.get('publication_status')!r}")
        elif entry.get("sha256") != file_hash(root / f):
            problems.append(f"{f}: checksum differs from the source manifest")
    for path in listed:
        if not (root / path).is_file():
            problems.append(f"{path}: listed in the source manifest but missing")
    return CheckResult(name, not problems, _listing(problems) or f"{len(listed)} artifacts traced and fingerprinted")


def _unpublishable(names: set[str]) -> list[str]:
    try:
        registry = load_registry()
    except RegistryError:
        return sorted(names)
    known = {m.id: m for m in registry.models}
    return sorted(n for n in names if n not in OFFLINE_SYSTEMS and not (n in known and known[n].publishable))


def check_api_outputs(root: Path, files: list[str]) -> CheckResult:
    name = "7. no API outputs are stored without confirmed publication rights"
    problems = []
    for f in files:
        path = root / f
        if path.name in RUN_ARTIFACT_NAMES:
            problems.append(f"{f}: raw run artifact is tracked")
            continue
        if path.suffix != ".json" or path.stat().st_size > MAX_TRACKED_BYTES:
            continue
        try:
            bundle = json.loads(path.read_text())
        except ValueError:
            continue
        if not isinstance(bundle, dict) or not str(bundle.get("schema", "")).startswith("smh-research-data"):
            continue
        for key, experiment in (bundle.get("experiments") or {}).items():
            measured = set(experiment.get("measured_systems", []))
            if blocked := _unpublishable(measured):
                problems.append(f"{f}: experiment {key} contains results for {', '.join(blocked)}")
    return CheckResult(name, not problems, _listing(problems) or "no stored provider output lacks publication approval")


def check_reports(root: Path, files: list[str]) -> CheckResult:
    name = "8. no generated report references unapproved data"
    problems = []
    for f in files:
        path = root / f
        generated = path.suffix == ".html" or (path.suffix == ".json" and "report" in path.name)
        if not generated or f.startswith("src/"):
            continue
        text = path.read_text(errors="ignore")
        if path.suffix == ".json":
            try:
                bundle = json.loads(text)
            except ValueError:
                bundle = {}
            for key, experiment in (bundle.get("experiments") or {}).items() if isinstance(bundle, dict) else []:
                ds = experiment.get("dataset", {})
                if ds.get("name") in RESTRICTED_DATASETS or ds.get("publication_allowed") is not True:
                    problems.append(f"{f}: experiment {key} uses a dataset that is not approved for publication")
        if re.search(r"REG-\d{3}\b", text):
            problems.append(f"{f}: contains regulatory-finding case identifiers")
    return CheckResult(name, not problems, _listing(problems) or "no tracked report or bundle uses unapproved data")


def _approval(root: Path, key: str, label: str) -> CheckResult:
    review = load_manifest(root).get("reviews", {}).get(key, {})
    done = review.get("status") == "approved" and bool(review.get("reviewer")) and bool(review.get("date"))
    detail = (
        f"approved by {review.get('reviewer')} on {review.get('date')}"
        if done
        else "pending: " + str(review.get("scope", ""))
    )
    return CheckResult(label, done, detail, kind="approval")


def check_sensitive_review(root: Path, files: list[str]) -> CheckResult:
    return _approval(
        root, "sensitive_data", "5b. review for personal or sensitive information is recorded (method in its scope)"
    )


def check_legal_review(root: Path, files: list[str]) -> CheckResult:
    return _approval(root, "legal", "9. review of open licensing questions is recorded (kind of review in its scope)")


def check_release_approval(root: Path, files: list[str]) -> CheckResult:
    release = load_manifest(root).get("release", {})
    done = release.get("approved") is True and bool(release.get("approved_by")) and bool(release.get("date"))
    detail = (
        f"approved by {release.get('approved_by')} on {release.get('date')}"
        if done
        else "pending: owner approval of this release"
    )
    return CheckResult("10. the release is explicitly approved", done, detail, kind="approval")


Check = Callable[[Path, list[str]], CheckResult]
AUTOMATED: tuple[Check, ...] = (
    check_source_rights, check_provenance, check_restricted_files, check_notices, check_sensitive_scan,
    check_artifacts, check_api_outputs, check_reports,
)  # fmt: skip
APPROVALS: tuple[Check, ...] = (check_sensitive_review, check_legal_review, check_release_approval)


def run_preflight(root: Path = REPO_ROOT, technical_only: bool = False) -> list[CheckResult]:
    files = tracked_files(root)
    if files is None:
        return [CheckResult("repository", False, "not a Git checkout: tracked files cannot be determined")]
    results = []
    for check in AUTOMATED if technical_only else (*AUTOMATED, *APPROVALS):
        try:
            results.append(check(root, files))
        except (OSError, ValueError, KeyError) as exc:
            results.append(CheckResult(check.__name__, False, f"check could not run: {type(exc).__name__}: {exc}"))
    return results
