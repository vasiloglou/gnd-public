"""OS1 ordinary-lane contract for standalone Ossie ontology export."""

from __future__ import annotations

import hashlib
import json
import os
from concurrent.futures import ThreadPoolExecutor
from importlib.resources import files
from pathlib import Path
from time import monotonic

import pytest
from jsonschema import Draft202012Validator
from ruamel.yaml import YAML

from gnd import cli, safefs
from gnd.errors import ModelValidationError
from gnd.export.ossie import _metadata, _ontology, render_ossie
from gnd.model import MAX_MODEL_BYTES, json_document, load_model, parse_model_document
from gnd.values import model_identity

ROOT = Path(__file__).resolve().parents[1]
MILESTONE = ROOT / ".gnd-planning/milestones/ossie-interchange"
CENSUS = (MILESTONE / "evidence/OS0/revised/census.txt").read_text().splitlines()
RESOURCES = files("gnd")
REPORT = Draft202012Validator(
    json.loads(RESOURCES.joinpath("ossie-loss-report.schema.json").read_bytes())
)
ONTOLOGY = Draft202012Validator(
    json.loads(RESOURCES.joinpath("schema/ossie/ontology.json").read_bytes())
)
MODALITY = {
    "source": "explicit",
    "status": "confirmed",
    "modality": "alethic",
    "provenance": {"user_quote": "A synthetic uniqueness witness."},
}


def _pointers(value, path=""):
    yield path
    if isinstance(value, dict):
        children = value.items()
    elif isinstance(value, list):
        children = enumerate(value)
    else:
        return
    for key, child in children:
        key = str(key).replace("~", "~0").replace("/", "~1")
        yield from _pointers(child, f"{path}/{key}")


def _get(document, pointer):
    for token in pointer.split("/")[1:]:
        key = token.replace("~1", "/").replace("~0", "~")
        document = document[int(key) if isinstance(document, list) else key]
    return document


@pytest.mark.parametrize("relative", CENSUS)
def test_census_export(relative):
    source = ROOT / relative
    authored = json_document(parse_model_document(source.read_bytes(), source=source))
    if "includes" in authored:
        with pytest.raises(ModelValidationError, match="include:unsupported-route"):
            render_ossie(source, output_format="json")
        return

    exported = render_ossie(source, output_format="json")
    doc = json.loads(exported.document)
    report = json.loads(exported.loss_report)
    sidecar = json.loads(exported.sidecar)
    ONTOLOGY.validate(doc)
    REPORT.validate(report)
    identity = model_identity(load_model(source))
    digest = hashlib.sha256(exported.document).hexdigest()
    for metadata in (report, sidecar):
        assert metadata["model_identity"] == identity
        assert metadata["document_sha256"] == digest
    rows = report["dispositions"]
    assert [row["pointer"] for row in rows] == list(_pointers(authored))
    retained = set()
    for group in sidecar["elements"].values():
        for pointer, entry in group.items():
            assert pointer not in retained
            retained.add(pointer)
            value = _get(authored, pointer)
            match entry["kind"]:
                case "copy":
                    assert _get(doc, entry["from"]) == value
                case "literal":
                    assert entry["value"] == value
                case "array":
                    assert isinstance(value, list)
                case "object":
                    assert isinstance(value, dict)
                case _:
                    pytest.fail(f"unexpected reconstruction entry {entry}")
    assert retained == {row["pointer"] for row in rows if row["disposition"] != "refused"}


@pytest.mark.parametrize("encoding", ("yaml", "json"))
def test_output_deterministic_across_source_paths(tmp_path, encoding):
    source = ROOT / "src/gnd/examples/refunds/model.orm.yaml"
    same_source = tmp_path / "unrelated.yaml"
    same_source.write_bytes(source.read_bytes())
    assert render_ossie(source, output_format=encoding) == render_ossie(
        same_source, output_format=encoding
    )


def _synthetic(tmp_path, *, two_directions=False):
    ucs = [{"type": "uniqueness", "roles": ["elapsed"], **MODALITY}]
    if two_directions:
        ucs.append({"type": "uniqueness", "roles": ["entry"], **MODALITY})
    document = {
        "version": 3,
        "source": {"a/b~c": "probe"},
        "object_types": [
            {"id": "entry", "kind": "value", "name": "Entry", "primitive": "String"},
            {"id": "elapsed", "kind": "value", "name": "Elapsed", "primitive": "Duration"},
        ],
        "fact_types": [
            {
                "id": "entry_elapsed",
                "reading": "{Entry} has {Elapsed}",
                "inverse_reading": "belongs to",
                "roles": [
                    {"object_type": "entry", "role_name": "entry"},
                    {"object_type": "elapsed", "role_name": "elapsed"},
                ],
                "constraints": ucs,
            }
        ],
    }
    path = tmp_path / "example.json"
    path.write_text(json.dumps(document))
    return path


@pytest.mark.parametrize("both", (False, True))
def test_role_permutation_and_multiplicity(tmp_path, both):
    bundle = render_ossie(_synthetic(tmp_path, two_directions=both), output_format="json")
    entry, elapsed = json.loads(bundle.document)["ontology"]
    assert elapsed["extends"] == ["Integer"]
    owner = entry if both else elapsed
    (relation,) = owner["relationships"]
    if both:
        assert relation["multiplicity"] == "OneToOne"
        assert relation["verbalizes"] == [
            "{Entry} has {Elapsed:elapsed}",
            "{Elapsed:elapsed} belongs to {Entry}",
        ]
    else:
        assert relation["multiplicity"] == "ManyToOne"
        assert relation["verbalizes"] == [
            "{Entry:entry} has {Elapsed}",
            "{Elapsed} belongs to {Entry:entry}",
        ]
    sidecar = json.loads(bundle.sidecar)
    assert sidecar["elements"]["elapsed"]["/object_types/1/primitive"]["value"] == "Duration"
    assert "/source/a~1b~0c" in sidecar["elements"][""]


def test_identifying_relationships(tmp_path):
    source = ROOT / "src/gnd/skills/gnd-model-from-text/examples"
    library = render_ossie(source / "library_with_subtypes.orm.yaml", output_format="json")
    concepts = {c["concept"]: c for c in json.loads(library.document)["ontology"]}
    assert concepts["BookItem"]["extends"] == ["LibraryItem"]
    assert concepts["BookItem"]["identify_by"] == concepts["LibraryItem"]["identify_by"]
    (relation,) = [
        r
        for r in concepts["LibraryItem"]["relationships"]
        if r["name"] in concepts["LibraryItem"]["identify_by"]
    ]
    assert relation["multiplicity"] == "OneToOne"

    composite = source / "reference_scheme_elicitation.orm.yaml"
    doc = json.loads(render_ossie(composite, output_format="json").document)
    concepts = {c["concept"]: c for c in doc["ontology"]}
    assert "identify_by" not in concepts["Task"]
    assert concepts["gnd_date"]["extends"] == ["Date"]

    authored = json_document(parse_model_document(composite.read_bytes(), source=composite))
    link = next(fact for fact in authored["fact_types"] if fact["id"] == "task_in_project")
    link["constraints"].append({"type": "uniqueness", "roles": ["task"], **MODALITY})
    target = tmp_path / "functional.json"
    target.write_text(json.dumps(authored))
    doc = json.loads(render_ossie(target, output_format="json").document)
    task = next(c for c in doc["ontology"] if c["concept"] == "Task")
    assert task["identify_by"] == ["task_in_project", "task_has_name"]


def test_vendored_ontology_bytes_match_os0_pin():
    bundle = RESOURCES.joinpath("schema/ossie")
    pin = json.loads(bundle.joinpath("PINNED.json").read_bytes())
    os0 = json.loads((MILESTONE / "evidence/OS0/pins.json").read_bytes())
    assert pin["commit"] == os0["ossie_commit"]
    assert pin["sha256"] == os0["ossie_sha256"]["ontology/ontology.json"]
    assert (
        pin["sha256"] == hashlib.sha256(bundle.joinpath("ontology.json").read_bytes()).hexdigest()
    )


def test_cli_loss_and_strict_policy(tmp_path, capsys):
    model = ROOT / "src/gnd/examples/growth/model.orm.yaml"
    output = tmp_path / "sample.json"
    report = tmp_path / "custom.json"
    argv = [
        "export",
        "ossie",
        str(model),
        "--out",
        str(output),
        "--format",
        "json",
        "--loss-report",
        str(report),
    ]
    assert cli.main([*argv, "--strict"]) == 3
    assert "population:out-of-scope" in capsys.readouterr().err
    assert not list(tmp_path.iterdir())
    assert cli.main(argv) == 0
    assert output.exists() and (tmp_path / "sample.json.gnd.json").exists()
    report_doc = json.loads(report.read_bytes())
    assert any(row["disposition"] == "refused" for row in report_doc["dispositions"])
    sidecar = json.loads((tmp_path / "sample.json.gnd.json").read_bytes())
    assert all(
        "/sample_population" not in pointer
        for group in sidecar["elements"].values()
        for pointer in group
    )


@pytest.mark.parametrize(
    "kind, expected",
    [
        ("missing", 66),
        ("malformed", 3),
        ("oversized", 3),
        ("include", 3),
        ("alias", 74),
        ("sidecar-alias", 74),
        ("missing-parent", 74),
    ],
)
def test_cli_refusal_order_and_outputs(tmp_path, kind, expected, capsys):
    model = _synthetic(tmp_path)
    output = tmp_path / "out.yaml"
    extra = []
    if kind == "missing":
        model.unlink()
    elif kind == "malformed":
        model.write_text("{")
    elif kind == "oversized":
        model.write_bytes(b" " * (MAX_MODEL_BYTES + 1))
    elif kind == "include":
        model.write_text('{"version": 5, "includes": [{"path": "missing.orm.yaml"}]}')
    elif kind in {"alias", "sidecar-alias"}:
        alias = output if kind == "alias" else output.with_name(output.name + ".gnd.json")
        extra = ["--loss-report", str(alias)]
    elif kind == "missing-parent":
        extra = ["--loss-report", str(tmp_path / "missing" / "report.json")]
    assert cli.main(["export", "ossie", str(model), "--out", str(output), *extra]) == expected
    if kind == "include":
        assert "include:unsupported-route" in capsys.readouterr().err
    assert {p.name for p in tmp_path.iterdir()} <= {model.name}


@pytest.mark.parametrize("leaf", ("output", "output.gnd.json", "output.loss.json"))
def test_cli_rollback_on_output_collision(tmp_path, leaf):
    model = _synthetic(tmp_path)
    (tmp_path / leaf).write_bytes(b"occupied")
    result = cli.main(["export", "ossie", str(model), "--out", str(tmp_path / "output")])
    assert result == 11
    assert (tmp_path / leaf).read_bytes() == b"occupied"
    assert {p.name for p in tmp_path.iterdir()} == {model.name, leaf}


@pytest.mark.parametrize("failing_link", (1, 2, 3))
def test_publication_rolls_back_after_link_failure(tmp_path, monkeypatch, failing_link):
    original = safefs.os.link
    calls = 0

    def link(*args, **kwargs):
        nonlocal calls
        calls += 1
        if calls == failing_link:
            raise OSError("injected publication refusal")
        return original(*args, **kwargs)

    monkeypatch.setattr(safefs.os, "link", link)
    files_to_write = [(tmp_path / name, b"content") for name in ("report", "sidecar", "ontology")]
    with pytest.raises(OSError, match="injected"):
        safefs.publish_new_files(files_to_write)
    assert not list(tmp_path.iterdir())


def test_group_publication_create_once_with_concurrent_callers(tmp_path):
    names = ("report", "sidecar", "ontology")

    def publish(value):
        try:
            safefs.publish_new_files([(tmp_path / name, value) for name in names])
        except FileExistsError:
            return None
        return value

    with ThreadPoolExecutor(max_workers=2) as executor:
        first, second = executor.map(publish, (b"first", b"second"))
    assert (first is None) != (second is None)
    assert {(tmp_path / name).read_bytes() for name in names} == {first or second}


def test_pointer_walk_time_bound():
    source = {"source": {str(index): {"nested": [1, False]} for index in range(12_000)}}
    start = monotonic()
    rows, _, refused = _metadata(source, {})
    assert len(rows) == 48_002 and not refused
    assert monotonic() - start < 4.0


def test_projection_time_bound(tmp_path):
    path = _synthetic(tmp_path)
    source = json.loads(path.read_bytes())
    (fact,) = source["fact_types"]
    source["fact_types"] = [dict(fact, id=f"elapsed_{index}") for index in range(400)]
    path.write_text(json.dumps(source))
    model = load_model(path)
    start = monotonic()
    ontology, _ = _ontology(source, model)
    assert len(ontology["ontology"][1]["relationships"]) == 400
    assert monotonic() - start < 4.0


def test_census_roster_matches_phase_selection():
    assert len(CENSUS) == len(set(CENSUS)) == 41
    assert (
        sum(
            "includes" in parse_model_document((ROOT / path).read_bytes(), source=path)
            for path in CENSUS
        )
        == 3
    )


def test_missing_object_type_names_use_ids(tmp_path):
    source = _synthetic(tmp_path)
    authored = json.loads(source.read_bytes())
    for obj in authored["object_types"]:
        del obj["name"]
    source.write_text(json.dumps(authored))
    bundle = render_ossie(source, output_format="json")
    assert {c["concept"] for c in json.loads(bundle.document)["ontology"]} == {"entry", "elapsed"}


def test_yaml_11_compatibility_for_role_names(tmp_path):
    source = _synthetic(tmp_path, two_directions=True)
    authored = json.loads(source.read_bytes())
    authored["fact_types"][0]["roles"][1]["role_name"] = "on"
    authored["fact_types"][0]["constraints"][0]["roles"] = ["on"]
    source.write_text(json.dumps(authored))
    bundle = render_ossie(source, output_format="yaml")
    reader = YAML(typ="safe", pure=True)
    reader.version = (1, 1)
    doc = reader.load(bundle.document)
    assert doc["ontology"][0]["relationships"][0]["roles"][0]["name"] == "on"
    ONTOLOGY.validate(doc)


def test_strict_keeps_empty_population_containers(tmp_path):
    source = _synthetic(tmp_path)
    authored = json.loads(source.read_bytes())
    authored["version"] = 4
    authored["reference_populations"] = []
    authored["fact_types"][0]["sample_population"] = []
    source.write_text(json.dumps(authored))
    bundle = render_ossie(source, output_format="json", strict=True)
    rows = {
        row["pointer"]: row["disposition"] for row in json.loads(bundle.loss_report)["dispositions"]
    }
    assert rows["/reference_populations"] == rows["/fact_types/0/sample_population"] == "extension"


def test_deontic_and_proposed_uniqueness_stay_in_sidecar():
    samples = ROOT / "src/gnd/examples/plan_apps/skill-sessions"
    for relative, facts in (
        ("claude-default/run-2/model.orm.json", {"course_has_title", "course_has_credits"}),
        (
            "claude-haiku/run-1/model.orm.yaml",
            {"student_has_id", "course_has_code", "term_has_label"},
        ),
    ):
        bundle = render_ossie(samples / relative, output_format="json")
        ontology = json.loads(bundle.document)
        found = [
            rel
            for c in ontology["ontology"]
            for rel in c.get("relationships", ())
            if rel["name"] in facts
        ]
        assert {rel["name"] for rel in found} == facts
        assert all("multiplicity" not in rel for rel in found)


def test_cyclic_subtypes_refuse_before_publication(tmp_path, capsys):
    source = tmp_path / "cycle.json"
    source.write_text(
        json.dumps(
            {
                "version": 1,
                "object_types": [
                    {
                        "id": "a",
                        "name": "A",
                        "kind": "entity",
                        "subtype_of": ["b"],
                        "inherits_reference": False,
                    },
                    {
                        "id": "b",
                        "name": "B",
                        "kind": "entity",
                        "subtype_of": ["a"],
                        "inherits_reference": False,
                    },
                ],
                "fact_types": [],
            }
        )
    )
    destination = tmp_path / "out.yaml"
    assert cli.main(["export", "ossie", str(source), "--out", str(destination)]) == 3
    assert "ossie:cyclic-subtypes" in capsys.readouterr().err
    assert {p.name for p in tmp_path.iterdir()} == {"cycle.json"}


@pytest.mark.parametrize("kind", ["directory", "fifo", "depth", "non-json"])
def test_input_boundaries(tmp_path, kind, capsys):
    model = tmp_path / "input.yaml"
    if kind == "directory":
        model.mkdir()
    elif kind == "fifo":
        os.mkfifo(model)
    elif kind == "depth":
        model.write_text("source: " + "[" * 600 + "0" + "]" * 600)
    else:
        model.write_text(
            "version: 1\nobject_types: [{id: a, kind: value, primitive: String}]\n"
            "fact_types: []\nsource: {timestamp: 2026-11-10}\n"
        )
    out = tmp_path / "out.yaml"
    assert cli.main(["export", "ossie", str(model), "--out", str(out)]) == 3
    if kind in {"directory", "fifo"}:
        assert "not a regular file" in capsys.readouterr().err
    assert {p.name for p in tmp_path.iterdir()} == {"input.yaml"}


@pytest.mark.parametrize("when", ["before-withdrawal", "after-identity-check"])
def test_rollback_preserves_a_racing_replacement(tmp_path, monkeypatch, when):
    original_link = safefs.os.link
    original_stat = safefs.os.stat
    rollback_started = False
    replaced = False

    def replace():
        nonlocal replaced
        replaced = True
        replacement = tmp_path / "replacement"
        replacement.write_bytes(b"another writer")
        safefs.os.replace(replacement, tmp_path / "sidecar")

    def link(source, dest, **kwargs):
        nonlocal rollback_started
        if dest == "ontology":
            rollback_started = True
            if when == "before-withdrawal":
                replace()
            raise OSError("marker failure")
        return original_link(source, dest, **kwargs)

    def stat(name, **kwargs):
        observed = original_stat(name, **kwargs)
        if rollback_started and not replaced and kwargs.get("dir_fd") is not None:
            replace()
        return observed

    monkeypatch.setattr(safefs.os, "link", link)
    monkeypatch.setattr(safefs.os, "stat", stat)
    with pytest.raises(OSError, match="marker failure"):
        safefs.publish_new_files(
            [(tmp_path / name, b"ours") for name in ("report", "sidecar", "ontology")]
        )
    assert replaced
    assert (tmp_path / "sidecar").read_bytes() == b"another writer"
    assert {leaf.name for leaf in tmp_path.iterdir()} == {"sidecar"}


@pytest.mark.parametrize("staging_fsync", [1, 2, 3])
def test_no_publication_if_a_staged_write_fails(tmp_path, monkeypatch, staging_fsync):
    original = safefs.os.fsync
    calls = 0

    def fsync(descriptor):
        nonlocal calls
        calls += 1
        if calls == staging_fsync:
            raise OSError("staging fault")
        return original(descriptor)

    monkeypatch.setattr(safefs.os, "fsync", fsync)
    with pytest.raises(OSError, match="staging fault"):
        safefs.publish_new_files(
            [(tmp_path / name, b"ours") for name in ("report", "sidecar", "ontology")]
        )
    assert not list(tmp_path.iterdir())


def test_proposed_alethic_uniqueness_is_not_projected_as_multiplicity(tmp_path):
    source = _synthetic(tmp_path)
    authored = json.loads(source.read_bytes())
    constraint = authored["fact_types"][0]["constraints"][0]
    constraint.update(
        source="llm-inferred",
        status="proposed",
        rationale="Proposed independently of the confirmed rules.",
        provenance={"rationale_world_fact": "A hypothetical unique reading."},
    )
    source.write_text(json.dumps(authored))
    bundle = render_ossie(source, output_format="json")
    ontology = json.loads(bundle.document)
    assert "multiplicity" not in ontology["ontology"][0]["relationships"][0]
    by_pointer = {
        row["pointer"]: row["disposition"] for row in json.loads(bundle.loss_report)["dispositions"]
    }
    assert by_pointer["/fact_types/0/constraints/0"] == "extension"


def test_rn0_k1_ossie_surfaces_are_every_mode_because_exports_carry_model_literals():
    """RN0 review K1: an export writes value-constraint literals in every disclosure mode.

    The table must not call these commands value-free while that is so. The sample and
    reference populations are omitted; the literals a constraint names are not.
    """
    from gnd import disclosure

    source = MILESTONE / "evidence/OS2/corpus-r2/model.orm.json"
    unset = render_ossie(source, output_format="json", strict=True)
    with disclosure.invocation("customer"):
        customer = render_ossie(source, output_format="json", strict=True)
    assert b"'Retail'" in customer.document
    assert (customer.document, customer.sidecar, customer.loss_report) == (
        unset.document, unset.sidecar, unset.loss_report)
    for leaf in ("gnd export ossie", "gnd import ossie"):
        assert disclosure.SURFACES[leaf].kind == "every-mode", leaf
