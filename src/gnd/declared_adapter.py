"""Caller-selected command and one-turn OpenAI-compatible adapters.

This module is intentionally outside :mod:`gnd.exp`. The deterministic
experiment package owns contracts, verification and persisted evidence while
the CLI injects this live invocation edge.
"""

from __future__ import annotations

import asyncio
import base64
import hashlib
import json
import math
import os
import secrets
import ssl
import stat
import time
from pathlib import Path, PurePosixPath, PureWindowsPath
from urllib.parse import urlsplit

from gnd import input_policy as _rf7_input
from gnd.agents import AgentCLIError, InvocationStatus
from gnd.artifacts import canonical_json_bytes, reject_json_constant, reject_json_duplicate_pairs
from gnd.exp.adapter_policy import (
    CommandAdapterPolicy,
    OpenAICompatiblePolicy,
    ResolvedAdapterPolicy,
)
from gnd.exp.declared_invocation import DeclaredInvocationResult, declared_effective_prompt
from gnd.process import BoundedProcessResult, ProcessLimits, run_bounded_process

__all__ = [
    "MAX_BUNDLE_FILES",
    "MAX_BUNDLE_PATH_BYTES",
    "MAX_BUNDLE_TOTAL_BYTES",
    "MAX_HTTP_HEADER_BYTES",
    "MAX_HTTP_RESPONSE_BYTES",
    "CandidateBundleError",
    "OpenAIResponseError",
    "apply_candidate_bundle",
    "invoke_declared_adapter",
]

MAX_PROMPT_BYTES = 1024 * 1024
MAX_HTTP_HEADER_BYTES = 64 * 1024
MAX_HTTP_RESPONSE_BYTES = 1024 * 1024
MAX_BUNDLE_TOTAL_BYTES = 1024 * 1024
MAX_BUNDLE_FILES = 256
MAX_BUNDLE_PATH_BYTES = 4096
VERSION_OUTPUT_BYTES = 16 * 1024
VERSION_TIMEOUT_SECONDS = 5.0


class CandidateBundleError(ValueError):
    """Assistant content is not one safe closed candidate bundle."""


class OpenAIResponseError(ValueError):
    """The one-turn HTTP response is not an admissible candidate response."""


def _validate_feedback(feedback_bytes: bytes | None, feedback_sha256: str | None) -> None:
    if (feedback_bytes is None) != (feedback_sha256 is None):
        raise ValueError("feedback bytes and digest must be supplied together")
    if feedback_bytes is not None and hashlib.sha256(feedback_bytes).hexdigest() != feedback_sha256:
        raise ValueError("feedback digest does not match feedback bytes")


def _safe_bundle_path(value: object) -> tuple[str, ...]:
    if not isinstance(value, str) or not value or "\\" in value or "\x00" in value:
        raise CandidateBundleError("bundle paths must be non-empty relative POSIX paths")
    if len(value.encode("utf-8")) > MAX_BUNDLE_PATH_BYTES:
        raise CandidateBundleError("bundle path exceeds the UTF-8 byte cap")
    posix = PurePosixPath(value)
    windows = PureWindowsPath(value)
    parts = tuple(value.split("/"))
    if (
        posix.is_absolute()
        or windows.is_absolute()
        or windows.drive
        or any(part in {"", ".", ".."} for part in parts)
    ):
        raise CandidateBundleError("bundle path is not normalized and relative")
    return parts


def _bundle_rows(content: str) -> list[tuple[tuple[str, ...], bytes]]:


    try:
        document = _rf7_input.loads(
            content,
            parse_constant=reject_json_constant,
            object_pairs_hook=reject_json_duplicate_pairs,
        )
    except (json.JSONDecodeError, ValueError, RecursionError) as error:
        raise CandidateBundleError(f"assistant content is not bundle JSON: {error}") from error
    if not isinstance(document, dict) or set(document) != {"schema_version", "files"}:
        raise CandidateBundleError("bundle requires exactly schema_version and files")
    if type(document["schema_version"]) is not int or document["schema_version"] != 1:
        raise CandidateBundleError("bundle schema version or files collection is invalid")
    if not isinstance(document["files"], list):
        raise CandidateBundleError("bundle schema version or files collection is invalid")
    if len(document["files"]) > MAX_BUNDLE_FILES:
        raise CandidateBundleError("bundle exceeds the file-count cap")
    rows: list[tuple[tuple[str, ...], bytes]] = []
    seen: set[tuple[str, ...]] = set()
    total = 0
    for row in document["files"]:
        if not isinstance(row, dict) or set(row) != {"path", "content_base64"}:
            raise CandidateBundleError("bundle file rows have a closed shape")
        parts = _safe_bundle_path(row["path"])
        if parts in seen:
            raise CandidateBundleError("bundle paths must be unique")
        if any(parts[:index] in seen for index in range(1, len(parts))):
            raise CandidateBundleError("a bundle file cannot be another file's ancestor")
        if any(existing[: len(parts)] == parts for existing in seen):
            raise CandidateBundleError("a bundle file cannot be another file's ancestor")
        encoded = row["content_base64"]
        if not isinstance(encoded, str):
            raise CandidateBundleError("content_base64 must be text")
        try:
            data = base64.b64decode(encoded, validate=True)
        except (ValueError, base64.binascii.Error) as error:
            raise CandidateBundleError("content_base64 is not strict RFC 4648 base64") from error
        total += len(data)
        if total > MAX_BUNDLE_TOTAL_BYTES:
            raise CandidateBundleError("bundle exceeds the decoded-byte cap")
        seen.add(parts)
        rows.append((parts, data))
    return rows


def _check_existing_path(root: Path, parts: tuple[str, ...]) -> None:
    current = root
    for index, part in enumerate(parts):
        current /= part
        try:
            info = current.lstat()
        except FileNotFoundError:
            return
        except OSError as error:
            raise CandidateBundleError(f"candidate path could not be inspected: {error}") from error
        if stat.S_ISLNK(info.st_mode):
            raise CandidateBundleError("bundle paths cannot traverse or replace symlinks")
        if index < len(parts) - 1 and not stat.S_ISDIR(info.st_mode):
            raise CandidateBundleError("bundle ancestor is not a directory")
        if index == len(parts) - 1 and not stat.S_ISREG(info.st_mode):
            raise CandidateBundleError("bundle destination is not a regular file")


def apply_candidate_bundle(content: str, *, candidate_root: str | Path) -> None:
    """Validate a complete semantic bundle, then atomically replace each leaf."""

    root = Path(candidate_root)
    info = root.lstat()
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
        raise CandidateBundleError("candidate root must be a real directory")
    rows = _bundle_rows(content)
    for parts, _ in rows:
        _check_existing_path(root, parts)
    root_fd = os.open(
        root,
        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0),
    )
    try:
        opened = os.fstat(root_fd)
        if (opened.st_dev, opened.st_ino) != (info.st_dev, info.st_ino):
            raise CandidateBundleError("candidate root changed before application")
        for parts, data in rows:
            parent_fd = os.dup(root_fd)
            temporary = ".gnd-adapter-" + secrets.token_hex(16)
            descriptor = -1
            try:
                for part in parts[:-1]:
                    try:
                        os.mkdir(part, 0o755, dir_fd=parent_fd)
                    except FileExistsError:
                        pass
                    child = os.open(
                        part,
                        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0),
                        dir_fd=parent_fd,
                    )
                    os.close(parent_fd)
                    parent_fd = child
                try:
                    leaf = os.stat(parts[-1], dir_fd=parent_fd, follow_symlinks=False)
                except FileNotFoundError:
                    pass
                else:
                    if stat.S_ISLNK(leaf.st_mode) or not stat.S_ISREG(leaf.st_mode):
                        raise CandidateBundleError("bundle destination changed before application")
                descriptor = os.open(
                    temporary,
                    os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
                    0o600,
                    dir_fd=parent_fd,
                )
                with os.fdopen(descriptor, "wb", closefd=True) as handle:
                    descriptor = -1
                    handle.write(data)
                    handle.flush()
                    os.fsync(handle.fileno())
                    os.fchmod(handle.fileno(), 0o644)
                os.replace(
                    temporary,
                    parts[-1],
                    src_dir_fd=parent_fd,
                    dst_dir_fd=parent_fd,
                )
                os.fsync(parent_fd)
            finally:
                if descriptor >= 0:
                    os.close(descriptor)
                try:
                    os.unlink(temporary, dir_fd=parent_fd)
                except FileNotFoundError:
                    pass
                os.close(parent_fd)
    finally:
        os.close(root_fd)


def _redacted_command_argv(
    policy: CommandAdapterPolicy,
    *,
    effective_prompt: str,
    model: str | None,
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    prompt_digest = hashlib.sha256(effective_prompt.encode("utf-8")).hexdigest()
    actual: list[str] = []
    evidence: list[str] = []
    for word in policy.argv:
        if word == "{prompt}":
            actual.append(effective_prompt)
            evidence.append(f"<prompt:sha256={prompt_digest}>")
        elif word == "{model}":
            assert model is not None
            actual.append(model)
            evidence.append(f"<model:sha256={hashlib.sha256(model.encode()).hexdigest()}>")
        else:
            actual.append(word)
            evidence.append(word)
    return tuple(actual), tuple(evidence)


def _command_result(
    process: BoundedProcessResult,
    *,
    policy: ResolvedAdapterPolicy,
    executable_name: str,
    executable_path: str,
    version: str,
    evidence_argv: tuple[str, ...],
    prompt_sha256: str,
    effective_prompt_sha256: str,
    feedback_sha256: str | None,
) -> DeclaredInvocationResult:
    status = {
        "succeeded": InvocationStatus.succeeded,
        "failed": InvocationStatus.failed,
        "spawn-failed": InvocationStatus.failed,
        "timed-out": InvocationStatus.timed_out,
        "cleanup-failed": InvocationStatus.failed,
    }[process.status]
    exit_code = process.return_code
    if exit_code is None and process.signal is not None:
        exit_code = -process.signal
    return DeclaredInvocationResult(
        policy_id=policy.policy.policy_id,
        policy_kind="command",
        policy_sha256=policy.policy_sha256,
        status=status,
        executable=executable_name,
        executable_sha256=hashlib.sha256(executable_path.encode()).hexdigest(),
        version=version,
        argv=evidence_argv,
        spawned=process.spawned,
        spawn_error=process.spawn_error,
        termination=process.termination,
        process_group_cleaned=process.process_group_cleaned,
        exit_code=exit_code,
        started_monotonic=process.started_monotonic,
        ended_monotonic=process.ended_monotonic,
        stdout_observed_bytes=process.stdout_observed_bytes,
        stdout_retained_bytes=process.stdout_retained_bytes,
        stdout_truncated=process.stdout_truncated,
        stderr_observed_bytes=process.stderr_observed_bytes,
        stderr_retained_bytes=process.stderr_retained_bytes,
        stderr_truncated=process.stderr_truncated,
        environment=process.environment,
        request_bytes=0,
        response_header_bytes=0,
        response_body_bytes=0,
        prompt_sha256=prompt_sha256,
        effective_prompt_sha256=effective_prompt_sha256,
        feedback_sha256=feedback_sha256,
        stdout=process.stdout,
        stderr=process.stderr,
    )


async def _invoke_command(
    resolved: ResolvedAdapterPolicy,
    *,
    prompt: str,
    effective_prompt: str,
    cwd: Path,
    timeout_seconds: float,
    feedback_bytes: bytes | None,
    feedback_sha256: str | None,
) -> DeclaredInvocationResult:
    policy = resolved.policy
    assert isinstance(policy, CommandAdapterPolicy)
    environment = resolved.environment
    executable = resolved.executable_path
    if executable is None:  # pragma: no cover - policy resolution owns this refusal
        raise AgentCLIError(f"trusted adapter executable {policy.executable!r} was not found")
    deadline = time.monotonic() + timeout_seconds
    version_result = await run_bounded_process(
        (executable, *policy.version_argv),
        cwd=cwd,
        env=environment,
        limits=ProcessLimits(
            timeout_seconds=min(VERSION_TIMEOUT_SECONDS, timeout_seconds),
            terminate_grace_seconds=0.25,
            stdin_limit_bytes=0,
            stdout_limit_bytes=VERSION_OUTPUT_BYTES,
            stderr_limit_bytes=VERSION_OUTPUT_BYTES,
            total_output_limit_bytes=VERSION_OUTPUT_BYTES * 2,
        ),
    )
    if version_result.status != "succeeded":
        return _command_result(
            version_result,
            policy=resolved,
            executable_name=policy.executable,
            executable_path=executable,
            version="",
            evidence_argv=(policy.executable, *policy.version_argv),
            prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest(),
            effective_prompt_sha256=hashlib.sha256(effective_prompt.encode()).hexdigest(),
            feedback_sha256=feedback_sha256,
        )
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise AgentCLIError("declared adapter deadline expired after version probe")
    words, evidence_words = _redacted_command_argv(
        policy,
        effective_prompt=effective_prompt,
        model=resolved.model,
    )
    stdin_bytes = feedback_bytes
    if policy.prompt_transport == "stdin":
        stdin_bytes = canonical_json_bytes(
            {
                "schema_version": 1,
                "prompt": effective_prompt,
                "feedback_base64": (
                    None if feedback_bytes is None else base64.b64encode(feedback_bytes).decode()
                ),
            }
        )
    if stdin_bytes is not None and len(stdin_bytes) > MAX_PROMPT_BYTES:
        raise ValueError("declared adapter stdin exceeds the byte cap")
    process = await run_bounded_process(
        (executable, *words),
        cwd=cwd,
        env=environment,
        limits=ProcessLimits(
            timeout_seconds=remaining,
            terminate_grace_seconds=1.0,
            stdin_limit_bytes=0 if stdin_bytes is None else len(stdin_bytes),
            stdout_limit_bytes=MAX_HTTP_RESPONSE_BYTES,
            stderr_limit_bytes=MAX_HTTP_RESPONSE_BYTES,
            total_output_limit_bytes=MAX_HTTP_RESPONSE_BYTES * 2,
        ),
        stdin_bytes=stdin_bytes,
    )
    version = f"<version:sha256={hashlib.sha256(version_result.stdout).hexdigest()}>"
    return _command_result(
        process,
        policy=resolved,
        executable_name=policy.executable,
        executable_path=executable,
        version=version,
        evidence_argv=(policy.executable, *evidence_words),
        prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest(),
        effective_prompt_sha256=hashlib.sha256(effective_prompt.encode()).hexdigest(),
        feedback_sha256=feedback_sha256,
    )


async def _read_http_response(
    reader: asyncio.StreamReader,
) -> tuple[int, int, bytes]:
    buffer = bytearray()
    while b"\r\n\r\n" not in buffer:
        chunk = await reader.read(4096)
        if not chunk:
            raise OpenAIResponseError("HTTP response ended before headers completed")
        buffer.extend(chunk)
        if len(buffer) > MAX_HTTP_HEADER_BYTES + 4096:
            raise OpenAIResponseError("HTTP response headers exceed the byte cap")
    header_end = buffer.index(b"\r\n\r\n") + 4
    if header_end > MAX_HTTP_HEADER_BYTES:
        raise OpenAIResponseError("HTTP response headers exceed the byte cap")
    header_bytes = bytes(buffer[:header_end])
    body = bytearray(buffer[header_end:])
    try:
        header_text = header_bytes.decode("iso-8859-1")
        lines = header_text[:-4].split("\r\n")
        status_parts = lines[0].split(" ", 2)
        status = int(status_parts[1])
    except (UnicodeDecodeError, ValueError, IndexError) as error:
        raise OpenAIResponseError("malformed HTTP status line") from error
    headers: dict[str, str] = {}
    for line in lines[1:]:
        if ":" not in line:
            raise OpenAIResponseError("malformed HTTP header")
        name, value = line.split(":", 1)
        lowered = name.strip().lower()
        if lowered in headers:
            raise OpenAIResponseError("duplicate HTTP response header")
        headers[lowered] = value.strip()
    transfer = headers.get("transfer-encoding", "").lower()
    if transfer:
        if transfer != "chunked":
            raise OpenAIResponseError("unsupported HTTP transfer encoding")
        raw = body
        decoded = bytearray()
        while True:
            while b"\r\n" not in raw:
                chunk = await reader.read(4096)
                if not chunk:
                    raise OpenAIResponseError("truncated HTTP chunk header")
                raw.extend(chunk)
                if len(raw) > MAX_HTTP_RESPONSE_BYTES + MAX_HTTP_HEADER_BYTES:
                    raise OpenAIResponseError("HTTP response exceeds the byte cap")
            line, _, remainder = raw.partition(b"\r\n")
            raw = bytearray(remainder)
            try:
                size = int(line.split(b";", 1)[0], 16)
            except ValueError as error:
                raise OpenAIResponseError("invalid HTTP chunk size") from error
            if size == 0:
                while True:
                    while b"\r\n" not in raw:
                        chunk = await reader.read(4096)
                        if not chunk:
                            raise OpenAIResponseError("truncated HTTP chunk terminator")
                        raw.extend(chunk)
                    trailer, _, remainder = raw.partition(b"\r\n")
                    raw = bytearray(remainder)
                    if not trailer:
                        break
                    raise OpenAIResponseError("HTTP chunk trailers are refused")
                if raw:
                    raise OpenAIResponseError("trailing bytes follow the HTTP chunk terminator")
                break
            if len(decoded) + size > MAX_HTTP_RESPONSE_BYTES:
                raise OpenAIResponseError("HTTP response exceeds the byte cap")
            while len(raw) < size + 2:
                chunk = await reader.read(min(64 * 1024, size + 2 - len(raw)))
                if not chunk:
                    raise OpenAIResponseError("truncated HTTP chunk")
                raw.extend(chunk)
            if raw[size : size + 2] != b"\r\n":
                raise OpenAIResponseError("invalid HTTP chunk framing")
            decoded.extend(raw[:size])
            raw = raw[size + 2 :]
        body_bytes = bytes(decoded)
    elif "content-length" in headers:
        try:
            length = int(headers["content-length"])
        except ValueError as error:
            raise OpenAIResponseError("invalid Content-Length") from error
        if length < 0 or length > MAX_HTTP_RESPONSE_BYTES:
            raise OpenAIResponseError("HTTP response exceeds the byte cap")
        if len(body) < length:
            body.extend(await reader.readexactly(length - len(body)))
        if len(body) != length:
            raise OpenAIResponseError("HTTP response body length is inconsistent")
        body_bytes = bytes(body)
    else:
        while True:
            if len(body) > MAX_HTTP_RESPONSE_BYTES:
                raise OpenAIResponseError("HTTP response exceeds the byte cap")
            chunk = await reader.read(min(64 * 1024, MAX_HTTP_RESPONSE_BYTES + 1 - len(body)))
            if not chunk:
                break
            body.extend(chunk)
        if len(body) > MAX_HTTP_RESPONSE_BYTES:
            raise OpenAIResponseError("HTTP response exceeds the byte cap")
        body_bytes = bytes(body)
    return status, len(header_bytes), body_bytes


async def _invoke_http(
    resolved: ResolvedAdapterPolicy,
    *,
    prompt: str,
    effective_prompt: str,
    cwd: Path,
    timeout_seconds: float,
    feedback_sha256: str | None,
) -> DeclaredInvocationResult:
    policy = resolved.policy
    assert isinstance(policy, OpenAICompatiblePolicy)
    request_body = canonical_json_bytes(
        {
            "messages": [{"role": "user", "content": effective_prompt}],
            "model": resolved.model,
            "stream": False,
        }
    )
    if len(request_body) > MAX_PROMPT_BYTES:
        raise ValueError("OpenAI-compatible request exceeds the byte cap")
    split = urlsplit(policy.request_url)
    host = split.hostname
    assert host is not None
    port = split.port or (443 if split.scheme == "https" else 80)
    target = split.path or "/"
    credential = resolved.credential_value
    assert credential is not None
    rendered_host = f"[{host}]" if ":" in host else host
    host_header = rendered_host if split.port is None else f"{rendered_host}:{port}"
    request = (
        f"POST {target} HTTP/1.1\r\n"
        f"Host: {host_header}\r\n"
        "Content-Type: application/json\r\n"
        f"Content-Length: {len(request_body)}\r\n"
        f"Authorization: Bearer {credential}\r\n"
        "Connection: close\r\n\r\n"
    ).encode() + request_body
    started = time.monotonic()
    deadline = started + timeout_seconds
    writer: asyncio.StreamWriter | None = None
    header_bytes = 0
    response_body = b""
    failure: str | None = None
    status = InvocationStatus.failed
    try:
        async with asyncio.timeout(timeout_seconds):
            context = ssl.create_default_context() if split.scheme == "https" else None
            reader, writer = await asyncio.open_connection(
                host,
                port,
                ssl=context,
                server_hostname=host if context is not None else None,
            )
            writer.write(request)
            await writer.drain()
            http_status, header_bytes, response_body = await _read_http_response(reader)
            if 300 <= http_status < 400:
                raise OpenAIResponseError("HTTP redirects are refused")
            if not 200 <= http_status < 300:
                raise OpenAIResponseError(f"HTTP response status {http_status} is not successful")
            try:
                document = _rf7_input.loads(response_body.decode("utf-8"))
                message = document["choices"][0]["message"]
                if message.get("tool_calls"):
                    raise OpenAIResponseError("tool-call responses are refused")
                content = message["content"]
            except (
                UnicodeDecodeError,
                json.JSONDecodeError,
                KeyError,
                IndexError,
                TypeError,
                RecursionError,
            ) as error:
                raise OpenAIResponseError(
                    "response lacks text choices[0].message.content"
                ) from error
            if not isinstance(content, str):
                raise OpenAIResponseError("assistant content must be text")
            apply_candidate_bundle(content, candidate_root=cwd)
            status = InvocationStatus.succeeded
    except TimeoutError:
        failure = "DeadlineExceeded"
        status = InvocationStatus.timed_out
    except (
        OSError,
        asyncio.IncompleteReadError,
        OpenAIResponseError,
        CandidateBundleError,
    ) as error:
        failure = type(error).__name__
    finally:
        if writer is not None:
            writer.close()
            remaining = deadline - time.monotonic()
            if remaining > 0:
                try:
                    await asyncio.wait_for(writer.wait_closed(), timeout=remaining)
                except (TimeoutError, OSError, ssl.SSLError):
                    pass
    ended = time.monotonic()
    succeeded = status is InvocationStatus.succeeded
    return DeclaredInvocationResult(
        policy_id=policy.policy_id,
        policy_kind="openai-compatible",
        policy_sha256=resolved.policy_sha256,
        status=status,
        endpoint_sha256=hashlib.sha256(policy.request_url.encode()).hexdigest(),
        spawned=True,
        spawn_error=failure,
        termination="exited",
        process_group_cleaned=True,
        exit_code=0 if succeeded else 1,
        started_monotonic=started,
        ended_monotonic=ended,
        stdout_observed_bytes=0,
        stdout_retained_bytes=0,
        stdout_truncated=False,
        stderr_observed_bytes=0,
        stderr_retained_bytes=0,
        stderr_truncated=False,
        environment=(),
        request_bytes=len(request),
        response_header_bytes=header_bytes,
        response_body_bytes=len(response_body),
        prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest(),
        effective_prompt_sha256=hashlib.sha256(effective_prompt.encode()).hexdigest(),
        feedback_sha256=feedback_sha256,
        stdout=b"",
        stderr=b"",
    )


async def invoke_declared_adapter(
    policy: ResolvedAdapterPolicy,
    *,
    prompt: str,
    cwd: str | Path,
    timeout_seconds: float,
    feedback_bytes: bytes | None = None,
    feedback_sha256: str | None = None,
) -> DeclaredInvocationResult:
    """Invoke exactly one locally declared adapter under one attempt deadline."""

    if not math.isfinite(timeout_seconds) or timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be finite and greater than zero")
    if not isinstance(prompt, str):
        raise TypeError("prompt must be text")
    _validate_feedback(feedback_bytes, feedback_sha256)
    effective = declared_effective_prompt(
        prompt,
        policy_kind=policy.policy.kind,
        feedback_bytes=feedback_bytes,
        feedback_sha256=feedback_sha256,
    )
    if len(effective.encode("utf-8")) > MAX_PROMPT_BYTES:
        raise ValueError("prompt exceeds the declared-adapter byte cap")
    candidate = Path(cwd)
    info = candidate.lstat()
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
        raise ValueError("cwd must be an existing real directory")
    if isinstance(policy.policy, CommandAdapterPolicy):
        return await _invoke_command(
            policy,
            prompt=prompt,
            effective_prompt=effective,
            cwd=candidate,
            timeout_seconds=timeout_seconds,
            feedback_bytes=feedback_bytes,
            feedback_sha256=feedback_sha256,
        )
    return await _invoke_http(
        policy,
        prompt=prompt,
        effective_prompt=effective,
        cwd=candidate,
        timeout_seconds=timeout_seconds,
        feedback_sha256=feedback_sha256,
    )
