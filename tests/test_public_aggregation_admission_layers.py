"""Distinct semantic and schema refusal controls for malformed aggregation."""
from pathlib import Path

import pytest
from ruamel.yaml import YAML

from gnd.model import ModelValidationError, load_model, semantic_validate

ROOT = Path(__file__).resolve().parents[1]

def test_malformed_aggregation_control_names_the_layer2_diagnostic_and_public_refusal():
    path = ROOT / "tests/fixtures/derivation/cases/r38-aggregate-key.orm.yaml"
    document = YAML(typ="safe").load(path.read_text(encoding="utf-8"))
    issues = semantic_validate(document)
    matches = [
        issue
        for issue in issues
        if issue.rule_id == "semantic:aggregate-shape" and ".aggregate" in issue.path
    ]
    assert matches
    with pytest.raises(ModelValidationError) as error:
        load_model(path)
    assert "jsonschema:oneOf" in {issue.rule_id for issue in error.value.issues}
