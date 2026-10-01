"""Conjunctive value-domain semantics shared by synthesis components.

Each ``value`` constraint is one predicate. Multiple constraints governing the
same object/role are conjoined, while a single ``ranges`` field is a union of
intervals. This module owns collection, membership, interval intersection, and
generation so the pool gate, pool builder, assembler, and mutator cannot drift.
"""

from __future__ import annotations

from random import Random
from typing import Any

from gnd.model import Model
from gnd.synth.identity import scalar_identity
from gnd.synth.values import make_value


class EmptyValueDomain(ValueError):
    """The intersection of all governing value constraints is empty."""


def _iter_constraints(model: Model):
    for fact_type in model.fact_types or []:
        for constraint in fact_type.get("constraints") or []:
            yield constraint
    for constraint in model.constraints or []:
        yield constraint


def object_value_constraints(model: Model) -> dict[str, list[dict[str, Any]]]:
    """All object-scoped value constraints, preserving declaration order."""
    result: dict[str, list[dict[str, Any]]] = {}
    for constraint in _iter_constraints(model):
        if constraint.get("type") != "value" or constraint.get("role_ref") is not None:
            continue
        oid = constraint.get("object_type")
        if oid is not None:
            result.setdefault(str(oid), []).append(constraint)
    return result


def governing_value_constraints(
    model: Model, oid: str, *, ftid: str | None = None, role_name: str | None = None
) -> list[dict[str, Any]]:
    """All object- and optional role-scoped predicates governing one draw."""
    constraints = list(object_value_constraints(model).get(str(oid), []))
    if ftid is None or role_name is None:
        return constraints
    for constraint in _iter_constraints(model):
        if constraint.get("type") != "value":
            continue
        role_ref = constraint.get("role_ref")
        if not isinstance(role_ref, dict):
            continue
        if (
            str(role_ref.get("fact_type")) == str(ftid)
            and str(role_ref.get("role")) == str(role_name)
        ):
            constraints.append(constraint)
    return constraints


def _ranges(constraint: dict[str, Any]) -> list[dict[str, Any]]:
    if constraint.get("ranges") is not None:
        return [dict(value_range) for value_range in constraint.get("ranges") or []]
    if constraint.get("range") is not None:
        return [dict(constraint["range"])]
    return []


def _in_range(value: Any, value_range: dict[str, Any]) -> bool:
    low = value_range.get("min")
    high = value_range.get("max")
    try:
        if low is not None:
            if value_range.get("min_inclusive", True):
                if value < low:
                    return False
            elif value <= low:
                return False
        if high is not None:
            if value_range.get("max_inclusive", True):
                if value > high:
                    return False
            elif value >= high:
                return False
    except TypeError:
        return False
    return True


def constraint_accepts(value: Any, constraint: dict[str, Any]) -> bool:
    allowed = constraint.get("allowed")
    if allowed is not None:
        allowed_keys = {scalar_identity(member) for member in allowed}
        return scalar_identity(value) in allowed_keys
    ranges = _ranges(constraint)
    return bool(ranges) and any(_in_range(value, value_range) for value_range in ranges)


def value_satisfies_all(value: Any, constraints: list[dict[str, Any]]) -> bool:
    return all(constraint_accepts(value, constraint) for constraint in constraints)


def _intersect_pair(
    left: dict[str, Any], right: dict[str, Any]
) -> dict[str, Any] | None:
    lows = [
        (candidate.get("min"), candidate.get("min_inclusive", True))
        for candidate in (left, right)
        if candidate.get("min") is not None
    ]
    highs = [
        (candidate.get("max"), candidate.get("max_inclusive", True))
        for candidate in (left, right)
        if candidate.get("max") is not None
    ]
    try:
        low = max((value for value, _inclusive in lows), default=None)
        high = min((value for value, _inclusive in highs), default=None)
    except TypeError:
        return None
    low_inclusive = all(inclusive for value, inclusive in lows if value == low)
    high_inclusive = all(inclusive for value, inclusive in highs if value == high)
    if low is not None and high is not None and (
        low > high or (low == high and not (low_inclusive and high_inclusive))
    ):
        return None
    result: dict[str, Any] = {}
    if low is not None:
        result["min"] = low
        result["min_inclusive"] = low_inclusive
    if high is not None:
        result["max"] = high
        result["max_inclusive"] = high_inclusive
    return result


def intersected_ranges(constraints: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Intersection of constraints, retaining each constraint's range union."""
    result: list[dict[str, Any]] = [{}]
    for constraint in constraints:
        alternatives = _ranges(constraint)
        if not alternatives:
            continue
        intersections = [
            intersection
            for current in result
            for alternative in alternatives
            if (intersection := _intersect_pair(current, alternative)) is not None
        ]
        result = intersections
        if not result:
            break
    return result


def draw_value_for_constraints(
    primitive: str,
    rng: Random,
    constraints: list[dict[str, Any]],
) -> Any:
    """Draw from the conjunctive domain or raise :class:`EmptyValueDomain`."""
    enums = [constraint.get("allowed") for constraint in constraints if "allowed" in constraint]
    if enums:
        candidates = [
            value
            for value in enums[0]
            if value_satisfies_all(value, constraints)
        ]
        if not candidates:
            raise EmptyValueDomain("governing value constraints have an empty intersection")
        return rng.choice(candidates)

    ranges = intersected_ranges(constraints)
    if constraints and not ranges:
        raise EmptyValueDomain("governing value ranges have an empty intersection")
    if not constraints:
        return make_value(primitive, rng)
    for _attempt in range(200):
        candidate = make_value(primitive, rng, value_range=rng.choice(ranges))
        if value_satisfies_all(candidate, constraints):
            return candidate
    raise EmptyValueDomain(
        "could not draw a value from the governing constraint intersection"
    )
