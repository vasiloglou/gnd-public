

import ast
import inspect
from dataclasses import replace

import pytest
from test_v6_phase2_value_helpers import constraint, fact, snapshot

from gnd import semantic_spec as spec
from gnd.semantic_adapter import canonical_scalar
from gnd.semantic_ir import IRRelation, IRRole, IRRoster


def object_case(values, variant="enum", **changes):
    changes.setdefault("object_type", "score")
    rule = constraint(variant, **changes)
    return rule, snapshot(rosters=(IRRoster("score", tuple(values), ()),))


def role_case(rows, variant="enum-role", **changes):
    roles = (
        IRRole("decoy", "score", "Integer"),
        IRRole("quantity", "score", "Integer"),
    )
    rule = constraint(variant, role_refs=(("observed", "quantity"),), **changes)
    data = snapshot(
        fact_types=(fact("observed", roles),),
        relations=(IRRelation("observed", tuple(rows), ()),),
    )
    return rule, data


def test_cursor_is_total():
    number = canonical_scalar(1, None)
    empty = snapshot()
    for cursor in ((0, -1, -1), (1, -1, -1), (1, 100, -1), (2, -1, 0), (2, 100, 0)):
        assert spec.value_occurrence_count(cursor, empty) == -1
        assert spec.value_occurrence_scalar(cursor, empty, 0) is None
        assert spec.value_occurrence_state(cursor, constraint("enum"), empty, 0) == -1
    malformed = snapshot(
        fact_types=(fact("observed", (IRRole("quantity", "score", "Integer"),)),),
        relations=(IRRelation("observed", ((),), ()),),
    )
    rule = constraint("enum-role", role_refs=(("observed", "quantity"),), allowed=(number,))
    cursor = spec.value_cursor(rule, malformed)
    assert cursor == (2, 0, 0)
    assert spec.value_occurrence_count(cursor, malformed) == 1
    assert spec.value_occurrence_scalar(cursor, malformed, 0) is None
    assert spec.value_state(rule, malformed) == -1
    assert spec.value_witness(rule, malformed) == []


def test_cursor_is_linear(monkeypatch):
    allowed = canonical_scalar(0, None)
    values = tuple(canonical_scalar(index, None) for index in range(1100))
    rule, data = object_case(values, allowed=(allowed,))
    cursor = spec.value_cursor(rule, data)
    calls = 0
    original = spec.value_occurrence_state

    def observed(cursor_arg, constraint_arg, snapshot_arg, index):
        nonlocal calls
        calls += 1
        return original(cursor_arg, constraint_arg, snapshot_arg, index)

    monkeypatch.setattr(spec, "value_occurrence_state", observed)
    assert spec.value_cursor_state(cursor, rule, data) == 0
    assert calls == len(values)
    calls = 0
    assert len(spec.value_cursor_witness(cursor, rule, data)) == len(values) - 1
    assert calls == 2 * len(values)


@pytest.mark.parametrize("subject", ["object", "role"])
def test_value_witness_is_exact(subject):
    good = canonical_scalar(20, None)
    first = canonical_scalar(130, None)
    second = canonical_scalar(120, None)
    duplicate = replace(first)
    if subject == "object":
        rule, data = object_case((good, first, second, duplicate), allowed=(good,))
    else:
        decoy = canonical_scalar(999, None)
        rule, data = role_case(
            ((decoy, good), (decoy, first), (decoy, second), (decoy, duplicate)),
            allowed=(good,),
        )

    cursor = spec.value_cursor(rule, data)
    assert spec.value_occurrence_count(cursor, data) == 4
    witness = spec.value_witness(rule, data)
    assert len(witness) == 3
    assert witness[0] is first and witness[1] is second and witness[2] is duplicate
    assert spec.value_state(rule, data) == 0
    assert spec.value_verdict(rule, data) == "fail"


def test_public_value_path_has_no_intermediate_list_helpers():
    tree = ast.parse(inspect.getsource(spec))
    forbidden = {"value_subjects", "value_states", "violating_positions", "map_value_witness"}
    definitions = {node.name for node in tree.body if isinstance(node, ast.FunctionDef)}
    assert not definitions & forbidden
    public = {"value_state", "value_holds", "value_witness", "value_verdict", "value_reason"}
    for function in (node for node in tree.body if isinstance(node, ast.FunctionDef)):
        if function.name not in public:
            continue
        calls = {
            node.func.id
            for node in ast.walk(function)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        }
        assert not calls & forbidden, (function.name, calls & forbidden)


def test_cursor_resolution_rejects_wrong_subject_and_preserves_role_column():
    number = canonical_scalar(1, None)
    missing, empty = object_case((number,), object_type="other", allowed=(number,))
    assert spec.value_cursor(missing, empty) == (0, -1, -1)
    assert spec.value_state(missing, empty) == -1
    decoy = canonical_scalar(999, None)
    rule, data = role_case(((decoy, number),), allowed=(number,))
    assert spec.value_cursor(rule, data) == (2, 0, 1)
    assert spec.value_occurrence_scalar((2, 0, 1), data, 0) is number
    assert spec.value_occurrence_scalar((2, 0, 2), data, 0) is None













































