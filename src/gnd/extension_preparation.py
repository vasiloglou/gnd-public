"""Bounded ephemeral preparation for one admitted check evaluation."""
from __future__ import annotations

import math
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field, fields, is_dataclass
from enum import Enum
from typing import TypeVar, cast

from pydantic import BaseModel
from ruamel.yaml.comments import CommentedMap, CommentedSeq

from gnd.branches import capture_branches

MAX_FINGERPRINT_NODES = 2_000_000
MAX_FINGERPRINT_CHARACTERS = 16_000_000
MAX_PREPARED_CALCULATIONS = 8
Result = TypeVar("Result")


class _Unsupported(Exception):
    pass


@dataclass(slots=True)
class _Fingerprint:
    nodes: int = 0
    characters: int = 0
    active: set[int] = field(default_factory=set)
    node_limit: int | None = None
    character_limit: int | None = None

    def freeze(self, value: object, depth: int = 0) -> tuple:
        node_limit = MAX_FINGERPRINT_NODES if self.node_limit is None else self.node_limit
        character_limit = (MAX_FINGERPRINT_CHARACTERS if self.character_limit is None
                           else self.character_limit)
        if self.nodes >= node_limit or depth > 64:
            raise _Unsupported
        self.nodes += 1
        kind = type(value)
        if kind in (str, int, bool, float, type(None)):
            if kind is str:
                if len(value) > character_limit - self.characters:
                    raise _Unsupported
                self.characters += len(value)
            if kind is int:
                storage = max(1, (value.bit_length() + 7) // 8)
                if storage > character_limit - self.characters:
                    raise _Unsupported
                self.characters += storage
            if kind is float:
                if not math.isfinite(value):
                    raise _Unsupported
                return ("float", value.hex())
            return (kind.__name__, value)
        if isinstance(value, Enum):
            return ("enum", kind, self.freeze(value.value, depth+1))
        if (is_dataclass(value) and not isinstance(value, type)
                and kind.__module__.startswith("gnd.")):
            if id(value) in self.active:
                raise _Unsupported
            self.active.add(id(value))
            try:
                return ("record", kind, tuple(
                    (self.freeze(f.name, depth + 1), self.freeze(getattr(value, f.name), depth + 1))
                    for f in fields(value)
                ))
            finally:
                self.active.remove(id(value))
        if isinstance(value, BaseModel):
            if id(value) in self.active:
                raise _Unsupported
            self.active.add(id(value))
            try:
                return ("model", kind, tuple((self.freeze(name, depth+1),
                                              self.freeze(getattr(value, name), depth+1))
                                             for name in kind.model_fields))
            finally:
                self.active.remove(id(value))
        if kind not in (dict, list, tuple, CommentedMap, CommentedSeq) or id(value) in self.active:
            raise _Unsupported
        self.active.add(id(value))
        try:
            if kind in (dict, CommentedMap):
                return ("dict", tuple((self.freeze(k, depth+1), self.freeze(v, depth+1))
                                      for k, v in value.items()))
            container = "list" if kind in (list, CommentedSeq) else "tuple"
            return (container, tuple(self.freeze(v, depth+1) for v in value))
        finally:
            self.active.remove(id(value))


def fingerprint(value: object) -> tuple | None:
    try:
        return _Fingerprint().freeze(value)
    except (_Unsupported, TypeError, ValueError, AttributeError, RecursionError):
        return None


@dataclass(slots=True)
class _Prepared:
    value: object
    branches: tuple[str, ...]


@dataclass(slots=True)
class CalculationScope:
    model: object
    population: object
    records: dict[tuple, _Prepared] = field(default_factory=dict)
    nodes: int = 0
    characters: int = 0

    def calculate(
        self, key_identity: tuple, snapshot: object,
        calculate: Callable[[], Result], clone: Callable[[Result], Result | None],
        record: Callable[[str], str],
    ) -> Result:
        try:
            hash(key_identity)
        except TypeError:
            return calculate()
        remaining_nodes = MAX_FINGERPRINT_NODES - self.nodes
        remaining_characters = MAX_FINGERPRINT_CHARACTERS - self.characters
        if (remaining_nodes <= 0 or remaining_characters <= 0
                or len(self.records) >= MAX_PREPARED_CALCULATIONS):
            return calculate()
        shape = _Fingerprint(node_limit=remaining_nodes, character_limit=remaining_characters)
        key: tuple | None = None
        try:
            frozen = snapshot(shape.freeze) if callable(snapshot) else shape.freeze(snapshot)
            key = (key_identity, frozen)
        except (_Unsupported, TypeError, ValueError, RecursionError, AttributeError):
            pass
        finally:
            # Every visited shape is charged, including hits and failed attempts.
            self.nodes += shape.nodes
            self.characters += shape.characters
        if key is None:
            return calculate()
        prior = self.records.get(key)
        if prior is not None:
            result = clone(cast(Result, prior.value))
            if result is not None:
                for branch in prior.branches:
                    record(branch)
                return result
        with capture_branches() as branches:
            result = calculate()
        stored = clone(result)
        if stored is not None:
            self.records[key] = _Prepared(stored, tuple(sorted(branches)))
        return result


_SCOPE: ContextVar[CalculationScope | None] = ContextVar("gnd_calculation_scope", default=None)


def current_scope() -> CalculationScope | None:
    return _SCOPE.get()


@contextmanager
def calculation_scope(model: object, population: object) -> Iterator[CalculationScope]:
    current = current_scope()
    if current is not None and current.model is model and current.population is population:
        yield current
        return
    owned = CalculationScope(model, population)
    token = _SCOPE.set(owned)
    try:
        yield owned
    finally:
        _SCOPE.reset(token)
