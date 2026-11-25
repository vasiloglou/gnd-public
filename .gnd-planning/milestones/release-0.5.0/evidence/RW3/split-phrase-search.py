"""List page text where a line break splits a phrase the publication check looks for.

`tools/release_text.py check` reads lines, so it does not report such a phrase. This search joins
the lines of each block of text (blocks are separated by blank lines) and prints every block that
holds more of the check's phrases joined than its lines hold one by one. It judges nothing: a
person reads what it prints. Run from the repository root; exit 1 when it prints a block.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, "tools")
import release_text

root = Path(".")
found = []
for relative in ["docs/release-notes.md", *release_text.page_files(root)]:
    try:
        text = (root / relative).read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue
    for block in re.split(r"\n[ \t]*\n", text):
        lines = [" ".join(line.split()) for line in block.splitlines() if line.strip()]
        joined = " ".join(lines)
        if len(release_text.STALE.findall(joined)) > sum(len(release_text.STALE.findall(line)) for line in lines):
            found.append(f"{relative}: {joined[:200]}")
for entry in found:
    print(entry)
print(f"split-phrase search: {len(found)} block(s)")
sys.exit(1 if found else 0)
