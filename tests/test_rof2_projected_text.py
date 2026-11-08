"""ROF2 (report-output-fidelity): text output for walks, admission and verify.

The corpus under tests/fixtures/rof2-projected-text is the phase's approval
instrument; its README tells each case and expected/ holds the answers. Every
case runs from the corpus directory. Written before the implementation: the
answer-key and no-report-line cases fail until ROF2 lands; the JSON pins, the
canaries and the corpus self-check pass now.
"""

from __future__ import annotations

import json
import re

import pytest
from support.cli_runner import run_main
from support.repository import REPO_ROOT

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
