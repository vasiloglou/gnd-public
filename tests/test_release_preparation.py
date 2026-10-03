"""Bounded build-origin and offline identity controls, not candidate acceptance."""
import hashlib
import os
import shlex
import shutil
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_workflow_never_publishes_and_keeps_origins_separate():
    text = (ROOT / '.github/workflows/release.yml').read_text()
    assert 'workflow_dispatch:' in text
    assert 'push:' not in text and 'pull_request:' not in text
    assert 'id-token:' not in text and 'pypa/gh-action-pypi-publish' not in text
    assert 'uv publish' not in text and 'twine' not in text
    assert text.count('uv build') == 2
    from ruamel.yaml import YAML
    workflow = YAML(typ='safe').load(text)
    assert workflow['on'] == {'workflow_dispatch': None}
    builds = [shlex.split(line.strip())
              for step in workflow['jobs']['prepare']['steps']
              for line in step.get('run', '').splitlines()
              if line.strip().startswith('uv build ')]
    assert builds == [
        ['uv', 'build', '--out-dir', 'candidate/release'],
        ['uv', 'build', '--wheel', 'candidate/source/*', '--out-dir', '$PWD/candidate/comparison'],
    ]
    assert 'sha256sum -c SHA256SUMS' in text


@pytest.mark.parametrize('mutation', ['exact', 'missing', 'changed'])
def test_promotion_identity_refuses_changed_files(tmp_path, mutation):
    # Exercise the actual documented offline primitive, not mocked success.
    artifact = tmp_path / 'release.whl'
    artifact.write_bytes(b'prepared artifact')
    sdist = tmp_path / 'release.tar.gz'
    sdist.write_bytes(b'prepared source')
    (tmp_path / 'SHA256SUMS').write_text(''.join(
        hashlib.sha256(p.read_bytes()).hexdigest() + '  ' + p.name + '\n'
        for p in [artifact, sdist]
    ))
    if mutation == 'missing':
        artifact.unlink()
    if mutation == 'changed':
        artifact.write_bytes(b'different artifact')
    command = ['sha256sum'] if shutil.which('sha256sum') else ['shasum', '-a', '256']
    run = subprocess.run([*command, '-c', 'SHA256SUMS'], cwd=tmp_path, check=False, capture_output=True)
    assert (run.returncode == 0) == (mutation == 'exact')


@pytest.mark.distribution
def test_two_wheel_build_import_smoke(tmp_path):
    env = {k: v for k, v in os.environ.items() if k not in {'PYTHONPATH', 'PYTHONHOME', 'VIRTUAL_ENV'}}
    env['PYTHONNOUSERSITE'] = '1'
    def run(args, cwd=tmp_path):
        result = subprocess.run(args, cwd=cwd, env=env, check=False, capture_output=True, text=True, timeout=180)
        assert result.returncode == 0, result.stdout + result.stderr
        return result.stdout
    release = tmp_path / 'release'
    comparison = tmp_path / 'comparison'
    run(['uv', 'build', '--out-dir', str(release)], ROOT)
    sdist = next(release.glob('*.tar.gz'))
    unpacked = tmp_path / 'source'
    unpacked.mkdir()
    with tarfile.open(sdist) as archive:
        archive.extractall(unpacked, filter='data')
    run(['uv', 'build', '--wheel', str(next(unpacked.iterdir())), '--out-dir', str(comparison)])
    identities = []
    for origin, wheel in [('release', next(release.glob('*.whl'))), ('sdist-wheel', next(comparison.glob('*.whl')))]:
        with zipfile.ZipFile(wheel) as archive:
            names = archive.namelist()
            assert 'gnd/yaml_comments.py' in names
            assert any(n.endswith('/LICENSE') for n in names)
            assert any(n.endswith('/NOTICE') for n in names)
            for domain in ['dispatch', 'release']:
                assert f'gnd/examples/{domain}/model.orm.json' in names
            payload_bytes = sum(i.file_size for i in archive.infolist())
            assert payload_bytes <= 12 * 1024 * 1024
            print('Preparation wheel payload:', origin, payload_bytes, 'bytes')
        venv = tmp_path / ('venv-' + origin)
        run(['uv', 'venv', '--python', sys.executable, str(venv)])
        python = venv / 'bin/python'
        run(['uv', 'pip', 'install', '--python', str(python), str(wheel)])
        code = """import gnd,json,sys
from pathlib import Path
from importlib.resources import files
from gnd import api
assert Path(gnd.__file__).is_relative_to(Path(sys.prefix))
import importlib.util
assert importlib.util.find_spec('faker') is None
assert importlib.util.find_spec('pytest') is None
for d in ['dispatch','release']:
 p=files('gnd')/'examples'/d
 for f,e in [('seed.pop.json',1),('repaired.pop.json',0)]:
  assert api.check(p/'model.orm.json',p/f,admission=True)['exit_code']==e
print(gnd.__file__)
"""
        run([str(python), '-c', code])
        run([str(venv / 'bin/gnd'), '--help'])
        identities.append((origin, hashlib.sha256(wheel.read_bytes()).hexdigest()))
    identities.append(('sdist', hashlib.sha256(sdist.read_bytes()).hexdigest()))
    print('Preparation artifact identities:', identities)


def test_workflow_control_rejects_overwriting_comparison(monkeypatch):
    original = Path.read_text
    workflow = ROOT / '.github/workflows/release.yml'

    def overwritten(path, *args, **kwargs):
        value = original(path, *args, **kwargs)
        if path == workflow:
            return value.replace('--out-dir "$PWD/candidate/comparison"',
                                 '--out-dir "$PWD/candidate/release"')
        return value

    monkeypatch.setattr(Path, 'read_text', overwritten)
    with pytest.raises(AssertionError):
        test_workflow_never_publishes_and_keeps_origins_separate()
