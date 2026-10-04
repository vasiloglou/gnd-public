from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML as RuamelYAML

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / 'tests/fixtures/v62-phase5'
CASES_DOC = json.loads((FIXTURE / 'cases.json').read_text(encoding='utf-8'))
YAML = RuamelYAML(typ='safe')

def document() -> dict[str, Any]:
    return copy.deepcopy(YAML.load((FIXTURE / CASES_DOC['model']).read_text(encoding='utf-8')))

def population_path(name: str='clean') -> Path:
    return FIXTURE / CASES_DOC['populations'][name]
