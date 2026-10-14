"""PA5R public native-query seam: name pin and output identity with captured checkpoints."""
import json
import shutil
import subprocess
from importlib.resources import files
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
NATIVE = ROOT / 'tutorials/runtimes/.venv/bin/python'
pytestmark = pytest.mark.pyrel_oracle

SEAM = ['NativeApp', 'open_app', 'run_app']
APP_METHODS = ['candidate', 'check_work', 'has', 'match', 'propose', 'ref', 'refuse',
               'relationship', 'rows']


def test_emitted_program_exposes_public_seam(tmp_path):
    from gnd.export.emit import render_pyrel

    program = tmp_path / 'program.py'
    program.write_text(render_pyrel(ROOT / 'src/gnd/examples/bookrec/model.orm.yaml'))
    probe = ('import json, runpy, sys; g = runpy.run_path(sys.argv[1]); '
             'print(json.dumps({"seam": sorted(n for n in %r if n in g), '
             '"methods": sorted(n for n in dir(g.get("NativeApp", object)) if not n.startswith("_")), '
             '"private": all(n in g for n in ("_parse_document", "_profile_admit", "ApplicationOracle"))}))'
             .replace('%r', repr(SEAM)))
    run = subprocess.run([str(NATIVE), '-I', '-c', probe, str(program)], capture_output=True,
                         text=True, timeout=60, check=False)
    assert run.returncode == 0, run.stderr
    found = json.loads(run.stdout)
    assert found['seam'] == SEAM
    assert set(APP_METHODS) <= set(found['methods'])
    assert found['private']


@pytest.mark.parametrize('domain', ['bookrec', 'expense'])
def test_owned_queries_use_only_the_public_seam(domain):
    path = ROOT / 'src/gnd/examples' / domain / ('extension/bookrec' if domain == 'bookrec' else '') / 'native_query.py'
    text = path.read_text()
    for private in ('_parse_document', '_profile', '_rows', '_concept_for', 'oracle.', 'frontend.base',
                    'ApplicationOracle', 'MODEL_TEXT', 'local_config'):
        assert private not in text, private
    assert "['run_app']" in text


BOOKREC = [('advisory', 'model.orm.yaml', ['recommend', '--user', 'ada', '--limit', '2']),
           ('strict', 'strict.orm.yaml', ['recommend', '--user', 'ada', '--limit', '2']),
           ('preferred', 'strict.orm.yaml', ['recommend', '--user', 'ada', '--limit', '2', '--preferred-only']),
           ('complete', 'complete.orm.yaml', ['complete'])]
EXPENSE = [('baseline', 'model.orm.json', 'seed.population.json', ['report']),
           ('team-lead', 'model.orm.json', 'seed.population.json', ['approve', '--expense', '101', '--chain', 'team-lead']),
           ('chain-limit', 'model.orm.json', 'invalid-chain.population.json', ['report']),
           ('finance', 'model.orm.json', 'seed.population.json', ['approve', '--expense', '102', '--chain', 'finance']),
           ('meal-cap', 'model.orm.json', 'invalid-meal.population.json', ['report']),
           ('currency-missing', 'currency.orm.json', 'currency-missing.population.json', ['report']),
           ('currency-explicit', 'currency.orm.json', 'currency.population.json', ['report']),
           ('usd', 'currency.orm.json', 'tutorial-assets/checkpoints/usd.input.json', ['report'])]


def _library_result(home, model, population, command, args, output, owned, guards):
    """Call the driver directly so the comparison includes the calculation."""
    from gnd.export.applications import execute_application

    return execute_application(home / model, home / population, output, native_python=NATIVE,
                               query_script=home / 'native_query.py', query_args=args,
                               owned_relations=owned, allowed_guard_kinds=guards)


@pytest.mark.parametrize('name,model,args', BOOKREC)
def test_bookrec_native_outputs_match_checkpoints(tmp_path, name, model, args):
    from gnd.export.applications import execute_application

    home = tmp_path / 'bookrec'
    shutil.copytree(str(files('gnd').joinpath('examples', 'bookrec')), home)
    command = args[0]
    user = args[args.index('--user') + 1] if '--user' in args else ''
    limit = args[args.index('--limit') + 1] if '--limit' in args else '2'
    output = tmp_path / 'out.json'
    result = execute_application(home / model, home / 'seed.population.json', output, native_python=NATIVE,
                                 query_script=home / 'extension/bookrec/native_query.py',
                                 query_args=(command, user, limit, 'true' if '--preferred-only' in args else 'false'),
                                 owned_relations=('recommendation',))
    expected = json.loads((home / 'tutorial-assets/checkpoints' / (name + '.json')).read_text())
    for key in ('exit_code', 'accepted', 'published', 'calculation', 'policy'):
        assert result[key] == expected[key], key
    candidate = home / 'tutorial-assets/checkpoints' / ((name if name != 'strict' else 'advisory') + '.candidate.json')
    if result['published'] and candidate.exists():
        assert output.read_bytes() == candidate.read_bytes()


@pytest.mark.parametrize('name,model,population,args', EXPENSE)
def test_expense_native_outputs_match_checkpoints(tmp_path, name, model, population, args):
    home = tmp_path / 'expense'
    shutil.copytree(str(files('gnd').joinpath('examples', 'expense')), home)
    command = args[0]
    query_args = (command, args[2] if command == 'approve' else '', args[4] if command == 'approve' else '')
    owned = ('expense_is_approved', 'expense_approved_by_chain') if command == 'approve' else ()
    result = _library_result(home, model, population, command, query_args, tmp_path / 'out.json', owned,
                             ('unknown-expense', 'already-approved', 'unsupported-currency'))
    expected = json.loads((home / 'tutorial-assets/checkpoints' / (name + '.json')).read_text())
    for key in ('exit_code', 'accepted', 'published', 'calculation', 'policy', 'application_refusal'):
        assert result.get(key) == expected.get(key), key
