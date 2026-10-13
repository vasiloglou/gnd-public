"""Generated states must retain JSON decoding through the validating loader."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from test_v70_phase4_runtime import _stage

from gnd import api, population, transition
from gnd.model import load_model
from gnd.population import load_population

ROOT = Path(__file__).resolve().parents[1]
ANSWERS = json.loads(
    (ROOT / ".gnd-planning/milestones/analytics-m3-repairs/notes/phase-6-answers.json").read_text()
)


@pytest.mark.parametrize("case", ["legacy", "opaque"])
def test_generated_transition_states_use_json(case, tmp_path, monkeypatch):
    if case == "legacy":
        corpus = ROOT / "tests/fixtures/public-transition-contract"
        model = load_model(corpus / "v2_expense.orm.yaml")
        pre = load_population(corpus / "walks/clean-walk/pre.pop.yaml", model=model)
        steps = json.loads((corpus / "walks/clean-walk/steps.json").read_text())
        steps.update(
            model_digest=transition.model_digest(model),
            operations_digest=transition.operations_digest(model.operations),
        )
    else:
        model_path, pre_path, steps_path = _stage("T01-walk-unknown-precondition", tmp_path)
        model = load_model(model_path)
        pre = load_population(pre_path, model=model)
        steps = json.loads(steps_path.read_text())
    observed = []
    original = population._parse_document_bytes

    def capture(data, *, suffix, source):
        observed.append((source, suffix))
        return original(data, suffix=suffix, source=source)

    monkeypatch.setattr(population, "_parse_document_bytes", capture)
    payload = api.transition(model, pre, steps)
    assert payload["exit_code"] == ANSWERS[case]["exit_code"]
    assert bool(payload["transition"]["computed_post"]) == ANSWERS[case]["computed_post"]
    assert observed
    assert all(suffix == ".json" for _, suffix in observed), observed
    for prefix in (
        "<dynamic asserted state",
        "<intermediate state",
        "<computed post>",
        "<computed post evaluation view>",
    ):
        assert any(source.startswith(prefix) for source, _ in observed), prefix
