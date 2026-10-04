from __future__ import annotations

from pathlib import Path

import pytest

from gnd.model import load_model
from gnd.population import load_population

FIXTURES = Path(__file__).parent / 'fixtures'
CHECKER = FIXTURES / 'checker'
SKELETON = FIXTURES / 'skeleton'
PAIRINGS = [(CHECKER / 'misc.orm.yaml', CHECKER / 'population.misc_pass.yaml'), (CHECKER / 'misc.orm.yaml', CHECKER / 'population.misc_fail.yaml'), (CHECKER / 'ring.orm.yaml', CHECKER / 'population.ring_pass.yaml'), (CHECKER / 'ring.orm.yaml', CHECKER / 'population.ring_fail.yaml'), (CHECKER / 'setfam.orm.yaml', CHECKER / 'population.setfam_pass.yaml'), (CHECKER / 'setfam.orm.yaml', CHECKER / 'population.setfam_fail.yaml'), (CHECKER / 'setfam.orm.yaml', CHECKER / 'population.empty.yaml'), (CHECKER / 'setfam.orm.yaml', CHECKER / 'population.coverage_omission.yaml'), (CHECKER / 'setfam.orm.yaml', CHECKER / 'population.covers_none.yaml'), (CHECKER / 'setfam.orm.yaml', CHECKER / 'population.precedence.yaml'), (SKELETON / 'model.orm.yaml', SKELETON / 'population.good.yaml'), (SKELETON / 'model.orm.yaml', SKELETON / 'population.good.json'), (SKELETON / 'model.orm.yaml', SKELETON / 'population.bad.yaml'), (SKELETON / 'model.orm.yaml', SKELETON / 'population.vacuous.yaml')]
EXPECTED_PAIRING_COUNT = 14

@pytest.mark.parametrize(('model_path', 'population_path'), PAIRINGS, ids=[f'{m.parent.name}/{m.stem}-x-{p.name}' for m, p in PAIRINGS])
def test_every_fixture_population_conforms_to_its_model(model_path, population_path):
    model = load_model(model_path)
    population = load_population(population_path, model=model)
    assert population.validated_against is model, 'loading with model= must stamp the D-02 marker, or this test would prove nothing about layer 2 having run'

def test_the_pairing_table_covers_every_conforming_fixture_on_disk():
    assert len(PAIRINGS) == EXPECTED_PAIRING_COUNT, f'expected {EXPECTED_PAIRING_COUNT} pairings (the count research measured), got {len(PAIRINGS)}'
    on_disk = {path for directory in (CHECKER, SKELETON) for path in directory.iterdir() if path.name.startswith('population.')}
    tabled = {population for _, population in PAIRINGS}
    assert tabled == on_disk, f'the pairing table and the fixture tree disagree.\non disk but untested: {sorted(p.name for p in on_disk - tabled)}\ntabled but absent:    {sorted(p.name for p in tabled - on_disk)}'
    for model_path, _ in PAIRINGS:
        assert model_path.exists(), f'{model_path} is tabled but absent'
