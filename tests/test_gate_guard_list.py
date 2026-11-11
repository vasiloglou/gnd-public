"""Issue 171: the structure and inventory guards are named in the phase gate rules.

Two milestones closed with green focused gates while these guards were red on
main, because no gate named them. The gate rules in ``project.md`` now carry
one command that runs them. This file keeps that command usable: every file it
names exists, the files the issue listed are all there, and the two copies of
the page agree.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = (
    ROOT / ".codex/skills/process-phase/references/project.md",
    ROOT / ".claude/skills/process-phase/references/project.md",
)

#: The guard files issue 171 listed. The block may grow; it may not lose one of these.
ISSUE_171_GUARDS = frozenset({
    "tests/test_rf5_commands.py",
    "tests/test_rf5_review_regressions.py",
    "tests/test_rf6_query_policy.py",
    "tests/test_rf7_structure.py",
    "tests/test_rf8_structure.py",
    "tests/test_rf9_repairs.py",
    "tests/test_rof4_accept_identities.py",
    "tests/test_disclosure_mode.py",
    "tests/test_disclosure_docs.py",
    "tests/test_packaged_skills.py",
    "tests/test_conformance_payload.py",
    "tests/test_development_scaffold.py",
})


def guard_command(text: str) -> list[str]:
    """Return the words of the one guard command in the gate rules."""
    rule = text.split("- Structure and inventory guards, issue 171:", 1)
    assert len(rule) == 2, "the guard rule is missing from the gate rules"
    blocks = re.findall(r"```bash\n(.*?)\n\s*```", rule[1].split("\n- ", 1)[0], flags=re.DOTALL)
    assert len(blocks) == 1, "the guard rule holds exactly one command block"
    lines = [line.strip() for line in blocks[0].splitlines() if line.strip()]
    assert len(lines) == 1, "the guard command is one line, so it can be pasted"
    return lines[0].split()


def test_the_guard_command_names_existing_files_and_every_listed_guard():
    words = guard_command(PAGES[0].read_text(encoding="utf-8"))
    assert words[:4] == ["uv", "run", "pytest", "-q"]
    files = [word for word in words if word.startswith("tests/")]
    assert len(files) == len(set(files)), "a guard file is named twice"
    missing = [name for name in files if not (ROOT / name).is_file()]
    assert not missing, f"the guard command names files that do not exist: {missing}"
    assert ISSUE_171_GUARDS <= set(files), sorted(ISSUE_171_GUARDS - set(files))
    # The default lane filter stays in force: no marker or addopts override.
    assert not {"-m", "-o", "--override-ini"} & set(words)


def test_both_copies_of_the_gate_rules_agree():
    assert PAGES[0].read_bytes() == PAGES[1].read_bytes()


def test_a_missing_or_split_command_is_reported():
    text = PAGES[0].read_text(encoding="utf-8")
    words = guard_command(text)
    broken = text.replace(" ".join(words), " ".join(words[:5]) + "\n  " + " ".join(words[5:]))
    assert broken != text
    for bad in (text.replace("- Structure and inventory guards, issue 171:", "- Guards:"), broken):
        try:
            guard_command(bad)
        except AssertionError:
            continue
        raise AssertionError("a damaged gate rule was accepted")
