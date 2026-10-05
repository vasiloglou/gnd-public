from __future__ import annotations

import ast
import dataclasses
import runpy
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
from support import ring_cases as corpus

from gnd import semantic_spec as spec
from gnd.semantic_adapter import adapt_snapshot


def _case(case_id: str, tmp_path: Path):
    model, population = corpus._build(case_id, tmp_path)
    snapshot = adapt_snapshot(model, population)
    reference = corpus.CASE_BY_ID[case_id]['ref']
    return (next(row for row in snapshot.constraints if row.ref == reference), snapshot)
EXPECTED = {'P2-045': (1, []), 'P2-046': (0, [['1/1', '1/1']]), 'P2-047': (0, [['1/1', '1/1']]), 'P2-048': (1, []), 'P2-049': (0, [['1/1', '2/1'], ['2/1', '1/1']]), 'P2-050': (0, [['1/1', '2/1'], ['2/1', '1/1']]), 'P2-051': (1, []), 'P2-052': (0, [['1/1', '2/1', '3/1']]), 'P2-053': (0, [['1/1', '2/1', '3/1']]), 'P2-054': (1, []), 'P2-055': (0, [['1/1', '2/1'], ['2/1', '1/1']]), 'P2-056': (0, [['1/1', '2/1'], ['2/1', '1/1']]), 'P2-057': (1, []), 'P2-058': (0, [['1/1', '2/1', '3/1', '1/1']]), 'P2-059': (0, [['1/1', '2/1', '3/1', '1/1']]), 'P2-060': (1, []), 'P2-061': (0, [['1/1', '2/1'], ['2/1', '1/1']]), 'P2-062': (0, [['1/1', '2/1'], ['2/1', '1/1']]), 'P2-063': (1, []), 'P2-064': (0, [['1/1', '2/1', '3/1']]), 'P2-065': (0, [['1/1', '2/1', '3/1']]), 'P2-066': (1, []), 'P2-067': (0, [['1/1', '2/1']]), 'P2-068': (0, [['1/1', '2/1']]), 'P2-069': (1, []), 'P2-070': (0, [['1/1', '1/1']]), 'P2-071': (0, [['1/1', '1/1']]), 'P2-072': (1, []), 'P2-073': (0, [['1/1', '2/1']]), 'P2-074': (0, [['1/1', '2/1']]), 'P2-075': (1, []), 'P2-076': (0, [['1/1', '2/1']]), 'P2-077': (0, [['1/1', '2/1']]), 'P2-078': (1, []), 'P2-079': (0, [['1/1']]), 'P2-080': (0, [['1/1']]), 'P2-081': (1, []), 'P2-082': (0, [['1/1', '2/1', '3/1']]), 'P2-083': (0, [['1/1', '2/1', '3/1']]), 'P2-084': (1, []), 'P2-085': (-1, [])}

@pytest.mark.parametrize('case_id', tuple(EXPECTED))
def test_frozen_ring_cases_match_active_clauses(case_id: str, tmp_path: Path) -> None:
    constraint, snapshot = _case(case_id, tmp_path)
    state, witness = EXPECTED[case_id]
    before = hash(snapshot)
    assert spec.ring_state(constraint, snapshot) == state
    assert spec.ring_holds(constraint, snapshot) is (state == 1)
    actual = spec.ring_witness(constraint, snapshot)
    assert [[value.token for value in row] for row in actual] == witness
    assert hash(snapshot) == before

def _with_rows(constraint, snapshot, rows):
    position = spec.snapshot_relation_index(snapshot, constraint.fact_type)
    relations = list(snapshot.relations)
    relations[position] = dataclasses.replace(relations[position], rows=tuple(rows))
    return dataclasses.replace(snapshot, relations=tuple(relations))

def test_duplicate_facts_collapse_at_pair_set_formation(tmp_path: Path) -> None:
    constraint, snapshot = _case('P2-046', tmp_path)
    position = spec.snapshot_relation_index(snapshot, constraint.fact_type)
    row = snapshot.relations[position].rows[0]
    duplicated = _with_rows(constraint, snapshot, (row, row, row))
    assert spec.ring_result(constraint, duplicated) == spec.ring_result(constraint, snapshot)
    mutant = _mutant(tmp_path, 'ring_result', 'pairs = canonical_distinct_rows(source_pairs)', 'pairs = source_pairs')
    assert mutant['ring_result'](constraint, duplicated) != spec.ring_result(constraint, duplicated)

def test_ring_pair_input_is_canonicalized_before_component_evaluation(tmp_path: Path) -> None:
    constraint, snapshot = _case('P2-049', tmp_path)
    position = spec.snapshot_relation_index(snapshot, constraint.fact_type)
    rows = tuple(reversed(snapshot.relations[position].rows))
    reversed_input = _with_rows(constraint, snapshot, rows)
    expected = spec.ring_witness(constraint, snapshot)
    assert spec.ring_witness(constraint, reversed_input) == expected
    mutant = _mutant(tmp_path, 'ring_result', 'pairs = canonical_distinct_rows(source_pairs)', 'pairs = source_pairs')
    assert mutant['ring_witness'](constraint, reversed_input) != expected

def test_combined_variant_retains_both_components_in_order(tmp_path: Path) -> None:
    constraint, snapshot = _case('P2-060', tmp_path)
    position = spec.snapshot_relation_index(snapshot, constraint.fact_type)
    one = snapshot.relations[position].rows[0][0]
    assert one is not None
    both = _with_rows(constraint, snapshot, ((one, one),))
    witness = spec.ring_witness(constraint, both)
    assert [[value.token for value in row] for row in witness] == [['1/1', '1/1'], ['1/1', '1/1', '1/1']]
    mutant = _mutant(tmp_path, 'ring_result', 'while component_index < len(components):', 'while component_index < len(components) - 1:')
    assert mutant['ring_witness'](constraint, both) != witness

def test_local_reflexivity_does_not_quantify_over_range(tmp_path: Path) -> None:
    constraint, snapshot = _case('P2-084', tmp_path)
    assert spec.ring_state(constraint, snapshot) == 1
    mutant = _mutant(tmp_path, 'ring_component_witness', 'domain_values.append(pairs[pair_index][0])', 'domain_values.append(pairs[pair_index][0])\n            domain_values.append(pairs[pair_index][1])')
    position = spec.snapshot_relation_index(snapshot, constraint.fact_type)
    pairs = spec.canonical_distinct_rows([(row[0], row[1]) for row in snapshot.relations[position].rows if row[0] and row[1]])
    assert mutant['ring_component_witness']('reflexive', pairs) != []

def test_cycle_witness_follows_relation_direction(tmp_path: Path) -> None:
    constraint, snapshot = _case('P2-058', tmp_path)
    expected = spec.ring_witness(constraint, snapshot)
    mutant = _mutant(tmp_path, 'ring_cycle_witness', 'index = len(indexes) - 1', 'index = 0')
    position = spec.snapshot_relation_index(snapshot, constraint.fact_type)
    pairs = spec.canonical_distinct_rows([(row[0], row[1]) for row in snapshot.relations[position].rows if row[0] is not None and row[1] is not None])
    assert [mutant['ring_cycle_witness'](pairs)] != expected

def test_ring_membership_uses_identity_kind_as_well_as_token(tmp_path: Path) -> None:
    constraint, snapshot = _case('P2-067', tmp_path)
    position = spec.snapshot_relation_index(snapshot, constraint.fact_type)
    left, right = snapshot.relations[position].rows[0]
    assert left is not None and right is not None
    false_reverse = (dataclasses.replace(right, identity_kind='string'), dataclasses.replace(left, identity_kind='string'))
    changed = _with_rows(constraint, snapshot, (snapshot.relations[position].rows[0], false_reverse))
    assert spec.ring_state(constraint, changed) == 0
    mutant = _mutant(tmp_path, 'ring_pair_member', 'return row_list_member(pair, pairs)', 'return any(len(item) == len(pair) and all(a.token == b.token for a, b in zip(item, pair)) for item in pairs)')
    assert mutant['ring_state'](constraint, changed) == 1

@pytest.mark.parametrize('case_id,function,before,after', [('P2-046', 'ring_component_witness', '(component == "irreflexive" and same)', '(component == "irreflexive" and not same)'), ('P2-049', 'ring_component_witness', '(component == "asymmetric" and reverse)', '(component == "asymmetric" and not reverse)'), ('P2-055', 'ring_component_witness', '(component == "antisymmetric" and not same and reverse)', '(component == "antisymmetric" and same and reverse)'), ('P2-067', 'ring_component_witness', '(component == "symmetric" and not reverse)', '(component == "symmetric" and reverse)'), ('P2-076', 'ring_component_witness', '(component == "purely-reflexive" and not same)', '(component == "purely-reflexive" and same)'), ('P2-052', 'ring_component_witness', '(component == "intransitive" and closing)', '(component == "intransitive" and not closing)'), ('P2-082', 'ring_component_witness', 'component == "transitive" and not closing', 'component == "transitive" and closing'), ('P2-079', 'ring_component_witness', 'if not ring_pair_member((domain[node_index], domain[node_index]), pairs):', 'if False:'), ('P2-058', 'ring_component_witness', 'if cycle:', 'if False:')], ids=['irreflexive', 'asymmetric', 'antisymmetric', 'symmetric', 'purely-reflexive', 'intransitive', 'transitive', 'reflexive', 'acyclic'])
def test_each_primitive_ring_mutation_has_a_counterexample(case_id: str, function: str, before: str, after: str, tmp_path: Path) -> None:
    constraint, snapshot = _case(case_id, tmp_path)
    mutant = _mutant(tmp_path, function, before, after)
    assert mutant['ring_result'](constraint, snapshot) != spec.ring_result(constraint, snapshot)

def _mutant(tmp_path: Path, function: str, before: str, after: str):
    source = Path(spec.__file__).read_text()
    node = next(item for item in ast.parse(source).body if isinstance(item, ast.FunctionDef) and item.name == function)
    segment = ast.get_source_segment(source, node)
    assert segment is not None and segment.count(before) == 1
    lines = source.splitlines(keepends=True)
    start = sum(len(line) for line in lines[:node.lineno - 1])
    end = sum(len(line) for line in lines[:node.end_lineno])
    path = tmp_path / 'ring_mutant.py'
    path.write_text(source[:start] + segment.replace(before, after) + source[end:])
    return runpy.run_path(str(path))
