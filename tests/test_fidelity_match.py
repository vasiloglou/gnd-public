from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from gnd.extract.refscheme import applicable_set
from gnd.fidelity.match import FidelityPartitionError, match_case, match_fact_type
from gnd.model import load_model

REPO_ROOT = Path(__file__).resolve().parent.parent
SETFAM = REPO_ROOT / 'tests' / 'fixtures' / 'checker' / 'setfam.orm.yaml'

@pytest.fixture(scope='module')
def setfam() -> Any:
    return load_model(str(SETFAM))

@pytest.fixture(scope='module')
def applicable(setfam: Any) -> dict[str, Any]:
    return applicable_set(setfam)

def rows(source: dict[str, list[dict[str, Any]]], extracted: dict[str, list[dict[str, Any]]], model: Any, applicable: dict[str, Any]) -> dict[str, Any]:
    return {match.fact_type_id: match for match in match_case(source, extracted, model=model, applicable=applicable)}

def test_multiset_matching_counts_duplicates(setfam: Any, applicable: dict[str, Any]) -> None:
    source = {'person_teaches_course': [{'person': 1, 'course': 'C1'}, {'person': 1, 'course': 'C1'}]}
    extracted = {'person_teaches_course': [{'person': 1, 'course': 'C1'}]}
    row = rows(source, extracted, setfam, applicable)['person_teaches_course']
    assert row.source_total == 2
    assert row.extracted_total == 1
    assert row.tp == 1
    assert row.missed == 1, 'the duplicate is half the evidence, not an artefact'
    assert row.unmatched == 0
    both = rows(source, {'person_teaches_course': [{'person': 1, 'course': 'C1'}, {'person': 1, 'course': 'C1'}]}, setfam, applicable)['person_teaches_course']
    assert both.tp == 2, 'a set intersection reads tp=1 here'
    assert both.missed == 0
    assert both.unmatched == 0

def test_inclusive_precision_counts_unresolved_in_denominator(setfam: Any, applicable: dict[str, Any]) -> None:
    source = {'person_teaches_course': [{'person': 1, 'course': 'C1'}, {'person': 2, 'course': 'C2'}]}
    extracted = {'person_teaches_course': [{'person': 1, 'course': 'C1'}, {'person': 2, 'course': 'C2'}, {'person': 99, 'course': 'C1'}]}
    row = rows(source, extracted, setfam, applicable)['person_teaches_course']
    assert row.tp == 2
    assert row.unresolved == 1, 'person 99 resolves to no source entity (R-10)'
    assert row.extracted_total == 3
    assert row.precision_numerator == 2
    assert row.precision_denominator == 3, 'the unresolved extraction stays in'
    assert row.recall_numerator == 2
    assert row.recall_denominator == 2

def test_ambiguous_on_normalization_collision(setfam: Any, applicable: dict[str, Any]) -> None:
    source = {'room_has_seats': [{'room': 'Ann B', 'seats': 20}, {'room': 'ann  b', 'seats': 30}]}
    extracted = {'room_has_seats': [{'room': 'Ann B', 'seats': 20}]}
    row = rows(source, extracted, setfam, applicable)['room_has_seats']
    assert row.ambiguous == 1
    assert row.tp == 0, 'an arbitrary assignment would have scored a tp here'
    assert row.missed == 2
    assert row.extracted_total == 1
    assert row.precision_denominator == 1, 'ambiguous stays in the denominator'

def test_ambiguous_on_broken_composite(setfam: Any, applicable: dict[str, Any]) -> None:
    source = {'booking_by_person': [{'booking': 'b1', 'person': 1}], 'booking_of_room': [{'booking': 'b1', 'room': 'R1'}]}
    extracted = {'booking_by_person': [{'booking': 'bX', 'person': 1}]}
    row = rows(source, extracted, setfam, applicable)['booking_by_person']
    assert row.extracted_total == 1
    assert row.ambiguous == 1
    assert row.tp == 0
    assert row.missed == 1
    assert row.unresolved == 0

def test_composite_identity_matches_across_renamed_surrogates(setfam: Any, applicable: dict[str, Any]) -> None:
    source = {'booking_by_person': [{'booking': 'b1', 'person': 1}], 'booking_of_room': [{'booking': 'b1', 'room': 'R1'}]}
    extracted = {'booking_by_person': [{'booking': 'zzz-9', 'person': 1}], 'booking_of_room': [{'booking': 'zzz-9', 'room': 'R1'}]}
    matched = rows(source, extracted, setfam, applicable)
    assert matched['booking_by_person'].tp == 1
    assert matched['booking_by_person'].ambiguous == 0
    assert matched['booking_of_room'].tp == 1

@pytest.mark.parametrize('extracted_filler', [1, '1', 'true'], ids=('number', 'string', 'lexical'))
def test_scalar_identity_domains_in_matching(setfam: Any, applicable: dict[str, Any], extracted_filler: Any) -> None:
    source = {'person_is_active': [{'person': True}]}
    row = rows(source, {'person_is_active': [{'person': extracted_filler}]}, setfam, applicable)['person_is_active']
    assert row.tp == 0
    assert row.unresolved == 1
    control = rows(source, {'person_is_active': [{'person': True}]}, setfam, applicable)['person_is_active']
    assert control.tp == 1, 'the domain guard must not reject the right domain'

def test_match_partition_invariant_raises_in_production(setfam: Any, applicable: dict[str, Any], monkeypatch: pytest.MonkeyPatch) -> None:
    from gnd.fidelity import match as match_module
    source = {'person_teaches_course': [{'person': 1, 'course': 'C1'}]}
    extracted = {'person_teaches_course': [{'person': 1, 'course': 'C1'}]}
    match_fact_type('person_teaches_course', source, extracted, model=setfam, applicable=applicable)
    real = match_module._multiset_true_positives
    monkeypatch.setattr(match_module, '_multiset_true_positives', lambda source_keys, extracted_keys: real(source_keys, extracted_keys) + 1)
    with pytest.raises(FidelityPartitionError, match='partition'):
        match_fact_type('person_teaches_course', source, extracted, model=setfam, applicable=applicable)

def test_matcher_identity_is_independent_of_the_checker() -> None:
    import ast
    source = (REPO_ROOT / 'src' / 'gnd' / 'fidelity' / 'match.py').read_text(encoding='utf-8')
    imported: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
    assert 'gnd.extract.identity' in imported, 'the ONE matcher-side identity'
    for forbidden in ('gnd.checker', 'gnd.synth.identity'):
        assert not any(name == forbidden or name.startswith(forbidden + '.') for name in imported), f'the matcher must not import {forbidden} (C1 independence)'

def test_inapplicable_fact_types_leave_the_denominator_with_a_mechanism(setfam: Any, applicable: dict[str, Any]) -> None:
    matched = rows({}, {}, setfam, applicable)
    declared = {str(row['id']) for row in applicable['fact_types']}
    assert set(matched) == declared, 'every fact type contributes a row (the census half)'
    for row in applicable['fact_types']:
        assert matched[str(row['id'])].applicable is bool(row['applicable'])
        if not row['applicable']:
            assert matched[str(row['id'])].reason == row['reason']
