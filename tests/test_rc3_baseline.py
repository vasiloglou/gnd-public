"""RC3 (rule-check-adoption): gnd check --baseline, new vs standing violations.

The corpus under tests/fixtures/rc3-baseline is the phase's approval
instrument; its README tells each case and expected/ holds the answers.
"""

from __future__ import annotations

import json

import pytest
from jsonschema import Draft202012Validator
from support.cli_runner import run_main
from support.repository import REPO_ROOT

CORPUS = REPO_ROOT / "tests" / "fixtures" / "rc3-baseline"
EXPECTED = CORPUS / "expected"
REPORT_SCHEMA = json.loads((REPO_ROOT / "src" / "gnd" / "report.schema.json").read_text())
JSON_CASES = ("standing-only", "mixed", "rowless-new", "head-vacuous", "base-unchecked")


def _exits() -> dict[str, int]:
    return json.loads((EXPECTED / "exits.json").read_text())


def _baseline(case: str, *flags: str, model: str = "models/graph.orm.yaml"):
    return run_main(
        ["check", model, f"populations/{case}.head.pop.yaml",
         "--baseline", f"populations/{case}.base.pop.yaml", *flags],
        cwd=CORPUS,
    )


def test_corpus_lists_every_case_once() -> None:
    assert set(_exits()) == {*JSON_CASES, "text-mixed", "bad-base", "refuse-derivation",
                             "refuse-temporal", "conflict-populations"}
    assert not (CORPUS / "populations" / "absent.pop.yaml").exists()


@pytest.mark.parametrize("case", JSON_CASES)
def test_baseline_case_matches_answer_key(case: str) -> None:
    result = _baseline(case, "--format", "json")
    assert result.returncode == _exits()[case]
    assert result.stdout == (EXPECTED / f"{case}.json").read_bytes()
    Draft202012Validator(REPORT_SCHEMA).validate(json.loads(result.stdout))


def test_text_case_matches_answer_key() -> None:
    result = _baseline("mixed")
    assert result.returncode == _exits()["text-mixed"]
    assert result.stdout == (EXPECTED / "mixed.txt").read_bytes()


def test_an_ill_formed_base_is_named() -> None:
    expected = json.loads((EXPECTED / "refusals.json").read_text())["bad-base"]
    result = _baseline("bad-base", "--format", "json")
    assert result.returncode == _exits()["bad-base"]
    payload = json.loads(result.stdout)
    Draft202012Validator(REPORT_SCHEMA).validate(payload)
    for key in ("schema_version", "outcome", "exit_code", "population"):
        assert payload[key] == expected[key]
    assert [[issue["path"], issue["rule_id"]] for issue in payload["issues"]] == expected["issues"]


@pytest.mark.parametrize(("case", "model"), [
    ("refuse-derivation", "models/derivations.orm.yaml"),
    ("refuse-temporal", "models/temporal.orm.yaml"),
])
def test_refusal_precedes_both_population_loads(case: str, model: str) -> None:
    expected = json.loads((EXPECTED / "refusals.json").read_text())[case]
    result = run_main(
        ["check", model, "populations/absent.pop.yaml", "--baseline", "populations/absent.pop.yaml",
         "--format", "json"],
        cwd=CORPUS,
    )
    assert result.returncode == _exits()[case]
    payload = json.loads(result.stdout)
    Draft202012Validator(REPORT_SCHEMA).validate(payload)
    for key in ("schema_version", "outcome", "exit_code"):
        assert payload[key] == expected[key]
    assert [issue["rule_id"] for issue in payload["issues"]] == expected["issue_rule_ids"]
    assert payload["error"] is None


def test_baseline_with_another_arm_is_a_usage_error() -> None:
    result = run_main(
        ["check", "models/graph.orm.yaml", "--populations", "populations",
         "--baseline", "populations/mixed.base.pop.yaml", "--format", "json"],
        cwd=CORPUS,
    )
    assert result.returncode == _exits()["conflict-populations"]
    assert result.stdout == b""
    assert b"unrecognized arguments" not in result.stderr
