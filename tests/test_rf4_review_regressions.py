"""Bounded current-byte RF4 compatibility and identity-control successors."""
import ast
import importlib
import json
from pathlib import Path

import pytest

import gnd

ROOT = Path(gnd.__file__).resolve().parents[2]
ROWS = json.loads((ROOT / '.gnd-planning/milestones/code-refactoring/evidence/RF4/review-missing-imports-pre-fix.json').read_text())


@pytest.mark.parametrize('row', ROWS, ids=lambda row: row['module'] + ':' + row['name'])
def test_predecessor_import_binding_survives(row):
    old = importlib.import_module(row['module'])
    node = ast.parse(row['statement']).body[0]
    alias = node.names[0]
    if isinstance(node, ast.Import):
        expected = importlib.import_module(alias.name if alias.asname else alias.name.split('.')[0])
    else:
        module = importlib.import_module(node.module)
        expected = getattr(module, alias.name, None)
        if expected is None:
            expected = importlib.import_module(node.module + '.' + alias.name)
    assert getattr(old, row['name']) is expected


@pytest.mark.parametrize('mutation', ['source', 'missing-source', 'omitted-roster'])
def test_identity_stimulus_targets_the_actual_assurance_home(tmp_path, monkeypatch, mutation):
    import test_v6_phase6_release_reader as legacy

    original_fixture, original_publish = legacy.synthetic_release, legacy.publish
    original_bytes = (ROOT / 'src/gnd/assurance/core.py').read_bytes()

    def guarded_publish(package, manifest):
        subject = package / 'assurance/core.py'
        if mutation == 'source':
            assert subject.read_bytes() != original_bytes, 'source mutant missed actual assurance home'
        elif mutation == 'missing-source':
            assert not subject.exists(), 'missing-source mutant missed actual assurance home'
        else:
            assert not any(row['address']['path'] == 'src/gnd/assurance/core.py' for row in manifest['files'])
        original_publish(package, manifest)

    def fixture(root):
        package, manifest = original_fixture(root)
        assert legacy._load(package).available
        monkeypatch.setattr(legacy, 'publish', guarded_publish)
        return package, manifest

    monkeypatch.setattr(legacy, 'synthetic_release', fixture)
    legacy.test_dirty_release_is_rejected_at_its_identity_boundary(tmp_path, mutation)


@pytest.mark.parametrize("case_id", ["C18", "C20"])
def test_cache_stimulus_changes_an_existing_assurance_member(tmp_path, monkeypatch, case_id):
    import test_v63_phase2_cache as legacy

    original = legacy.synthetic_release
    original_open = Path.open

    def fixture(root):
        package, manifest = original(root)
        assert (package / "assurance/core.py").is_file()
        def guarded_open(path, mode="r", *args, **kwargs):
            if mode == "ab":
                assert path == package / "assurance/core.py", "cache stimulus missed actual home"
                assert path.is_file(), "cache stimulus is not an existing production member"
            return original_open(path, mode, *args, **kwargs)

        monkeypatch.setattr(Path, "open", guarded_open)
        return package, manifest

    monkeypatch.setattr(legacy, "synthetic_release", fixture)
    legacy.test_phase2_branch(case_id, tmp_path, monkeypatch)


def test_transition_source_guard_visits_the_defining_payload_module(monkeypatch):
    import public_site_census as census
    import test_public_construction_site_guards as guards

    # Isolate this RF4 finding from the separately reproduced base forwarder defect.
    monkeypatch.setattr(census, "_FORWARDERS", {})
    guards.test_transition_assurance_delegation_is_an_exact_static_site(census.inventory(ROOT))
