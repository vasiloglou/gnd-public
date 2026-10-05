from __future__ import annotations

import copy
import inspect
import json
import re
import subprocess
import sys
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
from ruamel.yaml import YAML
from ruamel.yaml.constructor import DuplicateKeyError
from support.public_guarded_temporal_cases import P3_TEMPORAL_REJECTING_CASES

from gnd import model as model_module
from gnd.model import ModelValidationError, load_model, semantic_validate
from gnd.report import PAYLOAD_SCHEMA_VERSION

REPO_ROOT = Path(__file__).resolve().parent.parent
MODELS = REPO_ROOT / 'tests' / 'fixtures' / 'models'
GUARDED_MINIMAL = MODELS / 'guarded_minimal.orm.yaml'
CANONICAL_SCHEMA = REPO_ROOT / 'src' / 'gnd' / 'skills' / 'gnd-orm-core' / 'references' / 'orm-meta.schema.json'
VENDORED_SCHEMA = REPO_ROOT / 'src' / 'gnd' / 'schema' / 'orm-meta.schema.json'

def _load_yaml(path: Path) -> Any:
    yaml = YAML(typ='rt')
    with open(path, encoding='utf-8') as handle:
        return yaml.load(handle)

def _dump_yaml(document: Any, path: Path) -> Path:
    yaml = YAML(typ='rt')
    with open(path, 'w', encoding='utf-8') as handle:
        yaml.dump(document, handle)
    return path

def _run_cli(*args: str, text: bool=True) -> subprocess.CompletedProcess[Any]:
    return subprocess.run([sys.executable, '-m', 'gnd', *args], cwd=REPO_ROOT, capture_output=True, text=text, check=False)

def _rule_ids(error: ModelValidationError) -> set[str]:
    return {issue.rule_id for issue in error.issues}

def _comparison(document: Any) -> Any:
    return document['constraints'][0]

def _atom_consequent(document: Any) -> Any:
    return document['constraints'][1]

def _absence_consequent(document: Any) -> Any:
    return document['constraints'][2]

def test_guarded_schema_shape_and_operator_home() -> None:
    assert CANONICAL_SCHEMA.read_bytes() == VENDORED_SCHEMA.read_bytes()
    schema = json.loads(VENDORED_SCHEMA.read_text(encoding='utf-8'))
    defs = schema['$defs']
    assert defs['comparison_operator'] == {'enum': ['<', '<=', '=', '>=', '>', '!=']}
    assert defs['guarded_comparison']['required'] == ['operator', 'left', 'right']
    assert defs['guarded_comparison']['properties']['left'] == {'$ref': '#/$defs/term'}
    assert defs['guarded_comparison']['properties']['right'] == {'$ref': '#/$defs/term'}
    assert defs['guarded']['required'] == ['type', 'antecedent', 'consequent']
    assert {branch['$ref'] for branch in defs['top_level_constraint']['allOf'][1]['oneOf']} >= {'#/$defs/guarded'}
    assert '#/$defs/guarded' not in {branch['$ref'] for branch in defs['inline_constraint']['allOf'][1]['oneOf']}
    operator_sites = (defs['guarded_comparison']['properties']['operator'], defs['value_comparison_inline']['properties']['operator'], defs['value_comparison_cross']['properties']['operator'], defs['dynamic_rule']['properties']['op'])
    assert operator_sites == ({'$ref': '#/$defs/comparison_operator'},) * 4

def test_guarded_minimal_loads_without_warnings_and_cli_validates() -> None:
    model = load_model(GUARDED_MINIMAL)
    assert model.warnings == []
    assert _run_cli('validate', str(GUARDED_MINIMAL)).returncode == 0

def test_guarded_minimal_exercises_all_three_consequent_kinds() -> None:
    model = load_model(GUARDED_MINIMAL)
    guarded = [constraint for constraint in model.constraints if constraint['type'] == 'guarded']
    assert len(guarded) == 3
    assert {next(iter(constraint['consequent'])) for constraint in guarded} == {'atom', 'comparison', 'absence'}

def _reject_comparison_unbound(document: Any) -> None:
    _comparison(document)['consequent']['comparison']['left'] = '$x'

def _reject_atom_unbound(document: Any) -> None:
    _atom_consequent(document)['consequent']['atom']['bind']['status'] = '$x'

def _reject_absence_unbound(document: Any) -> None:
    _absence_consequent(document)['consequent']['absence']['bind']['status'] = '$x'

def _reject_comparison_type(document: Any) -> None:
    constraint = _comparison(document)
    constraint['antecedent'][0]['bind']['category'] = '$category'
    constraint['consequent']['comparison']['left'] = '$category'

def _reject_antecedent_fact_type(document: Any) -> None:
    _comparison(document)['antecedent'][0]['fact_type'] = 'expense_missing_fact'

def _reject_atom_fact_type(document: Any) -> None:
    _atom_consequent(document)['consequent']['atom']['fact_type'] = 'expense_missing_fact'

def _reject_antecedent_role(document: Any) -> None:
    _comparison(document)['antecedent'][0]['bind']['missing_role'] = '$e'

def _reject_absence_role(document: Any) -> None:
    _absence_consequent(document)['consequent']['absence']['bind']['missing_role'] = '$e'

def _reject_antecedent_missing_role(document: Any) -> None:
    del _comparison(document)['antecedent'][0]['bind']['category']

def _reject_atom_missing_role(document: Any) -> None:
    del _atom_consequent(document)['consequent']['atom']['bind']['status']

def _reject_mixed_consequent(document: Any) -> None:
    _comparison(document)['consequent']['atom'] = {'fact_type': 'expense_has_status', 'bind': {'expense': '$e', 'status': 'review'}}

def _reject_empty_antecedent(document: Any) -> None:
    _comparison(document)['antecedent'] = []

def _reject_operator(document: Any) -> None:
    _comparison(document)['consequent']['comparison']['operator'] = '=>'

def _reject_unknown_guarded_key(document: Any) -> None:
    _comparison(document)['surprise'] = True

def _reject_inline_guarded(document: Any) -> None:
    constraint = document['constraints'].pop(0)
    document['fact_types'][0]['constraints'] = [constraint]

def _reject_missing_antecedent(document: Any) -> None:
    del _comparison(document)['antecedent']

def _reject_missing_consequent(document: Any) -> None:
    del _comparison(document)['consequent']

def _reject_missing_right(document: Any) -> None:
    del _comparison(document)['consequent']['comparison']['right']

def _reject_absence_missing_role(document: Any) -> None:
    del _absence_consequent(document)['consequent']['absence']['bind']['status']

def _reject_missing_left(document: Any) -> None:
    del _comparison(document)['consequent']['comparison']['left']

def _reject_missing_operator(document: Any) -> None:
    del _comparison(document)['consequent']['comparison']['operator']

def _reject_kindless_consequent(document: Any) -> None:
    _comparison(document)['consequent'] = {}

def _reject_var_var_incompatible(document: Any) -> None:
    constraint = _comparison(document)
    constraint['antecedent'][0]['bind']['category'] = '$c'
    constraint['consequent']['comparison']['left'] = '$c'
    constraint['consequent']['comparison']['right'] = '$a'

def _reject_right_side_variable(document: Any) -> None:
    constraint = _comparison(document)
    constraint['antecedent'][0]['bind']['category'] = '$c'
    constraint['consequent']['comparison']['left'] = 2000
    constraint['consequent']['comparison']['right'] = '$c'

def _reject_multiply_bound_incompatible(document: Any) -> None:
    constraint = _comparison(document)
    constraint['antecedent'].append({'fact_type': 'expense_has_status', 'bind': {'expense': '$e', 'status': '$a'}})

def _reject_exists_where_unbound(document: Any) -> None:
    constraint = _comparison(document)
    constraint['consequent'] = {'exists': {'atoms': [{'fact_type': 'expense_has_status', 'bind': {'expense': '$e', 'status': 'review'}}], 'where': [{'operator': '=', 'left': {'fn': 'mod', 'args': ['$unbound', 30]}, 'right': 1}]}}

def _reject_exists_where_unbound_nested(document: Any) -> None:
    constraint = _comparison(document)
    constraint['consequent'] = {'exists': {'atoms': [{'fact_type': 'expense_has_status', 'bind': {'expense': '$e', 'status': 'review'}}], 'where': [{'operator': '=', 'left': '$unknown', 'right': 1}]}}

def _reject_exists_where_type(document: Any) -> None:
    constraint = _comparison(document)
    constraint['consequent'] = {'exists': {'atoms': [{'fact_type': 'expense_has_status', 'bind': {'expense': '$e', 'status': 'review'}}], 'where': [{'operator': '=', 'left': '$a', 'right': 'review'}]}}
REJECTING_CASES: list[tuple[str, Callable[[Any], None], str]] = [('R-01-comparison-unbound', _reject_comparison_unbound, 'semantic:guarded-consequent-ground'), ('R-01b-atom-unbound', _reject_atom_unbound, 'semantic:guarded-consequent-ground'), ('R-01c-absence-unbound', _reject_absence_unbound, 'semantic:guarded-consequent-ground'), ('R-02-comparison-type', _reject_comparison_type, 'semantic:guarded-comparison-type'), ('R-03-antecedent-fact-type', _reject_antecedent_fact_type, 'semantic:guarded-term-ref'), ('R-03b-atom-fact-type', _reject_atom_fact_type, 'semantic:guarded-term-ref'), ('R-04-antecedent-role', _reject_antecedent_role, 'semantic:guarded-term-ref'), ('R-04b-absence-role', _reject_absence_role, 'semantic:guarded-term-ref'), ('R-05-antecedent-missing-role', _reject_antecedent_missing_role, 'semantic:guarded-role-claim'), ('R-05b-atom-missing-role', _reject_atom_missing_role, 'semantic:guarded-role-claim'), ('R-05c-absence-missing-role', _reject_absence_missing_role, 'semantic:guarded-role-claim'), ('R-07-mixed-consequent', _reject_mixed_consequent, 'jsonschema:'), ('R-08-empty-antecedent', _reject_empty_antecedent, 'jsonschema:'), ('R-09-operator', _reject_operator, 'jsonschema:'), ('R-10-unknown-key', _reject_unknown_guarded_key, 'jsonschema:'), ('R-11-inline', _reject_inline_guarded, 'jsonschema:'), ('R-12-missing-antecedent', _reject_missing_antecedent, 'jsonschema:'), ('R-13-missing-consequent', _reject_missing_consequent, 'jsonschema:'), ('R-14-missing-right', _reject_missing_right, 'jsonschema:'), ('R-14b-missing-left', _reject_missing_left, 'jsonschema:'), ('R-14c-missing-operator', _reject_missing_operator, 'jsonschema:'), ('R-15-kindless-consequent', _reject_kindless_consequent, 'jsonschema:'), ('R-16-var-var-type', _reject_var_var_incompatible, 'semantic:guarded-comparison-type'), ('R-17-right-variable-type', _reject_right_side_variable, 'semantic:guarded-comparison-type'), ('R-18-multi-site-type', _reject_multiply_bound_incompatible, 'semantic:guarded-comparison-type'), ('E10A-exists-variable-only-in-where', _reject_exists_where_unbound, 'semantic:guarded-exists-range'), ('E10B-where-variable-neither-antecedent-nor-exists', _reject_exists_where_unbound_nested, 'semantic:guarded-exists-where-bound'), ('exists-where-compatible-types', _reject_exists_where_type, 'semantic:guarded-exists-where-type')]
REJECTING_CASES += P3_TEMPORAL_REJECTING_CASES

@pytest.mark.parametrize(('name', 'edit', 'expected_rule_id'), REJECTING_CASES, ids=[case[0] for case in REJECTING_CASES])
def test_each_guarded_rejecting_case_refuses_load_and_cli(name: str, edit: Callable[[Any], None], expected_rule_id: str, tmp_path: Path) -> None:
    document = copy.deepcopy(_load_yaml(GUARDED_MINIMAL))
    edit(document)
    path = _dump_yaml(document, tmp_path / f'{name}.orm.yaml')
    with pytest.raises(ModelValidationError) as excinfo:
        load_model(path)
    rule_ids = _rule_ids(excinfo.value)
    if expected_rule_id.endswith(':'):
        assert any(rule_id.startswith(expected_rule_id) for rule_id in rule_ids)
    else:
        assert expected_rule_id in rule_ids
    result = _run_cli('validate', str(path))
    assert result.returncode == 3
    if name == 'R-01-comparison-unbound':
        legacy_message = "consequent variables ['$x'] are not introduced by an antecedent bind"
        assert [issue.message for issue in excinfo.value.issues if issue.rule_id == 'semantic:guarded-consequent-ground'] == [legacy_message]
        assert legacy_message in result.stdout + result.stderr

def test_duplicate_bind_key_is_parse_refused_and_cli_exits_three(tmp_path: Path) -> None:
    source = GUARDED_MINIMAL.read_text(encoding='utf-8')
    original = '        bind: { expense: "$e", category: travel }'
    duplicate = '        bind:\n          expense: "$e"\n          expense: "$other"\n          category: travel'
    assert source.count(original) == 2
    path = tmp_path / 'R-06-duplicate-bind.orm.yaml'
    path.write_text(source.replace(original, duplicate, 1), encoding='utf-8')
    with pytest.raises(DuplicateKeyError):
        load_model(path)
    assert _run_cli('validate', str(path)).returncode == 3

def _population_document(*, populated: bool) -> dict[str, Any]:
    fact_types = ['expense_in_category', 'expense_has_amount', 'expense_has_status']
    facts: dict[str, list[dict[str, Any]]] = {fact_type: [] for fact_type in fact_types}
    if populated:
        facts = {'expense_in_category': [{'expense': 1, 'category': 'travel'}], 'expense_has_amount': [{'expense': 1, 'amount': 1500}], 'expense_has_status': [{'expense': 1, 'status': 'review'}]}
    return {'population': {'model': 'guarded_minimal.orm.yaml', 'model_id': 'urn:gnd-fixture:guarded-minimal@1', 'source': 'fixture', 'covers': fact_types}, 'instances': {}, 'facts': facts}

def _check_payload(model: Path, population: Path) -> tuple[subprocess.CompletedProcess[str], dict]:
    result = _run_cli('check', str(model), str(population), '--format', 'json')
    return (result, json.loads(result.stdout))

def test_guarded_routing_evaluates_populated_population(tmp_path: Path) -> None:
    population = _dump_yaml(_population_document(populated=True), tmp_path / 'populated.yaml')
    result, payload = _check_payload(GUARDED_MINIMAL, population)
    guarded = [verdict for verdict in payload['verdicts'] if verdict['constraint_type'] == 'guarded']
    assert result.returncode == 0
    assert len(guarded) == 3
    assert {(verdict['verdict'], verdict['reason_code']) for verdict in guarded} == {('pass', None)}
    assert {verdict['constraint_type'] for verdict in guarded} == {'guarded'}
    assert all('bindings=1' in verdict['message'] for verdict in guarded)

def test_guarded_routing_is_vacuous_for_empty_population(tmp_path: Path) -> None:
    population = _dump_yaml(_population_document(populated=False), tmp_path / 'empty.yaml')
    result, payload = _check_payload(GUARDED_MINIMAL, population)
    guarded = [verdict for verdict in payload['verdicts'] if verdict['constraint_type'] == 'guarded']
    assert result.returncode == 2
    assert len(guarded) == 3
    assert all(verdict['verdict'] == 'vacuous' for verdict in guarded)
    assert all(verdict['reason_code'] is None for verdict in guarded)

def test_guarded_pass_count_is_in_text_summary(tmp_path: Path) -> None:
    population = _dump_yaml(_population_document(populated=True), tmp_path / 'summary.yaml')
    result = _run_cli('check', str(GUARDED_MINIMAL), str(population))
    assert result.returncode == 0
    assert 'pass=3 fail=0 warning=0 unchecked=0 vacuous=0' in result.stdout

def test_guarded_addition_does_not_change_payload_schema_version() -> None:
    assert PAYLOAD_SCHEMA_VERSION == 3

def _hostile_documents() -> list[dict[str, Any]]:
    deep: Any = 'leaf'
    for _ in range(200):
        deep = {'nested': [deep]}
    return [{'constraints': [7]}, {'constraints': [{'type': 'guarded', 'antecedent': 'banana', 'consequent': {}}]}, {'constraints': [{'type': 'guarded', 'antecedent': [7, {'fact_type': 'missing', 'bind': []}], 'consequent': {'atom': 7}}]}, {'constraints': [{'type': 'guarded', 'antecedent': [{'fact_type': 'missing', 'bind': {'role': deep}}], 'consequent': {'comparison': {'operator': '<=', 'left': deep, 'right': []}}}]}]

@pytest.mark.parametrize('rule', [model_module._rule_guarded_term_ref, model_module._rule_guarded_role_claim, model_module._rule_guarded_consequent_ground, model_module._rule_guarded_comparison_type], ids=lambda rule: rule.__name__)
def test_guarded_rules_are_total_on_hostile_documents(rule: Callable[[Any], Any]) -> None:
    for document in _hostile_documents():
        assert isinstance(rule(document), list)

def test_semantic_validate_is_total_on_guarded_hostile_documents() -> None:
    for document in _hostile_documents():
        assert isinstance(semantic_validate(document), list)

def _timed_guarded_document(size: int) -> dict[str, Any]:
    antecedent = [{'fact_type': 'number_fact', 'bind': {'value': f'$value_{index}'}} for index in range(size)]
    return {'object_types': [{'id': 'number', 'name': 'Number', 'kind': 'value', 'primitive': 'Integer'}], 'fact_types': [{'id': 'number_fact', 'reading': '{Number}', 'roles': [{'object_type': 'number', 'role_name': 'value'}]}], 'constraints': [{'type': 'guarded', 'antecedent': antecedent, 'consequent': {'comparison': {'operator': '<=', 'left': '$value_0', 'right': 10}}}]}

def _best_guarded_time(document: dict[str, Any]) -> float:
    durations = []
    for _ in range(3):
        started = time.perf_counter()
        assert model_module._rule_guarded_comparison_type(document) == []
        durations.append(time.perf_counter() - started)
    return min(durations)

def test_guarded_validation_walk_is_linear_and_time_bounded() -> None:
    small = _best_guarded_time(_timed_guarded_document(2000))
    large = _best_guarded_time(_timed_guarded_document(4000))
    assert large < 1.0
    assert large <= small * 4 + 0.05

def _green(document: Any, tmp_path: Path, name: str) -> None:
    path = _dump_yaml(document, tmp_path / f'{name}.orm.yaml')
    load_model(path)
    assert _run_cli('validate', str(path)).returncode == 0

def test_g04_green_controls_for_comparison_typing(tmp_path: Path) -> None:
    base = _load_yaml(GUARDED_MINIMAL)
    var_var = copy.deepcopy(base)
    constraint = _comparison(var_var)
    constraint['antecedent'].append({'fact_type': 'expense_has_amount', 'bind': {'expense': '$e2', 'amount': '$b'}})
    constraint['consequent']['comparison'] = {'operator': '<=', 'left': '$a', 'right': '$b'}
    _green(var_var, tmp_path, 'var_var')
    multi_site = copy.deepcopy(base)
    constraint = _comparison(multi_site)
    constraint['antecedent'].append({'fact_type': 'expense_has_amount', 'bind': {'expense': '$e2', 'amount': '$a'}})
    _green(multi_site, tmp_path, 'multi_site')
    numeric_family = copy.deepcopy(base)
    numeric_family['object_types'].append({'id': 'rate', 'name': 'Rate', 'kind': 'value', 'primitive': 'Float'})
    numeric_family['fact_types'].append({'id': 'expense_has_rate', 'reading': '{Expense} has {Rate}', 'roles': [{'object_type': 'expense', 'role_name': 'expense'}, {'object_type': 'rate', 'role_name': 'rate'}]})
    constraint = _comparison(numeric_family)
    constraint['antecedent'].append({'fact_type': 'expense_has_rate', 'bind': {'expense': '$e', 'rate': '$r'}})
    constraint['consequent']['comparison'] = {'operator': '<=', 'left': '$a', 'right': '$r'}
    _green(numeric_family, tmp_path, 'numeric_family')
    date_literal = copy.deepcopy(base)
    date_literal['object_types'].append({'id': 'booked_on', 'name': 'BookedOn', 'kind': 'value', 'primitive': 'Date'})
    date_literal['fact_types'].append({'id': 'expense_booked_on', 'reading': '{Expense} is booked on {BookedOn}', 'roles': [{'object_type': 'expense', 'role_name': 'expense'}, {'object_type': 'booked_on', 'role_name': 'booked_on'}]})
    constraint = _comparison(date_literal)
    constraint['antecedent'].append({'fact_type': 'expense_booked_on', 'bind': {'expense': '$e', 'booked_on': '$d'}})
    constraint['consequent']['comparison'] = {'operator': '=', 'left': '$d', 'right': '2026-01-01'}
    _green(date_literal, tmp_path, 'date_literal')
    non_iso_date = copy.deepcopy(date_literal)
    constraint = _comparison(non_iso_date)
    constraint['consequent']['comparison']['right'] = '01/02/2026'
    _green(non_iso_date, tmp_path, 'non_iso_date')
    float_vs_integer_role = copy.deepcopy(base)
    constraint = _comparison(float_vs_integer_role)
    constraint['consequent']['comparison']['right'] = 2.5
    _green(float_vs_integer_role, tmp_path, 'float_vs_integer_role')

def test_u04_guarded_verbalization_is_a_pinned_if_then_pattern() -> None:
    from gnd.model_verbalization import render_model_verbalization
    text = render_model_verbalization(GUARDED_MINIMAL)
    assert text.count('If ') == 3
    assert text.count(', then ') == 3
    assert 'If expense_in_category(expense = $e, category = "travel") and expense_has_amount(expense = $e, amount = $a), then $a is at most 2000.' in text
    assert 'then expense_has_status(expense = $e, status = "review") holds.' in text
    assert 'then no expense_has_status(expense = $e, status = "blocked") fact holds.' in text

def test_every_registered_guarded_error_rule_has_a_rejecting_case() -> None:
    covered = {rule_id for _, _, rule_id in REJECTING_CASES}
    registered = set()
    for rule in model_module._SEMANTIC_RULES:
        identifiers = set(re.findall('rule_id="([^"]+)"', inspect.getsource(rule)))
        if identifiers and next(iter(identifiers)).startswith('semantic:guarded-'):
            assert 'severity="warning"' not in inspect.getsource(rule)
            registered.update(identifiers)
    assert registered <= covered, 'Assertion did not hold.'
