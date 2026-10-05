from __future__ import annotations

import inspect
import json
import re
from datetime import date
from pathlib import Path
from types import SimpleNamespace
from typing import Literal, get_args, get_origin

import pytest

from gnd import api, redaction, semantic_adapter, semantic_spec
from gnd import model as model_module
from gnd.artifacts import canonical_json_bytes
from gnd.checker import (
    EXACT_DERIVATION_REASON_CODES,
    _FixpointJoinWork,
    _partial_bindings,
    _Wildcard,
)
from gnd.cli import main
from gnd.diff import _tuple_status
from gnd.extract.anchors import lexical_ranges, recognised_ranges, recognition_index
from gnd.model import (
    _layer1_structural,
    derivation_dependencies,
    derivation_dependency_edges,
    derivation_strata,
    load_model,
)
from gnd.population import load_population_bytes
from gnd.redaction import RedactionProjectionError
from gnd.semantic_ir import Scalar
from gnd.terms import evaluate_term, guarded_operand_evaluator


@pytest.mark.parametrize(('kind', 'value', 'source'), [('integer', 1, '1,234.5'), ('integer', 1, '1,23'), ('integer', -1, '--1'), ('decimal', 12.5, '12.50.5'), ('percent', 12.5, '12.5 %%'), ('iso-8601-date', '2024-02-29', '2024-02-29-'), ('iso-8601-date', '2024-02-29', '2024-02-29+01:00')])
def test_malformed_numeric_or_date_token_has_no_prefix_witness(kind, value, source):
    assert recognised_ranges(recognition_index(source, {kind}), kind, value) == []

def test_repeated_source_indexes_only_selected_occurrences():
    import time
    source = 'a ' * 500000
    started = time.monotonic()
    selected = lexical_ranges(source, {'a'}, wanted_occurrences={'a': {0, 499999}})
    assert selected == {'a': {0: (0, 1), 499999: (999998, 999999)}}
    assert time.monotonic() - started < 8

def test_graph_and_schema_diagnostics_are_total_on_huge_integer() -> None:
    huge = 10 ** 5000
    document = {'fact_types': [{'id': 'result', 'derivation_rule': {'body': [{'fact_type': huge, 'bind': {'value': '$value'}}], 'head': {'value': '$value'}}}]}
    assert derivation_dependencies(document) == {'result': {'<unrenderable int>'}}
    assert len(derivation_dependency_edges(document)) == 1
    assert derivation_strata(document) == [('result',)]
    document['fact_types'][0]['derivation_rule'][huge] = 'unknown'
    issue = _layer1_structural(document)[0]
    assert issue.path.endswith('.derivation_rule')
    assert issue.rule_id == 'jsonschema:oneOf'

def test_exact_reason_table_includes_partial_membership() -> None:
    assert 'derived-unknown' in EXACT_DERIVATION_REASON_CODES

def test_compatible_wildcard_join_compacts_equivalent_candidates() -> None:
    count = 5000
    atoms = [{'fact_type': 'left', 'bind': {'v': '$v'}}, {'fact_type': 'right', 'bind': {'v': '$v'}}]
    facts = {'left': [{'v': str(index)} for index in range(count)], 'right': [{'v': _Wildcard('String', ('right', index, 'v'))} for index in range(count)]}
    work = _FixpointJoinWork()
    rows = _partial_bindings(atoms, facts, work)
    assert len(rows) == count
    assert work.join_matches_merged <= count * 2

def test_every_population_emitter_is_registered() -> None:
    rows = {spec.id: spec for spec in redaction.emitter_specs()}
    for emitter_id in ('api-population-verbalization', 'cli-population-verbalization-text', 'cli-population-verbalization-jsonl'):
        assert rows[emitter_id].kind == 'population-verbalization'
        assert 70 in rows[emitter_id].reachable_exits

def test_boolean_number_and_equal_numeric_tokens_sort_by_codec(tmp_path: Path) -> None:
    model_path = tmp_path / 'mixed.orm.yaml'
    model_path.write_text('version: 1\nsource: {kind: text-conversation, confidence: standard, mode: guided}\nobject_types:\n  - {id: mass, name: Mass, kind: entity, reference: {mode: unit-based, unit: kg, measure_type: mass}}\nfact_types:\n  - id: measured\n    reading: "{Mass} is recorded"\n    roles: [{object_type: mass, role_name: mass}]\nconstraints: []\nrejected_proposals: []\n')
    model = load_model(model_path)
    data = {'population': {'model': 'mixed.orm.yaml', 'source': 'fixture', 'covers': ['measured']}, 'instances': {}, 'facts': {'measured': [{'mass': 1}, {'mass': True}, {'mass': 1.0}, {'mass': False}]}}
    population = load_population_bytes(json.dumps(data).encode(), source='mixed.json', model=model)
    result = api.verbalize(model, population)
    assert result['exit_code'] == 0, result['error']
    assert [row['fact_ref']['index'] for row in result['rows']] == [3, 1, 0, 2]

def test_forward_reading_uses_validated_position_even_if_qualifier_disagrees(tmp_path: Path) -> None:
    model_path = tmp_path / 'positional.orm.yaml'
    model_path.write_text('version: 1\nsource: {kind: text-conversation, confidence: standard, mode: guided}\nobject_types:\n  - {id: person, name: Person, kind: value, primitive: String}\nfact_types:\n  - id: relation\n    reading: "{Person:right} meets {Person:left}"\n    roles: [{object_type: person, role_name: left}, {object_type: person, role_name: right}]\nconstraints: []\nrejected_proposals: []\n')
    model = load_model(model_path)
    data = {'population': {'model': 'positional.orm.yaml', 'source': 'fixture', 'covers': ['relation']}, 'instances': {}, 'facts': {'relation': [{'left': 'Ada', 'right': 'Zoe'}]}}
    population = load_population_bytes(json.dumps(data).encode(), source='positional.json', model=model)
    assert api.verbalize(model, population)['rows'][0]['sentence'] == "'Ada' meets 'Zoe'."

def test_cli_projector_fault_has_no_partial_stdout(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:

    def broken(*args, **kwargs):
        raise RedactionProjectionError('forced')
    monkeypatch.setattr(api, 'diff', broken)
    code = main(['diff', 'a.orm.yaml', 'b.orm.yaml', '--format', 'json'])
    captured = capsys.readouterr()
    assert code == 70
    assert captured.out == ''

def test_derived_membership_keeps_boolean_distinct_from_integer() -> None:
    view = SimpleNamespace(facts={'permitted': ({'record': 1},)}, possible={}, unavailable={})
    population = SimpleNamespace(facts={'permitted': ({'record': 1},)})
    assert _tuple_status(view, population, True, 'permitted', {'record': True}, ('record',)) == 'out'

@pytest.mark.parametrize('function,expected', [('date_add', '2024-02-29'), ('date_sub', '2024-02-27')])
def test_guarded_operand_seam_preserves_date_coordinates(function, expected):
    operand = semantic_adapter._guarded_term({'fn': function, 'args': [{'date': '2024-02-28'}, {'duration_days': 1}]}, {})
    evaluator = guarded_operand_evaluator(semantic_spec.guarded_operand_value, Scalar)
    result = evaluator(operand, (), ())
    assert result == semantic_adapter.canonical_scalar(expected, 'Date')
    assert result.num == date.fromisoformat(expected).toordinal()

def test_nested_budget_counts_every_application():
    term = {'fn': 'date_sub', 'args': [{'fn': 'date_add', 'args': [{'date': '2024-02-28'}, {'duration_days': 1}]}, {'duration_days': 1}]}
    work = [9998]
    result = evaluate_term(term, {}, temporal_work=work)
    assert result.value == '2024-02-28'
    assert work == [10000]
    assert evaluate_term(term, {}, temporal_work=work).reason == 'term:temporal-work-limit'

def test_temporal_classifier_and_analyzer_are_total_for_non_string_functions():
    from gnd.terms import analyze_term, uses_temporal
    for function in ([], {}, None, True, 3):
        term = {'fn': function, 'args': []}
        assert not uses_temporal(term)
        assert analyze_term(term, {}).issue == 'semantic:term-function-name'
        assert evaluate_term(term, {}).reason == 'term:function-name'

def test_guarded_operand_seam_refuses_malformed_temporal_operands():
    evaluator = guarded_operand_evaluator(semantic_spec.guarded_operand_value, Scalar)
    for args in ([], [{'date': '2024-01-01'}], [{'date': '2024-01-01'}, 1]):
        operand = semantic_adapter._guarded_term({'fn': 'date_add', 'args': args}, {})
        assert evaluator(operand, (), ()) is None

def test_opaque_temporal_applications_still_observe_the_work_budget():
    term = {'fn': 'date_add', 'args': ['$day', {'duration_days': 1}]}
    work = [10000]
    assert evaluate_term(term, {'day': None}, temporal_work=work).reason == 'term:temporal-work-limit'

def test_current_temporal_rule_emits_a_declared_identifier_family():
    identifiers = set(re.findall('rule_id="([^"]+)"', inspect.getsource(model_module._rule_temporal_language)))
    assert identifiers == {'semantic:guarded-binding-type', 'semantic:temporal-comparison-type', 'semantic:temporal-site'}
    assert model_module._rule_temporal_language in model_module._SEMANTIC_RULES

@pytest.mark.parametrize('policy', [{'metric': 'producer-score', 'direction': 'max'}, {'metric': 'candidate_admitted_unique', 'direction': 'max', 'callback': 'producer'}], ids=['unknown-metric', 'unknown-field'])
def test_result_ranking_policy_uses_the_closed_metric_vocabulary(policy):
    from gnd.exp.session_store import SessionResult
    document = SessionResult(schema_version=6, run_id='rank-control', disposition='budget-exhausted', terminal_reason='control', attempt_count=1, referenced_evidence_digests={}, contract_sha256='a' * 64, ranking_policy=None, best_ranking=None).model_dump(mode='json')
    document['ranking_policy'] = [policy]
    with pytest.raises(ValueError):
        SessionResult.model_validate(document)

def test_candidate_edit_requires_replay_evidence():
    from gnd.exp.session_store import CandidateEdit
    with pytest.raises(ValueError):
        CandidateEdit(mode='patch', patch_path='.gnd-patch.json', patch_raw_sha256=None, base_candidate_sha256='a' * 64, result_candidate_sha256='b' * 64, refusal=None)

def test_patch_extreme_numeric_exponent_refuses_boundedly():
    from gnd.exp.session_patch import PatchRefusal, read_patch_document
    raw = b'{"schema_version":1,"base_candidate_sha256":null,"operations":[{"op":"replace-artifact","artifact":"notes.json","value":1e9999999999999999999999}]}'
    with pytest.raises(PatchRefusal, match='numeric'):
        read_patch_document(raw)

def test_patch_unpaired_surrogate_refuses_boundedly():
    from gnd.exp.session_patch import PatchRefusal, read_patch_document
    raw = b'{"schema_version":1,"base_candidate_sha256":null,"operations":[{"op":"replace-artifact","artifact":"notes.json","value":"\\ud800"}]}'
    with pytest.raises(PatchRefusal):
        read_patch_document(raw)

def test_canonical_json_producer_keeps_legacy_and_exact_number_boundaries():
    from decimal import Decimal
    assert canonical_json_bytes({'z': [1.0, True], 'a': 'Ω'}) == '{"a":"Ω","z":[1.0,true]}\n'.encode()
    assert canonical_json_bytes({'number': Decimal('9007199254740993.0')}, exact_numbers=True) == b'{"number":9007199254740993.0}\n'
    with pytest.raises(ValueError):
        canonical_json_bytes(Decimal('Infinity'), exact_numbers=True)
    with pytest.raises(ValueError):
        canonical_json_bytes({1: 'integer key'}, exact_numbers=True)

def test_current_successor_version_sets_are_closed():
    from typing import get_args

    from gnd.exp.session_contract import DataDrivenContract
    from gnd.exp.session_eval import AttemptFeedback
    from gnd.exp.session_store import AttemptRecord, DeclaredLaunchIntent, SessionResult
    for cls, expected in ((DataDrivenContract, set(range(1, 9))), (AttemptRecord, set(range(1, 11))), (AttemptFeedback, set(range(1, 10))), (SessionResult, set(range(1, 8))), (DeclaredLaunchIntent, {2, 3, 4})):
        assert set(get_args(cls.model_fields['schema_version'].annotation)) == expected

def test_current_schema_readers_refuse_undeclared_version():
    from gnd.exp.session_contract import DataDrivenContract
    from gnd.exp.session_eval import AttemptFeedback
    from gnd.exp.session_store import AttemptRecord, DeclaredLaunchIntent, SessionResult
    for cls in (DataDrivenContract, AttemptFeedback, AttemptRecord, SessionResult, DeclaredLaunchIntent):
        with pytest.raises(ValueError):
            cls.model_validate({'schema_version': 99})


def _literal_values(annotation: object) -> set[object]:
    if get_origin(annotation) is Literal:
        return set(get_args(annotation))
    values: set[object] = set()
    for argument in get_args(annotation):
        values.update(_literal_values(argument))
    return values


def test_declared_launch_preserves_legacy_default_two() -> None:
    from gnd.exp.session_store import DeclaredLaunchIntent

    assert DeclaredLaunchIntent.model_fields['schema_version'].default == 2


def test_attempt_reader_retains_versions_one_through_seven() -> None:
    from gnd.exp.session_store import AttemptRecord

    assert set(range(1, 8)) <= _literal_values(AttemptRecord.model_fields['schema_version'].annotation)
