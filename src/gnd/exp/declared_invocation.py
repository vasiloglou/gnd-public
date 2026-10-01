"""Closed evidence model shared by declared adapter execution and sessions."""

from __future__ import annotations

import base64
import math
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from gnd.agent_cli import EnvironmentFact, InvocationStatus

__all__ = ["DeclaredInvocationResult", "declared_effective_prompt"]


def declared_effective_prompt(
    prompt: str,
    *,
    policy_kind: Literal["command", "openai-compatible"],
    feedback_bytes: bytes | None,
    feedback_sha256: str | None,
) -> str:
    """Return the exact retry prompt shape shared by controller and adapter."""

    if feedback_sha256 is None:
        return prompt
    if feedback_bytes is None:
        raise ValueError("feedback bytes and digest must be supplied together")
    if policy_kind == "command":
        return (
            f"{prompt}\n\nCurrent attempt feedback SHA-256: {feedback_sha256}\n"
            "Canonical current-attempt feedback is supplied byte-for-byte by the "
            "adapter transport."
        )
    encoded = base64.b64encode(feedback_bytes).decode("ascii")
    return (
        f"{prompt}\n\nCurrent attempt feedback SHA-256: {feedback_sha256}\n"
        "Canonical current-attempt feedback (RFC 4648 base64):\n"
        f"{encoded}"
    )


class DeclaredInvocationResult(BaseModel):
    """Sanitized one-process or one-request provenance.

    Raw streams are usable by the evidence store but excluded from the JSON
    model. Trusted policy paths, endpoint text, credential names and credential
    values are absent by construction.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    policy_id: str = Field(min_length=1)
    policy_kind: Literal["command", "openai-compatible"]
    policy_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    status: InvocationStatus
    executable: str | None = None
    executable_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    endpoint_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    version: str = ""
    argv: tuple[str, ...] = ()
    cwd: Literal["<candidate-root>"] = "<candidate-root>"
    spawned: bool
    spawn_error: str | None = None
    termination: Literal["not-started", "exited", "terminated", "killed"]
    process_group_cleaned: bool
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
    request_bytes: int = Field(ge=0)
    response_header_bytes: int = Field(ge=0)
    response_body_bytes: int = Field(ge=0)
    prompt_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    effective_prompt_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    feedback_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    stdout: bytes = Field(exclude=True, repr=False)
    stderr: bytes = Field(exclude=True, repr=False)

    @model_validator(mode="after")
    def _provenance_is_closed(self) -> Self:
        if (
            not math.isfinite(self.started_monotonic)
            or not math.isfinite(self.ended_monotonic)
            or self.ended_monotonic < self.started_monotonic
        ):
            raise ValueError("invocation end cannot precede its start")
        if self.policy_kind == "command":
            if self.executable is None or self.executable_sha256 is None:
                raise ValueError("command evidence requires executable identity")
            if self.endpoint_sha256 is not None or self.request_bytes:
                raise ValueError("command evidence cannot carry HTTP provenance")
        else:
            if self.endpoint_sha256 is None or self.executable is not None or self.argv:
                raise ValueError("HTTP evidence requires only sanitized endpoint identity")
            if self.environment:
                raise ValueError("HTTP evidence never retains credential environment names")
        if self.status is InvocationStatus.succeeded:
            if not self.spawned or self.termination != "exited" or self.exit_code != 0:
                raise ValueError("successful invocation requires one clean completed operation")
            if self.spawn_error is not None:
                raise ValueError("successful invocation cannot carry a failure reason")
        elif not self.spawned:
            if self.termination != "not-started" or self.exit_code is not None:
                raise ValueError("unstarted invocation cannot claim termination or exit")
            if self.spawn_error is None:
                raise ValueError("unstarted invocation requires a closed failure reason")
        return self
