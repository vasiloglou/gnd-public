"""Public COUNT membership controls with an independently authored answer roster."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

FIXTURE = Path(__file__).parent / "fixtures/count-certificates"
ANSWER = json.loads((FIXTURE / "expected.json").read_bytes())


def _read(file):
    return json.loads(file.read_bytes())


def _write(file, data):
    file.write_text(json.dumps(data))


def _command(folder, *arguments):
    process = subprocess.run((sys.executable, "-m", "gnd", *arguments), cwd=folder,
                             capture_output=True, check=False)
    return process.returncode, process.stdout, process.stderr


@pytest.fixture
def case(tmp_path):
    shutil.copytree(FIXTURE, tmp_path, dirs_exist_ok=True)
    return tmp_path


def _produce(case, request="group.json", output="certificate.json"):
    return _command(case, "witness-count", "model.orm.yaml", "population.json", "--request", request,
                    "--raw", "--out", output)


def _replay(case, certificate="certificate.json", request="group.json"):
    return _command(case, "replay-count", "model.orm.yaml", "population.json", certificate,
                    "--request", request, "--raw")


def _certify(case, request="group.json"):
    code, out, err = _produce(case, request)
    assert code == 0, (out, err)
    return _read(case / "certificate.json")


@pytest.mark.parametrize(("request_file", "answer"), (("group.json", "nonempty"), ("empty-group.json", "empty")))
def test_exact_membership_and_public_replay(case, request_file, answer):
    before = _command(case, "check", "model.orm.yaml", "population.json", "--format", "json")
    proof = _certify(case, request_file)
    expected = ANSWER[answer]
    assert proof["kind"] == "count-membership"
    assert proof["status"] == expected["status"]
    assert proof["count"] == expected["count"]
    assert [row["fact_index"] for row in proof["members"]] == expected["origins"]
    assert [row["over"][0]["value"] for row in proof["members"]] == expected["members"]
    assert _replay(case, request=request_file)[0] == 0
    assert before[0] == 0
    assert _command(case, "check", "model.orm.yaml", "population.json", "--format", "json") == before


@pytest.mark.parametrize("edit", ("omitted-and-recounted", "duplicated-and-recounted", "unrelated-index",
                                  "swapped-order", "substituted-of", "alternate-representative",
                                  "false-empty", "extra-member", "count-only", "wrong-type"))
def test_well_formed_membership_forgery_refuses(case, edit):
    proof = _certify(case)
    members = proof["members"]
    if edit == "omitted-and-recounted":
        members.pop()
    elif edit == "duplicated-and-recounted":
        members.insert(0, members[0])
    elif edit == "unrelated-index":
        members[0]["fact_index"] = 1
    elif edit == "swapped-order":
        members.reverse()
    elif edit == "alternate-representative":
        members[1]["fact_index"] = 3
    elif edit == "false-empty":
        members.clear()
        proof["status"] = "empty-group"
    elif edit == "extra-member":
        members.append({**members[0], "fact_index": 1, "over": [{"primitive": "String", "value": "gamma"}]})
    elif edit == "wrong-type":
        members[0]["over"][0] = {"primitive": "Integer", "value": 1}
    elif edit == "substituted-of":
        members[0]["of"]["value"] = "forged"
    proof["count"] = len(members) + (edit == "count-only")
    _write(case / "certificate.json", proof)
    assert _replay(case)[0] == ANSWER["forged_exit"]


@pytest.mark.parametrize("edit", ("model", "population", "request"))
def test_edited_inputs_precede_forged_membership(case, edit):
    proof = _certify(case)
    proof["members"][0]["fact_index"] = 1
    _write(case / "certificate.json", proof)
    if edit == "model":
        path = case / "model.orm.yaml"
        text = path.read_text()
        path.write_text(text.replace("has sample", "sees sample", 1).replace(
            "reports {Method}", "records {Method}", 1))
    elif edit == "population":
        path = case / "population.json"
        data = _read(path)
        data["facts"]["observation"][1]["source"] = "unrelated-change"
        _write(path, data)
    else:
        path = case / "group.json"
        data = _read(path)
        data["group"]["group"]["value"] = "other"
        _write(path, data)
    code, out, err = _replay(case)
    assert code == ANSWER["stale_exit"], (out, err)
    assert json.loads(out)["reason"] == "binding-stale"


def test_missing_body_coverage_cannot_prove_empty(case):
    path = case / "population.json"
    value = _read(path)
    value["population"]["covers"].remove("observation")
    _write(path, value)
    code, _, _ = _produce(case, "empty-group.json")
    assert code == ANSWER["unsupported_exit"]
    assert not (case / "certificate.json").exists()


def test_forged_zero_aggregate_row_remains_unsound(case):
    path = case / "population.json"
    value = _read(path)
    value["facts"]["method_count"].append({"group": "empty", "count": 0})
    _write(path, value)
    out = _command(case, "check", "model.orm.yaml", "population.json", "--format", "json")
    assert out[0] == 1
    assert any(row["kind"] == "derived-extension-unsound"
               for item in json.loads(out[1])["derivations"] for row in item["findings"])


def test_individual_base_occurrence_still_witnesses_and_replays(case):
    assert _command(case, "witness", "model.orm.yaml", "population.json", "--targets", "member-targets.json",
                    "--raw", "--out", "member.json")[0] == 0
    assert _command(case, "replay", "model.orm.yaml", "population.json", "member.json", "--raw")[0] == 0


@pytest.mark.parametrize("request_file", ("group.json", "empty-group.json"))
def test_declared_coverage_is_authenticated_for_both_paths(case, request_file):
    _certify(case, request_file)
    path = case / "population.json"
    value = _read(path)
    value["population"]["covers"].remove("observation")
    _write(path, value)
    code, out, _ = _replay(case, request=request_file)
    assert code == 3 and json.loads(out)["reason"] == "binding-stale"
    assert _produce(case, request_file, "uncertified.json")[0] == 2


@pytest.mark.parametrize("defect", ("missing", "extra", "wrong-primitive"))
def test_bad_group_shape_is_never_an_empty_proof(case, defect):
    path = case / "group.json"
    doc = _read(path)
    if defect == "missing":
        doc["group"] = {}
    elif defect == "extra":
        doc["group"]["bad"] = doc["group"]["group"]
    else:
        doc["group"]["group"] = {"primitive": "Integer", "value": 1}
    _write(path, doc)
    assert _produce(case)[0] == 3


def test_empty_covered_relation_and_edited_nonempty_snapshot(case):
    _certify(case, "empty-group.json")
    path = case / "population.json"
    prior = _read(path)
    row = {"group": "empty", "member": "new", "tag": "included", "source": "notes"}
    prior["facts"]["observation"].append(row)
    _write(path, prior)
    assert _replay(case, request="empty-group.json")[0] == 3
    prior["facts"]["observation"] = []
    prior["facts"]["method_count"] = []
    _write(path, prior)
    assert _produce(case, "empty-group.json", "truly-empty.json")[0] == 0
    assert _replay(case, "truly-empty.json", "empty-group.json")[0] == 0
