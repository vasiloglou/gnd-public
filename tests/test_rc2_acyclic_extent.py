"""RC2 (rule-check-adoption): the full extent of an acyclic violation, report version 15.

The corpus under tests/fixtures/rc2-acyclic is the phase's approval
instrument; its README tells each case and expected/ holds the answers.
"""

from __future__ import annotations

import json

import pytest
from jsonschema import Draft202012Validator
from support.cli_runner import run_main
from support.repository import REPO_ROOT

CORPUS = REPO_ROOT / "tests" / "fixtures" / "rc2-acyclic"
EXPECTED = CORPUS / "expected"
REPORT_SCHEMA = json.loads((REPO_ROOT / "src" / "gnd" / "report.schema.json").read_text())

CASES = {
    "two-groups": "models/graph.orm.yaml",
    "add-disjoint": "models/graph.orm.yaml",
    "self-loop": "models/graph.orm.yaml",
    "clean": "models/graph.orm.yaml",
    "composite": "models/graph-composite.orm.yaml",
}


def _exits() -> dict[str, int]:
    return json.loads((EXPECTED / "exits.json").read_text())


def _check(case: str, *flags: str):
    return run_main(["check", CASES[case], f"populations/{case}.pop.yaml", *flags], cwd=CORPUS)


def test_corpus_lists_every_case_once() -> None:
    assert set(_exits()) == {*CASES, "text-two-groups"}


@pytest.mark.parametrize("case", sorted(CASES))
def test_rule_ids_case_matches_answer_key(case: str) -> None:
    result = _check(case, "--rule-ids", "--format", "json")
    assert result.returncode == _exits()[case]
    assert result.stdout == (EXPECTED / f"{case}.json").read_bytes()
    Draft202012Validator(REPORT_SCHEMA).validate(json.loads(result.stdout))


@pytest.mark.parametrize("case", sorted(CASES))
def test_version_7_is_unchanged(case: str) -> None:
    result = _check(case, "--format", "json")
    assert result.returncode == _exits()[case]
    assert result.stdout == (EXPECTED / f"{case}.v7.json").read_bytes()


def test_text_case_matches_answer_key() -> None:
    result = _check("two-groups", "--rule-ids")
    assert result.returncode == _exits()["text-two-groups"]
    assert result.stdout == (EXPECTED / "two-groups.txt").read_bytes()


def test_a_disjoint_loop_leaves_the_existing_rows_in_place() -> None:
    """RC2-C2: every row of case 1 is still a row, in the same order, after case 2 adds a loop."""
    before = json.loads(_check("two-groups", "--rule-ids", "--format", "json").stdout)
    after = json.loads(_check("add-disjoint", "--rule-ids", "--format", "json").stdout)
    old = before["verdicts"][0]["offending_facts"]
    new = after["verdicts"][0]["offending_facts"]
    assert old and [row for row in new if row in old] == old
