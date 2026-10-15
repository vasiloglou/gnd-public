"""PL2: the hand-written PyRel rules agree with GND's checker, witness for witness."""
from __future__ import annotations

import json
import subprocess
from importlib.resources import files
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
NATIVE = ROOT / 'tutorials/runtimes/.venv/bin/python'
pytestmark = pytest.mark.pyrel_oracle

BOOKREC = Path(str(files('gnd').joinpath('examples', 'bookrec')))
EXPENSE = Path(str(files('gnd').joinpath('examples', 'expense')))

CASES = [
    ('bookrec', 'model.orm.yaml', 'seed.population.json', 0),
    ('bookrec', 'model.orm.yaml', 'adult-for-minor.population.json', 1),
    ('bookrec', 'model.orm.yaml', 'already-read.population.json', 1),
    ('bookrec', 'model.orm.yaml', 'genre-warning.population.json', 0),
    ('expense', 'model.orm.json', 'seed.population.json', 0),
    ('expense', 'model.orm.json', 'approved.population.json', 0),
    ('expense', 'model.orm.json', 'invalid-chain.population.json', 1),
    ('expense', 'model.orm.json', 'invalid-meal.population.json', 1),
    ('expense', 'currency.orm.json', 'currency.population.json', 0),
    ('expense', 'currency.orm.json', 'currency-missing.population.json', 1),
    ('expense', 'currency.orm.json', 'tutorial-assets/checkpoints/usd.input.json', 1),
]


def _path(domain, population):
    home = BOOKREC if domain == 'bookrec' else EXPENSE
    return Path(population) if Path(population).is_absolute() else home / population


def _run(domain, population):
    home = BOOKREC if domain == 'bookrec' else EXPENSE
    run = subprocess.run([str(NATIVE), '-I', str(home / 'rules_in_pyrel.py'), str(_path(domain, population))],
                         capture_output=True, text=True, timeout=300, check=False)
    assert run.stderr == '', run.stderr
    findings = set()
    for line in run.stdout.splitlines():
        rule, _, rest = line.partition('  ')
        if rest == 'OK':
            continue
        status, _, witness = rest.partition('  ')
        if status == 'vacuous':
            findings.add((rule, 'vacuous', 'null'))
            continue
        findings.add((rule, status, json.dumps(json.loads(witness), sort_keys=True)))
    return run.returncode, findings


def _gnd(domain, model, population):
    from gnd import api

    home = BOOKREC if domain == 'bookrec' else EXPENSE
    document = json.loads((home / model).read_text())
    names = {f'constraints[{i}]': c['id'] for i, c in enumerate(document['constraints'])}
    for fact in document['fact_types']:
        for i, c in enumerate(fact.get('constraints', [])):
            names[f'fact_types[{fact["id"]}].constraints[{i}]'] = c.get('id', f'{fact["id"]}#{i}')
    report = api.check(home / model, _path(domain, population), unredacted=True)
    findings = set()
    for verdict in report['verdicts']:
        if verdict['verdict'] == 'pass':
            continue
        rule = names[verdict['constraint_ref']]
        if verdict['verdict'] == 'vacuous':
            findings.add((rule, 'vacuous', 'null'))
            continue
        status = 'violated' if verdict['verdict'] == 'fail' else 'warning'
        for witness in verdict['offending_facts']:
            # GND lists a mandatory rule's witnesses as one flat list of ids and a subset rule's as
            # one-element tuples; the hand-written rules print one `[id]` line per distinct value.
            if not isinstance(witness, (list, dict)) and verdict['constraint_type'] == 'mandatory':
                witness = [witness]
            findings.add((rule, status, json.dumps(witness, sort_keys=True)))
    return report['exit_code'], findings


@pytest.mark.parametrize('domain,model,population,expected_exit', CASES)
def test_hand_written_rules_agree_with_gnd(domain, model, population, expected_exit):
    native_exit, native = _run(domain, population)
    gnd_exit, gnd = _gnd(domain, model, population)
    assert native_exit == expected_exit == gnd_exit
    assert native == gnd, f'native-only {native - gnd}; gnd-only {gnd - native}'


def test_empty_currency_list_is_vacuous_on_both_sides(tmp_path):
    document = json.loads((EXPENSE / 'currency.population.json').read_text())
    document['facts']['expense_has_currency'] = []
    population = tmp_path / 'currency-empty.population.json'
    population.write_text(json.dumps(document))
    native_exit, native = _run('expense', str(population))
    gnd_exit, gnd = _gnd('expense', 'currency.orm.json', str(population))
    assert native_exit == gnd_exit == 2
    assert ('required_expense_has_currency', 'vacuous', 'null') in native
    assert {f for f in native if f[0] in {'required_expense_has_currency', 'supported_currency'}} == \
           {f for f in gnd if f[0] in {'required_expense_has_currency', 'supported_currency'}}


def test_malformed_population_exits_three(tmp_path):
    bad = tmp_path / 'bad.json'
    bad.write_text('{"facts": [')
    for home in (BOOKREC, EXPENSE):
        run = subprocess.run([str(NATIVE), '-I', str(home / 'rules_in_pyrel.py'), str(bad)],
                             capture_output=True, text=True, timeout=60, check=False)
        assert run.returncode == 3 and 'not a readable population' in run.stderr


def test_bad_candidates_print_the_pinned_witnesses():
    assert ('age_appropriate', 'violated', '{"$b": "night", "$u": "ada"}') in _run('bookrec', 'adult-for-minor.population.json')[1]
    assert ('unread_only', 'violated', '{"$b": "read", "$u": "ada"}') in _run('bookrec', 'already-read.population.json')[1]
    assert ('approval_limit_team_lead', 'violated', '{"$a": 800, "$e": 102}') in _run('expense', 'invalid-chain.population.json')[1]


def test_usage_error_without_a_population():
    for home in (BOOKREC, EXPENSE):
        run = subprocess.run([str(NATIVE), '-I', str(home / 'rules_in_pyrel.py')], capture_output=True,
                             text=True, timeout=60, check=False)
        assert run.returncode == 2 and 'usage' in run.stderr


def test_doc_twins_match_the_shipped_rules():
    for domain, home in (('bookrec', BOOKREC), ('expense', EXPENSE)):
        twin = ROOT / 'docs/assets/applications' / f'{domain}-rules-in-pyrel.txt'
        assert twin.read_bytes() == (home / 'rules_in_pyrel.py').read_bytes(), twin
