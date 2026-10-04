import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import json
import sys
from pathlib import Path

from gnd import checker
from gnd.model import Model, load_model, semantic_validate
from gnd.population import load_population, load_population_bytes
from tests.support.v62_phase4_corpus import CASES_DOC, FIXTURE, document

ROOT = Path(__file__).resolve().parents[1]

def test_k02_aggregate_dispatch_selects_exact_lane_without_function_terms() -> None:
    model = Model.model_validate(document())
    assert checker._model_uses_exact_derivations(model)
    population = load_population(FIXTURE / CASES_DOC["population"], model=model)
    view = checker.structured_extension_view(model, population)
    assert view.work.aggregate_candidate_bindings > 0


def test_k03_aggregate_free_model_keeps_predecessor_dispatch() -> None:
    model = load_model(ROOT / "tests/fixtures/v61-phase4/models/role-declaration.orm.yaml")
    assert not checker._model_uses_exact_derivations(model)
    assert checker._evaluate_derivations is checker._evaluate_derivations_dispatch
    assert checker._PHASE3_LEGACY_EVALUATE_DERIVATIONS is not checker._evaluate_derivations


def test_k04_aggregate_free_public_exact_comparison_keeps_phase3_result() -> None:
    model_document = document()
    model_document["object_types"].append(
        {"id": "score", "name": "Score", "kind": "value", "primitive": "Float"}
    )
    observation = model_document["fact_types"][0]
    observation["reading"] = (
        "{Scenario} has sample {Sample} with resource blocks {Integer} and score {Score}"
    )
    observation["roles"].append({"object_type": "score", "role_name": "score"})
    accepted = {
        "id": "accepted",
        "reading": "{Scenario} is accepted",
        "roles": [{"object_type": "scenario", "role_name": "scenario"}],
        "derivation": "derived",
        "derivation_rule": {
            "body": [
                {
                    "fact_type": "observation",
                    "bind": {
                        "scenario": "$scenario",
                        "sample": "$sample",
                        "rb": "$rb",
                        "score": "$score",
                    },
                }
            ],
            "where": [{"operator": ">", "left": "$rb", "right": "$score"}],
            "head": {"scenario": "$scenario"},
        },
    }
    model_document["fact_types"] = [observation, accepted]
    model_document["constraints"] = []
    model_document["operations"] = []
    assert semantic_validate(model_document) == []
    model = Model.model_validate(model_document)
    raw = {
        "population": {
            "model": "aggregate-free.orm.yaml",
            "model_id": model_document["model_id"],
            "source": "fixture",
            "covers": ["observation", "accepted"],
        },
        "facts": {
            "observation": [
                {
                    "scenario": "north",
                    "sample": "s1",
                    "rb": (1 << 65_535) - 1,
                    "score": 5e-324,
                }
            ],
            "accepted": [{"scenario": "north"}],
        },
    }
    prior_limit = sys.get_int_max_str_digits()
    try:
        sys.set_int_max_str_digits(0)
        population = load_population_bytes(
            json.dumps(raw).encode(), source="aggregate-free.json", model=model
        )
        envelope = checker.exact_extension_envelope(model, population)
    finally:
        sys.set_int_max_str_digits(prior_limit)
    assert envelope["unavailable"] == {}
    assert envelope["relations"]["accepted"] == [['["string","north"]']]
