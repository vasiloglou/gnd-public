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


@pytest.mark.parametrize('damage', ['uncovered', 'uncovered-antecedent', 'missing-list', 'rows', 'objects', 'unknown-family', 'derived', 'primitive'])
def test_profile_admission_refuses_before_native_import(damage):
    model, population = toy()
    if damage == 'uncovered':
        population['population']['covers'].remove('s')
    elif damage == 'uncovered-antecedent':
        population['population']['covers'].remove('r')
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


@pytest.mark.parametrize('damage', ['integer-limit', 'fact-limit', 'constraint-limit', 'role-limit',
                                   'join-limit', 'bytes', 'version', 'root-field', 'object-field',
                                   'fact-field', 'role-field', 'storage', 'label', 'scope', 'modality',
                                   'empty-key', 'value-shape', 'subset-shape', 'subset-fact', 'subset-role',
                                   'atom-shape', 'comparison-shape', 'comparison-literal',
                                   'comparison-type', 'string-order', 'consequent-kind'])
def test_each_profile_boundary_has_a_discriminating_case(damage):
    model, pop = toy()
    rule = model['constraints'][0]
    if damage == 'integer-limit':
        pop['facts']['r'][0]['y'] = 2**53
    elif damage == 'fact-limit':
        for i in range(31):
            fact = copy.deepcopy(model['fact_types'][0])
            fact['id'] = f'f{i}'
            model['fact_types'].append(fact)
            pop['facts'][fact['id']] = []
            pop['population']['covers'].append(fact['id'])
    elif damage == 'constraint-limit':
        model['constraints'] *= 65
    elif damage == 'role-limit':
        fact = model['fact_types'][0]
        for i in range(7):
            fact['roles'].append({'role_name': f'z{i}', 'object_type': 's'})
            pop['facts']['r'][0][f'z{i}'] = 'a'
    elif damage == 'join-limit':
        pop['facts']['r'] *= 317
        rule['antecedent'] *= 2
    elif damage == 'bytes':
        pop['facts']['r'][0]['x'] = 'x' * 1_048_576
    elif damage == 'version':
        model['version'] = 3
    elif damage == 'root-field':
        model['future'] = True
    elif damage == 'object-field':
        model['object_types'][0]['future'] = True
    elif damage == 'fact-field':
        model['fact_types'][0]['future'] = True
    elif damage == 'role-field':
        model['fact_types'][0]['roles'][0]['future'] = True
    elif damage == 'storage':
        model['fact_types'][0]['storage'] = 'computed'
    elif damage in {'label', 'scope', 'modality'}:
        rule[{'label': 'id', 'scope': 'scope', 'modality': 'modality'}[damage]] = {'future': True}
    elif damage == 'empty-key':
        model['constraints'] = []
        model['fact_types'][0]['constraints'] = [{'type': 'uniqueness', 'roles': []}]
    elif damage == 'value-shape':
        model['constraints'] = [{'type': 'value', 'object_type': 'missing', 'allowed': []}]
    elif damage.startswith('subset-'):
        model['constraints'] = [{'type': 'subset', 'subset_role_seq': [{'fact_type': 'r', 'role': 'x'}],
                                 'superset_role_seq': [{'fact_type': 's', 'role': 'x'}]}]
        seq = model['constraints'][0]['subset_role_seq']
        if damage == 'subset-shape':
            seq.append(copy.deepcopy(seq[0]))
        else:
            seq[0]['fact_type' if damage == 'subset-fact' else 'role'] = 'missing'
    elif damage == 'atom-shape':
        rule['antecedent'][0]['extra'] = True
    elif damage == 'consequent-kind':
        rule['consequent'] = {'exists': {}}
    else:
        comparison = {'operator': '=', 'left': '$y', 'right': 7}
        rule['consequent'] = {'comparison': comparison}
        if damage == 'comparison-shape':
            comparison['extra'] = True
        elif damage == 'comparison-literal':
            comparison['right'] = 7.5
        elif damage == 'comparison-type':
            comparison['right'] = '7'
        else:
            comparison.update(left='$x', right='a', operator='<')
    report = api()(model, pop, model_sha256='a' * 64, population_sha256='b' * 64)
    assert report['status'] == 'incomplete' and report['accepted'] is False
    assert report['exit_code'] == 2 and all(row['reason'] for row in report['verdicts'])


def test_engine_failure_without_constraints_cannot_accept(monkeypatch):
    import importlib.metadata
    model, pop = toy()
    model['constraints'] = []
    monkeypatch.setattr(importlib.metadata, 'version', lambda _: 'wrong-version')
    report = api()(model, pop, model_sha256='a' * 64, population_sha256='b' * 64)
    assert report['status'] == 'runtime_failure' and report['exit_code'] == 70
    assert report['accepted'] is False


def test_native_result_cap_refuses_and_native_exception_withholds(monkeypatch):
    import importlib.metadata
    namespace = runpy.run_path(str(RUNTIME))
    oracle = namespace['ApplicationOracle']
    monkeypatch.setattr(namespace['PyrelOracle'], '_rows', lambda *_: [[0]] * 10001)
    with pytest.raises(namespace['ProfileRefusal'], match='native-result-tuple-limit'):
        object.__new__(oracle)._rows(None)
    monkeypatch.setattr(importlib.metadata, 'version', lambda name: {'relationalai': '1.30.1', 'duckdb': '1.5.5'}[name])
    function = namespace['acceptance_document']
    class Broken:
        def __init__(self, *_args, **_kwargs):
            raise RuntimeError('seeded-native-construction-failure')
    monkeypatch.setitem(function.__globals__, 'ApplicationOracle', Broken)
    model, pop = toy()
    report = function(model, pop, model_sha256='a' * 64, population_sha256='b' * 64)
    assert report['status'] == 'runtime_failure' and not report['accepted'] and report['exit_code'] == 70
    assert all(row['status'] == 'error' and 'seeded-native' in row['reason'] for row in report['verdicts'])


@pytest.mark.parametrize('damage,expected', [('raw-binding', 2), ('malformed', 3), ('missing', 66),
                                            ('occupied', 11), ('require', 2), ('named', 2),
                                            ('persisted', 2), ('bytes', 2)])
def test_acceptance_cli_boundary(tmp_path, monkeypatch, damage, expected):
    import hashlib
    import json
    model, pop = toy()
    pop['population']['covers'] = []  # Real refusal exercises CLI without native dependencies.
    raw = json.dumps(pop, ensure_ascii=False, indent=3) + '\n \n'
    source = json.dumps(model, ensure_ascii=False, indent=2)
    population = tmp_path / 'population.json'
    population.write_text(raw)
    output = tmp_path / 'report.json'
    main = runpy.run_path(str(RUNTIME))['program_main']
    monkeypatch.setitem(main.__globals__, 'MODEL_TEXT', source)
    config = {'connection': None, 'duckdb_path': ':memory:'}
    monkeypatch.setitem(main.__globals__, 'EXPORT_CONFIG', config)
    args = [str(population), '--out', str(output), '--accept']
    if damage == 'malformed':
        population.write_text('[]')
    elif damage == 'missing':
        population.unlink()
    elif damage == 'occupied':
        output.write_text('owner bytes')
    elif damage == 'require':
        args.extend(['--mode', 'require'])
    elif damage == 'named':
        config['connection'] = 'remote'
    elif damage == 'persisted':
        config['duckdb_path'] = 'persistent.db'
    elif damage == 'bytes':
        population.write_text(' ' * 1_048_577)
    assert main(args) == expected
    if damage == 'raw-binding':
        report = json.loads(output.read_text())
        assert report['binding'] == {'model_sha256': hashlib.sha256(source.encode()).hexdigest(),
                                     'population_sha256': hashlib.sha256(raw.encode()).hexdigest()}
        assert not report['accepted']
    elif damage == 'occupied':
        assert output.read_text() == 'owner bytes'
    elif damage in {'require', 'named', 'persisted'}:
        report = json.loads(output.read_text())
        assert not report['accepted'] and report['status'] == 'incomplete'
    else:
        assert not output.exists()


@pytest.mark.parametrize('damage', ['boolean-in-integer', 'model-id', 'metadata', 'digest', 'instance-rows'])
def test_scalar_identity_and_metadata_cannot_silently_accept(damage):
    model, pop = toy()
    model_sha = 'a' * 64
    if damage == 'boolean-in-integer':
        pop['facts']['r'][0]['y'] = True
    elif damage == 'model-id':
        pop['population']['model_id'] = 'different-model'
    elif damage == 'metadata':
        pop['population'] = []
    elif damage == 'digest':
        model_sha = 'A' * 64
    else:
        pop['instances'] = {'s': ['a'] * 1000}
    if damage == 'instance-rows':
        report = api()(model, pop, model_sha256=model_sha, population_sha256='b' * 64)
        assert report['status'] == 'incomplete' and not report['accepted']
        assert report['verdicts'][0]['reason'] == 'population-row-limit'
    else:
        with pytest.raises(ValueError):
            api()(model, pop, model_sha256=model_sha, population_sha256='b' * 64)
