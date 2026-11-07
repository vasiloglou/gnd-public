"""ROF1 (report-output-fidelity): text output for redaction and temporal models.

The corpus under tests/fixtures/rof1-projected-text is the phase's approval
instrument; its README tells each case and expected/ holds the answers. Every
case runs from the corpus directory. Written before the implementation: the
text cases fail until ROF1 lands, the JSON pins and the two controls pass now.
"""

from __future__ import annotations

import json

import pytest
from support.cli_runner import run_main
from support.repository import REPO_ROOT

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
