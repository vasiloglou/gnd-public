import inspect
import json
import subprocess
import sys
from pathlib import Path

import gnd.api

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/public-emitter-trust-controls"
CASES = json.loads((FIXTURE / "cases.json").read_text())
ANSWERS = json.loads((FIXTURE / "canary-policy.json").read_text())
MODELS = {row["id"]: FIXTURE / row["path"] for row in CASES["models"]}
SNAPSHOTS = {row["id"]: row for row in CASES["snapshot_cases"]}
TRANSITIONS = {row["id"]: row for row in CASES["transition_cases"]}
SYNTHETIC_EXITS = {row["id"]: row for row in CASES["synthetic_exits"]}
SELECTED_CANARIES = tuple(ANSWERS["canaries"]["selected"])
PUBLIC_CANARIES = tuple(ANSWERS["canaries"]["public_controls"])

def _run_cli(*arguments: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        [sys.executable, "-m", "gnd", *arguments],
        cwd=ROOT,
        capture_output=True,
        check=False,
    )


def _payload(completed: subprocess.CompletedProcess[bytes]) -> dict[str, object]:
    value = json.loads(completed.stdout)
    assert isinstance(value, dict)
    return value


def _fixture_path(relative: str) -> str:
    return str((FIXTURE / relative).relative_to(ROOT))


def _encoded(value: object) -> bytes:
    return json.dumps(value, allow_nan=False, sort_keys=True).encode("utf-8")


def _assert_applied_bytes_are_safe(raw: bytes) -> None:
    assert not [token for token in SELECTED_CANARIES if token.encode() in raw]


def _assert_no_false_marker(raw: bytes) -> None:
    assert b'"redaction"' not in raw
    assert ANSWERS["marker_text"].encode() not in raw
    assert ANSWERS["instance_text_marker"].encode() not in raw


def _identity(payload: dict[str, object]) -> dict[str, object]:
    return {key: payload.get(key) for key in ANSWERS["identity_fields"]}


def test_pre_model_failure_has_no_false_marker() -> None:
    completed = _run_cli("check", "--format", "json")
    raw = completed.stdout + completed.stderr
    assert completed.returncode == 64
    _assert_no_false_marker(raw)


def test_invalid_model_has_no_false_marker(tmp_path: Path) -> None:
    model = MODELS["M-01"].read_text(encoding="utf-8")
    assert model.count("redact: true") == 1
    invalid_model = tmp_path / "invalid-redaction.orm.yaml"
    invalid_model.write_text(model.replace("redact: true", "redact: yes"), encoding="utf-8")
    completed = _run_cli(
        "check",
        str(invalid_model),
        _fixture_path(SNAPSHOTS["SN-00"]["population"]),
        "--format",
        "json",
    )
    raw = completed.stdout + completed.stderr
    _assert_no_false_marker(raw)
    assert completed.returncode == 3


def test_missing_model_before_policy_has_no_false_marker() -> None:
    case = SYNTHETIC_EXITS["X-03-PRE"]
    completed = _run_cli(
        "check",
        "tests/fixtures/v61-phase4/models/does-not-exist.orm.yaml",
        _fixture_path(SNAPSHOTS["SN-00"]["population"]),
        "--format",
        "json",
    )
    raw = completed.stdout + completed.stderr
    _assert_no_false_marker(raw)
    assert completed.returncode == case["expected_exit"]


def test_over_cap_model_before_policy_has_no_false_marker(tmp_path: Path) -> None:
    case = SYNTHETIC_EXITS["X-03-PRE"]
    canary = b"P4_PREMODEL_CANARY_03"
    prefix = b"version: 2\nmodel_id: " + canary + b"\n#"
    document = prefix + (b"x" * (10_485_761 - len(prefix)))
    over_cap = tmp_path / "over-cap.orm.yaml"
    over_cap.write_bytes(document)
    assert over_cap.stat().st_size == 10_485_761

    completed = _run_cli(
        "check",
        str(over_cap),
        _fixture_path(SNAPSHOTS["SN-00"]["population"]),
        "--format",
        "json",
    )
    raw = completed.stdout + completed.stderr
    _assert_no_false_marker(raw)
    assert canary not in raw
    assert completed.returncode == case["expected_exit"]


def test_raw_applied_and_unredacted_outputs_enforce_canary_policy() -> None:
    case = TRANSITIONS["B-01"]
    model = MODELS[case["model"]]
    applied = gnd.api.transition(
        model,
        FIXTURE / case["pre"],
        FIXTURE / case["steps"],
        post=None,
    )
    unredacted = gnd.api.transition(
        model,
        FIXTURE / case["pre"],
        FIXTURE / case["steps"],
        post=None,
        unredacted=True,
    )
    applied_bytes = _encoded(applied)
    unredacted_bytes = _encoded(unredacted)
    _assert_applied_bytes_are_safe(applied_bytes)
    assert any(token.encode() in unredacted_bytes for token in SELECTED_CANARIES)
    assert any(token.encode() in applied_bytes for token in PUBLIC_CANARIES)
    assert applied["redaction"] == ANSWERS["applied_redaction"]
    assert unredacted["redaction"] == ANSWERS["unredacted_redaction"]


def test_redaction_changes_no_semantic_identity() -> None:
    case = SNAPSHOTS["SN-01"]
    model = MODELS[case["model"]]
    population = FIXTURE / case["population"]
    applied = gnd.api.check(model, population)
    unredacted = gnd.api.check(model, population, unredacted=True)
    assert _identity(applied) == _identity(unredacted)


def test_api_and_cli_expose_only_the_trusted_unredacted_switch() -> None:
    for function in (gnd.api.validate, gnd.api.check, gnd.api.transition):
        parameter = inspect.signature(function).parameters["unredacted"]
        assert parameter.kind is inspect.Parameter.KEYWORD_ONLY
        assert parameter.default is False

    case = SNAPSHOTS["SN-00"]
    completed = _run_cli(
        "check",
        str(MODELS[case["model"]].relative_to(ROOT)),
        _fixture_path(case["population"]),
        "--unredacted",
        "--format",
        "json",
    )
    assert completed.returncode == case["expected_exit"]
    assert _payload(completed)["redaction"] == ANSWERS["unredacted_redaction"]
