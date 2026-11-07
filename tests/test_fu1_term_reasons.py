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
    """The schema locations a branch's derivation rows are validated at.

    The two row definitions are validated directly. A report branch is
    validated at every location inside it whose items reference
    derivation_verdict or derivation_verdict_v9, through the branch's own
    JSON pointer, so a broken route inside the branch fails the case
    (review R1).
    """
    if branch in ("derivation_verdict", "derivation_verdict_v9"):
        return [branch]
    targets = {"#/$defs/derivation_verdict", "#/$defs/derivation_verdict_v9"}
    found: list[str] = []

    def walk(node: object, pointer: str) -> None:
        if isinstance(node, dict):
            if node.get("$ref") in targets:
                # Validate at the enclosing items schema, so a narrowing
                # wrapped around the reference is exercised too.
                head, _, _ = pointer.rpartition("/items")
                found.append(f"{head}/items" if head else pointer)
            for key, value in node.items():
                walk(value, f"{pointer}/{key}")
        elif isinstance(node, list):
            for index, value in enumerate(node):
                walk(value, f"{pointer}/{index}")

    walk(SCHEMA["$defs"][branch], branch)
    assert found, branch
    return sorted(set(found))


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
