import dataclasses
import math
from itertools import pairwise

import pytest

from gnd import semantic_adapter as adapter
from gnd import semantic_ir as ir


def test_scalar_identity_and_order_are_separate():
    integer = adapter.canonical_scalar(1, 'Integer')
    floating = adapter.canonical_scalar(1.0, 'Float')
    boolean = adapter.canonical_scalar(True, 'Boolean')
    string = adapter.canonical_scalar('1', 'String')
    assert integer == floating
    assert len({(value.identity_kind, value.token) for value in (integer, boolean, string)}) == 3
    decimal = adapter.canonical_scalar(0.1, 'Number')
    assert (decimal.num, decimal.den) == (3602879701896397, 36028797018963968)
    left = adapter.canonical_scalar('2026-09-07T07:00:00-05:00', 'DateTime')
    right = adapter.canonical_scalar('2026-09-07T12:00:00Z', 'DateTime')
    assert left.kind == right.kind == 'datetime-aware'
    assert left.num == right.num and left.den == right.den == 1
    assert left.token != right.token
    assert left.identity_kind == right.identity_kind == 'string'
    date = adapter.canonical_scalar('2026-09-07', 'Date')
    assert date.identity_kind == 'string' and date.token == '2026-09-07'
    assert adapter.canonical_scalar('2026-09-07T12:00:00', 'DateTime').kind == 'datetime-naive'

@pytest.mark.parametrize('value,primitive', [(math.nan, None), (math.inf, 'Float'), (-math.inf, None), (True, 'Integer'), ([], None), ({}, None), ('wrong-date', 'Date')])
def test_unrepresentable_scalars_are_refused_without_coercion(value, primitive):
    assert adapter.canonical_scalar(value, primitive) is None

def test_scalar_datetime_arithmetic_does_not_overflow_at_calendar_boundary():
    value = adapter.canonical_scalar('0001-01-01T00:00:00+14:00', 'DateTime')
    assert value.kind == 'datetime-aware' and value.num == -50400000000

def test_numeric_order_uses_value_not_text():
    two = adapter.canonical_scalar(2, 'Integer')
    ten = adapter.canonical_scalar(10, 'Integer')
    assert two.num * ten.den < ten.num * two.den

def test_role_order_multiplicity_covers_and_explicit_instances(tmp_path):
    import support.adapter_universe as universe
    model = universe._model(tmp_path, universe.VEHICLE_TYPES, universe.VEHICLE_FACTS)
    population = universe._population(tmp_path, model, covers=['car_has_colour'], facts={'car_has_colour': [{'car': 'C1', 'colour': 'red'} for _ in range(2)]}, instances={'vehicle': ['V1', 'V1'], 'car': ['C2']})
    result = adapter.adapt_snapshot(model, population)
    assert result.covers == ('car_has_colour',)
    assert [(row.id, row.declared) for row in result.fact_types] == [('car_has_colour', True), ('vehicle_has_plate', False)]
    fact = result.fact_types[0]
    assert [(role.name, role.object_type, role.primitive) for role in fact.roles] == [('car', 'car', 'String'), ('colour', 'colour', 'String')]
    assert [tuple(cell.token for cell in row) for row in result.relations[0].rows] == [('C1', 'red'), ('C1', 'red')]
    assert [(row.object_type, tuple(value.token for value in row.members)) for row in result.explicit_rosters] == [('vehicle', ('V1', 'V1')), ('car', ('C2',))]

def test_subtype_closure_retains_grandchildren(tmp_path):
    import support.adapter_universe as universe
    model = universe._model(tmp_path, [*universe.VEHICLE_TYPES, universe._subtype('electric', 'Electric', ['car'])], universe.VEHICLE_FACTS)
    population = universe._population(tmp_path, model, instances={'electric': ['E1']})
    result = adapter.adapt_snapshot(model, population)
    types = {row.id: row for row in result.object_types}
    assert types['vehicle'].subtypes == ('car', 'electric', 'vehicle')
    assert types['car'].subtypes == ('car', 'electric')
    assert types['electric'].primitive == 'String'
    rosters = {row.object_type: row for row in result.rosters}
    assert tuple(value.token for value in rosters['vehicle'].members) == ('E1',)

def test_typed_string_range_is_preserved_without_an_untyped_refusal(tmp_path):
    import support.adapter_universe as universe
    model = universe._model(tmp_path, universe.VEHICLE_TYPES, universe.VEHICLE_FACTS, [{'type': 'value', 'object_type': 'plate', 'range': {'min': 'A', 'max': 'Z'}, 'modality': 'alethic', 'source': 'explicit', 'status': 'confirmed', 'provenance': {'user_quote': 'Plates range from A to Z.'}}])
    population = universe._population(tmp_path, model, instances={'plate': ['M']})
    result = adapter.adapt_snapshot(model, population).constraints[0]
    assert result.refused == ''
    assert result.ranges[0][0].kind == 'string'
    assert not result.ranges[0][0].ordered

def test_date_coordinates_preserve_calendar_order_and_leap_days():
    expected = (('1900-02-28', 693654), ('1900-03-01', 693655), ('2000-02-28', 730178), ('2000-02-29', 730179), ('2000-03-01', 730180))
    scalars = [adapter.canonical_scalar(value, 'Date') for value, _ in expected]
    assert [(item.num, item.den, item.ordered) for item in scalars] == [(ordinal, 1, True) for _, ordinal in expected]
    assert all((a.num * b.den < b.num * a.den for a, b in pairwise(scalars)))

def test_datetime_coordinates_retain_every_instant_component():
    expected = (('2000-01-01T00:00:00Z', 63082281600000000), ('2024-02-29T12:34:56.123456Z', 63844806896123456), ('2024-02-29T12:34:56.123456+05:30', 63844787096123456), ('2024-02-29T12:34:56.123456-03:15', 63844818596123456))
    for spelling, microseconds in expected:
        value = adapter.canonical_scalar(spelling, 'DateTime')
        assert (value.num, value.den) == (microseconds, 1)
        assert value.kind == 'datetime-aware' and value.token == spelling
    naive = adapter.canonical_scalar('2024-02-29T12:34:56.123456', 'DateTime')
    assert naive.kind == 'datetime-naive' and naive.num == 63844806896123456

def test_ir_container_fields_do_not_require_unsupported_dataclass_defaults():
    unsupported = [(name, field.name) for name, value in vars(ir).items() if isinstance(value, type) and dataclasses.is_dataclass(value) for field in dataclasses.fields(value) if isinstance(field.default, tuple)]
    assert not unsupported, unsupported
