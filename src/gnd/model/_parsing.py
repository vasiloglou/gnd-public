"""Bounded model-document parsing, shared by model loading and include resolution.

Moved verbatim from ``gnd.model._validation`` (main CI repair, 2026-11-16) so that
module stays under its RF6 size ceiling. ``_validation`` and ``gnd.model``
re-export both names, and ``parse_model_document`` keeps its public
``gnd.model`` identity.
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
import re
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from functools import wraps
from pathlib import Path
from typing import Any, TypeVar

from ruamel.yaml import YAML

from gnd.documents import MAX_YAML_EVENTS
from gnd.errors import ModelLoadError
from gnd.yaml_comments import configure_comment_scanner

MAX_MODEL_BYTES = 10 * 1024 * 1024  # 10 MB — same cap as population input

_F = TypeVar("_F", bound=Callable[..., Any])
# One dict per outermost parse scope: (sha256, strict JSON) -> [document, copy or None].
_PARSE_SCOPE: ContextVar[dict[tuple[str, bool], list[Any]] | None] = ContextVar(
    "gnd_model_parse_scope", default=None
)
_VERIFY = False


def _strict_json_source(source: str | Path) -> bool:
    """True when the source name selects the strict JSON reader. It is the only
    way the name changes a successful parse (GO1): any other name tries JSON for
    text that starts with ``{`` and falls back to YAML."""
    return Path(source).suffix == ".json"


def set_parse_scope_verify(enabled: bool) -> bool:
    """Switch the parse scope's write check on or off; return the old setting.

    With the check on, every scope keeps a type-preserving copy of each document
    it remembers and, when the outermost scope exits, raises AssertionError if a
    remembered document no longer equals its copy. Tests switch it on; it is off
    by default because the copy costs more than the parse it saves."""
    global _VERIFY
    previous, _VERIFY = _VERIFY, bool(enabled)
    return previous


def _same(left: Any, right: Any) -> bool:
    """Equal type and value at every node: ``1`` and ``True`` differ here."""
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        return list(left) == list(right) and all(_same(left[key], right[key]) for key in left)
    if isinstance(left, (list, tuple)):
        return len(left) == len(right) and all(map(_same, left, right))
    if left == right or (isinstance(left, float) and math.isnan(left) and math.isnan(right)):
        return True  # NaN is the one float unequal to itself
    # A round-trip YAML node without value equality (a tagged scalar) is compared
    # by its attributes, so a deep copy of an unchanged node is the same node.
    state = getattr(left, "__dict__", None)
    return state is not None and _same(state, getattr(right, "__dict__", None))


@contextmanager
def parse_scope() -> Iterator[None]:
    """Remember each document ``parse_model_document`` builds, for one public call.

    Keyed by the sha256 of the bytes and by whether the source name selects the
    strict JSON reader. Re-entrant: an inner scope shares the outer one. Dropped
    when the outermost scope exits. A parse that raises is not remembered. The
    remembered document is shared by reference and must not be written to; the
    write check of ``set_parse_scope_verify`` holds that in tests."""
    if _PARSE_SCOPE.get() is not None:
        yield
        return
    remembered: dict[tuple[str, bool], list[Any]] = {}
    token = _PARSE_SCOPE.set(remembered)
    try:
        yield
    finally:
        _PARSE_SCOPE.reset(token)
        changed = [key for key, (document, snapshot) in remembered.items()
                   if snapshot is not None and not _same(document, snapshot)]
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
    remembered = _PARSE_SCOPE.get()
    if remembered is None or len(data) > MAX_MODEL_BYTES:
        return _parse_model_document(data, source=source)
    key = (hashlib.sha256(data).hexdigest(), _strict_json_source(source))
    if key not in remembered:
        document = _parse_model_document(data, source=source)
        remembered[key] = [document, copy.deepcopy(document) if _VERIFY else None]
    return remembered[key][0]


def _parse_model_document(data: bytes, *, source: str | Path) -> Any:
    from ruamel.yaml.events import AliasEvent

    if len(data) > MAX_MODEL_BYTES:
        raise ModelLoadError("model exceeds the 10 MiB input cap")
    text = data.decode("utf-8")
    if re.search(r"(?m)[|>][-+0-9]{0,2}[ \t]*(?:#.*)?$", text) is None:
        text = text.rstrip()
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
        for count, event in enumerate(configure_comment_scanner(YAML(typ="safe")).parse(text), 1):
            if count > MAX_YAML_EVENTS or isinstance(event, AliasEvent):
                raise ModelLoadError("model YAML alias/event guard refused input")
        doc = configure_comment_scanner(YAML(typ="rt")).load(text)
    return doc

parse_model_document.__module__ = "gnd.model"
