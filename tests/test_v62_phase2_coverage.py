from __future__ import annotations

import json

from ruamel.yaml import YAML
from support.v62_phase2_corpus import FIXTURE, population, steps

from gnd.api import transition

MODEL = FIXTURE / 'models/dynamic.orm.yaml'
YAML_READER = YAML(typ='safe')

def _without_cover(tmp_path, missing: str):
    doc = YAML_READER.load(population('pre_open').read_text(encoding='utf-8'))
    doc['population']['covers'].remove(missing)
    path = tmp_path / f'missing-{missing}.pop.yaml'
    yaml = YAML()
    yaml.default_flow_style = False
    with path.open('w', encoding='utf-8') as stream:
        yaml.dump(doc, stream)
    return path

def _post_without_claim(tmp_path, missing: str):
    doc = YAML_READER.load(population('post_resolved').read_text(encoding='utf-8'))
    doc['population']['covers'].remove(missing)
    doc['facts'].pop(missing, None)
    path = tmp_path / f'post-without-{missing}.pop.yaml'
    yaml = YAML()
    yaml.default_flow_style = False
    with path.open('w', encoding='utf-8') as stream:
        yaml.dump(doc, stream)
    return path

def test_e01_missing_asserted_leaf_refuses_before_effects(tmp_path) -> None:
    payload = transition(MODEL, _without_cover(tmp_path, 'blocked'), steps(), population('post_resolved'))
    assert payload['exit_code'] == 3
    assert payload['issues'][0]['rule_id'] == 'transition:dynamic-derivation-coverage'

def test_e07_missing_dynamic_head_refuses_before_intermediate_reads(tmp_path) -> None:
    payload = transition(MODEL, _without_cover(tmp_path, 'ready'), steps(), population('post_resolved'))
    assert payload['exit_code'] == 3
    assert payload['issues'][0]['rule_id'] == 'transition:dynamic-derivation-coverage'

def test_dual_coverage_refusal_retains_legacy_frame_precedence(tmp_path) -> None:
    payload = transition(MODEL, _without_cover(tmp_path, 'evidence'), steps(), population('post_resolved'))
    assert payload['exit_code'] == 3
    assert payload['issues'][0]['rule_id'] == 'transition:frame-coverage'

def test_e03_coverage_issue_redacts_instance_canary(tmp_path) -> None:
    payload = transition(MODEL, _without_cover(tmp_path, 'blocked'), steps(), population('post_resolved'))
    assert 'SECRET-TICKET-314159' not in json.dumps(payload, sort_keys=True)

def test_post_that_makes_no_head_claim_does_not_owe_its_closure(tmp_path) -> None:
    payload = transition(MODEL, population('pre_open'), steps(), _post_without_claim(tmp_path, 'ready'), unredacted=True)
    assert payload['transition']['evaluated'] is True
    assert not [issue for issue in payload['issues'] if issue['rule_id'] == 'transition:dynamic-derivation-coverage']
