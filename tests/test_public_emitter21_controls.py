"""Frozen 21-emitter fixture and projection controls; no full registry coverage claim."""

import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FIXTURE = ROOT / "tests/fixtures/public-emitter21"

CASES = json.loads((FIXTURE / "cases.json").read_text(encoding="utf-8"))

ANSWERS = json.loads((FIXTURE / "answers.json").read_text(encoding="utf-8"))

EMITTERS = json.loads((FIXTURE / "emitter-manifest.json").read_text(encoding="utf-8"))

SESSION = json.loads((FIXTURE / CASES["session"]["answers"]).read_text(encoding="utf-8"))

MODELS = {row["id"]: FIXTURE / row["path"] for row in CASES["models"]}

SELECTED_CANARIES = tuple(ANSWERS["canaries"]["selected"])

PUBLIC_CANARIES = tuple(ANSWERS["canaries"]["public_controls"])


def _encoded(value: object) -> bytes:
    return json.dumps(value, allow_nan=False, sort_keys=True).encode("utf-8")


def _identity(payload: dict[str, object]) -> dict[str, object]:
    return {key: payload.get(key) for key in ANSWERS["identity_fields"]}


def _instrument_failures(
    *,
    applied: dict[str, object],
    unredacted: dict[str, object],
    executed_emitters: set[str],
) -> set[str]:
    failures: set[str] = set()
    applied_bytes = _encoded(applied)
    unredacted_bytes = _encoded(unredacted)
    if any(token.encode() in applied_bytes for token in SELECTED_CANARIES):
        failures.add("selected-canary-leak")
    if not any(token.encode() in unredacted_bytes for token in SELECTED_CANARIES):
        failures.add("unredacted-canary-missing")
    if applied.get("redaction") != ANSWERS["applied_redaction"]:
        failures.add("marker-coordinate-change")
    if unredacted.get("redaction") != ANSWERS["unredacted_redaction"]:
        failures.add("unredacted-marker-change")
    if _identity(applied) != _identity(unredacted):
        failures.add("semantic-identity-change")
    expected_emitters = {row["id"] for row in EMITTERS["emitters"]}
    if executed_emitters != expected_emitters:
        failures.add("emitter-coverage-change")
    return failures


def _synthetic_pair() -> tuple[dict[str, object], dict[str, object]]:
    identity = {key: None for key in ANSWERS["identity_fields"]}
    identity.update(
        {
            "exit_code": 1,
            "outcome": "violated",
            "acceptance_ready": False,
            "counts": {"fail": 1},
            "constraint_ref": "optional_code:uniqueness:code",
            "constraint_type": "uniqueness",
            "modality": "alethic",
            "verdict": "fail",
            "reason_code": "duplicate-role-value",
        }
    )
    applied = {
        **identity,
        "redaction": copy.deepcopy(ANSWERS["applied_redaction"]),
        "witness": ANSWERS["marker"],
        "message": ANSWERS["marker_text"],
        "public": PUBLIC_CANARIES[0],
    }
    unredacted = {
        **identity,
        "redaction": copy.deepcopy(ANSWERS["unredacted_redaction"]),
        "witness": SELECTED_CANARIES[0],
        "message": SELECTED_CANARIES[0],
        "public": PUBLIC_CANARIES[0],
    }
    return applied, unredacted


def _emitter_case_matrix_failures(manifest: dict[str, object]) -> set[str]:
    emitters = manifest["emitters"]
    matrix = manifest["exit_case_matrix"]
    expected = {
        (emitter["id"], str(exit_code))
        for emitter in emitters
        for exit_code in emitter["reachable_exits"]
    }
    declared = {(row["emitter_id"], exit_code) for row in matrix for exit_code in row["cases"]}
    failures = {"registry-minus-executed"} if declared != expected else set()
    if failures:
        return failures
    case_exits = {
        row["id"]: {row["expected_exit"]}
        for group in (CASES["snapshot_cases"], CASES["transition_cases"], CASES["synthetic_exits"])
        for row in group
        if "expected_exit" in row
    }
    case_exits.update({"M-01": {0}, "M-04A": {3}, "B-02": set(range(5)), "B-03": {0}})
    case_exits.update({case_id: {0, 1, 2, 3, 4, 70} for case_id in SESSION["case_ids"]})
    pre_model = {
        (row["emitter_id"], row["exit"], row["case_id"]) for row in manifest["pre_model_exceptions"]
    }
    from gnd.model import load_model
    from gnd.redaction import RedactionPolicy, project_output

    policy = RedactionPolicy.from_model(load_model(MODELS["M-01"]))
    emitter_by_id = {row["id"]: row for row in emitters}
    for emitter_id, exit_code in expected:
        case_id = next(row["cases"][exit_code] for row in matrix if row["emitter_id"] == emitter_id)
        numeric_exit = int(exit_code)
        if (emitter_id, numeric_exit, case_id) in pre_model:
            continue
        if numeric_exit not in case_exits.get(case_id, set()):
            failures.add("behavioral-case-mismatch")
            continue
        payload = project_output(
            emitter_by_id[emitter_id]["kind"],
            {
                "exit_code": numeric_exit,
                "issues": [
                    {"path": "$.facts.optional_code[0].code", "message": SELECTED_CANARIES[0]}
                ],
            },
            policy=policy,
            mode="applied",
            emitter_id=emitter_id,
        )
        if SELECTED_CANARIES[0] in json.dumps(payload) or payload["redaction"]["mode"] != "applied":
            failures.add("behavioral-projection-failure")
    return failures


def test_emitter_manifest_is_closed_and_declares_every_reachable_exit() -> None:
    assert CASES["schema_version"] == ANSWERS["schema_version"] == 1
    assert EMITTERS["schema_version"] == 1
    emitters = EMITTERS["emitters"]
    ids = [row["id"] for row in emitters]
    assert len(ids) == len(set(ids)) == 21
    assert set(EMITTERS["output_kinds"]) == {row["kind"] for row in emitters}
    assert set(EMITTERS["post_model_exit_cases"]) == {
        "0",
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "64",
        "70",
        "74",
    }
    case_ids = {
        row["id"]
        for group in (
            CASES["snapshot_cases"],
            CASES["transition_cases"],
            CASES["synthetic_exits"],
        )
        for row in group
    }
    assert set(EMITTERS["post_model_exit_cases"].values()) <= case_ids
    before_model = set(EMITTERS["exit_policy"]["before_model_load"]["exits"])
    after_model = set(EMITTERS["exit_policy"]["after_model_load"]["exits"])
    post_model_cases = EMITTERS["post_model_exit_cases"]
    for emitter in emitters:
        for exit_code in emitter["reachable_exits"]:
            assert exit_code in before_model | after_model
            if exit_code in after_model:
                assert str(exit_code) in post_model_cases
    matrix = EMITTERS["exit_case_matrix"]
    assert [row["emitter_id"] for row in matrix] == ids
    for emitter, row in zip(emitters, matrix, strict=True):
        assert set(row["cases"]) == {str(code) for code in emitter["reachable_exits"]}
        assert all(isinstance(case_id, str) and case_id for case_id in row["cases"].values())
    assert not _emitter_case_matrix_failures(EMITTERS)

    expected_pre_model = {
        (row["id"], 3, "X-03-PRE") for row in emitters if row["surface"] in {"api", "cli"}
    }
    expected_pre_model |= {(row["id"], 64, "X-64") for row in emitters if row["surface"] == "cli"}
    expected_pre_model |= {
        ("cli-batch-json", 66, "X-66-PRE"),
        ("cli-batch-json", 74, "X-74-PRE"),
    }
    assert {
        (row["emitter_id"], row["exit"], row["case_id"]) for row in EMITTERS["pre_model_exceptions"]
    } == expected_pre_model
    assert set(CASES["negative_controls"]) == {
        "bypass-projection",
        "drop-emitter-case",
        "structured-canary-leak",
        "free-text-canary-leak",
        "marker-coordinate-change",
        "semantic-identity-change",
    }


def test_emitter_exit_case_matrix_drop_cell_control_is_live() -> None:
    control = EMITTERS["matrix_negative_control"]
    assert control["mutation"] == "drop-emitter-exit-cell"
    mutated = copy.deepcopy(EMITTERS)
    row = next(
        row for row in mutated["exit_case_matrix"] if row["emitter_id"] == control["emitter_id"]
    )
    del row["cases"][str(control["exit"])]
    assert control["expected_failure"] in _emitter_case_matrix_failures(mutated)


def test_emitter_exit_case_matrix_rejects_a_wrong_behavioral_case() -> None:
    mutated = copy.deepcopy(EMITTERS)
    row = next(
        row for row in mutated["exit_case_matrix"] if row["emitter_id"] == "cli-measure-json"
    )
    row["cases"]["6"] = "SN-00"
    assert "behavioral-case-mismatch" in _emitter_case_matrix_failures(mutated)


def test_leak_instrument_rejects_every_declared_dirty_control() -> None:
    applied, unredacted = _synthetic_pair()
    emitter_ids = {row["id"] for row in EMITTERS["emitters"]}
    assert not _instrument_failures(
        applied=applied,
        unredacted=unredacted,
        executed_emitters=emitter_ids,
    )

    structured = copy.deepcopy(applied)
    structured["witness"] = SELECTED_CANARIES[0]
    assert "selected-canary-leak" in _instrument_failures(
        applied=structured,
        unredacted=unredacted,
        executed_emitters=emitter_ids,
    )
    free_text = copy.deepcopy(applied)
    free_text["message"] = f"detail: {SELECTED_CANARIES[0]}"
    assert "selected-canary-leak" in _instrument_failures(
        applied=free_text,
        unredacted=unredacted,
        executed_emitters=emitter_ids,
    )
    wrong_marker = copy.deepcopy(applied)
    wrong_marker["redaction"] = copy.deepcopy(ANSWERS["dirty_controls"]["marker"])
    assert "marker-coordinate-change" in _instrument_failures(
        applied=wrong_marker,
        unredacted=unredacted,
        executed_emitters=emitter_ids,
    )
    changed_identity = copy.deepcopy(applied)
    changed_identity["exit_code"] = ANSWERS["dirty_controls"]["changed_exit"] + 1
    assert "semantic-identity-change" in _instrument_failures(
        applied=changed_identity,
        unredacted=unredacted,
        executed_emitters=emitter_ids,
    )
    missing = emitter_ids - {ANSWERS["dirty_controls"]["missing_emitter"]}
    assert "emitter-coverage-change" in _instrument_failures(
        applied=applied,
        unredacted=unredacted,
        executed_emitters=missing,
    )
