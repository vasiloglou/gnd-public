"""Byte-preserving model and population fixture writers."""

from __future__ import annotations

from pathlib import Path


def _write(root: Path, content: str | bytes, name: str) -> Path:
    destination = root / name
    payload = content.encode("utf-8") if isinstance(content, str) else content
    destination.write_bytes(payload)
    return destination


def write_model(root: Path, content: str | bytes, *, name: str = "model.orm.yaml") -> Path:
    """Write exact model bytes beneath an existing directory."""
    return _write(root, content, name)


def write_population(
    root: Path, content: str | bytes, *, name: str = "population.json"
) -> Path:
    """Write exact population bytes beneath an existing directory."""
    return _write(root, content, name)
