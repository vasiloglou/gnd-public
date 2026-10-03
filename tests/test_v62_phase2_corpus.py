from __future__ import annotations

import copy
import json

import pytest
from support.v62_phase2_corpus import ANSWERS, CASES, CASES_DOC, FIXTURE

EXPECTED_IDS = {'A01', 'A02', *(f'B{index:02d}' for index in range(1, 7)), *(f'C{index:02d}' for index in range(1, 4)), *(f'D{index:02d}' for index in range(1, 4)), *(f'E{index:02d}' for index in range(1, 8)), *(f'F{index:02d}' for index in range(1, 3)), *(f'G{index:02d}' for index in range(1, 9)), *(f'H{index:02d}' for index in range(1, 4)), *(f'I{index:02d}' for index in range(1, 7)), *(f'M{index:02d}' for index in range(1, 4)), *(f'P{index:02d}' for index in range(1, 4)), *(f'Q{index:02d}' for index in range(1, 6)), 'R01', 'K01', *(f'S{index:02d}' for index in range(1, 4)), *(f'V{index:02d}' for index in range(1, 3))}

def _check_answers(answers: dict[str, object]) -> None:
    assert set(answers) == EXPECTED_IDS
    for case_id, answer in answers.items():
        assert isinstance(answer, dict) and answer, case_id

def test_case_and_answer_manifests_are_closed() -> None:
    assert CASES_DOC['schema_version'] == 1
    assert set(CASES) == set(ANSWERS) == EXPECTED_IDS
    assert len(CASES) == len({row['branch'] for row in CASES.values()})
    _check_answers(ANSWERS)

def test_every_fixture_coordinate_resolves() -> None:
    assert (FIXTURE / CASES_DOC['model']).is_file()
    assert (FIXTURE / CASES_DOC['steps']).is_file()
    for path in CASES_DOC['populations'].values():
        assert (FIXTURE / path).is_file()

def test_readme_narrates_every_family_without_machine_answers() -> None:
    narrative = (FIXTURE / 'README.md').read_text(encoding='utf-8')
    for prefix in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'M', 'P', 'Q', 'R', 'K', 'S'):
        assert prefix in narrative
    for forbidden in ('"exit"', '"band"', '"rule_id"'):
        assert forbidden not in narrative

def test_dirty_answer_control_is_live() -> None:
    dirty = copy.deepcopy(ANSWERS)
    dirty.pop('A01')
    with pytest.raises(AssertionError):
        _check_answers(dirty)

def test_json_files_are_canonical_and_newline_terminated() -> None:
    for relative in ('cases.json', 'answers.json', 'walks/ticket.steps.json'):
        raw = (FIXTURE / relative).read_bytes()
        assert raw.endswith(b'\n')
        assert json.loads(raw) is not None
