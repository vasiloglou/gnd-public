

from __future__ import annotations

import pytest
from support.v62_phase1_corpus import ANSWERS, CASES, document, write_model

from gnd.model import ModelValidationError, load_model, semantic_validate

CURRENT_RULE_OVERRIDES = {
    "V03": "semantic:derivation-effect-on-semiderived",
}


@pytest.mark.parametrize("case_id", [f"V{index:02d}" for index in range(1, 6)])
def test_validation_case(case_id: str, tmp_path) -> None:
    case = CASES[case_id]
    answer = ANSWERS[case_id]
    path = write_model(tmp_path, case["variant"])
    if answer["exit"] == 0:
        load_model(path)
        return
    with pytest.raises(ModelValidationError) as caught:
        load_model(path)
    assert caught.value.issues[0].rule_id == CURRENT_RULE_OVERRIDES.get(case_id, answer["rule_id"])
    if case_id == "V01":
        assert ".assert" in caught.value.issues[0].path
    if case_id == "V02":
        assert ".retract" in caught.value.issues[0].path


def test_old_blanket_refusal_is_gone(tmp_path) -> None:
    try:
        load_model(write_model(tmp_path, "base"))
    except ModelValidationError as error:
        assert all(
            issue.rule_id != "semantic:derivation-operations-unsupported" for issue in error.issues
        )


def test_existing_role_claim_error_precedes_new_dynamic_boundary() -> None:
    doc = document("touch_positive")
    doc["fact_types"][2]["derivation_rule"]["body"][0]["bind"] = {}
    derivation_issues = [
        issue for issue in semantic_validate(doc) if issue.rule_id.startswith("semantic:derivation")
    ]
    assert derivation_issues[0].rule_id == "semantic:derivation-role-claim"


def test_existing_recursive_error_precedes_new_dynamic_boundary() -> None:

    doc = document("touch_positive")
    doc["fact_types"][2]["derivation_rule"]["body"][0]["fact_type"] = "final_eligible"
    derivation_issues = [
        issue for issue in semantic_validate(doc) if issue.rule_id.startswith("semantic:derivation")
    ]
    assert derivation_issues == []


def test_opaque_derived_fact_retains_legacy_effect_behavior() -> None:
    doc = document("one_stratum")
    eligible = next(row for row in doc["fact_types"] if row["id"] == "eligible")
    eligible["derivation"] = "derived"
    eligible["derivation_rule"] = "opaque legacy rule"
    doc["operations"][0]["effects"] = [
        {"assert": {"fact_type": "eligible", "bind": {"item": "$item"}}}
    ]
    assert all(
        issue.rule_id != "semantic:derivation-effect-on-derived" for issue in semantic_validate(doc)
    )
