"""Exact runtime-only citation reader support; no Git/census/ledger instrument."""
from __future__ import annotations

import functools
import re
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from gnd.exp.frontmatter import FrontmatterError, read_frontmatter

REPO_ROOT = Path(__file__).resolve().parents[2]
PLANNING_ROOT = REPO_ROOT / ".gnd-planning"
_HEX64 = re.compile(r"^[0-9a-f]{64}$")

class PlanningTreeError(Exception):
    """A record is defective, as opposed to simply not being a record."""


@dataclass(frozen=True)
class Citation:
    """One ``path`` + ``sha256`` claim made by one record."""

    record: str
    line: int
    path: str
    digest: str


def _markdown_files(root: Path) -> list[Path]:
    if root.is_file():
        return [root]
    return sorted(
        path for path in root.rglob("*.md") if not _is_retained_baseline_source(path)
    )


def _is_retained_baseline_source(path: Path) -> bool:
    """Exclude source-tree copies nested inside retained evidence matrices."""
    parts = path.parts
    return "evidence" in parts and (
        "staging" in parts
        or any(
            parts[index : index + 2] == ("baseline", "source")
            for index in range(len(parts) - 1)
        )
    )


def _relative(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _citation_line(text: str, cited: str) -> int:
    """The 1-based line of the ``path:`` entry, for the failure message.

    ``read_frontmatter`` returns a mapping and drops line numbers, so this
    recovers one. A finding that cannot say where it is costs a reader the same
    search every time.
    """
    needle = re.compile(rf"""^\s*-?\s*path:\s*['"]?{re.escape(cited)}['"]?\s*$""")
    for number, line in enumerate(text.splitlines(), 1):
        if needle.match(line):
            return number
    return 0


def _safe_relative(cited: str, *, record: str) -> None:
    """Refuse a cited path that leaves the repository root.

    Runs BEFORE any git subprocess is constructed, not after -- a containment
    check downstream of the thing it protects is a report, not a guard.
    """
    if "\x00" in cited or "\\" in cited:
        raise PlanningTreeError(f"{record}: cited path contains a NUL or backslash: {cited!r}")
    if cited.startswith("/") or re.match(r"^[A-Za-z]:", cited):
        raise PlanningTreeError(f"{record}: cited path is absolute: {cited!r}")
    parts = cited.split("/")
    if any(part in ("", ".", "..") for part in parts):
        raise PlanningTreeError(f"{record}: cited path escapes the repository root: {cited!r}")


def _walk_frontmatter(node: Any, key: str) -> Iterable[tuple[str, Any, str]]:
    """Yield ``(path, sha256, key)`` for every mapping carrying a ``path``.

    Any key, at any depth. Scoping this to ``evidence:`` would drop a real
    unresolvable citation that lives under ``plans_reviewed:`` -- measured, not
    supposed (IF-P3b-9).
    """
    if isinstance(node, dict):
        if isinstance(node.get("path"), str):
            yield node["path"], node.get("sha256"), key
        for child_key, value in node.items():
            if isinstance(value, (dict, list)):
                yield from _walk_frontmatter(value, child_key)
    elif isinstance(node, list):
        for value in node:
            yield from _walk_frontmatter(value, key)


@dataclass(frozen=True)
class _Scan:
    citations: tuple[Citation, ...]
    digestless: int
    non_hex: tuple[str, ...]
    defects: tuple[str, ...]
    markdown_files: int
    frontmatter_documents: int
    keys: tuple[tuple[str, int], ...]


@functools.cache
def _scan(root: Path) -> _Scan:
    """Read the tree once, tolerantly, and report everything found.

    Tolerant on purpose: this is the survey. ``read_citations`` applies the
    strict policy on top, so the strict and tolerant readings can never
    disagree about what is in the tree.
    """
    citations: list[Citation] = []
    defects: list[str] = []
    non_hex: list[str] = []
    keys: dict[str, int] = {}
    digestless = 0
    files = _markdown_files(root)
    parsed = 0

    for path in files:
        record = _relative(path)
        try:
            mapping, _body = read_frontmatter(path)
        except FrontmatterError as error:
            # 101 of the tree's 167 markdown files are notes, panel outputs and
            # reviews that never open a frontmatter fence. Those are not
            # records. EVERYTHING ELSE the reader refuses -- an unclosed fence,
            # unparseable YAML, an alias bomb, a non-mapping block, undecodable
            # bytes, the byte cap -- is a DEFECT, because a fenced document we
            # cannot parse may carry citations, and skipping it would lose them
            # silently. The adversarial review reproduced exactly that loss
            # before this branch distinguished the two (IF-P3b-17).
            if " does not open with a " in str(error):
                continue
            defects.append(f"{record}: {error}")
            continue
        parsed += 1
        text = path.read_text(encoding="utf-8", errors="replace")
        for cited, digest, key in _walk_frontmatter(mapping, "<root>"):
            if digest is None:
                digestless += 1
                continue
            if not isinstance(digest, str):
                # An all-digit scalar is typed by YAML as an int, and an int
                # cannot carry a leading zero back out. A caller must be able to
                # reproduce a cited digest from the record's bytes, so the type
                # is refused rather than coerced.
                non_hex.append(
                    f"{record}: sha256 is a {type(digest).__name__}, not a string -- "
                    f"quote it so YAML does not retype it: {digest!r}"
                )
                continue
            if not _HEX64.match(digest):
                non_hex.append(
                    f"{record}: sha256 is present and is not 64 lowercase hex: {digest!r}"
                )
                continue
            try:
                _safe_relative(cited, record=record)
            except PlanningTreeError as error:
                defects.append(str(error))
                continue
            keys[key] = keys.get(key, 0) + 1
            citations.append(
                Citation(record=record, line=_citation_line(text, cited), path=cited, digest=digest)
            )

    return _Scan(
        citations=tuple(citations),
        digestless=digestless,
        non_hex=tuple(non_hex),
        defects=tuple(defects),
        markdown_files=len(files),
        frontmatter_documents=parsed,
        keys=tuple(sorted(keys.items())),
    )


@functools.cache
def read_citations(*, root: Path = PLANNING_ROOT) -> tuple[Citation, ...]:
    """Every citation in ``root``, or raise if any record is defective.

    Order is load-bearing and pinned by a two-fault case: the byte cap is
    reported before a malformed digest in the same document, because the cap is
    a refusal of the input and the digest is a judgement about its content.
    """
    scan = _scan(root)
    if scan.defects:
        raise PlanningTreeError(scan.defects[0])
    if scan.non_hex:
        raise PlanningTreeError(scan.non_hex[0])
    return scan.citations
