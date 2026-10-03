"""Mapping-backed transition JSON witnesses retain their values and guards."""
from types import MappingProxyType

import pytest

from gnd.report import build_transition_payload
from gnd.transition import TransitionReport, TransitionVerdict


@pytest.mark.parametrize('family,scope,kind,extra',[
    ('pre_snapshot','transition:compiled-subset:n-a:violated:alethic','compiled-subset',{}),
    ('frame','transition:frame-delta:undeclared-assert:violated:alethic','frame-delta',{'direction':'undeclared-assert'}),
])
def test_mapping_backed_transition_witness_reaches_json(family,scope,kind,extra):
    witness = MappingProxyType({'value':'generic'})
    verdict = TransitionVerdict(scope_id=scope,family=family,kind=kind,locator='$.fixture',modality='alethic',verdict='fail',message='generic mapping-backed fixture',offending_facts=[witness],**extra)
    assert verdict.offending_facts[0] is witness
    key = 'frame_verdicts' if family == 'frame' else 'pre_snapshot_verdicts'
    report = TransitionReport(**{key:[verdict]})
    payload = build_transition_payload(1,'model.orm.yaml',evaluated=True,transition_report=report)
    assert payload['exit_code'] == 1
    assert payload['transition']['evaluated'] is True
    assert payload['transition'][key][0]['offending_facts'] == [{'value':'generic'}]

import math
from datetime import date

from gnd.checker import CheckReport, ConstraintVerdict
from gnd.report import NonJsonValueError, build_plan_transition_payload, render_json
from gnd.transition import StepResult


def _snapshot(witness):
    row = ConstraintVerdict(scope_id='snapshot:uniqueness:inline:violated:alethic', constraint_ref='fixture', constraint_type='uniqueness', modality='alethic', source='explicit', status='confirmed', verdict='fail', message='generic snapshot fixture', offending_facts=[witness])
    return CheckReport(verdicts=[row])


@pytest.mark.parametrize('location', ['pre_snapshot', 'post_snapshot', 'intermediate', 'step'])
def test_nested_transition_locations_normalize_without_mutating(location):
    nested = MappingProxyType({'flag': False, 'integer': 1, 'nested': (MappingProxyType({'date': date(2026, 1, 1)}),)})
    report = TransitionReport()
    if location == 'step':
        row = TransitionVerdict(scope_id='transition:precondition:n-a:violated:alethic', family='step', kind='precondition', locator='$.fixture', modality='alethic', verdict='fail', message='generic step fixture', offending_facts=[nested])
        report.steps = [StepResult(index=1, operation='fixture', bindings={}, verdicts=[row])]
    elif location == 'intermediate':
        report.steps = [StepResult(index=1, operation='fixture', bindings={}, intermediate=_snapshot(nested))]
    else:
        setattr(report, location, _snapshot(nested))
    before = report.model_dump(mode='python')
    payload = build_transition_payload(1, 'model.orm.yaml', evaluated=True, transition_report=report)
    block = payload['transition']
    target = block['steps'][0]['verdicts'] if location == 'step' else block['steps'][0]['intermediate']['verdicts'] if location == 'intermediate' else block[location]['verdicts']
    assert target[0]['offending_facts'] == [{'flag': False, 'integer': 1, 'nested': [{'date': '2026-01-01'}]}]
    assert type(target[0]['offending_facts'][0]['flag']) is bool
    assert type(target[0]['offending_facts'][0]['integer']) is int
    assert report.model_dump(mode='python') == before
    assert isinstance(nested['nested'][0], MappingProxyType)


@pytest.mark.parametrize('value', [math.nan, math.inf, -math.inf])
def test_mapping_transition_witness_retains_nonfinite_refusal(value):
    report = TransitionReport(pre_snapshot=_snapshot(MappingProxyType({'value': value})))
    payload = build_transition_payload(1, 'model.orm.yaml', evaluated=True, transition_report=report)
    actual = payload['transition']['pre_snapshot']['verdicts'][0]['offending_facts'][0]['value']
    assert math.isnan(actual) if math.isnan(value) else actual == value
    with pytest.raises(NonJsonValueError):
        render_json(payload)


def test_computed_post_builder_inherits_mapping_witness_totality():
    report = TransitionReport(pre_snapshot=_snapshot(MappingProxyType({'value': 'generic'})))
    payload = build_plan_transition_payload(1, 'model.orm.yaml', evaluated=True, transition_report=report)
    assert payload['transition']['pre_snapshot']['verdicts'][0]['offending_facts'] == [{'value': 'generic'}]
    assert payload['transition']['frame_verdicts'] is None


@pytest.mark.parametrize("witness, expected_keys, refuses", [
    ({1: math.nan, "finite": 2}, ["1", "finite"], True),
    ({True: math.nan, None: 3}, ["true", "None"], True),
    ({"nested": {1: {"value": math.nan}, None: 2}}, ["nested"], True),
    ({1: math.nan, "1": 2}, ["1"], False),
    ({1: 2, "1": math.nan}, ["1"], True),
])
def test_nonstring_witness_keys_keep_json_mode_order_and_collision_policy(
    witness, expected_keys, refuses
):
    report = TransitionReport(pre_snapshot=_snapshot(witness))
    payload = build_transition_payload(1, "model.orm.yaml", evaluated=True, transition_report=report)
    actual = payload["transition"]["pre_snapshot"]["verdicts"][0]["offending_facts"][0]
    assert list(actual) == expected_keys
    if "nested" in actual:
        assert list(actual["nested"]) == ["1", "None"]
    if refuses:
        with pytest.raises(NonJsonValueError):
            render_json(payload)
    else:
        assert actual == {"1": 2}
        assert render_json(payload)
