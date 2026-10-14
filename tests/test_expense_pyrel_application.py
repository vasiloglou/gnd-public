"""PA4 red-first native reporting and approval outcomes."""
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


@pytest.fixture
def home(tmp_path):
    example = Path(str(files('gnd').joinpath('examples', 'expense')))
    project = tmp_path / 'expense'; shutil.copytree(example, project)
    cli = project / 'cli'; cli.mkdir(); (cli / '__init__.py').write_text('')
    for source, target in [('extension.py', 'expense_cli.py'), ('reporting.py', 'reporting.py'),
                           ('native_query.py', 'native_query.py')]:
        if (project / source).exists():
            shutil.copy2(project / source, cli / target)
    return project


def launch(home, command, *, model='model.orm.json', population='seed.population.json', expense=101, chain='team-lead'):
    help_run = subprocess.run([sys.executable, '-m', 'cli.expense_cli', command, '--help'], cwd=home,
                              capture_output=True, text=True, timeout=20, check=False)
    assert '--backend' in help_run.stdout and '--pyrel-python' in help_run.stdout, 'native expense interface is absent'
    args = [command, '--model', model, '--population', population, '--backend', 'pyrel', '--pyrel-python', str(NATIVE), '--format', 'json']
    if command == 'approve':
        args += ['--expense', str(expense), '--chain', chain, '--output', 'result.json']
    return subprocess.run([sys.executable, '-m', 'cli.expense_cli', *args], cwd=home,
                          env={k: v for k, v in os.environ.items() if k not in {'PYTHONPATH', 'PYTHONHOME'}},
                          capture_output=True, text=True, timeout=150, check=False)


@pytest.mark.parametrize('mode', ['baseline', 'currency', 'repeated-amounts'])
def test_native_expense_report_arithmetic(home, mode):
    model, population = ('currency.orm.json', 'currency.population.json') if mode == 'currency' else ('model.orm.json', 'seed.population.json')
    if mode == 'repeated-amounts':
        source = home / population; document = json.loads(source.read_bytes())
        for row in document['facts']['expense_has_amount']:
            row['amount'] = 60
        source.write_text(json.dumps(document))
    before = (home / population).read_bytes()
    completed = launch(home, 'report', model=model, population=population)
    assert completed.returncode == 0, completed.stderr + completed.stdout
    result = json.loads(completed.stdout)
    assert result['accepted'] and result['policy']['accepted']
    expected = {'submitted': 3, 'approved': 1, 'totals_by_currency': {'EUR': 2260}} if mode == 'currency' else {
        'submitted': 3, 'approved': 1, 'total_eur': 180 if mode == 'repeated-amounts' else 2260}
    assert result['report'] == expected
    assert (home / population).read_bytes() == before and not (home / 'result.json').exists()


@pytest.mark.parametrize('expense,chain', [(101, 'team-lead'), (102, 'finance')])
def test_native_legitimate_approval_publishes(home, expense, chain):
    before = (home / 'seed.population.json').read_bytes()
    completed = launch(home, 'approve', expense=expense, chain=chain)
    assert completed.returncode == 0, completed.stderr + completed.stdout
    result = json.loads(completed.stdout); candidate = json.loads((home / 'result.json').read_bytes())
    assert result['accepted'] and result['published'] and result['policy']['accepted']
    assert 'calculation' not in result
    assert {'expense': expense} in candidate['facts']['expense_is_approved']
    assert {'expense': expense, 'chain': chain} in candidate['facts']['expense_approved_by_chain']
    assert (home / 'seed.population.json').read_bytes() == before
    reported = launch(home, 'report', population='result.json')
    assert reported.returncode == 0, reported.stderr + reported.stdout
    assert json.loads(reported.stdout)['report'] == {'submitted': 3, 'approved': 2, 'total_eur': 2260}


@pytest.mark.parametrize('mode,expected', [('chain-limit', 1), ('unknown-chain', 1), ('unknown-expense', 1),
                                         ('duplicate', 1), ('meal-cap', 1), ('category', 1),
                                         ('nonpositive', 1),
                                         ('missing-submitter', 1), ('currency-missing', 1), ('currency-usd', 1),
                                         ('unknown-coverage', 2)])
def test_native_expense_refusals_preserve_inputs(home, mode, expected):
    model = 'currency.orm.json' if mode.startswith('currency') else 'model.orm.json'
    population = 'currency.population.json' if mode.startswith('currency') else 'seed.population.json'
    source = home / population; document = json.loads(source.read_bytes()); facts = document['facts']
    expense, chain = 101, 'team-lead'
    if mode == 'chain-limit':
        expense = 102
    elif mode == 'unknown-chain':
        chain = 'fast-track'
    elif mode == 'unknown-expense':
        expense = 999
    elif mode == 'duplicate':
        expense = 103
    elif mode == 'meal-cap':
        facts['expense_has_amount'][0]['amount'] = 76
    elif mode == 'nonpositive':
        facts['expense_has_amount'][0]['amount'] = 0
    elif mode == 'category':
        facts['expense_in_category'][0]['category'] = 'unknown'
    elif mode == 'missing-submitter':
        facts['expense_submitted_by_employee'] = facts['expense_submitted_by_employee'][1:]
    elif mode == 'currency-missing':
        facts['expense_has_currency'] = facts['expense_has_currency'][1:]
    elif mode == 'currency-usd':
        facts['expense_has_currency'][0]['currency'] = 'USD'
    else:
        document['population']['covers'].remove('expense_has_amount'); facts['expense_has_amount'] = []
    source.write_text(json.dumps(document)); before = source.read_bytes()
    completed = launch(home, 'approve', model=model, population=population, expense=expense, chain=chain)
    assert completed.returncode == expected, completed.stderr + completed.stdout
    assert not (home / 'result.json').exists() and source.read_bytes() == before
    result = json.loads(completed.stdout)
    assert not result['accepted'] and not result['published'] and 'report' not in result
    if mode in {'unknown-expense', 'duplicate', 'missing-submitter', 'currency-usd'}:
        assert result['application_refusal']['kind'] == {'unknown-expense': 'unknown-expense',
            'duplicate': 'already-approved', 'missing-submitter': 'unknown-expense',
            'currency-usd': 'unsupported-currency'}[mode]
    if mode == 'currency-missing':
        row = next(row for row in result['policy']['verdicts'] if row['id'] == 'required_expense_has_currency')
        assert row['status'] == 'violated' and row['witnesses'] == [[101]]
    if mode in {'chain-limit', 'unknown-chain', 'meal-cap', 'category', 'nonpositive'}:
        identity = {'chain-limit': 'approval_limit_team_lead', 'unknown-chain': 'known_chains',
                    'meal-cap': 'policy_meals', 'category': 'known_categories', 'nonpositive': 'positive_amount'}[mode]
        assert next(row for row in result['policy']['verdicts'] if row['id'] == identity)['status'] == 'violated'


@pytest.mark.parametrize('mode', ['zero-approvals', 'empty'])
def test_native_empty_arithmetic_is_not_policy_acceptance(home, tmp_path, mode):
    # Interface presence is required before the library path can receive credit.
    launch(home, 'report')
    from gnd.export.applications import execute_application

    source = home / 'seed.population.json'; document = json.loads(source.read_bytes())
    if mode == 'empty':
        document['facts'] = {name: [] for name in document['facts']}
    else:
        document['facts']['expense_is_approved'] = []
        document['facts']['expense_approved_by_chain'] = []
    source.write_text(json.dumps(document))
    result = execute_application(home / 'model.orm.json', source, tmp_path / 'checked.json',
                                 native_python=NATIVE, query_script=home / 'cli/native_query.py',
                                 query_args=('report', '', ''))
    assert result['exit_code'] == 2 and not result['accepted'] and not result['published'], result
    assert result['calculation']['report'] == {'submitted': 0 if mode == 'empty' else 3,
                                             'approved': 0, 'total_eur': 0 if mode == 'empty' else 2260}
    assert any(row['status'] == 'vacuous' for row in result['policy']['verdicts'])


@pytest.mark.parametrize('fault', ['chain-limit', 'unknown-approval', 'duplicate-approval', 'currency-edit'])
def test_native_post_proposal_approval_faults_and_repair(home, tmp_path, fault):
    launch(home, 'report')
    from gnd.export.applications import execute_application

    source = home / ('currency.population.json' if fault == 'currency-edit' else 'seed.population.json')
    model = home / ('currency.orm.json' if fault == 'currency-edit' else 'model.orm.json')
    before = source.read_bytes()
    def damage(candidate):
        if fault == 'chain-limit':
            candidate['facts']['expense_approved_by_chain'][-1]['chain'] = 'team-lead'
        elif fault == 'unknown-approval':
            candidate['facts']['expense_is_approved'].append({'expense': 999})
            candidate['facts']['expense_approved_by_chain'].append({'expense': 999, 'chain': 'finance'})
        elif fault == 'duplicate-approval':
            candidate['facts']['expense_is_approved'].append({'expense': 103})
        else:
            candidate['facts']['expense_has_currency'][0]['currency'] = 'USD'
        return candidate
    options = {'native_python': NATIVE, 'query_script': home / 'cli/native_query.py',
               'query_args': ('approve', '102', 'finance'),
               'owned_relations': ('expense_is_approved', 'expense_approved_by_chain'),
               'allowed_guard_kinds': ('unknown-expense', 'already-approved', 'unsupported-currency')}
    # This separate library caller explicitly owns currency editing. The CLI
    # approval caller owns only approval/chain and would refuse this edit3.
    if fault == 'currency-edit':
        options['owned_relations'] += ('expense_has_currency',)
    result = execute_application(model, source, tmp_path / 'bad.json',
                                 candidate_transform=damage, **options)
    assert result['exit_code'] == 1 and not result['published'] and source.read_bytes() == before, result
    identity = {'chain-limit': 'approval_limit_team_lead', 'unknown-approval': 'approval_needs_submission',
                'duplicate-approval': 'one_expense_is_approved', 'currency-edit': 'supported_currency'}[fault]
    assert next(row for row in result['policy']['verdicts'] if row['id'] == identity)['status'] == 'violated'
    repaired = execute_application(model, source, tmp_path / 'repaired.json', **options)
    assert repaired['published'] and repaired['accepted'], repaired


def test_native_existing_output_is_not_replaced(home):
    output = home / 'result.json'; output.write_bytes(b'owner bytes')
    before = (home / 'seed.population.json').read_bytes()
    completed = launch(home, 'approve')
    assert completed.returncode == 2, completed.stdout + completed.stderr
    assert output.read_bytes() == b'owner bytes' and (home / 'seed.population.json').read_bytes() == before


@pytest.mark.parametrize('missing', [False, True])
def test_invalid_currency_withholds_successful_report(home, missing):
    source = home / 'currency.population.json'; document = json.loads(source.read_bytes())
    if missing:
        document['facts']['expense_has_currency'] = document['facts']['expense_has_currency'][1:]
    else:
        document['facts']['expense_has_currency'][0]['currency'] = 'USD'
    source.write_text(json.dumps(document)); before = source.read_bytes()
    completed = launch(home, 'report', model='currency.orm.json', population=source.name)
    assert completed.returncode == 1, completed.stdout + completed.stderr
    result = json.loads(completed.stdout)
    assert not result['accepted'] and 'report' not in result and 'calculation' not in result
    assert source.read_bytes() == before


def test_known_empty_currency_remains_nonaccepted(home):
    source = home / 'currency.population.json'; document = json.loads(source.read_bytes())
    document['facts']['expense_has_currency'] = []; source.write_text(json.dumps(document))
    completed = launch(home, 'report', model='currency.orm.json', population=source.name)
    assert completed.returncode == 2, completed.stdout + completed.stderr
    result = json.loads(completed.stdout)
    assert not result['accepted'] and 'report' not in result and 'calculation' not in result
    row = next(row for row in result['policy']['verdicts'] if row['id'] == 'required_expense_has_currency')
    assert row['status'] == 'vacuous' and result['policy']['status'] == 'incomplete'


def test_missing_submitter_on_other_expense_reaches_policy(home):
    source = home / 'seed.population.json'; document = json.loads(source.read_bytes())
    document['facts']['expense_submitted_by_employee'] = document['facts']['expense_submitted_by_employee'][1:]
    source.write_text(json.dumps(document)); before = source.read_bytes()
    completed = launch(home, 'approve', expense=102, chain='finance')
    assert completed.returncode == 1, completed.stdout + completed.stderr
    result = json.loads(completed.stdout)
    row = next(row for row in result['policy']['verdicts'] if row['id'] == 'required_expense_submitted_by_employee')
    assert row['status'] == 'violated' and row['witnesses'] == [[101]]
    assert source.read_bytes() == before and not (home / 'result.json').exists()


def test_shipped_missing_currency_fixture_reaches_policy(home):
    completed = launch(home, 'report', model='currency.orm.json', population='currency-missing.population.json')
    assert completed.returncode == 1, completed.stdout + completed.stderr
    result = json.loads(completed.stdout)
    row = next(row for row in result['policy']['verdicts'] if row['id'] == 'required_expense_has_currency')
    assert row['status'] == 'violated' and row['witnesses'] == [[101], [102]]
    assert 'report' not in result


def test_report_returns_exact_source_binding(home):
    import hashlib

    source = home / 'seed.population.json'; model = home / 'model.orm.json'
    completed = launch(home, 'report')
    assert completed.returncode == 0, completed.stdout + completed.stderr
    result = json.loads(completed.stdout)
    assert result['source_binding'] == {'model_sha256': hashlib.sha256(model.read_bytes()).hexdigest(),
                                       'input_sha256': hashlib.sha256(source.read_bytes()).hexdigest()}
