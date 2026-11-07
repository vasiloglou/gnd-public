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
