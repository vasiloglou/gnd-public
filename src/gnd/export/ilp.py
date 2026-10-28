"""The learner-neutral ILP export form, ``gnd-ilp/1`` (IK5).

One form serves every learner adapter (D4 (o)). Examples are the populations of
a class-mode IK3 label manifest; the learned predicate is ``wrong/1`` and it
covers the ``negative`` class (IK5-D2, IK5-D3). Modes come from fact-type roles:
one predicate per asserted fact type whose first argument is the example, plus
four comparison predicates per integer-typed object type. The contract page is
``docs/reference/ilp-bridge.md``; the schema is ``src/gnd/ilp.schema.json``.

Refusals are :class:`IlpError` with an exit code and a name the message starts
with. The export writes raw population values, so a model whose redaction policy
covers an exported role, and any opaque or unrepresentable cell, is refused
(IK5-D11).
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from gnd.exits import EXIT_ILL_FORMED

__all__ = [
    "COVERS_CLASS",
    "MAX_FACTS",
    "MAX_FILE_BYTES",
    "Column",
    "IlpError",
    "build_neutral",
    "canonical_bytes",
    "export_tree",
    "type_closures",
]

NEUTRAL_SCHEMA_VERSION = "gnd-ilp/1"
EXPORT_SCHEMA_VERSION = "gnd-ilp-export/1"
#: The neutral target's adapter version; an adapter with its own rendering
#: declares its own in the learner registry (IL1-A1).
ADAPTER_VERSION = "1"
COVERS_CLASS = "negative"
#: IK5-D14: bounds fixed before results. The facts bound is 500,000 by owner
#: amendment IK5-Q1 (2026-10-26): at the smallest entry, 97 bytes, 500,000 facts
#: fit the file cap, so both bounds can refuse (r1 said 1,000,000, unreachable).
MAX_FACTS = 500_000
MAX_FILE_BYTES = 64 * 1024 * 1024
_NAME = re.compile(r"[a-z][a-z0-9_]{0,58}")
_PRIMITIVES = {"Integer": "integer", "String": "string", "Boolean": "boolean"}
COMPARISONS = (("ge", ">="), ("gt", ">"), ("le", "<="), ("lt", "<"))
#: The spelling of every comparison predicate name; the adapters' readers match it.
COMPARISON_NAME = r"(?:gt|lt|ge|le)_t_[A-Za-z0-9_]+"


class IlpError(Exception):
    """A refused export or import, with its exit code; the message names the cause."""

    def __init__(self, code: int, message: str) -> None:
        super().__init__(message)
        self.code = code


def refusal_name(message: str) -> str:
    """The refusal name in an import's exit-3 message: ``clause K: <name>: ...``,
    ``rule K: <name>: ...`` (``gnd import mined-rules``, IL4-F9) or ``<name>: ...``."""
    if message.startswith(("clause ", "rule ")):
        return message.split(": ")[1]
    return message.split(":")[0]


def observed_integers(neutral: dict[str, Any]) -> dict[str, set[int]]:
    """The integer values each type takes in the neutral form's facts; booleans are not integers."""
    observed: dict[str, set[int]] = {}
    types = {row["name"]: row["types"][1:] for row in neutral["predicates"]}
    for fact in neutral["facts"]:
        for type_name, value in zip(types[fact["predicate"]], fact["values"], strict=True):
            if isinstance(value, int) and not isinstance(value, bool):
                observed.setdefault(type_name, set()).add(value)
    return observed


def canonical_bytes(document: Any) -> bytes:
    """Sorted keys, two-space indent, a trailing newline (spec §6)."""
    return (json.dumps(document, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False)
            + "\n").encode("utf-8")


def _compact(values: list[Any]) -> str:
    return json.dumps(values, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _refuse(name: str, detail: str) -> IlpError:
    return IlpError(EXIT_ILL_FORMED, f"{name}: {detail}")


@dataclass(frozen=True)
class Work:
    populations: int
    facts: int

    def report(self) -> dict[str, int]:
        return {"populations": self.populations, "facts": self.facts,
                "total": self.populations + self.facts,
                "ceiling": self.populations + MAX_FACTS}


@dataclass(frozen=True)
class Column:
    """One exported predicate: its fact type, role names and argument types."""

    fact_type: str
    role_names: tuple[str, ...]
    types: tuple[str, ...]


def _type_name(object_type: str) -> str:
    if _NAME.fullmatch(object_type) is None:
        raise _refuse("name", f"object type id {object_type!r} is not an ILP-safe name")
    return f"t_{object_type}"


def _primitive(object_type: dict[str, Any]) -> str | None:
    if object_type.get("kind") != "value":
        return None
    primitive = object_type.get("primitive")
    if primitive not in _PRIMITIVES:
        raise _refuse("primitive", f"object type {object_type.get('id')!r} has primitive "
                      f"{primitive!r}; the export renders Integer, String and Boolean only")
    return _PRIMITIVES[primitive]


def schema(model: Any, redacted: frozenset[tuple[str, str]]) -> tuple[dict[str, Any], dict[str, Column]]:
    """The neutral form's types, predicates, comparisons and skipped fact types,
    and the same predicates as columns for the readers that need them."""
    from gnd.model_index import ModelIndex

    index = ModelIndex.for_model(model)
    object_types = index.object_types_by_id()
    role_types = index.role_object_types()
    types: dict[str, dict[str, Any]] = {}
    columns: dict[str, Column] = {}
    derived: list[str] = []
    for fact_type in index.iter_fact_types_shared():
        fact_id = str(fact_type.get("id"))
        if fact_type.get("derivation") in ("derived", "semiderived"):
            derived.append(fact_id)
            continue
        if _NAME.fullmatch(fact_id) is None:
            raise _refuse("name", f"fact type id {fact_id!r} is not an ILP-safe name")
        names, argument_types = [], ["ex"]
        for role_name, object_type in role_types.get(fact_id, {}).items():
            if (fact_id, role_name) in redacted:
                raise _refuse("redacted", f"role {fact_id}.{role_name} is redacted by the model; "
                              "the export would write its values (IK5-D11)")
            name = _type_name(object_type)
            if name not in types:
                types[name] = {"name": name, "object_type": object_type,
                               "primitive": _primitive(object_types.get(object_type, {}))}
            names.append(role_name)
            argument_types.append(name)
        columns[f"f_{fact_id}"] = Column(fact_id, tuple(names), tuple(argument_types))
    comparisons = [
        {"name": f"{prefix}_{name}", "operator": operator, "type": name}
        for name, row in types.items() if row["primitive"] == "integer"
        for prefix, operator in COMPARISONS
    ]
    columns = dict(sorted(columns.items()))
    shape = {
        "types": sorted(types.values(), key=lambda row: row["name"]),
        "predicates": [{"name": name, "fact_type": column.fact_type,
                        "roles": list(column.role_names), "types": list(column.types)}
                       for name, column in columns.items()],
        "comparisons": sorted(comparisons, key=lambda row: row["name"]),
        "skipped": {"derived_fact_types": sorted(derived)},
    }
    return shape, columns


def type_closures(model: Any) -> dict[str, frozenset[str]]:
    """Each object type with its transitive supertypes, read through ModelIndex.

    ``supertype_closure`` leaves the type itself out, so it is added: the result
    is the ancestor closure that ``semantic:op-term-type-compat`` intersects. The
    import's join check reads it (D12 (o), D13 (o)); it never reaches the wire."""
    from gnd.model_index import ModelIndex

    index = ModelIndex.for_model(model)
    return {identifier: frozenset({identifier}) | index.supertype_closure(identifier)
            for identifier in index.object_types_by_id()}


def _value(value: Any, *, where: str) -> Any:
    if isinstance(value, dict) and set(value) == {"$opaque"}:
        raise _refuse("opaque", f"{where} holds an opaque value the export cannot render")
    if isinstance(value, (bool, str, int)):
        return value
    raise _refuse("unrepresentable", f"{where} holds a {type(value).__name__} value")


def build_neutral(
    *,
    model: Any,
    model_sha256: str,
    manifest: Any,
    populations: list[Any],
    redacted: frozenset[tuple[str, str]],
) -> tuple[dict[str, Any], dict[str, Column], Work]:
    """The neutral form for loaded populations given in manifest order, its
    columns, and the work done."""
    shape, columns = schema(model, redacted)
    entries = manifest.document["populations"]
    facts: list[tuple[int, str, str, list[Any]]] = []
    for position, (entry, population) in enumerate(zip(entries, populations, strict=True)):
        for name, column in columns.items():
            for row in population.facts.get(column.fact_type, []):
                where = f"population {entry['id']!r}, fact type {column.fact_type!r}"
                values = []
                for role in column.role_names:
                    if role not in row:
                        raise _refuse("unrepresentable", f"{where} lacks role {role!r}")
                    values.append(_value(row[role], where=where))
                facts.append((position, name, _compact(values), values))
                if len(facts) > MAX_FACTS:
                    raise _refuse("too-large", f"the export exceeds {MAX_FACTS} facts")
    facts.sort(key=lambda fact: fact[:3])
    neutral = {
        "schema_version": NEUTRAL_SCHEMA_VERSION,
        "model_sha256": model_sha256,
        "manifest_sha256": manifest.sha256,
        "target": {"predicate": "wrong", "arity": 1, "covers_class": COVERS_CLASS},
        **shape,
        "examples": [
            {"id": entry["id"], "class": entry["class"],
             "label": "pos" if entry["class"] == COVERS_CLASS else "neg"}
            for entry in entries
        ],
        "facts": [{"example": entries[position]["id"], "predicate": name, "values": values}
                  for position, name, _key, values in facts],
    }
    return neutral, columns, Work(len(entries), len(facts))


def export_tree(
    neutral: dict[str, Any], target: str, rendering: dict[str, bytes], *,
    adapter_version: str = ADAPTER_VERSION,
) -> dict[str, bytes]:
    """Every file the export writes, keyed by its path, ``export.json`` last.

    ``rendering`` is the adapter's files (none for the ``neutral`` target). The
    export digest E is the SHA-256 of ``export.json``, which lists every other
    file's digest (spec §6), so ``sha256sum DIR/export.json`` reproduces it."""
    return index_tree({"neutral.json": canonical_bytes(neutral), **rendering}, target,
                      adapter_version=adapter_version)


def index_tree(files: dict[str, bytes], target: str, *, adapter_version: str) -> dict[str, bytes]:
    """``files`` plus the ``export.json`` that indexes them, ``export.json`` last."""
    files = dict(files)
    for path, data in files.items():
        if len(data) > MAX_FILE_BYTES:
            raise _refuse("too-large", f"{path} would exceed {MAX_FILE_BYTES} bytes")
    index = {
        "schema_version": EXPORT_SCHEMA_VERSION,
        "target": target,
        "adapter_version": adapter_version,
        "files": [{"path": path, "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}
                  for path, data in sorted(files.items())],
    }
    files["export.json"] = canonical_bytes(index)
    return files


def export_digest(tree: dict[str, bytes]) -> str:
    return hashlib.sha256(tree["export.json"]).hexdigest()


def write_tree(out: Path, tree: dict[str, bytes]) -> None:
    """Create ``out`` and write the tree; ``out`` must not exist (checked by the caller)."""
    out.mkdir()
    for path, data in sorted(tree.items()):
        target = out / path
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("xb") as handle:
            handle.write(data)
