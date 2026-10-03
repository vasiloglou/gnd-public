from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from typing import Any

from gnd.model import Model, load_model
from gnd.population import load_population

REPO_ROOT = Path(__file__).resolve().parents[2]
CASES = {'cases': [{'id': 'P2-001', 'model': 'tests/fixtures/checker/setfam.orm.yaml', 'population': 'tests/fixtures/checker/population.setfam_pass.yaml', 'ref': 'fact_types[booking_by_person].constraints[0]'}, {'id': 'P2-002', 'model': 'tests/fixtures/checker/setfam.orm.yaml', 'population': 'tests/fixtures/checker/population.precedence.yaml', 'ref': 'fact_types[booking_by_person].constraints[0]'}, {'id': 'P2-039', 'model': 'tests/fixtures/checker/setfam.orm.yaml', 'population': 'tests/fixtures/checker/population.setfam_pass.yaml', 'ref': 'fact_types[person_takes_course].constraints[0]'}, {'id': 'P2-040', 'model': 'tests/fixtures/checker/setfam.orm.yaml', 'population': 'tests/fixtures/checker/population.setfam_fail.yaml', 'ref': 'fact_types[person_takes_course].constraints[0]'}, {'id': 'P2-134', 'model': 'tests/fixtures/checker/setfam.orm.yaml', 'population': 'tests/fixtures/checker/population.setfam_pass.yaml', 'ref': 'constraints[8]'}], 'negative_controls': {}}
ROUTE_CASES = {'negative_controls': {}}
CASE_BY_ID = {r['id']: r for r in CASES['cases']}
BUILD_BY_ID = CASE_BY_ID
_TOKEN = re.compile('^([A-Za-z_][A-Za-z0-9_]*)(?:\\[([^\\]]+)\\])?$')

def _load_yaml(path: Path) -> dict[str, Any]:
    from ruamel.yaml import YAML
    return YAML(typ='safe').load(path.read_text(encoding='utf-8'))

def _descend(node: Any, token: str) -> tuple[Any, Any]:
    """Resolve one path token to (container, key) without creating anything."""
    match = _TOKEN.match(token)
    assert match is not None, f'bad patch token {token!r}'
    name, key = (match.group(1), match.group(2))
    if key is None:
        if isinstance(node, dict) and name not in node:
            return (node, name)
        return (node, name)
    container = node[name]
    if isinstance(container, list):
        if key.isdigit():
            return (container, int(key))
        for index, item in enumerate(container):
            if isinstance(item, dict) and item.get('id') == key:
                return (container, index)
        raise KeyError(f'no list member with id {key!r} under {name}')
    return (container, key)

def _apply(document: dict[str, Any], patches: list[dict[str, Any]]) -> dict[str, Any]:
    document = copy.deepcopy(document)
    for patch in patches:
        tokens = patch['path'].split('.')
        node: Any = document
        for token in tokens[:-1]:
            container, key = _descend(node, token)
            node = container[key]
        container, key = _descend(node, tokens[-1])
        if patch.get('delete'):
            del container[key]
        elif 'append' in patch:
            target = container[key]
            assert isinstance(target, list), patch
            target.append(patch['append'])
        else:
            container[key] = patch['value']
    return document

def _documents(case_id: str):
    row = BUILD_BY_ID[case_id]
    model_doc = _load_yaml(REPO_ROOT / row['model'])
    population_doc = _load_yaml(REPO_ROOT / row['population'])
    if row.get('model_patch'):
        model_doc = _apply(model_doc, row['model_patch'])
    if row.get('population_patch'):
        population_doc = _apply(population_doc, row['population_patch'])
    return (model_doc, population_doc)

def _build(case_id: str, tmp_path: Path, *, negative=False):
    """The admitted pair, optionally with its single controlled input change."""
    row = BUILD_BY_ID[case_id]
    model_doc, population_doc = _documents(case_id)
    if negative:
        control = {**CASES['negative_controls'], **ROUTE_CASES['negative_controls']}[case_id]
        if control['document'] == 'model':
            model_doc = _apply(model_doc, [control['patch']])
        else:
            assert control['document'] == 'population'
            population_doc = _apply(population_doc, [control['patch']])
    model_path = tmp_path / f'{case_id}.model.orm.yaml'
    model_path.write_text(json.dumps(model_doc), encoding='utf-8')
    if row.get('admission') == 'unvalidated':
        model = Model.model_validate({**model_doc, 'warnings': []})
    else:
        model = load_model(model_path)
    population_path = tmp_path / f'{case_id}.population.json'
    population_path.write_text(json.dumps(population_doc), encoding='utf-8')
    return (model, load_population(population_path, model=model))
