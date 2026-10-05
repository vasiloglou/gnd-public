"""Complete finite Lean fixture integrity, without invoking native tools."""
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

import pytest
from jsonschema import Draft202012Validator


def _materialize_public_corpus():
    packed = (Path(__file__).parent / "fixtures/public-v71-lean-integrity/closure.json.gz").read_bytes()
    assert len(packed) <= 65536
    assert hashlib.sha256(packed).hexdigest() == "8fd9b5e352451daf72dbb759cac3cc5b25cc9609840720b5fc5c2332d36edbc7"
    with gzip.GzipFile(fileobj=io.BytesIO(packed)) as stream:
        raw = stream.read(1048577)
    assert len(raw) <= 1048576
    assert hashlib.sha256(raw).hexdigest() == "01041b39c76fbab02a10673d309e522aac02ff1035999afb0d74019bbe0853f5"
    documents = json.loads(raw)
    assert set(documents) == {'handwritten/ProofObligations.lean', 'handwritten/Definitions.lean', 'answers.json', 'dispatch/golden/inputs/candidate.json', 'release/base/model.orm.json', 'limits.json', 'answers.md', 'release/base/references/catalog.pop.json', 'dispatch/base/references/catalog.pop.json', 'release/golden/inputs/model.json', 'release/golden/manifest.json', 'wire.schema.json', 'dispatch/golden/ProofObligations.lean', 'release/golden/obligations.json', 'inputs.json', 'dispatch/golden/Definitions.lean', 'handwritten/Evaluations.lean', 'README.md', 'release/golden/lean-toolchain', 'release/base/candidate.pop.json', 'release/golden/ProofObligations.lean', 'dispatch/golden/inputs/model.json', 'handwritten/evaluations.json', 'dispatch/base/candidate.pop.json', 'release/golden/inputs/reference-0.json', 'release/golden/source-map.json', 'dispatch/base/model.orm.json', 'release/golden/Definitions.lean', 'dispatch/golden/manifest.json', 'dispatch/golden/source-map.json', 'release/golden/inputs/candidate.json', 'manifest.json', 'dispatch/golden/lean-toolchain', 'dispatch/golden/obligations.json', 'dispatch/golden/inputs/reference-0.json'}
    temporary = tempfile.TemporaryDirectory(prefix="gnd-public-lean-integrity-")
    root = Path(temporary.name).resolve()
    for name, text in documents.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return temporary, root

_TEMPORARY, CORPUS = _materialize_public_corpus()
atexit.register(_TEMPORARY.cleanup)
INPUTS = json.loads((CORPUS / "inputs.json").read_bytes())
ANSWERS = {row["id"]: row for row in json.loads((CORPUS / "answers.json").read_bytes())["cases"]}
SCHEMA = json.loads((CORPUS / "wire.schema.json").read_bytes())
CASES = INPUTS["cases"]

def assert_answer(observation, expected):
    for key, value in expected.items():
        if key not in {
            "id",
            "native_outcome",
            "native_comparison_truth",
            "native_hard_invariant",
            "native_derived_pairs",
        }:
            assert key in observation, f"missing {key}"
            assert type(observation[key]) is type(value), f"type drift {key}"
            assert observation[key] == value, f"{key}: {observation[key]!r} != {value!r}"


def validate_corpus(root):
    manifest = json.loads((root / "manifest.json").read_bytes())
    assert type(manifest["version"]) is int and manifest["version"] == 1
    actual = {
        p.relative_to(root).as_posix()
        for p in root.rglob("*")
        if p.is_file() and p != root / "manifest.json"
    }
    assert set(manifest["files"]) == actual
    for name, record in manifest["files"].items():
        p = root / name
        assert not p.is_symlink()
        raw = p.read_bytes()
        assert record == {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
    inputs = json.loads((root / "inputs.json").read_bytes())["cases"]
    answers = json.loads((root / "answers.json").read_bytes())["cases"]
    assert len({r["id"] for r in inputs}) == len(inputs)
    assert len({r["id"] for r in answers}) == len(answers)
    assert {r["id"] for r in inputs} == {r["id"] for r in answers}
    for row in inputs:
        assert set(row) == {"id", "domain", "branch", "mode", "parameters", "lane", "story"}
        assert row["lane"] == ("proof" if row["mode"] == "native" else "default")
        assert row["story"] and row["parameters"]["action"]
        assert (root / row["domain"] / "base/model.orm.json").is_file()
    for domain in ["dispatch", "release"]:
        groups = {r["branch"] for r in inputs if r["domain"] == domain and r["lane"] == "default"}
        assert groups == {f"S{i:02d}" for i in range(3, 22)} | {
            "S01" if domain == "dispatch" else "S02"
        }
        bundle = root / domain / "golden"
        for name, key in [
            ("manifest", "manifest"),
            ("obligations", "obligations"),
            ("source-map", "source_map"),
        ]:
            Draft202012Validator({**SCHEMA, "$ref": "#/$defs/" + key}).validate(
                json.loads((bundle / (name + ".json")).read_bytes())
            )
        doc = json.loads((bundle / "manifest.json").read_bytes())
        roster = {
            p.relative_to(bundle).as_posix()
            for p in bundle.rglob("*")
            if p.is_file() and p.name != "manifest.json"
        }
        assert {e["path"] for e in doc["files"]} == roster
        for entry in doc["files"]:
            raw = (bundle / entry["path"]).read_bytes()
            assert entry["bytes"] == len(raw) and entry["sha256"] == hashlib.sha256(raw).hexdigest()
        text = (bundle / "Definitions.lean").read_text()
        assert not re.search(r"\b(sorry|axiom)\b", text)
        obligations = json.loads((bundle / "obligations.json").read_bytes())
        assert len(obligations["constraints"]) == 4
        assert all(e["status"] == "unproved" for e in obligations["constraints"])


def test_corpus_integrity():
    validate_corpus(CORPUS)


def test_case_answer_bijection():
    assert len(CASES) == len(ANSWERS) == 508
    assert sum(r["lane"] == "proof" for r in CASES) == 12
    assert sum(r["lane"] == "default" for r in CASES) == 496


@pytest.mark.parametrize("mutation", ["answer", "missing", "extra", "symlink", "golden", "schema"])
def test_dirty_corpus_is_rejected(tmp_path, mutation):
    root = tmp_path / "copy"
    shutil.copytree(CORPUS, root)
    p = root / "answers.json"
    if mutation == "answer":
        doc = json.loads(p.read_bytes())
        doc["cases"][0]["exit_code"] = 4
        p.write_text(json.dumps(doc))
    elif mutation == "missing":
        (root / "dispatch/base/model.orm.json").unlink()
    elif mutation == "extra":
        (root / "unlisted.json").write_text("{}")
    elif mutation == "symlink":
        p.unlink()
        p.symlink_to(CORPUS / "answers.json")
    elif mutation == "golden":
        (root / "dispatch/golden/Definitions.lean").write_text("def c0 := True\n")
    else:
        (root / "wire.schema.json").write_text("{}")
    with pytest.raises(AssertionError):
        validate_corpus(root)


def test_dirty_observation_fails():
    expected = next(iter(ANSWERS.values()))
    good = {k: copy.deepcopy(v) for k, v in expected.items() if k != "id"}
    assert_answer(good, expected)
    good["exit_code"] = 4
    with pytest.raises(AssertionError):
        assert_answer(good, expected)
    good["exit_code"] = False
    with pytest.raises(AssertionError):
        assert_answer(good, expected)


def test_answer_key_is_separate():
    assert "answers.json" in (CORPUS / "README.md").read_text()
    assert all(not set(row) & {"expected", "exit_code", "answer", "result"} for row in CASES)


@pytest.mark.parametrize(
    "key", ["manifest", "obligations", "source_map", "result", "compile_result"]
)
def test_wire_is_closed(key):
    validator = Draft202012Validator({**SCHEMA, "$ref": "#/$defs/" + key})
    assert validator.schema["$defs"][key]["additionalProperties"] is False
    if key in {"manifest", "obligations", "source_map"}:
        name = "source-map" if key == "source_map" else key
        good = json.loads((CORPUS / "dispatch/golden" / (name + ".json")).read_bytes())
    else:
        good = {
            "version": 1,
            "kind": "lean-export-result",
            "exit_code": 0,
            "status": "exported",
            "reason": None,
            "assurance": "none",
            "proof_status": "unproved",
            "counts": {k: 0 for k in SCHEMA["$defs"][key]["properties"]["counts"]["properties"]},
        }
        if key == "compile_result":
            good["kind"] = "lean-compile-result"
            good.update(
                tool={"version": None, "raw_sha256": None},
                definitions={
                    "attempted": False,
                    "native_exit": None,
                    "status": "not-attempted",
                    "elapsed_seconds": 0,
                },
                stubs={
                    "attempted": False,
                    "native_exit": None,
                    "status": "not-attempted",
                    "elapsed_seconds": 0,
                },
            )
    validator.validate(good)
    for mutation in [{"version": True}, {"version": 2}, {"extra": True}]:
        bad = {**copy.deepcopy(good), **mutation}
        assert list(validator.iter_errors(bad))

