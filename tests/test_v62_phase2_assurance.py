from __future__ import annotations

from support.v62_phase2_corpus import ANSWERS, FIXTURE, population, steps

from gnd.api import transition

SCOPE = 'composition:derivation-view:dynamic:applied'

def test_a02_dynamic_composition_is_uncovered_and_never_proof_backed() -> None:
    payload = transition(FIXTURE / 'models/dynamic.orm.yaml', population('pre_open'), steps(), population('post_resolved'))
    assurance = payload['assurance']
    assert assurance['assurance_level'] == ANSWERS['A02']['assurance']
    assert SCOPE in assurance['uncovered_applicable_scope_ids']
    assert assurance['assurance_level'] != 'proof-backed'
