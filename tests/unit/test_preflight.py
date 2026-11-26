"""The publication preflight must fail for each release-blocking condition."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from triallab.config import REPO_ROOT
from triallab.preflight import checks as c


def git(root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)  # noqa: S603, S607


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A minimal clean repository that passes every automated check."""
    root = tmp_path / "repo"
    (root / "data" / "synthetic").mkdir(parents=True)
    (root / "docs").mkdir()
    data_file = root / "data" / "synthetic" / "cases.jsonl"
    data_file.write_text('{"case_id": "SYN-1"}\n')
    decisions = dict.fromkeys(c.DECISIONS, "ALLOWED")
    manifest = {
        "sources": [
            {"id": "own", "name": "Own synthetic data", "origin": "generated here", "source_version": "1", "license": "MIT",
             "rights_holder": "Us", "verification_date": "2026-11-16", "acquisition_date": "2026-11-16",
             "included_in_repository": True, "decisions": decisions, "notice_required": True, "notice_token": "Own synthetic data"},
        ],
        "artifacts": [{"path": "data/synthetic/cases.jsonl", "source_id": "own", "publication_status": "approved",
                       "sha256": c.file_hash(data_file)}],
        "reviews": {k: {"status": "pending", "reviewer": None, "date": None, "scope": "x"} for k in ("sensitive_data", "legal")},
        "release": {"approved": False},
    }  # fmt: skip
    (root / "data" / "source-manifest.json").write_text(json.dumps(manifest))
    (root / "pyproject.toml").write_text('[project]\ndependencies = [\n    "httpx>=0.27",\n]\n')
    (root / "THIRD_PARTY_NOTICES.md").write_text("Own synthetic data. Dependency: httpx (BSD-3-Clause).\n")
    for name in c.REQUIRED_FILES:
        if not (root / name).exists():
            (root / name).parent.mkdir(parents=True, exist_ok=True)
            (root / name).write_text("placeholder for the test repository\n")
    (root / ".gitignore").write_text("outputs/\n")
    git(root, "init", "-q", "-b", "main")
    git(root, "config", "user.email", "tester@example.com")
    git(root, "config", "user.name", "tester")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "init")
    return root


def failed(root: Path, technical: bool = True) -> set[str]:
    return {r.name.split(".")[0] for r in c.run_preflight(root, technical_only=technical) if not r.passed}


def edit_manifest(root: Path, change) -> None:
    path = root / "data" / "source-manifest.json"
    manifest = json.loads(path.read_text())
    change(manifest)
    path.write_text(json.dumps(manifest))


def test_clean_repository_passes_automated_checks_but_not_the_release(repo: Path) -> None:
    assert failed(repo) == set()
    assert failed(repo, technical=False) == {"5b", "9", "10"}  # approvals are pending


def test_recorded_approvals_unblock_the_release(repo: Path) -> None:
    def approve(m):
        for review in m["reviews"].values():
            review.update(status="approved", reviewer="Owner", date="2026-12-01")
        m["release"] = {"approved": True, "approved_by": "Owner", "date": "2026-12-01"}

    edit_manifest(repo, approve)
    assert failed(repo, technical=False) == set()


def test_unknown_rights_fail(repo: Path) -> None:
    edit_manifest(repo, lambda m: m["sources"][0]["decisions"].pop("redistribute_records"))
    assert "1" in failed(repo)


def test_unclear_rights_for_material_inside_the_repository_fail(repo: Path) -> None:
    edit_manifest(repo, lambda m: m["sources"][0]["decisions"].update(include_in_mit_repository="UNCLEAR"))
    assert "1" in failed(repo)


def test_missing_provenance_fails(repo: Path) -> None:
    edit_manifest(repo, lambda m: m["sources"][0].update(origin=""))
    assert "2" in failed(repo)


@pytest.mark.parametrize("path", ["data/external/letters.csv", "data/restricted/x.jsonl", "private/notes.md", "register.jsonl",
                                  "data/sdtm/dm.xpt", "data/fda-findings-v1/test.cases.jsonl"])  # fmt: skip
def test_restricted_file_fails_even_when_only_untracked(repo: Path, path: str) -> None:
    target = repo / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("x\n")
    assert "3" in failed(repo)


def test_restricted_file_in_history_fails_after_deletion(repo: Path) -> None:
    target = repo / "data" / "external" / "old.csv"
    target.parent.mkdir(parents=True)
    target.write_text("x\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "oops")
    git(repo, "rm", "-q", "data/external/old.csv")
    git(repo, "commit", "-q", "-m", "remove")
    results = {r.name[0]: r for r in c.run_preflight(repo, technical_only=True)}
    assert not results["3"].passed and "in history" in results["3"].detail


def test_missing_notice_fails(repo: Path) -> None:
    (repo / "THIRD_PARTY_NOTICES.md").write_text("Dependency: httpx.\n")
    assert "4" in failed(repo)
    (repo / "THIRD_PARTY_NOTICES.md").write_text("Own synthetic data.\n")  # dependency no longer listed
    assert "4" in failed(repo)


@pytest.mark.parametrize(
    "text",
    ["Contact jane.doe@hospital.org for details", "SSN 123-45-6789", "date_of_birth: 1970-01-01",
     "see https://www.fda.gov/inspections/warning-letters/some-person-md-123456-01012025"],
)  # fmt: skip
def test_sensitive_information_fails(repo: Path, text: str) -> None:
    (repo / "docs" / "note.md").write_text(text + "\n")
    assert "5a" in failed(repo)


def test_names_from_the_restricted_register_are_detected(
    repo: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    register = tmp_path / "restricted" / "fda-findings-v1" / "register.jsonl"
    register.parent.mkdir(parents=True)
    register.write_text(json.dumps({"recipient_name_as_published": "Zebulon Quackenbush, M.D."}) + "\n")
    monkeypatch.setenv("TRIALLAB_RESTRICTED_DATA", str(register.parent.parent))
    assert failed(repo) == set()
    (repo / "docs" / "note.md").write_text("The letter to Dr. Quackenbush says...\n")
    assert "5a" in failed(repo)


def test_untraced_or_changed_data_artifact_fails(repo: Path) -> None:
    (repo / "data" / "synthetic" / "extra.jsonl").write_text("{}\n")
    assert "6" in failed(repo)
    (repo / "data" / "synthetic" / "extra.jsonl").unlink()
    (repo / "data" / "synthetic" / "cases.jsonl").write_text('{"case_id": "changed"}\n')
    assert "6" in failed(repo)


def test_unapproved_artifact_status_fails(repo: Path) -> None:
    edit_manifest(repo, lambda m: m["artifacts"][0].update(publication_status="pending"))
    assert "6" in failed(repo)


def test_stored_api_outputs_without_publication_rights_fail(repo: Path) -> None:
    (repo / "docs" / "predictions.jsonl").write_text("{}\n")
    assert "7" in failed(repo)
    (repo / "docs" / "predictions.jsonl").unlink()
    bundle = {"schema": "smh-research-data/1", "experiments": {"x": {"measured_systems": ["rules", "jev"],
              "dataset": {"name": "synthetic-v1", "publication_allowed": True}}}}  # fmt: skip
    (repo / "docs" / "report-data.json").write_text(json.dumps(bundle))
    assert "7" in failed(repo)  # jev is not approved for publication in the registry
    bundle["experiments"]["x"]["measured_systems"] = ["rules"]
    (repo / "docs" / "report-data.json").write_text(json.dumps(bundle))
    assert failed(repo) == set()


def test_report_referencing_unapproved_data_fails(repo: Path) -> None:
    bundle = {"schema": "smh-research-data/1", "experiments": {"x": {"measured_systems": ["keyword"],
              "dataset": {"name": "fda-findings-v1", "publication_allowed": False}}}}  # fmt: skip
    (repo / "docs" / "report-data.json").write_text(json.dumps(bundle))
    assert "8" in failed(repo)
    (repo / "docs" / "report-data.json").unlink()
    (repo / "docs" / "report.html").write_text("<p>Case REG-014 was classified as consent.</p>")
    assert "8" in failed(repo)


def test_not_a_git_checkout_fails(tmp_path: Path) -> None:
    results = c.run_preflight(tmp_path, technical_only=True)
    assert len(results) == 1 and not results[0].passed


def test_this_repository_passes_the_automated_checks() -> None:
    if not (REPO_ROOT / ".git").exists() or shutil.which("git") is None:
        pytest.skip("not a git checkout")
    problems = [f"{r.name}: {r.detail}" for r in c.run_preflight(REPO_ROOT, technical_only=True) if not r.passed]
    assert not problems, problems
