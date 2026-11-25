"""SI3: corpus-bound Ossie identities and source round trips."""

import hashlib
import json
import time
from pathlib import Path

import pytest
from ruamel.yaml import YAML
from support.cli_runner import run_main
from test_ossie_external_oracle import oracle as oracle  # noqa: PLC0414 -- pytest fixture reexport

from gnd.export.ossie import render_ossie
from gnd.model import json_document, parse_model_document
from gnd.ossie_import import _NameGraph

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / ".gnd-planning/milestones/seeded-routes-and-identifiers/evidence/SI3"
ROWS = json.loads((EVIDENCE / "ontology-corpus.json").read_bytes())["models"]
OBJECTIFICATIONS = [
    ROOT / "src/gnd/examples/literature/assertions/model.orm.yaml",
    ROOT / "src/gnd/examples/literature/lineage/model.orm.yaml",
]


@pytest.mark.parametrize("row", ROWS, ids=lambda row: row["model"])
@pytest.mark.parametrize("output_format", ["json", "yaml"])
def test_changed_ontologies_and_bound_round_trip(row, output_format, tmp_path):
    source = ROOT / row["model"]
    expected = (EVIDENCE / row["fixture"]).read_bytes()
    assert hashlib.sha256(expected).hexdigest() == row["new_sha256"]
    ontology = tmp_path / f"ontology.{output_format}"
    result = run_main(["export", "ossie", str(source), "--format", output_format, "--out", str(ontology)])
    assert result.returncode == 0, result.stdout + result.stderr
    if output_format == "json":
        assert ontology.read_bytes() == expected
    else:
        assert YAML(typ="safe").load(ontology.read_text()) == json.loads(expected)
    restored = tmp_path / "restored.orm.json"
    result = run_main(["import", "ossie", str(ontology), "--out", str(restored)])
    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(restored.read_bytes()) == json_document(parse_model_document(source.read_bytes(), source=source))


@pytest.mark.parametrize("row", ROWS, ids=lambda row: row["model"])
@pytest.mark.parametrize("output_format", ["json", "yaml"])
@pytest.mark.ossie_oracle
def test_changed_ontologies_match_pinned_ossie(oracle, row, output_format, tmp_path):
    ontology = tmp_path / f"ontology.{output_format}"
    export = render_ossie(ROOT / row["model"], output_format=output_format)
    ontology.write_bytes(export.document)
    for operation in (oracle.validate, oracle.parse):
        result = operation(ontology)
        assert result.returncode == 0, result.stdout + result.stderr


def _gnd_extension(bundle):
    return json.loads(json.loads(bundle.mapping)["custom_extensions"][0]["data"])


def test_targeted_mapping_losses_close_and_objectification_losses_stay():
    for row in ROWS:
        bundle = render_ossie(ROOT / row["model"], output_format="json")
        if bundle.mapping is not None:
            data = _gnd_extension(bundle)
            assert not [link for link in data.get("unmapped_links", ()) if link["reason"] == "identification-differs"]
    for path in OBJECTIFICATIONS:
        data = _gnd_extension(render_ossie(path, output_format="json"))
        assert sum(row["reason"] == "identification-differs" for row in data["unmapped_links"]) == 2
        assert sum(row["reason"] == "identification-differs" for row in data["concepts"]) == 1


@pytest.mark.parametrize("inherits", [True, False])
def test_first_declared_supertype_defines_inherited_key(tmp_path, inherits):
    source = ROOT / "tests/fixtures/ilp_import_hardening/ih2/diamond-director.orm.yaml"
    authored = json_document(parse_model_document(source.read_bytes(), source=source))
    objects = {obj["id"]: obj for obj in authored["object_types"]}
    child = objects["director"]
    child["subtype_of"].reverse()
    child["inherits_reference"] = inherits
    if not inherits:
        child["reference"] = objects["manager"]["reference"].copy()
    path = tmp_path / "model.orm.json"
    path.write_text(json.dumps(authored))
    export = render_ossie(path, output_format="json", relational=False)
    graph = _NameGraph(json.loads(export.document))
    name = child.get("name", "director")
    key, = graph.concepts[name]["identify_by"]
    owner, relationship = graph.resolve(name, key)
    expected_owner = objects[child["subtype_of"][0]].get("name", child["subtype_of"][0]) if inherits else name
    assert owner == expected_owner
    source_id = objects[child["subtype_of"][0]]["reference"]["value_type"] if inherits else child["reference"]["value_type"]
    assert relationship["roles"][0]["concept"] == objects[source_id].get("name", source_id)


def test_local_relationship_never_shadows_the_first_supertype_identifier(tmp_path):
    source = ROOT / "tests/fixtures/ilp_import_hardening/ih2/diamond-director.orm.yaml"
    authored = json_document(parse_model_document(source.read_bytes(), source=source))
    fact = next(fact for fact in authored["fact_types"] if fact["id"] == "directs")
    fact["id"] = "gnd_reference"
    path = tmp_path / "shadowing.orm.json"
    path.write_text(json.dumps(authored))
    bundle = render_ossie(path, output_format="json")
    graph = _NameGraph(json.loads(bundle.document))
    key, = graph.concepts["Director"]["identify_by"]
    assert key != fact["id"]
    owner, relationship = graph.resolve("Director", key)
    assert owner == "Manager"
    assert relationship["roles"][0]["concept"] == "ManagerNo"
    assert graph.resolve("Director", fact["id"])[0] == "Director"


def test_multi_supertype_inherits_ordered_composite_identifier(tmp_path):
    source = ROOT / "tests/fixtures/rmap/cases/14-external-identification/model.yaml"
    authored = json_document(parse_model_document(source.read_bytes(), source=source))
    authored["object_types"].append({
        "id": "district", "name": "District", "kind": "entity",
        "subtype_of": ["state", "country"], "inherits_reference": True,
    })
    authored["fact_types"].append({
        "id": "district_in_country", "reading": "{District} is in {Country}",
        "roles": [{"role_name": "district", "object_type": "district"},
                  {"role_name": "country", "object_type": "country"}],
    })
    path = tmp_path / "composite-parent.orm.json"
    path.write_text(json.dumps(authored))
    bundle = render_ossie(path, output_format="json")
    graph = _NameGraph(json.loads(bundle.document))
    keys = graph.concepts["District"]["identify_by"]
    assert keys == ["state_in_country", "state_has_code"]
    assert [graph.resolve("District", key)[0] for key in keys] == ["State", "State"]
    assert {"fact_type": "district_in_country", "reason": "identification-differs"} in (
        _gnd_extension(bundle)["unmapped_links"]
    )


@pytest.mark.parametrize(("parents", "linked"), [(["height"], True), (["height", "person"], False)])
def test_unit_supertype_mapping_requires_the_same_key(tmp_path, parents, linked):
    path = tmp_path / "mixed-inheritance.orm.json"
    path.write_text(json.dumps({
        "version": 1,
        "object_types": [
            {"id": "height", "name": "Height", "kind": "entity",
             "reference": {"mode": "unit-based", "unit": "cm", "measure_type": "Length"}},
            {"id": "person", "name": "Person", "kind": "entity",
             "reference": {"mode": "popular", "value_type": "pid"}},
            {"id": "pid", "name": "Pid", "kind": "value", "primitive": "String"},
            {"id": "thing", "name": "Thing", "kind": "entity",
             "subtype_of": parents, "inherits_reference": True},
            {"id": "team", "name": "Team", "kind": "entity",
             "reference": {"mode": "popular", "value_type": "pid"}},
        ],
        "fact_types": [{
            "id": "thing_in_team", "reading": "{Thing} is in {Team}",
            "roles": [{"role_name": "thing", "object_type": "thing"},
                      {"role_name": "team", "object_type": "team"}],
        }],
    }))
    bundle = render_ossie(path, output_format="json")
    graph = _NameGraph(json.loads(bundle.document))
    key, = graph.concepts["Thing"]["identify_by"]
    owner, relationship = graph.resolve("Thing", key)
    assert owner == "Height" and relationship["roles"] == [{"concept": "Decimal"}]
    losses = _gnd_extension(bundle).get("unmapped_links", ())
    assert ({"fact_type": "thing_in_team", "reason": "identification-differs"} not in losses) is linked


def test_logical_mapping_refuses_different_direct_reference_targets(tmp_path):
    source = ROOT / "tests/fixtures/ilp_import_hardening/ih2/diamond-director.orm.yaml"
    authored = json_document(parse_model_document(source.read_bytes(), source=source))
    authored["object_types"].append({
        "id": "junior", "name": "Junior", "kind": "entity",
        "subtype_of": ["director", "team"], "inherits_reference": True,
    })
    authored["fact_types"].append({
        "id": "junior_joins_team", "reading": "{Junior} joins {Team}",
        "roles": [{"role_name": "junior", "object_type": "junior"},
                  {"role_name": "team", "object_type": "team"}],
    })
    path = tmp_path / "different-direct-targets.orm.json"
    path.write_text(json.dumps(authored))
    bundle = render_ossie(path, output_format="json")
    graph = _NameGraph(json.loads(bundle.document))
    key, = graph.concepts["Junior"]["identify_by"]
    owner, relationship = graph.resolve("Junior", key)
    assert owner == "Manager" and relationship["roles"] == [{"concept": "ManagerNo"}]
    assert {"fact_type": "junior_joins_team", "reason": "identification-differs"} in (
        _gnd_extension(bundle)["unmapped_links"]
    )


def test_large_unit_identifier_projection_stays_bounded(tmp_path):
    source = tmp_path / "model.orm.json"
    source.write_text(json.dumps({
        "version": 4,
        "object_types": [{"id": f"measure_{i}", "kind": "entity",
                          "reference": {"mode": "unit-based", "unit": "cm", "measure_type": "Length"}}
                         for i in range(1000)],
        "fact_types": [],
    }))
    start = time.monotonic()
    bundle = render_ossie(source, output_format="json", relational=False)
    assert len([obj for obj in json.loads(bundle.document)["ontology"] if obj["identify_by"]]) == 1000
    assert time.monotonic() - start < 10
