"""Bounded model-document parsing, shared by model loading and include resolution.

Moved verbatim from ``gnd.model._validation`` (main CI repair, 2026-11-16) so that
module stays under its RF6 size ceiling. ``_validation`` and ``gnd.model``
re-export both names, and ``parse_model_document`` keeps its public
``gnd.model`` identity.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML

from gnd.documents import MAX_YAML_EVENTS
from gnd.errors import ModelLoadError
from gnd.yaml_comments import configure_comment_scanner

MAX_MODEL_BYTES = 10 * 1024 * 1024  # 10 MB — same cap as population input


def parse_model_document(data: bytes, *, source: str | Path) -> Any:
    """Parse one bounded model buffer exactly as ``load_model_bytes`` does: strict
    JSON for a ``.json`` source, otherwise the alias/event guard and then the
    round-trip YAML reader. The document is returned unvalidated."""
    from ruamel.yaml.events import AliasEvent

    if len(data) > MAX_MODEL_BYTES:
        raise ModelLoadError("model exceeds the 10 MiB input cap")
    text = data.decode("utf-8")
    if re.search(r"(?m)[|>][-+0-9]{0,2}[ \t]*(?:#.*)?$", text) is None:
        text = text.rstrip()
    doc = None
    if Path(source).suffix == ".json" or text.lstrip().startswith("{"):
        from gnd.errors import PopulationLoadError
        from gnd.population import _parse_document_bytes

        try:
            doc = _parse_document_bytes(data, suffix=".json", source=str(source))
        except PopulationLoadError as error:
            from gnd.input_policy import InputRefusal

            if (Path(source).suffix == ".json"
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
