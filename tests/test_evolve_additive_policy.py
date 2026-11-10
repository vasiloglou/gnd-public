"""MG2: the additive policy on gnd evolve preview and apply.

Spec: .gnd-planning/milestones/model-growth-guardrails/notes/phase-MG2-spec.md
(§Tests T1-T14). The fixture is tests/fixtures/evolve-policy/base.orm.yaml:
customer_places_order is populated (two sample rows), order_has_amount is the
unpopulated control, and no `operations` section exists, so the operations
gate never pre-empts a policy cell.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, get_args

import pytest
from pydantic import ValidationError
from ruamel.yaml import YAML
from support.cli_runner import run_main

REPO_ROOT = Path(__file__).resolve().parent.parent
BASE = REPO_ROOT / "tests" / "fixtures" / "evolve-policy" / "base.orm.yaml"
CONTRACT = REPO_ROOT / "src/gnd/skills/gnd-model-evolve/references/evolution-contract.md"
POPULATED = "customer_places_order"
CONTROL = "order_has_amount"


# --- builders ---------------------------------------------------------------


def _doc(text: str | None = None) -> dict[str, Any]:
    return YAML(typ="safe").load(text if text is not None else BASE.read_text(encoding="utf-8"))


def _fact(document: dict[str, Any], fact_type_id: str) -> dict[str, Any]:
    return next(item for item in document["fact_types"] if item["id"] == fact_type_id)


def _object(document: dict[str, Any], object_type_id: str) -> dict[str, Any]:
    return next(item for item in document["object_types"] if item["id"] == object_type_id)


def _constraint(document: dict[str, Any], fact_type_id: str, family: str, occurrence: int = 0) -> dict[str, Any]:
    matches = [item for item in _fact(document, fact_type_id)["constraints"] if item["type"] == family]
    return matches[occurrence]


def _hosted(document: dict[str, Any], family: str) -> dict[str, Any]:
    return next(item for item in document["constraints"] if item["type"] == family)


def _op(kind: str, locator: Any, *, before: Any = None, after: Any = None, operation_id: str = "op") -> Any:
    from gnd.evolve import EvolutionOperation, EvolutionOperationKind

    return EvolutionOperation(
        operation_id=operation_id,
        kind=EvolutionOperationKind(kind),
        locator=locator,
        before=copy.deepcopy(before),
        after=copy.deepcopy(after),
    )


def _element(collection: str, element_id: str) -> Any:
    from gnd.evolve import ElementLocator

    return ElementLocator(collection=collection, element_id=element_id)


def _role(fact_type_id: str, role_name: str) -> Any:
    from gnd.evolve import RoleLocator

    return RoleLocator(fact_type_id=fact_type_id, role_name=role_name)


def _constraint_locator(host: str | None, constraint: dict[str, Any] | None, family: str, occurrence: int = 0) -> Any:
    from gnd.evolve import ConstraintLocator, canonical_sha256

    digest = canonical_sha256(constraint) if constraint is not None else None
    if host is None:
        return ConstraintLocator(host="model", family=family, canonical_before_sha256=digest,
                                 duplicate_occurrence=occurrence)
    return ConstraintLocator(host="fact_type", host_id=host, family=family,
                             canonical_before_sha256=digest, duplicate_occurrence=occurrence)


def _proposal(before_text: str, operations: tuple[Any, ...], *, artifacts: tuple[Any, ...] = (),
              proposal_id: str = "proposal-policy") -> Any:
    """A proposal whose candidate is the replay of ``operations`` over ``before_text``."""
    from gnd.discover import output
    from gnd.evolve import CommittedText, EvolutionOperationAudit, EvolutionProposal

    candidate = output.candidate_document(_doc(before_text), operations)
    return EvolutionProposal(
        proposal_id=proposal_id,
        expected_model_sha256=hashlib.sha256(before_text.encode("utf-8")).hexdigest(),
        candidate_model=CommittedText.from_text(output.candidate_text(candidate), media_type="application/yaml"),
        operations=operations,
        rationale="MG2 policy case.",
        audit=EvolutionOperationAudit(actor_id="owner:fixture", origin="test_evolve_additive_policy",
                                      requested_at=datetime(2026, 11, 4, 12, 0, tzinfo=UTC)),
        artifacts=artifacts,
    )


def _service(tmp_path: Path, before_text: str | None = None) -> Any:
    sys.path.insert(0, str(REPO_ROOT / "tests"))
    import test_model_evolution as evolution

    text = before_text if before_text is not None else BASE.read_text(encoding="utf-8")
    service, _model, _verbalization = evolution._service(tmp_path / "ws", text)
    return service


def _preview(tmp_path: Path, operations: tuple[Any, ...], *, before_text: str | None = None,
             populated: tuple[str, ...] = (), artifacts: tuple[Any, ...] = ()) -> Any:
    text = before_text if before_text is not None else BASE.read_text(encoding="utf-8")
    return _service(tmp_path, text).preview(_proposal(text, operations, artifacts=artifacts),
                                            policy="additive", populated=populated)


NEW_CONSTRAINT = {"type": "mandatory", "role": "order", "source": "user-supplied", "status": "confirmed",
                  "modality": "deontic", "provenance": {"user_quote": "Every row names an order."}}
DOCUMENT = {"sha256": "a" * 64, "label": "notes.txt"}
NEW_OBJECT = {"id": "region", "name": "Region", "kind": "value", "primitive": "String"}
NEW_FACT = {"id": "order_ships_to_region", "reading": "{Order} ships to {Region}",
            "roles": [{"object_type": "order", "role_name": "order"}, {"object_type": "region", "role_name": "region"}]}


# --- T1: one case per matrix cell ------------------------------------------


def _modified(element: dict[str, Any], **changes: Any) -> dict[str, Any]:
    result = copy.deepcopy(element)
    for key, value in changes.items():
        if value is None:
            result.pop(key, None)
        else:
            result[key] = value
    return result


def _cell_cases() -> list[tuple[str, Any, str | None, str | None]]:
    """(name, operations builder over the fixture document, expected cell, reach).

    ``reach`` is ``None`` when the service reaches the policy with a valid
    candidate, or the validation message that pre-empts the cell at the
    service level (spec F6); such a cell is still judged by the policy function
    directly, so every branch keeps a case that can fail it.
    """
    d = _doc()
    customer = _object(d, "customer")
    channel = _object(d, "channel")
    note = _object(d, "note")
    populated_fact = _fact(d, POPULATED)
    control_fact = _fact(d, CONTROL)
    memo_fact = _fact(d, "order_has_memo")
    exclusion = _hosted(d, "exclusion")
    uniq_populated = _constraint(d, POPULATED, "uniqueness")
    uniq_control = _constraint(d, CONTROL, "uniqueness")
    renamed_note = _modified(note, id="remark", name="Remark")
    renamed_memo_fact = _modified(memo_fact, id="order_carries_memo")
    memo_role = memo_fact["roles"][1]
    control_role = control_fact["roles"][1]
    identity_before = {"version": 1, "model_id": "evolve-policy-base"}
    identity_after = {"version": 2, "model_id": "evolve-policy-base"}
    from gnd.evolve import ModelIdentityLocator, SourceDocumentLocator

    new_fact_with_role = dict(NEW_FACT, reading="{Order} ships to {Region} via {Channel}",
                              roles=NEW_FACT["roles"] + [{"object_type": "channel", "role_name": "channel"}])
    reading_mismatch = r"placeholder\(s\) but"
    no_documents = "the model declares no source.documents"
    return [
        ("object_types.add", lambda: (_op("add", _element("object_types", "region"), after=NEW_OBJECT),), None, None),
        ("object_types.modify (confined)", lambda: (_op("modify", _element("object_types", "customer"),
            before=customer, after=_modified(customer, description={"summary": "A party that places orders; renamed in review."})),), None, None),
        ("object_types.modify", lambda: (_op("modify", _element("object_types", "channel"),
            before=channel, after=_modified(channel, primitive="Integer")),), "object_types.modify", None),
        ("object_types.rename", lambda: (_op("rename", _element("object_types", "note"),
            before=note, after=renamed_note),), "object_types.rename", None),
        ("object_types.delete", lambda: (_op("delete", _element("object_types", "note"), before=note),), "object_types.delete", None),
        ("fact_types.add", lambda: (_op("add", _element("object_types", "region"), after=NEW_OBJECT),
            _op("add", _element("fact_types", NEW_FACT["id"]), after=NEW_FACT, operation_id="op2")), None, None),
        ("fact_types.modify (confined)", lambda: (_op("modify", _element("fact_types", POPULATED),
            before=populated_fact, after=_modified(populated_fact, provenance={"rationale": "Reworded."})),), None, None),
        ("fact_types.modify", lambda: (_op("modify", _element("fact_types", POPULATED),
            before=populated_fact, after=_modified(populated_fact, reading="{Customer} placed {Order} via {Channel}")),), "fact_types.modify", None),
        # The hosted exclusion names order_has_memo; its DELETE (admitted: both
        # subjects unpopulated) keeps the candidate valid.
        ("fact_types.rename", lambda: (_op("rename", _element("fact_types", "order_has_memo"),
            before=memo_fact, after=renamed_memo_fact),
            _op("delete", _constraint_locator(None, exclusion, "exclusion"), before=exclusion, operation_id="op2")), "fact_types.rename", None),
        ("fact_types.delete", lambda: (_op("delete", _element("fact_types", "order_has_memo"), before=memo_fact),
            _op("delete", _constraint_locator(None, exclusion, "exclusion"), before=exclusion, operation_id="op2")), "fact_types.delete", None),
        ("role.add (existing)", lambda: (_op("add", _element("object_types", "region"), after=NEW_OBJECT),
            _op("add", _role(CONTROL, "region"), after={"object_type": "region", "role_name": "region"}, operation_id="op2")),
            "role.add", reading_mismatch),
        ("role.add (same-proposal)", lambda: (_op("add", _element("object_types", "region"), after=NEW_OBJECT),
            _op("add", _element("fact_types", NEW_FACT["id"]), after=NEW_FACT, operation_id="op2"),
            _op("add", _role(NEW_FACT["id"], "channel"), after={"object_type": "channel", "role_name": "channel"}, operation_id="op3")),
            None, reading_mismatch),
        ("role.modify", lambda: (_op("modify", _role("order_has_memo", "memo"), before=memo_role, after=dict(memo_role, redact=True)),), "role.modify", None),
        ("role.rename", lambda: (_op("rename", _role("order_has_memo", "memo"), before=memo_role, after=dict(memo_role, role_name="text")),), "role.rename", None),
        ("role.delete", lambda: (_op("delete", _role("order_has_memo", "memo"), before=memo_role),), "role.delete", reading_mismatch),
        ("constraint.add (control)", lambda: (_op("add", _constraint_locator(CONTROL, None, "mandatory"), after=NEW_CONSTRAINT),), None, None),
        ("constraint.modify (control)", lambda: (_op("modify", _constraint_locator(CONTROL, uniq_control, "uniqueness"),
            before=uniq_control, after=dict(uniq_control, roles=["order", "amount"])),), None, None),
        ("constraint.delete (control)", lambda: (_op("delete", _constraint_locator(CONTROL, uniq_control, "uniqueness"), before=uniq_control),), None, None),
        ("constraint.add (same-proposal fact type)", lambda: (_op("add", _element("object_types", "region"), after=NEW_OBJECT),
            _op("add", _element("fact_types", NEW_FACT["id"]), after=NEW_FACT, operation_id="op2"),
            _op("add", _constraint_locator(NEW_FACT["id"], None, "mandatory"), after=NEW_CONSTRAINT, operation_id="op3")), None, None),
        ("constraint.populated.add", lambda: (_op("add", _constraint_locator(POPULATED, None, "mandatory"), after=NEW_CONSTRAINT),), "constraint.populated.add", None),
        ("constraint.populated.modify", lambda: (_op("modify", _constraint_locator(POPULATED, uniq_populated, "uniqueness"),
            before=uniq_populated, after=dict(uniq_populated, roles=["order"])),), "constraint.populated.modify", None),
        ("constraint.populated.delete", lambda: (_op("delete", _constraint_locator(POPULATED, uniq_populated, "uniqueness"), before=uniq_populated),), None, None),
        ("model_identity.modify", lambda: (_op("modify", ModelIdentityLocator(), before=identity_before, after=identity_after),), "model_identity.modify", None),
        ("role.add on a fact type added with that role", lambda: (_op("add", _element("object_types", "region"), after=NEW_OBJECT),
            _op("add", _element("fact_types", NEW_FACT["id"]), after=new_fact_with_role, operation_id="op2")), None, None),
        ("role.modify on a role the control's constraints name", lambda: (_op("modify", _role(CONTROL, "amount"),
            before=control_role, after=dict(control_role, redact=True)),), "role.modify", None),
        # UG3: the fixture declares no source header, so the service's replay
        # pre-empts every source-document case; the function judges the cell.
        ("source_document.add", lambda: (_op("add", SourceDocumentLocator(sha256=DOCUMENT["sha256"]), after=DOCUMENT),),
            None, no_documents),
        ("source_document.modify", lambda: (_op("modify", SourceDocumentLocator(sha256=DOCUMENT["sha256"]),
            before=DOCUMENT, after=dict(DOCUMENT, label="renamed.txt")),), "source_document.modify", no_documents),
        ("source_document.delete", lambda: (_op("delete", SourceDocumentLocator(sha256=DOCUMENT["sha256"]),
            before=DOCUMENT),), "source_document.delete", no_documents),
    ]


CELL_CASES = _cell_cases()


def _direct_issues(operations: tuple[Any, ...], *, populated: frozenset[str] = frozenset({POPULATED})) -> tuple[Any, ...]:
    """The policy function over the fixture model, without the service."""
    from gnd.evolve import CommittedText, EvolutionOperationAudit, EvolutionProposal
    from gnd.evolve.policy import additive_policy_issues
    from gnd.model import load_model

    text = BASE.read_text(encoding="utf-8")
    bare = EvolutionProposal(
        proposal_id="direct", expected_model_sha256=hashlib.sha256(text.encode()).hexdigest(),
        candidate_model=CommittedText.from_text(text, media_type="application/yaml"), operations=operations,
        rationale="direct", audit=EvolutionOperationAudit(actor_id="a", origin="o", requested_at=datetime(2026, 11, 4, tzinfo=UTC)))
    return additive_policy_issues(load_model(str(BASE)), bare, populated=populated)


def _refused_index(operations: tuple[Any, ...], cell: str) -> int:
    kinds = {"object_types": "element", "fact_types": "element", "role": "role", "constraint": "constraint",
             "model_identity": "model-identity", "source_document": "source-document"}
    wanted = kinds[cell.split(".", 1)[0]]
    return next(index for index, operation in enumerate(operations) if operation.locator.locator_kind == wanted
                and operation.kind.value == cell.rsplit(".", 1)[-1])


@pytest.mark.parametrize(("name", "build", "cell", "reach"), CELL_CASES, ids=[row[0] for row in CELL_CASES])
def test_t1_one_case_per_matrix_cell(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, name: str, build: Any,
                                     cell: str | None, reach: str | None) -> None:
    import gnd.evolve.service as service_module
    from gnd.evolve import EvolutionError, PolicyIssue

    operations = build()
    expected_index = _refused_index(operations, cell) if cell is not None else None

    def check(issues: tuple[Any, ...]) -> None:
        if cell is None:
            assert issues == ()
        else:
            assert [issue.cell for issue in issues] == [cell], issues
            (issue,) = issues
            assert issue.operation_index == expected_index
            assert issue.operation_id == operations[expected_index].operation_id
            assert issue.reference == operations[expected_index].reference()
            assert issue.detail.startswith(issue.reference + ": ")

    check(_direct_issues(operations))
    if reach is not None:
        # Pre-empted at the service by candidate validation (3): the cell is
        # reachable only through the function, judged above.
        with pytest.raises(EvolutionError, match=reach):
            _preview(tmp_path, operations)
        return
    preview = _preview(tmp_path, operations)
    assert preview.policy == "additive"
    check(preview.policy_issues)
    # T1a: the case can fail. Under the opposite verdict (a mutant policy that
    # admits everything, or refuses everything) the same assertion fails.
    opposite = (lambda *a, **k: ()) if cell is not None else (
        lambda before, proposal, *, populated: (PolicyIssue(operation_index=0, operation_id="op",
            reference="x", cell="object_types.modify", detail="x: mutant"),))
    monkeypatch.setattr(service_module, "additive_policy_issues", opposite)
    mutant = _preview(tmp_path / "mutant", operations)
    assert (mutant.policy_issues == ()) != (cell is None)


def test_t1b_element_modify_allow_lists(tmp_path: Path) -> None:
    d = _doc()
    customer = _object(d, "customer")
    populated_fact = _fact(d, POPULATED)

    def verdict(operation: Any) -> list[str]:
        return [issue.cell for issue in _preview(tmp_path / operation.operation_id, (operation,)).policy_issues]

    assert verdict(_op("modify", _element("object_types", "customer"), before=customer,
                       after=_modified(customer, description={"summary": "Edited."}), operation_id="d")) == []
    assert verdict(_op("modify", _element("object_types", "customer"), before=customer,
                       after=_modified(customer, provenance={"rationale": "Edited."}), operation_id="r")) == []
    assert verdict(_op("modify", _element("object_types", "customer"), before=customer,
                       after=_modified(customer, description={"summary": "Edited."}, primitive="String"),
                       operation_id="dp")) == ["object_types.modify"]
    # O5: a replaced reference scheme is a refused object-type MODIFY.
    assert verdict(_op("modify", _element("object_types", "customer"), before=customer,
                       after=_modified(customer, reference={"mode": "popular", "value_type": "order_id"}),
                       operation_id="ref")) == ["object_types.modify"]
    assert verdict(_op("modify", _element("fact_types", POPULATED), before=populated_fact,
                       after=_modified(populated_fact, provenance={"rationale": "Edited."}), operation_id="fr")) == []
    assert verdict(_op("modify", _element("fact_types", POPULATED), before=populated_fact,
                       after=_modified(populated_fact, objectified_as="note"), operation_id="obj")) == ["fact_types.modify"]
    inside = copy.deepcopy(populated_fact)
    inside["constraints"].append(NEW_CONSTRAINT)
    assert verdict(_op("modify", _element("fact_types", POPULATED), before=populated_fact, after=inside,
                       operation_id="mand")) == ["fact_types.modify"]
    rows = copy.deepcopy(populated_fact)
    rows["sample_population"].append({"customer": 3, "order": 12, "channel": "phone"})
    assert verdict(_op("modify", _element("fact_types", POPULATED), before=populated_fact, after=rows,
                       operation_id="rows")) == ["fact_types.modify"]


def test_t1c_two_fault_operations_gate_exits_18_before_the_policy(tmp_path: Path) -> None:
    sys.path.insert(0, str(REPO_ROOT / "tests"))
    import test_model_v2 as v2

    from gnd.evolve import EvolutionOperationsGatedError

    before_text = v2.OPERATIONS_MODEL.read_text(encoding="utf-8")
    document = v2._operations_doc()
    referenced = next(ft for ft in document["fact_types"] if ft["id"] == "work_item_has_state")
    renamed = dict(referenced, id="work_item_in_state")
    proposal, _ = v2._proposal(before_text, document, (
        _op("rename", _element("fact_types", "work_item_has_state"), before=referenced, after=renamed),))
    service = v2._service(tmp_path / "ws", before_text)
    with pytest.raises(EvolutionOperationsGatedError):
        service.preview(proposal, policy="additive")
    # The CLI exit is 18 and no preview is written.
    work = tmp_path / "cli"
    work.mkdir()
    (work / "records").mkdir()
    (work / "model.orm.yaml").write_text(before_text, encoding="utf-8")
    (work / "proposal.json").write_text(json.dumps(proposal.model_dump(mode="json"), indent=2, sort_keys=True) + "\n")
    result = run_main(["evolve", "preview", str(work / "model.orm.yaml"), str(work / "proposal.json"), "--workspace", str(work),
                       "--records", str(work / "records"), "--out", str(work / "preview.json"), "--format", "json",
                       "--policy", "additive"])
    assert result.returncode == 18, result.stderr
    assert not (work / "preview.json").exists()


def test_t1d_d12_refusal_precedes_the_policy(tmp_path: Path) -> None:
    from gnd.evolve import EvolutionError

    bad = dict(NEW_CONSTRAINT, source="explicit", status="confirmed", modality="alethic")
    text = BASE.read_text(encoding="utf-8")
    with pytest.raises(EvolutionError, match="D-12"):
        _service(tmp_path, text).preview(_proposal(text, (
            _op("add", _constraint_locator(POPULATED, None, "mandatory"), after=bad),)), policy="additive")


def test_t1e_pre_empted_cells(tmp_path: Path) -> None:
    d = _doc()
    uniq = _constraint(d, POPULATED, "uniqueness")
    with pytest.raises(ValidationError, match="cannot be renamed"):
        _op("rename", _constraint_locator(POPULATED, uniq, "uniqueness"), before=uniq, after=dict(uniq, roles=["order"]))
    sys.path.insert(0, str(REPO_ROOT / "tests"))
    import test_model_v2 as v2

    from gnd.evolve import EvolutionOperationsGatedError

    before_text = v2.OPERATIONS_MODEL.read_text(encoding="utf-8")
    document = v2._operations_doc()
    operation = document["operations"][0]
    changed = dict(operation, reading=operation["reading"] + " (edited)")
    document["operations"][0] = changed
    proposal, _ = v2._proposal(before_text, document, (
        _op("modify", _element("operations", operation["id"]), before=operation, after=changed),))
    with pytest.raises(EvolutionOperationsGatedError):
        v2._service(tmp_path / "ws", before_text).preview(proposal, policy="additive")


# --- T2: strengthening, weakening, neither, populated sources ---------------


def _modify_constraint(host: str | None, family: str, after: dict[str, Any], which: int = 0) -> Any:
    """MODIFY the ``which``-th constraint of ``family`` on ``host``; the locator's
    duplicate occurrence is 0, since the fixture holds no byte-identical pair."""
    d = _doc()
    before = _constraint(d, host, family, which) if host is not None else _hosted(d, family)
    return _op("modify", _constraint_locator(host, before, family, 0), before=before, after=after)


def _with(constraint: dict[str, Any], **changes: Any) -> dict[str, Any]:
    return _modified(constraint, **changes)


def _strengthening_cases() -> list[tuple[str, Any]]:
    d = _doc()
    uniq = _constraint(d, POPULATED, "uniqueness")
    allowed = _constraint(d, POPULATED, "value", 0)
    freq = _constraint(d, POPULATED, "frequency")
    rng = _constraint(d, POPULATED, "value", 1)
    guarded = _hosted(d, "guarded")
    confirmed = copy.deepcopy(guarded)
    confirmed["status"] = "confirmed"
    confirmed["provenance"]["reviewed_in"] = "review-2026-11-04"
    return [
        ("roles narrowed", _modify_constraint(POPULATED, "uniqueness", _with(uniq, roles=["order"]))),
        ("allowed narrowed", _modify_constraint(POPULATED, "value", _with(allowed, allowed=["web", "phone"]))),
        ("range.min raised", _modify_constraint(POPULATED, "value", _with(rng, range=dict(rng["range"], min=2)), 1)),
        ("range.max lowered", _modify_constraint(POPULATED, "value", _with(rng, range=dict(rng["range"], max=999)), 1)),
        ("min_inclusive true->false", _modify_constraint(POPULATED, "value", _with(rng, range=dict(rng["range"], min_inclusive=False)), 1)),
        ("bound.min raised", _modify_constraint(POPULATED, "frequency", _with(freq, bound={"min": 2, "max": 10}))),
        ("bound.max lowered", _modify_constraint(POPULATED, "frequency", _with(freq, bound={"min": 1, "max": 9}))),
        ("deontic->alethic", _modify_constraint(POPULATED, "frequency", _with(freq, modality="alethic"))),
        ("proposed->confirmed", _modify_constraint(None, "guarded", confirmed)),
    ]


def _bound_max_added_case() -> Any:
    """A frequency constraint with `min` only, then `max` added: on a variant of the fixture."""
    text = BASE.read_text(encoding="utf-8").replace("bound: { min: 1, max: 10 }", "bound: { min: 1 }")
    d = _doc(text)
    freq = _constraint(d, POPULATED, "frequency")
    return text, _op("modify", _constraint_locator(POPULATED, freq, "frequency"), before=freq,
                     after=_with(freq, bound={"min": 1, "max": 10}))


STRENGTHENING = _strengthening_cases()


@pytest.mark.parametrize(("name", "operation"), STRENGTHENING, ids=[row[0] for row in STRENGTHENING])
def test_t2_each_strengthening_item_is_refused(tmp_path: Path, name: str, operation: Any) -> None:
    preview = _preview(tmp_path, (operation,))
    assert [issue.cell for issue in preview.policy_issues] == ["constraint.populated.modify"], preview.policy_issues
    (issue,) = preview.policy_issues
    assert "strengthening" in issue.detail or "neither" in issue.detail
    assert "strengthening" in issue.detail, issue.detail


def test_t2_bound_max_added_is_refused(tmp_path: Path) -> None:
    text, operation = _bound_max_added_case()
    preview = _preview(tmp_path, (operation,), before_text=text)
    assert [issue.cell for issue in preview.policy_issues] == ["constraint.populated.modify"]
    assert "bound.max strengthening" in preview.policy_issues[0].detail


def _weakening_cases() -> list[tuple[str, Any]]:
    d = _doc()
    uniq = _constraint(d, POPULATED, "uniqueness")
    allowed = _constraint(d, POPULATED, "value", 0)
    freq = _constraint(d, POPULATED, "frequency")
    rng = _constraint(d, POPULATED, "value", 1)
    return [
        ("roles widened", _modify_constraint(POPULATED, "uniqueness", _with(uniq, roles=["order", "channel", "customer"]))),
        ("allowed widened", _modify_constraint(POPULATED, "value", _with(allowed, allowed=["web", "phone", "store", "fax"]))),
        ("range.min lowered", _modify_constraint(POPULATED, "value", _with(rng, range=dict(rng["range"], min=0)), 1)),
        ("range.max raised", _modify_constraint(POPULATED, "value", _with(rng, range=dict(rng["range"], max=2000)), 1)),
        ("bound.min lowered", _modify_constraint(POPULATED, "frequency", _with(freq, bound={"min": 0, "max": 10}))),
        ("bound.max raised", _modify_constraint(POPULATED, "frequency", _with(freq, bound={"min": 1, "max": 11}))),
        ("bound.max removed", _modify_constraint(POPULATED, "frequency", _with(freq, bound={"min": 1}))),
        ("alethic->deontic", _modify_constraint(POPULATED, "uniqueness", _with(uniq, modality="deontic"))),
        ("rationale only", _modify_constraint(POPULATED, "value", _with(rng, rationale="Reworded."), 1)),
    ]


WEAKENING = _weakening_cases()


@pytest.mark.parametrize(("name", "operation"), WEAKENING, ids=[row[0] for row in WEAKENING])
def test_t2a_each_weakening_and_rationale_edit_is_admitted(tmp_path: Path, name: str, operation: Any) -> None:
    assert _preview(tmp_path, (operation,)).policy_issues == ()


def test_t2a_max_inclusive_false_to_true_is_admitted(tmp_path: Path) -> None:
    text = BASE.read_text(encoding="utf-8").replace("max_inclusive: true", "max_inclusive: false")
    d = _doc(text)
    rng = _constraint(d, POPULATED, "value", 1)
    operation = _op("modify", _constraint_locator(POPULATED, rng, "value"), before=rng,
                    after=_with(rng, range=dict(rng["range"], max_inclusive=True)))
    assert _preview(tmp_path, (operation,), before_text=text).policy_issues == ()


def test_t2a_confirmed_to_proposed_is_pre_empted_by_d12(tmp_path: Path) -> None:
    """Spec F2: D-12 admits only llm-inferred/proposed/deontic and user-supplied/
    confirmed changed constraints, so the status weakening never reaches the policy."""
    from gnd.evolve import EvolutionError

    d = _doc()
    uniq = _constraint(d, POPULATED, "uniqueness")
    text = BASE.read_text(encoding="utf-8")
    with pytest.raises(EvolutionError, match="D-12|must have status 'confirmed'"):
        _service(tmp_path, text).preview(_proposal(text, (_modify_constraint(POPULATED, "uniqueness", _with(uniq, status="proposed")),)),
                                         policy="additive")


def _neither_cases() -> list[tuple[str, Any]]:
    d = _doc()
    uniq = _constraint(d, POPULATED, "uniqueness")
    allowed = _constraint(d, POPULATED, "value", 0)
    freq = _constraint(d, POPULATED, "frequency")
    return [
        ("roles replaced", _modify_constraint(POPULATED, "uniqueness", _with(uniq, roles=["customer", "channel"]))),
        ("allowed -> range", _modify_constraint(POPULATED, "value", _with(allowed, allowed=None, range={"min": 0, "max": 1}))),
        ("status -> rejected", _modify_constraint(POPULATED, "uniqueness", _with(uniq, status="rejected"))),
        ("one strengthens, one weakens", _modify_constraint(POPULATED, "frequency", _with(freq, bound={"min": 0, "max": 9}))),
    ]


NEITHER = _neither_cases()


@pytest.mark.parametrize(("name", "operation"), NEITHER, ids=[row[0] for row in NEITHER])
def test_t2b_neither_is_refused_at_the_policy_or_before(tmp_path: Path, name: str, operation: Any) -> None:
    """Refused: by the policy when the candidate is otherwise valid, or by
    validation or D-12 first (both 3). The policy function itself refuses
    every row (asserted directly)."""
    from gnd.documents import Model
    from gnd.evolve import EvolutionError
    from gnd.evolve.policy import additive_policy_issues
    from gnd.model import load_model

    model = load_model(str(BASE))
    assert isinstance(model, Model)
    text = BASE.read_text(encoding="utf-8")
    try:
        preview = _service(tmp_path, text).preview(_proposal(text, (operation,)), policy="additive")
    except EvolutionError:
        pass
    else:
        assert [issue.cell for issue in preview.policy_issues] == ["constraint.populated.modify"]
    from gnd.evolve import CommittedText, EvolutionOperationAudit, EvolutionProposal

    bare = EvolutionProposal(
        proposal_id="direct", expected_model_sha256=hashlib.sha256(text.encode()).hexdigest(),
        candidate_model=CommittedText.from_text(text, media_type="application/yaml"), operations=(operation,),
        rationale="direct", audit=EvolutionOperationAudit(actor_id="a", origin="o", requested_at=datetime(2026, 11, 4, tzinfo=UTC)))
    issues = additive_policy_issues(model, bare, populated=frozenset({POPULATED}))
    assert [issue.cell for issue in issues] == ["constraint.populated.modify"]
    assert "neither" in issues[0].detail or "strengthening" in issues[0].detail


def test_t2c_each_populated_source_and_the_unpopulated_control(tmp_path: Path) -> None:
    from gnd.evolve import ArtifactLocator

    add = (_op("add", _constraint_locator(CONTROL, None, "mandatory"), after=NEW_CONSTRAINT),)
    control = _preview(tmp_path / "control", add)
    assert control.policy_issues == ()
    assert control.populated == (POPULATED,) and control.populated_args == ()

    by_argument = _preview(tmp_path / "arg", add, populated=(CONTROL,))
    assert [issue.cell for issue in by_argument.policy_issues] == ["constraint.populated.add"]
    assert by_argument.populated == (POPULATED, CONTROL) and by_argument.populated_args == (CONTROL,)

    artifact = ArtifactLocator(artifact_id="facts", artifact_kind="population", path="facts.population.json",
                               sha256="0" * 64, references=(f"fact_types[{CONTROL}]",))
    by_artifact = _preview(tmp_path / "artifact", add, artifacts=(artifact,))
    assert [issue.cell for issue in by_artifact.policy_issues] == ["constraint.populated.add"]
    assert by_artifact.populated == (POPULATED, CONTROL) and by_artifact.populated_args == ()

    # Sample rows: the fixture's own populated fact type.
    by_rows = _preview(tmp_path / "rows", (_op("add", _constraint_locator(POPULATED, None, "mandatory"), after=NEW_CONSTRAINT),))
    assert [issue.cell for issue in by_rows.policy_issues] == ["constraint.populated.add"]


def test_t2c_reference_owned_fact_type_is_populated(tmp_path: Path) -> None:
    sys.path.insert(0, str(REPO_ROOT / "tests"))
    import test_evolve_references as references

    from gnd.discover import output
    from gnd.evolve.service import _parse_model_text

    work = references._workspace(tmp_path)
    # The reference population `catalog` owns dispatch_catalog_allows; a new
    # constraint there is refused, while references._proposal's target
    # (dispatch_subject_warehouse, owned by no reference) is admitted.
    model_bytes = (work / "model.orm.yaml").read_bytes()
    document = _parse_model_text(model_bytes.decode("utf-8"))
    constraint = {"type": "mandatory", "role": "warehouse", "source": "user-supplied", "status": "confirmed",
                  "modality": "deontic", "rationale": "MG2 probe", "provenance": {"user_quote": "Every catalog row names a warehouse."}}
    ops = output.add_operations([("dispatch_catalog_allows", constraint)], prefix="mg2")
    built = output.proposal(model_bytes=model_bytes, document=output.candidate_document(document, ops), ops=ops,
                            actor="mg2", requested_at=datetime(2026, 11, 4, tzinfo=UTC), origin="mg2 test", prefix="mg2",
                            rationale="one mandatory constraint on a reference-owned fact type")
    proposal = work / "proposal.json"
    proposal.write_bytes(output.canonical_bytes(built.model_dump(mode="json")))
    result = run_main(["evolve", "preview", str(work / "model.orm.yaml"), str(proposal), "--workspace", str(work),
                       "--records", str(work / "records"), "--out", str(work / "preview.json"), "--format", "json",
                       "--policy", "additive"])
    assert result.returncode == 3, result.stderr
    document = json.loads((work / "preview.json").read_text(encoding="utf-8"))
    assert document["populated"] == ["dispatch_catalog_allows"]
    assert [issue["cell"] for issue in document["policy_issues"]] == ["constraint.populated.add"]
    control = references._proposal(work, name="control.json")
    result = run_main(["evolve", "preview", str(work / "model.orm.yaml"), str(control), "--workspace", str(work),
                       "--records", str(work / "records"), "--out", str(work / "control-preview.json"), "--format", "json",
                       "--policy", "additive"])
    assert result.returncode == 0, result.stderr


def test_t2d_model_hosted_constraint_counts_as_populated_when_any_subject_is(tmp_path: Path) -> None:
    equality = {"type": "equality", "role_seq_a": [{"fact_type": CONTROL, "role": "order"}],
                "role_seq_b": [{"fact_type": POPULATED, "role": "order"}],
                "source": "user-supplied", "status": "confirmed", "modality": "deontic",
                "provenance": {"user_note": "Every placed order has an amount and vice versa."}}
    add = (_op("add", _constraint_locator(None, None, "equality"), after=equality),)
    spanning = _preview(tmp_path / "any", add)
    assert [issue.cell for issue in spanning.policy_issues] == ["constraint.populated.add"]
    # The "every" discriminator: with the populated side's rows removed, the
    # same ADD is admitted.
    text = re.sub(r"    sample_population:\n(      - \{[^\n]*\}\n)+", "", BASE.read_text(encoding="utf-8"))
    assert "sample_population" not in text
    assert _preview(tmp_path / "every", add, before_text=text).policy_issues == ()


def test_t2e_unknown_populated_argument_exits_3(tmp_path: Path) -> None:
    from gnd.evolve import EvolutionError

    text = BASE.read_text(encoding="utf-8")
    with pytest.raises(EvolutionError, match="no_such"):
        _service(tmp_path, text).preview(_proposal(text, (_op("add", _element("object_types", "region"), after=NEW_OBJECT),)),
                                         policy="additive", populated=("no_such",))
    paths = _cli_workspace(tmp_path / "cli", (_op("add", _element("object_types", "region"), after=NEW_OBJECT),))
    result = run_main(_preview_argv(paths, "--policy", "additive", "--populated", "no_such"))
    assert result.returncode == 3 and b"no_such" in result.stderr


# --- T3: the CLI and the service re-run --------------------------------------


def _cli_workspace(root: Path, operations: tuple[Any, ...], *, before_text: str | None = None) -> dict[str, Path]:
    text = before_text if before_text is not None else BASE.read_text(encoding="utf-8")
    root.mkdir(parents=True, exist_ok=True)
    (root / "records").mkdir(exist_ok=True)
    model = root / "model.orm.yaml"
    model.write_text(text, encoding="utf-8")
    (root / "model.verbalization.txt").write_text("pre-existing\n", encoding="utf-8")
    proposal = root / "proposal.json"
    proposal.write_text(json.dumps(_proposal(text, operations).model_dump(mode="json"), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"workspace": root, "model": model, "proposal": proposal, "preview": root / "preview.json", "records": root / "records"}


def _preview_argv(paths: dict[str, Path], *extra: str) -> list[str]:
    return ["evolve", "preview", str(paths["model"]), str(paths["proposal"]), "--workspace", str(paths["workspace"]),
            "--records", str(paths["records"]), "--out", str(paths["preview"]), "--format", "json", *extra]


def _apply_argv(paths: dict[str, Path], *extra: str) -> list[str]:
    return ["evolve", "apply", str(paths["model"]), str(paths["proposal"]), "--preview", str(paths["preview"]),
            "--workspace", str(paths["workspace"]), "--records", str(paths["records"]), "--format", "json", *extra]


ADMITTED_OPS = (_op("add", _element("object_types", "region"), after=NEW_OBJECT),)


def test_t3_cli_option_agreement_and_tampering(tmp_path: Path) -> None:
    # preview with --policy, apply without: 3, names --policy
    paths = _cli_workspace(tmp_path / "a", ADMITTED_OPS)
    assert run_main(_preview_argv(paths, "--policy", "additive")).returncode == 0
    result = run_main(_apply_argv(paths))
    assert result.returncode == 3 and b"--policy" in result.stderr
    # preview without, apply with: 3
    paths = _cli_workspace(tmp_path / "b", ADMITTED_OPS)
    assert run_main(_preview_argv(paths)).returncode == 0
    result = run_main(_apply_argv(paths, "--policy", "additive"))
    assert result.returncode == 3 and b"--policy" in result.stderr
    # different --populated: 3, names --populated
    paths = _cli_workspace(tmp_path / "c", ADMITTED_OPS)
    assert run_main(_preview_argv(paths, "--policy", "additive", "--populated", CONTROL)).returncode == 0
    result = run_main(_apply_argv(paths, "--policy", "additive"))
    assert result.returncode == 3 and b"--populated" in result.stderr
    # --populated without --policy on preview: 3
    paths = _cli_workspace(tmp_path / "d", ADMITTED_OPS)
    result = run_main(_preview_argv(paths, "--populated", CONTROL))
    assert result.returncode == 3 and b"--policy" in result.stderr
    assert not paths["preview"].exists()
    # policy_issues deleted and the digest recomputed, applied with matching options: 11
    refused = (_op("add", _constraint_locator(POPULATED, None, "mandatory"), after=NEW_CONSTRAINT),)
    paths = _cli_workspace(tmp_path / "e", refused)
    result = run_main(_preview_argv(paths, "--policy", "additive"))
    assert result.returncode == 3, result.stderr
    document = json.loads(paths["preview"].read_text(encoding="utf-8"))
    assert [issue["cell"] for issue in document["policy_issues"]] == ["constraint.populated.add"]
    from gnd.evolve import canonical_sha256

    document["policy_issues"] = []
    document["preview_sha256"] = canonical_sha256({k: v for k, v in document.items() if k != "preview_sha256"})
    paths["preview"].write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    result = run_main(_apply_argv(paths, "--policy", "additive"))
    assert result.returncode == 11, result.stderr
    # matching options and no issues: 0, and the published model is the candidate
    paths = _cli_workspace(tmp_path / "f", ADMITTED_OPS)
    assert run_main(_preview_argv(paths, "--policy", "additive")).returncode == 0
    result = run_main(_apply_argv(paths, "--policy", "additive"))
    assert result.returncode == 0, result.stderr
    assert "region" in paths["model"].read_text(encoding="utf-8")


def test_t3_preview_with_issues_writes_its_document_and_exits_3(tmp_path: Path) -> None:
    refused = (_op("add", _constraint_locator(POPULATED, None, "mandatory"), after=NEW_CONSTRAINT),)
    paths = _cli_workspace(tmp_path, refused)
    result = run_main(_preview_argv(paths, "--policy", "additive"))
    assert result.returncode == 3
    assert b"REFUSED (3)" in result.stderr and b"policy_issues" in result.stderr
    document = json.loads(paths["preview"].read_text(encoding="utf-8"))
    assert document["policy"] == "additive" and document["populated"] == [POPULATED]
    assert document["populated_args"] == []
    (issue,) = document["policy_issues"]
    assert issue["operation_index"] == 0 and issue["cell"] == "constraint.populated.add"
    assert json.loads(result.stdout)["policy_issues"] == document["policy_issues"]
    # Text mode names the policy and each issue only under a policy.
    paths = _cli_workspace(tmp_path / "text", refused)
    text_result = run_main([*_preview_argv(paths)[:-1], "text", "--policy", "additive"])
    assert text_result.returncode == 3
    assert b"  policy: additive\n" in text_result.stdout and b"  policy-issue: 0 constraint.populated.add" in text_result.stdout
    paths = _cli_workspace(tmp_path / "plain", ADMITTED_OPS)
    plain = run_main([*_preview_argv(paths)[:-1], "text"])
    assert plain.returncode == 0 and b"policy" not in plain.stdout


def test_t3a_option_check_precedes_the_retry_branch(tmp_path: Path) -> None:
    """A pending transaction with the candidate already live plus a mismatched
    --policy exits 3, not through the retry path."""
    paths = _cli_workspace(tmp_path, ADMITTED_OPS)
    assert run_main(_preview_argv(paths, "--policy", "additive")).returncode == 0
    assert run_main(_apply_argv(paths, "--policy", "additive")).returncode == 0
    # The candidate is live and the records hold a staged preview; a second apply
    # without --policy must be refused for the option before any retry logic.
    result = run_main(_apply_argv(paths))
    assert result.returncode == 3 and b"--policy" in result.stderr


def _stripped_preview(preview: Any) -> Any:
    """The same preview with its issue list removed and its digest recomputed."""
    from gnd.evolve import EvolutionPreview, canonical_sha256

    document = preview.model_dump(mode="json")
    document["policy_issues"] = []
    document["preview_sha256"] = canonical_sha256({k: v for k, v in document.items() if k != "preview_sha256"})
    return EvolutionPreview.model_validate(document)


def test_t3b_service_apply_re_runs_the_policy_on_its_own_bytes(tmp_path: Path) -> None:
    from gnd.evolve import EvolutionPolicyRefusedError

    refused = (_op("add", _constraint_locator(POPULATED, None, "mandatory"), after=NEW_CONSTRAINT),)
    text = BASE.read_text(encoding="utf-8")
    service = _service(tmp_path, text)
    preview = service.preview(_proposal(text, refused), policy="additive")
    assert preview.policy_issues
    stripped = _stripped_preview(preview)
    assert stripped.policy_issues == ()
    with pytest.raises(EvolutionPolicyRefusedError) as excinfo:
        service.apply(stripped)
    assert "operation 0" in str(excinfo.value) and "constraint.populated.add" in str(excinfo.value)
    assert excinfo.value.issues[0].cell == "constraint.populated.add"
    # The CLI maps the typed refusal to 3.
    from gnd.evolve.cli_service import _evolve_error_exit

    assert _evolve_error_exit(excinfo.value) == 3


def test_t3c_mutation_control_disabling_the_re_run_applies(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import gnd.evolve.service as service_module

    refused = (_op("add", _constraint_locator(POPULATED, None, "mandatory"), after=NEW_CONSTRAINT),)
    text = BASE.read_text(encoding="utf-8")
    service = _service(tmp_path, text)
    stripped = _stripped_preview(service.preview(_proposal(text, refused), policy="additive"))
    monkeypatch.setattr(service_module, "additive_policy_issues", lambda *a, **k: ())
    pending = service.apply(stripped)
    assert pending.proposal_id == "proposal-policy"


def test_t3_populated_set_change_before_apply_is_stale(tmp_path: Path) -> None:
    """The service compares its recomputed populated set with the preview's (11 band)."""
    from gnd.evolve import EvolutionError, EvolutionPreview, canonical_sha256
    from gnd.evolve.cli_service import _evolve_error_exit

    text = BASE.read_text(encoding="utf-8")
    service = _service(tmp_path, text)
    preview = service.preview(_proposal(text, ADMITTED_OPS), policy="additive")
    document = preview.model_dump(mode="json")
    document["populated"] = [POPULATED, "order_has_memo"]
    document["preview_sha256"] = canonical_sha256({k: v for k, v in document.items() if k != "preview_sha256"})
    with pytest.raises(EvolutionError, match="populated set changed before apply") as excinfo:
        service.apply(EvolutionPreview.model_validate(document))
    assert _evolve_error_exit(excinfo.value) == 11


# --- Review regressions (one reviewer, 2026-11-04) ---------------------------


def test_review_f1_hosted_modify_retargeted_onto_a_populated_fact_type_is_refused(tmp_path: Path) -> None:
    """Subjects of a model-hosted MODIFY come from before AND after: a constraint
    spanning only unpopulated fact types cannot be re-pointed at a populated one."""
    d = _doc()
    exclusion = _hosted(d, "exclusion")
    retargeted = _with(exclusion, role_seq_a=[{"fact_type": POPULATED, "role": "order"}])
    operation = _op("modify", _constraint_locator(None, exclusion, "exclusion"), before=exclusion, after=retargeted)
    preview = _preview(tmp_path, (operation,))
    assert [issue.cell for issue in preview.policy_issues] == ["constraint.populated.modify"]
    # Control: the same MODIFY keeping both subjects unpopulated is admitted.
    swapped = _with(exclusion, role_seq_a=exclusion["role_seq_b"], role_seq_b=exclusion["role_seq_a"])
    control = _op("modify", _constraint_locator(None, exclusion, "exclusion"), before=exclusion, after=swapped)
    assert _preview(tmp_path / "control", (control,)).policy_issues == ()


def test_review_f1_hosted_modify_moved_off_a_populated_fact_type_is_refused(tmp_path: Path) -> None:
    """The before side counts too: a constraint spanning a populated fact type
    stays judged when the MODIFY re-points it elsewhere (post-fix mutant M14a)."""
    d = _doc()
    subset = _hosted(d, "subset")
    moved = _with(subset, superset_role_seq=[{"fact_type": "order_has_memo", "role": "order"}])
    operation = _op("modify", _constraint_locator(None, subset, "subset"), before=subset, after=moved)
    preview = _preview(tmp_path, (operation,))
    assert [issue.cell for issue in preview.policy_issues] == ["constraint.populated.modify"]


def test_review_f2_frequency_roles_widened_is_refused(tmp_path: Path) -> None:
    """A wider frequency projection makes finer groups that must each reach
    `bound.min`: not a weakening. Only uniqueness is monotone in its role set."""
    d = _doc()
    freq = _constraint(d, POPULATED, "frequency")
    operation = _modify_constraint(POPULATED, "frequency", _with(freq, roles=["customer", "channel"]))
    preview = _preview(tmp_path, (operation,))
    assert [issue.cell for issue in preview.policy_issues] == ["constraint.populated.modify"]
    assert "roles neither" in preview.policy_issues[0].detail
    narrowed = _modify_constraint(POPULATED, "frequency", _with(freq, roles=[]))
    from gnd.evolve.policy import constraint_change

    assert constraint_change("roles", ["customer"], ["customer", "channel"], family="frequency") == "neither"
    assert constraint_change("roles", ["customer"], ["customer", "channel"], family="uniqueness") == "weakening"
    del narrowed


def test_review_f3_an_empty_sample_population_is_not_populated(tmp_path: Path) -> None:
    text = re.sub(r"    sample_population:\n(      - \{[^\n]*\}\n)+", "    sample_population: []\n", BASE.read_text(encoding="utf-8"))
    assert "sample_population: []" in text
    add = (_op("add", _constraint_locator(POPULATED, None, "mandatory"), after=NEW_CONSTRAINT),)
    preview = _preview(tmp_path, add, before_text=text)
    assert preview.policy_issues == () and preview.populated == ()


def test_review_f4_ranges_elementwise_and_bool_bounds(tmp_path: Path) -> None:
    from gnd.evolve.policy import constraint_change

    text = BASE.read_text(encoding="utf-8").replace(
        "range: { min: 1, max: 1000, min_inclusive: true, max_inclusive: true }",
        "ranges: [{ min: 1, max: 500 }, { min: 600, max: 1000 }]")
    d = _doc(text)
    rng = _constraint(d, POPULATED, "value", 1)
    assert "ranges" in rng
    raised = copy.deepcopy(rng)
    raised["ranges"][0]["min"] = 2
    operation = _op("modify", _constraint_locator(POPULATED, rng, "value"), before=rng, after=raised)
    preview = _preview(tmp_path, (operation,), before_text=text)
    assert [issue.cell for issue in preview.policy_issues] == ["constraint.populated.modify"]
    assert "ranges[0].min strengthening" in preview.policy_issues[0].detail
    lowered = copy.deepcopy(rng)
    lowered["ranges"][1]["max"] = 2000
    admitted = _op("modify", _constraint_locator(POPULATED, rng, "value"), before=rng, after=lowered)
    assert _preview(tmp_path / "wider", (admitted,), before_text=text).policy_issues == ()
    assert constraint_change("bound.min", 1, True) == "neither"
    assert constraint_change("bound.max", False, 3) == "neither"


# --- T5/T6/T12/T13/T14 ------------------------------------------------------


def test_t5_preview_without_policy_has_no_policy_keys_and_the_old_digest_shape(tmp_path: Path) -> None:
    text = BASE.read_text(encoding="utf-8")
    service = _service(tmp_path, text)
    plain = service.preview(_proposal(text, ADMITTED_OPS))
    document = plain.model_dump(mode="json")
    assert not {"policy", "populated", "populated_args", "policy_issues"} & set(document)
    assert "accepted_blast_radius_sha256" in document and document["accepted_blast_radius_sha256"] is None
    assert {'before_includes', 'candidate_includes'}.isdisjoint(document)
    assert json.loads(plain.model_dump_json()) == document
    with_policy = service.preview(_proposal(text, ADMITTED_OPS), policy="additive")
    assert with_policy.preview_sha256 != plain.preview_sha256
    assert with_policy.model_dump(mode="json")["policy_issues"] == []
    # Round trip through the V3 reader keeps the fields and the digest.
    from gnd.evolve import read_evolution_preview_document

    assert read_evolution_preview_document(with_policy.model_dump(mode="json")) == with_policy
    assert read_evolution_preview_document(document) == plain


def test_t5_policy_fields_are_set_together(tmp_path: Path) -> None:
    from gnd.evolve import EvolutionPreview, canonical_sha256

    text = BASE.read_text(encoding="utf-8")
    document = _service(tmp_path, text).preview(_proposal(text, ADMITTED_OPS), policy="additive").model_dump(mode="json")
    del document["populated"]
    document["preview_sha256"] = canonical_sha256({k: v for k, v in document.items() if k != "preview_sha256"})
    with pytest.raises(ValidationError, match="set together"):
        EvolutionPreview.model_validate(document)


def test_t6_issue_detail_never_quotes_a_value(tmp_path: Path) -> None:
    text = BASE.read_text(encoding="utf-8").replace("allowed: [web, phone, store]", "allowed: [web, SECRET-A, SECRET-B]")
    d = _doc(text)
    allowed = _constraint(d, POPULATED, "value", 0)
    operation = _op("modify", _constraint_locator(POPULATED, allowed, "value"), before=allowed,
                    after=_with(allowed, allowed=["web", "SECRET-A"]))
    preview = _preview(tmp_path, (operation,), before_text=text)
    (issue,) = preview.policy_issues
    assert "SECRET" not in issue.detail
    document = preview.model_dump(mode="json")
    for key in ("proposal", "before_model", "candidate_model", "verbalization", "blast_radius"):
        document.pop(key)
    assert "SECRET" not in json.dumps(document)


def test_t12_hostile_before_after_pairs_are_neither_never_a_traceback() -> None:
    from gnd.evolve.policy import constraint_change, diff_paths

    hostile = [
        ({1: "a"}, {1: "b"}),
        ({"roles": "x"}, {"roles": ["a"]}),
        ({"bound": 3}, {"bound": {"min": 1}}),
        ({"type": "mystery"}, {"type": "mystery", "k": 1}),
        ({"allowed": None}, {"allowed": [1]}),
        ({"allowed": [[1]]}, {"allowed": [[2]]}),
        ({"range": {"min": "a"}}, {"range": {"min": "b"}}),
        ({"modality": 1}, {"modality": 2}),
        ({"ranges": [{"min": 1}]}, {"ranges": [{"min": 1}, {"min": 2}]}),
    ]
    for before, after in hostile:
        changes = diff_paths(before, after)
        assert changes
        verdicts = {constraint_change(path, left, right) for path, left, right in changes}
        assert verdicts <= {"neither", "strengthening", "weakening", "admitted"}
        assert "neither" in verdicts or "strengthening" in verdicts
    # A `type` change is pre-empted at proposal read ("constraint family must
    # match the stable locator", spec F5); the policy still classes it neither.
    assert constraint_change("type", "frequency", "uniqueness") == "neither"
    assert constraint_change("allowed", [1, 2], [1]) == "strengthening"
    assert constraint_change("allowed", [1, {"x": 1}], [1]) == "neither"


def test_t13_linear_in_the_proposal_and_one_index_construction(monkeypatch: pytest.MonkeyPatch) -> None:
    from gnd.documents import Model
    from gnd.evolve import CommittedText, EvolutionOperationAudit, EvolutionProposal
    from gnd.evolve.policy import additive_policy_issues, effective_populated
    from gnd.model_index import ModelIndex

    count = 2000
    document = _doc()
    template = _fact(document, CONTROL)
    document["constraints"] = []
    document["fact_types"] = []
    for number in range(count):
        fact = copy.deepcopy(template)
        fact["id"] = f"ft_{number}"
        fact["sample_population"] = [{"order": number, "amount": 1}]
        for constraint in fact["constraints"]:
            if constraint["type"] == "value":
                constraint["role_ref"]["fact_type"] = fact["id"]
        document["fact_types"].append(fact)
    model = Model.model_validate(document)
    operations = []
    for number in range(count):
        before = document["fact_types"][number]["constraints"][0]
        operations.append(_op("modify", _constraint_locator(f"ft_{number}", before, "uniqueness"), before=before,
                              after=dict(before, roles=["order", "amount"]), operation_id=f"op-{number}"))
    text = json.dumps(document)
    proposal = EvolutionProposal(
        proposal_id="scale", expected_model_sha256=hashlib.sha256(text.encode()).hexdigest(),
        candidate_model=CommittedText.from_text(text, media_type="application/json"), operations=tuple(operations),
        rationale="scale", audit=EvolutionOperationAudit(actor_id="a", origin="o", requested_at=datetime(2026, 11, 4, tzinfo=UTC)))
    constructions = {"n": 0}
    visits = {"n": 0}
    original_uncached = ModelIndex._for_model_uncached
    original_iter = ModelIndex.iter_fact_types_shared

    def counted_uncached(model_arg: Any) -> Any:
        constructions["n"] += 1
        return original_uncached(model_arg)

    def counted_iter(self: Any) -> Any:
        for row in original_iter(self):
            visits["n"] += 1
            yield row

    monkeypatch.setattr(ModelIndex, "_for_model_uncached", classmethod(lambda cls, m: counted_uncached(m)))
    monkeypatch.setattr(ModelIndex, "iter_fact_types_shared", counted_iter)
    from gnd.model_index import index_scope

    started = time.perf_counter()
    with index_scope():
        populated = effective_populated(model, proposal, populated_args=())
        issues = additive_policy_issues(model, proposal, populated=populated)
    elapsed = time.perf_counter() - started
    assert len(populated) == count and len(issues) == 0
    assert constructions["n"] == 1
    # Spec F4: two linear walks (one per function), not one; still linear.
    assert visits["n"] <= 2 * count
    assert elapsed < 5.0, elapsed


def test_t14_the_cell_literal_the_contract_table_and_the_walk_agree() -> None:
    from gnd.evolve.models import PolicyCell

    literal = set(get_args(PolicyCell))
    section = CONTRACT.read_text(encoding="utf-8").split("### Additive policy", 1)[1].split("\n## ", 1)[0]
    documented = set(re.findall(r"`((?:object_types|fact_types|role|constraint\.populated|model_identity|source_document|include)\.[a-z_-]+)`", section))
    assert documented == literal, (documented ^ literal)
    emitted = {cell for _name, _build, cell, _reach in CELL_CASES if cell is not None}
    # MC3 adds one closed cell; retain every predecessor matrix case unchanged.
    assert emitted == literal - {'include.repin-include'}, (emitted ^ literal)
    from gnd.evolve import IncludeLocator

    old = {'id': 'vocabulary', 'path': 'before.json', 'sha256': 'a' * 64}
    repin = _op('repin-include', IncludeLocator(include_id='vocabulary'), before=old,
                after={**old, 'path': 'after.json'})
    assert [issue.cell for issue in _direct_issues((repin,))] == ['include.repin-include']
    from gnd.evolve import PolicyIssue

    with pytest.raises(ValidationError):
        PolicyIssue(operation_index=0, operation_id="x", reference="r", cell="constraint.rename", detail="d")


# --- close review R1-F1: object-scoped model-hosted constraints ----------------

_QUOTE = {"source": "user-supplied", "status": "confirmed", "modality": "alethic",
          "provenance": {"user_quote": "Stated by the owner."}}
OBJECT_SCOPED = [
    ("value-object-type", "value", {"type": "value", "object_type": "channel", "allowed": ["phone"], **_QUOTE}),
    ("value-entity-value-type", "value", {"type": "value", "object_type": "order_id",
                                          "range": {"min": 100, "max": 200}, **_QUOTE}),
    ("cardinality-object", "cardinality", {"type": "cardinality", "scope": "object", "object_type": "order",
                                           "bound": {"max": 1}, **_QUOTE}),
]


@pytest.mark.parametrize(("name", "family", "constraint"), OBJECT_SCOPED, ids=[row[0] for row in OBJECT_SCOPED])
def test_close_r1_f1_an_object_scoped_constraint_on_a_populated_player_is_refused(
        tmp_path: Path, name: str, family: str, constraint: dict[str, Any]) -> None:
    """`channel` and `order` play roles in the populated customer_places_order."""
    operation = _op("add", _constraint_locator(None, None, family), after=constraint)
    preview = _preview(tmp_path, (operation,))
    assert [issue.cell for issue in preview.policy_issues] == ["constraint.populated.add"]


def test_close_r1_f1_controls(tmp_path: Path) -> None:
    """An object type playing only unpopulated roles is admitted; a role_ref keeps the role's scope."""
    unpopulated = {"type": "value", "object_type": "amount", "range": {"min": 0, "max": 5}, **_QUOTE}
    preview = _preview(tmp_path / "a", (_op("add", _constraint_locator(None, None, "value"), after=unpopulated),))
    assert preview.policy_issues == ()
    from gnd.evolve.policy import _object_scoped_types

    role_scoped = {"type": "value", "object_type": "channel", "allowed": ["web"],
                   "role_ref": {"fact_type": "order_has_amount", "role": "amount"}}
    assert _object_scoped_types(role_scoped) == set()
    partition = {"type": "subtype-partition", "supertype": "customer", "subtypes": ["vip", "regular"]}
    assert _object_scoped_types(partition) == {"customer", "vip", "regular"}
