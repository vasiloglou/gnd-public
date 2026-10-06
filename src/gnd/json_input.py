"""Shared bounded JSON intake; domain readers own shape and error adapters."""

from __future__ import annotations

import json  # noqa: F401 -- historical compatibility binding
import math
from decimal import Decimal

from gnd import input_policy as _rf7_input

MAX_JSON_BYTES = 10 * 1024 * 1024


class JsonInputRefusal(ValueError):
    def __init__(self, reason: str, message: str):
        self.reason = reason
        super().__init__(message[:256])


def _refuse(reason, message):
    raise JsonInputRefusal(reason, message)


def bounded_json(raw: bytes, *, max_bytes=MAX_JSON_BYTES):
    if not isinstance(raw, bytes):
        _refuse("shape", "proposal must be bytes")
    if len(raw) > max_bytes:
        _refuse("limit", "proposal exceeds byte cap")
    depth = 0
    quoted = escaped = False
    for char in raw:
        if quoted:
            if escaped:
                escaped = False
            elif char == 92:
                escaped = True
            elif char == 34:
                quoted = False
        elif char == 34:
            quoted = True
        elif char in (91, 123):
            depth += 1
            if depth > 64:
                _refuse("shape", "JSON depth exceeds cap")
        elif char in (93, 125):
            depth -= 1

    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                _refuse("shape", "duplicate JSON key")
            result[key] = value
        return result

    def number(token, convert):
        if sum(c.isdigit() for c in token) > 128:
            _refuse("shape", "numeric digits exceed cap")
        try:
            value = convert(token)
        except ArithmeticError:
            _refuse("shape", "unsupported numeric magnitude")
        if isinstance(value, float) and not math.isfinite(value):
            _refuse("shape", "nonfinite number")
        return value

    try:
        doc = _rf7_input.loads(
            raw,
            object_pairs_hook=pairs,
            parse_int=lambda x: number(x, int),
            parse_float=lambda x: number(x, Decimal),
            parse_constant=lambda x: _refuse("shape", "nonfinite JSON"),
        )
    except (ValueError, UnicodeError, RecursionError) as error:
        if isinstance(error, JsonInputRefusal):
            raise
        _refuse("shape", "malformed JSON")
    validate_json_value(doc)
    return doc


def validate_json_value(doc):
    stack = [(doc, 0)]
    deepest = {}
    while stack:
        value, depth = stack.pop()
        if isinstance(value, (dict, list)):
            if isinstance(value, dict):
                for key in value:
                    if not isinstance(key, str):
                        _refuse("shape", "JSON objects require string keys")
            depth += 1
            if depth > 64:
                _refuse("shape", "JSON depth exceeds cap")
            identity = id(value)
            if depth <= deepest.get(identity, 0):
                continue
            deepest[identity] = depth
            children = [*value.keys(), *value.values()] if isinstance(value, dict) else value
            stack.extend((child, depth) for child in children)
        elif isinstance(value, str):
            try:
                size = len(value.encode())
            except UnicodeError:
                _refuse("shape", "scalar is not valid UTF-8")
            if size > 4096:
                _refuse("limit", "JSON scalar exceeds cap")
        elif type(value) in (int, float, Decimal):
            if type(value) is int and abs(value) >= 10**128:
                _refuse("shape", "nonfinite or over-limit number")
            token = str(value)
            if not Decimal(token).is_finite() or sum(c.isdigit() for c in token) > 128:
                _refuse("shape", "nonfinite or over-limit number")
        elif value is not None and type(value) is not bool:
            _refuse("shape", "JSON value required")
