"""RP5: the packaged literature models exported end to end, and the runtime page states every message."""
from __future__ import annotations

import subprocess
import sys
from importlib.resources import files
from pathlib import Path

import pytest
import test_pyrel_rules as rules_tests

from gnd.export.pyrel_rules import render

ROOT = Path(__file__).resolve().parents[1]
NATIVE = rules_tests.NATIVE
LIT = Path(str(files('gnd').joinpath('examples', 'literature')))
MODELS = ['model.orm.yaml', 'assertions/model.orm.yaml', 'lineage/model.orm.yaml', 'resolution/model.orm.yaml',
          'quantity_fixture/time.orm.yaml', 'interop_fixture/extraction.orm.json', 'interop_fixture/checking.orm.json',
          *[f'depth_fixture/{n}.orm.json' for n in ('algorithms', 'decimal', 'dynamics', 'molecular', 'vocabulary')]]


# RP5-C1: every packaged literature model in plan §1's table exports under both targets
@pytest.mark.parametrize('model', MODELS)
@pytest.mark.parametrize('target', ['duckdb', 'lqp'])
def test_literature_model_exports(tmp_path, model, target):
    run = subprocess.run([sys.executable, '-m', 'gnd', 'export', 'pyrel', str(LIT / model), '--rules', target,
                          '--out', str(tmp_path / 'rules.py')], capture_output=True, text=True, timeout=120, check=False)
    assert run.returncode == 0, run.stderr


# RP5-C2: agreement on every population of plan §1's table, with the GND exit that table records
POPULATIONS = (
    [('model.orm.yaml', p, 4) for p in sorted((LIT / 'answers/gold').glob('*.population.json'))]
    + [('assertions/model.orm.yaml', LIT / 'assertions/raw.population.json', 0)]
    + [('resolution/model.orm.yaml', p, None) for p in sorted((LIT / 'resolution/cases').glob('*/*/population.json'))]
    + [('quantity_fixture/time.orm.yaml', LIT / 'quantity_fixture/time.population.json', 4),
       ('depth_fixture/decimal.orm.json', LIT / 'depth_fixture/decimal.population.json', 0)]
)


def _label(row):
    model, population, _ = row
    return f'{Path(model).parent.name or "flat"}:{population.relative_to(LIT).as_posix()}'


@pytest.mark.pyrel_oracle
@pytest.mark.parametrize('model,population,expected', POPULATIONS, ids=[_label(r) for r in POPULATIONS])
def test_duckdb_program_agrees_with_gnd(tmp_path, monkeypatch, model, population, expected):
    monkeypatch.setitem(rules_tests.MODELS, 'rp5', LIT / model)
    program = tmp_path / 'rules.py'
    program.write_text(render(LIT / model, 'duckdb'))
    run = subprocess.run([str(NATIVE), '-I', str(program), str(population)], capture_output=True, text=True,
                         timeout=300, check=False)
    assert run.stderr == '', run.stderr
    gnd_exit, gnd = rules_tests._gnd('rp5', population)
    if expected is not None:   # the table's measured exit (the resolution cases are measured here)
        assert gnd_exit == expected
    assert run.returncode == gnd_exit
    assert rules_tests._findings(run.stdout) == gnd


# RP5-C3: every not-checked reason and refusal message this milestone added is stated on the runtime page.
# The phase tests (test_rp1..rp4) assert each message verbatim against what the programs print.
MESSAGES = [
    'source anchor: gnd check decides it with --anchors and --document; the rules programs read no sidecar',
    'textual rule: <expression>',
    'join-disconnected: <fact types> share no anchor object type',
    'GND accepts any scalar for an externally identified entity; the rules programs need strings',
    'external frequency is a later phase of the rules programs',
    ('the integer <N> is beyond 2**53, which a Float or Number value here (a binary float) cannot hold exactly; '
     'GND keeps it exact'),
    'an integer beyond 2**53, which a <Float or Number> here (a binary float) cannot hold exactly; GND keeps it exact',
    'arithmetic next to a Float or Number value is exact in GND and binary in PyRel; the rules programs refuse it',
    'a sum over or into a Float or Number value is exact in GND and binary in PyRel; the rules programs refuse it',
    'arithmetic on Float or Number values',
    'a number that is not finite; GND refuses it',
    'duplicate rows in <fact type>: PyRel relations are sets, so repeated facts cannot be checked here; GND reports them',
    'role_ref must be a {fact_type, role} mapping',
    ('<variable> is an Integer value written into the Float or Number role <role>; PyRel would round it '
     'beyond 2**53, so the rules programs refuse it'),
]


def test_every_message_is_on_the_runtime_page():
    page = (ROOT / 'docs/runtimes/pyrel.md').read_text()
    missing = [m for m in MESSAGES if m not in page]
    assert not missing, missing



# Review r1 F1: the Integer-into-Float-or-Number head refusal (RP3) is printed as the page states it
def test_an_integer_min_into_a_number_head_prints_the_documented_refusal():
    import json

    from gnd.export.pyrel_rules import _Model, requirements
    from gnd.export.pyrel_runtime import ExportInputError
    doc = json.loads((ROOT / 'tests/fixtures/pyrel-rules-coverage/rp3/sum-into-number.orm.json').read_text())
    doc['fact_types'][1]['derivation_rule']['aggregate']['fn'] = 'min'
    with pytest.raises(ExportInputError, match=r"\$total is an Integer value written into the Float or Number role "
                                               r"'score'; PyRel would round it beyond 2\*\*53, so the rules programs refuse it"):
        model = _Model(doc)
        requirements(doc, model)
        from gnd.export.pyrel_rules import _derivations, _Names
        _derivations(model, _Names(model), 'duckdb')
