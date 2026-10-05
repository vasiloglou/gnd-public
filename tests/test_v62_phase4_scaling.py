from __future__ import annotations

import json

from support.v62_phase4_corpus import FIXTURE, document, population_document

from gnd.checker import structured_extension_view
from gnd.model import Model, semantic_validate
from gnd.population import load_population_bytes

CONFIG = json.loads((FIXTURE / "scaling.json").read_text(encoding="utf-8"))


def _model() -> Model:
    model_document = document()
    model_document["fact_types"] = [
        row for row in model_document["fact_types"] if row["id"] in {"observation", "scenario_sum"}
    ]
    model_document["constraints"] = []
    model_document["operations"] = []
    assert semantic_validate(model_document) == []
    return Model.model_validate(model_document)


def _population_bytes(unique_rows: int, *, base_bits: int) -> bytes:
    population = population_document()
    population["population"]["covers"] = ["observation", "scenario_sum"]
    base = 1 << (base_bits - 1)
    seed = CONFIG["seed"]
    rows = [{"scenario": "north", "sample": f"s{index:06d}", "rb": base + (index + seed) % 17} for index in range(unique_rows)]
    rows += [rows[index].copy() for index in range(0, unique_rows, CONFIG["duplicate_every"])]
    population["facts"] = {"observation": rows, "scenario_sum": []}
    return json.dumps(population, sort_keys=True, separators=(",", ":")).encode()


def test_q01_tiny_oracle_exits_with_known_sum() -> None:
    model = _model()
    population = load_population_bytes(_population_bytes(3, base_bits=12), source="tiny-aggregate.json", model=model)
    view = structured_extension_view(model, population)
    assert view.facts["scenario_sum"] == ({"scenario": "north", "sum": 6175},)
    assert view.work.aggregate_distinct_contributions == 3
