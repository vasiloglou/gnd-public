from __future__ import annotations

import atexit
import gzip
import hashlib
import io
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import pytest

import gnd.api


def _materialize():
    path = Path(__file__).parent / "fixtures/public-redaction-reports/workspace.json.gz"
    assert path.is_file() and not path.is_symlink()
    with path.open("rb") as stream:
        packed = stream.read(16385)
    assert len(packed) <= 16384
    with gzip.GzipFile(fileobj=io.BytesIO(packed)) as stream:
        raw = stream.read(65537)
    assert len(raw) <= 65536
    assert hashlib.sha256(raw).hexdigest() == "86034c1913b781fd0208186de8e7be9333e922990cfe47292e88eb8e2f8eb49d"
    files = json.loads(raw)
    assert set(files) == {'populations/transition-post.yaml', 'steps/binding-only.json', 'measure/pool.phase4.pool.json', 'measure/index.json', 'batch/populations/02-band-2.yaml', 'batch/populations/00-band-0.yaml', 'populations/00-clean.yaml', 'batch/populations/01-band-1.yaml', 'measure/violating.json', 'measure/violating.meta.json', 'measure/z-conforming.meta.json', 'populations/transition-pre.yaml', 'steps/ill-formed.json', 'batch/populations/03-band-3.yaml', 'batch/populations/04-band-4.yaml', 'models/role-declaration.orm.yaml', 'measure/z-conforming.json', 'batch/model.orm.yaml'}
    assert all(isinstance(text, str) for text in files.values())
    temporary = tempfile.TemporaryDirectory(prefix="gnd-public-redaction-reports-")
    root = Path(temporary.name)
    fixture = root / "tests/fixtures/v61-phase4"
    for relative, text in files.items():
        path = fixture / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode("utf-8"))
        path.chmod(0o644)
    return temporary, root, fixture

_TEMPORARY, ROOT, FIXTURE = _materialize()
atexit.register(_TEMPORARY.cleanup)
CONTROL = Path(__file__).parent / "fixtures/public-emitter21"
CASES = json.loads((CONTROL / "cases.json").read_text(encoding="utf-8"))
ANSWERS = json.loads((CONTROL / "answers.json").read_text(encoding="utf-8"))
MODELS = {row["id"]: FIXTURE / row["path"] for row in CASES["models"]}
SNAPSHOTS = {row["id"]: row for row in CASES["snapshot_cases"]}
TRANSITIONS = {row["id"]: row for row in CASES["transition_cases"]}
SYNTHETIC_EXITS = {row["id"]: row for row in CASES["synthetic_exits"]}
SELECTED_CANARIES = tuple(ANSWERS["canaries"]["selected"])
MODEL = FIXTURE / "models/role-declaration.orm.yaml"
CLEAN = FIXTURE / "populations/00-clean.yaml"
TRANSITION_PRE = FIXTURE / "populations/transition-pre.yaml"
TRANSITION_POST = FIXTURE / "populations/transition-post.yaml"
TRANSITION_STEPS = FIXTURE / "steps/binding-only.json"


def _run_cli(*arguments: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run([sys.executable, '-m', 'gnd', *arguments], cwd=ROOT, capture_output=True, check=False)

def _payload(completed: subprocess.CompletedProcess[bytes]) -> dict[str, object]:
    value = json.loads(completed.stdout)
    assert isinstance(value, dict)
    return value

def _fixture_path(relative: str) -> str:
    return str((FIXTURE / relative).relative_to(ROOT))

def _assert_applied_bytes_are_safe(raw: bytes) -> None:
    assert not [token for token in SELECTED_CANARIES if token.encode() in raw]

def _contains(value: object, target: object) -> bool:
    if value == target:
        return True
    if isinstance(value, dict):
        return any(_contains(child, target) for child in value.values())
    if isinstance(value, list | tuple):
        return any(_contains(child, target) for child in value)
    return False

def test_steps_issue_omits_instance() -> None:
    case = TRANSITIONS['I-02']
    completed = _run_cli('check', str(MODELS[case['model']].relative_to(ROOT)), '--pre', _fixture_path(case['pre']), '--steps', _fixture_path(case['steps']), '--format', 'json')
    assert completed.returncode == case['expected_exit']
    payload = _payload(completed)
    assert payload['schema_version'] == ANSWERS['wire_versions']['report']
    assert payload['redaction'] == ANSWERS['applied_redaction']
    assert [{key: issue[key] for key in ('path', 'rule_id', 'severity', 'message')} for issue in payload['issues']] == [ANSWERS['structural_issues']['I-02']]
    _assert_applied_bytes_are_safe(completed.stdout + completed.stderr)

def test_missing_population_after_model_carries_redaction() -> None:
    case = SYNTHETIC_EXITS['X-03']
    completed = _run_cli('check', str(MODELS['M-01'].relative_to(ROOT)), 'tests/fixtures/v61-phase4/populations/does-not-exist.yaml', '--format', 'json')
    assert completed.returncode == case['expected_exit']
    payload = _payload(completed)
    assert payload['schema_version'] == ANSWERS['wire_versions']['report']
    assert payload['redaction'] == ANSWERS['applied_redaction']
    _assert_applied_bytes_are_safe(completed.stdout + completed.stderr)

def test_over_cap_population_after_model_omits_instance(tmp_path: Path) -> None:
    case = SYNTHETIC_EXITS['X-03']
    generator = case['generator']
    assert generator['kind'] == 'padded-yaml'
    canary = generator['canary'].encode()
    prefix = b'facts:\n  optional_code:\n    - {item: public, code: ' + canary + b'}\n#'
    document = prefix + b'x' * (generator['bytes'] - len(prefix))
    over_cap = tmp_path / 'over-cap.yaml'
    over_cap.write_bytes(document)
    assert over_cap.stat().st_size == generator['bytes']
    completed = _run_cli('check', str(MODELS['M-01'].relative_to(ROOT)), str(over_cap), '--format', 'json')
    assert completed.returncode == case['expected_exit']
    payload = _payload(completed)
    assert payload['schema_version'] == ANSWERS['wire_versions']['report']
    assert payload['redaction'] == ANSWERS['applied_redaction']
    assert canary not in completed.stdout + completed.stderr

def test_clean_transition_binding_is_projected() -> None:
    case = TRANSITIONS['B-01']
    completed = _run_cli('check', str(MODELS[case['model']].relative_to(ROOT)), '--pre', _fixture_path(case['pre']), '--steps', _fixture_path(case['steps']), '--post', _fixture_path(case['post']), '--format', 'json')
    assert completed.returncode == case['expected_exit']
    payload = _payload(completed)
    assert payload['schema_version'] == ANSWERS['wire_versions']['report']
    assert payload['redaction'] == ANSWERS['applied_redaction']
    assert _contains(payload['transition']['steps'], ANSWERS['marker'])
    assert b'P4_PUBLIC_TRANSITION_ITEM' in completed.stdout
    _assert_applied_bytes_are_safe(completed.stdout + completed.stderr)

def _assert_v9(payload: dict[str, Any], *, post: str | None) -> None:
    answer = ANSWERS['report_v9']
    assert payload['schema_version'] == ANSWERS['wire_versions']['report'] == 9
    assert set(payload) == set(answer['root_required_keys'])
    assert payload['post'] == post
    assert payload['redaction'] in (ANSWERS['applied_redaction'], ANSWERS['unredacted_redaction'])
    transition = payload['transition']
    assert isinstance(transition, dict)
    assert set(transition) == set(answer['transition_required_keys'])
    if post is None:
        assert transition['evaluated'] is False
        assert transition['frame_status'] is None
        assert transition['computed_post'] is None

def _assert_marker(marker: dict[str, Any]) -> None:
    assert set(marker) == {'redacted', 'roles'}
    assert marker['redacted'] is True
    assert marker['roles']
    assert marker['roles'] == sorted(set(marker['roles']))

def test_report_answer_contract_and_marker_checker_are_live() -> None:
    assert CASES['schema_version'] == ANSWERS['schema_version'] == 1
    assert ANSWERS['wire_versions']['report'] == 9
    assert len(ANSWERS['report_v9']['root_required_keys']) == len(set(ANSWERS['report_v9']['root_required_keys']))
    assert len(ANSWERS['report_v9']['transition_required_keys']) == len(set(ANSWERS['report_v9']['transition_required_keys']))
    assert ANSWERS['report_v9']['post_values'] == [None, 'declared', 'computed']
    _assert_marker(ANSWERS['marker'])
    with pytest.raises(AssertionError):
        _assert_marker(ANSWERS['dirty_controls']['marker'])

def test_report_v9_closed_shape() -> None:
    payloads = [(gnd.api.validate(MODEL), None), (gnd.api.check(MODEL, CLEAN), None), (gnd.api.transition(MODEL, TRANSITION_PRE, TRANSITION_STEPS, TRANSITION_POST), 'declared'), (gnd.api.transition(MODEL, TRANSITION_PRE, TRANSITION_STEPS, post=None), 'computed')]
    for payload, post in payloads:
        _assert_v9(payload, post=post)


def test_batch_v2_every_band() -> None:
    case = CASES['batch']
    completed = _run_cli('check', _fixture_path(case['model']), '--populations', _fixture_path(case['populations']), '--format', 'json')
    payload = _payload(completed)
    assert payload['schema_version'] == ANSWERS['wire_versions']['batch']
    assert payload['redaction'] == ANSWERS['applied_redaction']
    assert sorted(row['exit_code'] for row in payload['rows']) == case['expected_row_bands']
    assert ANSWERS['batch_v2'] == {'row_bands': case['expected_row_bands'], 'aggregate_exit': case['expected_exit']}
    assert completed.returncode == case['expected_exit']
    _assert_applied_bytes_are_safe(completed.stdout + completed.stderr)

def test_measurement_v3_json_and_text() -> None:
    case = CASES['measurement']
    measure_canaries = tuple(ANSWERS['measurement_v3']['selected_evidence_canaries'])
    assert set(measure_canaries) <= set(SELECTED_CANARIES)
    assert (FIXTURE / case['index']).is_file()
    for output_format in ('json', 'text'):
        outputs: dict[str, bytes] = {}
        for mode, extra in (('applied', ()), ('unredacted', ('--unredacted',))):
            completed = _run_cli('measure', _fixture_path(case['model']), '--populations', _fixture_path(case['corpus']), '--format', output_format, *extra)
            assert completed.returncode == case['expected_exit']
            outputs[mode] = completed.stdout + completed.stderr
        applied = outputs['applied']
        unredacted = outputs['unredacted']
        if output_format == 'json':
            payload = json.loads(applied)
            assert payload['schema_version'] == case['expected_wire_version']
            assert payload['schema_version'] == ANSWERS['wire_versions']['measurement']
            assert payload['redaction'] == ANSWERS['applied_redaction']
            assert payload['population_count'] == ANSWERS['measurement_v3']['corpus_rows']
            assert payload['pool_source'] == ANSWERS['measurement_v3']['pool_source']
        else:
            assert applied.startswith(ANSWERS['exact_text_prefixes']['applied'].encode())
            assert unredacted.startswith(ANSWERS['exact_text_prefixes']['unredacted'].encode())
        assert not [token for token in measure_canaries if token.encode() in applied]
        assert all(token.encode() in unredacted for token in measure_canaries)
