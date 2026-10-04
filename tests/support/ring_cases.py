from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from typing import Any

from gnd.model import Model, load_model
from gnd.population import load_population

REPO_ROOT = Path(__file__).resolve().parents[2]
CASES = {'cases': [{'id': 'P2-045', 'model': 'tests/fixtures/checker/ring.orm.yaml', 'population': 'tests/fixtures/checker/population.ring_pass.yaml', 'ref': 'fact_types[rel_irreflexive].constraints[0]'}, {'id': 'P2-046', 'model': 'tests/fixtures/checker/ring.orm.yaml', 'population': 'tests/fixtures/checker/population.ring_fail.yaml', 'ref': 'fact_types[rel_irreflexive].constraints[0]'}, {'id': 'P2-047', 'model': 'tests/fixtures/checker/ring.orm.yaml', 'population': 'tests/fixtures/checker/population.ring_fail.yaml', 'ref': 'fact_types[rel_irreflexive].constraints[0]', 'model_patch': [{'path': 'fact_types[rel_irreflexive].constraints[0].modality', 'value': 'deontic'}]}, {'id': 'P2-048', 'model': 'tests/fixtures/checker/ring.orm.yaml', 'population': 'tests/fixtures/checker/population.ring_pass.yaml', 'ref': 'fact_types[rel_asymmetric].constraints[0]'}, {'id': 'P2-049', 'model': 'tests/fixtures/checker/ring.orm.yaml', 'population': 'tests/fixtures/checker/population.ring_fail.yaml', 'ref': 'fact_types[rel_asymmetric].constraints[0]'}, {'id': 'P2-050', 'model': 'tests/fixtures/checker/ring.orm.yaml', 'population': 'tests/fixtures/checker/population.ring_fail.yaml', 'ref': 'fact_types[rel_asymmetric].constraints[0]', 'model_patch': [{'path': 'fact_types[rel_asymmetric].constraints[0].modality', 'value': 'deontic'}]}, {'id': 'P2-051', 'model': 'tests/fixtures/checker/ring.orm.yaml', 'population': 'tests/fixtures/checker/population.ring_pass.yaml', 'ref': 'fact_types[rel_intransitive].constraints[0]'}, {'id': 'P2-052', 'model': 'tests/fixtures/checker/ring.orm.yaml', 'population': 'tests/fixtures/checker/population.ring_fail.yaml', 'ref': 'fact_types[rel_intransitive].constraints[0]'}, {'id': 'P2-053', 'model': 'tests/fixtures/checker/ring.orm.yaml', 'population': 'tests/fixtures/checker/population.ring_fail.yaml', 'ref': 'fact_types[rel_intransitive].constraints[0]', 'model_patch': [{'path': 'fact_types[rel_intransitive].constraints[0].modality', 'value': 'deontic'}]}, {'id': 'P2-054', 'model': 'tests/fixtures/checker/ring.orm.yaml', 'population': 'tests/fixtures/checker/population.ring_pass.yaml', 'ref': 'fact_types[rel_antisymmetric].constraints[0]'}, {'id': 'P2-055', 'model': 'tests/fixtures/checker/ring.orm.yaml', 'population': 'tests/fixtures/checker/population.ring_fail.yaml', 'ref': 'fact_types[rel_antisymmetric].constraints[0]'}, {'id': 'P2-056', 'model': 'tests/fixtures/checker/ring.orm.yaml', 'population': 'tests/fixtures/checker/population.ring_fail.yaml', 'ref': 'fact_types[rel_antisymmetric].constraints[0]', 'model_patch': [{'path': 'fact_types[rel_antisymmetric].constraints[0].modality', 'value': 'deontic'}]}, {'id': 'P2-057', 'model': 'tests/fixtures/checker/ring.orm.yaml', 'population': 'tests/fixtures/checker/population.ring_pass.yaml', 'ref': 'fact_types[rel_acyclic].constraints[0]'}, {'id': 'P2-058', 'model': 'tests/fixtures/checker/ring.orm.yaml', 'population': 'tests/fixtures/checker/population.ring_fail.yaml', 'ref': 'fact_types[rel_acyclic].constraints[0]'}, {'id': 'P2-059', 'model': 'tests/fixtures/checker/ring.orm.yaml', 'population': 'tests/fixtures/checker/population.ring_fail.yaml', 'ref': 'fact_types[rel_acyclic].constraints[0]', 'model_patch': [{'path': 'fact_types[rel_acyclic].constraints[0].modality', 'value': 'deontic'}]}, {'id': 'P2-060', 'model': 'tests/fixtures/checker/ring.orm.yaml', 'population': 'tests/fixtures/checker/population.ring_pass.yaml', 'ref': 'fact_types[rel_asymmetric_intransitive].constraints[0]'}, {'id': 'P2-061', 'model': 'tests/fixtures/checker/ring.orm.yaml', 'population': 'tests/fixtures/checker/population.ring_fail.yaml', 'ref': 'fact_types[rel_asymmetric_intransitive].constraints[0]'}, {'id': 'P2-062', 'model': 'tests/fixtures/checker/ring.orm.yaml', 'population': 'tests/fixtures/checker/population.ring_fail.yaml', 'ref': 'fact_types[rel_asymmetric_intransitive].constraints[0]', 'model_patch': [{'path': 'fact_types[rel_asymmetric_intransitive].constraints[0].modality', 'value': 'deontic'}]}, {'id': 'P2-063', 'model': 'tests/fixtures/checker/ring.orm.yaml', 'population': 'tests/fixtures/checker/population.ring_pass.yaml', 'ref': 'fact_types[rel_acyclic_intransitive].constraints[0]'}, {'id': 'P2-064', 'model': 'tests/fixtures/checker/ring.orm.yaml', 'population': 'tests/fixtures/checker/population.ring_fail.yaml', 'ref': 'fact_types[rel_acyclic_intransitive].constraints[0]'}, {'id': 'P2-065', 'model': 'tests/fixtures/checker/ring.orm.yaml', 'population': 'tests/fixtures/checker/population.ring_fail.yaml', 'ref': 'fact_types[rel_acyclic_intransitive].constraints[0]', 'model_patch': [{'path': 'fact_types[rel_acyclic_intransitive].constraints[0].modality', 'value': 'deontic'}]}, {'id': 'P2-066', 'model': 'tests/fixtures/checker/ring.orm.yaml', 'population': 'tests/fixtures/checker/population.ring_pass.yaml', 'ref': 'fact_types[rel_symmetric].constraints[0]'}, {'id': 'P2-067', 'model': 'tests/fixtures/checker/ring.orm.yaml', 'population': 'tests/fixtures/checker/population.ring_fail.yaml', 'ref': 'fact_types[rel_symmetric].constraints[0]'}, {'id': 'P2-068', 'model': 'tests/fixtures/checker/ring.orm.yaml', 'population': 'tests/fixtures/checker/population.ring_fail.yaml', 'ref': 'fact_types[rel_symmetric].constraints[0]', 'model_patch': [{'path': 'fact_types[rel_symmetric].constraints[0].modality', 'value': 'deontic'}]}, {'id': 'P2-069', 'model': 'tests/fixtures/checker/ring.orm.yaml', 'population': 'tests/fixtures/checker/population.ring_pass.yaml', 'ref': 'fact_types[rel_symmetric_irreflexive].constraints[0]'}, {'id': 'P2-070', 'model': 'tests/fixtures/checker/ring.orm.yaml', 'population': 'tests/fixtures/checker/population.ring_fail.yaml', 'ref': 'fact_types[rel_symmetric_irreflexive].constraints[0]'}, {'id': 'P2-071', 'model': 'tests/fixtures/checker/ring.orm.yaml', 'population': 'tests/fixtures/checker/population.ring_fail.yaml', 'ref': 'fact_types[rel_symmetric_irreflexive].constraints[0]', 'model_patch': [{'path': 'fact_types[rel_symmetric_irreflexive].constraints[0].modality', 'value': 'deontic'}]}, {'id': 'P2-072', 'model': 'tests/fixtures/checker/ring.orm.yaml', 'population': 'tests/fixtures/checker/population.ring_pass.yaml', 'ref': 'fact_types[rel_symmetric_intransitive].constraints[0]'}, {'id': 'P2-073', 'model': 'tests/fixtures/checker/ring.orm.yaml', 'population': 'tests/fixtures/checker/population.ring_fail.yaml', 'ref': 'fact_types[rel_symmetric_intransitive].constraints[0]'}, {'id': 'P2-074', 'model': 'tests/fixtures/checker/ring.orm.yaml', 'population': 'tests/fixtures/checker/population.ring_fail.yaml', 'ref': 'fact_types[rel_symmetric_intransitive].constraints[0]', 'model_patch': [{'path': 'fact_types[rel_symmetric_intransitive].constraints[0].modality', 'value': 'deontic'}]}, {'id': 'P2-075', 'model': 'tests/fixtures/checker/ring.orm.yaml', 'population': 'tests/fixtures/checker/population.ring_pass.yaml', 'ref': 'fact_types[rel_purely_reflexive].constraints[0]'}, {'id': 'P2-076', 'model': 'tests/fixtures/checker/ring.orm.yaml', 'population': 'tests/fixtures/checker/population.ring_fail.yaml', 'ref': 'fact_types[rel_purely_reflexive].constraints[0]'}, {'id': 'P2-077', 'model': 'tests/fixtures/checker/ring.orm.yaml', 'population': 'tests/fixtures/checker/population.ring_fail.yaml', 'ref': 'fact_types[rel_purely_reflexive].constraints[0]', 'model_patch': [{'path': 'fact_types[rel_purely_reflexive].constraints[0].modality', 'value': 'deontic'}]}, {'id': 'P2-078', 'model': 'tests/fixtures/checker/ring.orm.yaml', 'population': 'tests/fixtures/checker/population.ring_pass.yaml', 'ref': 'fact_types[rel_reflexive].constraints[0]'}, {'id': 'P2-079', 'model': 'tests/fixtures/checker/ring.orm.yaml', 'population': 'tests/fixtures/checker/population.ring_fail.yaml', 'ref': 'fact_types[rel_reflexive].constraints[0]', 'population_patch': [{'path': 'facts.rel_reflexive', 'value': [{'a': 1, 'b': 2}, {'a': 2, 'b': 2}]}]}, {'id': 'P2-080', 'model': 'tests/fixtures/checker/ring.orm.yaml', 'population': 'tests/fixtures/checker/population.ring_fail.yaml', 'ref': 'fact_types[rel_reflexive].constraints[0]', 'model_patch': [{'path': 'fact_types[rel_reflexive].constraints[0].modality', 'value': 'deontic'}], 'population_patch': [{'path': 'facts.rel_reflexive', 'value': [{'a': 1, 'b': 2}, {'a': 2, 'b': 2}]}]}, {'id': 'P2-081', 'model': 'tests/fixtures/checker/ring.orm.yaml', 'population': 'tests/fixtures/checker/population.ring_pass.yaml', 'ref': 'fact_types[rel_transitive].constraints[0]'}, {'id': 'P2-082', 'model': 'tests/fixtures/checker/ring.orm.yaml', 'population': 'tests/fixtures/checker/population.ring_fail.yaml', 'ref': 'fact_types[rel_transitive].constraints[0]'}, {'id': 'P2-083', 'model': 'tests/fixtures/checker/ring.orm.yaml', 'population': 'tests/fixtures/checker/population.ring_fail.yaml', 'ref': 'fact_types[rel_transitive].constraints[0]', 'model_patch': [{'path': 'fact_types[rel_transitive].constraints[0].modality', 'value': 'deontic'}]}, {'id': 'P2-084', 'model': 'tests/fixtures/checker/ring.orm.yaml', 'population': 'tests/fixtures/checker/population.ring_fail.yaml', 'ref': 'fact_types[rel_reflexive].constraints[0]'}, {'id': 'P2-085', 'model': 'tests/fixtures/checker/ring.orm.yaml', 'population': 'tests/fixtures/checker/population.ring_pass.yaml', 'ref': 'fact_types[rel_irreflexive].constraints[0]', 'model_patch': [{'path': 'fact_types[rel_irreflexive].roles', 'append': {'object_type': 'node', 'role_name': 'c'}}], 'population_patch': [{'path': 'facts.rel_irreflexive', 'value': [{'a': 1, 'b': 2, 'c': 3}]}], 'admission': 'unvalidated'}], 'negative_controls': {}}
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
