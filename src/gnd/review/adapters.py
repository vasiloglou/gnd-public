"""Closed terminal-reviewer invocation policies.

Repository content never selects an executable, flag, model, environment
value, or working directory.  The six policies below are Python-owned data;
the shared process primitive owns all spawning, draining, deadlines, and
process-group cleanup.
"""

from __future__ import annotations

import math
import os
import re
import shutil
import stat
import time
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, model_validator

from gnd.process import BoundedProcessResult, ProcessLimits, run_bounded_process

__all__ = [
    "REVIEWER_IDS",
    "AdapterAttempt",
    "ResolvedReviewerPolicy",
    "ReviewEffort",
    "ReviewerId",
    "ReviewerPolicy",
    "resolve_reviewer_policies",
    "reviewer_policies",
    "reviewer_process_environment",
    "run_reviewer_adapter",
    "sanitized_reviewer_environment",
]


class ReviewerId(StrEnum):
    """Every reviewer ID readable from current and committed evidence."""

    claude = "claude"
    codex = "codex"
    qwen = "qwen"
    gemini = "gemini"
    kimi = "kimi"
    glm = "glm"


class ReviewEffort(StrEnum):
    """Closed per-run effort profiles accepted by the review harness."""

    xhigh = "xhigh"
    high = "high"
    medium = "medium"


# GLM is appended after Kimi so every committed roster is a prefix of this
# tuple: four-envelope (pre-Kimi) and five-envelope (pre-GLM) evidence stays
# readable through the fixed-order prefixes the runner accepts.
REVIEWER_IDS: tuple[ReviewerId, ...] = (
    ReviewerId.claude,
    ReviewerId.codex,
    ReviewerId.qwen,
    ReviewerId.gemini,
    ReviewerId.kimi,
    ReviewerId.glm,
)


class ReviewerPolicy(BaseModel):
    """One fixed executable, invocation surface, and prompt transport policy.

    The three environment fields are a per-seat projection applied AFTER the
    shared allowlist sanitization, in a fixed order: removals, then credential
    remaps (copy the value of one already-sanitized name to another, never
    reading the secret into policy data), then literal overrides. They exist so
    one seat can be redirected to a provider-compatible endpoint without the
    redirect or its credential ever reaching any other seat.
    """

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    reviewer_id: ReviewerId
    executable_name: str
    capability_argv: tuple[str, ...]
    capability_proof: Literal["help-invocation-flags-v1"] = "help-invocation-flags-v1"
    invocation_argv: tuple[str, ...]
    prompt_transport: Literal["stdin", "argv"] = "stdin"
    environment_removals: tuple[str, ...] = ()
    environment_credential_remaps: tuple[tuple[str, str], ...] = ()
    environment_overrides: tuple[tuple[str, str], ...] = ()

    @model_validator(mode="after")
    def _environment_projection_is_closed(self) -> ReviewerPolicy:
        touched = (
            *self.environment_removals,
            *(name for pair in self.environment_credential_remaps for name in pair),
            *(name for name, _value in self.environment_overrides),
        )
        for name in touched:
            if not name or "\x00" in name or "=" in name:
                raise ValueError("environment projection names must be plain variable names")
        if "PATH" in touched:
            raise ValueError(
                "a per-seat projection must not touch PATH; executables are "
                "resolved once from the shared validated PATH"
            )
        if any("\x00" in value for _name, value in self.environment_overrides):
            raise ValueError("environment override values must contain non-NUL text")
        return self


# Quality-first model IDs are Python-owned policy, never request data. Refresh
# these through the packaged gnd-update-review-panel workflow, which verifies
# current vendor documentation and each installed CLI flag before changing the
# fixed invocation contract.
_POLICIES: tuple[ReviewerPolicy, ...] = (
    ReviewerPolicy(
        reviewer_id=ReviewerId.claude,
        executable_name="claude",
        capability_argv=("--help",),
        invocation_argv=(
            "--print",
            "--safe-mode",
            "--model",
            "opus",
            "--effort",
            "xhigh",
            "--permission-mode",
            "plan",
            "--output-format",
            "text",
            "--no-session-persistence",
        ),
    ),
    ReviewerPolicy(
        reviewer_id=ReviewerId.codex,
        executable_name="codex",
        capability_argv=("exec", "--help"),
        invocation_argv=(
            "exec",
            "--ephemeral",
            "--ignore-user-config",
            "--model",
            "gpt-6-sol",
            "--config",
            'model_reasoning_effort="xhigh"',
            "--sandbox",
            "read-only",
            "--color",
            "never",
            "--skip-git-repo-check",
            "-",
        ),
    ),
    ReviewerPolicy(
        reviewer_id=ReviewerId.qwen,
        executable_name="qwen",
        capability_argv=("--help",),
        invocation_argv=(
            "--bare",
            "--safe-mode",
            "--sandbox",
            "--auth-type",
            "openai",
            "--openai-base-url",
            "https://openrouter.ai/api/v1",
            "--model",
            "qwen/qwen3.8-max",
            "--approval-mode",
            "plan",
            "--max-wall-time",
            "600s",
            "--max-session-turns",
            "4",
            "--max-tool-calls",
            "0",
            "--max-subagent-depth",
            "1",
            "--exclude-tools",
            "agent",
            "--output-format",
            "text",
            "--prompt",
            "-",
        ),
        environment_removals=("OPENAI_API_KEY", "OPENAI_BASE_URL"),
        environment_credential_remaps=(("OPENROUTER_API_KEY", "OPENAI_API_KEY"),),
    ),
    ReviewerPolicy(
        reviewer_id=ReviewerId.gemini,
        executable_name="gemini",
        capability_argv=("--help",),
        invocation_argv=(
            "--model",
            "gemini-3.1-pro-preview",
            "--approval-mode",
            "plan",
            "--skip-trust",
            "--output-format",
            "text",
            "--prompt",
            "-",
        ),
    ),
    ReviewerPolicy(
        reviewer_id=ReviewerId.kimi,
        executable_name="kimi",
        capability_argv=("--help",),
        invocation_argv=(
            "--model",
            "kimi-code/kimi-for-coding",
            "--output-format",
            "stream-json",
            "--prompt",
        ),
        prompt_transport="argv",
    ),
    # The GLM seat runs the same Claude Code CLI against Z.AI's documented
    # Anthropic-compatible endpoint. The projection removes every real
    # Anthropic credential first, so a misconfigured seat fails auth at Z.AI
    # instead of silently reviewing on the Anthropic account; the model ID is
    # the reverse guard — api.anthropic.com would reject `glm-5.3`. The seat's
    # credential is ZAI_API_KEY, remapped to ANTHROPIC_AUTH_TOKEN for this
    # seat only; a missing ZAI_API_KEY yields this seat's ordinary
    # auth-failure envelope, never a fallback. Z.AI documents no per-run
    # effort control on this endpoint, so like Qwen, Gemini, and Kimi the
    # policy is byte-identical across effort profiles.
    ReviewerPolicy(
        reviewer_id=ReviewerId.glm,
        executable_name="claude",
        capability_argv=("--help",),
        invocation_argv=(
            "--print",
            "--safe-mode",
            "--model",
            "glm-5.3",
            "--permission-mode",
            "plan",
            "--output-format",
            "text",
            "--no-session-persistence",
        ),
        environment_removals=(
            "ANTHROPIC_API_KEY",
            "ANTHROPIC_AUTH_TOKEN",
            "CLAUDE_CODE_OAUTH_TOKEN",
        ),
        environment_credential_remaps=(("ZAI_API_KEY", "ANTHROPIC_AUTH_TOKEN"),),
        environment_overrides=(("ANTHROPIC_BASE_URL", "https://api.z.ai/api/anthropic"),),
    ),
)


def reviewer_policies(
    reviewer_effort: ReviewEffort | str = ReviewEffort.xhigh,
) -> tuple[ReviewerPolicy, ...]:
    """Return the policies in evidence order at one closed effort profile.

    Claude and Codex expose supported per-run effort controls. Qwen, Gemini,
    Kimi, and the GLM seat (whose Z.AI endpoint documents no effort control)
    expose no per-run effort flag, so those four policies remain byte-identical
    across profiles.
    """

    try:
        effort = ReviewEffort(reviewer_effort)
    except ValueError as error:
        allowed = ", ".join(item.value for item in ReviewEffort)
        raise ValueError(f"reviewer effort must be one of: {allowed}") from error
    if effort is ReviewEffort.xhigh:
        return _POLICIES

    selected: list[ReviewerPolicy] = []
    for policy in _POLICIES:
        argv = tuple(
            (
                effort.value
                if policy.reviewer_id is ReviewerId.claude and token == "xhigh"
                else f'model_reasoning_effort="{effort.value}"'
                if policy.reviewer_id is ReviewerId.codex
                and token == 'model_reasoning_effort="xhigh"'
                else token
            )
            for token in policy.invocation_argv
        )
        selected.append(policy.model_copy(update={"invocation_argv": argv}))
    return tuple(selected)


def _invocation_long_flags(policy: ReviewerPolicy) -> tuple[str, ...]:
    return tuple(token for token in policy.invocation_argv if re.fullmatch(r"--[\w-]+", token))


def _help_documents_flag(help_text: str, flag: str) -> bool:
    return re.search(rf"(?<![\w-]){re.escape(flag)}(?![\w-])", help_text) is not None


def _capability_is_proven(
    policy: ReviewerPolicy,
    capability: BoundedProcessResult,
) -> bool:
    if (
        capability.status != "succeeded"
        or not capability.process_group_cleaned
        or capability.stdout_truncated
        or capability.stderr_truncated
    ):
        return False
    help_text = capability.stdout.decode("utf-8", errors="replace")
    return all(
        _help_documents_flag(help_text, flag) for flag in _invocation_long_flags(policy)
    )


_ENVIRONMENT_ALLOWLIST = frozenset(
    {
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
        "GEMINI_CLI_HOME",
        "QWEN_CODE_HOME",
        "KIMI_CODE_HOME",
        "KIMI_CONFIG_DIR",
        "OPENAI_API_KEY",
        "OPENAI_BASE_URL",
        "ANTHROPIC_API_KEY",
        "ANTHROPIC_AUTH_TOKEN",
        "CLAUDE_CODE_OAUTH_TOKEN",
        "GOOGLE_API_KEY",
        "GEMINI_API_KEY",
        "DASHSCOPE_API_KEY",
        "OPENROUTER_API_KEY",
        "MOONSHOT_API_KEY",
        "ZAI_API_KEY",
    }
)


def _validated_path(environment: dict[str, str]) -> str:
    path_value = environment.get("PATH")
    if not path_value:
        raise ValueError("empty PATH is not allowed for reviewer resolution")
    entries = path_value.split(os.pathsep)
    if any(not entry for entry in entries):
        raise ValueError("empty PATH entries are not allowed for reviewer resolution")
    for entry in entries:
        path = Path(entry)
        if not path.is_absolute():
            raise ValueError("every PATH entry must be absolute for reviewer resolution")
        if "\x00" in entry:
            raise ValueError("PATH entries cannot contain NUL")
    return path_value


def sanitized_reviewer_environment(
    source: dict[str, str] | None = None,
) -> dict[str, str]:
    """Copy only explicit process/config/credential names plus fixed controls."""

    source_snapshot = dict(vars(os)["environ"] if source is None else source)
    _validated_path(source_snapshot)
    environment = {
        name: value for name, value in source_snapshot.items() if name in _ENVIRONMENT_ALLOWLIST
    }
    if any(
        not isinstance(name, str) or not isinstance(value, str) or "\x00" in name or "\x00" in value
        for name, value in environment.items()
    ):
        raise ValueError("reviewer environment must contain non-NUL text")
    environment["NO_COLOR"] = "1"
    environment["PYTHONUNBUFFERED"] = "1"
    return environment


def reviewer_process_environment(
    policy: ReviewerPolicy,
    environment: dict[str, str],
) -> dict[str, str]:
    """Apply one policy's closed projection to the shared sanitized environment.

    Removals, then credential remaps, then literal overrides. The input is
    never mutated, and a remap whose source name is absent simply leaves the
    target unset — the seat then fails authentication in its ordinary envelope
    rather than borrowing another seat's credential.
    """

    seat = dict(environment)
    for name in policy.environment_removals:
        seat.pop(name, None)
    for source, target in policy.environment_credential_remaps:
        value = seat.get(source)
        if value is not None:
            seat[target] = value
    for name, value in policy.environment_overrides:
        seat[name] = value
    return seat


@dataclass(frozen=True)
class ResolvedReviewerPolicy:
    """One policy with an absolute executable, or an explicit missing result.

    ``executable_identity`` is a TOCTOU tuple over the resolved executable,
    not a content digest. Resolution follows symlinks, so an ``env node`` shim
    binds the launcher it resolves to rather than the JavaScript package tree.
    """

    policy: ReviewerPolicy
    executable: str | None
    executable_identity: tuple[int, int, int, int] | None


def _executable_identity(path: str | Path) -> tuple[int, int, int, int]:
    executable = Path(path)
    try:
        info = executable.lstat()
    except OSError as error:
        raise ValueError("resolved reviewer executable changed or disappeared") from error
    if (
        stat.S_ISLNK(info.st_mode)
        or not stat.S_ISREG(info.st_mode)
        or not os.access(executable, os.X_OK)
    ):
        raise ValueError("resolved reviewer executable is no longer an executable regular file")
    return (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns)


def _assert_executable_identity(resolved: ResolvedReviewerPolicy) -> None:
    if resolved.executable is None or resolved.executable_identity is None:
        raise ValueError("resolved reviewer executable is missing its retained identity")
    if _executable_identity(resolved.executable) != resolved.executable_identity:
        raise ValueError("resolved reviewer executable changed identity before invocation")


def resolve_reviewer_policies(
    environment: dict[str, str],
    reviewer_effort: ReviewEffort | str = ReviewEffort.xhigh,
) -> tuple[ResolvedReviewerPolicy, ...]:
    """Resolve every executable from a validated absolute-only PATH."""

    path_value = _validated_path(environment)
    resolved: list[ResolvedReviewerPolicy] = []
    for policy in reviewer_policies(reviewer_effort):
        located = shutil.which(policy.executable_name, path=path_value)
        if located is None:
            resolved.append(
                ResolvedReviewerPolicy(
                    policy=policy,
                    executable=None,
                    executable_identity=None,
                )
            )
            continue
        try:
            canonical = Path(located).resolve(strict=True)
            info = canonical.stat()
        except (OSError, RuntimeError) as error:
            raise ValueError(
                f"reviewer executable {policy.executable_name!r} could not be resolved"
            ) from error
        if not stat.S_ISREG(info.st_mode) or not os.access(canonical, os.X_OK):
            raise ValueError(
                f"reviewer executable {policy.executable_name!r} is not an executable regular file"
            )
        resolved.append(
            ResolvedReviewerPolicy(
                policy=policy,
                executable=str(canonical),
                executable_identity=(
                    info.st_dev,
                    info.st_ino,
                    info.st_size,
                    info.st_mtime_ns,
                ),
            )
        )
    return tuple(resolved)


@dataclass(frozen=True)
class AdapterAttempt:
    """Raw neutral-runner outcomes before reviewer-status normalization."""

    resolved: ResolvedReviewerPolicy
    capability: BoundedProcessResult | None
    invocation: BoundedProcessResult | None
    capability_proven: bool


def _process_limits(
    *,
    deadline: float,
    terminate_grace_seconds: float,
    stdin_limit_bytes: int,
    stdout_limit_bytes: int,
    stderr_limit_bytes: int,
    total_output_limit_bytes: int,
) -> ProcessLimits:
    remaining = deadline - time.monotonic()
    if not math.isfinite(remaining) or remaining <= 0:
        remaining = 1e-9
    return ProcessLimits(
        timeout_seconds=remaining,
        terminate_grace_seconds=terminate_grace_seconds,
        stdin_limit_bytes=stdin_limit_bytes,
        stdout_limit_bytes=stdout_limit_bytes,
        stderr_limit_bytes=stderr_limit_bytes,
        total_output_limit_bytes=total_output_limit_bytes,
    )


async def run_reviewer_adapter(
    resolved: ResolvedReviewerPolicy,
    *,
    prompt: bytes,
    cwd: str | Path,
    environment: dict[str, str],
    deadline: float,
    terminate_grace_seconds: float,
    stdout_limit_bytes: int,
    stderr_limit_bytes: int,
    total_output_limit_bytes: int,
) -> AdapterAttempt:
    """Probe, then invoke one reviewer inside one shared absolute deadline."""

    if resolved.executable is None:
        return AdapterAttempt(
            resolved=resolved,
            capability=None,
            invocation=None,
            capability_proven=False,
        )
    executable = resolved.executable
    policy = resolved.policy
    seat_environment = reviewer_process_environment(policy, environment)
    _assert_executable_identity(resolved)
    capability = await run_bounded_process(
        (executable, *policy.capability_argv),
        cwd=cwd,
        env=seat_environment,
        limits=_process_limits(
            deadline=deadline,
            terminate_grace_seconds=terminate_grace_seconds,
            stdin_limit_bytes=0,
            stdout_limit_bytes=stdout_limit_bytes,
            stderr_limit_bytes=stderr_limit_bytes,
            total_output_limit_bytes=total_output_limit_bytes,
        ),
    )
    _assert_executable_identity(resolved)
    proven = _capability_is_proven(policy, capability)
    if not proven:
        return AdapterAttempt(
            resolved=resolved,
            capability=capability,
            invocation=None,
            capability_proven=False,
        )
    _assert_executable_identity(resolved)
    if policy.prompt_transport == "stdin":
        invocation_argv = (executable, *policy.invocation_argv)
        stdin_bytes = prompt
        stdin_limit_bytes = len(prompt)
    else:
        # Kimi's documented one-shot mode accepts the prompt only as the value
        # of --prompt.  Passing one decoded string directly to exec avoids a
        # shell and therefore gives reviewed bytes no command-parsing surface.
        invocation_argv = (
            executable,
            *policy.invocation_argv,
            prompt.decode("utf-8"),
        )
        stdin_bytes = None
        stdin_limit_bytes = 0
    invocation = await run_bounded_process(
        invocation_argv,
        cwd=cwd,
        env=seat_environment,
        limits=_process_limits(
            deadline=deadline,
            terminate_grace_seconds=terminate_grace_seconds,
            stdin_limit_bytes=stdin_limit_bytes,
            stdout_limit_bytes=stdout_limit_bytes,
            stderr_limit_bytes=stderr_limit_bytes,
            total_output_limit_bytes=total_output_limit_bytes,
        ),
        stdin_bytes=stdin_bytes,
    )
    _assert_executable_identity(resolved)
    return AdapterAttempt(
        resolved=resolved,
        capability=capability,
        invocation=invocation,
        capability_proven=True,
    )
