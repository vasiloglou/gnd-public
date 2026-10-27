"""Model documents as plain JSON values (evolve-loading follow-up, IK4-Q3, IKE-Q2).

One walk, shared by evolve and recovery verify, over a document that
``gnd.model.parse_model_document`` built. A separate home inside the
``gnd.model`` package; it imports nothing from ``gnd``.
"""

from __future__ import annotations

from typing import Any


class ModelValueError(ValueError):
    """A model value outside the JSON data model, named by path and kind."""

    def __init__(self, path: str, kind: str) -> None:
        super().__init__(f"{path} holds a {kind}")
        self.path = path
        self.kind = kind


_CORE_TAGS = frozenset(
    f"tag:yaml.org,2002:{name}" for name in ("str", "int", "float", "bool", "null", "map", "seq")
)


def json_document(document: Any, *, refuse: bool = True, encodable: bool = False) -> dict[str, Any]:
    """The parsed model document as plain Python, in one walk over every value.

    Evidence that is canonical JSON (evolve's digests, the recovery
    verbalization) needs a model inside the JSON data model. With ``refuse``,
    the first value outside it raises ``ModelValueError`` with its path and
    kind. Without it, such values are kept as the safe YAML reader gives them,
    for callers that never digest them (discover writes a dated candidate as
    block YAML).

    ``encodable`` narrows the refusal to what ``json.dumps`` itself cannot write,
    for callers that render the loaded model with it (the verbalizer, recovery
    verify): a tuple, an ordered map and a tagged collection are written as a
    list or a map there, so they pass; a tagged scalar of any tag does not."""
    import datetime
    import math

    from ruamel.yaml.comments import CommentedOrderedMap, CommentedSet, TaggedScalar

    def outside(path: str, kind: str) -> ModelValueError:
        return ModelValueError(path or "the model", kind)

    def walk(value: Any, path: str) -> Any:
        tag = getattr(getattr(value, "tag", None), "value", None)
        named = f"tag {tag}".replace("tag:yaml.org,2002:", "!!")
        if isinstance(value, TaggedScalar):
            if not refuse or (tag == "tag:yaml.org,2002:str" and not encodable):
                return str(value.value)
            raise outside(path, named)
        # The round-trip reader keeps a scalar tag on a collection that the safe
        # reader refused (``!!str {b: 1}``); only the collection's own tag passes.
        own = "tag:yaml.org,2002:map" if isinstance(value, dict) else "tag:yaml.org,2002:seq"
        if tag is not None and refuse and not encodable and (tag not in _CORE_TAGS or (
                isinstance(value, (dict, list)) and tag != own)):
            raise outside(path, named)
        if isinstance(value, CommentedOrderedMap) and refuse and not encodable:
            raise outside(path, "tag !!omap")
        if isinstance(value, dict):
            plain = {}
            for key, item in value.items():
                if not isinstance(key, str) and refuse:
                    raise outside(path, "non-string key")
                plain[key if not isinstance(key, str) else str(key)] = walk(
                    item, f"{path}.{key}" if path else str(key)
                )
            return plain
        if isinstance(value, list) or (encodable and isinstance(value, tuple)):
            return [walk(item, f"{path}[{index}]") for index, item in enumerate(value)]
        if isinstance(value, bool) or value is None:
            return value
        if isinstance(value, str):
            return str(value)
        if isinstance(value, int):
            return int(value)
        if isinstance(value, float):
            if not math.isfinite(value) and refuse:
                raise outside(path, "non-finite float")
            return float(value)
        if not refuse:
            if isinstance(value, CommentedSet):
                return set(value)
            if isinstance(value, datetime.datetime):
                # As the safe reader gives it: a plain datetime, keeping its zone,
                # which discover's YAML writer can represent (review B1).
                return datetime.datetime(
                    value.year, value.month, value.day, value.hour, value.minute,
                    value.second, value.microsecond, tzinfo=value.tzinfo,
                )
            return value
        if isinstance(value, tuple):
            raise outside(path, "tag !!pairs")
        if isinstance(value, datetime.datetime):
            raise outside(path, "timestamp")
        if isinstance(value, datetime.date):
            raise outside(path, "date")
        if isinstance(value, bytes):
            raise outside(path, "binary")
        if isinstance(value, (set, CommentedSet)):
            raise outside(path, "set")
        raise outside(path, type(value).__name__)

    return walk(document, "")
