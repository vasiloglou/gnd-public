"""Authored current alias-schema boundaries; no private consumer corpus claim."""
import json

import pytest
from jsonschema import Draft202012Validator, ValidationError
from support.repository import REPO_ROOT


def test_public_alias_schema_admits_owned_sample_and_refuses_all_original_dirty_shapes():
    schema = json.loads((REPO_ROOT / 'src/gnd/rai-alias.schema.json').read_text())
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    sample = {'schema_version': 1, 'dialect': 'rai-orm',
              'source': {'artifact': 'public/owned.orm.yaml', 'commit': None, 'sha256': '0' * 64},
              'output': {'filename': 'model.orm.yaml', 'sha256': '1' * 64},
              'roles': [{'source_pointer': '/fact_types/0/roles/0', 'source_name': 'Item',
                         'output_pointer': '/fact_types/0/roles/0', 'output_name': 'item'}],
              'constraints': [{'source_pointer': '/constraints/0',
                               'output_pointer': '/fact_types/0/constraints/0', 'rewrite': 'ring-placement'}]}
    validator.validate(sample)
    for dirty in (
        {**sample, "surprise": True},
        {key: value for key, value in sample.items() if key != "roles"},
        {**sample, "schema_version": "1"},
        {**sample, "source": {**sample["source"], "sha256": 7}},
        {**sample, "source": {**sample["source"], "surprise": True}},
        {**sample, "source": {key: value for key, value in sample["source"].items() if key != "commit"}},
        {**sample, "output": {**sample["output"], "surprise": True}},
        {**sample, "output": {**sample["output"], "filename": 7}},
        {**sample, "roles": [{**sample["roles"][0], "surprise": True}]},
        {**sample, "roles": [{key: value for key, value in sample["roles"][0].items() if key != "source_name"}, *sample["roles"][1:]]},
        {**sample, "roles": [{**sample["roles"][0], "source_pointer": 7}, *sample["roles"][1:]]},
        {**sample, "constraints": [{**sample["constraints"][0], "surprise": True}, *sample["constraints"][1:]]},
        {**sample, "constraints": [{key: value for key, value in sample["constraints"][0].items() if key != "rewrite"}, *sample["constraints"][1:]]},
    ):
        with pytest.raises(ValidationError):
            validator.validate(dirty)


def test_owned_import_rewrites_all_four_classes_in_order_and_identity_stays_exact(tmp_path):
    from gnd.model import load_model_bytes
    from gnd.rai_import import RaiImportRequest, plan_rai_import

    source_bytes = b'''version: 1
source: { kind: text-conversation, confidence: standard, mode: one-shot }
object_types:
  - { id: node, name: Node, kind: value, primitive: String }
fact_types:
  - id: node_precedes_node
    reading: "{Node:Left} precedes {Node:Right}"
    roles:
      - { object_type: node, role_name: Left }
      - { object_type: node, role_name: Right }
    constraints:
      - { type: uniqueness, roles: [Left], source: explicit, status: confirmed, provenance: { user_quote: Each left node precedes at most one right node. } }
      - { type: mandatory, role: Left, source: explicit, status: confirmed, modality: alethic }
constraints:
  - { type: ring, variant: acyclic, fact_type: node_precedes_node, source: explicit, status: confirmed, modality: alethic, provenance: { user_quote: Precedence is acyclic. } }
rejected_proposals: []
'''
    source = tmp_path / 'owned.orm.yaml'
    source.write_bytes(source_bytes)
    result = plan_rai_import(RaiImportRequest(source, tmp_path / 'out', 'public/owned.orm.yaml', 'synthetic-owned-input'))
    assert result.rewrites == ('modality', 'role-name', 'ring-placement', 'provenance')
    assert load_model_bytes(result.model_bytes, source='owned-output.orm.yaml')
    aliases = json.loads(result.alias_bytes)
    assert len(aliases['roles']) == 2 and len(aliases['constraints']) == 1
    assert aliases['source']['artifact'] == 'public/owned.orm.yaml'
    model = load_model_bytes(result.model_bytes, source='owned-output.orm.yaml')
    mandatory = next(c for c in model.fact_types[0]['constraints'] if c['type'] == 'mandatory')
    assert (mandatory['source'], mandatory['status'], mandatory['modality']) == ('imported', 'proposed', 'deontic')
    assert mandatory['provenance']['anchor'] == '- id: node_precedes_node'
    assert mandatory['provenance']['anchor'] in source_bytes.decode()
    identity = REPO_ROOT / 'tests/fixtures/v61-phase1/import/identity.source.orm.yaml'
    unchanged = plan_rai_import(RaiImportRequest(identity, tmp_path / 'identity-out', 'public/identity.orm.yaml', None))
    assert unchanged.model_bytes == identity.read_bytes() and unchanged.rewrites == ()
