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

    document = (json.loads(document_text) if document_text.startswith("{")
                else dict(YAML(typ="safe").load(document_text)))
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
    # The reader gives !!pairs as a list of tuples: the first entry is named.
    ("x: !!pairs [{a: 1}]", "tag !!pairs"),
])
def test_e2_each_value_outside_json_is_named(tmp_path, line, kind):
    work = _staff(tmp_path, _with_source(line))
    assert run_main(["validate", str(work / "staff.orm.yaml")]).returncode == 0
    result = _preview(work, _proposal(work))
    assert result.returncode == 3, _text(result)
    path = "source.x[0]" if kind == "tag !!pairs" else "source.x"
    assert f"current model validation failed: {path} holds a {kind}," in _text(result)


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


# Review regressions (notes/followup-evolve-loading-agent-review.md).


@pytest.mark.parametrize("stamp", ["2024-01-01T10:00:00+02:00", "2024-01-01T10:00:00Z"])
def test_rv1_discover_keeps_a_zoned_timestamp_as_the_safe_reader_did(tmp_path, stamp):
    """Review B1: discover exited 0 on the base and crashed on the round-trip
    TimeStamp; evolve then names the timestamp."""
    from ruamel.yaml import YAML

    from gnd.evolve.service import _parse_model_text

    text = f"x: {stamp}\n"
    kept = _parse_model_text(text)["x"]
    expected = YAML(typ="safe").load(text)["x"]
    assert (type(kept), kept, kept.tzinfo) == (type(expected), expected, expected.tzinfo)
    work = _staff(tmp_path, _with_source(f"created: {stamp}"))
    discovered = _discover(work)
    assert discovered.returncode == 0, _text(discovered)
    result = _preview(work, work / "discovered.json")
    assert result.returncode == 3, _text(result)
    assert "source.created holds a timestamp," in _text(result)


def _long_key_description(tmp_path: Path, *, model: str) -> Path:
    from ruamel.yaml import YAML

    document = dict(YAML(typ="safe").load(STAFF))
    document["object_types"][0]["description"] = {"summary": "s", "x" * 1100: 1}
    work = tmp_path / "ws"
    work.mkdir()
    (work / "records").mkdir()
    if model.endswith(".json"):
        (work / model).write_text(json.dumps(document), encoding="utf-8")
    else:
        import io

        stream = io.StringIO()
        YAML().dump(document, stream)  # block style: the long key is an explicit "? " key
        (work / model).write_text(stream.getvalue(), encoding="utf-8")
    assert run_main(["validate", str(work / model)]).returncode == 0
    return work


@pytest.mark.parametrize("model", ["staff.orm.yaml", "staff.json"])
def test_rv2_a_json_document_is_not_put_through_the_yaml_scanner(tmp_path, model):
    """Review B2: a key over YAML's 1024-character implicit-key limit is valid
    JSON; the YAML guard made its JSON candidate (or JSON model) exit 70."""
    from ruamel.yaml import YAML

    work = _long_key_description(tmp_path, model=model)
    document = dict(YAML(typ="safe").load(STAFF))
    document["object_types"][0]["description"] = {"summary": "s", "x" * 1100: 1}
    result = _preview(work, _proposal(work, model=model, document_text=json.dumps(document)),
                      model=model)
    assert result.returncode == 0, _text(result)


def test_rv3_every_parse_refusal_lands_in_the_malformed_band():
    """Review H1: guard and YAML refusals carried no CLI marker and exited 70."""
    from gnd.evolve.cli_service import _evolve_error_exit
    from gnd.evolve.service import EvolutionError, _parse_model_text

    deep = "x: " + "[" * 80 + "]" * 80 + "\n"
    for text, label in [(deep, "current model"), ("a: [unclosed\n", "current model"),
                        ("a: [unclosed\n", "staged candidate model at finalize")]:
        with pytest.raises(EvolutionError) as caught:
            _parse_model_text(text, label=label)
        assert _evolve_error_exit(caught.value) == 3, str(caught.value)


@pytest.mark.parametrize(("line", "kind"), [("x: !!str {b: 1}", "tag !!str"),
                                            ("x: !!str [1]", "tag !!str")])
def test_rv4_a_core_scalar_tag_on_a_collection_is_named(tmp_path, line, kind):
    """Review H1: the safe reader refused these; the walk passed them as plain."""
    from gnd.evolve.service import EvolutionError, _json_document
    from gnd.model import parse_model_document

    document = parse_model_document(f"{line}\n".encode(), source="m.orm.yaml")
    with pytest.raises(EvolutionError, match=f"^m validation failed: x holds a {kind},"):
        _json_document(document, label="m")


# Amendment r2 (spec r2.4; rulings D6-A, D7-A, D8-A).


@pytest.mark.parametrize(("value", "spelled"), [(".inf", ".inf"), ("-.inf", "-.inf"), (".nan", ".nan")])
def test_q1_discover_writes_a_non_finite_float_and_evolve_names_it(tmp_path, value, spelled):
    """IKE-Q1: the base exits 1 (a traceback in the candidate writer)."""
    work = _staff(tmp_path, _with_source(f"x: {value}"))
    discovered = _discover(work)
    assert discovered.returncode == 0, _text(discovered)
    candidate = json.loads((work / "discovered.json").read_text())["candidate_model"]["text"]
    assert f"x: {spelled}\n" in candidate
    result = _preview(work, work / "discovered.json")
    assert result.returncode == 3, _text(result)
    assert "current model validation failed: source.x holds a non-finite float," in _text(result)


def _dated_recovery_bundle(root: Path) -> Path:
    import sys

    sys.path.insert(0, str(REPO_ROOT / "tests"))
    from test_recovery_adversarial import _write_bundle

    _write_bundle(root)
    text = (root / "model.orm.yaml").read_text()
    document = json.loads(text)
    lines = [f"version: {document['version']}", f"model_id: {document['model_id']}",
             "source:", "  kind: codebase", "  created: 2024-01-01",
             f"object_types: {json.dumps(document['object_types'])}",
             "fact_types: []", "constraints: []", "rejected_proposals: []", ""]
    (root / "model.orm.yaml").write_text("\n".join(lines))
    report = json.loads((root / "model.recovery.json").read_text())
    for out in report["outputs"]:
        if out["path"] == "model.orm.yaml":
            out["sha256"] = hashlib.sha256((root / "model.orm.yaml").read_bytes()).hexdigest()
    (root / "model.recovery.json").write_text(json.dumps(report, indent=2) + "\n")
    return root


def test_q2a_recovery_verify_names_a_dated_value(tmp_path):
    """IKE-Q2: the base exits 3 with the unnamed json.dumps message."""
    root = _dated_recovery_bundle(tmp_path / "bundle")
    assert run_main(["validate", str(root / "model.orm.yaml")]).returncode == 0
    result = run_main(["recovery", "verify", str(root), str(root / "model.recovery.json"),
                       "--model", str(root / "model.orm.yaml"),
                       "--verbalization", str(root / "model.verbalization.txt")])
    assert result.returncode == 3, _text(result)
    errors = json.loads(result.stdout)["errors"]
    assert errors == [("invalid-model-value: source.created holds a date, which the recovery "
                       "verbalization cannot represent; quote it or remove it")]


def test_q2b_the_verbalizer_refuses_by_type(tmp_path):
    from gnd.model_verbalization import VerbalizationError, render_model_verbalization

    root = _dated_recovery_bundle(tmp_path / "bundle")
    with pytest.raises(VerbalizationError, match="cannot represent"):
        render_model_verbalization(root / "model.orm.yaml")


def test_h4_the_shared_helper_raises_the_binders_own_errors(tmp_path, monkeypatch):
    import gnd.model

    dispatch = REPO_ROOT / "tests" / "fixtures" / "reference-corpus" / "dispatch"
    data = (dispatch / "model.orm.yaml").read_bytes()
    model, context = gnd.model.load_model_bytes_bound(
        data, source=dispatch / "model.orm.yaml", root=dispatch)
    assert context is not None and model._references is None
    attached, context = gnd.model.load_model_bytes_bound(
        data, source=dispatch / "model.orm.yaml", root=dispatch, attach=True)
    assert attached._references is context
    staff, none = gnd.model.load_model_bytes_bound(
        STAFF.encode(), source="staff.orm.yaml", root=tmp_path)
    assert none is None and not staff.reference_populations
    probe = OSError("probe")

    def refusing(model, *, root):
        raise probe

    monkeypatch.setattr(gnd.model, "bind_references", refusing)
    with pytest.raises(OSError) as caught:
        gnd.model.load_model_bytes_bound(data, source=dispatch / "model.orm.yaml", root=dispatch)
    assert caught.value is probe


# exp.session_replay._model is an RF8-frozen moved body with no successor
# mechanism, so it keeps its own bind (spec finding F11); H3 still pins it.
@pytest.mark.parametrize("home", ["discover", "lean", "souffle", "pyrel", "witness",
                                  "judgments"])
def test_h2_every_home_binds_through_the_shared_helper(tmp_path, monkeypatch, home):
    from support import reference_homes

    import gnd.model

    real = gnd.model.bind_declared_references
    calls = []

    def counting(model, *, root, attach=False):
        calls.append(root)
        return real(model, root=root, attach=attach)

    monkeypatch.setattr(gnd.model, "bind_declared_references", counting)
    work = reference_homes.workspace(tmp_path, None)
    reference_homes.run(home, work, tmp_path, monkeypatch)
    assert calls, f"{home} bound its references without the shared helper"


H3_BEFORE = json.loads((REPO_ROOT / "tests" / "fixtures" / "induced_knowledge"
                        / "reference-homes-before-r2.json").read_text())["outcomes"]

# IKE-Q3 (notes/followup-ike-q3-spec.md, rulings D1-A..D3-A): the two homes that
# leaked an ArtifactError now refuse by name. The fixture keeps the before-r2
# measurement; these four rows are the ruled outcomes.
IKE_Q3_RULED = {
    "discover/missing": ["return", 66, None],
    "discover/linked": ["return", 74, None],
    "judgments/missing": ["return", 3, {"message": "invalid bound judgment input",
                                        "reason": "binding"}],
    "judgments/linked": ["return", 3, {"message": "invalid bound judgment input",
                                       "reason": "binding"}],
}


@pytest.mark.parametrize("key", sorted(H3_BEFORE))
def test_h3_every_homes_outcome_is_unchanged(tmp_path, monkeypatch, key):
    """D6-A: adopting the helper changes no home's outcome, except the four
    rows IKE-Q3 ruled (discover and judgments on a missing or linked reference)."""
    from support import reference_homes

    home, damage = key.split("/")
    work = reference_homes.workspace(tmp_path, None if damage == "intact" else damage)
    expected = IKE_Q3_RULED.get(key, H3_BEFORE[key])
    assert reference_homes.run(home, work, tmp_path, monkeypatch) == expected


# r2 review regressions (notes/followup-evolve-loading-agent-review.md, round 2).


def _recovery_bundle(root: Path, source_lines: list[str]) -> Path:
    """The recovery test bundle with its model's source replaced, the complete
    verbalization re-rendered as the base did, and both digests rebound."""
    import sys

    import gnd.model_verbalization as verbalizer

    sys.path.insert(0, str(REPO_ROOT / "tests"))
    from test_recovery_adversarial import _write_bundle

    _write_bundle(root)
    document = json.loads((root / "model.orm.yaml").read_text())
    lines = ["version: 1", f"model_id: {document['model_id']}", "source:", *source_lines,
             f"object_types: {json.dumps(document['object_types'])}",
             "fact_types: []", "constraints: []", "rejected_proposals: []", ""]
    (root / "model.orm.yaml").write_text("\n".join(lines))
    guard = getattr(verbalizer, "_refuse_values_outside_json", None)
    if guard is not None:
        verbalizer._refuse_values_outside_json = lambda loaded: None
    try:
        rendered = verbalizer.render_model_verbalization(root / "model.orm.yaml")
    finally:
        if guard is not None:
            verbalizer._refuse_values_outside_json = guard
    (root / "model.verbalization.txt").write_text(rendered)
    report = json.loads((root / "model.recovery.json").read_text())
    for out in report["outputs"]:
        if out["path"] in ("model.orm.yaml", "model.verbalization.txt"):
            out["sha256"] = hashlib.sha256((root / out["path"]).read_bytes()).hexdigest()
    (root / "model.recovery.json").write_text(json.dumps(report, indent=2) + "\n")
    return root


def _recovery_verify(root: Path):
    return run_main(["recovery", "verify", str(root), str(root / "model.recovery.json"),
                     "--model", str(root / "model.orm.yaml"),
                     "--verbalization", str(root / "model.verbalization.txt")])


@pytest.mark.parametrize("line", ["  meta: !!omap [{a: 1}, {b: 2}]",
                                  "  meta: !!pairs [{a: 1}, {a: 2}]",
                                  "  meta: !foo {a: 1}"])
def test_rv5_recovery_still_verifies_what_json_could_write(tmp_path, line):
    """Review round 2, B1: these rendered and verified before r2; json.dumps
    writes an ordered map, a list of pairs and a tagged mapping."""
    root = _recovery_bundle(tmp_path / "bundle", ["  kind: codebase", line])
    result = _recovery_verify(root)
    assert result.returncode == 0, _text(result)


def test_rv6_the_model_origin_refusal_keeps_its_precedence(tmp_path):
    """Review round 2, H1: a non-codebase model is invalid-model-origin, as before."""
    root = tmp_path / "bundle"
    import sys

    sys.path.insert(0, str(REPO_ROOT / "tests"))
    from test_recovery_adversarial import _write_bundle

    _write_bundle(root)
    document = json.loads((root / "model.orm.yaml").read_text())
    lines = ["version: 1", f"model_id: {document['model_id']}", "source:",
             "  kind: text-conversation", "  created: 2024-01-01",
             f"object_types: {json.dumps(document['object_types'])}",
             "fact_types: []", "constraints: []", "rejected_proposals: []", ""]
    (root / "model.orm.yaml").write_text("\n".join(lines))
    report = json.loads((root / "model.recovery.json").read_text())
    for out in report["outputs"]:
        if out["path"] == "model.orm.yaml":
            out["sha256"] = hashlib.sha256((root / "model.orm.yaml").read_bytes()).hexdigest()
    (root / "model.recovery.json").write_text(json.dumps(report, indent=2) + "\n")
    result = _recovery_verify(root)
    assert result.returncode == 3, _text(result)
    assert json.loads(result.stdout)["errors"][0].startswith("invalid-model-origin:")


def test_rv7_the_verbalizer_names_an_explicit_str_tag(tmp_path):
    """Review round 2, C1: a !!str-tagged scalar loads as a TaggedScalar that
    json.dumps cannot write; the verbalizer refused it with TypeError."""
    from gnd.model_verbalization import VerbalizationError, render_model_verbalization

    model = tmp_path / "m.orm.yaml"
    model.write_text("version: 1\nmodel_id: m\nsource:\n  kind: codebase\n  note: !!str 5\n"
                     "object_types: []\nfact_types: []\n")
    assert run_main(["validate", str(model)]).returncode == 0
    with pytest.raises(VerbalizationError, match=r"source\.note holds a tag !!str"):
        render_model_verbalization(model)


@pytest.mark.parametrize("value", [float("inf"), float("-inf"), float("nan")])
def test_rv8_the_candidate_writer_spells_non_finite_floats(value):
    """Review round 2, C2: candidate_text serves discover and gnd import
    ilp-rules alike; both now write a non-finite float as YAML."""
    import math

    from gnd.discover.output import candidate_text
    from gnd.evolve.service import _parse_model_text
    back = _parse_model_text(candidate_text({"x": value}))["x"]
    assert math.isnan(back) if math.isnan(value) else back == value
