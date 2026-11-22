"""RP1: external uniqueness in the rules programs, over GND's shared-entity join."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import time
from importlib.resources import files
from pathlib import Path

import pytest
import test_pyrel_rules as rules_tests

from gnd import api
from gnd.export import pyrel_rules
from gnd.export.pyrel_rules import _Model, render, render_report, requirements
from gnd.export.pyrel_runtime import ExportInputError, _parse_document

ROOT = Path(__file__).resolve().parents[1]
NATIVE = rules_tests.NATIVE
LIT = Path(str(files('gnd').joinpath('examples', 'literature')))
RP1 = ROOT / 'tests/fixtures/pyrel-rules-coverage/rp1'
REVIEW = ROOT / 'tests/fixtures/pyrel-rules-families/review'
ASSERTIONS = LIT / 'assertions/model.orm.yaml'
D4 = ("GND accepts any scalar for an externally identified entity; the rules programs need strings")


def _run(program, population):
    return subprocess.run([str(NATIVE), '-I', str(program), str(population)], capture_output=True, text=True,
                          timeout=300, check=False)


def _agree(tmp_path, monkeypatch, model, population):
    """(program exit, GND exit, program findings, GND findings), through the shared comparator."""
    monkeypatch.setitem(rules_tests.MODELS, 'rp1', model)
    program = tmp_path / 'rules.py'
    program.write_text(render(model, 'duckdb'))
    run = _run(program, population)
    assert run.stderr == '', run.stderr
    gnd_exit, gnd = rules_tests._gnd('rp1', population)
    return run.returncode, gnd_exit, rules_tests._findings(run.stdout), gnd


def _external(model):
    doc = _parse_document(model.read_text())
    return [r for r in requirements(doc, _Model(doc)) if dict(r.info).get('external')]


# T1, RP1-C1
@pytest.mark.parametrize('model', [ASSERTIONS, LIT / 'lineage/model.orm.yaml'], ids=lambda p: p.parent.name)
@pytest.mark.parametrize('target', ['duckdb', 'lqp'])
def test_literature_models_with_external_uniqueness_render(tmp_path, model, target):
    run = subprocess.run([sys.executable, '-m', 'gnd', 'export', 'pyrel', str(model), '--rules', target,
                          '--out', str(tmp_path / 'out.py')], capture_output=True, text=True, timeout=120, check=False)
    assert run.returncode == 0, run.stderr


# T2, RP1-C2: one Requirement, stated by both programs
def test_both_programs_state_the_one_requirement():
    checked = [r for r in _external(ASSERTIONS) if not r.listing]
    assert len(checked) == 1 and checked[0].check.kind == 'same'
    assert [r.part for r in _external(ASSERTIONS)] == ['join', '']
    statement = ('m.where(assertion_names_passage(assertion_1, passage), assertion_names_work(assertion_1, work), '
                 'assertion_names_passage(assertion_2, passage), assertion_names_work(assertion_2, work))'
                 '.require(assertion_1 == assertion_2)')
    duckdb, lqp = (render(ASSERTIONS, target) for target in ('duckdb', 'lqp'))
    assert duckdb.count(f'#   rule:      {statement}') == 1
    assert lqp.count(f'    {statement}\n') == 1
    assert duckdb.count('#   rule:') == sum(1 for r in requirements(_parse_document(ASSERTIONS.read_text()))
                                            if not r.listing)


# T3, RP1-C5
def test_the_review_fixture_renders_and_external_frequency_still_refuses():
    render(REVIEW / 'refuse-external-uniqueness.orm.json', 'duckdb')
    with pytest.raises(ExportInputError, match='external frequency'):
        render(REVIEW / 'refuse-external-frequency.orm.json', 'duckdb')


# T4, RP1-C6 (render half)
def test_a_disconnected_join_is_listed_not_lowered():
    doc = _parse_document((RP1 / 'disconnected.orm.json').read_text())
    model = _Model(doc)
    assert not [r for r in requirements(doc, model) if r.id == 'eu']
    assert model.unchecked == [{'id': 'eu', 'modality': 'alethic', 'vacuous_if_empty': ['lives', 'capital'],
                                'reason': 'join-disconnected: lives, capital share no anchor object type'}]
    source = Path(pyrel_rules.__file__).read_text()
    body = source[source.index('def _external_uniqueness('):source.index('def spanning_uniqueness(')]
    assert body.index('join-disconnected') < body.index('atoms = [')   # classification precedes the lowering


# T10: one walk over the model's rules
def test_no_second_walk_over_the_model_rules():
    source = Path(pyrel_rules.__file__).read_text()
    for name in ('def requirements(', 'def render('):
        start = source.index(name)
        end = source.find('\ndef ', start + 1)
        body = source[start:end if end > 0 else len(source)]
        assert body.count("doc.get(\"constraints\"") + body.count("doc['constraints']") <= 1, name


# T11
def test_runtime_page_checks_external_uniqueness_and_refuses_external_frequency():
    page = (ROOT / 'docs/runtimes/pyrel.md').read_text()
    assert 'External uniqueness is checked' in page
    assert 'External frequency, exclusive-or' in page
    assert 'External uniqueness\nand frequency' not in page
    assert 'programs need strings' in page


# T12: totality over malformed role_refs
@pytest.mark.parametrize('refs,match', [
    (None, 'non-empty list'), ([], 'non-empty list'), ('lives', 'non-empty list'), ([['lives', 'country']], 'non-empty list'),
    ([{'fact_type': 'lives'}], 'non-empty list'), ([{'fact_type': 'nowhere', 'role': 'x'}], "unknown fact type 'nowhere'"),
    ([{'fact_type': 'lives', 'role': 'x'}], "has no role 'x'"),
    ([{'fact_type': 'lives', 'role': 'country'}, {'fact_type': 'lives', 'role': 'country'}], 'twice'),
])
def test_malformed_role_refs_are_refused_by_name(refs, match):
    doc = json.loads((RP1 / 'renamed-anchor.orm.json').read_text())
    doc['constraints'][0]['role_refs'] = refs
    with pytest.raises(ExportInputError, match=match):
        requirements(doc, _Model(doc))


# T13: linear lowering
def test_a_two_hundred_fact_type_chain_renders_quickly(tmp_path):
    n = 200
    objects = [o for i in range(n + 1) for o in (
        {'id': f'o{i}', 'name': f'O{i}', 'kind': 'entity', 'reference': {'mode': 'popular', 'value_type': 'code'}},)]
    objects += [{'id': 'code', 'name': 'Code', 'kind': 'value', 'primitive': 'String'}]
    facts = [{'id': f'f{i}', 'reading': '{A} {B} {C}', 'roles': [
        {'object_type': f'o{i}', 'role_name': 'left'}, {'object_type': f'o{i + 1}', 'role_name': 'right'},
        {'object_type': 'code', 'role_name': 'value'}]} for i in range(n)]
    doc = {'version': 1, 'model_id': 'urn:gnd:rp1:chain', 'object_types': objects, 'fact_types': facts,
           'source': {'kind': 'text-conversation', 'confidence': 'standard', 'mode': 'one-shot'},
           'constraints': [{'id': 'eu', 'type': 'uniqueness', 'scope': 'external', 'modality': 'alethic',
                            'source': 'explicit', 'status': 'confirmed',
                            'role_refs': [{'fact_type': f'f{i}', 'role': 'value'} for i in range(n)]}]}
    start = time.monotonic()
    found = requirements(doc, _Model(doc))
    assert time.monotonic() - start < 5
    assert [r.part for r in found if r.id == 'eu'] == ['join', '']


# T14, RP1-C7: an ambiguous join is an invalid model, for both
def test_an_ambiguous_join_is_refused_as_gnd_refuses_the_model(tmp_path):
    model = RP1 / 'ambiguous.orm.json'
    export = subprocess.run([sys.executable, '-m', 'gnd', 'export', 'pyrel', str(model), '--rules', 'duckdb',
                             '--out', str(tmp_path / 'out.py')], capture_output=True, text=True, timeout=120, check=False)
    assert export.returncode == 3 and 'invalid model' in export.stderr
    assert 'multiple candidate anchor roles' in export.stderr
    check = subprocess.run([sys.executable, '-m', 'gnd', 'check', str(model), str(RP1 / 'disconnected-facts.population.json')],
                           capture_output=True, text=True, timeout=120, check=False)
    assert check.returncode == 3


def test_the_ambiguity_guard_also_holds_without_model_validation():
    doc = json.loads((RP1 / 'ambiguous.orm.json').read_text())
    with pytest.raises(ExportInputError, match='ambiguous in knows'):
        pyrel_rules._external_uniqueness(_Model(doc), {**doc['constraints'][0]})


# T17, plan §3: the Ossie export keeps its bytes (digests measured at 6e04fe7f, before this phase)
OSSIE = {
    ASSERTIONS: ('d10e534ff9fbdb93f8c80f335538a9450d2553192639113f757b64f2714136c1',
                 '9af8c1516396d1b6356fc16b13c3532f5da6fd96a03e31f8012b6974cf2432c0',
                 '017e724cc5cfafce9489d8589ab0961a3de9fe6d8b147fd2a6d98a0c20a47f72'),
    RP1 / 'three-way.orm.json': ('d4e1122e034fd267af4a2e09bde0cfd0bde6c9addd7f055fcafc49eaf9a52c3f',
                                 'ae6e72bdd22434a29a275b73066426ca9affe635100be8d18d7ba0b20658eb12',
                                 'cd8ba04eb13fe970e18fe0388d8b89e277c9c01ca58d26c5d38decfca1ffc0da'),
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


# T5-T9, T15, T16, RP1-C3/C4/C6/C8/C9: the DuckDB program against gnd check
AGREE = [
    ('assertions-raw', ASSERTIONS, LIT / 'assertions/raw.population.json', 0, set()),
    ('assertions-duplicate', ASSERTIONS, RP1 / 'assertions-duplicate.population.json', 1,
     {('constraints_0', 'violated', '[["p01", "working-notes"]]')}),
    ('assertions-empty-join', ASSERTIONS, RP1 / 'assertions-empty-join.population.json', 2,
     {('constraints_0', 'vacuous', 'null')}),
    ('disconnected-facts', RP1 / 'disconnected.orm.json', RP1 / 'disconnected-facts.population.json', 4,
     {('eu', 'not checked', 'null')}),
    ('disconnected-partial', RP1 / 'disconnected.orm.json', RP1 / 'disconnected-partial.population.json', 4,
     {('eu', 'not checked', 'null')}),
    ('disconnected-empty', RP1 / 'disconnected.orm.json', RP1 / 'disconnected-empty.population.json', 2,
     {('eu', 'vacuous', 'null')}),
    ('renamed-anchor', RP1 / 'renamed-anchor.orm.json', RP1 / 'renamed-duplicate.population.json', 1,
     {('eu', 'violated', '[["fr", "fr"]]')}),
    ('numeric-anchor', RP1 / 'numeric-anchor.orm.json', RP1 / 'numeric-duplicate.population.json', 1,
     {('eu', 'violated', '[["fr", "paris"]]')}),
    ('three-way-duplicate', RP1 / 'three-way.orm.json', RP1 / 'three-way-duplicate.population.json', 1,
     {('eu', 'violated', '[["acme", "paris", "fr"]]')}),
    ('three-way-pass', RP1 / 'three-way.orm.json', RP1 / 'three-way-pass.population.json', 0, set()),
]


@pytest.mark.pyrel_oracle
@pytest.mark.parametrize('model,population,expected,findings', [row[1:] for row in AGREE], ids=[row[0] for row in AGREE])
def test_duckdb_program_agrees_with_gnd(tmp_path, monkeypatch, model, population, expected, findings):
    ours, theirs, found, gnd = _agree(tmp_path, monkeypatch, model, population)
    assert ours == theirs == expected
    assert found == gnd == findings


@pytest.mark.pyrel_oracle
def test_a_non_string_external_id_is_refused_where_gnd_accepts_it(tmp_path):
    population = RP1 / 'assertions-integer-id.population.json'
    program = tmp_path / 'rules.py'
    program.write_text(render(ASSERTIONS, 'duckdb'))
    run = _run(program, population)
    assert run.returncode == 3
    assert f'assertion_names_passage.assertion is 7: {D4}' in run.stdout + run.stderr
    assert api.check(ASSERTIONS, population, unredacted=True)['exit_code'] == 0   # D4's stated difference


@pytest.mark.pyrel_oracle
def test_negative_control_a_join_without_the_anchor_check_disagrees(tmp_path, monkeypatch):
    source = render(ASSERTIONS, 'duckdb')
    tampered = source.replace(', assertion_1 != assertion_2).select(passage, work)', ').select(passage, work)')
    assert tampered != source
    monkeypatch.setitem(rules_tests.MODELS, 'rp1', ASSERTIONS)
    program = tmp_path / 'rules.py'
    program.write_text(tampered)
    population = LIT / 'assertions/raw.population.json'
    run = _run(program, population)
    assert rules_tests._findings(run.stdout) != rules_tests._gnd('rp1', population)[1]


@pytest.mark.pyrel_oracle
def test_lqp_compile_lists_the_disconnected_rule(tmp_path):
    program = tmp_path / 'rules_lqp.py'
    program.write_text(render(RP1 / 'disconnected.orm.json', 'lqp'))
    run = subprocess.run([str(NATIVE), '-I', str(program), '--compile'], capture_output=True, text=True,
                         timeout=300, check=False)
    assert run.returncode == 0, run.stdout + run.stderr
    assert 'eu  not checked  (join-disconnected: lives, capital share no anchor object type)' in run.stdout


@pytest.mark.pyrel_oracle
@pytest.mark.parametrize('model', [ASSERTIONS, RP1 / 'three-way.orm.json'], ids=lambda p: p.name)
def test_lqp_program_compiles_the_requirement(tmp_path, model):
    program = tmp_path / 'rules_lqp.py'
    program.write_text(render(model, 'lqp'))
    run = subprocess.run([str(NATIVE), '-I', str(program), '--compile'], capture_output=True, text=True,
                         timeout=300, check=False)
    assert run.returncode == 0, run.stdout + run.stderr


# Review r1 F1: 1 and 1.0 are one number to GND, so two such rows repeat a fact; the programs refuse
# repeated facts (relations are sets) instead of merging them into a pass
@pytest.mark.pyrel_oracle
@pytest.mark.parametrize('model,population', [
    (RP1 / 'numeric-anchor.orm.json', RP1 / 'numeric-repeated-fact.population.json'),
    (RP1 / 'numeric-inline.orm.json', RP1 / 'numeric-inline-repeated.population.json'),
], ids=['external', 'inline'])
def test_numerically_repeated_facts_are_refused_not_merged(tmp_path, model, population):
    program = tmp_path / 'rules.py'
    program.write_text(render(model, 'duckdb'))
    run = _run(program, population)
    assert run.returncode == 3 and 'duplicate rows in holds' in run.stderr, run.stdout + run.stderr
    assert api.check(model, population, unredacted=True)['exit_code'] == 1   # GND reports the repeat


# Review r1 F2: a disconnected rule's emptiness is read from the computed view of semiderived types
@pytest.mark.pyrel_oracle
def test_disconnected_vacuity_reads_computed_semiderived_relations(tmp_path, monkeypatch):
    ours, theirs, found, gnd = _agree(tmp_path, monkeypatch, RP1 / 'disconnected-semiderived.orm.json',
                                      RP1 / 'disconnected-semiderived.population.json')
    assert ours == theirs == 2
    assert found == gnd == {('eu', 'vacuous', 'null')}


# Review r1 F3: the LQP program refuses an unreadable population with exit 3, before any connection
@pytest.mark.pyrel_oracle
def test_lqp_refuses_a_non_string_external_id_with_exit_3(tmp_path):
    program = tmp_path / 'rules_lqp.py'
    program.write_text(render(ASSERTIONS, 'lqp'))
    run = subprocess.run([str(NATIVE), '-I', str(program), str(RP1 / 'assertions-integer-id.population.json'),
                          '--connection', 'unused'], capture_output=True, text=True, timeout=300, check=False)
    assert run.returncode == 3, run.stdout + run.stderr
    assert D4 in run.stderr and 'Traceback' not in run.stderr


# Review r2 F2: a non-finite number (1e400 reads as infinity) is refused with exit 3, never a traceback
@pytest.mark.pyrel_oracle
@pytest.mark.parametrize('target', ['duckdb', 'lqp'])
def test_a_non_finite_number_is_refused_with_exit_3(tmp_path, target):
    model, population = RP1 / 'numeric-anchor.orm.json', RP1 / 'infinite.population.json'
    program = tmp_path / 'rules.py'
    program.write_text(render(model, target))
    extra = ['--connection', 'unused'] if target == 'lqp' else []
    run = subprocess.run([str(NATIVE), '-I', str(program), str(population), *extra], capture_output=True, text=True,
                         timeout=300, check=False)
    assert run.returncode == 3 and 'not finite' in run.stderr and 'Traceback' not in run.stderr
    check = subprocess.run([sys.executable, '-m', 'gnd', 'check', str(model), str(population)],
                           capture_output=True, text=True, timeout=120, check=False)
    assert check.returncode == 3


# Review r3 F1: the finite check lives in the shared check_cell, so rosters and plan bindings take it too
@pytest.mark.pyrel_oracle
@pytest.mark.parametrize('target', ['duckdb', 'lqp'])
def test_a_non_finite_roster_value_is_refused_with_exit_3(tmp_path, target):
    model, population = RP1 / 'numeric-anchor.orm.json', RP1 / 'infinite-roster.population.json'
    program = tmp_path / 'rules.py'
    program.write_text(render(model, target))
    extra = ['--connection', 'unused'] if target == 'lqp' else []
    run = subprocess.run([str(NATIVE), '-I', str(program), str(population), *extra], capture_output=True, text=True,
                         timeout=300, check=False)
    assert run.returncode == 3 and 'instances.badge is inf, a number that is not finite' in run.stderr
    assert 'Traceback' not in run.stderr


@pytest.mark.pyrel_oracle
@pytest.mark.parametrize('value', ["float('nan')", "float('inf')", "float('-inf')"])
def test_check_cell_refuses_non_finite_numbers_for_every_caller(tmp_path, value):
    program = tmp_path / 'rules.py'
    program.write_text(render(RP1 / 'numeric-anchor.orm.json', 'duckdb'))
    code = (f"import runpy\nns = runpy.run_path({str(program)!r}, run_name='probe')\n"
            f"try:\n    ns['check_cell']('step 1', 'badge', 'Float', {value})\n"
            "except ValueError as error:\n    print(error)\n")
    run = subprocess.run([str(NATIVE), '-I', '-c', code], capture_output=True, text=True, timeout=300, check=False)
    assert run.returncode == 0, run.stderr
    assert 'step 1.badge is' in run.stdout and 'not finite' in run.stdout


def test_success_line_counts_a_disconnected_rule(tmp_path):
    _, listed = render_report(RP1 / 'disconnected.orm.json', 'duckdb')
    assert listed == ['eu']


# Close review B1: the LQP version decides a disconnected join's vacuity from the population, as GND does
@pytest.mark.pyrel_oracle
@pytest.mark.parametrize('population,expected', [('disconnected-empty', 2), ('disconnected-facts', 4),
                                                 ('disconnected-partial', 4)])
def test_lqp_report_bands_a_disconnected_join_as_gnd(tmp_path, population, expected):
    program = tmp_path / 'rules_lqp.py'
    program.write_text(render(RP1 / 'disconnected.orm.json', 'lqp'))
    path = RP1 / f'{population}.population.json'
    code = (f"import runpy, sys\nns = runpy.run_path({str(program)!r}, run_name='lqp')\n"
            f"sys.exit(ns['lqp_report']([], ns['read_population']({str(path)!r})))\n")
    run = subprocess.run([str(NATIVE), '-I', '-c', code], capture_output=True, text=True, timeout=300, check=False)
    assert run.returncode == expected, run.stdout + run.stderr
    assert api.check(RP1 / 'disconnected.orm.json', path, unredacted=True)['exit_code'] == expected


def test_lqp_refuses_a_disconnected_join_over_a_derived_fact_type():
    with pytest.raises(ExportInputError, match='LQP version cannot tell whether it is vacuous'):
        render(RP1 / 'disconnected-semiderived.orm.json', 'lqp')
    render(RP1 / 'disconnected-semiderived.orm.json', 'duckdb')   # the DuckDB version checks it (RP1 review r1-F2)


# Close review B2: a population that is not an object, or a fact list that is not a list of objects, exits 3
@pytest.mark.pyrel_oracle
@pytest.mark.parametrize('target', ['duckdb', 'lqp'])
@pytest.mark.parametrize('population', ['array', 'bad-row'])
def test_a_malformed_population_is_refused_with_exit_3(tmp_path, target, population):
    program = tmp_path / 'rules.py'
    program.write_text(render(RP1 / 'disconnected.orm.json', target))
    extra = ['--connection', 'unused'] if target == 'lqp' else []
    run = subprocess.run([str(NATIVE), '-I', str(program), str(RP1 / f'{population}.population.json'), *extra],
                         capture_output=True, text=True, timeout=300, check=False)
    assert run.returncode == 3 and 'not a readable population' in run.stderr and 'Traceback' not in run.stderr


# Close review (claude): GND accepts a role named twice in role_refs and decides it; the programs refuse it
def test_a_role_named_twice_is_refused_where_gnd_decides_it(tmp_path):
    doc = json.loads((RP1 / 'renamed-anchor.orm.json').read_text())
    doc['constraints'][0]['role_refs'] = [{'fact_type': 'lives', 'role': 'country'},
                                          {'fact_type': 'lives', 'role': 'country'},
                                          {'fact_type': 'heads', 'role': 'country'}]
    model = tmp_path / 'twice.orm.json'
    model.write_text(json.dumps(doc))
    with pytest.raises(ExportInputError, match='twice; the rules programs refuse that'):
        render(model, 'duckdb')
    population = json.loads((RP1 / 'renamed-duplicate.population.json').read_text())
    population['population']['model'] = model.name
    (tmp_path / 'twice.population.json').write_text(json.dumps(population))
    assert api.check(model, tmp_path / 'twice.population.json', unredacted=True)['exit_code'] == 1
