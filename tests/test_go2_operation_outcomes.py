"""GO2: an outcome for every operation of a proposal (#227).

Spec: .gnd-planning/milestones/growth-round-outcomes/notes/phase-GO2-spec.md (§8, T1-T10).
Verdicts are walked from the verdict table, one committed case per word (GO2-C2),
not from the code.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import pytest
import test_evolve_additive_policy as policy
from support.cli_runner import run_main

from gnd.evolve import (
    EvolutionError,
    EvolutionOutcomeReport,
    RoleLocator,
    read_evolution_outcome_report,
)
from gnd.evolve import outcomes as _outcomes

TEXT = policy.BASE.read_text(encoding="utf-8")
HOST = "order_ships_to_region"


def _op(kind: str, locator: Any, after: Any = None, oid: str = "op", before: Any = None) -> Any:
    return policy._op(kind, locator, after=after, before=before, operation_id=oid)


ADD_OBJECT = _op("add", policy._element("object_types", "region"), policy.NEW_OBJECT, "op-object")
ADD_FACT = _op("add", policy._element("fact_types", HOST), policy.NEW_FACT, "op-fact")


def _constraint(oid: str = "op-constraint", **changes: Any) -> Any:
    body = {**policy.NEW_CONSTRAINT, **changes}
    if "roles" in changes:
        body.pop("role")
    return _op("add", policy._constraint_locator(HOST, None, body["type"]), body, oid)


def _invalid_object(object_id: str, oid: str) -> Any:
    """A value type with no primitive: refused by the structural layer at its own path."""
    return _op("add", policy._element("object_types", object_id),
               {"id": object_id, "name": object_id.title(), "kind": "value"}, oid)


def _refused(tmp_path: Path, operations: tuple[Any, ...], **options: Any) -> Any:
    with pytest.raises(EvolutionError) as caught:
        policy._service(tmp_path, TEXT).preview(policy._proposal(TEXT, operations),
                                                operation_outcomes=True, **options)
    return caught.value


def _rows(pending: Any) -> list[tuple[str, tuple[str, ...]]]:
    return [(row.verdict, row.gates_not_run) for row in pending.operation_outcomes]


# --- T1 (GO2-C1): four operations, one refused by validation -------------------------------------


def _four(tmp_path: Path) -> dict[str, Path]:
    return policy._cli_workspace(tmp_path, (ADD_OBJECT, ADD_FACT, _invalid_object("bad", "op-bad"),
                                            _constraint(status="confirmed")))


def test_t1_the_report_names_all_four_and_the_refusal_is_unchanged(tmp_path: Path) -> None:
    plain = _four(tmp_path / "plain")
    without = run_main(policy._preview_argv(plain))
    paths = _four(tmp_path / "with")
    report = paths["workspace"] / "outcomes.json"
    result = run_main([*policy._preview_argv(paths), "--operation-outcomes", "--outcome-report", str(report)])
    assert result.returncode == without.returncode == 3
    assert result.stderr.replace(b"/with/", b"/plain/") == without.stderr
    assert not paths["preview"].exists()
    document = read_evolution_outcome_report(report)
    assert isinstance(document, EvolutionOutcomeReport)
    assert document.refusal.exit == 3 and document.refusal.gate == "candidate-validation"
    assert f"EVOLUTION PREVIEW REFUSED (3): {document.refusal.message}".encode() in result.stderr
    rows = [(row.operation_id, row.verdict) for row in document.operation_outcomes]
    assert rows == [("op-object", "unassessed"), ("op-fact", "unassessed"), ("op-bad", "refused-by-validation"),
                    ("op-constraint", "unassessed")]
    # The structural layer failed, so the semantic layer and the replay did not run; D-12 ran (GO2-D2).
    assert document.operation_outcomes[0].gates_not_run == ("semantic-validation", "replay-equality")
    assert document.before_model.sha256 == json.loads(paths["proposal"].read_text())["expected_model_sha256"]


def test_t1_the_report_is_written_only_when_asked(tmp_path: Path) -> None:
    paths = _four(tmp_path)
    assert run_main([*policy._preview_argv(paths), "--operation-outcomes"]).returncode == 3
    assert sorted(p.name for p in paths["workspace"].iterdir()) == ["model.orm.yaml", "model.verbalization.txt",
                                                                    "proposal.json", "records"]
    result = run_main([*policy._preview_argv(paths), "--outcome-report", str(paths["workspace"] / "o.json")])
    assert result.returncode == 3 and b"--outcome-report requires --operation-outcomes" in result.stderr
    result = run_main([*policy._preview_argv(paths), "--operation-outcomes", "--outcome-report", str(paths["preview"])])
    assert result.returncode == 3 and b"must not be the preview output path" in result.stderr


# --- T2 (GO2-C2): one case per verdict word, and two faults ---------------------------------------


def test_t2_admitted(tmp_path: Path) -> None:
    preview = policy._service(tmp_path, TEXT).preview(
        policy._proposal(TEXT, (ADD_OBJECT, ADD_FACT)), operation_outcomes=True)
    assert [row.verdict for row in preview.operation_outcomes] == ["admitted", "admitted"]


def test_t2_refused_by_policy_in_the_preview(tmp_path: Path) -> None:
    refused = _op("add", policy._constraint_locator(policy.POPULATED, None, "mandatory"), policy.NEW_CONSTRAINT, "op-p")
    preview = policy._service(tmp_path, TEXT).preview(
        policy._proposal(TEXT, (ADD_OBJECT, refused)), policy="additive", operation_outcomes=True)
    assert [(r.verdict, r.detail) for r in preview.operation_outcomes] == [
        ("admitted", ""), ("refused-by-policy", "constraint.populated.add")]
    assert [issue.operation_index for issue in preview.policy_issues] == [1]


def test_t2_refused_by_validation_and_dropped_with(tmp_path: Path) -> None:
    broken = dict(policy.NEW_FACT, roles=[{"object_type": "nowhere", "role_name": "region"},
                                          {"object_type": "order", "role_name": "order"}])
    fact = _op("add", policy._element("fact_types", HOST), broken, "op-fact")
    error = _refused(tmp_path, (ADD_OBJECT, fact, _constraint(status="confirmed")))
    assert error.outcome_refusal.gate == "semantic-validation"
    assert [row.verdict for row in error.outcome_refusal.operation_outcomes] == [
        "unassessed", "refused-by-validation", "dropped-with"]
    assert error.outcome_refusal.operation_outcomes[2].detail == f"fact_types[{HOST}] is refused"


def test_t2_unassessed_names_the_gates_not_run(tmp_path: Path) -> None:
    error = _refused(tmp_path, (ADD_OBJECT, _invalid_object("bad", "op-bad")), policy="additive")
    assert _rows(error.outcome_refusal)[0] == (
        "unassessed", ("semantic-validation", "replay-equality", "policy"))


def test_t2_two_faults_in_two_operations_are_both_named(tmp_path: Path) -> None:
    error = _refused(tmp_path, (_invalid_object("bad", "op-1"), ADD_OBJECT, _invalid_object("worse", "op-3")))
    assert [row.verdict for row in error.outcome_refusal.operation_outcomes] == [
        "refused-by-validation", "unassessed", "refused-by-validation"]
    error = _refused(tmp_path / "d12", (ADD_OBJECT, ADD_FACT, _constraint("op-c1", source="explicit"),
                                        _constraint("op-c2", type="uniqueness", roles=["order"], source="explicit")))
    assert [row.verdict for row in error.outcome_refusal.operation_outcomes] == [
        "admitted", "admitted", "refused-by-d12", "refused-by-d12"]


def test_t2_the_printed_refusal_is_the_first_as_today(tmp_path: Path) -> None:
    operations = (ADD_OBJECT, ADD_FACT, _constraint("op-c1", source="explicit"),
                  _constraint("op-c2", type="uniqueness", roles=["order"], source="llm-inferred",
                              rationale="r", provenance={"rationale_world_fact": "x"}))
    with pytest.raises(EvolutionError) as without:
        policy._service(tmp_path / "a", TEXT).preview(policy._proposal(TEXT, operations))
    error = _refused(tmp_path / "b", operations)
    assert str(error) == str(without.value)
    assert type(error) is type(without.value)


# --- T3 (GO2-C7, VG2): every D-12 family on the right row ------------------------------------------


@pytest.mark.parametrize(("changes", "message"), [
    ({"source": "explicit"}, "new or changed constraints must be"),
    ({"source": "llm-inferred", "status": "confirmed", "rationale": "r",
      "provenance": {"rationale_world_fact": "x"}}, "new llm-inferred constraints"),
    ({"source": "sample", "status": "confirmed", "rationale": "r", "provenance": {"spans": []}},
     "new sample and common-sense constraints"),
    ({"source": "common-sense", "status": "proposed", "modality": "alethic", "rationale": "r",
      "provenance": {"library_entry": "x"}}, "new sample and common-sense constraints"),
], ids=["explicit", "llm-inferred", "sample", "common-sense"])
def test_t3_each_d12_refusal_is_located(tmp_path: Path, changes: dict[str, Any], message: str) -> None:
    error = _refused(tmp_path, (ADD_OBJECT, ADD_FACT, _constraint(**changes)))
    assert str(error).startswith(message)
    assert error.outcome_refusal.gate == "d12"
    rows = error.outcome_refusal.operation_outcomes
    assert [row.verdict for row in rows] == ["admitted", "admitted", "refused-by-d12"]
    assert rows[2].detail.startswith(message)


def test_t3_a_d12_refusal_under_a_policy_leaves_the_rest_unassessed(tmp_path: Path) -> None:
    error = _refused(tmp_path, (ADD_OBJECT, ADD_FACT, _constraint(source="explicit")), policy="additive")
    assert _rows(error.outcome_refusal) == [("unassessed", ("policy",)), ("unassessed", ("policy",)),
                                            ("refused-by-d12", ())]


# --- whole-proposal refusals (T2, spec r2 item 2) ---------------------------------------------------


def test_t2_a_gated_proposal_is_refused_whole(tmp_path: Path) -> None:
    import test_model_v2 as v2

    before_text = v2.OPERATIONS_MODEL.read_text(encoding="utf-8")
    document = v2._operations_doc()
    referenced = next(ft for ft in document["fact_types"] if ft["id"] == "work_item_has_state")
    renamed = dict(referenced, id="work_item_in_state")
    proposal, _ = v2._proposal(before_text, document, (
        policy._op("rename", policy._element("fact_types", "work_item_has_state"), before=referenced, after=renamed),))
    with pytest.raises(EvolutionError) as caught:
        v2._service(tmp_path / "ws", before_text).preview(proposal, operation_outcomes=True)
    pending = caught.value.outcome_refusal
    assert pending.gate == "operations-gate"
    assert _rows(pending) == [("unassessed", ("candidate-validation", "semantic-validation",
                                              "replay-equality", "d12"))]


def test_t2_vg4_repin_on_an_unattended_root_is_refused_whole(tmp_path: Path) -> None:
    import test_vg4_seeded_growth_rounds as vg4

    root = vg4.cases.write(tmp_path / "ws")
    with pytest.raises(EvolutionError, match="evolve:unattended-repin: ") as caught:
        vg4._service(root).preview(vg4._proposal(root, (vg4._repin(root),), replay=False), operation_outcomes=True)
    pending = caught.value.outcome_refusal
    assert pending.gate == "include-ownership"
    assert [row.verdict for row in pending.operation_outcomes] == ["unassessed"]


# --- T4 (GO2-C3): a preview without outcomes keeps its bytes -----------------------------------------


def test_t4_without_the_flag_nothing_changes(tmp_path: Path) -> None:
    proposal = policy._proposal(TEXT, (ADD_OBJECT, ADD_FACT))
    plain = policy._service(tmp_path / "a", TEXT).preview(proposal)
    with_outcomes = policy._service(tmp_path / "b", TEXT).preview(proposal, operation_outcomes=True)
    plain_document = plain.model_dump(mode="json")
    assert "operation_outcomes" not in plain_document
    outcome_document = with_outcomes.model_dump(mode="json")
    assert [row["verdict"] for row in outcome_document.pop("operation_outcomes")] == ["admitted", "admitted"]
    assert {k: v for k, v in outcome_document.items() if k != "preview_sha256"} == {
        k: v for k, v in plain_document.items() if k != "preview_sha256"}
    assert plain.proposal_sha256 == with_outcomes.proposal_sha256


# --- T5, T7 (GO2-C5, C6): apply and the outcomes ------------------------------------------------------


def test_t5_apply_refuses_an_outcome_report(tmp_path: Path) -> None:
    paths = _four(tmp_path)
    report = paths["workspace"] / "outcomes.json"
    run_main([*policy._preview_argv(paths), "--operation-outcomes", "--outcome-report", str(report)])
    result = run_main(policy._apply_argv({**paths, "preview": report}))
    assert result.returncode == 3, result.stderr
    assert b"is malformed" in result.stderr


def test_t7_apply_replays_the_outcomes_setting(tmp_path: Path) -> None:
    paths = policy._cli_workspace(tmp_path / "a", (ADD_OBJECT, ADD_FACT))
    assert run_main([*policy._preview_argv(paths), "--operation-outcomes"]).returncode == 0
    assert json.loads(paths["preview"].read_text())["operation_outcomes"]
    assert run_main(policy._apply_argv(paths)).returncode == 0
    from gnd.evolve import canonical_sha256

    paths = policy._cli_workspace(tmp_path / "b", (ADD_OBJECT, ADD_FACT))
    assert run_main([*policy._preview_argv(paths), "--operation-outcomes"]).returncode == 0
    document = json.loads(paths["preview"].read_text())
    document["operation_outcomes"][0]["detail"] = "edited"
    document["preview_sha256"] = canonical_sha256({k: v for k, v in document.items() if k != "preview_sha256"})
    paths["preview"].write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")
    result = run_main(policy._apply_argv(paths))
    assert result.returncode == 11, result.stderr


# --- T6 (GO2-C4): value-free ----------------------------------------------------------------------


def test_t6_no_constraint_value_reaches_an_outcome(tmp_path: Path) -> None:
    secret = "SECRET-VALUE-7731"
    value = _op("add", policy._constraint_locator(None, None, "value"),
                {"type": "value", "object_type": "region", "allowed": [secret], "source": "explicit",
                 "status": "confirmed", "modality": "alethic", "rationale": "r",
                 "provenance": {"user_quote": secret}}, "op-value")
    error = _refused(tmp_path, (ADD_OBJECT, value))
    text = json.dumps([row.model_dump(mode="json") for row in error.outcome_refusal.operation_outcomes])
    assert secret not in text and "refused-by-d12" in text


# --- T8: the report reader is total ----------------------------------------------------------------


@pytest.mark.parametrize("payload", [
    b"[" * 10_000 + b"]" * 10_000,
    b'{"schema_version": ' + b"9" * 5_000 + b"}",
    b'{"schema_version": NaN}',
    b'{"schema_version": 1, "kind": "evolution-outcome-report", "extra": 1}',
    b'{"a": "' + b"x" * (11 * 1024 * 1024) + b'"}',
    b"not json",
], ids=["deep", "long-int", "nan", "extra-key", "oversize", "not-json"])
def test_t8_a_hostile_report_is_a_named_refusal(tmp_path: Path, payload: bytes) -> None:
    path = tmp_path / "report.json"
    path.write_bytes(payload)
    with pytest.raises(EvolutionError):
        read_evolution_outcome_report(path, anchor=tmp_path, relative="report.json")


# --- T9: the locator is linear -----------------------------------------------------------------------


def test_t9_the_locator_over_two_thousand_operations_and_issues() -> None:
    from gnd.errors import ValidationIssue

    n = 2_000
    operations = tuple(_op("add", policy._element("object_types", f"t{i}"),
                           {"id": f"t{i}", "name": f"T{i}", "kind": "value"}, f"op-{i}") for i in range(n))
    candidate = {"object_types": [operation.after for operation in operations]}
    issues = [ValidationIssue(path=f"$.object_types[{i}]", message="m", rule_id="jsonschema:required")
              for i in range(n)]
    start = time.perf_counter()
    refused, complete = _outcomes.locate_validation_issues(issues, candidate, operations)
    rows = _outcomes.outcomes(operations, refused)
    assert time.perf_counter() - start < 1.0
    assert complete and len(refused) == n and {row.verdict for row in rows} == {"refused-by-validation"}


# --- Diff review r1 (notes/reviews/phase-GO2-r1/FINDINGS.md): one case per finding ---------------


def test_r1_f1_a_non_list_value_in_after_is_still_a_validation_refusal(tmp_path: Path) -> None:
    operations = (ADD_OBJECT, _op("add", policy._element("fact_types", HOST), dict(policy.NEW_FACT, roles=1), "op-fact"))
    error = _refused(tmp_path, operations)
    rows = error.outcome_refusal.operation_outcomes
    assert rows[1].verdict == "refused-by-validation"
    weird = _op("add", policy._element("object_types", "odd"), {"id": "odd", "subtype_of": 1, "subtypes": {"a": 2}}, "odd")
    assert _outcomes._needs(weird) == []


def test_r1_f2_a_refused_embedded_constraint_refuses_its_fact_type(tmp_path: Path) -> None:
    embedded = {**policy.NEW_CONSTRAINT, "source": "explicit"}
    fact = _op("add", policy._element("fact_types", HOST), dict(policy.NEW_FACT, constraints=[embedded]), "op-fact")
    error = _refused(tmp_path, (ADD_OBJECT, fact))
    assert error.outcome_refusal.gate == "d12"
    assert [row.verdict for row in error.outcome_refusal.operation_outcomes] == ["admitted", "refused-by-d12"]


def _issue(path: str) -> Any:
    from gnd.errors import ValidationIssue

    return ValidationIssue(path=path, message="m", rule_id="semantic:probe")


def test_r1_f3_an_issue_is_pinned_on_the_role_operation_not_on_its_host() -> None:
    role = {"object_type": "missing", "role_name": "extra"}
    operations = (ADD_FACT, _op("add", RoleLocator(fact_type_id=HOST, role_name="extra"), role, "op-role"))
    candidate = {"fact_types": [dict(policy.NEW_FACT, roles=[*policy.NEW_FACT["roles"], role])]}
    refused, complete = _outcomes.locate_validation_issues([_issue("$.fact_types[0].roles[2].object_type")],
                                                           candidate, operations)
    assert complete and list(refused) == [1]


def test_r1_f3_two_changes_to_one_element_locate_nothing() -> None:
    first = _op("modify", policy._element("object_types", "note"), {"id": "note", "name": "Note"}, "m1",
                before={"id": "note"})
    second = _op("modify", policy._element("object_types", "note"), {"id": "note", "name": 3}, "m2",
                 before={"id": "note"})
    refused, complete = _outcomes.locate_validation_issues([_issue("$.object_types[id=note].name")],
                                                           {"object_types": [{"id": "note"}]}, (first, second))
    assert refused == {} and not complete


def test_r1_f4_an_added_operation_is_located() -> None:
    operation = _op("add", policy._element("operations", "ship"), {"id": "ship"}, "op-ship")
    refused, complete = _outcomes.locate_validation_issues(
        [_issue("$.operations[0]")], {"operations": [{"id": "ship"}]}, (ADD_OBJECT, operation))
    assert complete and list(refused) == [1]


def test_r1_f5_a_dependent_before_its_refused_role_player_is_dropped(tmp_path: Path) -> None:
    operations = (ADD_FACT, _invalid_object("region", "op-object"))
    error = _refused(tmp_path, operations)
    assert [row.verdict for row in error.outcome_refusal.operation_outcomes] == [
        "dropped-with", "refused-by-validation"]
    chain = (_op("add", policy._element("fact_types", "f2"), {"id": "f2", "roles": [{"object_type": "o2"}]}, "a"),
             _op("add", policy._element("object_types", "o2"), {"id": "o2", "subtype_of": ["o1"]}, "b"),
             _op("add", policy._element("object_types", "o1"), {"id": "o1"}, "c"))
    rows = _outcomes.outcomes(chain, {2: ("refused-by-validation", "x")})
    assert [row.verdict for row in rows] == ["dropped-with", "dropped-with", "refused-by-validation"]


def test_r1_f6_a_value_constraint_on_a_refused_object_type_is_dropped() -> None:
    value = {"type": "value", "object_type": "region", "values": ["north"], "source": "user-supplied"}
    operations = (_invalid_object("region", "op-object"),
                  _op("add", policy._constraint_locator(None, None, "value"), value, "op-value"))
    rows = _outcomes.outcomes(operations, {0: ("refused-by-validation", "x")})
    assert [row.verdict for row in rows] == ["refused-by-validation", "dropped-with"]


def test_r1_f7_an_include_analysis_refusal_writes_the_requested_report(tmp_path: Path) -> None:
    import shutil

    import test_mc3_evolution as mc3

    work = tmp_path / "workspace"
    shutil.copytree(mc3.CORPUS, work)
    result = mc3.preview(work, "repin-only.proposal.json", "--operation-outcomes",
                         "--outcome-report", str(work / "outcomes.json"))
    assert result.returncode == 3, result.stderr
    report = read_evolution_outcome_report(work / "outcomes.json", anchor=work, relative="outcomes.json")
    assert report.refusal.exit == 3 and len(report.operation_outcomes) >= 1


def test_r1_f8_id_paths_are_linear() -> None:
    n = 20_000
    operations = tuple(_op("add", policy._element("object_types", f"t{i}"),
                           {"id": f"t{i}", "name": f"T{i}", "kind": "value"}, f"op-{i}") for i in range(n))
    candidate = {"object_types": [operation.after for operation in operations]}
    issues = [_issue(f"$.object_types[id=t{i}]") for i in range(n)]
    start = time.perf_counter()
    refused, complete = _outcomes.locate_validation_issues(issues, candidate, operations)
    assert time.perf_counter() - start < 1.0
    assert complete and len(refused) == n


# --- Diff review r2 (notes/reviews/phase-GO2-r2/FINDINGS.md) -------------------------------------


def test_r2_f1_a_named_role_step_is_pinned_on_the_role_operation() -> None:
    role = {"object_type": "missing", "role_name": "region"}
    operations = (ADD_OBJECT, ADD_FACT,
                  _op("modify", RoleLocator(fact_type_id=HOST, role_name="region"), role, "op-role",
                      before=policy.NEW_FACT["roles"][1]))
    candidate = {"fact_types": [dict(policy.NEW_FACT, roles=[policy.NEW_FACT["roles"][0], role])]}
    refused, complete = _outcomes.locate_validation_issues(
        [_issue(f"$.fact_types[id={HOST}].roles[region]")], candidate, operations)
    assert complete and list(refused) == [2]


def test_r2_f2_a_sample_row_is_not_a_reference() -> None:
    fact = _op("add", policy._element("fact_types", "order_is_flagged"),
               {"id": "order_is_flagged", "reading": "{Order} is flagged",
                "roles": [{"object_type": "order", "role_name": "object_type"}],
                "sample_population": [{"object_type": "bad"}],
                "provenance": {"fact_type": "bad", "object_type": "bad"}}, "op-fact")
    assert _outcomes._needs(fact) == [("object_types", "order")]
    rows = _outcomes.outcomes((_invalid_object("bad", "op-bad"), fact), {0: ("refused-by-validation", "x")},
                              gates_not_run=("semantic-validation",))
    assert [row.verdict for row in rows] == ["refused-by-validation", "unassessed"]


def test_r2_f3_depends_on_is_a_dependency() -> None:
    broken = _op("add", policy._element("fact_types", "broken"), {"id": "broken", "roles": 1}, "op-broken")
    dependent = _op("add", policy._element("fact_types", "dependent"),
                    dict(policy.NEW_FACT, id="dependent", depends_on=["broken"]), "op-dependent")
    assert ("fact_types", "broken") in _outcomes._needs(dependent)
    rows = _outcomes.outcomes((broken, dependent), {0: ("refused-by-validation", "x")})
    assert [row.verdict for row in rows] == ["refused-by-validation", "dropped-with"]


def test_r2_f4_an_unlocated_constraint_issue_never_blames_its_host() -> None:
    good = {"type": "uniqueness", "roles": ["order"], "source": "user-supplied", "status": "confirmed"}
    bad = dict(good, source="not_a_source")
    host = {"id": "order_has_amount", "reading": "{Order} has {Amount} always", "constraints": [good]}
    locator = policy._constraint_locator("order_has_amount", None, "uniqueness")
    operations = (_op("modify", policy._element("fact_types", "order_has_amount"), host, "innocent-reading",
                      before=dict(host, reading="{Order} has {Amount}")),
                  _op("add", locator, bad, "bad-first"), _op("add", locator, good, "restore-good"),
                  _op("add", locator, bad, "bad-last"))
    candidate = {"fact_types": [dict(host, constraints=[bad])]}
    refused, complete = _outcomes.locate_validation_issues(
        [_issue("$.fact_types[0].constraints[0].source")], candidate, operations)
    assert refused == {} and not complete


def test_r2_f5_the_constraint_index_is_linear() -> None:
    n = 40_000
    body = dict(policy.NEW_CONSTRAINT)
    locator = policy._constraint_locator(HOST, None, body["type"])
    operation = _op("add", locator, body, "c")
    operations = [operation.model_copy(update={"operation_id": f"c{i}"}) for i in range(n)]
    start = time.perf_counter()
    index = _outcomes._Index(operations)
    assert time.perf_counter() - start < 1.0
    assert len(index.constraints[(HOST, _outcomes.canonical_sha256(body))]) == n
