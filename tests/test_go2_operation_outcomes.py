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

from gnd.evolve import EvolutionError, EvolutionOutcomeReport, read_evolution_outcome_report
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
