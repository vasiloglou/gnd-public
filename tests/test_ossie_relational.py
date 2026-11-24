"""OB3: the Ossie semantic model and mapping against their owner-approved corpus.

The corpus (tests/fixtures/ossie_relational) and its hand-derived expected files were
approved at the OB3 corpus gate before any renderer existed.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from support import ossie_relational_corpus as corpus

ROOT = Path(__file__).resolve().parents[1]
CASES = corpus.cases()


def _render(number, output_format="yaml"):
    from gnd.export.ossie import render_ossie

    return render_ossie(
        corpus.rmap_case(number), output_format=output_format, document_name=f"ontology.{output_format}"
    )


@pytest.mark.parametrize("number", CASES)
def test_t1_yaml_equals_the_approved_files(number):
    bundle = _render(number)
    directory = corpus.CORPUS / number
    assert bundle.semantic_model == (directory / "expected.semantic_model.yaml").read_bytes()
    assert bundle.mapping == (directory / "expected.mapping.yaml").read_bytes()


@pytest.mark.parametrize("number", CASES)
def test_t1_extension_parses_to_the_readable_copy(number):
    mapping = corpus.load_yaml_bytes(_render(number).mapping)
    (extension,) = mapping["custom_extensions"]
    expected = json.loads((corpus.CORPUS / number / "expected.extension.json").read_text(encoding="utf-8"))
    assert json.loads(extension["data"]) == expected


@pytest.mark.parametrize("number", CASES)
def test_t1_json_equals_the_approved_structure(number):
    bundle = _render(number, "json")
    directory = corpus.CORPUS / number
    semantic = json.loads(bundle.semantic_model)
    mapping = json.loads(bundle.mapping)
    assert semantic == corpus.load_yaml(directory / "expected.semantic_model.yaml")
    expected = corpus.load_yaml(directory / "expected.mapping.yaml")
    # The JSON run names JSON files and binds the JSON bytes, so those members differ.
    assert mapping["ontology_ref"]["iri"] == "./ontology.json"
    assert mapping["semantic_model_ref"]["iri"] == "./ontology.json.semantic_model.json"
    for document in (mapping, expected):
        document.pop("ontology_ref"), document.pop("semantic_model_ref")
    actual_payload = json.loads(mapping.pop("custom_extensions")[0]["data"])
    expected_payload = json.loads(expected.pop("custom_extensions")[0]["data"])
    for key in ("ontology_sha256", "semantic_model_sha256"):
        actual_payload.pop(key), expected_payload.pop(key)
    assert mapping == expected
    assert actual_payload == expected_payload


# --- T2-T5: every model the export admits ------------------------------------------------------


def _model_paths():
    found = set()
    for base in (ROOT / "src/gnd", ROOT / "tests/fixtures"):
        for pattern in ("*.orm.yaml", "*.orm.json"):
            found.update(base.rglob(pattern))
    found.update((corpus.RMAP / "cases").glob("*/model.yaml"))
    return sorted(found)


@pytest.fixture(scope="module")
def exported():
    """(path, format) -> bundle for every scanned model the export admits."""
    from gnd.export.ossie import render_ossie

    bundles = {}
    for path in _model_paths():
        for output_format in ("json", "yaml"):
            try:
                bundles[(path, output_format)] = render_ossie(path, output_format=output_format)
            except Exception:  # noqa: BLE001 -- a refused model has no export to check
                break
    assert len(bundles) >= 800  # 844 on 2026-11-24; a collapse of the scan fails here
    return bundles


def _documents(bundle, output_format):
    load = json.loads if output_format == "json" else corpus.load_yaml_bytes
    return load(bundle.document), load(bundle.semantic_model), load(bundle.mapping)


def test_t2_pinned_schemas_accept_every_relational_file(exported):
    from gnd.export.ossie_relational import validate_relational

    checked = 0
    for (_path, output_format), bundle in exported.items():
        if bundle.semantic_model is None:
            continue
        _ontology, semantic, mapping = _documents(bundle, output_format)
        validate_relational(semantic, mapping)
        checked += 1
    assert checked >= 800


def test_t2_validation_is_offline_and_can_fail():
    import jsonschema

    from gnd.export.ossie_relational import validate_relational

    semantic = corpus.load_yaml(corpus.CORPUS / "01" / "expected.semantic_model.yaml")
    mapping = corpus.load_yaml(corpus.CORPUS / "01" / "expected.mapping.yaml")
    validate_relational(semantic, mapping)
    with pytest.raises(jsonschema.ValidationError):
        validate_relational({**semantic, "datasets": []}, mapping)
    broken = json.loads(json.dumps(mapping))
    # ConceptMapping lives in ontology.json, behind the mapping schema's upstream $ref.
    broken["concept_mappings"][0]["link_mappings"][0]["object_mapping"] = {}
    with pytest.raises(jsonschema.ValidationError):
        validate_relational(semantic, broken)


def test_t3_cross_checks_hold_for_every_model(exported):
    for (path, output_format), bundle in exported.items():
        if output_format != "json" or bundle.semantic_model is None:
            continue
        try:
            corpus.cross_check(*_documents(bundle, output_format))
        except AssertionError as error:
            raise AssertionError(f"{path}: {error}") from error


def test_t4_one_walk_lists_every_fact_type_and_constraint(exported):
    from gnd.model import load_model_bytes
    from gnd.model_index import ModelIndex

    reasons = set()
    for (path, output_format), bundle in exported.items():
        if output_format != "json" or bundle.semantic_model is None:
            continue
        ontology, semantic, mapping = _documents(bundle, output_format)
        payload = json.loads(mapping["custom_extensions"][0]["data"])
        model = load_model_bytes(path.read_bytes(), source=path)  # as the export reads it
        expected = []
        for fact in ModelIndex.for_model(model).iter_fact_types_shared():
            expected.append(("fact_type", fact["id"]))
            expected += [("constraint", f"fact_types/{fact['id']}/constraints/{i}")
                         for i, _ in enumerate(fact.get("constraints") or ())]
        expected += [("constraint", f"constraints/{i}") for i, _ in enumerate(model.constraints or ())]
        listed = [(row["kind"], row["id"]) for row in payload["dispositions"]]
        assert sorted(listed) == sorted(expected), path
        assert all(bool(row["carried_as"]) != (row["reason"] is not None) for row in payload["dispositions"]), path
        carried = {row["id"] for row in payload["dispositions"] if row["kind"] == "fact_type" and row["reason"] is None}
        linked = corpus.cross_check(ontology, semantic, mapping)
        unlinked = [row["fact_type"] for row in payload.get("unmapped_links", [])]
        assert len(linked) == len(set(linked)) and not set(linked) & set(unlinked), path
        assert set(linked) | set(unlinked) == carried, path
        reasons.update(row["reason"] for row in payload.get("unmapped_links", []))
        reasons.update(row["reason"] for row in payload["concepts"])
    assert reasons == {"identification-differs", "subtype-absorbed"}


def test_t5_bytes_do_not_depend_on_the_run_or_the_path(tmp_path):
    import shutil

    from gnd.export.ossie import render_ossie

    for number in CASES:
        source = corpus.rmap_case(number)
        moved = tmp_path / number / "elsewhere" / "renamed.yaml"
        moved.parent.mkdir(parents=True)
        shutil.copyfile(source, moved)
        for output_format in ("yaml", "json"):
            first = render_ossie(source, output_format=output_format)
            assert render_ossie(source, output_format=output_format) == first
            assert render_ossie(moved, output_format=output_format) == first


# --- T6-T9: the command ------------------------------------------------------------------------

OB1_BASELINE = json.loads((ROOT / "tests/fixtures/ossie_ob1_baseline.json").read_bytes())
LEGACY = ("document", "sidecar", "loss_report")
MODEL_01 = corpus.rmap_case("01")


@pytest.mark.parametrize("key", sorted(OB1_BASELINE))
def test_t6_ontology_only_equals_the_ob1_baseline(key):
    """The default run's legacy files are checked by test_ossie_export's OB1 T1."""
    import hashlib

    from gnd.export.ossie import render_ossie

    relative, _, output_format = key.partition("::")
    try:
        bundle = render_ossie(ROOT / relative, output_format=output_format, relational=False)
        actual = {name: hashlib.sha256(getattr(bundle, name)).hexdigest() for name in LEGACY}
        actual["sizes"] = [len(getattr(bundle, name)) for name in LEGACY]
        assert bundle.semantic_model is None and bundle.mapping is None
    except Exception as error:  # noqa: BLE001 -- the baseline records refusals by type and text
        actual = {"refused": f"{type(error).__name__}: {error}"}
    assert actual == OB1_BASELINE[key]


def _argv(model, out, *extra):
    return ["export", "ossie", str(model), "--out", str(out), *extra]


@pytest.mark.parametrize("output_format", ("yaml", "json"))
def test_t6_command_writes_five_files_and_ontology_only_three(tmp_path, output_format, capsys):
    from gnd import cli

    five, three = tmp_path / "five", tmp_path / "three"
    five.mkdir(), three.mkdir()
    name = f"o.{output_format}"
    assert cli.main(_argv(MODEL_01, five / name, "--format", output_format)) == 0
    assert cli.main(_argv(MODEL_01, three / name, "--format", output_format, "--ontology-only")) == 0
    legacy = [name, f"{name}.gnd.json", f"{name}.loss.json"]
    relational = [f"{name}.mapping.{output_format}", f"{name}.semantic_model.{output_format}"]
    assert sorted(p.name for p in three.iterdir()) == sorted(legacy)
    assert sorted(p.name for p in five.iterdir()) == sorted(legacy + relational)
    for leaf in legacy:
        assert (five / leaf).read_bytes() == (three / leaf).read_bytes()
    load = json.loads if output_format == "json" else corpus.load_yaml_bytes
    mapping = load((five / relational[0]).read_bytes())
    assert mapping["ontology_ref"]["iri"] == f"./{name}"
    assert mapping["semantic_model_ref"]["iri"] == f"./{relational[1]}"
    assert "semantic model and mapping" in capsys.readouterr().out


@pytest.mark.parametrize("leaf", ("o.yaml", "o.yaml.gnd.json", "o.yaml.loss.json",
                                  "o.yaml.semantic_model.yaml", "o.yaml.mapping.yaml"))
def test_t7_a_collision_on_any_path_publishes_nothing(tmp_path, leaf):
    from gnd import cli

    (tmp_path / leaf).write_text("occupied")
    assert cli.main(_argv(MODEL_01, tmp_path / "o.yaml")) == 11
    assert [p.name for p in tmp_path.iterdir()] == [leaf]
    assert (tmp_path / leaf).read_text() == "occupied"


def test_t7_ontology_only_ignores_the_relational_paths(tmp_path):
    from gnd import cli

    (tmp_path / "o.yaml.mapping.yaml").write_text("occupied")
    assert cli.main(_argv(MODEL_01, tmp_path / "o.yaml", "--ontology-only")) == 0


def _largest(tmp_path, artifact):
    """A model whose named relational artifact is strictly the largest of the five."""
    from gnd.export.ossie import render_ossie

    long = "x" * 4000
    document = corpus.load_yaml(MODEL_01)
    if artifact == "mapping":
        # A unary's id is its flag column, its relationship and its disposition.
        document["fact_types"] = [{"id": f"flag_{long}", "reading": "{Customer} is flagged",
                                   "roles": [{"object_type": "customer", "role_name": "customer"}]}]
    else:
        # A referenced key column is named four times per reference in the semantic model
        # (field, expression, and both sides of the relationship), and twice in the mapping.
        modality = {"source": "explicit", "status": "confirmed", "modality": "alethic",
                    "provenance": {"user_quote": "one"}}
        document["object_types"] += [
            {"id": "target", "name": "Target", "kind": "entity", "independent": True,
             "reference": {"mode": "popular", "value_type": f"id_{long}"}},
            {"id": f"id_{long}", "name": "TargetId", "kind": "value", "primitive": "Integer"},
        ]
        document["fact_types"] = [
            {"id": f"f{n}", "reading": "{Customer} points at {Target}",
             "roles": [{"object_type": "customer", "role_name": "customer"},
                       {"object_type": "target", "role_name": f"r{n}"}],
             "constraints": [{"type": "uniqueness", "roles": ["customer"], **modality}]}
            for n in range(3)
        ]
    path = tmp_path / "model.json"
    path.write_text(json.dumps(document))
    # The mapping names its sibling files, so its size depends on the output name.
    bundle = render_ossie(path, output_format="json", document_name="o.json")
    sizes = {name: len(getattr(bundle, name)) for name in (*LEGACY, "semantic_model", "mapping")}
    assert max(sizes, key=sizes.get) == artifact and sorted(sizes.values())[-2] < sizes[artifact], sizes
    return path, sizes[artifact]


@pytest.mark.parametrize("artifact", ("semantic_model", "mapping"))
def test_t8_the_output_bound_covers_the_relational_files(tmp_path, artifact, capsys):
    from gnd import cli

    source, size = _largest(tmp_path, artifact)
    refused, published = tmp_path / "refused", tmp_path / "published"
    refused.mkdir(), published.mkdir()
    assert cli.main(_argv(source, refused / "o.json", "--format", "json", "--max-output-bytes", str(size - 1))) == 3
    assert "ossie:output-size" in capsys.readouterr().err
    assert not list(refused.iterdir())
    assert cli.main(_argv(source, published / "o.json", "--format", "json", "--max-output-bytes", str(size))) == 0
    assert len(list(published.iterdir())) == 5
    # Without the relational files the same bound minus one is enough.
    assert cli.main(_argv(source, refused / "o.json", "--format", "json", "--ontology-only",
                          "--max-output-bytes", str(size - 1))) == 0


def test_t9_a_sample_population_changes_only_the_identity(tmp_path):
    from gnd.export.ossie import render_ossie

    document = corpus.load_yaml(MODEL_01)
    plain, populated = tmp_path / "plain.json", tmp_path / "populated.json"
    plain.write_text(json.dumps(document))
    document["fact_types"][0]["sample_population"] = [{"customer": 1, "email": "a@example.org"}]
    populated.write_text(json.dumps(document))
    without, with_rows = (render_ossie(path, output_format="yaml") for path in (plain, populated))
    assert with_rows.semantic_model == without.semantic_model
    assert with_rows.document == without.document
    assert b"example.org" not in with_rows.semantic_model + with_rows.mapping
    payloads = []
    for bundle in (without, with_rows):
        mapping = corpus.load_yaml_bytes(bundle.mapping)
        payloads.append(json.loads(mapping.pop("custom_extensions")[0]["data"]))
        payloads.append(mapping)
    assert payloads[1] == payloads[3]
    assert payloads[0].pop("model_identity") != payloads[2].pop("model_identity")
    assert payloads[0] == payloads[2]
    rows = json.loads(with_rows.loss_report)["dispositions"]
    assert any(row["reason"] == "population:out-of-scope" for row in rows)
    assert not any(row["reason"] == "population:out-of-scope" for row in json.loads(without.loss_report)["dispositions"])


def test_no_table_means_no_relational_files(tmp_path, capsys):
    """Core-spec requires a dataset, so a model that maps to no table writes three files."""
    from gnd import cli
    from gnd.export.ossie import render_ossie

    document = corpus.load_yaml(MODEL_01)
    document["fact_types"] = []
    path = tmp_path / "model.json"
    path.write_text(json.dumps(document))
    bundle = render_ossie(path, output_format="yaml")
    assert bundle.semantic_model is None and bundle.mapping is None
    assert bundle.document == render_ossie(path, output_format="yaml", relational=False).document
    out = tmp_path / "out"
    out.mkdir()
    assert cli.main(_argv(path, out / "o.yaml")) == 0
    assert sorted(p.name for p in out.iterdir()) == ["o.yaml", "o.yaml.gnd.json", "o.yaml.loss.json"]
    assert "maps to no table" in capsys.readouterr().err


# --- T10: time ---------------------------------------------------------------------------------


def test_t10_render_time_is_bounded_and_not_quadratic(tmp_path):
    from time import monotonic

    from support.rmap_large import large_rmap_model

    from gnd.export.ossie import render_ossie

    times = {}
    for scale in (1, 5):
        path = tmp_path / f"large{scale}.json"
        path.write_text(json.dumps(large_rmap_model(280 * scale, 900 * scale), separators=(",", ":")))
        best = float("inf")
        for _ in range(2):
            start = monotonic()
            bundle = render_ossie(path, output_format="json", max_output_bytes=268435456)
            best = min(best, monotonic() - start)
        assert bundle.mapping is not None
        times[scale] = best
    # 1,400 entities and 4,500 fact types (the reporter's scale): 3.3 s for the five files and
    # 2.6 s for the ontology's three, measured on 2026-11-24; the ratio to one fifth was 5.1.
    assert times[5] < 60
    assert times[5] / times[1] < 12  # linear about 5; quadratic about 25


# --- T13-T16: the decisions ---------------------------------------------------------------------


def _render_document(tmp_path, document, name="model.json"):
    from gnd.export.ossie import render_ossie

    path = tmp_path / name
    path.write_text(json.dumps(document))
    return render_ossie(path, output_format="json")


def test_t13_an_identifier_needs_functional_components(tmp_path):
    """E3 (a): a component that is not single-valued for the entity identifies nothing."""
    document = corpus.load_yaml(corpus.rmap_case("14"))
    code = next(f for f in document["fact_types"] if f["id"] == "state_has_code")
    code["constraints"] = [c for c in code["constraints"] if c["type"] != "uniqueness"]
    bundle = _render_document(tmp_path, document)
    semantic, mapping = json.loads(bundle.semantic_model), json.loads(bundle.mapping)
    assert "state" not in [d["name"] for d in semantic["datasets"]]
    payload = json.loads(mapping["custom_extensions"][0]["data"])
    rows = {(row["kind"], row["id"]): row for row in payload["dispositions"]}
    assert rows[("fact_type", "state_has_population")]["reason"] == "identification-unmatchable"
    assert "State" not in [entry["concept"] for entry in mapping["concept_mappings"]]
    # The ontology agrees: it declares no identifier for State either.
    state = next(c for c in json.loads(bundle.document)["ontology"] if c["concept"] == "State")
    assert "identify_by" not in state


def test_t13_identification_differs_is_listed_not_guessed(tmp_path):
    """E3 (b): a unit-based entity has a key column but no identifier in the ontology."""
    bundle = _render_document(tmp_path, corpus.load_yaml(corpus.rmap_case("23")))
    mapping = json.loads(bundle.mapping)
    payload = json.loads(mapping["custom_extensions"][0]["data"])
    assert payload["unmapped_links"] == [{"fact_type": "person_has_height", "reason": "identification-differs"}]
    linked = corpus.cross_check(json.loads(bundle.document), json.loads(bundle.semantic_model), mapping)
    assert "person_has_height" not in linked


def test_t14_reserved_words_are_quoted_not_listed(tmp_path):
    """E5: `order` and `select` are legal names; quoted and uppercased they are not keywords."""
    document = corpus.load_yaml(MODEL_01)
    document["object_types"] += [
        {"id": "select", "name": "Select", "kind": "entity", "independent": True,
         "reference": {"mode": "popular", "value_type": "order"}},
        {"id": "order", "name": "Order", "kind": "value", "primitive": "Integer"},
    ]
    document["fact_types"].append({
        "id": "from", "reading": "{Customer} from {Select}",
        "roles": [{"object_type": "customer", "role_name": "where"}, {"object_type": "select", "role_name": "group"}],
        "constraints": [{"type": "uniqueness", "roles": ["where"], "source": "explicit", "status": "confirmed",
                         "modality": "alethic", "provenance": {"user_quote": "one"}}],
    })
    bundle = _render_document(tmp_path, document)
    ontology, semantic, mapping = (json.loads(part) for part in (bundle.document, bundle.semantic_model, bundle.mapping))
    corpus.cross_check(ontology, semantic, mapping)
    customer = next(d for d in semantic["datasets"] if d["name"] == "customer")
    assert {"name": "group_order", "expression": {"sql": '"GROUP_ORDER"'}, "datatype": "Integer"} in customer["fields"]
    select = next(e for e in mapping["concept_mappings"] if e["concept"] == "Select")
    assert select["object_mappings"] == [{"expression": '"SELECT"."ORDER"'}]
    links = next(e for e in mapping["concept_mappings"] if e["concept"] == "Customer")["link_mappings"]
    assert links[-1]["children"] == [{
        "object_mapping": {"concept": "Select", "expression": '"CUSTOMER"."GROUP_ORDER"'}, "relationship": "from"}]


def test_t14_quoting_escapes_an_embedded_quote():
    from gnd.export.ossie_relational import _quoted

    assert _quoted('a"b') == '"A""B"'
    assert corpus.quoted_identifiers(_quoted('a"b') + "." + _quoted("c")) == (['A"B', "C"], "?.?")


def test_t15_the_datatype_map_covers_every_primitive(tmp_path):
    from importlib.resources import files

    from gnd.export.ossie_relational import DATATYPES

    schema = json.loads(files("gnd").joinpath("schema", "orm-meta.schema.json").read_bytes())
    core = json.loads(files("gnd").joinpath("schema", "ossie", "core-spec.json").read_bytes())
    assert set(DATATYPES) == set(schema["$defs"]["object_type"]["properties"]["primitive"]["enum"])
    assert set(DATATYPES.values()) <= set(core["$defs"]["DataType"]["enum"])
    assert DATATYPES == {
        "String": "String", "Integer": "Integer", "Float": "Float", "Boolean": "Boolean", "Date": "Date",
        "DateTime": "DateTime", "Number": "Decimal", "Binary": "Opaque", "Duration": "Opaque",
    }
    document = corpus.load_yaml(MODEL_01)
    document["object_types"][2]["primitive"] = "Duration"
    document["version"] = 3  # temporal primitives need model version 3
    semantic = json.loads(_render_document(tmp_path, document).semantic_model)
    (email,) = [f for f in semantic["datasets"][0]["fields"] if f["name"] == "email"]
    assert email["datatype"] == "Opaque"
    assert email["custom_extensions"] == [{"vendor_name": "GND", "data": '{"gnd_primitive":"Duration"}'}]


def test_relational_files_are_the_same_in_every_disclosure_mode():
    """Plan §5: the new files are classed like the other Ossie surfaces (every-mode, RN0-K1)."""
    from gnd import disclosure
    from gnd.export.ossie import render_ossie

    source = corpus.rmap_case("14")
    unset = render_ossie(source, output_format="yaml")
    with disclosure.invocation("customer"):
        customer = render_ossie(source, output_format="yaml")
    assert (customer.semantic_model, customer.mapping) == (unset.semantic_model, unset.mapping)
    assert b"country_country_code" in customer.semantic_model
    assert disclosure.SURFACES["gnd export ossie"].kind == "every-mode"
