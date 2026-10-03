from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

import gnd.declared_adapter as declared
from gnd.exp.adapter_policy import OpenAICompatiblePolicy, ResolvedAdapterPolicy


class _Reader:

    def __init__(self, data: bytes=b'') -> None:
        self.data = data

    async def read(self, size: int) -> bytes:
        if not self.data:
            await asyncio.Event().wait()
        data, self.data = (self.data[:size], self.data[size:])
        return data

    async def readexactly(self, size: int) -> bytes:
        if len(self.data) < size:
            raise asyncio.IncompleteReadError(self.data, size)
        data, self.data = (self.data[:size], self.data[size:])
        return data

class _Writer:

    def __init__(self, *, hanging_close: bool=False) -> None:
        self.hanging_close = hanging_close
        self.wire = bytearray()

    def write(self, data: bytes) -> None:
        self.wire.extend(data)

    async def drain(self) -> None:
        return

    def close(self) -> None:
        return

    async def wait_closed(self) -> None:
        if self.hanging_close:
            await asyncio.Event().wait()

def _resolved_http(credential: str='secret') -> ResolvedAdapterPolicy:
    resolved = ResolvedAdapterPolicy(policy=OpenAICompatiblePolicy(schema_version=1, policy_id='local-openai', kind='openai-compatible', base_url='http://127.0.0.1:8765/v1', credential_env='PHASE6_API_KEY'), policy_sha256='0' * 64, model='stub-model-1')
    resolved._credential_value = credential
    return resolved

def test_review_http_cleanup_cannot_outlive_attempt_deadline(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    writer = _Writer(hanging_close=True)

    async def connect(*_args, **_kwargs):
        return (_Reader(), writer)
    monkeypatch.setattr(declared.asyncio, 'open_connection', connect)

    async def exercise():
        return await asyncio.wait_for(declared.invoke_declared_adapter(_resolved_http(), prompt='p', cwd=tmp_path, timeout_seconds=0.01), timeout=0.15)
    result = asyncio.run(exercise())
    assert result.status == 'timed-out'

def test_review_malformed_chunk_terminator_is_refused() -> None:

    async def exercise() -> None:
        reader = asyncio.StreamReader()
        reader.feed_data(b'HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n\r\n2\r\n{}\r\n0\r\nBROKEN')
        reader.feed_eof()
        with pytest.raises(declared.OpenAIResponseError, match='chunk'):
            await declared._read_http_response(reader)
    asyncio.run(exercise())

def test_review_deep_response_json_is_a_closed_failure(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    body = b'[' * 10000 + b']' * 10000
    wire = b'HTTP/1.1 200 OK\r\nContent-Length: ' + str(len(body)).encode() + b'\r\n\r\n' + body

    async def connect(*_args, **_kwargs):
        return (_Reader(wire), _Writer())
    monkeypatch.setattr(declared.asyncio, 'open_connection', connect)
    result = asyncio.run(declared.invoke_declared_adapter(_resolved_http(), prompt='p', cwd=tmp_path, timeout_seconds=1))
    assert result.status == 'failed'
    assert result.spawn_error == 'OpenAIResponseError'

def test_review_http_request_bytes_count_the_wire(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    writer = _Writer()

    async def connect(*_args, **_kwargs):
        return (_Reader(b'HTTP/1.1 503 Nope\r\nContent-Length: 0\r\n\r\n'), writer)
    monkeypatch.setattr(declared.asyncio, 'open_connection', connect)
    result = asyncio.run(declared.invoke_declared_adapter(_resolved_http(), prompt='p', cwd=tmp_path, timeout_seconds=1))
    assert result.request_bytes == len(writer.wire)

def test_review_bundle_version_requires_exact_integer(tmp_path: Path) -> None:
    with pytest.raises(declared.CandidateBundleError, match='schema version'):
        declared.apply_candidate_bundle('{"schema_version":true,"files":[]}', candidate_root=tmp_path)
