"""Current CLI and trace guards over a separately owned public transition fixture."""

from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path
from typing import Any

import pytest

from gnd.cli import main

CORPUS = Path(__file__).parent / "fixtures" / "public-transition-trace" / "expense"

MODEL = CORPUS / "v2_expense.orm.yaml"


def _run(argv: list[str], capsys: pytest.CaptureFixture[str]) -> tuple[int, Any]:
    """Run one CLI invocation and return (exit code, parsed payload or None).

    ``_BandSafeParser`` RAISES ``SystemExit(64)`` on a usage error rather than
    returning it, so the argument-shape cases would otherwise error out of the
    harness instead of asserting. The process exit code is the same either way,
    which is the thing the corpus pins."""
    try:
        code = main([*argv, "--format", "json"])
    except SystemExit as exit_:
        code = int(exit_.code or 0)
    captured = capsys.readouterr()
    _refuse_vacuous_usage_error(argv, captured.err)
    _CURRENT_STDERR["last"] = _first_error_line(captured.err)
    try:
        return code, json.loads(captured.out)
    except json.JSONDecodeError:
        return code, None


_NEW_FLAGS = {
    "check": {"--pre", "--steps", "--post"},
    "validate": {"--trace"},
}

_VALUED_FLAGS = {"--pre", "--steps", "--post"}


def _new_flags_for(argv: list[str]) -> set[str]:
    return _NEW_FLAGS.get(argv[0] if argv else "", set())


def _refuse_vacuous_usage_error(argv: list[str], stderr: str) -> None:
    """A 64 for "unrecognized arguments" is not always the 64 a case pins.

    Before the transition arm exists, argparse returns 64 for every invocation
    using --pre/--steps/--post, so cases pinning a SEMANTIC refusal would go
    green while testing nothing. Scoped per subcommand, because `check --trace`
    is a case whose expected mechanism IS argparse refusing an unknown flag:
    --trace belongs to `validate` and offering it on `check` would be the
    defect. Once the check-arm flags are recognized, this never fires for them.
    """
    if "unrecognized arguments" not in stderr:
        return
    offending = [flag for flag in _new_flags_for(argv) if flag in stderr]
    if offending:
        raise AssertionError(
            f"exit 64 came from argparse not recognizing {offending}, not from the "
            f"refusal this case pins -- that flag is supposed to exist here.\n"
            f"argv: {argv}\nstderr: {stderr.strip()}"
        )


def _strip_new_flags(argv: list[str]) -> list[str]:
    """Remove this phase's flags AND the values they take."""
    out: list[str] = []
    skip = False
    for arg in argv:
        if skip:
            skip = False
            continue
        if arg in _new_flags_for(argv):
            skip = arg in _VALUED_FLAGS
            continue
        out.append(arg)
    return out


def _assert_case_discriminates(name: str, argv: list[str], exit_code: int) -> None:
    """The mutation rule: strip this phase's flags and the REFUSAL must change.

    A case that produces the same exit code AND the same error for the same
    invocation minus its new flags pins behaviour that predates the transition
    arm rather than the refusal it claims to test. Comparing the message as well
    as the code matters: several refusals share exit 64 and differ only in what
    they say, which is exactly what a caller reads.
    """
    stripped = _strip_new_flags(argv)
    if stripped == argv:
        return
    control_err = io.StringIO()
    try:
        with contextlib.redirect_stderr(control_err), contextlib.redirect_stdout(io.StringIO()):
            control = main([*stripped, "--format", "json"])
    except SystemExit as exit_:
        control = int(exit_.code or 0)
    except Exception as error:
        # A control invocation that raises is not a control invocation. The
        # reviewed version returned here, so a broken control counted as
        # discrimination -- a guard reporting green over exactly the gap it was
        # written to cover, which is the defect this file exists to prevent.
        raise AssertionError(
            f"{name}: the control invocation ({stripped}) raised "
            f"{type(error).__name__}: {error}. The mutation rule cannot decide "
            f"anything from a control that does not run."
        ) from error
    same_reason = _first_error_line(control_err.getvalue()) == _CURRENT_STDERR.get(name, "")
    assert not (control == exit_code and same_reason), (
        f"{name}: exit {exit_code} and the same error survive when this phase's "
        f"flags are stripped ({stripped}), so the case cannot discriminate -- it "
        f"pins behaviour that predates the transition arm."
    )


def _first_error_line(stderr: str) -> str:
    for line in stderr.strip().splitlines():
        if ": error:" in line:
            return line.split(": error:", 1)[1].strip()
    return stderr.strip().splitlines()[-1] if stderr.strip() else ""


_CURRENT_STDERR: dict[str, str] = {}


def _run_text(argv: list[str]) -> int:
    """Same, for the text-rendering assertions: --trace prints for a human."""
    try:
        return main(argv)
    except SystemExit as exit_:
        return int(exit_.code or 0)


CLI_CASES = json.loads((CORPUS / "cli-cases.json").read_text(encoding="utf-8"))["cases"]

TRACE = json.loads((CORPUS / "trace-expected.json").read_text(encoding="utf-8"))


def _resolve(argv: list[str]) -> list[str]:
    """Fixture argv is written relative to the corpus root, so a case reads as
    the reviewer wrote it rather than as a wall of absolute paths."""
    return [str(CORPUS / a) if (CORPUS / a).exists() else a for a in argv]


@pytest.mark.parametrize("case", CLI_CASES, ids=[c["name"] for c in CLI_CASES])
def test_cli_argument_shape(case: dict[str, Any], capsys: pytest.CaptureFixture[str]) -> None:
    argv = _resolve(case["argv"])
    code, _ = _run(argv, capsys)
    assert code == case["exit"], (
        f"{case['name']}: expected exit {case['exit']}, got {code}.\nWhy: {case['story']}"
    )
    _CURRENT_STDERR[case["name"]] = _CURRENT_STDERR.get("last", "")
    _assert_case_discriminates(case["name"], argv, code)
    capsys.readouterr()


def test_trace_happy_path_exit(capsys: pytest.CaptureFixture[str]) -> None:
    code, _ = _run(_resolve(TRACE["argv"]), capsys)
    assert code == TRACE["exit"]


@pytest.mark.parametrize("digest_key", ["prints_model_digest", "prints_operations_digest"])
def test_trace_prints_the_digest_a_steps_file_must_carry(
    digest_key: str, capsys: pytest.CaptureFixture[str]
) -> None:
    """--trace is the only shipped producer of operations_digest, which every
    steps.json is REQUIRED to carry (D6). Asserted per digest, not as one smoke
    test: a required field no surface emits is a format defect."""
    _run_text(_resolve(TRACE["argv"]))
    out = capsys.readouterr().out
    assert TRACE[digest_key] in out, (
        f"--trace did not print {digest_key} ({TRACE[digest_key]}).\nGot:\n{out}"
    )


@pytest.mark.parametrize(
    "entry",
    TRACE["compiled"],
    ids=[f"{e['operation']}:{e['obligation']}" for e in TRACE["compiled"]],
)
def test_trace_reports_each_compiled_obligation(
    entry: dict[str, Any], capsys: pytest.CaptureFixture[str]
) -> None:
    _run_text(_resolve(TRACE["argv"]))
    out = capsys.readouterr().out
    assert entry["obligation"] in out and entry["locator"] in out, (
        f"--trace did not report {entry['operation']}.{entry['obligation']} "
        f"at {entry['locator']}.\nWhy it compiles: {entry['why']}\nGot:\n{out}"
    )


@pytest.mark.parametrize(
    "case", TRACE["other_paths"], ids=[c["name"] for c in TRACE["other_paths"]]
)
def test_trace_other_paths(case: dict[str, Any], capsys: pytest.CaptureFixture[str]) -> None:
    """--trace cases discriminate on OUTPUT, not on exit code.

    The flag adds a report; it never changes a verdict, which is D6's whole
    point -- `validate` exits the same with it and without it, by design. So the
    exit-based mutation rule cannot apply here: what must differ is whether the
    trace appears. Each case therefore names the lines it requires or forbids,
    and the two together are what a wrong implementation fails.
    """
    argv = _resolve(case["argv"])
    code, _ = _run(argv, capsys)
    assert code == case["exit"], (
        f"{case['name']}: expected exit {case['exit']}, got {code}.\nWhy: {case['story']}"
    )
    capsys.readouterr()
    _run_text(argv)
    printed = capsys.readouterr().out
    for expected in case.get("expect_output") or []:
        assert expected in printed, (
            f"{case['name']}: --trace did not print {expected!r}.\n"
            f"Why: {case['story']}\nGot:\n{printed}"
        )
    for forbidden in case.get("expect_absent") or []:
        assert forbidden not in printed, (
            f"{case['name']}: --trace printed {forbidden!r} and must not.\n"
            f"Why: {case['story']}\nGot:\n{printed}"
        )
    assert case.get("expect_output") or case.get("expect_absent"), (
        f"{case['name']} asserts only an exit code, which `validate` produces "
        f"with or without --trace -- the case cannot discriminate"
    )


def test_model_loads_with_exactly_the_pinned_warnings() -> None:
    """The corpus model's warnings are load-bearing, not incidental: two
    op-dynamic-functional warnings are the only route to band 4, and the
    op-dynamic-untouched warning is what tells an author their dynamic rule can
    never fire (owner decision 2026-08-20, ledger 14)."""
    from gnd.model import load_model

    expected = [(w["rule_id"], w["operation"]) for w in TRACE["model_warnings"]]
    warnings = load_model(MODEL).warnings
    got = [(w.rule_id, w.path) for w in warnings]
    assert len(warnings) == len(expected), (
        f"expected {len(expected)} warnings, got {len(warnings)}: {got}"
    )
    for rule_id, operation in expected:
        assert any(rule_id == r and operation in str(path) for r, path in got), (
            f"missing warning {rule_id} on {operation}; got {got}"
        )


@pytest.mark.parametrize(
    "entry",
    TRACE["transition_only"],
    ids=[f"{e['operation']}:{e['obligation']}" for e in TRACE["transition_only"]],
)
def test_trace_reports_each_retained_obligation(
    entry: dict[str, Any], capsys: pytest.CaptureFixture[str]
) -> None:
    """The retained half matters as much as the compiled half: `transition-only`
    is not `skipped`, and a reader who cannot see WHY an obligation stayed
    per-step will assume the compiler missed it."""
    _run_text(_resolve(TRACE["argv"]))
    out = capsys.readouterr().out
    assert f"{entry['operation']}.{entry['obligation']}: transition-only:" in out, (
        f"--trace did not report {entry['operation']}.{entry['obligation']} as "
        f"retained. Expected reason: {entry['reason']}\nGot:\n{out}"
    )


@pytest.mark.parametrize("fact_type", sorted(TRACE["frame_modalities"]))
def test_trace_reports_each_fact_types_frame_modality(
    fact_type: str, capsys: pytest.CaptureFixture[str]
) -> None:
    """Asserted per fact type, not as one blob: the whole point of per-fact-type
    grading is that two fact types in one model can grade differently, and a
    single substring check over the whole block would pass while getting one of
    them wrong."""
    _run_text(_resolve(TRACE["argv"]))
    out = capsys.readouterr().out
    expected = TRACE["frame_modalities"][fact_type]
    line = next((row for row in out.splitlines() if row.strip().startswith(f"{fact_type}:")), "")
    assert line, f"--trace reported no frame modality for {fact_type}\nGot:\n{out}"
    assert f"{fact_type}: {expected}" in line, (
        f"--trace graded {fact_type} as {line.strip()!r}, expected {expected}"
    )


def test_trace_over_an_invalid_model_is_refused_by_layer_2_not_by_a_missing_file(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The exit-3 case must fail for its own reason.

    `trace-over-invalid-model` names a model that must be REJECTED, and a
    missing file also exits 3 -- so the case would pass while proving nothing if
    the fixture were absent, which is exactly what it did until the fixture was
    authored. Pinning the rule id is what makes the case discriminate.
    """
    case = next(c for c in TRACE["other_paths"] if c["name"] == "trace-over-invalid-model")
    code, payload = _run(_resolve(case["argv"]), capsys)
    assert code == 3
    assert isinstance(payload, dict), "no JSON payload on stdout"
    rule_ids = [issue.get("rule_id") for issue in payload.get("issues") or []]
    assert any(str(rule_id).startswith("semantic:") for rule_id in rule_ids), (
        f"exit 3 carried no layer-2 rule id, so the model was not REJECTED -- "
        f"most likely the fixture is missing. issues: {rule_ids}"
    )
    # The other half of the claim: --trace never reaches compilation when the
    # model does not load. Reporting obligations for a model that was refused
    # would be reporting on nothing.
    text_out = _run_text(_resolve(case["argv"]))
    printed = capsys.readouterr().out
    assert text_out == 3
    assert "TRACE" not in printed and "COMPILED OBLIGATIONS" not in printed, (
        f"--trace printed a report for a model layer 2 refused:\n{printed}"
    )
