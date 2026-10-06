import copy
import json
from types import SimpleNamespace

import pytest
from support.v71_session_cases import bundle, session_case, write_json

from gnd import api
from gnd.admission_validation import validate_admission_payload
from gnd.artifacts import canonical_json_bytes
from gnd.exp.session_contract import DataDrivenContract
from gnd.model import load_model
from gnd.population import load_population


def test_guarded_message_redacts_unused_private_binding(tmp_path):
    b = bundle('dispatch', tmp_path)
    b['model']['fact_types'][0]['roles'][0]['redact'] = True
    rows = b['population']['facts'][b['ids']['fact']]
    rows[0][b['ids']['key']] = 'PRIVATE_GUARD_CANARY'
    rows[0][b['ids']['quantity']] = 0
    write_json(tmp_path / 'model.orm.yaml', b['model'])
    write_json(tmp_path / 'candidate.pop.json', b['population'])
    report = api.check(tmp_path / 'model.orm.yaml', tmp_path / 'candidate.pop.json', admission=True)
    assert report['exit_code'] == 1
    assert b'PRIVATE_GUARD_CANARY' not in canonical_json_bytes(report)
    b['model']['fact_types'][0]['roles'][0].pop('redact')
    write_json(tmp_path / 'model.orm.yaml', b['model'])
    visible = api.check(tmp_path / 'model.orm.yaml', tmp_path / 'candidate.pop.json', admission=True)
    assert visible['counts'] == report['counts']
    assert b'PRIVATE_GUARD_CANARY' in canonical_json_bytes(visible)

def test_inline_constraint_admission_and_repair_ownership(tmp_path):
    from gnd.admission_validation import constraint_annotations
    from gnd.model_verbalization import render_model_verbalization
    b = bundle('dispatch', tmp_path)
    rule = copy.deepcopy(b['model']['constraints'][0])
    rule.update(type='uniqueness', roles=[b['ids']['key']], owner='host', allowed_fixes=['delete-fact'])
    for key in ('antecedent', 'consequent', 'id'):
        rule.pop(key, None)
    b['model']['constraints'] = []
    b['model']['fact_types'][0]['constraints'] = [rule]
    write_json(tmp_path / 'model.orm.yaml', b['model'])
    model = load_model(tmp_path / 'model.orm.yaml')
    population = load_population(tmp_path / 'candidate.pop.json', model=model)
    report = api.check(model, population, admission=True)
    assert validate_admission_payload(report, model=model, candidate=population)['candidate_admitted_unique'] == 2
    assert next(iter(constraint_annotations(model).values()))['owner'] == 'host'
    assert '"owner":"host"' in render_model_verbalization(model)
    report['verdicts'][0]['constraint_ref'] = 'constraints[999]'
    with pytest.raises(ValueError):
        validate_admission_payload(report, model=model, candidate=population)

def test_numeric_admission_identity_ignores_json_number_spelling(tmp_path):
    b = bundle('dispatch', tmp_path)
    b['model']['object_types'][1]['primitive'] = 'Number'
    write_json(tmp_path / 'model.orm.yaml', b['model'])
    row = copy.deepcopy(b['population']['facts'][b['ids']['fact']][0])
    row[b['ids']['quantity']] = 1.0
    b['population']['facts'][b['ids']['fact']] = [b['population']['facts'][b['ids']['fact']][0], row]
    write_json(tmp_path / 'candidate.pop.json', b['population'])
    model = load_model(tmp_path / 'model.orm.yaml')
    pop = load_population(tmp_path / 'candidate.pop.json', model=model)
    report = api.check(model, pop, admission=True)
    assert validate_admission_payload(report, model=model, candidate=pop)['candidate_admitted_unique'] == 1

def test_v7_work_close_rebinds_walk_floor_evidence(tmp_path):
    from gnd.exp.close import _declared_case_findings
    b = bundle('dispatch', tmp_path)
    observed = session_case({'branch': 'B24', 'parameters': {'variant': 'transition-reference'}}, b)
    run = observed['_run_root']
    result = (run / 'result.json').read_bytes()
    findings = _declared_case_findings(SimpleNamespace(root=run), run.parent.parent, result, experiment_id='EXP-714-corpus')
    assert findings == []
    document = json.loads(result)
    assert document['walk_floors'][0]['discharged']
    document['walk_floors'][0]['required_ops'] += 1
    assert _declared_case_findings(SimpleNamespace(root=run), run.parent.parent, canonical_json_bytes(document), experiment_id='EXP-714-corpus')

def test_temporal_admission_keeps_successor_when_redaction_is_active(tmp_path):
    _temporal_bundle(tmp_path)
    report = api.check(tmp_path / 'model.orm.yaml', tmp_path / 'candidate.pop.json', admission=True)
    assert report['schema_version'] == 13
    loaded = load_model(tmp_path / 'model.orm.yaml')
    pop = load_population(tmp_path / 'candidate.pop.json', model=loaded)
    assert validate_admission_payload(report, model=loaded, candidate=pop)['candidate_admitted_unique'] == 2

def test_reference_transition_rejects_an_unknown_wrapper(tmp_path):
    from gnd.exp.session_contract import read_session_contract
    from gnd.exp.session_v7 import _evaluate
    b = bundle('dispatch', tmp_path)
    observed = session_case({'branch': 'B24', 'parameters': {'variant': 'transition-reference'}}, b)
    run = observed['_run_root']
    root = run.parent.parent
    contract = read_session_contract(root / 'session.contract.json', experiment_root=root, experiment_id=root.name)
    attempt = observed['_attempts'][0]
    directory = run / 'attempts/0001'
    raw = json.loads((directory / attempt['raw_verifier_payloads'][0]['path']).read_text())
    raw['schema_version'] = 99
    with pytest.raises(ValueError):
        _evaluate(contract.cases[0], canonical_json_bytes(raw), attempt['evaluation']['results'][0]['process_exit'], directory / 'candidate', root, attempt['candidate_inventory']['tree_sha256'], attempt['evaluation']['contract_sha256'])

@pytest.mark.parametrize('entry', ['direct', 'file'])
def test_v7_contract_refuses_duplicate_keys(entry, tmp_path):
    from gnd.exp.session_contract import SessionContractError, read_session_contract
    b = bundle('dispatch', tmp_path)
    raw = canonical_json_bytes(b['contract']).replace(b'"max_attempts":4', b'"max_attempts":0,"max_attempts":4')
    assert raw.count(b'"max_attempts"') == 2
    if entry == 'direct':
        with pytest.raises(ValueError):
            DataDrivenContract.model_validate_json(raw)
    else:
        (tmp_path / 'session.contract.json').write_bytes(raw)
        with pytest.raises(SessionContractError):
            read_session_contract(tmp_path / 'session.contract.json', experiment_root=tmp_path, experiment_id=b['contract']['experiment_id'])

@pytest.mark.parametrize('variant', ['depth', 'scalar'])
def test_patch_bounds_cover_values_and_direct_entry(variant, tmp_path):
    from support.v71_session_cases import base_files, patch_contract, proposal

    from gnd.exp.session_patch import apply_candidate_patch, read_patch_document
    b = bundle('dispatch', tmp_path)
    base, digest, _ = base_files(b)
    value = 'x' * 4097
    if variant == 'depth':
        value = 0
        for _ in range(65):
            value = [value]
    doc = proposal(b, [{'op': 'replace-artifact', 'artifact': 'notes.json', 'value': value}], digest)
    with pytest.raises(ValueError):
        if variant == 'depth':
            apply_candidate_patch(doc, contract=patch_contract(b), base_root=base, base_sha256=digest)
        else:
            read_patch_document(canonical_json_bytes(doc))

def test_patch_preserves_distinct_large_fractional_keys(tmp_path):
    from decimal import Decimal

    from support.v71_session_cases import base_files, patch_contract

    from gnd.exp.session_patch import apply_candidate_patch, read_patch_document
    from gnd.exp.session_store import SessionStore
    b = bundle('dispatch', tmp_path)
    base, _, _ = base_files(b)
    fact = b['ids']['fact']
    key = b['ids']['key']
    (base / 'candidate.pop.json').write_text(json.dumps({'facts': {fact: [{key: 'NUMBER', 'quantity': 1}]}}).replace('"NUMBER"', '9007199254740992.0'))
    digest = SessionStore(tmp_path / 'precision-store', run_id='precision').inventory_candidate(base).tree_sha256
    raw = json.dumps({'schema_version': 1, 'base_candidate_sha256': digest, 'operations': [{'op': 'upsert', 'artifact': 'candidate.pop.json', 'collection': ['facts', fact], 'key': ['NUMBER'], 'value': {key: 'NUMBER', 'quantity': 2}}]}).replace('"NUMBER"', '9007199254740993.0').encode()
    files = apply_candidate_patch(read_patch_document(raw), contract=patch_contract(b), base_root=base, base_sha256=digest)
    rows = json.loads(files['candidate.pop.json'], parse_float=Decimal)['facts'][fact]
    assert [row[key] for row in rows] == [Decimal('9007199254740992.0'), Decimal('9007199254740993.0')]

def test_v8_feedback_requires_all_payload_exits(tmp_path):
    from gnd.exp.session_eval import AttemptFeedback
    b = bundle('dispatch', tmp_path)
    observed = session_case({'branch': 'B24', 'parameters': {'variant': 'patch-repair'}}, b)
    attempt = observed['_attempts'][0]
    feedback = json.loads((observed['_run_root'] / 'attempts/0001' / attempt['feedback']['path']).read_text())
    feedback['payload_exit'] = []
    with pytest.raises(ValueError):
        AttemptFeedback.model_validate(feedback)

def test_v7_wall_bound_can_be_tightened(tmp_path, monkeypatch):
    import support.v71_session_cases as helper
    original = helper.main

    def tighten(argv):
        if '--wall-seconds' in argv:
            argv[argv.index('--wall-seconds') + 1] = '30'
        return original(argv)
    monkeypatch.setattr(helper, 'main', tighten)
    observed = session_case({'branch': 'B24', 'parameters': {'variant': 'complete'}}, bundle('dispatch', tmp_path))
    assert observed['disposition'] == 'accepted'

@pytest.mark.parametrize('variant', ['symlink', 'over-cap', 'seed-mode', 'root-swap'])
def test_v7_proposal_and_terminal_publication_boundaries(variant, tmp_path, monkeypatch):
    import support.v71_session_cases as helper

    from gnd.exp import session_v7
    if variant in {'symlink', 'over-cap'}:
        producer = helper.producer_source()
        statement = "pathlib.Path('.gnd-patch.json').write_bytes(b'x' * (10 * 1024 * 1024 + 1))"
        if variant == 'symlink':
            statement = "pathlib.Path('.gnd-patch.json').unlink(missing_ok=True); pathlib.Path('.gnd-patch.json').symlink_to('candidate.pop.json')"
        producer += '\n' + statement + '\n'
        monkeypatch.setattr(helper, 'producer_source', lambda: producer)
    if variant == 'root-swap':
        from gnd.exp import session_runtime
        publish = session_runtime.publish_leaf_atomic

        def swapped(root, relative, data, **kwargs):
            if relative == 'result.json':
                root.rename(root.with_name('original-run'))
                root.mkdir()
            return publish(root, relative, data, **kwargs)
        monkeypatch.setattr(session_runtime, 'publish_leaf_atomic', swapped)
        with pytest.raises(FileNotFoundError):
            session_case({'branch': 'B24', 'parameters': {'variant': 'patch-repair'}}, bundle('dispatch', tmp_path))
        assert not list(tmp_path.rglob('result.json'))
        return
    observed = session_case({'branch': 'B24', 'parameters': {'variant': 'patch-repair'}}, bundle('dispatch', tmp_path))
    first = observed['_attempts'][0]
    if variant == 'seed-mode':
        assert first['candidate_edit']['mode'] == 'complete'
    else:
        assert observed['disposition'] != 'accepted'
        assert first['candidate_edit']['refusal'] == ('limit' if variant == 'over-cap' else 'path')
        markers = [path for path in observed['_run_root'].rglob('proposal.json') if path.parent.name == 'rejected']
        assert markers
        marker = json.loads(markers[0].read_text())
        assert marker['non_replayable'] and marker['truncated']
        assert marker['observed_leaf_size_bytes'] > 10 * 1024 * 1024 if variant == 'over-cap' else marker['leaf_kind'] == 'symlink'
        assert not first['best_eligible']

def test_v7_programmatic_policy_must_match_contract(tmp_path):
    import asyncio

    from gnd.exp.session import run_session
    b = bundle('dispatch', tmp_path)
    calls = []

    async def forbidden(*args, **kwargs):
        calls.append(1)
        raise RuntimeError('producer invoked')
    import sys

    from gnd.exp.adapter_policy import read_adapter_policy
    write_json(tmp_path / 'policy.json', {'schema_version': 1, 'policy_id': 'other-policy', 'kind': 'command', 'executable': sys.executable, 'argv': ['-c', 'pass'], 'version_argv': ['--version'], 'prompt_transport': 'stdin', 'environment_allowlist': []})
    from gnd.exp.session_contract import AdapterDeclaration
    policy = read_adapter_policy(tmp_path / 'policy.json', declaration=AdapterDeclaration(policy_id='other-policy', parameters={'model': None}))
    with pytest.raises(ValueError, match='policy'):
        asyncio.run(run_session(DataDrivenContract.model_validate(b['contract']), contract_sha256='a' * 64, adapter_policy=policy, prompt='control', candidate_root=tmp_path, run_root=tmp_path / 'run', verifier=forbidden, declared_invoker=forbidden))
    assert calls == []

@pytest.mark.parametrize('temporal', [False, True], ids=['snapshot', 'temporal'])
def test_admission_production_enforces_its_propagation_ceiling(temporal, tmp_path, monkeypatch):
    from gnd import admission
    original = admission.build_admission
    seen = []

    def bounded(*args, **kwargs):
        seen.append(kwargs.get('max_cells'))
        return original(*args, max_cells=1 if kwargs.get('max_cells') is not None else None)
    monkeypatch.setattr(admission, 'build_admission', bounded)
    b = _temporal_bundle(tmp_path) if temporal else bundle('dispatch', tmp_path)
    for row in b['population']['facts'][b['ids']['fact']]:
        row[b['ids']['quantity']] = 0
        if temporal:
            row['deadline'] = row['start']
    write_json(tmp_path / 'candidate.pop.json', b['population'])
    report = api.check(tmp_path / 'model.orm.yaml', tmp_path / 'candidate.pop.json', admission=True)
    assert report['exit_code'] == 70
    assert seen == [1000000]
    assert report['schema_version'] == (13 if temporal else 10)

def test_resume_binds_the_current_policy_bytes(tmp_path):
    import asyncio
    import hashlib
    import shutil

    from gnd.exp.adapter_policy import read_adapter_policy
    from gnd.exp.session import run_session
    from gnd.exp.session_contract import read_session_contract
    observed = session_case({'branch': 'B24', 'parameters': {'variant': 'patch-repair'}}, bundle('dispatch', tmp_path))
    run = observed['_run_root']
    root = run.parent.parent
    (run / 'result.json').unlink()
    shutil.rmtree(run / 'attempts/0002')
    (run / 'launches/0002.json').unlink()
    first = observed['_attempts'][0]
    write_json(run / 'best.json', {'attempt_index': 1, 'attempt_manifest_sha256': hashlib.sha256((run / 'attempts/0001/attempt.json').read_bytes()).hexdigest(), 'candidate_sha256': first['candidate_inventory']['tree_sha256']})
    shutil.rmtree(root / 'candidate')
    shutil.copytree(run / 'attempts/0001/candidate', root / 'candidate')
    contract = read_session_contract(root / 'session.contract.json', experiment_root=root, experiment_id=root.name)
    policy_document = json.loads((tmp_path / 'command.policy.json').read_text())
    policy_document['argv'].append('changed-policy')
    write_json(tmp_path / 'changed-policy.json', policy_document)
    policy = read_adapter_policy(tmp_path / 'changed-policy.json', declaration=contract.adapter)
    calls = []

    async def forbidden(*args, **kwargs):
        calls.append(1)
        raise RuntimeError('new invocation')
    with pytest.raises(ValueError, match='binding'):
        asyncio.run(run_session(contract, contract_sha256=hashlib.sha256((root / 'session.contract.json').read_bytes()).hexdigest(), adapter_policy=policy, prompt='control', candidate_root=root / 'candidate', run_root=run, verifier=forbidden, declared_invoker=forbidden))
    assert calls == []

def test_proposals_preserve_protected_executable_bits(tmp_path, monkeypatch):
    import support.v71_session_cases as helper
    producer = helper.producer_source() + "\npathlib.Path('kept.json').chmod(0o755)\n"
    monkeypatch.setattr(helper, 'producer_source', lambda: producer)
    observed = session_case({'branch': 'B24', 'parameters': {'variant': 'patch-repair'}}, bundle('dispatch', tmp_path))
    assert observed['_attempts'][0]['candidate_edit']['refusal'] == 'protected'
    assert not observed['_attempts'][0]['best_eligible']

def _temporal_bundle(tmp_path):
    b = bundle('dispatch', tmp_path)
    model = b['model']
    model['object_types'].append({'id': 'calendar_day', 'name': 'Day', 'kind': 'value', 'primitive': 'Date'})
    model['fact_types'][0]['roles'] += [{'role_name': 'start', 'object_type': 'calendar_day'}, {'role_name': 'deadline', 'object_type': 'calendar_day'}]
    model['fact_types'][0]['roles'][0]['redact'] = True
    model['fact_types'][0]['reading'] += ' at {Day} before {Day}'
    model['constraints'][0]['antecedent'][0]['bind'].update(start='$s', deadline='$d')
    model['constraints'][0]['consequent']['comparison'] = {'left': {'fn': 'date_add', 'args': ['$s', {'duration_days': 2}]}, 'operator': '<=', 'right': '$d'}
    for row in b['population']['facts'][b['ids']['fact']]:
        row.update(start='2026-10-02', deadline='2026-10-04')
    write_json(tmp_path / 'model.orm.yaml', model)
    write_json(tmp_path / 'candidate.pop.json', b['population'])
    return b

def test_v7_verifier_obeys_the_remaining_run_deadline(tmp_path, monkeypatch):
    import asyncio
    import time

    import support.v71_session_cases as helper

    import gnd.exp.session as cli
    original_verifier = cli.run_gnd_verifier

    async def delayed(*args, **kwargs):
        await asyncio.sleep(3)
        return await original_verifier(*args, **kwargs)
    monkeypatch.setattr(cli, 'run_gnd_verifier', delayed)
    original_main = helper.main

    def tighten(argv):
        if '--wall-seconds' in argv:
            argv[argv.index('--wall-seconds') + 1] = '1'
        return original_main(argv)
    monkeypatch.setattr(helper, 'main', tighten)
    started = time.monotonic()
    observed = session_case({'branch': 'B24', 'parameters': {'variant': 'patch-repair'}}, bundle('dispatch', tmp_path))
    assert time.monotonic() - started < 2.5
    assert observed['disposition'] == 'budget-exhausted'
    assert observed['best_attempt'] is None

def test_ranking_and_work_closure_remain_separate_claims(tmp_path, monkeypatch):
    import support.v71_session_cases as helper

    from gnd.exp.close import _declared_case_findings
    original = helper.write_json

    def reverse(path, document):
        if path.name == 'session.contract.json':
            document['ranking'] = [{'metric': 'accepted_required_cases', 'direction': 'min'}]
        return original(path, document)
    monkeypatch.setattr(helper, 'write_json', reverse)
    observed = session_case({'branch': 'B24', 'parameters': {'variant': 'transition-reference'}}, bundle('dispatch', tmp_path))
    assert observed['disposition'] == 'accepted'
    assert observed['best_attempt'] == 1
    assert not observed['walk_floors'][0]['discharged']
    run = observed['_run_root']
    assert _declared_case_findings(SimpleNamespace(root=run), run.parent.parent, (run / 'result.json').read_bytes(), experiment_id='EXP-714-corpus')

def test_first_proposal_requires_the_complete_null_base_seed(tmp_path):
    from support.v71_session_cases import base_files, patch_contract, proposal

    from gnd.exp.session_patch import apply_candidate_patch
    b = bundle('dispatch', tmp_path)
    base, digest, _ = base_files(b)
    with pytest.raises(ValueError):
        apply_candidate_patch(proposal(b, [], digest), contract=patch_contract(b), base_root=base, base_sha256=digest, allow_initial_seed=True)

def test_patch_selector_cannot_contain_containers(tmp_path):
    from support.v71_session_cases import proposal

    from gnd.exp.session_patch import read_patch_document
    b = bundle('dispatch', tmp_path)
    doc = proposal(b, [{'op': 'delete', 'artifact': 'candidate.pop.json', 'collection': [{}], 'key': ['A']}], 'a' * 64)
    with pytest.raises(ValueError):
        read_patch_document(canonical_json_bytes(doc))

def test_replay_refuses_a_relabelled_complete_seed(tmp_path):
    from gnd.exp.session_contract import read_session_contract
    from gnd.exp.session_store import SessionStore
    from gnd.exp.session_v7 import reconstruct
    observed = session_case({'branch': 'B24', 'parameters': {'variant': 'patch-repair'}}, bundle('dispatch', tmp_path))
    run = observed['_run_root']
    (run / 'result.json').unlink()
    first = observed['_attempts'][0]
    first['candidate_edit']['mode'] = 'patch'
    (run / 'attempts/0001/attempt.json').write_bytes(canonical_json_bytes(first))
    root = run.parent.parent
    contract = read_session_contract(root / 'session.contract.json', experiment_root=root, experiment_id=root.name)
    with pytest.raises(ValueError, match='mode'):
        reconstruct(SessionStore(run, run_id=run.name, contract_id=root.name), contract)

def test_public_admission_refuses_deep_dicts_with_a_bounded_error(tmp_path):
    from gnd.admission_validation import AdmissionValidationError
    bundle('dispatch', tmp_path)
    model = load_model(tmp_path / 'model.orm.yaml')
    pop = load_population(tmp_path / 'candidate.pop.json', model=model)
    report = api.check(model, pop, admission=True)
    nested = 0
    for _ in range(10000):
        nested = [nested]
    report['unexpected'] = nested
    with pytest.raises(AdmissionValidationError):
        validate_admission_payload(report, model=model, candidate=pop)

def test_internal_verifier_reports_cannot_become_ranked_candidates(tmp_path, monkeypatch):
    from gnd.exp import session

    def failed_evaluator(*args, **kwargs):
        raise RuntimeError('controlled verifier failure')

    async def failing(case, snapshot, **kwargs):
        root = kwargs['experiment_root']
        report = api.check(root / case.verify.model.path, snapshot / case.verify.subject, admission=True, evaluator=failed_evaluator)
        assert report['exit_code'] == 70
        report['model'] = case.verify.model.path
        report['population'] = case.verify.subject
        return (70, canonical_json_bytes(report))
    monkeypatch.setattr(session, 'run_gnd_verifier', failing)
    observed = session_case({'branch': 'B24', 'parameters': {'variant': 'patch-repair'}}, bundle('dispatch', tmp_path))
    assert observed['disposition'] == 'verifier-failure'
    assert observed['best_attempt'] is None
    assert all(not row['best_eligible'] for row in observed['_attempts'])
