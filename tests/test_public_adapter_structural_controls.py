"""All nine original structural escape variants reach admission."""
import json
from pathlib import Path

import pytest
from support import public_adapter_cases as corpus

from gnd.model import load_model
from gnd.population import load_population

ROOT = Path(__file__).resolve().parents[1]

@pytest.mark.parametrize(
    "damage",
    [
        "missing-role",
        "missing-head",
        "head-list",
        "missing-body",
        "missing-atom-fact",
        "missing-bind",
        "unknown-head-role",
        "unknown-body-fact",
        "unknown-scope-fact",
    ],
)
def test_review_structural_escape_examples_are_rejected_at_admission(tmp_path, damage):
    from ruamel.yaml import YAML

    from gnd.model import ModelValidationError
    from gnd.population import PopulationValidationError

    directory = ROOT / "tests/fixtures/derivation-evaluation/cases/eval-bare-dollar-literal"
    document = YAML(typ="safe").load((directory / "model.orm.yaml").read_text())
    data = YAML(typ="safe").load((directory / "population.yaml").read_text())
    rule = document["fact_types"][1]["derivation_rule"]
    if damage == "missing-role":
        del data["facts"]["item_has_tag"][0]["tag"]
    elif damage == "missing-head":
        del rule["head"]
    elif damage == "head-list":
        rule["head"] = []
    elif damage == "missing-body":
        del rule["body"]
    elif damage == "missing-atom-fact":
        del rule["body"][0]["fact_type"]
    elif damage == "missing-bind":
        del rule["body"][0]["bind"]
    elif damage == "unknown-head-role":
        rule["head"] = {"absent": "$i"}
    elif damage == "unknown-body-fact":
        rule["body"][0]["fact_type"] = "absent"
    else:
        document, data = corpus._documents("P2-161")
        document["constraints"] = [document["constraints"][0]]
        document["constraints"][0]["antecedent"][0]["fact_type"] = "absent"
    model_path, population_path = tmp_path / "model.orm.yaml", tmp_path / "population.json"
    model_path.write_text(json.dumps(document))
    population_path.write_text(json.dumps(data))
    if damage == "missing-role":
        model = load_model(model_path)
        with pytest.raises(PopulationValidationError):
            load_population(population_path, model=model)
    else:
        with pytest.raises(ModelValidationError):
            load_model(model_path)

