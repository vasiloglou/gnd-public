"""The ``---``-fenced YAML frontmatter reader/writer (plan 03-01).

GND has never had a frontmatter parser (RESEARCH §1.3 item 7, grep-confirmed
across ``src/gnd/``), and it may not grow one as a PACKAGE: ``pyproject.toml``
freezes the base install at three dependencies and a fourth reds
``tests/test_packaged_skills.py::test_base_dependency_set_is_frozen`` against
``FROZEN_BASE_DEPENDENCIES = {"jsonschema", "pydantic", "ruamel-yaml"}`` (G-20).
So this module is built on the already-pinned ``ruamel.yaml.YAML(typ="safe")``,
the ``gnd.model`` idiom, and is deliberately small: split on the fences, load the
block with the safe loader, demand a mapping.

The prior art copied here is this repository's own ``.planning/**/*-PLAN.md``
frontmatter — a flat mapping of scalars and short lists, read and written by
hand. Nothing richer is needed and nothing richer is offered.

The document is UNTRUSTED committed metadata, so both bounds that
``gnd.extract.manifest`` and ``gnd.model`` apply are applied here:

- :data:`MAX_DOCUMENT_BYTES` is checked by ``stat()`` BEFORE the read (T-03-03).
  Reading and then measuring is not a cap — the hostile document is already
  resident by the time its size is known.
- the parse-event stream is walked for aliases before any node is constructed
  (T-03-04). ``gnd.model.yaml_stream_guard_error``'s own docstring records why
  the byte cap is not sufficient on its own: ruamel's safe loader expands
  anchors without limit, so a well-under-cap billion-laughs block exhausts
  memory during load. A 1 MB cap as the SOLE mitigation would be a bound that
  cannot fail for the attack it exists to stop.
"""

from __future__ import annotations

import io
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML, YAMLError

from gnd.model import MAX_YAML_EVENTS

__all__ = [
    "MAX_DOCUMENT_BYTES",
    "FrontmatterError",
    "read_frontmatter",
    "render_frontmatter",
]

#: Byte cap on a frontmatter-bearing document read. A SPEC.md or CONCLUSIONS.md
#: carries a handful of ids, one-line questions and short prose — 1 MB is
#: generous headroom, and the cap is what keeps a hostile 10 GB "spec" from
#: being slurped before validation (the MAX_MANIFEST_BYTES posture, T-03-03).
MAX_DOCUMENT_BYTES = 1 * 1024 * 1024

#: The fence line. Exactly three dashes on a line of their own, the form this
#: repository's own PLAN/SUMMARY documents already use.
_FENCE = "---"


class FrontmatterError(Exception):
    """A document could not be read, was unfenced, or its block was not a mapping.

    Loud by design. Returning an empty mapping for an unfenced document would
    make a SPEC.md that declares nothing read as a spec with nothing wrong — the
    gate-cannot-fail shape this phase exists to refuse.
    """


def _alias_issue(block: str) -> str | None:
    """The ``gnd.model.yaml_stream_guard_error`` rule applied to a block STRING.

    The shipped guard takes a path because it guards whole files; a frontmatter
    block is a slice of one, so the rule (not the code) is what is reused. Same
    two rejections, same budget constant imported from ``gnd.model`` so there is
    one number rather than two that can drift.
    """
    from ruamel.yaml.events import AliasEvent

    yaml = YAML(typ="safe")
    for count, event in enumerate(yaml.parse(io.StringIO(block)), start=1):
        if count > MAX_YAML_EVENTS:
            return (
                f"the frontmatter block exceeds the {MAX_YAML_EVENTS} parse-event "
                f"budget for untrusted input"
            )
        if isinstance(event, AliasEvent):
            return (
                f"the frontmatter block uses an anchor/alias ('*{event.anchor}') — "
                f"aliases are rejected for untrusted input (alias-amplification "
                f"defense, T-03-04)"
            )
    return None


def _split(text: str, path: Path) -> tuple[str, str]:
    """The fenced block and the body, or raise :class:`FrontmatterError`."""
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != _FENCE:
        raise FrontmatterError(
            f"{path} does not open with a '{_FENCE}' frontmatter fence; a document "
            f"without declared frontmatter is refused, never read as an empty one"
        )
    for index in range(1, len(lines)):
        if lines[index].strip() == _FENCE:
            return "".join(lines[1:index]), "".join(lines[index + 1 :])
    raise FrontmatterError(
        f"{path} has no closing '{_FENCE}' fence; an unterminated frontmatter "
        f"block is refused rather than read to end-of-file"
    )


def read_frontmatter(path: str | Path) -> tuple[dict[str, Any], str]:
    """Return ``(mapping, body)`` for a fenced document, or raise.

    Order is load-bearing: ``stat()`` cap, then read, then alias guard, then
    parse. Every step before the parse exists because the document is untrusted.
    """
    file_path = Path(path)
    try:
        size = file_path.stat().st_size
    except OSError as error:
        raise FrontmatterError(f"{file_path} could not be read: {error}") from error
    if size > MAX_DOCUMENT_BYTES:
        raise FrontmatterError(
            f"{file_path} is {size} bytes, over the {MAX_DOCUMENT_BYTES}-byte cap "
            f"for untrusted frontmatter input (T-03-03)"
        )
    try:
        text = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        raise FrontmatterError(f"{file_path} could not be read: {error}") from error

    block, body = _split(text, file_path)

    try:
        issue = _alias_issue(block)
    except (YAMLError, ValueError, RecursionError) as error:
        raise FrontmatterError(
            f"{file_path} has an unparseable frontmatter block: {error}"
        ) from error
    if issue is not None:
        raise FrontmatterError(f"{file_path}: {issue}")

    try:
        loaded = YAML(typ="safe").load(block)
    except (YAMLError, ValueError, RecursionError) as error:
        raise FrontmatterError(
            f"{file_path} has an unparseable frontmatter block: {error}"
        ) from error
    if not isinstance(loaded, dict):
        raise FrontmatterError(
            f"{file_path}'s frontmatter block is {type(loaded).__name__}, not a "
            f"mapping; a sequence, a scalar or an empty block declares no fields "
            f"and is refused rather than coerced"
        )
    return dict(loaded), body


def render_frontmatter(mapping: dict[str, Any], body: str) -> str:
    """Render ``mapping`` as a fenced block above ``body``, byte-deterministically.

    Keys are sorted and the result ends in a newline, so two renders of one
    mapping agree to the byte regardless of the caller's insertion order (the
    ``cli.py`` canonical-JSON discipline). ``gnd exp init`` writes a COMMITTED
    artifact; a render that varied by key order would produce diff noise
    indistinguishable from a real edit.
    """
    yaml = YAML(typ="safe")
    yaml.default_flow_style = False
    yaml.allow_unicode = True
    yaml.width = 4096
    stream = io.StringIO()
    yaml.dump({key: mapping[key] for key in sorted(mapping)}, stream)
    block = stream.getvalue()
    if not block.endswith("\n"):
        block += "\n"
    if not body.endswith("\n"):
        body += "\n"
    return f"{_FENCE}\n{block}{_FENCE}\n\n{body}"
