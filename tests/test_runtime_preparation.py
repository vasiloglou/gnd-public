"""Direct controls for four pre-existing adaptations selected by Phase 4."""
from copy import deepcopy

import pytest
from jsonschema import Draft202012Validator

from gnd.coverage import _declared_arm_errors
from gnd.model import _derivation_dependency_closures


@pytest.mark.parametrize('reference', [False, True])
@pytest.mark.parametrize('declared', [1, 2, 99])
def test_tagged_union_errors_select_only_claimed_arm(reference, declared):
    arms = [
        {'type': 'object', 'properties': {'schema_version': {'const': 1}}, 'required': ['one']},
        {'type': 'object', 'properties': {'schema_version': {'const': 2}}, 'required': ['two']},
    ]
    schema = {'$defs': {'a': arms[0], 'b': arms[1]}, 'oneOf': [
        {'$ref': '#/$defs/a'}, {'$ref': '#/$defs/b'}
    ] if reference else arms}
    document = {'schema_version': declared}
    error = next(Draft202012Validator(schema).iter_errors(document))
    selected = _declared_arm_errors(error, schema, document)
    if declared == 99:
        assert selected == []
    else:
        assert len(selected) == 1
        assert selected[0].validator == 'required'
        assert selected[0].validator_value == ['one' if declared == 1 else 'two']


def test_nested_union_uses_inner_schema_and_relative_arm():
    inner = {'oneOf': [
        {'properties': {'schema_version': {'const': 10}}, 'required': ['ten']},
        {'properties': {'schema_version': {'const': 20}}, 'required': ['twenty']},
    ]}
    schema = {'oneOf': [
        {'properties': {'schema_version': {'const': 1}, 'nested': inner}},
        {'properties': {'schema_version': {'const': 2}}, 'required': ['other']},
    ]}
    document = {'schema_version': 1, 'nested': {'schema_version': 20}}
    error = next(Draft202012Validator(schema).iter_errors(document))
    selected = _declared_arm_errors(error, schema, document)
    assert len(selected) == 1
    assert selected[0].validator == 'required'
    assert selected[0].validator_value == ['twenty']
    assert list(selected[0].absolute_path) == ['nested']


@pytest.mark.parametrize('identifier', ['derived', None, 17])
def test_derivation_closure_cannot_call_malformed_id_complete(identifier):
    doc = {'version': 3, 'fact_types': [
        {'id': 'asserted'},
        {'id': identifier, 'derivation': 'derived', 'derivation_rule': {
            'body': [{'fact_type': 'asserted', 'bind': {'x': '$x'}}],
            'head': {'x': '$x'},
        }},
    ]}
    closures = _derivation_dependency_closures(deepcopy(doc))
    assert len(closures) == 1
    leaves, complete, _ = next(iter(closures.values()))
    assert leaves == frozenset({'asserted'})
    assert complete == isinstance(identifier, str)


def test_successful_v7_session_has_no_v8_judgment_field(tmp_path):
    from support.v71_session_cases import bundle, session_case

    result = session_case({'branch': 'preparation', 'parameters': {'variant': 'patch-repair'}}, bundle('dispatch', tmp_path))
    assert result['exit_code'] == 0
    assert 'judgment_admission' not in result


def test_registry_owners_resolve_to_real_callables():
    import importlib

    from gnd.semantic_registry import REGISTRY

    for branch in REGISTRY:
        module_name, attribute = branch.production_owner.rsplit('.', 1)
        assert callable(getattr(importlib.import_module(module_name), attribute))


@pytest.mark.parametrize('kind', ['safe', 'rt'])
@pytest.mark.parametrize('stream', [False, True])
def test_scanner_keeps_comment_and_stream_semantics(kind, stream):
    import io

    from ruamel.yaml import YAML

    from gnd.yaml_comments import configure_comment_scanner

    text = '\ufeff# heading\nkey: value # inline\nother: [a, b]\n# trailing\n'
    original = YAML(typ=kind, pure=True)
    configured = configure_comment_scanner(YAML(typ=kind, pure=True))
    source = io.StringIO(text) if stream else text
    actual = configured.load(source)
    assert actual == original.load(text)
    if kind == 'rt':
        expected_output, actual_output = io.StringIO(), io.StringIO()
        original.dump(original.load(text), expected_output)
        configured.dump(actual, actual_output)
        assert actual_output.getvalue() == expected_output.getvalue()
