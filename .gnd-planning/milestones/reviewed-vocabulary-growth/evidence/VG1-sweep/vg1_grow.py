"""VG1 growth helper: the five shapes of the VG1 spec, section 8.

Kept identical to the helper in tests/test_vg1_object_type_scaling.py, so
the sweep at the base commit grows the same models as the tests at the head.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

CHRONOLOGY = "vocabulary/chronology.orm.json"
ROOTS = ("checking.orm.json", "extraction.orm.json")
SHAPES = ("values", "entities", "shared", "tree", "both")


def _value(identifier):
    return {"id": identifier, "kind": "value", "primitive": "String"}


def _entity(identifier, value_type):
    return {"id": identifier, "kind": "entity",
            "reference": {"mode": "popular", "value_type": value_type}}


def _subtype(identifier, parent):
    return {"id": identifier, "kind": "entity", "subtype_of": [parent], "inherits_reference": True}


def extra_rows(shape, count):
    """(object types, fact types) the shape adds for COUNT extra types."""
    if shape == "values":
        return [_value(f"extra_{i}") for i in range(count)], []
    if shape == "entities":
        half = count // 2
        return ([_value(f"extra_v{i}") for i in range(half)]
                + [_entity(f"extra_e{i}", f"extra_v{i}") for i in range(half)]), []
    if shape == "shared":
        return [_value("extra_v")] + [_entity(f"extra_e{i}", "extra_v") for i in range(count)], []
    if shape == "tree":
        rows = [_value("extra_v")]
        for r in range(count // 100):
            rows.append(_entity(f"extra_r{r}", "extra_v"))
            for s in range(9):
                rows.append(_subtype(f"extra_r{r}_s{s}", f"extra_r{r}"))
                rows.extend(_subtype(f"extra_r{r}_s{s}_t{t}", f"extra_r{r}_s{s}") for t in range(10))
        return rows, []
    if shape == "both":
        values = [_value(f"extra_{i}") for i in range(count)]
        facts = [{"id": f"extra_ft_{i}", "reading": f"{{Extra{i}}} pairs with {{Extra{(i + 1) % count}}}",
                  "roles": [{"object_type": f"extra_{i}", "role_name": "left"},
                            {"object_type": f"extra_{(i + 1) % count}", "role_name": "right"}]}
                 for i in range(count)]
        return values, facts
    raise ValueError(f"unknown shape {shape!r}")


def deep_chain(count):
    """One value type, one root entity and a subtype chain COUNT deep (plan H4a)."""
    rows = [_value("extra_v"), _entity("extra_c0", "extra_v")]
    rows.extend(_subtype(f"extra_c{i}", f"extra_c{i - 1}") for i in range(1, count))
    return rows, []


def _sha(raw):
    return hashlib.sha256(raw).hexdigest()


def grow(root: Path, rows) -> None:
    """Append ROWS (object types, fact types) to the chronology include and re-pin both roots."""
    object_types, fact_types = rows
    path = root / CHRONOLOGY
    doc = json.loads(path.read_bytes())
    doc["object_types"].extend(object_types)
    doc["fact_types"].extend(fact_types)
    path.write_text(json.dumps(doc))
    digest = _sha(path.read_bytes())
    for name in ROOTS:
        model = json.loads((root / name).read_bytes())
        for entry in model["includes"]:
            if entry["path"] == CHRONOLOGY:
                entry["sha256"] = digest
        (root / name).write_text(json.dumps(model))
