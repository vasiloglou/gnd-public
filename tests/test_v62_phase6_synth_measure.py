from __future__ import annotations

import contextlib
import copy
import io
import json
from pathlib import Path

from ruamel.yaml import YAML
from support.v62_phase6_corpus import (
    ROOT,
    assert_answer,
    document,
    loaded_case,
    population_document,
    write_case,
)

from gnd.cli import main
from gnd.measure.report import render_measurement
from gnd.model import load_model
from gnd.synth.guarded import exists_witness, modular_repair_plan
from gnd.synth.mutate import expected_state, operators_for


def test_exists_no_witness_mutation(tmp_path: Path) -> None:
    model_path, population_path = write_case(tmp_path / 'baseline')
    model = load_model(model_path)
    baseline_doc = population_document()
    baseline_doc['facts']['radio_sample'] = [row for row in baseline_doc['facts']['radio_sample'] if row['sample'] == 'alpha-1']
    population_path = tmp_path / 'baseline' / 'one-witness.pop.yaml'
    with population_path.open('w', encoding='utf-8') as handle:
        YAML(typ='safe').dump(baseline_doc, handle)
    from random import Random

    from gnd.checker import check
    from gnd.population import load_population
    from gnd.synth.mutate import emit_violating
    population = load_population(population_path, model=model)
    baseline_report = check(model, population)
    assert baseline_report.verdicts[0].verdict == 'pass'
    mutations, stand_downs = operators_for(model, 'constraints[0]', baseline_doc)
    assert not stand_downs and [row.name for row in mutations] == ['remove-exists-witness-for-antecedent-binding']
    case = emit_violating(model, baseline_doc, baseline_report, mutations[0], 'constraints[0]', tmp_path / 'mutated.pop.json', Random(2718))
    assert case.report.verdicts[0].verdict == 'fail'
    assert case.predicted['constraints[0]'].expected_verdict == 'fail'
    assert case.isolating
    assert_answer('E16', exit=0, mutated_verdict=case.report.verdicts[0].verdict, seed=2718)

def test_e40_exists_synthesis_oracle_abstains_on_work_exhaustion(tmp_path: Path) -> None:
    model_doc = document()
    exists = model_doc['constraints'][0]['consequent']['exists']
    exists.pop('where', None)
    exists['atoms'][1]['bind'] = {'cell': '$cell2', 'pci': '$neighbor_pci2', 'modulus': '$modulus2'}
    population_doc = population_document()
    population_doc['facts']['radio_sample'] = [{'sample': 's0', 'monitor': 'm0', 'pci': 29, 'token': 'T'}]
    population_doc['facts']['neighbor_seen'] = [{'sample': 's0', 'neighbor': f'n{index}'} for index in range(400)]
    population_doc['facts']['neighbor_cell'] = [{'cell': f'c{index}', 'pci': 59, 'modulus': 30} for index in range(497)]
    model, population, report, checker_exit = loaded_case(tmp_path, model_doc, population_doc)
    from gnd.synth.mutate import expected_state
    checker_row = report.verdicts[0]
    oracle_claim = exists_witness(model.constraints[0], population.facts)
    expected_state_claim = expected_state(model.constraints[0], None, population_doc, model, {})
    assert checker_exit == 4
    assert checker_row.reason_code == 'guarded-exists-work-limit'
    assert oracle_claim is None
    assert expected_state_claim is None
    assert_answer('E40', exit=checker_exit, checker_reason=checker_row.reason_code, oracle_claim=oracle_claim, expected_state_claim=expected_state_claim, existential_product_rows=198800)
    shared_model_doc = document()
    shared_model_doc['constraints'][0]['antecedent'].append({'fact_type': 'neighbor_seen', 'bind': {'sample': '$sample', 'neighbor': '$other'}})
    shared_path, _ = write_case(tmp_path / 'shared', shared_model_doc, population_document())
    shared_model = load_model(shared_path)
    shared_population = population_document()
    shared_population['facts']['radio_sample'] = [row for row in shared_population['facts']['radio_sample'] if row['sample'] == 'alpha-1']
    shared_mutations, shared_stand_downs = operators_for(shared_model, 'constraints[0]', shared_population)
    assert shared_mutations == []
    assert shared_stand_downs and 'shared' in shared_stand_downs[0]['mechanism']

def test_e44_empty_first_exists_relation_does_not_hide_work_exhaustion(tmp_path: Path) -> None:
    model_doc = document()
    exists = model_doc['constraints'][0]['consequent']['exists']
    exists.pop('where', None)
    population_doc = population_document()
    population_doc['facts']['radio_sample'] = [{'sample': 's0', 'monitor': 'm0', 'pci': 29, 'token': 'T'}]
    population_doc['facts']['neighbor_seen'] = []
    population_doc['facts']['neighbor_cell'] = [{'cell': f'c{index}', 'pci': 59, 'modulus': 30} for index in range(200000)]
    model_path, _ = write_case(tmp_path, model_doc, population_doc)
    population_path = tmp_path / 'population.pop.json'
    population_path.write_text(json.dumps(population_doc, separators=(',', ':')) + '\n', encoding='utf-8')
    model = load_model(model_path)
    from gnd.checker import band, check
    from gnd.population import load_population
    population = load_population(population_path, model=model)
    report = check(model, population)
    checker_exit = band(report)
    from gnd.synth.mutate import expected_state
    checker_row = report.verdicts[0]
    oracle_claim = exists_witness(model.constraints[0], population.facts)
    expected_state_claim = expected_state(model.constraints[0], None, population_doc, model, {})
    assert checker_exit == 4
    assert checker_row.reason_code == 'guarded-exists-work-limit'
    assert oracle_claim is None
    assert expected_state_claim is None
    assert_answer('E44', exit=checker_exit, checker_reason=checker_row.reason_code, oracle_claim=oracle_claim, expected_state_claim=expected_state_claim, existential_source_rows=200000, empty_first_relation=population.facts['neighbor_seen'] == [])

def test_e45_zero_binding_baseline_stands_down_from_witness_removal(tmp_path: Path) -> None:
    model_doc = document()
    model_doc['constraints'][0]['antecedent'][0]['bind']['monitor'] = '$sample'
    model, population, report, checker_exit = loaded_case(tmp_path, model_doc, population_document())
    baseline_doc = population_document()
    oracle_claim = exists_witness(model.constraints[0], population.facts)
    mutations, stand_downs = operators_for(model, 'constraints[0]', baseline_doc)
    checker_row = report.verdicts[0]
    assert checker_exit == 0
    assert checker_row.verdict == 'pass'
    assert oracle_claim is True
    assert mutations == []
    assert len(stand_downs) == 1
    stand_down = stand_downs[0]
    assert stand_down['operator'] == 'remove-exists-witness-for-antecedent-binding'
    assert stand_down['mechanism'] == 'baseline has zero antecedent bindings; no witness can be selected for removal'
    assert_answer('E45', exit=checker_exit, checker_verdict=checker_row.verdict, oracle_claim=oracle_claim, mutation_offered=bool(mutations), stand_down_operator=stand_down['operator'], stand_down_mechanism=stand_down['mechanism'], antecedent_binding_count=0)

def test_exists_measure_reports_support(tmp_path: Path) -> None:
    mixed_model_doc = document()
    mixed_model_doc['constraints'].append({'id': 'unsupported_guarded_comparison', 'type': 'guarded', 'modality': 'alethic', 'source': 'explicit', 'status': 'confirmed', 'antecedent': [{'fact_type': 'radio_sample', 'bind': {'sample': '$sample', 'monitor': '$monitor', 'pci': '$pci', 'token': '$token'}}], 'consequent': {'exists': {'atoms': [{'fact_type': 'radio_sample', 'bind': {'sample': '$sample', 'monitor': '$monitor', 'pci': '$pci', 'token': '$token'}}]}}, 'provenance': {'user_quote': 'Every radio sample is itself a radio sample.'}})
    model_path, _ = write_case(tmp_path / 'mixed', mixed_model_doc, population_document())
    out = tmp_path / 'synth'
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        exit_code = main(['synth', str(model_path), '--class', 'violating', '--seed', '2718', '--out', str(out), '--format', 'json'])
    assert exit_code == 0, output.getvalue()
    synth = json.loads(output.getvalue())
    assert len(synth['populations']) == 1
    emitted = synth['populations'][0]
    assert emitted['baseline_seed'] == 2718
    assert emitted['operator'] == 'remove-exists-witness-for-antecedent-binding'
    assert emitted['band'] == 1
    measurement_path = tmp_path / 'measure.json'
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        exit_code = main(['measure', str(model_path), '--populations', str(out), '--format', 'json', '--out', str(measurement_path)])
    assert exit_code == 0, output.getvalue()
    measured = json.loads(measurement_path.read_text(encoding='utf-8'))
    summary = measured['coverage_summary']
    assert summary['population_count'] == 1
    assert summary['operators_exercised'] == ['remove-exists-witness-for-antecedent-binding']
    assert summary['isolating_cases'] == 1
    not_derivable = synth.get('not_derivable', [])
    assert any(row.get('constraint_ref') == 'constraints[1]' and 'only the bounded two-atom' in row.get('mechanism', '') for row in not_derivable)
    assert summary['boundary_not_derivable'] >= 1
    unsupported_exists = summary.get('unsupported_exists_rules', [])
    assert len(unsupported_exists) == 1
    assert unsupported_exists[0]['constraint_ref'] == 'constraints[1]'
    assert unsupported_exists[0]['mechanism']
    rendered_measurement = render_measurement(measured)
    assert 'constraints[1]' in rendered_measurement
    assert unsupported_exists[0]['mechanism'] in rendered_measurement
    assert_answer('E17', exit=0, supported_mutations=len(synth['populations']), denominator=summary['population_count'], unsupported_named=any(row.get('constraint_ref') == 'constraints[1]' for row in unsupported_exists))
    legacy_model_path = ROOT / 'tests/fixtures/v62-phase3/models/exact-terms.orm.yaml'
    legacy_model = load_model(legacy_model_path)
    legacy_doc = {'population': {'covers': ['input']}, 'facts': {'input': [{'ticket': 't1', 'value': 1, 'divisor': 30}]}}
    mutations, not_derivable = operators_for(legacy_model, 'constraints[0]', legacy_doc)
    assert mutations == []
    assert not_derivable and 'post-MVP frontier' in not_derivable[0]['mechanism']

def test_exists_mutation_stands_down_for_opaque_derived_source(tmp_path: Path) -> None:
    model_doc = document()
    source = next(row for row in model_doc['fact_types'] if row['id'] == 'neighbor_cell')
    source['derivation'] = 'derived'
    source['derivation_rule'] = 'Opaque legacy rule that derives neighbor cells.'
    model_path, _ = write_case(tmp_path, model_doc, population_document())
    model = load_model(model_path)
    baseline = population_document()
    baseline['facts']['radio_sample'] = [row for row in baseline['facts']['radio_sample'] if row['sample'] == 'alpha-1']
    mutations, stand_downs = operators_for(model, 'constraints[0]', baseline)
    assert mutations == [] and stand_downs
    assert any('shared with another constraint or derivation' in row['mechanism'] for row in stand_downs)
    assert_answer('E29', exit=0, mutation_stood_down=not mutations, source_derivation='opaque')

def test_exists_mutation_stands_down_for_structured_derived_source(tmp_path: Path) -> None:
    model_doc = document()
    source = next(row for row in model_doc['fact_types'] if row['id'] == 'neighbor_cell')
    source['derivation'] = 'semiderived'
    source['derivation_rule'] = {'body': [{'fact_type': 'neighbor_seen', 'bind': {'sample': '$sample', 'neighbor': '$cell'}}, {'fact_type': 'radio_sample', 'bind': {'sample': '$sample', 'pci': '$pci', 'monitor': '$monitor', 'token': '$token'}}], 'head': {'cell': '$cell', 'pci': '$pci', 'modulus': 30}}
    model_path, _ = write_case(tmp_path, model_doc, population_document())
    model = load_model(model_path)
    baseline = population_document()
    baseline['facts']['radio_sample'] = [row for row in baseline['facts']['radio_sample'] if row['sample'] == 'alpha-1']
    mutations, stand_downs = operators_for(model, 'constraints[0]', baseline)
    assert mutations == [] and stand_downs
    assert_answer('E27', exit=0, mutation_stood_down=not mutations, source_derivation='structured')

def test_exists_mutation_stands_down_for_derived_source_consumer(tmp_path: Path) -> None:
    model_doc = document()
    model_doc['fact_types'].append({'id': 'derived_neighbor_cell', 'reading': '{Cell} is derived with PCI {Integer} under modulus {Integer}', 'roles': [{'object_type': 'cell', 'role_name': 'cell'}, {'object_type': 'integer', 'role_name': 'pci', 'redact': True}, {'object_type': 'integer', 'role_name': 'modulus'}], 'derivation': 'derived', 'derivation_rule': {'body': [{'fact_type': 'neighbor_cell', 'bind': {'cell': '$cell', 'pci': '$pci', 'modulus': '$modulus'}}], 'head': {'cell': '$cell', 'pci': '$pci', 'modulus': '$modulus'}}})
    model_path, _ = write_case(tmp_path, model_doc, population_document())
    model = load_model(model_path)
    baseline = population_document()
    baseline['facts']['radio_sample'] = [row for row in baseline['facts']['radio_sample'] if row['sample'] == 'alpha-1']
    mutations, stand_downs = operators_for(model, 'constraints[0]', baseline)
    assert mutations == [] and stand_downs
    assert any('derivation' in row['mechanism'] for row in stand_downs)
    assert_answer('E28', exit=0, mutation_stood_down=not mutations, derived_consumer_named=any('derivation' in row['mechanism'] for row in stand_downs))

def test_exists_mutation_stands_down_for_opaque_consumer(tmp_path: Path) -> None:
    model_doc = document()
    model_doc['fact_types'].append({'id': 'opaque_neighbor_summary', 'reading': 'Opaque summary for {Cell}', 'roles': [{'object_type': 'cell', 'role_name': 'cell'}], 'derivation': 'derived', 'derivation_rule': 'Opaque rule may read neighbor_cell'})
    model_path, _ = write_case(tmp_path, model_doc, population_document())
    model = load_model(model_path)
    baseline = population_document()
    baseline['facts']['radio_sample'] = [row for row in baseline['facts']['radio_sample'] if row['sample'] == 'alpha-1']
    mutations, stand_downs = operators_for(model, 'constraints[0]', baseline)
    assert mutations == [] and stand_downs
    assert_answer('E30', exit=0, mutation_stood_down=not mutations, opaque_consumer_stood_down=True)

def test_exists_mutation_stands_down_for_literal_bound_source(tmp_path: Path) -> None:
    model_doc = document()
    model_doc['constraints'][0]['antecedent'][0]['bind']['monitor'] = 'alice'
    model_path, _ = write_case(tmp_path, model_doc, population_document())
    model = load_model(model_path)
    assert modular_repair_plan(model.constraints[0]) is None
    mutations, stand_downs = operators_for(model, 'constraints[0]', population_document())
    assert mutations == [] and stand_downs
    assert any('literal' in row['mechanism'].lower() for row in stand_downs)
    assert_answer('E32', exit=0, mutation_stood_down=not mutations, literal_binding_named=True)

def test_e35_literal_role_bindings_have_no_independent_oracle_claim(tmp_path: Path) -> None:
    model_doc = document()
    model_doc['constraints'][0]['antecedent'][0]['bind']['monitor'] = 'alice'
    population = population_document()
    population['facts']['radio_sample'] = [population['facts']['radio_sample'][0], {**population['facts']['radio_sample'][0], 'sample': 'alpha-bob', 'monitor': 'bob', 'pci': 11, 'token': 'TOKEN-BOB'}]
    model_path, _ = write_case(tmp_path, model_doc, population)
    model = load_model(model_path)
    from gnd.checker import band, check
    from gnd.population import load_population
    loaded_population = load_population(tmp_path / 'population.pop.yaml', model=model)
    checker_report = check(model, loaded_population)
    checker_exit = band(checker_report)
    checker_passes_literal_antecedent = checker_report.verdicts[0].verdict == 'pass'
    antecedent_oracle = exists_witness(model.constraints[0], loaded_population.facts)
    antecedent_expected_state = expected_state(model.constraints[0], None, population, model, {})
    exists_literal_doc = document()
    neighbor_cell = next(fact_type for fact_type in exists_literal_doc['fact_types'] if fact_type['id'] == 'neighbor_cell')
    neighbor_cell['roles'].append({'object_type': 'token', 'role_name': 'tag'})
    neighbor_cell['reading'] += ' and tag {Token}'
    exists_literal_doc['constraints'][0]['consequent']['exists']['atoms'][1]['bind']['tag'] = 'fixed-tag'
    exists_literal_population = population_document()
    for row in exists_literal_population['facts']['neighbor_cell']:
        row['tag'] = 'fixed-tag'
    exists_model_path, exists_population_path = write_case(tmp_path / 'exists-literal', exists_literal_doc, exists_literal_population)
    exists_model = load_model(exists_model_path)
    exists_loaded_population = load_population(exists_population_path, model=exists_model)
    exists_literal_constraint = copy.deepcopy(exists_model.constraints[0])
    exists_atom_model_validated = exists_literal_constraint['id'] == 'neighbor_residue'
    exists_atom_oracle = exists_witness(exists_literal_constraint, exists_loaded_population.facts)
    exists_atom_expected_state = expected_state(exists_literal_constraint, None, exists_literal_population, exists_model, {})
    exists_atom_mutation_plan_rejected = modular_repair_plan(exists_literal_constraint) is None
    numeric_literal_model_doc = document()
    numeric_literal_constraint = numeric_literal_model_doc['constraints'][0]
    numeric_literal_constraint['antecedent'][0]['bind']['pci'] = 11
    numeric_literal_constraint['consequent']['exists'].pop('where', None)
    numeric_literal_population = population_document()
    numeric_literal_population['facts']['radio_sample'] = [row for row in numeric_literal_population['facts']['radio_sample'] if row['sample'] == 'alpha-3']
    numeric_literal_model, _, numeric_literal_report, numeric_literal_exit = loaded_case(tmp_path / 'numeric-literal-antecedent', numeric_literal_model_doc, numeric_literal_population)
    numeric_literal_row = numeric_literal_report.verdicts[0]
    numeric_literal_expected_state = expected_state(numeric_literal_model.constraints[0], None, numeric_literal_population, numeric_literal_model, {})
    from gnd.synth.boundary import predict_boundary
    numeric_literal_boundary = predict_boundary(numeric_literal_model, numeric_literal_population)
    assert numeric_literal_exit == 1 and numeric_literal_row.verdict == 'fail'
    assert numeric_literal_expected_state is None
    assert 'constraints[0]' not in numeric_literal_boundary
    assert_answer('E35', exit=checker_exit, checker_literal_antecedent_passes=checker_passes_literal_antecedent, antecedent_oracle_claim=antecedent_oracle, antecedent_expected_state_claim=antecedent_expected_state, exists_atom_model_validated=exists_atom_model_validated, exists_atom_oracle_claim=exists_atom_oracle, exists_atom_expected_state_claim=exists_atom_expected_state, exists_atom_mutation_plan_rejected=exists_atom_mutation_plan_rejected, numeric_literal_checker_verdict=numeric_literal_row.verdict, numeric_literal_expected_state_claim=numeric_literal_expected_state, numeric_literal_boundary_claimed='constraints[0]' in numeric_literal_boundary)

def test_e38_synth_oracle_keeps_later_undefined_where_terms(tmp_path: Path) -> None:
    model_doc = document()
    where = model_doc['constraints'][0]['consequent']['exists']['where']
    where[:] = [{'operator': '=', 'left': 0, 'right': 1}, {'operator': '=', 'left': {'fn': 'mod', 'args': [1, 0]}, 'right': 0}]
    population_doc = population_document()
    model_path, population_path = write_case(tmp_path, model_doc, population_doc)
    model = load_model(model_path)
    from gnd.checker import band, check
    from gnd.population import load_population
    population = load_population(population_path, model=model)
    report = check(model, population)
    checker_exit = band(report)
    checker_reason = report.verdicts[0].reason_code
    oracle_result = exists_witness(model.constraints[0], population.facts)
    independent_expected = expected_state(model.constraints[0], None, population_doc, model, {})
    mutation_plan_supported = modular_repair_plan(model.constraints[0]) is not None
    assert checker_exit == 4 and checker_reason == 'term:mod-zero'
    assert oracle_result is None
    assert independent_expected is None
    assert not mutation_plan_supported
    assert_answer('E38', exit=0, checker_exit=checker_exit, checker_reason=checker_reason, oracle_claim=oracle_result, expected_state_claim=independent_expected, mutation_plan_supported=mutation_plan_supported)
