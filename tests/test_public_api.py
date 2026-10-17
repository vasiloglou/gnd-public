"""Current API compatibility on independently synthetic public inputs."""
from __future__ import annotations

import inspect
from pathlib import Path

import pytest

from gnd import api
from gnd.model import load_model

FIXTURES = Path(__file__).parent / "fixtures/public-launch-phase-2"


def test_public_exports_and_current_keyword_signatures():
    assert api.__all__ == ("validate", "check", "transition", "verbalize", "diff", "witness", "replay", "check_with_receipt", "CheckReceipt", "ReceiptRefused")
    expected = {
        "validate": ("model", "unredacted", "references"),
        "check": ("model", "population", "compiled_operations", "unredacted", "anchors", "document", "population_bytes", "admission", "references"),
        "transition": ("model", "pre", "steps", "post", "unredacted", "references", "pre_receipt"),
    }
    for name, parameters in expected.items():
        signature = inspect.signature(getattr(api, name))
        assert tuple(signature.parameters) == parameters
        assert signature.parameters["unredacted"].kind is inspect.Parameter.KEYWORD_ONLY
        assert signature.parameters["unredacted"].default is False
        assert signature.return_annotation != inspect.Signature.empty


def test_loaded_model_validation_rechecks_nested_mutation():
    model = load_model(FIXTURES / "model.orm.yaml")
    assert api.validate(model)["exit_code"] == 0
    model.fact_types[0]["roles"][0]["object_type"] = "undeclared-after-load"
    payload = api.validate(model)
    assert payload["exit_code"] == 3
    assert any(issue["rule_id"] == "semantic:role-ref" for issue in payload["issues"])


@pytest.mark.parametrize("invoke", [
    lambda: api.validate(41),
    lambda: api.check(41, FIXTURES / "clean.population.json"),
    lambda: api.transition(FIXTURES / "model.orm.yaml", 41, {}),
])
def test_bad_object_shapes_raise_type_error_before_evaluation(invoke):
    with pytest.raises(TypeError):
        invoke()
