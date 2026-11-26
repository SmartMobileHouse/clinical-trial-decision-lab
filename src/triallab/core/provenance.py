"""Local experiment identity and atomic checkpoints; no provider requests.

Copied from Fraud Decision Lab v0.2.0 (`fraudlab/benchmark/provenance.py`); the
pandas-specific helpers were replaced by JSON Lines helpers.
"""

from __future__ import annotations

import hashlib
import json
import os
from collections.abc import Iterable
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from triallab.config import REPO_ROOT


def json_hash(value: Any) -> str:
    data = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    return hashlib.sha256(data).hexdigest()


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source_hash() -> str:
    """Bind even uncommitted executable code and the dependency lock to the run."""
    paths = sorted((REPO_ROOT / "src" / "triallab").rglob("*.py"))
    paths += [REPO_ROOT / "uv.lock"]
    return json_hash({str(p.relative_to(REPO_ROOT)): file_hash(p) for p in paths if p.is_file()})


def atomic_json(path: Path, value: Any) -> None:
    tmp = path.with_name(f".{path.name}.tmp")
    with tmp.open("w") as f:
        json.dump(value, f, indent=2, allow_nan=False)
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())
    tmp.replace(path)


def atomic_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    tmp = path.with_name(f".{path.name}.tmp")
    with tmp.open("w") as f:
        for row in rows:
            f.write(json.dumps(row, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n")
        f.flush()
        os.fsync(f.fileno())
    tmp.replace(path)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open() as f:
        return [json.loads(line) for line in f if line.strip()]


@contextmanager
def run_lock(out: Path):
    """Prevent concurrent resumes; the OS releases the lock after an interruption."""
    import fcntl

    with (out / ".run.lock").open("a") as f:
        try:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise ValueError("this run is already being executed by another process") from exc
        try:
            yield
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)
