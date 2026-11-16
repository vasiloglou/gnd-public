"""Exercise include-model certificate provenance through witness and replay."""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

import jsonschema
import pytest

from gnd import api
from gnd.anchors import vocabulary_digest
from gnd.artifacts import canonical_json_bytes
from gnd.cli import main
from gnd.model import load_model
from gnd.witness.io import certificate_shape

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests/fixtures"
EXPECTED = json.loads((FIXTURES / "lx2-witness-flattening/expected.json").read_bytes())
DERIVED = {
    "id": "root_uses_component",
    "reading": "{Component} uses {Component} according to the root",
    "roles": [
        {"role_name": "using", "object_type": "component"},
        {"role_name": "used", "object_type": "component"},
    ],
    "derivation": "derived",
    "derivation_rule": {
        "body": [{"fact_type": "component_uses_component",
                  "bind": {"using": "$a", "used": "$b"}}],
        "head": {"using": "$a", "used": "$b"},
    },
}


def write(path, value):
    path.write_bytes(canonical_json_bytes(value))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dirs(tmp_path, *, derived=False):
    tmp_path = tmp_path.resolve()
    source = tmp_path / "root"
    shutil.copytree(FIXTURES / "lx1-flattening", source)
    model = source / "project.orm.json"
    if derived:
        root = json.loads(model.read_bytes())
        root["fact_types"] = [DERIVED]
        write(model, root)
    population = tmp_path / "candidate.json"
    facts = json.loads((source / "facts.json").read_bytes())
    write(population, {"population": {"model": model.name, "source": "fixture"}, "facts": facts})
    target = tmp_path / "target.json"
    write(target, {"version": 1, "targets": [
        {"fact_type": "root_uses_component" if derived else "component_uses_component",
         "tuple": [{"primitive": "String", "value": value} for value in ("a", "b")]}
    ]})
    certificate = tmp_path / "witness.json"
    return model, population, target, certificate


def make_artifacts(model, tmp_path, capsys):
    bundle = tmp_path.resolve() / "artifacts"
    assert main(["extract", str(model), "--out", str(bundle)]) == 0
    capsys.readouterr()
    return bundle / "project.orm.flat.orm.json", bundle / "project.orm.flattening.json"


def witness(paths, *options):
    model, population, target, certificate = paths
    return main(["witness", str(model), str(population), "--targets", str(target),
                 "--raw", "--out", str(certificate), *map(str, options)])


def replay(paths, capsys, *options):
    model, population, _, certificate = paths
    capsys.readouterr()
    code = main(["replay", str(model), str(population), str(certificate),
                 "--raw", *map(str, options)])
    result = json.loads(capsys.readouterr().out)
    return [code, result["reason"]]


def test_public_extract_witness_and_replay(tmp_path, capsys):
    paths = dirs(tmp_path)
    flat, record = make_artifacts(paths[0], tmp_path, capsys)
    args = ("--flat-model", flat, "--flattening-record", record)
    assert witness(paths, *args) == 0
    cert = json.loads(paths[3].read_bytes())
    assert cert["version"] == EXPECTED["version"]
    assert cert["binding"]["flattening_sha256"] == digest(record)
    assert cert["nodes"][0]["model_origin"]["origin"] == "includes[components]"
    assert replay(paths, capsys, *args) == [0, None]
    for name in ("src/gnd/schema/witness.schema.json",
                 "src/gnd/skills/gnd-export/references/witness.schema.json"):
        jsonschema.validate(cert, json.loads((ROOT / name).read_bytes()))


@pytest.mark.parametrize("axis", ["model", "fact", "binding", "schema"])
def test_each_origin_axis(tmp_path, capsys, axis):
    paths = dirs(tmp_path, derived=True)
    assert witness(paths) == 0
    assert replay(paths, capsys) == [0, None]
    cert = json.loads(paths[3].read_bytes())
    assert sorted({n["model_origin"]["origin"] for n in cert["nodes"]}) == EXPECTED["origin_sources"]
    node = next(n for n in cert["nodes"] if n["kind"] == "base")
    if axis == "model":
        node["model_origin"]["origin"] = "model"
    elif axis == "fact":
        node["origin"]["fact_index"] += 1
    elif axis == "binding":
        cert["binding"]["flattening_sha256"] = "0" * 64
    else:
        node["model_origin"]["extra"] = True
        with pytest.raises(ValueError):
            certificate_shape(cert)
    write(paths[3], cert)
    name = {"model": "forged", "fact": "forged", "binding": "stale", "schema": "invalid"}[axis]
    assert replay(paths, capsys) == EXPECTED[name]


@pytest.mark.parametrize("coordinate", ["root", "include", "flat", "record"])
def test_stale_projection_inputs(tmp_path, capsys, coordinate):
    paths = dirs(tmp_path)
    flat, record = make_artifacts(paths[0], tmp_path, capsys)
    args = ("--flat-model", flat, "--flattening-record", record)
    assert witness(paths, *args) == 0
    path = {"root": paths[0], "include": paths[0].parent / "components.orm.json",
            "flat": flat, "record": record}[coordinate]
    cert = json.loads(paths[3].read_bytes())
    cert["nodes"][0]["model_origin"]["origin"] = "model"
    write(paths[3], cert)
    path.write_bytes(path.read_bytes() + b" ")
    assert replay(paths, capsys, *args) == EXPECTED["stale"]


def test_reference_free_composition_proof(tmp_path, capsys):
    model, pop, target, certificate = dirs(tmp_path, derived=True)
    folder = tmp_path.resolve() / "sources" / "a"
    folder.mkdir(parents=True)
    document = "Component a uses component b. Both components have owner x.\n"
    facts = json.loads(pop.read_bytes())["facts"]
    (folder / "document.txt").write_text(document)
    source = folder / "population.json"
    source.write_bytes(pop.read_bytes())
    loaded = load_model(model)
    start = document.index(" a ") + 1
    write(folder / "population.json.anchors.json", {
        "schema_version": 2, "population_sha256": digest(source),
        "vocabulary_digest": vocabulary_digest(loaded),
        "document_sha256": digest(folder / "document.txt"),
        "anchors": [{
            "fact_key": {"fact_type": "component_uses_component",
                         "roles": facts["component_uses_component"][0]},
            "role": "using", "span": {"start": start, "end": start + 1},
            "occurrence": 0, "excerpt_sha256": hashlib.sha256(b"a").hexdigest(),
        }],
    })
    write(folder.parent / "manifest.json", {
        "schema": "gnd-composition-manifest/1", "sources": ["a"], "renamings": [],
        "deduplications": "identical-rows", "scope_tags": [],
    })
    record = tmp_path.resolve() / "composed.json"
    composed = tmp_path.resolve() / "composed.population.json"
    assert main(["compose", str(model), str(folder.parent), "--out", str(composed), "--record", str(record)]) == 0
    result = api.witness(model, composed, target, composition=record)
    assert result["exit_code"] == 0
    result_schema = json.loads((ROOT / "src/gnd/schema/witness-result.schema.json").read_bytes())
    jsonschema.validate(result, result_schema)
    cert = result["certificate"]
    assert cert["version"] == EXPECTED["version"]
    assert cert["binding"]["composition_sha256"] == digest(record)
    write(certificate, cert)
    paths = model, composed, target, certificate
    assert replay(paths, capsys, "--composition", record) == [0, None]
    base = next(node for node in cert["nodes"] if node["kind"] == "base")
    assert base["sources"] == [{"source": "a", "fact_type": "component_uses_component", "fact_index": 0}]
    base["sources"][0]["fact_index"] = 1
    write(certificate, cert)
    assert replay(paths, capsys, "--composition", record) == EXPECTED["forged"]


def test_unpaired_paths_refuse_at_cli(tmp_path, capsys):
    paths = dirs(tmp_path)
    flat, _ = make_artifacts(paths[0], tmp_path, capsys)
    assert witness(paths, "--flat-model", flat) == 64
    assert "requires" in capsys.readouterr().err


def test_legacy_composed_bytes_and_replay(tmp_path, monkeypatch):
    from test_witness_composition import gnd, produce

    model, _, population, record, _, certificate = produce(tmp_path.resolve(), monkeypatch)
    assert digest(certificate) == EXPECTED["legacy_composed_sha256"]
    assert gnd("replay", model, population, certificate, "--composition", record).returncode == 0


def test_flat_inputs_are_bounded(tmp_path, capsys):
    paths = dirs(tmp_path)
    flat, record = make_artifacts(paths[0], tmp_path, capsys)
    assert witness(paths) == 0
    with record.open("wb") as stream:
        stream.truncate(10 * 1024 * 1024 + 1)
    assert replay(paths, capsys, "--flat-model", flat, "--flattening-record", record) == EXPECTED["invalid"]
