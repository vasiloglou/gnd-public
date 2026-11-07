"""FU1 (rule-check-followups): version-7 derivation reasons (issue 113).

The corpus under tests/fixtures/fu1-term-reasons is the phase's approval
instrument; its README tells each case and expected/answers.json holds the
answers.
"""

from __future__ import annotations

import json

import jsonschema
import pytest
from support.cli_runner import run_main
from support.repository import REPO_ROOT

CORPUS = REPO_ROOT / "tests" / "fixtures" / "fu1-term-reasons"
ANSWERS = json.loads((CORPUS / "expected" / "answers.json").read_text())
SCHEMA = json.loads((REPO_ROOT / "src" / "gnd" / "report.schema.json").read_text())


def _validator(definition: str) -> jsonschema.Draft202012Validator:
    return jsonschema.Draft202012Validator({"$ref": f"#/$defs/{definition}", "$defs": SCHEMA["$defs"]})


def _row(reason: str) -> dict:
    return {
        "derivation_ref": "derivation:out_mod",
        "derivation": "derived",
        "modality": "alethic",
        "verdict": "unchecked",
        "message": "The derivation for 'out_mod' is unavailable.",
        "findings": [],
        "reason_code": reason,
    }


def _derivation_definitions(branch: str) -> list[str]:
    """The definitions a branch's derivation rows are validated by."""
    if branch in ("derivation_verdict", "derivation_verdict_v9"):
        return [branch]
    text = json.dumps(SCHEMA["$defs"][branch])
    assert '"#/$defs/derivation_verdict"' in text or '"#/$defs/derivation_verdict_v9"' in text, branch
    return ["derivation_verdict"]


@pytest.mark.parametrize("case", sorted(ANSWERS["cli_cases"]))
def test_cli_case_matches_answer_and_validates(case: str) -> None:
    answer = ANSWERS["cli_cases"][case]
    result = run_main(
        ["check", "models/terms.orm.yaml", f"populations/{case}.pop.yaml", "--format", "json"], cwd=CORPUS
    )
    payload = json.loads(result.stdout)
    assert result.returncode == answer["exit"]
    assert payload["schema_version"] == answer["schema_version"]
    unchecked = [(d["derivation_ref"], d["reason_code"]) for d in payload["derivations"] if d["verdict"] == "unchecked"]
    assert unchecked == [(answer["unchecked_derivation"], answer["reason_code"])]
    errors = [e.message for e in jsonschema.Draft202012Validator(SCHEMA).iter_errors(payload)]
    assert (not errors) is answer["schema_valid"], errors


@pytest.mark.parametrize("branch", ANSWERS["branches"])
@pytest.mark.parametrize("reason", ANSWERS["schema_reasons"] + ANSWERS["pre_existing_reasons"])
def test_every_branch_accepts_each_reason(branch: str, reason: str) -> None:
    for definition in _derivation_definitions(branch):
        errors = [e.message for e in _validator(definition).iter_errors(_row(reason))]
        assert not errors, (definition, errors)


@pytest.mark.parametrize("reason", ANSWERS["schema_reasons"] + ANSWERS["pre_existing_reasons"])
def test_version_15_rows_still_validate(reason: str) -> None:
    errors = [e.message for e in _validator(ANSWERS["non_regression"]).iter_errors(_row(reason))]
    assert not errors, errors


@pytest.mark.parametrize("definition", ["derivation_verdict", ANSWERS["non_regression"]])
def test_an_unknown_reason_is_refused(definition: str) -> None:
    assert list(_validator(definition).iter_errors(_row(ANSWERS["refused_reason"])))
