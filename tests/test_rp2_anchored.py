"""RP2: anchored constraints are listed as not checked, as gnd check reports them without a sidecar."""
from __future__ import annotations

import ast
import json
import subprocess
import sys
from importlib.resources import files
from pathlib import Path

import pytest
import test_pyrel_rules as rules_tests

from gnd.export.pyrel_rules import _Model, render, render_report, requirements
from gnd.export.pyrel_runtime import ExportInputError, _parse_document

ROOT = Path(__file__).resolve().parents[1]
NATIVE = rules_tests.NATIVE
LIT = Path(str(files('gnd').joinpath('examples', 'literature')))
RP2 = ROOT / 'tests/fixtures/pyrel-rules-coverage/rp2'
REVIEW = ROOT / 'tests/fixtures/pyrel-rules-families/review'
FLAT = LIT / 'model.orm.yaml'
ANCHORED_IDS = ['work_introduces_method#0', 'method_builds_on_method#0', 'method_builds_on_method#1',
                'method_is_used_in_field#0']
REASON = ('source anchor: gnd check decides it with --anchors and --document; '
          'the rules programs read no sidecar')
GOLD = sorted((LIT / 'answers/gold').glob('*.population.json'))


def _run(program, population):
    return subprocess.run([str(NATIVE), '-I', str(program), str(population)], capture_output=True, text=True,
                          timeout=300, check=False)


def _agree(tmp_path, monkeypatch, model, population, source=None):
    """(program exit, GND exit, program findings, GND findings), through the shared comparator."""
    monkeypatch.setitem(rules_tests.MODELS, 'rp2', model)
    program = tmp_path / 'rules.py'
    program.write_text(source if source is not None else render(model, 'duckdb'))
    run = _run(program, population)
    assert run.stderr == '', run.stderr
    gnd_exit, gnd = rules_tests._gnd('rp2', population)
    return run.returncode, gnd_exit, rules_tests._findings(run.stdout), gnd


@pytest.mark.parametrize('model', [FLAT, LIT / 'resolution/model.orm.yaml', LIT / 'interop_fixture/extraction.orm.json',
                                   LIT / 'interop_fixture/checking.orm.json'], ids=lambda p: p.parent.name + '/' + p.name)
@pytest.mark.parametrize('target', ['duckdb', 'lqp'])
def test_anchored_models_render(model, target):
    source, listed = render_report(model, target)
    assert listed and 'not checked' in source


def test_quantity_fixture_passes_anchored_and_stops_on_its_value_rules():
    with pytest.raises(ExportInputError, match=r"time_step#1: family 'value'"):
        render(LIT / 'quantity_fixture/time.orm.yaml', 'duckdb')


def test_anchored_ids_are_listed_and_never_compiled():
    doc = _parse_document(FLAT.read_text())
    model = _Model(doc)
    found = requirements(doc, model)
    assert [row['id'] for row in model.unchecked] == ANCHORED_IDS
    assert {row['reason'] for row in model.unchecked} == {REASON}
    assert not {req.id for req in found} & set(ANCHORED_IDS)
    _, listed = render_report(FLAT, 'duckdb')
    assert listed == ANCHORED_IDS


def test_textual_reason_keeps_the_printed_line():
    doc = _parse_document((REVIEW / 'textual.orm.json').read_text())
    model = _Model(doc)
    requirements(doc, model)
    assert len(model.unchecked) == 2
    for row in model.unchecked:
        assert row['reason'] == f"textual rule: {row['expression']}"
    source = render(REVIEW / 'textual.orm.json', 'duckdb')
    assert "print(f\"{rule['id']}  not checked  ({rule['reason']})\")" in source


def _export(tmp_path, model, *extra):
    return subprocess.run([sys.executable, '-m', 'gnd', 'export', 'pyrel', str(model), *extra,
                           '--out', str(tmp_path / 'out.py')], capture_output=True, text=True, timeout=120, check=False)


def test_success_line_counts_the_listed_rules(tmp_path):
    run = _export(tmp_path, FLAT, '--rules', 'lqp')
    assert run.returncode == 0, run.stderr
    assert run.stdout.strip().endswith('; 4 rule(s) are not checked (listed in the program)')


def test_success_line_without_listed_rules_is_unchanged(tmp_path):
    out = tmp_path / 'out.py'
    run = _export(tmp_path, rules_tests.MODELS['bookrec'], '--rules', 'duckdb')
    assert run.returncode == 0, run.stderr
    assert run.stdout == f"Exported the model's rules as PyRel requirements (duckdb version) to {out}\n"


def test_checker_export_success_line_is_unchanged(tmp_path):
    from gnd.commands import export as export_commands
    source = Path(export_commands.__file__).read_text()
    checker = source[source.index('def _cmd_export_pyrel('):source.index('def _cmd_export_pyrel_rules(')]
    assert 'not checked' not in checker


def test_runtime_page_names_anchored_rules_and_the_deciding_route():
    page = (ROOT / 'docs/runtimes/pyrel.md').read_text()
    assert 'anchored rules are listed as not checked' in page.lower()
    assert '--anchors' in page and '--document' in page


@pytest.mark.pyrel_oracle
@pytest.mark.parametrize('population', GOLD, ids=lambda p: p.stem)
def test_gold_populations_agree_with_gnd(tmp_path, monkeypatch, population):
    ours, theirs, found, gnd = _agree(tmp_path, monkeypatch, FLAT, population)
    assert ours == theirs == 4
    assert found == gnd
    assert {(rule, 'not checked', 'null') for rule in ANCHORED_IDS} <= found


@pytest.mark.pyrel_oracle
def test_negative_control_a_dropped_anchored_id_disagrees(tmp_path, monkeypatch):
    source = render(FLAT, 'duckdb')
    marker = 'UNCHECKED = json.loads('
    start = source.index(marker)
    end = source.index('\n', start)
    rows = json.loads(ast.literal_eval(source[start + len(marker):end - 1]))
    kept = json.dumps(rows[1:])
    tampered = source[:start] + f'{marker}{kept!r})' + source[end:]
    _, _, found, gnd = _agree(tmp_path, monkeypatch, FLAT, GOLD[0], source=tampered)
    assert found != gnd


@pytest.mark.pyrel_oracle
@pytest.mark.parametrize('population,expected', [('full', 4), ('empty', 4)])
def test_anchored_over_an_empty_fact_list_is_still_not_checked(tmp_path, monkeypatch, population, expected):
    ours, theirs, found, gnd = _agree(tmp_path, monkeypatch, RP2 / 'anchored-only.orm.json',
                                      RP2 / f'{population}.population.json')
    assert ours == theirs == expected
    assert found == gnd == {('time_step#0', 'not checked', 'null')}


@pytest.mark.pyrel_oracle
def test_a_deontic_anchored_rule_keeps_the_band(tmp_path, monkeypatch):
    ours, theirs, found, gnd = _agree(tmp_path, monkeypatch, RP2 / 'anchored-deontic.orm.json',
                                      RP2 / 'full.population.json')
    assert ours == theirs == 0
    assert found == gnd


def _lqp_call(tmp_path, model, call):
    program = tmp_path / 'rules_lqp.py'
    program.write_text(render(model, 'lqp'))
    code = (f"import runpy, sys\nns = runpy.run_path({str(program)!r}, run_name='lqp')\n"
            f"sys.exit({call})\n")
    return subprocess.run([str(NATIVE), '-I', '-c', code], capture_output=True, text=True, timeout=300, check=False)


@pytest.mark.pyrel_oracle
def test_lqp_report_lists_the_rules_and_bands_a_must_rule_four(tmp_path):
    run = _lqp_call(tmp_path, FLAT, "ns['lqp_report']([])")
    assert run.returncode == 4, run.stderr
    lines = [line for line in run.stdout.splitlines() if 'not checked' in line]
    assert lines == [f'{rule}  not checked  ({REASON})' for rule in ANCHORED_IDS]
    deontic = _lqp_call(tmp_path, RP2 / 'anchored-deontic.orm.json', "ns['lqp_report']([])")
    assert deontic.returncode == 0, deontic.stderr


@pytest.mark.pyrel_oracle
def test_lqp_compile_prints_the_not_checked_rules(tmp_path):
    program = tmp_path / 'rules_lqp.py'
    program.write_text(render(RP2 / 'anchored-only.orm.json', 'lqp'))
    run = subprocess.run([str(NATIVE), '-I', str(program), '--compile'], capture_output=True, text=True,
                         timeout=300, check=False)
    assert run.returncode == 0, run.stdout + run.stderr
    assert f'time_step#0  not checked  ({REASON})' in run.stdout
