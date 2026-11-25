"""Consume retained candidate artifacts; never rebuild them during acceptance."""
import ast
import email
import hashlib
import itertools
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tarfile
import tomllib
import urllib.request
import zipfile
from pathlib import Path

import pytest
from support.markdown_sections import markdown_blocks
from support.recorded_version import move_version

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
    # release-0.5.0 RW2: growth from a reviewed vocabulary and the literature examples from a host.
    'test_vg3_unattended_includes.py', 'test_go2_operation_outcomes.py', 'test_lh1_reading_host.py',
    'test_lh2_reading_replay.py', 'test_lr3_reference_set.py',
]


def run(args, cwd, env, *, timeout=300, expected=0):
    result = subprocess.run([str(a) for a in args], cwd=cwd, env=env,
                            capture_output=True, text=True, timeout=timeout, check=False)
    assert result.returncode == expected, result.stdout[-12000:] + result.stderr[-12000:]
    return result.stdout


def candidate_source(root):
    source = (root / 'SOURCE_COMMIT').read_text(encoding='ascii').strip()
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    assert source == head, 'candidate SOURCE_COMMIT differs from the acceptance checkout HEAD'
    return head


def verify_files(root):
    candidate_source(root)
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
            from test_packaged_skills import EXPECTED_SKILL_FILES, EXPECTED_SKILL_NAMES
            skill_names = {n.removeprefix('gnd/skills/') for n in names
                           if n.startswith('gnd/skills/') and not n.endswith('/')}
            assert skill_names == EXPECTED_SKILL_FILES
            assert sum(n.endswith('/SKILL.md') for n in names) == len(EXPECTED_SKILL_NAMES)
            assert any(n.endswith('/LICENSE') for n in names)
            assert any(n.endswith('/NOTICE') for n in names)
            for domain in ['dispatch', 'release']:
                assert f'gnd/examples/{domain}/model.orm.json' in names
    with tarfile.open(next(candidate.glob('release/*.tar.gz'))) as archive:
        names = archive.getnames()
        assert len(names) == len(set(names))
        assert all(not Path(n).is_absolute() and '..' not in Path(n).parts for n in names)


@pytest.mark.parametrize('mutation', ['changed', 'missing', 'extra', 'wrong-source'])
def test_candidate_identity_negative_controls(candidate, tmp_path, mutation):
    copy = tmp_path / 'candidate'
    shutil.copytree(candidate, copy, ignore=shutil.ignore_patterns('source'))
    wheel = next(copy.glob('release/*.whl'))
    if mutation == 'changed':
        wheel.write_bytes(wheel.read_bytes() + b'changed')
    elif mutation == 'missing':
        wheel.unlink()
    elif mutation == 'extra':
        (copy / 'release' / 'extra.whl').write_bytes(b'extra')
    else:
        (copy / 'SOURCE_COMMIT').write_text('0' * 40 + '\n', encoding='ascii')
        with pytest.raises(AssertionError, match='candidate SOURCE_COMMIT differs'):
            verify_files(copy)
        return
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
    snapshot = subprocess.run(['git', 'archive', candidate_source(candidate)], cwd=ROOT,
                              capture_output=True, check=True)
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

# Only the latest published wheel provides release availability controls.
# The older release probes stay as positive regressions.
PUBLISHED_WHEEL_SHA256 = {'0.4.0': '36288e7a918b17d14ea307b6492acfbad741755e1e83818641836452cee9ea5c'}
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


def published_wheel(tmp_path_factory, version):
    """The PyPI wheel of `version`, hash-checked and installed in a fresh venv outside the checkout."""
    outside = tmp_path_factory.mktemp(f'published-{version}').resolve()
    env = {k: v for k, v in os.environ.items()
           if k in {'PATH', 'SYSTEMROOT', 'TMPDIR', 'LANG', 'LC_ALL'}}
    env.update(HOME=str(outside / 'home'), PYTHONNOUSERSITE='1')
    Path(env['HOME']).mkdir()
    with urllib.request.urlopen(f'https://pypi.org/pypi/get-nick-done/{version}/json', timeout=60) as response:
        (item,) = [u for u in json.load(response)['urls'] if u['packagetype'] == 'bdist_wheel']
    with urllib.request.urlopen(item['url'], timeout=60) as response:
        body = response.read()
    assert hashlib.sha256(body).hexdigest() == PUBLISHED_WHEEL_SHA256[version], item['url']
    wheel = outside / item['filename']
    wheel.write_bytes(body)
    venv = outside / 'venv'
    run(['uv', 'venv', '--python', sys.executable, venv], outside, env)
    run(['uv', 'pip', 'install', '--python', venv / 'bin/python', wheel], outside, env)
    return venv / 'bin/python', env


def declared_version(checkout):
    """The version pyproject.toml declares at the archived HEAD the fixture extracted."""
    return tomllib.loads((checkout / 'pyproject.toml').read_text(encoding='utf-8'))['project']['version']


def test_installed_rule_check_carries(candidate, installed, tmp_path):
    _outside, checkout, python, wheel, env, prefix = installed
    declared = declared_version(checkout)
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
    assert len(cycle) >= 3 and cycle[0] == cycle[-1]
    # every step of the cycle is an edge of the version-15 extent above
    assert set(itertools.pairwise(cycle)) <= set(edges(loops['offending_facts'])), cycle
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
    for address in REMEDIES:
        if marked[address]['row_novelty'] is not None:  # one mark per offending row
            assert len(marked[address]['row_novelty']) == len(marked[address]['offending_facts']), address
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
    # Control: the same source without the producer loads, so the producer is what was refused.
    edit(tmp_path / 'catalog/producer.population.yaml', '  producer: "components-scan 1.4.0 @ 9b72c55"\n', '',
         tmp_path / 'catalog/no-producer.population.yaml')
    assert check(MODEL, 'catalog/no-producer.population.yaml', expected=1)['issues'] == []

    # The installed version and the artifact names are the declared version.
    assert gnd(python, prefix, env, tmp_path, '--version', expected=0).stdout.strip() == f'gnd {declared}'
    with zipfile.ZipFile(wheel) as archive:
        assert {n.split('/')[0] for n in archive.namelist() if '.dist-info/' in n} == {
            f'get_nick_done-{declared}.dist-info'}
        metadata = email.message_from_bytes(archive.read(f'get_nick_done-{declared}.dist-info/METADATA'))
        assert metadata['Version'] == declared
    with tarfile.open(next(candidate.glob('release/*.tar.gz'))) as archive:
        assert {n.split('/')[0] for n in archive.getnames()} == {f'get_nick_done-{declared}'}


# -- release-0.3.0 RN2: what 0.3.0 adds, from the installed wheel (probes Q1 to Q5) --

ACCEPTANCE_INPUTS = 'tests/fixtures/release-acceptance/0.3.0'
OSSIE_FILES = ['gnd/schema/ossie/PINNED.json', 'gnd/schema/ossie/core-spec.json',
               'gnd/schema/ossie/ontology.json', 'gnd/ossie-loss-report.schema.json']
Q4_PREVIEW = ['evolve', 'preview', 'model.orm.yaml', 'proposal.json', '--workspace', '.',
              '--records', 'records', '--format', 'json', '--policy', 'additive',
              '--populated', 'customer_places_order']
OSSIE_ONTOLOGY_OUTPUTS = ['', '.gnd.json', '.loss.json']
OSSIE_OUTPUTS = [*OSSIE_ONTOLOGY_OUTPUTS, '.mapping.yaml', '.semantic_model.yaml']   # sorted, as iterdir is compared
SPANS_UNCHECKED = '1 of 10 source spans were not re-hashed'
YAML_TO_JSON = ('import json,sys; from ruamel.yaml import YAML; '
                "print(json.dumps(YAML(typ='safe').load(open(sys.argv[1], encoding='utf-8'))))")


def copy_packaged(python, prefix, env, work, relative, name):
    """Copy one file or directory of the installed gnd package into work/name."""
    program = ('import shutil,sys; from importlib.resources import files; '
               "source = files('gnd').joinpath(*sys.argv[1].split('/')); "
               '(shutil.copytree if source.is_dir() else shutil.copyfile)(str(source), sys.argv[2])')
    run([*prefix, python, '-I', '-c', program, relative, work / name], work, env)
    return work / name


def acceptance_inputs(python, prefix, env, checkout, work):
    """The probe inputs: packaged examples from the wheel, corpus copies from the tracked checkout."""
    work.mkdir(parents=True, exist_ok=True)
    (work / 'q1').mkdir()
    copy_packaged(python, prefix, env, work, 'examples/refunds/model.orm.yaml', 'q1/model.orm.yaml')
    copy_packaged(python, prefix, env, work, 'examples/expense/teams', 'q3')
    for name in ('q4', 'q5'):
        shutil.copytree(checkout / ACCEPTANCE_INPUTS / name, work / name)
    (work / 'q4/records').mkdir()
    return work


def identity(result):
    """The digest `gnd validate --identity` printed, checked against the document it printed."""
    first, second = result.stdout.splitlines()
    match = re.fullmatch(r'MODEL IDENTITY (sha256:[0-9a-f]{64}) \(identity_version 2\)', first)
    assert match, first
    assert match.group(1) == 'sha256:' + hashlib.sha256((second + '\n').encode('utf-8')).hexdigest()
    return match.group(1)


def test_installed_0_3_0_regressions(installed, tmp_path):
    _outside, checkout, python, wheel, env, prefix = installed
    version = declared_version(checkout)
    # The installed package is the declared version, before any probe input is touched.
    assert gnd(python, prefix, env, tmp_path, '--version', expected=0).stdout.strip() == f'gnd {version}'
    work = acceptance_inputs(python, prefix, env, checkout, tmp_path / 'work')

    def new(cwd, *args, expected):
        return gnd(python, prefix, env, work / cwd, *args, expected=expected)

    # The Ossie schemas are package data; a wheel without them breaks only when installed.
    with zipfile.ZipFile(wheel) as archive:
        names = set(archive.namelist())
    assert set(OSSIE_FILES) <= names, sorted(set(OSSIE_FILES) - names)

    # Q1: an Ossie export writes its files (five since 0.5.0; probe P5 holds the three-file run), and an
    # import with its sidecar restores the model.
    q1 = work / 'q1'
    new('q1', 'export', 'ossie', 'model.orm.yaml', '--out', 'o.yaml', expected=0)
    assert sorted(p.name for p in q1.iterdir()) == ['model.orm.yaml', *('o.yaml' + suffix for suffix in OSSIE_OUTPUTS)]
    # The exported YAML itself, read by the YAML library the wheel depends on (review G2).
    concepts = json.loads(run([*prefix, python, '-I', '-c', YAML_TO_JSON, 'o.yaml'], q1, env))['ontology']
    (refund_by,) = [r for c in concepts for r in c.get('relationships', ()) if r['name'] == 'refund_by']
    assert refund_by['multiplicity'] == 'ManyToOne'
    # The two companion files carry the schema names the format reference gives them (review G7).
    assert json.loads((q1 / 'o.yaml.gnd.json').read_text(encoding='utf-8'))['schema'] == 'gnd-ossie-sidecar/1'
    assert json.loads((q1 / 'o.yaml.loss.json').read_text(encoding='utf-8'))['schema'] == 'gnd-ossie-loss/1'
    new('q1', 'import', 'ossie', 'o.yaml', '--out', 'restored.orm.json', expected=0)
    report = json.loads((q1 / 'restored.orm.json.loss.json').read_text(encoding='utf-8'))
    assert report['source_identity_verified'] is True
    # Q1 control: the sidecar binds the ontology's bytes, so a changed ontology is refused and nothing is written.
    edit(q1 / 'o.yaml', 'name: refund_by', 'name: refund_bx', q1 / 'changed.yaml')
    for suffix in ('.gnd.json', '.loss.json'):
        shutil.copyfile(q1 / ('o.yaml' + suffix), q1 / ('changed.yaml' + suffix))
    refused = new('q1', 'import', 'ossie', 'changed.yaml', '--out', 'changed.orm.json', expected=3)
    assert 'ossie-import:' in refused.stderr   # the reference names the form, not each rule (review G7)
    assert not (q1 / 'changed.orm.json').exists() and not (q1 / 'changed.orm.json.loss.json').exists()

    # Q2: the identity is the sha256 of the document printed with it, and it is the one the import reported.
    refunds = identity(new('q1', 'validate', 'model.orm.yaml', '--identity', expected=0))
    assert report['source_model_identity'] == refunds
    # The restored file is a model with the source's identity, measured here and not taken
    # from the import's own report (review G3).
    assert identity(new('q1', 'validate', 'restored.orm.json', '--identity', expected=0)) == refunds
    # Q2 controls: a renamed object type and a changed rule each move the identity (review G4).
    edit(q1 / 'model.orm.yaml', 'name: Refund\n', 'name: RefundX\n', q1 / 'renamed.orm.yaml')
    edit(q1 / 'model.orm.yaml', 'right: 1000 }', 'right: 5 }', q1 / 'limit.orm.yaml')
    moved = {identity(new('q1', 'validate', name, '--identity', expected=0))
             for name in ('renamed.orm.yaml', 'limit.orm.yaml')}
    assert len(moved) == 2 and refunds not in moved

    # Q3: a version 5 model with a pinned include validates; a wrong pin is refused.
    assert 'OK: sales.orm.json is a valid GND ORM model' in new('q3', 'validate', 'sales.orm.json', expected=0).stdout
    sales = json.loads((work / 'q3/sales.orm.json').read_text(encoding='utf-8'))
    assert sales['version'] == 5 and len(sales['includes']) == 1
    edit(work / 'q3/sales.orm.json', sales['includes'][0]['sha256'], '0' * 64, work / 'q3/badpin.orm.json')
    wrong = json.loads(new('q3', 'validate', 'badpin.orm.json', '--format', 'json', expected=3).stdout)
    assert [(i['path'], i['rule_id']) for i in wrong['issues']] == [('$.includes[0]', 'include:hash-mismatch')]

    # Q4: under the additive policy a new rule on a populated fact type is refused, admitted
    # on a population that satisfies it, and refused on one that violates it (UG2 cases C01, C03).
    def preview(name, *extra, expected):
        new('q4', *Q4_PREVIEW, '--out', name, *extra, expected=expected)
        return json.loads((work / 'q4' / name).read_text(encoding='utf-8'))

    plain = preview('plain.json', expected=3)
    assert [(i['operation_index'], i['cell']) for i in plain['policy_issues']] == [(0, 'constraint.populated.add')]
    clean = preview('clean.json', '--check-population', 'populations/clean.json', expected=0)
    assert clean['policy_issues'] == []
    assert [row['operation_index'] for row in clean['population_check']['admitted']] == [0]
    violating = preview('violating.json', '--check-population', 'populations/violating.json', expected=3)
    assert [(i['operation_index'], i['cell']) for i in violating['policy_issues']] == [(0, 'constraint.populated.add')]
    assert violating['population_check']['admitted'] == []

    # Q5: an unchecked source span is a warning, and an error under --require-documents (UG3 cases A2a, A3, A4).
    def spans(*extra, expected):
        return json.loads(new('q5', 'validate', 'model.orm.yaml', '--document', 'ledger.txt', *extra,
                              '--format', 'json', expected=expected).stdout)

    warned = spans(expected=0)
    assert [(w['rule_id'], w['severity']) for w in warned['warnings']] == [('unattended:spans-unchecked', 'warning')]
    assert SPANS_UNCHECKED in warned['warnings'][0]['message'] and warned['issues'] == []
    required = spans('--require-documents', expected=3)
    assert [(i['rule_id'], i['path']) for i in required['issues']] == [('unattended:spans-unchecked', '$.source.documents')]
    assert SPANS_UNCHECKED in required['issues'][0]['message']
    covered = spans('--document', 'annex.txt', '--require-documents', expected=0)
    assert covered['issues'] == [] and covered['warnings'] == []


@pytest.fixture(scope='module')
def rv2_installed(installed):
    """The candidate, required to be 0.5.0 before any 0.4.0 or 0.5.0 probe touches its inputs."""
    outside, checkout, python, _wheel, env, prefix = installed
    assert declared_version(checkout) == '0.5.0'
    assert gnd(python, prefix, env, outside, '--version', expected=0).stdout.strip() == 'gnd 0.5.0'
    return installed


def test_installed_rv2_guarded_membership(rv2_installed, tmp_path):
    _, checkout, python, _, env, prefix = rv2_installed
    model = json.loads(run([*prefix, python, '-I', '-c', YAML_TO_JSON,
                            checkout / 'tests/fixtures/models/guarded_minimal.orm.yaml'], tmp_path, env))
    guard = model['constraints'][0]
    model['constraints'] = [guard]
    guard['where'] = [{'operator': '>=', 'left': '$a', 'right': 100}]
    guard['consequent'] = {'comparison': {'operator': 'in', 'left': '$a', 'right': [150, 200]}}
    model_path = tmp_path / 'guard.json'
    model_path.write_text(json.dumps(model), encoding='utf-8')
    gnd(python, prefix, env, tmp_path, 'validate', model_path, expected=0)

    facts = {'expense_in_category': [{'expense': 1, 'category': 'travel'}],
             'expense_has_amount': [{'expense': 1, 'amount': 150}]}
    population = {'population': {'model': model_path.name, 'model_id': model['model_id'],
                                 'source': 'fixture', 'covers': list(facts)},
                  'instances': {}, 'facts': facts}
    population_path = tmp_path / 'population.json'
    for amount, code, verdict, bindings in [(150, 0, 'pass', 1), (250, 1, 'fail', 1), (50, 2, 'vacuous', 0)]:
        facts['expense_has_amount'][0]['amount'] = amount
        population_path.write_text(json.dumps(population), encoding='utf-8')
        report = gnd_json(python, prefix, env, tmp_path, model_path, population_path,
                          '--guarded-diagnostics', expected=code)
        result, = [row for row in report['verdicts'] if row['constraint_type'] == 'guarded']
        assert (result['verdict'], result['guarded_antecedent']['binding_count']) == (verdict, bindings)


def test_installed_rv2_composition_and_catalog(rv2_installed, tmp_path):
    _, _, python, _, env, prefix = rv2_installed
    work = tmp_path.resolve() / 'interop'
    run([*prefix, python, '-I', '-m', 'gnd.examples.literature.interop', 'run', '--out', work], tmp_path, env)
    model, population, record = 'checking.orm.json', 'composed.population.json', 'composition.json'
    authored = json.loads((work / model).read_bytes())
    assert [item['id'] for item in authored['includes']] == ['literature', 'chronology']
    manifest_path = work / 'sources/manifest.json'
    manifest = json.loads(manifest_path.read_bytes())
    resolution_path = work / 'sources/resolution.json'
    raw_resolution = resolution_path.read_bytes()
    assert manifest['resolution'] == {'path': resolution_path.name,
                                      'sha256': hashlib.sha256(raw_resolution).hexdigest()}
    resolution = json.loads(raw_resolution)
    decision, = resolution['decisions']
    assert decision['decision'] == 'same'
    composition = json.loads((work / record).read_bytes())
    assert composition['schema'] == 'gnd-composition/2'
    decided = [row for row in composition['facts'] if row['fact_type'] == 'paper_names_parent_method']
    assert decided and all(row['decisions'] == [0] for row in decided)
    checked = gnd_json(python, prefix, env, work, model, population, '--composition', record,
                       '--sources', 'sources', expected=0)
    assert checked['exit_code'] == 0

    alias = copy_packaged(python, prefix, env, tmp_path, 'examples/literature/resolution', 'resolution')
    alias_args = ('compose', alias / 'model.orm.yaml', alias / 'cases/A-alias',
                  '--out', 'alias.population.json', '--record', 'alias.composition.json')
    gnd(python, prefix, env, tmp_path, *alias_args, expected=0)

    witness = ('witness', model, population, '--targets', 'targets.json', '--composition', record, '--raw')
    replay = ('replay', model, population, 'rv2.witness.json', '--composition', record, '--raw')
    gnd(python, prefix, env, work, *witness, '--out', 'rv2.witness.json', expected=0)
    proof = json.loads((work / 'rv2.witness.json').read_bytes())
    assert any(node.get('origin', {}).get('reference_id') == 'method-catalog' for node in proof['nodes'])
    assert json.loads(gnd(python, prefix, env, work, *replay, expected=0).stdout)['exit_code'] == 0

    catalog = work / 'reference/catalog.json'
    original_catalog = catalog.read_bytes()
    catalog.write_bytes(original_catalog + b' ')
    typed_refusal = '''from pathlib import Path
from gnd.errors import ReferenceHashMismatch
from gnd.model import bind_references, load_model
root = Path.cwd()
try:
    bind_references(load_model(root / "checking.orm.json"), root=root)
except ReferenceHashMismatch:
    pass
else:
    raise AssertionError("changed catalog bytes were accepted")
'''
    run([*prefix, python, '-I', '-c', typed_refusal], work, env)
    for command in (witness, replay):
        assert json.loads(gnd(python, prefix, env, work, *command, expected=3).stdout)['reason'] == 'binding-stale'
    catalog.write_bytes(original_catalog)

    decision['decision'] = 'different'
    changed = json.dumps(resolution).encode('utf-8')
    resolution_path.write_bytes(changed)
    manifest['resolution']['sha256'] = hashlib.sha256(changed).hexdigest()
    manifest_path.write_text(json.dumps(manifest), encoding='utf-8')
    result = gnd(python, prefix, env, work, 'compose', model, 'sources',
                 '--out', 'mutant.population.json', '--record', 'mutant.composition.json', expected=3)
    assert 'decision 0 (different) keys end joined' in result.stderr
    assert not list(work.glob('mutant.*.json'))


def test_installed_rv2_literature_assurance(rv2_installed, tmp_path):
    _, checkout, python, _, env, prefix = rv2_installed
    literature = copy_packaged(python, prefix, env, tmp_path, 'examples/literature', 'literature')
    reference = literature / 'runs/reference'
    command = ('-I', '-m', 'gnd.examples.literature.assurance_report', literature,
               literature / 'answers/answer-key.json', reference)
    result = run([*prefix, python, *command], tmp_path, env).encode('utf-8')
    tracked = checkout / 'src/gnd/examples/literature'
    expected = json.loads((tracked / 'expected/reference.report.json').read_bytes())
    actual_inputs = json.loads(result)['inputs']
    version = declared_version(checkout)
    assert actual_inputs['gnd_version'] == version
    assert actual_inputs['harness_sha256'] == hashlib.sha256((tracked / 'assurance_report.py').read_bytes()).hexdigest()
    expected['inputs']['harness_sha256'] = actual_inputs['harness_sha256']
    assert json.loads(move_version(result, version, expected['inputs']['gnd_version'])) == expected

    population = reference / 'composed/population.json'
    mutant = json.loads(population.read_bytes())
    assert mutant['facts']
    mutant['facts'] = {}
    population.write_text(json.dumps(mutant), encoding='utf-8')
    changed = json.loads(run([*prefix, python, *command], tmp_path, env, expected=1))
    assert changed['failed_stages'] == ['identity-decisions', 'derivation', 'freshness']


def test_installed_rv2_expense_receipts(rv2_installed, tmp_path):
    _, _, python, _, env, prefix = rv2_installed
    work = copy_packaged(python, prefix, env, tmp_path, 'examples/expense/receipts', 'receipts')
    model, population, record = 'checking.orm.json', 'claim.population.json', 'claim.composition.json'
    gnd(python, prefix, env, work, 'compose', model, 'claim', '--out', population, '--record', record, expected=0)
    checked = gnd_json(python, prefix, env, work, model, population, '--composition', record,
                       '--sources', 'claim', expected=1)
    failures = {row['constraint_ref']: row['offending_facts']
                for row in checked['report']['verdicts'] if row['verdict'] == 'fail'}
    assert failures == {
        'constraints[0]': [['Café Central, Vienna'], ['TAXI G7 (unresolved)']],
        'constraints[1]': [['Café Central, Vienna'], ['Spa Lumière'], ['TAXI G7 (unresolved)']],
        'constraints[3]': [{'$e': 'C4', '$t': 'T-114', '$d': '2026-03-09', '$b': '2026-03-06'}],
    }
    missing = gnd(python, prefix, env, work, 'compose', model, 'claim-missing',
                  '--out', 'missing.population.json', '--record', 'missing.composition.json', expected=3)
    assert 'joined without a same decision' in missing.stderr
    assert not list(work.glob('missing.*.json'))


# -- release-0.5.0 RW2: what 0.5.0 adds, from the installed wheel (probes P1 to P6) --
#
# Each probe has a control on the candidate and one on the published 0.4.0 wheel. The expected 0.4.0
# results are the ones measured for the RW2 spec (release-0.5.0 evidence/RW2/controls-0.4.0.md).

INCLUDES = ['literature', 'chronology']
JUDGE = ('judgments', 'check', 'checking.orm.json', 'composed.population.json', '--policy', 'policy.json',
         '--receipts', 'receipts.json', '--trusted-root', '.', '--format', 'json')
# The judgment inputs bind digests of files the interop run writes, so the installed package writes them.
BIND_JUDGMENT = '''import hashlib, json, sys
from pathlib import Path
from gnd.artifacts import canonical_json_bytes
from gnd.judgments import judgment_fact_digest
root = Path.cwd()
model, population, target = sys.argv[1:4]
sha = lambda raw: hashlib.sha256(raw).hexdigest()
document = json.loads((root / model).read_bytes())
raw = (root / population).read_bytes()
fact = json.loads(raw)["facts"][target][0]
(root / "evidence.txt").write_bytes(b"evidence")
identity = {"identity_version": 1, "references": [
    {"id": r["id"], "sha256": r["sha256"]} for r in document["reference_populations"]]}
receipts = [{
    "receipt_id": "r-" + judge, "judge_id": judge, "verdict": "approve", "trust": "consumer-pinned",
    "subject": {"model_sha256": sha((root / model).read_bytes()), "population_sha256": sha(raw),
                "reference_identity": identity, "fact_type": target, "index": 0,
                "fact_sha256": judgment_fact_digest(target, 0, fact)},
    "sources": [{"path": "evidence.txt", "sha256": sha(b"evidence"), "quote": None}],
    "external_evidence": None} for judge in ("a", "b")]
policy = {
    "admission": {"evidence_floor": None, "minimum_approvals": 2}, "judges": ["a", "b"], "policy_id": "rw2",
    "repair": {"evidence_floor": None, "minimum_rejections": 1}, "schema_version": 1,
    "targets": [{"fact_type": target, "index": 0}], "trust_mode": "consumer-pinned",
    "trusted_receipts": [{"judge_id": r["judge_id"],
                          "receipt_sha256": sha(canonical_json_bytes(r, exact_numbers=True))} for r in receipts]}
(root / "policy.json").write_bytes(canonical_json_bytes(policy))
(root / "receipts.json").write_bytes(canonical_json_bytes({"schema_version": 1, "receipts": receipts}))
'''
RMAP_TABLES = ('import json, sys; from pathlib import Path; from gnd import rmap; from gnd.model import load_model; '
               'print(json.dumps(sorted(t.name for t in rmap.map_model(load_model(Path(sys.argv[1]))).tables)))')
PACKAGE_HAS_DIRECTORY = ("import sys; from importlib.resources import files; "
                         "print(files('gnd').joinpath(*sys.argv[1].split('/')).is_dir())")


@pytest.fixture(scope='module')
def published_0_4_0(tmp_path_factory):
    python, env = published_wheel(tmp_path_factory, '0.4.0')
    assert gnd(python, [], env, python.parent, '--version', expected=0).stdout.strip() == 'gnd 0.4.0'
    return python, env


def sha256_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def program_constants(path, *names):
    """The named module-level constants of an exported PyRel program, read with ast; the program never runs.

    The export writes a constant either as a literal or as json.loads of one string literal.
    """
    found = {}
    for node in ast.parse(path.read_text(encoding='utf-8')).body:
        if not (isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name)):
            continue
        name = node.targets[0].id
        if name in names:
            assert name not in found, name
            value = node.value
            found[name] = (json.loads(ast.literal_eval(value.args[0])) if isinstance(value, ast.Call)
                           else ast.literal_eval(value))
    assert set(found) == set(names), sorted(set(names) - set(found))
    return found


def rules_mode(mode):
    return () if mode is None else ('--rules', mode)


def test_installed_rw2_include_roots(rv2_installed, published_0_4_0, tmp_path):
    _, _, python, _, env, prefix = rv2_installed
    old_python, old_env = published_0_4_0
    work = tmp_path.resolve() / 'interop'
    run([*prefix, python, '-I', '-m', 'gnd.examples.literature.interop', 'run', '--out', work], tmp_path, env)

    def new(*args, expected):
        return gnd(python, prefix, env, work, *args, expected=expected)

    def old(*args, expected):
        return gnd(old_python, prefix, old_env, work, *args, expected=expected)

    # P1: gnd judgments check judges the temporal include root; 0.4.0 refuses the route.
    run([*prefix, python, '-I', '-c', BIND_JUDGMENT, 'checking.orm.json', 'composed.population.json',
         'paper_names_parent_method'], work, env)
    judged = json.loads(new(*JUDGE, expected=0).stdout)
    assert (judged['outcome'], judged['error'], judged['judgment_policy']['admission']) == (0, None, True)
    assert json.loads(old(*JUDGE, expected=3).stdout)['error']['reason'] == 'include:unsupported-route'

    # P2: gnd flatten writes the flat model and its record for both roots, and never overwrites.
    flat = work / 'flat'
    records = {}
    for root in ('checking', 'extraction'):
        new('flatten', f'{root}.orm.json', '--out', 'flat', expected=0)
        record_path = flat / f'{root}.orm.flattening.json'
        record = json.loads(record_path.read_bytes())
        assert record['format'] == 'gnd-flattening/1'
        assert [entry['id'] for entry in record['includes']] == INCLUDES
        assert record['flat_model_sha256'] == sha256_file(flat / f'{root}.orm.flat.orm.json')
        records[root] = sha256_file(record_path)
    written = {path.name: path.read_bytes() for path in flat.iterdir()}
    assert sorted(written) == [f'{root}.orm.{kind}.json' for root in ('checking', 'extraction')
                               for kind in ('flat.orm', 'flattening')]
    new('flatten', 'checking.orm.json', '--out', 'flat', expected=11)
    assert {path.name: path.read_bytes() for path in flat.iterdir()} == written
    old('flatten', 'checking.orm.json', '--out', 'flat-old', expected=64)   # 0.4.0 has no such command
    assert not (work / 'flat-old').exists()

    # P3, include roots: every advertised mode exports through the flat model and records its digest.
    modes = {'checking': ('duckdb', 'lqp'), 'extraction': (None, 'duckdb', 'lqp')}
    for root, selected in modes.items():
        for mode in selected:
            program = work / f'{root}-{mode or "default"}.py'
            new('export', 'pyrel', f'{root}.orm.json', *rules_mode(mode), '--out', program, expected=0)
            constants = program_constants(program, 'FLATTENING_RECORD_SHA256', 'MODEL_INCLUDES')
            assert constants['FLATTENING_RECORD_SHA256'] == records[root], (root, mode)
            assert [entry[0] for entry in constants['MODEL_INCLUDES']] == INCLUDES
    # The default mode still refuses a temporal model, as the notes say.
    temporal = new('export', 'pyrel', 'checking.orm.json', '--out', 'temporal.py', expected=3)
    assert 'PyRel export does not support temporal models' in temporal.stderr
    for root in modes:
        for mode in (None, 'duckdb', 'lqp'):
            refused = old('export', 'pyrel', f'{root}.orm.json', *rules_mode(mode), '--out', 'old.py', expected=3)
            assert 'include:unsupported-route' in refused.stderr, (root, mode)
    assert not (work / 'temporal.py').exists() and not (work / 'old.py').exists()

    # P1 control, last because it changes an include: an include edited without a new pin is refused.
    include = work / 'vocabulary/chronology.orm.json'
    document = json.loads(include.read_bytes())
    document['object_types'].append({'id': 'extra_0', 'kind': 'value', 'name': 'Extra0', 'primitive': 'String'})
    include.write_text(json.dumps(document), encoding='utf-8')
    assert json.loads(new(*JUDGE, expected=3).stdout)['error'] == {
        'message': 'include:hash-mismatch', 'reason': 'binding'}


def test_installed_rw2_pyrel_rules(rv2_installed, published_0_4_0, tmp_path):
    _, checkout, python, _, env, prefix = rv2_installed
    old_python, old_env = published_0_4_0
    literature = copy_packaged(python, prefix, env, tmp_path, 'examples/literature', 'literature')
    fixtures = checkout / 'tests/fixtures'
    # Each model, with the refusal 0.4.0 gives it by name.
    cases = {
        'external': (literature / 'assertions/model.orm.yaml',
                     'external uniqueness is a later phase of the rules programs'),
        'anchored': (literature / 'model.orm.yaml', "family 'anchored' is a later phase of the rules programs"),
        'number': (literature / 'depth_fixture/decimal.orm.json',
                   "primitive 'Number' is not supported by the rules programs yet"),
        # The packaged role-scoped model also has an anchored rule, which 0.4.0 refuses first.
        'role-anchored': (literature / 'quantity_fixture/time.orm.yaml',
                          "family 'anchored' is a later phase of the rules programs"),
        'role': (fixtures / 'pyrel-rules-coverage/rp4/range.orm.json',
                 'role-scoped value constraints are a later phase'),
    }
    frequency = fixtures / 'pyrel-rules-families/review/refuse-external-frequency.orm.json'
    for mode in ('duckdb', 'lqp'):
        constants = {}
        for label, (model, refusal) in cases.items():
            program = tmp_path / f'{label}-{mode}.py'
            gnd(python, prefix, env, tmp_path, 'export', 'pyrel', model, '--rules', mode, '--out', program, expected=0)
            constants[label] = program_constants(program, 'RULES', 'UNCHECKED')
            refused = gnd(old_python, prefix, old_env, tmp_path, 'export', 'pyrel', model, '--rules', mode,
                          '--out', 'old.py', expected=3)
            assert refusal in refused.stderr, (label, mode)
        # What each program holds: the external-uniqueness requirement over its two roles, the anchored
        # rule listed as not checked, and the value rule of one role.
        external = [rule for rule in constants['external']['RULES'] if rule['info'].get('external')]
        assert external and all(rule['info']['refs'] == [['assertion_names_passage', 'passage'],
                                                         ['assertion_names_work', 'work']] for rule in external)
        unchecked = {rule['id']: rule['reason'] for rule in constants['anchored']['UNCHECKED']}
        assert unchecked['work_introduces_method#0'].startswith('source anchor:')
        assert ('time_step#1', 'value') in {(rule['id'], rule['family'])
                                            for rule in constants['role-anchored']['RULES']}
        assert any(rule['family'] == 'value' for rule in constants['role']['RULES'])
        # Control: an external frequency rule is still refused by name.
        still = gnd(python, prefix, env, tmp_path, 'export', 'pyrel', frequency, '--rules', mode,
                    '--out', 'frequency.py', expected=3)
        assert 'external frequency is a later phase of the rules programs' in still.stderr
    assert not (tmp_path / 'old.py').exists() and not (tmp_path / 'frequency.py').exists()


COUNT_COMMANDS = [
    ('check', 'model.orm.yaml', 'population.json'),
    ('witness-count', 'model.orm.yaml', 'population.json', '--request', 'group.json', '--raw', '--out', 'flow.cert.json'),
    ('replay-count', 'model.orm.yaml', 'population.json', 'flow.cert.json', '--request', 'group.json', '--raw'),
    ('witness-count', 'model.orm.yaml', 'population.json', '--request', 'empty-group.json', '--raw',
     '--out', 'empty.cert.json'),
    ('replay-count', 'model.orm.yaml', 'population.json', 'empty.cert.json', '--request', 'empty-group.json', '--raw'),
]


def readme_commands(folder, commands):
    """COMMANDS, after checking that each is a command line of a shell block in the packaged README.

    The README is read as Markdown blocks and each line of a `sh` or `bash` fence as a shell command, so
    a command that is commented out, given another executable or moved out of its block does not count.
    """
    blocks = markdown_blocks((folder / 'README.md').read_text(encoding='utf-8'))
    documented = [shlex.split(line, comments=True) for block in blocks
                  if block.kind == 'fence' and block.info.split()[:1] in (['sh'], ['bash'])
                  for line in block.text.splitlines()]
    for command in commands:
        assert ['gnd', *command] in documented, command
    return commands


def test_installed_rw2_count_certificates(rv2_installed, published_0_4_0, tmp_path):
    _, _, python, _, env, prefix = rv2_installed
    old_python, old_env = published_0_4_0
    work = copy_packaged(python, prefix, env, tmp_path, 'examples/literature/count_fixture', 'count')
    # P4: the README's commands, each exit 0; the certificates replay with their counts.
    replays = []
    for command in readme_commands(work, COUNT_COMMANDS):
        result = gnd(python, prefix, env, work, *command, expected=0)
        if command[0] == 'replay-count':
            replays.append(json.loads(result.stdout))
    assert [(row['count'], row['status']) for row in replays] == [(2, 'complete'), (0, 'empty-group')]
    assert json.loads((work / 'empty.cert.json').read_bytes())['members'] == []
    # Control: the population without the first roster member's row no longer replays.
    flow = json.loads((work / 'flow.cert.json').read_bytes())
    population = json.loads((work / 'population.json').read_bytes())
    del population['facts']['observation'][flow['members'][0]['fact_index']]
    (work / 'lost.population.json').write_text(json.dumps(population), encoding='utf-8')
    lost = gnd(python, prefix, env, work, 'replay-count', 'model.orm.yaml', 'lost.population.json', 'flow.cert.json',
               '--request', 'group.json', '--raw', expected=3)
    assert json.loads(lost.stdout)['reason'] == 'binding-stale'
    # 0.4.0 has neither the command nor the example.
    gnd(old_python, prefix, old_env, work, *COUNT_COMMANDS[1][:-1], 'old.cert.json', expected=64)
    assert not (work / 'old.cert.json').exists()
    assert run([*prefix, old_python, '-I', '-c', PACKAGE_HAS_DIRECTORY, 'examples/literature/count_fixture'],
               tmp_path, old_env).strip() == 'False'


def test_installed_rw2_ossie_relational(rv2_installed, published_0_4_0, tmp_path):
    _, _, python, _, env, prefix = rv2_installed
    old_python, old_env = published_0_4_0
    work, old_work = tmp_path / 'ossie', tmp_path / 'ossie-old'
    for folder in (work, old_work):
        folder.mkdir()
        copy_packaged(python, prefix, env, folder, 'examples/refunds/model.orm.yaml', 'model.orm.yaml')
    copy_packaged(python, prefix, env, work, 'examples/refunds/physical-binding.json', 'binding.json')

    def export(out, *extra, expected, runner=(python, env), cwd=work):
        return gnd(runner[0], prefix, runner[1], cwd, 'export', 'ossie', 'model.orm.yaml', '--out', out, *extra,
                   expected=expected)

    def written(folder, out):
        return sorted(path.name for path in folder.iterdir() if path.name.startswith(out))

    # P5: five files by default; the tables are the relational mapping's; --ontology-only keeps the
    # three-file run with the same bytes; a binding file is accepted.
    export('o.yaml', expected=0)
    assert written(work, 'o.yaml') == ['o.yaml' + suffix for suffix in OSSIE_OUTPUTS]
    semantic = json.loads(run([*prefix, python, '-I', '-c', YAML_TO_JSON, 'o.yaml.semantic_model.yaml'], work, env))
    tables = json.loads(run([*prefix, python, '-I', '-c', RMAP_TABLES, 'model.orm.yaml'], work, env))
    assert tables and sorted(dataset['name'] for dataset in semantic['datasets']) == tables
    export('t.yaml', '--ontology-only', expected=0)
    assert written(work, 't.yaml') == ['t.yaml' + suffix for suffix in OSSIE_ONTOLOGY_OUTPUTS]
    for suffix in OSSIE_ONTOLOGY_OUTPUTS:
        assert (work / ('t.yaml' + suffix)).read_bytes() == (work / ('o.yaml' + suffix)).read_bytes(), suffix
    export('b.yaml', '--physical-binding', 'binding.json', expected=0)
    assert written(work, 'b.yaml') == ['b.yaml' + suffix for suffix in OSSIE_OUTPUTS]
    # Controls: a file at a new path stops the run and nothing else is written; the two options
    # exclude each other; a bound of one byte is a size refusal.
    (work / 'c.yaml.mapping.yaml').write_text('kept', encoding='utf-8')
    export('c.yaml', expected=11)
    assert written(work, 'c.yaml') == ['c.yaml.mapping.yaml']
    assert (work / 'c.yaml.mapping.yaml').read_text(encoding='utf-8') == 'kept'
    export('u.yaml', '--physical-binding', 'binding.json', '--ontology-only', expected=64)
    assert 'ossie:output-size' in export('s.yaml', '--max-output-bytes', '1', expected=3).stderr
    assert written(work, 'u.yaml') == written(work, 's.yaml') == []
    # 0.4.0 writes the three ontology files, with the candidate's bytes, and has no --ontology-only.
    published = (old_python, old_env)
    export('o.yaml', expected=0, runner=published, cwd=old_work)
    assert written(old_work, 'o.yaml') == ['o.yaml' + suffix for suffix in OSSIE_ONTOLOGY_OUTPUTS]
    for suffix in OSSIE_ONTOLOGY_OUTPUTS:
        assert (old_work / ('o.yaml' + suffix)).read_bytes() == (work / ('o.yaml' + suffix)).read_bytes(), suffix
    export('t.yaml', '--ontology-only', expected=64, runner=published, cwd=old_work)
    assert written(old_work, 't.yaml') == []


GROWTH_COMMANDS = [
    ('validate', 'root.orm.yaml'),
    ('evolve', 'preview', 'root.orm.yaml', 'round-1.proposal.json', '--workspace', '.', '--records', 'records',
     '--out', 'preview-1.json', '--policy', 'additive'),
    ('evolve', 'apply', 'root.orm.yaml', 'round-1.proposal.json', '--preview', 'preview-1.json', '--workspace', '.',
     '--records', 'records', '--policy', 'additive'),
    ('evolve', 'preview', 'root.orm.yaml', 'round-2.proposal.json', '--workspace', '.', '--records', 'records',
     '--out', 'preview-2.json', '--policy', 'additive'),
    ('evolve', 'apply', 'root.orm.yaml', 'round-2.proposal.json', '--preview', 'preview-2.json', '--workspace', '.',
     '--records', 'records', '--policy', 'additive'),
    ('validate', 'root.orm.yaml', '--document', 'round-1.document.txt', '--document', 'round-2.document.txt',
     '--require-documents'),
    ('check', 'root.orm.yaml', 'population.json'),
    ('judgments', 'check', 'root.orm.yaml', 'population.json', '--policy', 'policy.json', '--receipts',
     'receipts.json', '--trusted-root', '.'),
]


def test_installed_rw2_seeded_growth(rv2_installed, published_0_4_0, tmp_path):
    _, _, python, _, env, prefix = rv2_installed
    old_python, old_env = published_0_4_0
    work = copy_packaged(python, prefix, env, tmp_path, 'examples/seeded_growth', 'growth')
    old_work = tmp_path / 'growth-old'
    shutil.copytree(work, old_work)
    # P6: the README's commands, each exit 0, from the packaged example.
    outputs = [gnd(python, prefix, env, work, *command, expected=0).stdout
               for command in readme_commands(work, GROWTH_COMMANDS)]
    assert sum(line.startswith('INCLUDE seed ') for line in outputs[0].splitlines()) == 1
    # 0.4.0 holds the reviewed include to the unattended rules, and does not ship the example.
    refused = gnd(old_python, prefix, old_env, old_work, *GROWTH_COMMANDS[0], '--format', 'json', expected=3)
    assert 'semantic:unattended-u5' in {issue['rule_id'] for issue in json.loads(refused.stdout)['issues']}
    assert run([*prefix, old_python, '-I', '-c', PACKAGE_HAS_DIRECTORY, 'examples/seeded_growth'],
               tmp_path, old_env).strip() == 'False'
