"""Shared session invocation proof and controller disposition."""
from __future__ import annotations

import hashlib
import json
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from gnd.agents import (
    AgentAdapterId,
    InvocationResult,
    InvocationStatus,
    build_agent_argv,
)
from gnd.exp.adapter_policy import ResolvedAdapterPolicy
from gnd.exp.declared_invocation import (
    DeclaredInvocationResult,
    declared_effective_prompt,
)
from gnd.exp.session_contract import (
    DataDrivenContract,
    SessionCase,
)
from gnd.exp.session_eval import (
    AttemptEvaluation,
)

Verifier = Callable[[SessionCase, Path], Awaitable[tuple[int, bytes]]]
SessionInvoker = Callable[..., Awaitable[InvocationResult]]
DeclaredSessionInvoker = Callable[..., Awaitable[DeclaredInvocationResult]]
InvocationEvidence = InvocationResult | DeclaredInvocationResult

_VERIFIER_FAILURE_REASON = "one or more declared verifier cases did not produce valid evidence"


def _required_evidence_complete(
    contract: DataDrivenContract,
    evaluation: AttemptEvaluation,
) -> bool:
    """Whether every required case has one current, schema-valid result."""

    by_id = {result.case_id: result for result in evaluation.results}
    return all(
        (result := by_id.get(case.case_id)) is not None
        and result.payload_valid
        and result.role == "required"
        and result.process_exit != 70
        and result.payload_exit != 70
        and result.outcome != "internal_error"
        and result.candidate_sha256 == evaluation.candidate_sha256
        and result.contract_sha256 == evaluation.contract_sha256
        for case in contract.required_cases
    )


def _has_verifier_harness_failure(evaluation: AttemptEvaluation) -> bool:
    """Whether any declared result reports the closed internal-error band."""

    return any(
        result.process_exit == 70 or result.payload_exit == 70 or result.outcome == "internal_error"
        for result in evaluation.results
    )


def _declared_evidence_complete(
    contract: DataDrivenContract,
    evaluation: AttemptEvaluation,
) -> bool:
    """Whether every declared verifier case produced one valid result."""

    by_id = {result.case_id: result for result in evaluation.results}
    return all(
        (result := by_id.get(case.case_id)) is not None
        and result.payload_valid
        and result.role == case.role.value
        and result.candidate_sha256 == evaluation.candidate_sha256
        and result.contract_sha256 == evaluation.contract_sha256
        for case in contract.cases
    )


def _agent_failure_reason(invocation: InvocationEvidence) -> str:
    if invocation.status is InvocationStatus.timed_out:
        return "agent attempt timed out"
    if not invocation.spawned:
        detail = invocation.spawn_error or "unknown spawn error"
        return f"agent process did not start ({detail})"
    return f"agent exited {invocation.exit_code}"


def _expected_invocation_argv(
    adapter: AgentAdapterId,
    *,
    prompt: str,
    feedback_sha256: str | None,
) -> tuple[str, ...]:
    effective = _effective_agent_prompt(prompt, feedback_sha256=feedback_sha256)
    prompt_token = f"<prompt:sha256={hashlib.sha256(effective.encode('utf-8')).hexdigest()}>"
    fixed = build_agent_argv(adapter, effective)
    return (*fixed[:-1], prompt_token)


def _effective_agent_prompt(prompt: str, *, feedback_sha256: str | None) -> str:
    effective = prompt
    if feedback_sha256 is not None:
        effective = (
            f"{prompt}\n\nCurrent attempt feedback SHA-256: {feedback_sha256}\n"
            "Canonical current-attempt feedback is supplied byte-for-byte on stdin."
        )
    return effective


def _effective_policy_sha256(contract: DataDrivenContract) -> str:
    encoded = json.dumps(
        contract.model_dump(mode="json"),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _policy_bound_prompt(prompt: str, contract: DataDrivenContract) -> str:
    return f"{prompt}\n\nSession policy SHA-256: {_effective_policy_sha256(contract)}"


def _validated_invocation_proof(
    invocation: InvocationResult,
    *,
    adapter: AgentAdapterId,
    prompt: str,
    feedback_sha256: str | None,
    bind_missing_identity: bool,
) -> InvocationResult:
    """Validate one invocation boundary and bind controller-owned request identity.

    Injected invokers predate the request-identity fields, so the live
    controller may fill only omitted identity from the exact arguments it
    supplied. Explicit claims are never overwritten. Immutable replay requires
    the complete bound form and therefore follows the same validation path.
    """

    if not invocation.process_group_cleaned:
        raise ValueError("agent invocation does not prove process-group cleanup")
    invocation.ensure_closed_provenance()
    if invocation.adapter is not adapter:
        raise ValueError("agent invocation belongs to a different agent adapter")
    if invocation.status is InvocationStatus.succeeded and (
        not invocation.spawned
        or invocation.termination == "not-started"
        or invocation.exit_code != 0
    ):
        raise ValueError("successful agent invocation has inconsistent launch evidence")

    expected_prompt_sha256 = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
    if invocation.prompt_sha256 is not None and invocation.prompt_sha256 != expected_prompt_sha256:
        raise ValueError("agent invocation belongs to different agent instructions")
    if invocation.feedback_sha256 is not None and invocation.feedback_sha256 != feedback_sha256:
        raise ValueError("agent invocation names stale retry feedback")

    expected_argv = _expected_invocation_argv(
        adapter,
        prompt=prompt,
        feedback_sha256=feedback_sha256,
    )
    has_bound_prompt_argv = any(
        len(argument) == len("<prompt:sha256=>") + 64
        and argument.startswith("<prompt:sha256=")
        and argument.endswith(">")
        and all(character in "0123456789abcdef" for character in argument[15:-1])
        for argument in invocation.argv
    )
    if has_bound_prompt_argv and invocation.argv != expected_argv:
        raise ValueError("agent invocation has stale fixed adapter arguments")

    if bind_missing_identity:
        return invocation.model_copy(
            update={
                "argv": expected_argv,
                "prompt_sha256": expected_prompt_sha256,
                "feedback_sha256": feedback_sha256,
            }
        )
    if invocation.prompt_sha256 is None:
        raise ValueError("attempt evidence lacks agent instruction identity")
    if invocation.feedback_sha256 != feedback_sha256:
        raise ValueError("attempt evidence names stale retry feedback")
    if invocation.argv != expected_argv:
        raise ValueError("attempt evidence has stale fixed adapter arguments")
    return invocation


def _validated_declared_invocation_proof(
    invocation: DeclaredInvocationResult,
    *,
    policy: ResolvedAdapterPolicy,
    prompt: str,
    feedback_bytes: bytes | None,
    feedback_sha256: str | None,
) -> DeclaredInvocationResult:
    """Bind declared invocation evidence to controller-owned policy inputs."""

    if (
        invocation.policy_id != policy.policy.policy_id
        or invocation.policy_kind != policy.policy.kind
        or invocation.policy_sha256 != policy.policy_sha256
    ):
        raise ValueError("declared invocation belongs to a different adapter policy")
    if not invocation.process_group_cleaned:
        raise ValueError("declared invocation does not prove cleanup")
    expected_prompt = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
    if invocation.prompt_sha256 != expected_prompt:
        raise ValueError("declared invocation belongs to different agent instructions")
    if invocation.feedback_sha256 != feedback_sha256:
        raise ValueError("declared invocation names stale retry feedback")
    effective = declared_effective_prompt(
        prompt,
        policy_kind=policy.policy.kind,
        feedback_bytes=feedback_bytes,
        feedback_sha256=feedback_sha256,
    )
    expected_effective = hashlib.sha256(effective.encode("utf-8")).hexdigest()
    if invocation.effective_prompt_sha256 != expected_effective:
        raise ValueError("declared invocation binds a stale effective prompt")
    return invocation


def _budget_reason(*, wall_bound_hit: bool) -> str:
    if wall_bound_hit:
        return "session wall budget exhausted"
    return "session attempt budget exhausted without required-case acceptance"


@dataclass(frozen=True, slots=True)
class _Disposition:
    value: Literal[
        "accepted",
        "retry",
        "agent-failure",
        "verifier-failure",
        "stagnation",
        "oscillation",
        "budget-exhausted",
    ]
    reason: str


def _decide_disposition(
    *,
    invocation: InvocationEvidence,
    accepted: bool,
    explicit_wall_expiry: bool,
    wall_bound_hit: bool,
    verifier_failed: bool,
    recurrence_disposition: Literal["stagnation", "oscillation"] | None,
    recurrence_first_seen: int | None,
    attempt_bound_hit: bool,
) -> _Disposition:
    """Apply one precedence table to live and replayed immutable attempts."""

    if accepted:
        return _Disposition("accepted", "all required cases accepted")
    if explicit_wall_expiry:
        return _Disposition(
            "budget-exhausted",
            _budget_reason(wall_bound_hit=True),
        )
    if invocation.status is not InvocationStatus.succeeded:
        return _Disposition("agent-failure", _agent_failure_reason(invocation))
    if verifier_failed:
        return _Disposition("verifier-failure", _VERIFIER_FAILURE_REASON)
    if recurrence_disposition is not None:
        if recurrence_first_seen is None:  # pragma: no cover - caller invariant
            raise ValueError("recurrence disposition lacks its first attempt")
        return _Disposition(
            recurrence_disposition,
            f"exact candidate/signature pair first seen at attempt {recurrence_first_seen}",
        )
    if wall_bound_hit:
        return _Disposition(
            "budget-exhausted",
            _budget_reason(wall_bound_hit=True),
        )
    if attempt_bound_hit:
        return _Disposition(
            "budget-exhausted",
            _budget_reason(wall_bound_hit=False),
        )
    return _Disposition("retry", "")




# Preserve the historical public qualification of moved objects.
_required_evidence_complete.__module__ = "gnd.exp.session"
_has_verifier_harness_failure.__module__ = "gnd.exp.session"
_declared_evidence_complete.__module__ = "gnd.exp.session"
_agent_failure_reason.__module__ = "gnd.exp.session"
_expected_invocation_argv.__module__ = "gnd.exp.session"
_effective_agent_prompt.__module__ = "gnd.exp.session"
_effective_policy_sha256.__module__ = "gnd.exp.session"
_policy_bound_prompt.__module__ = "gnd.exp.session"
_validated_invocation_proof.__module__ = "gnd.exp.session"
_validated_declared_invocation_proof.__module__ = "gnd.exp.session"
_budget_reason.__module__ = "gnd.exp.session"
_Disposition.__module__ = "gnd.exp.session"
_decide_disposition.__module__ = "gnd.exp.session"
