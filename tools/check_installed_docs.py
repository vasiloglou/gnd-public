"""Build two wheel origins and run actual tutorial Markdown outside the checkout."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tarfile
import zipfile
from email.parser import Parser
from pathlib import Path

from run_tutorials import GROUP_EXTRAS


def declared_extras(archive: zipfile.ZipFile) -> list[str]:
    """The extras a wheel declares, read from its METADATA headers."""
    metadata = [name for name in archive.namelist()
                if name.count('/') == 1 and name.split('/')[0].endswith('.dist-info')
                and name.endswith('/METADATA')]
    assert len(metadata) == 1, metadata
    headers = Parser().parsestr(archive.read(metadata[0]).decode('utf-8'), headersonly=True)
    return sorted(headers.get_all('Provides-Extra') or [])


def check_origin(installed: str, venv: Path, root: Path) -> None:
    path = Path(installed).resolve()
    assert path.is_relative_to(venv.resolve()) and not path.is_relative_to(root.resolve()), installed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    env = os.environ.copy()
    for key in ('PYTHONPATH', 'PYTHONHOME', 'VIRTUAL_ENV'):
        env.pop(key, None)
    env['PYTHONNOUSERSITE'] = '1'

    def run(argv, cwd=out):
        result = subprocess.run([str(a) for a in argv], cwd=cwd, env=env, text=True,
                                capture_output=True, timeout=600, check=False)
        print(result.stdout, end='', flush=True)
        if result.returncode:
            raise AssertionError(f'{argv}: exit {result.returncode}\n{result.stderr}')
        return result.stdout

    run(['uv', 'build', '--out-dir', out / 'release'], root)
    sdist = next((out / 'release').glob('*.tar.gz'))
    source = out / 'source'
    source.mkdir()
    with tarfile.open(sdist) as archive:
        archive.extractall(source, filter='data')
    run(['uv', 'build', '--wheel', next(source.iterdir()), '--out-dir', out / 'comparison'])
    tutorial = out / 'tutorial-source'
    shutil.copytree(root / 'docs', tutorial / 'docs')
    shutil.copy2(root / 'README.md', tutorial / 'README.md')
    shutil.copytree(root / 'tools', tutorial / 'tools', ignore=shutil.ignore_patterns('__pycache__'))
    results = []
    for origin in ('release', 'comparison'):
        wheel = next((out / origin).glob('*.whl'))
        with zipfile.ZipFile(wheel) as archive:
            payload = sum(info.file_size for info in archive.infolist())
            # 13 MiB: the owner raised the wheel budget at induction-skill IS2 checkpoint C2.
            assert payload < 13 * 1024 * 1024, payload
            for domain in ('bookrec', 'expense', 'dispatch', 'release', 'release_governance', 'approvals', 'plan_apps', 'refunds', 'quoted_claims'):
                assert any(name.startswith(f'gnd/examples/{domain}/') for name in archive.namelist())
            declared = declared_extras(archive)
        # The extras the extra-needing groups name, each of which the wheel must declare.
        extras = sorted({extra for needed in GROUP_EXTRAS.values() for extra in needed})
        assert set(extras) <= set(declared), (extras, declared)
        # Groups that need no extra run on the bare install a reader of those pages gets; the groups
        # whose pages name an extra (run_tutorials.GROUP_EXTRAS) run with those extras.
        passes = []
        installs = [('without', str(wheel))] + ([('with', f'{wheel}[{",".join(extras)}]')] if extras else [])
        for scope, spec in installs:
            venv = out / f'venv-{origin}-{scope}-extras'
            run(['uv', 'venv', '--python', sys.executable, venv])
            python = venv / 'bin/python'
            run(['uv', 'pip', 'install', '--python', python, spec])
            installed = run([python, '-c', 'import gnd; print(gnd.__file__)']).strip()
            check_origin(installed, venv, root)
            output = run([python, tutorial / 'tools/run_tutorials.py', '--root', tutorial,
                          '--python', python, '--extras-scope', scope])
            (out / f'{origin}-{scope}-extras-tutorials.txt').write_text(output)
            passes.append({'install': Path(spec).name, 'groups': f'{scope} extras',
                           'result': output.splitlines()[-1]})
        results.append({'origin': origin, 'artifact': str(wheel.relative_to(out)),
                        'sha256': hashlib.sha256(wheel.read_bytes()).hexdigest(),
                        'payload_bytes': payload, 'extras': extras, 'passes': passes})
    assert results[0]['sha256'] == results[1]['sha256'], 'wheel origins differ'
    results.append({'origin': 'sdist', 'artifact': str(sdist.relative_to(out)),
                    'sha256': hashlib.sha256(sdist.read_bytes()).hexdigest()})
    (out / 'results.json').write_text(json.dumps(results, indent=2) + '\n')
    print('Both installed wheel origins passed the documented learning paths.')


if __name__ == '__main__':
    main()
