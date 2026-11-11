"""Query-budget headroom (issue 170): reads moved behind ModelIndex keep their values.

Spec: .gnd-planning/maintenance/2026-11-11-query-budget-headroom/spec.md (T1, T2, T5).
The budget itself is judged by tests/test_rf6_query_policy.py.
"""
import time
from pathlib import Path

import pytest

from gnd.model import ModelValidationError, load_model
from gnd.model_index import ModelIndex

ROOT = Path(__file__).resolve().parents[1]
LARGEST = ROOT / 'tests/fixtures/coverage/positional/library.orm.yaml'


def _models():
    paths = sorted([*ROOT.glob('examples/**/*.orm.yaml'), *ROOT.glob('tests/fixtures/**/*.orm.yaml')])
    for path in paths:
        try:
            yield path, load_model(path)
        except (ModelValidationError, OSError, ValueError):
            continue  # deliberately invalid fixtures are not models


@pytest.fixture(scope='module')
def models():
    loaded = list(_models())
    assert len(loaded) >= 200, len(loaded)  # the comparison must not go vacuous
    return loaded


def test_t1_index_rows_equal_the_models_rows(models):
    for path, model in models:
        shared = list(ModelIndex.for_model(model).iter_fact_types_shared())
        assert shared == list(model.fact_types or []), path


def test_t2_converted_functions_keep_their_values(models):
    from gnd.diff import _structured
    from gnd.synth.frontier import frontier_codes_for

    seen = {'structured': set(), 'anchored': set()}
    for path, model in models:
        rows = list(model.fact_types or [])
        structured = any(row.get('derivation_rule') for row in rows)
        assert _structured(model) is structured, path
        seen['structured'].add(structured)

        anchored = any(c.get('type') == 'anchored' for row in rows for c in row.get('constraints') or [])
        assert ('anchor-non-lexical' in frontier_codes_for(model)) is anchored, path
        seen['anchored'].add(anchored)
    # Both branches of each predicate are present in the fixture set.
    assert seen == {'structured': {True, False}, 'anchored': {True, False}}


def test_shared_rows_are_not_mutated_by_the_converted_readers(models):
    """The index's rows are shared through a cache: a converted reader must leave them equal."""
    from copy import deepcopy

    from gnd.diff import _structured
    from gnd.synth.frontier import frontier_codes_for
    from gnd.vocabulary import render_verbalization

    for path, model in models[:40]:
        before = deepcopy(list(ModelIndex.for_model(model).iter_fact_types_shared()))
        _structured(model)
        frontier_codes_for(model)
        render_verbalization(model)
        assert list(ModelIndex.for_model(model).iter_fact_types_shared()) == before, path


def test_a_non_model_now_raises_type_error():
    """A recorded change: a non-Model raised AttributeError before, TypeError now."""
    from gnd.diff import _structured

    with pytest.raises(TypeError, match='ModelIndex requires a Model'):
        _structured({'fact_types': []})


def test_t5_unscoped_index_reads_stay_cheap():
    model = load_model(LARGEST)
    assert len(model.fact_types) == 19
    started = time.perf_counter()
    for _ in range(10):
        assert sum(1 for _ in ModelIndex.for_model(model).iter_fact_types_shared()) == 19
    # Measured 0.003 s for ten calls at the spec's base; the bound is two orders looser.
    assert time.perf_counter() - started < 1.0


def _count_reads(monkeypatch, reader, model):
    calls = []
    original = ModelIndex.iter_fact_types_shared
    monkeypatch.setattr(ModelIndex, 'iter_fact_types_shared',
                        lambda self: calls.append(1) or original(self))
    reader(model)
    monkeypatch.setattr(ModelIndex, 'iter_fact_types_shared', original)
    return len(calls)


def test_each_converted_reader_reads_the_fact_types_once_per_call(models, monkeypatch):
    """Frequency control: a converted read must not move inside a loop.

    It counts reads of the fact types, not constructions of the index: a reader that
    built the index repeatedly without reading it would pass.
    """
    from gnd.codegen.emit import render_skill_document
    from gnd.coverage import _element_universe
    from gnd.diff import _structured
    from gnd.extract.projection import _build_projection
    from gnd.synth.frontier import frontier_codes_for
    from gnd.vocabulary import render_verbalization

    readers = {
        '_structured': _structured,
        'frontier_codes_for': frontier_codes_for,
        '_build_projection': _build_projection,
        '_element_universe': _element_universe,
        'render_verbalization': render_verbalization,
        'render_skill_document': lambda model: render_skill_document(
            model, model_path='m.orm.yaml', package='pkg', stem='m'),
    }
    # The skill document reads fact types only for a model with a structured derivation.
    structured = next(model for _, model in models
                      if len(model.fact_types) > 1 and any(isinstance(row.get('derivation_rule'), dict) for row in model.fact_types))
    for name, reader in readers.items():
        assert _count_reads(monkeypatch, reader, structured) == 1, name

    def looped(model):  # negative control: one read per fact type
        for _ in model.fact_types:
            list(ModelIndex.for_model(model).iter_fact_types_shared())

    assert _count_reads(monkeypatch, looped, structured) == len(structured.fact_types) > 1
