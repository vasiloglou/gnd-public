"""Phase 4 transition successor behavior."""
from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator
from ruamel.yaml import YAML
from support.v70_phase4 import FIXTURE, _positive, _write
from test_v70_phase4_runtime import _stage

from gnd import api
from gnd.model import Model, _attach_compiled_obligations, load_model
from gnd.population import load_population_bytes
from gnd.report import load_report_schema
from gnd.transition import evaluate_plan, model_digest, operations_digest


def test_dynamic_refresh_turns_a_possible_path_into_a_definite_one(tmp_path: Path) -> None:
    model = YAML(typ="safe").load((FIXTURE / "recursive.orm.yaml").read_text())
    population = json.loads((FIXTURE / "recursive.pop.json").read_text())
    population["facts"]["edge"][1]["target"] = {"$opaque": "unknown-target"}
    model["operations"].append({
        "id": "link", "reading": "{Node:source} links to {Node:target}",
        "parameters": [
            {"name": "source", "object_type": "node"},
            {"name": "target", "object_type": "node"},
        ],
        "preconditions": [],
        "effects": [{"assert": {"fact_type": "edge", "bind": {"source": "$source", "target": "$target"}}}],
        "frame": {"modality": "alethic"},
        "source": "user-supplied", "status": "confirmed",
        "provenance": {"user_quote": "A link adds an edge."},
    })
    model_path, population_path = _write(tmp_path, model, population)
    loaded = load_model(model_path)
    steps = {
        "steps_schema": 1, "model": "model.orm.yaml",
        "model_digest": model_digest(loaded),
        "operations_digest": operations_digest(loaded.operations),
        "steps": [
            {"op": "link", "bindings": {"source": "B", "target": "C"}},
            {"op": "visit", "bindings": {"source": "A", "target": "C"}},
        ],
    }
    steps_path = tmp_path / "steps.json"
    steps_path.write_text(json.dumps(steps) + "\n")
    payload = api.transition(model_path, population_path, steps_path)
    assert payload["exit_code"] == 4  # legacy embedded snapshot projects the opaque source
    visit = payload["transition"]["steps"][1]
    assert not [row for row in visit["verdicts"] if row["kind"] == "precondition"]
    assert {"source": "A", "target": "C"} in payload["transition"]["computed_post"]["facts"]["visited"]


def test_possible_walk_report_validates_and_definite_miss_fails(tmp_path: Path) -> None:
    model, population, steps = _stage("T01-walk-unknown-precondition", tmp_path)
    assert steps is not None
    unknown = api.transition(model, population, steps)
    assert not list(Draft202012Validator(load_report_schema()).iter_errors(unknown))

    model, population, steps = _stage("T02-walk-scalar-control", tmp_path)
    assert steps is not None
    document = json.loads(steps.read_text())
    document["steps"][0]["bindings"]["target"] = "Z"
    steps.write_text(json.dumps(document) + "\n")
    missing = api.transition(model, population, steps)
    assert missing["exit_code"] == 1
    assert any(row["kind"] == "precondition" and row["verdict"] == "fail"
               for row in missing["transition"]["steps"][0]["verdicts"])
    assert {"source": "A", "target": "Z"} in missing["transition"]["computed_post"]["facts"]["visited"]


def test_unknown_old_dynamic_subject_is_unchecked(tmp_path: Path) -> None:
    document, population = _positive()
    document["object_types"][1]["primitive"] = "Integer"
    document["fact_types"][1]["constraints"] = [{
        "type": "uniqueness", "roles": ["record"], "modality": "alethic",
        "source": "explicit", "status": "confirmed",
        "provenance": {"user_quote": "Each record has one item."},
    }]
    document["operations"] = [{
        "id": "update", "reading": "{Record} updates {Item}",
        "parameters": [{"name": "record", "object_type": "record"},
                       {"name": "item", "object_type": "item"}],
        "preconditions": [],
        "effects": [{"assert": {"fact_type": "observed", "bind": {
            "record": "$record", "item": "$item"}}}],
        "dynamic_rules": [{
            "id": "rise", "subject": {"fact_type": "inferred", "value_role": "item",
                                      "bind": {"record": "$record"}},
            "op": ">", "modality": "alethic", "source": "user-supplied",
            "status": "confirmed", "provenance": {"user_quote": "Item must rise."},
        }],
        "frame": {"modality": "alethic"}, "source": "user-supplied",
        "status": "confirmed", "provenance": {"user_quote": "Update records item."},
    }]
    model = Model.model_validate(document)
    _attach_compiled_obligations(model)
    population["facts"]["observed"] = [{"record": "R1", "item": {"$opaque": "unknown"}}]
    population["facts"]["inferred"] = []
    admitted = load_population_bytes(json.dumps(population).encode(), source="population.json", model=model)
    result = evaluate_plan(model, admitted, [{"op": "update", "bindings": {
        "record": "R1", "item": 5}}])
    verdicts = [row for row in result.report.steps[0].verdicts if row.kind == "dynamic-rule"]
    assert [(row.verdict, row.reason_code) for row in verdicts] == [
        ("unchecked", "derived-unknown")
    ]


def test_retraction_removes_a_possible_path_before_next_step(tmp_path: Path) -> None:
    model = YAML(typ="safe").load((FIXTURE / "recursive.orm.yaml").read_text())
    population = json.loads((FIXTURE / "recursive.pop.json").read_text())
    population["facts"]["edge"][1]["target"] = {"$opaque": "unknown-target"}
    model["operations"].append({
        "id": "unlink", "reading": "{Node:source} unlinks {Node:target}",
        "parameters": [{"name": role, "object_type": "node"}
                       for role in ("source", "target")],
        "preconditions": [],
        "effects": [{"retract": {"fact_type": "edge", "bind": {
            "source": "$source", "target": "$target"}}}],
        "frame": {"modality": "alethic"}, "source": "user-supplied",
        "status": "confirmed", "provenance": {"user_quote": "Unlink removes the edge."},
    })
    model_path, population_path = _write(tmp_path, model, population)
    loaded = load_model(model_path)
    steps = {
        "steps_schema": 1, "model": "model.orm.yaml",
        "model_digest": model_digest(loaded),
        "operations_digest": operations_digest(loaded.operations),
        "steps": [
            {"op": "unlink", "bindings": {"source": "A", "target": "B"}},
            {"op": "visit", "bindings": {"source": "A", "target": "C"}},
        ],
    }
    steps_path = tmp_path / "steps.json"
    steps_path.write_text(json.dumps(steps) + "\n")
    result = api.transition(model_path, population_path, steps_path)
    verdicts = [row for row in result["transition"]["steps"][1]["verdicts"]
                if row["kind"] == "precondition"]
    assert [(row["verdict"], row["reason_code"]) for row in verdicts] == [("fail", None)]
