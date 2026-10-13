"""Public regression for issue 16; defaults and opt-in semantics are separate."""
import json
import subprocess
import sys
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
    code, payload = cli('check', 'model', '--compiled-operations', *extra)
    assert code == 64 and payload is None
