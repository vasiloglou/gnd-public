"""Marketplace paths must expose the complete canonical skill tree in either host."""
import json
import re
import shutil
import tomllib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def resolve_component(root, relative):
    assert relative.startswith('./')
    result = (root / relative).resolve()
    assert result.is_relative_to(root.resolve()), relative
    assert result.exists(), relative
    return result


def check_bundle(root):
    version = tomllib.loads((root / 'pyproject.toml').read_text())['project']['version']
    canonical = root / 'src/gnd/skills'
    expected = {p.parent.name for p in canonical.glob('*/SKILL.md')}
    assert len(expected) == 16
    assert not {'process-phase', 'plan-review-panel'} & expected
    for host in ['.claude-plugin', '.codex-plugin']:
        manifest = json.loads((root / host / 'plugin.json').read_text())
        assert manifest['name'] == 'gnd' and manifest['version'] == version
        assert manifest['license'] == 'Apache-2.0'
        skills = resolve_component(root, manifest['skills'])
        assert skills == canonical.resolve()
        assert {p.parent.name for p in skills.glob('*/SKILL.md')} == expected
    for path in canonical.rglob('*.md'):
        for href in re.findall(r'\]\(([^)]+)\)', path.read_text()):
            if '://' not in href and not href.startswith('#'):
                assert (path.parent / href.split('#')[0]).exists(), (path, href)
    assert (root / 'LICENSE').is_file() and (root / 'NOTICE').is_file()
    claude = json.loads((root / '.claude-plugin/marketplace.json').read_text())
    codex = json.loads((root / '.agents/plugins/marketplace.json').read_text())
    assert claude['name'] == codex['name'] == 'gnd-marketplace'
    assert len(claude['plugins']) == len(codex['plugins']) == 1
    for entry, source in [(claude['plugins'][0], claude['plugins'][0]['source']),
                          (codex['plugins'][0], codex['plugins'][0]['source']['path'])]:
        assert entry['name'] == 'gnd'
        assert resolve_component(root, source) == root.resolve()
    assert codex['plugins'][0]['policy']['installation'] == 'AVAILABLE'


def test_marketplaces_use_complete_canonical_skills():
    check_bundle(ROOT)


@pytest.mark.parametrize('mutation', ['outside_root', 'missing_reference', 'version'])
def test_broken_plugin_bundle_refused(tmp_path, mutation):
    # Materialize only the bundle boundary, retaining relative reference semantics.
    for folder in ['.claude-plugin', '.codex-plugin', '.agents/plugins', 'src/gnd/skills']:
        shutil.copytree(ROOT / folder, tmp_path / folder)
    for filename in ['pyproject.toml', 'LICENSE', 'NOTICE']:
        shutil.copy2(ROOT / filename, tmp_path / filename)
    check_bundle(tmp_path)
    if mutation == 'missing_reference':
        reference = tmp_path / 'src/gnd/skills/gnd-orm-core/references/representation-format.md'
        reference.unlink()
    else:
        path = tmp_path / '.codex-plugin/plugin.json'
        manifest = json.loads(path.read_text())
        if mutation == 'outside_root':
            manifest['skills'] = './../outside'
        else:
            manifest['version'] = '999.0.0'
        path.write_text(json.dumps(manifest))
    with pytest.raises(AssertionError):
        check_bundle(tmp_path)
