from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from gnd.model import ModelValidationError, load_model

REPO_ROOT = Path(__file__).resolve().parents[1]
CORPUS = REPO_ROOT / 'tests' / 'fixtures' / 'derivation'
ANSWER_KEY = json.loads((CORPUS / 'expected.json').read_text(encoding='utf-8'))
CASES: list[dict[str, Any]] = ANSWER_KEY['cases']
CASES_BY_ID = {str(case['id']): case for case in CASES}
MATRIX_FLOOR = 60
CURRENTLY_SUPERSEDED_CASES = {'R-22', 'R-37'}
V70_ADMITTED_RECURSION = {'R-29', 'R-30', 'R-31', 'M-07'}
RECLASSIFIED_CASE_RULES = {'R-21': 'semantic:derivation-head-term-type', 'R-23': 'semantic:derivation-head-term-type', 'R-24': 'semantic:derivation-head-term-type'}
REQUIRED_BRANCHES = frozenset({'load:string-arm', 'load:object-arm', 'load:absent', 'ref:fact-type-undeclared', 'ref:role-undeclared', 'ref:head-role-undeclared', 'ref:negate-fact-type-undeclared', 'shape:rule-not-mapping', 'shape:rule-extra-key', 'shape:body-missing', 'shape:body-not-array', 'shape:body-empty', 'shape:atom-not-mapping', 'shape:negate-not-array', 'shape:head-not-mapping', 'shape:head-empty', 'claim:atom-role-missing', 'claim:atom-role-extra', 'claim:head-role-missing', 'claim:head-role-extra', 'bind:head-unbound', 'bind:negate-unbound', 'bind:component-unused', 'head:literal-string', 'head:literal-number', 'head:literal-boolean', 'head:malformed-variable', 'type:repeated-within-atom', 'type:across-positive-atoms', 'type:positive-vs-negated', 'type:body-vs-head', 'type:compatible-subtype', 'type:compatible-numeric', 'graph:self-loop', 'graph:cycle-2', 'graph:cycle-3', 'graph:opaque-dependency-positive', 'graph:opaque-dependency-negated', 'graph:dag-depth-3', 'decl:rule-on-asserted', 'decl:storage-contradiction', 'decl:structured-on-object-type', 'decl:operations-plus-derivation', 'decl:no-roles', 'decl:rule-not-string-or-object', 'shape:rule-extra-key-layer2', 'shape:head-term-layer2', 'grammar:aggregate-key', 'grammar:sum-key', 'grammar:disjunction-key', 'grammar:arithmetic-key', 'mutation:one-token-fact-type', 'mutation:one-token-head-variable', 'mutation:one-token-derivation-mode', 'mutation:one-token-orphan-component', 'mutation:one-token-storage', 'mutation:one-token-asserted', 'mutation:one-token-cycle', 'mutation:one-token-derivation-enum', 'mutation:one-token-type-clash', 'order:precedence-reference-before-shape', 'order:precedence-shape-before-graph', 'order:partition-stable', 'order:topological-stable', 'order:edge-direction-proven'})

def _case_path(case: dict[str, Any]) -> Path:
    return CORPUS / str(case['path'])

def _load(case: dict[str, Any]) -> tuple[Any, ModelValidationError | None]:
    try:
        return (load_model(_case_path(case)), None)
    except ModelValidationError as error:
        return (None, error)

def _read_doc(path: Path) -> dict[str, Any]:
    from ruamel.yaml import YAML
    return YAML(typ='safe').load(path.read_text(encoding='utf-8'))

def test_matrix_floor_and_ids_are_unique():
    assert len(CASES) >= MATRIX_FLOOR
    assert ANSWER_KEY['matrix_floor'] == MATRIX_FLOOR
    ids = [str(case['id']) for case in CASES]
    assert len(ids) == len(set(ids)) == len(CASES)

def test_branch_manifest_is_exactly_covered():
    exercised = {branch for case in CASES for branch in case['branches']}
    exercised |= set(ANSWER_KEY.get('direct_branches', {}))
    assert exercised == set(REQUIRED_BRANCHES), 'Assertion did not hold.'

def test_every_case_declares_at_least_one_branch():
    for case in CASES:
        assert case['branches'], 'Assertion did not hold.'

@pytest.mark.parametrize('case', CASES, ids=[str(c['id']) for c in CASES])
def test_case_outcome_matches_answer_key(case: dict[str, Any]):
    model, error = _load(case)
    if case['id'] in CURRENTLY_SUPERSEDED_CASES | V70_ADMITTED_RECURSION:
        assert error is None, 'Assertion did not hold.'
        assert model is not None
        return
    if case['outcome'] == 'load':
        assert error is None, 'Assertion did not hold.'
        assert model is not None
        return
    assert error is not None, 'Assertion did not hold.'
    rule_ids = [issue.rule_id for issue in error.issues]
    expected_rule = RECLASSIFIED_CASE_RULES.get(case['id'], case['rule_id'])
    assert expected_rule in rule_ids, 'Assertion did not hold.'

@pytest.mark.parametrize('case', [c for c in CASES if c['outcome'] == 'refuse' and c['id'] not in CURRENTLY_SUPERSEDED_CASES], ids=[str(c['id']) for c in CASES if c['outcome'] == 'refuse' and c['id'] not in CURRENTLY_SUPERSEDED_CASES])
def test_refusal_points_at_the_declared_location(case: dict[str, Any]):
    _, error = _load(case)
    if case['id'] in V70_ADMITTED_RECURSION:
        assert error is None
        return
    assert error is not None
    expected_rule = RECLASSIFIED_CASE_RULES.get(case['id'], case['rule_id'])
    matching = [i for i in error.issues if i.rule_id == expected_rule]
    assert matching, 'Assertion did not hold.'
    fragment = case.get('path_contains')
    assert fragment, 'Assertion did not hold.'
    assert any(fragment in issue.path for issue in matching), 'Assertion did not hold.'
    for issue in matching:
        assert issue.message.strip()

def test_every_refusal_case_declares_a_path_discriminator():
    missing = [c['id'] for c in CASES if c['outcome'] == 'refuse' and (not c.get('path_contains'))]
    assert not missing, 'Assertion did not hold.'

def test_every_accepting_case_has_a_discriminating_sibling():
    unpaired = [case['id'] for case in CASES if case['outcome'] == 'load' and 'mutation' not in case]
    assert not unpaired, 'Assertion did not hold.'
    for case in CASES:
        if case['outcome'] != 'load':
            continue
        sibling = CASES_BY_ID[str(case['mutation'])]
        assert sibling['outcome'] == 'refuse'
        assert sibling.get('mutation_of') == case['id']

def test_every_mutation_pair_is_one_token_apart():
    import difflib
    for case in CASES:
        base_id = case.get('mutation_of')
        if not base_id:
            continue
        base = (CORPUS / CASES_BY_ID[base_id]['path']).read_text(encoding='utf-8')
        mutant = (CORPUS / case['path']).read_text(encoding='utf-8')
        changed = [line for line in difflib.unified_diff(base.splitlines(), mutant.splitlines(), n=0) if line[:1] in '+-' and line[:3] not in ('---', '+++')]
        assert 1 <= len(changed) <= 2, 'Assertion did not hold.'

def test_reference_errors_precede_shape_errors():
    _, error = _load(CASES_BY_ID['R-42'])
    assert error is not None
    ids = [issue.rule_id for issue in error.issues]
    assert 'semantic:derivation-term-ref' in ids
    assert 'semantic:derivation-rule-shape' in ids
    assert ids.index('semantic:derivation-term-ref') < ids.index('semantic:derivation-rule-shape')

def test_shape_errors_precede_graph_errors():
    _, error = _load(CASES_BY_ID['R-43'])
    assert error is not None
    ids = [issue.rule_id for issue in error.issues]
    assert 'semantic:derivation-rule-shape' in ids
    assert 'semantic:derivation-unstratified' not in ids
HOSTILE_RULES: list[tuple[str, Any]] = [('rule-is-list', [1, 2, 3]), ('rule-is-number', 7), ('rule-is-null', None), ('rule-is-bool', True), ('body-is-string', {'body': 'nope', 'head': {'book': '$b'}}), ('body-of-numbers', {'body': [1, 2], 'head': {'book': '$b'}}), ('atom-bind-is-string', {'body': [{'fact_type': 'book_flagged', 'bind': 'x'}], 'head': {'book': '$b'}}), ('atom-bind-non-string-key', {'body': [{'fact_type': 'book_flagged', 'bind': {7: '$b'}}], 'head': {'book': '$b'}}), ('head-is-list', {'body': [{'fact_type': 'book_flagged', 'bind': {'book': '$b'}}], 'head': [1]}), ('head-nested-object', {'body': [{'fact_type': 'book_flagged', 'bind': {'book': '$b'}}], 'head': {'book': {'deep': {'deeper': 1}}}}), ('nan-term', {'body': [{'fact_type': 'book_flagged', 'bind': {'book': float('nan')}}], 'head': {'book': '$b'}}), ('infinity-term', {'body': [{'fact_type': 'book_flagged', 'bind': {'book': float('inf')}}], 'head': {'book': '$b'}}), ('oversized-integer', {'body': [{'fact_type': 'book_flagged', 'bind': {'book': 10 ** 4300}}], 'head': {'book': '$b'}}), ('empty-variable', {'body': [{'fact_type': 'book_flagged', 'bind': {'book': '$'}}], 'head': {'book': '$'}}), ('deep-nesting', {'body': [{'fact_type': 'book_flagged', 'bind': {'book': '$b'}}], 'head': {'book': '$b'}, 'negate': [{'deep': {'a': {'b': {'c': {}}}}}]}), ('huge-body', {'body': [{'fact_type': 'book_flagged', 'bind': {'book': f'$v{i}'}} for i in range(10000)], 'head': {'book': '$v0'}})]

@pytest.mark.parametrize('label,rule', HOSTILE_RULES, ids=[h[0] for h in HOSTILE_RULES])
def test_derivation_rules_are_total_over_hostile_shapes(label: str, rule: Any):
    doc = {'version': 1, 'model_id': 'urn:gnd-fixture:hostile@1', 'source': {'kind': 'text-conversation', 'confidence': 'standard', 'mode': 'one-shot'}, 'object_types': [{'id': 'book', 'name': 'Book', 'kind': 'entity', 'reference': {'mode': 'popular', 'value_type': 'book_id'}}, {'id': 'book_id', 'name': 'BookId', 'kind': 'value', 'primitive': 'Integer'}], 'fact_types': [{'id': 'book_flagged', 'reading': '{Book} is flagged', 'roles': [{'object_type': 'book', 'role_name': 'book'}]}, {'id': 'eligible', 'reading': '{Book} is eligible', 'roles': [{'object_type': 'book', 'role_name': 'book'}], 'derivation': 'derived', 'derivation_rule': rule}], 'constraints': []}
    from gnd.model import semantic_validate
    issues = semantic_validate(doc)
    assert isinstance(issues, list)
    assert issues, 'Assertion did not hold.'
    for issue in issues:
        assert issue.rule_id and issue.path
    raised = [i for i in issues if i.rule_id == 'internal:rule-raised']
    assert len(raised) < len(issues), 'Assertion did not hold.'

def test_component_partition_and_strata_are_functions_of_the_bytes():
    from gnd.model import body_components, derivation_strata
    path = _case_path(CASES_BY_ID['A-06'])
    docs = [_read_doc(path) for _ in range(2)]
    assert derivation_strata(docs[0]) == derivation_strata(docs[1])
    rules = [fact_type['derivation_rule'] for doc in docs for fact_type in doc['fact_types'] if isinstance(fact_type.get('derivation_rule'), dict)]
    partitions = [body_components(rule) for rule in rules]
    half = len(partitions) // 2
    assert partitions[:half] == partitions[half:]
    disconnected = _read_doc(_case_path(CASES_BY_ID['A-07']))
    eligible = next(f for f in disconnected['fact_types'] if f['id'] == 'eligible')
    assert len(body_components(eligible['derivation_rule'])) == 2, 'Assertion did not hold.'

def test_dependency_order_is_dependency_first_and_reversal_would_fail():
    from gnd.model import derivation_dependencies, derivation_strata
    doc = _read_doc(_case_path(CASES_BY_ID['A-06']))
    order = derivation_strata(doc)
    assert order == [('eligible',), ('mid_a',), ('mid_b',)], 'Assertion did not hold.'
    dependencies = derivation_dependencies(doc)
    assert 'eligible' in dependencies['mid_a']
    assert 'mid_a' in dependencies['mid_b']
    flat = [head for component in order for head in component]
    for index, head in enumerate(flat):
        for dependency in dependencies[head] & set(dependencies):
            assert flat.index(dependency) < index, 'Assertion did not hold.'

def _work_counter() -> int:
    from gnd import model as model_module
    return getattr(model_module, '_DERIVATION_WORK', 0)

def test_derivation_graph_work_is_bounded_by_counted_operations():
    from gnd.model import body_components, derivation_strata

    def rule_of(size: int) -> dict[str, Any]:
        return {'body': [{'fact_type': 'pair', 'bind': {'a': f'$v{i}', 'b': f'$v{i + 1}'}} for i in range(size)], 'head': {'book': '$v0'}}
    partition_costs = {}
    for size in (50, 100, 200):
        before = _work_counter()
        components = body_components(rule_of(size))
        partition_costs[size] = _work_counter() - before
        assert len(components) == 1, 'Assertion did not hold.'
        assert partition_costs[size] > 0, 'Assertion did not hold.'
    assert partition_costs[200] <= 8 * partition_costs[50], 'Assertion did not hold.'
    chain_costs = {}
    for depth in (20, 40, 80):
        doc = {'fact_types': [{'id': f'd{i}', 'roles': [{'object_type': 'book', 'role_name': 'book'}], 'derivation': 'derived', 'derivation_rule': {'body': [{'fact_type': 'book_flagged' if i == 0 else f'd{i - 1}', 'bind': {'book': '$b'}}], 'head': {'book': '$b'}}} for i in range(depth)]}
        before = _work_counter()
        order = derivation_strata(doc)
        chain_costs[depth] = _work_counter() - before
        assert order == [(f'd{i}',) for i in range(depth)], 'Assertion did not hold.'
    assert chain_costs[80] <= 8 * chain_costs[20], 'Assertion did not hold.'

def test_legacy_string_rule_still_loads_and_is_never_interpreted():
    model, error = _load(CASES_BY_ID['A-01'])
    assert error is None
    fact_type = next(f for f in model.fact_types if str(f.get('id')) == 'eligible')
    assert isinstance(fact_type.get('derivation_rule'), str)
    assert fact_type['derivation_rule'] == 'Each eligible pair is one a human decides.'

def test_derived_subtype_still_routes_to_the_out_of_scope_verdict():
    from gnd.model import load_model as _load_model
    model = _load_model(REPO_ROOT / 'tests' / 'fixtures' / 'models' / 'library.orm.yaml')
    reference_copy = next(ot for ot in model.object_types if str(ot.get('id')) == 'reference_copy')
    assert reference_copy.get('derivation') == 'derived'
    assert isinstance(reference_copy.get('derivation_rule'), str)

def test_a_roleless_fact_type_with_a_rule_is_refused_as_defense_in_depth():
    from gnd.model import semantic_validate
    issues = semantic_validate({'fact_types': [{'id': 'roleless', 'roles': [], 'derivation': 'derived', 'derivation_rule': {'body': [{'fact_type': 'roleless', 'bind': {}}], 'head': {'r': '$v'}}}]})
    matching = [issue for issue in issues if issue.rule_id == 'semantic:derivation-rule-shape' and 'declares none' in issue.message]
    assert matching, 'Assertion did not hold.'

def test_a_rule_that_is_neither_string_nor_object_is_refused_at_layer_two():
    from gnd.model import semantic_validate
    for value in ([1, 2, 3], 7, True):
        issues = semantic_validate({'fact_types': [{'id': 'x', 'roles': [{'object_type': 'o', 'role_name': 'r'}], 'derivation': 'derived', 'derivation_rule': value}]})
        assert any(issue.rule_id == 'semantic:derivation-rule-shape' and 'opaque string or a structured' in issue.message for issue in issues), 'Assertion did not hold.'

def test_shape_rules_survive_as_defense_in_depth_behind_the_closed_schema():
    from gnd.model import semantic_validate

    def rule_issues(rule: Any) -> list[str]:
        return [issue.message for issue in semantic_validate({'fact_types': [{'id': 'x', 'roles': [{'object_type': 'o', 'role_name': 'r'}], 'derivation': 'derived', 'derivation_rule': rule}]}) if issue.rule_id == 'semantic:derivation-rule-shape']
    good_body = [{'fact_type': 'x', 'bind': {'r': '$v'}}]
    assert any("'or'" in message for message in rule_issues({'body': good_body, 'head': {'r': '$v'}, 'or': []}))
    assert any('declares no body' in message for message in rule_issues({'head': {'r': '$v'}}))
    assert any('head binds no role' in message for message in rule_issues({'body': good_body, 'head': {}}))

def test_the_published_schema_refuses_what_the_product_refuses():
    import json as _json

    from jsonschema import Draft202012Validator
    schema = _json.loads((REPO_ROOT / 'src/gnd/skills/gnd-orm-core/references/orm-meta.schema.json').read_text(encoding='utf-8'))
    validator = Draft202012Validator(schema)
    for case in CASES:
        if case['id'] not in CURRENTLY_SUPERSEDED_CASES | RECLASSIFIED_CASE_RULES.keys() and case.get('refused_at', '').startswith('layer-1'):
            document = _read_doc(CORPUS / case['path'])
            assert list(validator.iter_errors(document)), 'Assertion did not hold.'

def test_structured_rule_on_an_object_type_is_refused_by_name():
    _, error = _load(CASES_BY_ID['R-36'])
    assert error is not None
    matching = [issue for issue in error.issues if issue.rule_id == 'semantic:derivation-structured-on-object-type']
    assert matching
    assert 'D6' in matching[0].message or 'out of scope' in matching[0].message

@pytest.mark.parametrize('case_id,construct', [('R-38', 'aggregate'), ('R-39', 'sum'), ('R-40', 'or'), ('R-41', 'arithmetic')])
def test_grammar_refusal_names_the_construct(case_id: str, construct: str):
    _, error = _load(CASES_BY_ID[case_id])
    assert error is not None
    messages = [issue.message for issue in error.issues if issue.rule_id == 'jsonschema:oneOf']
    assert any(f"'{construct}'" in message for message in messages), 'Assertion did not hold.'
