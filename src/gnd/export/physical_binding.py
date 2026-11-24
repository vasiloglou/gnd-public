"""Read a physical binding and bind a model's roles to a delivered relational schema.

The normative rules have one home: "Physical binding" under "Ossie interchange" in
``gnd-orm-core/references/representation-format.md``. The document's members are
defined by the packaged schema ``gnd/schema/physical-binding.schema.json``.

A binding is untrusted input. :func:`read_binding` is total over arbitrary bytes, and
:func:`bind` over any schema-valid document and admitted model: every refusal is a
:class:`BindingError` with a rule id. The checks run in one pinned order
(:data:`RULE_ORDER`), and within a rule the first violation in sorted order is
reported, so a message never depends on the document's member order.

:func:`bind` returns the same :class:`gnd.rmap.RelationalSchema` the Rmap returns, so
the semantic model, the mapping and the one walk over fact types and constraints are
shared with the built-in path.
"""

from __future__ import annotations

import hashlib
import unicodedata
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from functools import lru_cache
from importlib.resources import files
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from gnd.export.ossie_relational import OntologyView
from gnd.input_policy import MAX_BYTES, loads
from gnd.model_index import ModelIndex
from gnd.rmap import (
    Column,
    Identification,
    RelationalSchema,
    RolePlacement,
    Table,
    Unmapped,
    name_foreign_keys,
)
from gnd.safefs import NotRegularFileError, open_regular

__all__ = ["RULE_ORDER", "SQL_TYPES", "Binding", "BindingError", "bind", "normalize_role_name", "read_binding", "sql_datatype"]

SCHEMA_ID = "gnd-physical-binding/1"

#: Every rule id, in the one order the checks run. The first three need only the
#: file; the fourth only the JSON; the rest need the model and the ontology view.
RULE_ORDER = (
    "binding:not-a-file",
    "binding:size",
    "binding:syntax",
    "binding:schema",
    "binding:name-collision",
    "binding:unknown-table",
    "binding:unknown-column",
    "binding:ambiguous-column",
    "binding:unknown-fact-type",
    "binding:role-name",
    "binding:unknown-role",
    "binding:unknown-object-type",
    "binding:reference-group",
    "binding:reference-not-a-key",
    "binding:partial-fact-type",
    "binding:role-arity",
    "binding:target-mismatch",
    "binding:key-role",
    "binding:incompatible-keys",
)

#: Normalized SQL type name -> Ossie core-spec data type (OB4 D7). A type outside this
#: closed map leaves ``datatype`` absent.
SQL_TYPES: dict[str, str] = {
    **dict.fromkeys(
        ("char", "character", "varchar", "character varying", "nchar", "nvarchar", "text", "string", "uuid"), "String"),
    **dict.fromkeys(
        ("smallint", "integer", "int", "bigint", "tinyint", "int2", "int4", "int8", "serial", "bigserial",
         "long", "short", "byte"), "Integer"),
    **dict.fromkeys(("numeric", "decimal", "dec", "number"), "Decimal"),
    **dict.fromkeys(("real", "float", "float4", "float8", "double", "double precision"), "Float"),
    **dict.fromkeys(("boolean", "bool"), "Boolean"),
    "date": "Date",
    **dict.fromkeys(("time", "time without time zone"), "Time"),
    **dict.fromkeys(("timestamp", "timestamp without time zone", "timestamp_ntz", "datetime"), "DateTime"),
    **dict.fromkeys(("timestamp with time zone", "timestamptz", "timestamp_ltz"), "DateTimeTz"),
    **dict.fromkeys(("bytea", "binary", "varbinary", "blob", "json", "jsonb"), "Opaque"),
}

_WORD = frozenset("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_")
_DIGITS = frozenset("0123456789")


class BindingError(ValueError):
    """A physical binding is refused. ``rule`` is one of :data:`RULE_ORDER`."""

    def __init__(self, rule: str, detail: str = "") -> None:
        assert rule in RULE_ORDER, rule
        self.rule = rule
        super().__init__(f"{rule}: {detail}" if detail else rule)


@dataclass(frozen=True)
class Binding:
    """A schema-valid binding document and the digest of the bytes it was read from."""

    document: Mapping[str, Any]
    sha256: str


@lru_cache(maxsize=1)
def _validator() -> Draft202012Validator:
    schema = loads(files("gnd").joinpath("schema", "physical-binding.schema.json").read_bytes())
    return Draft202012Validator(schema)


def read_binding(path: Path) -> Binding:
    """Read and schema-check a binding. A missing file raises ``FileNotFoundError``."""
    try:
        descriptor = open_regular(path)
    except NotRegularFileError as error:
        raise BindingError("binding:not-a-file", "the path is not a regular file") from error
    with open(descriptor, "rb") as stream:
        raw = stream.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise BindingError("binding:size", f"the file is larger than {MAX_BYTES} bytes")
    try:
        document = loads(raw, max_bytes=MAX_BYTES)
    except (ValueError, RecursionError, OverflowError) as error:
        raise BindingError("binding:syntax", "the file is not JSON within the input limits") from error
    violations = sorted(
        ("/" + "/".join(str(part) for part in error.absolute_path) if error.absolute_path else "", error.message)
        for error in _validator().iter_errors(document)
    )
    if violations:
        pointer, message = violations[0]
        raise BindingError("binding:schema", f"at {pointer or 'the document root'}: {message[:200]}")
    return Binding(document, hashlib.sha256(raw).hexdigest())


def sql_datatype(sql_type: str) -> str | None:
    """The Ossie data type of an SQL type, or None when the type is outside the map.

    A type is words of letters, digits and underscores separated by spaces, with at
    most one parenthesized list of unsigned integers after a word. Its name is the
    words, casefolded and joined by one space.
    """
    words: list[str] = []
    listed = False
    position = 0
    while position < len(sql_type):
        character = sql_type[position]
        if character == " ":
            position += 1
        elif character in _WORD:
            end = position
            while end < len(sql_type) and sql_type[end] in _WORD:
                end += 1
            words.append(sql_type[position:end].casefold())
            position = end
        elif character == "(" and words and not listed:
            end = sql_type.find(")", position)
            if end < 0:
                return None
            items = [item.strip(" ") for item in sql_type[position + 1:end].split(",")]
            if not all(item and set(item) <= _DIGITS for item in items):
                return None
            listed = True
            position = end + 1
        else:
            return None
    return SQL_TYPES.get(" ".join(words))


def normalize_role_name(name: str) -> str:
    """A role name for matching (OB4 D8): NFKC, casefolded, letters and digits only."""
    folded = unicodedata.normalize("NFKC", name).casefold()
    return "".join(c for c in folded if unicodedata.category(c)[0] in "LN")


ColumnRef = tuple[str, str]


class _Binder:
    def __init__(self, model: Any, view: OntologyView, binding: Binding) -> None:
        self.model = model
        self.view = view
        self.sha256 = binding.sha256
        self.tables: Mapping[str, Any] = binding.document["tables"]
        self.role_sections: dict[str, Mapping[str, Any]] = {
            "roles": binding.document["roles"],
            "extension_roles": binding.document.get("extension_roles", {}),
        }
        index = ModelIndex.for_model(model)
        self.objects = index.object_types_by_id()
        self.players: Mapping[str, Mapping[str, str]] = index.role_object_types()
        self.facts = list(index.iter_fact_types_shared())
        self.spelled: dict[str, list[ColumnRef]] = {}
        for table, body in self.tables.items():
            for column in body["columns"]:
                self.spelled.setdefault(f"{table}.{column}", []).append((table, column))
        #: (section, fact type, model role name) -> columns, filled by the name checks.
        self.bound: dict[tuple[str, str, str], tuple[ColumnRef, ...]] = {}
        self._arity: dict[str, int | None] = {}

    # -- iteration in sorted order ------------------------------------------------------

    def columns(self) -> Iterable[tuple[str, str, Mapping[str, Any]]]:
        for table in sorted(self.tables):
            for column in sorted(self.tables[table]["columns"]):
                yield table, column, self.tables[table]["columns"][column]

    def role_entries(self) -> Iterable[tuple[str, str, str, list[Any]]]:
        """(section, fact type, role name as written, column references)."""
        for section in ("roles", "extension_roles"):
            for fact in sorted(self.role_sections[section]):
                for role in sorted(self.role_sections[section][fact]):
                    yield section, fact, role, self.role_sections[section][fact][role]

    def targets(self, kinds: tuple[str, ...]) -> Iterable[tuple[str, str, Mapping[str, str]]]:
        for table, column, body in self.columns():
            for target in body.get("targets", ()):
                if target["kind"] in kinds:
                    yield table, column, target

    # -- step 5: names ---------------------------------------------------------------------

    def check_names(self) -> None:
        # binding:name-collision. Expressions quote and uppercase every name.
        for label, names in [("tables", sorted(self.tables)),
                             *((f"columns of {t}", sorted(self.tables[t]["columns"])) for t in sorted(self.tables))]:
            seen: dict[str, str] = {}
            for name in names:
                other = seen.setdefault(name.upper(), name)
                if other != name:
                    raise BindingError("binding:name-collision", f"{label}: {other!r} and {name!r} are one identifier")
        # binding:unknown-table
        for table, column, body in self.columns():
            target = body.get("references", {}).get("table")
            if target is not None and target not in self.tables:
                raise BindingError("binding:unknown-table", f"{table}.{column} references table {target!r}")
        for _section, fact, role, references in self.role_entries():
            for reference in references:
                if not isinstance(reference, str) and reference["table"] not in self.tables:
                    raise BindingError("binding:unknown-table", f"{fact}.{role} names table {reference['table']!r}")
        # binding:unknown-column
        for table in sorted(self.tables):
            body = self.tables[table]
            for key in [body.get("primary_key", ()), *body.get("unique_keys", ())]:
                for column in key:
                    if column not in body["columns"]:
                        raise BindingError("binding:unknown-column", f"a key of {table} names column {column!r}")
        for table, column, body in self.columns():
            reference = body.get("references")
            if reference is not None:
                for name in reference["columns"]:
                    if name not in self.tables[reference["table"]]["columns"]:
                        raise BindingError(
                            "binding:unknown-column", f"{table}.{column} references {reference['table']}.{name}")
        for _section, fact, role, references in self.role_entries():
            for reference in references:
                if isinstance(reference, str):
                    if reference not in self.spelled:
                        raise BindingError("binding:unknown-column", f"{fact}.{role} names column {reference!r}")
                elif reference["column"] not in self.tables[reference["table"]]["columns"]:
                    raise BindingError(
                        "binding:unknown-column", f"{fact}.{role} names column {reference['table']}.{reference['column']}")
        # binding:ambiguous-column. A string is looked up, never split on its dots.
        for _section, fact, role, references in self.role_entries():
            for reference in references:
                if isinstance(reference, str) and len(self.spelled[reference]) > 1:
                    raise BindingError(
                        "binding:ambiguous-column", f"{fact}.{role}: {reference!r} spells more than one table and column")
        # binding:unknown-fact-type
        for _section, fact, _role, _references in self.role_entries():
            if fact not in self.players:
                raise BindingError("binding:unknown-fact-type", f"{fact!r} is not a fact type of the model")
        for table, column, target in self.targets(("role",)):
            if target["fact_type"] not in self.players:
                raise BindingError("binding:unknown-fact-type", f"a target of {table}.{column} names {target['fact_type']!r}")
        # binding:role-name, then binding:unknown-role. A name that normalizes to nothing,
        # or like another, cannot be looked up, so it is judged before the lookup.
        resolved: dict[tuple[str, str, str], str] = {}
        model_names: dict[str, dict[str, str]] = {}
        named_facts = sorted({fact for _s, fact, _r, _c in self.role_entries()}
                             | {target["fact_type"] for _t, _c, target in self.targets(("role",))})
        for fact in named_facts:
            names: dict[str, str] = {}
            for role in self.players[fact]:
                normal = normalize_role_name(role)
                if not normal or normal in names:
                    raise BindingError("binding:role-name", f"the roles of {fact} cannot be told apart once normalized")
                names[normal] = role
            model_names[fact] = names
        for section in ("roles", "extension_roles"):
            for fact in sorted(self.role_sections[section]):
                written: dict[str, str] = {}
                for role in sorted(self.role_sections[section][fact]):
                    normal = normalize_role_name(role)
                    if not normal:
                        raise BindingError("binding:role-name", f"{fact}: role name {role!r} has no letter or digit")
                    if normal in written:
                        raise BindingError(
                            "binding:role-name", f"{fact}: {written[normal]!r} and {role!r} are one role name")
                    written[normal] = role
        for table, column, target in self.targets(("role",)):
            if not normalize_role_name(target["role"]):
                raise BindingError("binding:role-name", f"a target of {table}.{column} names role {target['role']!r}")
        for section, fact, role, _references in self.role_entries():
            match = model_names[fact].get(normalize_role_name(role))
            if match is None:
                raise BindingError("binding:unknown-role", f"{fact} has no role {role!r}")
            resolved[(section, fact, role)] = match
        for table, column, target in self.targets(("role",)):
            if normalize_role_name(target["role"]) not in model_names[target["fact_type"]]:
                raise BindingError(
                    "binding:unknown-role", f"a target of {table}.{column}: {target['fact_type']} has no role {target['role']!r}")
        # binding:unknown-object-type
        for table, column, target in self.targets(("identifier", "reference")):
            if target["object_type"] not in self.objects:
                raise BindingError("binding:unknown-object-type", f"a target of {table}.{column} names {target['object_type']!r}")
        self.model_names = model_names
        for section, fact, role, references in self.role_entries():
            self.bound[(section, fact, resolved[(section, fact, role)])] = tuple(
                self.spelled[r][0] if isinstance(r, str) else (r["table"], r["column"]) for r in references)

    # -- identification, as the ontology declares it ---------------------------------------

    def components(self, object_type: str) -> list[tuple[str, str, str]] | None:
        """(fact type, component role, component player) per identifying relationship of
        a composite identifier, in the ontology's order; None for any other object type."""
        form, payload = self.view.identification.get(object_type, (None, None))
        if form != "composite":
            return None
        result = []
        for fact in payload:
            _owner, order, players = self.view.relations[fact]
            result.append((fact, order[1], players[order[1]]))
        return result

    def arity(self, object_type: str) -> int | None:
        """How many columns hold one object of the type; None when the ontology declares
        no identifier for it (the mapping then lists it as identification-differs)."""
        if object_type in self._arity:
            return self._arity[object_type]
        self._arity[object_type] = None  # a re-entrant request has no answer
        result: int | None
        if self.objects[object_type]["kind"] == "value" or self.view.identification.get(object_type, (None,))[0] == "simple":
            result = 1
        elif (components := self.components(object_type)) is not None:
            parts = [self.arity(player) for _fact, _role, player in components]
            result = None if None in parts else sum(parts)  # type: ignore[arg-type]
        else:
            result = None
        self._arity[object_type] = result
        return result

    def related(self, first: str, second: str) -> bool:
        """The same object type, or one a subtype of the other."""
        def ancestors(object_type: str) -> set[str]:
            seen, pending = set(), [object_type]
            while pending:
                current = pending.pop()
                if current not in seen:
                    seen.add(current)
                    pending += [str(parent) for parent in self.objects.get(current, {}).get("subtype_of") or ()]
            return seen

        return first in ancestors(second) or second in ancestors(first)

    def declared_homes(self) -> list[tuple[str, str]]:
        """(table, object type) wherever every primary-key column is marked as that
        object type's identifier, in sorted order."""
        declared = []
        for table in sorted(self.tables):
            key = tuple(self.tables[table].get("primary_key", ()))
            marked = [
                {t["object_type"] for t in self.tables[table]["columns"][c].get("targets", ()) if t["kind"] == "identifier"}
                for c in key
            ]
            declared += [(table, object_type) for object_type in (sorted(set.intersection(*marked)) if marked else ())]
        return declared

    def home_tables(self) -> dict[str, str]:
        """object type -> the table its object mapping reads: the first declared home
        whose key is exactly the columns its identifier is bound to there."""
        homes: dict[str, str] = {}
        for table, object_type in self.declared_homes():
            if object_type not in homes and self.home_key(object_type, table) is not None:
                homes[object_type] = table
        return homes

    def identified_through(self, whole: str, part: str) -> bool:
        """Whether ``part`` is a component of ``whole``'s identifier, at any depth."""
        seen, pending = set(), [whole]
        while pending:
            current = pending.pop()
            if current in seen:
                continue
            seen.add(current)
            for _fact, _role, player in self.components(current) or ():
                if self.related(player, part):
                    return True
                pending.append(player)
        return False

    def home_key(self, object_type: str, table: str) -> tuple[str, ...] | None:
        """The table's key columns in the object type's identification order, or None
        when the key is not that object type's identifier."""
        key = tuple(self.tables[table].get("primary_key", ()))
        if self.objects[object_type]["kind"] != "entity" or self.arity(object_type) is None:
            return None
        components = self.components(object_type)
        if components is None:
            return key if len(key) == 1 else None
        ordered: list[str] = []
        for fact, role, _player in components:
            columns = self.bound.get(("roles", fact, role))
            if columns is None or any(t != table for t, _c in columns):
                return None
            ordered += [column for _t, column in columns]
        return tuple(ordered) if sorted(ordered) == sorted(key) else None

    # -- step 6: contradictions ------------------------------------------------------------

    def foreign_keys(self, table: str) -> list[tuple[tuple[str, ...], str, tuple[str, ...]]]:
        """(columns, target table, target columns) per group of equal `references`, in
        the order of each group's first column. Columns pair by table column order."""
        groups: dict[tuple[str, tuple[str, ...]], list[str]] = {}
        for column, body in self.tables[table]["columns"].items():
            reference = body.get("references")
            if reference is not None:
                groups.setdefault((reference["table"], tuple(reference["columns"])), []).append(column)
        return [(tuple(columns), target, target_columns) for (target, target_columns), columns in groups.items()]

    def check_contradictions(self) -> None:
        # binding:reference-group
        for table in sorted(self.tables):
            for columns, target, target_columns in self.foreign_keys(table):
                if len(columns) != len(target_columns):
                    raise BindingError(
                        "binding:reference-group",
                        f"{table}: {len(columns)} column(s) reference {len(target_columns)} column(s) of {target}")
        # binding:reference-not-a-key
        for table in sorted(self.tables):
            for _columns, target, target_columns in self.foreign_keys(table):
                body = self.tables[target]
                keys = [tuple(body.get("primary_key", ())), *(tuple(key) for key in body.get("unique_keys", ()))]
                if target_columns not in keys:
                    raise BindingError(
                        "binding:reference-not-a-key", f"{table} references {target}{list(target_columns)}, which is not a key")
        # binding:partial-fact-type
        for section in ("roles", "extension_roles"):
            for fact in sorted(self.role_sections[section]):
                missing = sorted(role for role in self.players[fact] if (section, fact, role) not in self.bound)
                if missing:
                    raise BindingError("binding:partial-fact-type", f"{fact}: no columns for role {missing[0]!r}")
        # binding:role-arity
        for (_section, fact, role), columns in sorted(self.bound.items()):
            wanted = self.arity(self.players[fact][role])
            if wanted is not None and len(columns) != wanted:
                raise BindingError(
                    "binding:role-arity", f"{fact}.{role} needs {wanted} column(s) and has {len(columns)}")
        # binding:target-mismatch
        holders: dict[ColumnRef, list[tuple[str, str, str]]] = {}
        for (section, fact, role), columns in sorted(self.bound.items()):
            for reference in columns:
                holders.setdefault(reference, []).append((section, fact, role))
        for table, column, target in self.targets(("role",)):
            role = self.model_names[target["fact_type"]][normalize_role_name(target["role"])]
            if not any((fact, name) == (target["fact_type"], role) for _s, fact, name in holders.get((table, column), ())):
                raise BindingError(
                    "binding:target-mismatch", f"{table}.{column} is not among the columns of {target['fact_type']}.{role}")
        for table, column, target in self.targets(("reference",)):
            if not any(self.players[fact][role] == target["object_type"] for _s, fact, role in holders.get((table, column), ())):
                raise BindingError(
                    "binding:target-mismatch", f"{table}.{column} holds no role played by {target['object_type']}")
        # binding:key-role
        for table, object_type in self.declared_homes():
            identifying = {(fact, role) for fact, role, _player in self.components(object_type) or ()}
            for column in self.tables[table]["primary_key"]:
                for _section, fact, role in holders.get((table, column), ()):
                    if not self.related(self.players[fact][role], object_type) and (fact, role) not in identifying:
                        raise BindingError(
                            "binding:key-role", f"{table}.{column} is a key of {object_type} and holds {fact}.{role}")
        # binding:incompatible-keys
        for reference in sorted(holders):
            held = sorted({self.players[fact][role] for section, fact, role in holders[reference] if section == "roles"})
            for first in held:
                for second in held:
                    compatible = (
                        self.related(first, second)
                        # A key column holds an entity and the part of its identifier kept there.
                        or self.identified_through(first, second)
                        or self.identified_through(second, first)
                    )
                    if first < second and not compatible:
                        raise BindingError(
                            "binding:incompatible-keys",
                            f"{reference[0]}.{reference[1]} holds both {first} and {second}")
        self.homes = self.home_tables()

    # -- the relational schema -------------------------------------------------------------

    def schema(self) -> RelationalSchema:
        carried: dict[tuple[str, str], tuple[str, ...]] = {}
        unmapped: dict[tuple[str, str], str] = {}
        placements: list[RolePlacement] = []
        fact_table: dict[str, str] = {}
        role_columns: dict[tuple[str, str], tuple[str, ...]] = {}
        for fact in self.facts:
            fid = str(fact["id"])
            roles = list(self.players[fid])
            if ("roles", fid, roles[0]) not in self.bound:
                extension = ("extension_roles", fid, roles[0]) in self.bound
                unmapped[("fact_type", fid)] = "extension-role" if extension else "unbound"
                continue
            held = {role: self.bound[("roles", fid, role)] for role in roles}
            used = {table for columns in held.values() for table, _column in columns}
            if len(used) != 1:
                unmapped[("fact_type", fid)] = "spans-tables"
                continue
            (table,) = used
            fact_table[fid] = table
            listed: list[str] = []
            for role in roles:
                names = tuple(column for _table, column in held[role])
                role_columns[(fid, role)] = names
                placements.append(RolePlacement(fid, role, table, names))
                listed += [name for name in names if name not in listed]
            carried[("fact_type", fid)] = ("columns", table, *listed)

        # Uniqueness: every confirmed alethic one whose roles sit in one table.
        position = {t: {c: i for i, c in enumerate(body["columns"])} for t, body in self.tables.items()}
        derived: dict[str, dict[frozenset[str], tuple[str, ...]]] = {t: {} for t in self.tables}
        pending: list[tuple[tuple[str, str], str, frozenset[str]]] = []

        def confirmed(constraint: Mapping[str, Any]) -> bool:
            return constraint.get("status") == "confirmed" and constraint.get("modality") == "alethic"

        def place(address: tuple[str, str], constraint: Mapping[str, Any], roles: list[tuple[str, str]]) -> None:
            reasons = sorted({unmapped[("fact_type", f)] for f, _r in roles if ("fact_type", f) in unmapped})
            if reasons:
                unmapped[address] = reasons[0]
            elif not confirmed(constraint):
                unmapped[address] = "uniqueness-not-confirmed"
            elif len({fact_table[f] for f, _r in roles}) != 1:
                unmapped[address] = "spans-tables"
            else:
                table = fact_table[roles[0][0]]
                columns = frozenset(c for f, r in roles for c in role_columns[(f, r)])
                pending.append((address, table, columns))
                if columns != frozenset(self.tables[table].get("primary_key", ())):
                    derived[table][columns] = tuple(sorted(columns, key=position[table].__getitem__))

        for fact in self.facts:
            fid = str(fact["id"])
            for number, constraint in enumerate(fact.get("constraints") or ()):
                address = ("constraint", f"fact_types/{fid}/constraints/{number}")
                if ("fact_type", fid) in unmapped:
                    unmapped[address] = unmapped[("fact_type", fid)]
                elif constraint.get("type") == "uniqueness" and constraint.get("scope") != "external":
                    place(address, constraint, [(fid, role) for role in ModelIndex.constraint_roles(constraint)])
                else:
                    unmapped[address] = "not-relational"
        for number, constraint in enumerate(self.model.constraints or ()):
            address = ("constraint", f"constraints/{number}")
            if constraint.get("type") == "uniqueness" and constraint.get("scope") == "external":
                place(address, constraint, [
                    (str(ref.get("fact_type")), str(ref.get("role"))) for ref in constraint.get("role_refs") or ()])
            else:
                unmapped[address] = "not-relational"

        unique_keys: dict[str, tuple[tuple[str, ...], ...]] = {}
        for table, body in self.tables.items():
            if "unique_keys" in body:
                unique_keys[table] = tuple(tuple(key) for key in body["unique_keys"])
            else:  # none declared: the model's own, one per column set, in column order
                unique_keys[table] = tuple(sorted(
                    derived[table].values(), key=lambda key: [position[table][c] for c in key]))
        for address, table, columns in pending:
            if columns == frozenset(self.tables[table].get("primary_key", ())):
                carried[address] = ("primary_key", table)
            elif any(columns == frozenset(key) for key in unique_keys[table]):
                carried[address] = ("unique_key", table, *sorted(columns, key=position[table].__getitem__))
            else:
                unmapped[address] = "not-in-binding"

        foreign_keys = name_foreign_keys({table: self.foreign_keys(table) for table in self.tables})
        tables = tuple(
            Table(
                table, ("table", table),
                tuple(Column(column, None, True, ("binding", table)) for column in self.tables[table]["columns"]),
                tuple(self.tables[table].get("primary_key", ())), unique_keys[table], foreign_keys[table],
            )
            for table in sorted(self.tables)
        )
        return RelationalSchema(
            None, tables,
            tuple(Unmapped(kind, ident, reason) for (kind, ident), reason in sorted(unmapped.items())),  # type: ignore[arg-type]
            tuple(sorted(placements, key=lambda p: (p.fact_type, p.role))),
            tuple(self.identifications()),
            tuple(sorted(carried.items())),
        )

    def identifications(self) -> list[Identification]:
        """How each object type is identified, as the ontology declares it; the mapping
        compares these with the ontology view and never guesses beyond it."""
        result = []
        for object_type in sorted(self.objects):
            width = self.arity(object_type)
            if width is None:
                continue
            table = self.homes.get(object_type)
            if self.objects[object_type]["kind"] == "value":
                result.append(Identification(object_type, "value", (object_type,), (None,), None))
                continue
            components = self.components(object_type)
            if components is None:
                columns = self.home_key(object_type, table) if table else (object_type,)
                result.append(Identification(object_type, "direct", columns, (None,), table))  # type: ignore[arg-type]
                continue
            origins: list[tuple[str, str]] = []
            for fact, role, player in components:
                origins += [(fact, role)] * (self.arity(player) or 0)
            columns = self.home_key(object_type, table) if table else tuple(f"{f}.{r}" for f, r in origins)
            result.append(Identification(object_type, "composite", columns, tuple(origins), table))  # type: ignore[arg-type]
        return result

    def extension_roles(self) -> list[dict[str, Any]]:
        rows = []
        for (section, fact, role), columns in sorted(self.bound.items()):
            if section == "extension_roles":
                tables = sorted({table for table, _column in columns})
                rows.append({
                    "fact_type": fact, "role": role,
                    "table": tables[0] if len(tables) == 1 else None,
                    "columns": [column if len(tables) == 1 else f"{table}.{column}" for table, column in columns],
                })
        return rows

    def fields(self) -> dict[tuple[str, str], tuple[str | None, str | None]]:
        """(table, column) -> (Ossie data type or None, raw SQL type or None)."""
        return {
            (table, column): (sql_datatype(body["sql_type"]) if "sql_type" in body else None, body.get("sql_type"))
            for table, column, body in self.columns()
        }


@dataclass(frozen=True)
class Bound:
    """What a binding gives the relational files: the schema, each field's type, and
    the members the mapping's extension carries."""

    schema: RelationalSchema
    fields: Mapping[tuple[str, str], tuple[str | None, str | None]]
    extension: Mapping[str, Any]


def bind(model: Any, view: OntologyView, binding: Binding) -> Bound:
    """Resolve a binding against a model: names first, then contradictions."""
    binder = _Binder(model, view, binding)
    binder.check_names()
    binder.check_contradictions()
    return Bound(
        binder.schema(), binder.fields(),
        {"binding_sha256": binding.sha256, "extension_roles": binder.extension_roles()},
    )
