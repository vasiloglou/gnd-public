from __future__ import annotations

import itertools
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path
from types import SimpleNamespace

import pytest
from jsonschema import Draft202012Validator, ValidationError
from support.digests import sha256_file

from gnd import batch
from gnd.model import ValidationIssue
from gnd.population import MAX_POPULATION_BYTES

ROOT = Path(__file__).resolve().parents[1]
BATCH = ROOT / 'tests/fixtures/v61-phase1/batch'
CASES = json.loads((BATCH / 'cases.json').read_text(encoding='utf-8'))
ANSWERS = json.loads((BATCH / 'expected.json').read_text(encoding='utf-8'))

def _assert_lane_exists(result: subprocess.CompletedProcess[bytes]) -> None:
    parser_refusal = b'unrecognized arguments: --populations' in result.stderr
    assert not parser_refusal, 'expected corpus-first RED: the approved `gnd check --populations` production surface is still absent'

def _assert_exact(actual: bytes, expected: bytes) -> None:
    assert actual == expected

def _run(case: dict[str, object], tmp_path: Path) -> subprocess.CompletedProcess[bytes]:
    populations = tmp_path / 'populations'
    populations.mkdir()
    for filename in case['populations']:
        shutil.copyfile(BATCH / 'populations' / filename, populations / filename)
    return subprocess.run([sys.executable, '-m', 'gnd', 'check', str(BATCH / 'model.orm.yaml'), '--populations', str(populations), '--format', 'json'], cwd=ROOT, capture_output=True, check=False)

def test_batch_corpus_is_closed_and_pins_every_pair() -> None:
    assert CASES['precedence'] == [3, 1, 4, 2, 0]
    rows = CASES['cases']
    assert len(rows) == 11
    assert rows[0]['bands'] == [0, 1, 2, 3, 4]
    assert {tuple(row['bands']) for row in rows[1:]} == set(itertools.combinations(range(5), 2))
    answers = {row['id']: row for row in ANSWERS['cases']}
    assert set(answers) == {row['id'] for row in rows}
    for row in rows:
        document = json.loads((BATCH / row['expected_matrix']).read_text())
        assert document['summary']['aggregate_exit'] == row['expected_exit']
        assert [item['population'] for item in document['rows']] == row['populations']
        assert sha256_file(BATCH / row['expected_matrix']) == answers[row['id']]['matrix_sha256']

@pytest.mark.parametrize('band', range(5))
def test_each_projection_reaches_its_pinned_existing_band(band: int) -> None:
    population = BATCH / 'populations' / f'0{band}-band-{band}.yaml'
    result = subprocess.run([sys.executable, '-m', 'gnd', 'check', str(BATCH / 'model.orm.yaml'), str(population), '--format', 'json'], cwd=ROOT, capture_output=True, text=True, check=False)
    assert result.returncode == band
    assert json.loads(result.stdout)['exit_code'] == band

def test_batch_harness_negative_control_rejects_one_dirty_byte() -> None:
    expected = (BATCH / 'expected.matrix.json').read_bytes()
    with pytest.raises(AssertionError):
        _assert_exact(expected + b' ', expected)

@pytest.mark.parametrize('case', CASES['cases'], ids=lambda row: row['id'])
def test_batch_matrix_case(case: dict[str, object], tmp_path: Path) -> None:
    result = _run(case, tmp_path)
    _assert_lane_exists(result)
    assert result.returncode == case['expected_exit'], result.stderr.decode()
    _assert_exact(result.stdout, (BATCH / case['expected_matrix']).read_bytes())

def test_batch_schema_is_closed_and_all_expected_matrices_validate() -> None:
    schema = json.loads((ROOT / 'src/gnd/batch-report.schema.json').read_text())
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    for case in CASES['cases']:
        validator.validate(json.loads((BATCH / case['expected_matrix']).read_text()))
    sample = json.loads((BATCH / CASES['cases'][0]['expected_matrix']).read_text())
    for dirty in ({**sample, 'surprise': True}, {key: value for key, value in sample.items() if key != 'rows'}, {**sample, 'schema_version': '1'}, {**sample, 'model': {**sample['model'], 'sha256': 7}}, {**sample, 'model': {**sample['model'], 'surprise': True}}, {**sample, 'model': {key: value for key, value in sample['model'].items() if key != 'filename'}}, {**sample, 'rows': [{**sample['rows'][0], 'surprise': True}]}, {**sample, 'rows': [{**sample['rows'][0], 'population': 7}, *sample['rows'][1:]]}, {**sample, 'rows': [{**sample['rows'][0], 'counts': {**sample['rows'][0]['counts'], 'surprise': 1}}, *sample['rows'][1:]]}, {**sample, 'rows': [{**sample['rows'][0], 'counts': {key: value for key, value in sample['rows'][0]['counts'].items() if key != 'pass'}}, *sample['rows'][1:]]}, {**sample, 'rows': [{**sample['rows'][0], 'issues': [{**sample['rows'][3]['issues'][0], 'surprise': True}]}, *sample['rows'][1:]]}, {**sample, 'rows': [{**sample['rows'][0], 'issues': [{key: value for key, value in sample['rows'][3]['issues'][0].items() if key != 'severity'}]}, *sample['rows'][1:]]}, {**sample, 'summary': {**sample['summary'], 'surprise': True}}, {**sample, 'summary': {key: value for key, value in sample['summary'].items() if key != 'projections'}}, {**sample, 'summary': {**sample['summary'], 'outcomes': {**sample['summary']['outcomes'], 'surprise': 1}}}, {**sample, 'summary': {**sample['summary'], 'outcomes': {key: value for key, value in sample['summary']['outcomes'].items() if key != 'accepted'}}}):
        with pytest.raises(ValidationError):
            validator.validate(dirty)

def test_batch_command_level_failures_emit_no_partial_matrix(tmp_path: Path) -> None:
    empty = tmp_path / 'empty'
    empty.mkdir()

    def run(model: Path, populations: Path, *, output_format: str='json') -> subprocess.CompletedProcess[bytes]:
        return subprocess.run([sys.executable, '-m', 'gnd', 'check', str(model), '--populations', str(populations), '--format', output_format], cwd=ROOT, capture_output=True, check=False)
    no_rows = run(BATCH / 'model.orm.yaml', empty)
    assert no_rows.returncode == 64 and no_rows.stdout == b''
    absent = run(BATCH / 'model.orm.yaml', tmp_path / 'absent')
    assert absent.returncode == 66 and absent.stdout == b''
    broken_root = tmp_path / 'broken-root'
    broken_root.symlink_to(tmp_path / 'no-directory', target_is_directory=True)
    broken = run(BATCH / 'model.orm.yaml', broken_root)
    assert broken.returncode == 74 and broken.stdout == b''
    text = run(BATCH / 'model.orm.yaml', BATCH / 'populations', output_format='text')
    assert text.returncode == 64 and text.stdout == b''
    linked = tmp_path / 'linked'
    linked.mkdir()
    (linked / 'case.yaml').symlink_to(BATCH / 'populations/00-band-0.yaml')
    refused = run(BATCH / 'model.orm.yaml', linked)
    assert refused.returncode == 74 and refused.stdout == b''
    valid = tmp_path / 'valid'
    valid.mkdir()
    shutil.copyfile(BATCH / 'populations/00-band-0.yaml', valid / 'case.yaml')
    missing_model = run(tmp_path / 'missing.orm.yaml', valid)
    assert missing_model.returncode == 66 and missing_model.stdout == b''
    linked_model = tmp_path / 'linked.orm.yaml'
    linked_model.symlink_to(BATCH / 'model.orm.yaml')
    refused_model = run(linked_model, valid)
    assert refused_model.returncode == 74 and refused_model.stdout == b''

def test_invalid_model_is_a_band_three_zero_row_envelope(tmp_path: Path) -> None:
    populations = tmp_path / 'populations'
    populations.mkdir()
    shutil.copyfile(BATCH / 'populations/00-band-0.yaml', populations / 'case.yaml')
    model = tmp_path / 'bad.orm.yaml'
    model.write_text('version: nope\n', encoding='utf-8')
    result = subprocess.run([sys.executable, '-m', 'gnd', 'check', str(model), '--populations', str(populations), '--format', 'json'], cwd=ROOT, capture_output=True, check=False)
    payload = json.loads(result.stdout)
    assert result.returncode == 3
    assert payload['rows'] == []
    assert payload['summary']['projections'] == 0
    assert payload['issues']

def test_unexpected_population_loader_failure_is_internal(monkeypatch: pytest.MonkeyPatch) -> None:

    def fail_loader(*_args: object, **_kwargs: object) -> object:
        raise RuntimeError('injected loader invariant')
    monkeypatch.setattr(batch, 'load_population', fail_loader)
    with pytest.raises(batch.BatchInternalError, match='injected loader invariant'):
        batch.check_population_directory(BATCH / 'model.orm.yaml', BATCH / 'populations')

def test_nested_population_paths_are_relative_and_lexically_sorted(tmp_path: Path) -> None:
    populations = tmp_path / 'populations'
    (populations / 'z').mkdir(parents=True)
    (populations / 'a').mkdir()
    shutil.copyfile(BATCH / 'populations/00-band-0.yaml', populations / 'z/case.yaml')
    shutil.copyfile(BATCH / 'populations/00-band-0.yaml', populations / 'a/case.yaml')
    result = batch.check_population_directory(BATCH / 'model.orm.yaml', populations)
    assert [row.population for row in result.rows] == ['a/case.yaml', 'z/case.yaml']
    assert str(tmp_path) not in json.dumps(batch.build_batch_payload(result))

def test_nonregular_population_candidate_is_io(tmp_path: Path) -> None:
    populations = tmp_path / 'populations'
    populations.mkdir()
    (populations / 'case.yaml').mkdir()
    with pytest.raises(batch.BatchIOError, match='not a regular file'):
        batch.check_population_directory(BATCH / 'model.orm.yaml', populations)

def test_unexpected_checker_failure_is_internal_without_payload(monkeypatch: pytest.MonkeyPatch) -> None:

    def fail_checker(*_args: object, **_kwargs: object) -> object:
        raise RuntimeError('injected checker invariant')
    monkeypatch.setattr(batch, 'check', fail_checker)
    with pytest.raises(batch.BatchInternalError, match='injected checker invariant'):
        batch.check_population_directory(BATCH / 'model.orm.yaml', BATCH / 'populations')

def test_serializer_rejects_aggregate_invariant() -> None:
    row = batch.BatchRow('case.yaml', 0, 'accepted', {}, (), ())
    result = batch.BatchResult('model.orm.yaml', '0' * 64, (row,), 3, ())
    with pytest.raises(batch.BatchInternalError, match='aggregate exit'):
        batch.build_batch_payload(result)

def test_hostile_json_integer_is_an_ill_formed_row(tmp_path: Path) -> None:
    populations = tmp_path / 'populations'
    populations.mkdir()
    (populations / 'huge.json').write_bytes(b'{"population":{"model":"x","source":"x"},"instances":{},"facts":{},"n":' + b'9' * 5000 + b'}\n')
    result = batch.check_population_directory(BATCH / 'model.orm.yaml', populations)
    assert result.aggregate_exit == 3
    assert result.rows[0].exit_code == 3
    assert result.rows[0].issues[0]['rule_id'] == 'population:parse'

def test_batch_error_payloads_are_path_neutral(tmp_path: Path) -> None:
    populations = tmp_path / 'populations'
    populations.mkdir()
    (populations / 'alias.yaml').write_text('population: &p {model: x, source: x}\ncopy: *p\n', encoding='utf-8')
    result = batch.check_population_directory(BATCH / 'model.orm.yaml', populations)
    payload = json.dumps(batch.build_batch_payload(result))
    assert str(tmp_path) not in payload
    assert str(ROOT) not in payload

def test_invalid_model_precedes_empty_population_enumeration(tmp_path: Path) -> None:
    populations = tmp_path / 'populations'
    populations.mkdir()
    model = tmp_path / 'bad.orm.yaml'
    model.write_text('version: nope\n', encoding='utf-8')
    result = batch.check_population_directory(model, populations)
    assert result.aggregate_exit == 3
    assert result.rows == ()

def test_model_replacement_during_load_is_refused(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    model = tmp_path / 'model.orm.yaml'
    shutil.copyfile(BATCH / 'model.orm.yaml', model)
    real_load = batch.load_model

    def load_then_replace(path: Path) -> object:
        loaded = real_load(path)
        path.write_text('version: nope\n', encoding='utf-8')
        return loaded
    monkeypatch.setattr(batch, 'load_model', load_then_replace)
    with pytest.raises(batch.BatchIOError, match='changed'):
        batch.check_population_directory(model, BATCH / 'populations')

def test_model_is_loaded_exactly_once(monkeypatch: pytest.MonkeyPatch) -> None:
    real_load = batch.load_model
    calls = 0

    def counted(path: Path) -> object:
        nonlocal calls
        calls += 1
        return real_load(path)
    monkeypatch.setattr(batch, 'load_model', counted)
    batch.check_population_directory(BATCH / 'model.orm.yaml', BATCH / 'populations')
    assert calls == 1

def test_issue_projection_is_capped_at_200() -> None:
    issues = [ValidationIssue(path='$', message=str(index), rule_id='test') for index in range(201)]
    assert len(batch._issue_records(issues)) == 200

def test_duplicate_failing_constraints_are_emitted_once(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    populations = tmp_path / 'populations'
    populations.mkdir()
    shutil.copyfile(BATCH / 'populations/00-band-0.yaml', populations / 'case.yaml')
    report = SimpleNamespace(verdicts=[SimpleNamespace(verdict='fail', constraint_ref='constraint/x'), SimpleNamespace(verdict='fail', constraint_ref='constraint/x')], counts=lambda: {'pass': 0, 'fail': 2, 'warning': 0, 'unchecked': 0, 'vacuous': 0})
    monkeypatch.setattr(batch, 'check', lambda *_args: report)
    monkeypatch.setattr(batch, 'checker_band', lambda _report: 1)
    result = batch.check_population_directory(BATCH / 'model.orm.yaml', populations)
    assert result.rows[0].failing_constraints == ('constraint/x',)

def test_unreadable_population_is_a_command_io_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(batch, 'load_population', lambda *_args, **_kwargs: (_ for _ in ()).throw(PermissionError('injected unreadable')))
    with pytest.raises(batch.BatchIOError, match='injected unreadable'):
        batch.check_population_directory(BATCH / 'model.orm.yaml', BATCH / 'populations')

def test_batch_hot_paths_do_not_rescan_accumulators() -> None:
    source = (ROOT / 'src/gnd/batch.py').read_text(encoding='utf-8')
    assert 'verdict.constraint_ref not in failing' not in source


def test_many_legal_exact_cap_populations_are_processed_serially(tmp_path: Path) -> None:
    populations = tmp_path / 'populations'
    populations.mkdir()
    base = (BATCH / 'populations/00-band-0.yaml').read_bytes()
    data = base + b'#' + b'x' * (MAX_POPULATION_BYTES - len(base) - 2) + b'\n'
    for index in range(3):
        (populations / f'{index}.yaml').write_bytes(data)
    started = time.monotonic()
    result = batch.check_population_directory(BATCH / 'model.orm.yaml', populations)
    assert time.monotonic() - started < 30
    assert len(result.rows) == 3 and result.aggregate_exit == 0
