from __future__ import annotations

from dataclasses import fields

from support.v62_phase2_corpus import FIXTURE, population

from gnd import checker
from gnd.model import load_model
from gnd.population import load_population

MODEL = FIXTURE / 'models/dynamic.orm.yaml'

def _inputs():
    model = load_model(MODEL)
    pre = load_population(population('pre_open'), model=model)
    post = load_population(population('post_resolved'), model=model)
    return (model, pre, post)

def test_s01_full_view_is_byte_equivalent_to_existing_extension_surface() -> None:
    assert hasattr(checker, 'structured_extension_view')
    model, pre, _ = _inputs()
    view = checker.structured_extension_view(model, pre)
    assert view.facts == checker.structured_extension_facts(model, pre)
    assert view.recomputed == ('resolvable', 'ready', 'ticket_score')

def test_s02_empty_refresh_does_zero_work_and_preserves_previous() -> None:
    model, pre, _ = _inputs()
    full = checker.structured_extension_view(model, pre)
    empty = checker.structured_extension_view(model, pre, previous=full.facts, refresh=())
    assert empty.facts == full.facts
    assert empty.recomputed == ()
    assert all(getattr(empty.work, field.name) == 0 for field in fields(empty.work))

def test_s03_transitive_chain_refreshes_both_levels() -> None:
    model, pre, post = _inputs()
    old = checker.structured_extension_view(model, pre)
    refreshed = checker.structured_extension_view(model, post, previous=old.facts, refresh=('resolvable', 'ready'))
    assert refreshed.recomputed == ('resolvable', 'ready')
    assert refreshed.facts['resolvable'] == ({'ticket': 'SECRET-TICKET-314159'},)
    assert refreshed.facts['ready'] == ({'ticket': 'SECRET-TICKET-314159'},)
