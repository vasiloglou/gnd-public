"""Red-first boundary controls for the opt-in standalone acceptance profile."""
from __future__ import annotations

import copy
import runpy
from pathlib import Path

import pytest

RUNTIME = Path(__file__).resolve().parents[1] / 'src/gnd/export/pyrel_runtime.py'


def toy():
    model = {'version': 1, 'model_id': 'toy',
             'object_types': [{'id': 's', 'kind': 'value', 'primitive': 'String'},
                              {'id': 'n', 'kind': 'value', 'primitive': 'Integer'}],
             'fact_types': [{'id': ft, 'roles': [{'role_name': 'x', 'object_type': 's'},
                                                {'role_name': 'y', 'object_type': 'n'}]}
                            for ft in ['r', 's']],
             'constraints': [{'id': 'rule', 'type': 'guarded', 'modality': 'alethic',
                              'antecedent': [{'fact_type': 'r', 'bind': {'x': '$x', 'y': '$y'}}],
                              'consequent': {'atom': {'fact_type': 's', 'bind': {'x': '$x', 'y': '$y'}}}}]}
    population = {'population': {'model_id': 'toy', 'covers': ['r', 's']},
                  'facts': {'r': [{'x': 'a', 'y': 7}], 's': [{'x': 'a', 'y': 7}]}}
    return model, population


def api():
    function = runpy.run_path(str(RUNTIME)).get('acceptance_document')
    assert callable(function), 'applications-v1 acceptance interface is not implemented'
    return function


@pytest.mark.parametrize('damage', ['uncovered', 'missing-list', 'rows', 'objects', 'unknown-family', 'derived', 'primitive'])
def test_profile_admission_refuses_before_native_import(damage):
    model, population = toy()
    if damage == 'uncovered':
        population['population']['covers'].remove('s')
    elif damage == 'missing-list':
        del population['facts']['s']
    elif damage == 'rows':
        population['facts']['r'] *= 1001
    elif damage == 'objects':
        model['object_types'] += [{'id': f'x{i}', 'kind': 'value', 'primitive': 'String'} for i in range(64)]
    elif damage == 'unknown-family':
        model['constraints'][0]['type'] = 'future-family'
    elif damage == 'derived':
        model['fact_types'][1]['derivation'] = 'derived'
        model['fact_types'][1]['storage'] = 'computed'
        model['fact_types'][1]['derivation_rule'] = {'body': [{'fact_type': 'r', 'bind': {'x': '$x', 'y': '$y'}}],
                                                   'head': {'x': '$x', 'y': '$y'}}
    else:
        model['object_types'][1]['primitive'] = 'Float'
    report = api()(model, population, model_sha256='a' * 64, population_sha256='b' * 64)
    assert report['accepted'] is False and report['exit_code'] == 2
    assert report['status'] == 'incomplete'
    assert {v['constraint_ref'] for v in report['verdicts']} == {'constraints[0]'}


@pytest.mark.parametrize('damage', ['unbound', 'role', 'fact', 'extra-consequent', 'operator', 'typed-variable', 'atoms'])
def test_unsupported_guarded_shape_cannot_accept(damage):
    model, population = toy()
    rule = model['constraints'][0]
    if damage == 'unbound':
        rule['consequent']['atom']['bind']['x'] = '$unbound'
    elif damage == 'role':
        rule['antecedent'][0]['bind']['missing'] = '$x'
    elif damage == 'fact':
        rule['antecedent'][0]['fact_type'] = 'missing'
    elif damage == 'extra-consequent':
        rule['consequent']['absence'] = copy.deepcopy(rule['consequent']['atom'])
    elif damage == 'operator':
        rule['consequent'] = {'comparison': {'operator': '===', 'left': '$y', 'right': 7}}
    elif damage == 'typed-variable':
        rule['antecedent'][0]['bind']['y'] = '$x'
    else:
        rule['antecedent'] *= 9
    report = api()(model, population, model_sha256='a' * 64, population_sha256='b' * 64)
    assert report['accepted'] is False and report['exit_code'] == 2


def test_acceptance_signature_and_binding_shape():
    # Refusal is executable in the GND interpreter even though PyRel is absent.
    model, population = toy()
    population['population']['covers'] = []
    report = api()(model, population, model_sha256='a' * 64, population_sha256='b' * 64)
    assert report['schema_version'] == 1 and report['profile'] == 'applications-v1'
    assert report['binding'] == {'model_sha256': 'a' * 64, 'population_sha256': 'b' * 64}
    row = report['verdicts'][0]
    assert row['id'] == 'rule' and row['modality'] == 'alethic' and row['constraint_type'] == 'guarded'
    assert isinstance(row['witnesses'], list) and isinstance(row['reason'], str)
