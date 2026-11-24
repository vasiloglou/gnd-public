"""GO5: one summary per growth round (#227).

Spec: .gnd-planning/milestones/growth-round-outcomes/notes/phase-GO5-spec.md (§8, T1-T8). The
known-mix round's expected counts are stated in tests/fixtures/round-summary/README.md, from how
the fixture was built, not from the code.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import pytest
import test_evolve_additive_policy as policy
import test_go2_operation_outcomes as go2
import test_unattended_model_growth_acceptance as acceptance
from support.cli_runner import run_main

from gnd.discover.narrow import narrow_proposal
from gnd.evolve import (
    read_evolution_outcome_report,
    read_evolution_preview,
    read_evolution_proposal,
    read_evolution_record,
)
from gnd.evolve.summary import RoundFileError, read_round_file, round_summary

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "round-summary"


def _round_file(tmp_path: Path, name: str = "round.json", **fields: Any) -> Path:
    document = {"schema_version": 1, "round": "r1", "document": "round-1.txt", **fields}
    path = tmp_path / name
    path.write_text(json.dumps(document), encoding="utf-8")
    return path


def _record(paths: dict[str, Path], proposal: Any) -> Any:
    return read_evolution_record(paths["records"] / proposal.proposal_id / "record.json")


# --- T1 (GO5-C1): three rounds of the acceptance replay ---------------------------------------------


def test_t1_three_replay_rounds_add_up(tmp_path: Path) -> None:
    ws = acceptance._workspace(tmp_path / "ws")
    for n, reply in enumerate(acceptance.ROUNDS, 1):
        raw = acceptance._document(n)
        acceptance._declare(ws["model"], raw, f"round-{n}.txt")
        paths = acceptance._write_proposal(ws, f"r{n}", acceptance._operations(reply, raw))
        result = run_main([*policy._preview_argv(paths, "--policy", "additive", "--shape-report"),
                           "--operation-outcomes"])
        assert result.returncode == 0, result.stderr
        assert run_main(policy._apply_argv(paths, "--policy", "additive")).returncode == 0
        proposal = read_evolution_proposal(paths["proposal"])
        preview = read_evolution_preview(paths["preview"])
        summary = round_summary(read_round_file(_round_file(tmp_path, f"round-{n}.json", round=f"r{n}")),
                                proposal=proposal, preview=preview, record=_record(paths, proposal))
        assert summary.proposed["total"] == len(proposal.operations) == sum(summary.outcomes.values())
        assert summary.outcomes == {"admitted": len(proposal.operations)}
        added = [op.locator.element_id for op in proposal.operations
                 if getattr(op.locator, "collection", None) in ("object_types", "fact_types")]
        assert sorted(summary.added["object_types"] + summary.added["fact_types"]) == sorted(added)
        assert summary.shape_matches == len(preview.shape_matches)


# --- T2 (GO5-C1): the known-mix round, counts from the fixture's README ----------------------------


def test_t2_the_known_mix_round(tmp_path: Path) -> None:
    expected = json.loads((FIXTURES / "known-mix.expected.json").read_text(encoding="utf-8"))
    refused = go2._op("add", policy._constraint_locator(policy.POPULATED, None, "mandatory"),
                      policy.NEW_CONSTRAINT, "op-refused")
    same_players = go2._op("add", policy._element("fact_types", "customer_returns_order_via_channel"),
                           {"id": "customer_returns_order_via_channel",
                            "reading": "{Customer} returns {Order} via {Channel}",
                            "roles": [{"object_type": "customer", "role_name": "customer"},
                                      {"object_type": "order", "role_name": "order"},
                                      {"object_type": "channel", "role_name": "channel"}]}, "op-same-players")
    operations = (go2.ADD_OBJECT, refused, same_players)
    proposal = policy._proposal(go2.TEXT, operations)
    preview = policy._service(tmp_path, go2.TEXT).preview(proposal, policy="additive", shape_report=True,
                                                          operation_outcomes=True)
    round_file = read_round_file(FIXTURES / "known-mix.round.json")
    summary = round_summary(round_file, proposal=proposal, preview=preview)
    observed = {"proposed": summary.proposed["total"], "outcomes": summary.outcomes,
                "host_drops": len(summary.host_drops), "reused": sum(map(len, summary.reused.values())),
                "added": sum(map(len, summary.added.values())), "shape_matches": summary.shape_matches}
    assert observed == expected


def test_t2_a_dropped_with_row_is_counted(tmp_path: Path) -> None:
    broken = dict(policy.NEW_FACT, roles=[{"object_type": "nowhere", "role_name": "region"},
                                          {"object_type": "order", "role_name": "order"}])
    operations = (go2.ADD_OBJECT, go2._op("add", policy._element("fact_types", go2.HOST), broken, "op-fact"),
                  go2._constraint(status="confirmed"))
    proposal = policy._proposal(go2.TEXT, operations)
    error = go2._refused(tmp_path, operations)
    report = error.outcome_refusal.report(exit_code=3, message=str(error))
    summary = round_summary(read_round_file(_round_file(tmp_path)), proposal=proposal, report=report)
    assert summary.outcomes == {"dropped-with": 1, "refused-by-validation": 1, "unassessed": 1}
    assert summary.added == {"object_types": (), "fact_types": (), "constraints": ()}


# --- T3 (GO5-C1b): applied or not; narrowed then applied ---------------------------------------------


def test_t3_previewed_and_not_applied_adds_nothing(tmp_path: Path) -> None:
    paths = policy._cli_workspace(tmp_path / "ws", (go2.ADD_OBJECT, go2.ADD_FACT))
    assert run_main([*policy._preview_argv(paths), "--operation-outcomes"]).returncode == 0
    proposal, preview = read_evolution_proposal(paths["proposal"]), read_evolution_preview(paths["preview"])
    summary = round_summary(read_round_file(_round_file(tmp_path)), proposal=proposal, preview=preview)
    assert summary.added == {"object_types": (), "fact_types": (), "constraints": ()}
    assert run_main(policy._apply_argv(paths)).returncode == 0
    applied = round_summary(read_round_file(_round_file(tmp_path)), proposal=proposal, preview=preview,
                            record=_record(paths, proposal))
    assert applied.added == {"object_types": ("region",), "fact_types": (go2.HOST,), "constraints": ()}


def test_t3_a_narrowed_round_reports_the_narrowed_additions(tmp_path: Path) -> None:
    operations = (go2.ADD_OBJECT, go2.ADD_FACT, go2._invalid_object("bad", "op-bad"))
    paths = policy._cli_workspace(tmp_path / "ws", operations)
    report_path = paths["workspace"] / "outcomes.json"
    assert run_main([*policy._preview_argv(paths), "--operation-outcomes",
                     "--outcome-report", str(report_path)]).returncode == 3
    original = read_evolution_proposal(paths["proposal"])
    narrowed, _reasons = narrow_proposal(original, read_evolution_outcome_report(report_path))
    paths["proposal"].write_text(json.dumps(narrowed.model_dump(mode="json")), encoding="utf-8")
    assert run_main([*policy._preview_argv(paths), "--operation-outcomes"]).returncode == 0
    assert run_main(policy._apply_argv(paths)).returncode == 0
    proposal, preview = read_evolution_proposal(paths["proposal"]), read_evolution_preview(paths["preview"])
    summary = round_summary(read_round_file(_round_file(tmp_path)), proposal=proposal, preview=preview,
                            record=_record(paths, proposal))
    assert summary.narrowed_from == original.proposal_id
    assert summary.added["object_types"] == ("region",) and "bad" not in summary.added["object_types"]


# --- T4 (GO5-C2): two empty rounds that differ only in what they reused ------------------------------


def test_t4_an_empty_round_and_a_covered_round_differ(tmp_path: Path) -> None:
    empty = round_summary(read_round_file(_round_file(tmp_path, "empty.json")))
    covered = round_summary(read_round_file(_round_file(
        tmp_path, "covered.json", reused=[{"collection": "fact_types", "id": "customer_places_order"}])))
    assert empty != covered
    assert empty.proposed == {"total": 0, "by_kind": {}, "by_collection": {}}
    assert sum(map(len, empty.reused.values())) == 0 and sum(map(len, empty.added.values())) == 0
    assert covered.reused["fact_types"] == ("customer_places_order",)


# --- T5 (GO5-C3): the host's drops ------------------------------------------------------------------


def test_t5_host_drops_are_reported_as_the_hosts(tmp_path: Path) -> None:
    drops = [{"kind": "fact_type", "id": "policy_has_note", "reason": "no constraint and no open question"}]
    summary = round_summary(read_round_file(_round_file(tmp_path, host_drops=drops)))
    assert [drop.model_dump() for drop in summary.host_drops] == drops


# --- T6: hostile round files and unbound artifacts, refused by name, in order ------------------------


@pytest.mark.parametrize("payload", [
    b"{" + b" " * (2 * 1024 * 1024) + b"}",
    b'{"schema_version": NaN}',
    b'{"schema_version": 1, "round": "r", "document": "d", "x": ' + b"[" * 10_000 + b"]" * 10_000 + b"}",
    b'{"schema_version": ' + b"9" * 5_000 + b"}",
    b'{"schema_version": 1, "round": "r", "document": "d", "extra": 1}',
    b'{"schema_version": 1, "schema_version": 1, "round": "r", "document": "d"}',
    (b'{"schema_version": 1, "round": "r", "document": "d", "reused": [{"collection": "fact_types", "id": "a"},'
     b' {"collection": "fact_types", "id": "a"}]}'),
], ids=["oversize", "nan", "deep", "long-int", "extra-key", "duplicate-key", "duplicate-reused"])
def test_t6_a_hostile_round_file_is_refused_by_name(tmp_path: Path, payload: bytes) -> None:
    path = tmp_path / "round.json"
    path.write_bytes(payload)
    with pytest.raises(RoundFileError):
        read_round_file(path)


def test_t6_unbound_artifacts_are_refused_in_order(tmp_path: Path) -> None:
    round_file = read_round_file(_round_file(tmp_path))
    a = policy._cli_workspace(tmp_path / "a", (go2.ADD_OBJECT,))
    b = policy._cli_workspace(tmp_path / "b", (go2.ADD_OBJECT, go2.ADD_FACT))
    for paths in (a, b):
        assert run_main(policy._preview_argv(paths)).returncode == 0
    proposal_a, preview_a = read_evolution_proposal(a["proposal"]), read_evolution_preview(a["preview"])
    preview_b = read_evolution_preview(b["preview"])
    with pytest.raises(RoundFileError, match="reads a RoundFile"):
        round_summary({"schema_version": 1}, proposal=proposal_a)
    with pytest.raises(RoundFileError, match="needs its proposal"):
        round_summary(round_file, preview=preview_a)
    with pytest.raises(RoundFileError, match="not this proposal's"):
        round_summary(round_file, proposal=proposal_a, preview=preview_b)
    assert run_main(policy._apply_argv(b)).returncode == 0
    record_b = _record(b, read_evolution_proposal(b["proposal"]))
    with pytest.raises(RoundFileError, match="not this preview's"):
        round_summary(round_file, proposal=proposal_a, preview=preview_a, record=record_b)


# --- T7: linear -----------------------------------------------------------------------------------------


def test_t7_ten_thousand_rows() -> None:
    from gnd.evolve.summary import RoundFile

    rows = [{"collection": "object_types", "id": f"t{i}"} for i in range(10_000)]
    drops = [{"kind": "fact_type", "id": f"f{i}", "reason": "r"} for i in range(10_000)]
    round_file = RoundFile.model_validate({"schema_version": 1, "round": "r", "document": "d",
                                           "reused": rows, "host_drops": drops})
    start = time.perf_counter()
    summary = round_summary(round_file)
    assert time.perf_counter() - start < 1.0
    assert len(summary.reused["object_types"]) == 10_000 and len(summary.host_drops) == 10_000


# --- The command: gnd evolve summary ------------------------------------------------------------------


def test_the_command_prints_the_summary_and_refuses_by_name(tmp_path: Path) -> None:
    paths = policy._cli_workspace(tmp_path / "ws", (go2.ADD_OBJECT, go2.ADD_FACT))
    assert run_main([*policy._preview_argv(paths), "--operation-outcomes"]).returncode == 0
    assert run_main(policy._apply_argv(paths)).returncode == 0
    proposal = read_evolution_proposal(paths["proposal"])
    record = paths["records"] / proposal.proposal_id / "record.json"
    round_path = _round_file(tmp_path)
    result = run_main(["evolve", "summary", str(round_path), "--proposal", str(paths["proposal"]),
                       "--preview", str(paths["preview"]), "--record", str(record)])
    assert result.returncode == 0, result.stderr
    document = json.loads(result.stdout)
    assert document["kind"] == "gnd-round-summary" and document["outcomes"] == {"admitted": 2}
    assert document["added"]["fact_types"] == [go2.HOST]
    refused = run_main(["evolve", "summary", str(round_path), "--record", str(record)])
    assert refused.returncode == 3 and b"needs its proposal" in refused.stderr and not refused.stdout
    both = run_main(["evolve", "summary", str(round_path), "--preview", "a", "--outcome-report", "b"])
    assert both.returncode == 64 and b"not allowed with argument --preview" in both.stderr


# --- Diff review r1 (notes/reviews/phase-GO3-GO5-r1/FINDINGS.md) ----------------------------------


def _report_with(proposal: Any, rows: tuple[Any, ...], message: str = "refused") -> Any:
    from gnd.evolve import CommittedText, EvolutionOutcomeReport, OutcomeRefusal

    return EvolutionOutcomeReport(
        proposal_id=proposal.proposal_id, proposal_sha256=proposal.proposal_sha256,
        before_model=CommittedText.from_text(go2.TEXT, media_type="application/yaml"),
        refusal=OutcomeRefusal(gate="policy", exit=3, message=message), operation_outcomes=rows)


def test_r1_f2_outcomes_that_do_not_cover_the_proposal_are_refused(tmp_path: Path) -> None:
    proposal = policy._proposal(go2.TEXT, (go2.ADD_OBJECT, go2.ADD_FACT))
    with pytest.raises(RoundFileError, match="not the proposal's operations"):
        round_summary(read_round_file(_round_file(tmp_path)), proposal=proposal, report=_report_with(proposal, ()))


def test_r1_f4_bindings_name_every_artifact_read(tmp_path: Path) -> None:
    from gnd.evolve import OperationOutcome

    proposal = policy._proposal(go2.TEXT, (go2.ADD_OBJECT,))
    rows = (OperationOutcome(operation_index=0, operation_id="op-object",
                             reference=go2.ADD_OBJECT.locator.reference(), verdict="unassessed",
                             gates_not_run=("policy",)),)
    round_file = read_round_file(_round_file(tmp_path))
    one = round_summary(round_file, proposal=proposal, report=_report_with(proposal, rows, "one"))
    two = round_summary(round_file, proposal=proposal, report=_report_with(proposal, rows, "two"))
    assert one.bindings["outcome_report_sha256"] != two.bindings["outcome_report_sha256"]
    assert set(one.bindings) == {"round_file_sha256", "proposal_sha256", "outcome_report_sha256"}
    paths = policy._cli_workspace(tmp_path / "ws", (go2.ADD_OBJECT,))
    assert run_main(policy._preview_argv(paths)).returncode == 0
    assert run_main(policy._apply_argv(paths)).returncode == 0
    applied = read_evolution_proposal(paths["proposal"])
    record = _record(paths, applied)
    summary = round_summary(round_file, proposal=applied, preview=read_evolution_preview(paths["preview"]),
                            record=record)
    from gnd.evolve import canonical_sha256

    assert summary.bindings["record_sha256"] == canonical_sha256(record)
    assert summary.bindings["preview_sha256"] == record.preview_sha256


def test_r1_f5_host_text_is_reported_verbatim(tmp_path: Path) -> None:
    drops = [{"kind": " fact_type", "id": "x ", "reason": "  host reason\n"}]
    summary = round_summary(read_round_file(_round_file(tmp_path, host_drops=drops, document=" round 1.txt ")))
    assert [drop.model_dump() for drop in summary.host_drops] == drops and summary.document == " round 1.txt "
