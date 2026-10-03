from __future__ import annotations

import ast
import dataclasses
import runpy
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
from support import counting_cases as corpus

from gnd import semantic_spec as spec
from gnd.semantic_adapter import adapt_snapshot, canonical_scalar


def _frozen(case_id: str, tmp_path: Path):
    model, population = corpus._build(case_id, tmp_path)
    snapshot = adapt_snapshot(model, population)
    reference = corpus.CASE_BY_ID[case_id]['ref']
    return (next(row for row in snapshot.constraints if row.ref == reference), snapshot)

def _scalar(value: object):
    result = canonical_scalar(value, None)
    assert result is not None
    return result

def test_integral_bound_states_include_zero_and_reject_malformed_values() -> None:
    zero, one, two = (_scalar(value) for value in (0, 1, 2))
    assert spec.count_interval_state(0, one, None) == 0
    assert spec.count_interval_state(1, one, two) == 1
    assert spec.count_interval_state(3, None, two) == 0
    assert spec.count_interval_state(0, None, None) == 1
    assert spec.count_interval_state(0, two, one) == -1
    assert spec.count_interval_state(0, dataclasses.replace(zero, den=2, num=1), None) == -1
    assert spec.count_interval_state(0, _scalar('1'), None) == -1

def test_frequency_minimum_does_not_create_an_absent_group(tmp_path: Path) -> None:
    constraint, snapshot = _frozen('P2-039', tmp_path)
    relation = next(row for row in snapshot.relations if row.fact_type == constraint.fact_type)
    empty = dataclasses.replace(snapshot, relations=tuple(dataclasses.replace(row, rows=()) if row is relation else row for row in snapshot.relations))
    assert constraint.minimum is not None
    assert spec.frequency_state(constraint, empty) == 1
    assert spec.frequency_witness(constraint, empty) == []

@pytest.mark.parametrize('kind', ['fact', 'role', 'relation', 'coverage', 'row', 'cell', 'refusal'])
def test_internal_counting_resolution_boundaries_are_unchecked(tmp_path: Path, kind: str) -> None:
    constraint, snapshot = _frozen('P2-001', tmp_path)
    fact_index = next((i for i, row in enumerate(snapshot.fact_types) if row.id == constraint.fact_type))
    relation_index = next((i for i, row in enumerate(snapshot.relations) if row.fact_type == constraint.fact_type))
    if kind == 'fact':
        snapshot = dataclasses.replace(snapshot, fact_types=snapshot.fact_types[:fact_index] + snapshot.fact_types[fact_index + 1:])
    elif kind == 'role':
        constraint = dataclasses.replace(constraint, roles=('absent',))
    elif kind == 'relation':
        snapshot = dataclasses.replace(snapshot, relations=snapshot.relations[:relation_index] + snapshot.relations[relation_index + 1:])
    elif kind == 'coverage':
        snapshot = dataclasses.replace(snapshot, covers=tuple(value for value in snapshot.covers if value != constraint.fact_type))
    elif kind == 'row':
        rows = snapshot.relations[relation_index].rows + ((),)
        relations = list(snapshot.relations)
        relations[relation_index] = dataclasses.replace(relations[relation_index], rows=rows)
        snapshot = dataclasses.replace(snapshot, relations=tuple(relations))
    elif kind == 'cell':
        rows = list(snapshot.relations[relation_index].rows)
        rows[0] = (None, *rows[0][1:])
        relations = list(snapshot.relations)
        relations[relation_index] = dataclasses.replace(relations[relation_index], rows=tuple(rows))
        snapshot = dataclasses.replace(snapshot, relations=tuple(relations))
    else:
        constraint = dataclasses.replace(constraint, refused='malformed-constraint')
    assert spec.uniqueness_state(constraint, snapshot) == -1
    assert spec.uniqueness_witness(constraint, snapshot) == []

def _mutated_namespace(tmp_path: Path, function: str, before: str, after: str):
    source = Path(spec.__file__).read_text()
    target = next(node for node in ast.parse(source).body if isinstance(node, ast.FunctionDef) and node.name == function)
    segment = ast.get_source_segment(source, target)
    assert segment is not None and segment.count(before) == 1
    lines = source.splitlines(keepends=True)
    start = sum(len(line) for line in lines[:target.lineno - 1])
    end = sum(len(line) for line in lines[:target.end_lineno])
    path = tmp_path / (function + '_mutant.py')
    path.write_text(source[:start] + segment.replace(before, after) + source[end:])
    return runpy.run_path(str(path))

def test_uniqueness_duplicate_threshold_mutation_has_counterexample(tmp_path: Path) -> None:
    constraint, snapshot = _frozen('P2-002', tmp_path)
    mutant = _mutated_namespace(tmp_path, 'uniqueness_result', 'if count >= 2:', 'if count >= 3:')
    assert spec.uniqueness_state(constraint, snapshot) == 0
    assert mutant['uniqueness_state'](constraint, snapshot) == 1

def test_frequency_deduplication_mutation_has_counterexample(tmp_path: Path) -> None:
    constraint, snapshot = _frozen('P2-040', tmp_path)
    mutant = _mutated_namespace(tmp_path, 'frequency_result', 'while row_index < len(keys):', 'while row_index < len(groups):')
    assert spec.frequency_state(constraint, snapshot) == 0
    assert mutant['frequency_state'](constraint, snapshot) == 1

def test_cardinality_occurrence_count_mutation_has_counterexample(tmp_path: Path) -> None:
    constraint, snapshot = _frozen('P2-134', tmp_path)
    relation_index = next((i for i, row in enumerate(snapshot.relations) if row.fact_type == constraint.role_refs[0][0]))
    rows = snapshot.relations[relation_index].rows
    relations = list(snapshot.relations)
    relations[relation_index] = dataclasses.replace(relations[relation_index], rows=rows + rows + rows)
    duplicated = dataclasses.replace(snapshot, relations=tuple(relations))
    mutant = _mutated_namespace(tmp_path, 'cardinality_result', 'distinct = canonical_distinct_rows(rows)', 'distinct = rows')
    assert spec.cardinality_state(constraint, duplicated) == 1
    assert mutant['cardinality_state'](constraint, duplicated) == 0
