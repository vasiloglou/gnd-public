"""RF3 shared dependency home; algorithms retain predecessor semantics."""
from __future__ import annotations

from collections.abc import Sequence
from functools import cmp_to_key

from gnd import semantic_spec
from gnd.semantic_ir import IRConstraint, Scalar, SnapshotIR


def _scalar_identity(value: Scalar) -> tuple[str, str]:
    return value.identity_kind, value.token


def _canonical_rows(rows: Sequence[tuple[Scalar, ...]]) -> tuple[tuple[Scalar, ...], ...]:
    """Deduplicate canonical IR rows without the specification's quadratic scan."""
    distinct: dict[tuple[tuple[str, str], ...], tuple[Scalar, ...]] = {}
    for row in rows:
        distinct.setdefault(tuple(_scalar_identity(value) for value in row), row)

    def compare(left: tuple[Scalar, ...], right: tuple[Scalar, ...]) -> int:
        if semantic_spec.row_canonical_less(left, right):
            return -1
        if semantic_spec.row_canonical_less(right, left):
            return 1
        return 0

    return tuple(sorted(distinct.values(), key=cmp_to_key(compare)))


canonical_rows = _canonical_rows
scalar_identity = _scalar_identity

_scalar_identity.__module__ = 'gnd.correspondence'

_canonical_rows.__module__ = 'gnd.correspondence'


def indexed_subset_verdict(
    constraint: IRConstraint, snapshot: SnapshotIR
) -> tuple[str, str | None, tuple[tuple[Scalar, ...], ...]]:
    """Production subset decision with one projection and typed hash membership.

    The unchanged pure specification supplies applicability, projection semantics
    and canonical order. Only membership/preparation differ from its oracle.
    """
    applicability = semantic_spec.applicability_of(constraint, snapshot)
    if applicability.startswith("vacuous-"):
        return "vacuous", None, ()
    if applicability.startswith("unchecked-"):
        return "unchecked", applicability.removeprefix("unchecked-"), ()
    valid = (
        constraint.family == "subset"
        and constraint.refused == ""
        and len(constraint.sequences) == 2
        and constraint.variant in {"single", "joined"}
    )
    fact_counts = [len({ref[0] for ref in sequence}) for sequence in constraint.sequences]
    if constraint.variant == "single":
        valid = valid and all(count == 1 for count in fact_counts)
    else:
        valid = valid and any(count >= 2 for count in fact_counts)
    if not valid:
        return "unchecked", semantic_spec.unchecked_reason_of(constraint, snapshot), ()
    left_ok, left = semantic_spec.role_sequence_rows(constraint.sequences[0], snapshot)
    right_ok, right = semantic_spec.role_sequence_rows(constraint.sequences[1], snapshot)
    if not left_ok or not right_ok:
        return "unchecked", semantic_spec.unchecked_reason_of(constraint, snapshot), ()
    right_keys = {tuple(scalar_identity(value) for value in row) for row in right}
    witness = canonical_rows([
        row for row in left
        if tuple(scalar_identity(value) for value in row) not in right_keys
    ])
    if witness:
        return ("warning" if constraint.modality == "deontic" else "fail"), None, witness
    return "pass", None, ()
