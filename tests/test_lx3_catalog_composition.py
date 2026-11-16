"""Catalog-backed composition, checking and independent witness replay."""
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
from gnd.composition import CompositionError, parse_record
from gnd.model import load_model, parse_model_document
from gnd.witness.io import certificate_shape

ROOT = Path(__file__).resolve().parent.parent
DISPATCH = ROOT / "tests/fixtures/reference-corpus/dispatch"
EXPECTED = json.loads((ROOT / "tests/fixtures/lx3-catalog-composition/expected.json").read_bytes())
CATALOG = EXPECTED["catalog_fact"]
SUBJECT = "dispatch_subject_warehouse"
ELIGIBLE = "dispatch_eligible_product"
PROVENANCE = {
    "source": "explicit", "status": "confirmed", "modality": "alethic",
    "provenance": {"user_quote": "Use the fixed warehouse catalog."},
}


def write(path, obj):
    path.write_bytes(canonical_json_bytes(obj))


def read(path):
    return json.loads(path.read_bytes())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def role(fact_type, name):
    return {"fact_type": fact_type, "role": name}


def source(directory, model, name, facts, document):
    folder = directory / name
    folder.mkdir(parents=True)
    doc = folder / "document.txt"
    doc.write_bytes(document.encode("utf-8"))
    pop = folder / "population.json"
    write(pop, {"population": {"model": "model.orm.json", "model_id": model.model_id,
                               "source": "fixture", "covers": sorted(facts)},
                "instances": {}, "facts": facts})
    anchors = []
    for fact_type, rows in facts.items():
        for row in rows:
            for role_name, value in row.items():
                start = document.index(value)
                anchors.append({
                    "fact_key": {"fact_type": fact_type, "roles": row}, "role": role_name,
                    "span": {"start": start, "end": start + len(value)}, "occurrence": 0,
                    "excerpt_sha256": hashlib.sha256(value.encode("utf-8")).hexdigest(),
                })
    write(folder / "population.json.anchors.json", {
        "schema_version": 2, "population_sha256": digest(pop),
        "vocabulary_digest": vocabulary_digest(model), "document_sha256": digest(doc), "anchors": anchors,
    })


def setup(tmp_path, *, includes=True, dependency=False):
    top = tmp_path.resolve()
    dispatch = DISPATCH / "model.orm.yaml"
    standalone = parse_model_document(dispatch.read_bytes(), source=dispatch)
    catalog = top / "catalog.json"
    shutil.copyfile(DISPATCH / "references/catalog.pop.json", catalog)
    data = read(catalog)
    data["population"]["model"] = "model.orm.json"
    write(catalog, data)
    vocabulary = {"version": 2, "source": standalone["source"], "object_types": standalone["object_types"],
                  "fact_types": standalone["fact_types"], "constraints": []}
    for fact in vocabulary["fact_types"]:
        if fact["id"] == CATALOG:
            fact["constraints"] = [{"type": "uniqueness", "roles": ["warehouse"], **PROVENANCE}]
        if fact["id"] == SUBJECT:
            fact["constraints"] = [{"type": "anchored", "role": "warehouse", **PROVENANCE}]
    vocabulary_path = top / "vocabulary.orm.json"
    write(vocabulary_path, vocabulary)
    model = top / "model.orm.json"
    left, right = (CATALOG, SUBJECT) if dependency else (SUBJECT, CATALOG)
    subset = {"id": "dispatch_catalog_membership", "type": "subset",
              "subset_role_seq": [role(left, "warehouse")], "superset_role_seq": [role(right, "warehouse")],
              **PROVENANCE}
    derived = {
        "id": ELIGIBLE, "reading": "{Shipment} is eligible for {Product}",
        "roles": [{"role_name": "shipment", "object_type": "dispatch_shipment"},
                  {"role_name": "product", "object_type": "dispatch_product"}],
        "derivation": "derived", "derivation_rule": {
            "body": [{"fact_type": SUBJECT, "bind": {"shipment": "$s", "warehouse": "$w"}},
                     {"fact_type": CATALOG, "bind": {"warehouse": "$w", "product": "$p"}}],
            "head": {"shipment": "$s", "product": "$p"},
        },
    }
    root = {
        **vocabulary, "version": 5 if includes else 4, "constraints": [subset],
        "model_id": standalone["model_id"],
        "fact_types": [derived] if includes else [*vocabulary["fact_types"], derived],
        "reference_populations": [{"id": "catalog", "path": catalog.name, "sha256": digest(catalog),
                                  "fact_types": [CATALOG]}],
    }
    if includes:
        root["object_types"] = []
        root["includes"] = [{"id": "dispatch", "path": vocabulary_path.name, "sha256": digest(vocabulary_path)}]
    write(model, root)
    selected = load_model(model)
    sources = top / "sources"
    source(sources, selected, "first", {SUBJECT: [{"shipment": "SHIP-17", "warehouse": "A Depot"}]},
           "SHIP-17 is assigned to A Depot.")
    source(sources, selected, "second", {SUBJECT: [{"shipment": "SHIP-18", "warehouse": "WH-A"}]},
           "SHIP-18 is assigned to WH-A.")
    write(sources / "manifest.json", {
        "schema": "gnd-composition-manifest/1", "sources": EXPECTED["sources"],
        "renamings": [{"source": "first", "fact_type": SUBJECT, "role": "warehouse",
                       "from": "A Depot", "to": "WH-A"}],
        "deduplications": "identical-rows", "scope_tags": [],
    })
    targets = top / "targets.json"
    write(targets, {"version": 1, "targets": [{"fact_type": ELIGIBLE, "tuple": [
        {"primitive": "String", "value": value} for value in ("SHIP-17", "GEAR-2")
    ]}]})
    return model, sources, catalog, targets


def run(capsys, *args):
    capsys.readouterr()
    code = main(list(map(str, args)))
    output = capsys.readouterr()
    return code, output.out, output.err


def composition(tmp_path, capsys, *, includes=True):
    model, sources, catalog, targets = setup(tmp_path, includes=includes)
    population, record = model.with_name("population.json"), model.with_name("record.json")
    code, output, error = run(capsys, "compose", model, sources, "--out", population, "--record", record)
    assert code == 0, output + error
    return model, sources, catalog, targets, population, record


def check(capsys, model, sources, population, record, *extra):
    return run(capsys, "check", model, population, "--composition", record, "--sources", sources,
               "--format", "json", *extra)


def witness(capsys, model, population, record, targets, *extra):
    return run(capsys, "witness", model, population, "--targets", targets, "--composition", record,
               "--raw", *extra)


def replay(capsys, model, population, record, certificate):
    code, output, error = run(capsys, "replay", model, population, certificate, "--composition", record, "--raw")
    assert output, error
    result = json.loads(output)
    return [code, result["reason"] or (result["results"][0]["reason"] if code else None)]


def test_composed_check_binds_catalog_and_candidate_sources(tmp_path, capsys):
    model, sources, catalog, _, population, record = composition(tmp_path, capsys)
    assert read(population)["facts"] == {SUBJECT: [
        {"shipment": "SHIP-17", "warehouse": EXPECTED["candidate_warehouse"]},
        {"shipment": "SHIP-18", "warehouse": EXPECTED["candidate_warehouse"]},
    ]}
    lineage = read(record)
    assert lineage["schema"] == EXPECTED["record_schema"]
    assert lineage["references"] == [{"id": EXPECTED["catalog"], "raw_sha256": digest(catalog)}]
    assert [row["id"] for row in lineage["sources"]] == EXPECTED["sources"]
    assert [row["sources"][0]["source"] for row in lineage["facts"]] == EXPECTED["sources"]
    assert [row["renamings"] for row in lineage["facts"]] == [[0], []]
    assert {row["fact_type"] for row in lineage["facts"]} == {SUBJECT}
    assert parse_record(record.read_bytes()) == lineage
    jsonschema.validate(lineage, read(ROOT / "src/gnd/composition.schema.json"))
    code, output, error = check(capsys, model, sources, population, record)
    assert code == 0, output + error
    report = json.loads(output)
    assert report["report"]["composition"]["record_sha256"] == digest(record)
    assert report["report"]["counts"]["pass"] == 3
    assert {row["origin"]["kind"] for row in report["occurrence_origins"]} == {"candidate", "reference"}
    # With the same candidate bytes and no catalog, the subset must fail.
    root = read(model)
    root.pop("reference_populations")
    write(model, root)
    code, output, _ = run(capsys, "check", model, population, "--format", "json")
    assert code == 1
    assert json.loads(output)["counts"]["fail"] == 1


@pytest.mark.parametrize("defect", ["dependency", "key", "stale"])
def test_catalog_is_refused_before_invalid_manifest(tmp_path, defect):
    model, sources, catalog, _ = setup(tmp_path, dependency=defect == "dependency")
    if defect == "key":
        doc = read(catalog)
        doc["facts"][CATALOG].append({"warehouse": "WH-A", "product": "OTHER"})
        write(catalog, doc)
        root = read(model)
        root["reference_populations"][0]["sha256"] = digest(catalog)
        write(model, root)
    elif defect == "stale":
        catalog.write_bytes(catalog.read_bytes() + b" ")
    (sources / "manifest.json").write_text("{}")
    result = api.compose(model, sources)
    assert result["exit_code"] == 3
    key = {"dependency": "catalog_candidate_dependency", "key": "catalog_key_conflict", "stale": "catalog_stale"}[defect]
    assert EXPECTED[key] in result["error"]["message"]


@pytest.mark.parametrize("axis", ["catalog", "source", "record-roster", "record-bytes"])
def test_consumers_refuse_independent_stale_bindings(tmp_path, capsys, axis):
    model, sources, catalog, targets, population, record = composition(tmp_path, capsys)
    certificate = model.with_name("witness.json")
    assert witness(capsys, model, population, record, targets, "--out", certificate)[0] == 0
    preserved = digest(population)
    if axis == "catalog":
        catalog.write_bytes(catalog.read_bytes() + b" ")
    elif axis == "source":
        doc = sources / "first/document.txt"
        doc.write_bytes(doc.read_bytes() + b" ")
    elif axis == "record-roster":
        stale = read(record)
        stale["references"][0]["raw_sha256"] = "0" * 64
        write(record, stale)
    else:
        changed = read(record)
        changed["scope_tags"].append({"source": "first", "tag": "stale"})
        write(record, changed)
    code, output, error = check(capsys, model, sources, population, record)
    assert code == 3, output + error
    message = {"catalog": EXPECTED["catalog_stale"], "source": "anchor:", "record-roster": EXPECTED["record_catalog_stale"],
               "record-bytes": "scope_tags"}[axis]
    assert message in output + error
    if axis in {"catalog", "record-roster"}:
        code, output, _ = witness(capsys, model, population, record, targets)
        assert [code, json.loads(output)["reason"]] == EXPECTED["binding_stale"]
    if axis != "source":
        assert replay(capsys, model, population, record, certificate) == EXPECTED["binding_stale"]
    assert digest(population) == preserved


@pytest.mark.parametrize("axis", ["authentic", "candidate-to-catalog", "catalog-to-candidate", "model", "catalog-pin"])
def test_mixed_proof_origin_axes(tmp_path, capsys, axis):
    model, _, _, targets, population, record = composition(tmp_path, capsys)
    certificate = model.with_name("witness.json")
    code, output, error = witness(capsys, model, population, record, targets, "--out", certificate)
    assert code == 0, output + error
    proof = read(certificate)
    assert proof["version"] == EXPECTED["certificate_version"]
    assert proof["binding"]["composition_sha256"] == digest(record)
    candidates = [n for n in proof["nodes"] if n["kind"] == "base" and n["origin"]["kind"] == "candidate"]
    refs = [n for n in proof["nodes"] if n["kind"] == "base" and n["origin"]["kind"] == "reference"]
    assert len(candidates) == len(refs) == 1
    candidate, reference = candidates[0], refs[0]
    assert candidate["sources"] == [{"source": "first", "fact_type": SUBJECT, "fact_index": 0}]
    assert reference["origin"] == {"kind": "reference", "reference_id": "catalog", "fact_index": 0}
    assert reference["sources"] == []
    assert {n["model_origin"]["origin"] for n in proof["nodes"]} == {"model", "includes[dispatch]"}
    for schema in ("src/gnd/schema/witness.schema.json", "src/gnd/skills/gnd-export/references/witness.schema.json"):
        jsonschema.validate(proof, read(ROOT / schema))
    jsonschema.validate(json.loads(output), read(ROOT / "src/gnd/schema/witness-result.schema.json"))
    if axis == "authentic":
        assert replay(capsys, model, population, record, certificate) == [0, None]
        return
    if axis == "candidate-to-catalog":
        candidate["origin"] = dict(reference["origin"])
        candidate["sources"] = []
    elif axis == "catalog-to-candidate":
        reference["origin"] = dict(candidate["origin"])
        reference["sources"] = candidate["sources"]
    elif axis == "model":
        reference["model_origin"]["origin"] = "model"
    else:
        proof["binding"]["references"][0]["raw_sha256"] = "0" * 64
    certificate_shape(proof)
    write(certificate, proof)
    assert replay(capsys, model, population, record, certificate) == EXPECTED[
        "binding_stale" if axis == "catalog-pin" else "proof_invalid"
    ]


def test_include_free_catalog_witness_has_no_flattening_binding(tmp_path, capsys):
    model, _, _, targets, population, record = composition(tmp_path, capsys, includes=False)
    certificate = model.with_name("witness.json")
    assert witness(capsys, model, population, record, targets, "--out", certificate)[0] == 0
    proof = read(certificate)
    assert proof["version"] == EXPECTED["certificate_version"]
    assert "flattening_sha256" not in proof["binding"]
    assert all("model_origin" not in node for node in proof["nodes"])
    assert replay(capsys, model, population, record, certificate) == [0, None]


def test_composition_override_and_catalog_write_collisions(tmp_path, capsys):
    model, sources, catalog, targets = setup(tmp_path)
    population, record = model.with_name("population.json"), model.with_name("record.json")
    original = catalog.read_bytes()
    assert run(capsys, "compose", model, sources, "--out", catalog, "--record", record)[0] == 64
    assert catalog.read_bytes() == original
    assert run(capsys, "compose", model, sources, "--out", population, "--record", record)[0] == 0
    code, output, error = check(capsys, model, sources, population, record, "--anchors",
                                sources / "first/population.json.anchors.json")
    assert code == 3
    assert "composition cannot be combined with anchors" in output + error
    assert witness(capsys, model, population, record, targets, "--reference-root", sources)[0] == 64


def test_catalog_roster_is_closed_and_capped(tmp_path, capsys):
    _, _, _, _, _, record = composition(tmp_path, capsys)
    data = read(record)
    data["references"] *= 33
    with pytest.raises(CompositionError):
        parse_record(canonical_json_bytes(data))
    data["references"] = [{"id": "catalog", "raw_sha256": "0" * 64, "owner": "input"}]
    with pytest.raises(CompositionError):
        parse_record(canonical_json_bytes(data))


def test_reference_free_artifact_bytes_match_predecessor(tmp_path, capsys):
    model, sources, _, _ = setup(tmp_path)
    root = read(model)
    del root["reference_populations"]
    write(model, root)
    population, record = model.with_name("population.json"), model.with_name("record.json")
    assert run(capsys, "compose", model, sources, "--out", population, "--record", record)[0] == 0
    assert digest(population) == EXPECTED["legacy_population_sha256"]
    assert digest(record) == EXPECTED["legacy_record_sha256"]


def test_catalog_does_not_discharge_candidate_resolution(tmp_path):
    base = ROOT / "src/gnd/examples/literature/resolution"
    original = base / "model.orm.yaml"
    model = tmp_path / "model.orm.json"
    root = parse_model_document(original.read_bytes(), source=original)
    root["version"] = 4
    root["fact_types"].append({
        "id": "catalog_method", "reading": "{Method} is catalogued",
        "roles": [{"role_name": "method", "object_type": "method"}],
    })
    catalog = tmp_path / "catalog.json"
    write(catalog, {"population": {"model": model.name, "model_id": root["model_id"], "source": "fixture"},
                    "facts": {"catalog_method": [{"method": "TRACE"}]}})
    root["reference_populations"] = [{"id": "catalog", "path": catalog.name, "sha256": digest(catalog),
                                      "fact_types": ["catalog_method"]}]
    write(model, root)
    directory = tmp_path / "case"
    shutil.copytree(base / "cases/H-no-decision", directory)
    vocab = vocabulary_digest(load_model(model))
    for path in directory.glob("*/population.json.anchors.json"):
        sidecar = read(path)
        sidecar["vocabulary_digest"] = vocab
        write(path, sidecar)
    result = api.compose(model, directory)
    assert result["exit_code"] == 3
    assert result["error"]["message"] == EXPECTED["missing_resolution"]
