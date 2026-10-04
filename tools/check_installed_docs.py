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
from pathlib import Path


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
            assert payload < 12 * 1024 * 1024, payload
            for domain in ('bookrec', 'expense', 'dispatch', 'release'):
                assert any(name.startswith(f'gnd/examples/{domain}/') for name in archive.namelist())
        venv = out / f'venv-{origin}'
        run(['uv', 'venv', '--python', sys.executable, venv])
        python = venv / 'bin/python'
        run(['uv', 'pip', 'install', '--python', python, wheel])
        installed = run([python, '-c', 'import gnd; print(gnd.__file__)']).strip()
        check_origin(installed, venv, root)
        output = run([python, tutorial / 'tools/run_tutorials.py', '--root', tutorial,
                      '--python', python])
        (out / f'{origin}-tutorials.txt').write_text(output)
        results.append({'origin': origin, 'artifact': str(wheel.relative_to(out)),
                        'sha256': hashlib.sha256(wheel.read_bytes()).hexdigest(),
                        'payload_bytes': payload, 'result': output.splitlines()[-1]})
    assert results[0]['sha256'] == results[1]['sha256'], 'wheel origins differ'
    results.append({'origin': 'sdist', 'artifact': str(sdist.relative_to(out)),
                    'sha256': hashlib.sha256(sdist.read_bytes()).hexdigest()})
    (out / 'results.json').write_text(json.dumps(results, indent=2) + '\n')
    print('Both installed wheel origins passed the documented learning paths.')


if __name__ == '__main__':
    main()
