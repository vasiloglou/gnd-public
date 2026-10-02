

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

import gnd.exp.session_store as session_store_module
from gnd.agent_cli import AgentAdapterId, InvocationResult, InvocationStatus
from gnd.exp.session_contract import DataDrivenContract
from gnd.exp.session_eval import (
    LEGACY_FEEDBACK_SCHEMA_VERSION,
    AttemptEvaluation,
    AttemptFeedback,
    ExpectedOutputObservation,
    best_key,
    build_attempt_feedback,
    canonical_feedback,
    contract_accepts,
    validate_verifier_payload,
)
from gnd.exp.session_store import SessionResult, SessionStore
from gnd.report import PAYLOAD_SCHEMA_VERSION

CONTRACT_SHA = "c" * 64


def _contract() -> DataDrivenContract:
    bound = {
        "path": "input.json",
        "media_type": "application/json",
        "encoding": "utf-8",
        "sha256": "1" * 64,
        "size_bytes": 1,
    }
    return DataDrivenContract.model_validate(
        {
            "schema_version": 1,
            "experiment_id": "EXP-feedback",
            "max_attempts": 3,
            "wall_seconds": 30.0,
            "cases": [
                {
                    "case_id": "required-a",
                    "role": "required",
                    "inputs": [bound],
                    "expected_outputs": [
                        {
                            **bound,
                            "path": "expected.json",
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
            ],
        }
    )


def _raw_verifier_payload(*, accepted: bool, facts: int = 1) -> bytes:
    exit_code = 0 if accepted else 4
    verdict = {
        "constraint_ref": "constraints[0]",
        "constraint_type": "mandatory",
        "modality": "alethic",
        "source": "explicit",
        "status": "confirmed",
        "verdict": "pass" if accepted else "unchecked",
        "message": "fixture accepted" if accepted else "fixture unchecked",
        "offending_facts": [],
        "reason_code": None if accepted else "unsupported",
    }
    document = {
        
        
        
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
        "coverage": {"fact": {"declared": "declared", "facts": facts}},
        "extraction": {},
        "issues": [],
        "issues_total": 0,
        "issues_truncated": False,
        "warnings": [],
        "error": None,
        
        
        
        "transition": None,
    }
    return (json.dumps(document, sort_keys=True, separators=(",", ":")) + "\n").encode()


def _evaluation(index: int, candidate_sha: str, *, accepted: bool = False) -> AttemptEvaluation:
    raw = _raw_verifier_payload(accepted=accepted)
    case = validate_verifier_payload(
        raw,
        case_id="required-a",
        role="required",
        process_exit=0 if accepted else 4,
        expected_command="check",
        expected_model="model.orm.yaml",
        expected_subject="candidate.json",
        candidate_sha256=candidate_sha,
        contract_sha256=CONTRACT_SHA,
        evidence_candidate_sha256=candidate_sha,
        evidence_contract_sha256=CONTRACT_SHA,
        expected_outputs=(
            ExpectedOutputObservation(
                output_id="required-a-out",
                expected_sha256="1" * 64,
                observed_sha256="1" * 64 if accepted else None,
                state="matched" if accepted else "absent",
            ),
        ),
    )
    return AttemptEvaluation(
        attempt_index=index,
        candidate_sha256=candidate_sha,
        contract_sha256=CONTRACT_SHA,
        results=(case,),
    )


def _invocation(index: int) -> InvocationResult:
    prompt_sha256 = hashlib.sha256(b"fixture-controller-prompt").hexdigest()
    return InvocationResult(
        adapter=AgentAdapterId.codex,
        status=InvocationStatus.succeeded,
        executable="/usr/bin/codex",
        version="fixture",
        argv=("codex", "exec", f"<prompt:sha256={prompt_sha256}>"),
        cwd="candidate",
        termination="exited",
        exit_code=0,
        started_monotonic=float(index),
        ended_monotonic=float(index) + 0.25,
        stdout_observed_bytes=0,
        stdout_retained_bytes=0,
        stdout_truncated=False,
        stderr_observed_bytes=0,
        stderr_retained_bytes=0,
        stderr_truncated=False,
        environment=(),
        prompt_sha256=prompt_sha256,
        stdout=b"",
        stderr=b"",
    )


def _reserve_launch(
    store: SessionStore,
    candidate: Path,
    index: int,
    invocation: InvocationResult,
) -> None:
    assert invocation.prompt_sha256 is not None
    effective_prompt_sha256 = invocation.argv[-1].removeprefix("<prompt:sha256=").removesuffix(
        ">"
    )
    store.publish_launch_intent(
        attempt_index=index,
        contract_sha256=CONTRACT_SHA,
        policy_sha256="a" * 64,
        adapter=invocation.adapter,
        base_prompt_sha256=invocation.prompt_sha256,
        controller_prompt_sha256=invocation.prompt_sha256,
        effective_prompt_sha256=effective_prompt_sha256,
        feedback_sha256=invocation.feedback_sha256,
        candidate_root=candidate,
    )


def _publish_attempt(
    store: SessionStore,
    candidate: Path,
    index: int,
    *,
    accepted: bool = False,
    feedback_schema_version: int = 2,
    candidate_state: str | None = None,
):
    (candidate / "state.txt").write_text(
        candidate_state if candidate_state is not None else f"attempt-{index}\n",
        encoding="utf-8",
    )
    invocation = _invocation(index)
    _reserve_launch(store, candidate, index, invocation)
    staged = store.stage_candidate(attempt_index=index, candidate_root=candidate)
    evaluation = _evaluation(index, staged.inventory.tree_sha256, accepted=accepted)
    feedback = build_attempt_feedback(
        run_id=store.run_id,
        contract=_contract(),
        contract_sha256=CONTRACT_SHA,
        invocation=invocation,
        evaluation=evaluation,
        disposition="accepted" if accepted else "retry",
        schema_version=feedback_schema_version,
    )
    feedback_evidence = store.publish_feedback(
        attempt_index=index,
        feedback=feedback,
        staged_candidate=staged,
    )
    record = store.publish_attempt(
        attempt_index=index,
        candidate_root=candidate,
        invocation=invocation,
        verifier_payloads={"required-a": _raw_verifier_payload(accepted=accepted)},
        evaluation=evaluation,
        contract=_contract(),
        best_eligible=True,
        staged_candidate=staged,
    )
    return feedback, feedback_evidence, record


def _constraint_contract(*, minimum: int = 1) -> DataDrivenContract:
    bound = {
        "path": "input.json",
        "media_type": "application/json",
        "encoding": "utf-8",
        "sha256": "1" * 64,
        "size_bytes": 1,
    }
    return DataDrivenContract.model_validate(
        {
            "schema_version": 2,
            "experiment_id": "EXP-feedback-constraint",
            "max_attempts": 3,
            "wall_seconds": 30.0,
            "cases": [
                {
                    "case_id": "required-a",
                    "role": "required",
                    "inputs": [bound],
                    "acceptance": {
                        "mode": "constraint-satisfaction",
                        "coverage": [{"fact_type": "fact", "min_facts": minimum}],
                    },
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
            ],
        }
    )


def _publish_constraint_attempt(
    store: SessionStore,
    candidate: Path,
    index: int,
    *,
    contract: DataDrivenContract,
    accepted: bool,
    facts: int = 1,
):
    (candidate / "state.txt").write_text(f"attempt-{index}\n", encoding="utf-8")
    invocation = _invocation(index)
    _reserve_launch(store, candidate, index, invocation)
    staged = store.stage_candidate(attempt_index=index, candidate_root=candidate)
    raw = _raw_verifier_payload(accepted=accepted, facts=facts)
    result = validate_verifier_payload(
        raw,
        case_id="required-a",
        role="required",
        process_exit=0 if accepted else 4,
        expected_command="check",
        expected_model="model.orm.yaml",
        expected_subject="candidate.json",
        candidate_sha256=staged.inventory.tree_sha256,
        contract_sha256=CONTRACT_SHA,
        evidence_candidate_sha256=staged.inventory.tree_sha256,
        evidence_contract_sha256=CONTRACT_SHA,
        expected_outputs=(),
    )
    evaluation = AttemptEvaluation(
        attempt_index=index,
        candidate_sha256=staged.inventory.tree_sha256,
        contract_sha256=CONTRACT_SHA,
        results=(result,),
    )
    feedback = build_attempt_feedback(
        run_id=store.run_id,
        contract=contract,
        contract_sha256=CONTRACT_SHA,
        invocation=invocation,
        evaluation=evaluation,
        disposition="accepted" if contract_accepts(contract, evaluation) else "retry",
    )
    store.publish_feedback(
        attempt_index=index,
        feedback=feedback,
        staged_candidate=staged,
    )
    return store.publish_attempt(
        attempt_index=index,
        candidate_root=candidate,
        invocation=invocation,
        verifier_payloads={"required-a": raw},
        evaluation=evaluation,
        contract=contract,
        best_eligible=True,
        staged_candidate=staged,
    )


def test_new_attempt_and_result_leaves_are_v2_while_fixed_leaves_remain_v1(
    tmp_path: Path,
) -> None:
    run = tmp_path / "run-v2-leaves"
    store = SessionStore(run, run_id="run-1", contract_id=_contract().experiment_id)
    candidate = tmp_path / "candidate-v2-leaves"
    candidate.mkdir()

    feedback, _, record = _publish_attempt(store, candidate, 1, accepted=True)
    attempt_document = json.loads(
        (run / "attempts" / "0001" / "attempt.json").read_bytes()
    )
    launch_document = json.loads((run / "launches" / "0001.json").read_bytes())
    result = SessionResult(
        run_id="run-1",
        disposition="accepted",
        terminal_reason="contract accepted",
        attempt_count=1,
        best_attempt=1,
        best_attempt_manifest_sha256="a" * 64,
        best_candidate_sha256=record.candidate_inventory.tree_sha256,
        referenced_evidence_digests={"attempt_manifest_sha256": "a" * 64},
        acceptance_modes=("exact-bytes",),
    )

    assert feedback.schema_version == record.schema_version == result.schema_version == 2
    assert attempt_document["feedback_schema_version"] == 2
    assert record.candidate_inventory.schema_version == 1
    assert launch_document["schema_version"] == 1


def test_attempt_and_result_dispatch_reject_cross_version_shapes(tmp_path: Path) -> None:
    store = SessionStore(
        tmp_path / "run-cross-version",
        run_id="run-1",
        contract_id=_contract().experiment_id,
    )
    candidate = tmp_path / "candidate-cross-version"
    candidate.mkdir()
    _, _, record = _publish_attempt(store, candidate, 1)
    attempt_document = record.model_dump(mode="json")

    with pytest.raises(ValidationError):
        session_store_module.AttemptRecord.model_validate(
            {**attempt_document, "schema_version": 1}
        )
    without_v2_binding = dict(attempt_document)
    without_v2_binding.pop("feedback_schema_version")
    with pytest.raises(ValidationError):
        session_store_module.AttemptRecord.model_validate(without_v2_binding)

    result = SessionResult(
        run_id="run-1",
        disposition="budget-exhausted",
        terminal_reason="attempt bound reached",
        attempt_count=1,
        referenced_evidence_digests={},
        acceptance_modes=("exact-bytes",),
    )
    result_document = result.model_dump(mode="json")
    with pytest.raises(ValidationError):
        SessionResult.model_validate({**result_document, "schema_version": 1})
    without_modes = dict(result_document)
    without_modes.pop("acceptance_modes")
    with pytest.raises(ValidationError):
        SessionResult.model_validate(without_modes)


def test_schema_v2_session_result_rejects_empty_acceptance_modes() -> None:
    with pytest.raises(ValidationError, match="acceptance modes must be nonempty"):
        SessionResult(
            run_id="run-1",
            disposition="budget-exhausted",
            terminal_reason="attempt bound reached",
            attempt_count=1,
            referenced_evidence_digests={},
            acceptance_modes=(),
        )


def test_schema_v4_result_admits_snapshot_only_acceptance() -> None:
    result = SessionResult.model_validate(
        {
            "schema_version": 4,
            "run_id": "run-1",
            "disposition": "budget-exhausted",
            "terminal_reason": "attempt bound reached",
            "attempt_count": 1,
            "referenced_evidence_digests": {},
            "acceptance_modes": ["constraint-satisfaction"],
            "redaction": {
                "mode": "applied",
                "declarations": [
                    {
                        "case_id": "required-a",
                        "source": "role",
                        "fact_type": "optional_code",
                        "roles": ["code"],
                    }
                ],
            },
        }
    )

    assert result.schema_version == 4
    assert result.acceptance_modes == ("constraint-satisfaction",)


def test_publish_result_revalidates_model_copy_before_creating_terminal_leaf(
    tmp_path: Path,
) -> None:
    run = tmp_path / "run-invalid-result"
    store = SessionStore(run, run_id="run-1", contract_id=_contract().experiment_id)
    valid = SessionResult(
        run_id="run-1",
        disposition="budget-exhausted",
        terminal_reason="attempt bound reached",
        attempt_count=1,
        referenced_evidence_digests={},
        acceptance_modes=("exact-bytes",),
    )
    invalid = valid.model_copy(update={"acceptance_modes": ()})

    with pytest.raises(ValidationError, match="Tuple should have at least 1 item"):
        store.publish_result(invalid)

    assert not (run / "result.json").exists()


@pytest.mark.parametrize(
    "acceptance_modes",
    [
        ("constraint-satisfaction",),
        ("exact-bytes",),
        ("constraint-satisfaction", "exact-bytes"),
    ],
)
def test_every_schema_v2_session_result_acceptance_mode_round_trips(
    tmp_path: Path,
    acceptance_modes: tuple[str, ...],
) -> None:
    run = tmp_path / "run"
    store = SessionStore(run, run_id="run-1", contract_id=_contract().experiment_id)
    result = SessionResult(
        run_id="run-1",
        disposition="budget-exhausted",
        terminal_reason="attempt bound reached",
        attempt_count=1,
        referenced_evidence_digests={},
        acceptance_modes=acceptance_modes,
    )

    result_path = store.publish_result(result)

    assert SessionResult.model_validate(json.loads(result_path.read_bytes())) == result


def test_v1_contract_can_append_v1_and_v2_attempts_without_rewriting(
    tmp_path: Path,
) -> None:
    contract = _contract()
    store = SessionStore(
        tmp_path / "run-mixed-version",
        run_id="run-1",
        contract_id=contract.experiment_id,
    )
    candidate = tmp_path / "candidate-mixed-version"
    candidate.mkdir()
    _, _, first = _publish_attempt(
        store,
        candidate,
        1,
        feedback_schema_version=LEGACY_FEEDBACK_SCHEMA_VERSION,
    )
    store.publish_best(first)
    before = {
        path.relative_to(store.root).as_posix(): path.read_bytes()
        for path in store.root.rglob("*")
        if path.is_file() and path.name != "best.json"
    }

    _, _, second = _publish_attempt(store, candidate, 2, accepted=True)
    store.publish_best(second)
    state = store.read_resume_state(contract)

    assert first.schema_version == 1
    assert second.schema_version == 2
    assert state.next_attempt_index == 3
    assert all((store.root / path).read_bytes() == data for path, data in before.items())


@pytest.mark.parametrize(
    "scenario",
    ["exact", "constraint", "floor-deficient", "mixed-version", "recurrence"],
)
def test_live_best_selection_replays_identically_across_the_mode_matrix(
    tmp_path: Path,
    scenario: str,
) -> None:
    constraint_mode = scenario in {"constraint", "floor-deficient"}
    contract = (
        _constraint_contract(minimum=2 if scenario == "floor-deficient" else 1)
        if constraint_mode
        else _contract()
    )
    store = SessionStore(
        tmp_path / scenario / "run",
        run_id="run-1",
        contract_id=contract.experiment_id,
    )
    candidate = tmp_path / scenario / "candidate"
    candidate.mkdir(parents=True)

    if scenario == "constraint":
        records = (
            _publish_constraint_attempt(
                store, candidate, 1, contract=contract, accepted=False
            ),
            _publish_constraint_attempt(
                store, candidate, 2, contract=contract, accepted=True
            ),
        )
    elif scenario == "floor-deficient":
        records = (
            _publish_constraint_attempt(
                store, candidate, 1, contract=contract, accepted=True, facts=1
            ),
            _publish_constraint_attempt(
                store, candidate, 2, contract=contract, accepted=True, facts=2
            ),
        )
    elif scenario == "mixed-version":
        records = (
            _publish_attempt(
                store,
                candidate,
                1,
                feedback_schema_version=LEGACY_FEEDBACK_SCHEMA_VERSION,
            )[2],
            _publish_attempt(store, candidate, 2, accepted=True)[2],
        )
    elif scenario == "recurrence":
        records = (
            _publish_attempt(store, candidate, 1, candidate_state="same\n")[2],
            _publish_attempt(store, candidate, 2, candidate_state="same\n")[2],
        )
    else:
        records = (
            _publish_attempt(store, candidate, 1)[2],
            _publish_attempt(store, candidate, 2, accepted=True)[2],
        )

    live_best = min(records, key=lambda record: best_key(contract, record.evaluation))
    store.publish_best(live_best)
    before = {
        path.relative_to(store.root).as_posix(): path.read_bytes()
        for path in store.root.rglob("*")
        if path.is_file()
    }

    resumed = store.read_resume_state(contract)

    assert resumed.best_attempt_identity is not None
    assert resumed.best_attempt_identity.attempt_index == live_best.attempt_index
    assert resumed.best_attempt_identity.candidate_sha256 == (
        live_best.candidate_inventory.tree_sha256
    )
    if scenario == "recurrence":
        assert len(resumed.seen_recurrence_pairs) == 1
    assert {
        path.relative_to(store.root).as_posix(): path.read_bytes()
        for path in store.root.rglob("*")
        if path.is_file()
    } == before


def test_feedback_is_recursively_closed_current_attempt_only_and_canonical() -> None:
    contract = _contract()
    evaluation = _evaluation(1, "a" * 64)
    feedback = build_attempt_feedback(
        run_id="run-1",
        contract=contract,
        contract_sha256=CONTRACT_SHA,
        invocation=_invocation(1),
        evaluation=evaluation,
        disposition="retry",
    )
    encoded, digest = canonical_feedback(feedback)
    document = json.loads(encoded)

    assert set(document) == {
        "schema_version",
        "run_id",
        "contract_id",
        "contract_sha256",
        "source_attempt_index",
        "candidate_sha256",
        "case_payload_sha256s",
        "normalized_verifier_signature",
        "process_exit",
        "payload_exit",
        "acceptance_ready",
        "required",
        "diagnostic",
        "disposition",
    }
    rendered = encoded.decode("utf-8")
    for forbidden in (
        "prose must be removed",
        "/private/source",
        "stderr",
        "environment",
        "elapsed",
        "best_attempt",
        "prior_attempt",
        "cumulative",
    ):
        assert forbidden not in rendered
    assert digest == hashlib.sha256(encoded).hexdigest()
    assert encoded.endswith(b"\n")
    assert encoded == canonical_feedback(feedback)[0]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("prose", "repair this"),
        ("elapsed_seconds", 1.0),
        ("absolute_path", "/private/repo"),
        ("stderr", "secret"),
        ("environment", {"TOKEN": "secret"}),
        ("best_attempt", 1),
        ("cumulative_attempts", []),
        ("unknown", True),
    ],
)
def test_every_forbidden_feedback_addition_is_rejected(field: str, value: object) -> None:
    feedback = build_attempt_feedback(
        run_id="run-1",
        contract=_contract(),
        contract_sha256=CONTRACT_SHA,
        invocation=_invocation(1),
        evaluation=_evaluation(1, "a" * 64),
        disposition="retry",
    )
    document = feedback.model_dump(mode="json")
    document[field] = value

    with pytest.raises(ValidationError):
        AttemptFeedback.model_validate(document)


def test_every_allowed_feedback_mutation_changes_the_digest() -> None:
    feedback = build_attempt_feedback(
        run_id="run-1",
        contract=_contract(),
        contract_sha256=CONTRACT_SHA,
        invocation=_invocation(1),
        evaluation=_evaluation(1, "a" * 64),
        disposition="retry",
    )
    _, original = canonical_feedback(feedback)
    mutations = (
        feedback.model_copy(update={"run_id": "run-2"}),
        feedback.model_copy(update={"source_attempt_index": 2}),
        feedback.model_copy(update={"candidate_sha256": "f" * 64}),
        feedback.model_copy(update={"process_exit": 7}),
        feedback.model_copy(update={"disposition": "verifier-failure"}),
    )

    assert all(canonical_feedback(mutation)[1] != original for mutation in mutations)


def test_canonical_feedback_revalidates_model_copy_updates_recursively() -> None:
    feedback = build_attempt_feedback(
        run_id="run-1",
        contract=_contract(),
        contract_sha256=CONTRACT_SHA,
        invocation=_invocation(1),
        evaluation=_evaluation(1, "a" * 64),
        disposition="retry",
    )
    invalid_case = feedback.required[0].model_copy(update={"outcome": "provider-prose"})

    with pytest.raises(ValidationError):
        canonical_feedback(feedback.model_copy(update={"required": (invalid_case,)}))
    with pytest.raises(ValidationError):
        canonical_feedback(feedback.model_copy(update={"disposition": "accepted"}))
    with pytest.raises(ValueError, match="hidden or missing"):
        canonical_feedback(feedback.model_copy(update={"provider_prose": "repair this"}))


def test_attempt_two_stub_accepts_only_exact_attempt_one_feedback_bytes_and_digest(
    tmp_path: Path,
) -> None:
    store = SessionStore(
        tmp_path / "run", run_id="run-1", contract_id=_contract().experiment_id
    )
    candidate = tmp_path / "candidate"
    candidate.mkdir()
    feedback, evidence, _ = _publish_attempt(store, candidate, 1)
    expected_bytes, expected_sha = canonical_feedback(feedback)

    def attempt_two_stub(received: bytes, received_sha: str) -> bool:
        return received == expected_bytes and received_sha == expected_sha

    assert evidence.sha256 == expected_sha
    assert attempt_two_stub((store.attempt_path(1) / "feedback.json").read_bytes(), evidence.sha256)
    assert not attempt_two_stub(expected_bytes + b" ", expected_sha)
    assert not attempt_two_stub(expected_bytes, "0" * 64)


def test_resume_reconstructs_contiguous_best_recurrence_budget_and_prior_feedback(
    tmp_path: Path,
) -> None:
    store = SessionStore(
        tmp_path / "run", run_id="run-1", contract_id=_contract().experiment_id
    )
    candidate = tmp_path / "candidate"
    candidate.mkdir()
    _, _, first = _publish_attempt(store, candidate, 1)
    _, second_feedback, second = _publish_attempt(store, candidate, 2, accepted=True)
    store.publish_best(second)

    state = store.read_resume_state(_contract())

    assert state.next_attempt_index == 3
    assert state.best_attempt_identity is not None
    assert state.best_attempt_identity.attempt_index == 2
    assert state.best_attempt_identity.candidate_sha256 == second.candidate_inventory.tree_sha256
    assert [entry.first_attempt_index for entry in state.seen_recurrence_pairs] == [1, 2]
    assert state.accounted_wall_seconds == pytest.approx(0.5)
    assert state.prior_feedback_bytes == (store.attempt_path(2) / "feedback.json").read_bytes()
    assert state.prior_feedback_sha256 == second_feedback.sha256
    assert first.attempt_index == 1


def test_append_once_launch_intent_consumes_index_and_trailing_intent_blocks_resume(
    tmp_path: Path,
) -> None:
    store = SessionStore(
        tmp_path / "run",
        run_id="run-1",
        contract_id=_contract().experiment_id,
    )
    candidate = tmp_path / "candidate-launch-intent"
    candidate.mkdir()
    (candidate / "state.txt").write_text("before launch\n", encoding="utf-8")
    invocation = _invocation(1)

    _reserve_launch(store, candidate, 1, invocation)
    intent_path = store.launch_path(1)
    before = intent_path.read_bytes()

    with pytest.raises(FileExistsError):
        _reserve_launch(store, candidate, 1, invocation)
    with pytest.raises(ValueError, match="uncommitted launch intent"):
        store.read_resume_state(_contract())

    assert intent_path.read_bytes() == before
    assert not store.attempt_path(1).exists()


@pytest.mark.parametrize(
    "mutation",
    ["gap", "feedback", "payload", "pointer", "terminal", "noncanonical"],
)
def test_resume_refuses_gaps_stale_digests_pointer_mismatch_terminal_and_encoding(
    tmp_path: Path, mutation: str
) -> None:
    run = tmp_path / mutation / "run"
    store = SessionStore(run, run_id="run-1", contract_id=_contract().experiment_id)
    candidate = tmp_path / mutation / "candidate"
    candidate.mkdir(parents=True)
    _, _, first = _publish_attempt(store, candidate, 1)
    store.publish_best(first)

    if mutation == "gap":
        store.attempt_path(1).rename(store.attempt_path(2))
    elif mutation == "feedback":
        (store.attempt_path(1) / "feedback.json").write_bytes(b"{}\n")
    elif mutation == "payload":
        (store.attempt_path(1) / "verifier" / "required-a.json").write_bytes(b"changed")
    elif mutation == "pointer":
        pointer = json.loads((run / "best.json").read_text(encoding="utf-8"))
        pointer["candidate_sha256"] = "f" * 64
        (run / "best.json").write_text(json.dumps(pointer), encoding="utf-8")
    elif mutation == "terminal":
        best = json.loads((run / "best.json").read_text(encoding="utf-8"))
        store.publish_result(
            SessionResult(
                run_id="run-1",
                disposition="budget-exhausted",
                terminal_reason="fixture",
                attempt_count=1,
                best_attempt=1,
                best_attempt_manifest_sha256=best["attempt_manifest_sha256"],
                best_candidate_sha256=best["candidate_sha256"],
                referenced_evidence_digests={
                    "attempt_manifest_sha256": best["attempt_manifest_sha256"]
                },
            )
        )
    else:
        path = store.attempt_path(1) / "feedback.json"
        document = json.loads(path.read_bytes())
        path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")

    before = sorted(
        (path.relative_to(run).as_posix(), path.read_bytes())
        for path in run.rglob("*")
        if path.is_file()
    )
    with pytest.raises((ValueError, FileNotFoundError), match="."):
        store.read_resume_state(_contract())
    after = sorted(
        (path.relative_to(run).as_posix(), path.read_bytes())
        for path in run.rglob("*")
        if path.is_file()
    )
    assert after == before, "resume validation must never repair or rewrite evidence"


def test_publish_failure_cleans_unpublished_staging(tmp_path: Path) -> None:
    store = SessionStore(
        tmp_path / "run", run_id="run-1", contract_id=_contract().experiment_id
    )
    candidate = tmp_path / "candidate"
    candidate.mkdir()
    (candidate / "state.txt").write_text("one", encoding="utf-8")
    _reserve_launch(store, candidate, 1, _invocation(1))
    staged = store.stage_candidate(attempt_index=1, candidate_root=candidate)
    evaluation = _evaluation(1, staged.inventory.tree_sha256)
    feedback = build_attempt_feedback(
        run_id="run-1",
        contract=_contract(),
        contract_sha256=CONTRACT_SHA,
        invocation=_invocation(1),
        evaluation=evaluation,
        disposition="retry",
    )
    store.publish_feedback(attempt_index=1, feedback=feedback, staged_candidate=staged)

    with pytest.raises(ValueError, match="digest"):
        store.publish_attempt(
            attempt_index=1,
            candidate_root=candidate,
            invocation=_invocation(1),
            verifier_payloads={"required-a": b"wrong"},
            evaluation=evaluation,
            contract=_contract(),
            best_eligible=True,
            staged_candidate=staged,
        )

    assert not store.attempt_path(1).exists()
    assert not list((store.root / ".staging").iterdir())


def test_store_refuses_symlinked_or_replaced_owned_directories(tmp_path: Path) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    run = tmp_path / "preexisting"
    run.mkdir()
    (run / "attempts").symlink_to(outside, target_is_directory=True)

    with pytest.raises(ValueError, match="must be real"):
        SessionStore(run, run_id="run-1", contract_id=_contract().experiment_id)

    live = tmp_path / "live"
    store = SessionStore(live, run_id="run-1", contract_id=_contract().experiment_id)
    (live / ".staging").rmdir()
    (live / ".staging").symlink_to(outside, target_is_directory=True)
    candidate = tmp_path / "candidate-replaced-directory"
    candidate.mkdir()
    (candidate / "state.txt").write_text("one", encoding="utf-8")

    with pytest.raises(ValueError, match="could not be opened safely|changed identity"):
        store.stage_candidate(attempt_index=1, candidate_root=candidate)
    assert not list(outside.iterdir())


def test_resume_refuses_a_self_consistent_root_replaced_after_preflight(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    live = tmp_path / "run-root-race"
    store = SessionStore(live, run_id="run-1", contract_id=_contract().experiment_id)
    preserved = tmp_path / "run-root-race-preserved"
    original_assert = store._assert_store_layout
    injected = False

    def replace_after_preflight() -> None:
        nonlocal injected
        original_assert()
        if not injected:
            injected = True
            live.rename(preserved)
            live.mkdir()
            (live / "attempts").mkdir()
            (live / ".staging").mkdir()

    monkeypatch.setattr(store, "_assert_store_layout", replace_after_preflight)
    with pytest.raises(ValueError, match="changed identity"):
        store.read_resume_state(_contract())

    assert injected is True


def test_resume_binds_each_attempt_inode_captured_during_enumeration(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    primary = SessionStore(
        tmp_path / "primary",
        run_id="run-1",
        contract_id=_contract().experiment_id,
    )
    alternate = SessionStore(
        tmp_path / "alternate",
        run_id="run-1",
        contract_id=_contract().experiment_id,
    )
    primary_candidate = tmp_path / "primary-candidate"
    primary_candidate.mkdir()
    alternate_candidate = tmp_path / "alternate-candidate"
    alternate_candidate.mkdir()
    (alternate_candidate / "alternate.txt").write_text("other", encoding="utf-8")
    _, _, primary_record = _publish_attempt(primary, primary_candidate, 1)
    _, _, alternate_record = _publish_attempt(alternate, alternate_candidate, 1)
    primary.publish_best(primary_record)
    alternate.publish_best(alternate_record)

    original_load = primary._load_attempt_for_resume_bound
    injected = False

    def swap_after_enumeration(attempt_index: int, **kwargs):
        nonlocal injected
        if not injected:
            injected = True
            primary_attempt = primary.attempt_path(1)
            primary_attempt.rename(primary_attempt.with_name("0001-preserved"))
            alternate.attempt_path(1).rename(primary_attempt)
            (primary.root / "best.json").rename(primary.root / "best-preserved.json")
            (alternate.root / "best.json").rename(primary.root / "best.json")
        return original_load(attempt_index, **kwargs)

    monkeypatch.setattr(primary, "_load_attempt_for_resume_bound", swap_after_enumeration)
    with pytest.raises(ValueError, match="enumerated identity"):
        primary.read_resume_state(_contract())

    assert injected is True


def test_resume_requires_the_exact_deterministic_best_pointer(tmp_path: Path) -> None:
    candidate = tmp_path / "candidate"
    candidate.mkdir()

    missing_store = SessionStore(
        tmp_path / "missing",
        run_id="run-1",
        contract_id=_contract().experiment_id,
    )
    _publish_attempt(missing_store, candidate, 1)
    with pytest.raises(ValueError, match="without a complete best pointer"):
        missing_store.read_resume_state(_contract())

    stale_store = SessionStore(
        tmp_path / "stale",
        run_id="run-1",
        contract_id=_contract().experiment_id,
    )
    _, _, first = _publish_attempt(stale_store, candidate, 1)
    _publish_attempt(stale_store, candidate, 2, accepted=True)
    stale_store.publish_best(first)
    with pytest.raises(ValueError, match="deterministic best"):
        stale_store.read_resume_state(_contract())


def test_resume_rejects_boolean_best_attempt_identity(tmp_path: Path) -> None:
    run = tmp_path / "run-boolean-pointer"
    store = SessionStore(run, run_id="run-1", contract_id=_contract().experiment_id)
    candidate = tmp_path / "candidate-boolean-pointer"
    candidate.mkdir()
    _, _, first = _publish_attempt(store, candidate, 1)
    store.publish_best(first)
    pointer_path = run / "best.json"
    pointer = json.loads(pointer_path.read_bytes())
    pointer["attempt"] = True
    pointer_path.write_text(
        json.dumps(pointer, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="attempt must be an integer"):
        store.read_resume_state(_contract())


def test_publish_best_refuses_a_leaf_created_after_validated_absence(tmp_path: Path) -> None:
    run = tmp_path / "run-best-absence-race"
    store = SessionStore(run, run_id="run-1", contract_id=_contract().experiment_id)
    assert store.read_resume_state(_contract()).best_attempt_identity is None
    candidate = tmp_path / "candidate-best-absence-race"
    candidate.mkdir()
    _, _, record = _publish_attempt(store, candidate, 1)
    (run / "best.json").write_bytes(b"racer\n")

    with pytest.raises(ValueError, match="appeared after its absence"):
        store.publish_best(record)
    assert (run / "best.json").read_bytes() == b"racer\n"


def test_attempt_publication_is_independent_of_a_swapped_staging_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    store = SessionStore(
        tmp_path / "run-source-race",
        run_id="run-1",
        contract_id=_contract().experiment_id,
    )
    candidate = tmp_path / "candidate-source-race"
    candidate.mkdir()
    (candidate / "state.txt").write_text("one", encoding="utf-8")
    _reserve_launch(store, candidate, 1, _invocation(1))
    staged = store.stage_candidate(attempt_index=1, candidate_root=candidate)
    evaluation = _evaluation(1, staged.inventory.tree_sha256)
    feedback = build_attempt_feedback(
        run_id="run-1",
        contract=_contract(),
        contract_sha256=CONTRACT_SHA,
        invocation=_invocation(1),
        evaluation=evaluation,
        disposition="retry",
    )
    store.publish_feedback(attempt_index=1, feedback=feedback, staged_candidate=staged)
    original_publish = session_store_module.publish_directory_once
    injected = False

    def swap_source(root, relative, files, **kwargs):
        nonlocal injected
        if not injected:
            injected = True
            preserved = staged._staging_path.with_name(
                f"{staged._staging_path.name}-preserved"
            )
            staged._staging_path.rename(preserved)
            staged._staging_path.mkdir()
            try:
                return original_publish(root, relative, files, **kwargs)
            finally:
                staged._staging_path.rmdir()
                preserved.rename(staged._staging_path)
        return original_publish(root, relative, files, **kwargs)

    monkeypatch.setattr(
        session_store_module,
        "publish_directory_once",
        swap_source,
    )
    store.publish_attempt(
        attempt_index=1,
        candidate_root=candidate,
        invocation=_invocation(1),
        verifier_payloads={"required-a": _raw_verifier_payload(accepted=False)},
        evaluation=evaluation,
        contract=_contract(),
        best_eligible=True,
        staged_candidate=staged,
    )

    assert injected is True
    assert (store.attempt_path(1) / "candidate" / "state.txt").read_text() == "one"
    assert not list((store.root / ".staging").iterdir())
