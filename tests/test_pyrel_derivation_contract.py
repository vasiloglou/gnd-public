"""Red-first subprocess/output contract for the third derivation-parity seat.

All subprocesses are replaced before invocation; these default-suite tests never
execute uv or PyRel. Presence is asserted outside refusal contexts so a missing
driver cannot accidentally satisfy a negative control.
"""
from __future__ import annotations

import json
import os
import shutil
import signal
import subprocess
from pathlib import Path
from typing import Any

import pytest
import support.pyrel_contract as parity

CASE = parity.CORPUS / 'cases' / 'wire-v4-structured-check'
MODEL = CASE / 'model.orm.yaml'
POPULATION = CASE / 'population.yaml'
TOKEN = '["string","λ"]'
LIMIT = 4 * 1024 * 1024
REFUSALS = (AssertionError, ValueError, RuntimeError)

def _driver() -> Any:
    driver = getattr(parity, '_pyrel_extensions', None)
    assert callable(driver), 'Phase 3 PyRel raw-path driver does not exist'
    return driver

def _document(rows: list[list[str]] | None=None) -> dict[str, Any]:
    return {'schema_version': 1, 'backend': 'pyrel', 'version': '1.30.1', 'extensions': {'result': [] if rows is None else rows}}

def _fake_process(monkeypatch: pytest.MonkeyPatch, raw: str | bytes | None, *, returncode: int=0, timeout: bool=False) -> list[dict[str, Any]]:
    calls: list[dict[str, Any]] = []
    monkeypatch.setattr(shutil, 'which', lambda name: '/mock/uv' if name == 'uv' else None)

    class FakePopen:
        pid = 4242

        def __init__(self, argv: Any, **kwargs: Any) -> None:
            self.args = [str(arg) for arg in argv]
            self.output = Path(self.args[self.args.index('--out') + 1])
            self.returncode = returncode
            self.timed_out = False
            calls.append({'argv': self.args, 'kwargs': kwargs, 'output': self.output, 'communicate_timeouts': [], 'killed': []})

        def communicate(self, timeout: int | None=None) -> tuple[str, str]:
            calls[-1]['communicate_timeouts'].append(timeout)
            if timeout is not None and should_timeout and (not self.timed_out):
                self.timed_out = True
                raise subprocess.TimeoutExpired(self.args, timeout=timeout)
            if raw is not None:
                self.output.write_bytes(raw.encode('utf-8') if isinstance(raw, str) else raw)
            return ('', 'fixture failure')
    should_timeout = timeout
    monkeypatch.setattr(subprocess, 'Popen', FakePopen)
    monkeypatch.setattr(os, 'killpg', lambda pid, sig: calls[-1]['killed'].append((pid, sig)))
    return calls

@pytest.mark.parametrize('rows', [[], [[TOKEN]]], ids=['empty-head', 'nonempty-head'])
def test_pyrel_output_accepts_complete_valid_extensions(monkeypatch: pytest.MonkeyPatch, rows: list[list[str]]) -> None:
    driver = _driver()
    _fake_process(monkeypatch, json.dumps(_document(rows)))
    assert driver(MODEL, POPULATION) == {'result': tuple(tuple(row) for row in rows)}

def _invalid_documents() -> list[Any]:
    documents: list[Any] = [None, [], {}, {**_document(), 'schema_version': 2}, {**_document(), 'schema_version': True}, {**_document(), 'backend': 'duckdb'}, {**_document(), 'version': '1.30.0'}, {**_document(), 'version': None}, {**_document(), 'extensions': {}}, {**_document(), 'extensions': {'result': [], 'invented': []}}, {**_document(), 'extensions': []}, {**_document(), 'extensions': {'result': None}}, {**_document(), 'extensions': {'result': [TOKEN]}}, _document([[]]), _document([[TOKEN, TOKEN]]), _document([[TOKEN], [TOKEN]]), _document([['["string","z"]'], ['["string","a"]']]), _document([['["number",[1,1]]']])]
    for token in ['not-json', 'null', '"scalar"', '["invented","x"]', '["string",1]', '["boolean",1]', '["number",[1,0]]', '["number",[1,-1]]', '["number",[2,2]]', '["number",[true,1]]', '["string", "noncanonical"]']:
        documents.append(_document([[token]]))
    documents.append(_document([[1]]))
    return documents

@pytest.mark.parametrize('document', _invalid_documents(), ids=['null-envelope', 'array-envelope', 'missing-fields', 'wrong-schema', 'boolean-schema', 'wrong-backend', 'wrong-pin', 'missing-version', 'missing-head', 'extra-head', 'array-extensions', 'null-rows', 'scalar-row', 'short-row', 'long-row', 'duplicate-row', 'unsorted-row', 'role-incompatible-token', 'malformed-token', 'null-token', 'scalar-token', 'unknown-token-tag', 'wrong-string-type', 'wrong-boolean-type', 'zero-denominator', 'negative-denominator', 'unreduced-number', 'boolean-numerator', 'noncanonical-token-json', 'nonstring-token'])
def test_pyrel_output_refuses_invalid_envelope_heads_rows_and_tokens(monkeypatch: pytest.MonkeyPatch, document: Any) -> None:
    driver = _driver()
    _fake_process(monkeypatch, json.dumps(document))
    with pytest.raises(REFUSALS):
        driver(MODEL, POPULATION)

@pytest.mark.parametrize('raw', ['{', b'\xff', '{"schema_version":1,"schema_version":1,"backend":"pyrel","version":"1.30.1","extensions":{"result":[]}}', '{"schema_version":1,"backend":"pyrel","version":"1.30.1","extensions":{"result":[],"result":[]}}', json.dumps(_document()) + '\n{}'], ids=['malformed-json', 'invalid-utf8', 'duplicate-envelope-key', 'duplicate-head-key', 'trailing-document'])
def test_pyrel_output_refuses_malformed_or_duplicate_json(monkeypatch: pytest.MonkeyPatch, raw: str | bytes) -> None:
    driver = _driver()
    _fake_process(monkeypatch, raw)
    with pytest.raises((*REFUSALS, UnicodeError)):
        driver(MODEL, POPULATION)

def test_pyrel_driver_preserves_raw_argv_and_isolates_scratch(monkeypatch: pytest.MonkeyPatch) -> None:
    driver = _driver()
    monkeypatch.setenv('PHASE3_PARENT_SENTINEL', 'inherited')
    monkeypatch.setenv('RAI_BUILD_DIR', '/must-not-use-parent-build')
    calls = _fake_process(monkeypatch, json.dumps(_document()))
    assert driver(MODEL, POPULATION) == {'result': ()}
    assert len(calls) == 1
    call = calls[0]
    argv, kwargs = (call['argv'], call['kwargs'])
    assert argv[:4] == ['/mock/uv', 'run', '--locked', '--script']
    assert Path(argv[4]).name == 'pyrel_derivation_oracle.py'
    assert argv[5:7] == [str(MODEL), str(POPULATION)]
    assert argv[7] == '--out'
    assert kwargs.get('shell', False) is False
    assert kwargs['start_new_session'] is True
    assert call['communicate_timeouts'] == [120]
    assert kwargs['env']['PHASE3_PARENT_SENTINEL'] == 'inherited'
    build = Path(kwargs['env']['RAI_BUILD_DIR'])
    assert build.is_absolute()
    assert build != Path(os.environ['RAI_BUILD_DIR'])
    assert build == call['output'].parent or call['output'].parent in build.parents
    assert not call['output'].exists(), 'result must be owned by a cleaned temporary directory'
    assert not build.exists(), 'PyRel build directory must be temporary'

@pytest.mark.parametrize('raw', [None, '{'], ids=['missing-output', 'malformed-output'])
def test_pyrel_process_nonzero_is_checked_before_output(monkeypatch: pytest.MonkeyPatch, raw: str | None) -> None:
    driver = _driver()
    _fake_process(monkeypatch, raw, returncode=23)
    with pytest.raises((*REFUSALS, subprocess.CalledProcessError), match='23'):
        driver(MODEL, POPULATION)

def test_pyrel_process_timeout_is_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    driver = _driver()
    calls = _fake_process(monkeypatch, None, timeout=True)
    with pytest.raises((*REFUSALS, subprocess.TimeoutExpired)):
        driver(MODEL, POPULATION)
    assert calls[0]['communicate_timeouts'] == [120, None]
    assert calls[0]['killed'] == [(4242, signal.SIGKILL)]

def test_pyrel_success_without_output_is_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    driver = _driver()
    _fake_process(monkeypatch, None)
    with pytest.raises((*REFUSALS, FileNotFoundError)):
        driver(MODEL, POPULATION)

def test_pyrel_output_read_is_bounded(monkeypatch: pytest.MonkeyPatch) -> None:
    driver = _driver()
    calls = _fake_process(monkeypatch, json.dumps(_document()) + ' ' * (LIMIT + 1))
    original_open = Path.open
    reads: list[int] = []

    class BoundedReader:

        def __init__(self, wrapped: Any) -> None:
            self.wrapped = wrapped

        def __enter__(self) -> Any:
            self.wrapped.__enter__()
            return self

        def __exit__(self, *args: object) -> Any:
            return self.wrapped.__exit__(*args)

        def read(self, size: int=-1) -> Any:
            reads.append(size)
            return self.wrapped.read(size)

        def __getattr__(self, name: str) -> Any:
            return getattr(self.wrapped, name)

    def tracked_open(path: Path, *args: Any, **kwargs: Any) -> Any:
        opened = original_open(path, *args, **kwargs)
        mode = args[0] if args else kwargs.get('mode', 'r')
        if calls and path == calls[-1]['output'] and ('r' in mode):
            return BoundedReader(opened)
        return opened
    monkeypatch.setattr(Path, 'open', tracked_open)
    with pytest.raises(REFUSALS):
        driver(MODEL, POPULATION)
    assert reads and all(0 < size <= LIMIT + 1 for size in reads)
    assert sum(reads) <= LIMIT + 1
