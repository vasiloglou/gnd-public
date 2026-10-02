"""Phase 5 float function evaluation and analysis, at the terms.py layer.

Case ids in test names address tests/fixtures/v62-phase5/cases.json's G and
E/U branches for the pure-function evaluator, independent of the checker or
population machinery (tested separately in test_v62_phase5_checker.py).
"""

from __future__ import annotations

import math

import pytest

from gnd.terms import (
    EARTH_RADIUS_KM,
    EXACT_FUNCTION_ARITY,
    FLOAT_FUNCTION_ARITY,
    analyze_term,
    evaluate_term,
    materialize_scalar,
)


def test_g01_g06_every_float_function_has_a_closed_arity() -> None:
    assert FLOAT_FUNCTION_ARITY == {
        "div": 2,
        "sqrt": 1,
        "round": 2,
        "floor": 1,
        "ceil": 1,
        "haversine": 4,
    }
    assert set(FLOAT_FUNCTION_ARITY) & set(EXACT_FUNCTION_ARITY) == set()


def test_g07_round_digit_argument_must_be_integer() -> None:
    analysis = analyze_term(
        {"fn": "round", "args": [{"fn": "div", "args": ["$rb", "$duration"]}, 2.5]},
        {"rb": "Integer", "duration": "Float"},
    )
    assert analysis.issue == "semantic:term-argument-type"


def test_g09_unknown_function_name_refused() -> None:
    analysis = analyze_term({"fn": "log", "args": ["$x"]}, {"x": "Float"})
    assert analysis.issue == "semantic:term-function-name"
    result = evaluate_term({"fn": "log", "args": ["$x"]}, {"x": 2.0})
    assert not result.available
    assert result.reason == "term:function-name"


@pytest.mark.parametrize(
    ("term", "binding", "expected"),
    [
        ({"fn": "div", "args": ["$rb", "$duration"]}, {"rb": 1250, "duration": 400.0}, 3.125),
        ({"fn": "sqrt", "args": ["$margin"]}, {"margin": 6.25}, 2.5),
        (
            {"fn": "floor", "args": [{"fn": "div", "args": ["$rb", "$duration"]}]},
            {"rb": 1250, "duration": 400.0},
            3,
        ),
        (
            {"fn": "ceil", "args": [{"fn": "div", "args": ["$rb", "$duration"]}]},
            {"rb": 1250, "duration": 400.0},
            4,
        ),
    ],
)
def test_e01_e02_e04_e05_happy_path_functions(term: dict, binding: dict, expected: float) -> None:
    result = evaluate_term(term, binding)
    assert result.available
    assert result.value == expected


def test_e03_round_ties_to_even() -> None:
    # 1250/400 = 3.125 exactly (binary64-representable) -- halfway between
    # 3.12 and 3.13 at two decimal digits. Ties-to-even picks 3.12.
    result = evaluate_term(
        {"fn": "round", "args": [{"fn": "div", "args": ["$rb", "$duration"]}, 2]},
        {"rb": 1250, "duration": 400.0},
    )
    assert result.available
    assert result.value == 3.12
    # a second exact-half case at a different digit count, confirming it is
    # not an accident of one denominator
    tie = evaluate_term({"fn": "round", "args": [2.5, 0]}, {})
    assert tie.value == 2.0  # ties to even: 2, not 3


def test_e06_haversine_reference_pair() -> None:
    close = evaluate_term(
        {
            "fn": "round",
            "args": [
                {"fn": "haversine", "args": ["$a", "$b", "$c", "$d"]},
                3,
            ],
        },
        {"a": 48.8584, "b": 2.2945, "c": 48.8606, "d": 2.3010},
    )
    assert close.available
    assert close.value == 0.535
    far = evaluate_term(
        {"fn": "haversine", "args": ["$a", "$b", "$c", "$d"]},
        {"a": 48.8584, "b": 2.2945, "c": 48.8738, "d": 2.3950},
    )
    assert far.available
    assert round(far.value, 3) == 7.548


def test_u01_div_zero() -> None:
    result = evaluate_term(
        {"fn": "div", "args": ["$rb", "$duration"]}, {"rb": 500, "duration": 0.0}
    )
    assert not result.available
    assert result.reason == "term:div-zero"


def test_u02_sqrt_negative() -> None:
    result = evaluate_term({"fn": "sqrt", "args": ["$margin"]}, {"margin": -6.25})
    assert not result.available
    assert result.reason == "term:sqrt-negative"


@pytest.mark.parametrize(
    "binding",
    [
        {"a": 95.0, "b": 2.2945, "c": 48.8606, "d": 2.3010},  # lat1 out of range
        {"a": 48.8584, "b": 2.2945, "c": 95.0, "d": 2.3010},  # lat2 out of range
        {"a": 48.8584, "b": 200.0, "c": 48.8606, "d": 2.3010},  # lon1 out of range
        {"a": 48.8584, "b": 2.2945, "c": 48.8606, "d": 200.0},  # lon2 out of range
    ],
)
def test_u03_u04_haversine_coordinate_range_both_axes(binding: dict) -> None:
    result = evaluate_term({"fn": "haversine", "args": ["$a", "$b", "$c", "$d"]}, binding)
    assert not result.available
    assert result.reason == "term:haversine-coordinate-range"


def test_k05_k06_wide_fraction_coerces_to_the_same_float_python_produces() -> None:
    from fractions import Fraction

    wide = Fraction(10**60 + 1, 3**40)
    direct = float(wide)
    via_div = evaluate_term(
        {"fn": "div", "args": ["$n", "$d"]}, {"n": wide.numerator, "d": wide.denominator}
    )
    # div computes IEEE-754 float division directly; sqrt round-trips a Fraction
    # argument through _to_float, which must match Python's own conversion.
    sqrt_of_wide = evaluate_term(
        {"fn": "sqrt", "args": [{"fn": "abs", "args": ["$w"]}]}, {"w": wide}
    )
    assert sqrt_of_wide.available
    assert sqrt_of_wide.value == math.sqrt(abs(direct))
    assert via_div.available


def test_k15_float_term_budget_reuses_existing_limits() -> None:
    from gnd.terms import DEFAULT_LIMITS

    deep = {"fn": "sqrt", "args": [{"fn": "sqrt", "args": ["$x"]}]}
    for _ in range(DEFAULT_LIMITS.max_depth):
        deep = {"fn": "sqrt", "args": [deep]}
    result = evaluate_term(deep, {"x": 4.0})
    assert not result.available
    assert result.reason == "term:depth-budget"


def test_k16_no_float_function_reaches_a_nonfinite_intermediate() -> None:
    import random

    rng = random.Random(0)
    for _ in range(200):
        a = rng.uniform(-1000, 1000)
        b = rng.uniform(0.001, 1000)
        for term, binding in (
            ({"fn": "div", "args": ["$a", "$b"]}, {"a": a, "b": b}),
            ({"fn": "sqrt", "args": [{"fn": "abs", "args": ["$a"]}]}, {"a": a}),
            ({"fn": "round", "args": ["$a", 2]}, {"a": a}),
            ({"fn": "floor", "args": ["$a"]}, {"a": a}),
            ({"fn": "ceil", "args": ["$a"]}, {"a": a}),
        ):
            result = evaluate_term(term, binding)
            if result.available:
                assert math.isfinite(float(result.value))


def test_haversine_radius_constant_matches_the_normative_value() -> None:
    assert EARTH_RADIUS_KM == 6371.0088


def test_g1_materialize_scalar_passes_a_float_through_unchanged() -> None:
    assert materialize_scalar(3.12) == 3.12
    assert isinstance(materialize_scalar(3.12), float)
