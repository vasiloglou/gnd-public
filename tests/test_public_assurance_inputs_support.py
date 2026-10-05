"""Exact consumed containment helper only; no proof/publication functions."""
from pathlib import Path

from gnd.assurance_evidence import _read, _relative

__all__ = ["_read", "contained"]

def contained(root: Path, relative: str) -> Path:
    parts = _relative(relative)
    path = root.joinpath(*parts)
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError("proof input escapes its source root")
    cursor = root
    for part in parts:
        cursor = cursor / part
        if cursor.is_symlink():
            raise ValueError("proof source input is a symlink")
    return path
