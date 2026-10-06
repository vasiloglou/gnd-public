"""Policy-neutral bounded process lifecycle."""
from __future__ import annotations

import asyncio
import hashlib
import math
import os
import signal
import stat
import time
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

_READ_SIZE = 64 * 1024


_MIN_POST_KILL_REAP_DRAIN_SECONDS = 0.5


class EnvironmentFact(BaseModel):
    """A disclosed environment NAME and provenance, never its value."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str
    provenance: Literal["inherited", "fixed", "supplied"]


class ProcessLimits(BaseModel):
    """Closed resource limits for one bounded process lifecycle."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    timeout_seconds: float = Field(gt=0)
    terminate_grace_seconds: float = Field(gt=0)
    stdin_limit_bytes: int = Field(ge=0)
    stdout_limit_bytes: int = Field(ge=0)
    stderr_limit_bytes: int = Field(ge=0)
    total_output_limit_bytes: int = Field(ge=0)

    @field_validator("timeout_seconds", "terminate_grace_seconds")
    @classmethod
    def _finite_duration(cls, value: float) -> float:
        if not math.isfinite(value):
            raise ValueError("duration limits must be finite")
        return value


class BoundedProcessResult(BaseModel):
    """Closed process evidence with raw streams available only out of band.

    Raw argv, cwd, and environment values are deliberately absent. ``stdout``
    and ``stderr`` are usable by the caller but excluded from serialization.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    status: Literal[
        "succeeded",
        "failed",
        "spawn-failed",
        "timed-out",
        "cleanup-failed",
    ]
    spawned: bool
    timed_out: bool
    termination: Literal["not-started", "exited", "terminated", "killed"]
    return_code: int | None
    signal: int | None = Field(default=None, ge=1)
    spawn_error: str | None
    started_monotonic: float
    ended_monotonic: float
    elapsed_seconds: float = Field(ge=0)
    argv_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    argv_count: int = Field(ge=1)
    cwd: Literal["<working-directory>"] = "<working-directory>"
    stdout_observed_bytes: int = Field(ge=0)
    stdout_retained_bytes: int = Field(ge=0)
    stdout_truncated: bool
    stderr_observed_bytes: int = Field(ge=0)
    stderr_retained_bytes: int = Field(ge=0)
    stderr_truncated: bool
    environment: tuple[EnvironmentFact, ...]
    termination_steps: tuple[Literal["sigterm", "sigkill"], ...] = ()
    process_group_cleaned: bool
    stdout: bytes = Field(exclude=True, repr=False)
    stderr: bytes = Field(exclude=True, repr=False)


@dataclass
class _RetentionBudget:
    remaining: int

    def take(self, chunk: bytes, stream_remaining: int) -> bytes:
        size = min(len(chunk), stream_remaining, self.remaining)
        self.remaining -= size
        return chunk[:size]


@dataclass
class _DrainState:
    limit: int
    retained: bytearray = field(default_factory=bytearray)
    observed: int = 0


async def _drain(
    stream: asyncio.StreamReader | None,
    state: _DrainState,
    aggregate: _RetentionBudget,
) -> None:
    if stream is None:
        return
    while True:
        chunk = await stream.read(_READ_SIZE)
        if not chunk:
            return
        state.observed += len(chunk)
        kept = aggregate.take(chunk, state.limit - len(state.retained))
        if kept:
            state.retained.extend(kept)


async def _write_stdin(
    writer: asyncio.StreamWriter | None,
    payload: bytes,
) -> None:
    if writer is None:
        return
    try:
        writer.write(payload)
        await writer.drain()
    except (BrokenPipeError, ConnectionResetError):
        pass
    finally:
        writer.close()
        try:
            await writer.wait_closed()
        except (BrokenPipeError, ConnectionResetError):
            pass


def _signal_group(pid: int, process: asyncio.subprocess.Process, sig: signal.Signals) -> None:
    try:
        if os.name == "posix":
            os.killpg(pid, sig)
        elif process.returncode is None:  # pragma: no cover - Windows best effort
            process.send_signal(sig)
    except ProcessLookupError:
        pass


def _group_exists(pid: int) -> bool:
    if os.name != "posix":  # pragma: no cover - Windows best effort
        return False
    try:
        os.killpg(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


async def _wait_group_gone(pid: int, timeout: float) -> bool:
    deadline = time.monotonic() + timeout
    while _group_exists(pid):
        if time.monotonic() >= deadline:
            return False
        await asyncio.sleep(min(0.01, max(0.001, deadline - time.monotonic())))
    return True


async def _wait_cleanup_targets(
    pid: int,
    direct_wait: asyncio.Task[int] | None,
    *,
    deadline: float,
) -> bool:
    """Wait for the original group and direct child under one shared deadline."""

    group_wait = asyncio.create_task(
        _wait_group_gone(pid, max(0.0, deadline - time.monotonic()))
    )
    targets: set[asyncio.Task[object]] = {group_wait}  # type: ignore[arg-type]
    if direct_wait is not None:
        targets.add(direct_wait)  # type: ignore[arg-type]
    remaining = max(0.0, deadline - time.monotonic())
    if remaining:
        await asyncio.wait(targets, timeout=remaining)
    group_gone = group_wait.done() and not group_wait.cancelled() and group_wait.result()
    if not group_wait.done():
        group_wait.cancel()
        await asyncio.gather(group_wait, return_exceptions=True)
    return group_gone and (direct_wait is None or direct_wait.done())


async def _stop_process_group(
    process: asyncio.subprocess.Process,
    grace_seconds: float,
) -> tuple[
    Literal["terminated", "killed"],
    tuple[Literal["sigterm", "sigkill"], ...],
    bool,
    float,
]:
    """Stop the original group under one TERM and one post-KILL deadline.

    The direct child and group-disappearance poll run concurrently instead of
    each consuming ``grace_seconds``. The returned deadline is shared with
    pipe draining, bounding cleanup to TERM grace plus one finite post-KILL
    reap/drain window.
    """

    pid = process.pid
    steps: list[Literal["sigterm", "sigkill"]] = []
    term_deadline = time.monotonic() + grace_seconds
    cleanup_deadline = term_deadline + max(
        grace_seconds,
        _MIN_POST_KILL_REAP_DRAIN_SECONDS,
    )
    group_live = _group_exists(pid)
    if group_live or process.returncode is None:
        steps.append("sigterm")
        _signal_group(pid, process, signal.SIGTERM)

    direct_wait = asyncio.create_task(process.wait()) if process.returncode is None else None
    term_cleaned = await _wait_cleanup_targets(
        pid,
        direct_wait,
        deadline=term_deadline,
    )

    termination: Literal["terminated", "killed"] = "terminated"
    if not term_cleaned:
        termination = "killed"
        steps.append("sigkill")
        _signal_group(pid, process, signal.SIGKILL)
        if direct_wait is None and process.returncode is None:
            direct_wait = asyncio.create_task(process.wait())
        group_cleaned = await _wait_cleanup_targets(
            pid,
            direct_wait,
            deadline=cleanup_deadline,
        )
    else:
        group_cleaned = True

    if direct_wait is not None:
        if not direct_wait.done():
            direct_wait.cancel()
        await asyncio.gather(direct_wait, return_exceptions=True)

    if os.name != "posix":  # pragma: no cover - Windows best effort
        group_cleaned = process.returncode is not None
    return (
        termination,
        tuple(steps),
        group_cleaned and process.returncode is not None,
        cleanup_deadline,
    )


def _argv_digest(argv: tuple[str, ...]) -> str:
    return hashlib.sha256(b"\0".join(arg.encode("utf-8") for arg in argv)).hexdigest()


def _environment_facts(env: Mapping[str, str]) -> tuple[EnvironmentFact, ...]:
    return tuple(EnvironmentFact(name=name, provenance="supplied") for name in sorted(env))


def _sensitive_values(env: Mapping[str, str]) -> tuple[bytes, ...]:
    # The neutral runner cannot safely infer sensitivity from arbitrary names.
    # Every meaningful supplied value is private; short values are excluded to
    # avoid replacing common one-byte locale/flag text throughout evidence.
    values = {
        value.encode("utf-8")
        for value in env.values()
        if value and len(value) >= 4
    }
    return tuple(sorted(values, key=len, reverse=True))


def _suffix_prefix_overlap(left: bytes, right: bytes, *, maximum: int) -> int:
    """Return the longest suffix(left) equal to prefix(right), in linear time."""

    if maximum <= 0:
        return 0
    prefix = right[:maximum]
    tail = left[-maximum:]
    sequence = [*prefix, -1, *tail]
    lengths = [0] * len(sequence)
    for index in range(1, len(sequence)):
        candidate = lengths[index - 1]
        while candidate and sequence[index] != sequence[candidate]:
            candidate = lengths[candidate - 1]
        if sequence[index] == sequence[candidate]:
            candidate += 1
        lengths[index] = candidate
    return lengths[-1]


def _redact(data: bytes, sensitive_values: tuple[bytes, ...]) -> bytes:
    for value in sensitive_values:
        fragment_cap = min(len(data), len(value) - 1)
        leading = _suffix_prefix_overlap(value, data, maximum=fragment_cap)
        trailing = _suffix_prefix_overlap(data, value, maximum=fragment_cap)
        if leading >= 4 and trailing >= 4 and leading + trailing >= len(data):
            data = b"***"
        else:
            if leading >= 4:
                data = b"***" + data[leading:]
            if trailing >= 4:
                data = data[:-trailing] + b"***"
        # The replacement is intentionally shorter than the minimum retained
        # secret, so sanitization can never expand beyond any retention cap.
        data = data.replace(value, b"***")
    return data


def _result(
    *,
    status: Literal[
        "succeeded",
        "failed",
        "spawn-failed",
        "timed-out",
        "cleanup-failed",
    ],
    spawned: bool,
    termination: Literal["not-started", "exited", "terminated", "killed"],
    process: asyncio.subprocess.Process | None,
    spawn_error: str | None,
    started: float,
    argv: tuple[str, ...],
    env: Mapping[str, str],
    stdout_state: _DrainState,
    stderr_state: _DrainState,
    termination_steps: tuple[Literal["sigterm", "sigkill"], ...] = (),
    process_group_cleaned: bool,
    did_time_out: bool = False,
) -> BoundedProcessResult:
    ended = time.monotonic()
    stdout_raw = bytes(stdout_state.retained)
    stderr_raw = bytes(stderr_state.retained)
    stdout = _redact(stdout_raw, _sensitive_values(env))
    stderr = _redact(stderr_raw, _sensitive_values(env))
    raw_return_code = process.returncode if process is not None else None
    return_code = raw_return_code if raw_return_code is None or raw_return_code >= 0 else None
    signal_number = (
        -raw_return_code if raw_return_code is not None and raw_return_code < 0 else None
    )
    return BoundedProcessResult(
        status=status,
        spawned=spawned,
        timed_out=did_time_out or status == "timed-out",
        termination=termination,
        return_code=return_code,
        signal=signal_number,
        spawn_error=spawn_error,
        started_monotonic=started,
        ended_monotonic=ended,
        elapsed_seconds=ended - started,
        argv_sha256=_argv_digest(argv),
        argv_count=len(argv),
        stdout_observed_bytes=stdout_state.observed,
        stdout_retained_bytes=len(stdout),
        stdout_truncated=stdout_state.observed > len(stdout_raw),
        stderr_observed_bytes=stderr_state.observed,
        stderr_retained_bytes=len(stderr),
        stderr_truncated=stderr_state.observed > len(stderr_raw),
        environment=_environment_facts(env),
        termination_steps=termination_steps,
        process_group_cleaned=process_group_cleaned,
        stdout=stdout,
        stderr=stderr,
    )


async def run_bounded_process(
    trusted_argv: tuple[str, ...],
    *,
    cwd: str | Path,
    env: dict[str, str],
    limits: ProcessLimits,
    stdin_bytes: bytes | None = None,
) -> BoundedProcessResult:
    """Run trusted argv under one wall deadline and return closed evidence.

    On POSIX the child starts a new session and cleanup is guaranteed for all
    descendants that remain in that process group. Deliberate ``setsid`` escape
    is outside the guarantee. Cancellation performs shielded cleanup and drain
    before propagating ``CancelledError``.
    """

    if not isinstance(limits, ProcessLimits):
        limits = ProcessLimits.model_validate(limits)
    if not trusted_argv or any(not isinstance(arg, str) or "\0" in arg for arg in trusted_argv):
        raise ValueError("trusted_argv must contain non-NUL strings")
    if stdin_bytes is not None and len(stdin_bytes) > limits.stdin_limit_bytes:
        raise ValueError("stdin exceeds stdin_limit_bytes")
    env_snapshot = MappingProxyType(dict(env))
    if any(
        not isinstance(name, str)
        or not isinstance(value, str)
        or "\0" in name
        or "\0" in value
        for name, value in env_snapshot.items()
    ):
        raise ValueError("env must contain non-NUL string names and values")
    cwd_path = Path(cwd)
    try:
        cwd_info = cwd_path.lstat()
    except OSError as error:
        raise ValueError("cwd must be an existing real directory") from error
    if stat.S_ISLNK(cwd_info.st_mode) or not stat.S_ISDIR(cwd_info.st_mode):
        raise ValueError("cwd must be an existing real directory")

    cwd_fd = -1
    cwd_for_spawn: str | Path | None = cwd_path
    pass_fds: tuple[int, ...] = ()
    preexec_fn = None
    if os.name == "posix":
        cwd_fd = os.open(
            cwd_path,
            os.O_RDONLY
            | getattr(os, "O_DIRECTORY", 0)
            | getattr(os, "O_NOFOLLOW", 0),
        )
        opened_cwd = os.fstat(cwd_fd)
        if (
            not stat.S_ISDIR(opened_cwd.st_mode)
            or (opened_cwd.st_dev, opened_cwd.st_ino) != (cwd_info.st_dev, cwd_info.st_ino)
        ):
            os.close(cwd_fd)
            raise ValueError("cwd changed before its directory descriptor opened")
        # ``subprocess`` resolves its cwd pathname in the child, after this
        # validation.  A retained directory descriptor plus ``fchdir`` closes
        # that swap window on POSIX (including Darwin, where /dev/fd entries
        # cannot themselves be used as a subprocess cwd).  The callback calls
        # only the async-signal-safe fchdir syscall before exec.
        def enter_open_cwd() -> None:
            os.fchdir(cwd_fd)

        cwd_for_spawn = None
        pass_fds = (cwd_fd,)
        preexec_fn = enter_open_cwd

    argv = tuple(trusted_argv)
    started = time.monotonic()
    deadline = started + limits.timeout_seconds
    stdout_state = _DrainState(limits.stdout_limit_bytes)
    stderr_state = _DrainState(limits.stderr_limit_bytes)
    aggregate = _RetentionBudget(limits.total_output_limit_bytes)
    process: asyncio.subprocess.Process | None = None

    try:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError
        try:
            spawn_options: dict[str, object] = {
                "cwd": cwd_for_spawn,
                "stdin": (
                    asyncio.subprocess.DEVNULL
                    if stdin_bytes is None
                    else asyncio.subprocess.PIPE
                ),
                "stdout": asyncio.subprocess.PIPE,
                "stderr": asyncio.subprocess.PIPE,
                "env": dict(env_snapshot),
                "start_new_session": os.name == "posix",
            }
            if os.name == "posix":
                spawn_options["pass_fds"] = pass_fds
                spawn_options["preexec_fn"] = preexec_fn
            process = await asyncio.wait_for(
                asyncio.create_subprocess_exec(*argv, **spawn_options),
                timeout=remaining,
            )
        finally:
            if cwd_fd >= 0:
                os.close(cwd_fd)
                cwd_fd = -1
    except TimeoutError:
        return _result(
            status="timed-out",
            spawned=False,
            termination="not-started",
            process=None,
            spawn_error="TimeoutError",
            started=started,
            argv=argv,
            env=env_snapshot,
            stdout_state=stdout_state,
            stderr_state=stderr_state,
            process_group_cleaned=True,
        )
    except OSError as error:
        return _result(
            status="spawn-failed",
            spawned=False,
            termination="not-started",
            process=None,
            spawn_error=type(error).__name__,
            started=started,
            argv=argv,
            env=env_snapshot,
            stdout_state=stdout_state,
            stderr_state=stderr_state,
            process_group_cleaned=True,
        )

    stdout_task = asyncio.create_task(_drain(process.stdout, stdout_state, aggregate))
    stderr_task = asyncio.create_task(_drain(process.stderr, stderr_state, aggregate))
    writer_task = (
        asyncio.create_task(_write_stdin(process.stdin, stdin_bytes))
        if stdin_bytes is not None
        else None
    )
    wait_task = asyncio.create_task(process.wait())
    tasks = [stdout_task, stderr_task, wait_task]
    if writer_task is not None:
        tasks.append(writer_task)

    termination: Literal["exited", "terminated", "killed"] = "exited"
    termination_steps: tuple[Literal["sigterm", "sigkill"], ...] = ()
    group_cleaned = False
    timed_out = False
    cleanup_task: asyncio.Task[None] | None = None

    async def await_before_deadline(awaitable: object) -> object:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError
        return await asyncio.wait_for(asyncio.shield(awaitable), timeout=remaining)  # type: ignore[arg-type]

    async def cleanup_and_drain() -> None:
        nonlocal termination, termination_steps, group_cleaned
        (
            termination,
            termination_steps,
            group_cleaned,
            cleanup_deadline,
        ) = await _stop_process_group(
            process,
            limits.terminate_grace_seconds,
        )
        pending_io = [task for task in (writer_task, stdout_task, stderr_task) if task is not None]
        if pending_io:
            remaining_cleanup = max(0.0, cleanup_deadline - time.monotonic())
            try:
                if remaining_cleanup <= 0:
                    raise TimeoutError
                await asyncio.wait_for(
                    asyncio.gather(*pending_io, return_exceptions=True),
                    timeout=remaining_cleanup,
                )
            except TimeoutError:
                for task in pending_io:
                    if not task.done():
                        task.cancel()
                await asyncio.gather(*pending_io, return_exceptions=True)

    async def finish_cleanup() -> None:
        """Await the one cleanup task despite any number of cancellations."""

        nonlocal cleanup_task
        if cleanup_task is None:
            cleanup_task = asyncio.create_task(cleanup_and_drain())
        cancellation: asyncio.CancelledError | None = None
        while not cleanup_task.done():
            try:
                await asyncio.shield(cleanup_task)
            except asyncio.CancelledError as error:
                cancellation = error
        cleanup_task.result()
        if cancellation is not None:
            raise cancellation

    try:
        await await_before_deadline(wait_task)
        if _group_exists(process.pid):
            await finish_cleanup()
        else:
            await await_before_deadline(asyncio.gather(*tasks))
            group_cleaned = True
    except TimeoutError:
        timed_out = True
        await finish_cleanup()
    except asyncio.CancelledError:
        await finish_cleanup()
        raise

    if wait_task.done() and not wait_task.cancelled():
        await asyncio.gather(wait_task, return_exceptions=True)
    if not group_cleaned:
        status: Literal[
            "succeeded",
            "failed",
            "timed-out",
            "cleanup-failed",
        ] = "cleanup-failed"
    elif timed_out:
        status = "timed-out"
    elif termination != "exited":
        # A direct exit is not a clean success when descendants outlive it and
        # require forced group termination before the lifecycle can close.
        status = "failed"
    else:
        status = "succeeded" if process.returncode == 0 else "failed"
    return _result(
        status=status,
        spawned=True,
        termination=termination,
        process=process,
        spawn_error=None,
        started=started,
        argv=argv,
        env=env_snapshot,
        stdout_state=stdout_state,
        stderr_state=stderr_state,
        termination_steps=termination_steps,
        process_group_cleaned=group_cleaned,
        did_time_out=timed_out,
    )



# Historical qualifications are serialized by existing callers.
EnvironmentFact.__module__ = 'gnd.agent_cli'
ProcessLimits.__module__ = 'gnd.agent_cli'
BoundedProcessResult.__module__ = 'gnd.agent_cli'
_RetentionBudget.__module__ = 'gnd.agent_cli'
_DrainState.__module__ = 'gnd.agent_cli'
_drain.__module__ = 'gnd.agent_cli'
_write_stdin.__module__ = 'gnd.agent_cli'
_signal_group.__module__ = 'gnd.agent_cli'
_group_exists.__module__ = 'gnd.agent_cli'
_wait_group_gone.__module__ = 'gnd.agent_cli'
_wait_cleanup_targets.__module__ = 'gnd.agent_cli'
_stop_process_group.__module__ = 'gnd.agent_cli'
_argv_digest.__module__ = 'gnd.agent_cli'
_environment_facts.__module__ = 'gnd.agent_cli'
_sensitive_values.__module__ = 'gnd.agent_cli'
_suffix_prefix_overlap.__module__ = 'gnd.agent_cli'
_redact.__module__ = 'gnd.agent_cli'
_result.__module__ = 'gnd.agent_cli'
run_bounded_process.__module__ = 'gnd.agent_cli'

# Public dependency and compatibility spellings; same predecessor objects.
DrainState = _DrainState
MIN_POST_KILL_REAP_DRAIN_SECONDS = _MIN_POST_KILL_REAP_DRAIN_SECONDS
READ_SIZE = _READ_SIZE
RetentionBudget = _RetentionBudget
argv_digest = _argv_digest
drain = _drain
environment_facts = _environment_facts
group_exists = _group_exists
redact = _redact
result = _result
sensitive_values = _sensitive_values
signal_group = _signal_group
stop_process_group = _stop_process_group
suffix_prefix_overlap = _suffix_prefix_overlap
wait_cleanup_targets = _wait_cleanup_targets
wait_group_gone = _wait_group_gone
write_stdin = _write_stdin
