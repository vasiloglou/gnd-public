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


def _indexed_set_rows(
    constraint: IRConstraint, snapshot: SnapshotIR, family: str
) -> tuple[str, str | None, tuple[tuple[Scalar, ...], ...]] | tuple[
    tuple[tuple[Scalar, ...], ...], tuple[tuple[Scalar, ...], ...]
]:
    """Applicability, shape and distinct canonical rows shared by equality and exclusion.

    Returns a finished ``(verdict, reason, witness)`` when evaluation stops early,
    else the two distinct canonical row lists, as ``set_family_rows`` would.
    """
    applicability = semantic_spec.applicability_of(constraint, snapshot)
    if applicability.startswith("vacuous-"):
        return "vacuous", None, ()
    if applicability.startswith("unchecked-"):
        return "unchecked", applicability.removeprefix("unchecked-"), ()
    valid = (
        constraint.family == family
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
    return canonical_rows(left), canonical_rows(right)


def _row_key(row: tuple[Scalar, ...]) -> tuple[tuple[str, str], ...]:
    return tuple(scalar_identity(value) for value in row)


def _set_family_close(
    constraint: IRConstraint,
    left: tuple[tuple[Scalar, ...], ...],
    right: tuple[tuple[Scalar, ...], ...],
    witness: tuple[tuple[Scalar, ...], ...],
) -> tuple[str, str | None, tuple[tuple[Scalar, ...], ...]]:
    """Modality on violation, then NS-VACUITY-4 pass-only empty joined universe."""
    if witness:
        return ("warning" if constraint.modality == "deontic" else "fail"), None, witness
    joined = any(semantic_spec.sequence_spans_facts(sequence) for sequence in constraint.sequences)
    if joined and not left and not right:
        return "vacuous", None, ()
    return "pass", None, ()


def indexed_equality_verdict(
    constraint: IRConstraint, snapshot: SnapshotIR
) -> tuple[str, str | None, tuple[tuple[Scalar, ...], ...]]:
    """Production equality decision with typed hash membership (IK4).

    The pure specification's ``equality_witness`` lists left rows missing from
    the right, then right rows missing from the left, each in canonical order;
    this keeps that order. Only membership differs from the quadratic oracle.
    """
    rows = _indexed_set_rows(constraint, snapshot, "equality")
    if isinstance(rows[0], str):
        return rows  # type: ignore[return-value]
    left, right = rows
    left_keys = {_row_key(row) for row in left}
    right_keys = {_row_key(row) for row in right}
    witness = tuple(row for row in left if _row_key(row) not in right_keys) + tuple(
        row for row in right if _row_key(row) not in left_keys
    )
    return _set_family_close(constraint, left, right, witness)


def indexed_exclusion_verdict(
    constraint: IRConstraint, snapshot: SnapshotIR
) -> tuple[str, str | None, tuple[tuple[Scalar, ...], ...]]:
    """Production exclusion decision with typed hash membership (IK4).

    The witness is every left row also on the right, in canonical order, as the
    pure specification's ``exclusion_witness`` lists it.
    """
    rows = _indexed_set_rows(constraint, snapshot, "exclusion")
    if isinstance(rows[0], str):
        return rows  # type: ignore[return-value]
    left, right = rows
    right_keys = {_row_key(row) for row in right}
    witness = tuple(row for row in left if _row_key(row) in right_keys)
    return _set_family_close(constraint, left, right, witness)


def indexed_frequency_verdict(
    constraint: IRConstraint, snapshot: SnapshotIR
) -> tuple[str, str | None, tuple[tuple[Scalar, ...], ...]]:
    """Production frequency decision with one counting pass (IK4).

    The pure specification's ``frequency_result`` counts each canonical group by
    rescanning every key; this counts typed identities once. Groups, their
    canonical order, the interval test and pass-only vacuity are unchanged.
    """
    applicability = semantic_spec.applicability_of(constraint, snapshot)
    if applicability.startswith("vacuous-"):
        return "vacuous", None, ()
    if applicability.startswith("unchecked-"):
        return "unchecked", applicability.removeprefix("unchecked-"), ()
    valid, keys, _ = semantic_spec.counting_projection_rows(constraint, snapshot, "frequency")
    interval = (constraint.minimum, constraint.maximum)
    if not valid or semantic_spec.count_interval_state(0, *interval) == -1:
        return "unchecked", semantic_spec.unchecked_reason_of(constraint, snapshot), ()
    counts: dict[tuple[tuple[str, str], ...], int] = {}
    for key in keys:
        identity = _row_key(key)
        counts[identity] = counts.get(identity, 0) + 1
    witness = tuple(
        group for group in canonical_rows(keys)
        if semantic_spec.count_interval_state(counts[_row_key(group)], *interval) == 0
    )
    if witness:
        return ("warning" if constraint.modality == "deontic" else "fail"), None, witness
    if semantic_spec.joined_pass_is_empty(constraint, snapshot):
        return "vacuous", None, ()
    return "pass", None, ()
