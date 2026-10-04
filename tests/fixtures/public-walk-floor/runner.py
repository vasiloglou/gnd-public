from __future__ import annotations

import asyncio
import hashlib
import json
import shutil
import tempfile
from pathlib import Path
from typing import Literal, get_args, get_origin


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def _fake_invoker():
    from gnd.agent_cli import InvocationResult, InvocationStatus, build_agent_argv

    async def invoke(adapter, *, prompt, cwd, feedback_sha256, **_kwargs):
        effective = prompt
        if feedback_sha256 is not None:
            effective += f'\n\nCurrent attempt feedback SHA-256: {feedback_sha256}\nCanonical current-attempt feedback is supplied byte-for-byte on stdin.'
        token = f'<prompt:sha256={_sha256(effective.encode())}>'
        return InvocationResult(adapter=adapter, status=InvocationStatus.succeeded, executable='installed-matrix-agent', version='1', argv=(*build_agent_argv(adapter, effective)[:-1], token), cwd=str(cwd), spawned=True, process_group_cleaned=True, termination='exited', exit_code=0, started_monotonic=1.0, ended_monotonic=1.01, stdout_observed_bytes=0, stdout_retained_bytes=0, stdout_truncated=False, stderr_observed_bytes=0, stderr_retained_bytes=0, stderr_truncated=False, environment=(), prompt_sha256=_sha256(prompt.encode()), feedback_sha256=feedback_sha256, stdout=b'', stderr=b'')
    return invoke

async def _run(repository: Path, scratch: Path, *, deficient: bool=False, refused: bool=False, reordered: bool=False):
    from gnd.agent_cli import AgentAdapterId
    from gnd.exp.session import case_payload_versions, case_redaction, run_gnd_verifier, run_session
    from gnd.exp.session_contract import read_session_contract
    source = repository / 'tests/fixtures/v61-phase5/session'
    scenario = 'reordered' if reordered else 'refused' if refused else 'deficient' if deficient else 'accepted'
    experiment = scratch / scenario
    shutil.copytree(source, experiment)
    if deficient or refused:
        steps_path = experiment / 'candidate/steps.json'
        steps = json.loads(steps_path.read_text(encoding='utf-8'))
        if deficient:
            steps['steps'] = [step for step in steps['steps'] if step['op'] != 'approve_expense']
        else:
            steps['model_digest'] = 'sha256:' + '0' * 64
        steps_path.write_text(json.dumps(steps), encoding='utf-8')
    contract_path = experiment / 'contract-v5.json'
    if reordered:
        document = json.loads(contract_path.read_text(encoding='utf-8'))
        floor = document['cases'][0]
        document['cases'] = [{**floor, 'case_id': 'z-floor'}, {**floor, 'case_id': 'a-floor'}]
        contract_path.write_text(json.dumps(document), encoding='utf-8')
    contract = read_session_contract(contract_path, experiment_root=experiment, experiment_id='EXP-061-walk-floor')
    contract_sha = _sha256(contract_path.read_bytes())

    async def verifier(case, snapshot):
        return await run_gnd_verifier(case, snapshot, experiment_root=experiment, timeout_seconds=30.0)
    run_root = experiment / 'runs/run-0001'
    result = await run_session(contract, contract_sha256=contract_sha, adapter_id=AgentAdapterId.codex, prompt='Installed Phase 5 matrix probe.', candidate_root=experiment / 'candidate', run_root=run_root, verifier=verifier, invoker=_fake_invoker(), expected_payload_versions=case_payload_versions(contract, experiment), redaction=case_redaction(contract, experiment))
    feedback = json.loads((run_root / 'attempts/0001/feedback.json').read_text(encoding='utf-8'))
    attempt = json.loads((run_root / 'attempts/0001/attempt.json').read_text(encoding='utf-8'))
    return (result, feedback, attempt)


def _literal_values(annotation: object) -> set[object]:
    if get_origin(annotation) is Literal:
        return set(get_args(annotation))
    values: set[object] = set()
    for argument in get_args(annotation):
        values.update(_literal_values(argument))
    return values

def observe(repository: Path) -> dict[str, object]:
    from gnd.cli import _session_result_exit
    from gnd.exp.close import CloseResult, _declared_case_findings, _SessionRun, close_outcome
    from gnd.exp.session_eval import AttemptFeedback
    from gnd.exp.session_store import AttemptRecord, SessionResult
    with tempfile.TemporaryDirectory(prefix='gnd-phase5-installed-') as temporary:
        scratch = Path(temporary)
        accepted, accepted_feedback, accepted_attempt = asyncio.run(_run(repository, scratch, deficient=False))
        deficient, _deficient_feedback, _deficient_attempt = asyncio.run(_run(repository, scratch, deficient=True))
        close_exits = []
        for scenario, result in (('accepted', accepted), ('deficient', deficient)):
            experiment = scratch / scenario
            (experiment / 'session.contract.json').write_bytes((experiment / 'contract-v5.json').read_bytes())
            run_root = experiment / 'runs/run-0001'
            findings = _declared_case_findings(_SessionRun(index=1, root=run_root, result=None, launched=True), experiment, (run_root / 'result.json').read_bytes())
            close_exits.append(close_outcome(CloseResult(findings=findings, declared=(), resolved=())))
    return {'contract-v5': 5, 'feedback-v7': accepted_feedback['schema_version'] == 7 and 7 in _literal_values(AttemptFeedback.model_fields['schema_version'].annotation), 'attempt-v7': accepted_attempt['schema_version'] == 7 and 7 in _literal_values(AttemptRecord.model_fields['schema_version'].annotation), 'result-v5': accepted.schema_version == 5 and 5 in _literal_values(SessionResult.model_fields['schema_version'].annotation), 'accepted-floor': accepted.disposition.value == 'accepted', 'deficient-floor': deficient.disposition.value != 'accepted', 'accepted-parent-exit': _session_result_exit(accepted), 'deficient-parent-exit': _session_result_exit(deficient), 'close-accepted': close_exits[0], 'close-refused': close_exits[1], 'evidence-not-current': {'assurance_level': 'none', 'scope_id': 'applicability:refusal:n-a:evidence-not-current'}}
