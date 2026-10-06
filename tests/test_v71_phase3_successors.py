
from copy import deepcopy

from support.v71_witness_cases import bundle

import gnd.model._validation as validation_home
from gnd import model as model_module


def test_in_memory_certificate_intake_has_a_total_wire_byte_cap():
    import pytest

    from gnd.witness.io import validate_witness_structure
    from gnd.witness.types import WitnessInputError
    with pytest.raises(WitnessInputError):
        validate_witness_structure({'values': ['X' * 4096] * 2561})

def test_repeated_type_intake_work_is_linear(tmp_path, monkeypatch):
    document = bundle('dispatch', tmp_path)['model']
    clause = document['fact_types'][-1]['derivation_rule']['clauses'][0]
    clause['body'] *= 200
    document['fact_types'][-1]['derivation_rule'] = clause
    calls = 0
    original = model_module._ancestor_closure

    def counted(*args, **kwargs):
        nonlocal calls
        calls += 1
        return original(*args, **kwargs)
    monkeypatch.setattr(validation_home, '_ancestor_closure', counted)
    assert model_module._rule_derivation_term_type(document) == []
    assert calls <= 410, 'repeated compatible types must not repeat pairwise ancestor work'

def test_type_group_optimization_preserves_all_conflict_sites(tmp_path):
    document = bundle('dispatch', tmp_path)['model']
    other = deepcopy(document['object_types'][0])
    other['id'] = 'other'
    document['object_types'].append(other)
    right = deepcopy(document['fact_types'][0])
    right['id'] = 'right'
    for role in right['roles']:
        role['object_type'] = 'other'
    document['fact_types'].insert(0, right)
    ft = document['fact_types'][-1]
    clause = deepcopy(ft['derivation_rule']['clauses'][0])
    clause['body'] *= 3
    clause['body'].append({'fact_type': 'right', 'bind': {'source': '$x', 'target': '$y'}})
    ft['derivation_rule'] = clause
    issues = model_module._rule_derivation_term_type(document)
    assert len(issues) == 8
    assert [i.path.rsplit('.', 1)[-1] for i in issues] == ['bind[source]', 'bind[source]', 'bind[source]', 'bind[target]', 'bind[target]', 'bind[target]', 'head[source]', 'head[target]']

def test_json_model_intake_preserves_yaml_identity(tmp_path):
    import json

    from support.v71_witness_cases import CORPUS

    from gnd.references import reference_model_digest
    document = bundle('dispatch', tmp_path)['model']
    yaml_model = model_module.load_model_bytes((CORPUS / 'dispatch/model.orm.yaml').read_bytes(), source='model.orm.yaml')
    json_model = model_module.load_model_bytes(json.dumps(document).encode(), source='model.orm.json')
    assert yaml_model.model_dump(mode='json') == json_model.model_dump(mode='json')
    assert reference_model_digest(yaml_model) == reference_model_digest(json_model)

def test_malformed_model_api_is_total(tmp_path):
    from support.v71_witness_cases import save

    from gnd import api
    b = bundle('dispatch', tmp_path)
    save(b)
    (tmp_path / 'model.orm.yaml').write_text('{"version":4,"version":3}')
    result = api.witness(tmp_path / 'model.orm.yaml', tmp_path / 'candidate.pop.json', tmp_path / 'targets.json', reference_root=tmp_path)
    assert result['exit_code'] == 3

def test_non_success_certificate_cannot_hide_unreachable_axioms(tmp_path):
    from support.v71_witness_cases import kernel, save
    b = bundle('dispatch', tmp_path)
    save(b)
    b['certificate']['results'][0].update(status='missing', reason='target-missing', root=None)
    assert kernel(b)['exit_code'] == 1

def test_term_intake_analysis_is_once_per_validation(tmp_path, monkeypatch):
    document = bundle('dispatch', tmp_path)['model']
    calls = 0
    original = model_module._derivation_head_term_issues

    def counted(doc):
        nonlocal calls
        calls += 1
        return original(doc)
    monkeypatch.setattr(validation_home, '_derivation_head_term_issues', counted)
    assert model_module.semantic_validate(document) == []
    assert calls == 1, 'one validation must not repeat the same whole-model term analysis'
    assert model_module.semantic_validate(document) == []
    assert calls == 2, 'no analysis may be inherited across validation invocations'

def test_expanded_view_contains_bounded_explanation_occurrences(tmp_path):
    import json

    from support.v71_witness_cases import CORPUS

    from gnd.witness.view import witness_view
    cert = json.loads((CORPUS / 'dispatch/direct.witness.json').read_text())
    raw = witness_view(cert, raw=True, expand=True)
    assert raw['expanded'][0]['premises'][0]['tuple'] == cert['nodes'][0]['tuple']
    assert raw['work']['node_visits'] == 2
    assert raw['replayable'] is False
    redacted = witness_view(cert, expand=True)
    assert 'WH-A' not in json.dumps(redacted)
    assert redacted['expanded'][0]['premises'][0]['kind'] == 'base'

def test_reviewer_default_cli_refusals_and_replay_remove_values(tmp_path):
    from support.v71_witness_cases import cli, save
    b = bundle('dispatch', tmp_path)
    save(b)
    run = cli('replay', str(tmp_path / 'model.orm.yaml'), str(tmp_path / 'candidate.pop.json'), str(tmp_path / 'certificate.json'), '--reference-root', str(tmp_path), '--json')
    assert run.returncode == 0
    assert 'WH-A' not in run.stdout
    b['model']['fact_types'][-1]['derivation_rule']['clauses'][0]['negate'] = [deepcopy(b['model']['fact_types'][-1]['derivation_rule']['clauses'][0]['body'][0])]
    save(b)
    run = cli('witness', str(tmp_path / 'model.orm.yaml'), str(tmp_path / 'candidate.pop.json'), '--targets', str(tmp_path / 'targets.json'), '--reference-root', str(tmp_path))
    assert run.returncode == 2
    assert 'WH-A' not in run.stdout

def test_reviewer_unsupported_batch_keeps_grounded_base_request(tmp_path):
    from support.v71_witness_cases import produce, replay, save
    b = bundle('dispatch', tmp_path)
    clause = b['model']['fact_types'][-1]['derivation_rule']['clauses'][0]
    clause['negate'] = [deepcopy(clause['body'][0])]
    base = {'fact_type': b['ids']['edge'], 'tuple': deepcopy(b['certificate']['nodes'][0]['tuple'])}
    b['request']['targets'].insert(0, base)
    save(b)
    result = produce(b)
    assert result['exit_code'] == 2
    assert [r['status'] for r in result['results']] == ['proved', 'unsupported']
    b['certificate'] = result['certificate']
    assert [r['status'] for r in replay(b)['results']] == ['proved', 'unsupported']

def test_reviewer_malformed_target_is_input_refusal(tmp_path):
    from support.v71_witness_cases import produce, replay, save
    b = bundle('dispatch', tmp_path)
    save(b)
    b['request']['targets'][0]['tuple'][0]['value'] = 123
    assert produce(b)['exit_code'] == 3
    b['certificate']['results'][0]['target'] = b['request']['targets'][0]
    assert replay(b)['exit_code'] == 3

def test_reviewer_literal_ordering_is_unsupported_on_both_sides(tmp_path):
    from support.v71_witness_cases import produce, replay, save
    b = bundle('dispatch', tmp_path)
    b['model']['fact_types'][-1]['derivation_rule']['clauses'][0]['where'] = [{'left': 'a', 'operator': '<', 'right': 'b'}]
    save(b)
    assert produce(b)['exit_code'] == 2
    assert replay(b)['exit_code'] == 2

def test_exact_integer_number_comparison_uses_numeric_compatibility(tmp_path):
    from support.v71_witness_cases import comparison, produce, replay, save, scalar
    b = bundle('dispatch', tmp_path)
    b['domain'] = 'dispatch'
    comparison(b, {'primitive': 'Number', 'operator': '<', 'left': 5, 'right': 6})
    other = deepcopy(b['model']['object_types'][0])
    other.update(id='integer_limit', name='Limit', primitive='Integer')
    b['model']['object_types'].append(other)
    base = b['model']['fact_types'][0]
    base['roles'].append({'role_name': 'limit', 'object_type': 'integer_limit'})
    base['reading'] = '{Value} is bounded by {Limit}'
    rule = b['model']['fact_types'][-1]['derivation_rule']
    rule['body'][0]['bind']['limit'] = '$limit'
    rule['where'][0]['right'] = '$limit'
    b['candidate']['facts'][base['id']][0]['limit'] = 6
    b['certificate']['nodes'][0]['tuple'].append(scalar(6, 'Integer'))
    for node in b['certificate']['nodes'][1:]:
        node['bindings']['limit'] = scalar(6, 'Integer')
    save(b)
    assert produce(b)['exit_code'] == 0
    assert replay(b)['exit_code'] == 0

def test_unused_base_inputs_do_not_spend_proof_node_budget(tmp_path):
    from dataclasses import replace

    from support.v71_witness_cases import comparison, save

    from gnd.model import load_model
    from gnd.population import load_population
    from gnd.witness.producer import produce_witness
    from gnd.witness.types import DEFAULT_LIMITS
    b = bundle('dispatch', tmp_path)
    b['domain'] = 'dispatch'
    comparison(b, {'primitive': 'Integer', 'operator': '=', 'left': 5, 'right': 999})
    b['candidate']['facts']['dispatch_observed'].append({'value': 7})
    save(b)
    model = load_model(tmp_path / 'model.orm.yaml')
    pop = load_population(tmp_path / 'candidate.pop.json', model=model)
    result = produce_witness(model, pop, tuple(b['request']['targets']), limits=replace(DEFAULT_LIMITS, nodes=1)).model_dump(mode='json')
    assert result['exit_code'] == 2
    assert result['certificate']['nodes'] == []

def test_producer_refuses_a_certificate_larger_than_wire_budget(tmp_path):
    from support.v71_witness_cases import produce, save, scalar
    b = bundle('dispatch', tmp_path)
    b['model'].pop('reference_populations')
    edge, reach = (b['ids']['edge'], b['ids']['reach'])
    value = 'X' * 4096
    b['model']['fact_types'][-1]['derivation_rule'] = {'body': [{'fact_type': edge, 'bind': {'source': '$seed', 'target': f'$v{i}'}} for i in range(2600)], 'head': {'source': '$seed', 'target': '$v0'}}
    b['candidate']['population']['covers'] = [edge, reach]
    b['candidate']['facts'] = {edge: [{'source': 'S', 'target': value}], reach: []}
    b['request']['targets'][0]['tuple'] = [scalar('S'), scalar(value)]
    save(b, bind=False)
    result = produce(b)
    assert result['exit_code'] == 4
    assert result['certificate'] is None

def test_reviewer_unsupported_proof_scalar_preserves_valid_sibling(tmp_path):
    from support.v71_witness_cases import comparison, produce, replay, save, scalar
    b = bundle('dispatch', tmp_path)
    b['domain'] = 'dispatch'
    comparison(b, {'primitive': 'Number', 'operator': '<', 'left': 5, 'right': 9})
    b['candidate']['facts']['dispatch_observed'].append({'value': 7})
    b['request']['targets'] = [{'fact_type': 'dispatch_observed', 'tuple': [scalar(value, 'Number')]} for value in (5, 7)]
    save(b)
    result = produce(b)
    assert result['exit_code'] == 0
    b['certificate'] = result['certificate']
    b['certificate']['nodes'][1]['tuple'][0]['value'] = 1.5
    result = replay(b)
    assert result['exit_code'] == 2
    assert [r['status'] for r in result['results']] == ['proved', 'unsupported']
    b['request']['targets'][1]['fact_type'] = b['ids']['reach']
    save(b)
    b['certificate'] = produce(b)['certificate']
    for node in b['certificate']['nodes']:
        if node['kind'] == 'base' and node['tuple'][0]['value'] == 7:
            node['tuple'][0]['value'] = 1.5
    result = replay(b)
    assert result['exit_code'] == 2
    assert [r['status'] for r in result['results']] == ['proved', 'unsupported']

def test_generated_wire_budget_includes_canonical_final_newline(tmp_path):
    from dataclasses import replace

    from support.v71_witness_cases import save, scalar

    from gnd.artifacts import canonical_json_bytes
    from gnd.model import load_model
    from gnd.population import load_population
    from gnd.witness.producer import produce_witness
    from gnd.witness.types import DEFAULT_LIMITS
    b = bundle('dispatch', tmp_path)
    b['model'].pop('reference_populations')
    edge, reach = (b['ids']['edge'], b['ids']['reach'])
    value = 'X' * 512
    b['model']['fact_types'][-1]['derivation_rule'] = {'body': [{'fact_type': edge, 'bind': {'source': '$seed', 'target': f'$v{i}'}} for i in range(10)], 'head': {'source': '$seed', 'target': '$v0'}}
    b['candidate']['population']['covers'] = [edge, reach]
    b['candidate']['facts'] = {edge: [{'source': 'S', 'target': value}], reach: []}
    b['request']['targets'][0]['tuple'] = [scalar('S'), scalar(value)]
    save(b, bind=False)
    model = load_model(tmp_path / 'model.orm.yaml')
    candidate = load_population(tmp_path / 'candidate.pop.json', model=model)
    targets = tuple(b['request']['targets'])
    result = produce_witness(model, candidate, targets)
    assert result.exit_code == 0
    wire_bytes = len(canonical_json_bytes(result.certificate))
    at_limit = produce_witness(model, candidate, targets, limits=replace(DEFAULT_LIMITS, bytes=wire_bytes))
    assert at_limit.exit_code == 0
    result = produce_witness(model, candidate, targets, limits=replace(DEFAULT_LIMITS, bytes=wire_bytes - 1))
    assert result.exit_code == 4
    assert result.certificate is None
