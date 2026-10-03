"""Observe frozen finite-policy, strict-reader and legacy-feedback coordinates.

Finite-policy cases are abstract combinations, not admitted business inputs or
release capabilities. The separate public-command cases establish those routes.
This module never reads the answer key or creates proof evidence.
"""

from __future__ import annotations

import atexit
import copy
import gzip
import hashlib
import io
import json
import re
import shutil
import tempfile
from pathlib import Path
from typing import Any

import jsonschema
import test_public_assurance_inputs_support as inputs

import gnd
from gnd import assurance, assurance_evidence
from gnd.exp import session_eval
from gnd.exp.session_contract import SessionCase
from gnd.semantic_registry import capture_branches


def _materialize():
    path = Path(__file__).parent / "fixtures/public-finite-observer/corpus.json.gz"
    packed = path.read_bytes()
    assert len(packed) <= 32768
    assert hashlib.sha256(packed).hexdigest() == "ca372e31aefe4c7f8a14ab4e359eadd0b3e705749462357ef70552d1f39622a5"
    with gzip.GzipFile(fileobj=io.BytesIO(packed)) as stream:
        raw = stream.read(1048577)
    assert len(raw) <= 1048576
    assert hashlib.sha256(raw).hexdigest() == "0db81a8fa94f06ef51effd1f52077152dc78b14bd94eb0fba53d0294cb561abe"
    documents = json.loads(raw)
    assert len(documents) == 12
    temporary = tempfile.TemporaryDirectory(prefix="gnd-public-finite-observer-")
    root = Path(temporary.name).resolve()
    allowed = {"tests/fixtures/v6-assurance/matrix.json", "tests/fixtures/v6-assurance/answers/expected.json", "tests/fixtures/v6-assurance/legacy-feedback/case.json", "tests/fixtures/v6-assurance/legacy-feedback/evaluation.json", "tests/fixtures/v6-assurance/legacy-feedback/output.txt"}
    for name, value in documents.items():
        assert name in allowed or re.fullmatch(r"tests/fixtures/v6-assurance/hostile/[a-z][a-z0-9-]*\.bin", name)
        data = bytes.fromhex(value)
        assert len(data) <= 524288
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    schema = root / "src/gnd/assurance-anchor.schema.json"
    schema.parent.mkdir(parents=True)
    shutil.copyfile(Path(gnd.__file__).resolve().parent / "assurance-anchor.schema.json", schema)
    return temporary, root

_TEMPORARY, ROOT = _materialize()
atexit.register(_TEMPORARY.cleanup)
CORPUS = ROOT / "tests/fixtures/v6-assurance"

def read(path: Path) -> Any:
    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        return document
    encoding = document.get("encoding")
    if encoding == "shared-sets-v1":
        document.pop("encoding")
        sets = document.pop("sets")
        defaults = document.pop("row_defaults", {})
        for row in document["rows"]:
            for key, value in defaults.items():
                row.setdefault(key, copy.deepcopy(value))
            row["scope_ids"] = copy.deepcopy(sets[row.pop("scope_set")])
            for key in (
                "required_infrastructure",
                "applicable",
                "covered",
                "missing_infrastructure",
            ):
                if key + "_set" in row["recipe"]:
                    row["recipe"][key] = copy.deepcopy(sets[row["recipe"].pop(key + "_set")])
    elif encoding == "shared-expectations-v1":
        document.pop("encoding")
        expectations = document.pop("expectations")
        document["cases"] = {
            key: copy.deepcopy(expectations[ref]) for key, ref in document["cases"].items()
        }
    return document

def reader(row: dict, root: Path = ROOT) -> dict:
    raw = inputs._read(inputs.contained(root, row["recipe"]["raw_path"]))
    try:
        document = assurance_evidence._json(raw)
        schema = assurance_evidence._json(
            inputs._read(root / "src/gnd/assurance-anchor.schema.json")
        )
        jsonschema.validate(document, schema)
    except (ValueError, UnicodeError, jsonschema.ValidationError):
        return {
            "error": "invalid-evidence",
            "level": assurance.AssuranceBlockV1(None).assurance_level,
        }
    raise ValueError("hostile evidence specimen was unexpectedly admitted")


def legacy_feedback(row: dict, root: Path = ROOT) -> dict:
    recipe = row["recipe"]
    evaluation = session_eval.CaseEvaluation.model_validate_json(
        inputs._read(inputs.contained(root, recipe["source_fixture"]))
    )
    case = SessionCase.model_validate_json(
        inputs._read(root / "tests/fixtures/v6-assurance/legacy-feedback/case.json")
    )
    with capture_branches() as trace:
        try:
            value = session_eval._case_feedback(
                evaluation, case=case, schema_version=recipe["schema_version"]
            )
            payload, error, status = value.model_dump(mode="json", by_alias=True), None, "projected"
        except ValueError as failure:
            payload, error, status = None, str(failure), "refused"
    return {
        "status": status,
        "error": error,
        "payload": payload,
        "trace": sorted(trace),
        "assurance_level": assurance.AssuranceBlockV1(None).assurance_level,
    }
