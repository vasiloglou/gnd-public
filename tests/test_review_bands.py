from __future__ import annotations

import inspect
import json
import os
import stat
import sys
from pathlib import Path
from typing import Any

import pytest
from support.digests import sha256_bytes as _sha256

from gnd import cli
from gnd.cli import main
from gnd.review.adapters import (
    REVIEWER_IDS,
    ReviewEffort,
    ReviewerId,
    ReviewerPolicy,
    reviewer_policies,
)
from gnd.review.request import (
    MVP_TRIAGE_CRITERION,
    canonical_review_request,
    validate_review_request,
)
from gnd.review.runner import MAX_REVIEW_STREAM_BYTES, load_panel_run

PLAN_TEXT = b'# Plan\n\nBound every reviewer process and publish its evidence.\n'
REPO_ROOT = Path(__file__).resolve().parent.parent

def _response(reviewer: str) -> bytes:
    payload = {'schema_version': 1, 'reviewer_id': reviewer, 'disposition': 'revise', 'summary': f'{reviewer} reviewed the plan against the rubric.', 'concerns': [{'concern_id': f'concern-{reviewer}', 'severity': 'medium', 'relevance': 'blocking', 'title': 'The plan does not bound retained output', 'evidence': [{'artifact_path': 'plan.md', 'location': 'line 3', 'observation': 'No maximum retained byte count is stated.'}], 'recommendation': 'State an explicit per-stream byte cap.'}]}
    return json.dumps(payload, sort_keys=True, separators=(',', ':')).encode()
_FAKE_HELP = {ReviewerId.claude: 'Usage: claude [options] [prompt]\nOptions: --print --safe-mode --model --effort --permission-mode --output-format --no-session-persistence\n', ReviewerId.codex: 'Usage: codex exec [options] [prompt]\nOptions: --ephemeral --ignore-user-config --model --config --sandbox --color --skip-git-repo-check\n', ReviewerId.qwen: 'Usage: qwen [options]\nOptions: --bare --safe-mode --sandbox --model --auth-type --openai-base-url --approval-mode --max-wall-time --max-session-turns --max-tool-calls --max-subagent-depth --exclude-tools --output-format --prompt\n', ReviewerId.gemini: 'Usage: gemini [options]\nOptions: --model --approval-mode --skip-trust --output-format --prompt\n', ReviewerId.kimi: 'Usage: kimi [options]\nOptions: --model --output-format --prompt\n', ReviewerId.glm: 'Usage: claude [options] [prompt]\nOptions: --print --safe-mode --model --effort --permission-mode --output-format --no-session-persistence\n'}

def _capability_help(policy: ReviewerPolicy) -> str:
    return _FAKE_HELP[policy.reviewer_id]

def _script(seats: list[tuple[ReviewerPolicy, str]], record: Path) -> str:
    helps = {_capability_help(policy) for policy, _behavior in seats}
    assert len(helps) == 1, 'one executable has one help surface'
    capability = helps.pop()
    seat_config = {policy.reviewer_id.value: {'behavior': behavior, 'response': _response(policy.reviewer_id.value)} for policy, behavior in seats}
    return f"""#!{sys.executable}\nimport os\nimport sys\nimport time\n\nseat_config = {seat_config!r}\nif len(seat_config) == 1:\n    reviewer = next(iter(seat_config))\nelse:\n    reviewer = 'glm' if os.environ.get('ANTHROPIC_BASE_URL') == 'https://api.z.ai/api/anthropic' else 'claude'\nbehavior = seat_config[reviewer]['behavior']\nresponse = seat_config[reviewer]['response']\n\nwith open({str(record)!r}, 'a', encoding='utf-8') as handle:\n    handle.write(reviewer + '\\n')\n\nif '--help' in sys.argv:\n    if behavior == 'incompatible':\n        sys.stdout.write('usage: reviewer [options]\\nmissing required invocation flag\\n')\n    else:\n        sys.stdout.write({capability!r})\n    raise SystemExit(0)\n\nsys.stdin.buffer.read()\n\nif behavior == 'success':\n    os.write(1, response)\nelif behavior == 'timeout':\n    time.sleep(30)\nelif behavior == 'auth':\n    sys.stderr.write('authentication required: invalid api key')\n    raise SystemExit(7)\nelif behavior == 'auth-missing-key':\n    sys.stderr.write("Missing API key for OpenAI-compatible auth. Set the 'OPENROUTER_API_KEY' environment variable.")\n    raise SystemExit(1)\nelif behavior == 'success-mentions-auth':\n    os.write(1, response.replace(b'summary', b'summary', 1))\n    sys.stderr.write('note: the reviewed plan leaves an unauthorized path undocumented; please log in flows unspecified')\nelif behavior == 'malformed':\n    os.write(1, b'{{"schema_version":1,')\nelse:\n    raise SystemExit('unknown behavior ' + behavior)\n"""

def _repository(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, behaviors: dict[str, str], *, plan_text: bytes=PLAN_TEXT, request_bytes: bytes | None=None, write_plan: bool=True) -> Path:
    repository = tmp_path / 'repo'
    repository.mkdir(exist_ok=True)
    if write_plan:
        (repository / 'plan.md').write_bytes(plan_text)
    if request_bytes is None:
        request_bytes = canonical_review_request(validate_review_request({'schema_version': 1, 'kind': 'plan', 'plan': {'path': 'plan.md', 'sha256': _sha256(plan_text), 'media_type': 'text/markdown'}, 'rubric': {'name': 'bounded-execution review', 'criteria': ['Reject unbounded execution.', MVP_TRIAGE_CRITERION]}}))
    (repository / 'request.json').write_bytes(request_bytes)
    bin_dir = tmp_path / 'bin'
    bin_dir.mkdir(exist_ok=True)
    record = tmp_path / 'invocations.log'
    groups: dict[str, list[ReviewerPolicy]] = {}
    for policy in reviewer_policies():
        groups.setdefault(policy.executable_name, []).append(policy)
    for name, group in groups.items():
        seats = [(policy, behaviors[policy.reviewer_id.value]) for policy in group]
        missing = [policy for policy, behavior in seats if behavior == 'missing']
        if missing and len(missing) < len(group):
            raise AssertionError(f'{name!r} is one executable shared by {[policy.reviewer_id.value for policy in group]}; it cannot be missing for one seat only')
        if missing:
            continue
        executable = bin_dir / name
        executable.write_text(_script(seats, record), encoding='utf-8')
        executable.chmod(executable.stat().st_mode | stat.S_IXUSR)
    for name in list(os.environ):
        if name not in {'PATH', 'HOME', 'TMPDIR', 'LANG', 'TERM', 'USER', 'LOGNAME'}:
            monkeypatch.delenv(name, raising=False)
    (tmp_path / 'home').mkdir(exist_ok=True)
    monkeypatch.setenv('HOME', str(tmp_path / 'home'))
    monkeypatch.setenv('PATH', os.pathsep.join(dict.fromkeys([str(bin_dir), str(Path(sys.executable).parent), '/usr/bin', '/bin'])))
    monkeypatch.chdir(repository)
    return repository

def _behaviors(successes: int, filler: str='incompatible') -> dict[str, str]:
    return {reviewer.value: 'success' if index < successes else filler for index, reviewer in enumerate(REVIEWER_IDS)}

def _panel(out: Path, request: str='request.json') -> list[str]:
    return ['review', 'panel', request, '--out', str(out), '--reviewer-timeout', '6', '--overall-timeout', '20', '--max-output-bytes', '65536']

def _panel_light(out: Path, request: str='request.json', *, effort: str | None=None) -> list[str]:
    argv = _panel(out, request)
    argv[1] = 'panel-light'
    if effort is not None:
        argv.extend(('--effort', effort))
    return argv

def _run_panel(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], behaviors: dict[str, str]) -> tuple[int, dict[str, Any], Path]:
    _repository(tmp_path, monkeypatch, behaviors)
    out = tmp_path / 'panel-run'
    exit_code = main(_panel(out))
    captured = capsys.readouterr().out
    payload = json.loads(captured.splitlines()[-1]) if captured.strip() else {}
    return (exit_code, payload, out)

def _help_text(capsys: pytest.CaptureFixture[str], argv: list[str]) -> str:
    with pytest.raises(SystemExit):
        main(argv)
    return ' '.join(capsys.readouterr().out.split())

def test_the_panel_help_exposes_every_path_and_positive_resource_bound(capsys: pytest.CaptureFixture[str]) -> None:
    text = _help_text(capsys, ['review', 'panel', '--help'])
    for flag in ('--out', '--reviewer-timeout', '--overall-timeout', '--max-output-bytes'):
        assert flag in text, f'gnd review panel --help does not expose {flag}'
    assert 'positive' in text
    for code in ('Exits 0', ' 16 ', ' 3 ', ' 11 ', ' 64 ', ' 66 ', ' 70 ', ' 74 '):
        assert code in text, f'gnd review panel --help does not mention {code.strip()}'
    for forbidden in ('--executable', '--provider', '--model', '--argv', '--api-key'):
        assert forbidden not in text, f'{forbidden} would let argv choose what runs'

def test_the_light_panel_help_exposes_only_high_and_medium_effort(capsys: pytest.CaptureFixture[str]) -> None:
    text = _help_text(capsys, ['review', 'panel-light', '--help'])
    assert '--effort' in text
    assert 'high' in text and 'medium' in text
    assert 'xhigh' not in text
    for flag in ('--out', '--reviewer-timeout', '--overall-timeout', '--max-output-bytes'):
        assert flag in text

@pytest.mark.parametrize(('argument', 'expected'), ((None, ReviewEffort.high), ('medium', ReviewEffort.medium)))
def test_the_light_panel_defaults_high_and_accepts_medium(argument: str | None, expected: ReviewEffort, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    _repository(tmp_path, monkeypatch, _behaviors(3))
    out = tmp_path / 'panel-run'
    assert main(_panel_light(out, effort=argument)) == 0
    payload = json.loads(capsys.readouterr().out)
    run = load_panel_run(out)
    assert payload['command'] == 'review panel-light'
    assert payload['reviewer_effort'] == expected.value
    assert run.reviewer_effort is expected

def test_the_finalize_help_exposes_the_run_synthesis_report_boundary(capsys: pytest.CaptureFixture[str]) -> None:
    text = _help_text(capsys, ['review', 'finalize', '--help'])
    assert 'run' in text and 'synthesis' in text and ('--out' in text)
    assert 'never replaced' in text
    for code in ('Exits 0', ' 16 ', ' 3 ', ' 11 ', ' 64 ', ' 66 ', ' 74 '):
        assert code in text, f'gnd review finalize --help does not mention {code.strip()}'

def test_the_review_help_states_the_shipped_six_reviewer_surface(capsys: pytest.CaptureFixture[str]) -> None:
    text = _help_text(capsys, ['review', '--help'])
    assert 'six' in text
    assert 'three' in text
    assert 'kimi' in text
    assert 'glm' in text
    assert 'documents every long flag' in text
    assert 'GND does not sandbox reviewer CLIs' in text
    assert 'unchanged before publishing' in text

def test_review_without_a_subcommand_is_a_usage_error() -> None:
    with pytest.raises(SystemExit) as caught:
        main(['review'])
    assert caught.value.code == cli.EXIT_USAGE

def test_a_quorum_run_exits_zero(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    exit_code, payload, out = _run_panel(tmp_path, monkeypatch, capsys, _behaviors(3))
    assert exit_code == 0
    assert payload['quorum_met'] is True
    assert payload['outcome'] == 'quorum-established'
    assert payload['reviewer_effort'] == ReviewEffort.xhigh.value
    assert len(payload['successful_reviewer_ids']) == 3
    assert len(payload['reviewer_statuses']) == 6
    run = load_panel_run(out)
    assert run.quorum_met is True
    assert run.reviewer_effort is ReviewEffort.xhigh

def test_exactly_two_successes_exit_sixteen(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    exit_code, payload, out = _run_panel(tmp_path, monkeypatch, capsys, _behaviors(2))
    assert exit_code == cli.EXIT_REVIEW_INCONCLUSIVE
    assert payload['quorum_met'] is False
    assert payload['outcome'] == 'inconclusive-below-quorum'
    assert payload['successful_reviewer_ids'] == ['claude', 'codex']
    assert len(load_panel_run(out).envelopes) == 6

def test_a_missing_credential_is_an_auth_failure_not_a_reviewer_defect(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    behaviors = {'claude': 'success', 'codex': 'success', 'qwen': 'auth-missing-key', 'gemini': 'success', 'kimi': 'success', 'glm': 'success'}
    exit_code, payload, _ = _run_panel(tmp_path, monkeypatch, capsys, behaviors)
    statuses = {entry['reviewer_id']: entry['status'] for entry in payload['reviewer_statuses']}
    assert statuses['qwen'] == 'auth-failure'
    assert exit_code == 0
    assert payload['quorum_met'] is True

def test_a_reviewer_whose_own_prose_discusses_authorization_still_counts(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    behaviors = dict.fromkeys(('claude', 'codex', 'qwen', 'gemini', 'kimi', 'glm'), 'success')
    behaviors['qwen'] = 'success-mentions-auth'
    exit_code, payload, _ = _run_panel(tmp_path, monkeypatch, capsys, behaviors)
    statuses = {entry['reviewer_id']: entry['status'] for entry in payload['reviewer_statuses']}
    assert statuses['qwen'] == 'success'
    assert 'qwen' in payload['successful_reviewer_ids']
    assert exit_code == 0

def test_three_distinct_failures_and_one_success_exit_sixteen(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    behaviors = {'claude': 'timeout', 'codex': 'auth', 'qwen': 'missing', 'gemini': 'success', 'kimi': 'incompatible', 'glm': 'malformed'}
    exit_code, payload, out = _run_panel(tmp_path, monkeypatch, capsys, behaviors)
    assert exit_code == cli.EXIT_REVIEW_INCONCLUSIVE
    assert payload['successful_reviewer_ids'] == ['gemini']
    statuses = {entry['reviewer_id']: entry['status'] for entry in payload['reviewer_statuses']}
    assert statuses == {'claude': 'timeout', 'codex': 'auth-failure', 'qwen': 'missing', 'gemini': 'success', 'kimi': 'incompatible', 'glm': 'malformed'}
    run = load_panel_run(out)
    assert all(envelope.issues or envelope.response for envelope in run.envelopes)

def test_a_malformed_request_exits_three_and_spawns_nothing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _repository(tmp_path, monkeypatch, _behaviors(4), request_bytes=b'{"schema_version":1,"kind":"plan","plan":{"path":"plan.md"}}\n')
    out = tmp_path / 'panel-run'
    assert main(_panel(out)) == 3
    assert not out.exists()
    assert not (tmp_path / 'invocations.log').exists(), 'a malformed request reached a reviewer'

def test_a_missing_reviewed_artifact_exits_sixty_six(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _repository(tmp_path, monkeypatch, _behaviors(4), write_plan=False)
    out = tmp_path / 'panel-run'
    assert main(_panel(out)) == cli.EXIT_NO_INPUT
    assert not out.exists()

def test_invalid_review_request_never_reopens_or_probes_untrusted_artifact_paths(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    request = {'schema_version': 1, 'kind': 'plan', 'plan': {'path': '../../outside-secret', 'sha256': '0' * 64, 'media_type': 'text/markdown'}, 'rubric': {'name': 'bounded', 'criteria': ['Stay inside the repository.', MVP_TRIAGE_CRITERION]}}
    _repository(tmp_path, monkeypatch, _behaviors(4), request_bytes=json.dumps(request).encode('utf-8'))
    original_read_bytes = Path.read_bytes

    def forbidden_path_read(path: Path) -> bytes:
        if path.name == 'request.json':
            raise AssertionError('invalid review request was reopened by pathname')
        return original_read_bytes(path)
    monkeypatch.setattr(Path, 'read_bytes', forbidden_path_read)
    out = tmp_path / 'panel-run'
    assert main(_panel(out)) == 3
    assert not out.exists()

def test_a_missing_request_exits_sixty_six(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _repository(tmp_path, monkeypatch, _behaviors(4))
    (tmp_path / 'repo' / 'request.json').unlink()
    out = tmp_path / 'panel-run'
    assert main(_panel(out)) == cli.EXIT_NO_INPUT

def test_an_existing_output_directory_is_a_collision_that_destroys_nothing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _repository(tmp_path, monkeypatch, _behaviors(4))
    out = tmp_path / 'panel-run'
    out.mkdir()
    (out / 'prior.txt').write_text('kept\n', encoding='utf-8')
    assert main(_panel(out)) == cli.EXIT_COLLISION
    assert (out / 'prior.txt').read_text(encoding='utf-8') == 'kept\n'
    assert not (tmp_path / 'invocations.log').exists(), 'a refused output destination still invoked reviewers'

@pytest.mark.parametrize('bound', [['--reviewer-timeout', '0'], ['--reviewer-timeout', '-1'], ['--reviewer-timeout', 'nan'], ['--overall-timeout', '0'], ['--overall-timeout', '-2.5'], ['--max-output-bytes', '0'], ['--max-output-bytes', '-4096'], ['--max-output-bytes', str(MAX_REVIEW_STREAM_BYTES // 2 + 1)]])
def test_a_non_positive_or_over_ceiling_bound_is_refused_before_any_spawn(bound: list[str], tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _repository(tmp_path, monkeypatch, _behaviors(4))
    out = tmp_path / 'panel-run'
    with pytest.raises(SystemExit) as caught:
        main(['review', 'panel', 'request.json', '--out', str(out), *bound])
    assert caught.value.code == cli.EXIT_USAGE
    assert not out.exists()
    assert not (tmp_path / 'invocations.log').exists(), 'a refused bound still spawned a reviewer'

def test_the_light_panel_refuses_xhigh_before_any_spawn(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _repository(tmp_path, monkeypatch, _behaviors(4))
    out = tmp_path / 'panel-run'
    with pytest.raises(SystemExit) as caught:
        main(_panel_light(out, effort='xhigh'))
    assert caught.value.code == cli.EXIT_USAGE
    assert not out.exists()
    assert not (tmp_path / 'invocations.log').exists()

@pytest.mark.parametrize('request_path', ['/etc/passwd', '../request.json', './request.json'])
def test_an_unsafe_request_path_is_a_usage_error(request_path: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _repository(tmp_path, monkeypatch, _behaviors(4))
    with pytest.raises(SystemExit) as caught:
        main(_panel(tmp_path / 'panel-run', request=request_path))
    assert caught.value.code == cli.EXIT_USAGE

@pytest.mark.parametrize('successful', [0, 1, 2, 3, 4, 5, 6])
def test_the_quorum_table_over_zero_through_six_successes(successful: int) -> None:
    outcome = cli._review_outcome(cli.REVIEW_ATTEMPTED_REVIEWERS, successful)
    if successful >= cli.REVIEW_QUORUM:
        assert outcome == 0
    else:
        assert outcome == cli.EXIT_REVIEW_INCONCLUSIVE
    assert outcome in {0, cli.EXIT_REVIEW_INCONCLUSIVE}

def test_the_attempted_roster_size_is_pinned_to_the_runtime_tuple() -> None:
    assert cli.REVIEW_ATTEMPTED_REVIEWERS == len(REVIEWER_IDS) == 6

@pytest.mark.parametrize('attempted', [0, 1, 3, 4, 5, 7])
def test_a_partial_run_can_never_be_graded_as_below_quorum(attempted: int) -> None:
    with pytest.raises(ValueError):
        cli._review_outcome(attempted, 0)

def test_more_successes_than_attempts_is_refused() -> None:
    with pytest.raises(ValueError):
        cli._review_outcome(cli.REVIEW_ATTEMPTED_REVIEWERS, 7)

def _synthesis_document(run_directory: Path, agreed: list[str], divergent: list[str], *, fixes: list[dict[str, Any]] | None=None, supporting: list[str] | None=None) -> dict[str, Any]:
    run_sha256 = _sha256((run_directory / 'run.json').read_bytes())
    groups: list[dict[str, Any]] = []
    if agreed is not None:
        groups.append({'group_id': 'bounded-output', 'severity': 'medium', 'title': 'Retained output is unbounded', 'summary': 'Independently located by more than one reviewer.', 'concerns': [{'reviewer_id': reviewer, 'concern_id': f'concern-{reviewer}'} for reviewer in agreed], 'supporting_reviewers': supporting if supporting is not None else agreed})
    return {'schema_version': 1, 'run_sha256': run_sha256, 'summary': 'A synthesis over the retained successful responses.', 'agreed_concerns': groups, 'divergent_concerns': [{'reviewer_id': reviewer, 'concern_id': f'concern-{reviewer}'} for reviewer in divergent], 'prioritized_fixes': fixes if fixes is not None else []}

def _finalize(tmp_path: Path, run_directory: Path, document: dict[str, Any], *, report_name: str='PANEL-REVIEW.md') -> int:
    synthesis = tmp_path / 'synthesis.json'
    synthesis.write_text(json.dumps(document, sort_keys=True), encoding='utf-8')
    return main(['review', 'finalize', str(run_directory), str(synthesis), '--out', str(tmp_path / report_name)])

def test_finalize_refuses_a_below_quorum_run_with_sixteen(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    exit_code, _, run_directory = _run_panel(tmp_path, monkeypatch, capsys, _behaviors(2))
    assert exit_code == cli.EXIT_REVIEW_INCONCLUSIVE
    document = _synthesis_document(run_directory, ['claude', 'codex'], [])
    assert _finalize(tmp_path, run_directory, document) == cli.EXIT_REVIEW_INCONCLUSIVE
    payload = json.loads(capsys.readouterr().out.splitlines()[-1])
    assert payload['quorum_met'] is False
    assert payload['report_path'] is None
    assert not (tmp_path / 'PANEL-REVIEW.md').exists(), 'a below-quorum run rendered a report'

@pytest.mark.parametrize('supporters', [0, 1, 2, 3, 4, 5, 6])
def test_the_agreement_table_over_zero_through_six_supporters(supporters: int, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    exit_code, _, run_directory = _run_panel(tmp_path, monkeypatch, capsys, _behaviors(6))
    assert exit_code == 0
    everyone = [reviewer.value for reviewer in REVIEWER_IDS]
    agreed = everyone[:supporters]
    document = _synthesis_document(run_directory, agreed, everyone[supporters:])
    outcome = _finalize(tmp_path, run_directory, document, report_name=f'R{supporters}.md')
    capsys.readouterr()
    if supporters >= 2:
        assert outcome == 0
        assert (tmp_path / f'R{supporters}.md').is_file()
    else:
        assert outcome == 3
        assert not (tmp_path / f'R{supporters}.md').exists()

def test_quorum_and_agreement_are_different_thresholds() -> None:
    from gnd.review import report as review_report
    assert cli.REVIEW_QUORUM == 3
    source = inspect.getsource(review_report.finalize_panel_synthesis)
    assert 'len(supporters) < 2' in source
    assert 'len(responses) < REVIEW_QUORUM' in source

@pytest.mark.parametrize('mutation', ['forged-supporters', 'unknown-concern', 'duplicate-concern', 'incomplete-accounting', 'fix-without-evidence', 'fix-dropping-a-supporter', 'stale-run-digest'])
def test_finalize_refuses_every_overclaiming_synthesis(mutation: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    exit_code, _, run_directory = _run_panel(tmp_path, monkeypatch, capsys, _behaviors(3))
    assert exit_code == 0
    everyone = ['claude', 'codex', 'qwen']
    document = _synthesis_document(run_directory, everyone[:2], everyone[2:])
    if mutation == 'forged-supporters':
        document['agreed_concerns'][0]['supporting_reviewers'] = ['claude', 'codex', 'gemini']
    elif mutation == 'unknown-concern':
        document['agreed_concerns'][0]['concerns'][1] = {'reviewer_id': 'gemini', 'concern_id': 'concern-gemini'}
    elif mutation == 'duplicate-concern':
        document['divergent_concerns'].append({'reviewer_id': 'claude', 'concern_id': 'concern-claude'})
    elif mutation == 'incomplete-accounting':
        document['divergent_concerns'] = []
    elif mutation == 'fix-without-evidence':
        document['prioritized_fixes'] = [{'fix_id': 'cap-output', 'rank': 1, 'title': 'Cap retained output', 'action': 'State a per-stream byte cap.', 'concerns': [{'reviewer_id': 'claude', 'concern_id': 'concern-claude'}, {'reviewer_id': 'codex', 'concern_id': 'concern-codex'}], 'evidence': [], 'supporting_reviewers': ['claude', 'codex']}]
    elif mutation == 'fix-dropping-a-supporter':
        document['prioritized_fixes'] = [{'fix_id': 'cap-output', 'rank': 1, 'title': 'Cap retained output', 'action': 'State a per-stream byte cap.', 'concerns': [{'reviewer_id': 'claude', 'concern_id': 'concern-claude'}], 'evidence': [{'reviewer_id': 'claude', 'concern_id': 'concern-claude', 'evidence_index': 0}], 'supporting_reviewers': ['claude']}]
    else:
        document['run_sha256'] = '0' * 64
    assert _finalize(tmp_path, run_directory, document) == 3
    capsys.readouterr()
    assert not (tmp_path / 'PANEL-REVIEW.md').exists(), 'a refused synthesis still wrote a report'

def test_finalize_never_replaces_an_existing_report(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    exit_code, _, run_directory = _run_panel(tmp_path, monkeypatch, capsys, _behaviors(3))
    assert exit_code == 0
    report = tmp_path / 'PANEL-REVIEW.md'
    report.write_text('an earlier report\n', encoding='utf-8')
    document = _synthesis_document(run_directory, ['claude', 'codex'], ['qwen'])
    assert _finalize(tmp_path, run_directory, document) == cli.EXIT_COLLISION
    capsys.readouterr()
    assert report.read_text(encoding='utf-8') == 'an earlier report\n'

def test_finalize_over_a_missing_run_or_synthesis_exits_sixty_six(tmp_path: Path) -> None:
    absent_run = tmp_path / 'no-run'
    synthesis = tmp_path / 'synthesis.json'
    synthesis.write_text('{}', encoding='utf-8')
    assert main(['review', 'finalize', str(absent_run), str(synthesis), '--out', str(tmp_path / 'R.md')]) == cli.EXIT_NO_INPUT
    present_run = tmp_path / 'run'
    present_run.mkdir()
    assert main(['review', 'finalize', str(present_run), str(tmp_path / 'absent.json'), '--out', str(tmp_path / 'R.md')]) == cli.EXIT_NO_INPUT

def test_the_panel_handler_is_one_thin_programmatic_bridge() -> None:
    source = inspect.getsource(cli._cmd_review_panel)
    assert source.count('asyncio.run(') == 1
    assert source.count('run_review_panel(') == 1
    for forbidden in ('subprocess', 'shell=True', 'os.system', 'shutil.which'):
        assert forbidden not in source, f'{forbidden} in the panel handler would mean the CLI spawns reviewers itself instead of going through the audited adapter policies'

def test_the_finalize_handler_calls_the_public_services_and_parses_no_prose() -> None:
    source = inspect.getsource(cli._cmd_review_finalize)
    assert source.count('finalize_panel_synthesis(') == 1
    assert source.count('render_panel_markdown(') == 1
    assert 'run.quorum_met' in source, "the below-quorum band must be decided on the run's own derived quorum, never read out of an exception message"
    assert 'str(error)' not in source.replace('f"ERROR: {error}"', ''), 'no band may be selected by inspecting rendered prose'

def test_the_review_payload_carries_no_verdict_rate_or_conformance_field(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    _, payload, _ = _run_panel(tmp_path, monkeypatch, capsys, _behaviors(3))
    for forbidden in ('verdicts', 'acceptance_ready', 'counts', 'precision', 'recall', 'assertions', 'findings', 'band'):
        assert forbidden not in payload, f'a review payload must not carry {forbidden!r}'
    assert payload['advisory'] is True
