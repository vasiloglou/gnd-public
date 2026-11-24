"""Read one section of a Markdown page, skipping fenced code blocks (reviewed-vocabulary-growth VG2, VG5)."""
from __future__ import annotations


def markdown_section(text: str, heading: str) -> str:
    """The lines under the ATX heading line HEADING, up to the next heading of its level or above.

    Fenced code blocks (a line opening with three or more backticks or tildes,
    indented at most three spaces, closed by a run of the same character at
    least as long) are skipped, so an example inside one is never read as the
    section (VG2 review r1, F4).
    """
    level = len(heading) - len(heading.lstrip("#"))
    fence = None
    taken: list[str] | None = None
    for line in text.splitlines(keepends=True):
        stripped = line.lstrip(" ")
        indent = len(line) - len(stripped)
        marker = stripped[:1]
        run = len(stripped) - len(stripped.lstrip(marker)) if marker in ("`", "~") else 0
        if fence is None and indent <= 3 and run >= 3:
            fence = (marker, run)
        elif fence is not None and indent <= 3 and marker == fence[0] and run >= fence[1] \
                and not stripped[run:].strip():
            fence = None
        elif fence is None and stripped.startswith("#"):
            hashes = len(stripped) - len(stripped.lstrip("#"))
            if line.rstrip("\n").rstrip() == heading:
                taken = [line]
                continue
            if taken is not None and hashes <= level and stripped[hashes:hashes + 1] in (" ", "\n", ""):
                break
        if taken is not None:
            taken.append(line)
    if taken is None:
        raise AssertionError(f"no heading {heading!r} outside a fenced block")
    return "".join(taken)
