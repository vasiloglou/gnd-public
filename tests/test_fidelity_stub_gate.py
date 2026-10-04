from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

import pytest

from gnd.cli import main

REPO_ROOT = Path(__file__).resolve().parent.parent
MODEL = REPO_ROOT / 'tests' / 'fixtures' / 'checker' / 'setfam.orm.yaml'
ROUNDTRIP = REPO_ROOT / 'tests' / 'fixtures' / 'roundtrip'
ARTIFACTS = ROUNDTRIP / 'artifacts'
STEM = 'setfam'
ABSENT_FACT_DISTRACTOR = 'Person 2 does not teach course C1.'
NEAR_MISS_DISTRACTOR = 'Room R2'

def run(case: str, tmp_path: Path) -> dict[str, Any]:
    cases = tmp_path / 'cases'
    shutil.copytree(ROUNDTRIP / case, cases / case)
    out = tmp_path / 'fidelity.json'
    code = main(['fidelity', str(MODEL), '--cases', str(cases), '--artifacts', str(ARTIFACTS), '--format', 'json', '--out', str(out)])
    assert code == 0, f'gnd fidelity over the {case} case exited {code}'
    payload = json.loads(out.read_text(encoding='utf-8'))
    assert payload['cases'] == {'ran': 1, 'skipped': 0, 'failed': 0, 'reasons': []}, 'the case did not RUN, so any rate below describes nothing — check the committed digests with tests/fixtures/roundtrip/build_fixtures.py'
    return payload

def rows(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {row['id']: row for row in payload['per_fact_type']}

def test_the_committed_artifact_bundle_is_not_stale(tmp_path: Path) -> None:
    fresh = tmp_path / 'fresh'
    model_arg = MODEL.relative_to(REPO_ROOT).as_posix()
    assert main(['extract', model_arg, '--out', str(fresh)]) == 0
    committed = sorted(path.name for path in ARTIFACTS.iterdir())
    assert committed == [f'{STEM}.applicable.json', f'{STEM}.artifacts.json', f'{STEM}.projection.schema.json']
    for rel in committed:
        assert (ARTIFACTS / rel).read_bytes() == (fresh / rel).read_bytes(), f'tests/fixtures/roundtrip/artifacts/{rel} is stale — regenerate with: uv run python tests/fixtures/roundtrip/build_fixtures.py'

def test_stub_extractor_scores_below_one_precision(tmp_path: Path) -> None:
    payload = run('hoover', tmp_path)
    by_id = rows(payload)
    teaches = by_id['person_teaches_course']
    assert teaches['precision']['rate'] is not None
    assert teaches['precision']['rate'] < 1.0, f'the hoover swallowed the absent-fact distractor ({ABSENT_FACT_DISTRACTOR!r}) and still scored perfect precision — the extraction (person 2, course C1) is well-resolved and has no source counterpart, so it must sit in the denominator as unmatched'
    assert teaches['precision'] == {'numerator': 1, 'denominator': 2, 'rate': 0.5}
    assert teaches['matched']['unmatched'] == 1
    assert teaches['recall'] == {'numerator': 1, 'denominator': 1, 'rate': 1.0}, 'recall is untouched: the hoover found the real fact too. Precision is the direction distractors move, which is why R-05 names precision'
    seats = by_id['room_has_seats']
    assert seats['precision']['rate'] == 0.5, f'the hoover swallowed the near-miss distractor ({NEAR_MISS_DISTRACTOR!r}) and precision did not fall — an unresolved extraction must stay in the denominator (INCLUSIVE precision, PANEL-5); excluding it publishes 1.0 for an extraction that invented a room'
    assert seats['matched']['unresolved'] == 1
    assert seats['matched']['unmatched'] == 0
    below = [row['id'] for row in payload['per_fact_type'] if row['applicable'] and (row['precision']['rate'] or 1.0) < 1.0]
    assert below == ['person_teaches_course', 'room_has_seats'], 'exactly the two fact types the distractors touch may fall — a gate that reds everywhere is measuring the fixture, not the extractor'
    assert by_id['booking_by_person']['precision']['rate'] == 1.0
    assert by_id['booking_of_room']['precision']['rate'] == 1.0

def test_faithful_stub_scores_exactly_one(tmp_path: Path) -> None:
    payload = run('faithful', tmp_path)
    by_id = rows(payload)
    scored = [row for row in payload['per_fact_type'] if row['applicable'] and row['matched']['source_total'] > 0]
    assert len(scored) == 5, 'the control must exercise several fact types; a control resting on one row could pass on a matcher that resolves one identity path'
    for row in scored:
        assert row['precision']['rate'] == 1.0, f"{row['id']} precision"
        assert row['recall']['rate'] == 1.0, f"{row['id']} recall"
        assert row['matched']['unmatched'] == 0
        assert row['matched']['unresolved'] == 0
        assert row['matched']['ambiguous'] == 0
        assert row['matched']['missed'] == 0
    assert by_id['booking_by_person']['matched']['tp'] == 1, 'the composite identity matched across a renamed surrogate token'
    assert payload['publishable'] is False
    assert payload['calibration']['state'] == 'uncalibrated'

def test_the_gate_tells_the_two_extractions_apart(tmp_path: Path) -> None:
    hoover = rows(run('hoover', tmp_path / 'h'))
    faithful = rows(run('faithful', tmp_path / 'f'))
    moved = [fact_type_id for fact_type_id in hoover if hoover[fact_type_id]['precision'] != faithful[fact_type_id]['precision']]
    assert moved == ['person_teaches_course', 'room_has_seats']
    for fact_type_id in moved:
        assert faithful[fact_type_id]['precision']['rate'] == 1.0
        assert hoover[fact_type_id]['precision']['rate'] == 0.5

@pytest.mark.parametrize('case', ['hoover', 'faithful'])
def test_the_committed_documents_discharge_the_renderer_obligations(case: str, tmp_path: Path) -> None:
    assert main(['doccheck', str(MODEL), str(ROUNDTRIP / case / 'document.manifest.json'), '--artifacts', str(ARTIFACTS)]) == 0
