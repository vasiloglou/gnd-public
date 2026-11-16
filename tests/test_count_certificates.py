"""Public COUNT membership controls with an independently authored answer roster."""
from __future__ import annotations

import json
import shutil
import stat
import subprocess
import sys
from dataclasses import replace
from pathlib import Path

import pytest
from ruamel.yaml import YAML

from gnd.artifacts import canonical_json_bytes, sha256_hex
from gnd.witness.types import DEFAULT_LIMITS

FIXTURE = Path(__file__).resolve().parents[1] / "src/gnd/examples/literature/count_fixture"
ANSWER = json.loads((Path(__file__).parent / "fixtures/count-certificates/expected.json").read_bytes())


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
    roster = _certify(case)
    assert _command(case, "witness", "model.orm.yaml", "population.json", "--targets", "member-targets.json",
                    "--raw", "--out", "member.json")[0] == 0
    [node] = _read(case / "member.json")["nodes"]
    assert node["origin"]["fact_index"] == roster["members"][0]["fact_index"]
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
    prior["population"]["covers"].remove("observation")
    _write(path, prior)
    assert _produce(case, "empty-group.json", "uncovered.json")[0] == 2


def test_all_fixture_groups_match_independent_aggregate_evaluation(case):
    from gnd.checker import structured_extension_facts
    from gnd.model import load_model
    from gnd.population import load_population
    from gnd.witness.count_producer import produce_count

    model_path = case / "model.orm.yaml"
    population_path = case / "population.json"
    request_path = case / "group.json"
    model = load_model(model_path)
    population = load_population(population_path, model=model)
    rows = structured_extension_facts(model, population)["method_count"]
    assert {row["group"]: row["count"] for row in rows} == {"flow": 2, "other": 1}
    request = _read(request_path)
    for row in rows:
        request["group"]["group"]["value"] = row["group"]
        _write(request_path, request)
        result = produce_count(model_path, population_path, request_path)
        assert result["exit_code"] == 0
        assert result["count"] == row["count"]
    _write(case / "aggregate-targets.json", {"version": 1, "targets": [{
        "fact_type": "method_count", "tuple": [{"primitive": "String", "value": "flow"},
                                               {"primitive": "Integer", "value": 2}]
    }]})
    assert _command(case, "witness", model_path.name, population_path.name,
                    "--targets", "aggregate-targets.json", "--raw")[0] == 2


def test_replay_runs_with_producer_and_evaluator_imports_blocked(case):
    assert _produce(case)[0] == 0
    code = """
import sys
from importlib.abc import MetaPathFinder

class Block(MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname in {"gnd.extensions", "gnd.witness.count_producer", "gnd.witness.producer"}:
            raise AssertionError(f"unexpected import: {fullname}")

sys.meta_path.insert(0, Block())
from gnd.witness.count_replay import replay_count
result = replay_count("model.orm.yaml", "population.json", "certificate.json", "group.json")
assert result["exit_code"] == 0, result
"""
    process = subprocess.run((sys.executable, "-c", code), cwd=case, capture_output=True, check=False)
    assert process.returncode == 0, process.stderr.decode()


@pytest.mark.parametrize("mutation", ("version", "extra", "embedded-group", "nested"))
def test_certificate_intake_precedes_model_reads(case, monkeypatch, mutation):
    from gnd.witness import count_replay

    proof = _certify(case)
    if mutation == "version":
        proof["version"] = 2
    elif mutation == "extra":
        proof["coverage"] = []
    elif mutation == "embedded-group":
        proof["request"]["group"]["group"]["value"] = "other"
    else:
        for _ in range(DEFAULT_LIMITS.container_depth + 1):
            proof = [proof]
    path = case / "certificate.json"
    _write(path, proof)
    if mutation == "embedded-group":
        code, output, _ = _replay(case)
        assert code == 3 and json.loads(output)["reason"] == "binding-stale"
    else:
        def unexpected_read(*_args):
            pytest.fail("certificate refusal must precede request and snapshot intake")

        monkeypatch.setattr(count_replay, "read_request", unexpected_read)
        assert count_replay.replay_count(None, None, path, None) == {"exit_code": 3, "reason": "input-invalid"}


def test_work_limits_apply_to_empty_scans_both_ways_and_input_intake(case):
    from gnd.witness.count_producer import produce_count
    from gnd.witness.count_replay import replay_count

    model = case / "model.orm.yaml"
    population = case / "population.json"
    request = case / "empty-group.json"
    certificate = case / "certificate.json"
    _certify(case, request.name)
    refusal = {"exit_code": 4, "reason": "work-limit"}
    for limits in (replace(DEFAULT_LIMITS, joins=3), replace(DEFAULT_LIMITS, binding_cells=27)):
        assert produce_count(model, population, request, limits=limits) == refusal
        assert replay_count(model, population, certificate, request, limits=limits) == refusal
    assert produce_count(model, population, case / "group.json",
                         limits=replace(DEFAULT_LIMITS, nodes=1)) == refusal
    limits = replace(DEFAULT_LIMITS, bytes=1400)
    assert model.stat().st_size < limits.bytes
    population.write_bytes(b" " * (limits.bytes + 1))
    assert replay_count(model, population, certificate, request, limits=limits) == refusal
    certificate.write_bytes(b" " * (limits.bytes + 1))
    assert replay_count(model, population, certificate, request, limits=limits) == {
        "exit_code": 3, "reason": "input-invalid"
    }


def test_projected_output_has_its_own_byte_limit(case):
    from gnd.witness.count_producer import produce_count

    path = case / "population.json"
    population = _read(path)
    population["facts"]["observation"] = [
        {"group": "flow", "member": "alpha", "tag": str(index), "source": "x"}
        for index in range(40)
    ]
    path.write_bytes(canonical_json_bytes(population))
    args = (case / "model.orm.yaml", path, case / "group.json")
    proof = produce_count(*args)["certificate"]
    assert proof["count"] == 40
    assert len(canonical_json_bytes(proof)) > path.stat().st_size
    assert produce_count(*args, limits=replace(DEFAULT_LIMITS, bytes=path.stat().st_size)) == {
        "exit_code": 4, "reason": "work-limit"
    }


def test_changed_rule_binding_and_rebound_invalid_proof(case):
    proof = _certify(case)
    model = case / "model.orm.yaml"
    model.write_text(model.read_text().replace('of: "$tag"', 'of: "$source"'))
    stale = _replay(case)
    assert stale[0] == 3 and json.loads(stale[1])["reason"] == "binding-stale"
    assert _produce(case, output="new.json")[0] == 0
    proof["binding"]["model_sha256"] = sha256_hex(model.read_bytes())
    _write(case / "certificate.json", proof)
    assert _replay(case)[0] == 1


@pytest.mark.parametrize("rule_kind", ("no-group", "post-filter", "repeated", "constant", "join"))
def test_valid_models_outside_fragment_refuse(case, rule_kind):
    from gnd.model import load_model
    from gnd.witness.count_producer import produce_count

    path = case / "model.orm.yaml"
    model = YAML(typ="safe").load(path)
    count = model["fact_types"][1]
    rule = count["derivation_rule"]
    body = rule["body"][0]
    if rule_kind == "no-group":
        count["roles"].pop(0)
        count["reading"] = "There are {Count} qualifying contributions"
        del rule["head"]["group"]
    elif rule_kind == "post-filter":
        rule["where"] = [{"operator": ">", "left": "$n", "right": 0}]
    elif rule_kind == "repeated":
        body["bind"]["source"] = "$tag"
    elif rule_kind == "constant":
        body["bind"]["source"] = "notes-a"
    else:
        rule["body"].append(body)
    _write(path, model)
    load_model(path)
    assert produce_count(path, case / "population.json", case / "group.json") == {
        "exit_code": 2, "reason": "fragment-unsupported"
    }


def test_opaque_group_key_cannot_prove_either_group_complete(case):
    from gnd.model import load_model
    from gnd.population import load_population
    from gnd.witness.count_producer import produce_count

    model = case / "model.orm.yaml"
    path = case / "population.json"
    population = _read(path)
    population["format_version"] = 2
    population["facts"]["observation"][1]["group"] = {"$opaque": "redacted"}
    _write(path, population)
    load_population(path, model=load_model(model))
    for request in ("group.json", "empty-group.json"):
        assert produce_count(model, path, case / request) == {"exit_code": 2, "reason": "opaque-value"}


def test_malformed_snapshot_yaml_gets_a_structured_refusal(case):
    (case / "model.orm.yaml").write_text("fact_types: [")
    code, output, stderr = _produce(case)
    assert code == 3 and json.loads(output)["reason"] == "input-invalid"
    assert not stderr


def test_public_count_routes_share_disclosure_policy(case):
    args = ("model.orm.yaml", "population.json", "--request", "group.json")
    default = _command(case, "witness-count", *args)
    public = {"exit_code": 0, "reason": None, "status": "complete"}
    assert default[0] == 0 and json.loads(default[1]) == public
    assert _command(case, "--disclosure", "customer", "witness-count", *args,
                    "--raw", "--out", "certificate.json")[0] == 3
    assert not (case / "certificate.json").exists()
    assert _command(case, "--disclosure", "internal", "witness-count", *args,
                    "--out", "certificate.json")[0] == 0
    assert stat.S_IMODE((case / "certificate.json").stat().st_mode) == 0o600
    assert _command(case, "--disclosure", "customer", "replay-count", *args, "certificate.json",
                    "--raw")[0] == 3
    assert _command(case, "witness-count", *args, "--raw", "--out", "certificate.json")[0] == 3
    replay = _command(case, "--disclosure", "customer", "replay-count", *args, "certificate.json")
    assert replay[0] == 0 and json.loads(replay[1]) == public
