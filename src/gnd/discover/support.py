"""The population view discovery scans, its subjects and its work counter (IK4 §6).

Support is computed here, from the population, because the check report carries
no count field and a ``pass`` can be trivial (spec H2). One subject per family:

| family | subject |
|---|---|
| uniqueness | each distinct key value over the role subset that occurs |
| frequency | each distinct value of the role that occurs (its group) |
| mandatory | each member of the role's object-type roster |
| value | each occurrence in the role's column |
| subset | each distinct value on the subset side |
| equality / exclusion | each distinct value on either side |

Values are compared by the checker's own typed identity
(``semantic_adapter.canonical_scalar`` with the role's resolved primitive), so
``1`` and ``1.0`` are one value here exactly when they are one value to
``gnd check`` (review R1). A cell with no identity (opaque or unrepresentable)
makes the checker refuse any candidate over it; discovery never puts such a
cell into a value domain (review R2).

Ids (IK4-D8) are ``ft<k>#<i>`` for a fact (``k`` the fact type's position in
the model, ``i`` the fact's index in the scanned population) and ``ot<k>#<i>``
for a roster member (``i`` its position in first-appearance order). A subject
spanning several facts is named by its first.
"""

from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass, field
from typing import Any

from gnd.documents import Model
from gnd.model_index import ModelIndex
from gnd.population import Population
from gnd.semantic_adapter import canonical_scalar
from gnd.semantic_ir import Scalar
from gnd.universe import _instance_values_of, resolve_primitive

#: Work counters in report order; ``total`` is their sum (IK4-D7, as corrected).
WORK_COUNTERS = ("uniqueness", "mandatory", "value", "frequency", "sets")

Identity = tuple[str, str]


def identity(value: Any, primitive: str | None) -> Identity | None:
    """The checker's typed identity for one cell, or None when it has none."""
    scalar = canonical_scalar(value, primitive)
    if isinstance(scalar, Scalar):
        return scalar.identity_kind, scalar.token
    return None


def json_native(value: Any) -> bool:
    """A value a constraint's ``allowed`` list can carry unchanged as JSON."""
    if isinstance(value, (bool, str, int)):
        return True
    return isinstance(value, float) and math.isfinite(value)


@dataclass
class Work:
    """Discovery's own scans, one unit per fact row or roster member visited.

    The single ``gnd check`` run is outside it; the checker has its own guards.
    """

    counts: dict[str, int] = field(default_factory=lambda: dict.fromkeys(WORK_COUNTERS, 0))

    def charge(self, counter: str, units: int) -> None:
        self.counts[counter] += units

    def report(self, ceiling: int) -> dict[str, int]:
        return {**self.counts, "total": sum(self.counts.values()), "ceiling": ceiling}


@dataclass(frozen=True)
class Role:
    fact_type: str
    position: int  # the fact type's position in the model (k of ft<k>)
    name: str
    object_type: str
    primitive: str | None


@dataclass(frozen=True)
class Subjects:
    """One candidate's subjects: total count, violators, and their first-fact ids."""

    count: int
    violations: int
    examples: tuple[str, ...]  # satisfying subjects, first 256
    counterexamples: tuple[str, ...]  # violating subjects, first 32


EXAMPLES_MAX = 256
COUNTEREXAMPLES_MAX = 32


def _subjects(order: list[tuple[str, bool]]) -> Subjects:
    """``order`` lists (id, violates) per subject in first-appearance order."""
    satisfying = [ident for ident, bad in order if not bad]
    violating = [ident for ident, bad in order if bad]
    return Subjects(
        count=len(order),
        violations=len(violating),
        examples=tuple(satisfying[:EXAMPLES_MAX]),
        counterexamples=tuple(violating[:COUNTEREXAMPLES_MAX]),
    )


class PopulationView:
    """Read-only access to the model's roles and the population's columns."""

    def __init__(self, model: Model, population: Population, work: Work) -> None:
        self.model = model
        self.population = population
        self.work = work
        index = ModelIndex.for_model(model)
        role_types = index.role_object_types()
        self.fact_type_ids = list(role_types)
        self.position = {ft: k for k, ft in enumerate(self.fact_type_ids)}
        self.roles: dict[str, list[Role]] = {
            ft: [
                Role(ft, self.position[ft], name, object_type,
                     resolve_primitive(object_type, model))
                for name, object_type in roles.items()
            ]
            for ft, roles in role_types.items()
        }
        self.object_type_ids = list(index.object_types_by_id())
        self.object_position = {ot: k for k, ot in enumerate(self.object_type_ids)}
        self._rosters: dict[str, list[Identity]] = {}

    def rows(self, fact_type: str) -> list[dict[str, Any]]:
        rows = self.population.facts.get(fact_type) or []
        return [row for row in rows if isinstance(row, dict)]

    def row_count(self, fact_type: str) -> int:
        return len(self.rows(fact_type))

    def fact_id(self, fact_type: str, index: int) -> str:
        return f"ft{self.position[fact_type]}#{index}"

    def column(self, role: Role) -> list[tuple[int, Any, Identity | None]]:
        """(fact index, value, identity) for every row that carries the role."""
        return [
            (index, row[role.name], identity(row[role.name], role.primitive))
            for index, row in enumerate(self.rows(role.fact_type))
            if role.name in row
        ]

    def roster(self, object_type: str) -> list[Identity]:
        """The closed-world roster as identities, in first-appearance order."""
        if object_type not in self._rosters:
            primitive = resolve_primitive(object_type, self.model)
            values = _instance_values_of(object_type, self.model, self.population)
            keys = (identity(value, primitive) for value in values)
            self._rosters[object_type] = list(dict.fromkeys(k for k in keys if k is not None))
        return self._rosters[object_type]

    # -- per-family subjects -------------------------------------------------

    def uniqueness(self, fact_type: str, roles: tuple[str, ...]) -> Subjects:
        rows = self.rows(fact_type)
        self.work.charge("uniqueness", len(rows))
        by_name = {role.name: role for role in self.roles[fact_type]}
        first: dict[tuple[Identity | None, ...], int] = {}
        counts: Counter[tuple[Identity | None, ...]] = Counter()
        for index, row in enumerate(rows):
            if not all(name in row for name in roles):
                continue
            key = tuple(identity(row[name], by_name[name].primitive) for name in roles)
            if None in key:
                continue  # the checker refuses the candidate as unchecked
            first.setdefault(key, index)
            counts[key] += 1
        return _subjects(
            [(self.fact_id(fact_type, index), counts[key] > 1) for key, index in first.items()]
        )

    def mandatory(self, role: Role) -> Subjects:
        column = self.column(role)
        roster = self.roster(role.object_type)
        self.work.charge("mandatory", len(self.rows(role.fact_type)) + len(roster))
        players = {key for _, _, key in column if key is not None}
        k = self.object_position[role.object_type]
        return _subjects(
            [(f"ot{k}#{i}", member not in players) for i, member in enumerate(roster)]
        )

    def value_domain(self, role: Role) -> tuple[list[Any], list[int], bool]:
        """Distinct values (one representative per identity, sorted), every
        occurrence's fact index, and whether every cell can enter ``allowed``."""
        column = self.column(role)
        self.work.charge("value", len(self.rows(role.fact_type)))
        distinct: dict[Identity, Any] = {}
        representable = True
        for _, value, key in column:
            if key is None or not json_native(value):
                representable = False
                continue
            distinct.setdefault(key, value)
        return _sorted_values(list(distinct.values())), [i for i, _, _ in column], representable

    def groups(self, role: Role) -> tuple[Counter[Identity], dict[Identity, int]]:
        """Group counts per distinct identity, and each group's first fact index."""
        column = self.column(role)
        self.work.charge("frequency", len(self.rows(role.fact_type)))
        counts: Counter[Identity] = Counter()
        first: dict[Identity, int] = {}
        for index, _, key in column:
            if key is None:
                continue
            counts[key] += 1
            first.setdefault(key, index)
        return counts, first

    def side(self, role: Role) -> dict[Identity, str]:
        """Distinct identities of one set-comparison side -> first fact id."""
        firsts: dict[Identity, str] = {}
        for index, _, key in self.column(role):
            if key is not None:
                firsts.setdefault(key, self.fact_id(role.fact_type, index))
        return firsts

    def charge_pair(self, a: Role, b: Role) -> None:
        self.work.charge("sets", self.row_count(a.fact_type) + self.row_count(b.fact_type))


def _sorted_values(values: list[Any]) -> list[Any]:
    """Numbers numerically, then strings, then booleans."""

    def order(value: Any) -> tuple[int, Any]:
        if isinstance(value, bool):
            return (2, value)
        if isinstance(value, (int, float)):
            return (0, value)
        return (1, value)

    return sorted(values, key=order)


def subset_subjects(sub: dict[Identity, str], sup: dict[Identity, str]) -> Subjects:
    return _subjects([(ident, key not in sup) for key, ident in sub.items()])


def equality_subjects(a: dict[Identity, str], b: dict[Identity, str]) -> Subjects:
    order = list(a.items()) + [(k, v) for k, v in b.items() if k not in a]
    return _subjects([(ident, (key in a) != (key in b)) for key, ident in order])


def exclusion_subjects(a: dict[Identity, str], b: dict[Identity, str]) -> Subjects:
    """Both sides must be non-empty, else there is nothing to exclude (support 0)."""
    if not a or not b:
        return Subjects(0, 0, (), ())
    order = list(a.items()) + [(k, v) for k, v in b.items() if k not in a]
    return _subjects([(ident, key in a and key in b) for key, ident in order])


def work_ceiling(view: PopulationView, fact_types: list[str], pairs: int) -> int:
    """The corrected IK4-D7 bound (owner ruling 2026-10-25, review R11).

    W <= sum over scanned fact types of n_ft * (K_ft + 3 * a_ft)
         + sum over scanned roles of |roster(ot)|
         + 2 * P * R_max
    with K_ft the uniqueness key candidates (all proper subsets up to arity 4,
    sizes 1 and 2 above), a_ft the arity, P the pairs compared and R_max the
    largest scanned fact type's row count.
    """
    total = 0
    largest = 0
    for ft in fact_types:
        rows = view.row_count(ft)
        largest = max(largest, rows)
        arity = len(view.roles[ft])
        keys = 2**arity - 2 if arity <= 4 else arity + arity * (arity - 1) // 2
        total += rows * (keys + 3 * arity)
        total += sum(len(view.roster(role.object_type)) for role in view.roles[ft])
    return total + 2 * pairs * largest
