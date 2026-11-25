"""SI2: select a preferred reviewed composite key at the shared boundary."""

import json
import time
from copy import deepcopy
from importlib.resources import files

import pytest

from gnd.evolve.shapes import _references
from gnd.extract.guidelines import render_guidelines
from gnd.model import load_model, load_model_bytes
from gnd.model._documents import model_wire
from gnd.model_index import ModelIndex
from gnd.model_verbalization import render_model_verbalization
from gnd.refscheme import applicable_set, entity_reference, reference_identity
from gnd.vocabulary import render_verbalization

EXAMPLE = files("gnd").joinpath("skills/gnd-model-from-text/examples/reference_scheme_elicitation.orm.yaml")
ASSIGNMENT = "task_assigned_to_employee"
PROJECT = "task_in_project"


def _load(options, *, project_first=False, project_preferred=True):
    doc = model_wire(load_model(EXAMPLE))
    project = doc["constraints"][0]
    project["preferred"] = project_preferred
    assignment = deepcopy(project)
    assignment["role_refs"][0] = {"fact_type": ASSIGNMENT, "role": "employee"}
    assignment.update(options)
    facts = {fact["id"]: fact for fact in doc["fact_types"]}
    facts[PROJECT]["constraints"].append(deepcopy(facts["task_has_name"]["constraints"][0]))
    doc["constraints"] = [project, assignment] if project_first else [assignment, project]
    return load_model_bytes(json.dumps(doc).encode(), source="task-identifiers.orm.json")


@pytest.mark.parametrize("options", [
    {"preferred": False},
    {"source": "llm-inferred", "status": "proposed", "modality": "deontic",
     "provenance": {"rationale_world_fact": "An assignment is recorded."}},
    {"modality": "deontic"},
], ids=["nonpreferred", "proposed", "deontic"])
def test_later_eligible_identifier_reaches_all_consumers(options):
    model = _load(options)
    kind, components = reference_identity("task", model)
    assert kind == "composite"
    assert [(r["fact_type"], r["role"]) for r in components] == [(PROJECT, "project"), ("task_has_name", "name")]
    assert "Task is identified by the combination of project in task_in_project" in render_model_verbalization(model)
    assert "Task is identified by the combination of project (in fact type task_in_project)" in render_verbalization(model)
    task = next(row for row in applicable_set(model)["object_types"] if row["id"] == "task")
    assert task["role_refs"] == components
    assert entity_reference("task", model) == ("composite", None)
    refs = _references(ModelIndex.for_model(model), model, ("task",))
    assert [ref.identity for ref in refs] == ["composite"]
    assert "Identified by: a combination of roles (composite reference)" in render_guidelines(model)


@pytest.mark.parametrize("project_first", [True, False])
def test_eligible_tie_does_not_depend_on_declaration_order(project_first):
    model = _load({}, project_first=project_first)
    assert [r["fact_type"] for r in reference_identity("task", model)[1]] == [ASSIGNMENT, "task_has_name"]


def test_same_role_set_tie_uses_component_sequence():
    doc = model_wire(_load({}))
    candidate = doc["constraints"][0]
    reordered = {**candidate, "role_refs": list(reversed(candidate["role_refs"]))}
    doc["constraints"] = [reordered, candidate]
    model = load_model_bytes(json.dumps(doc).encode(), source="reordered-identifiers.orm.json")
    assert [r["fact_type"] for r in reference_identity("task", model)[1]] == [ASSIGNMENT, "task_has_name"]


def test_legacy_fallback_and_direct_reference():
    model = _load({"preferred": False}, project_preferred=False)
    assert reference_identity("task", model)[1][0]["fact_type"] == ASSIGNMENT
    assert reference_identity("project", model) == ("direct", "project_name")


def test_unmatchable_preferred_key_does_not_use_legacy_fallback():
    doc = model_wire(_load({"preferred": True}, project_first=True, project_preferred=False))
    employee = next(obj for obj in doc["object_types"] if obj["id"] == "employee")
    employee["reference"] = {"mode": "external"}
    doc["constraints"].append({
        **doc["constraints"][1],
        "role_refs": [{"fact_type": "employee_has_full_name", "role": "full_name"},
                      {"fact_type": "employee_works_on_project", "role": "project"}],
    })
    model = load_model_bytes(json.dumps(doc).encode(), source="nested-identifiers.orm.json")
    kind, reason = reference_identity("task", model)
    assert kind == "unmatchable"
    assert "nested composite joins" in reason
    assert next(row for row in applicable_set(model)["fact_types"]
                if row["id"] == "task_has_name")["applicable"] is False


def test_normative_reference_identity_explains_the_unmatchable_preferred_key():
    section = files("gnd").joinpath("skills/gnd-orm-core/references/representation-format.md")
    assert "An unresolvable selected key is reported as unmatchable." in section.read_text()


def test_many_nonpreferred_constraints_leave_a_bounded_walk():
    model = _load({"preferred": False})
    model = model.model_copy(update={"constraints": [deepcopy(model.constraints[0]) for _ in range(2000)]
                                      + [model.constraints[1]]})
    started = time.monotonic()
    assert reference_identity("task", model)[1][0]["fact_type"] == PROJECT
    assert time.monotonic() - started < 5
