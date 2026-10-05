"""RF3 shared dependency home; algorithms retain predecessor semantics."""
from __future__ import annotations

from collections.abc import Sequence
from functools import cmp_to_key

from gnd import semantic_spec
from gnd.semantic_ir import Scalar


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
