

import importlib
import itertools
from pathlib import Path

import pytest

from gnd.semantic_adapter import canonical_scalar
from gnd.semantic_registry import REGISTRY

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def spec():
    return importlib.import_module("gnd.semantic_spec")


def test_all_snapshot_families_have_executable_predicates(spec):
    # Generated operation findings use the composer, outside authored predicates.
    families = sorted({row.family for row in REGISTRY
                       if row.surface == "snapshot" and row.family != "compiled-subset"}
                      - {"textual"})
    assert set(families) == {"anchored", "cardinality", "equality", "exclusion", "exclusive-or", "frequency", "guarded", "mandatory", "ring", "subset", "mandatory-disjunctive", "subtype-partition", "uniqueness", "value", "value-comparison"}
    from gnd.checker import _anchored_verdicts
    assert callable(_anchored_verdicts)
    families.remove("anchored")
    missing = [
        family + suffix
        for family in families
        for suffix in ("_holds", "_witness")
        if not callable(getattr(spec, family.replace("-", "_") + suffix, None))
    ]
    assert not missing, missing
    assert callable(spec.applicability_of) and callable(spec.verdict_of)


def test_collection_membership_uses_identity_not_python_equality(spec):
    number = canonical_scalar(1, None)
    text = canonical_scalar("1", None)
    boolean = canonical_scalar(True, None)
    assert spec.scalar_member(number, (number,))
    assert not spec.scalar_member(number, (text, boolean))
    assert not spec.scalar_member(number, ())
    assert spec.row_identical((number, text), (number, text))
    assert not spec.row_identical((number, text), (text, number))
    assert not spec.row_identical((number,), (number, text))
    assert spec.row_identical((), ())
    assert spec.row_member((number, text), ((boolean,), (number, text)))
    assert not spec.row_member((number,), ((boolean,), (text,)))


def test_missing_identities_are_exhaustive_distinct_and_keep_first_occurrence(spec):
    number = canonical_scalar(1, None)
    text = canonical_scalar("1", None)
    boolean = canonical_scalar(True, None)
    assert spec.missing_identities((text, number, text, boolean), (number,)) == [text, boolean]
    assert spec.missing_identities((number, number), (number, number)) == []
    assert spec.missing_identities((), ()) == []
                                                                             
                                                                                
    from dataclasses import replace

    instant = canonical_scalar("2026-01-01T12:00:00Z", "DateTime")
    offset = canonical_scalar("2026-01-01T07:00:00-05:00", "DateTime")
    raw = replace(instant, kind="string", ordered=False, num=0)
    assert spec.scalar_member(instant, (raw,))
    assert spec.missing_identities((instant, raw, offset), ()) == [instant, offset]
    assert spec.missing_identities((instant, offset), (raw,)) == [offset]


def test_collection_operations_match_independent_finite_identity_sets(spec):
    values = tuple(canonical_scalar(value, None) for value in (1, "1", True))
    universes = tuple(row for size in range(5) for row in itertools.product(values, repeat=size))
    player_sets = tuple(row for size in range(4) for row in itertools.product(values, repeat=size))
    key = lambda scalar: (scalar.identity_kind, scalar.token)
    for universe in universes:
        for end in range(-1, len(universe) + 2):
            for value in values:
                assert spec.scalar_member_before(value, universe, end) == (
                    key(value) in {key(item) for item in universe[: max(0, end)]}
                )
        for players in player_sets:
            player_keys = {key(item) for item in players}
            expected = dict.fromkeys(key(item) for item in universe if key(item) not in player_keys)
            actual = spec.missing_identities(universe, players)
            assert [key(item) for item in actual] == list(expected)


def test_missing_values_retain_first_source_objects_and_complete_membership(spec):
    values = tuple(canonical_scalar(value, None) for value in (1, "1", True))
    key = lambda scalar: (scalar.identity_kind, scalar.token)
    for size in range(5):
        for universe in itertools.product(values, repeat=size):
            for players in ((), values[:1], values[1:], values):
                keys = [key(item) for item in universe]
                selected = [
                    i
                    for i, item in enumerate(keys)
                    if item not in {key(player) for player in players} and item not in keys[:i]
                ]
                actual = spec.missing_identities(universe, players)
                assert len(actual) == len(selected)
                assert all(item is universe[i] for item, i in zip(actual, selected, strict=True))


def test_list_membership_preserves_contents_and_distinguishes_identity(spec):
    values = tuple(canonical_scalar(value, None) for value in (1, "1", True))
    for size in range(5):
        for sequence in itertools.product(values, repeat=size):
            owned = list(sequence)
            for value in values:
                expected = (value.identity_kind, value.token) in {
                    (item.identity_kind, item.token) for item in sequence
                }
                assert spec.scalar_list_member(value, owned) == expected
                assert [id(item) for item in owned] == [id(item) for item in sequence]


def test_missing_values_have_no_recursion_depth_or_byte_index_limit(spec):
    universe = tuple(canonical_scalar(value, None) for value in range(1100))
    actual = spec.missing_identities(universe + universe, universe[::2])
    assert len(actual) == 550
    assert all(item is expected for item, expected in zip(actual, universe[1::2], strict=True))






































def test_range_bounds_match_independent_numeric_comparisons(spec):
    for value, minimum, maximum, min_inclusive, max_inclusive in itertools.product(
        range(-2, 3), (None, -1, 0, 1), (None, -1, 0, 1), (False, True), (False, True)
    ):
        expected = (
            minimum is None or (value >= minimum if min_inclusive else value > minimum)
        ) and (maximum is None or (value <= maximum if max_inclusive else value < maximum))
        bounds = tuple(
            canonical_scalar(x, None) if x is not None else None for x in (minimum, maximum)
        )
        assert spec.scalar_range_state(
            canonical_scalar(value, None), *bounds, min_inclusive, max_inclusive
        ) == int(expected)


def test_range_incomparability_and_disjunction_precedence(spec):
    value, low, high, text = (canonical_scalar(x, None) for x in (0, -1, 1, "text"))
    inside, outside, unknown = (
        (low, high, True, True),
        (high, None, True, True),
        (text, None, True, True),
    )
    assert spec.scalar_range_state(value, high, text, True, True) == -1
    assert spec.scalar_range_state(text, None, None, False, False) == 1
    for size in range(4):
        for choices in itertools.product(range(3), repeat=size):
            ranges = tuple((inside, outside, unknown)[choice] for choice in choices)
            expected = 1 if 0 in choices else -1 if 2 in choices else 0
            assert spec.scalar_ranges_state(value, ranges) == expected
    aware = canonical_scalar("2026-01-01T12:00:00Z", "DateTime")
    equal = canonical_scalar("2026-01-01T07:00:00-05:00", "DateTime")
    naive = canonical_scalar("2026-01-01T12:00:00", "DateTime")
    assert spec.scalar_range_state(aware, equal, equal, True, True) == 0
    assert spec.scalar_range_state(aware, equal, equal, False, True) == 0
    assert spec.scalar_range_state(aware, naive, None, True, True) == -1


def test_aggregate_witness_preserves_one_row_even_for_zero_members(spec):
    for members in (
        [],
        [canonical_scalar(1, None)],
        [canonical_scalar(x, None) for x in range(1100)],
    ):
        witness = spec.pack_witness_row(members)
        assert len(witness) == 1
        assert witness[0] is members


@pytest.mark.parametrize(
    "band,decision",
    [
        (0, "accept"),
        (1, "refuse"),
        (2, "indeterminate"),
        (4, "indeterminate"),
        (3, ""),
        (-1, ""),
        (70, ""),
    ],
)
def test_decision_table(spec, band, decision):
    assert spec.decision_of(band) == decision


@pytest.mark.parametrize(
    "applicable,current,in_scope,expected",
    [
        (3, 3, True, "proof-backed"),
        (3, 1, True, "partial"),
        (3, 0, True, "none"),
        (3, 3, False, "none"),
        (0, 0, True, "none"),
        (3, 4, True, "none"),
        (-1, 1, True, "none"),
        (3, -1, True, "none"),
    ],
)
def test_assurance_counts_have_no_empty_or_invalid_upgrade(
    spec, applicable, current, in_scope, expected
):
    assert spec.assurance_of(applicable, current, in_scope) == expected


@pytest.mark.parametrize(
    "admitted,currency_valid,extraction_required,authenticated",
    tuple(itertools.product([False, True], repeat=4)),
)
def test_extraction_authentication_and_currency_suppress_assurance(
    spec, admitted, currency_valid, extraction_required, authenticated
):
    result = spec.assurance_for_route(
        3, 3, True, admitted, currency_valid, extraction_required, authenticated
    )
    if not admitted or not currency_valid or (extraction_required and not authenticated):
        assert result == "none"
    else:
        assert result == "proof-backed"
    assert spec.assurance_for_route(3, 1, True, True, True, True, False) == "none"
    assert spec.assurance_for_route(3, 1, True, True, True, True, True) == "partial"


@pytest.mark.parametrize(
    "rows,expected",
    [
        ((), 0),
        ((("deontic", "warning"),), 0),
        ((("deontic", "unchecked"),), 0),
        ((("alethic", "vacuous"),), 2),
        ((("deontic", "vacuous"),), 2),
        ((("alethic", "unchecked"), ("deontic", "warning")), 4),
        ((("alethic", "fail"), ("alethic", "unchecked"), ("deontic", "vacuous")), 1),
        ((("alethic", "unchecked"), ("deontic", "vacuous"), ("alethic", "pass")), 4),
        ((("deontic", "vacuous"), ("alethic", "pass"), ("deontic", "warning")), 2),
    ],
)
def test_band_precedence_is_independent_of_input_order(spec, rows, expected):
    for ordering in set(itertools.permutations(rows)):
        assert spec.band_of(ordering) == expected


def test_scalar_order_and_identity_use_different_coordinates(spec):
    a = canonical_scalar("2026-01-01T07:00:00-05:00", "DateTime")
    b = canonical_scalar("2026-01-01T12:00:00Z", "DateTime")
    assert spec.scalar_order(a, b) == 0
    assert not spec.scalar_identical(a, b)
    assert spec.scalar_order(canonical_scalar(2, "Integer"), canonical_scalar(10, "Number")) == -1
    assert (
        spec.scalar_order(canonical_scalar(True, "Boolean"), canonical_scalar(1, "Integer")) == -2
    )
    assert not spec.scalar_identical(
        canonical_scalar(True, "Boolean"), canonical_scalar(1, "Integer")
    )
    assert spec.scalar_identical(canonical_scalar(1, "Integer"), canonical_scalar(1.0, "Float"))
    assert spec.scalar_order(canonical_scalar("a", "String"), canonical_scalar("z", "String")) == -2
    assert spec.scalar_order(canonical_scalar("2026-01-01T12:00:00", "DateTime"), b) == -2

























