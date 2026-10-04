from __future__ import annotations

from dataclasses import replace

import pytest

from gnd import semantic_spec
from gnd.semantic_adapter import canonical_scalar
from gnd.semantic_ir import IRConstraint, IRFactType, IRRelation, IRRole, IRRoster, SnapshotIR

pytestmark = pytest.mark.proof

def _constraint(variant: str, **changes) -> IRConstraint:
    value = IRConstraint(ref='phase25', family='value', variant=variant, modality='alethic', fact_type='', roles=(), role_refs=(), sequences=(), object_type='score', subtypes=(), flags=(), minimum=None, maximum=None, allowed=(), ranges=(), operator='', literal=None, operands=(), consequent_kind='', antecedent=(), consequent=(), scope_fact_types=(), expression='', refused='')
    return replace(value, **changes)

def _snapshot(**changes) -> SnapshotIR:
    value = SnapshotIR(object_types=(), fact_types=(), relations=(), rosters=(), constraints=(), finite=True, covers=(), explicit_rosters=(), derivations=(), derivation_order=(), refusals=())
    return replace(value, **changes)

def _object_case(variant: str, values: tuple) -> tuple[IRConstraint, SnapshotIR]:
    low, good = (canonical_scalar(1, None), canonical_scalar(20, None))
    rule = _constraint(variant, allowed=(low, good), minimum=low, maximum=canonical_scalar(100, None), flags=(False, False, True, True), ranges=((low, canonical_scalar(100, None), True, True),))
    return (rule, _snapshot(rosters=(IRRoster('score', values, ()),)))

def _role_case(variant: str, values: tuple) -> tuple[IRConstraint, SnapshotIR]:
    low, good = (canonical_scalar(1, None), canonical_scalar(20, None))
    roles = (IRRole('quantity', 'score', 'Integer'),)
    fact = IRFactType('observed', roles, True, '', False, 'claimed', '')
    rule = _constraint(variant, role_refs=(('observed', 'quantity'),), allowed=(low, good), minimum=low, maximum=canonical_scalar(100, None), flags=(False, False, True, True), ranges=((low, canonical_scalar(100, None), True, True),))
    data = _snapshot(fact_types=(fact,), relations=(IRRelation('observed', tuple((item,) for item in values), ()),))
    return (rule, data)

def test_pass_has_empty_witness() -> None:
    good = canonical_scalar(20, None)
    rule, data = _object_case('enum', (good,))
    assert semantic_spec.value_witness(rule, data) == []

def test_unknown_has_empty_witness_and_precedes_violation() -> None:
    unknown = canonical_scalar('text', None)
    bad = canonical_scalar(120, None)
    rule, data = _object_case('range', (unknown, bad))
    assert semantic_spec.value_state(rule, data) == -1
    assert semantic_spec.value_witness(rule, data) == []

def _assert_object_family_has_nonempty_witness(variant: str) -> None:
    bad = canonical_scalar(120, None)
    rule, data = _object_case(variant, (bad,))
    assert semantic_spec.value_witness(rule, data) == [bad]

def _assert_role_family_has_nonempty_witness(variant: str) -> None:
    bad = canonical_scalar(120, None)
    rule, data = _role_case(variant, (bad,))
    assert semantic_spec.value_witness(rule, data) == [bad]

def test_enum_object_nonempty_control() -> None:
    _assert_object_family_has_nonempty_witness('enum')

def test_range_object_nonempty_control() -> None:
    _assert_object_family_has_nonempty_witness('range')

def test_ranges_object_nonempty_control() -> None:
    _assert_object_family_has_nonempty_witness('ranges')

def test_enum_role_nonempty_control() -> None:
    _assert_role_family_has_nonempty_witness('enum-role')

def test_range_role_nonempty_control() -> None:
    _assert_role_family_has_nonempty_witness('range-role')

def test_ranges_role_nonempty_control() -> None:
    _assert_role_family_has_nonempty_witness('ranges-role')

def test_duplicate_violations_produce_duplicate_occurrences() -> None:
    bad = canonical_scalar(120, None)
    rule, data = _object_case('range', (bad, bad))
    witness = semantic_spec.value_witness(rule, data)
    assert len(witness) == 2 and witness[0] is bad and (witness[1] is bad)

def test_distinct_violations_keep_original_order() -> None:
    first, second = (canonical_scalar(120, None), canonical_scalar(130, None))
    rule, data = _object_case('range', (first, second))
    witness = semantic_spec.value_witness(rule, data)
    assert len(witness) == 2 and witness[0] is first and (witness[1] is second)

def test_equal_value_distinct_identity_is_not_collapsed() -> None:
    first = canonical_scalar(120, None)
    second = replace(first)
    rule, data = _object_case('range', (first, second))
    witness = semantic_spec.value_witness(rule, data)
    assert len(witness) == 2 and witness[0] is first and (witness[1] is second)
