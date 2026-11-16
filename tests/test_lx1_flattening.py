"""LX1 corpus-first extraction and verification through the public CLI."""
from __future__ import annotations

import copy
import hashlib
import json
import re
import shutil
from pathlib import Path

import pytest

from gnd.artifacts import canonical_json_bytes
from gnd.cli import main
from gnd.extract.projection import project
from gnd.extract.refscheme import applicable_set
from gnd.extract.vocabulary import render_verbalization
from gnd.model import load_model, load_model_bytes

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "lx1-flattening"
EXPECTED = json.loads((FIXTURE / "expected.json").read_bytes())
FIELD_ORDER = ("origin", "original_address", "composed_address", "element_id")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_doc(path: Path, document: dict) -> None:
    path.write_bytes(canonical_json_bytes(document))


def at(document: dict, address: str) -> dict:
    value = document
    for name, index in re.findall(r"\.([a-z_]+)\[(\d+)\]", address):
        value = value[name][int(index)]
    return value


@pytest.fixture
def inputs(tmp_path: Path) -> tuple[Path, Path]:
    source = tmp_path.resolve() / "source"
    shutil.copytree(FIXTURE, source)
    return source / "project.orm.json", tmp_path.resolve() / "bundle"


def extract(model: Path, bundle: Path) -> int:
    return main(["extract", str(model), "--out", str(bundle)])


@pytest.fixture
def handoff(inputs: tuple[Path, Path]) -> tuple[Path, Path, Path]:
    model, bundle = inputs
    assert extract(model, bundle) == 0
    index = json.loads((bundle / "project.artifacts.json").read_bytes())
    population = model.parent / "pop.json"
    write_doc(population, {
        "population": index["header_template"],
        "facts": json.loads((model.parent / "facts.json").read_bytes()),
    })
    document = model.parent / "document.txt"
    write_doc(population.with_suffix(".extraction.json"), {
        "schema_version": 1,
        "model": model.name,
        "model_sha256": sha(model),
        "population": population.name,
        "population_sha256": sha(population),
        "document": document.name,
        "document_sha256": sha(document),
        "projection_sha256": sha(bundle / "project.projection.schema.json"),
        "skill": "gnd-extract",
        "skill_version": "1",
        "executing_model": "fixture",
    })
    return model, bundle, population


def verify(handoff: tuple[Path, Path, Path]) -> int:
    model, bundle, population = handoff
    return main(["verify", str(model), str(population),
                 "--artifacts", str(bundle), "--format", "json"])


def test_public_extraction_and_origins(handoff: tuple[Path, Path, Path]) -> None:
    model, bundle, _ = handoff
    assert verify(handoff) == 0
    index = json.loads((bundle / "project.artifacts.json").read_bytes())
    flat = bundle / "project.flat.orm.json"
    record = bundle / "project.flattening.json"
    assert index["flattening"] == {"flat_model": flat.name, "record": record.name}
    assert index["model"]["sha256"] == sha(model)
    assert index["artifacts"][flat.name]["sha256"] == sha(flat)
    assert index["artifacts"][record.name]["sha256"] == sha(record)

    authors = {"model": json.loads(model.read_bytes())}
    for pin in authors["model"]["includes"]:
        authors[f"includes[{pin['id']}]"] = json.loads(
            (model.parent / pin["path"]).read_bytes()
        )
    payload = json.loads(record.read_bytes())
    assert payload["format"] == "gnd-flattening/1"
    assert payload["root_sha256"] == sha(model)
    assert payload["flat_model_sha256"] == sha(flat)
    assert payload["includes"] == authors["model"]["includes"]
    rows = [[entry[field] for field in FIELD_ORDER] for entry in payload["origins"]]
    assert rows == sorted(EXPECTED["origins"], key=lambda entry: entry[2])
    flattened = json.loads(flat.read_bytes())
    for origin, source, destination, id_ in rows:
        left, right = at(authors[origin], source), at(flattened, destination)
        if ".constraints[" not in destination and destination.startswith("$.fact_types"):
            left = {k: v for k, v in left.items() if k != "constraints"}
            right = {k: v for k, v in right.items() if k != "constraints"}
        assert left == right
        assert right.get("id") == id_
    loaded, reopened = load_model(model), load_model_bytes(flat.read_bytes(), source=flat)
    assert project(loaded) == project(reopened)
    assert applicable_set(loaded) == applicable_set(reopened)
    assert render_verbalization(loaded) == render_verbalization(reopened)
    first = {p.name: p.read_bytes() for p in bundle.iterdir()}
    assert extract(model, bundle) == 0
    assert first == {p.name: p.read_bytes() for p in bundle.iterdir()}


@pytest.mark.parametrize("which", EXPECTED["stale"])
def test_stale_coordinates(handoff, capsys, which: str) -> None:
    model, bundle, _ = handoff
    paths = {
        "root": model,
        "include": model.parent / "components.orm.json",
        "flat": bundle / "project.flat.orm.json",
        "record": bundle / "project.flattening.json",
    }
    capsys.readouterr()
    if which in {"root", "include"}:
        # Pair a stale flat input with either higher-precedence defect.
        paths["flat"].write_bytes(paths["flat"].read_bytes() + b" ")
    path = paths[which]
    path.write_bytes(path.read_bytes() + b" ")
    assert verify(handoff) == 3
    payload = json.loads(capsys.readouterr().out)
    assert EXPECTED["stale"][which] in payload["extraction"]["reason"]


@pytest.mark.parametrize("downgrade", [False, True])
def test_index_cannot_authenticate_changed_projection(handoff, capsys, downgrade) -> None:
    _, bundle, _ = handoff
    index_path = bundle / "project.artifacts.json"
    index = json.loads(index_path.read_bytes())
    flat = bundle / "project.flat.orm.json"
    record = bundle / "project.flattening.json"
    if downgrade:
        index.pop("flattening")
        index["artifacts"].pop(flat.name)
        index["artifacts"].pop(record.name)
    else:
        changed = json.loads(flat.read_bytes())
        changed["source"] = {"kind": "forged"}
        write_doc(flat, changed)
        binding = json.loads(record.read_bytes())
        binding["flat_model_sha256"] = sha(flat)
        write_doc(record, binding)
        for path in (flat, record):
            index["artifacts"][path.name]["sha256"] = sha(path)
    write_doc(index_path, index)
    capsys.readouterr()
    assert verify(handoff) == 3
    assert "extraction:binding-mismatch" in capsys.readouterr().out


@pytest.mark.parametrize("which", EXPECTED["include_refusals"])
def test_include_boundaries(inputs, capsys, which: str) -> None:
    model, bundle = inputs
    root = json.loads(model.read_bytes())
    pin = root["includes"][0]
    original = model.parent / pin["path"]
    child = copy.deepcopy(json.loads(original.read_bytes()))
    if which == "path":
        pin["path"] = "../escape.orm.json"
    elif which == "standalone":
        child["fact_types"][0]["roles"][0]["object_type"] = "absent"
    elif which == "nested":
        child["includes"] = []
    elif which == "references":
        child["reference_populations"] = []
    else:
        child["source"]["mode"] = "unattended"
    write_doc(original, child)
    pin["sha256"] = sha(original)
    write_doc(model, root)
    assert extract(model, bundle) == 3
    result = capsys.readouterr().out
    assert all(fragment in result for fragment in EXPECTED["include_refusals"][which])
    assert not bundle.exists()


@pytest.mark.parametrize("bad", [b"[]", b'{"model":1}', b'{"model":{},"model":{}}',
                                 b'{"model":NaN}', b"[" * 1024,
                                 b" " * (1024 * 1024 + 1)],
                         ids=["array", "scalar-model", "duplicate", "nan", "depth", "size"])
def test_hostile_indexes_refuse(handoff, capsys, bad: bytes) -> None:
    _, bundle, _ = handoff
    (bundle / "project.artifacts.json").write_bytes(bad)
    capsys.readouterr()
    assert verify(handoff) == 3
    result = json.loads(capsys.readouterr().out)
    assert result["issues"][0]["rule_id"] == "extraction:binding-mismatch"


def test_legacy_bundle_bytes(tmp_path, monkeypatch) -> None:
    from gnd.extract import service

    monkeypatch.setattr(service, "resolve_version", lambda: "0.3.1")
    monkeypatch.chdir(FIXTURE.parents[2])
    bundle = tmp_path / "legacy"
    assert main(["extract", "tests/fixtures/skeleton/model.orm.yaml",
                 "--out", str(bundle)]) == 0
    assert {p.name: sha(p) for p in bundle.iterdir()} == EXPECTED["legacy_bundle"]


def test_projection_time_bound(inputs) -> None:
    import subprocess
    import sys

    model, _ = inputs
    root = json.loads(model.read_bytes())
    extra = model.parent / root["includes"][1]["path"]
    child = json.loads(extra.read_bytes())
    child["object_types"] = [
        {"id": f"topic{index}", "name": f"Topic{index}", "kind": "value",
         "primitive": "String"}
        for index in range(1000)
    ]
    write_doc(extra, child)
    root["includes"][1]["sha256"] = sha(extra)
    write_doc(model, root)
    code = """
import json
import sys
from gnd.model import load_model
from gnd.model.flattening import flatten_model

model = load_model(sys.argv[1])
flat = flatten_model(model)
record = json.loads(flat.record_bytes)
assert len(record['origins']) == 1008
"""
    completed = subprocess.run(
        [sys.executable, "-c", code, str(model)],
        capture_output=True, text=True, timeout=5, check=False,
    )
    assert completed.returncode == 0, completed.stderr


def test_flat_wire_size_refusal(inputs, monkeypatch, capsys) -> None:
    from gnd.model import flattening

    model, bundle = inputs
    monkeypatch.setattr(flattening, "MAX_MODEL_BYTES", 100)
    assert extract(model, bundle) == 3
    assert "flattening" in capsys.readouterr().out
    assert not bundle.exists()


def test_temporal_extraction_refusal(tmp_path, capsys) -> None:
    from test_mc1_model_includes import split_existing

    temporal = FIXTURE.parent / "rc1-rule-ids" / "models" / "temporal.orm.yaml"
    model, _, _ = split_existing(tmp_path.resolve(), temporal)
    bundle = tmp_path / "bundle"
    assert extract(model, bundle) == 3
    assert "temporal" in capsys.readouterr().out
    assert not bundle.exists()
