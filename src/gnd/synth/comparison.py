"""Canonical value-comparison operands for synthesis and measurement.

This is deliberately independent of :mod:`gnd.checker`: synthesis ground truth
must not be derived from the implementation it measures.  It only normalizes the
model's documented tagged and legacy operand syntax and resolves declared
primitive types through the model layer.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, replace
from typing import Any

from gnd import popvalidate
from gnd.model import Model

_CLOCK_OPERAND = re.compile(
    r"^(now|today|current_date|current_time|current_timestamp)(\(\))?$",
    re.IGNORECASE,
)
_UNTYPEABLE = object()

_REVERSED_OPERATOR = {
    "<": ">",
    "<=": ">=",
    "=": "=",
    ">=": "<=",
    ">": "<",
    "!=": "!=",
}


@dataclass(frozen=True)
class ComparisonOperand:
    """One explicit role, literal, cross-role, clock, or invalid operand."""

    kind: str
    raw: Any
    role: str | None = None
    fact_type: str | None = None
    object_type: str | None = None
    primitive: str | None = None
    value: Any = _UNTYPEABLE


def literal_operand(operand: Any, primitive: str | None, *, legacy: bool = True) -> Any:
    """Interpret a non-role operand in the compared role's primitive domain."""
    if primitive in ("String", "Binary", "Date", "DateTime"):
        return operand if isinstance(operand, str) else _UNTYPEABLE
    if primitive == "Boolean":
        if isinstance(operand, bool):
            return operand
        if legacy and isinstance(operand, str) and operand.lower() in ("true", "false"):
            return operand.lower() == "true"
        return _UNTYPEABLE
    if primitive == "Integer":
        if isinstance(operand, int) and not isinstance(operand, bool):
            return operand
        if legacy and isinstance(operand, str):
            try:
                return int(operand)
            except ValueError:
                return _UNTYPEABLE
        return _UNTYPEABLE
    if primitive in ("Float", "Number"):
        if isinstance(operand, (int, float)) and not isinstance(operand, bool):
            return operand
        if legacy and isinstance(operand, str):
            try:
                return float(operand)
            except ValueError:
                return _UNTYPEABLE
        return _UNTYPEABLE
    return _UNTYPEABLE


def normalize_operands(
    model: Model,
    constraint: dict[str, Any],
    fact_type: dict[str, Any] | None,
) -> tuple[ComparisonOperand, ComparisonOperand]:
    """Normalize both comparison operands without consulting checker behavior."""
    raw_operands = (constraint.get("role_a"), constraint.get("role_b"))
    if fact_type is None:
        fact_types = {str(candidate.get("id")): candidate for candidate in model.fact_types or []}
        normalized: list[ComparisonOperand] = []
        for raw in raw_operands:
            if not isinstance(raw, dict) or "fact_type" not in raw or "role" not in raw:
                normalized.append(ComparisonOperand("invalid", raw))
                continue
            ftid, role_name = str(raw["fact_type"]), str(raw["role"])
            target_ft = fact_types.get(ftid)
            target_role = next(
                (
                    role
                    for role in (target_ft or {}).get("roles") or []
                    if str(role.get("role_name")) == role_name
                ),
                None,
            )
            if target_role is None:
                normalized.append(ComparisonOperand("invalid", raw))
                continue
            oid = str(target_role.get("object_type"))
            normalized.append(
                ComparisonOperand(
                    "cross-role",
                    raw,
                    role=role_name,
                    fact_type=ftid,
                    object_type=oid,
                    primitive=popvalidate.resolve_primitive(oid, model),
                )
            )
        return normalized[0], normalized[1]

    roles = {
        str(role.get("role_name")): str(role.get("object_type"))
        for role in fact_type.get("roles") or []
    }
    classified: list[ComparisonOperand] = []
    tagged_literal: list[bool] = []
    for raw in raw_operands:
        if isinstance(raw, dict) and "role" in raw and "literal" not in raw:
            role_name = str(raw["role"])
            oid = roles.get(role_name)
            classified.append(
                ComparisonOperand(
                    "role" if oid is not None else "invalid",
                    raw,
                    role=role_name if oid is not None else None,
                    object_type=oid,
                    primitive=(
                        popvalidate.resolve_primitive(oid, model) if oid is not None else None
                    ),
                )
            )
            tagged_literal.append(False)
        elif isinstance(raw, dict) and "literal" in raw and "role" not in raw:
            classified.append(ComparisonOperand("literal", raw, value=raw["literal"]))
            tagged_literal.append(True)
        elif isinstance(raw, str) and raw in roles:
            oid = roles[raw]
            classified.append(
                ComparisonOperand(
                    "role",
                    raw,
                    role=raw,
                    object_type=oid,
                    primitive=popvalidate.resolve_primitive(oid, model),
                )
            )
            tagged_literal.append(False)
        elif isinstance(raw, str) and _CLOCK_OPERAND.match(raw):
            classified.append(ComparisonOperand("clock", raw, value=raw))
            tagged_literal.append(False)
        elif isinstance(raw, (str, int, float, bool)) and not isinstance(raw, dict):
            classified.append(ComparisonOperand("literal", raw, value=raw))
            tagged_literal.append(False)
        else:
            classified.append(ComparisonOperand("invalid", raw))
            tagged_literal.append(False)

    for index, operand in enumerate(classified):
        if operand.kind != "literal":
            continue
        other = classified[1 - index]
        primitive = other.primitive if other.kind == "role" else None
        raw_literal = operand.value
        classified[index] = replace(
            operand,
            primitive=primitive,
            value=literal_operand(raw_literal, primitive, legacy=not tagged_literal[index]),
        )
    return classified[0], classified[1]


def role_literal_operands(
    model: Model,
    constraint: dict[str, Any],
    fact_type: dict[str, Any],
) -> tuple[ComparisonOperand, ComparisonOperand, str] | None:
    """Return ``(role, literal, role-oriented operator)`` for either side order."""
    left, right = normalize_operands(model, constraint, fact_type)
    operator = str(constraint.get("operator") or "")
    if left.kind == "role" and right.kind == "literal" and right.value is not _UNTYPEABLE:
        return left, right, operator
    if left.kind == "literal" and left.value is not _UNTYPEABLE and right.kind == "role":
        return right, left, _REVERSED_OPERATOR.get(operator, operator)
    return None


def reverse_operator(operator: str) -> str:
    return _REVERSED_OPERATOR.get(operator, operator)


__all__ = [
    "_CLOCK_OPERAND",
    "_UNTYPEABLE",
    "ComparisonOperand",
    "literal_operand",
    "normalize_operands",
    "reverse_operator",
    "role_literal_operands",
]
