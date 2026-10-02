

from __future__ import annotations

import asyncio
import hashlib
import json
from pathlib import Path
from typing import Any

import pytest

import gnd.exp.session as session_module
from gnd.agent_cli import AgentAdapterId, InvocationResult, InvocationStatus, build_agent_argv
from gnd.exp.session import run_session
from gnd.exp.session_contract import DataDrivenContract
from gnd.exp.session_eval import (
    AttemptEvaluation,
    CaseEvaluation,
    ExpectedOutputObservation,
    contract_accepts,
    normalized_verifier_signature,
)
from gnd.report import PAYLOAD_SCHEMA_VERSION

CONTRACT_SHA = "c" * 64


def _case(
    *, candidate: str, accepted: bool, bound_candidate: str | None = None
) -> CaseEvaluation:
    exit_code = 0 if accepted else 4
    return CaseEvaluation(
        payload_valid=True,
        case_id="required-a",
        role="required",
        candidate_sha256=bound_candidate or candidate,
        contract_sha256=CONTRACT_SHA,
        raw_payload_sha256=("a" if accepted else "b") * 64,
        process_exit=exit_code,
        payload_exit=exit_code,
        outcome="accepted" if accepted else "indeterminate",
        acceptance_ready=accepted,
        counts={
            "pass": int(accepted),
            "fail": 0,
            "warning": 0,
            "unchecked": int(not accepted),
            "vacuous": 0,
        },
        coverage={"fact": {"declared": "declared", "facts": 1}},
        issues=(),
        expected_outputs=(
            ExpectedOutputObservation(
                output_id="required-a-out",
                expected_sha256="1" * 64,
                observed_sha256="1" * 64 if accepted else None,
                state="matched" if accepted else "absent",
            ),
        ),
        alethic_failure_count=0,
        alethic_indeterminate_count=int(not accepted),
    )


def _attempt(index: int, candidate: str, case: CaseEvaluation) -> AttemptEvaluation:
    return AttemptEvaluation(
        attempt_index=index,
        candidate_sha256=candidate,
        contract_sha256=CONTRACT_SHA,
        results=(case,),
    )


def _pair(attempt: AttemptEvaluation) -> tuple[str, str]:
    return attempt.candidate_sha256, normalized_verifier_signature(_contract(), attempt)


def test_recurrence_requires_exact_candidate_and_normalized_signature_pair() -> None:
    first = _attempt(1, "a" * 64, _case(candidate="a" * 64, accepted=False))
    same_candidate_new_signature = _attempt(
        2, "a" * 64, _case(candidate="a" * 64, accepted=True)
    )
    same_signature_new_candidate = _attempt(
        3, "b" * 64, _case(candidate="b" * 64, accepted=False)
    )
    exact_repeat = _attempt(4, "a" * 64, _case(candidate="a" * 64, accepted=False))

    assert _pair(first) != _pair(same_candidate_new_signature)
    assert _pair(first) != _pair(same_signature_new_candidate)
    assert _pair(first) == _pair(exact_repeat)


def test_normalized_signature_excludes_raw_digest_prose_path_and_order_noise() -> None:
    candidate = "a" * 64
    first_case = _case(candidate=candidate, accepted=False).model_copy(
        update={
            "raw_payload_sha256": "1" * 64,
            "issues": (
                {
                    "path": "/private/first",
                    "message": "provider prose one",
                    "rule_id": "rule:a",
                    "severity": "error",
                },
                {
                    "path": "/private/second",
                    "message": "provider prose two",
                    "rule_id": "rule:b",
                    "severity": "error",
                },
            ),
            "issues_total": 2,
        }
    )
    second_case = first_case.model_copy(
        update={
            "raw_payload_sha256": "2" * 64,
            "coverage": {"fact": {"facts": 1, "declared": "declared"}},
            "issues": tuple(reversed(first_case.issues)),
        }
    )

    contract = _contract()
    assert normalized_verifier_signature(contract, _attempt(1, candidate, first_case)) == (
        normalized_verifier_signature(contract, _attempt(9, candidate, second_case))
    )


def test_acceptance_precedes_an_otherwise_repeated_semantic_pair() -> None:
    contract = _contract(max_attempts=2)
    candidate = "a" * 64
    stale = _attempt(
        1,
        candidate,
        _case(candidate=candidate, accepted=True, bound_candidate="f" * 64),
    )
    current = _attempt(2, candidate, _case(candidate=candidate, accepted=True))

    assert normalized_verifier_signature(contract, stale) == normalized_verifier_signature(
        contract, current
    )
    assert contract_accepts(contract, stale) is False
    assert contract_accepts(contract, current) is True
    assert _pair(stale) == _pair(current)
                                                                                        
    outcome = "accepted" if contract_accepts(contract, current) else "recurrence"
    assert outcome == "accepted"


def _contract(
    *,
    max_attempts: int = 5,
    wall_seconds: float = 30.0,
    diagnostic: bool = False,
    required_output_sha256: str = "1" * 64,
) -> DataDrivenContract:
    bound = {
        "path": "input.json",
        "media_type": "application/json",
        "encoding": "utf-8",
        "sha256": "1" * 64,
        "size_bytes": 1,
    }
    cases = [
        {
            "case_id": "required-a",
            "role": "required",
            "inputs": [bound],
            "expected_outputs": [
                {
                    **bound,
                    "path": "expected.json",
                    "sha256": required_output_sha256,
                    "output_id": "required-a-out",
                    "candidate_path": "produced.json",
                    "comparison": "exact-bytes",
                }
            ],
            "verify": {
                "command": "check",
                "model": {
                    **bound,
                    "path": "model.orm.yaml",
                    "sha256": "2" * 64,
                },
                "subject": "candidate.json",
            },
        }
    ]
    if diagnostic:
        cases.append(
            {
                "case_id": "diagnostic-a",
                "role": "diagnostic",
                "inputs": [bound],
                "expected_outputs": [
                    {
                        **bound,
                        "path": "diagnostic.json",
                        "output_id": "diagnostic-a-out",
                        "candidate_path": "diagnostic-produced.json",
                        "comparison": "exact-bytes",
                    }
                ],
                "verify": {
                    "command": "check",
                    "model": {
                        **bound,
                        "path": "model.orm.yaml",
                        "sha256": "2" * 64,
                    },
                    "subject": "candidate.json",
                },
            }
        )
    return DataDrivenContract.model_validate(
        {
            "schema_version": 1,
            "experiment_id": "EXP-session-a-b-a-oscillation",
            "max_attempts": max_attempts,
            "wall_seconds": wall_seconds,
            "cases": cases,
        }
    )


def _raw_payload(*, accepted: bool) -> bytes:
    verdict = {
        "constraint_ref": "constraints[0]",
        "constraint_type": "mandatory",
        "modality": "alethic",
        "source": "explicit",
        "status": "confirmed",
        "verdict": "pass" if accepted else "unchecked",
        "message": "ignored prose",
        "offending_facts": [],
        "reason_code": None if accepted else "unsupported",
    }
    exit_code = 0 if accepted else 4
    payload: dict[str, Any] = {
        "schema_version": PAYLOAD_SCHEMA_VERSION,
        "tool": "gnd",
        "command": "check",
        "outcome": "accepted" if accepted else "indeterminate",
        "exit_code": exit_code,
        "acceptance_ready": accepted,
        "model": "model.orm.yaml",
        "population": "candidate.json",
        "counts": {
            "pass": int(accepted),
            "fail": 0,
            "warning": 0,
            "unchecked": int(not accepted),
            "vacuous": 0,
        },
        "verdicts": [verdict],
        "coverage": {"fixture": {"declared": "declared", "facts": 1}},
        "extraction": {},
        "issues": [],
        "issues_total": 0,
        "issues_truncated": False,
        "warnings": [],
        "error": None,
                                                                            
                                                                            
                                              
        "transition": None,
    }
    return (
        json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"
    ).encode()


def _internal_error_payload() -> bytes:
    payload = json.loads(_raw_payload(accepted=False))
    payload.update(
        {
            "outcome": "internal_error",
            "exit_code": 70,
            "counts": {
                "pass": 0,
                "fail": 0,
                "warning": 0,
                "unchecked": 0,
                "vacuous": 0,
            },
            "verdicts": [],
            "coverage": {},
            "error": {"type": "RuntimeError", "message": "verifier failed"},
        }
    )
    return (
        json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"
    ).encode()


def _invocation(
    index: int,
    *,
    prompt: str,
    feedback_sha256: str | None,
) -> InvocationResult:
    effective_prompt = prompt
    if feedback_sha256 is not None:
        effective_prompt = (
            f"{prompt}\n\nCurrent attempt feedback SHA-256: {feedback_sha256}\n"
            "Canonical current-attempt feedback is supplied byte-for-byte on stdin."
        )
    effective_sha256 = hashlib.sha256(effective_prompt.encode("utf-8")).hexdigest()
    return InvocationResult(
        adapter=AgentAdapterId.codex,
        status=InvocationStatus.succeeded,
        executable="/usr/bin/codex",
        version="fixture",
        argv=(
            *build_agent_argv(AgentAdapterId.codex, effective_prompt)[:-1],
            f"<prompt:sha256={effective_sha256}>",
        ),
        cwd="candidate",
        termination="exited",
        exit_code=0,
        started_monotonic=float(index),
        ended_monotonic=float(index) + 0.1,
        stdout_observed_bytes=0,
        stdout_retained_bytes=0,
        stdout_truncated=False,
        stderr_observed_bytes=0,
        stderr_retained_bytes=0,
        stderr_truncated=False,
        environment=(),
        prompt_sha256=hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
        feedback_sha256=feedback_sha256,
        stdout=b"",
        stderr=b"",
    )


def test_session_a_b_a_oscillation_stops_before_a_fourth_invocation(tmp_path: Path) -> None:


    candidate = tmp_path / "candidate"
    candidate.mkdir()
    (candidate / "main.txt").write_text("initial", encoding="utf-8")
    invocations: list[int] = []
    versions = ("A", "B", "A", "SHOULD-NOT-RUN")

    async def invoker(*args, feedback_bytes=None, feedback_sha256=None, **kwargs):
        index = len(invocations) + 1
        invocations.append(index)
        if index > 1:
            assert feedback_bytes is not None
            assert hashlib.sha256(feedback_bytes).hexdigest() == feedback_sha256
        (candidate / "main.txt").write_text(versions[index - 1], encoding="utf-8")
        return _invocation(
            index,
            prompt=kwargs["prompt"],
            feedback_sha256=feedback_sha256,
        )

    async def verifier(case, snapshot: Path) -> tuple[int, bytes]:
        assert snapshot.joinpath("main.txt").read_text(encoding="utf-8") in {"A", "B"}
        return 4, _raw_payload(accepted=False)

    result = asyncio.run(
        run_session(
            _contract(),
            contract_sha256=CONTRACT_SHA,
            adapter_id=AgentAdapterId.codex,
            prompt="trusted initial instructions",
            candidate_root=candidate,
            run_root=tmp_path / "run",
            verifier=verifier,
            invoker=invoker,
        )
    )

    assert invocations == [1, 2, 3]
    assert result.disposition == "oscillation"
    assert result.attempt_count == 3


def test_diagnostic_verifier_failure_cannot_veto_required_acceptance(
    tmp_path: Path,
) -> None:
    candidate = tmp_path / "candidate"
    candidate.mkdir()
    (candidate / "main.txt").write_text("accepted", encoding="utf-8")
    produced = b'{"case":"required-a"}\n'
    (candidate / "produced.json").write_bytes(produced)

    async def invoker(*args, **kwargs):
        return _invocation(
            1,
            prompt=kwargs["prompt"],
            feedback_sha256=kwargs["feedback_sha256"],
        )

    async def verifier(case, snapshot: Path) -> tuple[int, bytes]:
        if case.case_id == "diagnostic-a":
            raise RuntimeError("diagnostic unavailable")
        return 0, _raw_payload(accepted=True)

    run = tmp_path / "run"
    result = asyncio.run(
        run_session(
            _contract(
                max_attempts=1,
                diagnostic=True,
                required_output_sha256=hashlib.sha256(produced).hexdigest(),
            ),
            contract_sha256=CONTRACT_SHA,
            adapter_id=AgentAdapterId.codex,
            prompt="trusted initial instructions",
            candidate_root=candidate,
            run_root=run,
            verifier=verifier,
            invoker=invoker,
        )
    )

    assert result.disposition == "accepted"
    assert result.best_attempt == 1
    assert (run / "best.json").is_file()
    feedback = json.loads((run / "attempts" / "0001" / "feedback.json").read_bytes())
    assert feedback["disposition"] == "accepted"
    assert feedback["diagnostic"] == []


def test_verifier_work_is_cancelled_at_the_monotonic_wall_bound(tmp_path: Path) -> None:
    candidate = tmp_path / "candidate"
    candidate.mkdir()
    (candidate / "main.txt").write_text("pending", encoding="utf-8")
    cancelled = False

    async def invoker(*args, **kwargs):
        return _invocation(
            1,
            prompt=kwargs["prompt"],
            feedback_sha256=kwargs["feedback_sha256"],
        )

    async def verifier(case, snapshot: Path) -> tuple[int, bytes]:
        nonlocal cancelled
        try:
            await asyncio.sleep(10)
        except asyncio.CancelledError:
            cancelled = True
            raise
        return 0, _raw_payload(accepted=True)

    run = tmp_path / "run"
    result = asyncio.run(
        run_session(
            _contract(max_attempts=3, wall_seconds=0.2),
            contract_sha256=CONTRACT_SHA,
            adapter_id=AgentAdapterId.codex,
            prompt="trusted initial instructions",
            candidate_root=candidate,
            run_root=run,
            verifier=verifier,
            invoker=invoker,
        )
    )

    assert cancelled is True
    assert result.disposition == "budget-exhausted"
    assert result.attempt_count == 1
    feedback = json.loads((run / "attempts" / "0001" / "feedback.json").read_bytes())
    assert feedback["disposition"] == "budget-exhausted"


def test_internal_error_exit_70_is_a_terminal_verifier_failure_not_best(
    tmp_path: Path,
) -> None:
    candidate = tmp_path / "candidate"
    candidate.mkdir()
    (candidate / "main.txt").write_text("broken verifier", encoding="utf-8")
    invocations = 0

    async def invoker(*args, **kwargs):
        nonlocal invocations
        invocations += 1
        return _invocation(
            invocations,
            prompt=kwargs["prompt"],
            feedback_sha256=kwargs["feedback_sha256"],
        )

    async def verifier(case, snapshot: Path) -> tuple[int, bytes]:
        return 70, _internal_error_payload()

    run = tmp_path / "run"
    result = asyncio.run(
        run_session(
            _contract(max_attempts=3),
            contract_sha256=CONTRACT_SHA,
            adapter_id=AgentAdapterId.codex,
            prompt="trusted initial instructions",
            candidate_root=candidate,
            run_root=run,
            verifier=verifier,
            invoker=invoker,
        )
    )

    assert invocations == 1
    assert result.disposition == "verifier-failure"
    assert result.best_attempt is None
    assert not (run / "best.json").exists()


def test_custom_invoker_is_cancelled_at_the_monotonic_wall_bound(tmp_path: Path) -> None:
    candidate = tmp_path / "candidate"
    candidate.mkdir()
    cancelled = False

    async def invoker(*args, **kwargs):
        nonlocal cancelled
        try:
            await asyncio.sleep(10)
        except asyncio.CancelledError:
            cancelled = True
            raise
        return _invocation(
            1,
            prompt=kwargs["prompt"],
            feedback_sha256=kwargs["feedback_sha256"],
        )

    async def verifier(case, snapshot: Path) -> tuple[int, bytes]:
        raise AssertionError("verifier must not run after invoker wall exhaustion")

    with pytest.raises(RuntimeError, match="invoker exceeded"):
        asyncio.run(
            run_session(
                _contract(max_attempts=3, wall_seconds=0.05),
                contract_sha256=CONTRACT_SHA,
                adapter_id=AgentAdapterId.codex,
                prompt="trusted initial instructions",
                candidate_root=candidate,
                run_root=tmp_path / "run",
                verifier=verifier,
                invoker=invoker,
            )
        )
    assert cancelled is True


def test_crash_after_terminal_attempt_replays_without_an_extra_invocation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    candidate = tmp_path / "candidate"
    candidate.mkdir()
    (candidate / "main.txt").write_text("not accepted", encoding="utf-8")
    invocations = 0

    async def invoker(*args, **kwargs):
        nonlocal invocations
        invocations += 1
        return _invocation(
            invocations,
            prompt=kwargs["prompt"],
            feedback_sha256=kwargs["feedback_sha256"],
        )

    async def verifier(case, snapshot: Path) -> tuple[int, bytes]:
        return 4, _raw_payload(accepted=False)

    run = tmp_path / "run"
    original_publish_result = session_module.SessionStore.publish_result

    def crash_before_result(self, result):
        raise RuntimeError("injected crash before result publication")

    monkeypatch.setattr(session_module.SessionStore, "publish_result", crash_before_result)
    with pytest.raises(RuntimeError, match="injected crash"):
        asyncio.run(
            run_session(
                _contract(max_attempts=1),
                contract_sha256=CONTRACT_SHA,
                adapter_id=AgentAdapterId.codex,
                prompt="trusted initial instructions",
                candidate_root=candidate,
                run_root=run,
                verifier=verifier,
                invoker=invoker,
            )
        )
    monkeypatch.setattr(
        session_module.SessionStore,
        "publish_result",
        original_publish_result,
    )

    result = asyncio.run(
        run_session(
            _contract(max_attempts=1),
            contract_sha256=CONTRACT_SHA,
            adapter_id=AgentAdapterId.codex,
            prompt="trusted initial instructions",
            candidate_root=candidate,
            run_root=run,
            verifier=verifier,
            invoker=invoker,
        )
    )

    assert invocations == 1
    assert result.disposition == "budget-exhausted"
    assert (run / "result.json").is_file()


def test_resume_refuses_a_new_contract_digest_before_invocation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    candidate = tmp_path / "candidate"
    candidate.mkdir()
    (candidate / "main.txt").write_text("not accepted", encoding="utf-8")

    async def invoker(*args, **kwargs):
        return _invocation(
            1,
            prompt=kwargs["prompt"],
            feedback_sha256=kwargs["feedback_sha256"],
        )

    async def verifier(case, snapshot: Path) -> tuple[int, bytes]:
        return 4, _raw_payload(accepted=False)

    run = tmp_path / "run"

    def crash_before_result(self, result):
        raise RuntimeError("injected crash before result publication")

    monkeypatch.setattr(session_module.SessionStore, "publish_result", crash_before_result)
    with pytest.raises(RuntimeError, match="injected crash"):
        asyncio.run(
            run_session(
                _contract(max_attempts=1),
                contract_sha256=CONTRACT_SHA,
                adapter_id=AgentAdapterId.codex,
                prompt="trusted initial instructions",
                candidate_root=candidate,
                run_root=run,
                verifier=verifier,
                invoker=invoker,
            )
        )

    with pytest.raises(ValueError, match="different session contract digest"):
        asyncio.run(
            run_session(
                _contract(max_attempts=1),
                contract_sha256="d" * 64,
                adapter_id=AgentAdapterId.codex,
                prompt="trusted initial instructions",
                candidate_root=candidate,
                run_root=run,
                verifier=verifier,
                invoker=invoker,
            )
        )
