from __future__ import annotations

import re
from importlib.resources import files
from importlib.resources.abc import Traversable
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
AGENTS_MD = REPO_ROOT / "AGENTS.md"


def _skills_root() -> Traversable:
    return files('gnd') / 'skills'


def _packaged_skill_names() -> set[str]:
    return {entry.name for entry in _skills_root().iterdir() if entry.is_dir()}


def test_agents_md_table_names_every_packaged_skill() -> None:
    text = AGENTS_MD.read_text(encoding='utf-8')
    listed = set(re.findall('\\]\\(src/gnd/skills/([a-z0-9-]+)/SKILL\\.md\\)', text))
    packaged = _packaged_skill_names()
    missing = sorted(packaged - listed)
    extra = sorted(listed - packaged)
    assert not missing and (not extra), f"AGENTS.md's skill table is not the packaged tree.\n  missing from the table ({len(missing)}): " + ', '.join(missing) + f'\n  listed but not packaged ({len(extra)}): ' + ', '.join(extra) + '\nThe table routes agents; a packaged skill it omits is a skill nobody is routed to (this is how gnd-new-project went missing), and a listed skill that does not ship is a route to nowhere.'
