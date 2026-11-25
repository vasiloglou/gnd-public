"""Compare the four public transfer entries with the owner-authorized source revision."""
import re
import subprocess
import sys
from pathlib import Path

REVISION = "65b73ee9d687365dfabb15cc1412a4ee9b4a4111"
SOURCE_HOME = Path(sys.argv[1])
RANGES = {
    "OQ-V52-P1-IMPORTWALK-1": ("milestones/v5.2/001-phase-1.md", 264, 264),
    "OQ-V52-CLOSE-CANONJSON-1": ("milestones/v5.2/notes/v5.2-close-amendments.md", 54, 56),
    "OQ-V63-CLOSE-HELPER-TAIL-1": ("milestones/v6.3/009-milestone-close.md", 116, 120),
    "OQ-V72-P1-ARTIFACT-COPIES": ("open-questions.md", 660, 665),
}


def source(path):
    return subprocess.check_output(
        ["git", "-C", str(SOURCE_HOME), "show", f"{REVISION}:.gnd-planning/{path}"], text=True,
    ).splitlines()


def normalized(lines):
    return " ".join(" ".join(lines).split())


register = source("open-questions.md")
public = Path(".gnd-planning/open-questions.md").read_text()
sections = re.split(r"^### (OQ-[\w-]+)\n", public, flags=re.MULTILINE)
assert sections[1::2] == list(RANGES)
for key, entry in zip(sections[1::2], sections[2::2], strict=True):
    path, first, last = RANGES[key]
    assert f"{REVISION}/.gnd-planning/{path}#L{first}" in entry
    assert entry.count("Decision for #308 is transfer to gnd-public.") == 1
    state = re.search(r"Transferred as \*\*(open|carried)\*\*", entry)[1]
    assert any(line.startswith(f"| `{key}` |") and line.endswith(f"| {state} |") for line in register)
    groups = re.findall(r"(?:^> [^\n]*(?:\n|$))+", entry, flags=re.MULTILINE)
    expected = [source(path)[first-1:last]]
    if key == "OQ-V72-P1-ARTIFACT-COPIES":
        expected.append(register[666:672])
    for quoted, original in zip(groups, expected, strict=True):
        assert normalized(line[2:] for line in quoted.splitlines()) in normalized(original)
    print(f"{key} {state} verified")
