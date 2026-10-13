"""Bounded build-origin and offline identity controls, not candidate acceptance."""
import hashlib
import io
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


def test_workflow_preparation_is_separate_from_opt_in_publication():
    text = (ROOT / '.github/workflows/release.yml').read_text()
    assert 'workflow_dispatch:' in text
    assert 'push:' not in text and 'pull_request:' not in text
    assert 'uv publish' not in text and 'twine' not in text
    assert text.count('uv build') == 2
    from ruamel.yaml import YAML
    workflow = YAML(typ='safe').load(text)
    assert set(workflow['on']) == {'workflow_dispatch'}
    inputs = workflow['on']['workflow_dispatch']['inputs']
    assert inputs['publish']['type'] == 'boolean'
    assert inputs['publish']['default'] is False
    assert set(workflow['jobs']) == {'prepare', 'publish'}
    assert workflow['permissions'] == {'contents': 'read'}
    prepare = workflow['jobs']['prepare']
    assert prepare['if'] == "github.ref == 'refs/heads/main'"
    assert prepare.get('permissions', workflow['permissions']) == {'contents': 'read'}
    assert not any('pypa/gh-action-pypi-publish' in step.get('uses', '')
                   for step in prepare['steps'])
    builds = [shlex.split(line.strip())
              for step in prepare['steps']
              for line in step.get('run', '').splitlines()
              if line.strip().startswith('uv build ')]
    assert builds == [
        ['uv', 'build', '--out-dir', 'candidate/release'],
        ['uv', 'build', '--wheel', 'candidate/source/*', '--out-dir', '$PWD/candidate/comparison'],
    ]
    assert 'sha256sum -c SHA256SUMS' in text
    publish = workflow['jobs']['publish']
    assert publish['if'] == "inputs.publish && github.ref == 'refs/heads/main'"
    assert publish['needs'] == 'prepare'
    assert publish['environment']['name'] == 'pypi'
    assert publish['permissions'] == {'contents': 'read', 'actions': 'read', 'id-token': 'write'}
    steps = publish['steps']
    downloads = [i for i, step in enumerate(steps)
                 if step.get('uses', '').startswith('actions/download-artifact@')]
    publishers = [i for i, step in enumerate(steps)
                  if step.get('uses', '').startswith('pypa/gh-action-pypi-publish@')]
    assert len(downloads) == len(publishers) == 1
    downloaded = steps[downloads[0]]['with']
    assert downloaded['name'] == 'preparation-${{ github.sha }}-${{ github.run_id }}'
    assert downloaded['path'] == 'candidate'
    verifiers = [i for i, step in enumerate(steps)
                 if 'sha256sum -c SHA256SUMS' in step.get('run', '')]
    assert len(verifiers) == 1 and downloads[0] < verifiers[0] < publishers[0]
    verifier = steps[verifiers[0]]
    assert verifier['working-directory'] == 'candidate'
    assert verifier['env']['EXPECTED_COMMIT'] == '${{ github.sha }}'
    assert 'test "$(cat SOURCE_COMMIT)" = "$EXPECTED_COMMIT"' in verifier['run']
    assert steps[publishers[0]]['with']['packages-dir'] == 'candidate/release/'
    assert steps[publishers[0]]['with']['attestations'] is True
    assert not any('uv build' in step.get('run', '') for step in steps)


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
        test_workflow_preparation_is_separate_from_opt_in_publication()


@pytest.mark.parametrize('mutation', [
    'publish-by-default', 'unguarded-publisher', 'missing-acceptance',
    'unprotected-environment', 'publish-from-prepare', 'wrong-artifact',
    'missing-verifier', 'publish-comparison',
])
def test_workflow_control_rejects_unsafe_publication(monkeypatch, mutation):
    from ruamel.yaml import YAML
    yaml = YAML(typ='safe')
    path = ROOT / '.github/workflows/release.yml'
    workflow = yaml.load(path.read_text())
    publish = workflow['jobs']['publish']
    if mutation == 'publish-by-default':
        workflow['on']['workflow_dispatch']['inputs']['publish']['default'] = True
    elif mutation == 'unguarded-publisher':
        publish['if'] = "github.ref == 'refs/heads/main'"
    elif mutation == 'missing-acceptance':
        del publish['needs']
    elif mutation == 'unprotected-environment':
        publish['environment']['name'] = 'unprotected'
    elif mutation == 'publish-from-prepare':
        workflow['jobs']['prepare']['steps'].append({'uses': 'pypa/gh-action-pypi-publish@fake'})
    elif mutation == 'wrong-artifact':
        publish['steps'][0]['with']['name'] = 'unvalidated-candidate'
    elif mutation == 'missing-verifier':
        publish['steps'] = [step for step in publish['steps']
                            if 'sha256sum -c SHA256SUMS' not in step.get('run', '')]
    elif mutation == 'publish-comparison':
        for step in publish['steps']:
            if step.get('uses', '').startswith('pypa/gh-action-pypi-publish@'):
                step['with']['packages-dir'] = 'candidate/comparison/'
    stream = io.StringIO()
    yaml.dump(workflow, stream)
    original = Path.read_text
    monkeypatch.setattr(Path, 'read_text',
                        lambda target, *args, **kwargs: stream.getvalue() if target == path
                        else original(target, *args, **kwargs))
    with pytest.raises((AssertionError, KeyError)):
        test_workflow_preparation_is_separate_from_opt_in_publication()
