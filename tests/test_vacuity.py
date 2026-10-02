from __future__ import annotations

from pathlib import Path

import pytest
from conftest import make_population
from support.cli_runner import run_gnd_text as _run_cli

from gnd.checker import check
from gnd.model import Model, load_model
from gnd.population import load_population

FIXTURES = Path(__file__).parent / 'fixtures' / 'checker'
ADVERSARIAL = Path(__file__).parent / 'fixtures' / 'adversarial'
MODEL = FIXTURES / 'setfam.orm.yaml'
POP_EMPTY = FIXTURES / 'population.empty.yaml'
POP_OMISSION = FIXTURES / 'population.coverage_omission.yaml'
POP_COVERS_NONE = FIXTURES / 'population.covers_none.yaml'
POP_PRECEDENCE = FIXTURES / 'population.precedence.yaml'

@pytest.fixture(scope='module')
def model():
    return load_model(MODEL)

def _report(model, population_path):
    return check(model, load_population(population_path, model=model))

def test_empty_population_zero_passes_all_vacuous(model):
    report = _report(model, POP_EMPTY)
    counts = report.counts()
    assert counts['pass'] == 0, 'Assertion did not hold.'
    assert counts['fail'] == 0 and counts['warning'] == 0
    assert report.verdicts, 'Assertion did not hold.'
    for verdict in report.verdicts:
        assert verdict.verdict == 'vacuous', 'Assertion did not hold.'

def test_covers_empty_list_all_vacuous(model):
    report = _report(model, POP_COVERS_NONE)
    counts = report.counts()
    assert counts['pass'] == 0
    for verdict in report.verdicts:
        assert verdict.verdict == 'vacuous', 'Assertion did not hold.'

def test_coverage_omission_mandatory_vacuous(model):
    report = _report(model, POP_OMISSION)
    mandatory = [v for v in report.verdicts if v.constraint_ref == 'fact_types[booking_by_person].constraints[1]']
    assert len(mandatory) == 1
    assert mandatory[0].verdict == 'vacuous', 'Assertion did not hold.'
    assert 'booking_by_person' in mandatory[0].message, 'Assertion did not hold.'

def test_coverage_omission_is_mandatory_specific(model):
    report = _report(model, POP_OMISSION)
    uniqueness = [v for v in report.verdicts if v.constraint_ref == 'fact_types[booking_by_person].constraints[0]']
    assert len(uniqueness) == 1
    assert uniqueness[0].verdict == 'pass'

def test_report_coverage_field(model):
    report = _report(model, POP_OMISSION)
    coverage = report.coverage
    assert coverage['booking_by_person'].declared == 'undeclared'
    assert coverage['booking_by_person'].facts == 2
    assert coverage['booking_of_room'].declared == 'declared'
    assert coverage['booking_of_room'].facts == 2
    assert set(coverage) == {str(ft.get('id')) for ft in model.fact_types}
_SUBJECTLESS_MODEL = ADVERSARIAL / 'models' / 'no_observable_subjects.orm.yaml'
_SUBJECTLESS_MIN_MODEL = ADVERSARIAL / 'models' / 'no_subjects_cardinality_min.orm.yaml'

def test_a_constraint_with_no_observable_subjects_is_vacuous_not_pass():
    subjectless = load_model(_SUBJECTLESS_MODEL)
    report = _report(subjectless, ADVERSARIAL / 'populations' / 'no_observable_subjects.yaml')
    assert [v.verdict for v in report.verdicts] == ['vacuous'], 'Assertion did not hold.'
    assert 'not evaluated' in report.verdicts[0].message
    assert 'satisfied' not in report.verdicts[0].message, 'Assertion did not hold.'

def test_a_roster_supplies_subjects_even_when_no_fact_type_does():
    subjectless = load_model(_SUBJECTLESS_MODEL)
    report = _report(subjectless, ADVERSARIAL / 'populations' / 'no_observable_subjects.roster.yaml')
    assert [v.verdict for v in report.verdicts] == ['fail'], 'Assertion did not hold.'

def test_roster_subjects_override_empty_fact_type_vacuity():
    roster_model = Model(version=1, object_types=[{'id': 'colour', 'kind': 'value', 'primitive': 'String'}], fact_types=[{'id': 'item_has_colour', 'reading': '{item} has {colour}', 'roles': [{'object_type': 'colour', 'role_name': 'colour'}]}], constraints=[{'type': 'value', 'object_type': 'colour', 'allowed': ['red'], 'modality': 'alethic'}])
    population = make_population(roster_model, model='roster.orm.yaml', source='fixture', covers=['item_has_colour'], instances={'colour': ['purple']}, facts={'item_has_colour': []})
    verdict = check(roster_model, population).verdicts[0]
    assert verdict.verdict == 'fail'
    assert verdict.offending_facts == ['purple']

def test_an_unmet_lower_bound_over_an_empty_universe_is_still_a_failure():
    subjectless = load_model(_SUBJECTLESS_MIN_MODEL)
    report = _report(subjectless, ADVERSARIAL / 'populations' / 'no_subjects_cardinality_min.yaml')
    assert [v.verdict for v in report.verdicts] == ['fail'], 'Assertion did not hold.'

def test_an_alethic_textual_constraint_stays_indeterminate_not_vacuous():
    textual = load_model(ADVERSARIAL / 'models' / 'textual_alethic.orm.yaml')
    report = _report(textual, ADVERSARIAL / 'populations' / 'textual_alethic.violating.yaml')
    assert [v.verdict for v in report.verdicts] == ['unchecked']
    assert report.has_unevaluated_alethic, 'Assertion did not hold.'

def test_cli_empty_population_exits_2_with_zero_pass():
    result = _run_cli('check', str(MODEL), str(POP_EMPTY))
    assert result.returncode == 2, 'Assertion did not hold.'
    assert 'pass=0' in result.stdout, 'Assertion did not hold.'

def test_cli_precedence_alethic_fail_beats_vacuous():
    result = _run_cli('check', str(MODEL), str(POP_PRECEDENCE))
    assert result.returncode == 1, 'Assertion did not hold.'
    assert 'BLOCKING' in result.stdout

def test_cli_coverage_omission_exits_2_and_prints_coverage():
    result = _run_cli('check', str(MODEL), str(POP_OMISSION))
    assert result.returncode == 2, 'Assertion did not hold.'
    assert 'booking_by_person: undeclared, facts=2' in result.stdout, 'Assertion did not hold.'
