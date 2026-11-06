"""RC1 (rule-check-adoption): declared rule identity in gnd check, report version 15.

The corpus under tests/fixtures/rc1-rule-ids is the phase's approval instrument;
its README tells each case and expected/ holds the answers. Every case runs
from the corpus directory so the paths in the report are the ones written in
the README.
"""

from __future__ import annotations

import json

import pytest
from jsonschema import Draft202012Validator
from support.cli_runner import run_main
from support.repository import REPO_ROOT

CORPUS = REPO_ROOT / "tests" / "fixtures" / "rc1-rule-ids"
EXPECTED = CORPUS / "expected"
REPORT_SCHEMA = json.loads((REPO_ROOT / "src" / "gnd" / "report.schema.json").read_text())

FAIL = ["check", "models/components.orm.yaml", "populations/graph-fail.pop.yaml", "--rule-ids"]
JSON_CASES = {
    "declared-fail": [*FAIL, "--format", "json"],
    "positional-pass": [
        "check", "models/components-positional.orm.yaml", "populations/graph-pass.pop.yaml",
        "--rule-ids", "--format", "json",
    ],
    "derivation-plain": [
        "check", "models/exact-terms.orm.yaml", "populations/term-ok.pop.yaml",
        "--rule-ids", "--format", "json",
    ],
    "derivation-mod-zero": [
        "check", "models/exact-terms.orm.yaml", "populations/term-input.pop.yaml",
        "--rule-ids", "--format", "json",
    ],
}
REFUSAL_CASES = {
    "refuse-redaction": "models/exact-terms-redacted.orm.yaml",
    "refuse-temporal": "models/temporal.orm.yaml",
    "refuse-reference": "models/reference/model.orm.yaml",
}


def _exits() -> dict[str, int]:
    return json.loads((EXPECTED / "exits.json").read_text())


def _run(argv: list[str]):
    return run_main(argv, cwd=CORPUS)


def test_corpus_lists_every_case_once() -> None:
    cases = {*JSON_CASES, *REFUSAL_CASES, "text-declared-fail", "conflict-populations"}
    assert set(_exits()) == cases
    assert not (CORPUS / "populations" / "absent.pop.yaml").exists()


@pytest.mark.parametrize("case", sorted(JSON_CASES))
def test_json_case_matches_answer_key(case: str) -> None:
    result = _run(JSON_CASES[case])
    assert result.returncode == _exits()[case]
    assert result.stdout == (EXPECTED / f"{case}.json").read_bytes()
    Draft202012Validator(REPORT_SCHEMA).validate(json.loads(result.stdout))


def test_text_case_matches_answer_key() -> None:
    result = _run(FAIL)
    assert result.returncode == _exits()["text-declared-fail"]
    assert result.stdout == (EXPECTED / "declared-fail.txt").read_bytes()


@pytest.mark.parametrize("case", sorted(REFUSAL_CASES))
def test_refusal_precedes_population_load(case: str) -> None:
    expected = json.loads((EXPECTED / "refusals.json").read_text())[case]
    result = _run(
        ["check", REFUSAL_CASES[case], "populations/absent.pop.yaml", "--rule-ids", "--format", "json"]
    )
    assert result.returncode == _exits()[case]
    payload = json.loads(result.stdout)
    Draft202012Validator(REPORT_SCHEMA).validate(payload)
    for key in ("schema_version", "outcome", "exit_code"):
        assert payload[key] == expected[key]
    report = payload["report"] if "report_issue_rule_ids" in expected else payload
    if "report_schema_version" in expected:
        assert report["schema_version"] == expected["report_schema_version"]
    rule_ids = expected.get("issue_rule_ids", expected.get("report_issue_rule_ids"))
    assert [issue["rule_id"] for issue in report["issues"]] == rule_ids
    assert report["error"] is None


def test_rule_ids_with_another_arm_is_a_usage_error() -> None:
    result = _run(
        ["check", "models/components.orm.yaml", "--populations", "populations",
         "--rule-ids", "--format", "json"]
    )
    assert result.returncode == _exits()["conflict-populations"]
    assert result.stdout == b""
    # 64 must come from the deliberate conflict check, not from an unknown flag.
    assert b"unrecognized arguments" not in result.stderr
    assert b"--rule-ids" in result.stderr
