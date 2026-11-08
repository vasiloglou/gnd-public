"""ROF2 (report-output-fidelity): text output for walks, admission and verify.

The corpus under tests/fixtures/rof2-projected-text is the phase's approval
instrument; its README tells each case and expected/ holds the answers. Every
case runs from the corpus directory. Written before the implementation: the
answer-key and no-report-line cases fail until ROF2 lands; the JSON pins, the
canaries and the corpus self-check pass now.
"""

from __future__ import annotations

import contextlib
import inspect
import io
import json
import re
import time

import pytest
from support.cli_runner import run_main
from support.repository import REPO_ROOT

from gnd import output, payloads
from gnd.commands import checking
from gnd.export import verification_service
from gnd.transition import TransitionReport

CORPUS = REPO_ROOT / "tests" / "fixtures" / "rof2-projected-text"
EXPECTED = CORPUS / "expected"
CASES = json.loads((EXPECTED / "exits.json").read_text())
APPLIED = sorted(case for case in CASES if not case.endswith("-unredacted"))
UNREDACTED = sorted(case for case in CASES if case.endswith("-unredacted"))
SECRET = re.compile(r"SECRET-[A-Z]+-\d+")
# Values that must show where the plain route prints them: a public nickname
# in a computed end state, a public customer code in an advisory message.
PUBLIC = {
    "transition-plan": "OPEN-NICK-333333",
    "admission": "customer 'c-1' has 2 facts",
    "verify": "customer 'c-1' has 2 facts",
}
# Secrets an unredacted text must show; a frame finding names no value, so the
# full walk is required to show none.
UNREDACTED_SECRETS = {
    "transition-plan-unredacted": {"SECRET-EMAIL-314159", "SECRET-EMAIL-271828"},
    "admission-unredacted": {"SECRET-EMAIL-271828"},
    "verify-unredacted": {"SECRET-EMAIL-271828"},
    "transition-full-unredacted": set(),
}


def _run(case: str, fmt: str):
    return run_main([*CASES[case]["argv"], "--format", fmt], cwd=CORPUS)


@pytest.mark.parametrize("case", sorted(CASES))
def test_json_route_is_unchanged(case: str) -> None:
    result = _run(case, "json")
    assert result.returncode == CASES[case]["exit"]
    assert result.stdout == (EXPECTED / "reports" / f"{case}.json").read_bytes()


@pytest.mark.parametrize("case", sorted(CASES))
def test_text_route_matches_answer_key(case: str) -> None:
    result = _run(case, "text")
    assert result.returncode == CASES[case]["exit"]
    assert result.stdout == (EXPECTED / f"{case}.txt").read_bytes()
    assert result.stderr == b""


@pytest.mark.parametrize("case", sorted(CASES))
def test_text_route_prints_no_report_line(case: str) -> None:
    # A computed end state is one JSON line of facts (D4); the report itself never is.
    for line in _run(case, "text").stdout.decode().splitlines():
        assert not line.startswith('{"schema_version"'), line


@pytest.mark.parametrize("case", APPLIED)
def test_applied_text_shows_no_secret(case: str) -> None:
    # Red on the base for transition-derived only: its JSON-as-text prints the step
    # bindings, and raise_score binds the ticket to ticket_score.ticket, a role the
    # model does not redact. The walk layout prints no bindings.
    text = _run(case, "text").stdout.decode()
    assert not SECRET.findall(text)
    if case in PUBLIC:
        assert PUBLIC[case] in text


@pytest.mark.parametrize("case", UNREDACTED)
def test_unredacted_text_shows_the_values(case: str) -> None:
    # Presence only: the exact lines are the answer key's to pin.
    text = _run(case, "text").stdout.decode()
    assert UNREDACTED_SECRETS[case] <= set(SECRET.findall(text))


def test_corpus_lists_every_case_once() -> None:
    stems = {path.stem for path in EXPECTED.glob("*.txt")}
    assert stems == set(CASES)
    assert {path.stem for path in (EXPECTED / "reports").glob("*.json")} == set(CASES)
    assert set(UNREDACTED_SECRETS) == set(UNREDACTED)


# --- the rest of the spec's section 8 (written with the implementation) -------------------

def _source(function) -> str:
    return inspect.getsource(function)


def _report(case: str) -> dict:
    return json.loads((EXPECTED / "reports" / f"{case}.json").read_text())


def _printed(function, payload) -> str:
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        function(payload)
    return buffer.getvalue()


@pytest.mark.parametrize(
    "block",
    [
        "not a mapping",
        {"evaluated": True, "steps": None},
        {"evaluated": True, "steps": ["a string", 7, None]},
        {"evaluated": True, "steps": [{"index": [1], "operation": {"x": 1}, "verdicts": "x"}]},
        {"evaluated": True, "frame_grading": [{}, {"operations": "abc"}, None]},
        {"evaluated": True, "frame_verdicts": [{"verdict": 10**5000, "locator": None}]},
        {"evaluated": True, "pre_snapshot": {"verdicts": [{"verdict": "fail"}]}},
        {"evaluated": True, "steps": [{"derived_changes": [{"added": 3, "removed": None}, "x"]}]},
    ],
)
@pytest.mark.parametrize("post", ["declared", "computed", None, 5])
def test_t11_walk_renderer_is_total(block, post) -> None:
    lines = output._projected_transition_lines({"post": post, "transition": block})
    assert all(isinstance(line, str) and "\n" not in line for line in lines)


def test_t11_unserializable_computed_post_prints_a_placeholder() -> None:
    nested: list = []
    nested.append(nested)
    for value in (float("nan"), {1j: 2}, nested):
        lines = output.render_transition_rows({"computed_post": value}, post="computed")
        assert lines[lines.index("COMPUTED POST") + 1] == "<non-text>"


def test_t11_issue_cap_and_other_envelopes() -> None:
    cap = payloads.MAX_POPULATION_ISSUES
    rows = [{"path": "p", "message": "m", "rule_id": "r"}] * (cap + 50)
    walk = output._projected_transition_lines(
        {"post": "computed", "issues": rows, "transition": {"evaluated": False}}
    )
    verify = output._projected_verify_lines({"command": "verify", "issues": rows})
    for lines in (walk, verify):
        assert len([line for line in lines if line.startswith("ERROR at")]) == cap
        assert any("50" in line for line in lines[cap:])
    assert output._projected_verify_lines({"error": {"message": "boom"}, "exit_code": 70}) == [
        "INTERNAL ERROR: boom"
    ]
    assert output.extraction_line(None) == "EXTRACTION: state="
    assert output.extraction_line({"state": "ran", "reason": [1]}) == (
        "EXTRACTION: state=ran (<non-text>)"
    )


def test_t11_a_walk_that_did_not_run_prints_only_its_preamble() -> None:
    payload = {"post": "declared", "warnings": [{"path": "w", "message": "m", "rule_id": "r"}],
               "transition": {"evaluated": False, "steps": [{"index": 1}]}}
    assert output._projected_transition_lines(payload) == ["WARNING at w: m [r]"]


def test_t12_plain_walk_text_is_an_adapter_over_the_one_renderer() -> None:
    assert "render_transition_rows(" in _source(output._print_transition)
    assert "render_transition_rows(" in _source(output._projected_transition_lines)
    for function in (
        output.render_transition_rows,
        output._projected_transition_lines,
        output._projected_verify_lines,
        output._print_projected_transition_text,
        output._print_projected_verify_text,
    ):
        text = _source(function)
        assert "TransitionReport" not in text and "CheckReport" not in text
        assert ".report" not in text
    assert "_print_projected_transition_text(mechanical_payload)" in _source(checking._cmd_transition)
    assert "_print_projected_check_text(mechanical_payload)" in _source(checking._cmd_check)
    assert "_print_projected_verify_text(payload)" in inspect.getsource(verification_service)
    assert "extraction_line(extraction)" in inspect.getsource(verification_service)


def test_t16_walk_renderer_is_linear_in_rows() -> None:
    verdicts = [
        {"locator": f"$.steps[{i}]", "verdict": "fail", "message": "m" * 40, "reason_code": None}
        for i in range(5)
    ]
    snapshot = {
        "verdicts": [
            {"constraint_ref": f"c[{i}]", "verdict": "fail", "modality": "alethic", "message": "m" * 40}
            for i in range(5)
        ]
    }
    steps = [
        {"index": i, "operation": "op", "verdicts": verdicts, "intermediate": snapshot}
        for i in range(10_000)
    ]
    frame = [{"locator": "$.post", "verdict": "warning", "message": "m" * 40}] * 5_000
    payload = {
        "post": "declared",
        "transition": {
            "evaluated": True, "pre_snapshot": snapshot, "pre_snapshot_verdicts": [],
            "steps": steps, "frame_grading": [], "frame_verdicts": frame, "post_snapshot": snapshot,
        },
    }
    started = time.perf_counter()
    lines = output._projected_transition_lines(payload)
    assert time.perf_counter() - started < 0.6
    assert len(lines) == 115_013


@pytest.mark.parametrize("case", sorted(CASES))
def test_t17_historical_entry_point_prints_the_route_text(case: str) -> None:
    report = _report(case)
    route = (
        output._print_projected_verify_text if report["command"] == "verify"
        else output._print_projected_transition_text if report.get("post")
        else output._print_projected_check_text
    )
    assert "redaction" in report  # every corpus report is projected
    assert _printed(output._print_projected_text, report) == _printed(route, report)


def test_t17_historical_entry_point_still_refuses_an_unprojected_payload() -> None:
    with pytest.raises(ValueError, match="redaction metadata"):
        output._print_projected_text({"command": "check"})


def test_t18_walk_lines_carry_the_reason_code_only_when_projected() -> None:
    unchecked = {"locator": "$.steps[1]", "verdict": "unchecked",
                 "message": "[REDACTED INSTANCE DETAIL]", "reason_code": "term:mod-zero"}
    snapshot = {"verdicts": [{"constraint_ref": "c[0]", "verdict": "unchecked", "modality": "alethic",
                              "message": "[REDACTED INSTANCE DETAIL]", "reason_code": "term:mod-zero"}]}
    block = {
        "evaluated": True, "pre_snapshot": snapshot, "pre_snapshot_verdicts": [unchecked],
        "steps": [{"index": 1, "operation": "op", "verdicts": [unchecked], "intermediate": snapshot}],
        "frame_verdicts": [unchecked], "post_snapshot": snapshot,
    }
    projected = output._projected_transition_lines({"post": "declared", "transition": block})
    suffixed = [line for line in projected if line.endswith(" [reason: term:mod-zero]")]
    assert len(suffixed) == 6  # pre snapshot, pre walk row, step row, intermediate, frame, post
    plain = output.render_transition_rows(block, post="declared")
    assert not [line for line in plain if "[reason:" in line]
    # A message that already carries the code is not suffixed twice.
    carried = {**unchecked, "message": "failed: term:mod-zero"}
    again = output._projected_transition_lines(
        {"post": "declared", "transition": {"evaluated": True, "frame_verdicts": [carried]}}
    )
    assert "  [unchecked] $.steps[1]: failed: term:mod-zero" in again


def test_plain_walk_text_is_unchanged_by_the_adapter() -> None:
    # The plain route over a report object prints the base renderer's layout
    # (the full byte-identity check is the plain transition suites in the gate).
    walk = TransitionReport.model_validate(
        {
            "pre_snapshot": {}, "pre_snapshot_verdicts": [], "steps": [], "frame_grading": [
                {"fact_type": "has_email", "modality": "deontic", "reason": "deontic-toucher",
                 "operations": ["add_email"]}
            ],
            "frame_verdicts": [], "post_snapshot": {},
        }
    )
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        output._print_transition(walk, [])
    assert buffer.getvalue() == (
        "PRE-STATE\nFRAME\n  has_email: deontic (deontic-toucher; add_email)\nPOST-STATE\n"
    )
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        output._print_transition(walk, [], computed_post={"facts": {}})
    assert buffer.getvalue() == (
        'PRE-STATE\nCOMPUTED POST\n{"facts": {}}\n'
        "FRAME COMPARISON: not applicable -- post is computed\nPOST-STATE\n"
    )
