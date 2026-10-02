"""Shared readers for the v6.2 Phase 3 corpus-first instrument."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML as RuamelYAML

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests/fixtures/v62-phase3"
CASES_DOC = json.loads((FIXTURE / "cases.json").read_text(encoding="utf-8"))
ANSWERS_DOC = json.loads((FIXTURE / "answers.json").read_text(encoding="utf-8"))
CASES = {row["id"]: row for row in CASES_DOC["cases"]}
ANSWERS = ANSWERS_DOC["answers"]
YAML = RuamelYAML(typ="safe")


def document() -> dict[str, Any]:
    """Return a fresh raw document while the Phase 3 loader is intentionally RED."""
    return copy.deepcopy(
        YAML.load((FIXTURE / CASES_DOC["model"]).read_text(encoding="utf-8"))
    )


def population_document() -> dict[str, Any]:
    return copy.deepcopy(
        YAML.load((FIXTURE / CASES_DOC["population"]).read_text(encoding="utf-8"))
    )


def case_rows(prefix: str) -> list[dict[str, Any]]:
    return [row for row in CASES.values() if str(row["id"]).startswith(prefix)]

