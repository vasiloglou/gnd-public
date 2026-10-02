from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

import pytest

from gnd.checker import DERIVATION_REASON_CODES
from gnd.measure.score import classify
from gnd.measure.truth import ConstraintRefError, resolve_constraint_ref
from gnd.model import load_model
from gnd.synth.frontier import BAND4_REASON_CODES, reason_codes_by_family
from gnd.synth.provenance import ExpectedState

CORPUS = Path(__file__).parent / 'fixtures' / 'phase3-consumers'
EXPECTED_CONSTRAINT_BAND4_REASON_CODES = frozenset({'bound-type-mismatch', 'derived-unknown', 'reference-join-work-limit', 'family-unimplemented', 'join-anchor-ambiguous', 'join-disconnected', 'literal-type-ambiguous', 'no-reference-clock', 'partition-asserts-nothing', 'ring-not-binary', 'role-unresolved', 'subject-type-ambiguous', 'subtype-derivation-only', 'textual-not-mechanical', 'values-not-comparable', 'xor-disjunctive-undefined'})

def _is_exact_constraint_band4_frontier(codes: Iterable[str]) -> bool:
    values = tuple(codes)
    return len(values) == 16 and len(set(values)) == 16 and (frozenset(values) == EXPECTED_CONSTRAINT_BAND4_REASON_CODES)

def test_resolve_constraint_ref_refuses_derivation_refs_by_name() -> None:
    model = load_model(CORPUS / 'eligibility.orm.yaml')
    with pytest.raises(ConstraintRefError) as caught:
        resolve_constraint_ref(model, 'derivation:book_is_eligible')
    message = str(caught.value)
    assert 'derivation obligation' in message
    assert 'constraint' in message

def test_the_band4_scan_scope_is_constraint_only_by_name() -> None:
    assert 'subtype-derivation-only' in BAND4_REASON_CODES
    assert 'derived-unknown' in BAND4_REASON_CODES
    assert 'derived-unknown' in reason_codes_by_family()['mandatory']
    assert 'reference-join-work-limit' in reason_codes_by_family()['guarded']
    for code in set(DERIVATION_REASON_CODES) - {'derived-unknown'}:
        assert code not in BAND4_REASON_CODES
        for family, owned in reason_codes_by_family().items():
            assert code not in owned, (family, code)

def test_the_constraint_band4_frontier_is_the_exact_registered_member_set() -> None:
    assert _is_exact_constraint_band4_frontier(BAND4_REASON_CODES)
    assert 'guarded-exists-coverage-missing' not in BAND4_REASON_CODES
    assert 'guarded-exists-work-limit' not in BAND4_REASON_CODES
    assert not _is_exact_constraint_band4_frontier(EXPECTED_CONSTRAINT_BAND4_REASON_CODES | {'negative-control'})
    assert not _is_exact_constraint_band4_frontier(EXPECTED_CONSTRAINT_BAND4_REASON_CODES - {'join-disconnected'})
    assert not _is_exact_constraint_band4_frontier((*EXPECTED_CONSTRAINT_BAND4_REASON_CODES, 'join-disconnected'))

def test_expected_unchecked_by_design_still_scores_correct() -> None:
    expectation = ExpectedState(ground_truth='satisfied', expected_verdict='unchecked', reason='subtype-derivation-only')
    assert classify(expectation, 'unchecked', 'alethic') == 'correct'
    assert classify(expectation, 'pass', 'alethic') == 'false_pass'
    assert classify(expectation, 'fail', 'alethic') == 'tool_defect'

def test_both_expected_unchecked_by_design_members_score_correct() -> None:
    for reason in ('textual-not-mechanical', 'subtype-derivation-only'):
        expectation = ExpectedState(ground_truth='satisfied', expected_verdict='unchecked', reason=reason)
        assert classify(expectation, 'unchecked', 'alethic') == 'correct'
