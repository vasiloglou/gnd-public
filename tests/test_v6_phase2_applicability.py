from __future__ import annotations

import json
from pathlib import Path

import pytest

from gnd import checker, correspondence
from gnd import semantic_registry as registry
from gnd.model import load_model
from gnd.population import Population, load_population

ROOT = Path(__file__).resolve().parents[1]

def _mandatory_inputs():
    root = ROOT / 'tests/fixtures/public-applicability'
    model = load_model(root / 'c01/model.orm.yaml')
    return (model, [load_population(root / f'{case}/population.yaml', model=model) for case in ('c01', 'c02')])

def test_opposite_outcomes_do_not_shrink_applicability(monkeypatch):
    model, (good, bad) = _mandatory_inputs()
    with monkeypatch.context() as context:

        def forbidden(*args, **kwargs):
            raise AssertionError('verdict evaluation is not applicability')
        context.setattr(checker, 'check', forbidden)
        context.setattr(checker, 'phase1_decide', forbidden)
        context.setattr(correspondence, 'evaluate_snapshot', forbidden)
        good_scope = registry.applicable_scope_ids(model, good)
        bad_scope = registry.applicable_scope_ids(model, bad)
    assert good_scope == bad_scope
    assert {'snapshot:mandatory:phase1-inline:clean', 'snapshot:mandatory:phase1-inline:violated:alethic', 'snapshot:mandatory:phase1-inline:vacuous-empty-subject', 'snapshot:mandatory:phase1-inline:vacuous-coverage-omission'} <= set(good_scope)
    assert 'snapshot:mandatory:inline:clean' not in good_scope
    assert 'snapshot:mandatory:phase1-inline:violated:deontic' not in good_scope
    assert checker.band(checker.check(model, good)) == 0
    assert checker.band(checker.check(model, bad)) == 1

def test_applicability_refuses_changed_or_unvalidated_population():
    model, (population, _) = _mandatory_inputs()
    unvalidated = Population.model_validate(population.model_dump())
    assert unvalidated.validated_against is None
    with pytest.raises(checker.UnvalidatedPopulationError):
        registry.applicable_scope_ids(model, unvalidated)
    population.instances['reviewer'].append('r3')
    with pytest.raises(checker.UnvalidatedPopulationError):
        registry.applicable_scope_ids(model, population)

def test_applicability_never_reads_a_declaration(monkeypatch):
    model, (population, _) = _mandatory_inputs()
    expected = registry.applicable_scope_ids(model, population)

    def forbidden(*args, **kwargs):
        raise AssertionError('no evidence file may define applicability')
    monkeypatch.setattr(Path, 'open', forbidden)
    assert registry.applicable_scope_ids(model, population) == expected

def test_a_changed_admission_route_has_a_different_owner(tmp_path):
    model, (population, _) = _mandatory_inputs()
    from ruamel.yaml import YAML
    document = YAML(typ='safe').load((ROOT / 'tests/fixtures/public-applicability/c01/population.yaml').read_text())
    document['instances']['reviewer'] = [f'r{i}' for i in range(20)]
    path = tmp_path / 'many.yaml'
    path.write_text(json.dumps(document))
    larger = load_population(path, model=model)
    small_scope = registry.applicable_scope_ids(model, population)
    large_scope = registry.applicable_scope_ids(model, larger)
    assert 'snapshot:mandatory:phase1-inline:clean' in small_scope
    assert 'snapshot:mandatory:phase1-inline:clean' not in large_scope
    assert 'snapshot:mandatory:inline:clean' in large_scope
    assert checker.check(model, larger).verdicts[0].scope_id in large_scope
