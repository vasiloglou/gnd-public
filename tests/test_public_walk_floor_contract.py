from __future__ import annotations

import copy
import json
import shutil
from pathlib import Path

import pytest
from pydantic import ValidationError

from gnd.exp.session_contract import DataDrivenContract, SessionContractError, read_session_contract

FIXTURE = Path(__file__).parent / "fixtures/public-walk-floor"
DOCUMENT = json.loads((FIXTURE / "session/contract-v5.json").read_text())
ANSWERS = json.loads((FIXTURE / "answers.json").read_text())
CASE_DATA = json.loads((FIXTURE / "contract-cases.json").read_text())
CASES = {"contract": CASE_DATA["contract"]}
V4_DOCUMENT = CASE_DATA["v4_contract"]
TESTS_CASE = CASE_DATA["tests_case"]

def _validate(document: dict[str, object]) -> DataDrivenContract:
    return DataDrivenContract.model_validate(document)


def _semantic_read(tmp_path: Path, document: dict[str, object]) -> DataDrivenContract:
    root = tmp_path / "session"
    shutil.copytree(FIXTURE / "session", root)
    path = root / "contract-v5.json"
    path.write_text(json.dumps(document, allow_nan=True), encoding="utf-8")
    return read_session_contract(
        path,
        experiment_root=root,
        experiment_id="EXP-061-walk-floor",
    )


def test_c01_c04_contract_v5_is_closed_and_version_dispatched(tmp_path: Path) -> None:
    contract = _semantic_read(tmp_path, DOCUMENT)
    assert contract.schema_version == ANSWERS["versions"]["contract"] == 5
    assert [case.acceptance.walk is not None for case in contract.cases] == [True, False]
    assert contract.model_dump(mode="json") == DOCUMENT
    assert DataDrivenContract.model_validate_json(json.dumps(DOCUMENT)).schema_version == 5


@pytest.mark.parametrize(
    "case_id,mutate",
    [
        (
            "C05",
            lambda d: d["cases"][0]["acceptance"].update(
                walk={"required_ops": [], "forbidden_ops": []}
            ),
        ),
        (
            "C06",
            lambda d: d["cases"][0]["acceptance"]["walk"]["required_ops"].append(
                copy.deepcopy(d["cases"][0]["acceptance"]["walk"]["required_ops"][0])
            ),
        ),
        (
            "C07",
            lambda d: d["cases"][0]["acceptance"]["walk"]["forbidden_ops"].append(
                "pay_without_approval"
            ),
        ),
        (
            "C08",
            lambda d: d["cases"][0]["acceptance"]["walk"]["forbidden_ops"].append(
                "approve_expense"
            ),
        ),
        ("C12", lambda d: d.update(schema_version=4)),
    ],
)
def test_c05_c08_c12_closed_shape_mutations_refuse(case_id: str, mutate) -> None:
    assert case_id in {row["id"] for row in CASES["contract"]}
    dirty = copy.deepcopy(DOCUMENT)
    mutate(dirty)
    with pytest.raises(ValidationError):
        _validate(dirty)


@pytest.mark.parametrize(
    "case_id,op,key,value",
    [
        ("C09", "unknown_operation", "expense", 41),
        ("C10", "approve_expense", "unknown_parameter", 41),
        ("C11", "approve_expense", "expense", "not-an-integer"),
    ],
)
def test_c09_c11_model_bound_declaration_mutations_refuse(
    tmp_path: Path, case_id: str, op: str, key: str, value: object
) -> None:
    assert case_id in {row["id"] for row in CASES["contract"]}
    dirty = copy.deepcopy(DOCUMENT)
    dirty["cases"][0]["acceptance"]["walk"]["required_ops"] = [
        {"op": op, "bindings_subset": {key: value}}
    ]
    with pytest.raises(SessionContractError):
        _semantic_read(tmp_path, dirty)


@pytest.mark.parametrize(
    "value",
    [[[[]]], 10**5000, float("nan"), float("inf")],
    ids=["deep-nesting", "long-integer", "nan", "infinity"],
)
def test_c13_c15_hostile_binding_values_refuse_without_raw_exception(value: object) -> None:
    dirty = copy.deepcopy(DOCUMENT)
    dirty["cases"][0]["acceptance"]["walk"]["required_ops"][0]["bindings_subset"]["expense"] = value
    with pytest.raises(ValidationError):
        _validate(dirty)


def test_review_01_walk_floor_arrays_are_element_bounded() -> None:
    dirty = copy.deepcopy(DOCUMENT)
    dirty["cases"][0]["acceptance"]["walk"]["forbidden_ops"] = [
        f"op-{index}" for index in range(4097)
    ]
    with pytest.raises(ValidationError):
        _validate(dirty)


def test_review_02_mixed_v5_tests_case_still_requires_sealed_tests(tmp_path: Path) -> None:
    dirty = copy.deepcopy(DOCUMENT)
    dirty["cases"][1] = copy.deepcopy(TESTS_CASE)
    dirty["cases"][1]["role"] = "diagnostic"
    with pytest.raises(SessionContractError):
        _semantic_read(tmp_path, dirty)


def test_review_07_mixed_v5_tests_case_round_trips_canonically() -> None:
    dirty = copy.deepcopy(DOCUMENT)
    dirty["cases"][1] = copy.deepcopy(TESTS_CASE)
    dirty["cases"][1]["role"] = "diagnostic"
    parsed = _validate(dirty)
    serialized = parsed.model_dump(mode="json")
    assert DataDrivenContract.model_validate(serialized).model_dump(mode="json") == serialized


def test_empty_binding_subset_is_a_legal_operation_only_requirement() -> None:
    document = copy.deepcopy(DOCUMENT)
    document["cases"][0]["acceptance"]["walk"]["required_ops"][0]["bindings_subset"] = {}
    assert _validate(document).cases[0].acceptance.walk.required_ops[0].bindings_subset == {}


def test_f02_v4_transition_shape_and_serialization_remain_frozen() -> None:
    parsed = _validate(V4_DOCUMENT)
    assert parsed.model_dump(mode="json") == V4_DOCUMENT

    widened = copy.deepcopy(V4_DOCUMENT)
    widened["cases"][0]["acceptance"]["walk"] = None
    with pytest.raises(ValidationError):
        _validate(widened)

    relabeled = copy.deepcopy(V4_DOCUMENT)
    relabeled["schema_version"] = 5
    with pytest.raises(ValidationError):
        _validate(relabeled)


def test_f03_duplicate_identity_preserves_numeric_json_spelling() -> None:
    document = copy.deepcopy(DOCUMENT)
    document["cases"][0]["acceptance"]["walk"]["required_ops"] = [
        {"op": "approve_expense", "bindings_subset": {"expense": 1}},
        {"op": "approve_expense", "bindings_subset": {"expense": 1.0}},
    ]

    required = _validate(document).cases[0].acceptance.walk.required_ops
    assert [row.bindings_subset["expense"] for row in required] == [1, 1.0]
