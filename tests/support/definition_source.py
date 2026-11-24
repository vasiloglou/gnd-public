"""The source lines of one top-level definition, as the Python parser counts lines.

Three pinning tests and one builder each digest a definition's lines. They cut
them with ``str.splitlines``, which also breaks a line at a form feed, at
U+2028 and at five more characters that the parser keeps inside a line, so a
definition holding one of them was cut short (review round pr-207-r1, F3).
The lines are cut where the parser cuts them: at LF, at CR and at CRLF, and
nowhere else.
"""

from __future__ import annotations

import ast
import io


def definition_source(source: str, node: ast.AST, *, decorators: bool = True) -> str:
    """The whole lines ``node`` spans in ``source``, each with its line break:
    from its first decorator when ``decorators`` is set, else from its own
    first line, through its last line."""
    start = node.lineno
    if decorators:
        start = min([start, *(decorator.lineno for decorator in getattr(node, "decorator_list", []))])
    # newline="" reads universal line breaks and leaves each one as it is.
    lines = list(io.StringIO(source, newline=""))
    return "".join(lines[start - 1:node.end_lineno])
