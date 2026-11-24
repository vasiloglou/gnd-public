"""Halpin's relational mapping (Rmap) of a loaded GND model.

The normative rules have one home: "Relational mapping (Rmap)" in
``gnd-orm-core/references/representation-format.md``. This module implements
them; it reads a loaded :class:`gnd.model.Model` and returns a deterministic
:class:`RelationalSchema`. It never raises for an admitted model: whatever it
cannot place becomes an :class:`Unmapped` row with a closed reason.
"""

from __future__ import annotations

import enum
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Literal

from gnd.model_index import ModelIndex
from gnd.model_queries import primitive_for

__all__ = [
    "Column",
    "Disposition",
    "ForeignKey",
    "RelationalSchema",
    "RmapVariant",
    "Table",
    "Unmapped",
    "UnmappedReason",
    "dispositions",
    "map_model",
]


class RmapVariant(enum.Enum):
    HALPIN = "halpin"  # subtypes absorbed; symmetric 1:1 toward the first object-type id
    ALTERNATE = "alternate"  # subtypes separate; symmetric 1:1 toward more functional roles


UnmappedReason = Literal[
    "derived-computed",
    "uniqueness-not-confirmed",
    "identification-unmatchable",
    "spans-tables",
    "not-relational",
]


@dataclass(frozen=True)
class Column:
    name: str
    datatype: str | None
    nullable: bool
    origin: tuple[str, str]


@dataclass(frozen=True)
class ForeignKey:
    name: str
    columns: tuple[str, ...]
    target_table: str
    target_columns: tuple[str, ...]


@dataclass(frozen=True)
class Table:
    name: str
    subject: tuple[str, str]
    columns: tuple[Column, ...]
    primary_key: tuple[str, ...]
    unique_keys: tuple[tuple[str, ...], ...]
    foreign_keys: tuple[ForeignKey, ...]


@dataclass(frozen=True)
class Unmapped:
    kind: Literal["fact_type", "constraint", "object_type"]
    id: str
    reason: UnmappedReason
    detail: str = ""


@dataclass(frozen=True)
class Disposition:
    kind: Literal["fact_type", "constraint"]
    id: str
    carried_as: tuple[str, ...]
    reason: UnmappedReason | None


@dataclass(frozen=True)
class RelationalSchema:
    variant: RmapVariant
    tables: tuple[Table, ...]
    unmapped: tuple[Unmapped, ...]
    # The one walk's result, keyed by (kind, id); read by dispositions().
    _carried: tuple[tuple[tuple[str, str], tuple[str, ...]], ...] = field(default=(), repr=False, compare=False)


# --------------------------------------------------------------------------- helpers


def _confirmed(constraint: dict[str, Any]) -> bool:
    return constraint.get("status") == "confirmed" and constraint.get("modality") == "alethic"


def _address(fact_id: str | None, index: int) -> str:
    return f"fact_types/{fact_id}/constraints/{index}" if fact_id is not None else f"constraints/{index}"


@dataclass
class _Key:
    """Key columns of an object type, before they land in any table."""

    names: list[str]
    datatypes: list[str | None]
    origins: list[tuple[str, str]]
    # For each key column: the (fact type, role, player) of the composite component
    # that holds it, else None. Each component is a foreign key when its player has a table.
    components: list[tuple[str, str, str] | None] = field(default_factory=list)


@dataclass
class _Placed:
    rule: int
    owner: str  # object type id (rules 1-5) or fact type id (rule 6)
    subject_role: str | None = None  # rule 5: the determining role
    key_roles: tuple[str, ...] = ()  # rule 6: the primary-key roles


class _Mapper:
    def __init__(self, model: Any, variant: RmapVariant) -> None:
        self.model = model
        self.variant = variant
        self.index = ModelIndex.for_model(model)
        self.objects: dict[str, dict[str, Any]] = dict(self.index.object_types_by_id())
        # Read-only rows from the shared index (RF6: model queries go through ModelIndex).
        self.facts: list[dict[str, Any]] = list(self.index.iter_fact_types_shared())
        self.role_players: dict[str, dict[str, str]] = self.index.role_object_types()
        self.fact_by_id = {str(f.get("id")): f for f in self.facts}
        self.top: list[dict[str, Any]] = list(model.constraints or ())
        self.unmapped: dict[tuple[str, str], tuple[str, str]] = {}
        self.carried: dict[tuple[str, str], tuple[str, ...]] = {}
        self._primitive: dict[str, str | None] = {}
        self._identity: dict[str, tuple[str, Any]] = {}
        self._keys: dict[str, _Key | None] = {}
        self.placed: dict[str, _Placed] = {}
        # fact type id -> role name -> the columns that hold it (rules 3, 5 and 6).
        self.role_cols: dict[str, dict[str, list[str]]] = {}
        self.tables: dict[str, dict[str, Any]] = {}
        # Rule 0: derived fact types with no stored extension are not placed.
        self.derived: set[str] = {
            str(f.get("id")) for f in self.facts
            if f.get("derivation") == "derived" and f.get("storage") in (None, "computed")
        }
        # Objectifications keyed by their fact type's own uniqueness (A5 fallback).
        self.objectified: dict[str, dict[str, Any]] = {
            str(f.get("objectified_as")): f for f in self.facts if f.get("objectified_as")
        }
        self.fallback: set[str] = set()
        # Preferred, confirmed alethic external uniqueness per anchored entity, built once.
        # A tie on the role set is broken by the role_refs sequence itself, so declaration
        # order never decides (review r2 F2). Computed fact types identify nothing (r2 F6).
        self.identifiers: dict[str, list[tuple[str, str]]] = {}
        for constraint in self.top:
            if (
                constraint.get("type") == "uniqueness"
                and constraint.get("scope") == "external"
                and constraint.get("preferred")
                and _confirmed(constraint)
            ):
                refs = self.refs(constraint)
                anchor = self.anchor(refs)
                if anchor is not None and not any(fact in self.derived for fact, _ in refs):
                    current = self.identifiers.get(anchor)
                    if current is None or (sorted(refs), refs) < (sorted(current), current):
                        self.identifiers[anchor] = refs

    # -- identification -------------------------------------------------------------

    def primitive(self, value_type: str) -> str | None:
        if value_type not in self._primitive:
            self._primitive[value_type] = primitive_for(value_type, self.objects, variant="strict")
        return self._primitive[value_type]

    def identity(self, oid: str) -> tuple[str, Any]:
        if oid not in self._identity:
            self._identity[oid] = ("unmatchable", oid)  # a re-entrant request is unmatchable
            obj = self.objects.get(oid, {})
            parents = obj.get("subtype_of") or []
            if obj.get("kind") == "value":
                self._identity[oid] = ("value", oid)
            elif (obj.get("reference") or {}).get("mode") == "unit-based":
                self._identity[oid] = ("unit", oid)  # A3: before refscheme
            elif (direct := self.index.reference_value_types().get(oid)) is not None:
                # ModelIndex's documented cache of gnd.universe's reference resolver:
                # one walk per model instead of one per entity.
                self._identity[oid] = ("direct", direct)
            elif oid in self.identifiers:
                # The preferred, confirmed alethic external uniqueness anchored on oid
                # (review r1 F1: never the first one declared, never a deontic one).
                self._identity[oid] = ("composite", [
                    {"fact_type": fact, "role": role, "object_type": self.role_players[fact][role]}
                    for fact, role in self.identifiers[oid]
                ])
            elif parents and obj.get("inherits_reference"):
                # An inheriting subtype is identified as its first supertype is (review r2 F4).
                self._identity[oid] = self.identity(str(parents[0]))
        return self._identity[oid]

    def refs(self, constraint: dict[str, Any]) -> list[tuple[str, str]]:
        return [(str(r.get("fact_type")), str(r.get("role"))) for r in constraint.get("role_refs") or ()]

    def anchor(self, refs: list[tuple[str, str]]) -> str | None:
        """The one object type every referenced binary's other role is played by, else None."""
        anchors = set()
        for fact_type, role in refs:
            players = self.role_players.get(fact_type, {})
            if len(players) != 2 or role not in players:
                return None
            anchors.update(player for name, player in players.items() if name != role)
        return next(iter(anchors)) if len(anchors) == 1 else None

    def key(self, oid: str) -> _Key | None:
        """Key columns of an object type, or None when its identification is unmatchable."""
        if oid in self._keys:
            return self._keys[oid]
        self._keys[oid] = None  # a re-entrant request is unmatchable
        kind, payload = self.identity(oid)
        result: _Key | None
        if kind == "value":
            result = _Key([oid], [self.primitive(oid)], [("reference", oid)], [None])
        elif kind == "unit":
            result = _Key([f"{oid}_value"], ["Number"], [("reference", oid)], [None])
        elif kind == "direct":
            result = _Key([str(payload)], [self.primitive(str(payload))], [("reference", oid)], [None])
        elif kind == "composite":
            result = self.components_key(
                [(str(e["fact_type"]), str(e["role"]), str(e["object_type"])) for e in payload],
                nested=False,
            )
        else:
            result = None
        if result is None and oid in self.objectified:
            # A5: an objectification whose identification does not resolve is keyed by
            # its fact type's effective uniqueness (S8), for every use of its key (r2 F1).
            fact = self.objectified[oid]
            fid = str(fact.get("id"))
            players = self.players(fact)
            key_roles = self.primary(fact, self.effective(fact), self.roles(fact))
            result = self.components_key([(fid, role, players[role]) for role in key_roles], nested=True)
            if result is not None:
                self.fallback.add(oid)
        self._keys[oid] = result
        return result

    def components_key(self, components: list[tuple[str, str, str]], *, nested: bool) -> _Key | None:
        """Key columns from (fact type, role, player) components, in the given order.

        A value component is one column named after its role; an entity component is a
        group ``<role>_<key>``. Each component records its player, so that it becomes a
        foreign key when that player has a table (review r2 F5). Unless ``nested``, a
        composite inside a composite is not resolved.
        """
        result = _Key([], [], [], [])
        for fact_type, role, player in components:
            origin = (fact_type, role)
            if self.objects.get(player, {}).get("kind") == "value":
                result.names.append(role)
                result.datatypes.append(self.primitive(player))
                result.origins.append(origin)
                result.components.append((fact_type, role, player))
                continue
            inner = self.key(player) if nested or self.identity(player)[0] != "composite" else None
            if inner is None:
                return None
            for name, datatype in zip(inner.names, inner.datatypes):
                result.names.append(f"{role}_{name}")
                result.datatypes.append(datatype)
                result.origins.append(origin)
                result.components.append((fact_type, role, player))
        return result

    # -- the effective uniqueness set -----------------------------------------------

    def uc_roles(self, fact: dict[str, Any], constraint: dict[str, Any]) -> tuple[str, ...]:
        names = set(ModelIndex.constraint_roles(constraint))
        return tuple(r for r in self.roles(fact) if r in names)

    def effective(self, fact: dict[str, Any]) -> list[tuple[tuple[str, ...], bool]]:
        """(role tuple in role order, preferred) for the effective uniqueness set.

        With no counting uniqueness, the implied spanning one (S1). Duplicates over the
        same roles are one key, preferred if any of them is (review r1 F2).
        """
        found: dict[tuple[str, ...], bool] = {}
        for constraint in fact.get("constraints") or ():
            if constraint.get("type") != "uniqueness" or constraint.get("scope") == "external":
                continue
            if not _confirmed(constraint):
                continue
            roles = self.uc_roles(fact, constraint)
            found[roles] = found.get(roles, False) or bool(constraint.get("preferred"))
        if not found:
            return [(tuple(self.roles(fact)), False)]
        sets = {roles: set(roles) for roles in found}
        return [
            (roles, preferred) for roles, preferred in found.items()
            if not any(other < sets[roles] for other in sets.values())  # implied by a shorter one (plan F9)
        ]

    # -- placement --------------------------------------------------------------------

    def players(self, fact: dict[str, Any]) -> dict[str, str]:
        return self.role_players.get(str(fact.get("id")), {})

    def roles(self, fact: dict[str, Any]) -> list[str]:
        """Role names in declared order."""
        return list(self.players(fact))

    def owner_of(self, oid: str) -> str:
        """HALPIN absorbs an inheriting subtype into its root supertype's table."""
        if self.variant is not RmapVariant.HALPIN:
            return oid
        seen = set()
        while oid not in seen:
            seen.add(oid)
            obj = self.objects.get(oid, {})
            parents = obj.get("subtype_of") or []
            if not parents or not obj.get("inherits_reference"):
                return oid
            oid = str(parents[0])
        return oid

    def is_absorbed(self, oid: str) -> bool:
        return self.owner_of(oid) != oid

    def run(self) -> RelationalSchema:
        derived = self.derived

        functional_count: dict[str, int] = defaultdict(int)
        effective: dict[str, list[tuple[int, tuple[str, ...]]]] = {}
        for fact in self.facts:
            fid = str(fact.get("id"))
            effective[fid] = self.effective(fact)
            if fid in derived:
                continue
            players = self.players(fact)
            for roles, _ in effective[fid]:
                if len(roles) == 1 and len(players) > 1:
                    functional_count[players[roles[0]]] += 1

        # Composite identification components (rule 2): fact type id -> entity.
        components: dict[str, str] = {}
        for oid, refs in sorted(self.identifiers.items()):
            # Only an identification that resolves names key columns (review r2 F1).
            if self.identity(oid)[0] == "composite" and self.key(oid) is not None and oid not in self.fallback:
                for fact_type, _role in refs:
                    components.setdefault(fact_type, oid)

        placed = self.placed
        for fact in self.facts:
            fid = str(fact.get("id"))
            if fid in derived:
                continue
            placed[fid] = self.place(fact, effective[fid], components, functional_count)

        # Which object types get a table (S7, A4, A15).
        tabled: set[str] = set()
        for fid, p in placed.items():
            if p.rule in (1, 2, 3, 4, 5):
                tabled.add(p.owner)
        for oid, obj in self.objects.items():
            if obj.get("kind") == "entity" and obj.get("independent"):
                tabled.add(self.owner_of(oid))
        if self.variant is RmapVariant.ALTERNATE:
            # A separate subtype table references its supertype's table (review r1 F6).
            pending = list(tabled)
            while pending:
                obj = self.objects.get(pending.pop(), {})
                supers = obj.get("subtype_of") or []
                if supers and obj.get("inherits_reference") and str(supers[0]) not in tabled:
                    tabled.add(str(supers[0]))
                    pending.append(str(supers[0]))

        return self.build(derived, effective, placed, tabled)

    def place(self, fact, eff, components, functional_count) -> _Placed:
        fid = str(fact.get("id"))
        roles = self.roles(fact)
        players = self.players(fact)
        singles = [r[0] for r, _ in eff if len(r) == 1 and len(roles) > 1]
        # Rule 1: the reference fact type of a popular or general reference (S4).
        if len(roles) == 2:
            for role in roles:
                other = roles[1 - roles.index(role)]
                entity = self.objects.get(players[role], {})
                reference = entity.get("reference") or {}
                if (
                    entity.get("kind") == "entity"
                    and reference.get("mode") in ("popular", "general")
                    and reference.get("value_type") == players[other]
                    and other in singles
                ):
                    return _Placed(1, self.owner_of(players[role]), subject_role=role)
        # Rule 2: an identification component.
        if fid in components:
            return _Placed(2, self.owner_of(components[fid]))
        # Rule 3: objectified.
        if fact.get("objectified_as"):
            return _Placed(3, str(fact.get("objectified_as")))
        # Rule 4: unary.
        if len(roles) == 1:
            return _Placed(4, self.owner_of(players[roles[0]]), subject_role=roles[0])
        # Rule 5: functional on a single role.
        if singles:
            subject = self.subject(fact, singles, players, roles, functional_count)
            return _Placed(5, self.owner_of(players[subject]), subject_role=subject)
        # Rule 6: own table.
        return _Placed(6, fid, key_roles=self.primary(fact, eff, roles))

    def subject(self, fact, singles, players, roles, functional_count) -> str:
        if len(singles) == 1:
            return singles[0]
        mandatory = {
            str(c.get("role"))
            for c in fact.get("constraints") or ()
            if c.get("type") == "mandatory" and _confirmed(c)
        }
        covered = [r for r in singles if r in mandatory]
        if len(covered) == 1:
            return covered[0]
        position = {r: i for i, r in enumerate(roles)}
        if self.variant is RmapVariant.HALPIN:
            return min(singles, key=lambda r: (players[r], position[r]))
        return min(singles, key=lambda r: (-functional_count[players[r]], players[r], position[r]))

    def primary(self, fact, eff, roles) -> tuple[str, ...]:
        position = {r: i for i, r in enumerate(roles)}
        preferred = [r for r, flag in eff if flag]
        if preferred:
            return min(preferred, key=lambda r: tuple(sorted(position[x] for x in r)))
        return min((r for r, _ in eff), key=lambda r: (len(r), tuple(sorted(position[x] for x in r))))

    # -- building tables --------------------------------------------------------------

    def build(self, derived, effective, placed, tabled) -> RelationalSchema:
        tables = self.tables
        unusable: set[str] = set()  # object types whose identification is unmatchable

        def new_table(name, subject):
            tables[name] = {"subject": subject, "columns": [], "names": set(), "pk": [], "uks": {}, "fks": [], "groups": [], "position": {}}
            return tables[name]

        def add_column(table, base, datatype, nullable, origin):
            name, n = base, 1
            while name in table["names"]:
                n += 1
                name = f"{base}_{n}"
            table["names"].add(name)
            table["position"][name] = len(table["columns"])
            table["columns"].append(Column(name, datatype, nullable, origin))
            return name

        # Object-type tables with their key columns first (A2).
        for oid in sorted(tabled):
            if oid in self.fact_by_id:
                continue
            key = self.key(oid)
            if key is None:
                unusable.add(oid)
                continue
            table = new_table(oid, ("object_type", oid))
            names = [add_column(table, n, d, False, o) for n, d, o in zip(key.names, key.datatypes, key.origins)]
            table["pk"] = names
            self.add_component_groups(table, names, key)
            supers = self.objects.get(oid, {}).get("subtype_of") or []
            if (
                self.variant is RmapVariant.ALTERNATE
                and supers
                and self.objects[oid].get("inherits_reference")
            ):
                table["groups"].append((tuple(table["pk"]), str(supers[0])))

        # Placements in fact type id order, roles in role order (A2).
        for fact in sorted(self.facts, key=lambda f: str(f.get("id"))):
            fid = str(fact.get("id"))
            if fid in derived:
                self.unmapped[("fact_type", fid)] = ("derived-computed", "")
                continue
            p = placed[fid]
            players = self.players(fact)
            roles = self.roles(fact)
            if p.rule != 6 and p.owner in unusable:
                self.unmapped[("fact_type", fid)] = ("identification-unmatchable", "")
                continue
            unresolved = [
                x for x in (players[r] for r in roles)
                if self.objects.get(x, {}).get("kind") != "value" and self.key(x) is None
            ]
            if p.rule in (3, 5, 6) and unresolved:
                unusable.update(unresolved)
                self.unmapped[("fact_type", fid)] = ("identification-unmatchable", "")
                continue
            if p.rule in (1, 2):
                key = self.key(p.owner)
                table = tables[p.owner]
                if p.rule == 1:
                    cols = [table["pk"][0]]
                else:
                    cols = [n for n, o in zip(table["pk"], key.origins) if o[0] == fid]
                self.carried[("fact_type", fid)] = ("key", p.owner, *cols)
            elif p.rule == 3:
                self.objectify(fact, tables[p.owner], players, roles, add_column)
            elif p.rule == 4:
                table = tables[p.owner]
                name = add_column(table, fid, "Boolean", self.is_absorbed(players[roles[0]]), (fid, roles[0]))
                self.carried[("fact_type", fid)] = ("columns", p.owner, name)
            elif p.rule == 5:
                table = tables[p.owner]
                absorbed = self.is_absorbed(players[p.subject_role])
                not_null = (not absorbed) and any(
                    c.get("type") == "mandatory" and _confirmed(c) and str(c.get("role")) == p.subject_role
                    for c in fact.get("constraints") or ()
                )
                added: list[str] = []
                columns_by_role: dict[str, list[str]] = {p.subject_role: list(table["pk"])}
                for role in roles:
                    if role == p.subject_role:
                        continue
                    names = self.role_columns(table, role, players[role], (fid, role), not not_null, add_column)
                    columns_by_role[role] = names
                    added.extend(names)
                self.carried[("fact_type", fid)] = ("columns", p.owner, *added)
                self.role_cols[fid] = columns_by_role
            else:
                table = new_table(fid, ("fact_type", fid))
                columns_by_role = {}
                for role in roles:
                    columns_by_role[role] = self.role_columns(table, role, players[role], (fid, role), False, add_column)
                table["pk"] = [c for r in p.key_roles for c in columns_by_role[r]]
                self.carried[("fact_type", fid)] = ("table", fid)
                self.role_cols[fid] = columns_by_role

        self.constraint_dispositions(derived, effective, placed, tables, unusable)

        # Foreign keys, named per (from, to) pair in column order (A11).
        built: list[Table] = []
        for name in sorted(tables):
            t = tables[name]
            counts: dict[str, int] = defaultdict(int)
            fks = []
            for columns, player in t["groups"]:
                target = self.owner_of(player)
                if target not in tables or not tables[target]["pk"]:
                    continue
                counts[target] += 1
                suffix = "" if counts[target] == 1 else f"__{counts[target]}"
                fks.append(ForeignKey(f"{name}__{target}{suffix}", tuple(columns), target, tuple(tables[target]["pk"])))
            position = {c.name: i for i, c in enumerate(t["columns"])}
            uks = sorted((tuple(u) for u in t["uks"].values()), key=lambda u: [position[c] for c in u])
            built.append(Table(name, t["subject"], tuple(t["columns"]), tuple(t["pk"]), tuple(uks), tuple(fks)))

        for oid in sorted(unusable):
            self.unmapped[("object_type", oid)] = ("identification-unmatchable", "")
        unmapped = tuple(
            Unmapped(kind, ident, reason, detail)  # type: ignore[arg-type]
            for (kind, ident), (reason, detail) in sorted(self.unmapped.items())
        )
        carried = tuple(sorted(self.carried.items()))
        return RelationalSchema(self.variant, tuple(built), unmapped, carried)

    def add_component_groups(self, table, names, key: _Key) -> None:
        """Foreign-key groups for composite components, one per (fact type, role)."""
        groups: dict[tuple[str, str, str], list[str]] = {}
        for name, component in zip(names, key.components):
            if component is not None:
                groups.setdefault(component, []).append(name)
        for (_fact, _role, player), columns in groups.items():
            table["groups"].append((tuple(columns), player))

    def role_columns(self, table, role, player, origin, nullable, add_column) -> list[str]:
        if self.objects.get(player, {}).get("kind") == "value":
            name = add_column(table, role, self.primitive(player), nullable, origin)
            table["groups"].append(((name,), player))  # a foreign key when the value type has a table (r1 F7)
            return [name]
        key = self.key(player)
        names = [add_column(table, f"{role}_{n}", d, nullable, origin) for n, d in zip(key.names, key.datatypes)]
        table["groups"].append((tuple(names), player))
        return names

    def objectify(self, fact, table, players, roles, add_column) -> None:
        """Rule 3 (A5): match the fact type's roles to the key's components by player."""
        fid = str(fact.get("id"))
        oid = str(fact.get("objectified_as"))
        key = self.key(oid)
        if oid in self.fallback:  # keyed by the fact type's effective uniqueness (S8)
            by_role: dict[str, list[str]] = defaultdict(list)
            for name, (_fact, role) in zip(table["pk"], key.origins):
                by_role[role].append(name)
            columns = {
                r: by_role[r] if r in by_role else self.role_columns(table, r, players[r], (fid, r), False, add_column)
                for r in roles
            }
            self.role_cols[fid] = columns
            extra = [c for r in roles if r not in by_role for c in columns[r]]
            self.carried[("fact_type", fid)] = ("columns", oid, *extra) if extra else ("key", oid, *table["pk"])
            return
        by_player: dict[str, list[str]] = defaultdict(list)
        for name, origin in zip(table["pk"], key.origins):
            fact_type, role = origin
            component = self.fact_by_id.get(fact_type)
            player = self.players(component).get(role) if component else None
            if player is not None:
                by_player[player].append(name)
        counts = defaultdict(int)
        for r in roles:
            counts[players[r]] += 1
        matched: list[str] = []
        extra: list[str] = []
        columns: dict[str, list[str]] = {}
        for r in roles:
            player = players[r]
            if counts[player] == 1 and by_player.get(player):
                columns[r] = list(by_player[player])
                matched.extend(columns[r])
            else:
                columns[r] = self.role_columns(table, r, player, (fid, r), False, add_column)
                extra.extend(columns[r])
        self.role_cols[fid] = columns
        if extra:
            self.carried[("fact_type", fid)] = ("columns", oid, *extra)
        else:
            self.carried[("fact_type", fid)] = ("key", oid, *matched)

    # -- constraints ------------------------------------------------------------------

    def constraint_dispositions(self, derived, effective, placed, tables, unusable) -> None:
        for fact in self.facts:
            fid = str(fact.get("id"))
            eff_roles = {roles for roles, _ in effective.get(fid, ())}
            for index, constraint in enumerate(fact.get("constraints") or ()):
                address = ("constraint", _address(fid, index))
                kind = constraint.get("type")
                if fid in derived:
                    self.unmapped[address] = ("derived-computed", "")
                    continue
                if ("fact_type", fid) in self.unmapped:
                    self.unmapped[address] = self.unmapped[("fact_type", fid)]
                    continue
                p = placed[fid]
                if kind == "uniqueness":
                    if not _confirmed(constraint):
                        self.unmapped[address] = ("uniqueness-not-confirmed", "")
                        continue
                    self.carried[address] = self.uniqueness(fact, constraint, p, eff_roles, tables)
                elif kind == "mandatory":
                    role = str(constraint.get("role"))
                    if p.rule in (1, 2) and _confirmed(constraint) and role == self.subject_of_key(fact, p):
                        self.carried[address] = ("primary_key", p.owner)
                    elif (
                        p.rule == 5
                        and _confirmed(constraint)
                        and role == p.subject_role
                        and not self.is_absorbed(self.players(fact)[role])
                    ):
                        cols = self.carried[("fact_type", fid)][2:]
                        self.carried[address] = ("not_null", p.owner, *cols)
                    else:
                        self.unmapped[address] = ("not-relational", "mandatory")
                else:
                    self.unmapped[address] = ("not-relational", str(kind))
        for index, constraint in enumerate(self.top):
            address = ("constraint", _address(None, index))
            if constraint.get("type") == "uniqueness" and constraint.get("scope") == "external":
                if not _confirmed(constraint):
                    self.unmapped[address] = ("uniqueness-not-confirmed", "")
                    continue
                self.external(constraint, index, address, tables)
            else:
                self.unmapped[address] = ("not-relational", str(constraint.get("type")))

    def subject_of_key(self, fact, p) -> str | None:
        """The role of a rule-1 or rule-2 fact type that is played by the identified entity."""
        for role, player in self.players(fact).items():
            if self.owner_of(player) == p.owner:
                return role
        return None

    def uniqueness(self, fact, constraint, p, eff_roles, tables) -> tuple[str, ...]:
        """One disposition per uniqueness; duplicates over the same roles share it (r1 F2)."""
        fid = str(fact.get("id"))
        if p.rule in (1, 2):
            return ("primary_key", p.owner)
        roles = self.uc_roles(fact, constraint)
        if p.rule == 4 or roles not in eff_roles:
            return ("implied", p.owner)
        if p.rule == 6 and roles == tuple(p.key_roles):
            return ("primary_key", p.owner)
        if p.rule == 5 and roles == (p.subject_role,):
            return ("placement", p.owner)
        columns = self.role_cols[fid]
        if p.rule == 5:
            columns = {**columns, p.subject_role: list(tables[p.owner]["pk"])}
        cols = [c for r in roles for c in columns[r]]
        return self.unique_key(tables[p.owner], p.owner, cols)

    def unique_key(self, table, name, cols) -> tuple[str, ...]:
        """One key per column set: a later uniqueness over the same columns shares it (r2 F3, F8)."""
        columns = frozenset(cols)
        if columns == frozenset(table["pk"]):
            return ("primary_key", name)
        existing = table["uks"].setdefault(columns, list(cols))
        return ("unique_key", name, *existing)

    def location(self, fact_type: str, role: str) -> tuple[str, list[str]] | None:
        """The table and columns that hold one role of a placed fact type."""
        p = self.placed.get(fact_type)
        if p is None or ("fact_type", fact_type) in self.unmapped or p.owner not in self.tables:
            return None
        table = self.tables[p.owner]
        if p.rule in (3, 5, 6):
            columns = self.role_cols.get(fact_type, {})
            if p.rule == 5 and role == p.subject_role:
                return p.owner, list(table["pk"])
            return (p.owner, list(columns[role])) if role in columns else None
        if p.rule == 4:
            # A unary role is played by the row's own object: its key, not the flag (r2 F7).
            return p.owner, list(table["pk"])
        if self.owner_of(self.role_players[fact_type][role]) == p.owner:
            return p.owner, list(table["pk"])
        return p.owner, list(self.carried[("fact_type", fact_type)][2:])

    def external(self, constraint, index, address, tables) -> None:
        refs = self.refs(constraint)
        anchor = self.anchor(refs)
        identifying = self.identifiers.get(anchor) if anchor is not None else None
        if identifying is not None and set(identifying) == set(refs):
            # The identifier, or a duplicate over the same roles: one key (review r2 F2).
            owner = self.owner_of(anchor)
            if (
                self.identity(anchor)[0] == "composite"
                and self.key(anchor) is not None
                and anchor not in self.fallback
                and owner in tables
            ):
                self.carried[address] = ("primary_key", owner)
            else:
                self.unmapped[address] = ("identification-unmatchable", "")
            return
        # Any other external uniqueness: a unique key when its columns lie in one table (r1 F4).
        places = [self.location(fact_type, role) for fact_type, role in refs]
        if all(place is not None for place in places) and len({place[0] for place in places}) == 1:
            table_name = places[0][0]
            position = tables[table_name]["position"]
            # Columns in table order, each once: role_refs order never shapes the key (r2 F3).
            cols = sorted({c for _, columns in places for c in columns}, key=position.__getitem__)
            self.carried[address] = self.unique_key(tables[table_name], table_name, cols)
            return
        reasons = {self.unmapped[("fact_type", f)][0] for f, _ in refs if ("fact_type", f) in self.unmapped}
        self.unmapped[address] = (next(iter(sorted(reasons))), "") if reasons else ("spans-tables", "")


def map_model(model: Any, *, variant: RmapVariant = RmapVariant.HALPIN) -> RelationalSchema:
    """Map one loaded model to its relational schema; never raises for an admitted model."""
    return _Mapper(model, variant).run()


def dispositions(model: Any, schema: RelationalSchema) -> tuple[Disposition, ...]:
    """Exactly one row per fact type and per constraint: carried (where) or unmapped (why)."""
    carried = dict(schema._carried)
    reasons = {(u.kind, u.id): u.reason for u in schema.unmapped}
    keys: list[tuple[str, str]] = []
    for fact in ModelIndex.for_model(model).iter_fact_types_shared():
        fid = str(fact.get("id"))
        keys.append(("fact_type", fid))
        keys.extend(("constraint", _address(fid, i)) for i, _ in enumerate(fact.get("constraints") or ()))
    keys.extend(("constraint", _address(None, i)) for i, _ in enumerate(model.constraints or ()))
    rows = []
    for key in sorted(keys):
        if key in carried:
            rows.append(Disposition(key[0], key[1], carried[key], None))  # type: ignore[arg-type]
        elif key in reasons:
            rows.append(Disposition(key[0], key[1], (), reasons[key]))  # type: ignore[arg-type]
        else:  # an internal invariant: the walk must place or list every element
            raise RuntimeError(f"rmap: no disposition for {key[0]} {key[1]!r}")
    return tuple(rows)
