"""Consume retained candidate artifacts; never rebuild them during acceptance."""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path

import pytest

pytestmark = pytest.mark.distribution
ROOT = Path(__file__).resolve().parents[1]
FAMILIES = [
    'test_checker_families.py', 'test_population_load.py', 'test_public_api.py',
    'test_derivation_rule.py', 'test_transition_mapping_totality.py',
    'test_synth_conforming.py', 'test_extract_cli.py', 'test_doccheck.py',
    'test_codegen_emit.py', 'test_conformance_structural.py',
    'test_model_evolution.py', 'test_recovery_inventory.py',
    'test_exp_session_e2e.py', 'test_v71_phase2_successors.py',
    'test_reference_population_corpus.py', 'test_v70_phase3_successors.py',
    'test_v71_phase4_successors.py', 'test_public_v71_full_judgments.py',
    'test_public_generated_examples.py', 'test_solve_successors.py',
    'test_public_v71_witness_corpus.py', 'test_public_lean_export_successors.py',
    'test_review_request.py', 'test_release_examples.py',
]


def run(args, cwd, env, *, timeout=300, expected=0):
    result = subprocess.run([str(a) for a in args], cwd=cwd, env=env,
                            capture_output=True, text=True, timeout=timeout, check=False)
    assert result.returncode == expected, result.stdout[-12000:] + result.stderr[-12000:]
    return result.stdout


def verify_files(root):
    lines = (root / 'SHA256SUMS').read_text().splitlines()
    expected = set()
    for line in lines:
        sha, name = line.split('  ', 1)
        relative = Path(name)
        assert not relative.is_absolute() and '..' not in relative.parts
        assert name not in expected
        expected.add(name)
        assert hashlib.sha256((root / name).read_bytes()).hexdigest() == sha
    # uv build writes a .gitignore into every output folder it creates; it is not an artifact.
    actual = {p.relative_to(root).as_posix() for folder in ['release', 'comparison']
              for p in (root / folder).iterdir() if p.is_file() and p.name != '.gitignore'}
    assert actual == expected and len(expected) == 3
    assert len(list((root / 'release').glob('*.whl'))) == 1
    assert len(list((root / 'release').glob('*.tar.gz'))) == 1
    assert len(list((root / 'comparison').glob('*.whl'))) == 1


@pytest.fixture(scope='module')
def candidate():
    value = os.environ.get('GND_CANDIDATE_DIR')
    assert value, 'Set GND_CANDIDATE_DIR to the retained candidate; no implicit build'
    root = Path(value).resolve()
    verify_files(root)
    return root


def test_retained_candidate_identity(candidate):
    for wheel in [*candidate.glob('release/*.whl'), *candidate.glob('comparison/*.whl')]:
        with zipfile.ZipFile(wheel) as archive:
            names = archive.namelist()
            assert len(names) == len(set(names))
            assert sum(p.file_size for p in archive.infolist()) <= 12 * 1024 * 1024
            assert 'gnd/yaml_comments.py' in names
            from test_packaged_skills import EXPECTED_SKILL_FILES
            skill_names = {n.removeprefix('gnd/skills/') for n in names
                           if n.startswith('gnd/skills/') and not n.endswith('/')}
            assert skill_names == EXPECTED_SKILL_FILES
            assert sum(n.endswith('/SKILL.md') for n in names) == 16
            assert any(n.endswith('/LICENSE') for n in names)
            assert any(n.endswith('/NOTICE') for n in names)
            for domain in ['dispatch', 'release']:
                assert f'gnd/examples/{domain}/model.orm.json' in names
    with tarfile.open(next(candidate.glob('release/*.tar.gz'))) as archive:
        names = archive.getnames()
        assert len(names) == len(set(names))
        assert all(not Path(n).is_absolute() and '..' not in Path(n).parts for n in names)


@pytest.mark.parametrize('mutation', ['changed', 'missing', 'extra'])
def test_candidate_identity_negative_controls(candidate, tmp_path, mutation):
    copy = tmp_path / 'candidate'
    shutil.copytree(candidate, copy, ignore=shutil.ignore_patterns('source'))
    wheel = next(copy.glob('release/*.whl'))
    if mutation == 'changed':
        wheel.write_bytes(wheel.read_bytes() + b'changed')
    elif mutation == 'missing':
        wheel.unlink()
    else:
        (copy / 'release' / 'extra.whl').write_bytes(b'extra')
    with pytest.raises((AssertionError, FileNotFoundError)):
        verify_files(copy)


@pytest.fixture(scope='module', params=['release', 'comparison'])
def installed(candidate, tmp_path_factory, request):
    outside = tmp_path_factory.mktemp('candidate-' + request.param).resolve()
    env = {k: v for k, v in os.environ.items()
           if k in {'PATH', 'SYSTEMROOT', 'TMPDIR', 'LANG', 'LC_ALL'}}
    env.update(HOME=str(outside / 'home'), PYTHONNOUSERSITE='1',
               PYTEST_DISABLE_PLUGIN_AUTOLOAD='1')
    Path(env['HOME']).mkdir()
    wheel = next(candidate.glob(request.param + '/*.whl'))
    local_wheel = outside / wheel.name
    shutil.copy2(wheel, local_wheel)
    venv = outside / 'base'
    run(['uv', 'venv', '--python', sys.executable, venv], outside, env)
    python = venv / 'bin/python'
    run(['uv', 'pip', 'install', '--python', python, local_wheel], outside, env)
    # Git-tracked candidate only: dirty/untracked local helpers cannot fill a gap.
    checkout = outside / 'checkout'
    checkout.mkdir()
    snapshot = subprocess.run(['git', 'archive', 'HEAD'], cwd=ROOT, capture_output=True, check=True)
    archive = outside / 'checkout.tar'
    archive.write_bytes(snapshot.stdout)
    with tarfile.open(archive) as source:
        source.extractall(checkout, filter='data')
    assert not outside.is_relative_to(ROOT)
    prefix = []
    if sys.platform == 'darwin':
        sandbox = shutil.which('sandbox-exec')
        assert sandbox, 'macOS acceptance requires enforced source-checkout denial'
        profile = '(version 1)(allow default)(deny file-read* (subpath ' + json.dumps(str(ROOT.parent)) + '))'
        prefix = [sandbox, '-p', profile]
    # CI uses a fresh checkout without the source repository; macOS also denies
    # reads of the original workspace parent while running all installed checks.
    return outside, checkout, python, local_wheel, env, prefix


def test_installed_optional_refusals(installed):
    outside, checkout, python, _wheel, env, prefix = installed
    program = '''import importlib.util,sys
from pathlib import Path
from random import Random
import gnd
from gnd import api
from importlib.resources import files
from gnd.synth.values import make_value,SynthDependencyError
assert Path(gnd.__file__).resolve().is_relative_to(Path(sys.prefix).resolve())
assert importlib.util.find_spec('faker') is None
assert importlib.util.find_spec('pytest') is None
try: make_value('String',Random(0))
except SynthDependencyError as error: assert str(error)==SynthDependencyError.REMEDIATION
else: raise AssertionError('missing extra accepted')
for domain in ['dispatch','release']:
 root=files('gnd')/'examples'/domain
 for name,expected in [('seed.pop.json',1),('repaired.pop.json',0)]:
  result=api.check(root/'model.orm.json',root/name,admission=True)
  assert result['exit_code']==expected,result
print(gnd.__file__)
'''
    print(run([*prefix, python, '-I', '-c', program], checkout, env))
    run([*prefix, python, '-I', '-m', 'gnd', '--help'], checkout, env)
    if prefix:
        program = 'from pathlib import Path; Path(' + repr(str(ROOT / 'pyproject.toml')) + ').read_bytes()'
        result = subprocess.run([*prefix, python, '-I', '-c', program], cwd=outside,
                                env=env, capture_output=True, text=True, check=False)
        assert result.returncode != 0 and 'Operation not permitted' in result.stderr


def dev_environment(installed):
    outside, checkout, _, wheel, env, prefix = installed
    venv = outside / 'dev'
    if not venv.exists():
        run(['uv', 'venv', '--python', sys.executable, venv], outside, env)
        run(['uv', 'pip', 'install', '--python', venv / 'bin/python', str(wheel) + '[synth]',
             'pytest==9.1.1', 'duckdb==1.5.5'], outside, env)
    env = {**env, 'PATH': str(venv / 'bin') + os.pathsep + env.get('PATH', '')}
    return checkout, venv / 'bin/python', env, prefix


def installed_pytest(installed, modules):
    checkout, python, env, prefix = dev_environment(installed)
    program = '''import sys,pytest,gnd,importlib.metadata
from pathlib import Path
assert Path(gnd.__file__).resolve().is_relative_to(Path(sys.prefix).resolve())
assert Path(importlib.metadata.distribution('get-nick-done').locate_file('')).resolve().is_relative_to(Path(sys.prefix).resolve())
class Gate:
 def __init__(self): self.skips=[];self.passed=0
 def pytest_collectreport(self,report):
  if report.skipped:self.skips.append(report.nodeid)
 def pytest_runtest_logreport(self,report):
  if report.skipped:self.skips.append(report.nodeid)
  if report.when=='call' and report.passed:self.passed+=1
p=Gate()
code=pytest.main(['-q','--tb=short',*sys.argv[1:]],plugins=[p])
assert code==0 and p.passed>0 and not p.skips,(code,p.passed,p.skips)
'''
    print(run([*prefix, python, '-I', '-c', program,
               *['tests/' + n for n in modules]], checkout, env, timeout=1200))


def test_installed_behavior_families(installed):
    installed_pytest(installed, FAMILIES)


def test_target_only_contributor_lifecycle(installed):
    installed_pytest(installed, [
        'test_public_installer.py', 'test_contributor_preparation.py',
        'test_packaged_skills.py',
        'test_development_scaffold.py::test_twins_modes_and_generated_links',
        'test_development_scaffold.py::test_non_authoritative_spec_record_exercise',
        'test_review_credential_launcher.py',
    ])
