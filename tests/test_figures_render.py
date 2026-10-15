"""A1 figures fix: a Markdown image right after an HTML opening tag prints as text on GitHub."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_no_markdown_image_directly_after_an_html_opening_tag():
    found = []
    for page in sorted((ROOT / 'docs').rglob('*.md')):
        lines = page.read_text(encoding='utf-8').splitlines()
        for before, line in zip(lines, lines[1:]):
            if line.lstrip().startswith('![') and re.match(r'\s*<(div|figure|section)\b[^>]*>\s*$', before):
                found.append(f'{page.relative_to(ROOT)}: {line[:60]}')
    assert not found, found
