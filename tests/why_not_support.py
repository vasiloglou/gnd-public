"""Shared model and population builders for the why-not kernel tests."""

from __future__ import annotations

import json

from gnd.model import load_model_bytes
from gnd.population import load_population_bytes

OBJECT_TYPES = [
    {"id": "code", "name": "Code", "kind": "value", "primitive": "String"},
    {"id": "int", "name": "Int", "kind": "value", "primitive": "Integer"},
    {"id": "num", "name": "Num", "kind": "value", "primitive": "Number"},
    {"id": "flag", "name": "Flag", "kind": "value", "primitive": "Boolean"},
]


def fact_type(fact_id, roles, rule=None, derivation="derived"):
    """``roles`` is a list of (role_name, object_type_id); a rule makes it derived."""
    reading = " ".join("{" + ot.capitalize() + "}" for _, ot in roles) + f" {fact_id}"
    row = {
        "id": fact_id,
        "reading": reading,
        "roles": [{"object_type": ot, "role_name": name} for name, ot in roles],
    }
    if rule is not None:
        row["derivation"] = derivation
        row["derivation_rule"] = rule
    return row


def model_document(fact_types):
    return {
        "version": 2,
        "model_id": "urn:why-not:test",
        "source": {"kind": "text-conversation", "confidence": "standard", "mode": "one-shot"},
        "object_types": [dict(ot) for ot in OBJECT_TYPES],
        "fact_types": [dict(ft) for ft in fact_types],
    }


def build(fact_types):
    document = model_document(fact_types)
    model = load_model_bytes(json.dumps(document).encode(), source="model.json")
    return model, document


def population_document(document, facts):
    covers = [
        ft["id"] for ft in document["fact_types"]
        if ft.get("derivation") in ("derived", "semiderived")
    ]
    return {
        "format_version": 2,
        "instances": {},
        "facts": {key: [dict(row) for row in rows] for key, rows in facts.items()},
        "population": {
            "model": "model.json", "model_id": document["model_id"],
            "source": "fixture", "covers": covers,
        },
    }


def population(model, document, facts):
    doc = population_document(document, facts)
    return load_population_bytes(json.dumps(doc).encode(), source="population.json", model=model), doc


def atom(fact_id, **bind):
    return {"fact_type": fact_id, "bind": bind}


def cells(*pairs):
    """``cells(("String", "a"), ("Integer", 1))`` builds a typed row."""
    return [{"primitive": primitive, "value": value} for primitive, value in pairs]


def strings(*values):
    return cells(*(("String", value) for value in values))
