from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from gnd.extract.refscheme import applicable_set, reference_identity
from gnd.model import load_model

FIXTURES = Path(__file__).parent / 'fixtures'
FULL_VOCAB = FIXTURES / 'models' / 'full_vocabulary.orm.yaml'
DISPATCH = FIXTURES / 'models' / 'dispatch.orm.yaml'
SETFAM = FIXTURES / 'checker' / 'setfam.orm.yaml'
RING = FIXTURES / 'checker' / 'ring.orm.yaml'

def test_repeated_composite_component_types_are_not_cycles() -> None:
    model = SimpleNamespace(object_types=[{'id': 'pair', 'kind': 'entity', 'reference': {'mode': 'external'}}, {'id': 'code', 'kind': 'entity', 'reference': {'mode': 'popular', 'value_type': 'code_value'}}, {'id': 'code_value', 'kind': 'value', 'primitive': 'string'}], fact_types=[{'id': 'pair_has_left_code', 'roles': [{'role_name': 'pair', 'object_type': 'pair'}, {'role_name': 'left', 'object_type': 'code'}]}, {'id': 'pair_has_right_code', 'roles': [{'role_name': 'pair', 'object_type': 'pair'}, {'role_name': 'right', 'object_type': 'code'}]}], constraints=[{'type': 'uniqueness', 'scope': 'external', 'role_refs': [{'fact_type': 'pair_has_left_code', 'role': 'left'}, {'fact_type': 'pair_has_right_code', 'role': 'right'}]}])
    kind, role_refs = reference_identity('pair', model)
    assert kind == 'composite'
    assert [row['path'] for row in role_refs] == ['direct', 'direct']

def test_nested_composites_are_declared_unmatchable_until_consumers_support_them() -> None:
    model = SimpleNamespace(object_types=[{'id': 'outer', 'kind': 'entity', 'reference': {'mode': 'external'}}, {'id': 'inner', 'kind': 'entity', 'reference': {'mode': 'external'}}, {'id': 'code', 'kind': 'entity', 'reference': {'mode': 'popular', 'value_type': 'code_value'}}, {'id': 'code_value', 'kind': 'value', 'primitive': 'string'}], fact_types=[{'id': 'inner_has_code', 'roles': [{'role_name': 'inner', 'object_type': 'inner'}, {'role_name': 'code', 'object_type': 'code'}]}, {'id': 'outer_has_inner', 'roles': [{'role_name': 'outer', 'object_type': 'outer'}, {'role_name': 'inner', 'object_type': 'inner'}]}], constraints=[{'type': 'uniqueness', 'scope': 'external', 'role_refs': [{'fact_type': 'inner_has_code', 'role': 'code'}]}, {'type': 'uniqueness', 'scope': 'external', 'role_refs': [{'fact_type': 'outer_has_inner', 'role': 'inner'}]}])
    kind, reason = reference_identity('outer', model)
    assert kind == 'unmatchable'
    assert 'nested composite joins are not supported' in reason
    fact_row = next((row for row in applicable_set(model)['fact_types'] if row['id'] == 'outer_has_inner'))
    assert fact_row['applicable'] is False

def test_applicable_set_full_vocabulary() -> None:
    model = load_model(str(FULL_VOCAB))
    result = applicable_set(model)
    object_rows = {row['id']: row for row in result['object_types']}
    assignment = object_rows['assignment']
    assert assignment['path'] == 'composite'
    pairs = [(ref['fact_type'], ref['role']) for ref in assignment['role_refs']]
    assert pairs == [('assignment_of_employee', 'employee'), ('assignment_on_project', 'project')], f'composite resolution must consume role_refs (PANEL-5); got {pairs}'
    salary = object_rows['salary']
    assert salary['path'] == 'unmatchable'
    reason = salary['reason']
    for fragment in ('unit-based', 'USD', 'Money', 'external uniqueness'):
        assert fragment in reason, f'the unmatchable reason must be a mechanism naming unit-based mode, the declared unit/measure_type and the absent anchoring external UC; missing {fragment!r} in: {reason}'
    fact_rows = result['fact_types']
    assert len(fact_rows) == 16
    inapplicable = [row for row in fact_rows if not row['applicable']]
    assert [row['id'] for row in inapplicable] == ['employee_earns_salary'], f"exactly 1 of 16 fact types is unmeasurable with a stated mechanism (R-10′) — got {[row['id'] for row in inapplicable]}"
    assert inapplicable[0]['reason'], 'an inapplicable row must carry its mechanism'
    applicable_ids = {row['id'] for row in fact_rows if row['applicable']}
    assert {'assignment_of_employee', 'assignment_on_project', 'assignment_has_hours', 'assignment_has_overtime_hours'} <= applicable_ids, 'the four assignment_* fact types are recovered via the composite path — 1/16, not 5/16'
    for row in fact_rows:
        if row['applicable']:
            assert row['reason'] is None, f"reason must be null-when-applicable; {row['id']} carries one"

def test_applicable_set_dispatch() -> None:
    model = load_model(str(DISPATCH))
    result = applicable_set(model)
    object_rows = {row['id']: row for row in result['object_types']}
    assert len(object_rows) == 13
    delivery = object_rows['delivery']
    assert delivery['path'] == 'composite', f"delivery is external-mode and must resolve composite via the external UC's role_refs; got {delivery['path']}"
    pairs = [(ref['fact_type'], ref['role']) for ref in delivery['role_refs']]
    assert pairs == [('delivery_of_parcel', 'parcel'), ('delivery_on_route', 'route')], f'composite resolution must consume role_refs (PANEL-5); got {pairs}'
    assert [(ref['object_type'], ref['path'], ref['value_type']) for ref in delivery['role_refs']] == [('parcel', 'direct', 'parcel_code'), ('route', 'direct', 'route_name')]
    unmatchable = [row for row in result['object_types'] if row['path'] == 'unmatchable']
    assert unmatchable == [], f"dispatch declares no unit-based entity, so nothing is unmatchable: {[row['id'] for row in unmatchable]}"
    assert reference_identity('route', model) == ('direct', 'route_name')
    assert reference_identity('courier', model) == ('direct', 'courier_id')
    fact_rows = result['fact_types']
    assert len(fact_rows) == 12
    inapplicable = [row for row in fact_rows if not row['applicable']]
    assert inapplicable == [], f"every dispatch fact type is applicable once delivery resolves composite; inapplicable: {[row['id'] for row in inapplicable]}"
    assert {'delivery_of_parcel', 'delivery_on_route', 'delivery_by_courier', 'delivery_has_stop_count'} <= {row['id'] for row in fact_rows}
    for row in fact_rows:
        assert row['reason'] is None, f"reason must be null-when-applicable; {row['id']} carries one"

def test_applicable_set_setfam() -> None:
    model = load_model(str(SETFAM))
    result = applicable_set(model)
    booking = next((r for r in result['object_types'] if r['id'] == 'booking'))
    assert booking['path'] == 'composite'
    pairs = [(ref['fact_type'], ref['role']) for ref in booking['role_refs']]
    assert pairs == [('booking_by_person', 'person'), ('booking_of_room', 'room')]
    fact_rows = result['fact_types']
    assert len(fact_rows) == 12
    assert all((row['applicable'] for row in fact_rows)), f"every setfam fact type is applicable once booking resolves composite; inapplicable: {[r['id'] for r in fact_rows if not r['applicable']]}"

def test_applicable_set_ring() -> None:
    model = load_model(str(RING))
    result = applicable_set(model)
    unmatchable = [r for r in result['object_types'] if r['path'] == 'unmatchable']
    assert unmatchable == [], f'ring has no unresolvable entity: {unmatchable}'
    assert all((row['applicable'] for row in result['fact_types']))
    kind, payload = reference_identity('node', model)
    assert (kind, payload) == ('direct', 'node_id')
