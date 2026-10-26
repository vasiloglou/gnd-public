"""Execute explicitly marked, trusted repository tutorial blocks as written."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

LANES = ('offline', 'pyrel', 'souffle', 'lean', 'all')
MARKER = re.compile(r"<!-- gnd-run expect=(\d+)(?: lane=([a-z]+))?(?: output=(stdout|stderr))? -->\s*\n"
                    r"```(sh|python)\n(.*?)\n```(?:[ \t]*\n\s*```text\n(.*?)\n```)?", re.DOTALL)


def _parsed(page: Path, text: str | None = None):
    text = page.read_text() if text is None else text
    rows = [(m.start(), m.group(4), int(m.group(1)), m.group(5), m.group(2) or 'offline', m.group(3), m.group(6))
            for m in MARKER.finditer(text)]
    if not rows or len(rows) != text.count('gnd-run expect='):
        raise AssertionError(f'{page}: missing or malformed runnable block')
    for _, language, expected, code, lane, stream, shown in sorted(rows):
        if not code.strip():
            raise AssertionError(f'{page}: empty runnable block')
        if lane not in LANES[:-1]:
            raise AssertionError(f'{page}: unknown executable lane {lane}')
        if stream and not (shown or '').strip():
            raise AssertionError(f'{page}: missing or malformed output block')
        yield language, expected, code, lane, stream, (shown if stream else None)


def parsed_blocks(page: Path, *, text: str | None = None):
    for language, expected, code, lane, _, _ in _parsed(page, text):
        yield language, expected, code, lane


def parsed_outputs(page: Path):
    """(stream, expected text) for every block; stream is None where no output is shown."""
    return [(stream, shown) for *_, stream, shown in _parsed(page)]


def normalize_output(text: str, cwd: Path) -> list[str]:
    for root in sorted({str(cwd), str(cwd.resolve())}, key=len, reverse=True):
        text = text.replace(root, '<run>')
    text = re.sub(r'gnd-native-(?:application|checker)-[A-Za-z0-9_]+', '<tmp>', text)
    text = re.sub(r'\b\d+\.\d+s\b', '<time>', text)
    lines = [line.rstrip() for line in text.splitlines()]
    while lines and not lines[-1]:
        lines.pop()
    return lines


def output_matches(expected: list[str], actual: list[str]) -> bool:
    """Line equality, where an expected line '...' matches any run of actual lines."""
    reachable = {0}
    for line in expected:
        if line == '...':
            reachable = set(range(min(reachable), len(actual) + 1)) if reachable else set()
        else:
            reachable = {i + 1 for i in reachable if i < len(actual) and actual[i] == line}
    return len(actual) in reachable


def blocks(page: Path):
    for language, expected, code, _ in parsed_blocks(page):
        yield language, expected, code


def require_runtime(lane: str, python: Path, env: dict) -> dict:
    if lane == 'pyrel':
        base_python = python.absolute()
        if not env.get('GND_TUTORIAL_PYREL_PYTHON'):
            raise AssertionError('pyrel: required explicit native interpreter GND_TUTORIAL_PYREL_PYTHON')
        python = Path(env['GND_TUTORIAL_PYREL_PYTHON'])
        if not python.is_absolute() or python == base_python:
            raise AssertionError('pyrel: required absolute separate native interpreter')
        argv = [str(python), '-c', "from importlib.metadata import version; import json; v={'relationalai':version('relationalai'),'duckdb':version('duckdb')}; print('PyRel '+v['relationalai']+'\\nDuckDB '+v['duckdb']); print(json.dumps(v))"]
    else:
        key, default = ('GND_TUTORIAL_SOUFFLE', 'souffle') if lane == 'souffle' else ('GND_TUTORIAL_LAKE', 'lake')
        tool = shutil.which(env.get(key, default), path=env['PATH'])
        if not tool:
            raise AssertionError(f'{lane}: required tool absent ({key})')
        argv = [tool, '--version']
    try:
        result = subprocess.run(argv, env=env, text=True, capture_output=True, timeout=30, check=False)
    except OSError as error:
        raise AssertionError(f'{lane}: required runtime absent: {error}') from error
    output = result.stdout + result.stderr
    pattern = {'pyrel': r'PyRel 1\.30\.1\s+DuckDB 1\.5\.5(?:\s|$)', 'souffle': r'Version: 2\.5(?:\s|$)',
               'lean': r'(?:Lean|Lake) version 4\.34\.0(?:\s|\)|$)'}[lane]
    if result.returncode or not re.search(pattern, output):
        raise AssertionError(f'{lane}: required runtime version unavailable\n{output}')
    if lane == 'souffle' and 'Word size: 64 bits' not in output:
        raise AssertionError('souffle: required 64-bit runtime unavailable')
    if lane == 'pyrel':
        try:
            versions = json.loads(result.stdout.strip().splitlines()[-1])
        except (ValueError, IndexError) as error:
            raise AssertionError('pyrel: required runtime identity JSON unavailable') from error
        if versions != {'relationalai': '1.30.1', 'duckdb': '1.5.5'}:
            raise AssertionError('pyrel: required runtime identity mismatch')
        return versions
    return {
            'souffle': {'souffle': '2.5', 'word_bits': 64},
            'lean': {'lean': '4.34.0'}}[lane]


def run_pages(pages: list[Path], cwd: Path, python: Path, lane: str = 'offline',
              *, receipts: list[dict] | None = None, group: str | None = None) -> int:
    if lane not in LANES:
        raise AssertionError(f'unknown lane {lane}')
    if receipts is not None and not isinstance(receipts, list):
        raise AssertionError('receipts must be a list or None')
    cwd.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    for key in ('PYTHONPATH', 'PYTHONHOME', 'PYTEST_ADDOPTS', 'PYTEST_PLUGINS', 'GND_PYREL_PYTHON'):
        env.pop(key, None)
    env['PATH'] = str(python.absolute().parent) + os.pathsep + env.get('PATH', '')
    env['PYTEST_DISABLE_PLUGIN_AUTOLOAD'] = '1'
    env['PYTHONUTF8'] = '1'
    env['GND_TUTORIAL_GND_PYTHON'] = str(python.absolute())
    count = 0
    checked = {}
    skipped = set()
    for page in pages:
        page_raw = page.read_bytes()
        for index, (language, expected, code, block_lane, stream, shown) in enumerate(
                _parsed(page, page_raw.decode('utf-8')), 1):
            observation = {'page': page.parent.name + '/' + page.name, 'group': group,
                           'page_sha256': hashlib.sha256(page_raw).hexdigest(),
                           'base_python': str(python.absolute()),
                           'native_python': env.get('GND_TUTORIAL_PYREL_PYTHON'),
                           'block': index, 'lane': block_lane,
                           'expected_exit': expected,
                           'code_sha256': hashlib.sha256(code.encode()).hexdigest()}
            if block_lane != 'offline' and lane not in (block_lane, 'all'):
                skipped.add(block_lane)
                if receipts is not None:
                    receipts.append({**observation, 'status': 'skipped'})
                continue
            if block_lane != 'offline' and block_lane not in checked:
                checked[block_lane] = require_runtime(block_lane, python, env)
            block_python = Path(env['GND_TUTORIAL_PYREL_PYTHON']) if block_lane == 'pyrel' else python
            block_env = dict(env)
            if block_lane == 'pyrel':
                # Bare `python` and `gnd` keep meaning the GND environment, as in a reader's
                # shell; the PyRel interpreter is only ever named by this variable.
                block_env['GND_PYREL_PYTHON'] = str(block_python.absolute())
            argv = ([str(block_python), '-c', code] if language == 'python'
                    else ['/bin/bash', '-euo', 'pipefail', '-c', code])
            started = time.monotonic()
            result = subprocess.run(argv, cwd=cwd, env=block_env, capture_output=True,
                                    text=True, timeout=600 if block_lane == 'pyrel' else 300, check=False)
            observation.update(actual_exit=result.returncode,
                               block_python=str(block_python.absolute()),
                               runtime_versions=checked.get(block_lane),
                               elapsed_seconds=round(time.monotonic() - started, 6),
                               stdout_sha256=hashlib.sha256(result.stdout.encode()).hexdigest(),
                               stderr_sha256=hashlib.sha256(result.stderr.encode()).hexdigest(),
                               output_checked=bool(stream))
            actual = normalize_output(result.stdout if stream == 'stdout' else result.stderr, cwd) if stream else []
            output_ok = not stream or output_matches(normalize_output(shown, cwd), actual)
            # Status is decided once, after both the exit and the shown-output comparison.
            observation['status'] = 'passed' if result.returncode == expected and output_ok else 'failed'
            if receipts is not None:
                receipts.append(observation)
            if result.returncode != expected:
                raise AssertionError(
                    f'{page.name} block {index}: expected {expected}, got {result.returncode}\n'
                    f'{code}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}')
            if not output_ok:
                raise AssertionError(f'{page.name} block {index}: {stream} output differs from the page\n'
                                     f'expected:\n{shown}\nactual:\n' + '\n'.join(actual))
            count += 1
        if page.read_bytes() != page_raw:
            raise AssertionError(f'{page.name}: tutorial page changed during execution')
        print(f'{page.name}: selected executable blocks passed', flush=True)
    if skipped:
        print('Native lanes not executed: ' + ', '.join(sorted(skipped)), flush=True)
    if checked:
        print('Native lanes executed: ' + ', '.join(sorted(checked)), flush=True)
    return count


def groups(root: Path) -> dict[str, list[Path]]:
    return {
        'quickstart': [root / 'docs/quickstart.md', root / 'README.md'],
        'release': [root / 'docs/release-example.md'],
        'bookrec': sorted((root / 'docs/bookrec').glob('[0-9]*.md')),
        'expense': sorted((root / 'docs/expense').glob('[0-9]*.md')),
        'api': [root / 'docs/reference/python-api.md'],
        'walkthrough': [root / 'docs/walkthrough.md'],
        'induced': [root / 'docs/tutorials/learn-rules.md'],
        'agent-install': [root / 'docs/agents/install.md'],
        'agent-plans': [root / 'docs/agents/plans.md'],
        'agent-model': [root / 'docs/agents/model-from-text.md'],
        'agent-session': [root / 'docs/agents/dev-session.md'],
        'agent-recorded': [root / 'docs/agents/recorded-sessions.md'],
        'runtime-pyrel': [root / 'docs/runtimes/scenario.md', root / 'docs/runtimes/pyrel.md'],
        'runtime-souffle': [root / 'docs/runtimes/scenario.md', root / 'docs/runtimes/souffle.md'],
        'runtime-lean': [root / 'docs/runtimes/scenario.md', root / 'docs/runtimes/lean.md'],
        'runtime-decision': [root / 'docs/runtimes/scenario.md', root / 'docs/runtimes/decision.md'],
        'plan-apps': [root / 'docs/tutorials/course-planner.md', root / 'docs/tutorials/clinic-refills.md',
                      root / 'docs/how-to/access-requests.md', root / 'docs/how-to/trip-budget.md',
                      root / 'docs/how-to/lease-schedule.md', root / 'docs/explanation/rules-as-pyrel.md'],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--python', type=Path, default=Path(sys.executable))
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--group', choices=list(groups(Path('.'))))
    parser.add_argument('--lane', choices=LANES, default='offline')
    parser.add_argument('--receipt', type=Path, help='Record observed step timings after a completed run')
    args = parser.parse_args()
    if args.receipt and (args.receipt.exists() or args.receipt.is_symlink()
                         or not args.receipt.parent.is_dir()):
        parser.error('receipt needs an existing parent and a fresh output path')
    total = 0
    receipts = []
    for name, pages in groups(args.root).items():
        if args.group and name != args.group:
            continue
        if not pages:
            raise AssertionError(f'{name}: no tutorial pages')
        with tempfile.TemporaryDirectory(prefix=f'gnd-docs-{name}-') as directory:
            total += run_pages(pages, Path(directory), args.python.absolute(), args.lane,
                               receipts=receipts, group=name)
    if args.receipt:
        try:
            from gnd.artifacts import ArtifactError
            from gnd.safefs import artifact_publish_leaf_atomic

            data = json.dumps({'schema_version': 1, 'lane': args.lane,
                    'scope': 'Execution of shipped steps; excludes setup, authoring and review time.',
                    'records': receipts}, indent=2) + '\n'
            artifact_publish_leaf_atomic(args.receipt.parent, args.receipt.name, data.encode())
        except (OSError, ArtifactError) as error:
            parser.error(f'receipt publication failed: {type(error).__name__}')
    print(f'{total} tutorial blocks passed')


if __name__ == '__main__':
    main()
