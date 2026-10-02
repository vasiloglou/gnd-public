"""Shared readers for the v6.2 Phase 2 corpus-first instrument."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML as RuamelYAML

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests/fixtures/v62-phase2"
CASES_DOC = json.loads((FIXTURE / "cases.json").read_text(encoding="utf-8"))
ANSWERS_DOC = json.loads((FIXTURE / "answers.json").read_text(encoding="utf-8"))
CASES = {row["id"]: row for row in CASES_DOC["cases"]}
ANSWERS = ANSWERS_DOC["answers"]
YAML = RuamelYAML(typ="safe")


def document() -> dict[str, Any]:
    return copy.deepcopy(
        YAML.load((FIXTURE / CASES_DOC["model"]).read_text(encoding="utf-8"))
    )


def write_model(tmp_path: Path, mutate=None) -> Path:
    doc = document()
    if mutate is not None:
        mutate(doc)
    path = tmp_path / "dynamic.orm.yaml"
    yaml = RuamelYAML()
    yaml.default_flow_style = False
    with path.open("w", encoding="utf-8") as stream:
        yaml.dump(doc, stream)
    return path


def population(name: str) -> Path:
    return FIXTURE / CASES_DOC["populations"][name]


def steps() -> Path:
    return FIXTURE / CASES_DOC["steps"]


def write_steps(tmp_path: Path, model, rows: list[dict[str, Any]]) -> Path:
    """Write a digest-bound walk for a focused Phase-2 test."""
    from gnd.transition import model_digest, operations_digest

    path = tmp_path / "focused.steps.json"
    path.write_text(
        json.dumps(
            {
                "steps_schema": 1,
                "model": "dynamic.orm.yaml",
                "model_digest": model_digest(model),
                "operations_digest": operations_digest(model.operations),
                "steps": rows,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return path
