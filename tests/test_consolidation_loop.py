"""One terminal decision per group, with restart through an interrupted publication."""

import json
from copy import deepcopy
from hashlib import sha256

import pytest
import test_evolve_additive_policy as policy

from gnd.evolve import EvolutionService
from gnd.evolve.consolidation import step


def workspace(tmp_path):
    value = {"id": "code", "kind": "value", "primitive": "Integer", "name": "Code"}
    facts = []
    for identifier, text, number in (("listed", "code 2", 2), ("archived", "code 3", 3)):
        digest = sha256(text.encode()).hexdigest()
        (tmp_path / (identifier + ".txt")).write_text(text)
        span = {"document_sha256": digest, "start": 0, "end": len(text), "excerpt_sha256": digest}
        facts.append({"id": identifier, "reading": "{Code} is listed",
            "roles": [{"role_name": "code", "object_type": "code"}],
            "sample_population": [{"code": number}],
            "provenance": {"spans": [span], "sample_spans": [{"row": 0, "span": span}]}})
    doc = {"version": 1, "source": {"kind": "fixture"}, "object_types": [value], "fact_types": facts}
    path = tmp_path / "model.orm.json"
    path.write_text(json.dumps(doc))
    (tmp_path / "model.verbalization.txt").write_text("initial\n")
    return path, doc


def decision(info, action, **more):
    group = info["group"]
    return {"model_sha256": info["model_sha256"], "group_id": group["group_id"],
            "evidence_sha256": group["evidence_sha256"], "actor": "owner:fixture", "action": action, **more}


def merge(path, doc, *, preserve=True):
    source, target = doc["fact_types"]
    after = deepcopy(target)
    if preserve:
        after["sample_population"].extend(deepcopy(source["sample_population"]))
        after["provenance"]["sample_spans"].append({"row": 1, "span": source["provenance"]["spans"][0]})
    ops = (policy._op("modify", policy._element("fact_types", target["id"]), before=target, after=after),
           policy._op("delete", policy._element("fact_types", source["id"]), before=source, operation_id="remove"))
    proposal = policy._proposal(path.read_text(), ops)
    service = EvolutionService(model_path=path, evidence_root=path.parent, allowed_project_root=path.parent)
    reviewed = service.preview(proposal)
    approved = service.preview(proposal, accepted_blast_radius_sha256=reviewed.blast_radius.report_sha256)
    return {"preview": approved.model_dump(mode="json"), "moves": [{"source": source["id"], "target": target["id"],
                "roles": {"code": "code"}}]}


@pytest.mark.parametrize("interrupt", [False, True])
def test_leave_merge_and_recover(tmp_path, monkeypatch, interrupt):
    path, doc = workspace(tmp_path)
    first = step(path)
    leave = decision(first, "leave")
    left = step(path, decision=leave)
    assert left["reason"] == "completed"
    assert step(path, decision=leave)["reason"] == "already-completed"
    second = step(path)
    assert second["group"]["group_id"] != first["group"]["group_id"]
    accept = decision(second, "merge", **merge(path, doc))
    if interrupt:
        def stop_after_publication(self, pending):
            raise RuntimeError("fixture interruption after apply")
        with monkeypatch.context() as m:
            m.setattr(EvolutionService, "finalize", stop_after_publication)
            with pytest.raises(RuntimeError, match="interruption"):
                step(path, decision=accept)
        result = step(path)
    else:
        result = step(path, decision=accept)
    assert result["reason"] == "completed"
    assert result["decision"]["after"] == sha256(path.read_bytes()).hexdigest()
    assert step(path, decision=accept)["reason"] == "already-completed"
    assert step(path)["reason"] == "no-eligible-group"
    final = json.loads(path.read_text())["fact_types"]
    assert len(final) == 1 and len(final[0]["sample_population"]) == 2
    assert {s["span"]["document_sha256"] for s in final[0]["provenance"]["sample_spans"]} == {
        f["provenance"]["spans"][0]["document_sha256"] for f in doc["fact_types"]}


def test_stale_or_incomplete_transfer_leaves_both_facts(tmp_path):
    path, doc = workspace(tmp_path)
    info = step(path)
    before = path.read_bytes()
    with pytest.raises(ValueError, match="lost a required"):
        step(path, decision=decision(info, "merge", **merge(path, doc, preserve=False)))
    with pytest.raises(ValueError, match="differs"):
        step(path, decision={**decision(info, "leave"), "model_sha256": "a" * 64})
    assert path.read_bytes() == before
    assert step(path, max_items=0)["reason"] == "items-limit"
    assert step(path, max_decisions=0)["reason"] == "decision-limit"


@pytest.mark.parametrize("target,accepted", [("customercodes", True), ("unrelated", False)])
def test_object_merge_redirects_roles_to_selected_survivor(tmp_path, target, accepted):
    path = tmp_path / "model.orm.json"
    types = [{"id": key, "name": key, "kind": "value", "primitive": "Integer"}
             for key in ("customercode", "customercodes", "unrelated")]
    fact = {"id": "listed", "reading": "{customercode} is listed",
            "roles": [{"role_name": "n", "object_type": "customercode"}], "sample_population": [{"n": 5}]}
    path.write_text(json.dumps({"version": 1, "object_types": types, "fact_types": [fact]}))
    (tmp_path / "model.verbalization.txt").write_text("original")
    info = step(path)
    assert set(info["group"]["members"]) == {"customercode", "customercodes"}
    new = deepcopy(fact)
    new.update(reading="{" + target + "} is listed")
    new["roles"][0]["object_type"] = target
    ops = (policy._op("modify", policy._element("fact_types", "listed"), before=fact, after=new),
           policy._op("delete", policy._element("object_types", "customercode"), before=types[0], operation_id="del"))
    service = EvolutionService(model_path=path, evidence_root=tmp_path)
    proposal = policy._proposal(path.read_text(), ops)
    preview = service.preview(proposal)
    review = service.preview(proposal, accepted_blast_radius_sha256=preview.blast_radius.report_sha256)
    choice = decision(info, "merge", preview=review.model_dump(mode="json"))
    if accepted:
        assert step(path, decision=choice)["reason"] == "completed"
        assert json.loads(path.read_text())["fact_types"][0]["roles"][0]["object_type"] == target
    else:
        before = path.read_bytes()
        with pytest.raises(ValueError, match="surviving group member"):
            step(path, decision=choice)
        assert path.read_bytes() == before


def test_recovery_matches_uninterrupted_history(tmp_path, monkeypatch):
    outcomes = []
    for interrupted in (False, True):
        folder = tmp_path / ("interrupted" if interrupted else "uninterrupted")
        folder.mkdir()
        path, doc = workspace(folder)
        first = step(path)
        step(path, decision=decision(first, "leave"))
        choice = decision(step(path), "merge", **merge(path, doc))
        if interrupted:
            def crash(self, state):
                raise RuntimeError("restart")
            with monkeypatch.context() as m:
                m.setattr(EvolutionService, "finalize", crash)
                with pytest.raises(RuntimeError, match="restart"):
                    step(path, decision=choice)
            step(path)
        else:
            step(path, decision=choice)
        journal = next((folder / ".gnd-consolidation").glob("*/decisions.json"))
        outcomes.append((path.read_bytes(), json.loads(journal.read_text()), step(path)))
    assert outcomes[0] == outcomes[1]


def test_changed_evidence_reopens_a_declined_group(tmp_path):
    path, doc = workspace(tmp_path)
    first = step(path)
    step(path, decision=decision(first, "leave"))
    changed = deepcopy(doc)
    changed["fact_types"][0]["provenance"]["spans"].append(doc["fact_types"][1]["provenance"]["spans"][0])
    path.write_text(json.dumps(changed))
    next_group = step(path)["group"]
    assert next_group["group_id"] == first["group"]["group_id"]
    assert next_group["evidence_sha256"] != first["group"]["evidence_sha256"]


def test_conflicting_transferred_values_refuse_publication(tmp_path):
    path, doc = workspace(tmp_path)
    for i, fact in enumerate(doc["fact_types"]):
        fact["roles"].append({"role_name": "value", "object_type": "code"})
        fact["reading"] = "{Code:code} denotes {Code:value}"
        fact["sample_population"][0] = {"code": 2, "value": i+1}
    doc["fact_types"][1]["constraints"] = [{"type": "uniqueness", "roles": ["code"],
        "modality": "deontic", "source": "user-supplied", "status": "confirmed",
        "provenance": {"rationale_world_fact": "Only one value per code."}}]
    path.write_text(json.dumps(doc))
    info = step(path)
    kwargs = merge(path, doc)
    kwargs["moves"][0]["roles"]["value"] = "value"
    before = path.read_bytes()
    with pytest.raises(ValueError, match="affected constraint"):
        step(path, decision=decision(info, "merge", **kwargs))
    assert path.read_bytes() == before


def test_located_additive_growth_then_consolidation(tmp_path):
    from pathlib import Path

    from support.cli_runner import run_main

    from gnd.evolve import SourceDocumentLocator

    base = Path(__file__).parent / "fixtures/unattended/conforming.orm.yaml"
    doc = policy._doc(base.read_text())
    primary = doc["fact_types"][0]
    another = deepcopy(primary)
    another["id"] = "other_order"
    another.pop("constraints", None)
    another["sample_population"] = []
    another["provenance"]["sample_spans"] = []
    doc["fact_types"].append(another)
    text = json.dumps(doc)
    line = b"Order 10 belongs to customer 1."
    digest = sha256(line).hexdigest()
    span = {"document_sha256": digest, "start": 0, "end": len(line), "excerpt_sha256": digest}
    appended = deepcopy(another)
    appended["sample_population"] = [primary["sample_population"][0]]
    appended["provenance"]["sample_spans"] = [{"row": 0, "span": span}]
    operations = (policy._op("add", SourceDocumentLocator(sha256=digest),
                             after={"sha256": digest, "label": "second"}, operation_id="declare"),
                  policy._op("modify", policy._element("fact_types", another["id"]), before=another, after=appended))
    paths = policy._cli_workspace(tmp_path, operations, before_text=text)
    source = tmp_path / "second.txt"
    source.write_bytes(line)
    args = ("--policy", "additive", "--sample-document", str(source))
    assert run_main(policy._preview_argv(paths, *args)).returncode == 0
    assert run_main(policy._apply_argv(paths, *args)).returncode == 0
    path = paths["model"]
    desired = {another["id"], primary["id"]}
    info = step(path)
    while set(info["group"]["members"]) != desired:
        step(path, decision=decision(info, "leave"))
        info = step(path)
    target = deepcopy(primary)
    target["provenance"]["sample_spans"].append({"row": len(target["sample_population"]), "span": span})
    target["sample_population"].append(primary["sample_population"][0])
    ops = (policy._op("modify", policy._element("fact_types", primary["id"]), before=primary, after=target),
           policy._op("delete", policy._element("fact_types", another["id"]), before=appended, operation_id="remove"))
    service = EvolutionService(model_path=path, evidence_root=paths["records"])
    proposal = policy._proposal(path.read_text(), ops, proposal_id="merge-orders")
    preview = service.preview(proposal)
    approved = service.preview(proposal, accepted_blast_radius_sha256=preview.blast_radius.report_sha256)
    roles = {r["role_name"]: r["role_name"] for r in primary["roles"]}
    chosen = decision(info, "merge", preview=approved.model_dump(mode="json"),
                      moves=[{"source": another["id"], "target": primary["id"], "roles": roles}])
    assert step(path, decision=chosen)["decision"]["conformance_exit"] == 0
    result = policy._doc(path.read_text())["fact_types"][0]
    assert result["sample_population"][0] == result["sample_population"][-1]
    assert result["provenance"]["sample_spans"][0]["span"] != result["provenance"]["sample_spans"][-1]["span"]


def test_demote_singleton_into_located_row(tmp_path):
    path, doc = workspace(tmp_path)
    entity = {"id": "onlycode", "kind": "entity", "reference": {"mode": "popular", "value_type": "code"}}
    doc["object_types"].append(entity)
    source = doc["fact_types"][0]
    source.update(reading="{onlycode} is listed")
    source["roles"][0]["object_type"] = "onlycode"
    path.write_text(json.dumps(doc))
    group = step(path)
    assert group["group"]["members"] == ["onlycode"]
    survivor = doc["fact_types"][1]
    after = deepcopy(survivor)
    after["sample_population"] += deepcopy(source["sample_population"])
    after["provenance"]["sample_spans"].append({"row": 1, "span": source["provenance"]["spans"][0]})
    ops = (policy._op("modify", policy._element("fact_types", survivor["id"]), before=survivor, after=after),
           policy._op("delete", policy._element("fact_types", source["id"]), before=source, operation_id="delete-fact"),
           policy._op("delete", policy._element("object_types", "onlycode"), before=entity, operation_id="delete-type"))
    service = EvolutionService(model_path=path, evidence_root=tmp_path)
    proposal = policy._proposal(path.read_text(), ops)
    radius = service.preview(proposal).blast_radius.report_sha256
    preview = service.preview(proposal, accepted_blast_radius_sha256=radius)
    choice = decision(group, "demote-to-row", preview=preview.model_dump(mode="json"),
                      moves=[{"source": source["id"], "target": survivor["id"], "roles": {"code": "code"}}])
    assert step(path, decision=choice)["decision"]["action"] == "demote-to-row"


def test_add_subtype_between_reviewed_members(tmp_path):
    path, doc = workspace(tmp_path)
    ref = {"mode": "popular", "value_type": "code"}
    objects = [{"id": key, "kind": "entity", "reference": ref} for key in ("customername", "customernames")]
    doc["object_types"] += objects
    doc["fact_types"] = []
    path.write_text(json.dumps(doc))
    before = objects[0]
    after = {**before, "subtype_of": ["customernames"], "inherits_reference": False}
    proposal = policy._proposal(path.read_text(), (
        policy._op("modify", policy._element("object_types", before["id"]), before=before, after=after),))
    service = EvolutionService(model_path=path, evidence_root=tmp_path)
    preview = service.preview(proposal)
    info = step(path)
    assert step(path, decision=decision(info, "link-subtype", preview=preview.model_dump(mode="json")))["reason"] == "completed"
