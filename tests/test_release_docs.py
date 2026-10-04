"""Focused release documentation checks, no whole-tree historical census."""
from pathlib import Path

import pytest
from test_contributor_preparation import check_links

ROOT = Path(__file__).resolve().parents[1]


def test_release_documentation():
    for name in ['README.md', 'AGENTS.md', 'CONTRIBUTING.md', 'docs/quickstart.md', 'docs/advanced.md',
                 'docs/support.md', 'docs/compatibility.md', 'docs/releasing.md',
                 'docs/launch-drafts.md', 'docs/demo-script.md', 'docs/release-notes.md']:
        check_links(ROOT / name)



def test_broken_link_rejected(tmp_path):
    p = tmp_path / 'doc.md'
    p.write_text('[broken](missing.md)')
    with pytest.raises(AssertionError):
        check_links(p)
