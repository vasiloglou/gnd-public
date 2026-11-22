"""RP3: Number is typed like Float; integers a binary float cannot hold exactly are refused (D6)."""
from __future__ import annotations

import hashlib
import subprocess
import sys
from importlib.resources import files
from pathlib import Path

import pytest
import test_pyrel_rules as rules_tests

from gnd import api
from gnd.export.pyrel_rules import render
from gnd.export.pyrel_runtime import ExportInputError

ROOT = Path(__file__).resolve().parents[1]
NATIVE = rules_tests.NATIVE
DEPTH = Path(str(files('gnd').joinpath('examples', 'literature', 'depth_fixture')))
RP3 = ROOT / 'tests/fixtures/pyrel-rules-coverage/rp3'
SIX = RP3 / 'six-line.orm.json'
DECIMAL = DEPTH / 'decimal.orm.json'
BEYOND = 9007199254740993


def _run(program, population):
    return subprocess.run([str(NATIVE), '-I', str(program), str(population)], capture_output=True, text=True,
                          timeout=300, check=False)


def _export(tmp_path, model, target='duckdb'):
    return subprocess.run([sys.executable, '-m', 'gnd', 'export', 'pyrel', str(model), '--rules', target,
                           '--out', str(tmp_path / 'out.py')], capture_output=True, text=True, timeout=120, check=False)


# T1, RP3-C1
@pytest.mark.parametrize('model', [SIX, DECIMAL], ids=lambda p: p.name)
@pytest.mark.parametrize('target', ['duckdb', 'lqp'])
def test_number_models_render(tmp_path, model, target):
    run = _export(tmp_path, model, target)
    assert run.returncode == 0, run.stderr
    assert "score" not in run.stderr


def test_number_is_a_float_field():
    source = render(SIX, 'duckdb')
    assert "['score', 'Number']" in source   # ROLES keeps the model's name for messages
    assert "Field('score', Float)" in source


# T2, T3, RP3-C2: agreement, and the boolean refusal both sides make
AGREE = [
    ('pass', SIX, RP3 / 'pass.population.json', 0),
    ('duplicate', SIX, RP3 / 'duplicate.population.json', 1),
    ('at-bound', SIX, RP3 / 'at-bound.population.json', 1),
    ('decimal', DECIMAL, DEPTH / 'decimal.population.json', 0),
]


@pytest.mark.pyrel_oracle
@pytest.mark.parametrize('model,population,expected', [row[1:] for row in AGREE], ids=[row[0] for row in AGREE])
def test_duckdb_program_agrees_with_gnd(tmp_path, monkeypatch, model, population, expected):
    monkeypatch.setitem(rules_tests.MODELS, 'rp3', model)
    program = tmp_path / 'rules.py'
    program.write_text(render(model, 'duckdb'))
    run = _run(program, population)
    assert run.stderr == '', run.stderr
    gnd_exit, gnd = rules_tests._gnd('rp3', population)
    assert run.returncode == gnd_exit == expected
    assert rules_tests._findings(run.stdout) == gnd


@pytest.mark.pyrel_oracle
def test_a_boolean_in_a_number_role_is_refused_by_both(tmp_path):
    program = tmp_path / 'rules.py'
    program.write_text(render(SIX, 'duckdb'))
    run = _run(program, RP3 / 'boolean.population.json')
    assert run.returncode == 3 and 'run_has_score.score is True, which is not a valid Number' in run.stderr
    assert api.check(SIX, RP3 / 'boolean.population.json', unredacted=True)['exit_code'] == 3


# T4, RP3-C3
def test_arithmetic_on_a_number_value_is_refused_as_on_float():
    with pytest.raises(ExportInputError, match=r'arithmetic on Float or Number values'):
        render(RP3 / 'arithmetic.orm.json', 'duckdb')


# T5, RP3-C4: D6 in a population cell, for Number and Float; GND decides it (pinned)
@pytest.mark.pyrel_oracle
@pytest.mark.parametrize('model,kind', [(SIX, 'Number'), (RP3 / 'float.orm.json', 'Float')], ids=['Number', 'Float'])
def test_an_integer_beyond_2_53_is_refused_by_name(tmp_path, model, kind):
    program = tmp_path / 'rules.py'
    program.write_text(render(model, 'duckdb'))
    population = RP3 / 'beyond.population.json'
    run = _run(program, population)
    assert run.returncode == 3
    assert (f'run_has_score.score is {BEYOND}, an integer beyond 2**53, which a {kind} here (a binary float) '
            'cannot hold exactly; GND keeps it exact') in run.stderr
    assert api.check(model, population, unredacted=True)['exit_code'] == 1   # GND tells the two apart


# T6, T7, T8, RP3-C5: D6 in the model's own constants
@pytest.mark.parametrize('model', ['allowed-beyond', 'range-beyond', 'compare-beyond'])
def test_a_model_constant_beyond_2_53_is_refused_at_export(tmp_path, model):
    run = _export(tmp_path, RP3 / f'{model}.orm.json')
    assert run.returncode == 3, run.stdout + run.stderr
    assert f'the integer {BEYOND} is beyond 2**53' in run.stderr


# T9: Ossie bytes from 6e04fe7f
OSSIE = {
    SIX: ('f1ddea9c2a5cd0df34b0288c0e57644e518a8091ab0f4c06e2c2ae17a1e03348',
          'be32de09bc449fd085c9ad6350048409f7e819bd34d11e0416639e77a54d39c6',
          '12cf0e013318c845b5259005707b91cc4f67e8f374efb2b345e639aca006dd8a'),
    DECIMAL: ('ddb7fd65761f568176f653cd1fbb8708c644008d494abf43686bd26809dca1ea',
              'ace1fceca229193f09a09685682785096f74621c582651e30a6bcec0021f7483',
              '67a1200d7418cea461f0dedc89669852b0c15a3fe5bedebd3da219bd29999405'),
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


# T10
def test_runtime_page_names_number_and_the_bound():
    page = (ROOT / 'docs/runtimes/pyrel.md').read_text()
    assert '`Number` is typed like `Float`' in page
    assert '2**53' in page


# T11: RP1 review r2-F1, deferred here; two Float anchors a binary float cannot tell apart are refused
@pytest.mark.pyrel_oracle
def test_rp1_deferred_float_anchors_beyond_2_53_are_refused(tmp_path):
    model = ROOT / 'tests/fixtures/pyrel-rules-coverage/rp1/numeric-anchor.orm.json'
    population = RP3 / 'anchor-beyond.population.json'
    program = tmp_path / 'rules.py'
    program.write_text(render(model, 'duckdb'))
    run = _run(program, population)
    assert run.returncode == 3 and f'is {BEYOND}, an integer beyond 2**53' in run.stderr
    assert api.check(model, population, unredacted=True)['exit_code'] == 1


# Review r1 F1: integer arithmetic in a derivation still exports (the D6 guard reads variables only)
def test_integer_arithmetic_still_exports(tmp_path):
    for target in ('duckdb', 'lqp'):
        (tmp_path / target).mkdir()
        run = _export(tmp_path / target, RP3 / 'int-arithmetic.orm.json', target)
        assert run.returncode == 0, run.stderr


# Review r1 F2: constants nested in a function term, and constants in a derived head, take the bound
# Review r2 F1/F2: a constant computed by arithmetic, and a Number role hidden behind an Integer one
ARITHMETIC_NEXT_TO_BINARY = 'arithmetic next to a Float or Number value is exact in GND and binary in PyRel'


@pytest.mark.parametrize('model,message', [
    ('nested-beyond', ARITHMETIC_NEXT_TO_BINARY),
    ('computed-beyond', ARITHMETIC_NEXT_TO_BINARY),
    ('head-beyond', f'the integer {BEYOND} is beyond 2**53'),
    ('order-beyond', f'the integer {BEYOND} is beyond 2**53'),
])
def test_a_nested_computed_or_head_constant_beyond_2_53_is_refused(tmp_path, model, message):
    run = _export(tmp_path, RP3 / f'{model}.orm.json')
    assert run.returncode == 3, run.stdout + run.stderr
    assert message in run.stderr


# Review r1 F3: facts of an embedded reference population take the same cell checks as the candidate
@pytest.mark.pyrel_oracle
def test_reference_facts_beyond_2_53_are_refused(tmp_path):
    model, population = RP3 / 'reference/model.orm.json', RP3 / 'reference/empty.population.json'
    program = tmp_path / 'rules.py'
    program.write_text(render(model, 'duckdb'))
    run = _run(program, population)
    assert run.returncode == 3 and f'is {BEYOND}, an integer beyond 2**53' in run.stderr
    assert api.check(model, population, unredacted=True)['exit_code'] == 1


# Review r3 F1: an aggregate written into a Float or Number head role; GND sums exactly, PyRel in binary
def test_a_sum_into_a_number_head_is_refused(tmp_path):
    run = _export(tmp_path, RP3 / 'sum-into-number.orm.json')
    assert run.returncode == 3, run.stdout + run.stderr
    assert 'a sum over or into a Float or Number value is exact in GND and binary in PyRel' in run.stderr


def test_a_count_into_a_number_head_still_exports(tmp_path):
    for target in ('duckdb', 'lqp'):
        (tmp_path / target).mkdir()
        run = _export(tmp_path / target, RP3 / 'count-into-number.orm.json', target)
        assert run.returncode == 0, run.stderr


# Review r5 F1: an Integer aggregate result compared with a Number variable is a mixed comparison, refused
def test_an_integer_sum_compared_with_a_number_value_is_refused(tmp_path):
    run = _export(tmp_path, RP3 / 'sum-compared.orm.json')
    assert run.returncode == 3, run.stdout + run.stderr
    assert 'comparing a Float variable with an Integer variable' in run.stderr
