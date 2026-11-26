"""Shared settings: where things live. Secrets are read from the environment only.

Adapted from Fraud Decision Lab (`fraudlab/config.py`, MIT, Smart Mobile House).
Nothing in this module ever returns or logs a secret value.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# Repository root: src/triallab/config.py -> parents[2]
REPO_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = REPO_ROOT / ".env"
CONFIGS = REPO_ROOT / "configs"
DATA = REPO_ROOT / "data"
OUTPUTS = REPO_ROOT / "outputs"
MODEL_REGISTRY = CONFIGS / "models.yaml"
SOURCE_MANIFEST = DATA / "source-manifest.json"


def load_env(env_file: Path = ENV_FILE) -> bool:
    """Load `.env` into the process environment without overriding real env vars."""
    if env_file.is_file():
        load_dotenv(env_file, override=False)
        return True
    return False


@dataclass(frozen=True)
class SecretStatus:
    """Presence of one secret. Holds only its name and length, never the value."""

    name: str
    is_set: bool
    length: int


def secret_status(name: str) -> SecretStatus:
    value = os.environ.get(name, "").strip()
    return SecretStatus(name=name, is_set=bool(value), length=len(value))
