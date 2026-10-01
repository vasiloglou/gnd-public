"""Explicitly selected, bounded P2 artifact and curated-diff controls."""
import email
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tarfile
import zipfile

import pytest

ROOT = Path(__file__).resolve().parents[1]
M = Path('.gnd-planning/milestones/public-launch')
MANIFEST = M/'migration/b2-files.json'
LATE = {MANIFEST.as_posix(), (M/'migration/b2-receipt.md').as_posix(),
        (M/'002-phase-2.md').as_posix()}
IGNORED_DIRS = {'.git','.venv','__pycache__','.pytest_cache','.ruff_cache','dist'}


def manifest(root):
    with (root/MANIFEST).open('rb') as stream:
        raw = stream.read(2097153)
    assert len(raw) <= 2097152, 'manifest read cap'
    try:
        data = json.loads(raw, parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))
    except (ValueError, RecursionError) as error:
        raise AssertionError('invalid manifest JSON') from error
    assert isinstance(data, dict) and isinstance(data.get('files'), list)
    assert len(data['files']) <= 2048
    seen = set()
    for row in data['files']:
        assert isinstance(row, dict)
        p = row.get('path')
        assert isinstance(p, str) and p and not Path(p).is_absolute()
        assert '..' not in Path(p).parts and p not in seen
        assert isinstance(row.get('bytes'), int) and not isinstance(row['bytes'], bool)
        assert row['bytes'] >= 0 and isinstance(row.get('public_sha256'), str)
        assert len(row['public_sha256']) == 64 and isinstance(row.get('mode'), int)
        seen.add(p)
    return data


def file_paths(root):
    paths = set()
    for base, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
        for d in list(dirs):
            p = Path(base)/d
            if p.is_symlink():
                paths.add(p.relative_to(root).as_posix())
                dirs.remove(d)
        for name in files:
            if name == '.gnd-install.json' or name.endswith('.pyc'):
                continue
            paths.add((Path(base)/name).relative_to(root).as_posix())
    return paths


def audit_tree(root):
    data = manifest(root)
    rows = {row['path']:row for row in data['files']}
    assert file_paths(root) - LATE == set(rows), 'unattributed path set'
    for path, row in rows.items():
        p = root/path
        assert p.is_symlink() == (row['kind'] == 'installer-link'), path
        if p.is_symlink():
            assert p.exists() and os.readlink(p) == row['link_value'], path
            raw = os.readlink(p).encode()
            mode = stat.S_IMODE(p.lstat().st_mode)
        else:
            assert p.is_file(), path
            raw = p.read_bytes()
            mode = stat.S_IMODE(p.stat().st_mode)
        assert len(raw) == row['bytes'] and hashlib.sha256(raw).hexdigest() == row['public_sha256'], path
        assert mode == row['mode'], path
        assert len(raw) <= 1048576, path
    assert sum(row['bytes'] for row in rows.values()) <= 67108864
    assert sum(row['bytes'] for row in rows.values() if row['path'].startswith('.gnd-planning/')) <= 2097152
    return data


def expected_runtime():
    assert (ROOT/'src/gnd/cli.py').is_file(), 'complete runtime not staged'
    return {row['path'][len('src/'):]:row for row in manifest(ROOT)['files']
            if row['path'].startswith('src/gnd/')}


def audit_payload(payload):
    expected = expected_runtime()
    assert set(payload) == set(expected), ('missing/extra resources', sorted(set(expected)-set(payload)), sorted(set(payload)-set(expected)))
    for path, raw in payload.items():
        assert hashlib.sha256(raw).hexdigest() == expected[path]['public_sha256'], path


def run(args, cwd, env=None, timeout=300):
    result = subprocess.run(list(map(str,args)), cwd=cwd, env=env, text=True,
                            capture_output=True, timeout=timeout)
    assert result.returncode == 0, result.stdout + result.stderr
    return result.stdout + result.stderr


@pytest.fixture(scope='session')
def package_probe(tmp_path_factory):
    expected_runtime()
    tmp = tmp_path_factory.mktemp('outside-checkouts')
    assert not tmp.is_relative_to(ROOT)
    outside = tmp/'working'; outside.mkdir()
    artifacts = tmp/'artifacts'; artifacts.mkdir()
    env = os.environ.copy()
    for key in ['PYTHONPATH','PYTHONHOME','VIRTUAL_ENV','UV_PROJECT_ENVIRONMENT']:
        env.pop(key,None)
    env['PYTHONNOUSERSITE'] = '1'
    logs = {}
    logs['lock'] = run(['uv','lock','--check'], ROOT, env)
    logs['sdist'] = run(['uv','build','--sdist','--out-dir',artifacts], ROOT, env)
    sdist, = artifacts.glob('*.tar.gz')
    logs['wheel'] = run(['uv','build','--wheel',sdist,'--out-dir',artifacts], outside, env)
    wheel, = artifacts.glob('*.whl')
    venv = tmp/'base'; logs['venv'] = run(['uv','venv','--python',sys.executable,venv],outside,env)
    python = venv/'bin/python'
    logs['install'] = run(['uv','pip','install','--python',python,wheel],outside,env)
    retain = os.environ.get('GND_P2_ARTIFACT_DIR')
    if retain:
        retain = Path(retain).resolve(); retain.mkdir(parents=True,exist_ok=True)
        for p in [sdist,wheel]: shutil.copy2(p,retain/p.name)
        (retain/'build-install-log.json').write_text(json.dumps(logs,indent=2)+'\n')
    return dict(python=python,venv=venv,outside=outside,env=env,sdist=sdist,wheel=wheel)


def test_curated_manifest_and_source_owned_ledger():
    audit_tree(ROOT)
    units = json.loads((ROOT/M/'migration/units.json').read_text())
    assert not units['authority_transfer'] and not units['publisher_enabled']
    assert all(row['state'] == 'source-owned' for row in units['units'])


@pytest.mark.parametrize('mutation',['unlisted','changed-b1'])
def test_curated_diff_refuses_mutants(tmp_path, mutation):
    stage = tmp_path/'stage'
    shutil.copytree(ROOT,stage,symlinks=True,ignore=shutil.ignore_patterns(*IGNORED_DIRS,'.gnd-install.json'))
    if mutation == 'unlisted': (stage/'unlisted.txt').write_text('not selected')
    else:
        p = stage/'src/gnd/skills/gnd-orm-core/references/milestone-record-format.md'
        p.write_text(p.read_text()+'drift\n')
    with pytest.raises(AssertionError): audit_tree(stage)


@pytest.mark.parametrize('raw',[b'[]',b'{"files":[7]}',b'{"files":[{"path":"../escape"}]}',b'NaN',b'{'*10000,b'x'*2097153])
def test_manifest_internal_audit_refuses_hostile_shapes(tmp_path, raw):
    p=tmp_path/MANIFEST; p.parent.mkdir(parents=True); p.write_bytes(raw)
    with pytest.raises(AssertionError): manifest(tmp_path)


def test_artifact_and_installed_resource_sets(package_probe):
    probe = package_probe
    with zipfile.ZipFile(probe['wheel']) as archive:
        assert sum(row.file_size for row in archive.infolist()) <= 12582912
        wheel_payload={n:archive.read(n) for n in archive.namelist() if n.startswith('gnd/') and not n.endswith('/')}
        metadata_name, = [n for n in archive.namelist() if n.endswith('.dist-info/METADATA')]
        metadata=email.message_from_bytes(archive.read(metadata_name))
        assert metadata['Name'] == 'get-nick-done' and metadata['Version'] == '0.1.0'
        requires = metadata.get_all('Requires-Dist')
        assert {r for r in requires if ';' not in r} == {'jsonschema==4.26.0','pydantic==2.13.4','ruamel-yaml==0.19.1'}
        assert any(r.startswith('faker==40.36.0') and 'synth' in r for r in requires)
        entry, = [n for n in archive.namelist() if n.endswith('.dist-info/entry_points.txt')]
        assert b'gnd = gnd.cli:main' in archive.read(entry)
    audit_payload(wheel_payload)
    with tarfile.open(probe['sdist']) as archive:
        payload={row.name.split('/src/',1)[1]:archive.extractfile(row).read()
                 for row in archive.getmembers() if row.isfile() and '/src/gnd/' in row.name}
    audit_payload(payload)
    code = "import json,hashlib; from importlib.resources import files; from pathlib import Path; root=Path(str(files('gnd'))); print(json.dumps({'gnd/'+p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts}))"
    installed=json.loads(run([probe['python'],'-c',code],probe['outside'],probe['env'],60))
    assert installed == {p:hashlib.sha256(b).hexdigest() for p,b in wheel_payload.items()}
    for resource in ['gnd/schema/orm-meta.schema.json','gnd/schema/population.schema.json']:
        json.loads(wheel_payload[resource])
    paths=[p for p in wheel_payload if p.endswith('/SKILL.md')]
    assert len(paths) == 16
    missing = dict(wheel_payload); missing.pop('gnd/schema/orm-meta.schema.json')
    with pytest.raises(AssertionError,match='orm-meta.schema.json'): audit_payload(missing)


def test_import_origin_contamination_control(package_probe):
    probe=package_probe
    code="import json,sys,gnd; from importlib.metadata import version; print(json.dumps({'file':gnd.__file__,'path':sys.path,'version':version('get-nick-done'),'python':sys.executable}))"
    dirty=probe['env']|{'PYTHONPATH':str(ROOT/'src')}
    control=json.loads(run([probe['python'],'-c',code],probe['outside'],dirty,60))
    assert Path(control['file']).is_relative_to(ROOT/'src'), 'contamination control did not resolve checkout'
    clean=json.loads(run([probe['python'],'-c',code],probe['outside'],probe['env'],60))
    assert clean['version'] == '0.1.0'
    assert Path(clean['file']).is_relative_to(probe['venv'])
    assert Path(clean['python']).parent == probe['venv']/'bin'
    assert not any(Path(p).is_relative_to(ROOT) for p in clean['path'] if p)
    assert not any('gnd/src' in p for p in clean['path'])
