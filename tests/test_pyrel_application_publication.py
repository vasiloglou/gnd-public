"""Red-first parent acceptance/publication boundaries for PA3."""
import copy
import hashlib
import importlib
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / 'src/gnd/examples/bookrec/model.orm.yaml'
POP = ROOT / 'src/gnd/examples/bookrec/seed.population.json'


def application():
    assert importlib.util.find_spec('gnd.export.applications') is not None, 'native publication parent is absent'
    module = importlib.import_module('gnd.export.applications')
    assert callable(getattr(module, 'execute_application', None))
    assert callable(getattr(module, 'verify_policy_report', None))
    return module


def valid_policy():
    doc = json.loads(MODEL.read_text())
    entries = [(f"fact_types[{f['id']}].constraints[{i}]", c)
               for f in doc['fact_types'] for i, c in enumerate(f.get('constraints', []))]
    entries += [(f'constraints[{i}]', c) for i, c in enumerate(doc['constraints'])]
    policy = {'schema_version': 1, 'profile': 'applications-v1', 'backend': 'duckdb-local',
              'accepted': True, 'status': 'accepted', 'exit_code': 0,
              'binding': {'model_sha256': 'a' * 64, 'population_sha256': 'b' * 64},
              'verdicts': [{'constraint_ref': ref, 'id': c.get('id', ref), 'constraint_type': c['type'],
                            'modality': c.get('modality', 'alethic'), 'status': 'satisfied',
                            'witnesses': [], 'reason': None} for ref, c in entries], 'derivations': []}
    return doc, policy


def test_parent_requires_complete_explicit_accepted_report():
    module = application()
    doc, report = valid_policy()
    module.verify_policy_report(report, doc, 'a' * 64, 'b' * 64, 0)


@pytest.mark.parametrize('damage', ['empty', 'accepted', 'schema', 'backend', 'binding', 'missing-row',
                                   'duplicate-row', 'row-type', 'row-id', 'row-modality', 'incomplete',
                                   'error', 'vacuous', 'status', 'exit', 'reason-field', 'extra-head'])
def test_parent_rejects_each_false_publication_boundary(damage):
    module = application()
    doc, report = valid_policy(); report = copy.deepcopy(report)
    if damage == 'empty':
        report = {}
    elif damage in {'accepted', 'schema', 'backend', 'status', 'exit'}:
        key, value = {'accepted': ('accepted', False), 'schema': ('schema_version', True),
                      'backend': ('backend', 'remote'), 'status': ('status', 'rejected'),
                      'exit': ('exit_code', 70)}[damage]
        report[key] = value
    elif damage == 'binding':
        report['binding']['population_sha256'] = 'c' * 64
    elif damage == 'missing-row':
        report['verdicts'].pop()
    elif damage == 'duplicate-row':
        report['verdicts'].append(report['verdicts'][0])
    elif damage.startswith('row-'):
        key = {'row-type': 'constraint_type', 'row-id': 'id', 'row-modality': 'modality'}[damage]
        report['verdicts'][0][key] = 'invented'
    elif damage in {'incomplete', 'error', 'vacuous'}:
        report['verdicts'][0]['status'] = damage
    elif damage == 'reason-field':
        del report['verdicts'][0]['reason']
    else:
        report['derivations'] = [{'derivation_ref': 'derivation:invented', 'status': 'satisfied'}]
    with pytest.raises(ValueError):
        module.verify_policy_report(report, doc, 'a' * 64, 'b' * 64, 0)


def test_existing_output_and_input_remain_exact_on_refusal(tmp_path):
    module = application()
    source = tmp_path / 'input.json'; source.write_bytes(POP.read_bytes())
    output = tmp_path / 'output.json'; output.write_bytes(b'owner bytes')
    before = hashlib.sha256(source.read_bytes()).hexdigest()
    result = module.execute_application(MODEL, source, output, native_python=Path('/absent/native/python'),
                                        query_script=tmp_path / 'query.py')
    assert not result['published'] and not result['accepted']
    assert source.read_bytes() == POP.read_bytes() and hashlib.sha256(source.read_bytes()).hexdigest() == before
    assert output.read_bytes() == b'owner bytes'
