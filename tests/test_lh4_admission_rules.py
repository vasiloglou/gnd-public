"""LH4: admission rules as data, the status policy-refused, and max_targets as an argument."""
from __future__ import annotations

import hashlib
import json
import time

import pytest
from test_lh3_admission_shape import (
    PACKAGED,
    ROWS,
    SHAPE,
    VERDICTS,
    _admit,
    _admitted,
    _case,
    _refuses,
    _wide,
)

from gnd.artifacts import canonical_json_bytes
from gnd.examples.literature import assertion_admission as admission

POLARITY = {"id": "claim_polarity", "reading": "{Claim} has polarity {Note}",
            "roles": [{"role_name": "claim", "object_type": "claim"}, {"role_name": "polarity", "object_type": "note"}]}
ROWS_P = {**ROWS, "claim_polarity": [{"claim": "c1", "polarity": "asserts"}, {"claim": "c2", "polarity": "asserts"},
                                     {"claim": "c2", "polarity": "negates"}, {"claim": "c4", "polarity": "asserts"}]}
RULES_A = {"format": admission.RULES_FORMAT, "requirements": [
    {"id": "positive", "fact_type": "claim_polarity", "role": "polarity", "admissible": ["asserts"],
     "reasons": [{"value": "negates", "reason": "negated"}]}]}
RULES_B = {"format": admission.RULES_FORMAT, "requirements": [
    {"id": "named-actor", "fact_type": "claim_actor", "role": "actor", "admissible": ["Quartz", "Slate"],
     "reasons": []}]}


def _sha(raw):
    return hashlib.sha256(raw).hexdigest()


def _add_polarity(model):
    model["fact_types"].append(POLARITY)


def _polar(tmp_path, name="case", verdicts=None):
    return _case(tmp_path, rows=ROWS_P, name=name, verdicts=verdicts, edit_model=_add_polarity)


def _stage(record, stage="admission-rules"):
    return {row["assertion"]: (row["status"], row["reason"]) for row in record["stages"][stage]}


def _packaged(out, **kwargs):
    return admission.admit(PACKAGED / "model.orm.yaml", PACKAGED / "raw.population.json", PACKAGED / "policy.json",
                           PACKAGED / "receipts.json", PACKAGED / "evidence", out, **kwargs)


def test_t1_two_rules_files_admit_two_sets(tmp_path):
    root = _polar(tmp_path)
    _, out_a = _admit(root, root.parent / "a", shape=SHAPE, rules=RULES_A)
    _, out_b = _admit(root, root.parent / "b", shape=SHAPE, rules=RULES_B)
    admitted_a = {row["claim"] for row in _admitted(out_a)["facts"]["claim_passage"]}
    admitted_b = {row["claim"] for row in _admitted(out_b)["facts"]["claim_passage"]}
    assert admitted_a == {"c1"}
    assert admitted_b == {"c1", "c3"}


def test_t2_policy_refused_is_distinct_from_fail(tmp_path):
    record, _ = _admit(_polar(tmp_path), shape=SHAPE, rules=RULES_A)
    assert _stage(record) == {"c1": ("pass", None), "c2": ("policy-refused", "negated"),
                              "c3": ("policy-refused", "positive"), "c4": ("fail", "rejected")}


def test_t3_every_row_must_be_admissible_and_one_must_exist(tmp_path):
    record, out = _admit(_polar(tmp_path), shape=SHAPE, rules=RULES_A)
    statuses = _stage(record)
    assert statuses["c2"][0] == "policy-refused" and statuses["c3"][0] == "policy-refused"
    assert {row["claim"] for row in _admitted(out)["facts"]["claim_polarity"]} == {"c1"}


@pytest.mark.parametrize("value", [3, 1025, 0, True])
def test_t4_max_targets(tmp_path, value):
    out = tmp_path / "out"
    _refuses(lambda: _admit(_polar(tmp_path), out, shape=SHAPE, max_targets=value), "input:max-targets")
    assert not out.exists()


def test_t4_max_targets_at_the_policy_size_admits(tmp_path):
    record, _ = _admit(_polar(tmp_path), shape=SHAPE, max_targets=len(VERDICTS))
    assert record["max_targets"] == len(VERDICTS)


def _requirement(**changes):
    return {**RULES_A["requirements"][0], **changes}


RULE_DEFECTS = {
    "not-object": ([], "rules:invalid"),
    "key-missing": ({"format": admission.RULES_FORMAT}, "rules:invalid"),
    "extra-key": ({**RULES_A, "mode": "any"}, "rules:invalid"),
    "duplicate-id": ({"format": admission.RULES_FORMAT, "requirements": [_requirement(), _requirement()]},
                     "rules:invalid"),
    "empty-admissible": ({"format": admission.RULES_FORMAT, "requirements": [_requirement(admissible=[])]},
                         "rules:invalid"),
    "reason-for-admissible": ({"format": admission.RULES_FORMAT, "requirements": [
        _requirement(reasons=[{"value": "asserts", "reason": "odd"}])]}, "rules:invalid"),
    "too-many": ({"format": admission.RULES_FORMAT, "requirements": [
        _requirement(id=f"r{index}") for index in range(65)]}, "rules:invalid"),
    "unknown-fact-type": ({"format": admission.RULES_FORMAT, "requirements": [
        _requirement(fact_type="claim_author")]}, "rules:unknown-fact-type"),
    "not-attached": ({"format": admission.RULES_FORMAT, "requirements": [
        _requirement(fact_type="quantity_value", role="value")]}, "rules:unknown-fact-type"),
    "unknown-role": ({"format": admission.RULES_FORMAT, "requirements": [_requirement(role="tone")]},
                     "rules:unknown-role"),
}


@pytest.mark.parametrize("case", sorted(RULE_DEFECTS))
def test_t5_a_bad_rule_refuses_before_the_judgment_route(tmp_path, monkeypatch, case):
    rules, reason = RULE_DEFECTS[case]
    root = _polar(tmp_path)
    monkeypatch.setattr(admission, "_judgments", lambda *_: pytest.fail("ran the judgment route"))
    out = tmp_path / "out"
    _refuses(lambda: _admit(root, out, shape=SHAPE, rules=rules), reason)
    assert not out.exists()


def test_t5_the_packaged_shape_names_assertion_statement_only(tmp_path, monkeypatch):
    rules = {"format": admission.RULES_FORMAT, "requirements": [
        {"id": "work", "fact_type": admission.WORK, "role": "work", "admissible": ["x"], "reasons": []}]}
    monkeypatch.setattr(admission, "_judgments", lambda *_: pytest.fail("ran the judgment route"))
    out = tmp_path / "out"
    _refuses(lambda: _packaged(out, rules=rules), "rules:unknown-fact-type")
    assert not out.exists()


def test_t6_the_default_rules_are_the_packaged_comparison(tmp_path):
    first = _packaged(tmp_path / "one")
    second = _packaged(tmp_path / "two", rules=admission.DEFAULT_RULES)
    assert first["schema"] == admission.SCHEMA and second["schema"] == admission.SHAPED_SCHEMA
    old = {row["index"]: row for row in first["stages"]["positive-own-findings"]}
    new = {row["index"]: row for row in second["stages"]["positive-own-findings"]}
    assert [old[index]["reason"] for index in sorted(old)] == [new[index]["reason"] for index in sorted(new)]
    supported = {row["index"] for row in first["stages"]["semantic-support"] if row["status"] == "pass"}
    for index, row in old.items():
        expected = "policy-refused" if row["status"] == "fail" and index in supported else row["status"]
        assert new[index]["status"] == expected
    assert [new[index]["status"] for index in (3, 4, 5, 6)] == ["policy-refused"] * 4
    assert (tmp_path / "one/admitted.population.json").read_bytes() == (
        tmp_path / "two/admitted.population.json").read_bytes()


def test_t7_a_v2_record_binds_every_setting(tmp_path):
    root = _polar(tmp_path)
    base, _ = _admit(root, root.parent / "base", shape=SHAPE, rules=RULES_A)
    assert base["shape"] == "caller" and base["shape_sha256"] == _sha(canonical_json_bytes(SHAPE))
    assert base["rules_sha256"] == _sha(canonical_json_bytes(RULES_A))
    assert base["max_targets"] == admission.MAX_TARGETS and base["max_rows"] == admission.MAX_ROWS
    changed = {
        "shape_sha256": {"shape": {**SHAPE, "follow": []}},
        "rules_sha256": {"rules": RULES_B},
        "max_targets": {"max_targets": len(VERDICTS)},
        "max_rows": {"max_rows": 1000},
    }
    for field, change in changed.items():
        arguments = {"shape": SHAPE, "rules": RULES_A, **change}
        record, _ = _admit(root, root.parent / field, **arguments)
        assert record[field] != base[field], field
    rules_only = _packaged(tmp_path / "packaged", rules=admission.DEFAULT_RULES)
    assert (rules_only["shape"], rules_only["shape_sha256"], rules_only["max_rows"]) == ("packaged", None, None)


def test_t8_sixty_four_requirements_at_the_row_ceiling(tmp_path):
    count, per = 1024, 61
    rows = _wide(count, per)
    verdicts = {("claim_passage", index): "approve" for index in range(count)}
    root = _case(tmp_path, rows=rows, verdicts=verdicts)
    actors = [f"a{extra}" for extra in range(per)]
    rules = {"format": admission.RULES_FORMAT, "requirements": [
        {"id": f"r{number}", "fact_type": "claim_actor", "role": "actor", "admissible": actors, "reasons": []}
        for number in range(admission.MAX_REQUIREMENTS)]}
    started = time.monotonic()
    record, _ = _admit(root, shape=SHAPE, rules=rules, max_rows=admission.MAX_ROWS_CEILING)
    assert time.monotonic() - started < 60
    assert all(row["status"] == "pass" for row in record["stages"]["admission-rules"])
    assert json.dumps(record["stages"]).count("policy-refused") == 0


@pytest.mark.parametrize("kind", ["object", "list", "infinity", "nan"])
@pytest.mark.parametrize("where", ["admissible", "reason-value"])
def test_r1_a_rule_value_must_be_a_json_scalar(tmp_path, monkeypatch, kind, where):
    value = {"object": {}, "list": [], "infinity": float("inf"), "nan": float("nan")}[kind]
    if where == "admissible":
        requirement = _requirement(admissible=[value])
    else:
        requirement = _requirement(reasons=[{"value": value, "reason": "odd"}])
    rules = {"format": admission.RULES_FORMAT, "requirements": [requirement]}
    monkeypatch.setattr(admission, "_judgments", lambda *_: pytest.fail("ran the judgment route"))
    out = tmp_path / "out"
    _refuses(lambda: _admit(_polar(tmp_path), out, shape=SHAPE, rules=rules), "rules:invalid")
    assert not out.exists()


def test_r2_reasons_are_optional(tmp_path):
    requirement = {key: value for key, value in _requirement().items() if key != "reasons"}
    rules = {"format": admission.RULES_FORMAT, "requirements": [requirement]}
    record, _ = _admit(_polar(tmp_path), shape=SHAPE, rules=rules)
    assert _stage(record)["c2"] == ("policy-refused", "positive")
