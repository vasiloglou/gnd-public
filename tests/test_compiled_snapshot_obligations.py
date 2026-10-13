"""Public regression for issue 16; defaults and opt-in semantics are separate."""
import copy
import json
import subprocess
import sys
import time
from pathlib import Path

import pytest

from gnd import api
from gnd.model import load_model
from gnd.population import load_population

CORPUS = Path(__file__).parent / 'fixtures/compiled-snapshot'


def cli(*args):
    result = subprocess.run([sys.executable, '-m', 'gnd', *map(str, args)],
                            capture_output=True, text=True, check=False, timeout=30)
    return result.returncode, json.loads(result.stdout) if result.stdout else None


def compiled(payload):
    payload = payload.get('report', payload)
    return [r for r in payload['verdicts'] if r['constraint_type'] == 'compiled-subset']


@pytest.mark.parametrize('case,walk_exit', [('nonnumeric', 1), ('numeric', 2)])
def test_baseline_and_walk(case, walk_exit):
    model = load_model(CORPUS / 'model.orm.json')
    pop = load_population(CORPUS / f'{case}.pop.json', model=model)
    snapshot = api.check(model, pop)
    assert snapshot['exit_code'] == 2 and snapshot['counts']['fail'] == 0
    assert not compiled(snapshot)
    assert not any(r['verdict'] == 'fail' for r in snapshot['derivations'])
    walk = api.transition(model, CORPUS / 'pre.pop.json',
                          json.loads((CORPUS / f'{case}.steps.json').read_text()))
    assert walk['exit_code'] == walk_exit
    if case == 'nonnumeric':
        assert any(r['obligation'] == 'pre_numeric' and r['verdict'] == 'fail'
                   for step in walk['transition']['steps'] for r in step['verdicts'])


@pytest.mark.parametrize('case,expected', [('nonnumeric', 1), ('numeric', 2)])
def test_opt_in_single_and_batch(case, expected, tmp_path):
    model = CORPUS / 'model.orm.json'
    population = CORPUS / f'{case}.pop.json'
    result = api.check(model, population, compiled_operations=True)
    assert result['exit_code'] == expected
    failures = [r for r in compiled(result) if r['verdict'] == 'fail']
    assert bool(failures) == (case == 'nonnumeric')
    if failures:
        assert any('filter_compare.pre_numeric' in r['message'] for r in failures)
    assert not any(r['verdict'] == 'fail' for r in result['derivations'])
    assert result['assurance']['assurance_level'] == 'none'
    code, single = cli('check', model, population, '--compiled-operations', '--format', 'json')
    assert code == expected and compiled(single) == compiled(result)
    (tmp_path / 'candidate.pop.json').write_bytes(population.read_bytes())
    code, batch = cli('check', model, '--populations', tmp_path,
                      '--compiled-operations', '--format', 'json')
    assert code == expected
    assert batch['rows'][0]['failing_constraints'] == [r['constraint_ref'] for r in failures]
    assert batch['rows'][0]['counts'] == result['counts']


def test_opt_in_cannot_be_silently_ignored_by_admission():
    with pytest.raises(ValueError, match='admission'):
        api.check(CORPUS / 'model.orm.json', CORPUS / 'nonnumeric.pop.json',
                  compiled_operations=True, admission=True)


@pytest.mark.parametrize('extra', [('--pre', 'before', '--steps', 'steps'), ('--admission',)])
def test_cli_refuses_conflicting_modes(extra):
    result = subprocess.run([sys.executable, '-m', 'gnd', 'check', 'model',
                             '--compiled-operations', *extra], capture_output=True,
                            text=True, check=False, timeout=30)
    assert result.returncode == 64 and not result.stdout
    assert '--compiled-operations cannot be combined' in result.stderr


def small_case(tmp_path, *, modality='alethic', facts=None, covers=None,
               derived=None, redacted=False, second_effect=False):
    provenance = {'source': 'explicit', 'status': 'confirmed',
                  'provenance': {'csdp_step': 7, 'user_quote': 'Recorded facts require a permit.'}}
    types = [{'id': name, 'reading': '{Token} is ' + name,
              'roles': [{'object_type': 'token', 'role_name': 'value',
                         **({'redact': True} if redacted and name == 'recorded' else {})}]}
             for name in ('recorded', 'permitted', 'seed', 'other')]
    if derived:
        types[1].update(derivation='derived', derivation_rule=derived)
    operation = {'id': 'record', 'reading': '{Token} is recorded',
                 'parameters': [{'name': 'x', 'object_type': 'token'}],
                 'preconditions': [{'id': 'pre_permitted', 'modality': modality,
                                    'require': [{'fact_type': 'permitted', 'bind': {'value': '$x'}}],
                                    **copy.deepcopy(provenance)}],
                 'effects': [{'assert': {'fact_type': 'recorded', 'bind': {'value': '$x'}}}],
                 'frame': {'modality': 'alethic'}, **copy.deepcopy(provenance)}
    if second_effect:
        operation['effects'].append({'assert': {'fact_type': 'other', 'bind': {'value': '$x'}}})
    model = {'version': 2, 'source': {'kind': 'text-conversation', 'confidence': 'standard',
                                     'mode': 'one-shot'},
             'object_types': [{'id': 'token', 'name': 'Token', 'kind': 'value', 'primitive': 'String'}],
             'fact_types': types, 'operations': [operation]}
    population = {'population': {'model': 'model.orm.json', 'source': 'fixture',
                                 'covers': list(covers if covers is not None else
                                                ('recorded', 'permitted', 'seed', 'other'))},
                  'facts': facts if facts is not None else {'recorded': [{'value': 'PRIVATE_CANARY'}]}}
    model_path, pop_path = tmp_path / 'model.orm.json', tmp_path / 'population.json'
    model_path.write_text(json.dumps(model)); pop_path.write_text(json.dumps(population))
    return model_path, pop_path


@pytest.mark.parametrize('case,expected,band', [
    ('fail', 'fail', 1), ('warning', 'warning', 0), ('pass', 'pass', 0),
    ('vacuous', 'vacuous', 2), ('missing-of', 'unchecked', 4),
    ('missing-in', 'unchecked', 4), ('opaque-derived', 'unchecked', 4),
])
def test_dispositions(case, expected, band, tmp_path):
    args = {}
    if case == 'warning':
        args['modality'] = 'deontic'
    elif case == 'pass':
        args['facts'] = {'recorded': [{'value': 'x'}], 'permitted': [{'value': 'x'}]}
    elif case == 'vacuous':
        args['facts'] = {}
    elif case.startswith('missing-'):
        omitted = 'recorded' if case == 'missing-of' else 'permitted'
        args.update(covers=[s for s in ('recorded', 'permitted', 'seed', 'other') if s != omitted],
                    facts={'recorded': [{'value': 'x'}]} if omitted != 'recorded' else {})
    elif case == 'opaque-derived':
        args['derived'] = 'A human decides whether a token is permitted.'
    model, pop = small_case(tmp_path, **args)
    result = api.check(model, pop, compiled_operations=True)
    assert result['exit_code'] == band, result
    row, = compiled(result)
    assert row['verdict'] == expected
    assert (row['reason_code'] is not None) == (expected == 'unchecked')


def test_multiple_effects_and_no_compilation_mutation(tmp_path):
    model_path, pop_path = small_case(tmp_path, second_effect=True,
                                    facts={'recorded': [{'value': 'x'}], 'other': [{'value': 'y'}]})
    model = load_model(model_path)
    before = model.model_dump_json()
    result = api.check(model, load_population(pop_path, model=model), compiled_operations=True)
    rows = compiled(result)
    assert len(rows) == 2 and all(row['verdict'] == 'fail' for row in rows)
    assert len({row['constraint_ref'] for row in rows}) == 2
    assert before == model.model_dump_json()
    assert not compiled(api.check(model, pop_path))


def test_effective_derived_relation_and_unknown_claims(tmp_path):
    rule = {'body': [{'fact_type': 'seed', 'bind': {'value': '$x'}}], 'head': {'value': '$x'}}
    model, pop = small_case(tmp_path, derived=rule,
                           facts={'recorded': [{'value': 'x'}], 'seed': [{'value': 'x'}]})
    document = json.loads(model.read_text())
    document['fact_types'][1]['derivation'] = 'semiderived'
    model.write_text(json.dumps(document))
    result = api.check(model, pop, compiled_operations=True)
    assert compiled(result)[0]['verdict'] == 'pass', result
    assert any(row['verdict'] == 'fail' for row in result['derivations'])


def test_work_limit_and_linear_matching(tmp_path, monkeypatch):
    from gnd import compiled_obligations as implementation
    model, pop = small_case(tmp_path)
    monkeypatch.setattr(implementation, 'MAX_COMPILED_WORK', 0)
    row, = compiled(api.check(model, pop, compiled_operations=True))
    assert row['reason_code'] == 'compiled-obligation-work-limit'
    entry = {'subset': {'of': 'a', 'in': 'b'}, 'role_pairs': [('x', 'y')]}
    facts = {'a': [{'x': str(i)} for i in range(6000)],
             'b': [{'y': str(i)} for i in range(6000)]}
    budget = implementation.WorkBudget(12_000)
    start = time.monotonic()
    assert implementation.offending_rows(entry, facts, budget) == []
    assert budget.visits == 12_000 and time.monotonic() - start < 3


def test_typed_identity_and_repeated_role_pairs():
    from gnd.compiled_obligations import offending_rows
    entry = {'subset': {'of': 'a', 'in': 'b'}, 'role_pairs': [('x', 'y')]}
    assert offending_rows(entry, {'a': [{'x': True}, {'x': '1'}, {'x': 1}],
                                 'b': [{'y': 1.0}]}) == [{'x': True}, {'x': '1'}]
    entry['role_pairs'] = [('x', 'left'), ('x', 'right')]
    assert offending_rows(entry, {'a': [{'x': 1}], 'b': [{'left': 2, 'right': 1}]}) == [{'x': 1}]


def test_compiled_witness_redaction_and_schema(tmp_path):
    from importlib.resources import files

    import jsonschema
    model, pop = small_case(tmp_path, redacted=True)
    result = api.check(model, pop, compiled_operations=True)
    assert 'PRIVATE_CANARY' not in json.dumps(result)
    jsonschema.validate(result, json.loads((files('gnd') / 'report.schema.json').read_text()))
    raw = api.check(model, pop, compiled_operations=True, unredacted=True)
    assert 'PRIVATE_CANARY' in json.dumps(raw)


def test_anchor_route_does_not_drop_compiled_check(tmp_path):
    model_path, pop_path = small_case(tmp_path)
    doc = json.loads(model_path.read_text())
    doc['fact_types'][0]['constraints'] = [
        {'type': 'anchored', 'source': 'explicit', 'status': 'confirmed', 'modality': 'alethic',
         'provenance': {'csdp_step': 7, 'user_quote': 'Record comes from a source.'}}]
    model_path.write_text(json.dumps(doc))
    result = api.check(model_path, pop_path, compiled_operations=True)
    assert result['exit_code'] == 1 and compiled(result)[0]['verdict'] == 'fail', result


@pytest.mark.parametrize('value', ['false', 1, None])
def test_low_level_activation_is_boolean(value):
    from gnd.batch import check_population_directory
    from gnd.checker import check
    with pytest.raises(TypeError, match='boolean'):
        check(None, None, compiled_operations=value)
    with pytest.raises(TypeError, match='boolean'):
        check_population_directory(Path('missing'), Path('missing'), compiled_operations=value)


def test_current_operation_edits_do_not_reuse_stale_compilation(tmp_path):
    model_path, pop_path = small_case(tmp_path)
    model = load_model(model_path)
    pop = load_population(pop_path, model=model)
    model.operations[0]['preconditions'][0]['modality'] = 'deontic'
    result = api.check(model, pop, compiled_operations=True)
    row, = compiled(result)
    assert row['verdict'] == 'warning' and row['modality'] == 'deontic'


def test_reference_bound_compiled_check(tmp_path):
    import hashlib
    model_path, pop_path = small_case(tmp_path,
                                    facts={'recorded': [{'value': 'x'}]},
                                    covers=['recorded', 'seed', 'other'])
    document = json.loads(model_path.read_text())
    document['version'] = 4
    document['model_id'] = 'urn:gnd-fixture:compiled-reference@1'
    reference = {'population': {'model': 'model.orm.json', 'source': 'fixture',
                                'covers': ['permitted'], 'model_id': document['model_id']},
                 'facts': {'permitted': [{'value': 'x'}]}}
    raw = (json.dumps(reference) + '\n').encode()
    (tmp_path / 'reference.pop.json').write_bytes(raw)
    document['reference_populations'] = [{'id': 'permits', 'path': 'reference.pop.json',
                                          'sha256': hashlib.sha256(raw).hexdigest(),
                                          'fact_types': ['permitted']}]
    model_path.write_text(json.dumps(document))
    population = json.loads(pop_path.read_text())
    population['population']['model_id'] = document['model_id']
    pop_path.write_text(json.dumps(population))
    result = api.check(model_path, pop_path, compiled_operations=True)
    assert result['exit_code'] == 0 and compiled(result)[0]['verdict'] == 'pass', result


def test_trace_explains_activation():
    run = subprocess.run([sys.executable, '-m', 'gnd', 'validate', str(CORPUS / 'model.orm.json'),
                          '--trace'], capture_output=True, text=True, check=False, timeout=30)
    assert run.returncode == 0
    assert '--compiled-operations' in run.stdout and 'still require a walk' in run.stdout
    assert 'transition-only:' in run.stdout and 'filter_compare.pre_numeric' in run.stdout


def test_every_operation_and_duplicate_precondition_ids(tmp_path):
    model_path, pop = small_case(tmp_path,
                                 facts={'recorded': [{'value': 'x'}], 'other': [{'value': 'y'}]})
    document = json.loads(model_path.read_text())
    other = copy.deepcopy(document['operations'][0])
    other['id'] = 'record_other'
    other['effects'][0]['assert']['fact_type'] = 'other'
    document['operations'].append(other)
    model_path.write_text(json.dumps(document))
    rows = compiled(api.check(model_path, pop, compiled_operations=True))
    assert len(rows) == 2 and all(row['verdict'] == 'fail' for row in rows)
    assert len({row['constraint_ref'] for row in rows}) == 2
    assert any('record_other.pre_permitted' in row['message'] for row in rows)


def test_transition_only_literal_is_not_a_snapshot_obligation(tmp_path):
    model_path, pop = small_case(tmp_path)
    document = json.loads(model_path.read_text())
    document['operations'][0]['preconditions'][0]['require'][0]['bind']['value'] = 'required'
    model_path.write_text(json.dumps(document))
    result = api.check(model_path, pop, compiled_operations=True)
    assert result['exit_code'] == 0 and not compiled(result)


def test_required_role_redaction_also_suppresses_compiled_witness(tmp_path):
    model_path, pop = small_case(tmp_path)
    document = json.loads(model_path.read_text())
    document['fact_types'][1]['roles'][0]['redact'] = True
    model_path.write_text(json.dumps(document))
    result = api.check(model_path, pop, compiled_operations=True)
    assert 'PRIVATE_CANARY' not in json.dumps(result)


def test_possible_only_derived_input_is_unchecked(tmp_path):
    rule = {'body': [{'fact_type': 'seed', 'bind': {'value': '$x'}}], 'head': {'value': '$x'}}
    model, pop = small_case(tmp_path, derived=rule,
                           facts={'recorded': [{'value': 'x'}],
                                  'seed': [{'value': {'$opaque': 'unknown'}}]})
    document = json.loads(model.read_text())
    document['fact_types'][1]['derivation'] = 'semiderived'
    model.write_text(json.dumps(document))
    population = json.loads(pop.read_text())
    population['format_version'] = 2
    pop.write_text(json.dumps(population))
    result = api.check(model, pop, compiled_operations=True)
    assert result['exit_code'] == 4, result
    row, = compiled(result)
    assert row['reason_code'] == 'compiled-obligation-unavailable'
