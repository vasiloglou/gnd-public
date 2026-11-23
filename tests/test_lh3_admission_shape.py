"""LH3: admission over a caller-named assertion entity, identified by its own handle."""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

import pytest

from gnd.artifacts import canonical_json_bytes
from gnd.examples.literature import assertion_admission as admission
from gnd.examples.literature.assurance_report import Refusal
from gnd.judgments import judgment_fact_digest, judgment_receipt_digest

FIXTURE = Path(__file__).parent / "fixtures/lh3-admission"
PACKAGED = Path(__file__).resolve().parents[1] / "src/gnd/examples/literature/assertions"
SHAPE = {"format": admission.SHAPE_FORMAT, "assertion": "claim", "follow": ["quantity"]}
H18 = {
    "admitted.population.json": "6e45b93d",
    "raw.population.json": "ea96584c",
    "judgment-report.json": "3726a424",
    "admission.json": "6d262018",
}
ROWS = {
    "claim_passage": [{"claim": "c1", "passage": "p1"}, {"claim": "c2", "passage": "p1"},
                      {"claim": "c3", "passage": "p2"}, {"claim": "c4", "passage": "p2"}],
    "claim_actor": [{"claim": "c1", "actor": "Quartz"}, {"claim": "c1", "actor": "Slate"},
                    {"claim": "c3", "actor": "Quartz"}, {"claim": "c4", "actor": "Basalt"}],
    "claim_object": [{"claim": "c2", "object": "error rate"}, {"claim": "c3", "object": "noise"}],
    "claim_condition": [{"claim": "c2", "condition": "low noise"}, {"claim": "c2", "condition": "trial A"},
                        {"claim": "c2", "condition": "none"}],
    "claim_quantity": [{"claim": "c1", "quantity": "q1"}, {"claim": "c3", "quantity": "q2"},
                       {"claim": "c4", "quantity": "q1"}],
    "claim_paper": [{"claim": "c1", "paper": "w1"}],
    "claim_supports": [{"claim": "c1", "other": "c2"}, {"claim": "c1", "other": "c4"}],
    "quantity_value": [{"quantity": "q1", "value": "12"}, {"quantity": "q2", "value": "3"}],
    "quantity_unit": [{"quantity": "q1", "unit": "percent"}, {"quantity": "q2", "unit": "dB"}],
    "quantity_source": [{"quantity": "q1", "claim": "c4"}, {"quantity": "q2", "claim": "c3"}],
    "paper_title": [{"paper": "w1", "title": "Quartz study"}],
}
VERDICTS = {("claim_passage", 0): "approve", ("claim_passage", 1): "approve",
            ("claim_passage", 2): "approve", ("claim_passage", 3): "reject"}


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _case(tmp_path, *, rows=None, verdicts=None, name="case", model="claims.orm.json", edit_model=None):
    """A caller's admission inputs: model and include, raw population, policy, saved receipts, evidence."""
    root = tmp_path / name
    root.mkdir()
    for file in ("claims.orm.json", "terms.orm.json"):
        shutil.copyfile(FIXTURE / file, root / file)
    if edit_model is not None:
        document = json.loads((root / "claims.orm.json").read_bytes())
        edit_model(document)
        (root / "claims.orm.json").write_bytes(canonical_json_bytes(document))
    shutil.copytree(FIXTURE / "evidence", root / "evidence")
    rows = ROWS if rows is None else rows
    verdicts = VERDICTS if verdicts is None else verdicts
    model_raw = (root / model).read_bytes()
    population = {"population": {"covers": sorted(rows), "model": admission.MODEL,
                                 "model_id": "urn:gnd-test:lh3-claims@1", "source": "fixture"},
                  "instances": {}, "facts": rows}
    raw = canonical_json_bytes(population)
    (root / "raw.population.json").write_bytes(raw)
    evidence = (root / "evidence/passages.txt").read_bytes()
    receipts = []
    for number, ((fact_type, index), verdict) in enumerate(verdicts.items()):
        receipts.append({
            "receipt_id": f"opinion-{number:04d}", "judge_id": "corpus-author", "verdict": verdict,
            "trust": "consumer-pinned", "external_evidence": None,
            "subject": {"model_sha256": _sha(model_raw), "population_sha256": _sha(raw), "reference_identity": None,
                        "fact_type": fact_type, "index": index,
                        "fact_sha256": judgment_fact_digest(fact_type, index, rows[fact_type][index])},
            "sources": [{"path": "passages.txt", "sha256": _sha(evidence),
                         "quote": {"start": 0, "end": 10, "sha256": _sha(evidence[:10])}}],
        })
    policy = json.loads((PACKAGED / "policy.json").read_bytes())
    policy["targets"] = [{"fact_type": fact_type, "index": index} for fact_type, index in verdicts]
    policy["trusted_receipts"] = [{"judge_id": "corpus-author", "receipt_sha256": judgment_receipt_digest(item)}
                                  for item in receipts]
    (root / "policy.json").write_bytes(canonical_json_bytes(policy))
    (root / "receipts.json").write_bytes(canonical_json_bytes({"schema_version": 1, "receipts": receipts}))
    return root


def _admit(root, out=None, **kwargs):
    out = out or root.parent / f"{root.name}-out"
    record = admission.admit(root / "claims.orm.json", root / "raw.population.json", root / "policy.json",
                             root / "receipts.json", root / "evidence", out, **kwargs)
    return record, out


def _admitted(out):
    return json.loads((out / "admitted.population.json").read_bytes())


def _refuses(call, reason):
    with pytest.raises(Refusal) as caught:
        call()
    assert caught.value.reason == reason


@pytest.fixture(scope="module")
def shaped(tmp_path_factory):
    root = _case(tmp_path_factory.mktemp("lh3"))
    record, out = _admit(root, shape=SHAPE)
    return root, record, out


def test_t1_every_attached_and_followed_row_of_an_admitted_claim(shaped):
    root, record, out = shaped
    facts = _admitted(out)["facts"]
    assert facts["claim_passage"] == ROWS["claim_passage"][:3]
    assert facts["claim_actor"] == ROWS["claim_actor"][:3]
    assert facts["claim_object"] == ROWS["claim_object"]
    assert facts["claim_condition"] == ROWS["claim_condition"]
    assert facts["claim_quantity"] == ROWS["claim_quantity"][:2]
    assert facts["claim_paper"] == ROWS["claim_paper"]
    assert facts["quantity_value"] == ROWS["quantity_value"]
    assert facts["quantity_unit"] == ROWS["quantity_unit"]
    assert all("c4" not in json.dumps(rows) for rows in facts.values())
    assert record["schema"] == admission.SHAPED_SCHEMA
    assert record["shape_sha256"] == _sha(canonical_json_bytes(SHAPE))
    assert {row["assertion"]: row["status"] for row in record["stages"]["semantic-support"]} == {
        "c1": "pass", "c2": "pass", "c3": "pass", "c4": "fail"}
    check = root.parent / "check"
    check.mkdir()
    for file in ("terms.orm.json",):
        shutil.copyfile(root / file, check / file)
    shutil.copyfile(root / "claims.orm.json", check / admission.MODEL)
    shutil.copyfile(out / "admitted.population.json", check / "admitted.population.json")
    done = subprocess.run([sys.executable, "-m", "gnd", "check", admission.MODEL, "admitted.population.json"],
                          cwd=check, capture_output=True, check=False)
    assert done.returncode == 0, done.stdout.decode()[-600:]


def test_t1_covers_lists_attached_and_followed_fact_types(shaped):
    _, _, out = shaped
    covers = _admitted(out)["population"]["covers"]
    assert set(covers) == set(ROWS) - {"paper_title"}
    assert "paper_title" not in _admitted(out)["facts"]


def test_t2_an_entity_that_objectifies_a_fact_type_refuses(tmp_path):
    out = tmp_path / "out"
    shape = {"format": admission.SHAPE_FORMAT, "assertion": "assertion", "follow": []}
    _refuses(lambda: admission.admit(PACKAGED / "model.orm.yaml", PACKAGED / "raw.population.json",
                                     PACKAGED / "policy.json", PACKAGED / "receipts.json", PACKAGED / "evidence",
                                     out, shape=shape), "shape:objectified-assertion")
    assert not out.exists()


def test_t3_support_is_every_target_admitted_and_at_least_one(tmp_path):
    verdicts = {**VERDICTS, ("claim_actor", 1): "reject"}
    del verdicts[("claim_passage", 2)]
    record, out = _admit(_case(tmp_path, verdicts=verdicts), shape=SHAPE)
    reasons = {row["assertion"]: row["reason"] for row in record["stages"]["semantic-support"]}
    assert reasons == {"c1": "rejected", "c2": None, "c3": "missing", "c4": "rejected"}
    facts = _admitted(out)["facts"]
    assert facts["claim_condition"] == ROWS["claim_condition"]
    assert facts["claim_passage"] == [ROWS["claim_passage"][1]]


def test_t4_a_row_between_two_claims_needs_both_admitted(shaped):
    _, _, out = shaped
    assert _admitted(out)["facts"]["claim_supports"] == [{"claim": "c1", "other": "c2"}]


def test_t5_an_include_root_admits_and_binds_its_include(shaped, tmp_path):
    root, record, _ = shaped
    assert record["includes"] == {"terms.orm.json": _sha((root / "terms.orm.json").read_bytes())}
    edited = _case(tmp_path)
    path = edited / "terms.orm.json"
    path.write_bytes(path.read_bytes() + b"\n")
    out = tmp_path / "out"
    _refuses(lambda: _admit(edited, out, shape=SHAPE), "input:model")
    assert not out.exists()


def _shape(**changes):
    return {**SHAPE, **changes}


REFUSALS = {
    "shape-not-object": (["claim"], "shape:invalid"),
    "shape-key-missing": ({"format": admission.SHAPE_FORMAT, "assertion": "claim"}, "shape:invalid"),
    "shape-extra-key": (_shape(stop=True), "shape:invalid"),
    "unknown-assertion": (_shape(assertion="author"), "shape:unknown-assertion"),
    "value-type-assertion": (_shape(assertion="note"), "shape:unknown-assertion"),
    "unknown-follow": (_shape(follow=["author"]), "shape:unknown-follow"),
    "duplicate-follow": (_shape(follow=["quantity", "quantity"]), "shape:invalid"),
    "no-attached-facts": (_shape(assertion="venue", follow=[]), "shape:no-attached-facts"),
}


@pytest.mark.parametrize("case", sorted(REFUSALS))
def test_t6_a_shape_refusal_publishes_nothing(tmp_path, case):
    shape, reason = REFUSALS[case]
    root = _case(tmp_path)
    out = tmp_path / "out"
    _refuses(lambda: _admit(root, out, shape=shape), reason)
    assert not out.exists()


def test_t6_a_target_outside_the_shape_refuses(tmp_path):
    verdicts = {**VERDICTS, ("quantity_value", 0): "approve"}
    out = tmp_path / "out"
    _refuses(lambda: _admit(_case(tmp_path, verdicts=verdicts), out, shape=SHAPE), "judgments:target-outside-shape")
    assert not out.exists()


def test_t6_an_include_path_outside_the_root_refuses(tmp_path):
    root = _case(tmp_path)
    model = json.loads((root / "claims.orm.json").read_bytes())
    model["includes"][0]["path"] = "../terms.orm.json"
    (root / "claims.orm.json").write_bytes(canonical_json_bytes(model))
    out = tmp_path / "out"
    _refuses(lambda: _admit(root, out, shape=SHAPE), "input:include-path")
    assert not out.exists()


@pytest.mark.parametrize("value", [0, 65537, True])
def test_t6_max_rows_out_of_range_refuses(tmp_path, value):
    out = tmp_path / "out"
    _refuses(lambda: _admit(_case(tmp_path), out, shape=SHAPE, max_rows=value), "input:max-rows")
    assert not out.exists()


def test_t6_max_rows_without_a_shape_refuses(tmp_path):
    out = tmp_path / "out"
    _refuses(lambda: admission.admit(PACKAGED / "model.orm.yaml", PACKAGED / "raw.population.json",
                                     PACKAGED / "policy.json", PACKAGED / "receipts.json", PACKAGED / "evidence",
                                     out, max_rows=100), "input:max-rows")
    assert not out.exists()


def test_t7_the_value_none_is_ordinary(shaped):
    _, _, out = shaped
    assert {"claim": "c2", "condition": "none"} in _admitted(out)["facts"]["claim_condition"]


def test_t8_the_packaged_call_keeps_its_bytes(tmp_path):
    out = tmp_path / "packaged"
    record = admission.admit(PACKAGED / "model.orm.yaml", PACKAGED / "raw.population.json",
                             PACKAGED / "policy.json", PACKAGED / "receipts.json", PACKAGED / "evidence", out)
    assert record["schema"] == admission.SCHEMA and "shape_sha256" not in record
    for name, prefix in H18.items():
        assert _sha((out / name).read_bytes()).startswith(prefix), name
    reasons = {row["index"]: row["reason"] for row in record["stages"]["positive-own-findings"]}
    assert [reasons[index] for index in (3, 4, 5, 6)] == ["negated", "baseline-comparison", "speculation",
                                                           "cites-other-work"]


def _wide(count, rows_per_claim):
    rows = {name: [] for name in ROWS}
    for number in range(count):
        claim = f"c{number}"
        rows["claim_passage"].append({"claim": claim, "passage": "p"})
        rows["claim_quantity"].append({"claim": claim, "quantity": f"q{number}"})
        rows["quantity_value"].append({"quantity": f"q{number}", "value": str(number)})
        for extra in range(rows_per_claim):
            rows["claim_actor"].append({"claim": claim, "actor": f"a{extra}"})
    return rows


def test_t9_the_row_ceiling_in_time_and_one_over_refuses(tmp_path):
    count, per = 1024, 61
    rows = _wide(count, per)
    total = sum(len(value) for name, value in rows.items() if name != "paper_title")
    assert total == admission.MAX_ROWS_CEILING
    verdicts = {("claim_passage", index): "approve" for index in range(count)}
    root = _case(tmp_path, rows=rows, verdicts=verdicts)
    started = time.monotonic()
    record, out = _admit(root, shape=SHAPE, max_rows=total)
    assert time.monotonic() - started < 60
    assert len(_admitted(out)["facts"]["claim_actor"]) == count * per
    assert all(row["status"] == "pass" for row in record["stages"]["semantic-support"])
    second = tmp_path / "again"
    _refuses(lambda: _admit(root, second, shape=SHAPE, max_rows=total - 1), "input:row-cap")
    assert not second.exists()


def test_t10_shared_and_unlisted_entities(shaped):
    _, _, out = shaped
    facts = _admitted(out)["facts"]
    assert facts["quantity_value"].count({"quantity": "q1", "value": "12"}) == 1
    assert {"claim": "c4", "quantity": "q1"} not in facts["claim_quantity"]
    assert facts["quantity_source"] == [{"quantity": "q2", "claim": "c3"}]
    assert "paper_title" not in facts


def test_t10_with_an_empty_follow_list_nothing_is_followed(tmp_path):
    record, out = _admit(_case(tmp_path), shape=_shape(follow=[]))
    facts = _admitted(out)["facts"]
    assert "quantity_value" not in facts and "quantity_unit" not in facts
    assert facts["claim_quantity"] == ROWS["claim_quantity"][:2]
    assert record["schema"] == admission.SHAPED_SCHEMA


def _model(*fact_types):
    return {"object_types": [{"id": "claim", "kind": "entity"}, {"id": "passage", "kind": "entity"},
                             {"id": "note", "kind": "value"}],
            "fact_types": [{"id": name, "roles": [{"role_name": role, "object_type": kind} for role, kind in roles]}
                           for name, roles in fact_types]}


def _target(fact_type, index, admitted=True):
    return {"fact_type": fact_type, "index": index, "admitted": admitted,
            "judgments": [{"verdict": "approve" if admitted else "reject"}]}


CLAIM_SEEN = ("claim_seen", [("claim", "claim"), ("passage", "passage")])
LONE_SHAPE = {"format": admission.SHAPE_FORMAT, "assertion": "claim", "follow": []}


def test_r1_a_boolean_handle_is_not_a_number(tmp_path):
    subject = {"population": {}, "facts": {"claim_seen": [{"claim": True, "passage": "p"},
                                                           {"claim": 1, "passage": "p"}]}}
    population, stages = admission.project_shaped(subject, [_target("claim_seen", 0)], _model(CLAIM_SEEN),
                                                   LONE_SHAPE)
    assert population["facts"]["claim_seen"] == [{"claim": True, "passage": "p"}]
    assert [row["status"] for row in stages["semantic-support"]] == ["pass", "fail"]


def test_r1_one_and_one_point_zero_are_one_number():
    subject = {"population": {}, "facts": {"claim_seen": [{"claim": 1, "passage": "p"},
                                                           {"claim": 1.0, "passage": "q"}]}}
    population, stages = admission.project_shaped(subject, [_target("claim_seen", 0)], _model(CLAIM_SEEN),
                                                   LONE_SHAPE)
    assert len(population["facts"]["claim_seen"]) == 2 and len(stages["semantic-support"]) == 1


@pytest.mark.parametrize("includes", [1, True, [1], [{"path": 3}]])
def test_r2_a_malformed_include_list_refuses(includes):
    raw = canonical_json_bytes({"version": 5, "object_types": [], "fact_types": [], "includes": includes})
    _refuses(lambda: admission._include_paths(raw), "input:include-path")


def test_r2_a_missing_include_refuses(tmp_path):
    root = _case(tmp_path)
    (root / "terms.orm.json").unlink()
    out = tmp_path / "out"
    _refuses(lambda: _admit(root, out, shape=SHAPE), "input:include-read")
    assert not out.exists()


def test_r3_an_opaque_value_is_an_ordinary_value():
    subject = {"format_version": 2, "population": {}, "facts": {
        "claim_seen": [{"claim": "c1", "passage": "p"}],
        "claim_note": [{"claim": "c1", "note": {"$opaque": "unreadable-note"}}]}}
    model = _model(CLAIM_SEEN, ("claim_note", [("claim", "claim"), ("note", "note")]))
    population, _ = admission.project_shaped(subject, [_target("claim_seen", 0)], model, LONE_SHAPE)
    assert population["facts"]["claim_note"] == subject["facts"]["claim_note"]


def test_r4_covers_is_linear_in_the_fact_types():
    count = 40_000
    names = [f"seen_{index}" for index in range(count)]
    model = _model(*[(name, [("claim", "claim")]) for name in names])
    subject = {"population": {}, "facts": {name: [{"claim": "c1"}] for name in names}}
    started = time.monotonic()
    admission.project_shaped(subject, [_target(names[0], 0)], model, LONE_SHAPE, max_rows=65536)
    assert time.monotonic() - started < 1.5


@pytest.mark.parametrize("missing", ["claims.orm.json", "raw.population.json", "policy.json", "receipts.json"])
def test_r5_a_missing_primary_input_refuses_without_its_path(tmp_path, missing):
    root = _case(tmp_path)
    (root / missing).unlink()
    out = tmp_path / "out"
    _refuses(lambda: _admit(root, out, shape=SHAPE), "input:read")
    assert not out.exists()
