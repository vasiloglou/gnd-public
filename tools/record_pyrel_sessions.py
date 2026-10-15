"""Record real coding-assistant sessions on the BookRec and Expense tasks.

This is the ONLY place in the repository that calls a model. It runs the owner's
installed terminal agents (Claude Code and Codex) through ``gnd exp run`` with a
declared command policy, against a clean installed GND from which the two
example folders have been removed, so the answers are not on disk. Every run is
kept; the committed recording is the agent's candidate, GND's closed feedback and
the agent's stdout (with the workspace and home paths replaced), plus a manifest
of SHA-256 digests. Pages quote these bytes; they never re-run a model.

Refuses to start without ``--authorized-by PATH`` naming the owner's gate record.
The repository ``.env`` is never sourced; ``tools/agent_with_env_key.py`` reads one named
key from it as data for Claude Code only. Hosted models are out of scope here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STDOUT_CAP = 256 * 1024
AGENTS = {
    'claude': {
        'tool': 'Claude Code',
        'executable': 'claude',
        # The standalone CLI has no login of its own on this machine, so the wrapper imports
        # exactly one key from the owner's env file as data; the adapter never sees it.
        'wrapper_key': 'ANTHROPIC_API_KEY',
        'argv': ['--print', '--permission-mode', 'acceptEdits', '--allowedTools',
                 'Bash(gnd *),Read,Write,Edit,Glob,Grep', '--add-dir', '{experiment}',
                 '--output-format', 'stream-json', '--verbose', '{prompt}'],
        'environment_allowlist': ['PATH', 'HOME', 'TMPDIR', 'LANG', 'LC_ALL', 'CLAUDE_CONFIG_DIR'],
    },
    'codex': {
        'tool': 'Codex CLI',
        'executable': 'codex',
        'wrapper_key': None,
        'argv': ['exec', '--json', '--skip-git-repo-check', '--sandbox', 'workspace-write',
                 '--color', 'never', '--model', '{codex_model}', '{prompt}'],
        'environment_allowlist': ['PATH', 'HOME', 'TMPDIR', 'LANG', 'LC_ALL', 'CODEX_HOME'],
    },
}
DOMAINS = {
    'bookrec': {'model': 'model.orm.yaml', 'subject': 'recommendation.population.json',
                'coverage': 'recommendation', 'experiment': 'EXP-003-recommend-ada',
                'question': 'Q1=Can a coding assistant recommend books for Ada that pass every rule?'},
    'expense': {'model': 'model.orm.json', 'subject': 'approvals.population.json',
                'coverage': 'expense_approved_by_chain', 'experiment': 'EXP-004-approve-102',
                'question': 'Q1=Can a coding assistant record an approval of expense 102 that passes every rule?'},
}
TASKS = {
    ('bookrec', 'plain'): """# Task

Recommend books for Ada.

Write `recommendation.population.json` in the current directory (the candidate
directory): a copy of `../input/seed.population.json` whose `recommendation`
list contains at least two books for `ada`. Keep every other fact list and the
`population` header exactly as they are. The rules are in `../model.orm.yaml`;
the books, genres, ratings and reader preferences are in the seed facts.

If you can run commands, check your file with
`gnd check ../model.orm.yaml recommendation.population.json` and fix it until
the check exits 0. Edit nothing outside the candidate directory.
""",
    ('bookrec', 'conflict'): """# Task

Ada liked the look of `night` and asked for it. Recommend books for Ada,
including `night`.

Write `recommendation.population.json` in the current directory (the candidate
directory): a copy of `../input/seed.population.json` whose `recommendation`
list contains at least two books for `ada`. Keep every other fact list and the
`population` header exactly as they are. The rules are in `../model.orm.yaml`;
the books, genres, ratings and reader preferences are in the seed facts.

If you can run commands, check your file with
`gnd check ../model.orm.yaml recommendation.population.json` and fix it until
the check exits 0. Edit nothing outside the candidate directory.
""",
    ('expense', 'plain'): """# Task

Record an approval of expense 102.

Write `approvals.population.json` in the current directory (the candidate
directory): a copy of `../input/seed.population.json` with expense `102` added
to `expense_is_approved` and to `expense_approved_by_chain`, naming the chain
that approves it. Keep every other fact and the `population` header exactly as
they are. The rules, including who may approve how much, are in
`../model.orm.json`.

If you can run commands, check your file with
`gnd check ../model.orm.json approvals.population.json` and fix it until the
check exits 0. Edit nothing outside the candidate directory.
""",
    ('expense', 'conflict'): """# Task

Dana, the team lead, approved expense 102 this morning. Record it.

Write `approvals.population.json` in the current directory (the candidate
directory): a copy of `../input/seed.population.json` with expense `102` added
to `expense_is_approved` and to `expense_approved_by_chain` with the chain
`team-lead`. Keep every other fact and the `population` header exactly as they
are. The rules, including who may approve how much, are in `../model.orm.json`.

If you can run commands, check your file with
`gnd check ../model.orm.json approvals.population.json` and fix it until the
check exits 0. Edit nothing outside the candidate directory.
""",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def run(argv, *, cwd=None, env=None, timeout=1800, check=True):
    completed = subprocess.run([str(a) for a in argv], cwd=cwd, env=env, capture_output=True,
                               text=True, timeout=timeout, check=False)
    if check and completed.returncode != 0:
        raise SystemExit(f'{argv[0]} failed ({completed.returncode}):\n{completed.stdout}\n{completed.stderr}')
    return completed


def clean_install(workspace: Path) -> Path:
    """Install GND from this checkout into a fresh environment and remove the two example folders."""
    env_dir = workspace / 'rec-env'
    run(['uv', 'venv', str(env_dir), '--python', sys.executable])
    python = env_dir / 'bin' / 'python'
    run(['uv', 'pip', 'install', '--python', str(python), str(ROOT)])
    probe = run([python, '-c', 'import gnd, pathlib; print(pathlib.Path(gnd.__file__).parent)'])
    package = Path(probe.stdout.strip())
    if ROOT in package.parents:
        raise SystemExit('the recording environment imports gnd from the checkout; refusing')
    for domain in DOMAINS:
        shutil.rmtree(package / 'examples' / domain)
    probe_examples = ("from importlib.resources import files; import sys; "
                      "sys.exit(0 if not files('gnd').joinpath('examples','bookrec').is_dir() else 1)")
    run([python, '-c', probe_examples])
    return env_dir


def bound(experiment: Path, relative: str, media_type: str) -> dict:
    data = (experiment / relative).read_bytes()
    return {'path': relative, 'media_type': media_type, 'encoding': 'utf-8',
            'sha256': sha256(data), 'size_bytes': len(data)}


def prepare_experiment(workspace: Path, gnd: Path, domain: str, variant: str, max_attempts: int,
                       index: int) -> Path:
    spec = DOMAINS[domain]
    source = ROOT / 'src/gnd/examples' / domain
    experiment = workspace / f'{spec["experiment"]}-{variant}-{index}'
    run([gnd, 'exp', 'init', experiment.name, '--out', str(workspace), '--kind', 'data-driven',
         '--question', spec['question']])
    (experiment / 'input').mkdir()
    (experiment / 'candidate').mkdir()
    shutil.copy(source / spec['model'], experiment / spec['model'])
    shutil.copy(source / 'seed.population.json', experiment / 'input/seed.population.json')
    (experiment / 'input/TASK.md').write_text(TASKS[(domain, variant)], encoding='utf-8')
    contract = {
        'schema_version': 6, 'experiment_id': experiment.name, 'max_attempts': max_attempts,
        'wall_seconds': 900.0, 'adapter': {'policy_id': 'recorded-agent', 'parameters': {'model': None}},
        'cases': [{
            'case_id': 'required', 'role': 'required',
            'inputs': [bound(experiment, 'input/seed.population.json', 'application/json'),
                       bound(experiment, 'input/TASK.md', 'text/markdown')],
            'acceptance': {'mode': 'constraint-satisfaction',
                           'coverage': [{'fact_type': spec['coverage'], 'min_facts': 2}]},
            'verify': {'command': 'check', 'model': bound(experiment, spec['model'], 'application/json'),
                       'subject': spec['subject']},
        }],
    }
    (experiment / 'session.contract.json').write_text(json.dumps(contract, indent=2) + '\n')
    run([gnd, 'exp', 'validate', experiment.name], cwd=workspace)
    return experiment


def write_policy(workspace: Path, agent: str, experiment: Path, *, env_file: Path, codex_model: str) -> Path:
    spec = AGENTS[agent]
    executable = shutil.which(spec['executable'])
    if executable is None:
        raise SystemExit(f'{spec["executable"]} is not on PATH')
    words = [word.replace('{experiment}', str(experiment)).replace('{codex_model}', codex_model)
             for word in spec['argv']]
    if spec['wrapper_key']:
        policy_executable = sys.executable
        argv = [str(ROOT / 'tools/agent_with_env_key.py'), '--env-file', str(env_file.resolve()),
                '--name', spec['wrapper_key'], '--', spec['executable'], *words]
    else:
        policy_executable = executable
        argv = words
    policy = {
        'schema_version': 1, 'policy_id': 'recorded-agent', 'kind': 'command', 'executable': policy_executable,
        'argv': argv, 'version_argv': ['--version'], 'prompt_transport': 'argv',
        'environment_allowlist': spec['environment_allowlist'],
    }
    path = workspace / f'{agent}-{experiment.name}.policy.json'
    path.write_text(json.dumps(policy, indent=2) + '\n')
    return path


def redact(text: str, substitutions: list[tuple[str, str]]) -> str:
    for needle, replacement in substitutions:
        text = text.replace(needle, replacement)
    return text


def harvest(experiment: Path, run_dir: Path, destination: Path, substitutions) -> dict:
    """Copy one run's attempts into the recordings tree; return its manifest entry."""
    files: dict[str, str] = {}
    source_digests: dict[str, str] = {}
    result = json.loads((run_dir / 'result.json').read_text())
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True)
    (destination / 'result.json').write_text(json.dumps(
        {k: result[k] for k in ('disposition', 'attempt_count', 'best_attempt', 'terminal_reason')}, indent=2) + '\n')
    subject = json.loads((experiment / 'session.contract.json').read_text())['cases'][0]['verify']['subject']
    bands = []
    for attempt in sorted((run_dir / 'attempts').glob('[0-9]*')):
        target = destination / f'attempt-{attempt.name}'
        target.mkdir()
        candidate = attempt / 'candidate' / subject
        if candidate.exists():
            shutil.copy(candidate, target / subject)
        feedback = attempt / 'feedback.json'
        shutil.copy(feedback, target / 'feedback.json')
        payload = json.loads(feedback.read_text())
        exits = {case: code for case, code in payload.get('payload_exit', [])}
        bands.append(exits.get('required', 3 if payload.get('disposition') != 'accepted' else 0))
        stdout = attempt / 'agent.stdout'
        if stdout.exists():
            raw = stdout.read_bytes()
            source_digests[f'{target.relative_to(destination.parent)}/agent.stdout'] = sha256(raw)
            text = raw[:STDOUT_CAP].decode('utf-8', errors='replace')
            (target / 'agent.stdout').write_text(redact(text, substitutions), encoding='utf-8')
    for path in destination.rglob('*'):
        if path.is_file():
            files[str(path.relative_to(destination.parent))] = sha256(path.read_bytes())
    return {'result': result['disposition'], 'attempts': result['attempt_count'], 'bands': bands,
            'files': files, 'source_stdout_sha256': source_digests}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--authorized-by', required=True, type=Path,
                        help='the owner gate record that authorizes these live runs')
    parser.add_argument('--agents', default='claude,codex')
    parser.add_argument('--domains', default='bookrec,expense')
    parser.add_argument('--variants', default='conflict,plain')
    parser.add_argument('--runs', type=int, default=2)
    parser.add_argument('--max-attempts', type=int, default=3)
    parser.add_argument('--workspace', type=Path, help='fresh directory for the clean install and experiments')
    parser.add_argument('--out', type=Path, default=ROOT / 'src/gnd/examples', help='recordings parent')
    parser.add_argument('--env-file', type=Path, default=ROOT / '.env',
                        help='owner env file read as data for the one key Claude Code needs')
    parser.add_argument('--codex-model', default='gpt-5.6-sol')
    parser.add_argument('--keep-experiments', action='store_true')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    gate = args.authorized_by
    if not gate.is_file() or 'recording' not in gate.read_text(encoding='utf-8').lower():
        parser.error('--authorized-by must name an existing gate record that mentions recording')
    agents = [a for a in args.agents.split(',') if a]
    domains = [d for d in args.domains.split(',') if d]
    variants = [v for v in args.variants.split(',') if v]
    unknown = [a for a in agents if a not in AGENTS] + [d for d in domains if d not in DOMAINS]
    if unknown:
        parser.error(f'unknown selection: {unknown}')
    plan = [(a, d, v, r) for d in domains for v in variants for a in agents for r in range(1, args.runs + 1)]
    if args.dry_run:
        for row in plan:
            print('would run', *row)
        return 0
    workspace = args.workspace or Path(tempfile.mkdtemp(prefix='gnd-rec-'))
    workspace.mkdir(parents=True, exist_ok=True)
    env_dir = clean_install(workspace)
    gnd = env_dir / 'bin' / 'gnd'
    env = {k: v for k, v in os.environ.items() if not k.endswith(('_KEY', '_TOKEN', '_SECRET'))}
    env['PATH'] = str(env_dir / 'bin') + os.pathsep + env.get('PATH', '')
    run(['git', 'init', '-q', str(workspace)])
    run([gnd, 'install', '--project'], cwd=workspace, env=env)
    versions = {agent: run([shutil.which(AGENTS[agent]['executable']), '--version'], env=env).stdout.strip()
                for agent in agents}
    substitutions = [(str(workspace.resolve()), '<workspace>'), (str(workspace), '<workspace>'),
                     (str(Path.home()), '<home>')]
    today = datetime.now(UTC).date().isoformat()
    sessions: dict[str, list] = {}
    manifests: dict[str, dict] = {}
    for agent, domain, variant, index in plan:
        experiment = prepare_experiment(workspace, gnd, domain, variant, args.max_attempts, index)
        policy = write_policy(workspace, agent, experiment, env_file=args.env_file, codex_model=args.codex_model)
        started = time.monotonic()
        completed = run([gnd, 'exp', 'run', experiment.name, '--adapter-policy', str(policy)],
                        cwd=workspace, env=env, check=False, timeout=3600)
        elapsed = round(time.monotonic() - started, 1)
        runs = sorted((experiment / 'runs').glob('run-*'))
        if not runs:
            print(f'{agent} {domain} {variant} run {index}: no run directory ({completed.returncode})\n'
                  f'{completed.stderr[-800:]}', file=sys.stderr)
            sessions.setdefault(domain, []).append({'agent': AGENTS[agent]['tool'], 'variant': variant,
                                                    'run': index, 'disposition': 'agent-failure',
                                                    'attempts': 0, 'bands': [], 'exit': completed.returncode})
            if not args.keep_experiments:
                shutil.rmtree(experiment)
            continue
        name = f'{agent}-{variant}-{index}'
        destination = args.out / domain / 'recordings' / name
        entry = harvest(experiment, runs[-1], destination, substitutions)
        entry.update(kind='terminal agent', tool=versions[agent], variant=variant, run=index,
                     model=args.codex_model if agent == 'codex' else 'the account default at recording time',
                     route=f'gnd exp run --adapter-policy ({agent})', elapsed_seconds=elapsed,
                     exit=completed.returncode)
        manifests.setdefault(domain, {})[name] = entry
        sessions.setdefault(domain, []).append({'agent': AGENTS[agent]['tool'], 'variant': variant, 'run': index,
                                                'disposition': entry['result'], 'attempts': entry['attempts'],
                                                'bands': entry['bands'], 'exit': completed.returncode})
        print(f'{agent} {domain} {variant} run {index}: {entry["result"]} after {entry["attempts"]} '
              f'attempt(s), bands {entry["bands"]}, {elapsed}s', flush=True)
        if not args.keep_experiments:
            shutil.rmtree(experiment)
    for domain in domains:
        target = args.out / domain / 'recordings'
        target.mkdir(parents=True, exist_ok=True)
        for variant in variants:
            (target / f'TASK-{variant}.md').write_text(TASKS[(domain, variant)], encoding='utf-8')
        (target / 'results.json').write_text(json.dumps(
            {'recorded_on': today, 'max_attempts': args.max_attempts, 'tools': versions,
             'sessions': sessions.get(domain, [])}, indent=2) + '\n')
        (target / 'manifest.json').write_text(json.dumps(
            {'recorded_on': today, 'redactions': ['<workspace>', '<home>'],
             'stdout_cap_bytes': STDOUT_CAP, 'recordings': manifests.get(domain, {})}, indent=2, sort_keys=True) + '\n')
    print(f'workspace retained at {workspace}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
