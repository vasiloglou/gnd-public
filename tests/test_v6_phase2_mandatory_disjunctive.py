from __future__ import annotations

import ast
import dataclasses
import runpy
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
from gnd import semantic_spec as spec
from gnd.semantic_adapter import canonical_scalar
from gnd.semantic_ir import IRConstraint, IRFactType, IRRelation, IRRole, IRRoster, SnapshotIR


def _constraint() -> IRConstraint:
    return IRConstraint(ref='fixture', family='mandatory-disjunctive', variant='n-a', modality='alethic', fact_type='', roles=(), role_refs=(('left', 'subject'), ('right', 'subject')), sequences=(), object_type='', subtypes=(), flags=(False, False, True, True), minimum=None, maximum=None, allowed=(), ranges=(), operator='', literal=None, operands=(), consequent_kind='', antecedent=(), consequent=(), scope_fact_types=('left', 'right'), expression='', refused='')

def _small_snapshot(universe: tuple, left: tuple, right: tuple, *, right_type: str='thing', covers: tuple[str, ...]=('left', 'right')) -> tuple[IRConstraint, SnapshotIR]:
    constraint = _constraint()
    snapshot = SnapshotIR(object_types=(), fact_types=(IRFactType('left', (IRRole('subject', 'thing', ''),), True, 'asserted', False, 'claimed', ''), IRFactType('right', (IRRole('subject', right_type, ''),), True, 'asserted', False, 'claimed', '')), relations=(IRRelation('left', left, ()), IRRelation('right', right, ())), rosters=(IRRoster('thing', universe, ()),), constraints=(constraint,), finite=True, covers=covers, explicit_rosters=(), derivations=(), derivation_order=(), refusals=())
    return (constraint, snapshot)

def test_inclusive_role_union_and_duplicate_refs_use_set_truth() -> None:
    one = canonical_scalar(1, None)
    two = canonical_scalar(2, None)
    constraint, snapshot = _small_snapshot((one, two), ((one,),), ((two,),))
    assert spec.mandatory_disjunctive_state(constraint, snapshot) == 1
    duplicated = dataclasses.replace(constraint, role_refs=(constraint.role_refs[0], constraint.role_refs[0]))
    assert spec.mandatory_disjunctive_state(duplicated, snapshot) == 0
    assert spec.mandatory_disjunctive_witness(duplicated, snapshot) == [two]

def test_empty_subject_is_clean_and_uncovered_subject_is_unchecked() -> None:
    constraint, snapshot = _small_snapshot((), (), ())
    assert spec.mandatory_disjunctive_state(constraint, snapshot) == 1
    uncovered = dataclasses.replace(snapshot, covers=('left',))
    assert spec.mandatory_disjunctive_state(constraint, uncovered) == -1
    assert spec.mandatory_disjunctive_witness(constraint, uncovered) == []

@pytest.mark.parametrize('kind', ['short-row', 'missing-player', 'missing-roster'])
def test_malformed_or_unrepresented_cells_are_unchecked(kind: str) -> None:
    one = canonical_scalar(1, None)
    universe = (one,)
    left = ((one,),)
    if kind == 'short-row':
        left = ((),)
    elif kind == 'missing-player':
        left = ((None,),)
    elif kind == 'missing-roster':
        universe = (None,)
    constraint, snapshot = _small_snapshot(universe, left, ())
    assert spec.mandatory_disjunctive_state(constraint, snapshot) == -1
    assert not spec.mandatory_disjunctive_holds(constraint, snapshot)
    assert spec.mandatory_disjunctive_witness(constraint, snapshot) == []

def test_witness_is_canonical_under_universe_role_and_row_permutations() -> None:
    false = canonical_scalar(False, None)
    number = canonical_scalar(1, None)
    text = canonical_scalar('z', None)
    two = canonical_scalar(2, None)
    expected = [false, number, two, text]
    first = _small_snapshot((text, two, false, number, text), (), ())
    second = _small_snapshot((number, false, two, text), (), ())
    second_constraint = dataclasses.replace(second[0], role_refs=tuple(reversed(second[0].role_refs)))
    assert spec.mandatory_disjunctive_witness(*first) == expected
    assert spec.mandatory_disjunctive_witness(second_constraint, second[1]) == expected

def test_mixed_subject_types_are_unchecked_even_when_values_cover_the_first_roster() -> None:
    one = canonical_scalar(1, None)
    constraint, snapshot = _small_snapshot((one,), (), ((one,),), right_type='other')
    assert spec.mandatory_disjunctive_state(constraint, snapshot) == -1
    assert spec.mandatory_disjunctive_witness(constraint, snapshot) == []

@pytest.mark.parametrize('kind', ['fact', 'role', 'relation', 'roster', 'refusal'])
def test_each_resolution_boundary_is_unchecked(kind: str) -> None:
    one = canonical_scalar(1, None)
    constraint, snapshot = _small_snapshot((one,), ((one,),), ())
    if kind == 'fact':
        snapshot = dataclasses.replace(snapshot, fact_types=snapshot.fact_types[:1])
    elif kind == 'role':
        constraint = dataclasses.replace(constraint, role_refs=(constraint.role_refs[0], ('right', 'absent')))
    elif kind == 'relation':
        snapshot = dataclasses.replace(snapshot, relations=snapshot.relations[:1])
    elif kind == 'roster':
        snapshot = dataclasses.replace(snapshot, rosters=())
    else:
        constraint = dataclasses.replace(constraint, refused='subject-type-ambiguous')
    assert spec.mandatory_disjunctive_state(constraint, snapshot) == -1
    assert spec.mandatory_disjunctive_witness(constraint, snapshot) == []

def _mutated_namespace(tmp_path: Path, function: str, before: str, after: str) -> dict[str, object]:
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

@pytest.mark.parametrize('function,before,after,case', [('mandatory_disjunctive_state', 'while role_index < len(cursor[2]):', 'while role_index < 1:', 'only-first-role'), ('mandatory_disjunctive_cursor', 'elif object_type != shared_type:', 'elif False:', 'mixed-types'), ('mandatory_disjunctive_cursor', 'if fact_type not in snapshot.covers:', 'if False:', 'coverage'), ('mandatory_disjunctive_witness', 'return canonical_distinct(missing)', 'return missing', 'source-order'), ('scalar_identical', 'return left.identity_kind == right.identity_kind and left.token == right.token', 'return left.token == right.token', 'identity'), ('canonical_distinct', 'return result', 'return result + result', 'duplicates')], ids=['role-omission', 'mixed-type-acceptance', 'coverage-omission-as-evaluable', 'source-order-output', 'token-only-identity', 'duplicate-retention'])
def test_one_change_mutations_have_distinguishing_counterexamples(tmp_path: Path, function: str, before: str, after: str, case: str) -> None:
    mutant = _mutated_namespace(tmp_path, function, before, after)
    one = canonical_scalar(1, None)
    two = canonical_scalar(2, None)
    if case == 'only-first-role':
        constraint, snapshot = _small_snapshot((one, two), ((one,),), ((two,),))
        assert spec.mandatory_disjunctive_state(constraint, snapshot) == 1
        assert mutant['mandatory_disjunctive_state'](constraint, snapshot) == 0
    elif case == 'mixed-types':
        constraint, snapshot = _small_snapshot((one,), (), ((one,),), right_type='other')
        assert spec.mandatory_disjunctive_state(constraint, snapshot) == -1
        assert mutant['mandatory_disjunctive_state'](constraint, snapshot) == 1
    elif case == 'coverage':
        constraint, snapshot = _small_snapshot((one,), ((one,),), (), covers=('left',))
        assert spec.mandatory_disjunctive_state(constraint, snapshot) == -1
        assert mutant['mandatory_disjunctive_state'](constraint, snapshot) == 1
    elif case == 'source-order':
        constraint, snapshot = _small_snapshot((two, one), (), ())
        assert spec.mandatory_disjunctive_witness(constraint, snapshot) == [one, two]
        assert mutant['mandatory_disjunctive_witness'](constraint, snapshot) == [two, one]
    elif case == 'identity':
        text = canonical_scalar('1', None)
        altered = dataclasses.replace(text, identity_kind='number')
        constraint, snapshot = _small_snapshot((text,), ((altered,),), ())
        assert spec.mandatory_disjunctive_state(constraint, snapshot) == 0
        assert mutant['mandatory_disjunctive_state'](constraint, snapshot) == 1
    else:
        constraint, snapshot = _small_snapshot((one,), (), ())
        assert spec.mandatory_disjunctive_witness(constraint, snapshot) == [one]
        assert mutant['mandatory_disjunctive_witness'](constraint, snapshot) == [one, one]
