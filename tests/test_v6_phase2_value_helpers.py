

import ast
import inspect
import itertools
from dataclasses import replace

import pytest

from gnd import semantic_spec as spec
from gnd.semantic_adapter import canonical_scalar
from gnd.semantic_ir import IRConstraint, IRFactType, IRRelation, IRRole, IRRoster, SnapshotIR


def constraint(variant, **changes):
    value = IRConstraint(
        ref="value-test",
        family="value",
        variant=variant,
        modality="alethic",
        fact_type="",
        roles=(),
        role_refs=(),
        sequences=(),
        object_type="score",
        subtypes=(),
        flags=(),
        minimum=None,
        maximum=None,
        allowed=(),
        ranges=(),
        operator="",
        literal=None,
        operands=(),
        consequent_kind="",
        antecedent=(),
        consequent=(),
        scope_fact_types=(),
        expression="",
        refused="",
    )
    return replace(value, **changes)


def snapshot(**changes):
    value = SnapshotIR(
        object_types=(),
        fact_types=(),
        relations=(),
        rosters=(),
        constraints=(),
        finite=True,
        covers=(),
        explicit_rosters=(),
        derivations=(),
        derivation_order=(),
        refusals=(),
    )
    return replace(value, **changes)


def fact(name, roles=()):
    return IRFactType(
        id=name,
        roles=roles,
        declared=True,
        derivation="",
        structured_rule=False,
        relation_source="claimed",
        opaque_rule="",
    )


@pytest.mark.parametrize("variant", ["enum", "enum-role"])
def test_enum_cells_compare_canonical_identity_and_empty_allowed_set(variant):
    values = tuple(canonical_scalar(value, None) for value in (1, "1", True))
    for size in range(4):
        for allowed in itertools.product(values, repeat=size):
            keys = {(value.identity_kind, value.token) for value in allowed}
            for value in values:
                expected = int((value.identity_kind, value.token) in keys)
                assert (
                    spec.value_cell_state(value, constraint(variant, allowed=allowed)) == expected
                )


@pytest.mark.parametrize("variant", ["range", "range-role"])
def test_range_cells_require_flags_and_honor_each_inclusivity(variant):
    number = lambda value: canonical_scalar(value, None)
    for flag_count in range(4):
        assert (
            spec.value_cell_state(number(0), constraint(variant, flags=(True,) * flag_count)) == -1
        )
    for raw, lower_closed, upper_closed in itertools.product(
        range(-2, 3), (False, True), (False, True)
    ):
        expected = (-1 < raw < 1) or (raw == -1 and lower_closed) or (raw == 1 and upper_closed)
        rule = constraint(
            variant,
            minimum=number(-1),
            maximum=number(1),
            flags=(False, False, lower_closed, upper_closed),
        )
        assert spec.value_cell_state(number(raw), rule) == int(expected)
    rule = constraint(
        variant, minimum=number(1), maximum=canonical_scalar("text", None), flags=(True,) * 4
    )
    assert spec.value_cell_state(number(0), rule) == -1


@pytest.mark.parametrize("variant", ["range", "range-role"])
def test_inclusive_temporal_endpoint_requires_identity_not_only_equal_order(variant):
    endpoint = canonical_scalar("2026-01-01T12:00:00Z", "DateTime")
    equal_instant = canonical_scalar("2026-01-01T07:00:00-05:00", "DateTime")
    assert endpoint is not None and equal_instant is not None
    assert spec.scalar_order(equal_instant, endpoint) == 0
    assert not spec.scalar_identical(equal_instant, endpoint)
    rule = constraint(
        variant,
        minimum=endpoint,
        maximum=endpoint,
        flags=(False, False, True, True),
    )
    assert spec.value_cell_state(endpoint, rule) == 1
    assert spec.value_cell_state(equal_instant, rule) == 0


@pytest.mark.parametrize("variant", ["ranges", "ranges-role"])
def test_range_union_cells_keep_inclusion_and_unknown_precedence(variant):
    value = canonical_scalar(0, None)
    choices = (
        (None, None, True, True),
        (canonical_scalar(1, None), None, True, True),
        (canonical_scalar("text", None), None, True, True),
    )
    for size in range(4):
        for indexes in itertools.product(range(3), repeat=size):
            rule = constraint(variant, ranges=tuple(choices[i] for i in indexes))
            expected = 1 if 0 in indexes else -1 if 2 in indexes else 0
            assert spec.value_cell_state(value, rule) == expected


def test_unknown_value_variant_is_undecidable():
    assert spec.value_cell_state(canonical_scalar(0, None), constraint("future-variant")) == -1


@pytest.mark.parametrize("kind", ["roster", "fact", "relation", "role"])
def test_ir_lookup_returns_first_match_and_checks_last_position(kind):
    names = ("early", "duplicate", "duplicate", "last")
    if kind == "roster":
        subject = snapshot(rosters=tuple(IRRoster(name, (), ()) for name in names))
        lookup = spec.snapshot_roster_index
    elif kind == "fact":
        subject = snapshot(fact_types=tuple(fact(name) for name in names))
        lookup = spec.snapshot_fact_index
    elif kind == "relation":
        subject = snapshot(relations=tuple(IRRelation(name, (), ()) for name in names))
        lookup = spec.snapshot_relation_index
    else:
        subject = fact("f", tuple(IRRole(name, "score", "Integer") for name in names))
        lookup = spec.fact_role_index
    for name, expected in (("early", 0), ("duplicate", 1), ("last", 3), ("absent", -1)):
        assert lookup(subject, name) == expected
    assert lookup(fact("f") if kind == "role" else snapshot(), "absent") == -1


def test_column_projection_retains_occurrence_identity_multiplicity_and_missing_cells():
    first = canonical_scalar(1, None)
    equal_but_distinct = replace(first)
    text = canonical_scalar("1", None)
    rows = ((text, first), (first, None), (text, equal_but_distinct), (text, first))
    admitted, actual = spec.project_optional_column(rows, 1)
    assert admitted and len(actual) == 4
    assert all(
        a is b for a, b in zip(actual, (first, None, equal_but_distinct, first), strict=True)
    )
    assert rows[1][1] is None
    actual.clear()
    assert len(rows) == 4 and rows[0][1] is first


def test_column_projection_refuses_short_rows_at_every_position():
    value = canonical_scalar(1, None)
    for bad_index in range(5):
        rows = tuple((value,) if i == bad_index else (value, value) for i in range(5))
        assert spec.project_optional_column(rows, 1) == (False, [])
    assert spec.project_optional_column(((value,),), -1) == (False, [])
    assert spec.project_optional_column((), -1) == (False, [])
    assert spec.project_optional_column((), 10000) == (True, [])
    assert spec.project_optional_column(((),), 0) == (False, [])


def test_column_projection_has_no_byte_index_or_recursion_limit():
    values = tuple(canonical_scalar(value, None) for value in range(1100))
    admitted, actual = spec.project_optional_column(tuple((value,) for value in values), 0)
    assert admitted and len(actual) == len(values)
    assert all(a is b for a, b in zip(actual, values, strict=True))




































































def test_iterative_checks_do_not_call_recursive_mathematical_references():
    module = ast.parse(inspect.getsource(spec))
    references = {
        "_value_member_reference",
        "_value_ranges_reference",
        "_value_state_reference",
        "value_violation_count",
    }
    for definition in module.body:
        if isinstance(definition, ast.FunctionDef) and definition.name not in references:
            calls = {
                node.func.id
                for node in ast.walk(definition)
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
            }
            assert not calls & references, definition.name


@pytest.mark.parametrize("variant", ["enum", "range", "ranges"])
@pytest.mark.parametrize("modality,violated", [("alethic", "fail"), ("deontic", "warning")])
def test_complete_object_value_family_composes_state_witness_and_verdict(
    variant, modality, violated
):
    low, good, bad = (canonical_scalar(value, None) for value in (1, 20, 120))
    duplicate = replace(bad)
    rule = constraint(
        variant,
        modality=modality,
        allowed=(low, good),
        minimum=low,
        maximum=canonical_scalar(100, None),
        flags=(False, False, True, True),
        ranges=((low, canonical_scalar(100, None), True, True),),
    )
    data = snapshot(rosters=(IRRoster("score", (good, bad, duplicate), ()),))
    assert spec.value_state(rule, data) == 0
    assert not spec.value_holds(rule, data)
    witness = spec.value_witness(rule, data)
    assert len(witness) == 2 and witness[0] is bad and witness[1] is duplicate
    assert spec.value_verdict(rule, data) == violated
    assert spec.value_reason(rule, data) == ""
    assert spec.band_of(((modality, violated),)) == (1 if modality == "alethic" else 0)


@pytest.mark.parametrize("variant", ["enum-role", "range-role", "ranges-role"])
def test_complete_role_value_family_selects_the_role_and_preserves_duplicates(variant):
    decoy, good, bad = (canonical_scalar(value, None) for value in (999, 20, 120))
    duplicate = replace(bad)
    roles = (IRRole("decoy", "score", "Integer"), IRRole("quantity", "score", "Integer"))
    rule = constraint(
        variant,
        role_refs=(("observed", "quantity"),),
        allowed=(good,),
        minimum=canonical_scalar(1, None),
        maximum=canonical_scalar(100, None),
        flags=(False, False, True, True),
        ranges=((canonical_scalar(1, None), canonical_scalar(100, None), True, True),),
    )
    data = snapshot(
        fact_types=(fact("observed", roles),),
        relations=(IRRelation("observed", ((decoy, good), (decoy, bad), (decoy, duplicate)), ()),),
    )
    assert spec.value_state(rule, data) == 0
    witness = spec.value_witness(rule, data)
    assert len(witness) == 2 and witness[0] is bad and witness[1] is duplicate
    assert spec.value_verdict(rule, data) == "fail"
    assert spec.value_reason(rule, data) == ""


def test_value_family_keeps_unknown_vacuous_and_refusal_routes_distinct():
    number = canonical_scalar(20, None)
    text = canonical_scalar("bad", None)
    object_empty = snapshot(rosters=(IRRoster("score", (), ()),))
    role_empty = snapshot(
        fact_types=(fact("observed", (IRRole("quantity", "score", "Integer"),)),),
        relations=(IRRelation("observed", (), ()),),
    )
    object_rule = constraint("enum", allowed=(number,))
    role_rule = constraint("enum-role", role_refs=(("observed", "quantity"),), allowed=(number,))
    assert spec.value_holds(object_rule, object_empty)
    assert spec.value_verdict(object_rule, object_empty) == "vacuous"
    assert spec.value_reason(object_rule, object_empty) == "no-observable-subjects"
    assert spec.value_witness(object_rule, object_empty) == []
    assert spec.value_holds(role_rule, role_empty)
    assert spec.value_verdict(role_rule, role_empty) == "vacuous"
    assert spec.value_reason(role_rule, role_empty) == "empty-subject"
    unknown = constraint(
        "range",
        minimum=text,
        flags=(False, False, True, True),
    )
    populated = snapshot(rosters=(IRRoster("score", (number,), ()),))
    assert spec.value_state(unknown, populated) == -1
    assert spec.value_verdict(unknown, populated) == "unchecked"
    assert spec.value_reason(unknown, populated) == "bound-type-mismatch"
    assert spec.value_witness(unknown, populated) == []
    refused = replace(unknown, refused="untyped-string-ordering")
    assert spec.value_state(refused, populated) == -1
    assert spec.value_verdict(refused, populated) == "unchecked"
    assert spec.value_reason(refused, populated) == "bound-type-mismatch"
    assert spec.value_witness(refused, populated) == []
