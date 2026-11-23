"""Review round pr-207-r1, finding F4: the model parser and line endings.

``parse_model_document`` strips a document's trailing whitespace unless it
holds a block scalar, whose final line break is content. It used to find a
block scalar with a pattern over the text, which saw only headers that end in
LF: a model saved with CRLF lost the last line break of its closing block
scalar, and a plain scalar or a comment that ends in ``>`` or ``|`` kept
trailing blank lines no other document keeps. The YAML reader's own events
answer the question for every line ending.
"""
from __future__ import annotations

import pytest

from gnd.model import parse_model_document
from gnd.model._parsing import _snapshot

LINE_ENDINGS = pytest.mark.parametrize("ending", ["\n", "\r\n", "\r"], ids=["LF", "CRLF", "CR"])


def _parse(text: str, ending: str = "\n"):
    return parse_model_document(text.replace("\n", ending).encode("utf-8"), source="probe.orm.yaml")


@LINE_ENDINGS
@pytest.mark.parametrize("text, expected", [
    ("note: |\n  hello\n", "hello\n"),
    ("note: |  \n  hello\n", "hello\n"),
    ("note: |  # the reviewer's comment\n  hello\n", "hello\n"),
    ("note: >\n  hello\n", "hello\n"),
    ("note: |+\n  hello\n\n", "hello\n\n"),
    ("note: |2\n   hello\n", " hello\n"),
    ("note: |-\n  hello\n", "hello"),
    ("items:\n  - |\n    hello\n", None),
], ids=["clip", "header-spaces", "header-comment", "folded", "keep", "indent", "strip", "in-a-list"])
def test_a_closing_block_scalar_keeps_its_line_break(text, expected, ending):
    document = _parse(text, ending)
    value = document["items"][0] if expected is None else document["note"]
    assert str(value) == ("hello\n" if expected is None else expected)


@LINE_ENDINGS
@pytest.mark.parametrize("text", [
    "note: |\n  hello\n",
    "note: |\n  hello\nlast: 1\n\n\n",
    "a: 1\n\n\n",
    "note: a -> b >\nlast: 1\n\n\n",
    "note: 1  # a | b |\n\n\n",
    'note: "x |"\n\n',
], ids=["block-last", "block-then-key", "no-block", "plain-ends-gt", "comment-ends-bar", "quoted-ends-bar"])
def test_a_document_reads_the_same_under_every_line_ending(text, ending):
    assert _snapshot(_parse(text, ending)) == _snapshot(_parse(text))


@pytest.mark.parametrize("text", [
    "note: a -> b >\nlast: 1\n",
    "note: 1  # a | b |\n",
    'note: "x |"\n',
    "a: 1\n",
], ids=["plain-ends-gt", "comment-ends-bar", "quoted-ends-bar", "no-block"])
def test_trailing_blank_lines_are_dropped_when_no_block_scalar_holds_them(text):
    assert _snapshot(_parse(text + "\n\n \n")) == _snapshot(_parse(text))
