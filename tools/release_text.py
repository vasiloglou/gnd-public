"""Publication-day text: move the pages from "prepared" to "published", and check them.

Issue 176. Each release used to adapt a shell check and three hand-made patches
from the previous one. This tool replaces both.

``check`` confirms that no page still describes the state before the declared
version was published. It reads the declared version from ``pyproject.toml``
and the published versions from ``RELEASED`` in ``tests/test_release_version.py``.
While the declared version is not in ``RELEASED`` it reports nothing: that
state belongs to the rules in ``tests/test_release_version.py``.

``publish`` makes the edits that are the same at every release: the install
pins, the release link and wheel name, the tag sentence, the compatibility
paragraph, the opening and the heading of the release notes, the support row
and ``RELEASED``. It then runs the check and lists what is left. Those lines
are the ones a person wrote for this release ("needs the development
checkout", "is prepared and not published"), and a person rewrites them.

    uv run python tools/release_text.py check
    uv run python tools/release_text.py publish --date 2026-11-11 --built 4c07c0e6 \\
        --profile "macOS 27 arm64, Python 3.11, uv 0.10.10"

Exit codes: 0 clean, 1 problems listed on standard output, 2 usage or input error.
"""
from __future__ import annotations

import argparse
import re
import sys
import textwrap
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

RELEASED_HOME = "tests/test_release_version.py"
NOTES = "docs/release-notes.md"
COMPATIBILITY = "docs/compatibility.md"
SUPPORT = "docs/support.md"
INSTALLATION = "docs/installation.md"
PLUGINS = "docs/marketplace-plugins.md"
PIN_FILES = ("README.md", INSTALLATION, "docs/index.md", PLUGINS)

VERSION = r"\d+\.\d+\.\d+"
RELEASED_LINE = re.compile(r"^RELEASED = \{([^}\n]*)\}$", re.MULTILINE)
HEADING = re.compile(rf"^## ({VERSION})(?: \((.*)\))?\s*$")
ISO_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
PIN = re.compile(rf"(get-nick-done==){VERSION}")
RELEASE_LINK = re.compile(
    rf"\[v{VERSION} release\]\(https://github\.com/vasiloglou/gnd-public/releases/tag/v{VERSION}\)")
WHEEL_NAME = re.compile(rf"get_nick_done-{VERSION}-py3-none-any\.whl")
TAG_SENTENCE = re.compile(rf"The `v{VERSION}` tag contains")

#: Wording that describes a version that is not published yet, or a placeholder
#: the publication was meant to fill.
STALE = re.compile(
    r"next release|not published|not signed off|prepared \d|newer than"
    r"|unreleased (?:feature|example)|development checkout|PUBLICATION_DATE",
    re.IGNORECASE)
#: The same, inside the published version's own section of the release notes.
STALE_IN_NOTES = re.compile(
    r"not published|not in any published|development checkout|from a checkout|PUBLICATION_DATE",
    re.IGNORECASE)

#: Lines that name an older version or use one of the phrases, and stay true.
#: Each entry is a file (``None`` for any file) and a pattern the whole line
#: must contain. An entry for a named file that no longer matches any line is
#: itself a problem, so the list cannot keep dead entries. An entry for any
#: file is a form of statement, which may have no instance at a given time.
STANDING = (
    ("docs/development/candidate.md", r"^The artifact is `get_nick_done-0\.1\.0-py3-none-any\.whl`\."),
    (PLUGINS, r"^not register the development checkout in the user's marketplace configuration\.$"),
    ("docs/releasing.md", r"^were validated\. Every release through 0\.3\.0 \(0\.1\.0, 0\.2\.0 and 0\.3\.0\) was$"),
    (SUPPORT, r"^\| [^|]+ \| Observed in Phase 3 acceptance of 0\.1\.0 \|$"),
    (SUPPORT, rf"^\| [^|]+ \| Observed in release acceptance of the {VERSION} candidate built from `[0-9a-f]{{8}}` \|$"),
    # A feature's first version stays true after later releases.
    (None, rf"\bGND {VERSION} (?:and|or) later\b"),
)

COMPATIBILITY_START = "Distribution `get-nick-done`, import and CLI `gnd` remain stable."


class ReleaseTextError(Exception):
    """An input the tool cannot work from."""


def version_key(version: str) -> tuple[int, ...]:
    return tuple(int(part) for part in version.split("."))


def declared_version(root: Path) -> str:
    return tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]


def released_versions(root: Path) -> list[str]:
    """The published versions, oldest first, from their one home in the tests."""
    match = RELEASED_LINE.search((root / RELEASED_HOME).read_text(encoding="utf-8"))
    if not match:
        raise ReleaseTextError(f"{RELEASED_HOME} has no `RELEASED = {{...}}` line")
    versions = re.findall(rf'"({VERSION})"', match.group(1))
    return sorted(set(versions), key=version_key)


def _fill(text: str) -> str:
    return textwrap.fill(text, width=80, break_long_words=False, break_on_hyphens=False)


def _listed(versions: list[str]) -> str:
    return versions[0] if len(versions) == 1 else ", ".join(versions[:-1]) + " and " + versions[-1]


def notes_opening(declared: str, date: str, released: list[str]) -> str:
    """The first paragraph of the release notes once `declared` is published."""
    older = sorted((v for v in released if v != declared), key=version_key, reverse=True)
    if not older:
        standing = "is the first release."
    elif len(older) == 1:
        standing = f"is the latest release; {older[0]} was the first."
    else:
        standing = f"is the latest release; {_listed(older)} came before it."
    return _fill(
        f"Version {declared}, published on {date}, {standing} Releases follow the "
        "[release procedure](releasing.md). Changes on `main` after a release are listed "
        "in an `Unreleased:` section until the next one.")


def compatibility_paragraph(declared: str, date: str, released: list[str]) -> str:
    """The first paragraph of the compatibility page once `declared` is published."""
    versions = sorted({*released, declared}, key=version_key)
    subject = f"Version {versions[0]} is" if len(versions) == 1 else f"Versions {_listed(versions)} are"
    return _fill(
        f"{COMPATIBILITY_START} {subject} published ({declared} on {date}). For the next "
        "version, confirm service ownership and that the version is still free before "
        "candidate freeze and again before any upload. Milestone numbers are not package versions.")


def support_row(declared: str, built: str, profile: str) -> str:
    return f"| {profile} | Observed in release acceptance of the {declared} candidate built from `{built}` |"


def _paragraphs(text: str) -> list[str]:
    return text.split("\n\n")


def _mentions(line: str, version: str) -> bool:
    """True when `line` names exactly `version`, not a longer one such as `0.3.0.dev0`."""
    return re.search(rf"(?<![\d.]){re.escape(version)}(?![\w]|\.\w)", line) is not None


def _standing(relative: str, line: str) -> int | None:
    for index, (name, pattern) in enumerate(STANDING):
        if name in (None, relative) and re.search(pattern, line):
            return index
    return None


def page_files(root: Path) -> list[str]:
    """README.md and every text file under docs/, except the release notes."""
    names = ["README.md"]
    for path in sorted((root / "docs").rglob("*")):
        relative = path.relative_to(root).as_posix()
        if path.is_file() and relative != NOTES:
            names.append(relative)
    return names


def stale_lines(root: Path, declared: str, released: list[str]) -> list[str]:
    """Lines that name an older version or use prepared-state wording and are not standing."""
    older = [v for v in released if v != declared]
    problems = []
    used = set()
    for relative in page_files(root):
        try:
            text = (root / relative).read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue  # an image or another binary asset
        if relative == COMPATIBILITY:
            # The generated paragraph names every published version; it is compared whole.
            text = "\n\n".join("" if p.startswith(COMPATIBILITY_START) else p for p in _paragraphs(text))
        for line in text.splitlines():
            if not (STALE.search(line) or any(_mentions(line, v) for v in older)):
                continue
            entry = _standing(relative, line)
            if entry is None:
                problems.append(f"stale: {relative}: {line.strip()}")
            else:
                used.add(entry)
    for index, (name, pattern) in enumerate(STANDING):
        if name is not None and index not in used:
            problems.append(f"standing entry matches no line: {name}: {pattern}")
    return problems


def notes_problems(root: Path, declared: str, released: list[str]) -> list[str]:
    text = (root / NOTES).read_text(encoding="utf-8")
    lines = text.splitlines()
    headings = [(i, m) for i, line in enumerate(lines) if (m := HEADING.match(line)) and m.group(1) == declared]
    if len(headings) != 1:
        return [f"{NOTES}: expected one `## {declared} (DATE)` heading, found {len(headings)}"]
    start, match = headings[0]
    date = match.group(2) or ""
    if not ISO_DATE.fullmatch(date):
        return [f"{NOTES}: the {declared} heading carries {date!r}, not a publication date"]
    problems = []
    paragraphs = _paragraphs(text)
    opening = notes_opening(declared, date, released)
    if len(paragraphs) < 2 or paragraphs[1] != opening:
        problems.append(f"{NOTES}: the opening paragraph is not the published form:\n{opening}")
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    problems.extend(
        f"stale: {NOTES}: {line.strip()}" for line in lines[start:end] if STALE_IN_NOTES.search(line))
    compatibility = (root / COMPATIBILITY).read_text(encoding="utf-8")
    expected = compatibility_paragraph(declared, date, released)
    if expected not in _paragraphs(compatibility):
        problems.append(f"{COMPATIBILITY}: the version paragraph is not the published form:\n{expected}")
    return problems


def presence_problems(root: Path, declared: str) -> list[str]:
    """The pins, the links and the support row name the declared version."""
    def text(relative):
        return (root / relative).read_text(encoding="utf-8")

    problems = []
    for relative in PIN_FILES:
        pins = set(re.findall(rf"get-nick-done==({VERSION}[\w.]*)", text(relative)))
        if pins != {declared}:
            problems.append(f"{relative}: pins {sorted(pins)}, expected only {declared}")
    for relative, needle in (
        (INSTALLATION, f"releases/tag/v{declared})"),
        (INSTALLATION, f"get_nick_done-{declared}-py3-none-any.whl"),
        (PLUGINS, f"The `v{declared}` tag contains"),
    ):
        if needle not in text(relative):
            problems.append(f"{relative}: does not contain {needle!r}")
    observed = re.compile(
        rf"^\| [^|]+ \| Observed in release acceptance of the {re.escape(declared)} candidate "
        r"built from `[0-9a-f]{8}` \|$", re.MULTILINE)
    support = text(SUPPORT)
    if not observed.search(support):
        problems.append(f"{SUPPORT}: no row observes the {declared} candidate")
    if re.search(r"no profile is observed for", support, re.IGNORECASE):
        problems.append(f"{SUPPORT}: a row still says no profile is observed")
    return problems


def problems(root: Path = ROOT) -> list[str]:
    """Everything that still describes the state before the declared version was published."""
    declared = declared_version(root)
    released = released_versions(root)
    if declared not in released:
        return []
    return [
        *presence_problems(root, declared),
        *notes_problems(root, declared, released),
        *stale_lines(root, declared, released),
    ]


def publish(root: Path, *, date: str, built: str, profile: str) -> list[str]:
    """Make the publication-day edits for the declared version. Return the files changed."""
    if not ISO_DATE.fullmatch(date):
        raise ReleaseTextError(f"--date {date!r} is not YYYY-MM-DD")
    if not re.fullmatch(r"[0-9a-f]{8}", built):
        raise ReleaseTextError(f"--built {built!r} is not eight lowercase hexadecimal digits")
    if not profile.strip() or "|" in profile or "\n" in profile:
        raise ReleaseTextError("--profile must be one line of text without `|`")
    declared = declared_version(root)
    released = sorted({*released_versions(root), declared}, key=version_key)

    def notes(text):
        lines = text.split("\n")
        found = [i for i, line in enumerate(lines) if (m := HEADING.match(line)) and m.group(1) == declared]
        if len(found) != 1:
            raise ReleaseTextError(f"{NOTES}: expected one heading for {declared}, found {len(found)}")
        lines[found[0]] = f"## {declared} ({date})"
        paragraphs = _paragraphs("\n".join(lines))
        if len(paragraphs) < 2 or not paragraphs[1].startswith("Version "):
            raise ReleaseTextError(f"{NOTES}: the paragraph after the title does not start with `Version `")
        paragraphs[1] = notes_opening(declared, date, released)
        return "\n\n".join(paragraphs)

    def compatibility(text):
        paragraphs = _paragraphs(text)
        found = [i for i, p in enumerate(paragraphs) if p.startswith(COMPATIBILITY_START)]
        if len(found) != 1:
            raise ReleaseTextError(f"{COMPATIBILITY}: expected one paragraph starting {COMPATIBILITY_START!r}")
        paragraphs[found[0]] = compatibility_paragraph(declared, date, released)
        return "\n\n".join(paragraphs)

    def support(text):
        row = support_row(declared, built, profile)
        version = re.escape(declared)
        observed = re.compile(
            rf"^\| [^|\n]+ \| Observed in release acceptance of the {version} candidate built from `[0-9a-f]{{8}}` \|$",
            re.MULTILINE)
        prepared = re.compile(
            rf"^\|[^|\n]*\b{version}\b[^|\n]*\|[^|\n]*[Nn]o profile is observed for {version}\b[^|\n]*\|$",
            re.MULTILINE)
        for pattern in (observed, prepared):
            if len(pattern.findall(text)) == 1:
                return pattern.sub(lambda _: row, text)
        raise ReleaseTextError(f"{SUPPORT}: no single row for {declared} to replace")

    def released_home(text):
        literal = ", ".join(f'"{v}"' for v in released)
        return RELEASED_LINE.sub(lambda _: f"RELEASED = {{{literal}}}", text, count=1)

    edits = [
        *((name, lambda text: PIN.sub(rf"\g<1>{declared}", text)) for name in PIN_FILES),
        (INSTALLATION, lambda text: RELEASE_LINK.sub(
            f"[v{declared} release](https://github.com/vasiloglou/gnd-public/releases/tag/v{declared})", text)),
        (INSTALLATION, lambda text: WHEEL_NAME.sub(f"get_nick_done-{declared}-py3-none-any.whl", text)),
        (PLUGINS, lambda text: TAG_SENTENCE.sub(f"The `v{declared}` tag contains", text)),
        (NOTES, notes),
        (COMPATIBILITY, compatibility),
        (SUPPORT, support),
        (RELEASED_HOME, released_home),
    ]
    # Every edit is computed before any file is written: a page the tool cannot
    # work from stops the publication with the tree untouched.
    original = {}
    texts = {}
    for relative, edit in edits:
        if relative not in texts:
            original[relative] = texts[relative] = (root / relative).read_text(encoding="utf-8")
        texts[relative] = edit(texts[relative])
    changed = [relative for relative in texts if texts[relative] != original[relative]]
    for relative in changed:
        (root / relative).write_text(texts[relative], encoding="utf-8")
    return changed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--root", type=Path, default=ROOT, help="the repository to read (default: this one)")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("check", help="list what still describes the state before publication")
    publisher = commands.add_parser("publish", help="make the publication-day edits, then check")
    publisher.add_argument("--date", required=True, help="the publication date, YYYY-MM-DD")
    publisher.add_argument("--built", required=True, help="the candidate's commit, eight hexadecimal digits")
    publisher.add_argument("--profile", required=True, help="the observed profile for the support row")
    arguments = parser.parse_args(argv)
    try:
        if arguments.command == "publish":
            changed = publish(arguments.root, date=arguments.date, built=arguments.built, profile=arguments.profile)
            print(f"changed {len(changed)} files" + (": " + ", ".join(changed) if changed else ""))
        found = problems(arguments.root)
    except (ReleaseTextError, OSError, KeyError, tomllib.TOMLDecodeError) as error:
        print(f"release_text: {error}", file=sys.stderr)
        return 2
    for line in found:
        print(line)
    declared = declared_version(arguments.root)
    if declared not in released_versions(arguments.root):
        print(f"{declared} is not in RELEASED: nothing to check before publication")
    elif not found:
        print(f"no page describes the state before {declared} was published")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
