"""Detached model query snapshots with a bounded, content-keyed cache.

The cache marker is internal. It does not replace any public model identity.
"""
from __future__ import annotations

import hashlib
from collections import OrderedDict
from collections.abc import Iterator
from copy import deepcopy
from dataclasses import dataclass, field
from threading import RLock
from typing import Any, Literal

from gnd import artifacts
from gnd.address import positional_constraint_ref
from gnd.documents import Model
from gnd.model_queries import primitive_for

_CACHE: OrderedDict[str, ModelIndex] = OrderedDict()
_LOCK = RLock()
_LIMIT = 32


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

    @classmethod
    def for_model(cls, model: Model) -> ModelIndex:
        if not isinstance(model, Model):
            raise TypeError('ModelIndex requires a Model')
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

    def primitive(self, identifier: str, *, variant: Literal['truthy', 'strict']) -> str | None:
        return primitive_for(identifier, self._objects, variant=variant)

    def iter_constraints(self) -> Iterator[tuple[str, dict[str, Any], dict[str, Any] | None]]:
        for fact_type in self._document.get('fact_types') or []:
            for position, constraint in enumerate(fact_type.get('constraints') or []):
                yield (positional_constraint_ref(str(fact_type.get('id')), position),
                       deepcopy(constraint), deepcopy(fact_type))
        for position, constraint in enumerate(self._document.get('constraints') or []):
            yield positional_constraint_ref(None, position), deepcopy(constraint), None
