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


class Block:
    """One block of a Markdown page: ``paragraph`` (a list item included),
    ``table`` (``rows``: the cells of each body row), ``fence`` (``info``, the
    fence's info string, and ``text``, its literal content) or ``heading``.
    A paragraph's and a cell's ``text`` has its whitespace runs collapsed, so
    a reflowed sentence reads the same."""

    __slots__ = ("info", "kind", "rows", "text")

    def __init__(self, kind: str, text: str = "", *, rows: list[list[str]] | None = None, info: str = "") -> None:
        self.kind, self.text, self.rows, self.info = kind, text, rows or [], info


def _collapse(text: str) -> str:
    return " ".join(text.split())


def _cells(line: str) -> list[str]:
    """A table line's cells: optional outer pipes, padding stripped, ``\\|`` kept as a pipe."""
    body = line.strip()
    body = body.removeprefix("|")
    body = body[:-1] if body.endswith("|") and not body.endswith("\\|") else body
    cells, current, escaped = [], [], False
    for character in body:
        if escaped:
            current.append(character)
            escaped = False
        elif character == "\\":
            escaped = True
            current.append(character)
        elif character == "|":
            cells.append(_collapse("".join(current)))
            current = []
        else:
            current.append(character)
    cells.append(_collapse("".join(current)))
    return [cell.replace("\\|", "|") for cell in cells]


def _is_delimiter(line: str) -> bool:
    cells = _cells(line)
    return bool(cells) and all(cell and set(cell) <= set(":-") and "-" in cell for cell in cells)


def heading_text(line: str) -> tuple[int, str] | None:
    """An ATX heading line's level and text, its optional closing ``#`` run removed."""
    stripped = line.strip()
    if len(line) - len(line.lstrip(" ")) > 3 or not stripped.startswith("#"):
        return None
    level = len(stripped) - len(stripped.lstrip("#"))
    rest = stripped[level:]
    if level > 6 or (rest and not rest.startswith((" ", "\t"))):
        return None
    words = rest.strip().split(" ")
    if words and words[-1] and set(words[-1]) == {"#"}:
        words = words[:-1]
    return level, " ".join(words).strip()


def markdown_blocks(text: str) -> list[Block]:
    """The blocks of TEXT, in order. HTML comments are not content and are
    dropped; a fence keeps its lines verbatim."""
    blocks: list[Block] = []
    lines = text.splitlines()
    paragraph: list[str] = []

    def flush() -> None:
        if paragraph:
            blocks.append(Block("paragraph", _collapse(" ".join(paragraph))))
            paragraph.clear()

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.lstrip(" ")
        indent = len(line) - len(stripped)
        marker = stripped[:1]
        run = len(stripped) - len(stripped.lstrip(marker)) if marker in ("`", "~") else 0
        if indent <= 3 and run >= 3:
            flush()
            info, body, i = stripped[run:].strip(), [], i + 1
            while i < len(lines):
                closing = lines[i].lstrip(" ")
                closing_run = len(closing) - len(closing.lstrip(marker))
                if (len(lines[i]) - len(closing) <= 3 and closing.startswith(marker)
                        and closing_run >= run and not closing[closing_run:].strip()):
                    break
                body.append(lines[i])
                i += 1
            blocks.append(Block("fence", "\n".join(body), info=info))
            i += 1
            continue
        if stripped.startswith("<!--"):
            flush()
            while i < len(lines) and "-->" not in lines[i]:
                i += 1
            i += 1
            continue
        heading = heading_text(line)
        if heading is not None:
            flush()
            blocks.append(Block("heading", heading[1], info=str(heading[0])))
            i += 1
            continue
        if "|" in line and i + 1 < len(lines) and _is_delimiter(lines[i + 1]):
            flush()
            rows, i = [], i + 2
            while i < len(lines) and lines[i].strip() and "|" in lines[i]:
                rows.append(_cells(lines[i]))
                i += 1
            blocks.append(Block("table", rows=rows))
            continue
        if not line.strip():
            flush()
        elif stripped.startswith(("- ", "* ", "+ ")) or stripped[:1].isdigit() and ". " in stripped[:4]:
            flush()
            paragraph.append(stripped.split(" ", 1)[1] if " " in stripped else "")
        else:
            paragraph.append(line)
        i += 1
    flush()
    return blocks


def section_blocks(text: str, heading: str) -> list[Block]:
    """The blocks under the heading whose text is HEADING, up to the next
    heading of its level or above."""
    blocks = markdown_blocks(text)
    start = next((i for i, block in enumerate(blocks) if block.kind == "heading" and block.text == heading), None)
    if start is None:
        raise AssertionError(f"no heading {heading!r} outside a fenced block")
    level = int(blocks[start].info)
    end = next((i for i in range(start + 1, len(blocks))
                if blocks[i].kind == "heading" and int(blocks[i].info) <= level), len(blocks))
    return blocks[start + 1:end]
