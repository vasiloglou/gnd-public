"""OS3 offline admission, loss accounting and round-trip controls."""

from __future__ import annotations

import copy
import hashlib
import json
from collections import Counter
from pathlib import Path

import pytest
from support.cli_runner import run_main

from gnd.diff import diff_models
from gnd.export.ossie import render_ossie
from gnd.input_policy import MAX_BYTES
from gnd.model import json_document, load_model_bytes, parse_model_document
from gnd.ossie_import import OssieImportError, plan_ossie_import
from gnd.terms import uses_temporal

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / ".gnd-planning/milestones/ossie-interchange/evidence"
FLIGHTS = EVIDENCE / "OS3/flights.ontology.yaml"
REFUSED = json.loads((EVIDENCE / "OS3/refused-census-pointers.json").read_bytes())
CENSUS = [
    path for path in (EVIDENCE / "OS0/revised/census.txt").read_text().splitlines()
    if not path.startswith("src/gnd/examples/expense/teams/")
]


def _write(path, document):
    path.write_text(json.dumps(document))
    return path


def _companions(path):
    return Path(str(path) + ".gnd.json"), Path(str(path) + ".loss.json")


def _export(source, out):
    fmt = "yaml" if out.suffix == ".yaml" else "json"
    bundle = render_ossie(source, output_format=fmt)
    sidecar, report = _companions(out)
    out.write_bytes(bundle.document)
    sidecar.write_bytes(bundle.sidecar)
    report.write_bytes(bundle.loss_report)
    return sidecar, report


@pytest.mark.parametrize("relative", CENSUS)
def test_census_round_trip(tmp_path, relative):
    path = tmp_path / ("ontology.json" if relative.endswith(".json") else "ontology.yaml")
    source = ROOT / relative
    _export(source, path)
    actual = plan_ossie_import(path)
    original = json_document(parse_model_document(source.read_bytes(), source=source))
    expected = copy.deepcopy(original)
    losses = REFUSED.get(relative, {})
    for pointer in losses.get("subtree_roots", ()):
        *parents, key = pointer[1:].split("/")
        cursor = expected
        for parent in parents:
            cursor = cursor[int(parent)] if isinstance(cursor, list) else cursor[parent]
        assert cursor.pop(key)
    assert json.loads(actual.model) == expected
    report = json.loads(actual.loss_report)
    assert report["document_sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()
    assert report["dispositions"] == json.loads(_companions(path)[1].read_bytes())["dispositions"]
    assert {r["pointer"] for r in report["dispositions"] if r["disposition"] == "refused"} == set(
        losses.get("refused_pointers", ())
    )

    expected_model = load_model_bytes(json.dumps(expected).encode(), source="expected.orm.json")
    restored = load_model_bytes(actual.model, source="restored.orm.json")
    if not uses_temporal(expected_model):
        diff = diff_models(expected_model, restored, synthesize=False)
        assert diff["model_a_digest"] == diff["model_b_digest"]


@pytest.fixture
def bundle(tmp_path):
    path = tmp_path / "ontology.json"
    source = tmp_path / "source.orm.json"
    _write(source, {
        "version": 1,
        "object_types": [{"id": "code", "name": "Code", "kind": "value", "primitive": "String"}],
        "fact_types": [{
            "id": "valid", "reading": "{Code} is valid",
            "roles": [{"object_type": "code", "role_name": "code"}],
        }],
    })
    sidecar, report = _export(source, path)
    return path, sidecar, report


def _assert_refusal(path, rule):
    with pytest.raises(OssieImportError) as caught:
        plan_ossie_import(path)
    assert caught.value.rule_id == f"ossie-import:{rule}"


def test_binding_order_and_closed_messages(bundle):
    path, sidecar, report = bundle
    document = json.loads(path.read_bytes())
    metadata = json.loads(sidecar.read_bytes())
    malformed = dict(metadata, elements="private-value", document_sha256="0" * 64)
    _write(sidecar, malformed)
    _write(path, dict(document, ontology="private-value"))
    _assert_refusal(path, "schema")
    wrong_reference = copy.deepcopy(document)
    wrong_reference["ontology"][0]["relationships"][0]["roles"] = [{"concept": "Unknown"}]
    _write(path, wrong_reference)
    _assert_refusal(path, "reference")
    _write(path, document)
    _assert_refusal(path, "binding")

    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    _write(sidecar, dict(malformed, document_sha256=digest))
    _assert_refusal(path, "report-binding")
    report.unlink()
    _assert_refusal(path, "sidecar-entry")


@pytest.mark.parametrize("kind", ("duplicate", "escape", "sparse", "missing-parent", "copy-object"))
def test_invalid_sidecar_pointers(bundle, kind):
    path, sidecar, report = bundle
    report.unlink()
    metadata = json.loads(sidecar.read_bytes())
    group = metadata["elements"][""]
    if kind == "duplicate":
        metadata["elements"]["duplicate"] = {"": {"kind": "object"}}
    elif kind == "escape":
        group["/~2"] = {"kind": "literal", "value": 1}
    elif kind == "sparse":
        group["/object_types/999"] = {"kind": "literal", "value": 1}
    elif kind == "missing-parent":
        group["/missing/child"] = {"kind": "literal", "value": 1}
    else:
        group["/version"] = {"kind": "copy", "from": "/ontology/0"}
    _write(sidecar, metadata)
    _assert_refusal(path, "sidecar-entry" if kind == "copy-object" else "sidecar-pointer")


@pytest.mark.parametrize(
    ("suffix", "raw"),
    [
        ("yaml", b"x: &saved [0]\ny: *saved\n"),
        ("yaml", b"name: A\nname: B\n"),
        ("json", b'{"x": 0, "x": 1}'),
        ("json", b'{"x": NaN}'),
        ("json", b'{"x": "\\ud800"}'),
        ("json", b"[" * 70 + b"]" * 70),
        ("json", b"\xff"),
    ],
)
def test_hostile_syntax_refuses_before_schema(tmp_path, suffix, raw):
    path = tmp_path / f"ontology.{suffix}"
    path.write_bytes(raw)
    _assert_refusal(path, "syntax")


@pytest.mark.parametrize(("part", "rule"), [(0, "input-size"), (1, "sidecar-input-size"), (2, "report-input-size")])
def test_each_reader_caps_input_before_parsing(bundle, part, rule):
    with bundle[part].open("wb") as stream:
        stream.truncate(MAX_BYTES + 1)
    _assert_refusal(bundle[0], rule)


def test_sidecar_without_default_report_and_final_gnd_admission(bundle):
    path, sidecar, report = bundle
    report.rename(report.with_name("custom-report.json"))
    result = plan_ossie_import(path)
    assert {r["disposition"] for r in json.loads(result.loss_report)["dispositions"]} == {"extension"}
    metadata = json.loads(sidecar.read_bytes())
    metadata["elements"][""]["/version"] = {"kind": "literal", "value": -1}
    _write(sidecar, metadata)
    _assert_refusal(path, "model")


def test_report_must_account_for_all_retained_pointers(bundle):
    path, _, report = bundle
    value = json.loads(report.read_bytes())
    value["dispositions"].pop()
    _write(report, value)
    _assert_refusal(path, "report-pointer")


def test_dangling_sidecar_is_a_refusal(bundle):
    path, sidecar, _ = bundle
    sidecar.unlink()
    sidecar.symlink_to("absent")
    _assert_refusal(path, "sidecar-input")


def test_pinned_flights_foreign_provenance_and_losses(tmp_path):
    result = plan_ossie_import(FLIGHTS)
    document = json.loads(result.model)
    rows = json.loads(result.loss_report)["dispositions"]
    assert len(rows) == len({row["pointer"] for row in rows})
    assert Counter(row["disposition"] for row in rows).keys() == {"native", "refused"}
    assert {c["name"] for c in document["object_types"]} >= {"Airport", "State", "Carrier"}
    constraints = [c for f in document["fact_types"] for c in f.get("constraints", ())]
    assert len(constraints) >= 10
    assert all(
        c["source"] == "imported"
        and c["status"] == "proposed"
        and c["provenance"]["commit"] == "ee89dbdc2844d8b7d293ed42c8613928bb99505f"
        and c["provenance"]["artifact"] == "examples/flights.ontology.yaml"
        and c["provenance"]["anchor"].startswith("multiplicity: ")
        for c in constraints
    )
    copy_path = tmp_path / "different.yaml"
    copy_path.write_bytes(FLIGHTS.read_bytes() + b"\n")
    foreign = plan_ossie_import(copy_path)
    assert all("constraints" not in f for f in json.loads(foreign.model)["fact_types"])
    assert any(
        r["pointer"].endswith("/multiplicity") and r["disposition"] == "refused"
        for r in json.loads(foreign.loss_report)["dispositions"]
    )


def test_cli_publication_collision_and_exact_refusal(bundle, tmp_path):
    path, _, _ = bundle
    out = tmp_path / "restored.orm.json"
    report = tmp_path / "custom.json"
    cmd = ["import", "ossie", str(path), "--out", str(out), "--loss-report", str(report)]
    report.write_bytes(b"occupied")
    collision = run_main(cmd)
    assert collision.returncode == 11 and not out.exists()
    assert report.read_bytes() == b"occupied"
    report.unlink()

    ok = run_main(cmd)
    assert ok.returncode == 0, ok.stderr
    assert out.read_bytes() == plan_ossie_import(path).model
    assert report.read_bytes() == plan_ossie_import(path).loss_report
    report.unlink()
    assert run_main(cmd).returncode == 11
    assert not report.exists()

    path.write_text('{"untrusted secret": "value"}')
    refusal = run_main(cmd)
    assert refusal.returncode == 3
    assert refusal.stderr == b"ossie-import:schema\n"
    assert not report.exists()


def test_lossless_bundle_requires_restored_source_identity(bundle):
    path, sidecar, _ = bundle
    metadata = json.loads(sidecar.read_bytes())
    metadata["elements"]["code"]["/object_types/0/primitive"] = {
        "kind": "literal", "value": "Integer",
    }
    _write(sidecar, metadata)
    _assert_refusal(path, "model-identity")


def test_import_pins_offline_core_reference():
    from importlib.resources import files

    schema = files("gnd").joinpath("schema", "ossie")
    pin = json.loads(schema.joinpath("PINNED.json").read_bytes())
    reference = pin["core_reference"]
    assert reference["upstream_path"] == "core-spec/ossie-schema.json"
    assert reference["sha256"] == hashlib.sha256(schema.joinpath("core-spec.json").read_bytes()).hexdigest()
    assert hashlib.sha256(FLIGHTS.read_bytes()).hexdigest() == (
        "821d850f66098b2bb3ed8888e853a287627bb1eec676c2a7a190680d0ca89e87"
    )


def test_export_bounds_all_import_envelopes(bundle, monkeypatch):
    from gnd.export import ossie

    path, sidecar, report = bundle
    assert max(path.stat().st_size, sidecar.stat().st_size) < report.stat().st_size
    monkeypatch.setattr(ossie, "MAX_BYTES", report.stat().st_size - 1)
    with pytest.raises(ossie.OssieInputError, match="ossie:output-size"):
        render_ossie(path.with_name("source.orm.json"), output_format="json")


def test_reference_cycle_and_inherited_identifier(bundle, tmp_path):
    path, _, _ = bundle
    document = json.loads(path.read_bytes())
    document["ontology"][0]["extends"] = ["Code"]
    _write(path, document)
    _assert_refusal(path, "cycle")

    foreign = tmp_path / "foreign.json"
    document["ontology"] = [
        {"concept": "Code", "type": "ValueType", "extends": ["String"]},
        {
            "concept": "Root", "type": "EntityType", "identify_by": ["number"],
            "relationships": [
                {"name": "number", "roles": [{"concept": "Code"}], "verbalizes": ["{Root} has {Code}"]},
            ],
        },
        {"concept": "Child", "type": "EntityType", "extends": ["Root"], "identify_by": ["number"]},
    ]
    _write(foreign, document)
    result = plan_ossie_import(foreign)
    concepts = {concept["id"]: concept for concept in json.loads(result.model)["object_types"]}
    assert concepts["child"]["subtype_of"] == ["root"]
    rows = {r["pointer"]: r for r in json.loads(result.loss_report)["dispositions"]}
    assert rows["/ontology/2/identify_by/0"]["disposition"] == "refused"
