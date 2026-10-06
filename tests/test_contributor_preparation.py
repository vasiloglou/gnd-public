"""Current contributor surfaces; negative controls exercise each predicate."""
import re
import shutil
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def check_links(path):
    for href in re.findall(r'\]\(([^)]+)\)', path.read_text()):
        if '://' not in href and not href.startswith('#'):
            assert (path.parent / href.split('#')[0]).exists(), (path, href)


def check_current(root):
    for name in ['process-phase', 'plan-review-panel']:
        a = root / '.codex/skills' / name
        b = root / '.claude/skills' / name
        left = {p.relative_to(a) for p in a.rglob('*') if p.is_file()}
        assert left == {p.relative_to(b) for p in b.rglob('*') if p.is_file()}
        assert left
        for rel in left:
            assert (a / rel).read_bytes() == (b / rel).read_bytes()
            assert (a / rel).stat().st_mode & 0o111 == (b / rel).stat().st_mode & 0o111
            if rel.suffix == '.md':
                check_links(a / rel)
                check_links(b / rel)
    for base in ['.codex', '.claude']:
        links = list((root / base / 'skills').iterdir())
        for skill in (root / 'src/gnd/skills').glob('*/SKILL.md'):
            link = root / base / 'skills' / skill.parent.name
            assert link in links and link.is_symlink()
            assert link.resolve() == skill.parent.resolve()
    for path in (root / 'src/gnd/skills').rglob('*.md'):
        check_links(path)
    paths = [root / 'CONTRIBUTING.md', *root.glob('docs/development/examples/phase-*.md')]
    assert len(paths) >= 3
    for p in paths:
        check_links(p)
        if p.name.startswith('phase-'):
            assert 'non-authoritative' in p.read_text().lower()
    assert 'uv sync --locked --group dev' in paths[0].read_text()


def test_current_contributor_surfaces():
    check_current(ROOT)


@pytest.mark.parametrize('mutation', ['broken_reference', 'twin', 'sample', 'skill_reference'])
def test_contributor_controls_reject(tmp_path, mutation):
    # Copy only this predicate's dependency boundary, preserving link values.
    for name in ['.codex/skills', '.claude/skills', 'src/gnd/skills', 'docs/development']:
        shutil.copytree(ROOT / name, tmp_path / name, symlinks=True)
    for name in ['CONTRIBUTING.md', 'SECURITY.md', 'tools/gnd_layers.json',
                 '.gnd-planning/milestones/code-refactoring/notes/shim-inventory.md']:
        (tmp_path / name).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / name, tmp_path / name)
    (tmp_path / 'docs/releasing.md').write_text('placeholder')
    check_current(tmp_path)
    if mutation == 'broken_reference':
        (tmp_path / 'CONTRIBUTING.md').write_text('[missing](absent.md)')
    elif mutation == 'skill_reference':
        for base in ['.codex', '.claude']:
            with (tmp_path / base / 'skills/process-phase/SKILL.md').open('a') as f:
                f.write('\n[Required reference](definitely-missing-phase4-reference.md)\n')
    elif mutation == 'twin':
        with (tmp_path / '.codex/skills/process-phase/SKILL.md').open('a') as f:
            f.write('changed')
    else:
        (tmp_path / 'docs/development/examples/phase-record.md').write_text('unlabeled')
    with pytest.raises(AssertionError):
        check_current(tmp_path)
