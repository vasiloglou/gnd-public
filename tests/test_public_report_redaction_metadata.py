from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator

import gnd.api
from gnd.report import load_report_schema, render_json

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/public-emitter-trust-controls"
ANSWERS = json.loads((ROOT / "tests/fixtures/public-report-redaction-metadata.json").read_text(encoding="utf-8"))
MODEL = FIXTURE / "models/role-declaration.orm.yaml"
CLEAN = FIXTURE / "populations/00-clean.yaml"
VIOLATING = FIXTURE / "populations/01-violating.yaml"

def _marker_paths(value: Any, path: tuple[Any, ...] = ()) -> list[tuple[Any, ...]]:
    paths: list[tuple[Any, ...]] = []
    if isinstance(value, dict):
        if set(value) == {"redacted", "roles"} and value.get("redacted") is True:
            paths.append(path)
        for key, child in value.items():
            paths.extend(_marker_paths(child, (*path, key)))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            paths.extend(_marker_paths(child, (*path, index)))
    return paths


def _at_path(value: Any, path: tuple[Any, ...]) -> Any:
    cursor = value
    for coordinate in path:
        cursor = cursor[coordinate]
    return cursor


def _assert_marker(marker: dict[str, Any]) -> None:
    assert set(marker) == {"redacted", "roles"}
    assert marker["redacted"] is True
    assert marker["roles"]
    assert marker["roles"] == sorted(set(marker["roles"]))


def test_symmetric_metadata_exact_bytes() -> None:
    applied = gnd.api.check(MODEL, CLEAN)
    unredacted = gnd.api.check(MODEL, CLEAN, unredacted=True)
    assert applied["redaction"] == ANSWERS["applied_redaction"]
    assert unredacted["redaction"] == ANSWERS["unredacted_redaction"]
    assert json.dumps(applied["redaction"], allow_nan=False) == json.dumps(
        ANSWERS["applied_redaction"], allow_nan=False
    )
    assert json.dumps(unredacted["redaction"], allow_nan=False) == json.dumps(
        ANSWERS["unredacted_redaction"], allow_nan=False
    )
    assert json.loads(render_json(applied))["redaction"] == ANSWERS["applied_redaction"]
    assert json.loads(render_json(unredacted))["redaction"] == ANSWERS["unredacted_redaction"]


def test_marker_schema_mutations_refuse() -> None:
    schema = load_report_schema()
    validator = Draft202012Validator(schema)
    payload = gnd.api.check(MODEL, VIOLATING)
    validator.validate(payload)
    paths = _marker_paths(payload)
    assert paths, "the violating canary must exercise a replacement marker"

    for mutation in ("missing", "extra", "wrong-type", "empty", "unsorted"):
        dirty = copy.deepcopy(payload)
        marker = _at_path(dirty, paths[0])
        if mutation == "missing":
            marker.pop("redacted")
        elif mutation == "extra":
            marker["value"] = "secret"
        elif mutation == "wrong-type":
            marker["redacted"] = "true"
        elif mutation == "empty":
            marker["roles"] = []
        else:
            marker["roles"] = ["z.role", "a.role"]
        if mutation == "unsorted":
            with pytest.raises(AssertionError):
                _assert_marker(marker)
        else:
            assert list(validator.iter_errors(dirty)), mutation
