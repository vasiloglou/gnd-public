from __future__ import annotations

import json
from pathlib import Path

import pytest

from gnd import model as model_module
from gnd import transition as transition_module

FIXTURE = Path(__file__).parent / "fixtures/public-composition-digests/v62-phase1"
CASES_DOC = {'model': 'models/static.orm.yaml', 'steps': 'walks/activate.steps.json'}

def test_base_walk_digests_bind_the_fixture(monkeypatch: pytest.MonkeyPatch) -> None:
    old_rules = model_module._SEMANTIC_RULES
    monkeypatch.setattr(
        model_module,
        "_SEMANTIC_RULES",
        tuple(
            rule for rule in old_rules if rule.__name__ != "_rule_derivation_operations_unsupported"
        ),
    )
    model = model_module.load_model(FIXTURE / CASES_DOC["model"])
    step_doc = json.loads((FIXTURE / CASES_DOC["steps"]).read_text(encoding="utf-8"))
    assert step_doc["model_digest"] == transition_module.model_digest(model)
    assert step_doc["operations_digest"] == transition_module.operations_digest(model.operations)
