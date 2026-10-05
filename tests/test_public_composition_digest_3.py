from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML as RuamelYAML

from gnd.model import Model
from gnd.transition import model_digest, operations_digest

FIXTURE = Path(__file__).parent / "fixtures/public-composition-digests/v62-phase3"
CASES_DOC = {'model': 'models/exact-terms.orm.yaml', 'steps': 'walks/approve.steps.json'}
YAML = RuamelYAML(typ="safe")

def document() -> dict[str, Any]:
    """Return a fresh raw document while the Phase 3 loader is intentionally RED."""
    return copy.deepcopy(
        YAML.load((FIXTURE / CASES_DOC["model"]).read_text(encoding="utf-8"))
    )



def test_walk_digests_bind_the_future_loaded_model_bytes() -> None:
    model = Model.model_validate(document())
    walk = json.loads((FIXTURE / CASES_DOC["steps"]).read_text(encoding="utf-8"))
    assert walk["model_digest"] == model_digest(model)
    assert walk["operations_digest"] == operations_digest(model.operations)
