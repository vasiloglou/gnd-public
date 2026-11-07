"""RC4 (rule-check-adoption): gnd check --allow-vacuous.

The corpus under tests/fixtures/rc4-allow-vacuous is the phase's approval
instrument; its README tells each case and expected/ holds the answers.
"""

from __future__ import annotations

import json

import pytest
from jsonschema import Draft202012Validator
from support.cli_runner import run_main
from support.repository import REPO_ROOT

CORPUS = REPO_ROOT / "tests" / "fixtures" / "rc4-allow-vacuous"
EXPECTED = CORPUS / "expected"
REPORT_SCHEMA = json.loads((REPO_ROOT / "src" / "gnd" / "report.schema.json").read_text())
MODEL = "models/graph.orm.yaml"
CASES = {
    "vacuous-only": [MODEL, "populations/vacuous-only.pop.yaml", "--allow-vacuous"],
    "vacuous-only-plain": [MODEL, "populations/vacuous-only.pop.yaml", "--rule-ids"],
    "fail-and-vacuous": [MODEL, "populations/fail-and-vacuous.pop.yaml", "--allow-vacuous"],
    "unchecked-and-vacuous": [MODEL, "populations/unchecked-and-vacuous.pop.yaml", "--allow-vacuous"],
    "baseline-head-vacuous": [MODEL, "populations/head-vacuous.head.pop.yaml",
                              "--baseline", "populations/head-vacuous.base.pop.yaml", "--allow-vacuous"],
    "baseline-base-vacuous": [MODEL, "populations/base-vacuous.head.pop.yaml",
                              "--baseline", "populations/base-vacuous.base.pop.yaml", "--allow-vacuous"],
}


def _exits() -> dict[str, int]:
    return json.loads((EXPECTED / "exits.json").read_text())


def test_corpus_lists_every_case_once() -> None:
    assert set(_exits()) == {*CASES, "text-vacuous-only", "conflict-populations"}


@pytest.mark.parametrize("case", sorted(CASES))
def test_case_matches_answer_key(case: str) -> None:
    result = run_main(["check", *CASES[case], "--format", "json"], cwd=CORPUS)
    assert result.returncode == _exits()[case]
    assert result.stdout == (EXPECTED / f"{case}.json").read_bytes()
    Draft202012Validator(REPORT_SCHEMA).validate(json.loads(result.stdout))


def test_text_case_matches_answer_key() -> None:
    result = run_main(["check", *CASES["vacuous-only"]], cwd=CORPUS)
    assert result.returncode == _exits()["text-vacuous-only"]
    assert result.stdout == (EXPECTED / "vacuous-only.txt").read_bytes()


def test_allow_vacuous_with_another_arm_is_a_usage_error() -> None:
    result = run_main(
        ["check", MODEL, "--populations", "populations", "--allow-vacuous", "--format", "json"], cwd=CORPUS,
    )
    assert result.returncode == _exits()["conflict-populations"]
    assert result.stdout == b""
    assert b"unrecognized arguments" not in result.stderr


# --- Direct tests (spec §8) -----------------------------------------------------------


@pytest.mark.parametrize("verdicts", [
    (), ("fail",), ("unchecked",), ("vacuous",), ("fail", "vacuous"), ("unchecked", "vacuous"),
    ("fail", "unchecked", "vacuous"),
])
@pytest.mark.parametrize("compared", [False, True])
def test_t1_the_option_turns_only_a_two_into_a_zero(verdicts, compared) -> None:
    from types import SimpleNamespace

    from gnd.checker import CheckReport, ConstraintVerdict, band

    # A truth table over band() alone: rows built without the checker's validation.
    rows = [
        ConstraintVerdict.model_construct(
            constraint_ref=f"constraints[{index}]", modality="alethic", verdict=verdict,
            reason_code="opaque-value" if verdict == "unchecked" else None,
        )
        for index, verdict in enumerate(verdicts)
    ]
    report = CheckReport.model_construct(
        verdicts=rows, derivations=[], snapshot_projection=None, phase1_trace=None, coverage={},
    )
    baseline = (
        SimpleNamespace(new_alethic_fail="fail" in verdicts, undecided_alethic="unchecked" in verdicts)
        if compared else None
    )
    plain = band(report, baseline)
    allowed = band(report, baseline, allow_vacuous=True)
    assert allowed == (0 if plain == 2 else plain)


@pytest.mark.parametrize("arm", [
    ["--populations", "populations"], ["--pre", "x", "--steps", "y", "--post", "z"],
    ["--anchors", "x", "--document", "y"], ["--composition", "x", "--sources", "y"],
    ["--admission"], ["--compiled-operations"],
])
def test_t2_allow_vacuous_excludes_every_other_arm(arm) -> None:
    result = run_main(["check", "missing.orm.yaml", "missing.pop.yaml", *arm, "--allow-vacuous"], cwd=CORPUS)
    assert result.returncode == 64
    assert result.stdout == b""
    assert b"--allow-vacuous applies to one plain snapshot check" in result.stderr


def test_t3_the_option_without_vacuous_verdicts_changes_only_its_own_key() -> None:
    plain = json.loads(run_main(["check", MODEL, "populations/fail-and-vacuous.pop.yaml", "--rule-ids",
                                 "--format", "json"], cwd=CORPUS).stdout)
    allowed = json.loads(run_main(["check", *CASES["fail-and-vacuous"], "--format", "json"], cwd=CORPUS).stdout)
    assert allowed.pop("allow_vacuous") is True and plain.pop("allow_vacuous") is False
    assert allowed == plain
