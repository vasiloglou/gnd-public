"""PL12: the model's rules as two PyRel programs, one with require (LQP) and one without."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from importlib.resources import files
from pathlib import Path

import pytest

from gnd import api
from gnd.export.pyrel_rules import _Model, _Names, denial_text, render, require_text, requirements
from gnd.export.pyrel_runtime import ExportInputError, _parse_document

ROOT = Path(__file__).resolve().parents[1]
NATIVE = ROOT / 'tutorials/runtimes/.venv/bin/python'
BOOKREC = Path(str(files('gnd').joinpath('examples', 'bookrec')))
EXPENSE = Path(str(files('gnd').joinpath('examples', 'expense')))
PROBES = ROOT / 'tests/fixtures/pyrel-rules'
MODELS = {'bookrec': BOOKREC / 'model.orm.yaml', 'expense': EXPENSE / 'model.orm.json',
          'currency': EXPENSE / 'currency.orm.json', 'probe': PROBES / 'probe.orm.json',
          'names': PROBES / 'names.orm.json', 'names2': PROBES / 'names2.orm.json'}
CORPUS = [
    ('bookrec', BOOKREC / 'seed.population.json', 0),
    ('bookrec', BOOKREC / 'adult-for-minor.population.json', 1),
    ('bookrec', BOOKREC / 'already-read.population.json', 1),
    ('bookrec', BOOKREC / 'genre-warning.population.json', 0),
    ('expense', EXPENSE / 'seed.population.json', 0),
    ('expense', EXPENSE / 'approved.population.json', 0),
    ('expense', EXPENSE / 'invalid-chain.population.json', 1),
    ('expense', EXPENSE / 'invalid-meal.population.json', 1),
    ('currency', EXPENSE / 'currency.population.json', 0),
    ('currency', EXPENSE / 'currency-missing.population.json', 1),
    ('currency', EXPENSE / 'tutorial-assets/checkpoints/usd.input.json', 1),
    # Review probes (notes/phase-PL12-claude-review.md): multi-role subset, uniqueness with two
    # non-key roles, literals in consequents, instances rosters through a reference value type,
    # a vacuous rule after a violation, and a fact list the input does not cover.
    ('probe', PROBES / 'p1.population.json', 1),
    ('probe', PROBES / 'p2.population.json', 1),
    ('probe', PROBES / 'p3.population.json', 1),
    ('probe', PROBES / 'p4.population.json', 2),
    ('probe', PROBES / 'p5.population.json', 2),
    ('probe', PROBES / 'p6.population.json', 1),
    ('names', PROBES / 'names.population.json', 1),
    ('names2', PROBES / 'names2.population.json', 1),
]


def _program(tmp_path, name, target):
    path = tmp_path / f'{name}_{target}.py'
    path.write_text(render(MODELS[name], target))
    return path


def _findings(stdout):
    found = set()
    for line in stdout.splitlines():
        rule, _, rest = line.partition('  ')
        if rest == 'OK':
            continue
        status, _, witness = rest.partition('  ')
        if status in ('vacuous', 'unknown'):
            found.add((rule, status, 'null'))
        else:
            found.add((rule, status, json.dumps(json.loads(witness), sort_keys=True)))
    return found


def _gnd(name, population):
    doc = _parse_document(MODELS[name].read_text())
    names = {f'constraints[{i}]': c['id'] for i, c in enumerate(doc['constraints'])}
    for fact in doc['fact_types']:
        for i, c in enumerate(fact.get('constraints', [])):
            names[f'fact_types[{fact["id"]}].constraints[{i}]'] = c.get('id') or f'{fact["id"]}#{i}'
    report = api.check(MODELS[name], population, unredacted=True)
    found = set()
    for verdict in report['verdicts']:
        if verdict['verdict'] == 'pass':
            continue
        rule = names[verdict['constraint_ref']]
        if verdict['verdict'] == 'vacuous':
            found.add((rule, 'vacuous', 'null'))
            continue
        status = 'violated' if verdict['verdict'] == 'fail' else 'warning'
        if verdict['constraint_type'] == 'uniqueness':
            witnesses = [sorted(verdict['offending_facts'], key=lambda f: json.dumps(f, sort_keys=True))]
        elif verdict['constraint_type'] == 'mandatory':
            witnesses = [[w] for w in verdict['offending_facts']]
        else:
            witnesses = verdict['offending_facts']
        for w in witnesses:
            found.add((rule, status, json.dumps(w, sort_keys=True)))
    return report['exit_code'], found


@pytest.mark.pyrel_oracle
@pytest.mark.parametrize('name,population,expected', CORPUS, ids=[f'{n}-{p.name}' for n, p, _ in CORPUS])
def test_duckdb_program_agrees_with_gnd(tmp_path, name, population, expected):
    program = _program(tmp_path, name, 'duckdb')
    run = subprocess.run([str(NATIVE), '-I', str(program), str(population)], capture_output=True, text=True,
                         timeout=300, check=False)
    assert run.stderr == '', run.stderr
    gnd_exit, gnd = _gnd(name, population)
    assert run.returncode == gnd_exit == expected, run.stdout
    assert _findings(run.stdout) == gnd
    _assert_witness_lines_sorted(run.stdout)


def _boundary_population(tmp_path, meal, team_lead):
    """A meal and a team-lead approval sitting exactly on, or just over, their caps."""
    document = json.loads((EXPENSE / 'seed.population.json').read_text())
    for row in document['facts']['expense_has_amount']:
        if row['expense'] == 101:
            row['amount'] = meal
        if row['expense'] == 102:
            row['amount'] = team_lead
    document['facts']['expense_is_approved'].append({'expense': 102})
    document['facts']['expense_approved_by_chain'].append({'expense': 102, 'chain': 'team-lead'})
    path = tmp_path / f'boundary-{meal}-{team_lead}.population.json'
    path.write_text(json.dumps(document))
    return path


@pytest.mark.pyrel_oracle
@pytest.mark.parametrize('meal,team_lead,expected', [(75, 100, 0), (76, 101, 1)])
def test_duckdb_program_agrees_with_gnd_on_the_cap_boundary(tmp_path, meal, team_lead, expected):
    """Discriminates `<=` from `<`: on the cap the rule holds, one over it fails."""
    population = _boundary_population(tmp_path, meal, team_lead)
    program = _program(tmp_path, 'expense', 'duckdb')
    run = subprocess.run([str(NATIVE), '-I', str(program), str(population)], capture_output=True, text=True,
                         timeout=300, check=False)
    gnd_exit, gnd = _gnd('expense', population)
    assert run.returncode == gnd_exit == expected, run.stdout
    assert _findings(run.stdout) == gnd
    _assert_witness_lines_sorted(run.stdout)


def _assert_witness_lines_sorted(stdout):
    """Deterministic output: within a rule, witness lines come in sorted order."""
    by_rule = {}
    for line in stdout.splitlines():
        rule, _, rest = line.partition('  ')
        status, _, witness = rest.partition('  ')
        if status in ('violated', 'warning'):
            by_rule.setdefault(rule, []).append(json.loads(witness))
    for rule, values in by_rule.items():
        rows = [list(v.values()) if isinstance(v, dict) else v for v in values]
        assert rows == sorted(rows, key=lambda r: json.dumps(r)) or values == sorted(values, key=lambda v: json.dumps(v, sort_keys=True)), rule


@pytest.mark.pyrel_oracle
def test_guarded_rule_with_one_empty_antecedent_list_is_vacuous_as_in_gnd(tmp_path):
    """Discriminates 'vacuous when any antecedent list is empty' from 'when all are'."""
    document = json.loads((BOOKREC / 'adult-for-minor.population.json').read_text())
    document['facts']['user_is_minor'] = []
    population = tmp_path / 'no-minors.population.json'
    population.write_text(json.dumps(document))
    program = _program(tmp_path, 'bookrec', 'duckdb')
    run = subprocess.run([str(NATIVE), '-I', str(program), str(population)], capture_output=True, text=True,
                         timeout=300, check=False)
    gnd_exit, gnd = _gnd('bookrec', population)
    assert ('age_appropriate', 'vacuous', 'null') in gnd
    assert run.returncode == gnd_exit and _findings(run.stdout) == gnd


@pytest.mark.pyrel_oracle
@pytest.mark.parametrize('name', sorted(MODELS))
def test_lqp_program_compiles_one_require_per_rule(tmp_path, name):
    program = _program(tmp_path, name, 'lqp')
    run = subprocess.run([str(NATIVE), '-I', str(program), '--compile'], capture_output=True, text=True,
                         timeout=300, check=False)
    assert run.returncode == 0, run.stderr + run.stdout
    reqs = requirements(_parse_document(MODELS[name].read_text()))
    expected = sum(len(r.check.pairs) if r.check.kind == 'same' else 1 for r in reqs)
    lines = run.stdout.splitlines()
    assert lines[0] == f'{expected} requirements compiled for {len(reqs)} rules (expected {expected})'
    compiled = lines[1:]
    # A rule with several check statements compiles to one Require per statement, in order.
    per_rule = [text for req in reqs for text in [None] * (len(req.check.pairs) if req.check.kind == 'same' else 1)]
    assert len(compiled) == len(per_rule)
    firsts, index = [], 0
    for req in reqs:
        firsts.append(compiled[index])
        index += len(req.check.pairs) if req.check.kind == 'same' else 1
    for req, text in zip(reqs, firsts):
        domain, _, check = text.partition(' check ')
        for atom in req.domain:
            assert f' {atom.relation}(' in domain, (req.id, text)
        if req.check.atom is not None:
            assert f' {req.check.atom.relation}(' in check, (req.id, text)
        assert (' Not ' in check) == (req.check.kind == 'absent'), (req.id, text)


@pytest.mark.parametrize('name', sorted(MODELS))
def test_both_programs_state_each_rule_from_one_requirement(name):
    doc = _parse_document(MODELS[name].read_text())
    model, names = _Model(doc), _Names(_Model(doc))
    duckdb, lqp = render(MODELS[name], 'duckdb'), render(MODELS[name], 'lqp')
    for req in requirements(doc):
        rule = require_text(req, names, model)
        assert f'#   rule:      {rule}' in duckdb, req.id
        assert f'    {rule}\n' in lqp, req.id
        assert f'rows({denial_text(req, names, model)})' in duckdb, req.id
        assert '.require(' not in denial_text(req, names, model)
    assert duckdb.count('#   rule:      ') == len(requirements(doc))


def test_programs_are_labelled_by_who_enforces_the_rules():
    duckdb, lqp = render(MODELS['bookrec'], 'duckdb'), render(MODELS['bookrec'], 'lqp')
    assert 'Local DuckDB does not enforce require' in duckdb
    assert 'does NOT enforce require' in lqp and '--connection NAME' in lqp


@pytest.mark.parametrize('family,constraint', [
    ('ring', {'id': 'r', 'type': 'ring', 'modality': 'alethic', 'roles': ['user', 'book'], 'ring': ['irreflexive']}),
    ('frequency', {'id': 'f', 'type': 'frequency', 'modality': 'alethic'}),
])
def test_later_families_are_refused_by_name(family, constraint):
    doc = _parse_document(MODELS['bookrec'].read_text())
    doc['constraints'].append(constraint)
    with pytest.raises(ExportInputError, match=family):
        requirements(doc)


@pytest.mark.parametrize('model,reason', [
    (BOOKREC / 'complete.orm.yaml', 'derived'),
    (PROBES / 'sub.orm.json', 'subtype'),
    (PROBES / 'disc.orm.json', 'disconnected'),
    (PROBES / 'invalid.orm.json', 'invalid model'),
])
def test_unreproduced_semantics_are_refused_by_name(model, reason):
    with pytest.raises(ExportInputError, match=reason):
        render(model, 'duckdb')


@pytest.mark.pyrel_oracle
def test_repeated_facts_are_refused_not_silently_merged(tmp_path):
    """Spanning uniqueness: a set cannot hold the duplicate GND reports, so the input is refused."""
    program = tmp_path / 'span.py'
    program.write_text(render(PROBES / 'span.orm.json', 'duckdb'))
    assert 'Spanning uniqueness' in program.read_text()
    run = subprocess.run([str(NATIVE), '-I', str(program), str(PROBES / 'span.population.json')],
                         capture_output=True, text=True, timeout=300, check=False)
    assert run.returncode == 3 and 'duplicate rows' in run.stderr
    assert api.check(PROBES / 'span.orm.json', PROBES / 'span.population.json')['exit_code'] == 1


@pytest.mark.pyrel_oracle
def test_not_equal_comparison_exports_and_agrees(tmp_path):
    doc = json.loads((PROBES / 'probe.orm.json').read_text())
    for c in doc['constraints']:
        if c['id'] == 'level_cap':
            c['consequent']['comparison']['operator'] = '!='
    model = tmp_path / 'neq.orm.json'
    model.write_text(json.dumps(doc))
    MODELS['neq'] = model
    try:
        program = _program(tmp_path, 'neq', 'duckdb')
        population = PROBES / 'p1.population.json'
        run = subprocess.run([str(NATIVE), '-I', str(program), str(population)], capture_output=True, text=True,
                             timeout=300, check=False)
        gnd_exit, gnd = _gnd('neq', population)
        assert run.returncode == gnd_exit and _findings(run.stdout) == gnd
    finally:
        MODELS.pop('neq')


def test_lqp_program_is_labelled_engine_unverified_and_selects_the_direct_compiler():
    lqp = render(MODELS['bookrec'], 'lqp')
    assert 'ENGINE-UNVERIFIED' in lqp
    assert "'compiler': 'direct'" in lqp
    assert "'Requirements not met' in str(w.message)" in lqp


def test_cli_refuses_checker_options_with_rules(tmp_path):
    run = subprocess.run([sys.executable, '-m', 'gnd', 'export', 'pyrel', str(MODELS['bookrec']), '--rules', 'duckdb',
                          '--connection', 'x', '--out', str(tmp_path / 'r.py')], capture_output=True, text=True,
                         timeout=60, check=False)
    assert run.returncode == 64 and 'apply only to the checker export' in run.stderr


def test_operations_are_refused_until_plans_land():
    doc = _parse_document(MODELS['bookrec'].read_text())
    doc['operations'] = [{'id': 'x'}]
    with pytest.raises(ExportInputError, match='operations'):
        requirements(doc)


def test_cli_writes_new_files_only(tmp_path):
    out = tmp_path / 'rules.py'
    first = subprocess.run([sys.executable, '-m', 'gnd', 'export', 'pyrel', str(MODELS['bookrec']),
                            '--rules', 'lqp', '--out', str(out)], capture_output=True, text=True, timeout=60, check=False)
    assert first.returncode == 0, first.stderr
    assert '.require(' in out.read_text()
    again = subprocess.run([sys.executable, '-m', 'gnd', 'export', 'pyrel', str(MODELS['bookrec']),
                            '--rules', 'duckdb', '--out', str(out)], capture_output=True, text=True, timeout=60, check=False)
    assert again.returncode == 11
    checker = tmp_path / 'checker.py'
    plain = subprocess.run([sys.executable, '-m', 'gnd', 'export', 'pyrel', str(MODELS['bookrec']), '--out', str(checker)],
                           capture_output=True, text=True, timeout=60, check=False)
    assert plain.returncode == 0 and 'program_main' in checker.read_text()
    assert re.search(r'\.require\(', checker.read_text()) is None
