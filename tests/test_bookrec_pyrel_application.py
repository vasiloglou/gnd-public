"""Red-first actual native application outcomes, separate from checker-only tests."""
import json
import os
import shutil
import subprocess
import sys
from importlib.resources import files
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
NATIVE = ROOT / 'tutorials/runtimes/.venv/bin/python'
pytestmark = pytest.mark.pyrel_oracle


@pytest.mark.parametrize('mode,expected', [('advisory', 0), ('strict', 1), ('preferred', 0),
                                          ('complete', 0), ('unknown', 3), ('limit', 2), ('upper-limit', 2)])
def test_native_bookrec_cli_outcomes_and_pairs(tmp_path, mode, expected):
    home = tmp_path / 'bookrec'
    shutil.copytree(str(files('gnd').joinpath('examples', 'bookrec')), home)
    model = 'complete.orm.yaml' if mode == 'complete' else ('strict.orm.yaml' if mode in {'strict', 'preferred'} else 'model.orm.yaml')
    output = tmp_path / 'result.json'; source = home / 'seed.population.json'
    before = source.read_bytes()
    args = ['complete' if mode == 'complete' else 'recommend', '--model', str(home / model),
            '--input', str(source), '--output', str(output), '--backend', 'pyrel', '--pyrel-python', str(NATIVE), '--format', 'json']
    if mode != 'complete':
        args += ['--user', 'nobody' if mode == 'unknown' else 'ada', '--limit',
                 '0' if mode == 'limit' else '101' if mode == 'upper-limit' else '2']
    if mode == 'preferred':
        args.append('--preferred-only')
    help_run = subprocess.run([sys.executable, '-m', 'bookrec.cli', '--help'], cwd=home / 'extension',
                              capture_output=True, text=True, timeout=20, check=False)
    assert '--backend' in help_run.stdout and '--pyrel-python' in help_run.stdout, 'native application interface is absent'
    env = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'}
    if mode == 'advisory':
        # One case reaches the pinned interpreter through the environment variable instead of the flag.
        args = [a for a in args if a not in ('--pyrel-python', str(NATIVE))]
        env['GND_PYREL_PYTHON'] = str(NATIVE)
    completed = subprocess.run([sys.executable, '-m', 'bookrec.cli', *args], cwd=home / 'extension',
                               env=env, capture_output=True, text=True, timeout=150, check=False)
    assert completed.returncode == expected, completed.stderr + completed.stdout
    assert source.read_bytes() == before
    if expected:
        assert not output.exists()
        report = json.loads(completed.stdout)
        if mode == 'unknown':
            assert 'unknown preference-registered user' in report['reason']
        if mode in {'limit', 'upper-limit'}:
            assert 'limit must be between 1 and 100' in report['reason']
        return
    candidate = json.loads(output.read_text()); report = json.loads(completed.stdout)
    assert report['published'] and report['accepted']
    pairs = {(row['user'], row['book']) for row in candidate['facts']['recommendation']}
    if mode == 'advisory':
        assert pairs == {('ada', 'cosmos'), ('ada', 'map'), ('ben', 'night')}
        assert report['policy']['status'] == 'accepted_with_warnings'
        assert report['calculation']['selected_pairs'] == [{'user': 'ada', 'book': 'cosmos'}, {'user': 'ada', 'book': 'map'}]
        assert {(r['user'], r['book']) for r in report['calculation']['eligible_pairs']} == {
            ('ada', 'cosmos'), ('ada', 'map'), ('ada', 'river'),
            ('ben', 'cosmos'), ('ben', 'map'), ('ben', 'night'), ('ben', 'river')}
        assert report['calculation']['blocked_pairs'] == [{'user': 'ada', 'book': 'night'}]
        assert report['calculation']['already_read_pairs'] == [{'user': 'ada', 'book': 'read'}, {'user': 'ben', 'book': 'read'}]
    elif mode == 'preferred':
        assert pairs == {('ada', 'map'), ('ada', 'river'), ('ben', 'night')}
    else:
        assert pairs == {('ada', 'map'), ('ada', 'river'), ('ben', 'map'), ('ben', 'night'), ('ben', 'river')}
        assert {(row['user'], row['book']) for row in candidate['facts']['book_is_eligible']} == pairs
        assert candidate['facts']['book_is_blocked_for'] == [{'book': 'night', 'user': 'ada'}]


@pytest.mark.parametrize('fault', ['already-read', 'adult', 'strict-genre', 'omission', 'forged-claim'])
def test_native_post_proposal_faults_refuse_and_repair(tmp_path, fault):
    from gnd.export.applications import execute_application

    example = Path(str(files('gnd').joinpath('examples', 'bookrec')))
    model = example / ('complete.orm.yaml' if fault in {'omission', 'forged-claim'} else 'strict.orm.yaml')
    source = example / 'seed.population.json'
    before = source.read_bytes()
    query = example / 'extension/bookrec/native_query.py'
    output = tmp_path / 'rejected.json'
    def damage(candidate):
        if fault in {'already-read', 'adult', 'strict-genre'}:
            candidate['facts']['recommendation'].append({'user': 'ada', 'book': {
                'already-read': 'read', 'adult': 'night', 'strict-genre': 'cosmos'}[fault]})
        elif fault == 'omission':
            candidate['facts']['recommendation'].pop()
        else:
            candidate['facts']['book_is_eligible'].append({'book': 'night', 'user': 'ada'})
        return candidate
    options = {'native_python': NATIVE, 'query_script': query, 'owned_relations': ('recommendation',),
               'query_args': ('complete' if fault in {'omission', 'forged-claim'} else 'recommend',
                              'ada', '2', 'true')}
    result = execute_application(model, source, output, candidate_transform=damage, **options)
    assert result['exit_code'] == 1 and not result['published'] and not result['accepted'], result
    assert result['policy']['status'] == 'rejected'
    if fault == 'forged-claim':
        assert next(row for row in result['policy']['derivations'] if row['fact_type'] == 'book_is_eligible')['status'] == 'violated'
    else:
        identity = {'already-read': 'unread_only', 'adult': 'age_appropriate',
                    'strict-genre': 'preferred_genre', 'omission': 'all_eligible'}[fault]
        assert next(row for row in result['policy']['verdicts'] if row['id'] == identity)['status'] == 'violated'
    assert not output.exists() and source.read_bytes() == before
    repaired = execute_application(model, source, tmp_path / 'repaired.json', **options)
    assert repaired['published'] and repaired['accepted'], repaired


def test_native_asserted_unknown_coverage_is_not_repaired(tmp_path):
    from gnd.export.applications import execute_application

    example = Path(str(files('gnd').joinpath('examples', 'bookrec')))
    seed = json.loads((example / 'seed.population.json').read_text())
    seed['population']['covers'].remove('user_rated_book')
    seed['facts']['user_rated_book'] = []
    source = tmp_path / 'unknown.json'; source.write_text(json.dumps(seed))
    output = tmp_path / 'result.json'
    result = execute_application(example / 'complete.orm.yaml', source, output,
                                 native_python=NATIVE, owned_relations=("recommendation",),
                                 query_script=example / 'extension/bookrec/native_query.py',
                                 query_args=('complete', '', '2', 'false'))
    assert result['exit_code'] == 2 and not result['published'] and not output.exists(), result
    assert 'relation-not-covered-or-listed' in result['reason']


def test_native_complete_unknown_metadata_refuses_without_runtime_error(tmp_path):
    from gnd.export.applications import execute_application

    example = Path(str(files('gnd').joinpath('examples', 'bookrec')))
    seed = json.loads((example / 'seed.population.json').read_text())
    del seed['population']
    source = tmp_path / 'unknown.json'; source.write_text(json.dumps(seed))
    output = tmp_path / 'result.json'
    result = execute_application(example / 'complete.orm.yaml', source, output,
                                 native_python=NATIVE, owned_relations=("recommendation",),
                                 query_script=example / 'extension/bookrec/native_query.py',
                                 query_args=('complete', '', '2', 'false'))
    assert result['exit_code'] == 2 and not result['published'] and not output.exists(), result
    assert 'coverage-not-declared' in result['reason']


@pytest.mark.parametrize('fault', ['erase-rating', 'malformed-candidate'])
def test_review_source_and_malformed_boundaries(tmp_path, fault):
    from gnd.export.applications import execute_application

    example = Path(str(files('gnd').joinpath('examples', 'bookrec')))
    def damage(candidate):
        if fault == 'erase-rating':
            candidate['facts']['user_rated_book'] = [{'user': 'ben', 'book': 'read'}]
            candidate['facts']['recommendation'].append({'user': 'ada', 'book': 'read'})
        else:
            candidate['facts']['recommendation'].append({'user': 'ada', 'book': 'map', 'x': 1})
        return candidate
    output = tmp_path / 'out.json'
    result = execute_application(example / 'strict.orm.yaml', example / 'seed.population.json', output,
                                 native_python=NATIVE, owned_relations=("recommendation",), query_script=example / 'extension/bookrec/native_query.py',
                                 query_args=('recommend', 'ada', '2', 'true'), candidate_transform=damage)
    assert result['exit_code'] == 3 and not result['published'] and not output.exists(), result
    assert ('candidate changed asserted source facts: user_rated_book' if fault == 'erase-rating'
            else 'missing or extra roles in recommendation') in result['reason']


@pytest.mark.parametrize('boundary', ['malformed-input', 'wrong-version'])
def test_native_specific_intake_and_version_refusals(tmp_path, boundary):
    from gnd.export.applications import execute_application

    example = Path(str(files('gnd').joinpath('examples', 'bookrec')))
    source = tmp_path / 'source.json'; source.write_bytes((example / 'seed.population.json').read_bytes())
    query = tmp_path / 'query.py'; query.write_bytes((example / 'extension/bookrec/native_query.py').read_bytes())
    if boundary == 'malformed-input':
        source.write_bytes(b'{"facts": []}')
    else:
        # The pin lives in the emitted seam (open_app); patch the lookup it performs.
        text = query.read_text()
        assert 'import runpy\n' in text
        query.write_text(text.replace('import runpy\n', 'import runpy\nimport importlib.metadata\n'
                                      'importlib.metadata.version = lambda name: "wrong"\n', 1))
    before = source.read_bytes(); output = tmp_path / 'output.json'
    result = execute_application(example / 'model.orm.yaml', source, output,
                                 native_python=NATIVE, owned_relations=('recommendation',), query_script=query,
                                 query_args=('recommend', 'ada', '2', 'false'))
    assert result['exit_code'] == (3 if boundary == 'malformed-input' else 70), result
    assert ('population facts must be a mapping' if boundary == 'malformed-input' else 'requires PyRel 1.30.1/DuckDB 1.5.5') in result['reason']
    assert not output.exists() and source.read_bytes() == before


def test_native_fresh_checker_rejects_query_replacement_attack(tmp_path):
    from test_pyrel_application_publication import MODEL, POP, checker_attack

    from gnd.export.applications import execute_application

    output = tmp_path / 'result.json'
    result = execute_application(MODEL, POP, output, native_python=NATIVE,
                                 query_script=checker_attack(tmp_path), owned_relations=('recommendation',))
    assert result['exit_code'] == 1 and not result['published'] and not output.exists(), result
    assert result['policy']['status'] == 'rejected'
    assert next(row for row in result['policy']['verdicts'] if row['id'] == 'age_appropriate')['status'] == 'violated'


@pytest.mark.parametrize('name', ['seed.json', 'candidate.json', 'policy.json', 'runtime.py'])
def test_model_filename_cannot_collide_with_private_stage(tmp_path, name):
    from gnd.export.applications import execute_application

    example = Path(str(files('gnd').joinpath('examples', 'bookrec')))
    model = tmp_path / name; model.write_bytes((example / 'model.orm.yaml').read_bytes())
    output = tmp_path / 'out.json'
    result = execute_application(model, example / 'seed.population.json', output,
                                 native_python=NATIVE, owned_relations=('recommendation',),
                                 query_script=example / 'extension/bookrec/native_query.py',
                                 query_args=('recommend', 'ada', '2', 'false'))
    assert result['exit_code'] == 0 and result['published'] and result['policy']['accepted'], result


def test_native_query_and_checker_do_not_open_ambient_config(monkeypatch, tmp_path):
    from gnd.export import applications

    original = applications._child
    def audited(argv, home):
        launcher = home / 'deny-config.py'
        launcher.write_text('import sys,runpy,os\nfrom pathlib import Path\n'
                            'def deny(event,args):\n'
                            ' if event=="open" and isinstance(args[0],(str,bytes)):\n'
                            '  p=Path(os.fsdecode(args[0]))\n'
                            '  if {".rai",".snowflake"}&set(p.parts) or p.name in {"raiconfig.yaml","raiconfig.toml",".env"}:\n'
                            '   raise RuntimeError("ambient configuration read prohibited")\n'
                            'sys.addaudithook(deny)\ntarget=sys.argv[1];sys.argv=[target,*sys.argv[2:]]\n'
                            'runpy.run_path(target,run_name="__main__")\n')
        return original([*argv[:2], launcher, *argv[2:]], home)
    monkeypatch.setattr(applications, '_child', audited)
    example = Path(str(files('gnd').joinpath('examples', 'bookrec')))
    result = applications.execute_application(example / 'model.orm.yaml', example / 'seed.population.json',
                                               tmp_path / 'out.json', native_python=NATIVE,
                                               query_script=example / 'extension/bookrec/native_query.py',
                                               owned_relations=('recommendation',), query_args=('recommend','ada','2','false'))
    assert result['exit_code'] == 0 and result['published'], result
