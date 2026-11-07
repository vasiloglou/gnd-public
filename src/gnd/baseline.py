"""Compare a head check with a baseline check (``gnd check --baseline``).

A violation's key is its rule's address plus the canonical JSON of its
offending row; a failing rule with no rows is keyed by its address alone. A
key in both runs is standing, a key only in head is new, and a key only in
base is resolved. The band reads only the two flags this module computes.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from gnd.artifacts import canonical_json_bytes

#: A rule's address and one canonical offending row, or None for a row-less failure.
Key = tuple[str, bytes | None]


@dataclass(frozen=True, slots=True)
class VerdictView:
    """One verdict as version 15 reports it: its positional ref, outcome and rows."""

    ref: str
    verdict: str
    modality: str
    rows: Sequence[Any]


@dataclass(frozen=True, slots=True)
class Comparison:
    """Novelty per head verdict, the baseline block's counts, and the band's two inputs."""

    novelty: Mapping[str, tuple[str, list[str]]]
    counts: Mapping[str, int]
    new_alethic_fail: bool
    undecided_alethic: bool


def baseline_key(address: str, row: Any | None) -> Key:
    """The one key every family's offending row is compared by."""
    return address, None if row is None else canonical_json_bytes(row)


def _keys(view: VerdictView, address: str) -> list[Key]:
    if view.verdict not in ("fail", "warning"):
        return []
    return [baseline_key(address, row) for row in view.rows] or [baseline_key(address, None)]


def compare(
    head: Sequence[VerdictView],
    base: Sequence[VerdictView],
    addresses: Mapping[str, tuple[str, str]],
) -> Comparison:
    """Judge each head violation against the base; ``addresses`` maps ref -> (address, addressing)."""
    base_keys = {key for view in base for key in _keys(view, addresses[view.ref][0])}
    head_keys: set[Key] = set()
    novelty: dict[str, tuple[str, list[str]]] = {}
    positional = 0
    new_alethic_fail = False
    for view in head:
        address, addressing = addresses[view.ref]
        keys = _keys(view, address)
        if not keys:
            continue
        marks = ["standing" if key in base_keys else "new" for key in keys]
        label = "new" if "new" in marks else "standing"
        novelty[view.ref] = (label, marks if view.rows else [])
        new_alethic_fail |= view.verdict == "fail" and view.modality == "alethic" and label == "new"
        fresh = set(keys) - head_keys
        head_keys |= fresh
        positional += len(fresh) if addressing == "positional" else 0
    unchecked = [view for views in (head, base) for view in views if view.verdict == "unchecked"]
    return Comparison(
        novelty=novelty,
        counts={
            "new": len(head_keys - base_keys),
            "standing": len(head_keys & base_keys),
            "resolved": len(base_keys - head_keys),
            "positional_keyed": positional,
            "undecided": len({view.ref for view in unchecked}),
        },
        new_alethic_fail=new_alethic_fail,
        undecided_alethic=any(view.modality == "alethic" for view in unchecked),
    )
