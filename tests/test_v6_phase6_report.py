"""New report union and legacy compatibility at the actual production builders."""
import jsonschema
import pytest

from gnd.assurance import AssuranceBlockV1
from gnd.report import (
    build_check_payload,
    build_transition_payload,
    build_verify_payload,
    load_report_schema,
)


@pytest.mark.parametrize('band,decision', [(0, 'accept'), (1, 'refuse'), (2, 'indeterminate'), (3, None), (4, 'indeterminate'), (70, None)])
def test_v7_envelope_preserves_the_actual_band(band, decision):
    payload = build_check_payload(band, 'model.orm.yaml', 'population.json', schema_version=7)
    jsonschema.validate(payload, load_report_schema())
    assert payload['exit_code'] == band
    assert payload['assurance'] == AssuranceBlockV1(decision).as_dict()
    assert payload['model_digest'] is None and payload['derivations'] is None
    legacy = build_check_payload(band, 'model.orm.yaml', 'population.json')
    projected = {k: v for k, v in payload.items() if k not in {'model_digest', 'derivations', 'assurance'}}
    projected['schema_version'] = 3
    assert projected == legacy
    jsonschema.validate(legacy, load_report_schema())

@pytest.mark.parametrize('version', [3, 4, 5, 6])
def test_frozen_versions_refuse_added_assurance(version):
    kwargs = {'model_digest': 'sha256:' + 'a' * 64} if version in (5, 6) else {}
    legacy = build_check_payload(0, 'm', 'p', schema_version=version, **kwargs)
    jsonschema.validate(legacy, load_report_schema())
    with pytest.raises(ValueError, match='legacy'):
        build_check_payload(0, 'm', 'p', schema_version=version, assurance=AssuranceBlockV1('accept'), **kwargs)
    legacy['assurance'] = AssuranceBlockV1('accept').as_dict()
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(legacy, load_report_schema())

def test_transition_and_verify_forward_the_selected_version():
    transition = build_transition_payload(3, 'm', evaluated=False, schema_version=7)
    assert transition['assurance']['semantic_decision'] is None
    jsonschema.validate(transition, load_report_schema())
    verify = build_verify_payload(3, 'm', 'p', extraction={}, schema_version=7)
    assert verify['command'] == 'verify' and verify['schema_version'] == 7
    assert verify['assurance']['assurance_level'] == 'none'

def test_structured_empty_obligations_are_an_array():
    payload = build_check_payload(3, 'm', 'p', schema_version=7, structured=True)
    assert payload['derivations'] == []
    jsonschema.validate(payload, load_report_schema())

def test_claim_cannot_change_the_semantic_decision():
    with pytest.raises(ValueError, match='band'):
        build_check_payload(1, 'm', 'p', schema_version=7, assurance=AssuranceBlockV1('accept'))
    with pytest.raises(ValueError, match='band'):
        build_check_payload(0, 'm', 'p', schema_version=7, assurance={'assurance_level': 'proof-backed'})

@pytest.mark.parametrize('kwargs', [{'scope_digest': 'A' * 64}, {'scope_digest': 'short'}, {'assurance_level': 'unknown'}, {'assurance_level': 'partial'}, {'assumptions': ('z', 'a')}, {'assumptions': ('a', 'a')}, {'uncovered_applicable_scope_ids': ['a']}])
def test_malformed_wire_claim_is_refused(kwargs):
    with pytest.raises(ValueError):
        AssuranceBlockV1('accept', **kwargs)
