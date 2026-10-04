from __future__ import annotations

import ast
import dataclasses
import runpy
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
from support import set_relation_cases as corpus

from gnd import semantic_spec as spec
from gnd.semantic_adapter import adapt_snapshot, canonical_scalar
from gnd.semantic_ir import IRConstraint, IRFactType, IRRelation, IRRole, IRRoster, SnapshotIR


def _frozen(case_id: str, tmp_path: Path) -> tuple[IRConstraint, SnapshotIR]:
    model, population = corpus._build(case_id, tmp_path)
    snapshot = adapt_snapshot(model, population)
    reference = corpus.CASE_BY_ID[case_id]['ref']
    return (next(row for row in snapshot.constraints if row.ref == reference), snapshot)
FROZEN = {'P2-086': ('subset', 1, []), 'P2-087': ('subset', 0, [['3/1', 'C9']]), 'P2-088': ('subset', 0, [['3/1', 'C9']]), 'P2-089': ('subset', 1, []), 'P2-090': ('subset', 0, [['10/1', '20/1']]), 'P2-091': ('subset', 0, [['10/1', '20/1']]), 'P2-092': ('equality', 1, []), 'P2-093': ('equality', 0, [['1/1'], ['2/1']]), 'P2-094': ('equality', 0, [['1/1'], ['2/1']]), 'P2-095': ('equality', 1, []), 'P2-096': ('equality', 0, [['30/1', '40/1'], ['30/1', '41/1']]), 'P2-097': ('equality', 0, [['30/1', '40/1'], ['30/1', '41/1']]), 'P2-098': ('exclusion', 1, []), 'P2-099': ('exclusion', 0, [['1/1']]), 'P2-100': ('exclusion', 0, [['1/1']]), 'P2-101': ('exclusion', 1, []), 'P2-102': ('exclusion', 0, [['50/1', '60/1']]), 'P2-103': ('exclusion', 0, [['50/1', '60/1']]), 'P2-104': ('exclusive_or', 1, []), 'P2-105': ('exclusive_or', 0, [['2/1'], ['3/1'], ['4/1'], ['5/1'], ['6/1']]), 'P2-106': ('exclusive_or', 0, [['2/1'], ['3/1'], ['4/1'], ['5/1'], ['6/1']]), 'P2-107': ('exclusive_or', -1, []), 'P2-108': ('exclusive_or', 0, [['P1', 'C1']]), 'P2-109': ('exclusive_or', 0, [['P1', 'C1']]), 'P2-110': ('exclusive_or', -1, [])}

@pytest.mark.parametrize('case_id', tuple(FROZEN))
def test_frozen_set_relation_cases_match_their_normative_clauses(tmp_path: Path, case_id: str) -> None:
    constraint, snapshot = _frozen(case_id, tmp_path)
    family, state, witness = FROZEN[case_id]
    state_fn = getattr(spec, family + '_state')
    holds_fn = getattr(spec, family + '_holds')
    witness_fn = getattr(spec, family + '_witness')
    before = hash(snapshot)
    assert state_fn(constraint, snapshot) == state
    assert holds_fn(constraint, snapshot) is (state == 1)
    assert [[value.token for value in row] for row in witness_fn(constraint, snapshot)] == witness
    assert hash(snapshot) == before

def _scalar(value: object):
    result = canonical_scalar(value, None)
    assert result is not None
    return result

def _constraint(family: str, variant: str, sequences: tuple[tuple[tuple[str, str], ...], ...]) -> IRConstraint:
    return IRConstraint(ref='fixture', family=family, variant=variant, modality='alethic', fact_type='', roles=(), role_refs=(), sequences=sequences, object_type='', subtypes=(), flags=(False, False, True, True), minimum=None, maximum=None, allowed=(), ranges=(), operator='', literal=None, operands=(), consequent_kind='', antecedent=(), consequent=(), scope_fact_types=tuple(dict.fromkeys(ref[0] for seq in sequences for ref in seq)), expression='', refused='')

def _snapshot(constraint: IRConstraint, facts: tuple[IRFactType, ...], relations: tuple[IRRelation, ...], rosters: tuple[IRRoster, ...]=()) -> SnapshotIR:
    return SnapshotIR(object_types=(), fact_types=facts, relations=relations, rosters=rosters, constraints=(constraint,), finite=True, covers=tuple(fact.id for fact in facts), explicit_rosters=(), derivations=(), derivation_order=(), refusals=())

def _binary_fixture(family: str, left: tuple, right: tuple):
    sequences = ((('left', 'value'),), (('right', 'value'),))
    constraint = _constraint(family, 'single', sequences)
    facts = (IRFactType('left', (IRRole('value', 'thing', ''),), True, '', False, 'claimed', ''), IRFactType('right', (IRRole('value', 'thing', ''),), True, '', False, 'claimed', ''))
    return (constraint, _snapshot(constraint, facts, (IRRelation('left', left, ()), IRRelation('right', right, ()))))

def test_empty_duplicate_permuted_and_identity_sensitive_sets() -> None:
    one, two = (_scalar(1), _scalar(2))
    constraint, snapshot = _binary_fixture('subset', (), ((one,),))
    assert spec.subset_state(constraint, snapshot) == 1
    constraint, snapshot = _binary_fixture('equality', ((two,), (one,), (two,)), ((one,),))
    assert spec.equality_witness(constraint, snapshot) == [[two]]
    permuted = dataclasses.replace(snapshot, relations=(IRRelation('left', ((one,), (two,)), ()), snapshot.relations[1]))
    assert spec.equality_witness(constraint, permuted) == [[two]]
    same_token_other_identity = dataclasses.replace(one, identity_kind='string')
    constraint, snapshot = _binary_fixture('subset', ((one,),), ((same_token_other_identity,),))
    assert spec.subset_state(constraint, snapshot) == 0

def test_disconnected_ambiguous_and_variant_mismatched_sequences_are_unchecked() -> None:
    one = _scalar(1)
    disconnected = _constraint('subset', 'joined', ((('a', 'value'), ('b', 'value')), (('c', 'value'),)))
    facts = tuple(IRFactType(name, (IRRole('value', 'thing', ''),), True, '', False, 'claimed', '') for name in ('a', 'b', 'c'))
    snapshot = _snapshot(disconnected, facts, tuple(IRRelation(name, ((one,),), ()) for name in ('a', 'b', 'c')))
    assert spec.subset_state(disconnected, snapshot) == -1
    ambiguous = _constraint('subset', 'joined', ((('a', 'value'), ('b', 'value')), (('c', 'value'),)))
    ambiguous_facts = (IRFactType('a', (IRRole('value', 'thing', ''), IRRole('x', 'anchor', ''), IRRole('y', 'anchor', '')), True, '', False, 'claimed', ''), *facts[1:])
    assert spec.subset_state(ambiguous, dataclasses.replace(snapshot, fact_types=ambiguous_facts)) == -1
    ordinary, ordinary_snapshot = _binary_fixture('subset', ((one,),), ((one,),))
    assert spec.subset_state(dataclasses.replace(ordinary, variant='joined'), ordinary_snapshot) == -1

@pytest.mark.parametrize('kind', ['fact', 'role', 'relation', 'coverage', 'row', 'cell', 'refusal'])
def test_each_sequence_resolution_boundary_is_unchecked(kind: str) -> None:
    one = _scalar(1)
    constraint, snapshot = _binary_fixture('subset', ((one,),), ((one,),))
    if kind == 'fact':
        snapshot = dataclasses.replace(snapshot, fact_types=snapshot.fact_types[:1])
    elif kind == 'role':
        sequences = (constraint.sequences[0], (('right', 'absent'),))
        constraint = dataclasses.replace(constraint, sequences=sequences)
    elif kind == 'relation':
        snapshot = dataclasses.replace(snapshot, relations=snapshot.relations[:1])
    elif kind == 'coverage':
        snapshot = dataclasses.replace(snapshot, covers=('left',))
    elif kind == 'row':
        snapshot = dataclasses.replace(snapshot, relations=(IRRelation('left', ((),), ()), snapshot.relations[1]))
    elif kind == 'cell':
        snapshot = dataclasses.replace(snapshot, relations=(IRRelation('left', ((None,),), ()), snapshot.relations[1]))
    else:
        constraint = dataclasses.replace(constraint, refused='malformed-constraint')
    assert spec.subset_state(constraint, snapshot) == -1
    assert spec.subset_witness(constraint, snapshot) == []

def test_single_xor_witness_lists_both_before_neither_in_canonical_order() -> None:
    two, three, four = (_scalar(2), _scalar(3), _scalar(4))
    constraint = _constraint('exclusive-or', 'single-role', ((('left', 'value'),), (('right', 'value'),)))
    facts = (IRFactType('left', (IRRole('value', 'thing', ''),), True, '', False, 'claimed', ''), IRFactType('right', (IRRole('value', 'thing', ''),), True, '', False, 'claimed', ''))
    snapshot = _snapshot(constraint, facts, (IRRelation('left', ((three,), (two,)), ()), IRRelation('right', ((two,),), ())), (IRRoster('thing', (four, three, two), ()),))
    assert spec.exclusive_or_state(constraint, snapshot) == 0
    assert spec.exclusive_or_witness(constraint, snapshot) == [[two], [four]]
    assert spec.exclusive_or_state(dataclasses.replace(constraint, variant='multi-role'), snapshot) == -1

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

@pytest.mark.parametrize('function,before,after,family,expected,mutated', [('subset_state', 'valid, subset_rows, superset_rows =', 'valid, superset_rows, subset_rows =', 'subset', 0, 1), ('equality_state', 'while index < len(right):', 'while index < 0:', 'equality', 0, 1), ('exclusion_state', 'if row_list_member(left[index], right):', 'if not row_list_member(left[index], right):', 'exclusion', 0, 1)], ids=['subset-direction', 'equality-one-way', 'exclusion-polarity'])
def test_set_relation_truth_mutations_have_counterexamples(tmp_path: Path, function: str, before: str, after: str, family: str, expected: int, mutated: int) -> None:
    one, two = (_scalar(1), _scalar(2))
    if family == 'subset':
        constraint, snapshot = _binary_fixture(family, ((one,), (two,)), ((one,),))
    elif family == 'equality':
        constraint, snapshot = _binary_fixture(family, ((one,),), ((one,), (two,)))
    else:
        constraint, snapshot = _binary_fixture(family, ((one,),), ((one,),))
    mutant = _mutated_namespace(tmp_path, function, before, after)
    assert getattr(spec, function)(constraint, snapshot) == expected
    assert mutant[function](constraint, snapshot) == mutated

def test_multi_xor_clean_exclusion_is_unchecked_not_pass(tmp_path: Path) -> None:
    constraint, snapshot = _frozen('P2-110', tmp_path)
    mutant = _mutated_namespace(tmp_path, 'exclusive_or_result', 'if witness:\n            return 0, witness\n        return -1, witness', 'if witness:\n            return 0, witness\n        return 1, witness')
    assert spec.exclusive_or_state(constraint, snapshot) == -1
    assert mutant['exclusive_or_state'](constraint, snapshot) == 1

def test_row_witness_order_mutation_has_counterexample(tmp_path: Path) -> None:
    one, two = (_scalar(1), _scalar(2))
    constraint, snapshot = _binary_fixture('subset', ((two,), (one,)), ())
    mutant = _mutated_namespace(tmp_path, 'canonical_distinct_rows', 'while position < len(result) and not row_canonical_less(value, result[position]):', 'while position < len(result):')
    assert spec.subset_witness(constraint, snapshot) == [[one], [two]]
    assert mutant['subset_witness'](constraint, snapshot) == [[two], [one]]

def test_xor_both_neither_order_mutation_has_counterexample(tmp_path: Path) -> None:
    constraint, snapshot = _frozen('P2-105', tmp_path)
    before = 'member_index = 0\n    while member_index < len(both):\n        witness.append([both[member_index]])\n        member_index += 1\n    member_index = 0\n    while member_index < len(neither):\n        witness.append([neither[member_index]])\n        member_index += 1'
    after = 'member_index = 0\n    while member_index < len(neither):\n        witness.append([neither[member_index]])\n        member_index += 1\n    member_index = 0\n    while member_index < len(both):\n        witness.append([both[member_index]])\n        member_index += 1'
    mutant = _mutated_namespace(tmp_path, 'exclusive_or_result', before, after)
    expected = spec.exclusive_or_witness(constraint, snapshot)
    assert [[value.token for value in row] for row in expected] == [['2/1'], ['3/1'], ['4/1'], ['5/1'], ['6/1']]
    assert mutant['exclusive_or_witness'](constraint, snapshot) != expected

def test_join_uses_shared_anchor_instead_of_cross_product(tmp_path: Path) -> None:
    one, two, ten, twenty = (_scalar(1), _scalar(2), _scalar(10), _scalar(20))
    sequence = (('left', 'value'), ('right', 'value'))
    constraint = _constraint('subset', 'joined', (sequence, (('pair', 'a'), ('pair', 'b'))))
    facts = (IRFactType('left', (IRRole('anchor', 'entity', ''), IRRole('value', 'thing', '')), True, '', False, 'claimed', ''), IRFactType('right', (IRRole('anchor', 'entity', ''), IRRole('value', 'thing', '')), True, '', False, 'claimed', ''), IRFactType('pair', (IRRole('a', 'thing', ''), IRRole('b', 'thing', '')), True, '', False, 'claimed', ''))
    snapshot = _snapshot(constraint, facts, (IRRelation('left', ((one, ten),), ()), IRRelation('right', ((two, twenty),), ()), IRRelation('pair', (), ())))
    mutant = _mutated_namespace(tmp_path, 'role_sequence_rows', 'if compatible:', 'if True:')
    assert spec.subset_state(constraint, snapshot) == 1
    assert mutant['subset_state'](constraint, snapshot) == 0
