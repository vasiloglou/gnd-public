from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML as RuamelYAML

FIXTURE = Path(__file__).resolve().parents[1] / 'fixtures/v62-phase1'
CASES_DOC = {'model': 'models/static.orm.yaml'}
YAML = RuamelYAML(typ='safe')

def document(variant: str='base') -> dict[str, Any]:
    doc = YAML.load((FIXTURE / CASES_DOC['model']).read_text(encoding='utf-8'))
    doc = copy.deepcopy(doc)
    operation = doc['operations'][0]
    if variant == 'base':
        return doc
    if variant == 'one_stratum':
        doc['fact_types'] = [fact for fact in doc['fact_types'] if fact['id'] != 'final_eligible']
        operation['preconditions'][0]['require'][0]['fact_type'] = 'eligible'
        return doc
    if variant == 'bad_pre_ref':
        operation['preconditions'][0]['require'][0]['fact_type'] = 'absent_fact'
        return doc
    if variant == 'subtype_shape':
        doc['object_types'].append({'id': 'special_item', 'name': 'Special item', 'kind': 'value', 'primitive': 'String', 'subtype_of': ['item'], 'inherits_reference': True})
        doc['fact_types'][0]['roles'][0]['object_type'] = 'special_item'
        doc['fact_types'][0]['reading'] = '{SpecialItem} has evidence'
        return doc
    if variant == 'objectified_shape':
        doc['object_types'].extend([{'id': 'evidence_id', 'name': 'Evidence id', 'kind': 'value', 'primitive': 'String'}, {'id': 'evidence_record', 'name': 'Evidence record', 'kind': 'entity', 'reference': {'mode': 'popular', 'value_type': 'evidence_id'}}])
        doc['fact_types'][0]['objectified_as'] = 'evidence_record'
        doc['fact_types'][0]['objectification_independent'] = True
        return doc
    if variant == 'inherited_reference_shape':
        doc['object_types'].extend([{'id': 'item_id', 'name': 'Item id', 'kind': 'value', 'primitive': 'String'}, {'id': 'item_entity', 'name': 'Item entity', 'kind': 'entity', 'reference': {'mode': 'popular', 'value_type': 'item_id'}}, {'id': 'special_entity', 'name': 'Special entity', 'kind': 'entity', 'subtype_of': ['item_entity'], 'inherits_reference': True}])
        for fact in doc['fact_types']:
            for role in fact['roles']:
                if role['object_type'] == 'item':
                    role['object_type'] = 'special_entity'
            fact['reading'] = fact['reading'].replace('{Item}', '{SpecialEntity}')
        operation['parameters'][0]['object_type'] = 'special_entity'
        operation['reading'] = operation['reading'].replace('{Item}', '{SpecialEntity}')
        return doc
    if variant == 'touch_derived_assert':
        operation['effects'] = [{'assert': {'fact_type': 'final_eligible', 'bind': {'item': '$item'}}}]
        return doc
    if variant == 'touch_derived_retract':
        operation['effects'] = [{'retract': {'fact_type': 'final_eligible', 'bind': {'item': '$item'}}}]
        return doc
    target = {'touch_positive': 'evidence', 'touch_negative': 'blocked', 'touch_semiderived': 'eligible', 'touch_derived': 'final_eligible'}[variant]
    operation['effects'] = [{'retract': {'fact_type': target, 'bind': {'item': '$item'}}}, {'assert': {'fact_type': target, 'bind': {'item': '$item'}}}]
    return doc
