"""Bounded Gregorian evaluation at the guarded-comparison boundary."""

from __future__ import annotations

from fractions import Fraction
from typing import Any

from gnd.semantic_ir import IRConstraint, IROperand, Scalar, SnapshotIR
from gnd.terms import TEMPORAL_FUNCTIONS, evaluate_term


def temporal_operand(operand: IROperand) -> bool:
    return (
        operand.primitive == "Duration"
        or operand.function in TEMPORAL_FUNCTIONS
        or operand.tagged
        or any(temporal_operand(child) for child in operand.arguments)
    )


def _value(scalar: Scalar | None) -> Any:
    if scalar is None:
        return None
    if scalar.kind == "number":
        value = Fraction(scalar.num, scalar.den)
        return value.numerator if value.denominator == 1 else value
    if scalar.kind == "boolean":
        return scalar.token == "true"
    return scalar.token


def _syntax(operand: IROperand) -> Any:
    if operand.kind == "variable":
        return operand.variable
    if operand.kind == "function":
        return {"fn": operand.function, "args": [_syntax(child) for child in operand.arguments]}
    value = _value(operand.literal)
    if operand.tagged:
        return {"date" if operand.primitive == "Date" else "duration_days": value}
    return value


def evaluate_temporal_guard(constraint: IRConstraint, snapshot: SnapshotIR):
    """Stream connected joins; stop before the 10,001st function application.

    Indexes contain input rows only. DFS never materializes an intermediate
    cross product. An opaque join cell is a possible match and preserves
    unknown precedence after reaching the consequent.
    """
    if (
        constraint.family != "guarded"
        or constraint.variant != "comparison"
        or not any(temporal_operand(operand) for operand in constraint.operands)
    ):
        return None
    from gnd import semantic_spec
    from gnd.semantic_adapter import canonical_scalar

    facts = {fact.id: fact for fact in snapshot.fact_types}
    relations = {relation.fact_type: relation for relation in snapshot.relations}
    # Preserve the existing any-empty-antecedent vacuity rule.
    if any(not relations[atom.fact_type].rows for atom in constraint.antecedent):
        return None
    candidates = []
    variables = []
    uncertainties = {}
    for atom in constraint.antecedent:
        fact = facts[atom.fact_type]
        columns = {role.name: position for position, role in enumerate(fact.roles)}
        rows = []
        distinct = set()
        names = {term.variable for _, term in atom.bindings if term.kind == "variable"}
        for row in relations[atom.fact_type].rows:
            candidate = {}
            uncertain = None
            for role, term in atom.bindings:
                value = row[columns[role]]
                if value is None:
                    uncertain = uncertain or (
                        "term:opaque-date-operand"
                        if fact.roles[columns[role]].primitive in {"Date", "Duration"}
                        else "opaque-value"
                    )
                if term.kind == "literal":
                    if value is not None and not semantic_spec.scalar_identical(
                        value, term.literal
                    ):
                        break
                elif term.variable in candidate:
                    previous = candidate[term.variable]
                    if (
                        previous is not None
                        and value is not None
                        and not semantic_spec.scalar_identical(previous, value)
                    ):
                        break
                    candidate[term.variable] = previous if previous is not None else value
                else:
                    candidate[term.variable] = value
            else:
                key = (
                    tuple(
                        sorted(
                            (name, None if value is None else (value.identity_kind, value.token))
                            for name, value in candidate.items()
                        )
                    ),
                    uncertain,
                )
                if key not in distinct:
                    distinct.add(key)
                    rows.append(candidate)
                    uncertainties[id(candidate)] = uncertain
        candidates.append(rows)
        variables.append(names)
    order = [0]
    bound = set(variables[0])
    remaining = list(range(1, len(candidates)))
    while remaining:
        selected = next((index for index in remaining if bound & variables[index]), None)
        if selected is None:
            return "unchecked", "join-disconnected", ()
        order.append(selected)
        bound |= variables[selected]
        remaining.remove(selected)

    def identity(value):
        return None if value is None else (value.identity_kind, value.token)

    indexes = []
    bound = set()
    for selected in order:
        shared = tuple(sorted(bound & variables[selected]))
        index = {}
        opaque = []
        for candidate in candidates[selected]:
            key = tuple(identity(candidate[name]) for name in shared)
            if None in key:
                opaque.append(candidate)
            else:
                index.setdefault(key, []).append(candidate)
        indexes.append((shared, index, opaque))
        bound |= variables[selected]

    def walk(position, binding, uncertain=None):
        if position == len(order):
            yield binding, uncertain
            return
        shared, index, opaque = indexes[position]
        key = tuple(identity(binding[name]) for name in shared)
        probes = candidates[order[position]] if None in key else (*index.get(key, ()), *opaque)
        for candidate in probes:
            if any(
                name in binding
                and value is not None
                and binding[name] is not None
                and not semantic_spec.scalar_identical(value, binding[name])
                for name, value in candidate.items()
            ):
                continue
            merged = dict(binding)
            for name, value in candidate.items():
                merged[name] = merged.get(name) if merged.get(name) is not None else value
            yield from walk(position + 1, merged, uncertain or uncertainties[id(candidate)])

    names = semantic_spec.guarded_variable_names(constraint)
    syntax = [_syntax(operand) for operand in constraint.operands]
    work = [0]
    seen = set()
    violations = []
    unknown = None
    for binding, uncertain in walk(0, {}):
        row = tuple(binding[name] for name in names)
        seen_key = (row, uncertain)
        if seen_key in seen:
            continue
        seen.add(seen_key)
        raw = {name.removeprefix("$"): _value(value) for name, value in binding.items()}
        results = [evaluate_term(term, raw, temporal_work=work) for term in syntax]
        reason = next((result.reason for result in results if not result.available), None)
        if reason == "term:temporal-work-limit":
            return "unchecked", reason, ()
        if reason or uncertain:
            unknown = unknown or reason or uncertain
            continue
        values = [
            canonical_scalar(result.value, operand.primitive)
            for result, operand in zip(results, constraint.operands, strict=True)
        ]
        state = (
            -1
            if any(value is None for value in values)
            else semantic_spec.comparison_pair_state(values[0], values[1], constraint.operator)
        )
        if state < 0:
            unknown = unknown or "term:opaque-date-operand"
        elif state == 0:
            violations.append(row)
    if unknown:
        return "unchecked", unknown, ()
    if not violations:
        return "pass", None, ()
    from gnd.correspondence import _canonical_rows

    witness = _canonical_rows(violations)
    return "warning" if constraint.modality == "deontic" else "fail", None, witness
