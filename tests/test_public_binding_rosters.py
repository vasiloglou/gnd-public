from __future__ import annotations

import functools
import json
import os
import shutil
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
CORPUS = REPO_ROOT / "tests/fixtures/public-binding-rosters"
EVOLUTION = CORPUS / "evolution"
LINKED_PROJECT = EVOLUTION / "linked-project"
LINKED_PROJECT_LINKS = EVOLUTION / "linked-project.links.json"
EXPECTED = json.loads((CORPUS / "answers.json").read_text(encoding="utf-8"))


def _materialize_linked_project(destination: Path) -> Path:
    """Copy the committed linked project and create its declared symlink leaves.

    The links are declared as data rather than committed as tracked symlinks:
    every tracked symlink in this repository is installer output under
    ``.claude/skills/`` or ``.codex/skills/``, and
    ``tests/test_operator_neutral_evidence.py`` holds that invariant. Creating
    them here produces exactly the tree a real linked project with a symlink
    leaf presents, without adding a thirty-first tracked link.
    """
    shutil.copytree(LINKED_PROJECT, destination)
    declared = json.loads(LINKED_PROJECT_LINKS.read_text(encoding='utf-8'))['links']
    for relative, target in declared.items():
        leaf = destination.joinpath(*relative.split('/'))
        assert not leaf.exists(), f'{relative} is committed as a regular file'
        leaf.parent.mkdir(parents=True, exist_ok=True)
        os.symlink(target, leaf)
    return destination


def _roster(name: str) -> dict[str, Any]:
    return json.loads((EVOLUTION / 'rosters' / f'{name}.json').read_text(encoding='utf-8'))


def _refusal(callable_: Any, *arguments: Any, **keywords: Any) -> str:
    """Return the refusal text, or fail because nothing was refused."""
    try:
        callable_(*arguments, **keywords)
    except Exception as error:  # noqa: BLE001 - the refusal IS the observation
        return f'{type(error).__name__}: {error}'
    raise AssertionError('the reader accepted a document the corpus requires it to refuse')


def test_the_evolution_module_publishes_the_three_version_constants() -> None:
    """INTENDED RED. Version 2 is renamed to the locator constant and 3 becomes
    the current one."""
    from gnd.evolve import models as evolution_models
    for name, value in EXPECTED['evolution']['constants'].items():
        assert getattr(evolution_models, name, None) == value, name


def test_the_tracked_roster_model_accepts_the_two_legal_rosters() -> None:
    """INTENDED RED. An empty roster is legal and explicit."""
    from gnd.evolve.models import TrackedRoster
    complete = TrackedRoster.model_validate(_roster('complete'))
    assert list(complete.paths) == _roster('complete')['paths']
    empty = TrackedRoster.model_validate(_roster('empty'))
    assert list(empty.paths) == []
    assert complete.model_dump(mode='json') == _roster('complete')
    assert sorted(complete.model_dump(mode='json')) == EXPECTED['evolution']['roster']['wire']['keys']


@pytest.mark.parametrize('case_id', [case_id for case_id, stage in EXPECTED['evolution']['roster']['refusals'].items() if stage == 'schema'])
def test_every_unsafe_roster_is_refused_before_any_filesystem_access(case_id: str) -> None:
    """INTENDED RED. A schema refusal, with no leaf ever opened."""
    from gnd.evolve.models import TrackedRoster
    document = next(case['roster'] for case in _roster('unsafe')['cases'] if case['case_id'] == case_id)
    opened: list[str] = []
    real_open = Path.open

    def watched(self: Path, *arguments: Any, **keywords: Any):
        opened.append(str(self))
        return real_open(self, *arguments, **keywords)
    Path.open = watched
    try:
        _refusal(TrackedRoster.model_validate, document)
    finally:
        Path.open = real_open
    assert opened == []


def test_the_snapshot_primitive_binds_listed_leaves_and_ignores_everything_else(tmp_path: Path) -> None:
    """INTENDED RED. T3.4f-j in one walk over the approved identity moves."""
    from gnd.artifacts import snapshot_tracked_roster
    answer = EXPECTED['evolution']['roster']
    moves = EXPECTED['evolution']['identity_moves']
    roster = _roster('complete')['paths']

    def fresh() -> Path:
        return _materialize_linked_project(tmp_path / f'copy{len(list(tmp_path.iterdir()))}')
    base_root = fresh()
    entries, digest = snapshot_tracked_roster(base_root, roster, label='linked')
    assert [entry.model_dump(mode='json') for entry in entries] == answer['linked_project_entries']
    assert digest == answer['linked_project_digest']
    assert snapshot_tracked_roster(fresh(), [], label='empty')[1] == answer['empty_digest']
    unchanged = fresh()
    (unchanged / 'brand-new.txt').write_text('unlisted\n', encoding='utf-8')
    (unchanged / 'brand-new-directory').mkdir()
    os.symlink('README.md', unchanged / 'brand-new-link.md')
    assert snapshot_tracked_roster(unchanged, roster, label='linked')[1] == digest
    assert moves['add-unlisted-regular'] == 'unchanged'
    edited = fresh()
    (edited / 'README.md').write_text('edited\n', encoding='utf-8')
    assert snapshot_tracked_roster(edited, roster, label='linked')[1] != digest
    chmodded = fresh()
    (chmodded / 'README.md').chmod(493)
    assert snapshot_tracked_roster(chmodded, roster, label='linked')[1] != digest
    retargeted = fresh()
    (retargeted / 'symlink-to-readme.md').unlink()
    os.symlink('run.sh', retargeted / 'symlink-to-readme.md')
    assert snapshot_tracked_roster(retargeted, roster, label='linked')[1] != digest
    deleted = fresh()
    (deleted / 'README.md').unlink()
    _refusal(snapshot_tracked_roster, deleted, roster, label='linked')
    retyped = fresh()
    (retyped / 'README.md').unlink()
    (retyped / 'README.md').mkdir()
    _refusal(snapshot_tracked_roster, retyped, roster, label='linked')


@pytest.mark.parametrize('case_id', [case_id for case_id, stage in EXPECTED['evolution']['roster']['refusals'].items() if stage == 'snapshot'])
def test_snapshot_refuses_a_directory_or_missing_leaf(case_id: str, tmp_path: Path) -> None:
    """INTENDED RED. The two roster refusals that only the filesystem can find."""
    from gnd.artifacts import snapshot_tracked_roster
    document = next(case['roster'] for case in _roster('unsafe')['cases'] if case['case_id'] == case_id)
    root = _materialize_linked_project(tmp_path / 'project')
    _refusal(snapshot_tracked_roster, root, document['paths'], label='linked')


def test_the_roster_caps_and_traversal_guards_each_have_a_control(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """P3R-3: the three caps (§4 rule 3), an interior symlink, and the readlink race."""
    from gnd import artifacts
    caps = EXPECTED['evolution']['roster']['snapshot']
    assert artifacts.DEFAULT_MAX_FILES == caps['max_entries']
    assert artifacts.DEFAULT_MAX_FILE_BYTES == caps['max_file_bytes']
    assert artifacts.DEFAULT_MAX_TOTAL_BYTES == caps['max_total_bytes']
    root = _materialize_linked_project(tmp_path / 'project')
    snapshot = functools.partial(artifacts.snapshot_tracked_roster, root, label='linked')
    paths = _roster('complete')['paths']
    for cap, token in (('max_entries', '-path cap'), ('max_file_bytes', '-byte cap'), ('max_total_bytes', '-byte aggregate cap')):
        assert token in _refusal(snapshot, paths, **{cap: 1})
    os.symlink('nested', root / 'alias')
    assert "component 'alias' is a symlink" in _refusal(snapshot, ['alias/data.json'])
    real = os.readlink

    def retargeting(path: Any, *, dir_fd: int | None=None) -> str:
        target = real(path, dir_fd=dir_fd)
        os.unlink(path, dir_fd=dir_fd)
        os.symlink('run.sh', path, dir_fd=dir_fd)
        return target
    monkeypatch.setattr(os, 'readlink', retargeting)
    assert 'ArtifactIdentityError' in _refusal(snapshot, ['symlink-to-readme.md'])
