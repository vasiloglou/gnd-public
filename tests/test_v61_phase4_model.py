from __future__ import annotations

import copy
import importlib
import json
from pathlib import Path
from typing import Any

import pytest
from ruamel.yaml import YAML

from gnd.model import ModelValidationError, load_model
from gnd.model_verbalization import render_model_verbalization

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'tests/fixtures/v61-phase4'
CASES = json.loads((FIXTURE / 'cases.json').read_text(encoding='utf-8'))
ANSWERS = json.loads((FIXTURE / 'answers.json').read_text(encoding='utf-8'))
FACT_SENTENCE = 'Values of every role are redacted from reports.'
ROLE_SENTENCE = 'Values of this role are redacted from reports.'

def _model_case(identifier: str) -> dict[str, Any]:
    return next(row for row in CASES['models'] if row['id'] == identifier)

def _model_path(identifier: str) -> Path:
    return FIXTURE / _model_case(identifier)['path']

def _policy(identifier: str) -> Any:
    redaction = importlib.import_module('gnd.redaction')
    return redaction.RedactionPolicy.from_model(load_model(_model_path(identifier)))

def _declaration_tuple(declaration: Any) -> tuple[object, ...]:
    return (declaration.case_id, declaration.source, declaration.fact_type, tuple(declaration.roles))

def _assert_model_answers(cases: dict[str, Any]) -> None:
    expected = {'M-00': ((), ()), 'M-01': (('optional_code.code',), ('optional_code.code',)), 'M-02': (('optional_code.*',), ('optional_code.code', 'optional_code.item')), 'M-03': (('optional_code.*', 'optional_code.code'), ('optional_code.code', 'optional_code.item')), 'M-01U': (('optional_code.code',), ('optional_code.code',)), 'P-03W': (('node_links_to.to', 'derived_secret.node'), ('derived_secret.node', 'node_links_to.to')), 'P-02O': (('authorized_code.code', 'optional_code.code', 'item_has_rank.item'), ('authorized_code.code', 'item_has_rank.item', 'optional_code.code'))}
    observed = {row['id']: (tuple(row['declarations']), tuple(row['effective_roles'])) for row in cases['models']}
    assert observed == expected
    assert {row['id'] for row in cases['model_mutations']} == {'M-04A', 'M-04B'}
    assert all(row['expected_exit'] == 3 for row in cases['model_mutations'])
    assert {f'M-{index:02d}' for index in range(1, 6)} <= set(cases['branch_ids'])

def _write_yaml(path: Path, document: dict[str, Any]) -> None:
    yaml = YAML(typ='safe')
    with path.open('w', encoding='utf-8') as handle:
        yaml.dump(document, handle)

def _replace_pointer(document: dict[str, Any], pointer: str, replacement: Any) -> None:
    cursor: Any = document
    parts = [part.replace('~1', '/').replace('~0', '~') for part in pointer.split('/')[1:]]
    for part in parts[:-1]:
        cursor = cursor[int(part)] if isinstance(cursor, list) else cursor[part]
    leaf = parts[-1]
    if isinstance(cursor, list):
        cursor[int(leaf)] = replacement
    else:
        cursor[leaf] = replacement

def test_model_corpus_contract_is_closed_and_narrated() -> None:
    assert CASES['schema_version'] == ANSWERS['schema_version'] == 1
    _assert_model_answers(CASES)
    for row in CASES['models']:
        assert (FIXTURE / row['path']).is_file()
    narrative = (FIXTURE / 'README.md').read_text(encoding='utf-8')
    for identifier in ('M-01', 'M-02', 'M-03', 'M-04', 'M-05'):
        assert identifier in narrative

def test_model_answer_checker_rejects_dirty_effective_role() -> None:
    dirty = copy.deepcopy(CASES)
    _model = next(row for row in dirty['models'] if row['id'] == 'M-01')
    _model['effective_roles'] = ['optional_code.item']
    with pytest.raises(AssertionError):
        _assert_model_answers(dirty)

def test_role_declaration(tmp_path: Path) -> None:
    policy = _policy('M-01')
    assert policy.effective_roles == frozenset({('optional_code', 'code')})
    assert [_declaration_tuple(row) for row in policy.declarations] == [(None, 'role', 'optional_code', ('code',))]
    absent = _policy('M-00')
    assert absent.declarations == ()
    assert absent.effective_roles == frozenset()
    document = YAML(typ='safe').load(_model_path('M-01').read_text(encoding='utf-8'))
    document['fact_types'][1]['roles'][1]['redact'] = False
    false_path = tmp_path / 'role-false.orm.yaml'
    _write_yaml(false_path, document)
    redaction = importlib.import_module('gnd.redaction')
    false_policy = redaction.RedactionPolicy.from_model(load_model(false_path))
    assert false_policy.declarations == ()
    assert false_policy.effective_roles == frozenset()

def test_fact_type_declaration(tmp_path: Path) -> None:
    policy = _policy('M-02')
    assert policy.effective_roles == frozenset({('optional_code', 'item'), ('optional_code', 'code')})
    assert [_declaration_tuple(row) for row in policy.declarations] == [(None, 'fact-type', 'optional_code', ('code', 'item'))]
    document = YAML(typ='safe').load(_model_path('M-02').read_text(encoding='utf-8'))
    document['fact_types'][0]['roles'][1]['redact'] = False
    false_role_path = tmp_path / 'fact-true-role-false.orm.yaml'
    _write_yaml(false_role_path, document)
    redaction = importlib.import_module('gnd.redaction')
    false_role_policy = redaction.RedactionPolicy.from_model(load_model(false_role_path))
    assert false_role_policy.effective_roles == frozenset({('optional_code', 'item'), ('optional_code', 'code')})
    assert [_declaration_tuple(row) for row in false_role_policy.declarations] == [(None, 'fact-type', 'optional_code', ('code', 'item'))]

def test_redundant_declarations_are_retained_and_effective_roles_deduplicate() -> None:
    policy = _policy('M-03')
    assert [_declaration_tuple(row) for row in policy.declarations] == [(None, 'fact-type', 'optional_code', ('code', 'item')), (None, 'role', 'optional_code', ('code',))]
    assert policy.effective_roles == frozenset({('optional_code', 'item'), ('optional_code', 'code')})

@pytest.mark.parametrize('mutation', CASES['model_mutations'], ids=lambda row: row['id'])
def test_non_boolean_and_unknown_redact_forms_refuse(mutation: dict[str, Any], tmp_path: Path) -> None:
    document = YAML(typ='safe').load(_model_path(str(mutation['base'])).read_text(encoding='utf-8'))
    _replace_pointer(document, str(mutation['pointer']), mutation['replacement'])
    candidate = tmp_path / f"{mutation['id']}.orm.yaml"
    _write_yaml(candidate, document)
    with pytest.raises(ModelValidationError) as raised:
        load_model(candidate)
    assert any(issue.path.endswith('.redact') and issue.rule_id == 'jsonschema:type' for issue in raised.value.issues)

def test_verbalization_addresses_each_declaration_once() -> None:
    expected = {'M-00': (0, 0), 'M-01': (0, 1), 'M-02': (1, 0), 'M-03': (1, 1)}
    for identifier, counts in expected.items():
        rendered = render_model_verbalization(_model_path(identifier))
        assert (rendered.count(FACT_SENTENCE), rendered.count(ROLE_SENTENCE)) == counts
