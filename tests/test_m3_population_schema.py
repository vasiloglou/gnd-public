"""Frozen schema preparation preserves ordered shape-validation diagnostics."""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from gnd import population
from gnd.errors import ValidationIssue
from gnd.model import load_model

FIXTURES = Path(__file__).parent / "fixtures/skeleton"


def original_issues(doc, schema):
    return [ValidationIssue(path=e.json_path, message=e.message,
                            rule_id=f"jsonschema:{e.validator}")
            for e in sorted(Draft202012Validator(schema).iter_errors(doc), key=lambda e:e.json_path)]


def has_ref(value):
    if isinstance(value, dict):
        return "$ref" in value or any(has_ref(v) for v in value.values())
    return isinstance(value, list) and any(has_ref(v) for v in value)


def test_public_population_load_removes_repeated_local_ref_lookup(monkeypatch):
    observed = []
    def capture(schema):
        observed.append(schema)
        return Draft202012Validator(schema)
    monkeypatch.setattr(population, "Draft202012Validator", capture)
    model = load_model(FIXTURES / "model.orm.yaml")
    loaded = population.load_population(FIXTURES / "population.good.json", model=model)
    assert loaded.matches_validation_marker(model)
    assert observed and not any(has_ref(schema) for schema in observed)


@pytest.mark.parametrize("shape", [
    "good", "root", "header", "source", "facts", "rows", "row", "extra",
    "value", "opaque-v1", "opaque-v2", "opaque-extra", "opaque-empty", "instances", "ties",
])
def test_exact_ordered_issues_match_unexpanded_schema(shape):
    doc = json.loads((FIXTURES / "population.good.json").read_text())
    if shape == "root": doc = []
    elif shape == "header": doc.pop("population")
    elif shape == "source": doc["population"].pop("source")
    elif shape == "facts": doc["facts"] = []
    elif shape == "rows": doc["facts"]["movie_has_title"] = {}
    elif shape == "row": doc["facts"]["movie_has_title"] = [1]
    elif shape == "extra": doc["unknown"] = True
    elif shape == "instances": doc["instances"] = {"movie": [None, {}]}
    elif shape == "ties":
        doc["format_version"] = 1
        doc["facts"]["movie_has_title"][0]["title"] = {}
    elif shape in {"value", "opaque-v1", "opaque-v2", "opaque-extra", "opaque-empty"}:
        value = None if shape == "value" else {"$opaque": "existing marker"}
        if shape in {"opaque-v2", "opaque-extra", "opaque-empty"}: doc["format_version"] = 2
        if shape == "opaque-extra": value["extra"] = 1
        if shape == "opaque-empty": value["$opaque"] = ""
        doc["facts"]["movie_has_title"][0]["title"] = value
    schema = population._load_population_schema()
    before = copy.deepcopy(schema)
    assert population._schema_issues(doc) == original_issues(doc, schema)
    assert schema == before


@pytest.mark.parametrize("unsupported", ["unknown", "cycle", "sibling", "external", "nested-id", "dynamic", "deep"])
def test_unsupported_schema_uses_original_validator(unsupported):
    schema = population._load_population_schema()
    if unsupported == "unknown": schema["properties"]["facts"] = {"$ref": "#/$defs/missing"}
    elif unsupported == "cycle": schema["$defs"]["scalar"] = {"$ref": "#/$defs/scalar"}
    elif unsupported == "sibling": schema["$defs"]["fact_value"]["anyOf"][0]["description"] = "sibling"
    elif unsupported == "external": schema["$defs"]["scalar"] = {"$ref": "https://example.invalid/schema"}
    elif unsupported == "nested-id": schema["$defs"]["scalar"]["$id"] = "nested"
    elif unsupported == "dynamic": schema["$defs"]["scalar"]["$dynamicRef"] = "#scalar"
    else:
        node = schema["$defs"]["scalar"]
        for _ in range(100):
            node["items"] = {}
            node = node["items"]
    assert population._prepared_population_schema(schema) is schema


@pytest.mark.parametrize("schema", [None, [], True, 1, "schema", {"$defs": []}])
def test_hostile_schema_preparation_is_total(schema):
    assert population._prepared_population_schema(schema) is schema


def test_schema_preparation_work_bound_falls_back():
    schema = population._load_population_schema()
    schema["$defs"]["scalar"] = {"anyOf": [{"type": "string"}] * 5000}
    assert population._prepared_population_schema(schema) is schema
