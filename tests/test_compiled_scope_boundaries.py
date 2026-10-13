"""Opt-in generated findings cannot enlarge historical proof coverage."""
from gnd.assurance import phase3_scope_ids
from gnd.branches import REGISTRY
from gnd.constraint_families import FAMILIES
from gnd.semantic_adapter import _FAMILIES


def test_compiled_findings_are_registered_outside_frozen_assurance():
    compiled = {row.scope_id for row in REGISTRY
                if row.surface == 'snapshot' and row.family == 'compiled-subset'}
    assert compiled
    assert compiled.isdisjoint(phase3_scope_ids())
    assert 'compiled-subset' not in FAMILIES
    assert set(_FAMILIES) == set(FAMILIES)
