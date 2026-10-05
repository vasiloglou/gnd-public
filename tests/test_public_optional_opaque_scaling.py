"""A legal near-cap opaque SCC remains bounded without a Cartesian join."""
from __future__ import annotations

import json
from pathlib import Path
from time import perf_counter

import pytest
from ruamel.yaml import YAML

from gnd.checker import structured_extension_view
from gnd.model import load_model
from gnd.population import MAX_POPULATION_BYTES, load_population

FIXTURE = Path(__file__).parent / 'fixtures/v70-phase4'

@pytest.mark.slow
def test_near_cap_opaque_scc_finishes_with_indexed_candidate_probe(tmp_path: Path) -> None:
    model = YAML(typ='safe').load((FIXTURE / 'recursive.orm.yaml').read_text())
    population = json.loads((FIXTURE / 'recursive.pop.json').read_text())
    model['object_types'].append({'id': 'token', 'name': 'Token', 'kind': 'value', 'primitive': 'String'})
    model['fact_types'].append({'id': 'noise', 'reading': '{Token} is irrelevant', 'roles': [{'object_type': 'token', 'role_name': 'token'}]})
    population['population']['covers'].append('noise')
    population['facts']['edge'] = [{'source': f'N{index}', 'target': f'N{index + 1}'} for index in range(100)] + [{'source': 'X', 'target': {'$opaque': 'unreadable-node'}}]
    population['facts']['reaches'] = []
    population['facts']['visited'] = []
    population['facts']['noise'] = [{'token': f'{index:06d}-' + 'x' * 1000} for index in range(8200)]
    model_path = tmp_path / 'model.orm.yaml'
    with model_path.open('w') as stream:
        YAML().dump(model, stream)
    population_path = tmp_path / 'population.json'
    population_path.write_text(json.dumps(population, ensure_ascii=False) + '\n')
    assert 8000000 < population_path.stat().st_size < MAX_POPULATION_BYTES
    loaded = load_model(model_path)
    admitted = load_population(population_path, model=loaded)
    started = perf_counter()
    view = structured_extension_view(loaded, admitted)
    elapsed = perf_counter() - started
    assert elapsed < 60.0, elapsed
    assert len(view.facts['reaches']) == 5050
    assert len(view.possible['reaches']) == 5151
    assert view.work.fixpoint_iterations <= 105
