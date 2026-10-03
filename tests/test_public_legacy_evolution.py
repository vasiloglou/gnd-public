from __future__ import annotations

import base64
import gzip
import hashlib
import io
import json
import shutil
from pathlib import Path, PurePosixPath

import pytest
from test_public_binding_reports import _run_subprocess

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = REPO_ROOT / "tests/fixtures/public-legacy-evolution/workspace.json.gz"
GRAPHS = REPO_ROOT / "tests/fixtures/public-legacy-evolution/graphs"
GENERATED_PROJECT = REPO_ROOT / "tests/fixtures/public-legacy-evolution/generated-project"
FIXTURE_SHA256 = 'a597a55c5ff0e73538aadde9bd0bbfa4f70a355426c213560436a876a4540f6b'
EXPECTED = {'evolution': {'old_pending_refusal': {'error_type': 'EvolutionReadOnlyCompatibilityError', 'exit': 11, 'precedes': 'any interpretation of the old tree digest or any filesystem read', 'refused_versions': [1, 2], 'stable_name': 'evolution:old-pending-read-only'}, 'read_only_preview_refusal': {'exit': 70, 'message_contains': 'read-only compatibility evidence', 'refused_versions': [1, 2]}}}
GRAPH_DOCUMENTS = ("proposal.json", "preview.json", "intent.json", "pending.json", "conformance.json", "record.json")


@pytest.fixture(autouse=True)
def _bind_legacy_fixture(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    assert not FIXTURE.is_symlink()
    with FIXTURE.open("rb") as stream:
        packed = stream.read(64 * 1024 + 1)
    assert len(packed) <= 64 * 1024
    assert hashlib.sha256(packed).hexdigest() == FIXTURE_SHA256
    with gzip.GzipFile(fileobj=io.BytesIO(packed)) as stream:
        raw = stream.read(512 * 1024 + 1)
    assert len(raw) <= 512 * 1024
    members = json.loads(raw)
    assert len(members) == 27
    root = tmp_path / "fixture"
    root.mkdir()
    for name, member in members.items():
        relative = PurePosixPath(name)
        assert not relative.is_absolute() and all(part not in {"", ".", ".."} for part in name.split("/"))
        data = base64.b64decode(member["raw_base64"], validate=True)
        assert len(data) <= 64 * 1024
        assert hashlib.sha256(data).hexdigest() == member["sha256"]
        path = root.joinpath(*relative.parts)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        path.chmod(member["mode"])
    monkeypatch.setitem(globals(), "GRAPHS", root / "graphs")
    monkeypatch.setitem(globals(), "GENERATED_PROJECT", root / "generated-project")


def _tree_sha256(root: Path) -> str:
    """The whole-tree identity the v1/v2 wires record, recomputed here."""
    digest = hashlib.sha256()
    for path in sorted(root.rglob('*'), key=lambda item: item.relative_to(root).as_posix()):
        relative = path.relative_to(root).as_posix().encode('utf-8')
        if path.is_symlink():
            digest.update(b'L\x00' + relative + b'\x00' + path.readlink().as_posix().encode('utf-8'))
        elif path.is_file():
            digest.update(b'F\x00' + relative + b'\x00' + path.read_bytes())
        elif path.is_dir():
            digest.update(b'D\x00' + relative + b'\x00')
    return digest.hexdigest()


def _evolution_source_workspace(root: Path, *, with_proposal: bool=True) -> dict[str, Path]:
    """Rebuild the workspace the committed v2 graph was produced from.

    The linked project is COPIED from ``evolution/generated-project/`` rather
    than re-emitted: those bytes were emitted once with a workspace-relative
    model path, so they carry no absolute path, their tree identity is the one
    the committed graph binds, and the whole workspace reproduces at any
    filesystem location.
    """
    workspace = root / 'workspace'
    workspace.mkdir(parents=True)
    shutil.copy(GRAPHS / 'v2' / 'before-model.orm.yaml', workspace / 'model.orm.yaml')
    (workspace / 'model.verbalization.txt').write_text('pre-existing verbalization\n', encoding='utf-8')
    shutil.copy(GRAPHS / 'v2' / 'published-model.orm.yaml', workspace / 'candidate.orm.yaml')
    shutil.copytree(GENERATED_PROJECT, workspace / 'linked-project', symlinks=True)
    if with_proposal:
        shutil.copy(GRAPHS / 'v2' / 'proposal.json', workspace / 'proposal.json')
    return {'workspace': workspace, 'model': workspace / 'model.orm.yaml', 'candidate': workspace / 'candidate.orm.yaml', 'project_root': workspace / 'linked-project', 'project_tree': _tree_sha256(workspace / 'linked-project'), 'proposal': workspace / 'proposal.json', 'preview': workspace / 'review' / 'preview.json', 'records': workspace / 'records'}


def _evolution_preview_argv(paths: dict[str, Path]) -> list[str]:
    return ['evolve', 'preview', str(paths['model']), str(paths['proposal']), '--workspace', str(paths['workspace']), '--records', str(paths['records']), '--out', str(paths['preview']), '--format', 'json']


def _evolve_workspace(tmp_path: Path, version: int) -> dict[str, Path]:
    """A workspace holding one graph's model, records and linked project."""
    workspace = tmp_path / 'workspace'
    (workspace / 'records' / 'proposal-linked-conformance').mkdir(parents=True)
    shutil.copy(GRAPHS / 'v2' / 'published-model.orm.yaml', workspace / 'model.orm.yaml')
    shutil.copy(GRAPHS / 'v2' / 'published-model.verbalization.txt', workspace / 'model.verbalization.txt')
    records = workspace / 'records' / 'proposal-linked-conformance'
    for name in GRAPH_DOCUMENTS:
        if name == 'conformance.json':
            (records / 'conformance').mkdir(exist_ok=True)
            shutil.copy(GRAPHS / f'v{version}' / name, records / 'conformance' / 'linked.json')
            continue
        shutil.copy(GRAPHS / f'v{version}' / name, records / name)
    shutil.copytree(GENERATED_PROJECT, workspace / 'linked-project')
    return {'workspace': workspace, 'records': workspace / 'records', 'pending': records / 'pending.json'}


@pytest.mark.parametrize('version', [1, 2])
def test_an_old_pending_state_is_refused_by_name_at_exit_eleven(tmp_path: Path, version: int) -> None:
    """INTENDED RED. v1 and v2 pending states stay readable and are refused by
    name before any old tree digest is interpreted."""
    answer = EXPECTED['evolution']['old_pending_refusal']
    paths = _evolve_workspace(tmp_path, version)
    done = _run_subprocess(['evolve', 'finalize', str(paths['workspace'] / 'model.orm.yaml'), str(paths['pending']), '--workspace', str(paths['workspace']), '--records', str(paths['records']), '--format', 'json'], cwd=tmp_path)
    combined = (done.stdout + done.stderr).decode('utf-8', 'replace')
    assert done.returncode == answer['exit'], combined
    assert answer['stable_name'] in combined, combined


@pytest.mark.parametrize('version', [1, 2])
def test_an_old_proposal_can_no_longer_start_a_fresh_preview(tmp_path: Path, version: int) -> None:
    """v1 is already refused (CONTROL); v2 must join it (INTENDED RED)."""
    answer = EXPECTED['evolution']['read_only_preview_refusal']
    paths = _evolution_source_workspace(tmp_path, with_proposal=False)
    shutil.copy(GRAPHS / f'v{version}' / 'proposal.json', paths['proposal'])
    done = _run_subprocess(_evolution_preview_argv(paths), cwd=tmp_path)
    combined = (done.stdout + done.stderr).decode('utf-8', 'replace')
    assert done.returncode == answer['exit'], combined
    assert answer['message_contains'] in combined, combined
