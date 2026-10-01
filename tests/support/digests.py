"""Shared digest helpers for repository tests."""

from __future__ import annotations

import hashlib
from pathlib import Path


def sha256_bytes(data: bytes) -> str:
    """Return the lowercase SHA-256 digest of *data*."""
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    """Return the lowercase SHA-256 digest of a file's bytes."""
    return sha256_bytes(path.read_bytes())
