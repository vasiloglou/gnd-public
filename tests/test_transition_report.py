from __future__ import annotations

import ast
import datetime
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator, ValidationError
from pydantic import ValidationError as PydanticValidationError

from gnd import patterns, transition
from gnd.checker import _identity_key
from gnd.model import load_model
from gnd.report import load_report_schema

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC = REPO_ROOT / 'src' / 'gnd'

def test_no_type_this_phase_defines_carries_an_aggregate_verdict() -> None:
    banned = {'passed', 'ok', 'success', 'summary', 'result', 'verdict_summary', 'clean'}
    for model_type in (transition.TransitionVerdict, transition.StepResult, transition.FrameGrading, transition.TransitionReport):
        fields = set(model_type.model_fields)
        assert not fields & banned, f"{model_type.__name__} carries {sorted(fields & banned)}, an aggregate this phase's report deliberately does not have"
    assert set(transition.TransitionReport.model_fields) == {'pre_snapshot', 'pre_snapshot_verdicts', 'steps', 'frame_grading', 'frame_verdicts', 'post_snapshot'}

def test_band_never_returns_3() -> None:
    source = ast.parse((SRC / 'transition.py').read_text(encoding='utf-8'))
    function = next(node for node in ast.walk(source) if isinstance(node, ast.FunctionDef) and node.name == 'band')
    returned = {node.value.value for node in ast.walk(function) if isinstance(node, ast.Return) and isinstance(node.value, ast.Constant)}
    assert returned == {0, 1, 2, 4}, f'band() returns {sorted(returned)}'

@pytest.mark.parametrize(('kwargs', 'why'), [({'verdict': 'fail', 'reason_code': 'transition:dynamic-subject-not-functional'}, 'a reason_code on a verdict that is not unchecked'), ({'verdict': 'unchecked', 'reason_code': None}, 'an unchecked verdict with no reason_code')])
def test_the_reason_code_iff_invariant_is_enforced_by_the_model(kwargs: dict[str, Any], why: str) -> None:
    base = {'scope_id': 'transition:dynamic-rule:n-a:unchecked-nonfunctional', 'family': 'step', 'locator': '$.steps[1]', 'kind': 'dynamic-rule', 'modality': 'alethic', 'message': 'fixture'}
    with pytest.raises(PydanticValidationError):
        transition.TransitionVerdict(**base, **kwargs)

@pytest.mark.parametrize(('family', 'direction', 'why'), [('step', 'undeclared-assert', 'a direction on a non-frame finding'), ('frame', None, 'a frame finding with no direction')])
def test_the_direction_iff_invariant_is_enforced_by_the_model(family: str, direction: str | None, why: str) -> None:
    with pytest.raises(PydanticValidationError):
        transition.TransitionVerdict(scope_id='transition:frame-delta:undeclared-assert:violated:alethic' if family == 'frame' else 'transition:precondition:n-a:violated:alethic', family=family, locator='$.x', kind='frame-delta' if family == 'frame' else 'precondition', modality='alethic', verdict='fail', message='fixture', direction=direction)

def test_a_step_verdict_may_carry_a_fact_type() -> None:
    verdict = transition.TransitionVerdict(scope_id='transition:retract-target:n-a:violated:alethic', family='step', locator='$.steps[1].effects[0].retract', kind='retract-target', modality='alethic', verdict='fail', message='fixture', fact_type='chain_has_threshold')
    assert verdict.fact_type == 'chain_has_threshold'
    assert verdict.direction is None

@pytest.mark.parametrize(('payload', 'why'), [({'family': 'step', 'locator': '$.x', 'kind': 'precondition', 'modality': 'alethic', 'verdict': 'fail', 'message': 'm', 'reason_code': 'transition:dynamic-subject-not-functional'}, 'reason_code on a non-unchecked verdict'), ({'family': 'step', 'locator': '$.x', 'kind': 'dynamic-rule', 'modality': 'alethic', 'verdict': 'unchecked', 'message': 'm'}, 'unchecked with no reason_code'), ({'family': 'step', 'locator': '$.x', 'kind': 'precondition', 'modality': 'alethic', 'verdict': 'fail', 'message': 'm', 'direction': 'undeclared-assert'}, 'direction on a non-frame family')])
def test_the_payload_schema_enforces_the_same_two_invariants(payload: dict[str, Any], why: str) -> None:
    schema = load_report_schema()
    schema = schema.get('$defs', {}).get('legacy_reference_report', schema)
    verdict_schema = schema['properties']['transition']['oneOf'][1]['properties']['frame_verdicts']['oneOf'][1]['items']
    with pytest.raises(ValidationError):
        Draft202012Validator(verdict_schema).validate(payload)

def test_a_v1_model_an_absent_section_and_an_empty_one_share_one_digest() -> None:
    empty = transition.operations_digest([])
    assert transition.operations_digest(None) == empty
    v1 = load_model(REPO_ROOT / 'tests' / 'fixtures' / 'models' / 'full_vocabulary.orm.yaml')
    assert v1.operations == []
    assert transition.operations_digest(v1.operations) == empty

def test_the_digest_is_total_over_a_model_that_validates() -> None:
    quoted = [{'id': 'op', 'provenance': {'added_on': '2026-08-15'}}]
    unquoted = [{'id': 'op', 'provenance': {'added_on': datetime.date(2026, 8, 15)}}]
    assert transition.operations_digest(unquoted) == transition.operations_digest(quoted)

def test_a_value_outside_the_closed_set_is_refused_with_a_rule_id() -> None:
    with pytest.raises(transition.TransitionLoadError) as raised:
        transition.operations_digest([{'id': 'op', 'provenance': {'blob': {1, 2}}}])
    assert [issue.rule_id for issue in raised.value.issues] == ['transition:operations-digest-unrepresentable']

def test_the_transition_reason_codes_live_in_transition_py() -> None:
    source = (SRC / 'transition.py').read_text(encoding='utf-8')
    for code in ('transition:dynamic-subject-not-functional', 'transition:intermediate-state-unloadable'):
        assert code in source

def test_the_public_population_loader_signature_is_unchanged() -> None:
    import inspect

    from gnd.population import load_population_bytes
    signature = inspect.signature(load_population_bytes)
    assert list(signature.parameters) == ['data', 'source', 'model']
    assert signature.parameters['source'].kind is inspect.Parameter.KEYWORD_ONLY
    assert signature.parameters['model'].kind is inspect.Parameter.KEYWORD_ONLY

@pytest.mark.parametrize('value', [1, 1.0, True, False, '1', None, 0, 0.0, '', [1, 2], {'a': 1}])
def test_patterns_compares_values_exactly_as_the_checker_does(value: Any) -> None:
    fact = {'role': value}
    assert patterns.matches(fact, {'role': value}, identity=_identity_key)
    for other in (1, 1.0, True, '1', None):
        expected = _identity_key(value) == _identity_key(other)
        assert patterns.matches(fact, {'role': other}, identity=_identity_key) is expected

def test_patterns_imports_nothing_but_the_standard_library() -> None:
    tree = ast.parse((SRC / 'patterns.py').read_text(encoding='utf-8'))
    imported = {(node.module or '').split('.')[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)} | {alias.name.split('.')[0] for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}
    assert not {name for name in imported if name.startswith('gnd')}, imported

def test_the_retired_effect_order_sentence_has_not_come_back() -> None:
    doc = SRC / 'skills' / 'gnd-orm-core' / 'references' / 'representation-format.md'
    text = doc.read_text(encoding='utf-8')
    assert 'later effects win' not in text
    assert 'written order' in text or 'order is not semantic' in text, 'the replacement statement is missing -- deleting the wrong rule is only half the repair'
_SUBTYPE_MODEL = '\nversion: 2\nmodel_id: "urn:gnd-fixture:transition-subtype@1"\nsource: { kind: explicit, confidence: high }\nobject_types:\n  - { id: party_id, name: PartyId, kind: value, primitive: String }\n  - id: party\n    name: Party\n    kind: entity\n    reference: { mode: popular, value_type: party_id }\n  - id: employee\n    name: Employee\n    kind: entity\n    subtype_of: [party]\n    inherits_reference: true\nfact_types:\n  - id: party_is_active\n    reading: "{Party} is active"\n    roles:\n      - { object_type: party, role_name: party }\n  - id: employee_is_onsite\n    reading: "{Employee} is onsite"\n    roles:\n      - { object_type: employee, role_name: employee }\noperations:\n  - id: activate_party\n    reading: "{Party} is activated"\n    parameters:\n      - { name: party, object_type: party }\n    effects:\n      - assert: { fact_type: party_is_active, bind: { party: "$party" } }\n    frame: { modality: alethic }\n    source: explicit\n    status: confirmed\n    provenance: { csdp_step: 7, dialogue_turn: 1 }\n'

def test_the_touched_union_does_not_expand_through_the_subtype_hierarchy(tmp_path) -> None:
    path = tmp_path / 'subtype.orm.yaml'
    path.write_text(_SUBTYPE_MODEL, encoding='utf-8')
    model = load_model(path)
    union = transition.touched_fact_types(model, [{'op': 'activate_party', 'bindings': {}}])
    assert union == {'party_is_active'}, f'the touched union expanded through the subtype hierarchy: {sorted(union)}'
