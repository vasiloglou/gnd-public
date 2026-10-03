from __future__ import annotations

import copy
import hashlib
import json
import shutil
import sys
from pathlib import Path
from typing import Any

from gnd.artifacts import canonical_json_bytes
from gnd.cli import main
from gnd.exp.session_contract import DataDrivenContract
from gnd.exp.session_store import SessionStore
from gnd.model import load_model

ROOT = Path(__file__).resolve().parents[2]
CORPUS = ROOT / 'tests/fixtures/v71/phase4'
INPUTS = {'domains': {'dispatch': {'fact': 'dispatch_work', 'catalog': 'dispatch_approved', 'key': 'shipment_code', 'quantity': 'units', 'rule': 'dispatch_positive', 'model_id': 'urn:gnd-fixture:v71-dispatch-sessions@1', 'row1': {'shipment_code': 'A', 'units': 1}, 'row2': {'shipment_code': 'B', 'units': 2}, 'artifacts': [{'path': 'candidate.pop.json', 'collections': [{'path': ['facts', 'dispatch_work'], 'key': ['shipment_code']}]}, {'path': 'notes.json', 'collections': []}]}}}

def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_json_bytes(value))

def bundle(domain: str, root: Path) -> dict[str, Any]:
    root.mkdir(parents=True, exist_ok=True)
    source = CORPUS / domain
    for name in ('model.orm.yaml', 'candidate.pop.json', 'contract-v7.json', 'reference-model.orm.yaml', 'owned-model.orm.yaml', 'references/catalog.pop.json'):
        destination = root / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source / name, destination)
    return {'root': root, 'ids': copy.deepcopy(INPUTS['domains'][domain]), 'model': json.loads((source / 'model.orm.yaml').read_text()), 'population': json.loads((source / 'candidate.pop.json').read_text()), 'contract': json.loads((source / 'contract-v7.json').read_text())}

def patch_contract(b: dict) -> DataDrivenContract:
    doc = copy.deepcopy(b['contract'])
    doc['candidate_edits'] = {'patch_path': '.gnd-patch.json', 'artifacts': b['ids']['artifacts']}
    return DataDrivenContract.model_validate(doc)

def base_files(b: dict) -> tuple[Path, str, dict[str, bytes]]:
    base = b['root'] / 'base'
    base.mkdir(exist_ok=True)
    (base / 'candidate.pop.json').write_bytes(canonical_json_bytes(b['population']))
    write_json(base / 'notes.json', {'note': 'unchanged'})
    write_json(base / 'kept.json', {'keep': True})
    store = SessionStore(b['root'] / 'store', run_id='corpus')
    digest = store.inventory_candidate(base).tree_sha256
    return (base, digest, {p.name: p.read_bytes() for p in base.iterdir()})

def proposal(b: dict, operations: list[dict], digest: str | None) -> dict:
    ops = copy.deepcopy(operations)
    for op in ops:
        if op['op'] != 'replace-artifact':
            op.setdefault('artifact', 'candidate.pop.json')
            op.setdefault('collection', ['facts', b['ids']['fact']])
    return {'schema_version': 1, 'base_candidate_sha256': digest, 'operations': ops}

def producer_source() -> str:
    return "import base64,json,pathlib,sys\nif sys.argv[1:] == ['--version']:\n print('v71-corpus-command 1');raise SystemExit(0)\nplan=json.loads(pathlib.Path(sys.argv[1]).read_text())\nlog=pathlib.Path(sys.argv[2]);log.mkdir(exist_ok=True)\nindex=len(list(log.glob('stdin-*.bin')))\nraw=sys.stdin.buffer.read();(log/f'stdin-{index:04d}.bin').write_bytes(raw)\nframe=json.loads(raw) if raw else {}\nfeedback=json.loads(base64.b64decode(frame['feedback_base64'])) if frame.get('feedback_base64') else None\nitem=plan[min(index,len(plan)-1)]\nif item.get('direct_edit'):\n pathlib.Path(item['direct_edit']).write_text('tampered')\nif item.get('remove'):\n pathlib.Path(item['remove']).unlink()\nif item.get('symlink'):\n p=pathlib.Path(item['symlink']);p.unlink(missing_ok=True);p.symlink_to(sys.argv[1])\nfor path,value in item.get('raw_files',{}).items():\n pathlib.Path(path).write_text(value)\nfor path,value in item.get('files',{}).items():\n p=pathlib.Path(path);p.parent.mkdir(parents=True,exist_ok=True)\n p.write_text(json.dumps(value,sort_keys=True,separators=(',',':'))+'\\n')\nif 'proposal' in item:\n proposal=item['proposal']\n if proposal.get('base_candidate_sha256')=='CURRENT':\n  proposal['base_candidate_sha256']=feedback['candidate_edit_context']['base_candidate_sha256']\n pathlib.Path('.gnd-patch.json').write_text(json.dumps(proposal,sort_keys=True,separators=(',',':'))+'\\n')\n"

def session_case(row: dict, b: dict) -> dict:
    p = row['parameters']
    variant = p.get('variant', '')
    experiment = 'EXP-714-corpus'
    parent = b['root'] / 'experiment'
    assert main(['exp', 'init', experiment, '--out', str(parent), '--kind', 'data-driven', '--question', 'Q1=Does the declared candidate meet the frozen relation?']) == 0
    root = parent / experiment
    candidate = root / 'candidate'
    candidate.mkdir()
    model = copy.deepcopy(b['model'])
    initial = copy.deepcopy(b['population'])
    if variant in {'reference-repair', 'transition-reference', 'annotation-mixed'}:
        model = json.loads((b['root'] / 'reference-model.orm.yaml').read_text())
        shutil.copytree(b['root'] / 'references', root / 'references')
        fixed = json.loads((root / 'references/catalog.pop.json').read_text())
        fixed['facts'][b['ids']['catalog']].append({b['ids']['key']: 'C'})
        if variant == 'annotation-mixed':
            model['constraints'][0]['owner'] = 'reference'
            model['constraints'][0]['antecedent'].append({'fact_type': b['ids']['catalog'], 'bind': {b['ids']['key']: '$k'}})
            model['constraints'][0]['allowed_fixes'] = []
        write_json(root / 'references/catalog.pop.json', fixed)
        model['reference_populations'][0]['sha256'] = hashlib.sha256((root / 'references/catalog.pop.json').read_bytes()).hexdigest()
    if variant == 'temporal-repair':
        model['object_types'].append({'id': 'calendar_day', 'name': 'Day', 'kind': 'value', 'primitive': 'Date'})
        model['fact_types'][0]['roles'] += [{'role_name': 'start', 'object_type': 'calendar_day'}, {'role_name': 'deadline', 'object_type': 'calendar_day'}]
        model['fact_types'][0]['reading'] += ' at {Day} before {Day}'
        model['constraints'][0]['antecedent'][0]['bind'].update(start='$s', deadline='$d')
        model['constraints'][0]['consequent']['comparison'] = {'left': {'fn': 'date_add', 'args': ['$s', {'duration_days': 2}]}, 'operator': '<=', 'right': '$d'}
    if variant == 'transition-reference':
        model['operations'] = [{'id': 'record_work', 'reading': 'Record {' + model['object_types'][0]['name'] + '} with {' + model['object_types'][1]['name'] + '}', 'parameters': [{'name': 'key', 'object_type': model['object_types'][0]['id']}, {'name': 'quantity', 'object_type': model['object_types'][1]['id']}], 'effects': [{'assert': {'fact_type': b['ids']['fact'], 'bind': {b['ids']['key']: '$key', b['ids']['quantity']: '$quantity'}}}], 'frame': {'modality': 'alethic'}, 'source': 'user-supplied', 'status': 'confirmed', 'provenance': {'user_quote': 'Record the additional approved work.'}}]
    write_json(root / 'model.orm.yaml', model)
    write_json(candidate / 'candidate.pop.json', initial)
    write_json(candidate / 'notes.json', {'note': 'unchanged'})
    write_json(candidate / 'kept.json', {'keep': True})
    contract = copy.deepcopy(b['contract'])
    data = (root / 'model.orm.yaml').read_bytes()
    contract['cases'][0]['verify']['model'].update(sha256=hashlib.sha256(data).hexdigest(), size_bytes=len(data))
    contract['cases'][0]['acceptance']['coverage'][0]['min_facts'] = 3
    if variant in {'reference-repair', 'transition-reference', 'annotation-mixed'}:
        contract['cases'][0]['reference_root'] = '.'
    patch_mode = variant in {'patch-repair', 'reference-repair', 'protected', 'patch-byte-noise'}
    if patch_mode:
        contract['candidate_edits'] = {'patch_path': '.gnd-patch.json', 'artifacts': b['ids']['artifacts']}
    a = copy.deepcopy(initial)
    a['facts'][b['ids']['fact']] = [] if b['ids']['row1'] is None else [copy.deepcopy(b['ids']['row1'])]
    other = copy.deepcopy(a)
    if other['facts'][b['ids']['fact']]:
        other['facts'][b['ids']['fact']][0][b['ids']['quantity']] = 2
    better = copy.deepcopy(initial)
    third = copy.deepcopy(a)
    if third['facts'][b['ids']['fact']]:
        third['facts'][b['ids']['fact']][0][b['ids']['quantity']] = 3
    accepted = copy.deepcopy(initial)
    accepted['facts'][b['ids']['fact']].append({b['ids']['key']: 'C', b['ids']['quantity']: 3})
    if variant == 'temporal-repair':
        for pop in (a, other, better, third, accepted, initial):
            for r in pop['facts'][b['ids']['fact']]:
                r.update(start='2026-10-02', deadline='2026-10-04' if pop is accepted else '2026-10-03')
    sequence = [a, accepted]
    if variant in {'earlier-better', 'rejected-high-score'}:
        sequence = [better, a]
    elif variant == 'later-better':
        sequence = [a, better]
    elif variant in {'tie', 'case-order', 'resume', 'tampered-score'}:
        sequence = [a, other]
    elif variant in {'same-candidate', 'patch-byte-noise', 'annotation-parse', 'annotation-mixed'}:
        sequence = [a, a]
    elif variant == 'a-b-a':
        sequence = [a, other, a]
    elif variant == 'distinct-rejected':
        sequence = [a, other, third]
    elif variant == 'accepted-repeated':
        contract['cases'][0]['acceptance']['coverage'][0]['min_facts'] = 1
        sequence = [a, a]
    if row['branch'] in {'B16', 'B18'}:
        contract['ranking'] = [{'metric': 'candidate_admitted_unique', 'direction': 'max'}]
    if variant == 'case-order':
        second = copy.deepcopy(contract['cases'][0])
        second['case_id'] = 'z-last-in-canonical-order'
        contract['cases'].insert(0, second)
    contract['max_attempts'] = len(sequence)
    plan = []
    for index, pop in enumerate(sequence):
        if patch_mode:
            ops = [{'op': 'replace-artifact', 'artifact': 'candidate.pop.json', 'value': pop}, {'op': 'replace-artifact', 'artifact': 'notes.json', 'value': {'note': 'unchanged'}}]
            plan.append({'proposal': proposal(b, ops, None if index == 0 else 'CURRENT')})
        else:
            plan.append({'files': {'candidate.pop.json': pop}})
    if variant == 'annotation-parse':
        plan = [{'raw_files': {'candidate.pop.json': '{broken-json'}} for _ in sequence]
    if variant == 'protected':
        target = p['target']
        if target in {'direct-byte-edit', 'extra-file', 'missing-file'}:
            plan[-1]['remove' if target == 'missing-file' else 'direct_edit'] = 'kept.json' if target != 'extra-file' else 'extra.json'
        else:
            plan[-1]['proposal']['operations'].append({'op': 'replace-artifact', 'artifact': f'{target}.json', 'value': {'tampered': True}})
    if variant == 'transition-reference':
        pre = canonical_json_bytes(initial)
        (root / 'input').mkdir()
        (root / 'input/pre.json').write_bytes(pre)
        case = contract['cases'][0]
        case['inputs'] = [{'path': 'input/pre.json', 'sha256': hashlib.sha256(pre).hexdigest(), 'size_bytes': len(pre), 'media_type': 'application/json', 'encoding': 'utf-8'}]
        case['acceptance'] = {'mode': 'transition', 'walk': {'required_ops': [{'op': 'record_work', 'bindings_subset': {'quantity': 1}}], 'forbidden_ops': []}}
        case['verify'] = {'command': 'transition', 'model': case['verify']['model'], 'pre': 'input/pre.json', 'steps': 'steps.json', 'post': None}
        from gnd.transition import model_digest, operations_digest
        loaded_model = load_model(root / 'model.orm.yaml')
        plan = [{'files': {'steps.json': {'steps_schema': 1, 'model': 'model.orm.yaml', 'model_digest': model_digest(loaded_model), 'operations_digest': operations_digest(loaded_model.operations), 'steps': [{'op': 'record_work', 'bindings': {'key': 'C', 'quantity': q}}]}}} for q in (0, 1)]
    write_json(root / 'session.contract.json', contract)
    log = b['root'] / 'producer-log'
    write_json(b['root'] / 'producer-plan.json', plan)
    agent = b['root'] / 'producer.py'
    agent.write_text(producer_source())
    policy = b['root'] / 'command.policy.json'
    write_json(policy, {'schema_version': 1, 'policy_id': 'local-command', 'kind': 'command', 'executable': sys.executable, 'argv': [str(agent), str(b['root'] / 'producer-plan.json'), str(log)], 'version_argv': [str(agent), '--version'], 'prompt_transport': 'stdin', 'environment_allowlist': ['PATH', 'TMPDIR', 'LANG', 'LC_ALL']})
    exit_code = main(['exp', 'run', str(root), '--adapter-policy', str(policy), '--wall-seconds', '60'])
    run = root / 'runs/run-0001'
    result = json.loads((run / 'result.json').read_text())
    attempts = [json.loads(x.read_text()) for x in sorted((run / 'attempts').glob('*/attempt.json'))]
    wire = json.loads((CORPUS / 'wire-fields.json').read_text())
    assert result['schema_version'] == wire['versions']['result']
    assert sorted(result) == wire['root_keys']['result']
    assert attempts, 'a command session must retain an attempt'
    for directory, saved in zip(sorted((run / 'attempts').glob('*/attempt.json')), attempts, strict=True):
        assert saved['schema_version'] == wire['versions']['attempt']
        assert sorted(saved) == wire['root_keys']['attempt']
        if saved['candidate_edit'] is not None:
            assert sorted(saved['candidate_edit']) == wire['candidate_edit_keys']
        for leaf, audience in (('feedback', 'candidate'), ('operator_feedback', 'operator')):
            encoded = (directory.parent / saved[leaf]['path']).read_bytes()
            decoded = json.loads(encoded)
            assert decoded['schema_version'] == wire['versions']['feedback']
            assert sorted(decoded) == wire['root_keys']['feedback']
            assert decoded['audience'] == audience
            assert hashlib.sha256(encoded).hexdigest() == saved[leaf]['sha256']
    for leaf in sorted((run / 'launches').glob('*.json')):
        launch = json.loads(leaf.read_text())
        assert launch['schema_version'] == wire['versions']['launch']
        assert sorted(launch) == wire['root_keys']['launch']
    result['exit_code'] = exit_code
    result['best_attempt_index'] = result['best_attempt']
    result['_run_root'] = run
    result['_attempts'] = attempts
    result['_producer_log'] = log
    result['real_command'] = all(x['invocation']['policy_id'] == 'local-command' for x in attempts)
    result['no_partial_publish'] = all(x['candidate_edit']['result_candidate_sha256'] is None for x in attempts if isinstance(x.get('candidate_edit'), dict) and x['candidate_edit'].get('refusal') is not None)
    if variant in {'resume', 'tampered-score'}:
        from gnd.exp.session import case_payload_versions
        from gnd.exp.session_contract import read_session_contract
        loaded_contract = read_session_contract(root / 'session.contract.json', experiment_root=root, experiment_id=experiment)
        (run / 'result.json').unlink()
        before = len(list(log.glob('stdin-*.bin')))
        if variant == 'tampered-score':
            saved = run / 'best.json'
            changed = json.loads(saved.read_text())
            changed['attempt_index'] = 2
            write_json(saved, changed)
        try:
            reconstructed = SessionStore(run, run_id=result['run_id']).read_resume_state(loaded_contract, expected_payload_versions=case_payload_versions(loaded_contract, root))
        except ValueError:
            result['resume_refused'] = True
        else:
            result['resume_refused'] = False
            assert reconstructed.best_attempt_identity is not None
            assert reconstructed.best_attempt_identity.attempt_index == result['best_attempt']
        assert len(list(log.glob('stdin-*.bin'))) == before
    return result
