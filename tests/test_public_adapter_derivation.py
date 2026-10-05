import json
import math
from pathlib import Path

import pytest

from gnd import checker, correspondence, extensions
from gnd import semantic_adapter as adapter
from gnd import semantic_ir as ir
from gnd.model import load_model
from gnd.population import load_population

ROOT = Path(__file__).resolve().parents[1]

def test_dependency_graph_and_bare_dollar_literal_are_preserved(monkeypatch):

    def forbidden(*args, **kwargs):
        raise AssertionError('the adapter must not evaluate constraints or derive extensions')
    monkeypatch.setattr(checker, 'check', forbidden)
    for name in ('_python_extension_calculator', '_derivation_obligation'):
        monkeypatch.setattr(extensions, name, forbidden)
    monkeypatch.setattr(correspondence, 'evaluate_snapshot', forbidden)
    root = ROOT / 'tests/fixtures/derivation-evaluation/cases'
    directory = root / 'cost-chain-counted'
    model = load_model(directory / 'model.orm.yaml')
    population = load_population(directory / 'population.yaml', model=model)
    snapshot = adapter.adapt_snapshot(model, population)
    assert snapshot.derivation_order == ('low', 'middle', 'top')
    assert {row.fact_type: row.dependencies for row in snapshot.derivations} == {'low': ('seed',), 'middle': ('low',), 'top': ('middle',)}
    assert all(row.components == (('i',),) for row in snapshot.derivations)
    directory = root / 'eval-bare-dollar-literal'
    model = load_model(directory / 'model.orm.yaml')
    population = load_population(directory / 'population.yaml', model=model)
    snapshot = adapter.adapt_snapshot(model, population)
    terms = dict(snapshot.derivations[0].body[0].bindings)
    assert terms['tag'].kind == 'literal' and terms['tag'].raw_literal.token == '$'

def test_semiderived_claims_are_retained_without_computing_extensions(monkeypatch):
    root = ROOT / 'tests/fixtures/derivation-evaluation/cases/obligation-semiderived-surplus'
    model = load_model(root / 'model.orm.yaml')
    population = load_population(root / 'population.yaml', model=model)

    def forbidden(*args, **kwargs):
        raise AssertionError('preserve rules and claims without calculating their meaning')
    monkeypatch.setattr(extensions, '_python_extension_calculator', forbidden)
    result = adapter.adapt_snapshot(model, population)
    assert any(row.derivation == 'semiderived' and row.relation_source == 'computed-extension' for row in result.fact_types)
    for relation in result.relations:
        assert len(relation.rows) == len(population.facts.get(relation.fact_type, []))
    assert result.derivations and result.derivation_order

def test_negated_dependencies_are_not_dropped():
    directory = ROOT / 'tests/fixtures/derivation-evaluation/cases/eval-negated-present'
    model = load_model(directory / 'model.orm.yaml')
    population = load_population(directory / 'population.yaml', model=model)
    rule = adapter.adapt_snapshot(model, population).derivations[0]
    assert rule.dependencies == ('blocked', 'seed')
    assert rule.body[0].fact_type == 'seed'
    assert rule.negate[0].fact_type == 'blocked'

@pytest.mark.parametrize('section', ('body', 'negate'))
def test_admitted_nonfinite_derivation_literal_is_refused_without_crashing(tmp_path, section):
    directory = ROOT / 'tests/fixtures/derivation-evaluation/cases/eval-bare-dollar-literal'
    from ruamel.yaml import YAML
    document = YAML(typ='safe').load((directory / 'model.orm.yaml').read_text())
    document['object_types'][1]['primitive'] = 'Number'
    rule = document['fact_types'][1]['derivation_rule']
    if section == 'negate':
        rule['body'][0]['bind']['tag'] = '$tag'
        rule['negate'] = [{'fact_type': 'item_has_tag', 'bind': {'item': '$i', 'tag': 'OVERFLOW'}}]
    else:
        rule['body'][0]['bind']['tag'] = 'OVERFLOW'
    model_path = tmp_path / 'model.orm.yaml'
    model_path.write_text(json.dumps(document).replace('"OVERFLOW"', '1e999'))
    model = load_model(model_path)
    population_path = tmp_path / 'population.json'
    population_path.write_text(json.dumps({'population': {'model': 'model.orm.yaml', 'source': 'fixture', 'label': 'conforming'}, 'facts': {}}))
    population = load_population(population_path, model=model)
    assert math.isinf(model.fact_types[1]['derivation_rule'][section][0]['bind']['tag'])
    result = adapter.adapt_snapshot(model, population)
    assert not result.finite
    assert result.derivations[0].dependencies == ('item_has_tag',)
    atoms = getattr(result.derivations[0], section)
    term = dict(atoms[0].bindings)['tag']
    assert not term.valid and term.refused == 'non-finite-number'
    assert term.raw_literal is None and term.literal is None
    failure = ir.IRRefusal(f'derivations[result].{section}[0].bindings[tag]', 'non-finite-number')
    assert result.derivations[0].refusals == (failure,)
    assert failure in result.refusals

def test_structured_derived_relation_selection_preserves_coverage(tmp_path):
    from ruamel.yaml import YAML
    directory = ROOT / 'tests/fixtures/derivation-evaluation/cases/obligation-unlisted-derived-empty-computed'
    model = load_model(directory / 'model.orm.yaml')
    document = YAML(typ='safe').load((directory / 'population.yaml').read_text())
    for covers, selected in ((['seed'], 'empty'), (['seed', 'result'], 'claimed')):
        document['population']['covers'] = covers
        population_path = tmp_path / 'population.json'
        population_path.write_text(json.dumps(document))
        population = load_population(population_path, model=model)
        snapshot = adapter.adapt_snapshot(model, population)
        row = next(row for row in snapshot.fact_types if row.id == 'result')
        assert row.structured_rule and row.derivation == 'derived'
        assert row.relation_source == selected

@pytest.mark.parametrize('primitive,pattern,actual,kind', [('Number', True, 1, 'boolean'), ('Date', 'not-a-date', '2026-09-07', 'string')])
def test_derivation_literal_patterns_keep_raw_identity(tmp_path, primitive, pattern, actual, kind):
    from ruamel.yaml import YAML
    directory = ROOT / 'tests/fixtures/derivation-evaluation/cases/eval-bare-dollar-literal'
    document = YAML(typ='safe').load((directory / 'model.orm.yaml').read_text())
    document['object_types'][1]['primitive'] = primitive
    document['fact_types'][1]['derivation_rule']['body'][0]['bind']['tag'] = pattern
    model_path = tmp_path / 'model.orm.yaml'
    model_path.write_text(json.dumps(document))
    model = load_model(model_path)
    population_path = tmp_path / 'population.json'
    population_path.write_text(json.dumps({'population': {'model': 'model.orm.yaml', 'source': 'fixture', 'label': 'boundary', 'covers': ['item_has_tag', 'result']}, 'facts': {'item_has_tag': [{'item': 'alpha', 'tag': actual}], 'result': []}}))
    population = load_population(population_path, model=model)
    report = checker.check(model, population)
    assert report.derivations[0].verdict == 'pass'
    result = adapter.adapt_snapshot(model, population)
    term = dict(result.derivations[0].body[0].bindings)['tag']
    assert term.valid and term.refused == '' and result.finite
    assert term.primitive == primitive and term.raw_literal.kind == kind
    assert term.literal.identity_kind == kind
    assert not result.refusals
