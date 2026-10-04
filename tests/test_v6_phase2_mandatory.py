from __future__ import annotations

import ast
import dataclasses
import runpy
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
from support import mandatory_cases as corpus

from gnd import semantic_spec as spec
from gnd.semantic_adapter import adapt_snapshot, canonical_scalar
from gnd.semantic_ir import IRConstraint, IRFactType, IRRelation, IRRole, IRRoster, SnapshotIR


def _snapshot(case_id: str, tmp_path: Path) -> tuple[IRConstraint, SnapshotIR]:
    model, population = corpus._build(case_id, tmp_path)
    snapshot = adapt_snapshot(model, population)
    case = next(row for row in corpus.CASES['cases'] if row['id'] == case_id)
    constraint = next(row for row in snapshot.constraints if row.ref == case['ref'])
    return (constraint, snapshot)

@pytest.mark.parametrize('case_id,holds,witness', [('P2-008', True, []), ('P2-009', False, ['C1']), ('P2-010', False, ['C1'])])
def test_frozen_mandatory_cases_match_nf_mand_1(tmp_path: Path, case_id: str, holds: bool, witness: list[str]) -> None:
    constraint, snapshot = _snapshot(case_id, tmp_path)
    assert spec.mandatory_holds(constraint, snapshot) is holds
    assert [value.token for value in spec.mandatory_witness(constraint, snapshot)] == witness

def test_unresolved_role_is_unchecked_and_never_clean(tmp_path: Path) -> None:
    constraint, snapshot = _snapshot('P2-008', tmp_path)
    unresolved = dataclasses.replace(constraint, roles=('nobody',))
    assert spec.mandatory_state(unresolved, snapshot) == -1
    assert not spec.mandatory_holds(unresolved, snapshot)
    assert spec.mandatory_witness(unresolved, snapshot) == []

def test_coverage_omission_suppresses_family_evaluation(tmp_path: Path) -> None:
    constraint, snapshot = _snapshot('P2-165', tmp_path)
    assert spec.mandatory_state(constraint, snapshot) == -1
    assert not spec.mandatory_holds(constraint, snapshot)
    assert spec.mandatory_witness(constraint, snapshot) == []

def test_empty_subject_is_clean_inside_family_and_left_to_vacuity(tmp_path: Path) -> None:
    constraint, snapshot = _snapshot('P2-167', tmp_path)
    assert spec.mandatory_state(constraint, snapshot) == 1
    assert spec.mandatory_holds(constraint, snapshot)
    assert spec.mandatory_witness(constraint, snapshot) == []

def _small_snapshot(universe: tuple, players: tuple, *, rows: tuple | None=None, covers: tuple[str, ...]=('host',)) -> tuple[IRConstraint, SnapshotIR]:
    role = IRRole('subject', 'thing', '')
    constraint = IRConstraint(ref='fixture', family='mandatory', variant='inline', modality='alethic', fact_type='host', roles=('subject',), role_refs=(), sequences=(), object_type='', subtypes=(), flags=(False, False, True, True), minimum=None, maximum=None, allowed=(), ranges=(), operator='', literal=None, operands=(), consequent_kind='', antecedent=(), consequent=(), scope_fact_types=('host',), expression='', refused='')
    relation_rows = rows if rows is not None else tuple((value,) for value in players)
    snapshot = SnapshotIR(object_types=(), fact_types=(IRFactType('host', (role,), True, 'asserted', False, 'claimed', ''),), relations=(IRRelation('host', relation_rows, ()),), rosters=(IRRoster('thing', universe, ()),), constraints=(constraint,), finite=True, covers=covers, explicit_rosters=(), derivations=(), derivation_order=(), refusals=())
    return (constraint, snapshot)

def test_witness_is_exhaustive_distinct_and_canonical_under_source_permutations() -> None:
    false = canonical_scalar(False, None)
    true = canonical_scalar(True, None)
    one = canonical_scalar(1, None)
    two = canonical_scalar(2, None)
    text = canonical_scalar('z', None)
    null = canonical_scalar(None, None)
    assert all(value is not None for value in (false, true, one, two, text, null))
    ordered = [false, true, one, two, text, null]
    first = (null, text, two, true, one, false, two, text)
    second = tuple(reversed(first))
    for universe in (first, second):
        constraint, snapshot = _small_snapshot(universe, ())
        actual = spec.mandatory_witness(constraint, snapshot)
        assert actual == ordered
        assert spec.mandatory_state(constraint, snapshot) == 0

def test_identity_membership_does_not_collapse_boolean_number_or_string() -> None:
    boolean = canonical_scalar(True, None)
    number = canonical_scalar(1, None)
    text = canonical_scalar('1', None)
    constraint, snapshot = _small_snapshot((boolean, number, text), (number,))
    assert spec.mandatory_witness(constraint, snapshot) == [boolean, text]

@pytest.mark.parametrize('rows,universe', [(((),), (canonical_scalar(1, None),)), (((None,),), (canonical_scalar(1, None),)), ((), (None,))])
def test_malformed_or_unrepresented_cells_are_unchecked(rows: tuple, universe: tuple) -> None:
    constraint, snapshot = _small_snapshot(universe, (), rows=rows)
    before = hash(snapshot)
    assert spec.mandatory_state(constraint, snapshot) == -1
    assert not spec.mandatory_holds(constraint, snapshot)
    assert spec.mandatory_witness(constraint, snapshot) == []
    assert hash(snapshot) == before

def _mutated_namespace(tmp_path: Path, function: str, before: str, after: str) -> dict[str, object]:
    source = Path(spec.__file__).read_text()
    tree = ast.parse(source)
    target = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == function)
    segment = ast.get_source_segment(source, target)
    assert segment is not None and segment.count(before) == 1
    changed = segment.replace(before, after)
    lines = source.splitlines(keepends=True)
    start = sum(len(line) for line in lines[:target.lineno - 1])
    end = sum(len(line) for line in lines[:target.end_lineno])
    mutant = source[:start] + changed + source[end:]
    path = tmp_path / (function + '_mutant.py')
    path.write_text(mutant)
    return runpy.run_path(str(path))

@pytest.mark.parametrize('function,before,after,case', [('mandatory_state', 'if missing_identities(tuple(universe), tuple(player_values)):', 'if False:', 'missing'), ('mandatory_state', 'if cursor[0] < 0:\n        return -1', 'if cursor[0] < 0:\n        return 1', 'unresolved'), ('mandatory_witness', 'return canonical_distinct(missing)', 'return missing', 'order'), ('missing_identities', ' and not scalar_list_member(\n            universe[index], result\n        )', '', 'duplicates'), ('scalar_identical', 'return left.identity_kind == right.identity_kind and left.token == right.token', 'return left.token == right.token', 'identity')], ids=['missing-member-omission', 'unresolved-as-clean', 'source-order-output', 'duplicate-retention', 'token-only-identity'])
def test_mandatory_mutations_have_distinguishing_counterexamples(tmp_path: Path, function: str, before: str, after: str, case: str) -> None:
    mutant = _mutated_namespace(tmp_path, function, before, after)
    false = canonical_scalar(False, None)
    true = canonical_scalar(True, None)
    number = canonical_scalar(1, None)
    text = canonical_scalar('1', None)
    two = canonical_scalar(2, None)
    if case == 'missing':
        constraint, snapshot = _small_snapshot((number,), ())
        assert spec.mandatory_state(constraint, snapshot) == 0
        assert mutant['mandatory_state'](constraint, snapshot) == 1
    elif case == 'unresolved':
        constraint, snapshot = _small_snapshot((number,), ())
        constraint = dataclasses.replace(constraint, roles=('absent',))
        assert spec.mandatory_state(constraint, snapshot) == -1
        assert mutant['mandatory_state'](constraint, snapshot) == 1
    elif case == 'order':
        constraint, snapshot = _small_snapshot((two, number), ())
        assert spec.mandatory_witness(constraint, snapshot) == [number, two]
        assert mutant['mandatory_witness'](constraint, snapshot) == [two, number]
    elif case == 'duplicates':
        assert spec.missing_identities((number, number), ()) == [number]
        assert mutant['missing_identities']((number, number), ()) == [number, number]
    else:
        altered = dataclasses.replace(text, identity_kind='number')
        assert not spec.scalar_identical(text, altered)
        assert mutant['scalar_identical'](text, altered)
        assert false is not None and true is not None
