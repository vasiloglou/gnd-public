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

Ids (IK4-D8) are ``ft<k>#<i>`` for a fact (``k`` the fact type's position in
the model, ``i`` the fact's index in the population) and ``ot<k>#<i>`` for a
roster member (``i`` its position in first-appearance order). A subject
spanning several facts is named by its first.
"""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass, field
from typing import Any

from gnd.documents import Model
from gnd.model_index import ModelIndex
from gnd.population import Population
from gnd.universe import _instance_values_of

#: Work counters in report order; ``total`` is their sum (IK4-D7).
WORK_COUNTERS = ("uniqueness", "mandatory", "value", "frequency", "sets")


def cell_key(value: Any) -> str:
    """A canonical, type-preserving identity for one cell (``1`` is not ``True``)."""
    return json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False)


@dataclass
class Work:
    """Discovery's own scans, one unit per fact row or roster member visited.

    The single ``gnd check`` run is outside it; the checker has its own guards.
    """

    counts: dict[str, int] = field(default_factory=lambda: dict.fromkeys(WORK_COUNTERS, 0))

    def charge(self, counter: str, units: int) -> None:
        self.counts[counter] += units

    def report(self) -> dict[str, int]:
        return {**self.counts, "total": sum(self.counts.values())}


@dataclass(frozen=True)
class Role:
    fact_type: str
    position: int  # the fact type's position in the model (k of ft<k>)
    name: str
    object_type: str


@dataclass(frozen=True)
class Subjects:
    """One candidate's subjects: total count, violators, and their first-fact ids."""

    count: int
    violations: int
    examples: tuple[str, ...]  # satisfying subjects, first 256
    counterexamples: tuple[str, ...]  # violating subjects, first 32


def _subjects(order: list[tuple[str, bool]]) -> Subjects:
    """``order`` lists (id, violates) per subject in first-appearance order."""
    satisfying = [ident for ident, bad in order if not bad]
    violating = [ident for ident, bad in order if bad]
    return Subjects(
        count=len(order),
        violations=len(violating),
        examples=tuple(satisfying[:256]),
        counterexamples=tuple(violating[:32]),
    )


class PopulationView:
    """Read-only access to the model's roles and the population's columns."""

    def __init__(self, model: Model, population: Population, work: Work) -> None:
        self.model = model
        self.population = population
        self.work = work
        index = ModelIndex.for_model(model)
        self.fact_type_ids = list(index.role_object_types())
        self.position = {ft: k for k, ft in enumerate(self.fact_type_ids)}
        self.roles: dict[str, list[Role]] = {
            ft: [
                Role(ft, self.position[ft], name, object_type)
                for name, object_type in roles.items()
            ]
            for ft, roles in index.role_object_types().items()
        }
        self.object_type_ids = list(index.object_types_by_id())
        self.object_position = {ot: k for k, ot in enumerate(self.object_type_ids)}
        self._rosters: dict[str, list[str]] = {}

    def rows(self, fact_type: str) -> list[dict[str, Any]]:
        rows = self.population.facts.get(fact_type) or []
        return [row for row in rows if isinstance(row, dict)]

    def row_count(self, fact_type: str) -> int:
        return len(self.rows(fact_type))

    def fact_id(self, fact_type: str, index: int) -> str:
        return f"ft{self.position[fact_type]}#{index}"

    def column(self, role: Role) -> list[tuple[int, Any]]:
        """(fact index, value) for every row that carries the role."""
        return [
            (index, row[role.name])
            for index, row in enumerate(self.rows(role.fact_type))
            if role.name in row
        ]

    def roster(self, object_type: str) -> list[str]:
        """The closed-world roster as cell keys, in first-appearance order."""
        if object_type not in self._rosters:
            values = _instance_values_of(object_type, self.model, self.population)
            self._rosters[object_type] = list(dict.fromkeys(cell_key(v) for v in values))
        return self._rosters[object_type]

    # -- per-family subjects -------------------------------------------------

    def uniqueness(self, fact_type: str, roles: tuple[str, ...]) -> Subjects:
        rows = self.rows(fact_type)
        self.work.charge("uniqueness", len(rows))
        first: dict[tuple[str, ...], int] = {}
        counts: Counter[tuple[str, ...]] = Counter()
        for index, row in enumerate(rows):
            if not all(name in row for name in roles):
                continue
            key = tuple(cell_key(row[name]) for name in roles)
            first.setdefault(key, index)
            counts[key] += 1
        return _subjects(
            [(self.fact_id(fact_type, index), counts[key] > 1) for key, index in first.items()]
        )

    def mandatory(self, role: Role) -> Subjects:
        column = self.column(role)
        roster = self.roster(role.object_type)
        self.work.charge("mandatory", len(self.rows(role.fact_type)) + len(roster))
        players = {cell_key(value) for _, value in column}
        k = self.object_position[role.object_type]
        return _subjects(
            [(f"ot{k}#{i}", member not in players) for i, member in enumerate(roster)]
        )

    def value_domain(self, role: Role) -> tuple[list[Any], list[int]]:
        """Sorted distinct values and every occurrence's fact index."""
        column = self.column(role)
        self.work.charge("value", len(self.rows(role.fact_type)))
        distinct: dict[str, Any] = {}
        for _, value in column:
            distinct.setdefault(cell_key(value), value)
        return _sorted_values(list(distinct.values())), [index for index, _ in column]

    def groups(self, role: Role) -> tuple[Counter[str], dict[str, int]]:
        """Group counts per distinct value, and each group's first fact index."""
        column = self.column(role)
        self.work.charge("frequency", len(self.rows(role.fact_type)))
        counts: Counter[str] = Counter()
        first: dict[str, int] = {}
        for index, value in column:
            key = cell_key(value)
            counts[key] += 1
            first.setdefault(key, index)
        return counts, first

    def side(self, role: Role) -> dict[str, str]:
        """Distinct values of one set-comparison side -> first fact id."""
        firsts: dict[str, str] = {}
        for index, value in self.column(role):
            firsts.setdefault(cell_key(value), self.fact_id(role.fact_type, index))
        return firsts

    def charge_pair(self, a: Role, b: Role) -> None:
        self.work.charge("sets", self.row_count(a.fact_type) + self.row_count(b.fact_type))


def _sorted_values(values: list[Any]) -> list[Any]:
    """Numbers numerically, then strings, then anything else by canonical key."""

    def order(value: Any) -> tuple[int, Any]:
        if isinstance(value, bool):
            return (2, cell_key(value))
        if isinstance(value, (int, float)):
            return (0, value)
        if isinstance(value, str):
            return (1, value)
        return (2, cell_key(value))

    return sorted(values, key=order)


def subset_subjects(sub: dict[str, str], sup: dict[str, str]) -> Subjects:
    return _subjects([(ident, key not in sup) for key, ident in sub.items()])


def equality_subjects(a: dict[str, str], b: dict[str, str]) -> Subjects:
    order = list(a.items()) + [(k, v) for k, v in b.items() if k not in a]
    return _subjects([(ident, (key in a) != (key in b)) for key, ident in order])


def exclusion_subjects(a: dict[str, str], b: dict[str, str]) -> Subjects:
    """Both sides must be non-empty, else there is nothing to exclude (support 0)."""
    if not a or not b:
        return Subjects(0, 0, (), ())
    order = list(a.items()) + [(k, v) for k, v in b.items() if k not in a]
    return _subjects([(ident, key in a and key in b) for key, ident in order])
