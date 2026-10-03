"""Walk-floor matching and normative ordering for Phase 5."""

from __future__ import annotations

import copy
import json
from pathlib import Path

from gnd.exp import session_eval
from gnd.exp.session_contract import DataDrivenContract, RequiredOperation, WalkAcceptance
from gnd.exp.session_eval import CaseEvaluation

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/public-walk-floor"
DOCUMENT = json.loads((FIXTURE / "session/contract-v5.json").read_text(encoding="utf-8"))
STEPS = json.loads((FIXTURE / "session/candidate/steps.json").read_text(encoding="utf-8"))["steps"]
ANSWERS = json.loads((FIXTURE / "answers.json").read_text(encoding="utf-8"))


def _declaration(required: list[dict[str, object]], forbidden: list[str]):
    document = copy.deepcopy(DOCUMENT)
    document["cases"][0]["acceptance"]["walk"] = {
        "required_ops": required,
        "forbidden_ops": forbidden,
    }
    return DataDrivenContract.model_validate(document).cases[0].acceptance.walk


def _rows(gaps: object) -> list[dict[str, object]]:
    return [
        row.model_dump(mode="json") if hasattr(row, "model_dump") else dict(row) for row in gaps
    ]


def _gaps(required: list[dict[str, object]], forbidden: list[str], steps=STEPS):
    matcher = session_eval.walk_floor_gaps
    return _rows(matcher(_declaration(required, forbidden), steps))


def _result(band: int) -> CaseEvaluation:
    outcome = {0: "accepted", 1: "violated", 3: "ill_formed"}[band]
    return CaseEvaluation(
        payload_valid=True,
        case_id="expense-walk",
        role="required",
        candidate_sha256="1" * 64,
        contract_sha256="2" * 64,
        raw_payload_sha256="3" * 64,
        command="transition",
        process_exit=band,
        payload_exit=band,
        outcome=outcome,
        acceptance_ready=band == 0,
        counts={"pass": 0, "fail": 0, "warning": 0, "unchecked": 0, "vacuous": 0},
        coverage={},
        alethic_failure_count=int(band == 1),
        alethic_indeterminate_count=0,
    )


def test_e01_e04_required_subset_matches_one_step_and_allows_extra_bindings() -> None:
    required = [{"op": "approve_expense", "bindings_subset": {"expense": 41}}]
    assert _gaps(required, []) == ANSWERS["cases"]["E01"]["gaps"]
    assert _gaps(required, []) == ANSWERS["cases"]["E04"]["gaps"]


def test_e02_e03_missing_operation_or_wrong_binding_is_unmet() -> None:
    absent = [{"op": "approve_expense", "bindings_subset": {}}]
    wrong = [{"op": "approve_expense", "bindings_subset": {"expense": 99}}]
    no_approval = [step for step in STEPS if step["op"] != "approve_expense"]
    assert _gaps(absent, [], no_approval) == ANSWERS["cases"]["E02"]["gaps"]
    assert _gaps(wrong, []) == ANSWERS["cases"]["E03"]["gaps"]


def test_e05_different_steps_cannot_pool_one_required_subset() -> None:
    required = [
        {
            "op": "approve_expense",
            "bindings_subset": {"expense": 41, "approver": "P5_SECRET_APPROVER_271828"},
        }
    ]
    split = [
        {"op": "approve_expense", "bindings": {"expense": 41}},
        {"op": "approve_expense", "bindings": {"approver": "P5_SECRET_APPROVER_271828"}},
    ]
    assert _gaps(required, [], split) == ANSWERS["cases"]["E05"]["gaps"]


def test_e06_e09_forbidden_operation_is_an_absence_policy() -> None:
    assert _gaps([], ["pay_without_approval"]) == ANSWERS["cases"]["E06"]["gaps"]
    unsafe = [*STEPS, {"op": "pay_without_approval", "bindings": {"expense": 41}}]
    assert _gaps([], ["pay_without_approval"], unsafe) == ANSWERS["cases"]["E09"]["gaps"]


def test_e10_all_required_and_forbidden_floors_discharged() -> None:
    required = [{"op": "approve_expense", "bindings_subset": {"expense": 41}}]
    assert _gaps(required, ["pay_without_approval"]) == []


def test_e07_e08_nonzero_or_refused_transition_is_never_rescued_by_floors() -> None:
    case = DataDrivenContract.model_validate(DOCUMENT).cases[0]
    for band in (1, 3):
        decision = session_eval.case_decision(case, _result(band))
        assert decision.accepted is False
        assert decision.raw_band == band
        assert decision.walk_floor_gaps == ()


def test_floor_application_is_a_distinct_post_verdict_step() -> None:
    result = session_eval.attach_walk_floor_steps(_result(0), STEPS)
    decision = session_eval.case_decision(
        DataDrivenContract.model_validate(DOCUMENT).cases[0], result
    )
    assert decision.accepted is True
    assert decision.walk_floor_gaps == ()


def test_type_aware_scalar_identity_never_conflates_boolean_and_integer() -> None:
    required = [{"op": "approve_expense", "bindings_subset": {"expense": True}}]
    assert _gaps(required, []) == [
        {"kind": "required-op-missing", "operation_id": "approve_expense"}
    ]


def test_review_04_number_identity_matches_integer_and_float_spellings() -> None:
    declaration = WalkAcceptance(
        required_ops=(RequiredOperation(op="measure", bindings_subset={"value": 1}),),
        forbidden_ops=(),
    )
    assert (
        session_eval.walk_floor_gaps(
            declaration,
            [{"op": "measure", "bindings": {"value": 1.0}}],
        )
        == ()
    )


def test_e11_redacted_canary_is_matched_but_never_returned_in_a_gap() -> None:
    required = [
        {
            "op": "approve_expense",
            "bindings_subset": {"approver": ANSWERS["canary"]},
        }
    ]
    gaps = _gaps(required, [])
    assert gaps == []
    assert ANSWERS["canary"] not in json.dumps(gaps, sort_keys=True)


def test_e12_diagnostic_gap_is_separate_from_discharged_required_floor() -> None:
    required_gaps = _gaps([{"op": "approve_expense", "bindings_subset": {"expense": 41}}], [])
    diagnostic_gaps = _gaps(
        [{"op": "pay_without_approval", "bindings_subset": {"expense": 41}}], []
    )
    assert required_gaps == []
    assert diagnostic_gaps == [
        {"kind": "required-op-missing", "operation_id": "pay_without_approval"}
    ]
