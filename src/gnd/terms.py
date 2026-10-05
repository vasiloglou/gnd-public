"""Closed exact scalar-term language shared by derivations and guarded rules."""

from __future__ import annotations

import math
import re
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from fractions import Fraction
from typing import Any

EXACT_FUNCTION_ARITY = {
    "add": 2,
    "sub": 2,
    "mul": 2,
    "neg": 1,
    "abs": 1,
    "mod": 2,
}
FLOAT_FUNCTION_ARITY = {
    "div": 2,
    "sqrt": 1,
    "round": 2,
    "floor": 1,
    "ceil": 1,
    "haversine": 4,
}
#: floor/ceil always produce a whole value -- exactly representable, so R6's
#: head-quantization rule (a float value needs `round` to bind a head) does
#: not apply to them.
FLOAT_FUNCTION_RESULT_PRIMITIVE = {
    "div": "Float",
    "sqrt": "Float",
    "round": "Float",
    "floor": "Integer",
    "ceil": "Integer",
    "haversine": "Float",
}
EARTH_RADIUS_KM = 6371.0088
NUMERIC_PRIMITIVES = frozenset({"Integer", "Float", "Number"})
TEMPORAL_FUNCTIONS = frozenset({"date_add", "date_sub"})
MAX_DURATION_DAYS = 1_000_000
TEMPORAL_REASONS = (
    "term:date-out-of-range",
    "term:opaque-date-operand",
    "term:temporal-work-limit",
)


def valid_duration(value: object) -> bool:
    return (
        isinstance(value, int) and not isinstance(value, bool) and 0 <= value <= MAX_DURATION_DAYS
    )


def valid_date(value: object) -> bool:
    if not isinstance(value, str) or re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value) is None:
        return False
    try:
        date.fromisoformat(value)
        return True
    except ValueError:
        return False


def temporal_nodes(value: object):
    """Iterate authored syntax without descending into provenance or archived proposals."""
    stack = [("$", value)]
    while stack:
        path, node = stack.pop()
        if isinstance(node, dict):
            # Role-name maps are containers, even when a role is named date.
            if not path.endswith((".bind", ".head")):
                yield path, node
            stack.extend(
                (f"{path}.{key}", child)
                for key, child in node.items()
                if key not in {"provenance", "source", "rejected_proposals"}
            )
        elif isinstance(node, list):
            stack.extend((f"{path}[{index}]", child) for index, child in enumerate(node))


def is_temporal_node(node: Mapping) -> bool:
    return bool({"date", "duration_days"} & node.keys()) or (
        isinstance(node.get("fn"), str) and node["fn"] in TEMPORAL_FUNCTIONS
    )


def uses_temporal(model: Any) -> bool:
    document = (
        model
        if isinstance(model, dict)
        else {
            "object_types": model.object_types,
            "fact_types": model.fact_types,
            "constraints": model.constraints,
            "operations": model.operations,
        }
    )
    return any(
        node.get("primitive") == "Duration" or is_temporal_node(node)
        for _, node in temporal_nodes(document)
    )


def require_non_temporal(model: Any, consumer: str) -> None:
    """Refuse unsupported consumers before they publish artifacts or claims."""
    if uses_temporal(model):
        from gnd.errors import ModelValidationError, ValidationIssue

        raise ModelValidationError(
            [
                ValidationIssue(
                    path="$",
                    message=f"{consumer} does not support temporal models in Phase 1",
                    rule_id="temporal:consumer-unsupported",
                )
            ]
        )


@dataclass(frozen=True, slots=True)
class ExactTermLimits:
    max_nodes: int = 256
    max_depth: int = 32
    max_value_bits: int = 65_536


DEFAULT_LIMITS = ExactTermLimits()


@dataclass(frozen=True, slots=True)
class TermAnalysis:
    primitive: str | None
    variables: tuple[str, ...]
    nodes: int
    depth: int
    issue: str | None = None


@dataclass(frozen=True, slots=True)
class ExactTermResult:
    value: Any | None
    reason: str | None = None
    binding: Mapping[str, Any] | None = None
    operations: int = 0
    nodes: int = 0
    max_value_bits: int = 0

    @property
    def available(self) -> bool:
        return self.reason is None


def guarded_operand_evaluator(legacy, scalar_factory):
    """Build the unpinned exact-term extension of the guarded operand seam.

    A Phase 5 float-tier function (``operand.function`` in
    ``FLOAT_FUNCTION_ARITY``) returns a Python ``float`` or, for
    ``floor``/``ceil``, an ``int`` -- never a ``Fraction``. Both are folded
    into the same exact rational ``Scalar`` representation every number here
    already uses, via ``as_integer_ratio()`` for a finite float, exactly as
    ``_identity_token`` already treats a wire float. This is not a new
    representation kind: every number is already carried as a reduced
    numerator/denominator pair regardless of source tier.
    """

    def evaluate(operand, names, binding):
        if operand.kind != "function":
            return legacy(operand, names, binding)
        values = [evaluate(item, names, binding) for item in operand.arguments]
        if operand.function in TEMPORAL_FUNCTIONS:
            if (
                not operand.valid
                or len(operand.arguments) != 2
                or [child.primitive for child in operand.arguments] != ["Date", "Duration"]
            ):
                return None
            raw = [
                value.token
                if child.primitive == "Date" and value is not None
                else Fraction(value.num, value.den)
                if value is not None and value.kind == "number"
                else None
                for child, value in zip(operand.arguments, values, strict=True)
            ]
            raw = [
                value.numerator if isinstance(value, Fraction) and value.denominator == 1 else value
                for value in raw
            ]
            result = evaluate_term(
                {
                    "fn": operand.function,
                    "args": [
                        {"date": raw[0]} if raw[0] is not None else "$date",
                        {"duration_days": raw[1]} if raw[1] is not None else "$days",
                    ],
                },
                {},
            )
            if not result.available:
                return None
            return scalar_factory(
                "date",
                result.value,
                date.fromisoformat(result.value).toordinal(),
                1,
                True,
                "string",
            )
        if any(value is None or value.kind != "number" for value in values):
            return None
        exact = [Fraction(value.num, value.den) for value in values if value is not None]
        result = evaluate_term({"fn": operand.function, "args": exact}, {})
        if not result.available:
            return None
        outcome = result.value
        if isinstance(outcome, Fraction):
            value = outcome
        elif isinstance(outcome, bool):
            return None
        elif isinstance(outcome, int):
            value = Fraction(outcome, 1)
        elif isinstance(outcome, float) and math.isfinite(outcome):
            value = Fraction(*outcome.as_integer_ratio())
        else:
            return None
        return scalar_factory(
            "number",
            f"{value.numerator}/{value.denominator}",
            value.numerator,
            value.denominator,
            True,
            "number",
        )

    return evaluate


def variable_name(term: object) -> str | None:
    if isinstance(term, str) and len(term) > 1 and term.startswith("$"):
        return term[1:]
    return None


def is_function_term(term: object) -> bool:
    return isinstance(term, dict) and set(term) == {"fn", "args"}


def term_variables(term: object) -> tuple[str, ...]:
    """Return variables without an unbounded recursive walk.

    Validation owns the diagnostic for an over-budget tree.  This helper is used
    by later graph rules, so it observes the same finite prefix and can never do
    more work than the validator's advertised node/depth budget.
    """
    found: list[str] = []
    stack: list[tuple[object, int]] = [(term, 1)]
    visited = 0
    while stack and visited < DEFAULT_LIMITS.max_nodes:
        value, depth = stack.pop()
        visited += 1
        variable = variable_name(value)
        if variable is not None:
            if variable not in found:
                found.append(variable)
            continue
        if depth < DEFAULT_LIMITS.max_depth and is_function_term(value):
            arguments = value["args"]  # type: ignore[index]
            if isinstance(arguments, list):
                stack.extend((argument, depth + 1) for argument in reversed(arguments))
    return tuple(found)


def _literal_primitive(value: object) -> str | None:
    if isinstance(value, bool):
        return "Boolean"
    if isinstance(value, int):
        return "Integer"
    if isinstance(value, float) and math.isfinite(value):
        return "Float"
    if isinstance(value, str):
        return "String"
    return None


def analyze_term(
    term: object,
    variables: Mapping[str, str],
    *,
    limits: ExactTermLimits = DEFAULT_LIMITS,
) -> TermAnalysis:
    """Infer one term's primitive and structural budget without evaluating it."""

    seen_variables: list[str] = []
    visited = 0

    def walk(value: object, depth: int) -> tuple[str | None, int, int, str | None]:
        nonlocal visited
        visited += 1
        if visited > limits.max_nodes:
            return None, 1, depth, "semantic:term-node-budget"
        if depth > limits.max_depth:
            return None, 1, depth, "semantic:term-depth-budget"
        variable = variable_name(value)
        if variable is not None:
            if variable not in seen_variables:
                seen_variables.append(variable)
            primitive = variables.get(variable)
            return primitive, 1, depth, None if primitive is not None else "semantic:term-unbound"
        if not isinstance(value, dict):
            if isinstance(value, float) and not math.isfinite(value):
                return None, 1, depth, "semantic:term-non-finite-number"
            primitive = _literal_primitive(value)
            return primitive, 1, depth, None if primitive is not None else "semantic:term-shape"
        if set(value) != {"fn", "args"}:
            if set(value) == {"date"}:
                return (
                    "Date",
                    1,
                    depth,
                    None if valid_date(value["date"]) else "semantic:term-date-literal",
                )
            if set(value) == {"duration_days"}:
                return (
                    "Duration",
                    1,
                    depth,
                    None
                    if valid_duration(value["duration_days"])
                    else "semantic:term-duration-literal",
                )
            return None, 1, depth, "semantic:term-shape"
        function = value.get("fn")
        arguments = value.get("args")
        arity = EXACT_FUNCTION_ARITY.get(function) if isinstance(function, str) else None
        is_float_function = arity is None and isinstance(function, str)
        if is_float_function:
            arity = FLOAT_FUNCTION_ARITY.get(function)
        if isinstance(function, str) and function in TEMPORAL_FUNCTIONS:
            arity = 2
        if not isinstance(function, str) or arity is None:
            return None, 1, depth, "semantic:term-function-name"
        if not isinstance(arguments, list) or len(arguments) != arity:
            return None, 1, depth, "semantic:term-function-arity"
        analyses = [walk(argument, depth + 1) for argument in arguments]
        nodes = 1 + sum(item[1] for item in analyses)
        maximum_depth = max((item[2] for item in analyses), default=depth)
        issue = next((item[3] for item in analyses if item[3] is not None), None)
        if issue is not None:
            return None, nodes, maximum_depth, issue
        primitives = [item[0] for item in analyses]
        if isinstance(function, str) and function in TEMPORAL_FUNCTIONS:
            return (
                ("Date", nodes, maximum_depth, None)
                if primitives == ["Date", "Duration"]
                else (None, nodes, maximum_depth, "semantic:term-argument-type")
            )
        if any(item not in NUMERIC_PRIMITIVES for item in primitives):
            return None, nodes, maximum_depth, "semantic:term-argument-type"
        if function == "mod" and any(item != "Integer" for item in primitives):
            return None, nodes, maximum_depth, "semantic:term-argument-type"
        if function == "round" and primitives[1] != "Integer":
            return None, nodes, maximum_depth, "semantic:term-argument-type"
        if is_float_function:
            return FLOAT_FUNCTION_RESULT_PRIMITIVE[function], nodes, maximum_depth, None
        result = "Integer" if all(item == "Integer" for item in primitives) else "Number"
        return result, nodes, maximum_depth, None

    primitive, nodes, depth, issue = walk(term, 1)
    return TermAnalysis(primitive, tuple(seen_variables), nodes, depth, issue)


def _exact_number(value: object) -> Fraction | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return Fraction(value, 1)
    if isinstance(value, Fraction):
        return value
    if isinstance(value, float) and math.isfinite(value):
        numerator, denominator = value.as_integer_ratio()
        return Fraction(numerator, denominator)
    return None


def _too_wide(value: Fraction, limits: ExactTermLimits) -> bool:
    return max(value.numerator.bit_length(), value.denominator.bit_length()) > limits.max_value_bits


def evaluate_term(
    term: object,
    binding: Mapping[str, Any],
    *,
    limits: ExactTermLimits = DEFAULT_LIMITS,
    temporal_work: list[int] | None = None,
) -> ExactTermResult:
    """Evaluate exactly, returning a named unavailable result instead of raising."""

    operations = 0
    nodes = 0
    maximum_value_bits = 0

    def unavailable(reason: str) -> ExactTermResult:
        return ExactTermResult(
            None,
            reason,
            dict(binding),
            operations,
            nodes,
            maximum_value_bits,
        )

    def _to_float(candidate: Any) -> float | None:
        """A genuine type mismatch returns None; overflow is the caller's to catch.

        An Integer or exact Fraction inside the exact tier's 65,536-bit budget
        can still exceed a binary64's ~1.8e308 magnitude ceiling -- reproduced
        directly with 10**400, well inside that bit budget -- so `float()`'s
        OverflowError is left to propagate rather than folded into "wrong
        type": the two are different findings and need different reasons.
        """
        if isinstance(candidate, bool):
            return None
        if isinstance(candidate, float):
            return candidate  # already checked finite by the caller upstream
        if isinstance(candidate, (int, Fraction)):
            return float(candidate)
        return None

    def _to_digit_count(candidate: Any) -> int | None:
        if isinstance(candidate, bool):
            return None
        if isinstance(candidate, int):
            return candidate
        if isinstance(candidate, Fraction) and candidate.denominator == 1:
            return candidate.numerator
        return None

    def walk_float(function: str, arguments: object, depth: int) -> ExactTermResult:
        nonlocal operations
        arity = FLOAT_FUNCTION_ARITY[function]
        if not isinstance(arguments, list) or len(arguments) != arity:
            return unavailable("term:function-arity")
        results = [walk(argument, depth + 1) for argument in arguments]
        failed = next((result for result in results if not result.available), None)
        if failed is not None:
            return failed
        try:
            if function == "round":
                operand = _to_float(results[0].value)
                digits = _to_digit_count(results[1].value)
                if operand is None or digits is None:
                    return unavailable("term:argument-type")
                operations += 1
                outcome: Any = round(operand, digits)
            else:
                floats = [_to_float(result.value) for result in results]
                if any(item is None for item in floats):
                    return unavailable("term:argument-type")
                operations += 1
                if function == "div":
                    if floats[1] == 0.0:
                        return unavailable("term:div-zero")
                    outcome = floats[0] / floats[1]
                elif function == "sqrt":
                    if floats[0] < 0.0:
                        return unavailable("term:sqrt-negative")
                    outcome = math.sqrt(floats[0])
                elif function == "floor":
                    outcome = math.floor(floats[0])
                elif function == "ceil":
                    outcome = math.ceil(floats[0])
                else:  # haversine
                    lat1, lon1, lat2, lon2 = floats
                    if (
                        abs(lat1) > 90.0
                        or abs(lat2) > 90.0
                        or abs(lon1) > 180.0
                        or abs(lon2) > 180.0
                    ):
                        return unavailable("term:haversine-coordinate-range")
                    phi1, phi2 = math.radians(lat1), math.radians(lat2)
                    dphi = math.radians(lat2 - lat1)
                    dlambda = math.radians(lon2 - lon1)
                    haversine_a = (
                        math.sin(dphi / 2) ** 2
                        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
                    )
                    # Roundoff can push the sum a hair outside [0, 1] near
                    # antipodal points, which asin() then refuses -- clamped,
                    # not merely bounded by the earlier lat/lon range check.
                    haversine_a = min(1.0, max(0.0, haversine_a))
                    outcome = EARTH_RADIUS_KM * 2 * math.asin(math.sqrt(haversine_a))
        except OverflowError:
            return unavailable("term:float-overflow")
        if isinstance(outcome, float) and not math.isfinite(outcome):
            return unavailable("term:float-overflow")
        return ExactTermResult(
            outcome,
            binding=dict(binding),
            operations=operations,
            nodes=nodes,
            max_value_bits=maximum_value_bits,
        )

    def walk(value: object, depth: int) -> ExactTermResult:
        nonlocal maximum_value_bits, nodes, operations
        nodes += 1
        if nodes > limits.max_nodes:
            return unavailable("term:node-budget")
        if depth > limits.max_depth:
            return unavailable("term:depth-budget")
        variable = variable_name(value)
        if variable is not None:
            if variable not in binding:
                return unavailable("term:unbound-variable")
            bound = binding[variable]
            if isinstance(bound, float) and not math.isfinite(bound):
                return unavailable("term:non-finite-number")
            return ExactTermResult(
                bound,
                binding=dict(binding),
                operations=operations,
                nodes=nodes,
                max_value_bits=maximum_value_bits,
            )
        if not isinstance(value, dict):
            if isinstance(value, float) and not math.isfinite(value):
                return unavailable("term:non-finite-number")
            return ExactTermResult(
                value,
                binding=dict(binding),
                operations=operations,
                nodes=nodes,
                max_value_bits=maximum_value_bits,
            )
        if not is_function_term(value):
            if set(value) == {"date"} and valid_date(value["date"]):
                return ExactTermResult(value["date"], operations=operations)
            if set(value) == {"duration_days"} and valid_duration(value["duration_days"]):
                return ExactTermResult(value["duration_days"], operations=operations)
            return unavailable("term:shape")
        function = value["fn"]
        arguments = value["args"]
        if isinstance(function, str) and function in TEMPORAL_FUNCTIONS:
            if not isinstance(arguments, list) or len(arguments) != 2:
                return unavailable("term:function-arity")
            if temporal_work is not None:
                if temporal_work[0] >= 10_000:
                    return unavailable("term:temporal-work-limit")
                temporal_work[0] += 1
            results = [walk(argument, depth + 1) for argument in arguments]
            failed = next((result for result in results if not result.available), None)
            if failed is not None:
                return failed
            first, days = (result.value for result in results)
            if first is None or days is None or isinstance(first, dict) or isinstance(days, dict):
                return unavailable("term:opaque-date-operand")
            if not valid_date(first) or not valid_duration(days):
                return unavailable("term:argument-type")
            operations += 1
            ordinal = date.fromisoformat(first).toordinal() + (
                days if function == "date_add" else -days
            )
            if not 1 <= ordinal <= date.max.toordinal():
                return unavailable("term:date-out-of-range")
            return ExactTermResult(date.fromordinal(ordinal).isoformat(), operations=operations)
        if isinstance(function, str) and function in FLOAT_FUNCTION_ARITY:
            return walk_float(function, arguments, depth)
        if not isinstance(function, str) or function not in EXACT_FUNCTION_ARITY:
            return unavailable("term:function-name")
        if not isinstance(arguments, list) or len(arguments) != EXACT_FUNCTION_ARITY[function]:
            return unavailable("term:function-arity")
        results: list[ExactTermResult] = []
        for argument in arguments:
            results.append(walk(argument, depth + 1))
        failed = next((result for result in results if not result.available), None)
        if failed is not None:
            # Return the first semantic failure with the final counters from
            # every child that was evaluated, rather than that child's stale
            # counter snapshot.
            return unavailable(failed.reason or "term:dependency-unavailable")
        exact_values = [_exact_number(result.value) for result in results]
        if any(item is None for item in exact_values):
            return unavailable("term:argument-type")
        operand_bits = max(
            max(value.numerator.bit_length(), value.denominator.bit_length())
            for value in exact_values
            if value is not None
        )
        maximum_value_bits = max(
            maximum_value_bits,
            min(operand_bits, limits.max_value_bits + 1),
        )
        if any(_too_wide(value, limits) for value in exact_values if value is not None):
            return unavailable("term:exact-value-too-wide")
        operations += 1
        left = exact_values[0]
        if function == "add":
            result = left + exact_values[1]
        elif function == "sub":
            result = left - exact_values[1]
        elif function == "mul":
            result = left * exact_values[1]
        elif function == "neg":
            result = -left
        elif function == "abs":
            result = abs(left)
        else:
            divisor = exact_values[1]
            if divisor == 0:
                return unavailable("term:mod-zero")
            result = left - divisor * math.floor(left / divisor)
        maximum_value_bits = max(
            maximum_value_bits,
            min(
                max(result.numerator.bit_length(), result.denominator.bit_length()),
                limits.max_value_bits + 1,
            ),
        )
        if _too_wide(result, limits):
            return unavailable("term:exact-value-too-wide")
        return ExactTermResult(
            result,
            binding=dict(binding),
            operations=operations,
            nodes=nodes,
            max_value_bits=maximum_value_bits,
        )

    return walk(term, 1)


def compare_terms(
    operator: str,
    left: object,
    right: object,
    binding: Mapping[str, Any],
    *,
    limits: ExactTermLimits = DEFAULT_LIMITS,
    bound_cross_product: bool = False,
) -> ExactTermResult:
    left_result = evaluate_term(left, binding, limits=limits)
    if not left_result.available:
        return left_result
    right_result = evaluate_term(right, binding, limits=limits)
    if not right_result.available:
        return ExactTermResult(
            None,
            right_result.reason,
            dict(binding),
            left_result.operations + right_result.operations,
            left_result.nodes + right_result.nodes,
            max(left_result.max_value_bits, right_result.max_value_bits),
        )
    pair = (left_result.value, right_result.value)
    exact_pair = tuple(_exact_number(value) for value in pair)
    comparison_bits = 0
    exact_comparison = all(value is not None for value in exact_pair)
    if exact_comparison:
        first, second = exact_pair
        assert first is not None and second is not None
        if bound_cross_product:
            left_cross = first.numerator * second.denominator
            right_cross = second.numerator * first.denominator
            comparison_bits = min(
                max(
                    first.numerator.bit_length(),
                    first.denominator.bit_length(),
                    second.numerator.bit_length(),
                    second.denominator.bit_length(),
                    left_cross.bit_length(),
                    right_cross.bit_length(),
                ),
                limits.max_value_bits + 1,
            )
            if comparison_bits > limits.max_value_bits:
                return ExactTermResult(
                    None,
                    "term:exact-value-too-wide",
                    dict(binding),
                    left_result.operations + right_result.operations + 2,
                    left_result.nodes + right_result.nodes,
                    comparison_bits,
                )
            pair = (left_cross, right_cross)
        else:
            pair = exact_pair
    try:
        decision = {
            "<": lambda: pair[0] < pair[1],
            "<=": lambda: pair[0] <= pair[1],
            "=": lambda: pair[0] == pair[1],
            ">=": lambda: pair[0] >= pair[1],
            ">": lambda: pair[0] > pair[1],
            "!=": lambda: pair[0] != pair[1],
        }[operator]()
    except (KeyError, TypeError):
        return ExactTermResult(
            None,
            "term:values-not-comparable",
            dict(binding),
            left_result.operations + right_result.operations,
            left_result.nodes + right_result.nodes,
            max(left_result.max_value_bits, right_result.max_value_bits, comparison_bits),
        )
    return ExactTermResult(
        decision,
        binding=dict(binding),
        operations=left_result.operations
        + right_result.operations
        + (2 if bound_cross_product and exact_comparison else 0),
        nodes=left_result.nodes + right_result.nodes,
        max_value_bits=max(
            left_result.max_value_bits, right_result.max_value_bits, comparison_bits
        ),
    )


def materialize_scalar(value: Any) -> Any:
    """Return the existing wire scalar for a head value; fractions never escape.

    A Phase 5 float-function result is already a Python ``float`` (round,
    floor's/ceil's whole-valued ``int``, or another float-tier function's
    ``float``) -- never a ``Fraction`` -- so it passes through unchanged.
    """
    if isinstance(value, Fraction):
        if value.denominator != 1:
            raise ValueError("non-Integer exact value requires round before head materialization")
        return value.numerator
    return value
