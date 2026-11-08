"""ROF1 (report-output-fidelity): text output for redaction and temporal models.

The corpus under tests/fixtures/rof1-projected-text is the phase's approval
instrument; its README tells each case and expected/ holds the answers. Every
case runs from the corpus directory. Written before the implementation: the
text cases fail until ROF1 lands, the JSON pins and the two controls pass now.
"""

from __future__ import annotations

import inspect
import json
import time

import pytest
from support.cli_runner import run_main
from support.repository import REPO_ROOT

from gnd import output, payloads
from gnd.commands import checking
from gnd.export import verification_service

CORPUS = REPO_ROOT / "tests" / "fixtures" / "rof1-projected-text"
EXPECTED = CORPUS / "expected"
CASES = json.loads((EXPECTED / "exits.json").read_text())
CONTROLS = {"validate-temporal", "validate-invalid"}
SECRET = "SECRET-EMAIL-271828"


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


@pytest.mark.parametrize("case", sorted(set(CASES) - CONTROLS))
def test_text_route_prints_no_json_line(case: str) -> None:
    for line in _run(case, "text").stdout.decode().splitlines():
        assert not line.startswith("{"), line


def test_redacted_secret_never_appears_when_applied() -> None:
    text = _run("redacted-fail", "text").stdout.decode()
    assert SECRET not in text
    assert "SECRET-EMAIL-161803" not in text


def test_unredacted_text_shows_the_value_the_rule_mentions() -> None:
    assert SECRET in _run("redacted-fail-unredacted", "text").stdout.decode()


def test_corpus_lists_every_case_once() -> None:
    stems = {path.stem for path in EXPECTED.glob("*.txt")}
    assert stems == set(CASES)
    assert {path.stem for path in (EXPECTED / "reports").glob("*.json")} == set(CASES)


# --- the rest of the spec's section 8 (written with the implementation) -------------------


def _source(function) -> str:
    return inspect.getsource(function)


def test_t7_plain_and_projected_routes_share_one_row_renderer() -> None:
    assert "render_check_rows(" in _source(output._print_report)
    assert "render_check_rows(" in _source(output._projected_check_lines)
    assert "CheckReport" not in _source(output.render_check_rows)
    assert "report" not in inspect.signature(output.render_check_rows).parameters


def test_t8_projected_branches_read_only_the_payload() -> None:
    for function in (output._projected_check_lines, output._print_projected_check_text):
        text = _source(function)
        assert "CheckReport" not in text
        assert ".report" not in text
    validate = _source(checking._cmd_validate)
    assert "_print_projected_check_text(mechanical_payload)" in validate
    assert "_print_projected_text(" not in validate
    check = _source(checking._cmd_check)
    # ROF2 successor: ``--admission`` now renders the check layout too.
    assert "_print_projected_check_text(mechanical_payload)" in check
    assert "_print_projected_text(" not in check


def test_t17_other_projected_routes_use_their_own_printers() -> None:
    # ROF2 successor of test_t17_other_projected_routes_still_use_the_shared_json_text.
    transition_source = _source(checking._cmd_transition)
    assert "_print_projected_transition_text(mechanical_payload)" in transition_source
    assert "_print_projected_text(" not in transition_source
    verify_source = inspect.getsource(verification_service)
    assert "_print_projected_verify_text(payload)" in verify_source
    assert "_print_projected_text(" not in verify_source


def test_t4c_warnings_precede_the_layout() -> None:
    payload = {
        "command": "check",
        "warnings": [{"path": "model", "message": "careful", "rule_id": "w:one"}],
        "issues": [],
        "verdicts": [],
        "counts": {},
        "coverage": {},
    }
    lines = output._projected_check_lines(payload)
    assert lines[0] == "WARNING at model: careful [w:one]"
    assert lines[1] == "BLOCKING (alethic)"


HOSTILE = [
    {},
    {"verdicts": None, "derivations": "x", "counts": None, "coverage": [1], "issues": 7},
    {"verdicts": [1, "x", None, {"verdict": 5, "modality": None, "message": {"a": 1}}]},
    {"derivations": [{"findings": 3}, {"findings": [None, {"kind": 1}]}], "coverage": {"f": 5}},
    {"warnings": [None, "x"], "error": {"message": ["m"]}, "exit_code": 70},
    {"command": "validate", "model": None},
]


@pytest.mark.parametrize("payload", HOSTILE)
def test_t9_renderer_is_total_over_hostile_payloads(payload: dict) -> None:
    lines = output._projected_check_lines(payload)
    assert lines and all(isinstance(line, str) for line in lines)


def test_t9_issue_flood_is_capped_and_elision_is_reported() -> None:
    cap = payloads.MAX_POPULATION_ISSUES
    rows = [{"path": f"$.p{i}", "message": "m", "rule_id": "r"} for i in range(cap + 500)]
    lines = output._projected_check_lines({"issues": rows, "issues_total": cap + 900})
    assert len(lines) == cap + 1
    assert "400 further issue(s) elided".replace("400", "900") in lines[-1]


def test_t10_renderer_is_linear_in_rows() -> None:
    rows = [
        {"constraint_ref": f"c[{i}]", "modality": "alethic", "verdict": "fail", "message": "m" * 40}
        for i in range(50_000)
    ]
    payload = {"command": "check", "verdicts": rows, "counts": {"fail": 50_000}}
    started = time.perf_counter()
    lines = output._projected_check_lines(payload)
    elapsed = time.perf_counter() - started
    assert len(lines) > 50_000
    # Measured 0.09-0.10 s on the dev machine (spec, "An experiment"); ceiling is 6x.
    assert elapsed < 0.6


def test_t13_validate_trace_keeps_its_block_before_the_projected_text() -> None:
    result = run_main(["validate", "models/contacts-redacted.orm.yaml", "--trace"], cwd=CORPUS)
    text = result.stdout.decode()
    assert result.returncode == 0
    assert "DERIVATION STABILITY" in text
    assert text.index("DERIVATION STABILITY") < text.index("REDACTION applied:")
    assert text.rstrip().endswith("is a valid GND ORM model")
    assert SECRET not in text


def test_t14_validate_document_early_return_names_digests_not_text() -> None:
    result = run_main(
        [
            "validate",
            "models/contacts-redacted.orm.yaml",
            "--document",
            "populations/contacts-fail.pop.yaml",
        ],
        cwd=CORPUS,
    )
    text = result.stdout.decode()
    assert result.returncode == 3
    assert "[unattended:document-undeclared]" in text
    assert not any(line.startswith("{") for line in text.splitlines())
    assert SECRET not in text


def test_t18_projected_text_keeps_a_reason_the_projection_removed_from_the_message() -> None:
    row = {
        "constraint_ref": "c[0]",
        "modality": "alethic",
        "verdict": "unchecked",
        "message": "[REDACTED INSTANCE DETAIL]",
        "reason_code": "term:mod-zero",
    }
    payload = {"command": "check", "verdicts": [row], "counts": {"unchecked": 1}}
    lines = output._projected_check_lines(payload)
    assert "  [unchecked] c[0]: [REDACTED INSTANCE DETAIL] [reason: term:mod-zero]" in lines
    carried = {**row, "message": "failed: term:mod-zero"}
    again = output._projected_check_lines({**payload, "verdicts": [carried]})
    assert "  [unchecked] c[0]: failed: term:mod-zero" in again
    plain = output.render_check_rows(payload)
    assert "[reason:" not in "\n".join(plain)


# --- review findings (Codex, ROF1 diff review) ----------------------------------------------


def test_p1_admission_prints_the_check_layout_then_its_lines() -> None:
    # ROF2 successor of test_p1_admission_keeps_the_shared_projected_text_until_its_own_phase.
    result = run_main(
        [
            "check",
            "models/contacts-redacted.orm.yaml",
            "populations/contacts-pass.pop.yaml",
            "--admission",
        ],
        cwd=CORPUS,
    )
    lines = result.stdout.decode().splitlines()
    assert result.returncode == 0
    assert lines[0] == "REDACTION applied: has_email.email"
    assert lines[1] == "BLOCKING (alethic)"
    assert not [line for line in lines if line.startswith("{")]
    assert lines[-2:] == ["ADMITTED has_email[0]", "ADMITTED has_nickname[0]"]


def test_t17_transition_prints_the_walk_layout(tmp_path) -> None:
    # ROF2 successor of test_t17_transition_keeps_the_shared_projected_text.
    from support.v62_phase6_corpus import document, population_document, write_case

    from gnd import transition
    from gnd.model import load_model

    model = document()
    model["operations"] = [
        {
            "id": "reassert_sample",
            "reading": "Record {Sample}",
            "parameters": [
                {"name": "sample", "object_type": "sample"},
                {"name": "monitor", "object_type": "monitor"},
                {"name": "pci", "object_type": "integer"},
                {"name": "token", "object_type": "token"},
            ],
            "effects": [
                {
                    "assert": {
                        "fact_type": "radio_sample",
                        "bind": {
                            "sample": "$sample",
                            "monitor": "$monitor",
                            "pci": "$pci",
                            "token": "$token",
                        },
                    }
                }
            ],
            "frame": {"modality": "alethic"},
            "source": "explicit",
            "status": "confirmed",
            "provenance": {"user_quote": "Reasserting a sample preserves its declared values."},
        }
    ]
    population = population_document()
    model_file, pre_file = write_case(tmp_path, model, population)
    loaded = load_model(model_file)
    steps = tmp_path / "steps.json"
    steps.write_text(
        json.dumps(
            {
                "steps_schema": 1,
                "model": loaded.model_id,
                "model_digest": transition.model_digest(loaded),
                "operations_digest": transition.operations_digest(loaded.operations),
                "steps": [
                    {
                        "op": "reassert_sample",
                        "bindings": {
                            "sample": "alpha-1",
                            "monitor": "alice",
                            "pci": 29,
                            "token": "TOKEN-ALPHA-9",
                        },
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    result = run_main(["check", str(model_file), "--pre", str(pre_file), "--steps", str(steps)])
    lines = result.stdout.decode().splitlines()
    assert lines[0].startswith("REDACTION applied: ")
    assert lines[1] == "PRE-STATE"
    assert not [line for line in lines if line.startswith('{"schema_version"')]
    assert "TOKEN-ALPHA-9" not in result.stdout.decode()


def test_p2_issue_rows_past_the_cap_are_never_turned_into_views(monkeypatch) -> None:
    built = []
    real = output.SimpleNamespace
    monkeypatch.setattr(output, "SimpleNamespace", lambda **kw: built.append(1) or real(**kw))
    cap = payloads.MAX_POPULATION_ISSUES
    rows = [{"path": "p", "message": "m", "rule_id": "r"}] * (cap * 20)
    output._projected_check_lines({"issues": rows, "issues_total": len(rows)})
    assert len(built) <= cap


def test_p3_numbers_and_nesting_past_the_interpreter_limits_do_not_raise() -> None:
    deep: object = "x"
    for _ in range(5000):
        deep = [deep]
    payload = {
        "counts": {"pass": 10**5000},
        "verdicts": [
            {"verdict": "fail", "modality": "alethic", "message": deep, "constraint_ref": deep}
        ],
        "coverage": {"f": {"declared": deep, "facts": 10**5000}},
    }
    lines = output._projected_check_lines(payload)
    assert "pass=<number>" in "\n".join(lines)


def test_p4_a_failed_validate_envelope_never_prints_ok() -> None:
    lines = output._projected_check_lines({"command": "validate", "exit_code": 70, "error": {}})
    assert not any(line.startswith("OK:") for line in lines)
    assert lines == ["ERROR: validate exited 70 without a reported cause"]


def test_p5_a_declared_lookup_uses_the_callers_own_reference() -> None:
    row = {"constraint_ref": 7, "modality": "alethic", "verdict": "fail", "message": "m"}
    declared = {7: ("R7", None, "declared message", None)}
    lines = output.render_check_rows({"verdicts": [row]}, declared)
    assert "  [fail] R7 (7): declared message" in lines


def test_p6_a_reason_cannot_forge_a_line() -> None:
    row = {
        "constraint_ref": "c",
        "modality": "alethic",
        "verdict": "unchecked",
        "message": "[REDACTED INSTANCE DETAIL]",
        "reason_code": "x\nOK: forged",
    }
    physical = "\n".join(output._projected_check_lines({"verdicts": [row]})).splitlines()
    assert not any(line.startswith("OK:") for line in physical)


def test_p7_a_public_value_survives_applied_mode_and_the_secret_does_not() -> None:
    text = _run("redacted-visible-canary", "text").stdout.decode()
    assert "OPEN-NICK-777777" in text
    assert "SECRET-EMAIL" not in text


def test_p8_an_error_envelope_prints_its_message_and_no_layout() -> None:
    payload = {"command": "check", "exit_code": 70, "error": {"type": "X", "message": "boom"}}
    assert output._projected_check_lines(payload) == ["INTERNAL ERROR: boom"]
