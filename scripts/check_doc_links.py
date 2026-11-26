"""Check that relative links and backticked repository paths in Markdown files point at files that exist.

Offline: external URLs are not fetched.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"\[[^\]]*\]\(([^)\s#]+)(?:#[^)]*)?\)")
CODE_PATH = re.compile(r"`((?:docs|src|configs|data|scripts|tests|\.github)/[A-Za-z0-9_./-]+\.[a-z0-9]+)`")
# These two documents describe files of other projects, so their backticked paths are not checked.
PATHS_OF_OTHER_PROJECTS = ("FRAUD-LAB-REUSE-AUDIT.md", "DATA-LICENSING-AUDIT.md")
ROOT_FILE = re.compile(r"`([A-Z][A-Z_-]+\.(?:md|cff)|LICENSE|Makefile|pyproject\.toml|uv\.lock)`")


def tracked_markdown() -> list[Path]:
    out = subprocess.run(  # noqa: S603
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "*.md"],  # noqa: S607
        cwd=ROOT, capture_output=True, text=True, check=True,
    ).stdout  # fmt: skip
    return [ROOT / line for line in out.splitlines() if line]


def main() -> int:
    problems = []
    for path in tracked_markdown():
        text = path.read_text()
        if path.parts[-2] == "research":  # research appendices quote paths inside other projects
            continue
        for target in LINK.findall(text):
            if "://" in target or target.startswith("mailto:"):
                continue
            if not (path.parent / target).exists() and not (ROOT / target).exists():
                problems.append(f"{path.relative_to(ROOT)}: broken link {target}")
        if path.name in PATHS_OF_OTHER_PROJECTS:
            continue
        for target in CODE_PATH.findall(text) + ROOT_FILE.findall(text):
            if "*" in target or "<" in target:
                continue
            if not (ROOT / target).exists() and not target.startswith(("data/external", "data/restricted", "outputs/")):
                problems.append(f"{path.relative_to(ROOT)}: missing file {target}")
    for problem in sorted(set(problems)):
        print(problem)
    print(f"doc links: {len(set(problems))} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
