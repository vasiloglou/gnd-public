"""RF7 shared JSON, YAML and ISO datetime input restrictions."""
from __future__ import annotations

import json
import math
import re
from datetime import datetime

from ruamel.yaml import YAML
from ruamel.yaml.events import AliasEvent, CollectionEndEvent, CollectionStartEvent

MAX_BYTES = 10 * 1024 * 1024
MAX_DEPTH = 64
_DATETIME = re.compile(
    r'[0-9]{4}-[0-9]{2}-[0-9]{2}T(?:[01][0-9]|2[0-3]):[0-5][0-9]'
    r'(?::[0-5][0-9](?:\.[0-9]{1,6})?)?(?:Z|[+-](?:[01][0-9]|2[0-3]):[0-5][0-9])?'
)


def _text(raw):
    if isinstance(raw, (bytes, bytearray)):
        if len(raw) > MAX_BYTES:
            raise ValueError('JSON input exceeds byte cap')
        # Preserve the standard decoder's UTF BOM/encoding interpretation.
        raw = bytes(raw).decode(json.detect_encoding(raw), 'surrogatepass')
    if not isinstance(raw, str):
        raise TypeError('JSON input must be str, bytes or bytearray')
    if len(raw.encode('utf-8', 'surrogatepass')) > MAX_BYTES:
        raise ValueError('JSON input exceeds byte cap')
    return raw


def _depth(text, idx):
    if text[idx:idx + 1] not in ('{', '['):
        return
    depth = 0
    quoted = escaped = False
    for char in text[idx:]:
        if quoted:
            if escaped:
                escaped = False
            elif char == '\\':
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
        elif char in '{[':
            depth += 1
            if depth > MAX_DEPTH:
                raise InputRefusal('JSON depth exceeds cap', text, idx)
        elif char in '}]':
            depth -= 1
            if depth == 0:
                return


class InputRefusal(json.JSONDecodeError):
    """Keep domain diagnostic messages independent of synthetic locations."""

    def __str__(self):
        return self.msg


class JSONDecoder(json.JSONDecoder):
    """Native decoder interface with one duplicate/finite/depth policy."""

    def __init__(self, **kwargs):
        pairs_hook = kwargs.pop('object_pairs_hook', None)
        object_hook = kwargs.pop('object_hook', None)
        float_hook = kwargs.pop('parse_float', None) or float
        constant_hook = kwargs.pop('parse_constant', None)

        def pairs(items):
            # Preserve domain-specific refusals from an existing rejecting hook.
            result = pairs_hook(items) if pairs_hook else dict(items)
            if len({key for key, _ in items}) != len(items):
                raise InputRefusal('duplicate JSON key', '', 0)
            return object_hook(result) if object_hook and not pairs_hook else result

        def number(token):
            result = float_hook(token)
            if not math.isfinite(float(token)):
                raise InputRefusal('nonfinite JSON number', '', 0)
            return result

        def constant(token):
            if constant_hook:
                constant_hook(token)
            raise InputRefusal('nonfinite JSON constant', '', 0)

        super().__init__(object_pairs_hook=pairs, parse_float=number,
                         parse_constant=constant, **kwargs)

    def raw_decode(self, text, idx=0):
        text = _text(text)
        _depth(text, idx)
        return super().raw_decode(text, idx)


def loads(raw, **kwargs):
    """Decode with native numeric types or caller hooks; refuse unsafe syntax."""
    return JSONDecoder(**kwargs).decode(_text(raw))


def load(handle, **kwargs):
    """Apply the byte cap to the read, before decoding or constructing nodes."""
    raw = handle.read(MAX_BYTES + 1)
    return loads(raw, **kwargs)


def guard_yaml(raw, *, max_bytes=MAX_BYTES, max_events=1_000_000, max_depth=MAX_DEPTH):
    """Reject amplification and over-budget input before constructing YAML nodes."""
    if isinstance(raw, str):
        data = raw.encode('utf-8')
    elif isinstance(raw, bytes):
        data = raw
    else:
        raise TypeError('YAML input must be text or bytes')
    if len(data) > max_bytes:
        raise ValueError('YAML byte cap exceeded')
    depth = 0
    for count, event in enumerate(YAML(typ='safe').parse(data), 1):
        if count > max_events:
            raise ValueError('YAML event cap exceeded')
        if isinstance(event, AliasEvent):
            raise ValueError('YAML alias refused')  # noqa: TRY004 -- input syntax refusal
        if isinstance(event, CollectionStartEvent):
            depth += 1
            if depth > max_depth:
                raise ValueError('YAML depth cap exceeded')
        elif isinstance(event, CollectionEndEvent):
            depth -= 1


def parse_datetime(value):
    """Parse the approved ASCII extended ISO grammar, retaining naive values."""
    if not isinstance(value, str) or _DATETIME.fullmatch(value) is None:
        raise ValueError('strict ISO datetime required')
    return datetime.fromisoformat(value[:-1] + '+00:00' if value.endswith('Z') else value)
