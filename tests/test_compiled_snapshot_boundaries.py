"""Passing standing subsets do not establish walk-only obligations."""
import copy
import json

from test_compiled_snapshot_obligations import small_case

from gnd import api
from gnd.model import load_model
from gnd.transition import operations_digest, transition_model_identity


def walk_document(model_path, steps):
    model = load_model(model_path)
    return {'steps_schema': 1, 'model': model_path.name,
            'model_digest': transition_model_identity(model),
            'operations_digest': operations_digest(model.operations), 'steps': steps}


def assert_snapshot_passes(model_path, population_path):
    result = api.check(model_path, population_path, compiled_operations=True)
    assert result['exit_code'] == 0, result
    assert result['counts']['fail'] == result['counts']['unchecked'] == 0


def test_retained_literal_snapshot_passes_but_walk_rejects(tmp_path):
    model_path, pop = small_case(tmp_path, facts={'recorded': [{'value': 'x'}]})
    document = json.loads(model_path.read_text())
    document['operations'][0]['preconditions'][0]['require'][0]['bind']['value'] = 'required'
    model_path.write_text(json.dumps(document))
    assert_snapshot_passes(model_path, pop)
    result = api.transition(model_path, pop, walk_document(
        model_path, [{'op': 'record', 'bindings': {'x': 'x'}}]))
    assert result['exit_code'] == 1, result
    assert any(row['obligation'] == 'pre_permitted' and row['verdict'] == 'fail'
               for step in result['transition']['steps'] for row in step['verdicts'])


def test_frame_snapshot_passes_but_declared_walk_post_rejects(tmp_path):
    model_path, pre = small_case(tmp_path, facts={
        'recorded': [{'value': 'x'}], 'permitted': [{'value': 'x'}]})
    post = tmp_path / 'post.json'
    document = json.loads(pre.read_text())
    document['facts']['recorded'].append({'value': 'undeclared'})
    document['facts']['permitted'].append({'value': 'undeclared'})
    post.write_text(json.dumps(document))
    assert_snapshot_passes(model_path, pre)
    assert_snapshot_passes(model_path, post)
    result = api.transition(model_path, pre, walk_document(
        model_path, [{'op': 'record', 'bindings': {'x': 'x'}}]), post)
    assert result['exit_code'] == 1, result
    assert any(row['verdict'] == 'fail' for row in result['transition']['frame_verdicts'])


def test_intermediate_snapshot_endpoints_pass_but_walk_rejects(tmp_path):
    model_path, pre = small_case(tmp_path, facts={
        'recorded': [{'value': 'x'}], 'permitted': [{'value': 'x'}, {'value': 'y'}],
        'other': [{'value': 'y'}]})
    document = json.loads(model_path.read_text())
    metadata = {key: copy.deepcopy(document['operations'][0][key])
                for key in ('source', 'status', 'provenance')}
    document['constraints'] = [{
        'type': 'exclusion', 'modality': 'alethic', **metadata,
        'role_seq_a': [{'fact_type': 'recorded', 'role': 'value'}],
        'role_seq_b': [{'fact_type': 'other', 'role': 'value'}]}]
    forget = copy.deepcopy(document['operations'][0])
    forget['id'] = 'forget'
    forget['effects'] = [{'retract': {'fact_type': 'recorded', 'bind': {'value': '$x'}}}]
    document['operations'].append(forget)
    model_path.write_text(json.dumps(document))
    assert_snapshot_passes(model_path, pre)
    result = api.transition(model_path, pre, walk_document(model_path, [
        {'op': 'record', 'bindings': {'x': 'y'}},
        {'op': 'forget', 'bindings': {'x': 'y'}}]), pre)
    assert result['exit_code'] == 1, result
    assert any(row['verdict'] == 'fail'
               for step in result['transition']['steps']
               for row in step['intermediate']['verdicts'])
