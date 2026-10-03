from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from gnd import checker
from gnd.checker import _base_relations, _python_extension_calculator
from gnd.model import ModelValidationError, load_model
from gnd.population import PopulationValidationError, load_population

REPO_ROOT = Path(__file__).resolve().parents[1]
CORPUS = REPO_ROOT / 'tests' / 'fixtures' / 'derivation-evaluation'
CASES = [{'id': 'P2-038', 'branch': 'eval:depth3-dependency-order', 'path': 'cases/eval-depth3-dependency-order', 'profile': 'chain', 'status': 'red-missing-lane', 'question': 'Does eval:depth3-dependency-order reach its own declared boundary after its fixture preconditions are established?', 'expected': 'The exact dependency-first order is low, middle, top and yields the hand-computed non-empty top extension.'}, {'id': 'P2-071', 'branch': 'cost:chain-counted', 'path': 'cases/cost-chain-counted', 'profile': 'chain', 'status': 'red-missing-lane', 'question': 'Does cost:chain-counted reach its own declared boundary after its fixture preconditions are established?', 'expected': 'The exact named join-work event ledger stays within its declared ceiling, and the seeded rescan mutation exceeds it.'}, {'id': 'P2-073', 'branch': 'cost:quadratic-mutation-red', 'path': 'cases/cost-quadratic-mutation-red', 'profile': 'structured', 'status': 'red-missing-lane', 'question': 'Does cost:quadratic-mutation-red reach its own declared boundary after its fixture preconditions are established?', 'expected': 'The exact named join-work event ledger stays within its declared ceiling, and the seeded rescan mutation exceeds it.'}]
A8_MIGRATED_BRANCHES = frozenset({'obligation:unlisted-derived-nonempty-computed', 'obligation:unlisted-semiderived-nonempty-computed', 'constraint:unlisted-derived-claim-inert', 'constraint:mandatory-uncovered-vacuous-plus-band4'})

def _paths(case: dict[str, Any]) -> tuple[Path, Path]:
    root = CORPUS / str(case['path'])
    return (root / 'model.orm.yaml', root / 'population.yaml')

def _structured_rules(model: Any) -> list[Any]:
    return [fact_type.get('derivation_rule') for fact_type in model.fact_types if isinstance(fact_type.get('derivation_rule'), dict)]

def _assert_preconditions(case: dict[str, Any]) -> tuple[Any | None, Any | None]:
    """Establish this case's legal input/refusal shape before any RED sentinel."""
    model_path, population_path = _paths(case)
    profile = str(case['profile'])
    if profile == 'invalid-model':
        with pytest.raises(ModelValidationError):
            load_model(model_path)
        return (None, None)
    model = load_model(model_path)
    if profile in {'nonstructured', 'string-only'}:
        assert not _structured_rules(model), case['id']
    else:
        assert _structured_rules(model), case['id']
    if profile == 'population-refusal' or str(case['branch']) in A8_MIGRATED_BRANCHES:
        with pytest.raises(PopulationValidationError) as excinfo:
            load_population(population_path, model=model)
        if str(case['branch']) in A8_MIGRATED_BRANCHES:
            assert [issue.rule_id for issue in excinfo.value.issues] == ['population:uncovered-structured-derived-facts']
        return (model, None)
    population = load_population(population_path, model=model)
    assert population.matches_validation_marker(model)
    if profile == 'string-only':
        assert all(not isinstance(fact_type.get('derivation_rule'), dict) for fact_type in model.fact_types)
    if profile.startswith('mixed-'):
        rules = [fact_type.get('derivation_rule') for fact_type in model.fact_types]
        assert any(isinstance(rule, dict) for rule in rules)
        assert any(isinstance(rule, str) for rule in rules)
        assert ('legacy_result' in population.covers) == (profile == 'mixed-listed')
    if profile.startswith('unlisted-'):
        assert 'result' not in population.covers
        if profile.endswith('-empty'):
            assert population.facts['seed'] == []
        else:
            assert population.facts['seed']
    if profile == 'dollar-literal':
        assert any(atom.get('bind', {}).get('tag') == '$' for fact_type in model.fact_types for atom in (fact_type.get('derivation_rule', {}).get('body', []) if isinstance(fact_type.get('derivation_rule'), dict) else []))
    if profile == 'chain':
        assert [fact_type['id'] for fact_type in model.fact_types][-3:] == ['low', 'middle', 'top']
    if profile == 'disconnected':
        rule = next(fact_type['derivation_rule'] for fact_type in model.fact_types if fact_type['id'] == 'result')
        assert len(rule['body']) == 2
    if profile == 'unresolved':
        from gnd.popvalidate import resolve_primitive
        assert resolve_primitive('mass', model) is None
    if profile == 'primitives':
        primitives = {object_type.get('primitive') for object_type in model.object_types if object_type.get('primitive') is not None}
        assert primitives == {'String', 'Integer', 'Float', 'Number', 'Date', 'DateTime', 'Boolean', 'Binary'}
    return (model, population)

def _loaded(case: dict[str, Any]) -> tuple[Any, Any]:
    model, population = _assert_preconditions(case)
    assert model is not None and population is not None
    return (model, population)

def test_quadratic_join_mutation_reds(monkeypatch: pytest.MonkeyPatch) -> None:
    """A seeded nested rescan breaks the frozen event ceiling, as T2.12 requires."""
    case = next(case for case in CASES if case['branch'] == 'cost:quadratic-mutation-red')
    model, population = _loaded(case)
    relations = _base_relations(model, population)
    expected = vars(_python_extension_calculator(model, relations).counted_operations).copy()
    original = checker._joined_bindings

    def nested_rescan(atoms: Any, facts: Any, *, variable_of: Any, work: Any):
        bindings = original(atoms, facts, variable_of=variable_of, work=work)
        if work is not None:
            for atom in atoms:
                rows = facts.get(str(atom.get('fact_type')), ())
                for _left in rows:
                    for _right in rows:
                        work.atom_role_terms_read += 1
        return bindings
    with monkeypatch.context() as mutation:
        mutation.setattr(checker, '_joined_bindings', nested_rescan)
        mutated = vars(_python_extension_calculator(model, relations).counted_operations)
    assert mutated != expected
    with pytest.raises(AssertionError):
        assert mutated == expected

def test_relation_materialization_is_linear_in_strata(monkeypatch: pytest.MonkeyPatch) -> None:
    """Each relation map is materialized once, then only the new stratum is added."""
    case = next(case for case in CASES if case['branch'] == 'cost:chain-counted')
    model, population = _loaded(case)
    relations = _base_relations(model, population)
    sizes: list[int] = []
    original = checker._relation_facts

    def traced(current: Any):
        sizes.append(len(current))
        return original(current)
    monkeypatch.setattr(checker, '_relation_facts', traced)
    _python_extension_calculator(model, relations)
    assert sizes == [len(relations), 1, 1, 1]

def test_dependency_direction_mutation_reds(monkeypatch: pytest.MonkeyPatch) -> None:
    case = next(case for case in CASES if case['branch'] == 'eval:depth3-dependency-order')
    model, population = _loaded(case)
    relations = _base_relations(model, population)
    expected = _python_extension_calculator(model, relations).extensions
    assert expected['top'].rows == (('alpha',),)
    original = checker.derivation_strata
    for mutated_order in (lambda document: list(reversed(original(document))), lambda document: [component for component in original(document) if 'middle' not in component]):
        with monkeypatch.context() as mutation:
            mutation.setattr(checker, 'derivation_strata', mutated_order)
            changed = _python_extension_calculator(model, relations).extensions
        assert changed['top'].rows == ()
        with pytest.raises(AssertionError):
            assert changed['top'].rows == expected['top'].rows
