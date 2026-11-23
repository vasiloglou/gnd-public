"""Review round pr-207-r1, finding F3: a definition's lines are the parser's lines."""
from __future__ import annotations

import ast

import pytest
from support.definition_source import definition_source

#: Characters ``str.splitlines`` breaks a line at and the Python parser does not.
INSIDE_A_LINE = {
    "vertical-tab": "\x0b", "form-feed": "\x0c", "file-separator": "\x1c",
    "group-separator": "\x1d", "record-separator": "\x1e", "next-line": "\x85",
    "line-separator": " ", "paragraph-separator": " ",
}


def _only(source: str) -> ast.AST:
    (node,) = ast.parse(source).body
    return node


@pytest.mark.parametrize("character", INSIDE_A_LINE.values(), ids=INSIDE_A_LINE)
def test_a_character_the_parser_keeps_inside_a_line_does_not_cut_the_definition(character):
    source = f'def example():\n    """a{character}b"""\n    return 1\n'
    assert definition_source(source, _only(source)) == source


def test_the_definition_ends_at_its_last_line_and_starts_at_its_first_decorator():
    before = "import functools\n\n"
    definition = "@functools.cache\n@staticmethod\ndef example():\n    return 1\n"
    source = before + definition + "\n\nOTHER = 2\n"
    node = ast.parse(source).body[1]
    assert definition_source(source, node) == definition
    assert definition_source(source, node, decorators=False) == "def example():\n    return 1\n"


def test_a_last_line_without_a_line_break_is_kept_as_it_is():
    source = "def example():\n    return 1"
    assert definition_source(source, _only(source)) == source
