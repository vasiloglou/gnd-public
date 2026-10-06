"""Observed-effect regressions for RF3's independently found stale guards."""
from __future__ import annotations

import importlib
from pathlib import Path

import pytest
from support import public_adapter_mutation_controls

from gnd import extensions
from gnd.model import load_model
from gnd.population import load_population

ROOT = Path(__file__).resolve().parents[1]


def test_adapter_dependency_control_reaches_its_assertions(monkeypatch):
    public_adapter_mutation_controls.test_dependency_graph_and_bare_dollar_literal_are_preserved(monkeypatch)


@pytest.mark.parametrize('helper', ['support.v71_witness_cases', 'support.public_v71_witness_corpus'])
def test_replay_guard_blocks_the_defining_effective_view_calculator(helper, monkeypatch):
    directory = ROOT / 'tests/fixtures/derivation-evaluation/cases/obligation-semiderived-surplus'
    model = load_model(directory / 'model.orm.yaml')
    population = load_population(directory / 'population.yaml', model=model)
    importlib.import_module(helper).no_evaluator(monkeypatch)
    with pytest.raises(AssertionError, match='replay invoked'):
        extensions.effective_view(model, population)


@pytest.mark.parametrize('helper', ['support.v71_witness_cases', 'support.public_v71_witness_corpus'])
@pytest.mark.parametrize('name', [
    '_python_extension_calculator', 'python_extension_calculator',
    '_exact_extension_calculator', 'exact_extension_calculator',
    '_evaluate_stratified_extensions', 'evaluate_stratified_extensions',
    'structured_extension_view', 'evaluate_term', 'materialize_scalar',
])
def test_replay_guard_observes_every_moved_lookup(helper, name, monkeypatch):
    importlib.import_module(helper).no_evaluator(monkeypatch)
    with pytest.raises(AssertionError, match='replay invoked'):
        getattr(extensions, name)()
