"""RP4: value constraints scoped to a role, written at the top level or on a fact type."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from importlib.resources import files
from pathlib import Path

import pytest
import test_pyrel_rules as rules_tests

from gnd.export.pyrel_rules import _Model, render, requirements
from gnd.export.pyrel_runtime import ExportInputError

ROOT = Path(__file__).resolve().parents[1]
NATIVE = rules_tests.NATIVE
RP4 = ROOT / 'tests/fixtures/pyrel-rules-coverage/rp4'
TIME = Path(str(files('gnd').joinpath('examples', 'literature', 'quantity_fixture', 'time.orm.yaml')))


def _export(tmp_path, model, target):
    out = tmp_path / target
    out.mkdir(exist_ok=True)
    return subprocess.run([sys.executable, '-m', 'gnd', 'export', 'pyrel', str(model), '--rules', target,
                           '--out', str(out / 'rules.py')], capture_output=True, text=True, timeout=120, check=False)


# T1, T3: RP4-C1, RP4-C3
@pytest.mark.parametrize('model', [RP4 / 'top.orm.json', RP4 / 'fact.orm.json', TIME], ids=['top', 'fact', 'time'])
@pytest.mark.parametrize('target', ['duckdb', 'lqp'])
def test_role_scoped_value_models_export(tmp_path, model, target):
    run = _export(tmp_path, model, target)
    assert run.returncode == 0, run.stderr


def test_the_role_scoped_domain_is_the_role_not_the_universe():
    for model, rule in ((RP4 / 'top.orm.json', 'graded'), (RP4 / 'fact.orm.json', 'has_grade#0')):
        doc = json.loads(model.read_text())
        (req,) = [r for r in requirements(doc, _Model(doc)) if r.id == rule]
        assert [a.relation for a in req.domain] == ['has_grade']
        assert req.vacuous_when == ('any', ('has_grade',))


# T2, T4, T5: RP4-C2 and the fact-scoped universe form, against gnd check
AGREE = [(m, p, e) for m, rows in [
    ('top', [('deny', 1), ('other-role', 0), ('roster', 0), ('empty-role', 2)]),
    ('fact', [('deny', 1), ('other-role', 0), ('roster', 0), ('empty-role', 2)]),
    ('fact-plain', [('deny', 1), ('other-role', 1), ('roster', 1), ('empty-role', 1)]),
    ('range', [('range-deny', 1), ('range-pass', 0)]),
    # review r2 F1: a fact type whose name ends in _any is a fact type, not a universe
    ('any-named', [('any-named-deny', 1), ('any-named-other-role', 0), ('any-named-empty-role', 2)]),
    # review r3 F1: even <object type>_any, when no universe of that type is generated
    ('universe-named', [('universe-named-deny', 1), ('universe-named-other-role', 0), ('universe-named-empty-role', 2)]),
] for p, e in rows]


@pytest.mark.pyrel_oracle
@pytest.mark.parametrize('model,population,expected', AGREE, ids=[f'{m}-{p}' for m, p, _ in AGREE])
def test_duckdb_program_agrees_with_gnd(tmp_path, monkeypatch, model, population, expected):
    path = RP4 / f'{model}.orm.json'
    monkeypatch.setitem(rules_tests.MODELS, 'rp4', path)
    program = tmp_path / 'rules.py'
    program.write_text(render(path, 'duckdb'))
    pop = RP4 / f'{population}.population.json'
    run = subprocess.run([str(NATIVE), '-I', str(program), str(pop)], capture_output=True, text=True, timeout=300,
                         check=False)
    assert run.stderr == '', run.stderr
    gnd_exit, gnd = rules_tests._gnd('rp4', pop)
    assert run.returncode == gnd_exit == expected
    assert rules_tests._findings(run.stdout) == gnd


# T6: Ossie bytes from 33bd03db
OSSIE = {
    RP4 / 'top.orm.json': ('82f75e8ade7eb98c0a9b06f340db0b9927aed5668aa1ce14b65e128eca6b4f70',
                           'cd188f7c3526047ce71ff2d3170c11173887dc9d800d49c7fbb07230b44a9b51',
                           '0ac169ac4206b07bec39f74928234618c412081176240125d42d3585dc3fc645'),
    RP4 / 'fact.orm.json': ('921ae30d0bfeafd047d063a2657a0a343cbb97ffeddd0caa489e0f5ce22a9e99',
                            'be6475e6fb2cdc1e458f6365c10eff7a48f032f5e11fd1630a04c3edb81b8262',
                            'a364d857d33c0f7b3fd806fd840b83199580cb847d15786ca1f1d7b552cd51d7'),
    # review r1 F2: a fact-scoped value rule without role_ref stays an Ossie extension (digests at f02c58d8)
    RP4 / 'fact-plain.orm.json': ('826fdf3494ffe31961a1d2054c1cc65e8a448c058c0d53b5236cf463d872a0c9',
                                  '04cf03d721a83f2fb5886d82d76a261c12135fb3eb89bfb895174b2c42f6201b',
                                  'c6f34420842eee2a9195e9189abe09bf4cea74d08b173384ed033843d04dfea0'),
    TIME: ('59de2b6456176dcf3f215a327dce1577d2086a9310ae91aadf0d0f115a1d97f6',
           'bce83aab1ec991f77beac0bbe4797d76e1ed96a57045557b0880c4aaebe5fef1',
           'b727b3dbc4d17fc9963b94d05affd0c34cc279c71800a8447a2ca45d117ff722'),
}


@pytest.mark.parametrize('model', list(OSSIE), ids=lambda p: p.name)
def test_ossie_export_is_unchanged(tmp_path, model):
    out = tmp_path / 'ossie'
    run = subprocess.run([sys.executable, '-m', 'gnd', 'export', 'ossie', str(model), '--out', str(out)],
                         capture_output=True, text=True, timeout=120, check=False)
    assert run.returncode == 0, run.stderr
    digests = tuple(hashlib.sha256(Path(f'{out}{suffix}').read_bytes()).hexdigest()
                    for suffix in ('', '.gnd.json', '.loss.json'))
    assert digests == OSSIE[model]


# T7
def test_runtime_page_names_role_scoped_value_constraints():
    page = (ROOT / 'docs/runtimes/pyrel.md').read_text()
    assert 'A value constraint scoped to a role' in page


# T8
@pytest.mark.parametrize('ref,match', [
    ('has_grade', 'role_ref must be'), ({'fact_type': 'has_grade'}, 'role_ref must be'),
    ({'fact_type': 'has_grade', 'role': 'student'}, 'is not played by grade'),
    ({'fact_type': 'nowhere', 'role': 'grade'}, "unknown fact type 'nowhere'"),
])
def test_a_malformed_role_ref_is_refused_by_name(ref, match):
    doc = json.loads((RP4 / 'top.orm.json').read_text())
    doc['constraints'][0]['role_ref'] = ref
    with pytest.raises(ExportInputError, match=match):
        requirements(doc, _Model(doc))


# Review r1 F1: a range helper's universe is a generated name; a fact type may not take it
def test_a_fact_type_named_like_a_range_universe_is_refused():
    with pytest.raises(ExportInputError, match="fact type 'grade_any' has the name of a relation"):
        render(RP4 / 'universe-name.orm.json', 'duckdb')


# Review r4 F1 (predates RP4): a plan's create effect generates its object type's universe; a fact type of that
# name is refused by name instead of being redeclared
def test_a_fact_type_named_like_a_plan_created_universe_is_refused():
    with pytest.raises(ExportInputError, match="fact type 'grade_any' has the name of a relation"):
        render(RP4 / 'create-named.orm.json', 'duckdb')
