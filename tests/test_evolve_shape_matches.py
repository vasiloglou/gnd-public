"""MG3: the duplicate-shape report on gnd evolve preview.

Spec: .gnd-planning/milestones/model-growth-guardrails/notes/phase-MG3-spec.md
(§Tests T1-T13). Fixture: MG2's tests/fixtures/evolve-policy/base.orm.yaml,
where order_has_amount plays (order, amount) and customer_places_order plays
(customer, order, channel).
"""

from __future__ import annotations

import copy
import hashlib
import io
import json
import sys
import time
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
from ruamel.yaml import YAML
from support.cli_runner import run_main

REPO_ROOT = Path(__file__).resolve().parent.parent
BASE = REPO_ROOT / "tests" / "fixtures" / "evolve-policy" / "base.orm.yaml"


# --- builders ---------------------------------------------------------------


def _doc(text: str | None = None) -> dict[str, Any]:
    return YAML(typ="safe").load(text if text is not None else BASE.read_text(encoding="utf-8"))


def _op(kind: str, collection: str, element_id: str, *, before: Any = None, after: Any = None,
        operation_id: str = "op") -> Any:
    from gnd.evolve import ElementLocator, EvolutionOperation, EvolutionOperationKind

    return EvolutionOperation(
        operation_id=operation_id,
        kind=EvolutionOperationKind(kind),
        locator=ElementLocator(collection=collection, element_id=element_id),
        before=copy.deepcopy(before),
        after=copy.deepcopy(after),
    )


def _fact(document: dict[str, Any], fact_type_id: str) -> dict[str, Any]:
    return next(item for item in document["fact_types"] if item["id"] == fact_type_id)


def _delete_memo(first_id: str = "a") -> tuple[Any, Any]:
    """Delete order_has_memo and the hosted exclusion that names it (a breaking pair)."""
    from gnd.evolve import (
        ConstraintLocator,
        EvolutionOperation,
        EvolutionOperationKind,
        canonical_sha256,
    )

    exclusion = next(item for item in _doc()["constraints"] if item["type"] == "exclusion")
    locator = ConstraintLocator(host="model", family="exclusion", canonical_before_sha256=canonical_sha256(exclusion),
                                duplicate_occurrence=0)
    return (_op("delete", "fact_types", "order_has_memo", before=_fact(_doc(), "order_has_memo"),
                operation_id=first_id),
            EvolutionOperation(operation_id=f"{first_id}x", kind=EvolutionOperationKind.DELETE, locator=locator,
                               before=exclusion))


def _proposal(before_text: str, operations: tuple[Any, ...], *, proposal_id: str = "proposal-shape") -> Any:
    from gnd.discover import output
    from gnd.evolve import CommittedText, EvolutionOperationAudit, EvolutionProposal

    candidate = output.candidate_document(_doc(before_text), operations)
    return EvolutionProposal(
        proposal_id=proposal_id,
        expected_model_sha256=hashlib.sha256(before_text.encode("utf-8")).hexdigest(),
        candidate_model=CommittedText.from_text(output.candidate_text(candidate), media_type="application/yaml"),
        operations=operations,
        rationale="MG3 shape case.",
        audit=EvolutionOperationAudit(actor_id="owner:fixture", origin="test_evolve_shape_matches",
                                      requested_at=datetime(2026, 11, 4, 12, 0, tzinfo=UTC)),
    )


def _service(tmp_path: Path, text: str) -> Any:
    sys.path.insert(0, str(REPO_ROOT / "tests"))
    import test_model_evolution as evolution

    service, _model, _verbalization = evolution._service(tmp_path / "ws", text)
    return service


def _preview(tmp_path: Path, operations: tuple[Any, ...], **options: Any) -> Any:
    text = BASE.read_text(encoding="utf-8")
    return _service(tmp_path, text).preview(_proposal(text, operations), **options)


def _fact_type(fact_type_id: str, reading: str, *roles: tuple[str, str], **extra: Any) -> dict[str, Any]:
    return {"id": fact_type_id, "reading": reading,
            "roles": [{"object_type": player, "role_name": name} for name, player in roles], **extra}


# order_has_amount's shape, roles reordered.
COST = _fact_type("amount_costs_order", "{Amount} is the cost of {Order}",
                  ("amount", "amount"), ("order", "order"), inverse_reading="{Order} costs {Amount}")
# customer_places_order's shape.
VISIT = _fact_type("customer_visits_order", "{Customer} visits {Order} via {Channel}",
                   ("customer", "customer"), ("order", "order"), ("channel", "channel"))
LONELY = _fact_type("order_has_note", "{Order} has {Note}", ("order", "order"), ("note", "note"))
VIP = {"id": "vip", "name": "Vip", "kind": "entity", "subtype_of": ["customer"], "inherits_reference": True}
VIP_VISIT = _fact_type("vip_visits_order", "{Vip} visits {Order} via {Channel}",
                       ("vip", "vip"), ("order", "order"), ("channel", "channel"))


def _groups(preview: Any) -> list[dict[str, Any]]:
    return [group.model_dump(mode="json") for group in preview.shape_matches]


def _group(preview: Any, fact_type_id: str) -> dict[str, Any]:
    return next(group for group in _groups(preview)
                if any(member["fact_type"] == fact_type_id for member in group["added"]))


def _candidates(preview: Any, fact_type_id: str) -> list[tuple[str, str]]:
    """An added fact type's candidates: the other members of its group."""
    group = _group(preview, fact_type_id)
    return sorted([("added", m["fact_type"]) for m in group["added"] if m["fact_type"] != fact_type_id]
                  + [("existing", m["fact_type"]) for m in group["existing"]])


# --- T1: the signature helper -----------------------------------------------


def test_t1_role_player_signature() -> None:
    from gnd.refscheme import role_player_signature

    assert role_player_signature({"a": "order", "b": "amount"}) == role_player_signature({"x": "amount", "y": "order"})
    assert role_player_signature({"1": "A", "2": "A", "3": "B"}) != role_player_signature({"1": "A", "2": "B", "3": "B"})
    assert role_player_signature({"1": "vip", "2": "order"}) != role_player_signature({"1": "customer", "2": "order"})
    # Two value types with the same primitive (Integer) are two ids.
    assert role_player_signature({"1": "order", "2": "amount"}) != role_player_signature({"1": "order", "2": "order_id"})
    # Total over a hostile mapping: non-string players are ignored, never raised on.
    assert role_player_signature({"a": None, "b": 3, "c": ["x"], "d": "order"}) == ("order",)


def test_t1_fact_type_signatures_reads_through_model_index() -> None:
    from gnd.model import load_model
    from gnd.model_index import ModelIndex
    from gnd.refscheme import fact_type_signatures

    signatures = fact_type_signatures(ModelIndex.for_model(load_model(BASE)))
    assert signatures["customer_places_order"] == ("channel", "customer", "order")
    assert signatures["order_has_amount"] == ("amount", "order")


def test_t1b_two_identical_adds_match_each_other(tmp_path: Path) -> None:
    twin = dict(copy.deepcopy(LONELY), id="order_has_remark", reading="{Order} has remark {Note}")
    preview = _preview(tmp_path, (_op("add", "fact_types", LONELY["id"], after=LONELY, operation_id="a"),
                                  _op("add", "fact_types", twin["id"], after=twin, operation_id="b")),
                       shape_report=True)
    (group,) = _groups(preview)
    assert [(m["operation_index"], m["fact_type"]) for m in group["added"]] == [
        (0, "order_has_note"), (1, "order_has_remark")]
    assert _candidates(preview, "order_has_note") == [("added", "order_has_remark")]
    assert _candidates(preview, "order_has_remark") == [("added", "order_has_note")]


# --- T2: the report ---------------------------------------------------------


def test_t2_an_add_shaped_like_an_existing_fact_type(tmp_path: Path) -> None:
    preview = _preview(tmp_path, (_op("add", "fact_types", VISIT["id"], after=VISIT),), shape_report=True)
    (group,) = _groups(preview)
    assert group["signature"] == ["channel", "customer", "order"]
    assert group["added"] == [{"operation_index": 0, "fact_type": "customer_visits_order",
                               "reading": "{Customer} visits {Order} via {Channel}", "inverse_reading": None}]
    assert group["existing"] == [{"fact_type": "customer_places_order",
                                  "reading": "{Customer} places {Order} via {Channel}", "inverse_reading": None}]
    # Entity role players only, once each; channel is a value type.
    assert group["references"] == [
        {"object_type": "customer", "identity": "direct", "value_type": "customer_id"},
        {"object_type": "order", "identity": "direct", "value_type": "order_id"},
    ]


def test_t2_reordered_roles_match_and_carry_readings(tmp_path: Path) -> None:
    preview = _preview(tmp_path, (_op("add", "fact_types", COST["id"], after=COST),), shape_report=True)
    group = _group(preview, COST["id"])
    assert [m["fact_type"] for m in group["existing"]] == ["order_has_amount"]
    assert group["existing"][0]["reading"] == "{Order} has {Amount}"
    assert group["added"][0]["inverse_reading"] == "{Order} costs {Amount}"


def _composite_model() -> tuple[str, dict[str, Any]]:
    """The base fixture plus an externally identified entity (review R-F7)."""
    document = _doc()
    document["object_types"].append({"id": "shipment", "name": "Shipment", "kind": "entity",
                                     "reference": {"mode": "external"}})
    document["fact_types"].extend([
        _fact_type("shipment_carries_order", "{Shipment} carries {Order}", ("shipment", "shipment"), ("order", "order")),
        _fact_type("shipment_uses_channel", "{Shipment} uses {Channel}", ("shipment", "shipment"),
                   ("channel", "channel")),
    ])
    document["constraints"].append({
        "type": "uniqueness", "scope": "external",
        "role_refs": [{"fact_type": "shipment_carries_order", "role": "order"},
                      {"fact_type": "shipment_uses_channel", "role": "channel"}],
        "source": "user-supplied", "status": "confirmed", "modality": "alethic",
        "provenance": {"user_quote": "An order and a channel identify a shipment."}})
    buffer = io.StringIO()
    YAML().dump(document, buffer)
    return buffer.getvalue(), document


def test_t2_composite_and_unmatchable_references(tmp_path: Path) -> None:
    text, _document = _composite_model()
    composite = _fact_type("shipment_has_note", "{Shipment} has {Note}", ("shipment", "shipment"), ("note", "note"))
    # A subtype that neither inherits nor declares a reference: no printable value.
    orphan = {"id": "parcel", "name": "Parcel", "kind": "entity", "subtype_of": ["customer"],
              "inherits_reference": False}
    lonely = _fact_type("parcel_has_note", "{Parcel} has {Note}", ("parcel", "parcel"), ("note", "note"))
    preview = _service(tmp_path, text).preview(_proposal(text, (
        _op("add", "fact_types", composite["id"], after=composite, operation_id="a"),
        _op("add", "object_types", "parcel", after=orphan, operation_id="b"),
        _op("add", "fact_types", lonely["id"], after=lonely, operation_id="c"))), shape_report=True)
    assert _group(preview, "shipment_has_note")["references"] == [
        {"object_type": "shipment", "identity": "composite", "value_type": None}]
    assert _group(preview, "parcel_has_note")["references"] == [
        {"object_type": "parcel", "identity": "unmatchable", "value_type": None}]


def test_t2b_a_subtype_does_not_match_its_supertype(tmp_path: Path) -> None:
    preview = _preview(tmp_path, (_op("add", "object_types", "vip", after=VIP, operation_id="a"),
                                  _op("add", "fact_types", VIP_VISIT["id"], after=VIP_VISIT, operation_id="b")),
                       shape_report=True)
    (group,) = _groups(preview)
    assert group["added"][0]["operation_index"] == 1 and group["existing"] == []


def test_t2c_an_add_with_no_match_is_listed_empty(tmp_path: Path) -> None:
    preview = _preview(tmp_path, (_op("add", "fact_types", LONELY["id"], after=LONELY),), shape_report=True)
    assert _candidates(preview, LONELY["id"]) == []


def test_t2d_a_deleted_fact_type_still_matches_its_replacement(tmp_path: Path) -> None:
    replacement = _fact_type("order_carries_memo", "{Order} carries {Memo}", ("order", "order"), ("memo", "memo"))
    preview = _preview(tmp_path, (*_delete_memo(),
                                  _op("add", "fact_types", replacement["id"], after=replacement, operation_id="b")),
                       shape_report=True)
    assert _candidates(preview, replacement["id"]) == [("existing", "order_has_memo")]


def test_review_f3_a_modified_fact_type_is_judged_in_its_candidate_shape(tmp_path: Path) -> None:
    """R-F3: a MODIFY into the added shape matches; the old shape no longer does."""
    before = _fact(_doc(), "order_has_memo")
    after = dict(copy.deepcopy(before), reading="{Order} has {Note}",
                 roles=[{"object_type": "order", "role_name": "order"}, {"object_type": "note", "role_name": "memo"}])
    preview = _preview(tmp_path, (_op("modify", "fact_types", "order_has_memo", before=before, after=after,
                                      operation_id="a"),
                                  _op("add", "fact_types", LONELY["id"], after=LONELY, operation_id="b")),
                       shape_report=True)
    group = _group(preview, LONELY["id"])
    assert group["existing"] == [{"fact_type": "order_has_memo", "reading": "{Order} has {Note}",
                                  "inverse_reading": None}]


def test_review_f2_an_add_the_proposal_then_deletes_has_no_group(tmp_path: Path) -> None:
    from gnd.evolve.shapes import shape_matches
    from gnd.model import load_model

    proposal = _proposal(BASE.read_text(encoding="utf-8"), (_op("add", "fact_types", VISIT["id"], after=VISIT),))
    ghost = type("P", (), {"operations": proposal.operations + (
        _op("add", "fact_types", "ghost1", after=dict(LONELY, id="ghost1"), operation_id="g1"),
        _op("add", "fact_types", "ghost2", after=dict(LONELY, id="ghost2"), operation_id="g2"))})()
    before = load_model(BASE)
    # The candidate holds none of the three ids, as when each was added and then deleted.
    candidate = load_model(BASE)
    assert shape_matches(before, candidate, ghost) == ()


def test_review_f5_a_deleted_and_re_added_id_still_meets_its_old_shape(tmp_path: Path) -> None:
    from gnd.evolve.shapes import shape_matches
    from gnd.model import load_model

    before = load_model(BASE)
    document = _doc()
    reshaped = _fact_type("order_has_memo", "{Order} has {Note}", ("order", "order"), ("note", "note"))
    document["fact_types"] = [reshaped if item["id"] == "order_has_memo" else item for item in document["fact_types"]]
    from gnd.documents import Model

    candidate = Model.model_validate(document)
    twin = _fact_type("order_keeps_memo", "{Order} keeps {Memo}", ("order", "order"), ("memo", "memo"))
    candidate = Model.model_validate({**document, "fact_types": [*document["fact_types"], twin]})
    proposal = type("P", (), {"operations": (
        _op("add", "fact_types", "order_has_memo", after=reshaped, operation_id="a"),
        _op("add", "fact_types", twin["id"], after=twin, operation_id="b"))})()
    groups = {group.signature: group for group in shape_matches(before, candidate, proposal)}
    assert [m.fact_type for m in groups[("memo", "order")].existing] == ["order_has_memo"]


# --- T3: order and absence --------------------------------------------------


def test_t3_stable_order_and_byte_identical_reruns(tmp_path: Path) -> None:
    operations = (_op("add", "fact_types", VISIT["id"], after=VISIT, operation_id="a"),
                  _op("add", "fact_types", COST["id"], after=COST, operation_id="b"))
    first = _preview(tmp_path / "1", operations, shape_report=True)
    second = _preview(tmp_path / "2", operations, shape_report=True)
    assert [group["added"][0]["operation_index"] for group in _groups(first)] == [0, 1]
    assert first.model_dump(mode="json") == second.model_dump(mode="json")


def test_t3_one_group_per_signature(tmp_path: Path) -> None:
    twin = dict(copy.deepcopy(COST), id="amount_prices_order", reading="{Amount} prices {Order}")
    preview = _preview(tmp_path, (_op("add", "fact_types", COST["id"], after=COST, operation_id="a"),
                                  _op("add", "fact_types", twin["id"], after=twin, operation_id="b")),
                       shape_report=True)
    assert len(_groups(preview)) == 1
    assert _candidates(preview, COST["id"]) == [("added", "amount_prices_order"), ("existing", "order_has_amount")]


def test_t3b_without_the_option_there_is_no_key(tmp_path: Path) -> None:
    preview = _preview(tmp_path, (_op("add", "fact_types", VISIT["id"], after=VISIT),))
    assert preview.shape_matches is None
    assert "shape_matches" not in preview.model_dump(mode="json")


def test_t3c_a_proposal_with_no_fact_type_add_reports_an_empty_tuple(tmp_path: Path) -> None:
    preview = _preview(tmp_path, (_op("add", "object_types", "vip", after=VIP),), shape_report=True)
    assert preview.shape_matches == ()
    assert preview.model_dump(mode="json")["shape_matches"] == []


def test_t3d_the_reader_refuses_inconsistent_reports(tmp_path: Path) -> None:
    """R-F6, R-F7: every reader check refuses its hostile edit."""
    from gnd.evolve import EvolutionPreview, canonical_sha256

    twin = dict(copy.deepcopy(COST), id="amount_prices_order", reading="{Amount} prices {Order}")
    preview = _preview(tmp_path, (_op("add", "fact_types", COST["id"], after=COST, operation_id="a"),
                                  _op("add", "fact_types", twin["id"], after=twin, operation_id="b"),
                                  _op("add", "fact_types", VISIT["id"], after=VISIT, operation_id="c")),
                       shape_report=True)

    def reread(mutate: Any) -> None:
        document = preview.model_dump(mode="json")
        mutate(document["shape_matches"])
        document["preview_sha256"] = canonical_sha256({k: v for k, v in document.items() if k != "preview_sha256"})
        EvolutionPreview.model_validate(document)

    reread(lambda groups: None)  # the control reads
    cases = [
        ("first added operation", lambda g: g.reverse()),
        ("one group per signature", lambda g: g[1].update(signature=g[0]["signature"])),
        ("signature must be sorted", lambda g: g[0]["signature"].reverse()),
        ("unique and in operation order", lambda g: g[0]["added"].reverse()),
        ("does not add that fact type", lambda g: g[0]["added"][0].update(fact_type="order_has_amount")),
        ("does not add that fact type", lambda g: g[-1]["added"][0].update(operation_index=9)),
        ("existing members must be unique", lambda g: g[0]["existing"].append(dict(g[0]["existing"][0]))),
        ("references must be unique", lambda g: g[1]["references"].reverse()),
        ("references must be unique", lambda g: g[0]["references"].append(
            {"object_type": "customer", "identity": "direct", "value_type": "customer_id"})),
        ("exactly when identity is direct", lambda g: g[0]["references"][0].update(value_type=None)),
        ("exactly when identity is direct", lambda g: g[0]["references"][0].update(identity="composite")),
        ("at least 1 item", lambda g: g[0].update(added=[])),
    ]
    for message, mutate in cases:
        with pytest.raises(ValueError, match=message):
            reread(mutate)


# --- T4: advice never gates (MG-R4) -----------------------------------------


GATE_KEYS = ("breaking", "blast_radius", "affected_references", "policy", "populated_args", "populated",
             "policy_issues", "validation", "candidate_model", "verbalization")


@pytest.mark.parametrize("policy", [None, "additive"])
@pytest.mark.parametrize("subject", ["admitted", "refused", "breaking"])
def test_t4_the_report_changes_no_gate_field(tmp_path: Path, policy: str | None, subject: str) -> None:
    from gnd.evolve.service import EvolutionError

    mandatory = {"type": "mandatory", "role": "order", "source": "user-supplied", "status": "confirmed",
                 "modality": "deontic", "provenance": {"user_quote": "Every row names an order."}}
    visit = dict(copy.deepcopy(VISIT), constraints=[])
    if subject == "admitted":
        operations = (_op("add", "fact_types", VISIT["id"], after=VISIT),)
    elif subject == "refused":
        # A fact-type MODIFY on the populated fact type adding a constraint, plus an ADD.
        before = _fact(_doc(), "customer_places_order")
        after = copy.deepcopy(before)
        after["constraints"].append(mandatory)
        operations = (_op("modify", "fact_types", "customer_places_order", before=before, after=after,
                          operation_id="a"),
                      _op("add", "fact_types", visit["id"], after=visit, operation_id="b"))
    else:
        operations = (*_delete_memo(), _op("add", "fact_types", VISIT["id"], after=VISIT, operation_id="b"))
    outcomes = []
    for shape_report in (False, True):
        try:
            outcomes.append(_preview(tmp_path / str(shape_report), operations, policy=policy,
                                     shape_report=shape_report).model_dump(mode="json"))
        except EvolutionError as error:  # pragma: no cover - none of the subjects raise
            outcomes.append(str(error))
    without, with_report = outcomes
    for key in GATE_KEYS:
        assert without.get(key) == with_report.get(key), key
    assert without["blast_radius"]["report_sha256"] == with_report["blast_radius"]["report_sha256"]
    if subject == "refused" and policy:
        assert with_report["policy_issues"], "the refused subject must carry an issue"
    if subject == "breaking":
        assert with_report["breaking"] is True


def test_t4b_the_report_runs_after_the_policy(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from gnd.evolve import service as service_module

    calls: list[str] = []
    real_policy = service_module.EvolutionService._policy_values
    real_shapes = service_module.shape_matches

    def policy_spy(*args: Any, **kwargs: Any) -> Any:
        calls.append("policy")
        return real_policy(*args, **kwargs)

    def shapes_spy(*args: Any, **kwargs: Any) -> Any:
        calls.append("shapes")
        return real_shapes(*args, **kwargs)

    monkeypatch.setattr(service_module.EvolutionService, "_policy_values", staticmethod(policy_spy))
    monkeypatch.setattr(service_module, "shape_matches", shapes_spy)
    _preview(tmp_path, (_op("add", "fact_types", VISIT["id"], after=VISIT),), policy="additive", shape_report=True)
    assert calls == ["policy", "shapes"]


def test_t4c_a_refusal_before_the_report_is_unchanged(tmp_path: Path) -> None:
    from gnd.evolve.service import EvolutionError

    bad = dict(copy.deepcopy(VISIT), reading="{Customer} visits {Order}")  # one placeholder short
    for shape_report in (False, True):
        with pytest.raises(EvolutionError):
            _preview(tmp_path / str(shape_report), (_op("add", "fact_types", bad["id"], after=bad),),
                     shape_report=shape_report)


# --- T5: apply ---------------------------------------------------------------


def _cli_workspace(root: Path, operations: tuple[Any, ...], *, before_text: str | None = None) -> dict[str, Path]:
    text = before_text if before_text is not None else BASE.read_text(encoding="utf-8")
    root.mkdir(parents=True, exist_ok=True)
    (root / "records").mkdir(exist_ok=True)
    model = root / "model.orm.yaml"
    model.write_text(text, encoding="utf-8")
    (root / "model.verbalization.txt").write_text("pre-existing\n", encoding="utf-8")
    proposal = root / "proposal.json"
    proposal.write_text(json.dumps(_proposal(text, operations).model_dump(mode="json"), indent=2, sort_keys=True)
                        + "\n", encoding="utf-8")
    return {"workspace": root, "model": model, "proposal": proposal, "preview": root / "preview.json",
            "records": root / "records"}


def _preview_argv(paths: dict[str, Path], *extra: str) -> list[str]:
    return ["evolve", "preview", str(paths["model"]), str(paths["proposal"]), "--workspace", str(paths["workspace"]),
            "--records", str(paths["records"]), "--out", str(paths["preview"]), "--format", "json", *extra]


def _apply_argv(paths: dict[str, Path], *extra: str) -> list[str]:
    return ["evolve", "apply", str(paths["model"]), str(paths["proposal"]), "--preview", str(paths["preview"]),
            "--workspace", str(paths["workspace"]), "--records", str(paths["records"]), "--format", "json", *extra]


def _rewrite(paths: dict[str, Path], mutate: Any) -> None:
    from gnd.evolve import canonical_sha256

    document = json.loads(paths["preview"].read_text(encoding="utf-8"))
    mutate(document)
    document["preview_sha256"] = canonical_sha256({k: v for k, v in document.items() if k != "preview_sha256"})
    paths["preview"].write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")


ADD_VISIT = (_op("add", "fact_types", VISIT["id"], after=VISIT),)


def test_t5_a_shape_report_preview_applies(tmp_path: Path) -> None:
    paths = _cli_workspace(tmp_path, ADD_VISIT)
    result = run_main(_preview_argv(paths, "--shape-report"))
    assert result.returncode == 0, result.stderr
    assert json.loads(paths["preview"].read_text(encoding="utf-8"))["shape_matches"][0]["existing"]
    result = run_main(_apply_argv(paths))
    assert result.returncode == 0, result.stderr
    assert "customer_visits_order" in paths["model"].read_text(encoding="utf-8")


def test_t5_with_policy_and_shape_report_applies(tmp_path: Path) -> None:
    """MG2-Q1: MG2-C3's last CLI clause."""
    paths = _cli_workspace(tmp_path, ADD_VISIT)
    assert run_main(_preview_argv(paths, "--policy", "additive", "--shape-report")).returncode == 0
    result = run_main(_apply_argv(paths, "--policy", "additive"))
    assert result.returncode == 0, result.stderr


def test_t5_an_edited_report_is_stale(tmp_path: Path) -> None:
    paths = _cli_workspace(tmp_path, ADD_VISIT)
    assert run_main(_preview_argv(paths, "--shape-report")).returncode == 0
    _rewrite(paths, lambda document: document["shape_matches"][0].update(existing=[]))
    result = run_main(_apply_argv(paths))
    assert result.returncode == 11, result.stderr
    assert "customer_visits_order" not in paths["model"].read_text(encoding="utf-8")


def test_t5_a_stripped_report_applies_because_it_gates_nothing(tmp_path: Path) -> None:
    paths = _cli_workspace(tmp_path, ADD_VISIT)
    assert run_main(_preview_argv(paths, "--shape-report")).returncode == 0
    _rewrite(paths, lambda document: document.pop("shape_matches"))
    result = run_main(_apply_argv(paths))
    assert result.returncode == 0, result.stderr


def test_t5b_breaking_acceptance_rebuild_keeps_the_report(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    operations = (*_delete_memo(), _op("add", "fact_types", VISIT["id"], after=VISIT, operation_id="b"))
    paths = _cli_workspace(tmp_path, operations)
    assert run_main(_preview_argv(paths, "--shape-report")).returncode == 0
    document = json.loads(paths["preview"].read_text(encoding="utf-8"))
    assert document["breaking"] is True
    monkeypatch.setattr("builtins.input", lambda: document["blast_radius"]["report_sha256"])
    result = run_main(_apply_argv(paths))
    assert result.returncode == 0, result.stderr
    staged = json.loads((paths["records"] / "proposal-shape" / "preview.json").read_text(encoding="utf-8"))
    assert staged["shape_matches"] == document["shape_matches"]


def test_t5c_text_claim_lists_each_match(tmp_path: Path) -> None:
    paths = _cli_workspace(tmp_path, ADD_VISIT)
    argv = [arg if arg != "json" else "text" for arg in _preview_argv(paths, "--shape-report")]
    result = run_main(argv)
    assert result.returncode == 0, result.stderr
    assert (b"shape-group: channel,customer,order added customer_visits_order existing customer_places_order"
            in result.stdout)


# --- T7: cost ------------------------------------------------------------------


class _CountingDict(dict):
    probes = 0

    def setdefault(self, key: Any, default: Any = None) -> Any:
        type(self).probes += 1
        return super().setdefault(key, default)

    def __getitem__(self, key: Any) -> Any:
        type(self).probes += 1
        return super().__getitem__(key)

    def get(self, key: Any, default: Any = None) -> Any:
        type(self).probes += 1
        return super().get(key, default)


def test_t7_bucket_probes_are_linear() -> None:
    from gnd.documents import Model
    from gnd.evolve.shapes import shape_matches

    object_types = [{"id": f"o{i}", "name": f"O{i}", "kind": "value", "primitive": "String"} for i in range(100)]

    def fact(i: int, prefix: str) -> dict[str, Any]:
        a, b = f"o{i % 100}", f"o{(i * 7) % 100}"
        return {"id": f"{prefix}{i}", "reading": "{A} r {B}",
                "roles": [{"object_type": a, "role_name": "a"}, {"object_type": b, "role_name": "b"}]}

    existing = [fact(i, "f") for i in range(5000)]
    added = [fact(i, "n") for i in range(500)]
    before = Model.model_validate({"version": 1, "model_id": "scale", "object_types": object_types,
                                   "fact_types": existing})
    candidate = Model.model_validate({"version": 1, "model_id": "scale", "object_types": object_types,
                                      "fact_types": existing + added})
    proposal = type("P", (), {"operations": tuple(
        _op("add", "fact_types", item["id"], after=item, operation_id=f"op{n}") for n, item in enumerate(added))})()
    _CountingDict.probes = 0
    started = time.perf_counter()
    entries = shape_matches(before, candidate, proposal, bucket_factory=_CountingDict)
    elapsed = time.perf_counter() - started
    assert sum(len(group.added) for group in entries) == 500 and all(group.existing for group in entries)
    assert _CountingDict.probes <= 5500, _CountingDict.probes
    assert elapsed < 5.0, elapsed


def test_t7_a_single_bucket_stays_linear() -> None:
    """R-F1: 5,000 existing and 500 added fact types all of one shape."""
    from gnd.documents import Model
    from gnd.evolve.shapes import shape_matches

    object_types = [{"id": "a", "name": "A", "kind": "value", "primitive": "String"},
                    {"id": "b", "name": "B", "kind": "value", "primitive": "String"}]

    def fact(fact_type_id: str) -> dict[str, Any]:
        return {"id": fact_type_id, "reading": "{A} r {B}",
                "roles": [{"object_type": "a", "role_name": "a"}, {"object_type": "b", "role_name": "b"}]}

    existing = [fact(f"f{i}") for i in range(5000)]
    added = [fact(f"n{i}") for i in range(500)]
    before = Model.model_validate({"version": 1, "model_id": "s", "object_types": object_types, "fact_types": existing})
    candidate = Model.model_validate({"version": 1, "model_id": "s", "object_types": object_types,
                                      "fact_types": existing + added})
    proposal = type("P", (), {"operations": tuple(
        _op("add", "fact_types", item["id"], after=item, operation_id=f"op{n}") for n, item in enumerate(added))})()
    _CountingDict.probes = 0
    started = time.perf_counter()
    (group,) = shape_matches(before, candidate, proposal, bucket_factory=_CountingDict)
    elapsed = time.perf_counter() - started
    assert len(group.added) == 500 and len(group.existing) == 5000
    assert _CountingDict.probes <= 5500
    assert elapsed < 5.0, elapsed


def test_t7_a_large_group_previews_and_applies_under_the_read_cap(tmp_path: Path) -> None:
    """R-F1 at the CLI: 400 existing and 200 added fact types of one shape."""
    document = _doc()
    for i in range(400):
        document["fact_types"].append(_fact_type(f"order_memo_{i}", f"{{Order}} keeps memo{i} {{Memo}}",
                                                 ("order", "order"), ("memo", "memo")))
    buffer = io.StringIO()
    YAML().dump(document, buffer)
    text = buffer.getvalue()
    operations = tuple(_op("add", "fact_types", f"order_memo_new_{i}",
                           after=_fact_type(f"order_memo_new_{i}", f"{{Order}} notes memo{i} {{Memo}}",
                                            ("order", "order"), ("memo", "memo")),
                           operation_id=f"op{i}") for i in range(200))
    paths = _cli_workspace(tmp_path, operations, before_text=text)
    plain = tmp_path / "plain.json"
    assert run_main([*_preview_argv(paths)[:-4], "--out", str(plain), "--format", "json"]).returncode == 0
    result = run_main(_preview_argv(paths, "--shape-report"))
    assert result.returncode == 0, result.stderr
    assert paths["preview"].stat().st_size < 2 * plain.stat().st_size
    result = run_main(_apply_argv(paths))
    assert result.returncode == 0, result.stderr


# --- T9: no value in the report ----------------------------------------------


def test_t9_the_report_carries_no_population_value(tmp_path: Path) -> None:
    preview = _preview(tmp_path, (_op("add", "fact_types", VISIT["id"], after=VISIT),), shape_report=True)
    text = json.dumps([entry.model_dump(mode="json") for entry in preview.shape_matches])
    # A sample value and a value-constraint literal of customer_places_order.
    for value in ('"web"', '"phone"', '"store"'):
        assert value not in text


# --- T13: mutation controls, as data -----------------------------------------


def test_t13_signature_is_a_multiset_not_a_set() -> None:
    from gnd.refscheme import role_player_signature

    mutant = lambda players: tuple(sorted(set(players.values())))
    pair = ({"1": "A", "2": "A", "3": "B"}, {"1": "A", "2": "B"})
    assert mutant(pair[0]) == mutant(pair[1])
    assert role_player_signature(pair[0]) != role_player_signature(pair[1])
    assert Counter(role_player_signature(pair[0])) == Counter({"A": 2, "B": 1})


def test_review_f4_a_stripped_report_on_the_retry_branch_is_the_same_lineage(tmp_path: Path) -> None:
    """R-F4: the retry branch compares review identity without the advice field."""
    paths = _cli_workspace(tmp_path, ADD_VISIT)
    assert run_main(_preview_argv(paths, "--shape-report")).returncode == 0
    assert run_main(_apply_argv(paths)).returncode == 0
    retried = run_main(_apply_argv(paths))
    _rewrite(paths, lambda document: document.pop("shape_matches"))
    stripped = run_main(_apply_argv(paths))
    assert stripped.returncode == retried.returncode, (retried.stderr, stripped.stderr)
    assert stripped.returncode != 11 or b"staged accepted preview differs" not in stripped.stderr
