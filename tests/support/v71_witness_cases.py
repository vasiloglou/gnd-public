from __future__ import annotations

import copy
import hashlib
import importlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML

from gnd import api
from gnd.artifacts import canonical_json_bytes
from gnd.model import load_model
from gnd.population import load_population
from gnd.references import reference_model_digest

ROOT = Path(__file__).resolve().parents[2]
CORPUS = ROOT / 'tests/fixtures/v71/phase3'
INPUTS = {'domains': {'dispatch': {'edge': 'dispatch_leg', 'reach': 'dispatch_reachable', 'request': 'dispatch_request', 'node': 'dispatch_node', 'values': ['WH-A', 'HUB-B', 'PORT-C', 'DEST-D']}}}

def scalar(value: object, primitive: str='String') -> dict:
    return {'primitive': primitive, 'value': value}

def write_json(path: Path, document: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(document, ensure_ascii=False, indent=2) + '\n')

def bundle(domain: str, root: Path) -> dict[str, Any]:
    original = CORPUS / domain
    root = root.resolve()
    root.mkdir(parents=True, exist_ok=True)
    return {'root': root, 'ids': copy.deepcopy(INPUTS['domains'][domain]), 'model': YAML(typ='safe').load((original / 'model.orm.yaml').read_text()), 'candidate': json.loads((original / 'candidate.pop.json').read_text()), 'reference': json.loads((original / 'references/links.pop.json').read_text()), 'certificate': json.loads((original / 'recursive.witness.json').read_text()), 'request': json.loads((original / 'targets.json').read_text())}

def save(b: dict, *, bind: bool=True) -> None:
    root = b['root']
    if b['model'].get('reference_populations'):
        write_json(root / 'references/links.pop.json', b['reference'])
        digest = hashlib.sha256((root / 'references/links.pop.json').read_bytes()).hexdigest()
        b['model']['reference_populations'][0]['sha256'] = digest
    write_json(root / 'model.orm.yaml', b['model'])
    write_json(root / 'candidate.pop.json', b['candidate'])
    write_json(root / 'targets.json', b['request'])
    if bind:
        m = load_model(root / 'model.orm.yaml')
        p = load_population(root / 'candidate.pop.json', model=m)
        b['certificate']['binding'] = {'model_digest': reference_model_digest(m), 'candidate_digest': 'sha256:' + hashlib.sha256(canonical_json_bytes(p.model_dump(mode='json'))).hexdigest(), 'references': [{'id': d['id'], 'raw_sha256': d['sha256']} for d in b['model'].get('reference_populations', [])]}
    (root / 'certificate.json').write_text(json.dumps(b['certificate'], ensure_ascii=False, separators=(',', ':')) + '\n')

def target(b: dict, values: list, primitive: str='String') -> dict:
    return {'fact_type': b['ids']['reach'], 'tuple': [scalar(v, primitive) for v in values]}

def set_proof(b: dict, nodes: list[dict], values: list, primitive: str='String') -> None:
    for index, node in enumerate(nodes):
        node['id'] = index
    b['certificate']['nodes'] = nodes
    b['certificate']['results'] = [{'request_index': 0, 'target': target(b, values, primitive), 'status': 'proved', 'reason': None, 'root': len(nodes) - 1}]
    b['request'] = {'version': 1, 'targets': [target(b, values, primitive)]}

def replay(b: dict) -> dict:
    save(b, bind=False)
    return api.replay(b['root'] / 'model.orm.yaml', b['root'] / 'candidate.pop.json', b['root'] / 'certificate.json', reference_root=b['root'])

def produce(b: dict) -> dict:
    save(b, bind=False)
    return api.witness(b['root'] / 'model.orm.yaml', b['root'] / 'candidate.pop.json', b['root'] / 'targets.json', reference_root=b['root'])

def no_evaluator(monkeypatch) -> None:
    from gnd import checker, terms

    def forbidden(*args, **kwargs):
        raise AssertionError('replay invoked a production evaluator/comparison primitive')
    for name in ('check', 'structured_extension_view', 'structured_extension_facts', '_python_extension_calculator', '_exact_extension_calculator', '_evaluate_stratified_extensions', '_compare', '_typed_comparison_values'):
        if hasattr(checker, name):
            monkeypatch.setattr(checker, name, forbidden)
    for name in ('evaluate_term', 'guarded_operand_evaluator', 'materialize_scalar'):
        if hasattr(terms, name):
            monkeypatch.setattr(terms, name, forbidden)

def comparison(b: dict, parameters: dict) -> None:
    primitive = parameters['primitive']
    prefix = b['domain']
    obj = prefix + '_value'
    base = prefix + '_observed'
    out = b['ids']['reach']
    left = parameters['left']
    b['model'] = {'version': 4, 'model_id': f'urn:gnd-fixture:v71-{prefix}-comparison@1', 'source': {'kind': 'text-conversation', 'confidence': 'standard', 'mode': 'one-shot'}, 'object_types': [{'id': obj, 'name': 'Value', 'kind': 'value', 'primitive': primitive}], 'fact_types': [{'id': base, 'reading': '{Value} is observed', 'roles': [{'role_name': 'value', 'object_type': obj}]}, {'id': out, 'reading': '{Value} qualifies', 'roles': [{'role_name': 'value', 'object_type': obj}], 'derivation': 'derived', 'derivation_rule': {'body': [{'fact_type': base, 'bind': {'value': '$v'}}], 'where': [{'operator': parameters['operator'], 'left': '$v', 'right': parameters['right']}], 'head': {'value': '$v'}}}], 'constraints': [], 'rejected_proposals': []}
    b['candidate'] = {'population': {'model': 'model.orm.yaml', 'source': 'fixture', 'model_id': b['model']['model_id'], 'covers': [base, out]}, 'instances': {}, 'facts': {base: [{'value': left}], out: []}}
    binding = {'v': scalar(left, primitive)}
    if primitive in {'Date', 'DateTime'}:
        b['model']['fact_types'][0]['roles'].append({'role_name': 'limit', 'object_type': obj})
        b['model']['fact_types'][0]['reading'] = '{Value} is bounded by {Value}'
        r = b['model']['fact_types'][-1]['derivation_rule']
        r['body'][0]['bind']['limit'] = '$limit'
        r['where'][0]['right'] = '$limit'
        b['candidate']['facts'][base][0]['limit'] = parameters['right']
        binding['limit'] = scalar(parameters['right'], primitive)
    nodes = [{'kind': 'base', 'fact_type': base, 'tuple': [scalar(left, primitive)], 'origin': {'kind': 'candidate', 'reference_id': None, 'fact_index': 0}}, {'kind': 'comparison', 'rule_fact_type': out, 'clause_index': 0, 'where_index': 0, 'bindings': copy.deepcopy(binding), 'premises': []}, {'kind': 'rule', 'fact_type': out, 'clause_index': 0, 'tuple': [scalar(left, primitive)], 'bindings': copy.deepcopy(binding), 'premises': [0, 1]}]
    if primitive in {'Date', 'DateTime'}:
        nodes[0]['tuple'].append(scalar(parameters['right'], primitive))
    if parameters.get('bool_mutation'):
        nodes[2]['bindings']['v'] = scalar(True, 'Boolean')
    if parameters.get('drop_where'):
        nodes.pop(1)
        nodes[-1]['premises'] = [0]
    set_proof(b, nodes, [left], primitive)

def kernel(b: dict, cert: object | None=None) -> dict:
    module = importlib.import_module('gnd.witness.kernel')
    reference_inputs = ()
    if b['model'].get('reference_populations'):
        reference_inputs = (('links', (b['root'] / 'references/links.pop.json').read_bytes()),)
    result = module.replay_witness(b['model'], b['candidate'], b['certificate'] if cert is None else cert, reference_inputs=reference_inputs)
    return result if isinstance(result, dict) else result.model_dump(mode='json')

def cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, '-m', 'gnd', *args], cwd=ROOT, capture_output=True, text=True, timeout=15, check=False)
