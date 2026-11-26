"""Scan every publishable file for personal data with Microsoft Presidio.

Run through `make pii`. Presidio and its language model are not project dependencies; the Makefile
target installs them into a throwaway environment.

The scan covers the same file list as the publication preflight: every file Git tracks plus every new
file that is not ignored. A finding is reported unless `configs/presidio-allowlist.txt` accepts it:
one exact string per line, or `re:` followed by a pattern the whole finding must match, each with a
reason in a comment. Two kinds of finding are dropped before that, because they cannot be a person:
a run of digits that is the fractional part of a decimal number, and a "person" that does not read
as a name (one to four capitalised words), which is how fragments of source code show up.

Presidio is statistical. It misses some personal data and flags text that is not personal data, so a
clean result is evidence, not proof.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess  # noqa: S404 - git only, fixed arguments
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALLOWLIST = ROOT / "configs" / "presidio-allowlist.txt"

# Entity types that identify or locate a person. Dates, URLs and nationality words are left out:
# they are not personal data on their own and would bury real findings.
ENTITIES = [
    "PERSON",
    "EMAIL_ADDRESS",
    "PHONE_NUMBER",
    "CREDIT_CARD",
    "IBAN_CODE",
    "IP_ADDRESS",
    "US_SSN",
    "US_PASSPORT",
    "US_DRIVER_LICENSE",
    "US_BANK_NUMBER",
    "US_ITIN",
    "MEDICAL_LICENSE",
    "UK_NHS",
    "CRYPTO",
]
CHUNK_CHARS = 50_000
NAME_SHAPE = re.compile(r"(?:[A-ZÀ-Ý][A-Za-zÀ-ÿ'’.-]*)(?: [A-ZÀ-Ý][A-Za-zÀ-ÿ'’.-]*){0,3}")


def publishable_files() -> list[Path]:
    out = subprocess.run(  # noqa: S603
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],  # noqa: S607
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return [ROOT / line for line in out.splitlines() if line and (ROOT / line).is_file()]


def chunks(text: str) -> list[str]:
    parts, current, size = [], [], 0
    for line in text.splitlines(keepends=True):
        if size + len(line) > CHUNK_CHARS and current:
            parts.append("".join(current))
            current, size = [], 0
        current.append(line)
        size += len(line)
    if current:
        parts.append("".join(current))
    return parts


def allowlist() -> tuple[set[str], list[re.Pattern[str]]]:
    exact: set[str] = set()
    patterns: list[re.Pattern[str]] = []
    if ALLOWLIST.exists():
        for raw in ALLOWLIST.read_text().splitlines():
            line = raw.split(" #", 1)[0].strip()  # the reason follows " #"
            if line.startswith("re:"):
                patterns.append(re.compile(line[3:]))
            elif line and not line.startswith("#"):
                exact.add(line)
    return exact, patterns


def cannot_be_a_person(entity: str, value: str, chunk: str, start: int) -> bool:
    if value.isdigit() and start > 0 and chunk[start - 1] in ".0123456789":
        return True  # digits inside a longer number, such as the decimals of a probability
    return entity == "PERSON" and not NAME_SHAPE.fullmatch(value)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--min-score", type=float, default=0.5, help="lowest Presidio confidence to report")
    parser.add_argument("--report", type=Path, default=ROOT / "outputs" / "presidio-report.json")
    args = parser.parse_args()

    from presidio_analyzer import AnalyzerEngine  # imported late: optional tool

    analyzer = AnalyzerEngine()
    accepted, accepted_patterns = allowlist()
    findings: dict[str, Counter[tuple[str, str]]] = defaultdict(Counter)
    skipped: list[str] = []
    scanned = 0
    for path in publishable_files():
        name = str(path.relative_to(ROOT))
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            skipped.append(name)
            continue
        scanned += 1
        for chunk in chunks(text):
            for hit in analyzer.analyze(text=chunk, language="en", entities=ENTITIES, score_threshold=args.min_score):
                value = chunk[hit.start : hit.end].strip()
                if not value or cannot_be_a_person(hit.entity_type, value, chunk, hit.start):
                    continue
                if value in accepted or any(p.fullmatch(value) for p in accepted_patterns):
                    continue
                findings[name][(hit.entity_type, value)] += 1

    rows = [
        {"file": name, "entity": entity, "text": value, "count": count}
        for name, counter in sorted(findings.items())
        for (entity, value), count in sorted(counter.items())
    ]
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(
        json.dumps({"scanned_files": scanned, "skipped_binary": skipped, "findings": rows}, indent=1)
    )

    rules = len(accepted) + len(accepted_patterns)
    print(f"presidio: {scanned} files scanned, {len(skipped)} binary skipped, {rules} allowlist rules")
    by_entity = Counter(row["entity"] for row in rows)
    for row in rows:
        print(f"  {row['file']}: {row['entity']}: {row['text']!r} x{row['count']}")
    if rows:
        print(f"presidio: {len(rows)} unreviewed finding(s): {dict(by_entity)}. Details in {args.report}")
        return 1
    print("presidio: no unreviewed finding")
    return 0


if __name__ == "__main__":
    sys.exit(main())
