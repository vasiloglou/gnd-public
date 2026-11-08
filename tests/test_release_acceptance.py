"""Consume retained candidate artifacts; never rebuild them during acceptance."""
import email
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tomllib
import urllib.request
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
            assert sum(n.endswith('/SKILL.md') for n in names) == 18
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


# --- The candidate carries every item of issue 118 (rule-check-release RR2) ---
#
# Inputs are the shipped example gnd/examples/rule_check, copied out of the
# installed wheel. Expected values are copied from
# docs/reference/rule-check-report.md and docs/how-to/adopt-rules-with-a-baseline.md,
# which replays the same example; the RR2 spec (§6) cites each line.

# The wheel PyPI serves for the published 0.1.0, historical data like RELEASED in
# tests/test_release_version.py: the negative control installs exactly this file.
PUBLISHED_WHEEL_SHA256 = {'0.1.0': 'cc91decaf86d081fa023179792646900ac8f23c3cd1758e339006a4dab1ac183'}
DECLARED = tomllib.loads((ROOT / 'pyproject.toml').read_text(encoding='utf-8'))['project']['version']
MODEL, HEAD, BASE, FIXED = (f'catalog/{n}' for n in [
    'model.orm.yaml', 'head.population.yaml', 'base.population.yaml', 'fixed.population.yaml'])
REMEDIES = {
    'constraint:no_import_loops': 'Break the loop: move the shared code into a lower component both can import.',
    'constraint:every_component_has_an_owner': "Add the owning team to the component's catalog entry.",
    'constraint:no_legacy_components': 'Move the component out of the legacy area, or retire it.',
    'constraint:no_draft_releases': 'Ship the component in a numbered release, not a draft.',
}
LOOPS = 'constraint:no_import_loops'
LEGACY_ROW = {'$c': 'legacy_ui', '$a': 'legacy'}


def gnd(python, prefix, env, cwd, *args, expected):
    """Run `python -I -m gnd *args` under the sandbox prefix and assert its exit."""
    result = subprocess.run([*prefix, str(python), '-I', '-m', 'gnd', *map(str, args)], cwd=cwd,
                            env=env, capture_output=True, text=True, timeout=300, check=False)
    assert result.returncode == expected, (args, result.returncode, result.stderr[-4000:])
    return result


def gnd_json(python, prefix, env, cwd, *args, expected):
    """Run `gnd check *args --format json`, assert the exit and parse the report."""
    return json.loads(gnd(python, prefix, env, cwd, 'check', *args, '--format', 'json',
                          expected=expected).stdout)


def copy_example(python, prefix, env, work):
    """Copy gnd/examples/rule_check out of the installed wheel into work/catalog."""
    program = ('import shutil,sys; from importlib.resources import files; '
               "shutil.copytree(str(files('gnd') / 'examples' / 'rule_check'), sys.argv[1])")
    run([*prefix, python, '-I', '-c', program, work / 'catalog'], work, env)
    return work / 'catalog'


def edit(path, old, new, target=None):
    """Write path's text with exactly one `old` replaced, so a mutant never misses its target."""
    text = path.read_text(encoding='utf-8')
    assert text.count(old) == 1, (path, old)
    (target or path).write_text(text.replace(old, new), encoding='utf-8')


def by_address(report):
    return {verdict['address']: verdict for verdict in report['verdicts']}


def edges(rows):
    return sorted(tuple(row) for row in rows)


def acyclic_verdict(report):
    (verdict,) = [v for v in report['verdicts'] if "'component_imports_component' is acyclic" in v['message']]
    return verdict


@pytest.fixture(scope='module')
def published_0_1_0(tmp_path_factory):
    """The PyPI 0.1.0 wheel, hash-checked and installed in a fresh venv outside the checkout."""
    outside = tmp_path_factory.mktemp('published-0.1.0').resolve()
    env = {k: v for k, v in os.environ.items()
           if k in {'PATH', 'SYSTEMROOT', 'TMPDIR', 'LANG', 'LC_ALL'}}
    env.update(HOME=str(outside / 'home'), PYTHONNOUSERSITE='1')
    Path(env['HOME']).mkdir()
    with urllib.request.urlopen('https://pypi.org/pypi/get-nick-done/0.1.0/json', timeout=60) as response:
        (item,) = [u for u in json.load(response)['urls'] if u['packagetype'] == 'bdist_wheel']
    with urllib.request.urlopen(item['url'], timeout=60) as response:
        body = response.read()
    assert hashlib.sha256(body).hexdigest() == PUBLISHED_WHEEL_SHA256['0.1.0'], item['url']
    wheel = outside / item['filename']
    wheel.write_bytes(body)
    venv = outside / 'venv'
    run(['uv', 'venv', '--python', sys.executable, venv], outside, env)
    run(['uv', 'pip', 'install', '--python', venv / 'bin/python', wheel], outside, env)
    return venv / 'bin/python', env


def test_installed_rule_check_carries(candidate, installed, tmp_path):
    _outside, _checkout, python, wheel, env, prefix = installed
    copy_example(python, prefix, env, tmp_path)

    def check(*args, expected):
        return gnd_json(python, prefix, env, tmp_path, *args, expected=expected)

    # P1 --rule-ids: version 15, each rule's own address, addressing and remedy.
    head = check(MODEL, HEAD, '--rule-ids', expected=1)
    assert head['schema_version'] == 15
    assert head['baseline'] is None and head['allow_vacuous'] is False
    verdicts = by_address(head)
    assert set(verdicts) == set(REMEDIES)
    for address, remedy in REMEDIES.items():
        verdict = verdicts[address]
        assert (verdict['addressing'], verdict['remedy']) == ('declared-id', remedy), address
        assert verdict['novelty'] is None and verdict['row_novelty'] is None, address
    # P1 mutant: without an id and a remedy the rule is addressed by position.
    edit(tmp_path / MODEL, '      - id: no_import_loops\n        type: ring\n', '      - type: ring\n',
         tmp_path / 'catalog/positional.orm.yaml')
    edit(tmp_path / 'catalog/positional.orm.yaml', f'        remedy: "{REMEDIES[LOOPS]}"\n', '')
    positional = by_address(check('catalog/positional.orm.yaml', HEAD, '--rule-ids', expected=1))
    loop = positional['fact_types[component_imports_component].constraints[0]']
    assert (loop['addressing'], loop['remedy']) == ('positional', None)

    # P4 acyclic extent: every edge inside a strongly connected group.
    loops = verdicts[LOOPS]
    assert edges(loops['offending_facts']) == [('api', 'auth'), ('auth', 'api'), ('search', 'util'), ('util', 'search')]
    assert loops['message'].endswith('2 strongly connected groups (sizes 2, 2) hold 4 edges.')
    # Control: the same rule at version 7 lists one cycle, a closed walk.
    plain = check(MODEL, HEAD, expected=1)
    assert plain['schema_version'] == 7
    (cycle,) = acyclic_verdict(plain)['offending_facts']
    assert len(cycle) >= 3 and cycle[0] == cycle[-1] and set(cycle) <= {'api', 'auth', 'search', 'util'}
    # Control: without the separate search/util loop the api/auth rows keep their values.
    fixed = by_address(check(MODEL, FIXED, '--rule-ids', expected=1))[LOOPS]
    assert edges(fixed['offending_facts']) == [('api', 'auth'), ('auth', 'api')]
    assert fixed['message'].endswith('1 strongly connected group (size 2) holds 2 edges.')

    # P2 --baseline: new or standing per violation and per row.
    report = check(MODEL, HEAD, '--baseline', BASE, expected=1)
    assert report['baseline'] == {
        'population': BASE,
        'population_sha256': 'd816aea7caf713a67837f1361c4a2676a91a5aac82ba7167bf1ef88106fd5fcd',
        'new': 2, 'standing': 4, 'resolved': 2, 'positional_keyed': 0, 'undecided': 0}
    marked = by_address(report)
    assert {a: marked[a]['novelty'] for a in REMEDIES} == {
        LOOPS: 'new', 'constraint:no_legacy_components': 'standing',
        'constraint:every_component_has_an_owner': 'standing', 'constraint:no_draft_releases': None}
    rows = {a: sorted((json.dumps(r, sort_keys=True), m) for r, m in
                      zip(marked[a]['offending_facts'], marked[a]['row_novelty']))
            for a in REMEDIES if marked[a]['row_novelty']}
    assert rows == {
        LOOPS: sorted([(json.dumps(['api', 'auth']), 'standing'), (json.dumps(['auth', 'api']), 'standing'),
                       (json.dumps(['search', 'util']), 'new'), (json.dumps(['util', 'search']), 'new')]),
        'constraint:every_component_has_an_owner': [(json.dumps('metrics'), 'standing')],
        'constraint:no_legacy_components': [(json.dumps(LEGACY_ROW, sort_keys=True), 'standing')],
    }
    # Mutant: the head as its own base has nothing new; the vacuous rule leaves exit 2.
    itself = check(MODEL, HEAD, '--baseline', HEAD, expected=2)
    assert itself['baseline']['new'] == 0
    assert {v['novelty'] for v in itself['verdicts']} == {'standing', None}

    # P3 --allow-vacuous turns a 2 into 0, and nothing else.
    check(MODEL, FIXED, '--baseline', BASE, expected=2)
    accepted = check(MODEL, FIXED, '--baseline', BASE, '--allow-vacuous', expected=0)
    assert accepted['allow_vacuous'] is True and accepted['assurance']['assurance_level'] == 'none'
    check(MODEL, HEAD, '--baseline', BASE, '--allow-vacuous', expected=1)

    # P5 source: tool-output with a producer loads; a producer with another source is refused.
    assert check(MODEL, HEAD, expected=1)['issues'] == []
    edit(tmp_path / HEAD, 'source: tool-output', 'source: fixture', tmp_path / 'catalog/producer.population.yaml')
    assert check(MODEL, 'catalog/producer.population.yaml', expected=3)['issues']

    # The installed version and the artifact names are the declared version.
    assert gnd(python, prefix, env, tmp_path, '--version', expected=0).stdout.strip() == f'gnd {DECLARED}'
    with zipfile.ZipFile(wheel) as archive:
        assert {n.split('/')[0] for n in archive.namelist() if '.dist-info/' in n} == {
            f'get_nick_done-{DECLARED}.dist-info'}
        metadata = email.message_from_bytes(archive.read(f'get_nick_done-{DECLARED}.dist-info/METADATA'))
        assert metadata['Version'] == DECLARED
    with tarfile.open(next(candidate.glob('release/*.tar.gz'))) as archive:
        assert {n.split('/')[0] for n in archive.getnames()} == {f'get_nick_done-{DECLARED}'}


def test_published_0_1_0_lacks_rule_check(installed, published_0_1_0, tmp_path):
    _outside, _checkout, python, _wheel, env, prefix = installed
    old_python, old_env = published_0_1_0
    copy_example(python, prefix, env, tmp_path)

    def old(*args, expected):
        return gnd(old_python, prefix, old_env, tmp_path, 'check', *args, '--format', 'json', expected=expected)

    # The three flags are new: 0.1.0's parser refuses them (exit 64, not 2: RR2 spec §13).
    for flags in [['--rule-ids'], ['--baseline', BASE], ['--allow-vacuous']]:
        assert f'unrecognized arguments: {flags[0]}' in old(MODEL, HEAD, *flags, expected=64).stderr
    # `remedy` is new: 0.1.0's model schema refuses it.
    issues = json.loads(old(MODEL, HEAD, expected=3).stdout)['issues']
    assert any(i['path'] == '$.constraints[0]' and i['rule_id'] == 'jsonschema:unevaluatedProperties'
               and 'remedy' in i['message'] for i in issues), issues
    # `tool-output` and `producer` are new: on a model 0.1.0 accepts, the population is refused.
    model = tmp_path / MODEL
    text, removed = re.subn(r'(?m)^ *remedy: .*\n', '', model.read_text(encoding='utf-8'))
    assert removed == len(REMEDIES)
    (tmp_path / 'catalog/plain.orm.yaml').write_text(text, encoding='utf-8')
    issues = json.loads(old('catalog/plain.orm.yaml', HEAD, expected=3).stdout)['issues']
    assert any(i['path'] == '$.population' and 'producer' in i['message'] for i in issues), issues
    assert any(i['path'] == '$.population.source' and 'tool-output' in i['message'] for i in issues), issues
    # Without the new flags and fields nothing changed: both releases agree on input both accept.
    head, removed = re.subn(r'(?m)^  producer: .*\n', '', (tmp_path / HEAD).read_text(encoding='utf-8'))
    assert removed == 1 and head.count('source: tool-output') == 1
    fixture = 'catalog/fixture.population.yaml'
    (tmp_path / fixture).write_text(head.replace('source: tool-output', 'source: fixture'), encoding='utf-8')
    reports = [json.loads(old('catalog/plain.orm.yaml', fixture, expected=1).stdout),
               gnd_json(python, prefix, env, tmp_path, 'catalog/plain.orm.yaml', fixture, expected=1)]
    assert [r['schema_version'] for r in reports] == [7, 7]
    assert reports[0]['counts'] == reports[1]['counts']
    published, current = ([(v['constraint_ref'], v['verdict'], v['offending_facts']) for v in r['verdicts']] for r in reports)
    assert sorted(published, key=str) == sorted(current, key=str)
    (cycle,) = acyclic_verdict(reports[0])['offending_facts']
    assert acyclic_verdict(reports[1])['offending_facts'] == [cycle] and cycle[0] == cycle[-1]
