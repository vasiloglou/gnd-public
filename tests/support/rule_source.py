"""What a rule function declares, read from its syntax tree.

Four tests read rule ids out of a rule's source text with a pattern that saw
double-quoted literals only, so ``rule_id='semantic:x'`` was invisible to them
(review round pr-207-r1, F1 and F2). The parser sees every spelling of a
literal, and it does not see a quoted id that only a comment mentions.
"""

from __future__ import annotations

import ast
import inspect
import textwrap
from collections.abc import Callable
from typing import Any

SEMANTIC_PREFIX = "semantic:"


def _nodes(function: Callable[..., Any]) -> list[ast.AST]:
    """Every node of the function, in source order."""
    tree = ast.parse(textwrap.dedent(inspect.getsource(function)))
    placed = [node for node in ast.walk(tree) if hasattr(node, "lineno")]
    return sorted(placed, key=lambda node: (node.lineno, node.col_offset))


def _text(node: ast.AST) -> str | None:
    return node.value if isinstance(node, ast.Constant) and isinstance(node.value, str) else None


def _once(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))


def keyword_literals(function: Callable[..., Any], name: str) -> list[str]:
    """Each string literal passed as the keyword ``name``, in source order, once."""
    return _once([text for node in _nodes(function)
                  if isinstance(node, ast.keyword) and node.arg == name
                  and (text := _text(node.value)) is not None])


def rule_id_arguments(function: Callable[..., Any]) -> list[str]:
    """Each string literal the function passes as ``rule_id=``, in source order, once."""
    return keyword_literals(function, "rule_id")


def computed_keyword(function: Callable[..., Any], name: str) -> bool:
    """True when the keyword ``name`` is passed anything other than a string literal."""
    return any(isinstance(node, ast.keyword) and node.arg == name and _text(node.value) is None
               for node in _nodes(function))


def semantic_literals(function: Callable[..., Any]) -> list[str]:
    """Each string literal in the function that names a semantic rule, in source
    order, once: an id passed directly, and an id held in a tuple, a list or a
    mapping the function loops over. The fixed part of an f-string is not an
    id, so it is left out."""
    nodes = _nodes(function)
    fragments = {id(part) for node in nodes if isinstance(node, ast.JoinedStr) for part in node.values}
    return _once([text for node in nodes
                  if id(node) not in fragments
                  and (text := _text(node)) is not None and text.startswith(SEMANTIC_PREFIX)])
