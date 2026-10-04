from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path
from random import Random

import pytest

from gnd.checker import IMPLEMENTED_FAMILIES, check
from gnd.measure.coverage import (
    CASE_KINDS,
    Cell,
    applicability_matrix,
    coverage_fraction,
    families_in_model,
    observed_cells,
)
from gnd.measure.report import build_measurement_report, load_measurement_schema
from gnd.model import Model, load_model
from gnd.population import load_population
from gnd.synth.assemble import assemble_conforming
from gnd.synth.boundary import emit_boundary, enumerate_boundary
from gnd.synth.frontier import (
    BAND4_REASON_CODES,
    SHARED_REASON_CODES,
    enumerate_frontier,
    frontier_codes_for,
    no_subjects_cases,
    reason_codes_by_family,
    unchecked_cases,
)
from gnd.synth.provenance import CASE_KIND_TO_LABEL, read_sidecar

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURES = REPO_ROOT / 'tests' / 'fixtures'
FULL_VOCAB = FIXTURES / 'models' / 'full_vocabulary.orm.yaml'
RING = FIXTURES / 'checker' / 'ring.orm.yaml'
SETFAM = FIXTURES / 'checker' / 'setfam.orm.yaml'
XOR_MULTIROLE = FIXTURES / 'adversarial' / 'models' / 'xor_multirole.orm.yaml'
PARTITION_EXCLUSIVE = FIXTURES / 'adversarial' / 'models' / 'partition_exclusive.orm.yaml'
MISC = FIXTURES / 'checker' / 'misc.orm.yaml'
CORPUS_MODELS = [FULL_VOCAB, RING, SETFAM]

def _baseline(model_path: Path, seed: int=1):
    model = load_model(str(model_path))
    return (model, assemble_conforming(model, seed, model_ref=model_path.name).doc)

def _synth(model_path: Path, out: Path, *, seeds: int=2) -> dict:
    result = subprocess.run([sys.executable, '-m', 'gnd', 'synth', str(model_path), '--out', str(out), '--class', 'all', '--seed', '1', '--seeds', str(seeds), '--format', 'json'], capture_output=True, text=True, cwd=str(REPO_ROOT), check=False)
    assert result.returncode == 0, result.stdout + result.stderr
    return json.loads(result.stdout)

def _measure(model_path: Path, out: Path) -> dict:
    result = subprocess.run([sys.executable, '-m', 'gnd', 'measure', str(model_path), '--populations', str(out), '--format', 'json'], capture_output=True, text=True, cwd=str(REPO_ROOT), check=False)
    assert result.returncode in (0, 6), result.stdout + result.stderr
    return json.loads(result.stdout)

def test_five_case_kinds_map_onto_three_frozen_labels():
    assert CASE_KINDS == ('conforming', 'boundary', 'violating', 'no-subjects', 'unchecked')
    assert set(CASE_KIND_TO_LABEL.values()) == {'conforming', 'boundary', 'violating'}
    assert CASE_KIND_TO_LABEL['no-subjects'] == 'boundary'
    assert CASE_KIND_TO_LABEL['unchecked'] == 'boundary'

@pytest.mark.parametrize('model_path', CORPUS_MODELS, ids=lambda p: p.stem)
def test_every_emitted_label_is_one_of_d10s_three_values(model_path, tmp_path):
    out = tmp_path / 'c'
    payload = _synth(model_path, out)
    labels = set()
    kinds = set()
    for entry in payload['populations']:
        sidecar = read_sidecar(entry['sidecar'])
        labels.add(json.loads(Path(entry['population']).read_text())['population']['label'])
        kinds.add(sidecar.case_kind)
        assert CASE_KIND_TO_LABEL[sidecar.case_kind] == sidecar.class_
    assert labels <= {'conforming', 'boundary', 'violating'}
    assert kinds <= set(CASE_KINDS)

@pytest.mark.parametrize('model_path', CORPUS_MODELS, ids=lambda p: p.stem)
def test_every_cell_is_covered_or_not_applicable_with_a_reason(model_path, tmp_path):
    out = tmp_path / 'c'
    _synth(model_path, out)
    payload = _measure(model_path, out)
    summary = payload['coverage_summary']
    missing = [c for c in summary['applicability_matrix'] if c['status'] == 'missing']
    assert missing == [], missing
    for cell in summary['applicability_matrix']:
        assert cell['status'] in ('covered', 'not-applicable')
        if cell['status'] == 'not-applicable':
            assert cell['reason'] and len(cell['reason']) > 40, cell

def test_textual_conforming_and_violating_are_not_applicable():
    model = load_model(str(FULL_VOCAB))
    assert 'textual' not in IMPLEMENTED_FAMILIES
    cells = {(c.family, c.case_kind): c for c in applicability_matrix(model, {})}
    for kind in ('conforming', 'violating', 'boundary', 'no-subjects'):
        cell = cells['textual', kind]
        assert cell.status == 'not-applicable'
        assert 'textual' in (cell.reason or '') and len(cell.reason or '') > 40
    assert 'IMPLEMENTED_FAMILIES' in (cells['textual', 'conforming'].reason or '')
    assert 'IMPLEMENTED_FAMILIES' in (cells['textual', 'violating'].reason or '')
    assert cells['textual', 'unchecked'].status != 'not-applicable'

def test_subtype_partition_observability_is_resolved_both_ways():
    derivation_only = load_model(str(FULL_VOCAB))
    cells = {(c.family, c.case_kind): c for c in applicability_matrix(derivation_only, {})}
    for kind in ('violating', 'boundary', 'no-subjects'):
        cell = cells['subtype-partition', kind]
        assert cell.status == 'not-applicable'
        assert 'DERIVATION-ONLY' in (cell.reason or '')
    observable = load_model(str(PARTITION_EXCLUSIVE))
    cells = {(c.family, c.case_kind): c for c in applicability_matrix(observable, {})}
    for kind in ('violating', 'boundary'):
        assert cells['subtype-partition', kind].status != 'not-applicable'

def _partition_model(*partition_object_types: tuple[str, bool]):
    from types import SimpleNamespace
    object_types = [{'id': 'super', 'kind': 'entity'}]
    constraints = []
    for index, (suffix, derivation_only) in enumerate(partition_object_types):
        subtype = f'sub{index}{suffix}'
        entry: dict = {'id': subtype, 'kind': 'entity'}
        if derivation_only:
            entry['derivation'] = 'derived'
        object_types.append(entry)
        constraints.append({'type': 'subtype-partition', 'modality': 'alethic', 'supertype': 'super', 'subtypes': [subtype], 'exhaustive': True})
    return SimpleNamespace(object_types=object_types, fact_types=[], constraints=constraints)

def test_partition_observability_is_decided_over_the_family_not_the_first_constraint():
    from gnd.measure.coverage import _partition_is_derivation_only
    derivation_first = _partition_model(('derived', True), ('observable', False))
    observable_first = _partition_model(('observable', False), ('derived', True))
    assert _partition_is_derivation_only(derivation_first) is None, 'an observable partition declared SECOND was invisible — the family was marked unmeasurable and three cells left the coverage denominator'
    assert _partition_is_derivation_only(observable_first) is None
    only_derived = _partition_model(('derived', True), ('also-derived', True))
    assert 'DERIVATION-ONLY' in (_partition_is_derivation_only(only_derived) or '')
    assert _partition_is_derivation_only(_partition_model()) is None

def test_the_matrix_keeps_those_three_cells_applicable():
    derivation_first = _partition_model(('derived', True), ('observable', False))
    cells = {(c.family, c.case_kind): c for c in applicability_matrix(derivation_first, {})}
    for kind in ('violating', 'boundary', 'no-subjects'):
        assert cells['subtype-partition', kind].status != 'not-applicable', kind

def test_mixed_partition_model_keeps_real_unchecked_cell_applicable():
    model = load_model(str(MISC))
    cell = next(cell for cell in applicability_matrix(model, {}) if (cell.family, cell.case_kind) == ('subtype-partition', 'unchecked'))
    assert cell.status in ('covered', 'missing')
    assert cell.status != 'not-applicable'

@pytest.mark.parametrize(('case_kind', 'ground_truth', 'expected_verdict', 'reason', 'predicted'), [('unchecked', 'satisfied', 'pass', None, 'pass'), ('no-subjects', 'satisfied', 'pass', None, 'pass')])
def test_coverage_rejects_contradictory_frontier_sidecars(case_kind, ground_truth, expected_verdict, reason, predicted):
    from types import SimpleNamespace

    from gnd.measure.score import InconsistentExpectationError
    from gnd.synth.provenance import ExpectedState
    model = _partition_model(('derived', True))
    target = 'constraints[0]'
    sidecar = SimpleNamespace(population='contradictory.json', class_='boundary', case_kind=case_kind, target=target, violates_target=None, predicted_verdict=predicted, expectations={target: ExpectedState(ground_truth=ground_truth, expected_verdict=expected_verdict, reason=reason)})
    with pytest.raises(InconsistentExpectationError, match='coverage credit requires'):
        observed_cells([sidecar], model)

def _comparison_model(primitive_a: str, operator: str, primitive_b: str) -> Model:
    return Model(version=1, object_types=[{'id': 'a', 'kind': 'value', 'primitive': primitive_a}, {'id': 'b', 'kind': 'value', 'primitive': primitive_b}], fact_types=[{'id': 'compared', 'reading': '{a} is compared with {b}', 'roles': [{'object_type': 'a', 'role_name': 'a'}, {'object_type': 'b', 'role_name': 'b'}], 'constraints': [{'type': 'value-comparison', 'operator': operator, 'role_a': 'a', 'role_b': 'b', 'modality': 'alethic'}]}])

@pytest.mark.parametrize(('primitive_a', 'operator', 'primitive_b', 'applicable'), [('Integer', '<', 'Float', False), ('Number', '>=', 'Integer', False), ('Integer', '=', 'String', False), ('Integer', '!=', 'String', False), ('Integer', '<', 'String', True)])
def test_comparison_unchecked_matrix_matches_checker_domains(primitive_a, operator, primitive_b, applicable):
    model = _comparison_model(primitive_a, operator, primitive_b)
    cell = next(cell for cell in applicability_matrix(model, {}) if (cell.family, cell.case_kind) == ('value-comparison', 'unchecked'))
    assert (cell.status != 'not-applicable') is applicable

@pytest.mark.parametrize(('ranges', 'applicable'), [([{'min': 0}, {'max': 10}], False), ([{'min': 0}, {'max': 'not-a-number'}], True)])
def test_plural_range_bound_types_drive_unchecked_applicability(ranges, applicable):
    model = Model(version=1, object_types=[{'id': 'count', 'kind': 'value', 'primitive': 'Integer'}], fact_types=[], constraints=[{'type': 'value', 'object_type': 'count', 'ranges': ranges, 'modality': 'alethic'}])
    cell = next(cell for cell in applicability_matrix(model, {}) if (cell.family, cell.case_kind) == ('value', 'unchecked'))
    assert (cell.status != 'not-applicable') is applicable

def test_coverage_is_covered_applicable_over_applicable():
    cells = [Cell('a', 'conforming', 'covered', 3), Cell('a', 'boundary', 'covered', 1), Cell('a', 'violating', 'missing', 0, 'gap'), Cell('a', 'unchecked', 'not-applicable', 0, 'no route')]
    covered, applicable, fraction = coverage_fraction(cells)
    assert (covered, applicable) == (2, 3)
    assert fraction == pytest.approx(2 / 3)

def test_toggling_a_cells_applicability_moves_the_denominator_correctly():
    applicable_version = [Cell('a', 'conforming', 'covered', 1), Cell('a', 'violating', 'missing', 0, 'gap')]
    covered_a, denom_a, fraction_a = coverage_fraction(applicable_version)
    assert (covered_a, denom_a, fraction_a) == (1, 2, 0.5)
    not_applicable_version = [Cell('a', 'conforming', 'covered', 1), Cell('a', 'violating', 'not-applicable', 0, 'never mechanically violable')]
    covered_b, denom_b, fraction_b = coverage_fraction(not_applicable_version)
    assert (covered_b, denom_b, fraction_b) == (1, 1, 1.0)
    assert denom_b == denom_a - 1, 'the not-applicable cell must LEAVE the denominator'

def test_a_matrix_with_no_applicable_cell_is_none_not_a_flattering_one():
    cells = [Cell('textual', kind, 'not-applicable', 0, 'why') for kind in CASE_KINDS]
    assert coverage_fraction(cells) == (0, 0, None)

def test_the_numerator_is_computed_from_emitted_data(tmp_path):
    model, doc = _baseline(FULL_VOCAB)
    out = tmp_path / 'c'
    payload = _synth(FULL_VOCAB, out)
    sidecars = [read_sidecar(entry['sidecar']) for entry in payload['populations']]
    full = applicability_matrix(model, observed_cells(sidecars, model))
    covered_full, applicable_full, _ = coverage_fraction(full)
    kept = [s for s in sidecars if s.case_kind != 'no-subjects']
    assert len(kept) < len(sidecars)
    reduced = applicability_matrix(model, observed_cells(kept, model))
    covered_reduced, applicable_reduced, _ = coverage_fraction(reduced)
    assert covered_reduced < covered_full
    assert applicable_reduced == applicable_full
    del doc

def test_missing_can_actually_fire(tmp_path):
    out = tmp_path / 'c'
    _synth(XOR_MULTIROLE, out)
    payload = _measure(XOR_MULTIROLE, out)
    summary = payload['coverage_summary']
    missing = {(c['family'], c['case_kind']) for c in summary['applicability_matrix'] if c['status'] == 'missing'}
    assert missing == {('exclusive-or', 'violating'), ('exclusive-or', 'no-subjects')}
    assert summary['coverage_fraction'] is not None
    assert summary['coverage_fraction'] < 1.0

def test_families_and_case_kinds_are_derived_from_the_model_never_a_constant():
    model = load_model(str(FULL_VOCAB))
    declared = families_in_model(model)
    assert 'textual' in declared and 'ring' in declared
    assert len(declared) == 14
    assert len(families_in_model(load_model(str(PARTITION_EXCLUSIVE)))) == 1

def test_both_zero_row_join_constructions_are_present_and_score_no_subjects(tmp_path):
    model, doc = _baseline(FULL_VOCAB)
    cases, _downs = no_subjects_cases(model, doc, Random(3))
    names = {c.name for c in cases}
    assert 'zero-row-join-one-side-empty' in names
    assert 'zero-row-join-disjoint-anchors' in names
    disjoint = next(c for c in cases if c.name == 'zero-row-join-disjoint-anchors')
    admitted = emit_boundary(model, disjoint, tmp_path / 'disjoint.json')
    assert admitted.predicted[disjoint.constraint_ref].ground_truth == 'no-subjects'
    assert admitted.observed_verdict == 'vacuous'
    refs = [r for r in model.constraints[0].get('role_refs') or [] if isinstance(r, dict)]
    for role_ref in refs:
        assert disjoint.doc['facts'][str(role_ref['fact_type'])], 'the disjoint-anchors construction must leave both sides POPULATED — an emptied side is the other construction'

@pytest.mark.parametrize('model_path', CORPUS_MODELS, ids=lambda p: p.stem)
def test_every_no_subjects_case_really_lands_on_the_no_subjects_row(model_path, tmp_path):
    model, doc = _baseline(model_path)
    cases, _downs = no_subjects_cases(model, doc, Random(5))
    assert cases
    for index, case in enumerate(cases):
        admitted = emit_boundary(model, case, tmp_path / f'ns.{index}.json')
        state = admitted.predicted[case.constraint_ref]
        assert state.ground_truth == 'no-subjects', case.name
        assert admitted.observed_verdict == admitted.predicted_verdict

def test_cardinality_lower_bound_failure_is_not_labelled_no_subjects():
    model, doc = _baseline(FULL_VOCAB)
    cases, downs = no_subjects_cases(model, doc, Random(7))
    assert all(not (case.family == 'cardinality' and 'empty-object-scope' in case.name) for case in cases)
    assert any(down.family == 'cardinality' and 'violated' in down.reason and ('not a no-subjects one' in down.reason) for down in downs)

def test_a_masked_by_vacuity_candidate_is_refused_as_a_no_subjects_case():
    model, doc = _baseline(FULL_VOCAB)
    _cases, downs = no_subjects_cases(model, doc, Random(11))
    masked = [d for d in downs if 'masked-by-vacuity' in d.reason]
    assert masked, 'the family-emptied mandatory is exactly this shape'
    assert all(d.case_kind == 'no-subjects' for d in masked)

def test_role_scoped_value_frontier_empties_only_the_governed_fact_type(tmp_path):
    model = Model(version=1, object_types=[{'id': 'code', 'kind': 'value', 'primitive': 'String'}], fact_types=[{'id': 'a', 'reading': '{code} appears in a', 'roles': [{'object_type': 'code', 'role_name': 'code'}]}, {'id': 'b', 'reading': '{code} appears in b', 'roles': [{'object_type': 'code', 'role_name': 'code'}]}], constraints=[{'type': 'value', 'object_type': 'code', 'role_ref': {'fact_type': 'a', 'role': 'code'}, 'allowed': ['A'], 'modality': 'alethic'}])
    baseline = {'population': {'model': 'm.orm.yaml', 'source': 'fixture', 'label': 'conforming', 'covers': ['a', 'b']}, 'facts': {'a': [{'code': 'A'}], 'b': [{'code': 'A'}]}}
    cases, _downs = no_subjects_cases(model, baseline, Random(13))
    case = next(candidate for candidate in cases if candidate.constraint_ref == 'constraints[0]' and candidate.name == 'empty-all-scope-fact-types')
    assert not case.doc['facts'].get('a')
    assert case.doc['facts']['b'] == [{'code': 'A'}]
    admitted = emit_boundary(model, case, tmp_path / 'role-value-empty.json')
    assert admitted.predicted[case.constraint_ref].ground_truth == 'no-subjects'
    assert admitted.observed_verdict == 'vacuous'

def test_the_band4_route_set_is_derived_from_the_production_registry():
    from gnd.semantic_registry import REGISTRY
    for code in BAND4_REASON_CODES:
        assert any(row.reason_code == code and row.outcome == 'unchecked' and (row.surface == 'snapshot' or (row.surface == 'applicability' and row.family in {'implemented', 'join'})) for row in REGISTRY)
    assert len(BAND4_REASON_CODES) >= 12
    assert 'textual-not-mechanical' in BAND4_REASON_CODES
    assert 'xor-disjunctive-undefined' in BAND4_REASON_CODES

def test_owned_routes_are_separated_from_the_shared_resolver_guards():
    owned = reason_codes_by_family()
    assert owned['cardinality'] == ('derived-unknown',)
    assert owned['frequency'] == ('derived-unknown',)
    assert 'ring-not-binary' in owned['ring']
    assert 'xor-disjunctive-undefined' in owned['exclusive-or']
    assert owned['guarded'] == ('derived-unknown', 'literal-type-ambiguous', 'reference-join-work-limit', 'values-not-comparable')
    assert 'join-disconnected' in SHARED_REASON_CODES
    assert 'join-disconnected' not in owned['ring']
    assert 'join-disconnected' not in owned['guarded']
    from gnd.semantic_registry import REGISTRY
    assert 'derived-unknown' not in SHARED_REASON_CODES
    assert 'reference-join-work-limit' not in SHARED_REASON_CODES
    for family in ('cardinality', 'frequency', 'guarded'):
        branches = [row for row in REGISTRY if row.surface == 'snapshot' and row.family == family and row.reason_code == 'derived-unknown']
        assert branches
        assert all(row.production_owner == 'gnd.checker._partial_constraint_report' for row in branches)
    branches = [row for row in REGISTRY if row.surface == 'snapshot' and row.family == 'guarded' and row.reason_code == 'reference-join-work-limit']
    assert branches
    assert all(row.production_owner == 'gnd.correspondence._indexed_guarded_bindings' for row in branches)

@pytest.mark.parametrize('model_path', [*CORPUS_MODELS, XOR_MULTIROLE], ids=lambda p: p.stem)
def test_every_unchecked_case_produces_its_asserted_reason_code(model_path, tmp_path):
    model, doc = _baseline(model_path)
    cases, downs = unchecked_cases(model, doc, Random(13))
    for index, case in enumerate(cases):
        expected_code = case.name.removeprefix('unchecked-')
        admitted = emit_boundary(model, case, tmp_path / f'un.{index}.json')
        verdict = next(v for v in admitted.report.verdicts if v.constraint_ref == case.constraint_ref)
        assert verdict.verdict == 'unchecked'
        assert verdict.reason_code == expected_code
        assert admitted.predicted_verdict == 'unchecked'
    reached = {c.name.removeprefix('unchecked-') for c in cases}
    listed = {d.side.removeprefix('unchecked:') for d in downs}
    assert reached | listed == set(frontier_codes_for(model))
    for down in downs:
        assert 'not reachable over this model' in down.reason

def test_a_textual_abstention_is_correct_by_design_not_a_coverage_gap(tmp_path):
    from gnd.measure.score import classify
    from gnd.synth.provenance import ExpectedState
    expected = ExpectedState(ground_truth='satisfied', expected_verdict='unchecked', reason='textual-not-mechanical')
    assert classify(expected, 'unchecked', 'alethic') == 'correct'
    assert classify(expected, 'pass', 'alethic') == 'false_pass'

def test_the_multirole_xor_route_needs_a_populated_construction(tmp_path):
    model, doc = _baseline(XOR_MULTIROLE)
    cases, _downs = unchecked_cases(model, doc, Random(17))
    assert {c.name for c in cases} == {'unchecked-xor-disjunctive-undefined'}
    admitted = emit_boundary(model, cases[0], tmp_path / 'xor.json')
    verdict = next(v for v in admitted.report.verdicts if v.constraint_ref == cases[0].constraint_ref)
    assert verdict.reason_code == 'xor-disjunctive-undefined'

def _probe_routes(model_path: Path) -> set[str]:
    from gnd.model import ModelLoadError, ModelValidationError
    from gnd.synth.assemble import CheckerWitnessDiscrepancy, GeneratorError
    try:
        model, doc = _baseline(model_path)
    except (GeneratorError, CheckerWitnessDiscrepancy, ModelValidationError, ModelLoadError):
        return set()
    cases, _downs = unchecked_cases(model, doc, Random(19))
    return {c.name.removeprefix('unchecked-') for c in cases}


def test_the_payload_carries_the_matrix_and_validates(tmp_path):
    import jsonschema
    out = tmp_path / 'c'
    _synth(FULL_VOCAB, out)
    payload = _measure(FULL_VOCAB, out)
    jsonschema.validate(payload, load_measurement_schema())
    summary = payload['coverage_summary']
    assert summary['applicability_matrix']
    assert summary['coverage_fraction'] == pytest.approx(summary['covered_applicable_cells'] / summary['applicable_cells'])
    assert set(summary['case_kinds']) == set(CASE_KINDS)
    assert summary['boundary_cases_derived'] > 0
    assert summary['boundary_not_derivable'] > 0
    assert 'accuracy' not in json.dumps(payload).lower()

def test_every_rate_is_rendered_beside_its_n(tmp_path):
    out = tmp_path / 'c'
    _synth(FULL_VOCAB, out)
    result = subprocess.run([sys.executable, '-m', 'gnd', 'measure', str(FULL_VOCAB), '--populations', str(out)], capture_output=True, text=True, cwd=str(REPO_ROOT), check=False)
    assert result.returncode in (0, 6)
    text = result.stdout
    assert text.index('COVERAGE') < text.index('false_pass'), 'coverage comes BEFORE rates: a rate over six families is not the same object as a rate over fourteen'
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith(('false_pass=', 'false_fail=', 'undecided=')):
            assert '/' in line, f'a rate without its n: {line}'

def test_a_removed_case_kind_changes_the_payloads_coverage(tmp_path):
    out = tmp_path / 'c'
    payload_before = _synth(FULL_VOCAB, out)
    measured_before = _measure(FULL_VOCAB, out)
    removed = 0
    entries = []
    for entry in payload_before['populations']:
        sidecar = read_sidecar(entry['sidecar'])
        if sidecar.case_kind == 'unchecked':
            Path(entry['population']).unlink()
            Path(entry['sidecar']).unlink()
            removed += 1
        else:
            entries.append(entry)
    assert removed
    index_path = out / 'index.json'
    index = json.loads(index_path.read_text())
    index['populations'] = [e for e in index['populations'] if (out / e['population']).exists()]
    index_path.write_text(json.dumps(index, indent=2))
    measured_after = _measure(FULL_VOCAB, out)
    before = measured_before['coverage_summary']
    after = measured_after['coverage_summary']
    assert after['covered_applicable_cells'] < before['covered_applicable_cells']
    assert after['applicable_cells'] == before['applicable_cells']
    assert after['coverage_fraction'] < before['coverage_fraction']
    shutil.rmtree(out, ignore_errors=True)

def test_enumerate_frontier_returns_both_kinds():
    model, doc = _baseline(FULL_VOCAB)
    cases, downs = enumerate_frontier(model, doc, Random(23))
    assert {c.case_kind for c in cases} == {'no-subjects', 'unchecked'}
    assert downs

def test_boundary_and_frontier_together_cover_every_declared_constraint():
    from gnd.synth.assemble import _constraint_iter_with_ref
    model, doc = _baseline(FULL_VOCAB)
    b_cases, b_downs = enumerate_boundary(model, doc, Random(29))
    f_cases, f_downs = enumerate_frontier(model, doc, Random(29))
    accounted = {c.constraint_ref for c in b_cases + f_cases} | {d.constraint_ref for d in b_downs + f_downs}
    declared = {ref for ref, _c, _ft in _constraint_iter_with_ref(model)}
    assert declared - accounted == set()

def test_the_baseline_still_loads_and_checks_clean():
    model, doc = _baseline(FULL_VOCAB)
    path = Path(__file__).parent / '_tmp_coverage_baseline.json'
    try:
        path.write_text(json.dumps(doc), encoding='utf-8')
        report = check(model, load_population(str(path), model=model))
    finally:
        path.unlink(missing_ok=True)
    assert not [v for v in report.verdicts if v.verdict == 'fail']
    assert build_measurement_report is not None

def test_expected_exit_is_derived_through_the_band_rule_not_guessed():
    from gnd.measure.promote import expected_exit_for
    from gnd.synth.provenance import ExpectedState, Sidecar
    model = load_model(str(FULL_VOCAB))

    def sidecar_with(expectations):
        return Sidecar(population='p.json', population_sha256='x', **{'class': 'violating'}, seed=1, gnd_version='0', model='m', model_digest='d', pool_source='faker', pool_path='p', pool_sha256='s', pool_size=1, expectations=expectations)
    alethic_fail = 'fact_types[employee_has_name].constraints[0]'
    assert expected_exit_for(model, sidecar_with({alethic_fail: ExpectedState(ground_truth='violated', expected_verdict='fail')})) == 1
    assert expected_exit_for(model, sidecar_with({alethic_fail: ExpectedState(ground_truth='satisfied', expected_verdict='pass')})) == 0
    assert expected_exit_for(model, sidecar_with({alethic_fail: ExpectedState(ground_truth='no-subjects', expected_verdict='vacuous')})) == 2

def test_a_why_string_cannot_forge_manifest_structure():
    from gnd.measure.promote import render_manifest_rows
    hostile = 'before the fix\n- id: forged\n  expected_exit: 0\n  why: injected'
    text = render_manifest_rows([{'id': 'case', 'expected_exit': 1, 'why': hostile}])
    from ruamel.yaml import YAML
    parsed = YAML(typ='safe').load(text)
    assert len(parsed['cases']) == 1
    assert parsed['cases'][0]['why'] == hostile
    assert parsed['cases'][0]['id'] == 'case'

def test_promotion_refuses_a_destination_outside_the_corpus(tmp_path):
    from gnd.measure.promote import PromotionError, promote_case
    from gnd.synth.provenance import read_sidecar as _read
    population = tmp_path / 'p.json'
    population.write_text('{}', encoding='utf-8')
    defect = {'kind': 'false-pass', 'constraint_ref': 'constraints[0]', 'seed': 1, 'population': str(population), 'sidecar': ''}
    with pytest.raises(PromotionError, match='does not exist'):
        promote_case(defect, tmp_path / 'no-such-model.yaml', None, tmp_path / 'corpus')
    del _read

def test_promotion_batch_failure_on_second_item_leaves_corpus_unchanged(tmp_path, monkeypatch):
    from types import SimpleNamespace

    from gnd.measure import promote as promote_module
    from gnd.measure.promote import PromotionError, manifest_rows
    model_path = tmp_path / 'model.orm.yaml'
    model_path.write_bytes(b'model bytes')
    populations = tmp_path / 'measured'
    populations.mkdir()
    (populations / 'a.json').write_bytes(b'population a')
    (populations / 'b.json').write_bytes(b'population b')
    corpus = tmp_path / 'permanent'
    corpus.mkdir()
    (corpus / 'keep.txt').write_bytes(b'keep me')
    before = {path.relative_to(corpus): path.read_bytes() for path in corpus.rglob('*') if path.is_file()}
    defects = [{'kind': 'false-pass', 'constraint_ref': f'constraints[{index}]', 'seed': index, 'population': name, 'observed_verdict': 'pass', 'expected_verdict': 'fail', 'modality': 'alethic'} for index, name in enumerate(('a.json', 'b.json'))]
    sidecars = {name: SimpleNamespace(case_kind='violating', class_='violating') for name in ('a.json', 'b.json')}
    calls = 0

    def fail_second(_model, _sidecar):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise PromotionError('second row is invalid')
        return 1
    monkeypatch.setattr(promote_module, 'expected_exit_for', fail_second)
    with pytest.raises(PromotionError, match='second row'):
        manifest_rows(defects, Model(version=1, object_types=[], fact_types=[]), model_path, sidecars, corpus, generator_version='test', populations_root=populations)
    assert {path.relative_to(corpus): path.read_bytes() for path in corpus.rglob('*') if path.is_file()} == before

def test_promotion_is_idempotent_but_refuses_different_existing_bytes(tmp_path):
    from gnd.measure.promote import PromotionError, promote_case
    model = tmp_path / 'model.orm.yaml'
    model.write_bytes(b'model')
    populations = tmp_path / 'measured'
    populations.mkdir()
    (populations / 'case.json').write_bytes(b'population')
    defect = {'kind': 'false-pass', 'constraint_ref': 'constraints[0]', 'seed': 7, 'population': 'case.json'}
    corpus = tmp_path / 'permanent'
    copied = promote_case(defect, model, None, corpus, populations_root=populations)
    assert promote_case(defect, model, None, corpus, populations_root=populations) == copied
    destination = corpus / copied['population']
    destination.write_bytes(b'different')
    with pytest.raises(PromotionError, match='bytes differ'):
        promote_case(defect, model, None, corpus, populations_root=populations)
    assert destination.read_bytes() == b'different'

def test_an_empty_promotion_is_reported_as_a_finding(tmp_path, capsys):
    from gnd.cli import _cmd_measure
    out = tmp_path / 'corpus'
    _synth(FULL_VOCAB, out, seeds=1)
    exit_code = _cmd_measure(str(FULL_VOCAB), str(out), 'text', None, str(tmp_path / 'adversarial'))
    assert exit_code == 0
    assert 'no checker defects to promote' in capsys.readouterr().out

def test_the_promotion_path_is_exercised_end_to_end(monkeypatch, tmp_path):
    from ruamel.yaml import YAML
    from test_measure_negative_control import _ALWAYS_PASS

    import gnd.correspondence
    from gnd.cli import _cmd_measure
    from gnd.measure.promote import MANIFEST_RECORD_KEYS
    out = tmp_path / 'corpus'
    _synth(FULL_VOCAB, out, seeds=1)
    corpus_dir = tmp_path / 'adversarial'
    payload_path = tmp_path / 'broken.json'
    monkeypatch.setattr(gnd.correspondence, 'evaluate_snapshot', _ALWAYS_PASS)
    exit_code = _cmd_measure(str(FULL_VOCAB), str(out), 'json', str(payload_path), str(corpus_dir))
    monkeypatch.undo()
    assert exit_code == 6, 'an always-pass checker must be caught at the exit code'
    payload = json.loads(payload_path.read_text())
    defects = payload['checker_defects']
    assert defects, 'the stub must produce defects to promote'
    manifest_yaml = corpus_dir / 'promoted.manifest.yaml'
    from gnd.measure.promote import manifest_rows, render_manifest_rows
    from gnd.synth import GENERATOR_VERSION
    model = load_model(str(FULL_VOCAB))
    sidecars = {}
    index = json.loads((out / 'index.json').read_text())
    for entry in index['populations']:
        sidecars[entry['population']] = read_sidecar(out / entry['sidecar'])
    rows = manifest_rows(defects, model, str(FULL_VOCAB), sidecars, corpus_dir, generator_version=GENERATOR_VERSION, populations_root=out)
    text = render_manifest_rows(rows)
    manifest_yaml.write_text(text, encoding='utf-8')
    parsed = YAML(typ='safe').load(manifest_yaml.read_text())
    assert len(parsed['cases']) == len(rows)
    for case in parsed['cases']:
        assert set(case) <= set(MANIFEST_RECORD_KEYS)
        assert {'id', 'expected_exit', 'why'} <= set(case)
        assert isinstance(case['expected_exit'], int)
        assert 'Regenerate with seed' in case['why']
        assert GENERATOR_VERSION in case['why']
        assert (corpus_dir / case['model']).exists()
        assert (corpus_dir / case['population']).exists()
    for case in parsed['cases']:
        result = subprocess.run([sys.executable, '-m', 'gnd', 'check', str(corpus_dir / case['model']), str(corpus_dir / case['population'])], capture_output=True, text=True, cwd=str(REPO_ROOT), check=False)
        assert result.returncode == case['expected_exit'], f"{case['id']}: the real checker exits {result.returncode}, but the promoted row pins {case['expected_exit']}\n{result.stdout}{result.stderr}"

def test_every_band4_code_is_reached_by_SOME_fixture_model_or_justified(tmp_path):
    probes = [FULL_VOCAB, RING, SETFAM, XOR_MULTIROLE, PARTITION_EXCLUSIVE, FIXTURES / 'models' / 'guarded_minimal.orm.yaml', FIXTURES / 'checker' / 'misc.orm.yaml', FIXTURES / 'adversarial' / 'models' / 'partition_flagless.orm.yaml', FIXTURES / 'adversarial' / 'models' / 'unresolvable_bound.orm.yaml', FIXTURES / 'adversarial' / 'models' / 'uncomparable_literal.orm.yaml']
    reached: set[str] = set()
    for model_path in probes:
        if not model_path.exists():
            continue
        probed = _probe_routes(model_path)
        reached |= probed
    from support.v70_phase4 import _unknown_positive, _write
    from test_public_reference_budget import _reference_budget_report

    from gnd import api
    model, population = _unknown_positive()
    model['fact_types'][1]['constraints'] = [{'type': 'uniqueness', 'roles': ['item'], 'modality': 'alethic', 'source': 'explicit', 'status': 'confirmed', 'provenance': {'user_quote': 'An item occurs at most once.'}}]
    (tmp_path / 'unknown').mkdir()
    unknown_report = api.check(*_write(tmp_path / 'unknown', model, population), admission=True)
    assert unknown_report['exit_code'] == 4
    assert any(row['reason_code'] == 'derived-unknown' for row in unknown_report['verdicts'])
    reached.update(row['reason_code'] for row in unknown_report['verdicts'] if row['verdict'] == 'unchecked')
    reference_report = _reference_budget_report(tmp_path / 'reference')
    assert reference_report['exit_code'] == 4
    assert any(row['reason_code'] == 'reference-join-work-limit' for row in reference_report['report']['verdicts'])
    reached.update(row['reason_code'] for row in reference_report['report']['verdicts'] if row['verdict'] == 'unchecked')
    justified = {'anchor-sidecar-absent': 'v7.0 anchored model checked without a source sidecar; pinned by the Phase 1 anchor corpus', 'anchor-non-lexical': 'v7.0 anchored numeric role without a recogniser; pinned by the Phase 1 anchor corpus', 'family-unimplemented': 'every schema-admitted active family is now either mechanically implemented or textual (which has its own reason); this defensive route is reachable only from a hostile in-process Model', 'join-disconnected': 'a role sequence whose fact types share no anchor object type — rejected by `gnd validate` before the checker sees it', 'join-anchor-ambiguous': 'a role sequence with two candidate anchors; likewise rejected at validate', 'role-unresolved': 'a `mandatory` naming a role its fact type lacks; rejected at validate', 'subject-type-ambiguous': 'a disjunctive/exclusive constraint whose roles span two object types; rejected at validate', 'ring-not-binary': 'a ring constraint on a non-binary fact type; rejected at validate', 'no-reference-clock': 'a value-comparison against NOW() — present in misc.orm.yaml, whose assembler convergence is a recorded deferred item', 'bound-type-mismatch': 'a value bound typed against the wrong primitive — present in unresolvable_bound.orm.yaml, same deferral', 'literal-type-ambiguous': "a tagged literal outside the role's domain — present in uncomparable_literal.orm.yaml, same deferral", 'values-not-comparable': 'two operands of incomparable primitives — same deferral', 'partition-asserts-nothing': 'a subtype-partition with neither flag — present in partition_flagless.orm.yaml, same deferral'}
    unaccounted = set(BAND4_REASON_CODES) - reached - set(justified)
    assert unaccounted == set(), unaccounted
    assert reached, 'at least one route must actually be pinned'
    assert {'textual-not-mechanical', 'subtype-derivation-only', 'xor-disjunctive-undefined'} <= reached

def test_the_corpus_runner_is_untouched():
    runner = (REPO_ROOT / 'tests' / 'test_adversarial_corpus.py').read_text(encoding='utf-8')
    assert 'promote' not in runner
    assert 'expected_exit' in runner
