from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path
from random import Random

import pytest

from gnd.checker import CheckReport
from gnd.cli import main
from gnd.model import load_model
from gnd.synth import assemble as assemble_module
from gnd.synth.assemble import CheckerWitnessDiscrepancy, GeneratorError, assemble_conforming
from gnd.synth.oracle import constructive as constructive_module
from gnd.synth.poolfile import build_faker_pool

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / 'tests' / 'fixtures' / 'synth-external-uniqueness'

def _model(name: str):
    return load_model(str(CORPUS / f'{name}.orm.yaml'))

def _builder(model, seed=12):
    rng = Random(seed)
    pool = build_faker_pool(model, Random(rng.getrandbits(64)), size_per_type=8)
    return assemble_module._Builder(model, pool, rng, 6)

@pytest.mark.parametrize('name', ['external-single', 'external-second', 'external-pair', 'mandatory-one-to-one', 'external-exhausted', 'mandatory-exhausted'])
def test_corpus_models_are_valid(name):
    assert _model(name).version == 1

def test_external_pair_preserves_popular_reference_distinction():
    model = _model('external-pair')
    modes = {obj['reference']['mode'] for obj in model.object_types if obj.get('kind') == 'entity'}
    assert modes == {'popular'}

def test_external_pair_is_one_atomic_component():
    builder = _builder(_model('external-pair'))
    components = builder._external_uniqueness_components()
    assert [[ref for ref, _constraint in component] for component in components] == [['constraints[0]', 'constraints[1]']]

def test_external_search_groups_match_independent_join_order():
    model = _model('external-pair')
    builder = _builder(model)
    builder.construct()
    doc = {'facts': builder.facts, 'instances': {}}
    for constraint in model.constraints:
        if constraint.get('type') != 'uniqueness':
            continue
        refs = list(constraint['role_refs'])
        groups = builder._external_join_groups(refs)
        observed = [tuple((builder.facts[ftid][row_index][role] for ftid, row_index, role in group)) for group in groups]
        assert observed == assemble_module._join(doc, model, refs)

@pytest.mark.parametrize(('name', 'witness_refs'), [('external-single', {'constraints[0]'}), ('external-second', {'constraints[0]'}), ('external-pair', {'constraints[0]', 'constraints[1]'})])
def test_external_uniqueness_succeeds_for_200_seeds(name, witness_refs):
    model = _model(name)
    for seed in range(1, 201):
        assembly = assemble_conforming(model, seed, model_ref=f'{name}.orm.yaml')
        assert all(assembly.witnesses[ref] is True for ref in witness_refs)

def test_requested_seed_12_is_not_retried_or_relabelled(tmp_path):
    out = tmp_path / 'corpus'
    model_path = CORPUS / 'external-pair.orm.yaml'
    assert main(['synth', str(model_path), '--out', str(out), '--seed', '12']) == 0
    sidecars = list((out / 'conforming').glob('*.meta.json'))
    assert len(sidecars) == 1
    assert json.loads(sidecars[0].read_text(encoding='utf-8'))['seed'] == 12

def test_external_pair_same_seed_is_byte_deterministic():
    model = _model('external-pair')
    first = assemble_conforming(model, 12, model_ref='external-pair.orm.yaml')
    second = assemble_conforming(model, 12, model_ref='external-pair.orm.yaml')
    assert json.dumps(first.doc, sort_keys=True) == json.dumps(second.doc, sort_keys=True)

def test_external_pair_is_byte_deterministic_across_processes(tmp_path):
    outputs = []
    for name in ('first', 'second'):
        out = tmp_path / name
        completed = subprocess.run([sys.executable, '-m', 'gnd', 'synth', str(CORPUS / 'external-pair.orm.yaml'), '--out', str(out), '--seed', '12'], check=False, capture_output=True, text=True)
        assert completed.returncode == 0, completed.stdout + completed.stderr
        population = next(path for path in (out / 'conforming').glob('*.json') if not path.name.endswith(('.meta.json', '.pool.json')))
        outputs.append((population.read_bytes(), population.with_suffix('.meta.json').read_bytes()))
    assert outputs[0] == outputs[1]

def test_mandatory_one_to_one_succeeds_for_40_seeds_with_unused_counterparts():
    model = _model('mandatory-one-to-one')
    for seed in range(1, 41):
        assembly = assemble_conforming(model, seed, model_ref='mandatory-one-to-one.orm.yaml')
        rows = assembly.doc['facts']['cover_matches_slot']
        assert len({row['cover'] for row in rows}) == len(rows) == 3
        assert len({row['slot'] for row in rows}) == len(rows)

def test_deontic_external_uniqueness_is_not_a_fatal_goal():
    model = _model('external-exhausted')
    model.constraints[0]['modality'] = 'deontic'
    assembly = assemble_conforming(model, 12, model_ref='external-exhausted.orm.yaml')
    assert assembly.witnesses['constraints[0]'] is False

def test_deontic_singleton_uniqueness_does_not_block_mandatory_closure():
    model = _model('mandatory-exhausted')
    fact_type = next(ft for ft in model.fact_types if ft['id'] == 'card_matches_slot')
    fact_type['constraints'][1]['modality'] = 'deontic'
    builder = _builder(model)
    builder.construct()
    builder.facts['card_matches_slot'].pop()
    builder._close_mandatory()
    covered = {row['card'] for row in builder.facts['card_matches_slot']}
    assert covered == set(builder.work['card'])

def test_entity_counterpart_completion_does_not_advance_rng():
    model = _model('mandatory-one-to-one')
    builder = _builder(model)
    builder.construct()
    builder.facts['cover_matches_slot'].pop()
    state = builder.rng.getstate()
    builder._close_mandatory()
    assert builder.rng.getstate() == state

def test_value_counterpart_uses_first_compatible_draw(monkeypatch):
    model = _model('external-second')
    fact_type = next(ft for ft in model.fact_types if ft['id'] == 'link_has_number')
    fact_type['constraints'].append({'type': 'uniqueness', 'roles': ['number'], 'source': 'explicit', 'status': 'confirmed', 'modality': 'alethic'})
    builder = _builder(model)
    configurations = builder.work['link']
    builder.facts = {'link_has_number': [{'link': configurations[0], 'number': 1}, {'link': configurations[1], 'number': 2}]}
    draws = iter([3] + [1] * 20)
    monkeypatch.setattr(builder, '_draw_value', lambda *_args: next(draws))
    candidate = builder._mandatory_completion(fact_type, {'link': configurations[2]}, 'fact_types[link_has_number].constraints[1]')
    assert candidate['number'] == 3

def test_mandatory_candidate_validation_never_mutates_live_facts(monkeypatch):
    model = _model('mandatory-one-to-one')
    builder = _builder(model)
    builder.construct()
    row = builder.facts['cover_matches_slot'].pop()
    before = copy.deepcopy(builder.facts)
    calls = 0
    real_witness_map = assemble_module._witness_map

    def exploding_witness_map(*args, **kwargs):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise RuntimeError('injected witness failure')
        return real_witness_map(*args, **kwargs)
    monkeypatch.setattr(assemble_module, '_witness_map', exploding_witness_map)
    monkeypatch.setattr(constructive_module, '_witness_map', exploding_witness_map)
    fact_type = next(ft for ft in model.fact_types if ft['id'] == 'cover_matches_slot')
    with pytest.raises(RuntimeError, match='injected witness failure'):
        builder._mandatory_completion(fact_type, {'cover': row['cover']}, 'fact_types[cover_matches_slot].constraints[2]')
    assert builder.facts == before

def test_nonjoining_rows_do_not_spend_external_search_cap(monkeypatch):
    model = _model('external-single')
    builder = _builder(model)
    builder.construct()
    scenario_rows = builder.facts['link_for_group']
    cell_rows = builder.facts['link_of_slot']
    for row in scenario_rows:
        row['group'] = builder.work['group'][0]
    for row in cell_rows:
        row['slot'] = builder.work['slot'][0]
    scenario_rows.extend({'link': f'nonjoining-{index}', 'group': builder.work['group'][0]} for index in range(20))
    monkeypatch.setattr(constructive_module, '_EXTERNAL_UNIQUENESS_SEARCH_CAP', 30)
    builder._coordinate_external_uniqueness()
    doc = {'facts': builder.facts, 'instances': {}}
    constraint = model.constraints[0]
    assert assemble_module._witness(constraint, None, doc, model, builder.children) is True

def test_external_domain_exhaustion_names_constraint_and_reason():
    with pytest.raises(GeneratorError) as caught:
        assemble_conforming(_model('external-exhausted'), 12, model_ref='external-exhausted.orm.yaml')
    message = str(caught.value)
    assert 'constraints[0]' in message
    assert 'external-uniqueness-domain-exhausted' in message
    assert 'repair oscillated' not in message

def test_mandatory_domain_exhaustion_names_constraint_and_reason():
    with pytest.raises(GeneratorError) as caught:
        assemble_conforming(_model('mandatory-exhausted'), 12, model_ref='mandatory-exhausted.orm.yaml')
    message = str(caught.value)
    assert 'fact_types[card_matches_slot].constraints[2]' in message
    assert 'mandatory-uniqueness-domain-exhausted' in message
    assert 'repair oscillated' not in message

def test_external_search_cap_has_distinct_reason(monkeypatch):
    monkeypatch.setattr(constructive_module, '_EXTERNAL_UNIQUENESS_SEARCH_CAP', 1, raising=False)
    with pytest.raises(GeneratorError, match='external-uniqueness-search-cap') as caught:
        assemble_conforming(_model('external-pair'), 12, model_ref='external-pair.orm.yaml')
    message = str(caught.value)
    assert 'constraints[0], constraints[1]' in message
    assert 'after 1 candidate assignments' in message

def test_mixed_false_fail_quarantines_before_repair(monkeypatch):
    model = load_model(str(ROOT / 'tests' / 'fixtures' / 'checker' / 'setfam.orm.yaml'))
    real_check = assemble_module.check
    real_witness_map = assemble_module._witness_map
    targets = ['fact_types[booking_by_person].constraints[0]', 'fact_types[booking_of_room].constraints[0]']

    def mixed_check(model_arg, population):
        report = real_check(model_arg, population)
        verdicts = [verdict.model_copy(update={'verdict': 'fail', 'scope_id': 'snapshot:uniqueness:inline:violated:alethic'}) if verdict.constraint_ref in targets else verdict for verdict in report.verdicts]
        return CheckReport(verdicts=verdicts, coverage=report.coverage)

    def mixed_witnesses(*args, **kwargs):
        witnesses = real_witness_map(*args, **kwargs)
        witnesses[targets[0]] = False
        return witnesses
    monkeypatch.setattr(assemble_module, 'check', mixed_check)
    monkeypatch.setattr(assemble_module, '_witness_map', mixed_witnesses)
    monkeypatch.setattr(constructive_module, '_witness_map', mixed_witnesses)
    monkeypatch.setattr(assemble_module, '_repair', lambda *_args: pytest.fail('repair ran before checker disagreement quarantine'))
    with pytest.raises(CheckerWitnessDiscrepancy):
        assemble_conforming(model, 1, model_ref='setfam.orm.yaml')

def test_mixed_false_pass_quarantines_before_repair(monkeypatch):
    model = load_model(str(ROOT / 'tests' / 'fixtures' / 'checker' / 'setfam.orm.yaml'))
    real_check = assemble_module.check
    real_witness_map = assemble_module._witness_map
    targets = ['fact_types[booking_by_person].constraints[0]', 'fact_types[booking_by_person].constraints[1]']

    def mixed_check(model_arg, population):
        report = real_check(model_arg, population)
        verdicts = [verdict.model_copy(update={'verdict': 'fail', 'scope_id': 'snapshot:uniqueness:inline:violated:alethic'}) if verdict.constraint_ref == targets[0] else verdict for verdict in report.verdicts]
        return CheckReport(verdicts=verdicts, coverage=report.coverage)

    def mixed_witnesses(*args, **kwargs):
        witnesses = real_witness_map(*args, **kwargs)
        witnesses.update(dict.fromkeys(targets, False))
        return witnesses
    monkeypatch.setattr(assemble_module, 'check', mixed_check)
    monkeypatch.setattr(assemble_module, '_witness_map', mixed_witnesses)
    monkeypatch.setattr(constructive_module, '_witness_map', mixed_witnesses)
    monkeypatch.setattr(assemble_module, '_repair', lambda *_args: pytest.fail('repair ran before checker disagreement quarantine'))
    with pytest.raises(CheckerWitnessDiscrepancy):
        assemble_conforming(model, 1, model_ref='setfam.orm.yaml')

def test_unrelated_generic_repair_oscillation_remains_available(monkeypatch):
    model = load_model(str(ROOT / 'tests' / 'fixtures' / 'checker' / 'setfam.orm.yaml'))
    real_doc = assemble_module._Builder.doc

    def duplicate_row(self, model_ref):
        doc = real_doc(self, model_ref)
        rows = doc['facts']['booking_by_person']
        rows.append(dict(rows[0]))
        return doc
    monkeypatch.setattr(assemble_module._Builder, 'doc', duplicate_row)
    monkeypatch.setattr(assemble_module, '_repair', lambda *_args: None)
    with pytest.raises(GeneratorError, match='repair oscillated'):
        assemble_conforming(model, 1, model_ref='setfam.orm.yaml')

def test_class_all_then_measure_uses_the_requested_seed(tmp_path):
    model_path = CORPUS / 'external-pair.orm.yaml'
    out = tmp_path / 'corpus'
    assert main(['synth', str(model_path), '--out', str(out), '--class', 'all', '--seed', '12']) == 0
    assert main(['measure', str(model_path), '--populations', str(out), '--format', 'json', '--out', str(tmp_path / 'measure.json')]) == 0
