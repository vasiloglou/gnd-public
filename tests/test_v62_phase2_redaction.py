from __future__ import annotations

import json

from support.v62_phase2_corpus import FIXTURE, population, steps

from gnd.api import transition
from gnd.model import load_model
from gnd.redaction import RedactionPolicy, _project_transition

CANARY = 'SECRET-TICKET-314159'

def test_p03_all_derived_change_rows_use_the_existing_projection() -> None:
    payload = transition(FIXTURE / 'models/dynamic.orm.yaml', population('pre_open'), steps(), population('post_resolved'))
    encoded = json.dumps(payload['transition']['steps'][0]['derived_changes'], sort_keys=True)
    assert CANARY not in encoded
    changes = payload['transition']['steps'][0]['derived_changes']
    assert changes[0]['added'][0]['ticket'] != CANARY

def test_projected_rows_are_deduplicated_after_identity_collapse() -> None:
    model = load_model(FIXTURE / 'models/dynamic.orm.yaml')
    block = {'pre_snapshot': {}, 'post_snapshot': {}, 'steps': [{'operation': 'add_evidence', 'bindings': {}, 'verdicts': [], 'intermediate': {}, 'derived_changes': [{'fact_type': 'ready', 'added': [{'ticket': 'A'}, {'ticket': 'B'}], 'removed': []}]}]}
    _project_transition(block, RedactionPolicy.from_model(model))
    assert len(block['steps'][0]['derived_changes'][0]['added']) == 1
