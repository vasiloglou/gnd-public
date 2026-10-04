"""Execute explicitly marked, trusted repository tutorial blocks as written."""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

MARKER = re.compile(r"<!-- gnd-run expect=(\d+) -->\s*\n```(sh|python)\n(.*?)\n```", re.DOTALL)


def blocks(page: Path):
    text = page.read_text()
    rows = [(m.start(), m.group(2), int(m.group(1)), m.group(3))
            for m in MARKER.finditer(text)]
    if not rows or len(rows) != text.count('gnd-run expect='):
        raise AssertionError(f'{page}: missing or malformed runnable block')
    for _, language, expected, code in sorted(rows):
        if not code.strip():
            raise AssertionError(f'{page}: empty runnable block')
        yield language, expected, code


def run_pages(pages: list[Path], cwd: Path, python: Path) -> int:
    cwd.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    for key in ('PYTHONPATH', 'PYTHONHOME', 'PYTEST_ADDOPTS', 'PYTEST_PLUGINS'):
        env.pop(key, None)
    env['PATH'] = str(python.absolute().parent) + os.pathsep + env.get('PATH', '')
    env['PYTEST_DISABLE_PLUGIN_AUTOLOAD'] = '1'
    env['PYTHONUTF8'] = '1'
    count = 0
    for page in pages:
        for index, (language, expected, code) in enumerate(blocks(page), 1):
            argv = ([str(python), '-c', code] if language == 'python'
                    else ['/bin/bash', '-euo', 'pipefail', '-c', code])
            result = subprocess.run(argv, cwd=cwd, env=env, capture_output=True,
                                    text=True, timeout=300, check=False)
            if result.returncode != expected:
                raise AssertionError(
                    f'{page.name} block {index}: expected {expected}, got {result.returncode}\n'
                    f'{code}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}')
            count += 1
        print(f'{page.name}: executable blocks passed', flush=True)
    return count


def groups(root: Path) -> dict[str, list[Path]]:
    return {
        'quickstart': [root / 'docs/quickstart.md', root / 'README.md'],
        'release': [root / 'docs/release-example.md'],
        'bookrec': sorted((root / 'docs/bookrec').glob('[0-9]*.md')),
        'expense': sorted((root / 'docs/expense').glob('[0-9]*.md')),
        'api': [root / 'docs/reference/python-api.md'],
        'walkthrough': [root / 'docs/walkthrough.md'],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--python', type=Path, default=Path(sys.executable))
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--group', choices=['quickstart', 'release', 'bookrec', 'expense', 'api', 'walkthrough'])
    args = parser.parse_args()
    total = 0
    for name, pages in groups(args.root).items():
        if args.group and name != args.group:
            continue
        if not pages:
            raise AssertionError(f'{name}: no tutorial pages')
        with tempfile.TemporaryDirectory(prefix=f'gnd-docs-{name}-') as directory:
            total += run_pages(pages, Path(directory), args.python.absolute())
    print(f'{total} tutorial blocks passed')


if __name__ == '__main__':
    main()
