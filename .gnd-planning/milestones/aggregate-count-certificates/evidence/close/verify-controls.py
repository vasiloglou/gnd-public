"""Run focused close-panel controls from the repository root."""
import json
import tempfile
from dataclasses import replace
from pathlib import Path

from ruamel.yaml import YAML

from gnd.artifacts import canonical_json_bytes, sha256_hex
from gnd.checker import structured_extension_facts
from gnd.model import load_model
from gnd.population import load_population
from gnd.witness.count_producer import produce_count
from gnd.witness.count_replay import replay_count
from gnd.witness.types import DEFAULT_LIMITS

FIXTURE = Path("src/gnd/examples/literature/count_fixture")
WORK = {"exit_code": 4, "reason": "work-limit"}
INPUT = {"exit_code": 3, "reason": "input-invalid"}
OPAQUE = {"exit_code": 2, "reason": "opaque-value"}


def read(path):
    return json.loads(path.read_bytes())


def write(path, value):
    path.write_bytes(canonical_json_bytes(value))


def typed(primitive, value):
    return {"primitive": primitive, "value": value}


def differential(directory):
    model = YAML(typ="safe").load(FIXTURE / "model.orm.yaml")
    model["object_types"].append(
        {"id": "enabled", "name": "Enabled", "kind": "value", "primitive": "Boolean"}
    )
    source, target = model["fact_types"]
    for fact in (source, target):
        fact["roles"].append({"object_type": "enabled", "role_name": "enabled"})
    source["reading"] = "{Method} reports {Method} with score {Count} in {Label} when {Enabled}"
    target["reading"] += " when {Enabled}"
    source["roles"][2]["object_type"] = "count"
    rule = target["derivation_rule"]
    rule["body"][0]["bind"]["enabled"] = "$enabled"
    rule["aggregate"]["over"] = ["$member", "$tag"]
    rule["head"]["enabled"] = "$enabled"

    population = read(FIXTURE / "population.json")
    for position, row in enumerate(population["facts"]["observation"]):
        row.update(tag=7, enabled=position != 1)
    for row in population["facts"]["method_count"]:
        row["enabled"] = row["group"] == "flow"
    request = read(FIXTURE / "group.json")
    model_path = directory / "model.orm.json"
    pop_path = directory / "population.json"
    request_path = directory / "request.json"
    certificate = directory / "proof.json"
    write(model_path, model)
    write(pop_path, population)
    declared = load_model(model_path)
    rows = structured_extension_facts(declared, load_population(pop_path, model=declared))["method_count"]
    assert {(row["group"], row["enabled"]): row["count"] for row in rows} == {
        ("flow", True): 2, ("other", False): 1
    }
    for group, enabled, expected in (("flow", True, 2), ("other", False, 1), ("flow", False, 0)):
        request["group"] = {"group": typed("String", group), "enabled": typed("Boolean", enabled)}
        write(request_path, request)
        result = produce_count(model_path, pop_path, request_path)
        assert result["exit_code"] == 0 and result["count"] == expected, result
        for member in result["certificate"]["members"]:
            assert [cell["primitive"] for cell in member["over"]] == ["String", "Integer"]
            assert member["over"][1] == member["of"] == typed("Integer", 7)
        write(certificate, result["certificate"])
        assert replay_count(model_path, pop_path, certificate, request_path)["exit_code"] == 0
    return {"aggregate_counts": [2, 1], "absent_group_replay_count": 0}


def replay_controls(directory):
    model = FIXTURE / "model.orm.yaml"
    population = directory / "population.json"
    request = FIXTURE / "group.json"
    certificate = directory / "certificate.json"
    doc = read(FIXTURE / "population.json")
    doc["facts"]["observation"] = [
        {"group": "flow", "member": "alpha", "tag": str(idx), "source": "x"}
        for idx in range(40)
    ]
    write(population, doc)
    full = produce_count(model, population, request)["certificate"]
    assert full["count"] == 40
    write(certificate, full)
    assert replay_count(model, population, certificate, request,
                        limits=replace(DEFAULT_LIMITS, nodes=1)) == INPUT
    byte_limit = population.stat().st_size
    assert certificate.stat().st_size > byte_limit
    assert replay_count(model, population, certificate, request,
                        limits=replace(DEFAULT_LIMITS, bytes=byte_limit)) == INPUT
    # A validly framed false-empty roster fits the input budget.
    write(certificate, {**full, "count": 0, "status": "empty-group", "members": []})
    assert certificate.stat().st_size < byte_limit
    assert replay_count(model, population, certificate, request) == {
        "exit_code": 1, "reason": "proof-invalid"
    }
    assert replay_count(model, population, certificate, request,
                        limits=replace(DEFAULT_LIMITS, nodes=1)) == WORK
    assert replay_count(model, population, certificate, request,
                        limits=replace(DEFAULT_LIMITS, bytes=byte_limit)) == WORK

    source = FIXTURE / "population.json"
    for filename in ("group.json", "empty-group.json"):
        request = FIXTURE / filename
        proof = produce_count(model, source, request)["certificate"]
        doc = read(source)
        doc["format_version"] = 2
        doc["facts"]["observation"][1]["group"] = {"$opaque": "redacted"}
        write(population, doc)
        assert produce_count(model, population, request) == OPAQUE
        write(certificate, proof)
        assert replay_count(model, population, certificate, request) == {
            "exit_code": 3, "reason": "binding-stale"
        }
        proof["binding"]["population_sha256"] = sha256_hex(population.read_bytes())
        write(certificate, proof)
        assert replay_count(model, population, certificate, request) == OPAQUE
    return {"submitted_roster_and_bytes_exit": 3, "reconstructed_roster_and_bytes_exit": 4,
            "false_empty_exit": 1, "opaque_populated_and_empty_exit": 2}


if __name__ == "__main__":
    with tempfile.TemporaryDirectory(prefix="gnd-ac1-close-controls-") as temporary:
        directory = Path(temporary)
        print(json.dumps({"typed_differential": differential(directory),
                          "replay": replay_controls(directory)}, indent=2, sort_keys=True))
