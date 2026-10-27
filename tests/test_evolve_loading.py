"""Evolve-loading follow-up: one loader, the validator's parser, named refusals.

Spec: .gnd-planning/milestones/induced-knowledge/notes/followup-evolve-loading-spec.md
(§8: E1-E4, J1-J3, W1, H1, D5, P1; rulings D1-A..D5-A). Fixtures are the
synthetic IK4 staff corpus and the IK5 orders corpus, copied to scratch.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from datetime import UTC, datetime
from pathlib import Path

import pytest
from support.cli_runner import run_main

REPO_ROOT = Path(__file__).resolve().parent.parent
IK4 = REPO_ROOT / "tests" / "fixtures" / "induced_knowledge" / "ik4-corpus"
IK5 = REPO_ROOT / "tests" / "fixtures" / "induced_knowledge" / "ik5-corpus"
STAFF = (IK4 / "staff.orm.yaml").read_text(encoding="utf-8")
TAGGED_EXTRA = "    description: {summary: s, extra: !foo {a: 1}}\n"


def _text(result) -> str:
    return (result.stdout + result.stderr).decode("utf-8", errors="replace")


def _staff(tmp_path: Path, model_text: str) -> Path:
    work = tmp_path / "ws"
    work.mkdir()
    (work / "records").mkdir()
    (work / "staff.orm.yaml").write_text(model_text, encoding="utf-8")
    shutil.copyfile(IK4 / "staff.population.yaml", work / "staff.population.yaml")
    return work


def _with_source(line: str) -> str:
    return STAFF.replace("  kind: fixture\n", f"  kind: fixture\n  {line}\n", 1)


def _with_person(line: str) -> str:
    return STAFF.replace("    name: Person\n", f"    name: Person\n{line}", 1)


def _proposal(work: Path, *, model: str = "staff.orm.yaml", candidate_text: str | None = None,
              document_text: str = STAFF) -> Path:
    """A one-op proposal against the bytes at ``work/model``. Its candidate is
    built from ``document_text`` (JSON-domain) unless ``candidate_text`` is given."""
    from ruamel.yaml import YAML

    from gnd.discover import output

    document = dict(YAML(typ="safe").load(document_text))
    constraint = {"type": "mandatory", "role": "person", "source": "user-supplied",
                  "status": "confirmed", "modality": "deontic", "rationale": "loading probe",
                  "provenance": {"user_quote": "Every person is on a team."}}
    ops = output.add_operations([(_first_fact_type(document), constraint)], prefix="ld")
    built = output.proposal(
        model_bytes=(work / model).read_bytes(), document=output.candidate_document(document, ops),
        ops=ops, actor="loading", requested_at=datetime(2026, 10, 27, tzinfo=UTC),
        origin="loading test", prefix="ld", rationale="one mandatory constraint")
    data = built.model_dump(mode="json")
    if candidate_text is not None:
        data["candidate_model"]["text"] = candidate_text
        data["candidate_model"]["sha256"] = hashlib.sha256(candidate_text.encode()).hexdigest()
    path = work / "proposal.json"
    path.write_bytes(output.canonical_bytes(data))
    return path


def _first_fact_type(document: dict) -> str:
    return str(document["fact_types"][0]["id"])


def _preview(work: Path, proposal: Path, model: str = "staff.orm.yaml"):
    return run_main(["evolve", "preview", str(work / model), str(proposal),
                     "--workspace", str(work), "--records", str(work / "records"),
                     "--out", str(work / "preview.json"), "--format", "json"])


def _apply(work: Path, proposal: Path, model: str = "staff.orm.yaml"):
    return run_main(["evolve", "apply", str(work / model), str(proposal),
                     "--preview", str(work / "preview.json"), "--workspace", str(work),
                     "--records", str(work / "records"), "--format", "json"])


def _discover(work: Path):
    return run_main([
        "discover", str(work / "staff.orm.yaml"), str(work / "staff.population.yaml"),
        "--out", str(work / "discovered.json"), "--report", str(work / "report.json"),
        "--actor", "loading", "--requested-at", "2026-10-27T00:00:00+00:00",
        "--families", "uniqueness"])


def test_e1_a_discover_proposal_on_a_dated_model_is_a_named_refusal(tmp_path):
    """IK4-Q3 / close reader one F2: the base exits 70."""
    work = _staff(tmp_path, _with_source("created: 2024-01-01"))
    assert run_main(["validate", str(work / "staff.orm.yaml")]).returncode == 0
    discovered = _discover(work)
    assert discovered.returncode == 0, _text(discovered)
    result = _preview(work, work / "discovered.json")
    assert result.returncode == 3, _text(result)
    assert "current model validation failed: source.created holds a date" in _text(result)
    assert not (work / "preview.json").exists()


@pytest.mark.parametrize(("line", "kind"), [
    ("x: 2024-01-01T10:00:00Z", "timestamp"),
    ("x: !!binary aGVsbG8=", "binary"),
    ("x: !!set {a, b}", "set"),
    ("x: .inf", "non-finite float"),
    ("x: .nan", "non-finite float"),
    ("x: !foo 3", "tag !foo"),
    ("x: !!omap [{a: 1}]", "tag !!omap"),
    ("x: !!pairs [{a: 1}]", "tag !!pairs"),
])
def test_e2_each_value_outside_json_is_named(tmp_path, line, kind):
    work = _staff(tmp_path, _with_source(line))
    assert run_main(["validate", str(work / "staff.orm.yaml")]).returncode == 0
    result = _preview(work, _proposal(work))
    assert result.returncode == 3, _text(result)
    assert f"current model validation failed: source.x holds a {kind}," in _text(result)


def test_e3_the_close_rows_tagged_extra_is_valid(tmp_path):
    work = _staff(tmp_path, _with_person(TAGGED_EXTRA))
    result = run_main(["validate", str(work / "staff.orm.yaml")])
    assert result.returncode == 0, _text(result)


def test_e3b_the_close_rows_tagged_extra_is_named_not_invalid_yaml(tmp_path):
    work = _staff(tmp_path, _with_person(TAGGED_EXTRA))
    result = _preview(work, _proposal(work))
    assert result.returncode == 3, _text(result)
    assert "not valid YAML" not in _text(result)
    assert ("current model validation failed: object_types[0].description.extra "
            "holds a tag !foo,") in _text(result)


def test_e4_a_candidate_alone_holding_a_date_is_named_before_replay(tmp_path):
    from gnd.discover.output import candidate_text
    from gnd.evolve.service import _parse_model_text

    work = _staff(tmp_path, STAFF)
    clean = json.loads(json.loads(_proposal(work).read_text())["candidate_model"]["text"])
    dated = candidate_text({**clean, "source": {**clean["source"], "created":
                            _parse_model_text("d: 2024-01-01\n")["d"]}})
    result = _preview(work, _proposal(work, candidate_text=dated))
    assert result.returncode == 3, _text(result)
    assert "candidate model validation failed: source.created holds a date" in _text(result)


def _orders(tmp_path: Path, *, as_json: bool) -> tuple[Path, Path]:
    """The IK5 corpus with its model copied to orders.json, as JSON text when
    ``as_json``. The ILP import runs on the YAML model its labels are bound to;
    the proposal is then re-pointed at the orders.json bytes."""
    from ruamel.yaml import YAML

    from gnd.discover import output

    work = tmp_path / "ws"
    shutil.copytree(IK5, work)
    (work / "records").mkdir()
    text = (work / "orders.orm.yaml").read_text(encoding="utf-8")
    if as_json:
        text = json.dumps(YAML(typ="safe").load(text), indent=2) + "\n"
    (work / "orders.json").write_text(text, encoding="utf-8")
    proposal = work / "i1.proposal.json"
    imported = run_main([
        "import", "ilp-rules", str(work / "orders.orm.yaml"), str(work / "i1.clauses.json"),
        "--labels", str(work / "m.labels.json"), "--reported-coverage", str(work / "i1.run.json"),
        "--target", "neutral", "--out", str(proposal),
        "--requested-at", "2026-10-26T00:00:00+00:00"])
    assert imported.returncode == 0, _text(imported)
    data = json.loads(proposal.read_text())
    data["expected_model_sha256"] = hashlib.sha256(text.encode()).hexdigest()
    proposal.write_bytes(output.canonical_bytes(data))
    return work, proposal


def test_j1_a_json_named_model_holding_yaml_is_refused(tmp_path):
    """D2-A, successor of test_r1_a_json_named_reference_free_model_previews_as_at_b:
    gnd validate refuses this model, and now evolve does too."""
    work, proposal = _orders(tmp_path, as_json=False)
    assert run_main(["validate", str(work / "orders.json")]).returncode == 3
    result = _preview(work, proposal, model="orders.json")
    assert result.returncode == 3, _text(result)
    assert "current model validation failed: model JSON input refused" in _text(result)
    assert not (work / "preview.json").exists()


def test_j2_a_json_model_previews_and_applies(tmp_path):
    work, proposal = _orders(tmp_path, as_json=True)
    assert run_main(["validate", str(work / "orders.json")]).returncode == 0
    result = _preview(work, proposal, model="orders.json")
    assert result.returncode == 0, _text(result)
    applied = _apply(work, proposal, model="orders.json")
    assert applied.returncode == 0, _text(applied)
    candidate = json.loads(proposal.read_text())["candidate_model"]["text"]
    assert (work / "orders.json").read_text(encoding="utf-8") == candidate


def test_j3_a_yaml_candidate_for_a_json_model_is_refused(tmp_path):
    import io

    from ruamel.yaml import YAML

    from gnd.discover import output

    work, proposal = _orders(tmp_path, as_json=True)
    data = json.loads(proposal.read_text())
    stream = io.StringIO()
    YAML(typ="safe").dump(json.loads(data["candidate_model"]["text"]), stream)
    data["candidate_model"]["text"] = stream.getvalue()
    data["candidate_model"]["sha256"] = hashlib.sha256(stream.getvalue().encode()).hexdigest()
    proposal.write_bytes(output.canonical_bytes(data))
    result = _preview(work, proposal, model="orders.json")
    assert result.returncode == 3, _text(result)
    assert "candidate model validation failed: model JSON input refused" in _text(result)


def test_w1_a_binder_refusal_is_wrapped_once(tmp_path, monkeypatch):
    """IK4-Q2 review R4: the binder's own ReferenceInputError is the cause."""
    import gnd.model
    from gnd.evolve import service
    from gnd.evolve.service import EvolutionError
    from gnd.model import ReferenceInputError

    dispatch = REPO_ROOT / "tests" / "fixtures" / "reference-corpus" / "dispatch"
    refusal = ReferenceInputError("probe refusal")

    def refusing(model, *, root):
        raise refusal

    monkeypatch.setattr(gnd.model, "bind_references", refusing)
    loader = getattr(service, "_load_model_document", None) or service._load_model_bytes
    with pytest.raises(EvolutionError, match="current model validation failed: probe refusal") as caught:
        loader((dispatch / "model.orm.yaml").read_bytes(), label="current model",
               model_path=dispatch / "model.orm.yaml")
    assert caught.value.__cause__ is refusal


def test_h1_every_load_goes_through_the_one_loader(tmp_path, monkeypatch):
    """IK4-Q2-R1: preview loads twice; apply rebuilds the preview (two), loads
    current, candidate and staged, and its chained finalize loads two: nine.
    A loaded model is never re-parsed apart from it; apply's gate parse of the
    preview text, before anything is loaded, is the one other parse."""
    from gnd.evolve import service

    loads: list[str] = []
    parses: list[str] = []
    real_load = getattr(service, "_load_model_document", None)
    real_parse = service._parse_model_text
    assert real_load is not None, "no single evolve loader"

    def counting_load(data, *, label, **kwargs):
        loads.append(label)
        return real_load(data, label=label, **kwargs)

    def counting_parse(text, label="candidate model"):
        parses.append(label)
        return real_parse(text, label)

    monkeypatch.setattr(service, "_load_model_document", counting_load)
    monkeypatch.setattr(service, "_parse_model_text", counting_parse)
    work = _staff(tmp_path, STAFF)
    proposal = _proposal(work)
    assert _preview(work, proposal).returncode == 0
    assert (len(loads), len(parses)) == (2, 0)
    assert _apply(work, proposal).returncode == 0
    assert len(loads) == 9, loads
    assert len(parses) == 1, parses


def test_d5_discover_reads_a_tagged_model(tmp_path):
    """D4-A: discover shares the validator's parser, so a valid tagged model is
    discovered (the base exits 1 with a traceback); evolve then names the tag."""
    work = _staff(tmp_path, _with_person(TAGGED_EXTRA))
    discovered = _discover(work)
    assert discovered.returncode == 0, _text(discovered)
    result = _preview(work, work / "discovered.json")
    assert result.returncode == 3, _text(result)
    assert "object_types[0].description.extra holds a tag !foo," in _text(result)


@pytest.mark.parametrize("text", [
    STAFF,
    json.dumps({"version": 1, "model_id": "m", "object_types": [], "fact_types": []}),
    "{version: 1, model_id: m, object_types: [], fact_types: []}\n",
])
def test_p1_the_shared_parser_is_the_validators(text):
    from gnd.model import load_model_bytes, parse_model_document

    data = text.encode()
    load_model_bytes(data, source="m.orm.yaml")
    assert dict(parse_model_document(data, source="m.orm.yaml")) == dict(
        __import__("ruamel.yaml", fromlist=["YAML"]).YAML(typ="safe").load(text))


def test_p1_the_shared_parser_keeps_the_loaders_refusals():
    from gnd.model import ModelLoadError, parse_model_document

    with pytest.raises(ModelLoadError, match="alias"):
        parse_model_document(b"x: &a [1]\ny: *a\n", source="m.orm.yaml")
    with pytest.raises(ModelLoadError, match="JSON"):
        parse_model_document(b"version: 1\n", source="m.json")
    with pytest.raises(ModelLoadError, match="10 MiB"):
        parse_model_document(b" " * (10 * 1024 * 1024 + 1), source="m.orm.yaml")


def test_the_walk_names_a_non_string_key():
    from gnd.evolve.service import EvolutionError, _json_document

    with pytest.raises(EvolutionError, match=r"^m validation failed: source holds a non-string key,"):
        _json_document({"source": {1: "a"}}, label="m")
