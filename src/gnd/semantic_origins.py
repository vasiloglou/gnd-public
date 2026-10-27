"""Ephemeral ordered witness-origin indexes over typed snapshot observations."""
from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import dataclass, field

from gnd.semantic_adapter import ValueOrigin
from gnd.semantic_ir import Scalar
from gnd.semantic_rows import scalar_identity

PublicScalar = bool | int | float | str | None
Role = str | None


@dataclass(slots=True)
class _Bucket:
    indices: list[int] = field(default_factory=list)
    unambiguous: bool | None = None


class OriginIndex:
    def __init__(self, origins: Sequence[ValueOrigin]) -> None:
        self.origins = origins
        self.values: list[ValueOrigin] = []
        self.exact: dict[tuple[int, Role], _Bucket] = {}
        self.canonical: dict[tuple[tuple[str, str], Role], _Bucket] = {}
        self.paths: dict[int, list[tuple[str | int, ...]]] = {}
        for index, origin in enumerate(origins):
            self.values.append(origin)
            identity = id(origin.scalar)
            path = origin.path
            if len(path) == 4 and path[0] == "facts":
                self.paths.setdefault(identity, []).append(path)
            admissible = (
                origin.source == "admitted"
                and origin.derivation_fact_type is None
                and not origin.dependency_paths
            ) or (
                origin.source == "derived"
                and origin.derivation_fact_type is not None
                and bool(origin.dependency_paths)
            )
            if not admissible:
                continue
            roles: tuple[Role, ...] = (None,)
            if path and isinstance(path[-1], str):
                roles += (path[-1],)
            canonical = scalar_identity(origin.scalar)
            for role in roles:
                self.exact.setdefault((identity, role), _Bucket()).indices.append(index)
                self.canonical.setdefault((canonical, role), _Bucket()).indices.append(index)

    def coordinates(self, witness: tuple[tuple[Scalar, ...], ...]) -> set[tuple[str, int]]:
        result: set[tuple[str, int]] = set()
        for identity in {id(value) for row in witness for value in row}:
            for path in self.paths.get(identity, ()):
                result.add((str(path[1]), int(path[2])))
        return result


@dataclass(slots=True)
class OriginSelection:
    index: OriginIndex
    used: set[int]
    cursors: dict[int, int] = field(default_factory=dict)
    # Object types a role-less witness may take its spelling from (IK4-Q4).
    scope: frozenset[str] = frozenset()
    scoped: dict[int, tuple[list[int], int]] = field(default_factory=dict)

    def _take(self, bucket: _Bucket) -> PublicScalar:
        cursor = self.cursors.get(id(bucket), 0)
        while cursor < len(bucket.indices) and bucket.indices[cursor] in self.used:
            cursor += 1
        self.cursors[id(bucket)] = cursor
        if cursor == len(bucket.indices):
            return self.index.values[bucket.indices[0]].admitted_value
        index = bucket.indices[cursor]
        self.used.add(index)
        self.cursors[id(bucket)] = cursor + 1
        return self.index.values[index].admitted_value

    def value(self, scalar: Scalar, witness_key: str | None) -> tuple[bool, PublicScalar]:
        role = None if witness_key is None or witness_key.startswith("$") else witness_key
        exact = self.index.exact.get((id(scalar), role))
        if exact is not None:
            return True, self._take(exact)
        bucket = self.index.canonical.get((scalar_identity(scalar), role))
        if bucket is None:
            return False, None
        if bucket.unambiguous is None:
            spellings = {
                (type(self.index.values[i].admitted_value).__name__,
                 json.dumps(self.index.values[i].admitted_value, ensure_ascii=False))
                for i in bucket.indices
            }
            bucket.unambiguous = len(spellings) == 1
        if bucket.unambiguous:
            return True, self._take(bucket)
        if role is None and self.scope:
            return self._take_scoped(bucket)
        return False, None

    def _take_scoped(self, bucket: _Bucket) -> tuple[bool, PublicScalar]:
        """The first unused origin of the witness's subject types, in observation order.

        Two spellings of one number (``4`` and ``4.0``) make the bucket
        ambiguous. A roster witness is a value of its subject type, so only
        that type's origins may spell it, and among them population order is
        deterministic.
        """
        key = id(bucket)
        if key not in self.scoped:
            self.scoped[key] = (
                [i for i in bucket.indices if self.index.values[i].object_type in self.scope],
                0,
            )
        candidates, cursor = self.scoped[key]
        if not candidates:
            return False, None
        # A cursor, as in _take, keeps a long witness linear in its bucket.
        while cursor < len(candidates) and candidates[cursor] in self.used:
            cursor += 1
        if cursor == len(candidates):
            self.scoped[key] = (candidates, cursor)
            return True, self.index.values[candidates[0]].admitted_value
        chosen = candidates[cursor]
        self.used.add(chosen)
        self.scoped[key] = (candidates, cursor + 1)
        return True, self.index.values[chosen].admitted_value
