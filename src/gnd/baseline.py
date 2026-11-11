"""Compare a head check with a baseline check (``gnd check --baseline``).

A violation's key is its rule's address plus the canonical JSON of its
offending row; a failing rule with no rows is keyed by its address alone. A
key in both runs is standing, a key only in head is new, and a key only in
base is resolved. The band reads only the two flags this module computes.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from fractions import Fraction
from typing import Any

from gnd.address import declared_constraint_address
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


def _identity(value: Any) -> Any:
    """A row value by identity: one number however it is spelled (``1`` is ``1.0``).

    Booleans and strings stay themselves, so ``True`` and ``"1"`` are never the number 1.
    """
    if isinstance(value, bool) or value is None or isinstance(value, str):
        return value
    if isinstance(value, (int, float)):
        exact = Fraction(value)
        return {"$number": f"{exact.numerator}/{exact.denominator}"}
    if isinstance(value, Mapping):
        return {key: _identity(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_identity(item) for item in value]
    return value


def baseline_key(address: str, row: Any | None) -> Key:
    """The one key every family's offending row is compared by."""
    return address, None if row is None else canonical_json_bytes(_identity(row))


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


EDITION_COMPARISON_WORK = 1_000_000
_EDITION_VERDICTS = frozenset({"pass", "vacuous", "fail", "warning", "unchecked"})


class EditionComparisonLimit(Exception):
    """The rule-edition comparison exhausted its work budget."""


def _guarded_projection(
    base: Mapping[str, Any], head: Mapping[str, Any], charge: Callable[[int], None],
) -> tuple[tuple[str, ...], tuple[str, ...]] | None:
    """Align only variable sites with an unambiguous antecedent correspondence."""
    from gnd.atoms import atom_bind
    from gnd.terms import variable_name

    base_atoms = base["antecedent"]
    head_atoms = head["antecedent"]
    charge(sum(1 + len(atom_bind(atom)) for atoms in (base_atoms, head_atoms) for atom in atoms))
    def variable_names(atoms):
        return {
            name for atom in atoms for term in atom_bind(atom).values()
            if (name := variable_name(term)) is not None
        }

    base_names = variable_names(base_atoms)
    if base_atoms == head_atoms:
        names = tuple(f"${name}" for name in sorted(base_names))
        return names, names

    def unique_atoms(atoms):
        entries = {}
        for atom in atoms:
            fact = atom["fact_type"]
            entries[fact] = None if fact in entries else atom
        return entries

    left, right = unique_atoms(base_atoms), unique_atoms(head_atoms)
    pairs: dict[str, str] = {}
    reverse: dict[str, str] = {}
    for fact, atom in left.items():
        if atom is None or right.get(fact) is None:
            continue
        other = atom_bind(right[fact])
        for role, term in atom_bind(atom).items():
            a, b = variable_name(term), variable_name(other.get(role))
            if a is None or b is None:
                continue
            if pairs.setdefault(a, b) != b or reverse.setdefault(b, a) != a:
                return None
    if not pairs or (pairs.keys() != base_names and reverse.keys() != variable_names(head_atoms)):
        return None
    names = sorted(pairs)
    return tuple(f"${a}" for a in names), tuple(f"${pairs[a]}" for a in names)


def compare_editions(
    base_verdicts: Sequence[Mapping[str, Any]],
    head_verdicts: Sequence[Mapping[str, Any]],
    base_constraints: Mapping[str, Mapping[str, Any]],
    head_constraints: Mapping[str, Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], bool]:
    """Compare side-local observations by declared ID and canonical witness identity."""
    remaining = EDITION_COMPARISON_WORK

    def charge(amount: int) -> None:
        nonlocal remaining
        remaining -= amount
        if remaining < 0:
            raise EditionComparisonLimit

    charge(len(base_verdicts) + len(head_verdicts) + len(base_constraints) + len(head_constraints))

    def observations(rows, constraints):
        observed = {row["constraint_ref"] for row in rows}
        missing = []
        for ref, rule in constraints.items():
            if ref not in observed:
                address, addressing = declared_constraint_address(ref, rule)
                missing.append({
                    "address": address, "addressing": addressing, "constraint_ref": ref,
                    "constraint_type": rule["type"], "modality": rule["modality"],
                    "verdict": "unchecked", "missing_observation": True,
                })
        return [*rows, *missing]

    base_verdicts = observations(base_verdicts, base_constraints)
    head_verdicts = observations(head_verdicts, head_constraints)

    def declared(rows):
        return {row["address"]: row for row in rows if row["addressing"] == "declared-id"}

    def summary(row):
        if row is None:
            return None
        return {
            **{name: row[name] for name in ("constraint_ref", "constraint_type", "modality")},
            "verdict": row["verdict"] if row["verdict"] in _EDITION_VERDICTS else "unchecked",
        }

    def unavailable(row):
        if row is None:
            return None
        if row.get("missing_observation"):
            return "missing-verdict"
        if row["verdict"] not in _EDITION_VERDICTS:
            return "unknown-verdict"
        return "unchecked" if row["verdict"] == "unchecked" else None

    def witness_rows(row):
        if row is None or row["verdict"] not in ("fail", "warning"):
            return ()
        return row["offending_facts"] or (None,)

    def keys(rows, projection):
        indexed = {}
        for row in rows:
            charge(1 + (len(row) if isinstance(row, (dict, list, tuple)) else 0))
            full = baseline_key("", row)
            if projection is None:
                key = full
            elif isinstance(row, dict) and all(name in row for name in projection):
                key = baseline_key("", [row[name] for name in projection])
            else:
                return None
            previous = indexed.setdefault(key, (full, row))
            if previous[0] != full:
                return None
        return indexed

    base, head = declared(base_verdicts), declared(head_verdicts)
    candidates = [
        (address, base.get(address), head.get(address), None)
        for address in sorted(base.keys() | head.keys())
    ]
    for side, rows in (("base", base_verdicts), ("head", head_verdicts)):
        candidates.extend(
            (row["address"], row if side == "base" else None, row if side == "head" else None, side)
            for row in rows if row["addressing"] == "positional"
        )

    comparisons = []
    incomplete = False
    for address, left, right, unpaired_side in candidates:
        pairing = "unpaired" if unpaired_side else "added" if left is None else "removed" if right is None else "paired"
        reason = unavailable(left) or unavailable(right)
        delta = None
        if reason is None and not unpaired_side:
            a_rows, b_rows = witness_rows(left), witness_rows(right)
            a_keys, b_keys = None, None
            if a_rows and b_rows and left["constraint_type"] != right["constraint_type"]:
                reason = "constraint-family-changed"
            elif a_rows and b_rows and left["constraint_type"] == "guarded":
                if (a_rows == (None,)) != (b_rows == (None,)):
                    reason = "binding-shape-unavailable"
                elif a_rows != (None,):
                    projection = _guarded_projection(
                        base_constraints[left["constraint_ref"]], head_constraints[right["constraint_ref"]], charge,
                    )
                    if projection is None:
                        reason = "binding-alignment-ambiguous"
                    else:
                        a_keys, b_keys = projection
            if reason is None:
                a, b = keys(a_rows, a_keys), keys(b_rows, b_keys)
                if a is None or b is None:
                    reason = "binding-projection-collision"
                else:
                    delta = {
                        "base_only": [entry[1] for key, entry in a.items() if key not in b],
                        "head_only": [entry[1] for key, entry in b.items() if key not in a],
                        "standing": [
                            {"base": entry[1], "head": b[key][1]}
                            for key, entry in a.items() if key in b
                        ],
                    }
        incomplete |= reason is not None
        comparisons.append({
            "address": address, "pairing": pairing, "base": summary(left), "head": summary(right),
            "reason": reason, "delta": delta,
        })
    return comparisons, incomplete
