"""Reproduced PA1 reviewer findings; expectations precede the repair."""
import copy
import importlib.metadata
import json
import runpy

import pytest
from test_pyrel_application_acceptance import RUNTIME, api, toy
from test_pyrel_application_native import execute_cases


@pytest.mark.parametrize('damage', ['value-type', 'subset-role', 'mandatory-role'])
def test_malformed_profile_shape_has_input_error(damage):
    model, pop = toy()
    if damage == 'value-type':
        model['constraints'] = [{'type': 'value', 'object_type': ['n'], 'allowed': [7]}]
    elif damage == 'subset-role':
        model['constraints'] = [{'type': 'subset', 'subset_role_seq': [{'fact_type': 'r', 'role': ['x']}],
                                 'superset_role_seq': [{'fact_type': 's', 'role': 'x'}]}]
    else:
        model['constraints'] = []
        model['fact_types'][0]['constraints'] = [{'type': 'mandatory'}]
    with pytest.raises(ValueError):
        api()(model, pop, model_sha256='a' * 64, population_sha256='b' * 64)


def test_consequent_work_is_part_of_conservative_guard_budget():
    model, pop = toy()
    pop['facts'] = {f: [{'x': 'a', 'y': 7}] * 400 for f in ['r', 's']}
    model['constraints'][0]['consequent'] = {'absence': {'fact_type': 's', 'bind': {}}}
    report = api()(model, pop, model_sha256='a' * 64, population_sha256='b' * 64)
    assert report['status'] == 'incomplete' and report['exit_code'] == 2
    assert report['verdicts'][0]['reason'] == 'guarded-join-work-limit'


def test_unexpected_native_status_never_accepts(monkeypatch):
    namespace = runpy.run_path(str(RUNTIME))
    function = namespace['acceptance_document']
    monkeypatch.setattr(importlib.metadata, 'version', lambda name: {'relationalai': '1.30.1', 'duckdb': '1.5.5'}[name])
    class FutureOracle:
        def __init__(self, *_args, **_kwargs):
            pass
        def profile_evaluate(self, *_):
            return 'future-status', []
    monkeypatch.setitem(function.__globals__, 'ApplicationOracle', FutureOracle)
    model, pop = toy()
    report = function(model, pop, model_sha256='a' * 64, population_sha256='b' * 64)
    assert not report['accepted'] and report['exit_code'] == 2


def test_missing_acceptance_output_directory_is_operational_failure(tmp_path, monkeypatch):
    model, pop = toy()
    pop['population']['covers'] = []
    path = tmp_path / 'pop.json'
    path.write_text(json.dumps(pop))
    main = runpy.run_path(str(RUNTIME))['program_main']
    monkeypatch.setitem(main.__globals__, 'MODEL_TEXT', json.dumps(model))
    monkeypatch.setitem(main.__globals__, 'EXPORT_CONFIG', {'connection': None, 'duckdb_path': ':memory:'})
    assert main([str(path), '--accept', '--out', str(tmp_path / 'missing/report.json')]) == 70


@pytest.mark.pyrel_oracle
@pytest.mark.parametrize('shape', ['value-roster', 'inline-value', 'inline-subset', 'inline-guarded', 'inline-mandatory'])
def test_vacuity_scope_does_not_turn_empty_subjects_into_acceptance(tmp_path, shape):
    model, pop = toy()
    model['constraints'] = []
    pop['facts']['r'] = []
    if shape == 'value-roster':
        pop['facts']['s'] = []
        pop['instances'] = {'n': [7]}
        constraint = {'type': 'value', 'object_type': 'n', 'allowed': [7]}
        model['constraints'] = [constraint]
    elif shape == 'inline-value':
        constraint = {'type': 'value', 'object_type': 'n', 'allowed': [7]}
        model['fact_types'][0]['constraints'] = [constraint]
    elif shape == 'inline-subset':
        constraint = {'type': 'subset', 'subset_role_seq': [{'fact_type': 'r', 'role': 'x'}],
                      'superset_role_seq': [{'fact_type': 's', 'role': 'x'}]}
        model['fact_types'][0]['constraints'] = [constraint]
    elif shape == 'inline-guarded':
        constraint = {'type': 'guarded', 'antecedent': [{'fact_type': 's', 'bind': {'x': '$x'}}],
                      'consequent': {'atom': {'fact_type': 's', 'bind': {'x': '$x'}}}}
        model['fact_types'][0]['constraints'] = [constraint]
    else:
        constraint = {'type': 'mandatory', 'role': 'x'}
        model['fact_types'][0]['constraints'] = [constraint]
    constraint.update(source='explicit', status='confirmed', modality='alethic',
                      provenance={'user_quote': 'Regression fixture constraint.'})
    model['object_types'][0]['id'] = 'string_type'
    for fact in model['fact_types']:
        fact['reading'] = '{string_type} relates to {n}'
        for role in fact['roles']:
            if role['object_type'] == 's':
                role['object_type'] = 'string_type'
    # Independently confirm the premise through the public GND checker.
    from gnd.api import check
    source = tmp_path / 'model.json'; population = tmp_path / 'pop.json'
    pop['population'].update(model='model.json', source='synthetic')
    source.write_text(json.dumps(model)); population.write_text(json.dumps(pop))
    report_gnd = check(source, population)
    if shape in {'inline-subset', 'inline-guarded'}:
        assert report_gnd['outcome'] == 'ill_formed', report_gnd
    else:
        assert report_gnd['verdicts'], report_gnd
        assert report_gnd['verdicts'][0]['verdict'] == ('vacuous' if shape == 'inline-mandatory' else 'pass'), report_gnd
    report = execute_cases(tmp_path, [{'model': model, 'population': pop}])[0]
    if shape == 'value-roster':
        assert report['accepted'] and report['exit_code'] == 0, report
    else:
        assert not report['accepted'] and report['exit_code'] == 2, report
        assert report['verdicts'][0]['status'] in {'vacuous', 'incomplete'}, report


@pytest.mark.pyrel_oracle
def test_repeated_calls_use_model_specific_legacy_negation(tmp_path):
    model, pop = toy()
    cases = [{'model': copy.deepcopy(model), 'population': copy.deepcopy(pop)}]
    model['constraints'] = []
    model['fact_types'][0]['constraints'] = [{'type': 'mandatory', 'role': 'x'}]
    pop['instances'] = {'s': ['missing']}
    cases.append({'model': copy.deepcopy(model), 'population': copy.deepcopy(pop)})
    model['fact_types'][0]['constraints'] = []
    model['constraints'] = [{'type': 'subset', 'subset_role_seq': [{'fact_type': 'r', 'role': 'x'}],
                            'superset_role_seq': [{'fact_type': 's', 'role': 'x'}]}]
    pop['facts']['s'] = []
    cases.append({'model': model, 'population': pop})
    reports = execute_cases(tmp_path, cases)
    assert [r['status'] for r in reports] == ['accepted', 'rejected', 'rejected'], reports


@pytest.mark.parametrize('mode', ['require', 'named', 'persisted', 'config-file'])
def test_execution_context_refusal_writes_bound_report(tmp_path, monkeypatch, mode):
    model, pop = toy()
    raw = json.dumps(pop)
    path = tmp_path / 'pop.json'; path.write_text(raw)
    output = tmp_path / 'report.json'
    main = runpy.run_path(str(RUNTIME))['program_main']
    monkeypatch.setitem(main.__globals__, 'MODEL_TEXT', json.dumps(model))
    config = {'connection': None, 'duckdb_path': ':memory:'}
    monkeypatch.setitem(main.__globals__, 'EXPORT_CONFIG', config)
    options = []
    if mode == 'require':
        options = ['--mode', 'require']
    elif mode == 'named':
        config['connection'] = 'remote'
    elif mode == 'persisted':
        config['duckdb_path'] = 'persistent.db'
    else:
        options = ['--config', str(tmp_path / 'ambient.yaml')]
    assert main([str(path), '--out', str(output), '--accept', *options]) == 2
    report = json.loads(output.read_text())
    assert not report['accepted'] and report['status'] == 'incomplete'
    assert 'in-memory local select' in report['verdicts'][0]['reason']


def test_raw_size_refusal_is_incomplete_without_false_binding(tmp_path, monkeypatch):
    model, _ = toy()
    path = tmp_path / 'too-large.json'; path.write_text(' ' * 1_048_577)
    main = runpy.run_path(str(RUNTIME))['program_main']
    monkeypatch.setitem(main.__globals__, 'MODEL_TEXT', json.dumps(model))
    monkeypatch.setitem(main.__globals__, 'EXPORT_CONFIG', {'connection': None, 'duckdb_path': ':memory:'})
    output = tmp_path / 'report.json'
    assert main([str(path), '--out', str(output), '--accept']) == 2
    assert not output.exists()  # Unread full bytes cannot have an honest SHA binding.


@pytest.mark.parametrize('statuses,exit_code', [(['error', 'violated'], 70),
                                               (['incomplete', 'violated'], 2),
                                               (['vacuous', 'warning'], 2),
                                               (['warning', 'violated'], 1)])
def test_mixed_precedence_and_evaluation_exception(monkeypatch, statuses, exit_code):
    function = api()
    monkeypatch.setattr(importlib.metadata, 'version', lambda name: {'relationalai': '1.30.1', 'duckdb': '1.5.5'}[name])
    class SeededOracle:
        def __init__(self, *_args, **_kwargs):
            self.remaining = iter(statuses)
        def profile_evaluate(self, *_):
            status = next(self.remaining)
            if status == 'error':
                raise RuntimeError('seeded-native-evaluation-error')
            return ('violated' if status == 'warning' else status), []
    monkeypatch.setitem(function.__globals__, 'ApplicationOracle', SeededOracle)
    model, pop = toy()
    model['constraints'] *= 2
    model['constraints'] = [dict(copy.deepcopy(rule), modality='deontic' if status == 'warning' else 'alethic')
                            for rule, status in zip(model['constraints'], statuses, strict=True)]
    report = function(model, pop, model_sha256='a' * 64, population_sha256='b' * 64)
    assert report['exit_code'] == exit_code and not report['accepted']
    if 'error' in statuses:
        assert 'seeded-native-evaluation-error' in report['verdicts'][0]['reason']


@pytest.mark.pyrel_oracle
def test_native_shared_join_partial_binding_string_and_left_literal(tmp_path):
    cases, expected = [], []
    for operator, right, status in [('=', 'a', 'satisfied'), ('!=', 'a', 'violated'), ('<>', 'a', 'violated')]:
        model, pop = toy()
        model['constraints'][0]['consequent'] = {'comparison': {'operator': operator, 'left': '$x', 'right': right}}
        cases.append({'model': model, 'population': pop}); expected.append(status)
    model, pop = toy()
    model['constraints'][0]['antecedent'][0]['bind'] = {'y': '$y'}
    model['constraints'][0]['consequent'] = {'comparison': {'operator': '>', 'left': 7, 'right': '$y'}}
    cases.append({'model': model, 'population': pop}); expected.append('violated')
    model, pop = toy()
    pop['facts']['s'][0]['y'] = 8
    model['constraints'][0]['antecedent'].append({'fact_type': 's', 'bind': {'x': '$x', 'y': '$z'}})
    model['constraints'][0]['consequent'] = {'comparison': {'operator': '>', 'left': '$y', 'right': '$z'}}
    cases.append({'model': model, 'population': pop}); expected.append('violated')
    reports = execute_cases(tmp_path, cases)
    assert [r['verdicts'][0]['status'] for r in reports] == expected, reports
    assert reports[-1]['verdicts'][0]['witnesses'] == [{'$x': 'a', '$y': 7, '$z': 8}]
    assert reports[-2]['verdicts'][0]['witnesses'] == [{'$y': 7}]


@pytest.mark.parametrize('position', ['population', 'atom', 'comparison', 'allowed'])
@pytest.mark.parametrize('value', [2**53, -(2**53)])
def test_signed_integer_bound_covers_literals_and_population(position, value):
    model, pop = toy()
    if position == 'population':
        pop['facts']['r'][0]['y'] = value
    elif position == 'atom':
        model['constraints'][0]['antecedent'][0]['bind']['y'] = value
    elif position == 'comparison':
        model['constraints'][0]['consequent'] = {'comparison': {'operator': '=', 'left': '$y', 'right': value}}
    else:
        model['constraints'] = [{'type': 'value', 'object_type': 'n', 'allowed': [value]}]
    report = api()(model, pop, model_sha256='a' * 64, population_sha256='b' * 64)
    assert report['exit_code'] == 2 and not report['accepted']


@pytest.mark.pyrel_oracle
def test_native_integer_endpoints_and_zero_constraints(tmp_path):
    cases = []
    for value in [2**53 - 1, -(2**53 - 1)]:
        model, pop = toy()
        pop['facts']['r'][0]['y'] = value
        model['constraints'][0]['consequent'] = {'comparison': {'operator': '=', 'left': '$y', 'right': value}}
        cases.append({'model': model, 'population': pop})
    model, pop = toy(); model['constraints'] = []
    cases.append({'model': model, 'population': pop})
    reports = execute_cases(tmp_path, cases)
    assert all(report['accepted'] and report['exit_code'] == 0 for report in reports), reports


@pytest.mark.pyrel_oracle
def test_cross_type_subset_refuses_instead_of_accepting_invalid_model(tmp_path):
    from gnd.api import check
    model, pop = toy()
    model['object_types'][0]['id'] = 'base_text'
    model['object_types'].append({'id': 'other_text', 'kind': 'value', 'primitive': 'String'})
    for fact in model['fact_types']:
        fact['reading'] = '{base_text} relates to {n}'
        fact['roles'][0]['object_type'] = 'base_text'
    model['fact_types'].append({'id': 'q', 'reading': '{other_text} relates to {n}',
                                'roles': [{'role_name': 'z', 'object_type': 'other_text'},
                                          {'role_name': 'y', 'object_type': 'n'}]})
    model['constraints'] = [{'type': 'subset', 'source': 'explicit', 'status': 'confirmed',
                             'modality': 'alethic', 'provenance': {'user_quote': 'Subset regression.'},
                             'subset_role_seq': [{'fact_type': 'r', 'role': 'x'}],
                             'superset_role_seq': [{'fact_type': 'q', 'role': 'z'}]}]
    pop['facts']['q'] = [{'z': 'a', 'y': 7}]
    pop['population']['covers'].append('q')
    pop['population'].update(model='model.json', source='synthetic')
    source = tmp_path / 'model.json'; population = tmp_path / 'population.json'
    source.write_text(json.dumps(model)); population.write_text(json.dumps(pop))
    gnd_result = check(source, population)
    assert gnd_result['outcome'] == 'ill_formed', gnd_result
    assert 'semantic:role-seq-type-compat' in {r['rule_id'] for r in gnd_result['issues']}
    report = execute_cases(tmp_path, [{'model': model, 'population': pop}])[0]
    assert report['exit_code'] == 2 and not report['accepted'], report
    assert report['verdicts'][0]['reason'] == 'subset-role-types-outside-application-profile'


def test_embedded_model_size_refuses_before_population_read(tmp_path, monkeypatch):
    main = runpy.run_path(str(RUNTIME))['program_main']
    monkeypatch.setitem(main.__globals__, 'MODEL_TEXT', ' ' * 1_048_577)
    monkeypatch.setitem(main.__globals__, 'EXPORT_CONFIG', {'connection': None, 'duckdb_path': ':memory:'})
    out = tmp_path / 'result.json'
    assert main([str(tmp_path / 'missing.json'), '--accept', '--out', str(out)]) == 2
    assert not out.exists()
