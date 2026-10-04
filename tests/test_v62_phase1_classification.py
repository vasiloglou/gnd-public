

from __future__ import annotations

import pytest
from support.v62_phase1_corpus import ANSWERS, CASES, document

from gnd import model as model_module


@pytest.mark.parametrize("case_id", [f"C{index:02d}" for index in range(1, 9)])
def test_classification_case(case_id: str) -> None:
    classify = model_module.derivation_classifications
    rows = classify(document(CASES[case_id]["variant"]))
    by_id = {row.fact_type: row for row in rows}
    row = by_id[CASES[case_id].get("fact_type", "final_eligible")]
    answer = ANSWERS[case_id]
    assert row.stability == answer["classification"]
    assert row.complete is True
    if row.stability == "dynamic":
        assert answer["dependency"] in row.shared_dependencies
        assert answer["operation"] in row.touching_operations


def test_classification_mutation_changes_c04_to_c05() -> None:
    classify = model_module.derivation_classifications
    dirty = {row.fact_type: row for row in classify(document("touch_positive"))}
    clean = {row.fact_type: row for row in classify(document("base"))}
    assert dirty["final_eligible"].stability == "dynamic"
    assert clean["final_eligible"].stability == "static"


def test_classification_is_total_on_hostile_collection_shapes() -> None:
    classify = model_module.derivation_classifications
    assert classify({"fact_types": 1, "operations": []}) == ()
    assert classify({"fact_types": [], "operations": 1}) == ()
    doc = document("one_stratum")
    doc["fact_types"][2]["id"] = None
    row = classify(doc)[0]
    assert row.stability == "dynamic"
    assert row.complete is False


@pytest.mark.parametrize(
    "effects",
    [
        1,
        None,
        [{"mutate": {"fact_type": "evidence"}}],
        [{"assert": {"fact_type": 7}}],
    ],
)
def test_classification_fails_closed_on_malformed_effects(effects) -> None:
    doc = document("base")
    if effects is None:
        doc["operations"][0].pop("effects")
    else:
        doc["operations"][0]["effects"] = effects
    rows = model_module.derivation_classifications(doc)
    assert rows
    assert all(row.stability == "dynamic" and row.complete is False for row in rows)


def test_classification_fails_closed_on_unknown_rule_keys() -> None:
    doc = document("base")
    doc["fact_types"][3]["derivation_rule"]["or"] = [{"fact_type": "ticket_status"}]
    rows = {row.fact_type: row for row in model_module.derivation_classifications(doc)}
    assert rows["final_eligible"].stability == "dynamic"
    assert rows["final_eligible"].complete is False


@pytest.mark.parametrize(
    "mutation",
    [
        lambda rule: rule.__setitem__("body", 1),
        lambda rule: rule.__setitem__("body", [1]),
        lambda rule: rule.pop("head"),
        lambda rule: rule.update({7: True, "aggregate": True}),
    ],
)
def test_classification_fails_closed_on_hostile_rule_shapes(mutation) -> None:
    doc = document("one_stratum")
    rule = doc["fact_types"][2]["derivation_rule"]
    mutation(rule)
    row = model_module.derivation_classifications(doc)[0]
    assert row.stability == "dynamic"
    assert row.complete is False
