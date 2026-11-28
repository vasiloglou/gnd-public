import json
import os
import subprocess
from pathlib import Path

import pytest

from gnd import api
from gnd.export.pyrel_rules import render
from gnd.export.pyrel_runtime import ExportInputError

MODEL = Path(__file__).parent / "fixtures/duckdb-guarded-existence/model.orm.json"


def population(approved, *, requested=("A",)):
    facts = {"requested": [{"id": key} for key in requested],
             "outcome": [{"id": "A", "result": "yes"}, {"id": "B", "result": "other"}]}
    if approved is not None:
        facts["approved"] = [{"result": value} for value in approved]
    return {"population": {"model": MODEL.name, "source": "fixture", "covers": list(facts)}, "facts": facts}


@pytest.mark.parametrize(("values", "requested", "exit_code"), [
    (["yes"], ("A",), 0), (["other"], ("A",), 1), ([], ("A",), 1),
    (None, ("A",), 4), ([], (), 2)])
def test_native_guarded_controls(tmp_path, values, requested, exit_code):
    path = tmp_path / "population.json"
    path.write_text(json.dumps(population(values, requested=requested)))
    assert api.check(MODEL, path)["exit_code"] == exit_code
    assert "not_(outcome(" in render(MODEL, "duckdb")


def test_export_boundaries(tmp_path):
    with pytest.raises(ExportInputError, match="duckdb-snapshot-only"):
        render(MODEL, "lqp")
    for change, reason in (("disconnect", "disconnected"), ("filter", "filters-unsupported")):
        doc = json.loads(MODEL.read_bytes())
        exists = doc["constraints"][0]["consequent"]["exists"]
        if change == "disconnect":
            exists["atoms"][0]["bind"]["id"] = "$another"
        else:
            exists["where"] = [{"left": "$r", "operator": "=", "right": "other"}]
        path = tmp_path / MODEL.name
        path.write_text(json.dumps(doc))
        with pytest.raises(ExportInputError, match=reason):
            render(path, "duckdb")


def test_generated_program_on_duckdb(tmp_path):
    interpreter = os.environ.get("GND_TUTORIAL_PYREL_PYTHON")
    if not interpreter:
        pytest.skip("requires isolated PyRel runtime")
    script = tmp_path / "rules.py"
    script.write_text(render(MODEL, "duckdb"))
    for values, keys, wanted, label in ((["yes"], ("A",), 0, "OK"),
                                         (["other"], ("A",), 1, '{"$i": "A"}'),
                                         ([], ("A",), 1, '{"$i": "A"}'),
                                         (None, ("A",), 4, "not checked"), ([], (), 2, "vacuous")):
        path = tmp_path / "population.json"
        path.write_text(json.dumps(population(values, requested=keys)))
        result = subprocess.run([interpreter, str(script), str(path)], cwd=tmp_path,
                                check=False, capture_output=True, text=True, timeout=90)
        assert result.returncode == wanted, (result.stdout, result.stderr)
        assert label in result.stdout


def test_renamed_roles_and_reordered_consequent(tmp_path):
    doc = json.loads(MODEL.read_bytes())
    for fact in doc["fact_types"]:
        for role in fact["roles"]:
            role["role_name"] = "db_" + role["role_name"]
    rule = doc["constraints"][0]
    atoms = rule["consequent"]["exists"]["atoms"]
    atoms.reverse()
    for atom in (*rule["antecedent"], *atoms):
        atom["bind"] = {"db_" + role: term for role, term in atom["bind"].items()}
    path = tmp_path / MODEL.name
    path.write_text(json.dumps(doc))
    assert "not_(approved(" in render(path, "duckdb")


def test_joint_variable_must_have_one_primitive(tmp_path):
    doc = json.loads(MODEL.read_bytes())
    doc["object_types"].append({"id": "number", "name": "NumberId", "kind": "value", "primitive": "Integer"})
    approved = doc["fact_types"][-1]
    approved["roles"][0]["object_type"] = "number"
    approved["reading"] = "{NumberId} is approved"
    path = tmp_path / MODEL.name
    path.write_text(json.dumps(doc))
    with pytest.raises(ExportInputError, match="variable-type-mismatch"):
        render(path, "duckdb")


@pytest.mark.parametrize(("size", "expected"), [(200, 0), (500, 4)])
def test_existential_work_ceiling_on_joint_prefixes(tmp_path, size, expected):
    interpreter = os.environ.get("GND_TUTORIAL_PYREL_PYTHON")
    if not interpreter:
        pytest.skip("requires isolated PyRel runtime")
    doc = json.loads(MODEL.read_bytes())
    doc["constraints"][0]["consequent"]["exists"]["atoms"].reverse()
    model = tmp_path / MODEL.name
    model.write_text(json.dumps(doc))
    keys = [str(i) for i in range(size)]
    data = population(keys, requested=keys)
    data["facts"]["outcome"] = [{"id": key, "result": key} for key in keys]
    path = tmp_path / "population.json"
    path.write_text(json.dumps(data))
    assert api.check(model, path)["exit_code"] == expected
    script = tmp_path / "rules.py"
    script.write_text(render(model, "duckdb"))
    result = subprocess.run([interpreter, str(script), str(path)], cwd=tmp_path, timeout=90,
                            capture_output=True, text=True, check=False)
    assert result.returncode == expected, (result.stdout, result.stderr)
