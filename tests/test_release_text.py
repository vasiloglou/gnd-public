"""Issue 176: the publication-day text check and edits are one maintained tool.

``tools/release_text.py`` replaces the shell check and the hand-made patches that
0.2.0 and 0.3.0 each adapted from the release before. The check runs here on
every default-lane run, so a page cannot drift back to prepared-state wording
between releases. The edits are exercised on a copy of the pages prepared for
an invented next version.
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

import pytest
import test_release_version as version_rules

ROOT = Path(__file__).resolve().parents[1]


def _tool():
    spec = importlib.util.spec_from_file_location("release_text", ROOT / "tools/release_text.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


tool = _tool()

# A small historical site shape keeps the mutation cases stable as releases
# change the live repository pages.
PIN_030 = "uv tool install get-nick-done==0.3.0\n"
PAGES = {
    "pyproject.toml": '[project]\nversion = "0.3.1"\n',
    "tests/test_release_version.py": 'RELEASED = {"0.1.0", "0.2.0", "0.3.0"}\nTAGGED = {"0.3.1"}\n',
    "README.md": PIN_030,
    "docs/index.md": PIN_030,
    "docs/installation.md": (
        "# Install GND\n\n" + PIN_030
        + "[v0.3.0 release](https://github.com/vasiloglou/gnd-public/releases/tag/v0.3.0)\n"
        "get_nick_done-0.3.0-py3-none-any.whl\n"
    ),
    "docs/marketplace-plugins.md": (
        PIN_030 + "The `v0.3.0` tag contains the marketplace entries.\n"
        "installs only the latest release. Install the runtime from a checkout of the\n"
        "same commit.\n"
        "not register the development checkout in the user's marketplace configuration.\n"
    ),
    "docs/release-notes.md": (
        "# Release notes\n\n"
        "Version 0.3.0, published on 2026-11-11, is the latest release; 0.2.0 and 0.1.0\n"
        "came before it. Version 0.3.1 is a GitHub tag only and is not published on the\n"
        "package index. Releases follow the [release procedure](releasing.md). Changes on\n"
        "`main` after a release are listed in an `Unreleased:` section until the next\n"
        "one.\n\n"
        "## 0.3.1 (tagged 2026-11-11, not published on PyPI)\n\n"
        'uv tool install "git+https://github.com/vasiloglou/gnd-public@v0.3.1"\n\n'
        "## 0.3.0 (2026-11-11)\n"
    ),
    "docs/compatibility.md": (
        "# Compatibility\n\n"
        "Distribution `get-nick-done`, import and CLI `gnd` remain stable. Versions\n"
        "0.1.0, 0.2.0 and 0.3.0 are published (0.3.0 on 2026-11-11). Version 0.3.1 is a\n"
        "GitHub tag only and is not published on the package index. For the next version,\n"
        "confirm service ownership and that the version is still free before candidate\n"
        "freeze and again before any upload. Milestone numbers are not package versions.\n\n"
    ),
    "docs/support.md": (
        "| Ubuntu, Python 3.11 | Observed in Phase 3 acceptance of 0.1.0 |\n"
        "| macOS 27 arm64 | Observed in release acceptance of the 0.2.0 candidate built from `7c0f4d0e` |\n"
        "| macOS 27 arm64, Python 3.11, uv 0.10.10 | Observed in release acceptance of the 0.3.0"
        " candidate built from `4c07c0e6` |\n"
        "| Other Python >=3.11 / OS | Metadata compatibility only, unmeasured |\n"
    ),
    "docs/releasing.md": (
        "were validated. Every release through 0.4.0 (0.1.0, 0.2.0, 0.3.0 and 0.4.0) was\n"
        "   `## X.Y.Z (tagged YYYY-MM-DD, not published on PyPI)`, and give in it the\n"
    ),
    "docs/development/candidate.md": "The artifact is `get_nick_done-0.1.0-py3-none-any.whl`.\n",
}
NEXT = "9.9.9"
PUBLISH = {"date": "2027-01-02", "built": "0123abcd", "profile": "macOS 27 arm64, Python 3.11, uv 0.10.10"}


def copy_tree(tmp_path: Path) -> Path:
    for relative, contents in PAGES.items():
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(contents, encoding="utf-8")
    return tmp_path


def edit(root: Path, relative: str, old: str, new: str) -> None:
    path = root / relative
    text = path.read_text(encoding="utf-8")
    assert old in text, (relative, old)
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def prepare_next(root: Path) -> Path:
    """Put the copied pages in the state release preparation leaves them in for `NEXT`."""
    current = tool.declared_version(root)
    edit(root, "pyproject.toml", f'version = "{current}"', f'version = "{NEXT}"')
    edit(root, "docs/release-notes.md", f"## {current} (", (
        f"## {NEXT} (prepared, not published)\n\n"
        f"Everything in this section is on `main` after {current} and is not in any published\npackage.\n\n"
        f"## {current} ("))
    edit(root, "docs/release-notes.md", "Releases follow the", f"Version {NEXT} is prepared. Releases follow the")
    edit(root, "docs/support.md", "| Other Python >=3.11 / OS |", (
        f"| Any profile, prepared {NEXT} package | Not signed off; no profile is observed for {NEXT} yet |\n"
        "| Other Python >=3.11 / OS |"))
    edit(root, "docs/marketplace-plugins.md", "installs only the latest release.", (
        f"installs only the latest release. The plugin on `main` is version {NEXT},\n"
        "which is prepared and not published."))
    return root


def test_no_page_describes_the_state_before_publication():
    assert tool.problems(ROOT) == []


def test_the_tool_and_the_version_rules_read_the_same_homes():
    assert tool.PIN_FILES == version_rules.PIN_FILES
    assert tool.released_versions(ROOT) == sorted(version_rules.RELEASED, key=tool.version_key)
    assert tool.declared_version(ROOT) == version_rules.declared_version()
    assert tool.tagged_versions(ROOT) == sorted(version_rules.TAGGED, key=tool.version_key)


# -- tag-only versions: a GitHub tag that never reaches the package index --

def tag_next(root: Path) -> Path:
    """Put the copied pages in the state of a tag-only `NEXT`, as a tag-only release leaves them."""
    declared = tool.declared_version(root)
    subject = tool.released_versions(root)[-1]
    edit(root, "pyproject.toml", f'version = "{declared}"', f'version = "{NEXT}"')
    line = tool.TAGGED_LINE.search((root / tool.RELEASED_HOME).read_text(encoding="utf-8")).group(0)
    edit(root, tool.RELEASED_HOME, line, f'TAGGED = {{"{NEXT}"}}')
    first = next(m.group(0) for m in re.finditer(r"^## .*$", (root / tool.NOTES).read_text(encoding="utf-8"), re.MULTILINE))
    edit(root, tool.NOTES, first, (
        f"## {NEXT} (tagged 2027-01-02, not published on PyPI)\n\n{tool.tag_install_command(NEXT)}\n\n{first}"))
    released = tool.released_versions(root)
    for relative, start, build in (
        (tool.NOTES, "Version ", tool.notes_opening),
        (tool.COMPATIBILITY, tool.COMPATIBILITY_START, tool.compatibility_paragraph),
    ):
        paragraphs = (root / relative).read_text(encoding="utf-8").split("\n\n")
        index = next(i for i, p in enumerate(paragraphs) if p.startswith(start))
        paragraphs[index] = build(subject, "2026-11-11", released, [NEXT])
        (root / relative).write_text("\n\n".join(paragraphs), encoding="utf-8")
    return root


def test_a_tag_only_version_is_checked_against_the_latest_published_pages(tmp_path):
    root = tag_next(copy_tree(tmp_path))
    assert tool.subject_version(root) == tool.released_versions(root)[-1]
    assert tool.problems(root) == []   # the control


@pytest.mark.parametrize("mutation, expected", [
    ("heading-undated", "not `tagged DATE, not published on PyPI`"),
    ("heading-missing", "expected one `## 9.9.9 (tagged DATE"),
    ("no-install-command", "does not give `uv tool install"),
    ("opening-silent", "the opening paragraph is not the published form"),
    ("compatibility-silent", "the version paragraph is not the published form"),
    ("also-released", "is in both RELEASED and TAGGED"),
    ("not-newer", "is not newer than published"),
])
def test_a_tag_only_version_left_incomplete_is_reported(tmp_path, mutation, expected):
    root = tag_next(copy_tree(tmp_path))
    if mutation == "heading-undated":
        edit(root, tool.NOTES, f"## {NEXT} (tagged 2027-01-02, not published on PyPI)", f"## {NEXT} (tagged)")
    elif mutation == "heading-missing":
        edit(root, tool.NOTES, f"## {NEXT} (tagged 2027-01-02, not published on PyPI)", "## Unreleased: something")
    elif mutation == "no-install-command":
        edit(root, tool.NOTES, tool.tag_install_command(NEXT), "Install from the tag.")
    elif mutation == "opening-silent":
        edit(root, tool.NOTES, tool.tag_sentence(NEXT).split(" is a ")[0], "A tag")
    elif mutation == "compatibility-silent":
        edit(root, tool.COMPATIBILITY, tool.tag_sentence(NEXT).split(" is a ")[0], "A tag")
    elif mutation == "also-released":
        line = tool.RELEASED_LINE.search((root / tool.RELEASED_HOME).read_text(encoding="utf-8")).group(0)
        edit(root, tool.RELEASED_HOME, line, line[:-1] + f', "{NEXT}"}}')
    else:
        edit(root, "pyproject.toml", f'version = "{NEXT}"', 'version = "0.0.1"')
        edit(root, tool.RELEASED_HOME, f'TAGGED = {{"{NEXT}"}}', 'TAGGED = {"0.0.1"}')
    found = tool.problems(root)
    assert any(expected in problem for problem in found), found


def test_a_tag_only_version_cannot_be_published_to_the_index(tmp_path):
    root = tag_next(copy_tree(tmp_path))
    with pytest.raises(tool.ReleaseTextError, match="tag-only"):
        tool.publish(root, **PUBLISH)


def test_a_later_publication_drops_the_older_tag_sentence(tmp_path):
    root = tag_next(copy_tree(tmp_path))
    def opening(*arguments):
        return " ".join(tool.notes_opening(*arguments).split())
    assert tool.tag_sentence(NEXT) in opening("0.3.0", "2026-11-11", ["0.3.0"], [NEXT])
    assert tool.tag_sentence(NEXT) not in opening("10.0.0", "2027-02-02", ["0.3.0", "10.0.0"], [NEXT])
    assert tool.tagged_versions(root) == [NEXT]


def test_publication_of_a_prepared_version(tmp_path):
    root = copy_tree(tmp_path)
    previous = tool.declared_version(root)
    prepare_next(root)
    before = tool.released_versions(root)
    assert NEXT not in before
    assert tool.problems(root) == []   # before publication the check has nothing to say

    changed = tool.publish(root, **PUBLISH)
    assert set(changed) == {
        "README.md", "docs/installation.md", "docs/index.md", "docs/marketplace-plugins.md",
        "docs/release-notes.md", "docs/compatibility.md", "docs/support.md", "tests/test_release_version.py"}
    assert tool.released_versions(root) == [*before, NEXT]

    def text(relative):
        return (root / relative).read_text(encoding="utf-8")

    for relative in tool.PIN_FILES:
        assert set(re.findall(r"get-nick-done==([\w.]+)", text(relative))) == {NEXT}, relative
    assert f"[v{NEXT} release](https://github.com/vasiloglou/gnd-public/releases/tag/v{NEXT})" in text("docs/installation.md")
    assert f"get_nick_done-{NEXT}-py3-none-any.whl" in text("docs/installation.md")
    assert f"The `v{NEXT}` tag contains" in text("docs/marketplace-plugins.md")
    notes = text("docs/release-notes.md")
    assert f"\n## {NEXT} (2027-01-02)\n" in notes and "prepared, not published)" not in notes
    opening = " ".join(notes.split("\n\n")[1].split())
    assert opening.startswith(
        f"Version {NEXT}, published on 2027-01-02, is the latest release; 0.3.0, 0.2.0 and 0.1.0 came before it.")
    compatibility = " ".join(text("docs/compatibility.md").split("\n\n")[1].split())
    assert f"Versions 0.1.0, 0.2.0, 0.3.0 and {NEXT} are published ({NEXT} on 2027-01-02)." in compatibility
    assert (f"| {PUBLISH['profile']} | Observed in release acceptance of the {NEXT} candidate built from "
            "`0123abcd` |") in text("docs/support.md")
    assert "no profile is observed" not in text("docs/support.md")

    # What is left is what a person wrote for this release, and only that.
    left = tool.problems(root)
    assert left == [
        f"stale: docs/release-notes.md: Everything in this section is on `main` after {previous} and is not in any published",
        "stale: docs/marketplace-plugins.md: which is prepared and not published. Install the runtime from a checkout of the",
    ], left
    edit(root, "docs/release-notes.md", " and is not in any published\npackage.", ".")
    edit(root, "docs/marketplace-plugins.md", f" The plugin on `main` is version {NEXT},\nwhich is prepared and not published.", "")
    assert tool.problems(root) == []

    # A second run changes nothing.
    snapshot = {relative: text(relative) for relative in PAGES}
    assert tool.publish(root, **PUBLISH) == []
    assert snapshot == {relative: text(relative) for relative in PAGES}


def _replace_line(root: Path, relative: str, start: str, new: str | None) -> None:
    path = root / relative
    lines = path.read_text(encoding="utf-8").split("\n")
    found = [i for i, line in enumerate(lines) if line.startswith(start)]
    assert len(found) == 1, (relative, start, found)
    if new is None:
        del lines[found[0]]
    else:
        lines[found[0]] = new
    path.write_text("\n".join(lines), encoding="utf-8")


MUTATIONS = {
    "old-pin": ("README.md", "uv tool install get-nick-done==", "uv tool install get-nick-done==0.2.0",
                "README.md: pins ['0.2.0']"),
    "older-version-named": ("docs/index.md", "uv tool install get-nick-done==",
                            "These pages need the 0.2.0 wheel.", "stale: docs/index.md: These pages need the 0.2.0 wheel."),
    "prepared-wording": ("docs/installation.md", "# ", "# Install the development checkout",
                         "stale: docs/installation.md: # Install the development checkout"),
    "date-placeholder": ("docs/release-notes.md", "## 0.3.0 (", "## 0.3.0 (PUBLICATION_DATE)",
                         "the 0.3.0 heading carries 'PUBLICATION_DATE'"),
    "heading-still-prepared": ("docs/release-notes.md", "## 0.3.0 (", "## 0.3.0 (prepared, not published)",
                               "the 0.3.0 heading carries 'prepared, not published'"),
    "opening-edited": ("docs/release-notes.md", "Version 0.3.0, published on",
                       "Version 0.3.0, published on 2026-11-11, is the latest release; 0.2.0 was the first.",
                       "docs/release-notes.md: the opening paragraph is not the published form"),
    "compatibility-edited": ("docs/compatibility.md", "0.1.0, 0.2.0 and 0.3.0 are published",
                             "0.1.0 and 0.2.0 are published (0.2.0 on 2026-11-08). For the next",
                             "docs/compatibility.md: the version paragraph is not the published form"),
    "support-row-missing": ("docs/support.md", "| macOS 27 arm64, Python 3.11, uv 0.10.10 | Observed in release acceptance of the 0.3.0",
                            None, "docs/support.md: no row observes the 0.3.0 candidate"),
    "standing-line-gone": ("docs/development/candidate.md", "The artifact is `get_nick_done-0.1.0", "The artifact is a wheel.",
                           "standing entry matches no line: docs/development/candidate.md"),
    "release-link-old": ("docs/installation.md", "[v0.3.0 release]", "[the release page](https://example.org).",
                         "docs/installation.md: does not contain 'releases/tag/v0.3.0)'"),
}


@pytest.mark.parametrize("name", sorted(MUTATIONS))
def test_a_page_left_in_the_earlier_state_is_reported(tmp_path, name):
    root = copy_tree(tmp_path)
    assert tool.subject_version(root) == "0.3.0"
    assert tool.problems(root) == []   # the control: the copy is clean
    relative, start, new, expected = MUTATIONS[name]
    _replace_line(root, relative, start, new)
    found = tool.problems(root)
    assert any(expected in problem for problem in found), found


# release-0.4.0 RC-03: the 0.4.0 publication found a page whose "where this ships" note the tool did
# not report. Each text below is such a note; the first is that page's, as it stood.
PREPARED_GUIDANCE = {
    "receipts": (
        "    Identity decisions, fixed reference lists and separate reading and checking\n"
        "    models are on `main` after 0.3.1. They are not in a published package yet.\n"
        "    Install GND from a checkout of the repository to run this chapter.\n"),
    "phrase-alone": "These commands are not in a published package yet.\n",
    "main-after-a-tag": "The receipts example is on `main` after 0.3.1.\n",
    "main-without-code-marks": "The receipts example is on main after 0.3.1.\n",
    "any-published": "The example is not in any published wheel.\n",
    # A run of spaces or a tab inside a line reads as one space (RW3 review r1, F3).
    "double-space": "These commands are not in a  published package yet.\n",
    "tab": "These commands are not in a\tpublished package yet.\n",
}


@pytest.mark.parametrize("name", sorted(PREPARED_GUIDANCE))
def test_prepared_install_guidance_is_reported(tmp_path, name):
    root = copy_tree(tmp_path)
    assert tool.problems(root) == []   # the control: the copy is clean
    page = root / "docs/expense/05-receipts.md"
    page.parent.mkdir(parents=True)
    page.write_text("# Receipts\n\n" + PREPARED_GUIDANCE[name] + "\nThe chapter starts here.\n", encoding="utf-8")
    found = tool.problems(root)
    assert found and all(problem.startswith("stale: docs/expense/05-receipts.md: ") for problem in found), found


def test_standing_install_guidance_is_not_reported(tmp_path):
    """Pages that say how to use unreleased work in general stay true after any release."""
    root = copy_tree(tmp_path)
    page = root / "docs/how-to/trip-budget.md"
    page.parent.mkdir(parents=True)
    page.write_text(
        "# Trip budget\n\n"
        "shows: GND from PyPI, or from a checkout for unreleased work on `main`, and\n"
        "the published package otherwise.\n\n"
        "To use unreleased work on `main`,\ninstall it from a checkout of the repository instead:\n\n"
        "The catalog on `main` holds three components. After 2 runs it holds four.\n", encoding="utf-8")
    assert tool.problems(root) == []


@pytest.mark.parametrize("sentence, standing", [
    ("were validated. Every release through 0.4.0 (0.1.0, 0.2.0, 0.3.0 and 0.4.0) was", True),
    ("were validated. Every release through 0.5.0 (0.1.0, 0.2.0, 0.3.0, 0.4.0 and 0.5.0) was", True),
    ("were validated. Every release through 0.2.0 (0.1.0 and 0.2.0) was", True),
    ("were validated. Every release through 0.4.0 was", False),   # the list is part of the sentence
    ("were validated. Every release through 0.4.0 (0.1.0, 0.2.0, 0.3.0 and 0.4.0) is", False),
])
def test_the_token_route_sentence_stands_for_any_list_of_releases(tmp_path, sentence, standing):
    root = copy_tree(tmp_path)
    edit(root, "docs/releasing.md",
         "were validated. Every release through 0.4.0 (0.1.0, 0.2.0, 0.3.0 and 0.4.0) was", sentence)
    found = tool.problems(root)
    assert (found == []) is standing, found


def test_a_longer_version_and_a_first_version_statement_are_not_stale(tmp_path):
    root = copy_tree(tmp_path)
    edit(root, "docs/index.md", "uv tool install get-nick-done==0.3.0", (
        "uv tool install get-nick-done==0.3.0\n"
        "GND supports Ossie ontology version `0.2.0.dev0`.\n"
        "The feature is in GND 0.2.0 and later."))
    assert tool.problems(root) == []
    assert tool._mentions("see 0.2.0.", "0.2.0") and tool._mentions("tag v0.2.0", "0.2.0")
    assert not tool._mentions("version 0.2.0.dev0", "0.2.0") and not tool._mentions("10.2.0", "0.2.0")


def test_a_recorded_replay_is_not_a_page_but_a_page_saying_the_same_is_stale(tmp_path):
    """induction-skill IS2: a replay is rendered verbatim from a recording, so its words are the recorded agent's
    and say nothing about a release."""
    root = copy_tree(tmp_path)
    words = "the model file is newer than the labels."
    (root / "docs/assets/replays").mkdir(parents=True)
    (root / "docs/assets/replays/replays.json").write_text(json.dumps({"example-run-1": {"title": "A run"}}),
                                                           encoding="utf-8")
    (root / "docs/assets/replays/example-run-1.txt").write_text(f"claude: {words}\n", encoding="utf-8")
    assert tool.problems(root) == []
    edit(root, "docs/index.md", "uv tool install get-nick-done==0.3.0", f"uv tool install get-nick-done==0.3.0\n{words}")
    assert tool.problems(root) == [f"stale: docs/index.md: {words}"]


@pytest.mark.parametrize("arguments, message", [
    ({"date": "11/11/2026"}, "is not YYYY-MM-DD"),
    ({"built": "4C07C0E6"}, "eight lowercase hexadecimal digits"),
    ({"built": "4c07c0e"}, "eight lowercase hexadecimal digits"),
    ({"profile": "macOS | Python"}, "one line of text"),
    ({"profile": " "}, "one line of text"),
])
def test_a_malformed_publication_input_changes_nothing(tmp_path, arguments, message):
    root = prepare_next(copy_tree(tmp_path))
    snapshot = {relative: (root / relative).read_bytes() for relative in PAGES}
    with pytest.raises(tool.ReleaseTextError, match=re.escape(message)):
        tool.publish(root, **{**PUBLISH, **arguments})
    assert snapshot == {relative: (root / relative).read_bytes() for relative in PAGES}


@pytest.mark.parametrize("page", ["support", "notes", "compatibility"])
def test_a_page_the_tool_cannot_work_from_stops_publication_with_the_tree_untouched(tmp_path, page):
    root = prepare_next(copy_tree(tmp_path))
    if page == "support":
        _replace_line(root, "docs/support.md", f"| Any profile, prepared {NEXT} package", None)
    elif page == "notes":
        _replace_line(root, "docs/release-notes.md", f"## {NEXT} (", "## Unreleased: something")
    else:
        edit(root, "docs/compatibility.md", "Distribution `get-nick-done`, import and CLI", "The distribution and CLI")
    snapshot = {relative: (root / relative).read_bytes() for relative in PAGES}
    with pytest.raises(tool.ReleaseTextError):
        tool.publish(root, **PUBLISH)
    assert snapshot == {relative: (root / relative).read_bytes() for relative in PAGES}


def test_command_exit_codes(tmp_path, capsys):
    root = prepare_next(copy_tree(tmp_path))
    base = ["--root", str(root)]
    assert tool.main([*base, "check"]) == 0
    assert f"{NEXT} is not in RELEASED" in capsys.readouterr().out
    publish = [*base, "publish", "--built", PUBLISH["built"], "--profile", PUBLISH["profile"], "--date"]
    assert tool.main([*publish, "soon"]) == 2
    assert "is not YYYY-MM-DD" in capsys.readouterr().err
    assert tool.main([*publish, PUBLISH["date"]]) == 1   # the hand-written lines are listed
    out = capsys.readouterr().out
    assert out.startswith("changed 8 files: ") and "stale: docs/marketplace-plugins.md" in out
    assert tool.main([*base, "check"]) == 1
    capsys.readouterr()
    published = copy_tree(tmp_path / "tagged")
    assert tool.main(["--root", str(published), "check"]) == 0
    assert "no page describes the state before" in capsys.readouterr().out


def test_authored_files_beside_the_replays_are_still_pages(tmp_path):
    """Review phase-IS2-r1 F12: the whole replay folder was left out, titles and authored files included."""
    root = copy_tree(tmp_path)
    folder = root / "docs/assets/replays"
    folder.mkdir(parents=True)
    title = "Install GND 0.2.0, the next release."
    (folder / "replays.json").write_text(json.dumps({"example-run-1": {"title": title}}), encoding="utf-8")
    (folder / "guide.md").write_text("This is not published yet.\n", encoding="utf-8")
    problems = tool.problems(root)
    assert any("replays.json" in p for p in problems) and any("guide.md" in p for p in problems)
