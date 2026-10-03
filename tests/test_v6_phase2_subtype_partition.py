from __future__ import annotations

import ast
import dataclasses
import runpy
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
from support import partition_cases as corpus

from gnd import semantic_spec as spec
from gnd.semantic_adapter import adapt_snapshot


def _case(case_id: str, tmp_path: Path):
    model, population = corpus._build(case_id, tmp_path)
    snapshot = adapt_snapshot(model, population)
    reference = corpus.CASE_BY_ID[case_id]['ref']
    return (next(row for row in snapshot.constraints if row.ref == reference), snapshot)
EXPECTED = {'P2-137': (1, []), 'P2-138': (0, [['carol']]), 'P2-139': (0, [['carol']]), 'P2-140': (1, []), 'P2-141': (0, [['dave']]), 'P2-142': (0, [['dave']]), 'P2-143': (1, []), 'P2-144': (0, [['30/1'], ['3/1'], ['20/1']]), 'P2-145': (0, [['30/1'], ['3/1'], ['20/1']]), 'P2-146': (1, []), 'P2-147': (1, []), 'P2-148': (0, [['bob']]), 'P2-149': (-1, []), 'P2-150': (-1, [])}

@pytest.mark.parametrize('case_id', tuple(EXPECTED))
def test_frozen_partition_cases_match_governing_clauses(tmp_path: Path, case_id: str) -> None:
    constraint, snapshot = _case(case_id, tmp_path)
    state, witness = EXPECTED[case_id]
    before = hash(snapshot)
    assert spec.subtype_partition_state(constraint, snapshot) == state
    assert spec.subtype_partition_holds(constraint, snapshot) is (state == 1)
    actual = spec.subtype_partition_witness(constraint, snapshot)
    assert [[value.token for value in row] for row in actual] == witness
    assert hash(snapshot) == before

def test_flag_variant_mismatch_and_missing_rosters_are_unchecked(tmp_path: Path) -> None:
    constraint, snapshot = _case('P2-137', tmp_path)
    assert spec.subtype_partition_state(dataclasses.replace(constraint, variant='both'), snapshot) == -1
    missing = dataclasses.replace(snapshot, rosters=tuple(row for row in snapshot.rosters if row.object_type != constraint.subtypes[0]))
    assert spec.subtype_partition_state(constraint, missing) == -1

def test_duplicate_supertype_members_do_not_duplicate_witness(tmp_path: Path) -> None:
    constraint, snapshot = _case('P2-138', tmp_path)
    position = next((i for i, row in enumerate(snapshot.rosters) if row.object_type == constraint.object_type))
    rosters = list(snapshot.rosters)
    rosters[position] = dataclasses.replace(rosters[position], members=rosters[position].members + rosters[position].members)
    duplicated = dataclasses.replace(snapshot, rosters=tuple(rosters))
    assert spec.subtype_partition_witness(constraint, duplicated) == spec.subtype_partition_witness(constraint, snapshot)

def test_partition_output_is_independent_of_roster_and_member_order(tmp_path: Path) -> None:
    constraint, snapshot = _case('P2-144', tmp_path)
    reversed_rosters = tuple(dataclasses.replace(row, members=tuple(reversed(row.members))) for row in reversed(snapshot.rosters))
    permuted = dataclasses.replace(snapshot, rosters=reversed_rosters)
    assert spec.subtype_partition_result(constraint, permuted) == spec.subtype_partition_result(constraint, snapshot)

def test_one_subtype_exclusive_is_decided_and_exhaustive_is_equality(tmp_path: Path) -> None:
    exclusive, first = _case('P2-146', tmp_path)
    exhaustive, second = _case('P2-148', tmp_path)
    assert spec.subtype_partition_state(exclusive, first) == 1
    assert spec.subtype_partition_state(exhaustive, second) == 0

def test_opaque_empty_semiderived_subtype_is_unchecked(tmp_path: Path) -> None:
    constraint, snapshot = _case('P2-150', tmp_path)
    subtype = constraint.subtypes[0]
    object_types = tuple(dataclasses.replace(row, derivation='semiderived') if row.id == subtype else row for row in snapshot.object_types)
    semiderived = dataclasses.replace(snapshot, object_types=object_types)
    assert spec.subtype_partition_state(constraint, semiderived) == -1

def test_empty_subtype_without_opaque_membership_rule_is_decided(tmp_path: Path) -> None:
    constraint, snapshot = _case('P2-150', tmp_path)
    subtype = constraint.subtypes[0]
    object_types = tuple(dataclasses.replace(row, opaque_rule='') if row.id == subtype else row for row in snapshot.object_types)
    transparent = dataclasses.replace(snapshot, object_types=object_types)
    assert spec.subtype_partition_state(constraint, transparent) == 0

def test_partition_membership_uses_identity_kind_as_well_as_token(tmp_path: Path) -> None:
    constraint, snapshot = _case('P2-138', tmp_path)
    position = next((i for i, row in enumerate(snapshot.rosters) if row.object_type == constraint.subtypes[1]))
    rosters = list(snapshot.rosters)
    original = rosters[position].members[0]
    assert original is not None
    rosters[position] = dataclasses.replace(rosters[position], members=(dataclasses.replace(original, identity_kind='number'),))
    distinct_identity = dataclasses.replace(snapshot, rosters=tuple(rosters))
    assert spec.subtype_partition_state(constraint, distinct_identity) == 1
    mutant = _mutant(tmp_path, 'if scalar_list_member(universe[member_index], populations[subtype_index]):', 'if any(item.token == universe[member_index].token for item in populations[subtype_index]):')
    assert mutant['subtype_partition_state'](constraint, distinct_identity) == 0

def _mutant(tmp_path: Path, before: str, after: str):
    source = Path(spec.__file__).read_text()
    node = next(item for item in ast.parse(source).body if isinstance(item, ast.FunctionDef) and item.name == 'subtype_partition_result')
    segment = ast.get_source_segment(source, node)
    assert segment is not None and segment.count(before) == 1
    lines = source.splitlines(keepends=True)
    start = sum(len(line) for line in lines[:node.lineno - 1])
    end = sum(len(line) for line in lines[:node.end_lineno])
    path = tmp_path / 'partition_mutant.py'
    path.write_text(source[:start] + segment.replace(before, after) + source[end:])
    return runpy.run_path(str(path))

@pytest.mark.parametrize('case_id,before,after', [('P2-138', 'if exclusive and count >= 2:', 'if exclusive and count >= 3:'), ('P2-141', 'if exhaustive and count == 0:', 'if exhaustive and count < 0:'), ('P2-150', 'object_type.derivation in ("derived", "semiderived")', 'object_type.derivation == "missing"'), ('P2-144', 'universe = canonical_distinct(universe_values)', 'universe = list(universe_values)'), ('P2-144', 'witness.append([neither[member_index]])', 'witness.insert(0, [neither[member_index]])')], ids=['exclusive-pair-threshold', 'exhaustive-direction', 'opaque-membership-refusal', 'canonical-output', 'both-before-neither'])
def test_partition_mutations_have_counterexamples(tmp_path: Path, case_id: str, before: str, after: str) -> None:
    constraint, snapshot = _case(case_id, tmp_path)
    mutant = _mutant(tmp_path, before, after)
    assert mutant['subtype_partition_result'](constraint, snapshot) != spec.subtype_partition_result(constraint, snapshot)
