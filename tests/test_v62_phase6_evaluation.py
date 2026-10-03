from __future__ import annotations

import copy
from types import SimpleNamespace

import pytest
from ruamel.yaml import YAML
from support.v62_phase6_corpus import (
    ROOT,
    assert_answer,
    document,
    loaded_case,
    population_document,
)

from gnd.checker import _base_relations, _correspondence_message, _exact_extension_calculator
from gnd.model import ModelValidationError
from gnd.semantic_adapter import adapt_constraint


def _only_sample(population: dict, sample: str) -> dict:
    result = copy.deepcopy(population)
    result['facts']['radio_sample'] = [row for row in result['facts']['radio_sample'] if row['sample'] == sample]
    return result

def _verdict(report):
    assert len(report.verdicts) == 1
    return report.verdicts[0]

def test_e01_single_witness(tmp_path):
    _, _, report, exit_code = loaded_case(tmp_path, population_doc=_only_sample(population_document(), 'alpha-1'))
    assert exit_code == 0
    assert _verdict(report).verdict == 'pass'
    assert_answer('E01', exit=exit_code, verdict=_verdict(report).verdict, bindings=int('bindings=1' in _verdict(report).message))

def test_e02_no_witness_alethic(tmp_path):
    _, _, report, exit_code = loaded_case(tmp_path, population_doc=_only_sample(population_document(), 'alpha-2'))
    row = _verdict(report)
    assert exit_code == 1 and row.verdict == 'fail'
    assert len(row.offending_facts) == 1
    assert set(row.offending_facts[0]) == {'$sample', '$monitor', '$pci', '$token'}
    assert_answer('E02', exit=exit_code, verdict=row.verdict, offending_bindings=len(row.offending_facts), witness_scope='antecedent-only')

def test_e03_no_witness_deontic_warning(tmp_path):
    model = document()
    model['constraints'][0]['modality'] = 'deontic'
    _, _, report, exit_code = loaded_case(tmp_path, model, _only_sample(population_document(), 'alpha-2'))
    assert exit_code == 0 and _verdict(report).verdict == 'warning'
    assert_answer('E03', exit=exit_code, verdict=_verdict(report).verdict, offending_bindings=len(_verdict(report).offending_facts), witness_scope='antecedent-only' if all(set(item) == {'$sample', '$monitor', '$pci', '$token'} for item in _verdict(report).offending_facts) else 'expanded')

def test_e04_zero_bindings_precede_exists_coverage_and_where(tmp_path):
    model = document()
    model['constraints'][0]['antecedent'][0]['bind']['monitor'] = 'no-such-monitor'
    population = population_document()
    population['population']['covers'].remove('neighbor_cell')
    population['facts']['neighbor_cell'][0]['modulus'] = 0
    loaded_model, loaded_population, report, exit_code = loaded_case(tmp_path, model, population)
    row = _verdict(report)
    assert exit_code == 0 and row.verdict == 'pass'
    assert 'bindings=0' in row.message
    assert row.reason_code is None and row.offending_facts == []
    from gnd import semantic_spec
    from gnd.correspondence import _indexed_guarded_exists_verdict, correspond_snapshot
    adapted, _ = correspond_snapshot(loaded_model, loaded_population)
    constraint = adapted.snapshot.constraints[0]
    direct = _indexed_guarded_exists_verdict(constraint, adapted.snapshot, semantic_spec.guarded_variable_names(constraint), (), adapted.snapshot.covers)
    assert direct == ('pass', None, ())
    assert_answer('E04', exit=exit_code, verdict=row.verdict, bindings=0, coverage_checked=False, where_evaluated=False)

def test_e05_existing_empty_antecedent_vacuity(tmp_path):
    population = population_document()
    population['facts']['radio_sample'] = []
    _, _, report, exit_code = loaded_case(tmp_path, population_doc=population)
    assert exit_code == 2 and _verdict(report).verdict == 'vacuous'
    assert_answer('E05', exit=exit_code, verdict=_verdict(report).verdict)

def test_e06_per_binding_witness_failure_is_antecedent_only(tmp_path):
    _, _, report, exit_code = loaded_case(tmp_path)
    row = _verdict(report)
    assert exit_code == 1 and row.verdict == 'fail'
    assert len(row.offending_facts) == 2
    assert [item['$sample'] for item in row.offending_facts] == ['alpha-2', 'alpha-3']
    assert all(set(item) == {'$sample', '$monitor', '$pci', '$token'} for item in row.offending_facts)
    assert_answer('E06', exit=exit_code, verdict=row.verdict, bindings=3, offending_samples=[item['$sample'] for item in row.offending_facts], witness_scope='antecedent-only')

def test_e07_exact_floor_mod_residue_witness(tmp_path):
    _, _, report, exit_code = loaded_case(tmp_path, population_doc=_only_sample(population_document(), 'alpha-1'))
    assert exit_code == 0 and _verdict(report).verdict == 'pass'
    assert_answer('E07', exit=exit_code, verdict=_verdict(report).verdict)

def test_e08_all_candidates_rejected_by_where(tmp_path):
    _, _, report, exit_code = loaded_case(tmp_path, population_doc=_only_sample(population_document(), 'alpha-2'))
    assert exit_code == 1 and _verdict(report).verdict == 'fail'
    assert_answer('E08', exit=exit_code, verdict=_verdict(report).verdict)

def test_e11_missing_witness_coverage_is_unchecked(tmp_path):
    population = _only_sample(population_document(), 'alpha-1')
    defined_coverage_population = copy.deepcopy(population)
    defined_coverage_population['population']['covers'].remove('neighbor_cell')
    defined_model, defined_loaded, defined_report, defined_exit = loaded_case(tmp_path / 'defined-coverage', population_doc=defined_coverage_population)
    defined_row = _verdict(defined_report)
    from gnd.synth.guarded import exists_witness
    from gnd.synth.mutate import expected_state
    defined_oracle = exists_witness(defined_model.constraints[0], defined_loaded.facts)
    defined_expected = expected_state(defined_model.constraints[0], None, defined_coverage_population, defined_model, {})
    assert defined_exit == 4
    assert defined_row.reason_code == 'guarded-exists-coverage-missing'
    assert defined_oracle is True
    assert defined_expected is None
    population['population']['covers'].remove('neighbor_cell')
    population['facts']['neighbor_cell'][1]['modulus'] = 0
    _, _, report, exit_code = loaded_case(tmp_path, population_doc=population)
    row = _verdict(report)
    assert exit_code == 4 and row.verdict == 'unchecked'
    assert row.reason_code == 'guarded-exists-coverage-missing'
    assert 'neighbor_cell' in row.message
    assert_answer('E11', exit=exit_code, verdict=row.verdict, reason=row.reason_code, defined_coverage_checker_exit=defined_exit, defined_coverage_reason=defined_row.reason_code, defined_coverage_oracle_claim=defined_oracle, defined_coverage_expected_state_claim=defined_expected)

def test_e12_undefined_candidate_precedes_a_successful_witness(tmp_path):
    population = _only_sample(population_document(), 'alpha-1')
    population['facts']['neighbor_cell'][1]['modulus'] = 0
    _, _, report, exit_code = loaded_case(tmp_path, population_doc=population)
    row = _verdict(report)
    assert exit_code == 4 and row.verdict == 'unchecked'
    assert row.reason_code == 'term:mod-zero'
    assert len(row.offending_facts) == 1
    binding = row.offending_facts[0]
    assert list(binding) == ['$monitor', '$pci', '$sample', '$token', '$neighbor', '$modulus', '$neighbor_pci']
    assert binding['$sample'] == 'alpha-1'
    assert binding['$monitor'] == 'alice'
    assert binding['$pci'] == 29
    assert binding['$token'] == 'SECRET-EXISTS-271828'
    assert binding['$neighbor'] == 'n-wrong'
    assert binding['$neighbor_pci'] == 28
    assert binding['$modulus'] == 0
    assert 'partial witnesses are suppressed' in row.message
    assert_answer('E12', exit=exit_code, verdict=row.verdict, reason=row.reason_code, binding_present=bool(row.offending_facts), binding_keys=list(binding), partial_pass_suppressed='partial witnesses are suppressed' in row.message)

def test_e13_repeated_join_variable_and_multiple_where_terms(tmp_path):
    model = document()
    exists = model['constraints'][0]['consequent']['exists']
    exists['where'].append({'operator': '!=', 'left': '$neighbor', 'right': 'n-match'})
    _, _, report, exit_code = loaded_case(tmp_path, model, _only_sample(population_document(), 'alpha-1'))
    assert exit_code == 1 and _verdict(report).verdict == 'fail'
    disjoint = population_document()
    disjoint['facts']['radio_sample'] = [row for row in disjoint['facts']['radio_sample'] if row['sample'] == 'alpha-1']
    disjoint['facts']['neighbor_seen'] = [{'sample': 'alpha-1', 'neighbor': 'dangling'}]
    disjoint['facts']['neighbor_cell'] = [{'cell': 'unrelated', 'pci': 59, 'modulus': 30}]
    _, _, disjoint_report, disjoint_exit = loaded_case(tmp_path / 'disjoint', model, disjoint)
    assert disjoint_exit == 1 and _verdict(disjoint_report).verdict == 'fail'
    assert_answer('E13', exit=exit_code, verdict=_verdict(report).verdict, where_count=len(exists['where']), disjoint_join_verdict=_verdict(disjoint_report).verdict)

def test_e26_predecessor_comparison_term_message_stays_comparison_scoped(tmp_path):
    yaml = YAML(typ='safe')
    model_doc = yaml.load((ROOT / 'tests/fixtures/v62-phase3/models/exact-terms.orm.yaml').read_text(encoding='utf-8'))
    population_doc = yaml.load((ROOT / 'tests/fixtures/v62-phase3/populations/term-input.pop.yaml').read_text(encoding='utf-8'))
    model, population, report, exit_code = loaded_case(tmp_path, model_doc, population_doc)
    row = next(row for row in report.verdicts if row.constraint_ref == 'constraints[0]')
    assert exit_code == 4 and row.verdict == 'unchecked'
    assert row.reason_code == 'term:mod-zero'
    finding = SimpleNamespace(constraint_type='guarded', verdict='unchecked', reason_code='term:mod-zero', scope_id='snapshot:guarded:comparison:unchecked-mod-zero')
    envelope_message = _correspondence_message(model.constraints[0], None, finding, [], model, population)
    assert 'Existential consequent' not in envelope_message
    assert_answer('E26', exit=exit_code, verdict=row.verdict, reason=row.reason_code, message_is_not_existential='Existential consequent' not in envelope_message)

def test_e31_unavailable_derived_exists_source_is_unchecked(tmp_path):
    model = document()
    source = next(row for row in model['fact_types'] if row['id'] == 'neighbor_cell')
    source['derivation'] = 'semiderived'
    source['derivation_rule'] = {'body': [{'fact_type': 'neighbor_seen', 'bind': {'sample': '$sample', 'neighbor': '$cell'}}, {'fact_type': 'radio_sample', 'bind': {'sample': '$sample', 'pci': '$pci', 'monitor': '$monitor', 'token': '$token'}}], 'where': [{'operator': '<', 'left': {'fn': 'mod', 'args': ['$pci', 0]}, 'right': 30}], 'head': {'cell': '$cell', 'pci': '$pci', 'modulus': 30}}
    population = population_document()
    population['facts'].pop('neighbor_cell')
    loaded_model, _, report, exit_code = loaded_case(tmp_path, model, population)
    row = _verdict(report)
    assert exit_code == 4 and row.verdict == 'unchecked'
    assert row.reason_code == 'term:mod-zero'
    from gnd.synth.boundary import predict_boundary
    from gnd.synth.mutate import expected_state
    expected_state_claim = expected_state(loaded_model.constraints[0], None, population, loaded_model, {})
    boundary_prediction = predict_boundary(loaded_model, population)
    assert expected_state_claim is None
    assert 'constraints[0]' not in boundary_prediction
    derived_antecedent_model = copy.deepcopy(model)
    derived_antecedent_model['constraints'][0]['antecedent'] = [{'fact_type': 'neighbor_cell', 'bind': {'cell': '$sample', 'pci': '$pci', 'modulus': '$antecedent_modulus'}}]
    derived_antecedent_loaded, _, derived_antecedent_report, derived_antecedent_exit = loaded_case(tmp_path / 'derived-antecedent', derived_antecedent_model, population)
    derived_antecedent_row = _verdict(derived_antecedent_report)
    derived_antecedent_expected_state = expected_state(derived_antecedent_loaded.constraints[0], None, population, derived_antecedent_loaded, {})
    derived_antecedent_boundary = predict_boundary(derived_antecedent_loaded, population)
    assert derived_antecedent_exit == 4
    assert derived_antecedent_row.verdict == 'unchecked'
    assert derived_antecedent_row.reason_code == 'term:mod-zero'
    assert derived_antecedent_expected_state is None
    assert 'constraints[0]' not in derived_antecedent_boundary
    uncovered = copy.deepcopy(population)
    uncovered['population']['covers'].remove('neighbor_cell')
    _, _, uncovered_report, uncovered_exit = loaded_case(tmp_path / 'uncovered', model, uncovered)
    uncovered_row = _verdict(uncovered_report)
    assert uncovered_exit == 4 and uncovered_row.verdict == 'unchecked'
    assert uncovered_row.reason_code == 'guarded-exists-coverage-missing'
    assert_answer('E31', exit=exit_code, verdict=row.verdict, reason=row.reason_code, uncovered_reason=uncovered_row.reason_code, expected_state_claim=expected_state_claim, boundary_claimed_constraint='constraints[0]' in boundary_prediction, derived_antecedent_exit=derived_antecedent_exit, derived_antecedent_reason=derived_antecedent_row.reason_code, derived_antecedent_expected_state_claim=derived_antecedent_expected_state, derived_antecedent_boundary_claimed='constraints[0]' in derived_antecedent_boundary)

def _unavailable_derived_exists_inputs(*, independent_of_antecedent: bool=False):
    model = document()
    source = next(row for row in model['fact_types'] if row['id'] == 'neighbor_cell')
    source['derivation'] = 'semiderived'
    source['derivation_rule'] = {'body': [{'fact_type': 'neighbor_seen', 'bind': {'sample': '$sample', 'neighbor': '$cell'}}, {'fact_type': 'radio_sample', 'bind': {'sample': '$sample', 'pci': '$pci', 'monitor': '$monitor', 'token': '$token'}}], 'where': [{'operator': '<', 'left': {'fn': 'mod', 'args': ['$pci', 0]}, 'right': 30}], 'head': {'cell': '$cell', 'pci': '$pci', 'modulus': 30}}
    if independent_of_antecedent:
        source['derivation_rule'] = {'body': [{'fact_type': 'neighbor_seen', 'bind': {'sample': '$sample', 'neighbor': '$cell'}}], 'where': [{'operator': '<', 'left': {'fn': 'mod', 'args': [1, 0]}, 'right': 30}], 'head': {'cell': '$cell', 'pci': 29, 'modulus': 30}}
    population = population_document()
    population['facts'].pop('neighbor_cell')
    return (model, population)

def test_e33_exists_dependency_does_not_override_coverage_or_zero_bindings(tmp_path):
    model, population = _unavailable_derived_exists_inputs()
    uncovered_other_source = copy.deepcopy(population)
    uncovered_other_source['population']['covers'].remove('neighbor_seen')
    _, _, coverage_report, coverage_exit = loaded_case(tmp_path / 'coverage', model, uncovered_other_source)
    coverage_row = _verdict(coverage_report)
    assert coverage_exit == 4
    assert coverage_row.verdict == 'unchecked'
    assert coverage_row.reason_code == 'guarded-exists-coverage-missing'
    zero_binding_model = copy.deepcopy(model)
    zero_binding_model['constraints'][0]['antecedent'][0]['bind']['monitor'] = 'nobody'
    _, _, zero_binding_report, zero_binding_exit = loaded_case(tmp_path / 'zero-bindings', zero_binding_model, population)
    zero_binding_row = _verdict(zero_binding_report)
    assert zero_binding_exit == 4
    assert zero_binding_row.verdict == 'pass'
    assert zero_binding_row.reason_code is None
    empty_antecedent_model, empty_antecedent_population = _unavailable_derived_exists_inputs(independent_of_antecedent=True)
    empty_antecedent_population['facts']['radio_sample'] = []
    empty_model, empty_population, empty_antecedent_report, empty_antecedent_exit = loaded_case(tmp_path / 'empty-antecedent', empty_antecedent_model, empty_antecedent_population)
    empty_antecedent_row = _verdict(empty_antecedent_report)
    empty_source_unavailable = 'neighbor_cell' in _exact_extension_calculator(empty_model, _base_relations(empty_model, empty_population)).extensions.unavailable
    assert empty_source_unavailable
    assert empty_antecedent_exit == 4
    assert empty_antecedent_row.verdict == 'vacuous'
    assert empty_antecedent_row.reason_code is None
    assert_answer('E33', exit=coverage_exit, uncovered_other_source_reason=coverage_row.reason_code, zero_binding_verdict=zero_binding_row.verdict, zero_binding_reason=zero_binding_row.reason_code, empty_source_unavailable=empty_source_unavailable, empty_antecedent_check_exit=empty_antecedent_exit, empty_antecedent_verdict=empty_antecedent_row.verdict, empty_antecedent_reason=empty_antecedent_row.reason_code)

def test_e36_disconnected_exists_antecedent_preserves_join_refusal(tmp_path):
    from gnd.synth.guarded import exists_witness
    from gnd.synth.mutate import expected_state
    base_model_doc = document()
    base_model_doc['constraints'][0]['antecedent'].append({'fact_type': 'neighbor_seen', 'bind': {'sample': '$other_sample', 'neighbor': '$other_neighbor'}})
    base_population_doc = population_document()
    base_model, base_population, base_report, base_exit = loaded_case(tmp_path / 'ordinary', base_model_doc, base_population_doc)
    base_row = _verdict(base_report)
    oracle_claim = exists_witness(base_model.constraints[0], base_population.facts)
    expected_state_claim = expected_state(base_model.constraints[0], None, base_population_doc, base_model, {})
    assert base_exit == 4
    assert base_row.reason_code == 'join-disconnected'
    assert oracle_claim is None
    assert expected_state_claim is None
    model, population = _unavailable_derived_exists_inputs()
    model['constraints'][0]['antecedent'].append({'fact_type': 'neighbor_seen', 'bind': {'sample': '$other_sample', 'neighbor': '$other_neighbor'}})
    _, _, report, exit_code = loaded_case(tmp_path, model, population)
    row = _verdict(report)
    assert exit_code == 4
    assert row.verdict == 'unchecked'
    assert row.reason_code == 'join-disconnected'
    assert_answer('E36', exit=exit_code, verdict=row.verdict, reason=row.reason_code, ordinary_checker_exit=base_exit, ordinary_checker_reason=base_row.reason_code, oracle_claim=oracle_claim, expected_state_claim=expected_state_claim)

def test_e37_exists_where_reports_exact_value_width_refusal(tmp_path):
    model = document()
    population = population_document()
    population['facts']['radio_sample'] = [row for row in population['facts']['radio_sample'] if row['sample'] == 'alpha-1']
    population['facts']['radio_sample'][0]['pci'] = 1 << 1000
    term = '$pci'
    for _ in range(7):
        term = {'fn': 'mul', 'args': [copy.deepcopy(term), copy.deepcopy(term)]}
    model['constraints'][0]['consequent']['exists']['where'] = [{'operator': '=', 'left': term, 'right': 0}]
    _, _, report, exit_code = loaded_case(tmp_path, model, population)
    row = _verdict(report)
    assert exit_code == 4
    assert row.verdict == 'unchecked'
    assert row.reason_code == 'term:exact-value-too-wide'
    assert len(row.offending_facts) == 2
    binding_keys = sorted(row.offending_facts[0])
    assert all(sorted(binding) == binding_keys for binding in row.offending_facts)
    assert_answer('E37', exit=exit_code, verdict=row.verdict, reason=row.reason_code, undefined_candidate_bindings=len(row.offending_facts), binding_keys=binding_keys, partial_pass_suppressed=row.verdict == 'unchecked')

def test_e39_exists_comparison_cross_product_width_refusal(tmp_path):
    from gnd.synth.guarded import exists_witness
    from gnd.synth.mutate import expected_state
    model = document()
    next(item for item in model['object_types'] if item['id'] == 'integer')['primitive'] = 'Float'
    population = population_document()
    population['facts']['radio_sample'] = [row for row in population['facts']['radio_sample'] if row['sample'] == 'alpha-1']
    population['facts']['radio_sample'][0]['pci'] = 1 << 400
    for row in population['facts']['neighbor_cell']:
        row['pci'] = 2.0 ** (-400)

    def square_seven_times(variable):
        term = variable
        for _ in range(7):
            term = {'fn': 'mul', 'args': [copy.deepcopy(term), copy.deepcopy(term)]}
        return term
    model['constraints'][0]['consequent']['exists']['where'] = [{'operator': '=', 'left': square_seven_times('$pci'), 'right': square_seven_times('$neighbor_pci')}]
    loaded_model, loaded_population, report, checker_exit = loaded_case(tmp_path, model, population)
    row = _verdict(report)
    oracle_claim = exists_witness(loaded_model.constraints[0], loaded_population.facts)
    expected_state_claim = expected_state(loaded_model.constraints[0], None, population, loaded_model, {})
    assert checker_exit == 4
    assert row.reason_code == 'term:exact-value-too-wide'
    assert oracle_claim is None
    assert expected_state_claim is None
    assert_answer('E39', exit=checker_exit, checker_reason=row.reason_code, oracle_claim=oracle_claim, expected_state_claim=expected_state_claim)

def test_e14_hostile_exists_shapes_are_total(tmp_path):
    model = document()
    raw = copy.deepcopy(model['constraints'][0])
    raw['antecedent'] = 'wrong-type'
    raw['consequent'] = {'exists': {'atoms': 'wrong-type', 'where': 12}}
    loaded_model, *_ = loaded_case(tmp_path)
    result = adapt_constraint(raw, None, 'constraints[hostile]', loaded_model)
    assert result.refused in {'malformed-constraint', 'unregistered-family'}
    valid = copy.deepcopy(document()['constraints'][0])
    malformed_where_refused = all((adapt_constraint({**copy.deepcopy(valid), 'consequent': {'exists': {**copy.deepcopy(valid['consequent']['exists']), 'where': value}}}, None, f'constraints[bad-where-{index}]', loaded_model).refused == 'malformed-constraint' for index, value in enumerate((0, False, {}))))
    assert malformed_where_refused
    assert_answer('E14', exit=3, validation='named-refusal', uncaught_exception=False, malformed_where_refused=malformed_where_refused)
    for exists in ({'atoms': []}, {'atoms': {}, 'surprise': True}, {'atoms': None}):
        hostile = copy.deepcopy(model)
        hostile['constraints'][0]['consequent'] = {'exists': exists}
        with pytest.raises(ModelValidationError):
            loaded_case(tmp_path / str(len(exists)), hostile, population_document())

def test_e25_witness_bytes_ignore_candidate_input_order(tmp_path):
    first = population_document()
    second = copy.deepcopy(first)
    second['facts']['neighbor_seen'].reverse()
    second['facts']['neighbor_cell'].reverse()
    second['facts']['radio_sample'].reverse()
    _, _, report_a, _ = loaded_case(tmp_path / 'a', population_doc=first)
    _, _, report_b, exit_b = loaded_case(tmp_path / 'b', population_doc=second)
    byte_identical = report_a.model_dump_json() == report_b.model_dump_json()
    assert byte_identical
    offending = _verdict(report_b).offending_facts
    assert [row['$sample'] for row in offending] == ['alpha-2', 'alpha-3']
    assert_answer('E25', exit=0, check_exit=exit_b, verdict_bytes='identical-after-input-order-swap' if byte_identical else 'different', offending_binding_count=len(offending))
