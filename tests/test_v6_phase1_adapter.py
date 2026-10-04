from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from gnd import proof_bridge
from gnd.address import positional_constraint_ref
from gnd.model import load_model
from gnd.population import load_population
from gnd.proof_kernel import SliceGroup, SliceInput, admit_phase1_slice, phase1_decide

REPO_ROOT = Path(__file__).resolve().parents[1]
CORPUS = REPO_ROOT / 'tests/fixtures/public-bridge'
CASES = {'cases': [{'id': 'C01', 'model': 'fixtures/c01/model.orm.yaml', 'population': 'fixtures/c01/population.yaml'}, {'id': 'C02', 'model': 'fixtures/c02/model.orm.yaml', 'population': 'fixtures/c02/population.yaml'}, {'id': 'C04', 'model': 'fixtures/c04/model.orm.yaml', 'population': 'fixtures/c04/population.yaml'}, {'id': 'C06', 'model': 'fixtures/c06/model.orm.yaml', 'population': 'fixtures/c06/population.yaml'}, {'id': 'C07', 'model': 'fixtures/c07/model.orm.yaml', 'population': 'fixtures/c07/population.yaml'}]}
CASE_BY_ID = {row['id']: row for row in CASES['cases']}

def _adapt(case_id: str, constraint_index: int=0) -> tuple[Any, ...]:
    row = CASE_BY_ID[case_id]
    model = load_model(CORPUS / row['model'])
    population = load_population(CORPUS / row['population'], model=model)
    declared: list[tuple[dict[str, Any], str, dict[str, Any] | None]] = []
    for fact_type in model.fact_types:
        for index, constraint in enumerate(fact_type.get('constraints') or []):
            declared.append((constraint, positional_constraint_ref(str(fact_type.get('id')), index), fact_type))
    for index, constraint in enumerate(model.constraints):
        declared.append((constraint, positional_constraint_ref(None, index), None))
    constraint, ref, fact_type = declared[constraint_index]
    return (model, population, constraint, ref, fact_type)

def _slice_of(case_id: str, constraint_index: int=0) -> SliceInput:
    model, population, constraint, ref, fact_type = _adapt(case_id, constraint_index)
    value = proof_bridge.adapt_phase1_slice(model, population, constraint, fact_type, ref)
    assert value is not None, f'{case_id} {ref} is inside the slice'
    return value

def test_covers_reaches_the_admitted_value_exactly() -> None:
    assert _slice_of('C01').covered is True
    assert _slice_of('C04').covered is False

def test_canonical_order_is_ascending_and_observable_at_the_bridge() -> None:
    value = _slice_of('C02')
    assert value.universe == tuple(sorted(value.universe))
    assert len(value.universe) == 2, 'C02 must keep two universe members'
    verdict = phase1_decide(value)
    assert verdict is not None
    assert verdict.witness == tuple(sorted(verdict.witness))

def test_m12_reordering_the_canonicalization_moves_the_bridge_output() -> None:
    baseline = _slice_of('C02')
    original = proof_bridge._canonical
    try:
        proof_bridge._canonical = lambda values: tuple(sorted(set(values), reverse=True))
        mutated = _slice_of('C02')
    finally:
        proof_bridge._canonical = original
    assert mutated is not None, 'order is not admission-refusable, by the carve-out'
    assert mutated.universe == tuple(reversed(baseline.universe))
    assert mutated.universe != baseline.universe

def test_multiplicity_reaches_the_groups_exactly() -> None:
    model, population, constraint, ref, fact_type = _adapt('C07')
    value = proof_bridge.adapt_phase1_slice(model, population, constraint, fact_type, ref)
    assert value is not None
    role = constraint['roles'][0]
    spelled: dict[str, int] = {}
    for fact in population.facts[str(fact_type['id'])]:
        spelled[fact[role]] = spelled.get(fact[role], 0) + 1
    assert {group.key[0]: group.count for group in value.groups} == spelled
    assert sum(spelled.values()) > len(spelled), 'C07 must exercise a real multiplicity'

def test_the_roster_and_identity_fields_survive_the_bridge() -> None:
    value = _slice_of('C02')
    model_text = (CORPUS / CASE_BY_ID['C02']['model']).read_text(encoding='utf-8')
    population_text = (CORPUS / CASE_BY_ID['C02']['population']).read_text(encoding='utf-8')
    for member in value.universe:
        assert member in model_text + population_text
    for player in value.players:
        assert player in population_text

def test_a_nonstring_identity_refuses_the_whole_slice() -> None:
    model, population, constraint, ref, fact_type = _adapt('C07')
    role = constraint['roles'][0]
    fact_type_id = str(fact_type['id'])
    population.facts[fact_type_id][0][role] = 7
    assert proof_bridge.adapt_phase1_slice(model, population, constraint, fact_type, ref) is None

def test_bounds_reach_the_admitted_value_exactly() -> None:
    model, population, constraint, ref, fact_type = _adapt('C06')
    value = proof_bridge.adapt_phase1_slice(model, population, constraint, fact_type, ref)
    assert value is not None
    assert value.minimum == constraint['bound'].get('min')
    assert value.maximum == constraint['bound'].get('max')

def _frequency_candidate(groups: tuple[SliceGroup, ...]) -> SliceInput:
    return SliceInput('constraints[0]', 'frequency', 'alethic', True, True, (), (), groups, 1, None)

@pytest.mark.parametrize(('description', 'candidate', 'universe', 'players', 'roles'), [('a dropped universe member', SliceInput('c', 'mandatory', 'alethic', True, True, ('a1',), (), (), None, None), ('a1', 'b2'), (), ()), ('an invented universe member', SliceInput('c', 'mandatory', 'alethic', True, True, ('a1', 'b2'), (), (), None, None), ('a1',), (), ()), ('a duplicated identity', SliceInput('c', 'mandatory', 'alethic', True, True, ('a1', 'a1'), (), (), None, None), ('a1',), (), ()), ('a dropped player', SliceInput('c', 'mandatory', 'alethic', True, True, ('a1', 'b2'), (), (), None, None), ('a1', 'b2'), ('a1',), ()), ('a deduplicated occurrence count', _frequency_candidate((SliceGroup(('p1',), 1),)), (), (), ('p1', 'p1')), ('a dropped group', _frequency_candidate((SliceGroup(('p1',), 2),)), (), (), ('p1', 'p1', 'q2')), ('an invented occurring group', _frequency_candidate((SliceGroup(('p1',), 2), SliceGroup(('z9',), 2))), (), (), ('p1', 'p1')), ('an invented zero-count group', _frequency_candidate((SliceGroup(('p1',), 2), SliceGroup(('z9',), 0))), (), (), ('p1', 'p1'))])
def test_the_admission_gate_refuses_a_lying_canonicalization(description: str, candidate: SliceInput, universe: tuple[str, ...], players: tuple[str, ...], roles: tuple[str, ...]) -> None:
    assert admit_phase1_slice(candidate, universe, players, roles) is None, description

def test_an_oversize_observation_is_refused_without_exception() -> None:
    raw = ('p1',) * 1100
    candidate = SliceInput('c', 'frequency', 'alethic', True, True, (), (), (SliceGroup(('p1',), 1100),), 1, None)
    assert admit_phase1_slice(candidate, (), (), raw) is None
