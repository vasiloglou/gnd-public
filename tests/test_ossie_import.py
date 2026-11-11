"""OS3 offline admission, loss accounting and round-trip controls."""

from __future__ import annotations

import ast
import copy
import hashlib
import json
import re
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
    from importlib.resources import files

    pin = json.loads(files("gnd").joinpath("schema/ossie/PINNED.json").read_bytes())
    result = plan_ossie_import(FLIGHTS)
    document = json.loads(result.model)
    rows = json.loads(result.loss_report)["dispositions"]
    assert len(rows) == len({row["pointer"] for row in rows})
    assert Counter(row["disposition"] for row in rows) == {"native": 607, "refused": 146}
    assert len(document["object_types"]) == 45
    assert len(document["fact_types"]) == 48
    assert {c["name"] for c in document["object_types"]} >= {"Airport", "State", "Carrier"}
    constraints = [c for f in document["fact_types"] for c in f.get("constraints", ())]
    assert len(constraints) == 55
    assert all(
        c["source"] == "imported"
        and c["status"] == "proposed"
        and c["provenance"]["commit"] == pin["commit"]
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


@pytest.mark.parametrize("verbalizes", [[], ["{Code} relates {Code:target} }"]])
def test_bad_foreign_reading_refuses_one_relationship(tmp_path, verbalizes):
    path = _write(tmp_path / "ontology.json", {
        "version": "0.3.0.dev0", "name": "ReadingControls",
        "ontology": [{
            "concept": "Code", "type": "ValueType", "extends": ["String"],
            "relationships": [{
                "name": "related", "roles": [{"concept": "Code", "name": "target"}],
                "verbalizes": verbalizes,
            }],
        }],
    })
    result = plan_ossie_import(path)
    assert json.loads(result.model)["fact_types"] == []
    rows = {row["pointer"]: row for row in json.loads(result.loss_report)["dispositions"]}
    assert rows["/ontology/0/relationships/0"]["disposition"] == "refused"


@pytest.mark.parametrize("pointer", ["/nonexistent", "/reference_populations/0/id"])
def test_invented_refusal_cannot_hide_an_identity_mismatch(bundle, pointer):
    path, sidecar, report = bundle
    metadata = json.loads(sidecar.read_bytes())
    metadata["elements"]["code"]["/object_types/0/primitive"] = {
        "kind": "literal", "value": "Integer",
    }
    _write(sidecar, metadata)
    claims = json.loads(report.read_bytes())
    claims["dispositions"].append({
        "pointer": pointer, "disposition": "refused", "reason": "population:out-of-scope",
    })
    _write(report, claims)
    _assert_refusal(path, "report-pointer")


def test_reportless_source_identity_match_is_explicit(bundle):
    path, sidecar, report = bundle
    report.unlink()
    verified = json.loads(plan_ossie_import(path).loss_report)
    assert verified["source_identity_verified"] is True
    metadata = json.loads(sidecar.read_bytes())
    metadata["elements"]["code"]["/object_types/0/primitive"] = {
        "kind": "literal", "value": "Integer",
    }
    _write(sidecar, metadata)
    unverified = json.loads(plan_ossie_import(path).loss_report)
    assert unverified["source_model_identity"] == verified["source_model_identity"]
    assert unverified["source_identity_verified"] is False


def test_inherited_identifier_lookup_reuses_work(tmp_path):
    from time import monotonic

    root = {
        "concept": "Base", "type": "EntityType", "identify_by": ["key"],
        "relationships": [{
            "name": "key", "roles": [{"concept": "String"}],
            "verbalizes": ["{Base} has {String}"],
        }],
    }
    chain = [
        {
            "concept": f"Type{i}", "type": "EntityType",
            "extends": ["Base" if i == 0 else f"Type{i - 1}"], "identify_by": ["key"],
        }
        for i in range(160)
    ]
    path = _write(tmp_path / "ontology.json", {
        "version": "0.3.0.dev0", "name": "InheritanceControls", "ontology": [*reversed(chain), root],
    })
    started = monotonic()
    restored = plan_ossie_import(path)
    assert len(json.loads(restored.model)["object_types"]) == len(chain) + 2
    assert monotonic() - started < 4


def test_reference_work_budget_bounds_distinct_ancestry_searches(tmp_path):
    from time import monotonic

    count = 300
    root = {
        "concept": "Base", "type": "EntityType",
        "relationships": [
            {"name": f"key{i}", "verbalizes": ["{Base} has an identifier"]}
            for i in range(count)
        ],
    }
    chain = [
        {
            "concept": f"Type{i}", "type": "EntityType",
            "extends": ["Base" if i == 0 else f"Type{i - 1}"], "identify_by": [f"key{i}"],
        }
        for i in range(count)
    ]
    path = _write(tmp_path / "ontology.json", {
        "version": "0.3.0.dev0", "name": "BudgetControls", "ontology": [root, *chain],
    })
    started = monotonic()
    _assert_refusal(path, "reference-budget")
    assert monotonic() - started < 4


def test_restored_output_size_caps(monkeypatch):
    from gnd import ossie_import

    monkeypatch.setattr(ossie_import, "MAX_BYTES", 512)
    oversized = "x" * 1100
    with pytest.raises(OssieImportError, match="ossie-import:model-size"):
        ossie_import._bounded_model({"description": oversized}, None, require_identity=False)
    with pytest.raises(OssieImportError, match="ossie-import:loss-size"):
        ossie_import._loss_report_bytes("0" * 64, None, False, [{"pointer": "/" + oversized}])


def test_refuses_sidecar_header_and_deep_pointer(bundle):
    path, sidecar, _ = bundle
    metadata = json.loads(sidecar.read_bytes())
    _write(sidecar, dict(metadata, schema="unknown"))
    _assert_refusal(path, "sidecar-header")
    metadata["elements"]["code"]["/part" * 65] = {"kind": "literal", "value": None}
    _write(sidecar, metadata)
    _assert_refusal(path, "sidecar-pointer")


def test_vendored_core_reference_admits_ai_context(bundle, tmp_path):
    path, _, _ = bundle
    document = json.loads(path.read_bytes())
    document["ai_context"] = {"instructions": "Use Code for an identifier."}
    foreign = _write(tmp_path / "foreign.json", document)
    imported = plan_ossie_import(foreign)
    rows = {row["pointer"]: row for row in json.loads(imported.loss_report)["dispositions"]}
    assert rows["/ai_context/instructions"]["disposition"] == "refused"


@pytest.mark.parametrize("variant,rule", [
    ("concept", "concept-name"), ("relationship", "relationship-name"), ("empty", "foreign-empty"),
])
def test_closed_foreign_name_refusals(tmp_path, variant, rule):
    concept = {
        "concept": "Code", "type": "ValueType", "extends": ["String"],
        "relationships": [{"name": "listed", "verbalizes": ["{Code} is listed"]}],
    }
    ontology = [concept]
    if variant == "concept":
        ontology.append(dict(concept, description="Another Code."))
    elif variant == "relationship":
        concept["relationships"].append({"name": "listed", "verbalizes": ["{Code} is recorded"]})
    else:
        ontology = [{"concept": "Record", "type": "EntityType"}]
    path = _write(tmp_path / "ontology.json", {
        "version": "0.3.0.dev0", "name": "NameControls", "ontology": ontology,
    })
    _assert_refusal(path, rule)


# Issue 173: the format reference defines the import report's schema name and every refusal rule.

REFERENCE = ROOT / "src/gnd/skills/gnd-orm-core/references/representation-format.md"
#: Raised and caught inside the foreign import: one relationship is omitted, nothing is refused
#: (test_bad_foreign_reading_refuses_one_relationship).
INTERNAL_RULES = {"reading"}


def _coded_import_rules():
    """Every rule name the import can raise or print, read from the two source files."""
    rules = set()
    tree = ast.parse((ROOT / "src/gnd/ossie_import.py").read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name):
            continue
        name = node.func.id
        if name == "OssieImportError":
            (argument,) = node.args
            if isinstance(argument, ast.Constant):
                rules.add(argument.value)
            else:
                # The two forwarding sites: `rule` itself, and `f"{rule}-size"` in `_read`.
                assert ast.unparse(argument) in {"rule", "f'{rule}-size'"}, ast.unparse(argument)
        elif name in {"_read", "_parse", "_schema_check"}:
            position = 2 if name == "_schema_check" else 1
            rule = node.args[position]
            assert isinstance(rule, ast.Constant), ast.unparse(node)
            rules.add(rule.value)
            if name == "_read":
                rules.add(rule.value + "-size")
    handler = (ROOT / "src/gnd/commands/checking.py").read_text(encoding="utf-8")
    rules.update(re.findall(r'"ossie-import:([a-z-]+)"', handler))
    return rules


def _reference_import_rules():
    text = REFERENCE.read_text(encoding="utf-8")
    section = text.split("### Import refusal rules", 1)[1].split("\n### ", 1)[0]
    return re.findall(r"^\| `([a-z-]+)` \|", section, flags=re.MULTILINE)


def test_the_reference_names_every_import_refusal_rule():
    documented = _reference_import_rules()
    assert len(documented) == len(set(documented)), "a rule is listed twice"
    coded = _coded_import_rules()
    assert INTERNAL_RULES <= coded
    assert set(documented) == coded - INTERNAL_RULES
    assert len(documented) == 29


def test_the_reference_names_the_import_report_schema_and_its_reasons(tmp_path):
    text = REFERENCE.read_text(encoding="utf-8")
    section = text.split("### The import loss report", 1)[1].split("\n### ", 1)[0]
    path = tmp_path / "flights.ontology.yaml"
    path.write_bytes(FLIGHTS.read_bytes())
    report = json.loads(plan_ossie_import(path).loss_report)
    assert f"`{report['schema']}`" in section and report["schema"] == "gnd-ossie-import-loss/1"
    for member in report:
        assert f"| `{member}` |" in section, member
    pairs = {(row["disposition"], row["reason"]) for row in report["dispositions"]}
    source = (ROOT / "src/gnd/ossie_import.py").read_text(encoding="utf-8")
    reasons = set(re.findall(r'"(foreign:[a-z-]+)"', source))
    assert reasons == {"foreign:unsupported", "foreign:decimal-domain"}
    assert pairs <= {("native", "projection"), *(("refused", reason) for reason in reasons)}
    for disposition, reason in pairs | {("refused", reason) for reason in reasons}:
        assert f"| `{disposition}` | `{reason}` |" in section, (disposition, reason)

