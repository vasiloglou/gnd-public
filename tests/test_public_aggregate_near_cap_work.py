"""Isolated near-cap aggregate work instrument fixed before its first run."""

from __future__ import annotations

import hashlib
import json
import sys
import time
from dataclasses import asdict
from pathlib import Path

import pytest

from gnd.checker import structured_extension_view
from gnd.model import Model, semantic_validate
from gnd.population import MAX_POPULATION_BYTES, load_population_bytes

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tests.support.v62_phase4_corpus import document, population_document

CONFIG = json.loads((Path(__file__).resolve().parent / "fixtures/public-aggregate-near-cap-scaling.json").read_text(encoding="utf-8"))


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
    rows = [
        {
            "scenario": "north",
            "sample": f"s{index:06d}",
            "rb": base + (index + seed) % 17,
        }
        for index in range(unique_rows)
    ]
    rows += [rows[index].copy() for index in range(0, unique_rows, CONFIG["duplicate_every"])]
    population["facts"] = {"observation": rows, "scenario_sum": []}
    return json.dumps(population, sort_keys=True, separators=(",", ":")).encode()


def _assert_sum_digest(value: int, digest: str) -> None:
    assert hashlib.sha256(str(value).encode()).hexdigest() == digest


@pytest.mark.slow
def test_q03_near_ten_megabyte_sum_stays_bounded(tmp_path: Path) -> None:
    started = time.perf_counter()
    assert CONFIG["population_cap_bytes"] == MAX_POPULATION_BYTES
    canonical_raw = _population_bytes(
        CONFIG["unique_rows"], base_bits=CONFIG["integer_base_bits"]
    )
    assert len(canonical_raw) == CONFIG["expected_input_bytes"]
    assert 0 <= MAX_POPULATION_BYTES - len(canonical_raw) < 1024
    # JSON permits insignificant trailing whitespace. Fill the remaining 866
    # bytes so the approved Q03 answer's exact 10 MiB input boundary is real,
    # while the pinned generator, row count, and sum remain unchanged.
    raw = canonical_raw + b" " * (MAX_POPULATION_BYTES - len(canonical_raw))
    assert len(raw) == MAX_POPULATION_BYTES
    path = tmp_path / "near-cap.pop.json"
    path.write_bytes(raw)
    model = _model()
    population = load_population_bytes(path.read_bytes(), source=path, model=model)
    assert len(population.facts["observation"]) == CONFIG["total_rows"]
    evaluation_started = time.perf_counter()
    view = structured_extension_view(model, population)
    evaluation_seconds = time.perf_counter() - evaluation_started
    rows = view.facts["scenario_sum"]
    assert len(rows) == CONFIG["group_count"] == 1
    assert rows[0]["scenario"] == "north"
    _assert_sum_digest(rows[0]["sum"], CONFIG["expected_sum_sha256"])
    work = asdict(view.work)
    for name, ceiling in CONFIG["maximum_work"].items():
        assert 0 < work[name] <= ceiling, (name, work[name], ceiling)
    print(
        json.dumps(
            {
                "schema_version": 1,
                "exit_code": 0,
                "input_bytes": len(raw),
                "body_rows": len(population.facts["observation"]),
                "distinct_contributions": work["aggregate_distinct_contributions"],
                "groups": work["aggregate_groups"],
                "exact_operations": work["aggregate_exact_operations"],
                "maximum_value_bits": work["aggregate_maximum_value_bits"],
                "evaluation_seconds": round(evaluation_seconds, 6),
                "total_seconds": round(time.perf_counter() - started, 6),
                "work": work,
            },
            sort_keys=True,
        )
    )
