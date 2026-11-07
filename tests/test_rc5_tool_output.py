"""RC5 (rule-check-adoption): population source tool-output and its producer.

The corpus under tests/fixtures/rc5-tool-output is the phase's approval
instrument; its README tells each case and expected/answers.json holds the
answers.
"""

from __future__ import annotations

import json

import pytest
from support.cli_runner import run_main
from support.repository import REPO_ROOT

CORPUS = REPO_ROOT / "tests" / "fixtures" / "rc5-tool-output"
ANSWERS = json.loads((CORPUS / "expected" / "answers.json").read_text())


def _check(case: str):
    return run_main(
        ["check", "models/catalog.orm.yaml", f"populations/{case}.pop.yaml", "--format", "json"], cwd=CORPUS
    )


@pytest.mark.parametrize("case", sorted(ANSWERS))
def test_case_matches_answer_key(case: str) -> None:
    result = _check(case)
    payload = json.loads(result.stdout)
    assert result.returncode == ANSWERS[case]["exit"]
    assert [[issue["rule_id"], issue["path"]] for issue in payload["issues"]] == ANSWERS[case]["issues"]
    if ANSWERS[case]["exit"] == 0:
        control = json.loads(_check("fixture-control").stdout)
        control["population"] = payload["population"]
        assert payload == control


@pytest.mark.parametrize("case", sorted(case for case, answer in ANSWERS.items() if answer["exit"] == 0))
def test_the_loaded_population_keeps_its_label(case: str) -> None:
    from gnd.model import load_model
    from gnd.population import load_population

    model = load_model(CORPUS / "models" / "catalog.orm.yaml")
    population = load_population(CORPUS / "populations" / f"{case}.pop.yaml", model=model)
    assert population.source == "tool-output"
    if "producer" in ANSWERS[case]:
        assert population.producer == ANSWERS[case]["producer"]
    if "producer_length" in ANSWERS[case]:
        assert len(population.producer) == ANSWERS[case]["producer_length"]
