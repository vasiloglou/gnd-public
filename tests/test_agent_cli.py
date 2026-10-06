

from __future__ import annotations

import asyncio
import hashlib
import json
import os
import stat
import sys
import time
from pathlib import Path

import pytest
from pydantic import ValidationError

from gnd.agent_cli import (
    AgentAdapterId,
    AgentCLIError,
    InvocationStatus,
    ProcessLimits,
    invoke_agent,
    run_bounded_process,
)


def _write_program(path: Path) -> Path:
    path.write_text(
        """#!/usr/bin/env python3
import hashlib
import os
import pathlib
import signal
import subprocess
import sys
import time

mode = sys.argv[1]

if mode == "exit":
    data = sys.stdin.buffer.read()
    os.write(1, b"stdout:" + data)
    os.write(2, b"stderr")
    raise SystemExit(int(sys.argv[2]))

if mode == "stdin-eof":
    data = sys.stdin.buffer.read()
    print(len(data))
    raise SystemExit(0)

if mode == "flood":
    for descriptor, payload in ((1, b"o" * 70000), (2, b"e" * 90000)):
        view = memoryview(payload)
        while view:
            view = view[os.write(descriptor, view):]
    raise SystemExit(0)

if mode == "secret":
    name = "SESSION_SECRET" if "SESSION_SECRET" in os.environ else "BROKER_DSN"
    secret = os.environ[name].encode()
    # Position the value across the runner's ordinary 64 KiB read boundary.
    os.write(1, b"x" * 65533 + secret[:3])
    os.write(1, secret[3:] + b"-suffix")
    os.write(2, secret)
    raise SystemExit(0)

if mode == "env-mutation":
    secret = os.environ["PRIVATE_VALUE"].encode()
    ready, release = map(pathlib.Path, sys.argv[2:4])
    ready.write_text("ready")
    while not release.exists():
        time.sleep(0.005)
    os.write(1, secret)
    raise SystemExit(0)

if mode == "cwd-write":
    pathlib.Path("cwd-marker").write_text("bound")
    raise SystemExit(0)

if mode in {"ignore-term", "timeout-cancel"}:
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
    marker = sys.argv[2]
    child_code = (
        "import pathlib,signal,time; "
        "signal.signal(signal.SIGTERM, signal.SIG_IGN); "
        "time.sleep(1); "
        f"pathlib.Path({marker!r}).write_text('survived')"
    )
    subprocess.Popen([sys.executable, "-c", child_code])
    if mode == "timeout-cancel":
        pathlib.Path(sys.argv[3]).write_text(str(os.getpid()))
    time.sleep(30)

if mode in {"orphan-pipes", "orphan-detached-streams"}:
    marker = sys.argv[2]
    child_code = (
        "import pathlib,time; time.sleep(0.7); "
        f"pathlib.Path({marker!r}).write_text('survived')"
    )
    kwargs = {}
    if mode == "orphan-detached-streams":
        kwargs = {"stdin": subprocess.DEVNULL, "stdout": subprocess.DEVNULL,
                  "stderr": subprocess.DEVNULL}
    subprocess.Popen([sys.executable, "-c", child_code], **kwargs)
    raise SystemExit(0)

if mode == "cancel":
    marker, ready = sys.argv[2:4]
    child_code = (
        "import pathlib,time; time.sleep(0.8); "
        f"pathlib.Path({marker!r}).write_text('survived')"
    )
    subprocess.Popen([sys.executable, "-c", child_code])
    pathlib.Path(ready).write_text("ready")
    time.sleep(30)

raise SystemExit(91)
""",
        encoding="utf-8",
    )
    path.chmod(path.stat().st_mode | stat.S_IXUSR)
    return path


def _limits(**changes: object) -> ProcessLimits:
    values: dict[str, object] = {
        "timeout_seconds": 2.0,
        "terminate_grace_seconds": 0.1,
        "stdin_limit_bytes": 4096,
        "stdout_limit_bytes": 4096,
        "stderr_limit_bytes": 4096,
        "total_output_limit_bytes": 6144,
    }
    values.update(changes)
    return ProcessLimits.model_validate(values)


def test_process_limits_are_frozen_closed_finite_and_positive() -> None:
    limits = _limits()

    with pytest.raises(ValidationError):
        ProcessLimits.model_validate({**limits.model_dump(), "unknown": 1})
    with pytest.raises(ValidationError):
        ProcessLimits.model_validate({**limits.model_dump(), "timeout_seconds": float("inf")})
    with pytest.raises(ValidationError):
        ProcessLimits.model_validate({**limits.model_dump(), "terminate_grace_seconds": 0})
    with pytest.raises(ValidationError):
        ProcessLimits.model_validate({**limits.model_dump(), "stdin_limit_bytes": -1})
    with pytest.raises(ValidationError):
        limits.timeout_seconds = 7                      


@pytest.mark.parametrize("exit_code", [0, 23])
def test_neutral_runner_returns_one_closed_result_for_exit_and_nonzero(
    tmp_path: Path,
    exit_code: int,
) -> None:
    program = _write_program(tmp_path / "program")
    stdin = b"exact-input\n"

    result = asyncio.run(
        run_bounded_process(
            (sys.executable, str(program), "exit", str(exit_code)),
            cwd=tmp_path,
            env={"PATH": os.environ.get("PATH", "")},
            limits=_limits(),
            stdin_bytes=stdin,
        )
    )

    assert result.spawned is True
    assert result.status == ("succeeded" if exit_code == 0 else "failed")
    assert result.return_code == exit_code
    assert result.signal is None
    assert result.stdout == b"stdout:" + stdin
    assert result.stderr == b"stderr"
    assert result.stdout_observed_bytes == result.stdout_retained_bytes == len(result.stdout)
    assert result.stderr_observed_bytes == result.stderr_retained_bytes == len(result.stderr)
    assert result.ended_monotonic >= result.started_monotonic
    assert result.elapsed_seconds == pytest.approx(
        result.ended_monotonic - result.started_monotonic
    )
    assert result.process_group_cleaned is True


def test_spawn_failure_is_data_and_does_not_raise(tmp_path: Path) -> None:
    missing = tmp_path / "definitely-not-an-executable"

    result = asyncio.run(
        run_bounded_process(
            (str(missing),),
            cwd=tmp_path,
            env={},
            limits=_limits(),
        )
    )

    assert result.status == "spawn-failed"
    assert result.spawned is False
    assert result.return_code is None
    assert result.signal is None
    assert result.stdout == result.stderr == b""
    assert result.spawn_error == "FileNotFoundError"


def test_none_stdin_is_devnull_and_oversize_stdin_is_refused_before_spawn(
    tmp_path: Path,
) -> None:
    program = _write_program(tmp_path / "program")
    argv = (sys.executable, str(program), "stdin-eof")

    result = asyncio.run(
        run_bounded_process(argv, cwd=tmp_path, env={}, limits=_limits(), stdin_bytes=None)
    )
    assert result.stdout == b"0\n"

    marker = tmp_path / "should-not-run"
    with pytest.raises(ValueError, match="stdin"):
        asyncio.run(
            run_bounded_process(
                (sys.executable, "-c", f"open({str(marker)!r}, 'w').write('ran')"),
                cwd=tmp_path,
                env={},
                limits=_limits(stdin_limit_bytes=3),
                stdin_bytes=b"four",
            )
        )
    assert not marker.exists()


def test_flood_is_drained_with_per_stream_and_aggregate_retention_caps(
    tmp_path: Path,
) -> None:
    program = _write_program(tmp_path / "program")

    result = asyncio.run(
        run_bounded_process(
            (sys.executable, str(program), "flood"),
            cwd=tmp_path,
            env={},
            limits=_limits(
                stdout_limit_bytes=5000,
                stderr_limit_bytes=4000,
                total_output_limit_bytes=6000,
            ),
        )
    )

    assert result.status == "succeeded"
    assert result.stdout_observed_bytes == 70000
    assert result.stderr_observed_bytes == 90000
    assert result.stdout_retained_bytes <= 5000
    assert result.stderr_retained_bytes <= 4000
    assert result.stdout_retained_bytes + result.stderr_retained_bytes <= 6000
    assert result.stdout_truncated is result.stderr_truncated is True


def test_result_never_serializes_argv_env_values_raw_streams_or_private_cwd(
    tmp_path: Path,
) -> None:
    program = _write_program(tmp_path / "program")
    secret = "tok_live_split_across_chunks_123456789"
    result = asyncio.run(
        run_bounded_process(
            (sys.executable, str(program), "secret", "argv-secret-value"),
            cwd=tmp_path,
            env={"BROKER_DSN": secret},
            limits=_limits(
                stdout_limit_bytes=131072,
                stderr_limit_bytes=4096,
                total_output_limit_bytes=135168,
            ),
        )
    )

    serialized = json.dumps(result.model_dump(mode="json"), sort_keys=True)
    assert "argv-secret-value" not in serialized
    assert secret not in serialized
    assert str(tmp_path) not in serialized
    assert "BROKER_DSN" in serialized
    assert secret.encode() not in result.stdout
    assert secret.encode() not in result.stderr
    assert (
        result.argv_sha256
        == hashlib.sha256(
            b"\0".join(
                arg.encode("utf-8")
                for arg in (sys.executable, str(program), "secret", "argv-secret-value")
            )
        ).hexdigest()
    )


def test_redaction_never_expands_published_streams_past_any_cap(tmp_path: Path) -> None:
    secret = "abcd"
    result = asyncio.run(
        run_bounded_process(
            (
                sys.executable,
                "-c",
                "import os; print(os.environ['SESSION_SECRET'] * 10, end='')",
            ),
            cwd=tmp_path,
            env={"SESSION_SECRET": secret},
            limits=_limits(
                stdout_limit_bytes=40,
                stderr_limit_bytes=0,
                total_output_limit_bytes=40,
            ),
        )
    )

    assert secret.encode() not in result.stdout
    assert len(result.stdout) == result.stdout_retained_bytes <= 40
    assert result.stdout_retained_bytes + result.stderr_retained_bytes <= 40


def test_environment_is_snapshotted_once_for_spawn_metadata_and_redaction(
    tmp_path: Path,
) -> None:
    program = _write_program(tmp_path / "program")
    ready = tmp_path / "env-ready"
    release = tmp_path / "env-release"
    initial = "initial-secret-value"
    supplied = {"PRIVATE_VALUE": initial}

    async def scenario():
        task = asyncio.create_task(
            run_bounded_process(
                (
                    sys.executable,
                    str(program),
                    "env-mutation",
                    str(ready),
                    str(release),
                ),
                cwd=tmp_path,
                env=supplied,
                limits=_limits(),
            )
        )
        for _ in range(100):
            if ready.exists():
                break
            await asyncio.sleep(0.01)
        assert ready.exists()
        supplied["PRIVATE_VALUE"] = "mutated-secret-value"
        release.write_text("release", encoding="utf-8")
        return await task

    result = asyncio.run(scenario())

    assert initial.encode() not in result.stdout
    assert result.stdout == b"***"
    assert tuple(fact.name for fact in result.environment) == ("PRIVATE_VALUE",)


@pytest.mark.skipif(os.name != "posix", reason="descriptor-bound cwd is POSIX-specific")
def test_cwd_swap_between_check_and_spawn_cannot_redirect_child_writes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import gnd.process as agent_cli_module

    program = _write_program(tmp_path / "program")
    checked = tmp_path / "checked"
    checked.mkdir()
    preserved = tmp_path / "checked-preserved"
    outside = tmp_path / "outside"
    outside.mkdir()
    real_create = agent_cli_module.asyncio.create_subprocess_exec
    swapped = False

    async def swap_before_spawn(*args, **kwargs):
        nonlocal swapped
        checked.rename(preserved)
        checked.symlink_to(outside, target_is_directory=True)
        swapped = True
        return await real_create(*args, **kwargs)

    monkeypatch.setattr(
        agent_cli_module.asyncio,
        "create_subprocess_exec",
        swap_before_spawn,
    )
    result = asyncio.run(
        run_bounded_process(
            (sys.executable, str(program), "cwd-write"),
            cwd=checked,
            env={},
            limits=_limits(),
        )
    )

    assert swapped is True
    assert result.status == "succeeded"
    assert (preserved / "cwd-marker").read_text(encoding="utf-8") == "bound"
    assert not (outside / "cwd-marker").exists()


@pytest.mark.skipif(os.name != "posix", reason="process-group assertion is POSIX-specific")
def test_unproven_cleanup_is_a_distinct_closed_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import gnd.process as agent_cli_module

    program = _write_program(tmp_path / "program")
    marker = tmp_path / "unproven-cleanup-survived"
    real_stop = agent_cli_module._stop_process_group

    async def unproven(process, grace_seconds):
        termination, steps, _cleaned, cleanup_deadline = await real_stop(
            process,
            grace_seconds,
        )
        return termination, steps, False, cleanup_deadline

    monkeypatch.setattr(agent_cli_module, "_stop_process_group", unproven)
    result = asyncio.run(
        run_bounded_process(
            (
                sys.executable,
                str(program),
                "orphan-detached-streams",
                str(marker),
            ),
            cwd=tmp_path,
            env={},
            limits=_limits(timeout_seconds=0.2, terminate_grace_seconds=0.05),
        )
    )

    assert result.status == "cleanup-failed"
    assert result.process_group_cleaned is False


def test_agent_wrapper_refuses_an_unproven_process_cleanup(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import gnd.agents as agent_cli_module

    executable = tmp_path / "codex"
    _write_fake_adapter(executable)
    monkeypatch.setenv("PATH", f"{tmp_path}{os.pathsep}{os.environ.get('PATH', '')}")
    real_runner = agent_cli_module.run_bounded_process
    calls = 0

    async def unproven_main(*args, **kwargs):
        nonlocal calls
        calls += 1
        result = await real_runner(*args, **kwargs)
        if calls == 2:
            return result.model_copy(
                update={"status": "cleanup-failed", "process_group_cleaned": False}
            )
        return result

    monkeypatch.setattr(agent_cli_module, "run_bounded_process", unproven_main)
    with pytest.raises(AgentCLIError, match="cleanup"):
        asyncio.run(
            invoke_agent(
                AgentAdapterId.codex,
                prompt="bounded",
                cwd=tmp_path,
                timeout_seconds=2.0,
            )
        )


@pytest.mark.skipif(os.name != "posix", reason="process-group assertion is POSIX-specific")
def test_timeout_escalates_term_to_kill_and_awaits_descendants(tmp_path: Path) -> None:
    program = _write_program(tmp_path / "program")
    marker = tmp_path / "descendant-survived"

    result = asyncio.run(
        run_bounded_process(
            (sys.executable, str(program), "ignore-term", str(marker)),
            cwd=tmp_path,
            env={},
            limits=_limits(timeout_seconds=0.05, terminate_grace_seconds=0.2),
        )
    )
    time.sleep(1.1)

    assert result.status == "timed-out"
    assert result.timed_out is True
    assert "sigterm" in result.termination_steps
    assert "sigkill" in result.termination_steps
    assert result.process_group_cleaned is True
    assert result.elapsed_seconds < 0.4, "group and direct child spent separate TERM grace"
    assert not marker.exists()



@pytest.mark.skipif(os.name != "posix", reason="process-group assertion is POSIX-specific")
@pytest.mark.parametrize(
    ("mode", "expected_status", "creation_delay"),
    [
        ("orphan-pipes", "timed-out", 0),
        ("orphan-pipes", "timed-out", 0.08),
        ("orphan-detached-streams", "failed", 0),
    ],
)
def test_direct_exit_is_not_cleanup_until_the_process_group_is_gone(
    tmp_path: Path,
    mode: str,
    expected_status: str,
    creation_delay: float,
    monkeypatch,
) -> None:
    program = _write_program(tmp_path / "program")
    marker = tmp_path / f"{mode}-survived"

    create = asyncio.create_subprocess_exec

    async def scheduled_create(*args, **kwargs):
        process = await create(*args, **kwargs)
        await asyncio.sleep(creation_delay)
        return process

    monkeypatch.setattr(asyncio, "create_subprocess_exec", scheduled_create)
    result = asyncio.run(
        run_bounded_process(
            (sys.executable, str(program), mode, str(marker)),
            cwd=tmp_path,
            env={},
            limits=_limits(timeout_seconds=0.2, terminate_grace_seconds=0.05),
        )
    )
    time.sleep(0.9)

    allowed = {"failed", "timed-out"} if mode == "orphan-pipes" else {expected_status}
    assert result.status in allowed
    assert result.process_group_cleaned is True
    assert result.termination in {"terminated", "killed"}
    assert not marker.exists(), "runner returned while a same-group descendant could mutate"


@pytest.mark.skipif(os.name != "posix", reason="process-group assertion is POSIX-specific")
def test_cancellation_cleans_and_drains_before_it_propagates(tmp_path: Path) -> None:
    program = _write_program(tmp_path / "program")
    marker = tmp_path / "cancelled-descendant-survived"
    ready = tmp_path / "ready"

    async def scenario() -> None:
        task = asyncio.create_task(
            run_bounded_process(
                (sys.executable, str(program), "cancel", str(marker), str(ready)),
                cwd=tmp_path,
                env={},
                limits=_limits(timeout_seconds=10.0, terminate_grace_seconds=0.05),
            )
        )
        for _ in range(100):
            if ready.exists():
                break
            await asyncio.sleep(0.01)
        assert ready.exists()
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

    asyncio.run(scenario())
    time.sleep(1.0)
    assert not marker.exists()


@pytest.mark.skipif(os.name != "posix", reason="process-group assertion is POSIX-specific")
def test_cancellation_during_timeout_cleanup_cannot_detach_the_cleanup_task(
    tmp_path: Path,
) -> None:
    program = _write_program(tmp_path / "program")
    marker = tmp_path / "timeout-cancel-descendant-survived"
    ready = tmp_path / "timeout-cleanup-ready"

    async def scenario() -> int:
        task = asyncio.create_task(
            run_bounded_process(
                (
                    sys.executable,
                    str(program),
                    "timeout-cancel",
                    str(marker),
                    str(ready),
                ),
                cwd=tmp_path,
                env={},
                limits=_limits(
                    timeout_seconds=0.1,
                    terminate_grace_seconds=0.3,
                ),
            )
        )
        for _ in range(100):
            if ready.exists():
                break
            await asyncio.sleep(0.005)
        assert ready.exists()
        process_group = int(ready.read_text())
        await asyncio.sleep(0.15)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        return process_group

    process_group = asyncio.run(scenario())
    with pytest.raises(ProcessLookupError):
        os.killpg(process_group, 0)
    time.sleep(0.8)
    assert not marker.exists()



def _write_fake_adapter(path: Path) -> None:
    path.write_text(
        """#!/usr/bin/env python3
import hashlib
import pathlib
import sys
import time

if "--version" in sys.argv:
    if pathlib.Path(__file__).with_name("slow-version").exists():
        time.sleep(2)
    print("bounded-fake-agent 1.0")
    raise SystemExit(0)

feedback = sys.stdin.buffer.read()
prompt = sys.argv[-1]
if feedback:
    digest = hashlib.sha256(feedback).hexdigest()
    if digest not in prompt:
        raise SystemExit(41)
pathlib.Path("received-feedback.bin").write_bytes(feedback)
print("agent stdout")
raise SystemExit(0)
""",
        encoding="utf-8",
    )
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


def test_writable_adapter_delegates_mechanics_and_delivers_exact_feedback(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    executable = tmp_path / "codex"
    _write_fake_adapter(executable)
    monkeypatch.setenv("PATH", f"{tmp_path}{os.pathsep}{os.environ.get('PATH', '')}")
    feedback = b'{"source_attempt_index":1}\n'
    digest = hashlib.sha256(feedback).hexdigest()

    result = asyncio.run(
        invoke_agent(
            AgentAdapterId.codex,
            prompt="repair only the candidate",
            cwd=tmp_path,
            timeout_seconds=2.0,
            feedback_bytes=feedback,
            feedback_sha256=digest,
        )
    )

    assert result.status is InvocationStatus.succeeded
    assert (tmp_path / "received-feedback.bin").read_bytes() == feedback
    assert result.feedback_sha256 == digest
    evidence = json.dumps(result.model_dump(mode="json"), sort_keys=True)
    assert feedback.decode().strip() not in evidence


def test_version_evidence_is_digest_only_even_when_probe_echoes_inherited_values(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    executable = tmp_path / "codex"
    executable.write_text(
        """#!/usr/bin/env python3
import os
import sys

if "--version" in sys.argv:
    print(os.environ.get("HOME", ""))
    print(os.environ.get("PATH", ""))
    print(os.environ.get("OPENAI_BASE_URL", ""))
raise SystemExit(0)
""",
        encoding="utf-8",
    )
    executable.chmod(executable.stat().st_mode | stat.S_IXUSR)
    inherited_path = f"{tmp_path}{os.pathsep}{os.environ.get('PATH', '')}"
    values = {
        "HOME": "/private/version-home-must-not-leak",
        "PATH": inherited_path,
        "OPENAI_BASE_URL": "https://private-version-endpoint.invalid/token",
    }
    for name, value in values.items():
        monkeypatch.setenv(name, value)

    result = asyncio.run(
        invoke_agent(
            AgentAdapterId.codex,
            prompt="bounded",
            cwd=tmp_path,
            timeout_seconds=2.0,
        )
    )

    serialized = json.dumps(result.model_dump(mode="json"), sort_keys=True)
    assert result.version.startswith("<version:sha256=")
    assert all(value not in serialized for value in values.values())


def test_credential_bearing_endpoint_is_redacted_from_main_streams_across_chunks(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    executable = tmp_path / "codex"
    executable.write_text(
        """#!/usr/bin/env python3
import os
import sys

if "--version" in sys.argv:
    print("endpoint-echo 1.0")
    raise SystemExit(0)
value = os.environ["OPENAI_BASE_URL"].encode()
os.write(1, b"x" * 65533 + value[:3])
os.write(1, value[3:] + b"-after")
os.write(2, value)
raise SystemExit(0)
""",
        encoding="utf-8",
    )
    executable.chmod(executable.stat().st_mode | stat.S_IXUSR)
    endpoint = "https://user:password@example.invalid/v1?token=private-query-token"
    monkeypatch.setenv("OPENAI_BASE_URL", endpoint)
    monkeypatch.setenv("PATH", f"{tmp_path}{os.pathsep}{os.environ.get('PATH', '')}")

    result = asyncio.run(
        invoke_agent(
            AgentAdapterId.codex,
            prompt="bounded",
            cwd=tmp_path,
            timeout_seconds=2.0,
            output_limit_bytes=131072,
        )
    )

    assert endpoint.encode() not in result.stdout
    assert endpoint.encode() not in result.stderr
    assert b"private-query-token" not in result.stdout + result.stderr
    assert result.stdout_retained_bytes <= 131072
    assert result.stderr_retained_bytes <= 131072


def test_main_spawn_failure_after_a_successful_probe_is_not_reported_as_exit(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    executable = tmp_path / "codex"
    executable.write_text(
        """#!/usr/bin/env python3
import pathlib
import sys

if "--version" in sys.argv:
    pathlib.Path(__file__).unlink()
    print("one-shot-version 1.0")
    raise SystemExit(0)
raise SystemExit(91)
""",
        encoding="utf-8",
    )
    executable.chmod(executable.stat().st_mode | stat.S_IXUSR)
    monkeypatch.setenv("PATH", f"{tmp_path}{os.pathsep}{os.environ.get('PATH', '')}")

    result = asyncio.run(
        invoke_agent(
            AgentAdapterId.codex,
            prompt="bounded",
            cwd=tmp_path,
            timeout_seconds=2.0,
        )
    )

    assert result.status is InvocationStatus.failed
    assert result.spawned is False
    assert result.termination == "not-started"
    assert result.exit_code is None
    assert result.spawn_error == "FileNotFoundError"


@pytest.mark.skipif(os.name != "posix", reason="process-group assertion is POSIX-specific")
def test_post_exit_descendant_cleanup_is_a_closed_invocation_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    executable = tmp_path / "codex"
    marker = tmp_path / "descendant-survived"
    executable.write_text(
        f"""#!/usr/bin/env python3
import pathlib
import subprocess
import sys

if "--version" in sys.argv:
    print("descendant-agent 1.0")
    raise SystemExit(0)
child = "import pathlib,time;time.sleep(0.7);pathlib.Path({str(marker)!r}).write_text('survived')"
subprocess.Popen(
    [sys.executable, "-c", child],
    stdin=subprocess.DEVNULL,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)
raise SystemExit(0)
""",
        encoding="utf-8",
    )
    executable.chmod(executable.stat().st_mode | stat.S_IXUSR)
    monkeypatch.setenv("PATH", f"{tmp_path}{os.pathsep}{os.environ.get('PATH', '')}")

    result = asyncio.run(
        invoke_agent(
            AgentAdapterId.codex,
            prompt="bounded",
            cwd=tmp_path,
            timeout_seconds=2.0,
            terminate_grace_seconds=0.05,
        )
    )
    time.sleep(0.9)

    assert result.status is InvocationStatus.failed
    assert result.spawned is True
    assert result.termination in {"terminated", "killed"}
    assert result.exit_code == 0
    assert result.process_group_cleaned is True
    assert not marker.exists()


def test_writable_adapter_refuses_a_mismatched_feedback_digest_before_launch(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    executable = tmp_path / "codex"
    _write_fake_adapter(executable)
    monkeypatch.setenv("PATH", f"{tmp_path}{os.pathsep}{os.environ.get('PATH', '')}")

    with pytest.raises(ValueError, match="feedback.*digest|digest.*feedback"):
        asyncio.run(
            invoke_agent(
                AgentAdapterId.codex,
                prompt="repair only the candidate",
                cwd=tmp_path,
                timeout_seconds=2.0,
                feedback_bytes=b'{"source_attempt_index":1}\n',
                feedback_sha256="0" * 64,
            )
        )

    assert not (tmp_path / "received-feedback.bin").exists()


def test_version_probe_consumes_the_same_invocation_deadline(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    executable = tmp_path / "codex"
    _write_fake_adapter(executable)
    (tmp_path / "slow-version").write_text("yes", encoding="utf-8")
    monkeypatch.setenv("PATH", f"{tmp_path}{os.pathsep}{os.environ.get('PATH', '')}")
    started = time.monotonic()

    result = asyncio.run(
        invoke_agent(
            AgentAdapterId.codex,
            prompt="bounded",
            cwd=tmp_path,
            timeout_seconds=0.1,
        )
    )

    assert result.status is InvocationStatus.timed_out
    assert result.spawned is False
    assert result.termination == "not-started"
    assert result.exit_code is None
    assert result.spawn_error == "VersionProbeTimedOut"
    assert result.stdout == result.stderr == b""
    assert result.stdout_observed_bytes == result.stderr_observed_bytes == 0
    assert result.stdout_retained_bytes == result.stderr_retained_bytes == 0
    assert time.monotonic() - started < 1.0


def test_failed_version_probe_never_claims_the_writable_main_process_ran(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    executable = tmp_path / "codex"
    main_marker = tmp_path / "main-ran"
    executable.write_text(
        f"""#!/usr/bin/env python3
import os
import pathlib
import sys

if "--version" in sys.argv:
    os.write(1, b"probe stdout must not become main stdout")
    os.write(2, b"probe stderr must not become main stderr")
    raise SystemExit(17)
pathlib.Path({str(main_marker)!r}).write_text("ran")
raise SystemExit(0)
""",
        encoding="utf-8",
    )
    executable.chmod(executable.stat().st_mode | stat.S_IXUSR)
    monkeypatch.setenv("PATH", f"{tmp_path}{os.pathsep}{os.environ.get('PATH', '')}")

    result = asyncio.run(
        invoke_agent(
            AgentAdapterId.codex,
            prompt="bounded",
            cwd=tmp_path,
            timeout_seconds=2.0,
        )
    )

    assert result.status is InvocationStatus.failed
    assert result.spawned is False
    assert result.termination == "not-started"
    assert result.exit_code is None
    assert result.spawn_error == "VersionProbeFailed"
    assert result.version == ""
    assert result.stdout == result.stderr == b""
    assert result.stdout_observed_bytes == result.stderr_observed_bytes == 0
    assert result.stdout_retained_bytes == result.stderr_retained_bytes == 0
    assert result.process_group_cleaned is True
    assert not main_marker.exists()
