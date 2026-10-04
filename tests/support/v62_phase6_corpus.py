from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML as RuamelYAML

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / 'tests/fixtures/v62-phase6'
CASES_DOC = json.loads((FIXTURE / 'cases.json').read_text(encoding='utf-8'))
ANSWERS_DOC = json.loads((FIXTURE / 'answers.json').read_text(encoding='utf-8'))
ANSWERS = ANSWERS_DOC['answers']
YAML = RuamelYAML(typ='safe')

def assert_answer(case_id: str, **actual: Any) -> None:
    expected = ANSWERS[case_id]
    assert set(actual) == set(expected), case_id
    assert actual == expected, case_id

def document() -> dict[str, Any]:
    return copy.deepcopy(YAML.load((FIXTURE / CASES_DOC['model']).read_text(encoding='utf-8')))

def population_document() -> dict[str, Any]:
    return copy.deepcopy(YAML.load((FIXTURE / CASES_DOC['population']).read_text(encoding='utf-8')))

def write_case(tmp_path: Path, model_doc=None, population_doc=None) -> tuple[Path, Path]:
    tmp_path.mkdir(parents=True, exist_ok=True)
    model_path = tmp_path / 'model.orm.yaml'
    population_path = tmp_path / 'population.pop.yaml'
    yaml = RuamelYAML(typ='safe')
    with model_path.open('w', encoding='utf-8') as handle:
        yaml.dump(model_doc if model_doc is not None else document(), handle)
    with population_path.open('w', encoding='utf-8') as handle:
        yaml.dump(population_doc if population_doc is not None else population_document(), handle)
    return (model_path, population_path)

def loaded_case(tmp_path: Path, model_doc=None, population_doc=None):
    from gnd.checker import band, check
    from gnd.model import load_model
    from gnd.population import load_population
    model_path, population_path = write_case(tmp_path, model_doc, population_doc)
    model = load_model(model_path)
    population = load_population(population_path, model=model)
    report = check(model, population)
    return (model, population, report, band(report))
