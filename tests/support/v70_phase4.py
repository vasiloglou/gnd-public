"""Fixture builders for Phase 4 successor cases."""
from __future__ import annotations

import json
from pathlib import Path

from ruamel.yaml import YAML

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures/v70-phase4"

def _write(tmp_path: Path, model: dict, population: dict) -> tuple[Path, Path]:
    model_path = tmp_path / "model.orm.yaml"
    with model_path.open("w") as stream:
        YAML().dump(model, stream)
    population_path = tmp_path / "population.json"
    population_path.write_text(json.dumps(population, ensure_ascii=False) + "\n")
    return model_path, population_path


def _positive() -> tuple[dict, dict]:
    return (
        YAML(typ="safe").load((FIXTURE / "positive.orm.yaml").read_text()),
        json.loads((FIXTURE / "positive.pop.json").read_text()),
    )


def _unknown_positive() -> tuple[dict, dict]:
    model, population = _positive()
    population["facts"]["observed"].append({"record": "R1", "item": {"$opaque": "source-cell"}})
    return model, population


def _derivation(payload: dict) -> dict:
    assert payload["derivations"] and len(payload["derivations"]) == 1
    return payload["derivations"][0]
