"""Current admitted-value bridge immutability; no formal proof invocation."""
from __future__ import annotations

import dataclasses
import json

import pytest
from support.public_transition_adapter import freeze_transition
from test_public_phase4_transition_support import BY_ID, materialize_walk

from gnd import transition
from gnd.model import load_model
from gnd.population import load_population


def test_transition_ir_is_immutable_and_meaning_preserving(tmp_path):
    paths = materialize_walk(BY_ID["clean-walk"], tmp_path)
    model = load_model(paths["model"])
    pre = load_population(paths["pre"], model=model)
    post = load_population(paths["post"], model=model)
    steps = transition.read_steps_document(paths["steps"])["steps"]
    frozen = freeze_transition(model, pre, post, steps)

    assert json.loads(frozen.object_types_json) == model.object_types
    assert json.loads(frozen.fact_types_json) == model.fact_types
    assert json.loads(frozen.pre.facts_json) == {
        name: [dict(fact) for fact in facts] for name, facts in pre.facts.items()
    }
    assert [step.operation for step in frozen.steps] == [step["op"] for step in steps]
    with pytest.raises(dataclasses.FrozenInstanceError):
        frozen.pre = frozen.post

