"""Explicit, bounded in-process reuse ownership. Never an admission authority.

Only completed transactions publish a candidate generation. Unit signatures
contain ordered typed inputs and evaluator policy; a key or clone failure misses
safely. The old public evaluators do not activate this state by default.
"""

from __future__ import annotations

import asyncio
import dataclasses
import math
import sys
from collections import Counter
from contextlib import contextmanager
from contextvars import ContextVar
from threading import Lock, get_ident
from types import BuiltinFunctionType, CodeType, FunctionType, MappingProxyType

from gnd.branches import capture_branches, record_branch
from gnd.documents import Model
from gnd.extension_preparation import fingerprint
from gnd.model import derivation_classifications, derivation_dependencies
from gnd.model_index import independent_index_scope

MAX_NODES = 100_000
MAX_DEPTH = 64
ENTRY_METADATA_BYTES = 1024  # conservative allowance for record and both index slots
_ACTIVE: ContextVar[tuple | None] = ContextVar("gnd_incremental_state", default=None)


class ReuseRefused(ValueError):
    def __init__(self, reason):
        self.reason = reason
        super().__init__(reason)


class _Unsupported(Exception):
    pass


def _children(value):
    kind = type(value)
    if kind in (dict, MappingProxyType):
        return (item for pair in value.items() for item in pair)
    if kind in (tuple, list, frozenset):
        return value
    if dataclasses.is_dataclass(value) and kind.__module__.startswith("gnd."):
        return (getattr(value, f.name) for f in dataclasses.fields(value))
    raise _Unsupported


def _measure(value, limit):
    """Bound work before cloning; count shared objects once and reject cycles."""
    seen, active = set(), set()
    nodes, total = 0, 0

    def walk(item, depth):
        nonlocal nodes, total
        nodes += 1
        if nodes > MAX_NODES or depth > MAX_DEPTH:
            raise _Unsupported
        identity = id(item)
        if identity in active:
            raise _Unsupported
        if identity in seen:
            return
        seen.add(identity)
        kind = type(item)
        if isinstance(item, (FunctionType, BuiltinFunctionType, CodeType, type)):
            total += 8  # borrowed module/code/type handle; never traverse globals
            return
        total += sys.getsizeof(item)
        if kind is MappingProxyType:
            if len(item) > MAX_NODES:
                raise _Unsupported
            total += sys.getsizeof(dict(item))
        if dataclasses.is_dataclass(item) and hasattr(item, "__dict__"):
            total += sys.getsizeof(item.__dict__)
        if total > limit:
            raise _Unsupported
        if item is None or kind in (str, int, bool):
            return
        if kind is float:
            if not math.isfinite(item):
                raise _Unsupported
            return
        active.add(identity)
        try:
            for child in _children(item):
                walk(child, depth + 1)
        finally:
            active.remove(identity)

    try:
        walk(value, 0)
        return total
    except (TypeError, ValueError, OverflowError, RecursionError, _Unsupported):
        return None


def _clone(value):
    memo = {}

    def clone(item):
        kind = type(item)
        if item is None or kind in (str, bool, int, float):
            return item
        if id(item) in memo:
            return memo[id(item)]
        if kind is list:
            result = []
            memo[id(item)] = result
            result.extend(clone(v) for v in item)
        elif kind in (dict, MappingProxyType):
            result = {clone(k): clone(v) for k, v in item.items()}
            if kind is MappingProxyType:
                result = MappingProxyType(result)
        elif kind is tuple:
            result = tuple(clone(v) for v in item)
        elif kind is frozenset:
            result = frozenset(clone(v) for v in item)
        elif dataclasses.is_dataclass(item) and kind.__module__.startswith("gnd."):
            result = dataclasses.replace(
                item,
                **{
                    f.name: clone(getattr(item, f.name)) for f in dataclasses.fields(item) if f.init
                },
            )
        else:
            raise _Unsupported
        memo[id(item)] = result
        return result

    return clone(value)


def _policy(value, *, guards=None, mutable=None):
    seen = set()
    nodes = 0

    def walk(item, depth):
        nonlocal nodes
        nodes += 1
        if nodes > MAX_NODES or depth > MAX_DEPTH:
            raise _Unsupported
        if isinstance(item, (FunctionType, BuiltinFunctionType, type, CodeType)):
            if guards is not None and isinstance(item, FunctionType):
                guards.append((item, item.__code__))
            return (type(item), item, item.__code__ if isinstance(item, FunctionType) else None)
        if type(item) is tuple:
            # Refuse shared tuple DAGs: both expansion and tuple hashing would
            # otherwise revisit their descendants exponentially.
            if len(item) > 1000 or (item and id(item) in seen):
                raise _Unsupported
            seen.add(id(item))
            return tuple(walk(v, depth + 1) for v in item)
        if _measure(item, 32 * 1024 * 1024) is None:
            raise _Unsupported
        key = fingerprint(item)
        if mutable is not None and type(item) not in (type(None), bool, int, float, str, bytes):
            mutable.append(item)
        if key is None:
            raise _Unsupported
        return key

    return walk(value, 0)


@dataclasses.dataclass(frozen=True, slots=True)
class _PreparedPolicy:
    authority: object
    key: object
    guards: tuple
    mutable: tuple
    mutable_key: object


_DIAGNOSTICS = (
    "session_calls", "session_fresh_calls", "extension_context_calls",
    "extension_context_fallbacks", "constraint_calls", "constraint_fallbacks",
)


@dataclasses.dataclass(frozen=True, slots=True)
class _Entry:
    signature: tuple
    value: object
    branches: tuple
    rows: int
    size: int


@dataclasses.dataclass(frozen=True, slots=True)
class _Committed:
    entries: dict
    binding: object = None
    binding_size: int = 0
    generation: int = 0
    sequence: int = 0


def _owner():
    try:
        task = asyncio.current_task()
    except RuntimeError:
        task = None
    return get_ident(), id(task) if task is not None else None


def active_state():
    authority = _ACTIVE.get()
    if authority is None:
        return None
    state, owner, _nonce = authority
    return state if state._authority is authority and owner == _owner() else None


def affected_heads(model, changed):
    """One reverse walk across existing positive/negative/aggregate edges."""
    with independent_index_scope(model) as index:
        if index is None:
            raise ReuseRefused("uncacheable-model")
        facts = list(index.iter_fact_types_shared())
        document = {"fact_types": facts}
        if any(
            f.get("derivation") in ("derived", "semiderived")
            and type(f.get("derivation_rule")) is not dict for f in facts
        ) or any(not row.complete for row in derivation_classifications(document)):
            raise ReuseRefused("incomplete-dependencies")
        graph = derivation_dependencies(document)
        known = {str(f["id"]) for f in facts}
    if type(changed) not in (set, frozenset, tuple, list) or len(changed) > MAX_NODES:
        raise ReuseRefused("incomplete-dependencies")
    if any(type(item) is not str for item in changed):
        raise ReuseRefused("incomplete-dependencies")
    changed = set(changed)
    if changed - known:
        return frozenset(graph)
    reverse = {}
    for head, dependencies in graph.items():
        for dependency in dependencies:
            reverse.setdefault(dependency, set()).add(head)
    pending = list(changed)
    dirty = set(changed)
    while pending:
        for head in reverse.get(pending.pop(), ()):
            if head not in dirty:
                dirty.add(head)
                pending.append(head)
    return frozenset(dirty.intersection(graph))


class ReuseState:
    """One committed generation plus a transaction-local candidate, never history."""

    def __init__(self, model, *, max_rows=100_000, max_bytes=32 * 1024 * 1024):
        if not isinstance(model, Model):
            raise TypeError("ReuseState requires a loaded Model")
        if any(type(v) is not int or v < 0 for v in (max_rows, max_bytes)):
            raise ValueError("cache-limit")
        self._model = model
        self._max_rows = max_rows
        self._max_bytes = max_bytes
        self._closed = False
        self._lock = Lock()
        self._committed = _Committed({})
        self._candidate = {}
        self._authority = None
        self._prior = {}
        self._disabled = False
        self._abort = False
        self._stats = Counter(dict.fromkeys(_DIAGNOSTICS, 0), hits=0, misses=0, bypasses=0, lookups=0)

    @property
    def _entries(self):
        return self._committed.entries

    @property
    def _binding(self):
        return self._committed.binding

    @property
    def _binding_size(self):
        return self._committed.binding_size

    def owns_model(self, model):
        return self._model is model and active_state() is self

    @contextmanager
    def transaction(self, model, *, options=(), sequence=None):
        if self._closed:
            raise ReuseRefused("closed")
        if not self._lock.acquire(blocking=False):
            raise ReuseRefused("busy")
        try:
            if self._closed:
                raise ReuseRefused("closed")
            if sequence is not None and (type(sequence) is not int or
                                         not 1 <= sequence <= 1_000_000 or
                                         sequence != self._committed.sequence + 1):
                raise ReuseRefused("attempt must be the next sequential feedback attempt")
            if model is not self._model:
                raise ReuseRefused("model-object")
            with independent_index_scope(model) as index:
                option_key = fingerprint(options) if _measure(options, self._max_bytes) is not None else None
                binding = (index.digest if index else None, option_key)
                binding_size = _measure(binding, self._max_bytes)
                self._disabled = binding[0] is None or option_key is None or binding_size is None
                if binding == self._binding:
                    binding = self._binding
                self._working_binding_size = (binding_size or 0) + (
                    self._binding_size if binding is not self._binding else 0
                )
                if self._working_binding_size + sum(v.size for v in self._entries.values()) > self._max_bytes:
                    self._disabled = True
                if self._disabled:
                    option_key = None
                    binding = None
                    binding_size = 0
                    self._working_binding_size = self._binding_size
                self._prior = (
                    self._entries if binding == self._binding and not self._disabled else {}
                )
                self._candidate = {}
                self._abort = False
                self._authority = (self, _owner(), object())
                token = _ACTIVE.set(self._authority)
                try:
                    yield self
                    previous = self._committed
                    next_sequence = previous.sequence if sequence is None else sequence
                    if not self._abort:
                        committed = _Committed(
                            {} if self._disabled else self._candidate,
                            None if self._disabled else binding,
                            0 if self._disabled else binding_size,
                            previous.generation + 1, next_sequence,
                        )
                    else:
                        committed = dataclasses.replace(previous, sequence=next_sequence)
                    # One publication point for all persistent session state.
                    self._committed = committed
                finally:
                    self._authority = None
                    _ACTIVE.reset(token)
                    self._candidate = {}
                    self._prior = {}
        finally:
            self._lock.release()

    def discard(self):
        if active_state() is not self:
            raise ReuseRefused("not-active")
        self._abort = True

    def note(self, event):
        """Bounded out-of-band event diagnostics, never semantic feedback."""
        if active_state() is not self:
            raise ReuseRefused("not-active")
        if event not in _DIAGNOSTICS:
            raise ValueError("unknown diagnostic event")
        self._stats[event] += 1

    def prepare_policy(self, policy):
        """Normalize once; preserve live guards and exact transaction authority."""
        if active_state() is not self:
            raise ReuseRefused("not-active")
        guards, mutable = [], []
        key = mutable_key = None
        try:
            key = _policy(policy, guards=guards, mutable=mutable)
            mutable_key = fingerprint(tuple(mutable))
            if mutable_key is None or _measure(key, self._max_bytes) is None:
                key = None
        except (TypeError, ValueError, OverflowError, RecursionError, _Unsupported):
            key = None
        return _PreparedPolicy(self._authority, key, tuple(guards), tuple(mutable), mutable_key)

    def reuse(self, namespace, unit, snapshot, calculate, *, policy=(), rows=0):
        if self._closed:
            raise ReuseRefused("closed")
        if active_state() is not self:
            raise ReuseRefused("not-active")
        self._stats["lookups"] += 1
        key = None
        try:
            if (
                self._disabled
                or type(namespace) is not str
                or _measure(snapshot, self._max_bytes) is None
            ):
                raise _Unsupported
            unit_key = fingerprint(unit)
            shape = fingerprint(snapshot)
            if unit_key is None or shape is None:
                raise _Unsupported
            key = (namespace, unit_key)
            if isinstance(policy, _PreparedPolicy):
                if (policy.authority is not self._authority or policy.key is None
                        or any(function.__code__ is not code for function, code in policy.guards)
                        or fingerprint(policy.mutable) != policy.mutable_key):
                    raise _Unsupported
                policy_key = policy.key
            else:
                policy_key = _policy(policy)
            signature = (policy_key, getattr(calculate, "__code__", calculate), shape)
            hash(signature)
            previous = self._candidate.get(key, self._prior.get(key))
            if previous is not None and previous.signature == signature:
                result = _clone(previous.value)
                self._candidate[key] = previous
                for branch in previous.branches:
                    record_branch(branch)
                self._stats["hits"] += 1
                return result
        except (TypeError, ValueError, OverflowError, RecursionError, _Unsupported):
            self._stats["bypasses"] += 1
            if key is not None:
                self._candidate.pop(key, None)
            return calculate()
        self._stats["misses"] += 1
        with capture_branches() as branches:
            value = calculate()
        try:
            count = rows(value) if callable(rows) else rows
        except Exception:  # noqa: BLE001 -- metadata must not alter full evaluation
            self._stats["bypasses"] += 1
            self._candidate.pop(key, None)
            return value
        measured = _measure(
            (key, signature, value, tuple(branches)), max(0, self._max_bytes - ENTRY_METADATA_BYTES)
        )
        if measured is None or type(count) is not int or count < 0:
            self._candidate.pop(key, None)
            self._stats["bypasses"] += 1
            return value
        try:
            private = _clone(value)
        except (TypeError, ValueError, OverflowError, RecursionError, _Unsupported):
            self._stats["bypasses"] += 1
            self._candidate.pop(key, None)
            return value
        stored_branches = tuple(sorted(branches))
        measured = _measure(
            (key, signature, private, stored_branches),
            max(0, self._max_bytes - ENTRY_METADATA_BYTES),
        )
        if measured is None:
            self._stats["bypasses"] += 1
            self._candidate.pop(key, None)
            return value
        entry = _Entry(signature, private, stored_branches, count, measured + ENTRY_METADATA_BYTES)
        proposed = dict(self._candidate)
        proposed[key] = entry
        # Existing committed entries still occupy memory even on a cold model/options change.
        retained = {id(v): v for v in [*self._entries.values(), *proposed.values()]}
        if (
            sum(v.size for v in retained.values()) + self._working_binding_size > self._max_bytes
            or sum(v.rows for v in retained.values()) > self._max_rows
        ):
            self._disabled = True
            self._candidate = {}
            self._stats["bypasses"] += 1
        else:
            self._candidate = proposed
        return value

    def reset(self):
        if self._closed:
            raise ReuseRefused("closed")
        if not self._lock.acquire(blocking=False):
            raise ReuseRefused("busy")
        try:
            if self._closed:
                raise ReuseRefused("closed")
            self._committed = dataclasses.replace(
                self._committed, entries={}, binding=None, binding_size=0)
        finally:
            self._lock.release()

    def close(self):
        if not self._lock.acquire(blocking=False):
            raise ReuseRefused("busy")
        try:
            self._committed = dataclasses.replace(
                self._committed, entries={}, binding=None, binding_size=0)
            self._closed = True
        finally:
            self._lock.release()

    def stats(self):
        return dict(
            self._stats,
            generation=self._committed.generation,
            entries=len(self._entries),
            rows=sum(v.rows for v in self._entries.values()),
            bytes=self._binding_size + sum(v.size for v in self._entries.values()),
        )
