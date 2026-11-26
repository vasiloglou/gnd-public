"""Bounded model-document parsing, shared by model loading and include resolution.

Moved verbatim from ``gnd.model._validation`` (main CI repair, 2026-11-16) so that
module stays under its RF6 size ceiling. ``_validation`` and ``gnd.model``
re-export both names, and ``parse_model_document`` keeps its public
``gnd.model`` identity.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from functools import wraps
from pathlib import Path
from typing import Any, TypeVar

from ruamel.yaml import YAML

from gnd.documents import MAX_YAML_EVENTS
from gnd.errors import ModelLoadError
from gnd.input_policy import checked_yaml_depth
from gnd.yaml_comments import configure_comment_scanner

MAX_MODEL_BYTES = 10 * 1024 * 1024  # 10 MB — same cap as population input

#: The two block scalar styles, as the YAML reader's scalar events name them.
_BLOCK_STYLES = ("|", ">")

_F = TypeVar("_F", bound=Callable[..., Any])


class _Scope:
    """One outermost parse scope: (sha256, strict JSON) -> [document, snapshot or None].

    ``open`` turns False when the scope exits, so a context copied while it was
    open (``contextvars.copy_context``, ``asyncio.to_thread``) cannot reuse it
    afterwards: it sees no scope and opens its own."""

    __slots__ = ("documents", "open")

    def __init__(self) -> None:
        self.documents: dict[tuple[str, bool], list[Any]] = {}
        self.open = True


_PARSE_SCOPE: ContextVar[_Scope | None] = ContextVar("gnd_model_parse_scope", default=None)
_VERIFY = False


def _strict_json_source(source: str | Path) -> bool:
    """True when the source name selects the strict JSON reader. It is the only
    way the name changes a successful parse (GO1): any other name tries JSON for
    text that starts with ``{`` and falls back to YAML."""
    return Path(source).suffix == ".json"


def set_parse_scope_verify(enabled: bool) -> bool:
    """Switch the parse scope's write check on or off; return the old setting.

    With the check on, every scope keeps a snapshot of each document it
    remembers and, when the outermost scope exits, raises AssertionError if the
    document's snapshot then differs. Tests switch it on; it is off by default
    because the snapshot costs more than the parse it saves."""
    global _VERIFY
    previous, _VERIFY = _VERIFY, bool(enabled)
    return previous


def _snapshot(document: Any) -> str:
    """The document as the round-trip YAML writer spells it: every key and value
    with its type, tag, anchor and comment, so any write into it changes this
    text and an unchanged document gives the same text twice."""
    import io

    stream = io.StringIO()
    YAML(typ="rt").dump(document, stream)
    return stream.getvalue()


def _active() -> _Scope | None:
    scope = _PARSE_SCOPE.get()
    return scope if scope is not None and scope.open else None


@contextmanager
def parse_scope() -> Iterator[None]:
    """Remember each document ``parse_model_document`` builds, for one public call.

    Keyed by the sha256 of the bytes and by whether the source name selects the
    strict JSON reader. Re-entrant: an inner scope shares the outer one. Dropped
    when the outermost scope exits, also for contexts copied from it. A parse
    that raises is not remembered. The remembered document is shared by
    reference and must not be written to; the write check of
    ``set_parse_scope_verify`` holds that in tests."""
    if _active() is not None:
        yield
        return
    scope = _Scope()
    token = _PARSE_SCOPE.set(scope)
    try:
        yield
    finally:
        _PARSE_SCOPE.reset(token)
        scope.open = False
        remembered, scope.documents = scope.documents, {}
        changed = [key for key, (document, snapshot) in remembered.items()
                   if snapshot is not None and _snapshot(document) != snapshot]
        if changed:
            raise AssertionError(f"a remembered model document was written to: {changed}")


def parse_scoped(function: _F) -> _F:
    """Run ``function`` inside a parse scope: the decorator ``gnd evolve`` uses."""
    @wraps(function)
    def run_scoped(*args: Any, **kwargs: Any) -> Any:
        with parse_scope():
            return function(*args, **kwargs)
    return run_scoped  # type: ignore[return-value]


def parse_model_document(data: bytes, *, source: str | Path) -> Any:
    """Parse one bounded model buffer exactly as ``load_model_bytes`` does: strict
    JSON for a ``.json`` source, otherwise the alias/event guard and then the
    round-trip YAML reader. The document is returned unvalidated.

    Inside a ``parse_scope`` the same bytes under the same reader return the
    document already built, shared and not copied."""
    scope = _active()
    if scope is None or len(data) > MAX_MODEL_BYTES:
        return _parse_model_document(data, source=source)
    key = (hashlib.sha256(data).hexdigest(), _strict_json_source(source))
    if key not in scope.documents:
        document = _parse_model_document(data, source=source)
        scope.documents[key] = [document, _snapshot(document) if _VERIFY else None]
    return scope.documents[key][0]


def _parse_model_document(data: bytes, *, source: str | Path) -> Any:
    from ruamel.yaml.events import AliasEvent, ScalarEvent

    if len(data) > MAX_MODEL_BYTES:
        raise ModelLoadError("model exceeds the 10 MiB input cap")
    text = data.decode("utf-8")
    doc = None
    strict = _strict_json_source(source)
    if strict or text.lstrip().startswith("{"):
        from gnd.errors import PopulationLoadError
        from gnd.population import _parse_document_bytes

        try:
            doc = _parse_document_bytes(data, suffix=".json", source=str(source))
        except PopulationLoadError as error:
            from gnd.input_policy import InputRefusal

            if (strict
                    or not isinstance(error.__cause__, json.JSONDecodeError)
                    or isinstance(error.__cause__, InputRefusal)):
                raise ModelLoadError("model JSON input refused") from error
            # A YAML flow mapping may start with an unquoted key.
    if doc is None:
        # A document's trailing whitespace is content only inside a block scalar,
        # so it is dropped unless the reader's own events show one. The events
        # know a block scalar under every line ending; a pattern over the text
        # knew it only under LF.
        stripped = text.rstrip()
        block_scalar = False
        depth = 0
        for count, event in enumerate(configure_comment_scanner(YAML(typ="safe")).parse(stripped), 1):
            if count > MAX_YAML_EVENTS or isinstance(event, AliasEvent):
                raise ModelLoadError("model YAML alias/event guard refused input")
            depth = checked_yaml_depth(depth, event, error_type=ModelLoadError)
            block_scalar = block_scalar or (isinstance(event, ScalarEvent) and event.style in _BLOCK_STYLES)
        doc = configure_comment_scanner(YAML(typ="rt")).load(text if block_scalar else stripped)
    return doc

parse_model_document.__module__ = "gnd.model"
