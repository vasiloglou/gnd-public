"""Execute explicitly marked, trusted repository tutorial blocks as written."""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

LANES = ('offline', 'pyrel', 'souffle', 'lean', 'all')
MARKER = re.compile(r"<!-- gnd-run expect=(\d+)(?: lane=([a-z]+))? -->\s*\n```(sh|python)\n(.*?)\n```", re.DOTALL)


def parsed_blocks(page: Path):
    text = page.read_text()
    rows = [(m.start(), m.group(3), int(m.group(1)), m.group(4), m.group(2) or 'offline')
            for m in MARKER.finditer(text)]
    if not rows or len(rows) != text.count('gnd-run expect='):
        raise AssertionError(f'{page}: missing or malformed runnable block')
    for _, language, expected, code, lane in sorted(rows):
        if not code.strip():
            raise AssertionError(f'{page}: empty runnable block')
        if lane not in LANES[:-1]:
            raise AssertionError(f'{page}: unknown executable lane {lane}')
        yield language, expected, code, lane


def blocks(page: Path):
    for language, expected, code, _ in parsed_blocks(page):
        yield language, expected, code


def require_runtime(lane: str, python: Path, env: dict) -> None:
    if lane == 'pyrel':
        python = Path(env.get('GND_TUTORIAL_PYREL_PYTHON', python))
        argv = [str(python), '-c', "from importlib.metadata import version; assert version('relationalai') == '1.30.1'; assert version('duckdb') == '1.5.5'; print('PyRel 1.30.1\\nDuckDB 1.5.5')"]
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


def run_pages(pages: list[Path], cwd: Path, python: Path, lane: str = 'offline') -> int:
    if lane not in LANES:
        raise AssertionError(f'unknown lane {lane}')
    cwd.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    for key in ('PYTHONPATH', 'PYTHONHOME', 'PYTEST_ADDOPTS', 'PYTEST_PLUGINS'):
        env.pop(key, None)
    env['PATH'] = str(python.absolute().parent) + os.pathsep + env.get('PATH', '')
    env['PYTEST_DISABLE_PLUGIN_AUTOLOAD'] = '1'
    env['PYTHONUTF8'] = '1'
    count = 0
    checked = set()
    skipped = set()
    for page in pages:
        for index, (language, expected, code, block_lane) in enumerate(parsed_blocks(page), 1):
            if block_lane != 'offline' and lane not in (block_lane, 'all'):
                skipped.add(block_lane)
                continue
            if block_lane != 'offline' and block_lane not in checked:
                require_runtime(block_lane, python, env)
                checked.add(block_lane)
            block_python = Path(env.get('GND_TUTORIAL_PYREL_PYTHON', python)) if block_lane == 'pyrel' else python
            block_env = dict(env)
            block_env['PATH'] = str(block_python.absolute().parent) + os.pathsep + env['PATH']
            argv = ([str(block_python), '-c', code] if language == 'python'
                    else ['/bin/bash', '-euo', 'pipefail', '-c', code])
            result = subprocess.run(argv, cwd=cwd, env=block_env, capture_output=True,
                                    text=True, timeout=600 if block_lane == 'pyrel' else 300, check=False)
            if result.returncode != expected:
                raise AssertionError(
                    f'{page.name} block {index}: expected {expected}, got {result.returncode}\n'
                    f'{code}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}')
            count += 1
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
        'agent-install': [root / 'docs/agents/install.md'],
        'agent-plans': [root / 'docs/agents/plans.md'],
        'agent-model': [root / 'docs/agents/model-from-text.md'],
        'agent-session': [root / 'docs/agents/dev-session.md'],
        'runtime-pyrel': [root / 'docs/runtimes/scenario.md', root / 'docs/runtimes/pyrel.md'],
        'runtime-souffle': [root / 'docs/runtimes/scenario.md', root / 'docs/runtimes/souffle.md'],
        'runtime-lean': [root / 'docs/runtimes/scenario.md', root / 'docs/runtimes/lean.md'],
        'runtime-decision': [root / 'docs/runtimes/scenario.md', root / 'docs/runtimes/decision.md'],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--python', type=Path, default=Path(sys.executable))
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--group', choices=list(groups(Path('.'))))
    parser.add_argument('--lane', choices=LANES, default='offline')
    args = parser.parse_args()
    total = 0
    for name, pages in groups(args.root).items():
        if args.group and name != args.group:
            continue
        if not pages:
            raise AssertionError(f'{name}: no tutorial pages')
        with tempfile.TemporaryDirectory(prefix=f'gnd-docs-{name}-') as directory:
            total += run_pages(pages, Path(directory), args.python.absolute(), args.lane)
    print(f'{total} tutorial blocks passed')


if __name__ == '__main__':
    main()
