from __future__ import annotations

EXPECTED = {'P2-111': (1, []), 'P2-112': (0, [['9/1', '3/1']]), 'P2-113': (0, [['9/1', '3/1']]), 'P2-114': (-1, []), 'P2-115': (1, []), 'P2-116': (0, [['150/1', '100/1']]), 'P2-117': (0, [['150/1', '100/1']]), 'P2-118': (1, []), 'P2-119': (0, [['-1/1', '0/1']]), 'P2-120': (-1, []), 'P2-121': (-1, []), 'P2-122': (-1, []), 'P2-123': (1, []), 'P2-124': (0, [['2026-01-01T12:00:00Z', '2026-01-01T10:00:00Z']]), 'P2-125': (0, [['2026-01-01T12:00:00Z', '2026-01-01T10:00:00Z']]), 'P2-126': (-1, []), 'P2-127': (1, []), 'P2-128': (0, [['2026-05-01', '2026-04-01']]), 'P2-129': (0, [['2026-05-01', '2026-04-01']]), 'P2-130': (-1, [])}
import ast
import dataclasses
import runpy
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
from support import comparison_cases as corpus

from gnd import semantic_spec as spec
from gnd.semantic_adapter import adapt_snapshot, canonical_scalar


def _case(case_id: str, tmp_path: Path):
    model, population = corpus._build(case_id, tmp_path)
    snapshot = adapt_snapshot(model, population)
    reference = corpus.CASE_BY_ID[case_id]['ref']
    return (next(row for row in snapshot.constraints if row.ref == reference), snapshot)

def test_all_six_operators_and_total_identity() -> None:
    one = canonical_scalar(1, None)
    one_float = canonical_scalar(1.0, None)
    two = canonical_scalar(2, None)
    text = canonical_scalar('1', None)
    assert one is not None and one_float is not None and (two is not None) and (text is not None)
    assert spec.comparison_pair_state(one, two, '<') == 1
    assert spec.comparison_pair_state(one, one_float, '<=') == 1
    assert spec.comparison_pair_state(one, one_float, '=') == 1
    assert spec.comparison_pair_state(two, one, '>=') == 1
    assert spec.comparison_pair_state(two, one, '>') == 1
    assert spec.comparison_pair_state(one, text, '!=') == 1
    assert spec.comparison_pair_state(one, text, '=') == 0
    assert spec.comparison_pair_state(one, text, '<') == -1

@pytest.mark.parametrize('operator,left_value,right_value', [('<', 1, 2), ('<=', 1, 1), ('=', 1, 1), ('>=', 1, 1), ('>', 2, 1), ('!=', 1, 2)])
def test_each_operator_has_a_one_change_counterexample(operator: str, left_value: int, right_value: int, tmp_path: Path) -> None:
    left = canonical_scalar(left_value, None)
    right = canonical_scalar(right_value, None)
    assert left is not None and right is not None
    mutant = _mutant(tmp_path, 'comparison_pair_state', f'if operator == "{operator}":', 'if operator == "unknown":')
    assert spec.comparison_pair_state(left, right, operator) == 1
    assert mutant['comparison_pair_state'](left, right, operator) != 1

def test_incomparable_pair_outranks_a_concrete_violation(tmp_path: Path) -> None:
    constraint, snapshot = _case('P2-112', tmp_path)
    position = spec.snapshot_relation_index(snapshot, constraint.fact_type)
    relation = snapshot.relations[position]
    unknown = canonical_scalar('unknown', None)
    assert unknown is not None
    rows = relation.rows + ((relation.rows[0][0], unknown, unknown),)
    relations = list(snapshot.relations)
    relations[position] = dataclasses.replace(relation, rows=rows)
    mixed = dataclasses.replace(snapshot, relations=tuple(relations))
    assert spec.value_comparison_result(constraint, mixed) == (-1, [])

def test_resolution_and_variant_shape_fail_closed(tmp_path: Path) -> None:
    constraint, snapshot = _case('P2-111', tmp_path)
    assert spec.value_comparison_state(dataclasses.replace(constraint, variant='inline-literal'), snapshot) == -1
    assert spec.value_comparison_state(dataclasses.replace(constraint, operator='unknown'), snapshot) == -1
    missing = dataclasses.replace(snapshot, relations=tuple(row for row in snapshot.relations if row.fact_type != constraint.fact_type))
    assert spec.value_comparison_state(constraint, missing) == -1

def test_duplicate_violations_collapse_and_output_is_canonical(tmp_path: Path) -> None:
    constraint, snapshot = _case('P2-112', tmp_path)
    position = spec.snapshot_relation_index(snapshot, constraint.fact_type)
    relation = snapshot.relations[position]
    first = relation.rows[0]
    low = dataclasses.replace(first[1], token='10/1', num=10)
    high = dataclasses.replace(first[2], token='1/1', num=1)
    second = (first[0], low, high)
    relations = list(snapshot.relations)
    relations[position] = dataclasses.replace(relation, rows=(second, first, second))
    changed = dataclasses.replace(snapshot, relations=tuple(relations))
    witness = spec.value_comparison_witness(constraint, changed)
    assert [[value.token for value in row] for row in witness] == [['9/1', '3/1'], ['10/1', '1/1']]
    duplicate_mutant = _mutant(tmp_path, 'value_comparison_result', 'witness = canonical_distinct_rows(violations)', 'witness = violations')
    assert duplicate_mutant['value_comparison_witness'](constraint, changed) != witness
    order_mutant = _mutant(tmp_path, 'value_comparison_result', 'witness = canonical_distinct_rows(violations)', 'witness = list(reversed(canonical_distinct_rows(violations)))')
    assert order_mutant['value_comparison_witness'](constraint, changed) != witness

def _mutant(tmp_path: Path, function: str, before: str, after: str):
    source = Path(spec.__file__).read_text()
    node = next(item for item in ast.parse(source).body if isinstance(item, ast.FunctionDef) and item.name == function)
    segment = ast.get_source_segment(source, node)
    assert segment is not None and segment.count(before) == 1
    lines = source.splitlines(keepends=True)
    start = sum(len(line) for line in lines[:node.lineno - 1])
    end = sum(len(line) for line in lines[:node.end_lineno])
    path = tmp_path / 'comparison_mutant.py'
    path.write_text(source[:start] + segment.replace(before, after) + source[end:])
    return runpy.run_path(str(path))

@pytest.mark.parametrize('case_id', tuple(EXPECTED))
def test_frozen_value_comparison_cases(case_id: str, tmp_path: Path) -> None:
    constraint, snapshot = _case(case_id, tmp_path)
    state, witness = EXPECTED[case_id]
    before = hash(snapshot)
    assert spec.value_comparison_state(constraint, snapshot) == state
    assert spec.value_comparison_holds(constraint, snapshot) is (state == 1)
    actual = spec.value_comparison_witness(constraint, snapshot)
    assert [[value.token for value in row] for row in actual] == witness
    assert hash(snapshot) == before

@pytest.mark.parametrize('case_id,function,before,after', [('P2-112', 'comparison_pair_state', 'if operator == "<=":', 'if operator == "<":'), ('P2-112', 'value_comparison_pairs', 'columns.append(column)', 'columns.append(0)'), ('P2-116', 'value_comparison_pairs', 'values.append(operand.literal)', 'values.append(relation.rows[row_index][0])'), ('P2-128', 'value_comparison_pairs', '((first.fact_type, first.role), (second.fact_type, second.role)), snapshot', '((second.fact_type, second.role), (first.fact_type, first.role)), snapshot'), ('P2-114', 'value_comparison_result', 'if undecidable:\n        return -1, empty', 'if False:\n        return -1, empty'), ('P2-112', 'value_comparison_result', 'witness = canonical_distinct_rows(violations)', 'witness = []')], ids=['operator-boundary', 'role-column', 'literal-selection', 'join-direction', 'unknown-priority', 'witness-omission'])
def test_value_comparison_mutations_have_counterexamples(case_id: str, function: str, before: str, after: str, tmp_path: Path) -> None:
    constraint, snapshot = _case(case_id, tmp_path)
    mutant = _mutant(tmp_path, function, before, after)
    assert mutant['value_comparison_result'](constraint, snapshot) != spec.value_comparison_result(constraint, snapshot)
