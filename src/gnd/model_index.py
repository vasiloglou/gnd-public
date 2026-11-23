"""Detached model query snapshots with a bounded, content-keyed cache.

The cache marker is internal. It does not replace any public model identity.

Within one public call, ``index_scope`` reuses one index per ``Model`` object, so a hit
costs no dump, walk or hash. Invalidation rule (its one home): a scope lives for exactly
one public call and drops every entry on exit, so the next call recomputes the canonical
key and the content-keyed cache decides; a mutated model therefore never reuses a stale
index across calls, including an operations-only mutation the population marker does not
see. Inside a scope a ``Model`` object is assumed unchanged, because GND does not mutate
model content while serving a call. A nested scope joins the outer one.
"""
from __future__ import annotations

import hashlib
from collections import OrderedDict
from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from copy import deepcopy
from dataclasses import dataclass, field
from functools import wraps
from threading import RLock
from types import MappingProxyType
from typing import Any, Literal

from gnd import artifacts
from gnd import input_policy as _rf7_input
from gnd.address import positional_constraint_ref
from gnd.documents import Model
from gnd.model_queries import _identifying_id, _resolve_reference, _supertype_parents, primitive_for

_CACHE: OrderedDict[str, ModelIndex] = OrderedDict()
_LOCK = RLock()
_LIMIT = 32
#: id(model) -> (model, index) for the public call in progress; None outside any call.
#: Each entry keeps its model alive, so an id cannot be reused within the scope.
_SCOPE: ContextVar[dict[int, tuple[Model, ModelIndex]] | None] = ContextVar(
    'gnd_model_index_scope', default=None)
_SCOPE_LIMIT = 8


class _IndependentScope(dict):
    live = True

    def get(self, key, default=None):
        return super().get(key, default) if self.live else default

    def __setitem__(self, key, value):
        if self.live:
            super().__setitem__(key, value)


def scoped(function):
    """Run ``function`` inside an index scope: the decorator public entry points use."""
    @wraps(function)
    def run_scoped(*args, **kwargs):
        with index_scope():
            return function(*args, **kwargs)
    return run_scoped


@contextmanager
def index_scope() -> Iterator[None]:
    """Reuse one ModelIndex per Model object for the duration of one public call."""
    if _SCOPE.get() is not None:
        yield
        return
    token = _SCOPE.set({})
    try:
        yield
    finally:
        _SCOPE.reset(token)


@contextmanager
def independent_index_scope(model: Model) -> Iterator[ModelIndex | None]:
    """Own a fresh call scope even under a caller-held outer index scope.

    A cache-key failure yields None; the public evaluator still owns validation
    and error mapping. Nested ordinary entry points join this seeded scope.
    """
    scope = _IndependentScope()
    token = _SCOPE.set(scope)
    try:
        try:
            index = ModelIndex.for_model(model)
        except Exception:  # noqa: BLE001 -- reuse must not replace public admission/errors
            index = None
        yield index
    finally:
        scope.live = False
        scope.clear()
        _SCOPE.reset(token)


def cache_info() -> dict[str, int]:
    with _LOCK:
        return {'size': len(_CACHE), 'limit': _LIMIT}


@dataclass(frozen=True, slots=True)
class ModelIndex:
    """A retained snapshot: queries return detached values, never writable cache state."""

    digest: str | None
    _document: dict[str, Any] = field(repr=False, compare=False)
    _facts: dict[str, dict[str, Any]] = field(init=False, repr=False, compare=False)
    _objects: dict[str, dict[str, Any]] = field(init=False, repr=False, compare=False)
    #: The universe tables (VG1), built on first use: name -> read-only table.
    _tables: dict[str, Any] = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        document = deepcopy(self._document)
        object.__setattr__(self, '_document', document)
        facts = {}
        for row in document.get('fact_types') or []:
            if isinstance(row, dict):
                facts.setdefault(str(row.get('id')), row)
        # Reference primitive resolution historically uses the last duplicate id.
        objects = {str(row.get('id')): row for row in document.get('object_types') or []
                   if isinstance(row, dict) and row.get('id') is not None}
        object.__setattr__(self, '_facts', facts)
        object.__setattr__(self, '_objects', objects)
        object.__setattr__(self, '_tables', {})

    @classmethod
    def for_model(cls, model: Model) -> ModelIndex:
        if not isinstance(model, Model):
            raise TypeError('ModelIndex requires a Model')
        scope = _SCOPE.get()
        if scope is not None:
            entry = scope.get(id(model))
            if entry is not None and entry[0] is model:
                return entry[1]
        index = cls._for_model_uncached(model)
        if scope is not None:
            scope[id(model)] = (model, index)
            while len(scope) > _SCOPE_LIMIT:
                del scope[next(iter(scope))]
        return index

    @classmethod
    def _for_model_uncached(cls, model: Model) -> ModelIndex:
        document = model.model_dump(exclude={'warnings'}, warnings=False)
        try:
            pending = [document]
            containers = set()
            while pending:
                item = pending.pop()
                if isinstance(item, (dict, list)):
                    if id(item) in containers:
                        raise TypeError('repeated container is not cacheable')
                    containers.add(id(item))
                if isinstance(item, dict):
                    if any(not isinstance(key, str) for key in item):
                        raise TypeError('non-string mapping key is not cacheable')
                    pending.extend(item.values())
                elif isinstance(item, tuple):
                    raise TypeError('non-JSON tuple is not cacheable')
                elif isinstance(item, list):
                    pending.extend(item)
            key = hashlib.sha256(artifacts.canonical_json_bytes(document)).hexdigest()
        except (ValueError, TypeError, OverflowError, RecursionError):
            return cls(None, document)
        with _LOCK:
            cached = _CACHE.get(key)
            if cached is not None:
                _CACHE.move_to_end(key)
                return cached
            built = cls(key, document)
            _CACHE[key] = built
            while len(_CACHE) > _LIMIT:
                _CACHE.popitem(last=False)
            return built

    @staticmethod
    def object_map(model: Any) -> dict[str, dict[str, Any]]:
        """Compatibility lookup retains live rows and historical malformed errors."""
        return {str(row.get('id')): row for row in model.object_types or []
                if row.get('id') is not None}

    @staticmethod
    def role_map(model: Any) -> dict[str, dict[str, str]]:
        return {str(ft.get('id')): {
            str(role.get('role_name')): str(role.get('object_type'))
            for role in ft.get('roles') or []
            if role.get('role_name') is not None and role.get('object_type') is not None
        } for ft in model.fact_types or [] if ft.get('id') is not None}

    @staticmethod
    def constraint_roles(constraint: Any) -> list[str]:
        """The role names a fact-type constraint spans (uniqueness, frequency), in declared order."""
        roles = constraint.get('roles') if isinstance(constraint, dict) else None
        return [str(role) for role in roles] if isinstance(roles, list) else []

    @staticmethod
    def scope_facts(model: Any, targets: Any) -> list[str]:
        return [str(ft.get('id')) for ft in model.fact_types
                if any(role.get('object_type') in targets for role in ft.get('roles') or [])]

    @property
    def fact_types(self) -> tuple[dict[str, Any], ...]:
        return tuple(deepcopy(self._document.get('fact_types') or []))

    def iter_fact_types(self) -> Iterator[dict[str, Any]]:
        return iter(self.fact_types)

    def iter_fact_types_shared(self) -> Iterator[dict[str, Any]]:
        """Internal readers only: the index's own fact-type rows, not copied.

        Callers must never mutate a row or anything inside it. The index is shared across
        calls through the content-keyed cache, so a write would corrupt every later caller.
        Public callers use ``iter_fact_types`` / ``fact_types``, which return detached copies.
        """
        return iter(self._document.get('fact_types') or [])

    def role_object_types(self) -> dict[str, dict[str, str]]:
        return {
            str(ft.get('id')): {
                str(role.get('role_name')): str(role.get('object_type'))
                for role in ft.get('roles') or []
                if role.get('role_name') is not None and role.get('object_type') is not None
            }
            for ft in self._document.get('fact_types') or [] if ft.get('id') is not None
        }

    def fact_type_roles(self) -> dict[str, set[str]]:
        return {str(ft.get('id')): {str(role.get('role_name')) for role in ft.get('roles') or []
                                  if isinstance(role, dict) and role.get('role_name')}
                for ft in self._document.get('fact_types') or []
                if isinstance(ft, dict) and ft.get('id') is not None}

    def facts_for_objects(self, identifiers: set[Any]) -> list[str]:
        return [str(ft.get('id')) for ft in self._document.get('fact_types') or []
                if any(role.get('object_type') in identifiers for role in ft.get('roles') or [])]

    @staticmethod
    def legacy_fact_type(model: Any, identifier: str) -> dict[str, Any] | None:
        for fact_type in model.fact_types:
            if str(fact_type.get('id')) == identifier:
                return fact_type
        return None

    @staticmethod
    def legacy_role_type(model: Any, fact_type_id: str, role_name: str) -> str | None:
        fact_type = ModelIndex.legacy_fact_type(model, fact_type_id)
        for role in (fact_type or {}).get('roles') or []:
            if role.get('role_name') == role_name:
                return str(role.get('object_type'))
        return None

    def fact_type(self, identifier: str) -> dict[str, Any] | None:
        return deepcopy(self._facts.get(identifier))

    def object_type(self, identifier: str) -> dict[str, Any] | None:
        return deepcopy(self._objects.get(identifier))

    def object_types_by_id(self) -> dict[str, dict[str, Any]]:
        return deepcopy(self._objects)

    def role_object_type(self, fact_type_id: str, role_name: str) -> str | None:
        fact = self._facts.get(fact_type_id)
        for role in (fact or {}).get('roles') or []:
            if role.get('role_name') == role_name:
                return str(role.get('object_type'))
        return None

    def supertype_closure(self, identifier: str) -> frozenset[str]:
        parents = {str(row.get('id')): [str(p) for p in row.get('subtype_of') or []]
                   for row in self._document.get('object_types') or [] if isinstance(row, dict)}
        seen: set[str] = set()
        pending = list(parents.get(identifier, []))
        while pending:
            parent = pending.pop()
            if parent not in seen:
                seen.add(parent)
                pending.extend(parents.get(parent, []))
        return frozenset(seen)

    # --- the universe tables (VG1) -------------------------------------------
    # Read by the checker's three universe walks (gnd.universe). Each is built
    # once per index and kept; a returned mapping is a read-only view, so no
    # caller can write into the shared cache.
    #
    # The tables are built from the canonical JSON form of the document, the
    # bytes the cache key is a digest of, so two models that share a key share
    # tables that are right for both. The rows of the first model to reach the
    # cache are not: a str-enum ``kind`` and the plain string share a key and
    # differ under ``str()`` (VG1 review r1, F1).

    def _table(self, name: str, build) -> Any:
        table = self._tables.get(name)
        if table is None:
            table = self._tables.setdefault(name, build())
        return table

    def _canonical(self) -> dict[str, Any]:
        def build() -> dict[str, Any]:
            if self.digest is None:
                return self._document  # uncacheable, so never shared with another model
            try:
                return _rf7_input.loads(artifacts.canonical_json_bytes(self._document))
            except (ValueError, RecursionError):
                # Over the routed reader's 10 MB or 64-level caps: the cached rows,
                # as before VG1 (a residual the VG1 record names).
                return self._document
        return self._table('canonical', build)

    def _canonical_objects(self) -> dict[str, dict[str, Any]]:
        """The last row of each id, as ``object_map`` reads live rows."""
        return {str(row.get('id')): row for row in self._canonical().get('object_types') or []
                if isinstance(row, dict) and row.get('id') is not None}

    def reference_value_types(self) -> MappingProxyType[str, str | None]:
        """object-type id -> the value type that denotes it, or None.

        A cache of ``gnd.universe.resolve_reference_value_type``, which stays the
        definition: built by the same walk (``_resolve_reference`` with
        ``_identifying_id``) over the same last-duplicate object map and one
        supertype map, once per object type.
        """
        def build() -> MappingProxyType[str, str | None]:
            objects = self._canonical_objects()
            parents = _supertype_parents(self._canonical())
            table: dict[str, str | None] = {}
            for identifier in objects:
                try:
                    table[identifier] = _resolve_reference(identifier, objects, parents, set(), _identifying_id)
                except (AttributeError, TypeError):
                    # A shape only a model built in code can hold (a reference that is
                    # not a mapping): not resolvable. The base walk raised here only
                    # for a type it was not asked to skip (VG1 review r1, F2).
                    table[identifier] = None
            return MappingProxyType(table)
        return self._table('reference', build)

    def denoted_by(self, value_type_ids: Any) -> set[str]:
        """Object types whose resolved value type is one of ``value_type_ids`` (a new set)."""
        def build() -> MappingProxyType[str, frozenset[str]]:
            inverse: dict[str, set[str]] = {}
            for identifier, value_type in self.reference_value_types().items():
                if value_type is not None:
                    inverse.setdefault(value_type, set()).add(identifier)
            return MappingProxyType({key: frozenset(value) for key, value in inverse.items()})
        inverse = self._table('denoted', build)
        result: set[str] = set()
        for value_type in value_type_ids:
            result.update(inverse.get(value_type, ()))
        return result

    def subtype_children(self) -> MappingProxyType[str, frozenset[str]]:
        """Declared id -> the ids that name it in ``subtype_of`` (direct children).

        The edges are those of ``_supertype_parents``: the last row of a
        duplicate id declares its supertypes.
        """
        def build() -> MappingProxyType[str, frozenset[str]]:
            children: dict[str, set[str]] = {}
            for identifier, supertypes in _supertype_parents(self._canonical()).items():
                for supertype in supertypes:
                    children.setdefault(supertype, set()).add(identifier)
            return MappingProxyType({key: frozenset(value) for key, value in children.items()})
        return self._table('children', build)

    def descendants(self, identifier: Any) -> set[str]:
        """``identifier`` and every transitive subtype of it, cycle-safe (a new set).

        Follows :meth:`subtype_children` downward. It reaches exactly the least
        set containing ``identifier`` that admits a declared type as soon as one
        of its supertypes is in it, which is the fixpoint
        ``gnd.universe._descendant_closure`` computed before VG1.
        """
        children = self.subtype_children()
        members = {identifier}
        pending = [identifier]
        while pending:
            for child in children.get(pending.pop(), ()):
                if child not in members:
                    members.add(child)
                    pending.append(child)
        return members

    def kind(self, identifier: Any) -> str | None:
        """The ``kind`` of the first object type whose ``str(id)`` is ``identifier``, or None."""
        def build() -> MappingProxyType[str, str | None]:
            kinds: dict[str, str | None] = {}
            for row in self._canonical().get('object_types') or []:
                if isinstance(row, dict):
                    value = row.get('kind')
                    kinds.setdefault(str(row.get('id')), str(value) if value is not None else None)
            return MappingProxyType(kinds)
        return self._table('kind', build).get(identifier) if isinstance(identifier, str) else None

    def primitive(self, identifier: str, *, variant: Literal['truthy', 'strict']) -> str | None:
        return primitive_for(identifier, self._objects, variant=variant)

    def iter_constraints_shared(
        self,
    ) -> Iterator[tuple[str, dict[str, Any], dict[str, Any] | None]]:
        """Internal readers only: ``iter_constraints`` refs and order, rows not copied.

        Callers must never mutate a row or anything inside it, for the reason
        ``iter_fact_types_shared`` gives. One linear pass, with no per-constraint
        copy of the containing fact type.
        """
        for fact_type in self._document.get('fact_types') or []:
            for position, constraint in enumerate(fact_type.get('constraints') or []):
                yield positional_constraint_ref(str(fact_type.get('id')), position), constraint, fact_type
        for position, constraint in enumerate(self._document.get('constraints') or []):
            yield positional_constraint_ref(None, position), constraint, None

    def iter_constraints(self) -> Iterator[tuple[str, dict[str, Any], dict[str, Any] | None]]:
        for fact_type in self._document.get('fact_types') or []:
            for position, constraint in enumerate(fact_type.get('constraints') or []):
                yield (positional_constraint_ref(str(fact_type.get('id')), position),
                       deepcopy(constraint), deepcopy(fact_type))
        for position, constraint in enumerate(self._document.get('constraints') or []):
            yield positional_constraint_ref(None, position), deepcopy(constraint), None
