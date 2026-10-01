"""Programmatic one-attempt controller for data-driven experiment sessions."""

from __future__ import annotations

import asyncio
import hashlib
import json
import math
import os
import shutil
import sys
import tempfile
import time
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Literal

from gnd.agent_cli import (
    AgentAdapterId,
    AgentCLIError,
    InvocationResult,
    InvocationStatus,
    ProcessLimits,
    build_agent_argv,
    invoke_agent,
    run_bounded_process,
)
from gnd.exp.adapter_policy import ResolvedAdapterPolicy
from gnd.exp.declared_invocation import (
    DeclaredInvocationResult,
    declared_effective_prompt,
)
from gnd.exp.session_contract import (
    DECLARED_ADAPTER_SESSION_CONTRACT_VERSION,
    ConstraintSatisfactionAcceptance,
    DataDrivenContract,
    SessionCase,
    TestsAcceptance,
    TransitionAcceptance,
)
from gnd.exp.session_eval import (
    ASSURANCE_FEEDBACK_SCHEMA_VERSION,
    DERIVATION_FEEDBACK_SCHEMA_VERSION,
    FEEDBACK_SCHEMA_VERSION,
    REDACTION_FEEDBACK_SCHEMA_VERSION,
    TRANSITION_FEEDBACK_SCHEMA_VERSION,
    WALK_FLOOR_FEEDBACK_SCHEMA_VERSION,
    AttemptEvaluation,
    CaseEvaluation,
    SessionRedaction,
    SessionRedactionDeclaration,
    VerifierPayloadError,
    attach_walk_floor_steps,
    best_key,
    build_attempt_feedback,
    canonical_feedback,
    case_decision,
    contract_accepts,
    normalized_verifier_signature,
    observe_expected_outputs,
    validate_tests_payload,
    validate_transition_payload,
    validate_verifier_payload,
)
from gnd.exp.session_store import (
    REDACTION_RESULT_SCHEMA_VERSION,
    TRANSITION_RESULT_SCHEMA_VERSION,
    WALK_FLOOR_RESULT_SCHEMA_VERSION,
    AttemptRecord,
    SessionResult,
    SessionStore,
    StagedCandidate,
    WalkFloorResult,
)
from gnd.report import DERIVATION_PAYLOAD_SCHEMA_VERSIONS, PAYLOAD_SCHEMA_VERSION

__all__ = [
    "case_payload_versions",
    "case_redaction",
    "run_gnd_verifier",
    "run_session",
    "verifier_environment",
]

Verifier = Callable[[SessionCase, Path], Awaitable[tuple[int, bytes]]]
SessionInvoker = Callable[..., Awaitable[InvocationResult]]
DeclaredSessionInvoker = Callable[..., Awaitable[DeclaredInvocationResult]]
InvocationEvidence = InvocationResult | DeclaredInvocationResult

_VERIFIER_FAILURE_REASON = "one or more declared verifier cases did not produce valid evidence"


def verifier_environment() -> dict[str, str]:
    """Return the live environment allowlist shared by verifier processes."""

    return {
        name: os.environ[name]
        for name in ("PATH", "HOME", "TMPDIR", "LANG", "LC_ALL", "SSL_CERT_FILE")
        if name in os.environ
    }


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


def _discard_unpublished_stage(
    store: SessionStore,
    *,
    attempt_index: int,
    staged: StagedCandidate,
) -> None:
    """Discard only the identity-bound staging tree created by this store."""

    store._discard_staged(attempt_index, staged)
    if staged._staging_path.exists():
        raise RuntimeError("identity-bound staged candidate could not be discarded")


@dataclass(frozen=True, slots=True)
class _PublishedAttempt:
    record: AttemptRecord
    evaluation: AttemptEvaluation
    feedback_bytes: bytes
    feedback_sha256: str
    accepted: bool
    pair: tuple[str, str]
    decision: _Disposition
    eligible: bool


def _publish_current_attempt(
    *,
    store: SessionStore,
    staged: StagedCandidate,
    candidate_path: Path,
    contract: DataDrivenContract,
    contract_sha256: str,
    invocation: InvocationEvidence,
    raw_payloads: dict[str, bytes],
    results: list[CaseEvaluation],
    verifier_failure: str | None,
    wall_expired: bool,
    wall_bound_hit: bool,
    attempt_bound_hit: bool,
    seen: dict[tuple[str, str], int],
    attempt_index: int,
    attempt_elapsed: float,
    feedback_schema_version: int = FEEDBACK_SCHEMA_VERSION,
    redaction: SessionRedaction | None = None,
) -> _PublishedAttempt:
    """Close one staged attempt or remove every unpublished staging byte."""

    try:
        evaluation = AttemptEvaluation(
            attempt_index=attempt_index,
            candidate_sha256=staged.inventory.tree_sha256,
            contract_sha256=contract_sha256,
            results=tuple(results),
        )
        accepted = invocation.status is InvocationStatus.succeeded and contract_accepts(
            contract, evaluation
        )
        pair = (
            staged.inventory.tree_sha256,
            normalized_verifier_signature(
                contract,
                evaluation,
                schema_version=feedback_schema_version,
            ),
        )
        first_seen = seen.get(pair)
        recurrence_disposition: Literal["stagnation", "oscillation"] | None = None
        if not accepted and first_seen is not None:
            recurrence_disposition = (
                "stagnation" if first_seen == attempt_index - 1 else "oscillation"
            )
        verifier_incomplete = not _declared_evidence_complete(contract, evaluation)
        verifier_harness_failure = _has_verifier_harness_failure(evaluation)
        decision = _decide_disposition(
            invocation=invocation,
            accepted=accepted,
            explicit_wall_expiry=(
                wall_expired
                or invocation.status is InvocationStatus.timed_out
                or (wall_bound_hit and verifier_incomplete)
            ),
            wall_bound_hit=wall_bound_hit,
            verifier_failed=(
                verifier_failure is not None or verifier_incomplete or verifier_harness_failure
            ),
            recurrence_disposition=recurrence_disposition,
            recurrence_first_seen=first_seen,
            attempt_bound_hit=attempt_bound_hit,
        )
        feedback = build_attempt_feedback(
            run_id=store.run_id,
            contract=contract,
            contract_sha256=contract_sha256,
            invocation=invocation,
            evaluation=evaluation,
            disposition=decision.value,
            schema_version=feedback_schema_version,
            redaction=redaction,
        )
        feedback_bytes, feedback_sha256 = canonical_feedback(feedback)
        store.publish_feedback(
            attempt_index=attempt_index,
            feedback=feedback,
            staged_candidate=staged,
        )
        eligible = invocation.status is InvocationStatus.succeeded and _required_evidence_complete(
            contract, evaluation
        )
        record = store.publish_attempt(
            attempt_index=attempt_index,
            candidate_root=candidate_path,
            invocation=invocation,
            verifier_payloads=raw_payloads,
            evaluation=evaluation,
            contract=contract,
            best_eligible=eligible,
            staged_candidate=staged,
            elapsed_seconds=attempt_elapsed,
        )
    except BaseException:
        _discard_unpublished_stage(
            store,
            attempt_index=attempt_index,
            staged=staged,
        )
        raise
    return _PublishedAttempt(
        record=record,
        evaluation=evaluation,
        feedback_bytes=feedback_bytes,
        feedback_sha256=feedback_sha256,
        accepted=accepted,
        pair=pair,
        decision=decision,
        eligible=eligible,
    )


def _copy_bound_model(
    case: SessionCase,
    experiment_root: Path,
    view: Path,
) -> None:
    """Copy a freshly rechecked contract model into an isolated verifier view."""

    from gnd.exp.session_contract import MAX_SESSION_INPUT_BYTES
    from gnd.extract.manifest import open_manifest_relative_path

    bound = case.verify.model
    anchor = experiment_root / ".session-contract-anchor"
    with open_manifest_relative_path(
        anchor,
        bound.path,
        field=f"cases.{case.case_id}.verify.model.path",
        rule_id="experiment:session-contract-invalid",
    ) as (_, stream):
        data = stream.read(MAX_SESSION_INPUT_BYTES + 1)
    if len(data) > MAX_SESSION_INPUT_BYTES:
        raise ValueError("session verifier model grew over its byte cap")
    if len(data) != bound.size_bytes or hashlib.sha256(data).hexdigest() != bound.sha256:
        raise ValueError("session verifier model changed after contract validation")

    destination = view.joinpath(*PurePosixPath(bound.path).parts)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        if destination.is_dir():
            raise ValueError("session verifier model path collides with a candidate directory")
        destination.unlink()
    destination.write_bytes(data)

    for index, input_file in enumerate(case.inputs):
        with open_manifest_relative_path(
            anchor,
            input_file.path,
            field=f"cases.{case.case_id}.inputs.{index}.path",
            rule_id="experiment:session-contract-invalid",
        ) as (_, stream):
            input_data = stream.read(MAX_SESSION_INPUT_BYTES + 1)
        if (
            len(input_data) != input_file.size_bytes
            or hashlib.sha256(input_data).hexdigest() != input_file.sha256
        ):
            raise ValueError("session verifier input changed after contract validation")
        input_destination = view.joinpath(*PurePosixPath(input_file.path).parts)
        input_destination.parent.mkdir(parents=True, exist_ok=True)
        if input_destination.exists() and input_destination.is_dir():
            raise ValueError("session verifier input path collides with a candidate directory")
        input_destination.write_bytes(input_data)


def _case_models(
    contract: DataDrivenContract,
    experiment_root: Path,
) -> list[tuple[SessionCase, object]]:
    """Load each non-tests case model through its digest-bound contract path."""

    from gnd.exp.session_contract import MAX_SESSION_INPUT_BYTES
    from gnd.extract.manifest import open_manifest_relative_path
    from gnd.model import load_model

    if contract.schema_version in {7, 8}:
        from gnd.exp.session_v7 import _model

        return [
            (case, _model(case, experiment_root)[0])
            for case in contract.cases
            if case.verify is not None
        ]
    models: list[tuple[SessionCase, object]] = []
    anchor = experiment_root / ".session-contract-anchor"
    for case in contract.cases:
        if isinstance(case.acceptance, TestsAcceptance):
            continue
        bound = case.verify.model
        with open_manifest_relative_path(
            anchor,
            bound.path,
            field=f"cases.{case.case_id}.verify.model.path",
            rule_id="experiment:session-contract-invalid",
        ) as (_, stream):
            data = stream.read(MAX_SESSION_INPUT_BYTES + 1)
        if len(data) != bound.size_bytes or hashlib.sha256(data).hexdigest() != bound.sha256:
            raise ValueError("session verifier model changed after contract validation")
        with tempfile.NamedTemporaryFile("wb", suffix=".orm.yaml") as handle:
            handle.write(data)
            handle.flush()
            models.append((case, load_model(handle.name)))
    return models


def case_payload_versions(
    contract: DataDrivenContract,
    experiment_root: Path,
) -> dict[str, int]:
    """The report schema version each case's digest-bound MODEL selects.

    D-P3.4 (v5.0 Phase 3): the model, never a constant, decides which payload
    version counts as this case's verifier evidence. The bytes are resolved
    and digest-checked exactly like :func:`_copy_bound_model` and loaded from
    a private copy, so the version cannot be decided by a file that changed
    after contract validation.

    v5.1 Phase 3: the session verifier runs `gnd check` or `gnd verify`, so it
    selects through the MODEL-BOUND selector and moves exactly when those two
    commands move. `validate` and `transition` keep the frozen versions, which
    is why this is the model-bound function rather than a widened
    :func:`payload_schema_version`.
    """

    from gnd.redaction import RedactionPolicy
    from gnd.report import current_payload_schema_version

    versions: dict[str, int] = {}
    for case, model in _case_models(contract, experiment_root):
        if contract.schema_version in {7, 8} and isinstance(
            case.acceptance, ConstraintSatisfactionAcceptance
        ):
            from gnd.terms import uses_temporal

            versions[case.case_id] = (
                (14 if uses_temporal(model) else 12)
                if model.reference_populations
                else (13 if uses_temporal(model) else 10)
            )
        elif RedactionPolicy.from_model(model).active:
            versions[case.case_id] = 9
        elif isinstance(case.acceptance, TransitionAcceptance):
            versions[case.case_id] = 8 if case.verify.post is None else 7
        else:
            versions[case.case_id] = current_payload_schema_version(model)
    return versions


def case_redaction(
    contract: DataDrivenContract,
    experiment_root: Path,
) -> SessionRedaction | None:
    """Return the applied, case-scoped policy selected by bound case models."""

    from gnd.redaction import RedactionPolicy

    declarations = [
        SessionRedactionDeclaration.model_validate(declaration.as_dict())
        for case, model in _case_models(contract, experiment_root)
        for declaration in RedactionPolicy.from_model(
            model,
            case_id=case.case_id,
        ).declarations
    ]
    if not declarations:
        return None
    declarations.sort(key=lambda row: (row.case_id, row.fact_type, row.source, row.roles))
    return SessionRedaction(mode="applied", declarations=tuple(declarations))


async def run_gnd_verifier(
    case: SessionCase,
    snapshot: Path,
    *,
    experiment_root: Path,
    timeout_seconds: float = 300.0,
) -> tuple[int, bytes]:
    """Run one fixed GND verifier command over an isolated immutable view.

    The contract selects only ``check`` or ``verify`` and normalized data paths;
    Python owns the executable and every option. Copying into a temporary view
    preserves the contract's exact payload identities while the model bytes
    still come from the digest-bound experiment artifact.
    """

    import secrets

    from gnd.assurance_transport import _NONCE_ENV, _PATH_ENV, consume_receipt, producer_identity
    from gnd.exp.session_eval import MAX_VERIFIER_PAYLOAD_BYTES

    with tempfile.TemporaryDirectory(prefix="gnd-session-verify-") as temporary:
        view = Path(temporary) / "view"
        shutil.copytree(snapshot, view, dirs_exist_ok=True)
        _copy_bound_model(case, experiment_root, view)
        if case._session_version in {7, 8} and case.reference_root is not None:
            from gnd.exp.session_v7 import _model

            _selected_model, context = _model(case, experiment_root)
            for _origin, relative, raw in context._snapshots:
                destination = view / Path(case.verify.model.path).parent / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                if destination.exists():
                    raise ValueError("candidate collides with bound reference")
                destination.write_bytes(raw)
        argv = [sys.executable, "-I", "-m", "gnd", "check", case.verify.model.path]
        if isinstance(case.acceptance, TransitionAcceptance):
            argv.extend(("--pre", case.verify.pre, "--steps", case.verify.steps))
            if case.verify.post is not None:
                argv.extend(("--post", case.verify.post))
        else:
            argv.append(case.verify.subject)
        if case._session_version in {7, 8} and isinstance(
            case.acceptance, ConstraintSatisfactionAcceptance
        ):
            argv.append("--admission")
        argv.extend(("--format", "json"))
        if case.verify.command == "verify" and (view / "artifacts").is_dir():
            argv.extend(("--artifacts", "artifacts"))
        environment = verifier_environment()
        receipt_path = Path(temporary) / "execution-receipt.json"
        nonce = secrets.token_hex(32)
        try:
            producer = producer_identity()
        except (OSError, ValueError):
            producer = None
        if producer is not None:
            environment.update({_PATH_ENV: str(receipt_path), _NONCE_ENV: nonce})
        result = await run_bounded_process(
            tuple(argv),
            cwd=view,
            env=environment,
            limits=ProcessLimits(
                timeout_seconds=timeout_seconds,
                terminate_grace_seconds=min(1.0, timeout_seconds),
                stdin_limit_bytes=0,
                stdout_limit_bytes=MAX_VERIFIER_PAYLOAD_BYTES,
                stderr_limit_bytes=MAX_VERIFIER_PAYLOAD_BYTES,
                total_output_limit_bytes=MAX_VERIFIER_PAYLOAD_BYTES * 2,
            ),
        )
        if not result.process_group_cleaned:
            raise AgentCLIError("trusted GND verifier cleanup could not be proven")
        if result.status == "timed-out":
            raise RuntimeError("GND verifier exceeded the session wall bound")
        if result.status == "spawn-failed":
            raise RuntimeError("trusted GND verifier process could not be spawned")
        if result.stdout_observed_bytes > MAX_VERIFIER_PAYLOAD_BYTES:
            raise ValueError("GND verifier output exceeded the retained payload cap")
        if result.stderr_observed_bytes > MAX_VERIFIER_PAYLOAD_BYTES:
            raise ValueError("GND verifier stderr exceeded the retained payload cap")
        if result.return_code is None:  # pragma: no cover - closed result invariant
            raise RuntimeError("trusted GND verifier process has no exit status")
        if producer is None:
            return result.return_code, result.stdout
        return result.return_code, consume_receipt(
            receipt_path, nonce=nonce, producer=producer, raw=result.stdout, case_id=case.case_id
        )


async def run_session(
    contract: DataDrivenContract,
    *,
    contract_sha256: str,
    adapter_id: AgentAdapterId | None = None,
    adapter_policy: ResolvedAdapterPolicy | None = None,
    prompt: str,
    candidate_root: str | Path,
    run_root: str | Path,
    verifier: Verifier,
    invoker: SessionInvoker | None = None,
    declared_invoker: DeclaredSessionInvoker | None = None,
    expected_payload_versions: Mapping[str, int] | None = None,
    redaction: SessionRedaction | None = None,
) -> SessionResult:
    """Run or resume a deterministic bounded agent/verifier feedback session.

    ``expected_payload_versions`` maps case id to the report schema version
    that case's model selects (:func:`case_payload_versions`); an absent entry
    expects the base version 3, which keeps every pre-derivation session and
    call site byte-identical. Any case expecting a derivation-carrying version
    promotes the whole session's feedback wire to schema version 3 (D-P3.2).

    v5.1 Phase 3 deliberately leaves the fallback on the frozen version 3. A
    programmatic caller that hands this function a handcrafted legacy payload
    is entitled to the meaning it was written against, and production
    orchestration never relies on the fallback: ``gnd exp run`` always computes
    the map with :func:`case_payload_versions`, which selects the model-bound
    pair.
    """

    if contract.schema_version in {7, 8}:
        if (
            adapter_policy is None
            or declared_invoker is None
            or adapter_id is not None
            or invoker is not None
        ):
            raise ValueError("v7 requires exactly one declared adapter")
        from gnd.exp.session_v7 import run

        return await run(
            contract,
            contract_sha256=contract_sha256,
            adapter_policy=adapter_policy,
            prompt=prompt,
            candidate_root=candidate_root,
            run_root=run_root,
            verifier=verifier,
            declared_invoker=declared_invoker,
            redaction=redaction,
        )
    declared_session = contract.schema_version == DECLARED_ADAPTER_SESSION_CONTRACT_VERSION
    if declared_session:
        if (
            adapter_policy is None
            or adapter_id is not None
            or contract.adapter is None
            or declared_invoker is None
        ):
            raise ValueError("schema-v6 sessions require exactly one declared adapter policy")
        if (
            adapter_policy.policy.policy_id != contract.adapter.policy_id
            or adapter_policy.model != contract.adapter.parameters.model
        ):
            raise ValueError("declared adapter policy does not match the session contract")
        if invoker is not None:
            raise ValueError("legacy invoker cannot execute a declared adapter session")
    elif adapter_id is None or adapter_policy is not None or declared_invoker is not None:
        raise ValueError("legacy sessions require exactly one closed adapter id")

    candidate_path = Path(candidate_root).resolve(strict=True)
    root = Path(run_root).resolve(strict=False)
    try:
        root.relative_to(candidate_path)
    except ValueError:
        pass
    else:
        raise ValueError("run evidence must live outside the mutable candidate root")
    controller_prompt = _policy_bound_prompt(prompt, contract)
    payload_versions: dict[str, int] = dict(expected_payload_versions or {})
    if (redaction is not None) != any(version == 9 for version in payload_versions.values()):
        raise ValueError("session redaction metadata and report-v9 cases must be selected together")

    def expected_version(case_id: str) -> int:
        return payload_versions.get(case_id, PAYLOAD_SCHEMA_VERSION)

    # The question is "does this session's verifier evidence carry derivation
    # obligations", not "is the payload version literally 4". v5.1 Phase 3
    # pairs the wire, so the structured arm is 4 OR its model-bound successor
    # 6; the membership set lives in gnd.report so the pairing has one home.
    has_walk_floor = any(
        isinstance(case.acceptance, TransitionAcceptance) and case.acceptance.walk is not None
        for case in contract.cases
    )
    feedback_schema_version = (
        WALK_FLOOR_FEEDBACK_SCHEMA_VERSION
        if has_walk_floor
        else REDACTION_FEEDBACK_SCHEMA_VERSION
        if redaction is not None
        else TRANSITION_FEEDBACK_SCHEMA_VERSION
        if any(isinstance(case.acceptance, TransitionAcceptance) for case in contract.cases)
        else ASSURANCE_FEEDBACK_SCHEMA_VERSION
        if any(version == 7 for version in payload_versions.values())
        else DERIVATION_FEEDBACK_SCHEMA_VERSION
        if any(
            version in DERIVATION_PAYLOAD_SCHEMA_VERSIONS for version in payload_versions.values()
        )
        else FEEDBACK_SCHEMA_VERSION
    )
    store = SessionStore(
        root,
        run_id=root.name,
        contract_id=contract.experiment_id,
    )
    resume = store.read_resume_state(contract, expected_payload_versions=payload_versions)

    records: list[AttemptRecord] = []
    seen: dict[tuple[str, str], int] = {}
    best_record: AttemptRecord | None = None
    best_identity = resume.best_attempt_identity
    pending_terminal: tuple[str, str, AttemptRecord] | None = None
    historical_accounted = 0.0
    historical_prior_feedback_sha256: str | None = None
    historical_prior_feedback_bytes: bytes | None = None
    last_historical_index = resume.next_attempt_index - 1
    for attempt_index in range(1, resume.next_attempt_index):
        record, _, feedback, persisted_feedback_bytes = store._load_attempt_for_resume(
            attempt_index,
            contract=contract,
            expected_payload_versions=payload_versions,
        )
        if record.evaluation.contract_sha256 != contract_sha256:
            raise ValueError("attempt evidence belongs to a different session contract digest")
        rebuilt_feedback = build_attempt_feedback(
            run_id=root.name,
            contract=contract,
            contract_sha256=contract_sha256,
            invocation=record.invocation,
            evaluation=record.evaluation,
            disposition=feedback.disposition,
            schema_version=feedback.schema_version,
            redaction=redaction,
        )
        if canonical_feedback(rebuilt_feedback)[0] != persisted_feedback_bytes:
            raise ValueError("persisted feedback is inconsistent with the supplied contract")
        if declared_session:
            assert adapter_policy is not None
            if not isinstance(record.invocation, DeclaredInvocationResult):
                raise ValueError("schema-v6 replay contains a legacy invocation")
            _validated_declared_invocation_proof(
                record.invocation,
                policy=adapter_policy,
                prompt=controller_prompt,
                feedback_bytes=historical_prior_feedback_bytes,
                feedback_sha256=historical_prior_feedback_sha256,
            )
        else:
            assert adapter_id is not None
            if not isinstance(record.invocation, InvocationResult):
                raise ValueError("legacy replay contains a declared invocation")
            _validated_invocation_proof(
                record.invocation,
                adapter=adapter_id,
                prompt=controller_prompt,
                feedback_sha256=historical_prior_feedback_sha256,
                bind_missing_identity=False,
            )
        historical_prior_feedback_sha256 = hashlib.sha256(persisted_feedback_bytes).hexdigest()
        historical_prior_feedback_bytes = persisted_feedback_bytes

        records.append(record)
        historical_accounted += record.elapsed_seconds
        expected_eligible = (
            record.invocation.status is InvocationStatus.succeeded
            and _required_evidence_complete(contract, record.evaluation)
        )
        if record.best_eligible != expected_eligible:
            raise ValueError("attempt best eligibility is inconsistent with required evidence")
        if record.best_eligible and (
            best_record is None
            or best_key(contract, record.evaluation) < best_key(contract, best_record.evaluation)
        ):
            best_record = record
        pair = (
            record.candidate_inventory.tree_sha256,
            feedback.normalized_verifier_signature,
        )
        accepted = record.invocation.status is InvocationStatus.succeeded and contract_accepts(
            contract, record.evaluation
        )
        first_seen = seen.get(pair)
        recurrence_disposition: Literal["stagnation", "oscillation"] | None = None
        if not accepted and first_seen is not None:
            recurrence_disposition = (
                "stagnation" if first_seen == attempt_index - 1 else "oscillation"
            )
        attempt_bound_hit = attempt_index >= contract.max_attempts
        wall_bound_hit = (
            contract.wall_seconds is not None and historical_accounted >= contract.wall_seconds
        )
        verifier_incomplete = not _declared_evidence_complete(
            contract,
            record.evaluation,
        )

        decision = _decide_disposition(
            invocation=record.invocation,
            accepted=accepted,
            explicit_wall_expiry=(
                record.invocation.status is InvocationStatus.timed_out
                or (wall_bound_hit and verifier_incomplete)
            ),
            wall_bound_hit=wall_bound_hit,
            verifier_failed=(
                verifier_incomplete or _has_verifier_harness_failure(record.evaluation)
            ),
            recurrence_disposition=recurrence_disposition,
            recurrence_first_seen=first_seen,
            attempt_bound_hit=attempt_bound_hit,
        )
        if feedback.disposition != decision.value:
            raise ValueError(
                "persisted feedback disposition is inconsistent with controller precedence"
            )
        if decision.value == "retry":
            seen[pair] = attempt_index
            continue
        if attempt_index != last_historical_index:
            raise ValueError("attempt evidence continues after a terminal disposition")
        pending_terminal = (decision.value, decision.reason, record)

    if not math.isclose(
        historical_accounted,
        resume.accounted_wall_seconds,
        rel_tol=0.0,
        abs_tol=1e-12,
    ):
        raise ValueError("resume wall accounting differs from immutable attempt evidence")

    def publish_terminal(
        disposition: str,
        reason: str,
        record: AttemptRecord,
    ) -> SessionResult:
        validated_resume = store.read_resume_state(
            contract, expected_payload_versions=payload_versions
        )
        if validated_resume.next_attempt_index != record.attempt_index + 1:
            raise ValueError("terminal attempt is not the final immutable record")
        loaded_record, attempt_bytes, _, _ = store._load_attempt_for_resume(
            record.attempt_index,
            contract=contract,
            expected_payload_versions=payload_versions,
        )
        # Process-local assurance capabilities are intentionally absent on replay.
        # Compare the complete persisted record, not ephemeral private attributes.
        if loaded_record.model_dump(mode="json") != record.model_dump(mode="json"):
            raise ValueError("terminal attempt changed before result publication")
        identity = validated_resume.best_attempt_identity
        if identity != best_identity:
            raise ValueError("best pointer changed before result publication")
        result = SessionResult(
            schema_version=(
                WALK_FLOOR_RESULT_SCHEMA_VERSION
                if has_walk_floor
                else REDACTION_RESULT_SCHEMA_VERSION
                if redaction is not None
                else TRANSITION_RESULT_SCHEMA_VERSION
                if any(isinstance(case.acceptance, TransitionAcceptance) for case in contract.cases)
                else 2
            ),
            run_id=root.name,
            disposition=disposition,
            terminal_reason=reason,
            attempt_count=record.attempt_index,
            best_attempt=None if identity is None else identity.attempt_index,
            best_attempt_manifest_sha256=(
                None if identity is None else identity.attempt_manifest_sha256
            ),
            best_candidate_sha256=None if identity is None else identity.candidate_sha256,
            referenced_evidence_digests={
                "attempt_manifest_sha256": hashlib.sha256(attempt_bytes).hexdigest()
            },
            acceptance_modes=tuple(sorted({case.acceptance.mode for case in contract.cases})),
            redaction=redaction,
            contract_sha256=(contract_sha256 if has_walk_floor else None),
            walk_floors=tuple(
                sorted(
                    (
                        WalkFloorResult(
                            case_id=case.case_id,
                            role=case.role.value,
                            required_ops=len(case.acceptance.walk.required_ops),
                            forbidden_ops=len(case.acceptance.walk.forbidden_ops),
                            discharged=(
                                best_record is not None
                                and (
                                    observed := {
                                        row.case_id: row for row in best_record.evaluation.results
                                    }.get(case.case_id)
                                )
                                is not None
                                and case_decision(case, observed).accepted
                            ),
                        )
                        for case in contract.cases
                        if isinstance(case.acceptance, TransitionAcceptance)
                        and case.acceptance.walk is not None
                    ),
                    key=lambda row: row.case_id,
                )
            ),
        )
        store.publish_result(result)
        return result

    if pending_terminal is not None:
        return publish_terminal(*pending_terminal)

    accounted_wall_seconds = resume.accounted_wall_seconds
    feedback_bytes = resume.prior_feedback_bytes
    feedback_sha256 = resume.prior_feedback_sha256
    next_attempt = resume.next_attempt_index
    while next_attempt <= contract.max_attempts:
        remaining = (
            None
            if contract.wall_seconds is None
            else contract.wall_seconds - accounted_wall_seconds
        )
        if remaining is not None and remaining <= 0:
            if not records:
                raise ValueError("wall budget was exhausted before any resumable attempt")
            return publish_terminal(
                "budget-exhausted",
                "session wall budget exhausted",
                records[-1],
            )

        if records:
            current_inventory = store.inventory_candidate(candidate_path)
            if current_inventory != records[-1].candidate_inventory:
                raise ValueError(
                    "mutable candidate differs from the final immutable attempt; "
                    "resume refuses unbound working bytes"
                )

        attempt_started = time.monotonic()
        if declared_session:
            assert adapter_policy is not None
            effective_agent_prompt = declared_effective_prompt(
                controller_prompt,
                policy_kind=adapter_policy.policy.kind,
                feedback_bytes=feedback_bytes,
                feedback_sha256=feedback_sha256,
            )
            store.publish_declared_launch_intent(
                attempt_index=next_attempt,
                contract_sha256=contract_sha256,
                policy_id=adapter_policy.policy.policy_id,
                policy_kind=adapter_policy.policy.kind,
                policy_sha256=adapter_policy.policy_sha256,
                model_sha256=(
                    None
                    if adapter_policy.model is None
                    else hashlib.sha256(adapter_policy.model.encode("utf-8")).hexdigest()
                ),
                base_prompt_sha256=hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
                controller_prompt_sha256=hashlib.sha256(
                    controller_prompt.encode("utf-8")
                ).hexdigest(),
                effective_prompt_sha256=hashlib.sha256(
                    effective_agent_prompt.encode("utf-8")
                ).hexdigest(),
                feedback_sha256=feedback_sha256,
                candidate_root=candidate_path,
            )
        else:
            assert adapter_id is not None
            effective_agent_prompt = _effective_agent_prompt(
                controller_prompt,
                feedback_sha256=feedback_sha256,
            )
            store.publish_launch_intent(
                attempt_index=next_attempt,
                contract_sha256=contract_sha256,
                policy_sha256=_effective_policy_sha256(contract),
                adapter=adapter_id,
                base_prompt_sha256=hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
                controller_prompt_sha256=hashlib.sha256(
                    controller_prompt.encode("utf-8")
                ).hexdigest(),
                effective_prompt_sha256=hashlib.sha256(
                    effective_agent_prompt.encode("utf-8")
                ).hexdigest(),
                feedback_sha256=feedback_sha256,
                candidate_root=candidate_path,
            )
        invocation_timeout = (
            300.0 if remaining is None else remaining - (time.monotonic() - attempt_started)
        )
        if invocation_timeout <= 0:
            raise RuntimeError("session wall bound expired after launch reservation")
        if declared_session:
            assert adapter_policy is not None
            assert declared_invoker is not None
            invocation_call = declared_invoker(
                adapter_policy,
                prompt=controller_prompt,
                cwd=candidate_path,
                timeout_seconds=invocation_timeout,
                feedback_bytes=feedback_bytes,
                feedback_sha256=feedback_sha256,
            )
            try:
                invocation = (
                    await invocation_call
                    if remaining is None
                    else await asyncio.wait_for(invocation_call, timeout=invocation_timeout)
                )
            except TimeoutError as error:
                raise RuntimeError("session invoker exceeded the monotonic wall bound") from error
            invocation = _validated_declared_invocation_proof(
                invocation,
                policy=adapter_policy,
                prompt=controller_prompt,
                feedback_bytes=feedback_bytes,
                feedback_sha256=feedback_sha256,
            )
        elif invoker is None:
            assert adapter_id is not None
            invocation = await invoke_agent(
                adapter_id,
                prompt=controller_prompt,
                cwd=candidate_path,
                timeout_seconds=invocation_timeout,
                feedback_bytes=feedback_bytes,
                feedback_sha256=feedback_sha256,
            )
        else:
            assert adapter_id is not None
            invocation_call = invoker(
                adapter_id,
                prompt=controller_prompt,
                cwd=candidate_path,
                timeout_seconds=invocation_timeout,
                feedback_bytes=feedback_bytes,
                feedback_sha256=feedback_sha256,
            )
            try:
                invocation = (
                    await invocation_call
                    if remaining is None
                    else await asyncio.wait_for(invocation_call, timeout=invocation_timeout)
                )
            except TimeoutError as error:
                raise RuntimeError("session invoker exceeded the monotonic wall bound") from error

        if not declared_session:
            assert adapter_id is not None
            assert isinstance(invocation, InvocationResult)
            invocation = _validated_invocation_proof(
                invocation,
                adapter=adapter_id,
                prompt=controller_prompt,
                feedback_sha256=feedback_sha256,
                bind_missing_identity=False,
            )

        if (
            not math.isfinite(invocation.started_monotonic)
            or not math.isfinite(invocation.ended_monotonic)
            or invocation.ended_monotonic < invocation.started_monotonic
        ):
            raise ValueError("agent invocation reported invalid monotonic timestamps")

        # Invocation return is the descendant-cleanup boundary.  Mutable bytes
        # become an immutable candidate only after that boundary.
        staged = store.stage_candidate(
            attempt_index=next_attempt,
            candidate_root=candidate_path,
        )
        candidate_sha256 = staged.inventory.tree_sha256
        # The staged inventory is the attempt's immutable identity, so expected
        # outputs are observed from it and never restatted on the candidate
        # tree, which is mutable again the moment the next attempt begins.
        candidate_files = {entry.path: entry.sha256 for entry in staged.inventory.files}
        raw_payloads: dict[str, bytes] = {}
        results = []
        verifier_failure: str | None = None
        wall_expired = False
        if invocation.status is InvocationStatus.succeeded:
            diagnostic_cases = tuple(
                case for case in contract.cases if case.role.value == "diagnostic"
            )
            for case in (*contract.required_cases, *diagnostic_cases):
                case_remaining = (
                    None if remaining is None else remaining - (time.monotonic() - attempt_started)
                )
                if case_remaining is not None and case_remaining <= 0:
                    wall_expired = True
                    break
                try:
                    if case_remaining is None:
                        process_exit, raw = await verifier(case, staged.snapshot_path)
                    else:
                        verifier_task = asyncio.create_task(verifier(case, staged.snapshot_path))
                        try:
                            done, _ = await asyncio.wait(
                                (verifier_task,),
                                timeout=case_remaining,
                            )
                        except BaseException:
                            verifier_task.cancel()
                            await asyncio.gather(verifier_task, return_exceptions=True)
                            raise
                        if not done:
                            verifier_task.cancel()
                            await asyncio.gather(verifier_task, return_exceptions=True)
                            wall_expired = True
                            break
                        process_exit, raw = verifier_task.result()
                except asyncio.CancelledError:
                    _discard_unpublished_stage(
                        store,
                        attempt_index=next_attempt,
                        staged=staged,
                    )
                    raise
                except AgentCLIError:
                    _discard_unpublished_stage(
                        store,
                        attempt_index=next_attempt,
                        staged=staged,
                    )
                    raise
                except Exception as error:  # noqa: BLE001 - injected verifier boundary
                    if verifier_failure is None:
                        verifier_failure = (
                            f"case {case.case_id} verifier raised {type(error).__name__}"
                        )
                    continue
                except BaseException:
                    _discard_unpublished_stage(
                        store,
                        attempt_index=next_attempt,
                        staged=staged,
                    )
                    raise
                try:
                    if isinstance(process_exit, bool) or not isinstance(process_exit, int):
                        raise TypeError("verifier process exit must be an integer")
                    if not isinstance(raw, bytes):
                        raise TypeError("verifier payload must be bytes")
                    raw_payloads[case.case_id] = raw
                    if isinstance(case.acceptance, TestsAcceptance):
                        validated = validate_tests_payload(
                            raw,
                            case_id=case.case_id,
                            role=case.role.value,
                            process_exit=process_exit,
                            required_tests=case.acceptance.required_tests,
                            candidate_sha256=candidate_sha256,
                            contract_sha256=contract_sha256,
                        )
                    elif isinstance(case.acceptance, TransitionAcceptance):
                        validated = validate_transition_payload(
                            raw,
                            case_id=case.case_id,
                            role=case.role,
                            process_exit=process_exit,
                            expected_schema_version=expected_version(case.case_id),
                            expected_model=case.verify.model.path,
                            expected_post=case.verify.post,
                            candidate_sha256=candidate_sha256,
                            contract_sha256=contract_sha256,
                            evidence_candidate_sha256=candidate_sha256,
                            evidence_contract_sha256=contract_sha256,
                        )
                        if case.acceptance.walk is not None and validated.payload_exit == 0:
                            from gnd.transition import read_steps_document

                            steps_document = read_steps_document(
                                staged.snapshot_path / case.verify.steps
                            )
                            submitted_steps = steps_document["steps"]
                            if [step["op"] for step in submitted_steps] != [
                                step.operation_id for step in validated.transition_steps
                            ]:
                                raise VerifierPayloadError(
                                    ["submitted step operations differ from report order"]
                                )
                            validated = attach_walk_floor_steps(validated, submitted_steps)
                    else:
                        validated = validate_verifier_payload(
                            raw,
                            case_id=case.case_id,
                            role=case.role,
                            process_exit=process_exit,
                            expected_command=case.verify.command,
                            expected_model=case.verify.model.path,
                            expected_subject=case.verify.subject,
                            candidate_sha256=candidate_sha256,
                            contract_sha256=contract_sha256,
                            evidence_candidate_sha256=candidate_sha256,
                            evidence_contract_sha256=contract_sha256,
                            require_extraction=case.verify.command == "verify",
                            expected_outputs=observe_expected_outputs(case, candidate_files),
                            expected_schema_version=expected_version(case.case_id),
                        )
                    results.append(validated)
                    from gnd.assurance_transport import bind_verified_execution

                    bind_verified_execution(raw, results[-1])
                except VerifierPayloadError as error:
                    if verifier_failure is None:
                        verifier_failure = f"case {case.case_id}: {'; '.join(error.issues)}"
                except Exception as error:  # noqa: BLE001 - untrusted verifier boundary
                    raw_payloads.pop(case.case_id, None)
                    if verifier_failure is None:
                        verifier_failure = (
                            f"case {case.case_id} returned invalid {type(error).__name__}"
                        )

        attempt_elapsed = time.monotonic() - attempt_started
        if not math.isfinite(attempt_elapsed) or attempt_elapsed < 0:
            _discard_unpublished_stage(
                store,
                attempt_index=next_attempt,
                staged=staged,
            )
            raise ValueError("attempt elapsed time is negative or non-finite")
        accounted_wall_seconds += attempt_elapsed

        attempt_bound_hit = next_attempt >= contract.max_attempts
        wall_bound_hit = wall_expired or (
            contract.wall_seconds is not None and accounted_wall_seconds >= contract.wall_seconds
        )
        published = _publish_current_attempt(
            store=store,
            staged=staged,
            candidate_path=candidate_path,
            contract=contract,
            contract_sha256=contract_sha256,
            invocation=invocation,
            raw_payloads=raw_payloads,
            results=results,
            verifier_failure=verifier_failure,
            wall_expired=wall_expired,
            wall_bound_hit=wall_bound_hit,
            attempt_bound_hit=attempt_bound_hit,
            seen=seen,
            attempt_index=next_attempt,
            attempt_elapsed=attempt_elapsed,
            feedback_schema_version=feedback_schema_version,
            redaction=redaction,
        )
        record = published.record
        evaluation = published.evaluation
        feedback_bytes = published.feedback_bytes
        feedback_sha256 = published.feedback_sha256
        pair = published.pair
        decision = published.decision
        eligible = published.eligible
        records.append(record)

        if eligible and (
            best_record is None
            or best_key(contract, evaluation) < best_key(contract, best_record.evaluation)
        ):
            best_record = record
            store.publish_best(record)
            best_identity = store.read_resume_state(
                contract, expected_payload_versions=payload_versions
            ).best_attempt_identity
            if best_identity is None:
                raise ValueError("best pointer publication did not retain an identity")

        if decision.value != "retry":
            return publish_terminal(decision.value, decision.reason, record)
        seen[pair] = next_attempt
        next_attempt += 1

    if not records:  # pragma: no cover - positive max_attempts makes this unreachable
        raise RuntimeError("session ended without an attempt")
    return publish_terminal(
        "budget-exhausted",
        "session attempt budget exhausted without required-case acceptance",
        records[-1],
    )
