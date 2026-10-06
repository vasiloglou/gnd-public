"""Approved RF7 accepting/refusing siblings and shared-policy dirty controls."""
from __future__ import annotations

import importlib
import json
from decimal import Decimal
from io import BytesIO, StringIO

import pytest


def policy():
    return importlib.import_module('gnd.input_policy')


@pytest.mark.parametrize('raw', ['{"x":1,"x":2}', '{"x":NaN}', '[Infinity]', '[1e999]', '[' * 65 + '0' + ']' * 65])
def test_json_refusal(raw):
    with pytest.raises(ValueError):
        policy().loads(raw)


def test_json_acceptance_types_and_custom_hooks():
    p = policy()
    assert p.loads('{"x":1.25,"n":1,"s":"[[["}') == {'x': 1.25, 'n': 1, 's': '[[['}
    assert p.loads('[1e100]', parse_float=Decimal) == [Decimal('1e100')]
    assert p.loads('{"x":1}', object_hook=lambda value: ('object', value)) == ('object', {'x': 1})
    assert p.loads('[' * 64 + '0' + ']' * 64)
    for handle in (BytesIO(b'{"x":1}'), StringIO('{"x":1}')):
        assert p.load(handle) == {'x': 1}
    with pytest.raises(ValueError):
        p.loads('[1e999]', parse_float=Decimal)
    with pytest.raises(ValueError):
        p.loads('{"x":1,"x":2}', object_pairs_hook=lambda items: dict(items))


def test_json_decoder_trailing_and_depth():
    decoder = policy().JSONDecoder()
    assert decoder.raw_decode('{"x":1} trailing') == ({'x': 1}, 7)
    with pytest.raises(ValueError):
        decoder.decode('{"x":1} trailing')
    with pytest.raises(ValueError):
        decoder.raw_decode('[' * 65 + '0' + ']' * 65)


@pytest.mark.parametrize('raw,limits', [
    ('x: &a [1]\ny: *a', {}), ('x: 1', {'max_bytes': 3}),
    ('x: [1, 2]', {'max_events': 3}), ('x: [[1]]', {'max_depth': 2}),
])
def test_yaml_preconstruction_refusal(raw, limits):
    with pytest.raises(ValueError):
        policy().guard_yaml(raw, **limits)


def test_yaml_accepted_quote_and_limits():
    policy().guard_yaml('x: "*alias [["\ny: [1, 2]')


@pytest.mark.parametrize('value', ['2024-02-29T00:00:00Z', '2024-02-29T00:00', '2024-02-29T00:00:00.123456+01:30'])
def test_datetime_accepted(value):
    assert policy().parse_datetime(value).year == 2024


@pytest.mark.parametrize('value', ['20240229T000000', '2024-02-29 00:00:00', '2024-02-29t00:00:00z', '2024-02-29T00:00:00+0130', '2024-02-29T00:00:00+01:99', '2024-02-30T00:00:00Z', '2024-02-29T00:00:00.1234567Z', '２０２４-02-29T00:00:00Z'])
def test_datetime_refusal(value):
    with pytest.raises(ValueError):
        policy().parse_datetime(value)
