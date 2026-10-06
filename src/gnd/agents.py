"""Trusted adapter selection and invocation."""
from __future__ import annotations

import hashlib
import math
import os
import shutil
import time
from enum import StrEnum
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from gnd.process import (
    BoundedProcessResult as BoundedProcessResult,  # noqa: PLC0414 -- compatibility surface
)
from gnd.process import (
    EnvironmentFact as EnvironmentFact,  # noqa: PLC0414 -- compatibility surface
)
from gnd.process import (
    ProcessLimits as ProcessLimits,  # noqa: PLC0414 -- compatibility surface
)
from gnd.process import (
    run_bounded_process as run_bounded_process,  # noqa: PLC0414 -- compatibility surface
)

__all__ = [
    "AgentAdapterId",
    "AgentCLIError",
    "BoundedProcessResult",
    "InvocationResult",
    "InvocationStatus",
    "ProcessLimits",
    "build_agent_argv",
    "invoke_agent",
    "run_bounded_process",
]


DEFAULT_OUTPUT_LIMIT_BYTES = 1 * 1024 * 1024


DEFAULT_PROMPT_LIMIT_BYTES = 1 * 1024 * 1024


VERSION_OUTPUT_LIMIT_BYTES = 16 * 1024


VERSION_TIMEOUT_SECONDS = 5.0


class AgentAdapterId(StrEnum):
    claude = "claude"
    codex = "codex"


class InvocationStatus(StrEnum):
    succeeded = "succeeded"
    failed = "failed"
    timed_out = "timed-out"


class AgentCLIError(Exception):
    """A trusted adapter could not be resolved or launched."""


class InvocationResult(BaseModel):
    """Sanitized adapter evidence plus separately persisted raw streams."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    adapter: AgentAdapterId
    status: InvocationStatus
    executable: str
    version: str
    argv: tuple[str, ...]
    cwd: str
    spawned: bool = True
    spawn_error: str | None = None
    termination: Literal["not-started", "exited", "terminated", "killed"]
    process_group_cleaned: bool = True
    exit_code: int | None
    started_monotonic: float
    ended_monotonic: float
    stdout_observed_bytes: int = Field(ge=0)
    stdout_retained_bytes: int = Field(ge=0)
    stdout_truncated: bool
    stderr_observed_bytes: int = Field(ge=0)
    stderr_retained_bytes: int = Field(ge=0)
    stderr_truncated: bool
    environment: tuple[EnvironmentFact, ...]
    prompt_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    feedback_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    stdout: bytes = Field(exclude=True, repr=False)
    stderr: bytes = Field(exclude=True, repr=False)

    def ensure_closed_provenance(self) -> InvocationResult:
        """Reject impossible main-process state, including unchecked model copies."""

        if (
            not math.isfinite(self.started_monotonic)
            or not math.isfinite(self.ended_monotonic)
            or self.ended_monotonic < self.started_monotonic
        ):
            raise ValueError("invocation end cannot precede its start")
        if self.spawned:
            if self.termination == "not-started" or self.spawn_error is not None:
                raise ValueError("a spawned invocation must describe main-process termination")
            if self.exit_code is None:
                raise ValueError("a spawned invocation requires a main-process exit code")
            if self.status is InvocationStatus.succeeded:
                if (
                    self.termination != "exited"
                    or self.exit_code != 0
                    or not self.process_group_cleaned
                ):
                    raise ValueError("successful invocation must exit normally and cleanly")
            elif self.status is InvocationStatus.failed:
                if self.termination == "exited" and self.exit_code == 0:
                    raise ValueError("failed invocation cannot claim exit zero")
            elif self.termination not in {"terminated", "killed"}:
                raise ValueError("timed-out invocation requires termination provenance")
            return self
        if self.status is InvocationStatus.succeeded:
            raise ValueError("an unstarted invocation cannot succeed")
        if self.termination != "not-started" or self.exit_code is not None:
            raise ValueError("an unstarted invocation cannot claim main-process exit")
        if self.spawn_error is None:
            raise ValueError("an unstarted invocation requires a closed reason")
        if (
            self.stdout_observed_bytes
            or self.stdout_retained_bytes
            or self.stdout_truncated
            or self.stderr_observed_bytes
            or self.stderr_retained_bytes
            or self.stderr_truncated
            or self.stdout
            or self.stderr
        ):
            raise ValueError("an unstarted invocation cannot contain main-process streams")
        return self

    @model_validator(mode="after")
    def _main_process_provenance_is_coherent(self) -> InvocationResult:
        return self.ensure_closed_provenance()


def build_agent_argv(adapter: AgentAdapterId, prompt: str) -> tuple[str, ...]:
    """Return the closed argv template for a known adapter."""

    if not isinstance(adapter, AgentAdapterId):
        raise ValueError("adapter must be a closed AgentAdapterId value")  # noqa: TRY004
    if adapter is AgentAdapterId.claude:
        return (
            "claude",
            "--print",
            "--permission-mode",
            "acceptEdits",
            "--output-format",
            "text",
            prompt,
        )
    if adapter is AgentAdapterId.codex:
        return (
            "codex",
            "exec",
            "--ephemeral",
            "--sandbox",
            "workspace-write",
            "--color",
            "never",
            prompt,
        )
    raise ValueError(f"unsupported adapter {adapter!r}")  # pragma: no cover


def _private_environment() -> tuple[dict[str, str], tuple[EnvironmentFact, ...]]:
    inherited_names = (
        "PATH",
        "HOME",
        "USER",
        "LOGNAME",
        "TMPDIR",
        "LANG",
        "LC_ALL",
        "TERM",
        "SSL_CERT_FILE",
        "SSL_CERT_DIR",
        "XDG_CONFIG_HOME",
        "CODEX_HOME",
        "CLAUDE_CONFIG_DIR",
        "OPENAI_API_KEY",
        "OPENAI_BASE_URL",
        "ANTHROPIC_API_KEY",
        "ANTHROPIC_AUTH_TOKEN",
        "CLAUDE_CODE_OAUTH_TOKEN",
    )
    environment: dict[str, str] = {}
    facts: list[EnvironmentFact] = []
    for name in inherited_names:
        if name in os.environ:
            environment[name] = os.environ[name]
            facts.append(EnvironmentFact(name=name, provenance="inherited"))
    environment["NO_COLOR"] = "1"
    environment["PYTHONUNBUFFERED"] = "1"
    facts.extend(
        (
            EnvironmentFact(name="NO_COLOR", provenance="fixed"),
            EnvironmentFact(name="PYTHONUNBUFFERED", provenance="fixed"),
        )
    )
    return environment, tuple(facts)


def _validate_feedback(
    feedback_bytes: bytes | None,
    feedback_sha256: str | None,
) -> None:
    if (feedback_bytes is None) != (feedback_sha256 is None):
        raise ValueError("feedback bytes and feedback digest must be supplied together")
    if feedback_bytes is None:
        return
    actual = hashlib.sha256(feedback_bytes).hexdigest()
    if feedback_sha256 != actual:
        raise ValueError("feedback digest does not match feedback bytes")


async def invoke_agent(
    adapter: AgentAdapterId,
    *,
    prompt: str,
    cwd: str | Path,
    timeout_seconds: float,
    output_limit_bytes: int = DEFAULT_OUTPUT_LIMIT_BYTES,
    terminate_grace_seconds: float = 1.0,
    feedback_bytes: bytes | None = None,
    feedback_sha256: str | None = None,
) -> InvocationResult:
    """Invoke one trusted adapter through the neutral bounded runner.

    The version probe and adapter share one absolute wall deadline. Canonical
    feedback, when present, is the sole stdin payload; only its digest is added
    to the prompt. The runner is the sole ``asyncio.create_subprocess_exec``
    owner, and no shell command construction is used.
    """

    if not math.isfinite(timeout_seconds) or timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be finite and greater than zero")
    if not math.isfinite(terminate_grace_seconds) or terminate_grace_seconds <= 0:
        raise ValueError("terminate_grace_seconds must be finite and greater than zero")
    if output_limit_bytes < 0:
        raise ValueError("output_limit_bytes cannot be negative")
    if not isinstance(prompt, str):
        raise ValueError("prompt must be text")  # noqa: TRY004
    _validate_feedback(feedback_bytes, feedback_sha256)

    prompt_bytes = prompt.encode("utf-8")
    if len(prompt_bytes) > DEFAULT_PROMPT_LIMIT_BYTES:
        raise ValueError("prompt exceeds the adapter prompt byte limit")
    effective_prompt = prompt
    if feedback_sha256 is not None:
        effective_prompt = (
            f"{prompt}\n\nCurrent attempt feedback SHA-256: {feedback_sha256}\n"
            "Canonical current-attempt feedback is supplied byte-for-byte on stdin."
        )
    effective_prompt_bytes = effective_prompt.encode("utf-8")
    if len(effective_prompt_bytes) > DEFAULT_PROMPT_LIMIT_BYTES:
        raise ValueError("prompt exceeds the adapter prompt byte limit")

    overall_deadline = time.monotonic() + timeout_seconds
    argv = build_agent_argv(adapter, effective_prompt)
    environment, environment_facts = _private_environment()
    executable = shutil.which(argv[0], path=environment.get("PATH"))
    if executable is None:
        raise AgentCLIError(f"trusted adapter executable {argv[0]!r} was not found on PATH")

    redacted_prompt = f"<prompt:sha256={hashlib.sha256(effective_prompt_bytes).hexdigest()}>"
    evidence_argv = (*build_agent_argv(adapter, effective_prompt)[:-1], redacted_prompt)

    def invocation_from_result(
        process_result: BoundedProcessResult,
        *,
        version: str,
    ) -> InvocationResult:
        status = {
            "succeeded": InvocationStatus.succeeded,
            "failed": InvocationStatus.failed,
            "spawn-failed": InvocationStatus.failed,
            "timed-out": InvocationStatus.timed_out,
            "cleanup-failed": InvocationStatus.failed,
        }[process_result.status]
        exit_code = (
            process_result.return_code
            if process_result.return_code is not None
            else (-process_result.signal if process_result.signal is not None else None)
        )
        return InvocationResult(
            adapter=adapter,
            status=status,
            executable=argv[0],
            version=version,
            argv=evidence_argv,
            cwd="<candidate-root>",
            spawned=process_result.spawned,
            spawn_error=process_result.spawn_error,
            termination=process_result.termination,
            process_group_cleaned=process_result.process_group_cleaned,
            exit_code=exit_code,
            started_monotonic=process_result.started_monotonic,
            ended_monotonic=process_result.ended_monotonic,
            stdout_observed_bytes=process_result.stdout_observed_bytes,
            stdout_retained_bytes=process_result.stdout_retained_bytes,
            stdout_truncated=process_result.stdout_truncated,
            stderr_observed_bytes=process_result.stderr_observed_bytes,
            stderr_retained_bytes=process_result.stderr_retained_bytes,
            stderr_truncated=process_result.stderr_truncated,
            environment=environment_facts,
            prompt_sha256=hashlib.sha256(prompt_bytes).hexdigest(),
            feedback_sha256=feedback_sha256,
            stdout=process_result.stdout,
            stderr=process_result.stderr,
        )

    def main_not_started(
        *,
        status: InvocationStatus,
        version: str,
        reason: Literal[
            "VersionProbeFailed",
            "VersionProbeSpawnFailed",
            "VersionProbeTimedOut",
            "VersionProbeDeadlineExhausted",
        ],
        decided_monotonic: float,
    ) -> InvocationResult:
        """Return main-process evidence without promoting preflight provenance."""

        return InvocationResult(
            adapter=adapter,
            status=status,
            executable=argv[0],
            version=version,
            argv=evidence_argv,
            cwd="<candidate-root>",
            spawned=False,
            spawn_error=reason,
            termination="not-started",
            process_group_cleaned=True,
            exit_code=None,
            started_monotonic=decided_monotonic,
            ended_monotonic=decided_monotonic,
            stdout_observed_bytes=0,
            stdout_retained_bytes=0,
            stdout_truncated=False,
            stderr_observed_bytes=0,
            stderr_retained_bytes=0,
            stderr_truncated=False,
            environment=environment_facts,
            prompt_sha256=hashlib.sha256(prompt_bytes).hexdigest(),
            feedback_sha256=feedback_sha256,
            stdout=b"",
            stderr=b"",
        )

    def remaining_timeout() -> float:
        remaining = overall_deadline - time.monotonic()
        if remaining <= 0:
            raise AgentCLIError("trusted adapter invocation timed out")
        return remaining

    version_result = await run_bounded_process(
        (executable, "--version"),
        cwd=cwd,
        env=environment,
        limits=ProcessLimits(
            timeout_seconds=min(VERSION_TIMEOUT_SECONDS, remaining_timeout()),
            terminate_grace_seconds=min(terminate_grace_seconds, 0.25),
            stdin_limit_bytes=0,
            stdout_limit_bytes=VERSION_OUTPUT_LIMIT_BYTES,
            stderr_limit_bytes=VERSION_OUTPUT_LIMIT_BYTES,
            total_output_limit_bytes=VERSION_OUTPUT_LIMIT_BYTES * 2,
        ),
    )
    if not version_result.process_group_cleaned:
        raise AgentCLIError("trusted adapter version cleanup could not be proven")
    if version_result.status != "succeeded":
        version_failure = {
            "failed": (InvocationStatus.failed, "VersionProbeFailed"),
            "spawn-failed": (InvocationStatus.failed, "VersionProbeSpawnFailed"),
            "timed-out": (InvocationStatus.timed_out, "VersionProbeTimedOut"),
        }
        status, reason = version_failure[version_result.status]
        return main_not_started(
            status=status,
            version="",
            reason=reason,
            decided_monotonic=version_result.ended_monotonic,
        )
    version = f"<version:sha256={hashlib.sha256(version_result.stdout).hexdigest()}>"

    remaining = overall_deadline - time.monotonic()
    if remaining <= 0:
        return main_not_started(
            status=InvocationStatus.timed_out,
            version=version,
            reason="VersionProbeDeadlineExhausted",
            decided_monotonic=time.monotonic(),
        )

    actual_argv = (executable, *argv[1:])
    main_result = await run_bounded_process(
        actual_argv,
        cwd=cwd,
        env=environment,
        limits=ProcessLimits(
            timeout_seconds=remaining,
            terminate_grace_seconds=terminate_grace_seconds,
            stdin_limit_bytes=(len(feedback_bytes) if feedback_bytes is not None else 0),
            stdout_limit_bytes=output_limit_bytes,
            stderr_limit_bytes=output_limit_bytes,
            total_output_limit_bytes=output_limit_bytes * 2,
        ),
        stdin_bytes=feedback_bytes,
    )
    if not main_result.process_group_cleaned:
        raise AgentCLIError("trusted adapter process cleanup could not be proven")
    return invocation_from_result(main_result, version=version)



# Historical qualifications are serialized by existing callers.
AgentAdapterId.__module__ = 'gnd.agent_cli'
InvocationStatus.__module__ = 'gnd.agent_cli'
AgentCLIError.__module__ = 'gnd.agent_cli'
InvocationResult.__module__ = 'gnd.agent_cli'
build_agent_argv.__module__ = 'gnd.agent_cli'
_private_environment.__module__ = 'gnd.agent_cli'
_validate_feedback.__module__ = 'gnd.agent_cli'
invoke_agent.__module__ = 'gnd.agent_cli'

# Public dependency and compatibility spellings; same predecessor objects.
compat_all = __all__
private_environment = _private_environment
validate_feedback = _validate_feedback
