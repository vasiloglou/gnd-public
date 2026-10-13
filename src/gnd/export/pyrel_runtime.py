"""Independent constraint translation runtime shared by oracle and exporter.

This module imports no GND module and is copied verbatim into standalone exports.
It reads raw YAML 1.2 rather than production-loader objects. Interpretation
independence is limited by the inherited conventions recorded in the v5.2
Phase 1 record. The export interface is documented in docs/pyrel-export.md;
mode semantics originate in the v5.2 plan's Dual-runtime evaluation directive.
"""

from __future__ import annotations

import argparse
import datetime
import json
import math
import os
import re
import stat
import sys
import tempfile
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError

SCHEMA_VERSION = 1
WITNESS_CAP = 25

# Bound only by the standalone artifact trailer; importing this module is inert.
MODEL_TEXT = ""
MODEL_NAME = ""
EXPORT_CONFIG: dict[str, Any] = {"duckdb_path": ":memory:", "connection": None}

_TIME_RELATIVE = {"now()", "now", "today", "today()", "current_date", "current_date()",
                  "current_time", "current_time()", "current_timestamp", "current_timestamp()"}

_NEGATED_OP = {">=": "<", ">": "<=", "<=": ">", "<": ">=", "=": "!=", "==": "!=",
               "!=": "=", "<>": "="}



def _load_yaml(path: Path) -> dict[str, Any]:
    return load_document(path)


def _scalar(value: Any) -> Any:
    """Normalise a YAML scalar: dates back to ISO strings (lexical order)."""
    if isinstance(value, datetime.datetime):
        return value.isoformat()
    if isinstance(value, datetime.date):
        return value.isoformat()
    return value


def _jsonable(value: Any) -> Any:
    if hasattr(value, "item"):
        return value.item()
    return _scalar(value)


class ModelIndex:
    """Read-only index over the raw model.orm.yaml document."""

    def __init__(self, doc: dict[str, Any]):
        self.doc = doc
        self.object_types = {ot["id"]: ot for ot in doc.get("object_types", [])}
        self.fact_types = {ft["id"]: ft for ft in doc.get("fact_types", [])}

    def roles(self, ft_id: str) -> list[dict[str, Any]]:
        return self.fact_types[ft_id].get("roles", [])

    def role_object_type(self, ft_id: str, role_name: str) -> str | None:
        for role in self.roles(ft_id):
            if role.get("role_name") == role_name:
                return role.get("object_type")
        return None

    def primitive(self, ot_id: str) -> str | None:
        """Resolve an object type to a primitive, mirroring the loader's walk."""
        seen: set[str] = set()

        def walk(oid: str, seen: set[str]) -> str | None:
            if oid in seen or oid not in self.object_types:
                return None
            seen.add(oid)
            ot = self.object_types[oid]
            if ot.get("kind") == "value":
                return ot.get("primitive")
            reference = ot.get("reference") or {}
            if reference.get("value_type"):
                return walk(reference["value_type"], seen)
            if ot.get("inherits_reference") is True:
                found = {p for p in (walk(sup, set(seen)) for sup in ot.get("subtype_of", [])) if p}
                if len(found) == 1:
                    return found.pop()
            return None

        return walk(ot_id, seen)

    def descendants(self, ot_id: str) -> set[str]:
        """The object type plus its transitive subtypes."""
        result = {ot_id}
        changed = True
        while changed:
            changed = False
            for oid, ot in self.object_types.items():
                if oid not in result and any(sup in result for sup in ot.get("subtype_of", [])):
                    result.add(oid)
                    changed = True
        return result

    def reference_value_type(self, ot_id: str) -> str | None:
        """The value type an entity type's reference scheme resolves to."""
        ot = self.object_types.get(ot_id)
        if ot is None or ot.get("kind") != "entity":
            return None
        reference = ot.get("reference") or {}
        if reference.get("value_type"):
            return reference["value_type"]
        if ot.get("inherits_reference") is True:
            found = {v for v in (self.reference_value_type(sup) for sup in ot.get("subtype_of", []))
                     if v}
            if len(found) == 1:
                return found.pop()
        return None


class PyrelOracle:
    """Builds one PyRel model per (model, population) pair and evaluates constraints."""

    def __init__(self, model: ModelIndex, population: dict[str, Any], *,
                 config: dict[str, Any] | None = None):
        from relationalai.config import Config
        from relationalai.semantics import Model

        self.model = model
        self.facts: dict[str, list[dict[str, Any]]] = {
            ft_id: [dict(fact) for fact in rows or []]
            for ft_id, rows in (population.get("facts") or {}).items()
        }
        self.instances: dict[str, list[Any]] = {
            ot_id: [_scalar(v) for v in values or []]
            for ot_id, values in (population.get("instances") or {}).items()
        }
        self.m = Model("gnd_constraint_oracle", config=Config(**(config or local_config())))
        self._relations: dict[str, Any] = {}
        self._concepts: dict[str, list[Any]] = {}
        self._universes: dict[str, Any] = {}
        self._universe_values: dict[str, set[Any]] = {}
        self._closure_counter = 0
        self._define_fact_relations()
        self.entity_concepts: dict[str, Any] = {}
        for ordinal, (oid, declaration) in enumerate(model.object_types.items()):
            if declaration.get("kind") != "entity":
                continue
            values = self.universe_values(oid)
            primitive = self._concept_for(model.primitive(oid), next(iter(values), None))
            concept = self.m.Concept(f"entity_{ordinal}", identify_by={"key": primitive},
                                     identity_includes_type=True)
            self.entity_concepts[oid] = concept
            if values:
                self.m.define(*[concept.new(key=self._coerce(primitive, value))
                                for value in sorted(values, key=repr)])

    # ------------------------------------------------------------------ setup

    def _concept_for(self, primitive: str | None, sample: Any = None) -> Any:
        from relationalai.semantics import Boolean, Float, Int, String

        table = {"String": String, "Date": String, "DateTime": String, "Binary": String,
                 "Integer": Int, "Float": Float, "Number": Float, "Boolean": Boolean}
        if primitive in table:
            return table[primitive]
        if isinstance(sample, bool):
            return Boolean
        if isinstance(sample, int):
            return Int
        if isinstance(sample, float):
            return Float
        return String

    def _coerce(self, concept: Any, value: Any) -> Any:
        from relationalai.semantics import Float, Int, String

        value = _scalar(value)
        if concept is Int:
            return int(value)
        if concept is Float:
            return float(value)
        if concept is String:
            return str(value)
        return value

    def _define_fact_relations(self) -> None:
        from relationalai.semantics import Int
        from relationalai.semantics.frontend.base import Field

        for ft_ordinal, ft_id in enumerate(self.model.fact_types):
            roles = self.model.roles(ft_id)
            rows = self.facts.get(ft_id, [])
            concepts = []
            for role in roles:
                primitive = self.model.primitive(role.get("object_type", ""))
                sample = next(
                    (_scalar(r[role["role_name"]]) for r in rows if role["role_name"] in r), None
                )
                concepts.append(self._concept_for(primitive, sample))
            fields = [Field(role["role_name"], concept)
                      for role, concept in zip(roles, concepts, strict=True)]
            fields.append(Field("gnd_ord", Int))
            relation = self.m.Relationship(fields=fields, short_name=f"ft_{ft_ordinal}")
            self._relations[ft_id] = relation
            self._concepts[ft_id] = concepts
            atoms = []
            for ordinal, row in enumerate(rows):
                args = [self._coerce(concept, row[role["role_name"]])
                        for role, concept in zip(roles, concepts, strict=True)]
                atoms.append(relation(*args, ordinal))
            if atoms:
                self.m.define(*atoms)

    def universe_values(self, ot_id: str) -> set[Any]:
        """Closed-world population of an object type (population-format.md)."""
        if ot_id in self._universe_values:
            return self._universe_values[ot_id]
        members = self.model.descendants(ot_id)
        values: set[Any] = set()
        for member in members:
            values.update(self.instances.get(member, []))
        for ft_id in self.model.fact_types:
            rows = self.facts.get(ft_id, [])
            if not rows:
                continue
            for role in self.model.roles(ft_id):
                role_ot = role.get("object_type")
                contributes = role_ot in members
                if not contributes and role_ot:
                    # Reference widening: a value type collects the values that
                    # identify entities under it. One direction only.
                    ref_vt = self.model.reference_value_type(role_ot)
                    contributes = ref_vt in members if ref_vt else False
                if contributes:
                    values.update(_scalar(r[role["role_name"]])
                                  for r in rows if role["role_name"] in r)
        self._universe_values[ot_id] = values
        return values

    def universe(self, ot_id: str) -> Any:
        """A unary PyRel relation holding the object type's closed-world population."""
        from relationalai.semantics.frontend.base import Field

        if ot_id in self._universes:
            return self._universes[ot_id]
        values = self.universe_values(ot_id)
        primitive = self.model.primitive(ot_id)
        concept = self._concept_for(primitive, next(iter(values), None))
        relation = self.m.Relationship(fields=[Field("member", concept)],
                                       short_name=f"inst_{list(self.model.object_types).index(ot_id)}")
        if values:
            self.m.define(*[relation(self._coerce(concept, v)) for v in sorted(values, key=repr)])
        self._universes[ot_id] = (relation, concept)
        return self._universes[ot_id]

    # ------------------------------------------------------------ query helpers

    def refs(self, ft_id: str) -> dict[str, Any]:
        """Fresh refs for every role of a fact type, by role name."""
        return {role["role_name"]: concept.ref()
                for role, concept in zip(self.model.roles(ft_id), self._concepts[ft_id],
                                         strict=True)}

    def pattern(self, ft_id: str, bind: dict[str, Any]) -> Any:
        """A relation atom with ``bind`` at named roles, fresh refs elsewhere."""
        from relationalai.semantics import Int

        args = []
        for role, concept in zip(self.model.roles(ft_id), self._concepts[ft_id], strict=True):
            name = role["role_name"]
            args.append(bind[name] if name in bind else concept.ref())
        ordinal = bind.get("gnd_ord")
        args.append(ordinal if ordinal is not None else Int.ref())
        return self._relations[ft_id](*args)

    def _rows(self, fragment: Any) -> list[list[Any]]:
        frame = fragment.to_df()
        rows = [[_jsonable(v) for v in row] for row in frame.itertuples(index=False)]
        rows.sort(key=repr)
        return rows

    def _witnesses(self, *queries: Any) -> list[list[Any]]:
        seen: list[list[Any]] = []
        for query in queries:
            for row in self._rows(query):
                if row not in seen:
                    seen.append(row)
        return seen

    def _closure(self, ft_id: str, left: str, right: str) -> Any:
        """Transitive closure of a binary fact type, as a fresh relation."""
        from relationalai.semantics.frontend.base import Field

        self._closure_counter += 1
        concept = self._concepts[ft_id][0]
        reach = self.m.Relationship(
            fields=[Field("a", concept), Field("b", concept)],
            short_name=f"reach_{self._closure_counter}",
        )
        a, b, c = concept.ref(), concept.ref(), concept.ref()
        self.m.where(self.pattern(ft_id, {left: a, right: b})).define(reach(a, b))
        self.m.where(reach(a, b), self.pattern(ft_id, {left: b, right: c})).define(reach(a, c))
        return reach

    # -------------------------------------------------------------- evaluators

    def evaluate(self, constraint: dict[str, Any], ft_id: str | None) -> tuple[str, Any]:
        """Return (status, witnesses-or-reason) for one constraint."""
        family = constraint.get("type")
        if family == "anchored":
            return "unsupported", "anchored-needs-bound-source-document"
        handlers = {
            "uniqueness": self._uniqueness,
            "mandatory": self._mandatory,
            "mandatory-disjunctive": self._mandatory_disjunctive,
            "value": self._value,
            "frequency": self._frequency,
            "ring": self._ring,
            "subset": self._subset,
            "equality": self._equality,
            "exclusion": self._exclusion,
            "exclusive-or": self._exclusive_or,
            "value-comparison": self._value_comparison,
            "cardinality": self._cardinality,
            "subtype-partition": self._subtype_partition,
        }
        handler = handlers.get(family)
        if handler is None:
            return "unsupported", f"family-not-evaluated:{family}"
        return handler(constraint, ft_id)

    def _decide(self, witnesses: list[list[Any]]) -> tuple[str, list[list[Any]]]:
        if witnesses:
            return "violated", witnesses[:WITNESS_CAP]
        return "satisfied", []

    def _uniqueness(self, constraint: dict[str, Any], ft_id: str | None) -> tuple[str, Any]:
        from relationalai.semantics import Int, count

        if constraint.get("scope") == "external" or ft_id is None:
            return self._external_group(constraint, lambda n, anchors: n > 1, count_join=False)
        covered = list(constraint.get("roles", []))
        refs = self.refs(ft_id)
        ordinal = Int.ref()
        group = [refs[name] for name in covered]
        query = (self.m
                 .where(self.pattern(ft_id, {**refs, "gnd_ord": ordinal}),
                        count(ordinal).per(*group) > 1)
                 .select(*group))
        return self._decide(self._witnesses(query))

    def _external_group(self, constraint: dict[str, Any], breach: Any,
                        count_join: bool) -> tuple[str, Any]:
        """Shared join machinery for external uniqueness / frequency.

        Joins exactly two fact types on their shared-object-type anchor roles
        (the non-referenced roles) and groups by the referenced-role tuple.
        ``breach(count_expr, anchor_refs)`` returns the violation condition.
        """
        from relationalai.semantics import Int, count

        role_refs = constraint.get("role_refs", [])
        ft_ids = [ref["fact_type"] for ref in role_refs]
        if len(set(ft_ids)) != 2:
            return "unsupported", "external-join-needs-exactly-two-fact-types"
        ft_a, ft_b = sorted(set(ft_ids), key=ft_ids.index)
        referenced = {(ref["fact_type"], ref["role"]) for ref in role_refs}
        anchors = []
        for role_a in self.model.roles(ft_a):
            if (ft_a, role_a["role_name"]) in referenced:
                continue
            for role_b in self.model.roles(ft_b):
                if (ft_b, role_b["role_name"]) in referenced:
                    continue
                if role_a.get("object_type") == role_b.get("object_type"):
                    anchors.append((role_a["role_name"], role_b["role_name"],
                                    role_a.get("object_type")))
        if not anchors:
            return "unsupported", "external-join-disconnected"
        bind_a: dict[str, Any] = {"gnd_ord": Int.ref()}
        bind_b: dict[str, Any] = {"gnd_ord": Int.ref()}
        anchor_refs = []
        for name_a, name_b, anchor_ot in anchors:
            primitive = self.model.primitive(anchor_ot or "")
            shared = self._concept_for(primitive).ref()
            bind_a[name_a] = shared
            bind_b[name_b] = shared
            anchor_refs.append(shared)
        group = []
        for ref in role_refs:
            target = bind_a if ref["fact_type"] == ft_a else bind_b
            ot = self.model.role_object_type(ref["fact_type"], ref["role"])
            var = self._concept_for(self.model.primitive(ot or "")).ref()
            target[ref["role"]] = var
            group.append(var)
        counted = ([*anchor_refs, bind_a["gnd_ord"], bind_b["gnd_ord"]]
                   if count_join else anchor_refs)
        tally = count(*counted).per(*group)
        query = (self.m
                 .where(self.pattern(ft_a, bind_a), self.pattern(ft_b, bind_b),
                        breach(tally, anchor_refs))
                 .select(*group))
        return self._decide(self._witnesses(query))

    def _mandatory(self, constraint: dict[str, Any], ft_id: str | None) -> tuple[str, Any]:
        if ft_id is None:
            return "unsupported", "mandatory-without-fact-type"
        role_name = constraint.get("role")
        ot = self.model.role_object_type(ft_id, role_name)
        if ot is None:
            return "unsupported", "mandatory-role-unresolved"
        relation, concept = self.universe(ot)
        member = concept.ref()
        from relationalai.semantics import not_

        query = (self.m
                 .where(relation(member), not_(self.pattern(ft_id, {role_name: member})))
                 .select(member))
        return self._decide(self._witnesses(query))

    def _mandatory_disjunctive(self, constraint: dict[str, Any],
                               ft_id: str | None) -> tuple[str, Any]:
        from relationalai.semantics import not_

        role_refs = constraint.get("role_refs", [])
        object_types = {self.model.role_object_type(ref["fact_type"], ref["role"])
                        for ref in role_refs}
        if len(object_types) != 1 or None in object_types:
            return "unsupported", "disjunctive-roles-not-one-object-type"
        relation, concept = self.universe(object_types.pop())
        member = concept.ref()
        absences = [not_(self.pattern(ref["fact_type"], {ref["role"]: member}))
                    for ref in role_refs]
        query = self.m.where(relation(member), *absences).select(member)
        return self._decide(self._witnesses(query))

    def _value(self, constraint: dict[str, Any], ft_id: str | None) -> tuple[str, Any]:
        if constraint.get("ranges") is not None:
            return "unsupported", "multi-range-not-evaluated"
        role_ref = constraint.get("role_ref")
        if role_ref is not None:
            ot = self.model.role_object_type(role_ref["fact_type"], role_ref["role"])
            concept = self._concept_for(self.model.primitive(ot or ""))
            member = concept.ref()

            def anchor() -> Any:
                return self.pattern(role_ref["fact_type"], {role_ref["role"]: member})
        else:
            relation, concept = self.universe(constraint["object_type"])
            member = concept.ref()

            def anchor() -> Any:
                return relation(member)

        def scope(*conditions: Any) -> Any:
            return self.m.where(anchor(), *conditions).select(member)

        allowed = constraint.get("allowed")
        if allowed is not None:
            return self._decide(self._witnesses(
                scope(*[member != self._coerce(concept, v) for v in allowed])))

        bounds = constraint.get("range")
        if bounds is None:
            return "unsupported", "value-without-allowed-or-range"
        # A DateTime range bound is compared lexically here and chronologically by
        # the production checker (_in_range parses and normalizes). Measured: min
        # 2026-01-01T00:00:00Z with value 2025-12-31T20:00:00-05:00 is INSIDE the
        # range chronologically and BELOW it lexically. An `allowed` enum needs no
        # such decline: the checker tests enum membership on textual identity,
        # which is exactly what this oracle does.
        if self._value_primitive(constraint, role_ref) == "DateTime":
            return "unsupported", "datetime-needs-instant-normalization"
        queries = []
        minimum, maximum = bounds.get("min"), bounds.get("max")
        if minimum is not None:
            low = self._coerce(concept, minimum)
            queries.append(scope(member < low if bounds.get("min_inclusive", True)
                                 else member <= low))
        if maximum is not None:
            high = self._coerce(concept, maximum)
            queries.append(scope(member > high if bounds.get("max_inclusive", True)
                                 else member >= high))
        return self._decide(self._witnesses(*queries))

    def _frequency(self, constraint: dict[str, Any], ft_id: str | None) -> tuple[str, Any]:
        from relationalai.semantics import Int, count

        bounds = constraint.get("bound") or {}
        minimum, maximum = bounds.get("min"), bounds.get("max")
        if constraint.get("scope") == "external" or ft_id is None:
            def breach(tally: Any, anchors: Any) -> Any:
                if maximum is not None and minimum is not None:
                    return (tally > maximum) | (tally < minimum)
                if maximum is not None:
                    return tally > maximum
                return tally < minimum
            return self._external_group(constraint, breach, count_join=True)
        covered = list(constraint.get("roles", []))
        refs = self.refs(ft_id)
        ordinal = Int.ref()
        group = [refs[name] for name in covered]
        queries = []
        if maximum is not None:
            queries.append(self.m.where(self.pattern(ft_id, {**refs, "gnd_ord": ordinal}),
                                        count(ordinal).per(*group) > maximum)
                           .select(*group))
        if minimum is not None:
            queries.append(self.m.where(self.pattern(ft_id, {**refs, "gnd_ord": ordinal}),
                                        count(ordinal).per(*group) < minimum)
                           .select(*group))
        return self._decide(self._witnesses(*queries))

    def _ring_components(self, variant: str) -> list[str]:
        composites = {
            "asymmetric-intransitive": ["asymmetric", "intransitive"],
            "acyclic-intransitive": ["acyclic", "intransitive"],
            "symmetric-irreflexive": ["symmetric", "irreflexive"],
            "symmetric-intransitive": ["symmetric", "intransitive"],
        }
        return composites.get(variant, [variant])

    def _ring(self, constraint: dict[str, Any], ft_id: str | None) -> tuple[str, Any]:
        from relationalai.semantics import not_

        if ft_id is None:
            return "unsupported", "ring-without-fact-type"
        roles = self.model.roles(ft_id)
        if len(roles) != 2:
            return "unsupported", "ring-needs-binary-fact-type"
        left, right = roles[0]["role_name"], roles[1]["role_name"]
        concept = self._concepts[ft_id][0]
        queries: list[Any] = []
        for component in self._ring_components(constraint.get("variant", "")):
            x, y, z = concept.ref(), concept.ref(), concept.ref()
            if component == "irreflexive":
                queries.append(self.m.where(self.pattern(ft_id, {left: x, right: x}))
                               .select(x))
            elif component == "asymmetric":
                queries.append(self.m.where(self.pattern(ft_id, {left: x, right: y}),
                                            self.pattern(ft_id, {left: y, right: x}))
                               .select(x, y))
            elif component == "antisymmetric":
                queries.append(self.m.where(self.pattern(ft_id, {left: x, right: y}),
                                            self.pattern(ft_id, {left: y, right: x}),
                                            x != y)
                               .select(x, y))
            elif component == "intransitive":
                queries.append(self.m.where(self.pattern(ft_id, {left: x, right: y}),
                                            self.pattern(ft_id, {left: y, right: z}),
                                            self.pattern(ft_id, {left: x, right: z}))
                               .select(x, y, z))
            elif component == "transitive":
                queries.append(self.m.where(self.pattern(ft_id, {left: x, right: y}),
                                            self.pattern(ft_id, {left: y, right: z}),
                                            not_(self.pattern(ft_id, {left: x, right: z})))
                               .select(x, y, z))
            elif component == "acyclic":
                reach = self._closure(ft_id, left, right)
                queries.append(self.m.where(reach(x, x)).select(x))
            elif component == "symmetric":
                queries.append(self.m.where(self.pattern(ft_id, {left: x, right: y}),
                                            not_(self.pattern(ft_id, {left: y, right: x})))
                               .select(x, y))
            elif component == "purely-reflexive":
                queries.append(self.m.where(self.pattern(ft_id, {left: x, right: y}), x != y)
                               .select(x, y))
            elif component == "reflexive":
                # Locally reflexive over domain ∪ range (GND's recorded reading).
                queries.append(self.m.where(self.pattern(ft_id, {left: x}),
                                            not_(self.pattern(ft_id, {left: x, right: x})))
                               .select(x))
                w = concept.ref()
                queries.append(self.m.where(self.pattern(ft_id, {right: w}),
                                            not_(self.pattern(ft_id, {left: w, right: w})))
                               .select(w))
            else:
                return "unsupported", f"ring-variant-unknown:{component}"
        return self._decide(self._witnesses(*queries))

    def _sequence_binding(self, sequence: list[dict[str, Any]]) -> tuple[str, list[Any]] | None:
        """(fact_type, refs) for a role sequence confined to one fact type."""
        ft_ids = {ref["fact_type"] for ref in sequence}
        if len(ft_ids) != 1:
            return None
        ft_id = ft_ids.pop()
        refs = []
        for ref in sequence:
            ot = self.model.role_object_type(ft_id, ref["role"])
            refs.append(self._concept_for(self.model.primitive(ot or "")).ref())
        return ft_id, refs

    def _seq_pattern(self, sequence: list[dict[str, Any]], ft_id: str,
                     refs: list[Any]) -> Any:
        bind = {ref["role"]: var for ref, var in zip(sequence, refs, strict=True)}
        return self.pattern(ft_id, bind)

    def _subset(self, constraint: dict[str, Any], ft_id: str | None) -> tuple[str, Any]:
        from relationalai.semantics import not_

        return self._one_direction(constraint.get("subset_role_seq", []),
                                   constraint.get("superset_role_seq", []), not_)

    def _one_direction(self, sub_seq: list[dict[str, Any]], sup_seq: list[dict[str, Any]],
                       not_: Any) -> tuple[str, Any]:
        sub = self._sequence_binding(sub_seq)
        sup = self._sequence_binding(sup_seq)
        if sub is None or sup is None or len(sub_seq) != len(sup_seq):
            return "unsupported", "role-sequence-spans-fact-types"
        sub_ft, refs = sub
        sup_ft, _ = sup
        query = (self.m
                 .where(self._seq_pattern(sub_seq, sub_ft, refs),
                        not_(self._seq_pattern(sup_seq, sup_ft, refs)))
                 .select(*refs))
        return self._decide(self._witnesses(query))

    def _equality(self, constraint: dict[str, Any], ft_id: str | None) -> tuple[str, Any]:
        from relationalai.semantics import not_

        forward = self._one_direction(constraint.get("role_seq_a", []),
                                      constraint.get("role_seq_b", []), not_)
        backward = self._one_direction(constraint.get("role_seq_b", []),
                                       constraint.get("role_seq_a", []), not_)
        for status, payload in (forward, backward):
            if status == "unsupported":
                return status, payload
        witnesses = [w for status, payload in (forward, backward)
                     if status == "violated" for w in payload]
        return self._decide(witnesses)

    def _exclusion(self, constraint: dict[str, Any], ft_id: str | None) -> tuple[str, Any]:
        seq_a = constraint.get("role_seq_a", [])
        seq_b = constraint.get("role_seq_b", [])
        side_a = self._sequence_binding(seq_a)
        side_b = self._sequence_binding(seq_b)
        if side_a is None or side_b is None or len(seq_a) != len(seq_b):
            return "unsupported", "role-sequence-spans-fact-types"
        ft_a, refs = side_a
        ft_b, _ = side_b
        query = (self.m
                 .where(self._seq_pattern(seq_a, ft_a, refs),
                        self._seq_pattern(seq_b, ft_b, refs))
                 .select(*refs))
        return self._decide(self._witnesses(query))

    def _exclusive_or(self, constraint: dict[str, Any], ft_id: str | None) -> tuple[str, Any]:
        from relationalai.semantics import not_

        sequences = constraint.get("role_seqs", [])
        if any(len(seq) != 1 for seq in sequences) or len(sequences) < 2:
            return "unsupported", "xor-multi-role-sequences"
        refs = [seq[0] for seq in sequences]
        object_types = {self.model.role_object_type(ref["fact_type"], ref["role"])
                        for ref in refs}
        if len(object_types) != 1 or None in object_types:
            return "unsupported", "xor-roles-not-one-object-type"
        relation, concept = self.universe(object_types.pop())
        member = concept.ref()
        queries = []
        for i in range(len(refs)):
            for j in range(i + 1, len(refs)):
                queries.append(
                    self.m.where(self.pattern(refs[i]["fact_type"], {refs[i]["role"]: member}),
                                 self.pattern(refs[j]["fact_type"], {refs[j]["role"]: member}))
                    .select(member))
        absences = [not_(self.pattern(ref["fact_type"], {ref["role"]: member})) for ref in refs]
        queries.append(self.m.where(relation(member), *absences).select(member))
        return self._decide(self._witnesses(*queries))

    def _value_comparison(self, constraint: dict[str, Any],
                          ft_id: str | None) -> tuple[str, Any]:
        operator = constraint.get("operator", "")
        negated = _NEGATED_OP.get(operator)
        if negated is None:
            return "unsupported", f"operator-unknown:{operator}"

        def is_time_relative(operand: Any) -> bool:
            return isinstance(operand, str) and operand.strip().lower() in _TIME_RELATIVE

        role_a, role_b = constraint.get("role_a"), constraint.get("role_b")
        if self._has_datetime_operand(ft_id, role_a, role_b):
            # DateTime is carried as PyRel String, so EVERY comparison here is
            # lexical. The production checker parses DateTime operands, rewrites a
            # trailing Z, and normalizes offset-aware values to UTC before
            # comparing -- for ordering AND for equality. Measured: with
            # 2026-01-01T00:00:00Z and 2025-12-31T19:00:00-05:00, production
            # equality is True while textual equality is False. An earlier
            # narrowing of this decline to ordering operators asserted the
            # opposite and was wrong.
            return "unsupported", "datetime-needs-instant-normalization"
        if is_time_relative(role_a) or is_time_relative(role_b):
            return "unsupported", "time-relative-operand"
        if (is_time_relative((role_a or {}).get("literal") if isinstance(role_a, dict) else None)
                or is_time_relative((role_b or {}).get("literal")
                                    if isinstance(role_b, dict) else None)):
            return "unsupported", "time-relative-operand"

        def compare(left: Any, right: Any) -> Any:
            return {"<": left < right, "<=": left <= right, ">": left > right,
                    ">=": left >= right, "=": left == right, "!=": left != right}[negated]

        cross = (isinstance(role_a, dict) and "fact_type" in role_a
                 and isinstance(role_b, dict) and "fact_type" in role_b)
        if cross:
            synthetic = {"role_refs": [role_a, role_b]}
            outcome = self._cross_comparison(synthetic, compare)
            return outcome
        if ft_id is None:
            return "unsupported", "value-comparison-shape"

        role_names = {role["role_name"] for role in self.model.roles(ft_id)}

        def resolve(operand: Any, other_concept: Any) -> tuple[str, Any] | None:
            """('role', name) or ('literal', coerced value); None when unresolvable."""
            if isinstance(operand, dict):
                if "role" in operand and "fact_type" not in operand:
                    return ("role", operand["role"])
                if "literal" in operand:
                    return ("literal", self._coerce(other_concept, operand["literal"]))
                return None
            if isinstance(operand, str) and operand in role_names:
                return ("role", operand)
            return ("literal", operand)

        concepts = {role["role_name"]: concept
                    for role, concept in zip(self.model.roles(ft_id), self._concepts[ft_id],
                                             strict=True)}
        kind_a = resolve(role_a, None)
        if kind_a is None or kind_a[0] != "role":
            return "unsupported", "value-comparison-shape"
        concept_a = concepts[kind_a[1]]
        kind_b = resolve(role_b, concept_a)
        if kind_b is None:
            return "unsupported", "value-comparison-shape"
        left = concept_a.ref()
        bind = {kind_a[1]: left}
        if kind_b[0] == "role":
            right = concepts[kind_b[1]].ref()
            bind[kind_b[1]] = right
        else:
            right = self._coerce(concept_a, kind_b[1])
        query = (self.m.where(self.pattern(ft_id, bind), compare(left, right))
                 .select(*[v for v in bind.values()]))
        return self._decide(self._witnesses(query))

    def _value_primitive(self, constraint: dict[str, Any], role_ref: Any) -> str | None:
        """The primitive a value constraint ranges over, role-scoped or object-scoped."""
        if role_ref is not None:
            ot = self.model.role_object_type(role_ref["fact_type"], role_ref["role"])
        else:
            ot = constraint.get("object_type")
        return self.model.primitive(ot) if ot else None

    def _has_datetime_operand(self, ft_id: str | None, *operands: Any) -> bool:
        """True when any operand resolves to a role whose primitive is DateTime."""
        for operand in operands:
            if isinstance(operand, dict) and "role" in operand:
                owner = operand.get("fact_type") or ft_id
                if owner is None:
                    continue
                ot = self.model.role_object_type(owner, operand["role"])
            elif isinstance(operand, str) and ft_id is not None:
                ot = self.model.role_object_type(ft_id, operand)
            else:
                continue
            if ot and self.model.primitive(ot) == "DateTime":
                return True
        return False

    def _cross_comparison(self, synthetic: dict[str, Any], compare: Any) -> tuple[str, Any]:
        """Cross-fact-type comparison joined on shared anchor roles."""
        from relationalai.semantics import Int

        role_refs = synthetic["role_refs"]
        ft_a, ft_b = role_refs[0]["fact_type"], role_refs[1]["fact_type"]
        if ft_a == ft_b:
            return "unsupported", "value-comparison-shape"
        referenced = {(ref["fact_type"], ref["role"]) for ref in role_refs}
        bind_a: dict[str, Any] = {"gnd_ord": Int.ref()}
        bind_b: dict[str, Any] = {"gnd_ord": Int.ref()}
        joined = False
        for role_a in self.model.roles(ft_a):
            if (ft_a, role_a["role_name"]) in referenced:
                continue
            for role_b in self.model.roles(ft_b):
                if (ft_b, role_b["role_name"]) in referenced:
                    continue
                if role_a.get("object_type") == role_b.get("object_type"):
                    shared = self._concept_for(
                        self.model.primitive(role_a.get("object_type") or "")).ref()
                    bind_a[role_a["role_name"]] = shared
                    bind_b[role_b["role_name"]] = shared
                    joined = True
        if not joined:
            return "unsupported", "external-join-disconnected"
        ot_a = self.model.role_object_type(ft_a, role_refs[0]["role"])
        ot_b = self.model.role_object_type(ft_b, role_refs[1]["role"])
        left = self._concept_for(self.model.primitive(ot_a or "")).ref()
        right = self._concept_for(self.model.primitive(ot_b or "")).ref()
        bind_a[role_refs[0]["role"]] = left
        bind_b[role_refs[1]["role"]] = right
        query = (self.m
                 .where(self.pattern(ft_a, bind_a), self.pattern(ft_b, bind_b),
                        compare(left, right))
                 .select(left, right))
        return self._decide(self._witnesses(query))

    def _count_scalar(self, query: Any) -> int:
        rows = self._rows(query)
        if not rows or rows[0][0] is None:
            return 0
        return int(rows[0][0])

    def _cardinality(self, constraint: dict[str, Any], ft_id: str | None) -> tuple[str, Any]:
        from relationalai.semantics import count

        bounds = constraint.get("bound") or {}
        if constraint.get("scope") == "object":
            relation, concept = self.universe(constraint["object_type"])
            member = concept.ref()
            observed = (self._count_scalar(self.m.where(relation(member)).select(count(member)))
                        if self.universe_values(constraint["object_type"]) else 0)
        elif constraint.get("scope") == "role":
            role_ref = constraint["role_ref"]
            ot = self.model.role_object_type(role_ref["fact_type"], role_ref["role"])
            member = self._concept_for(self.model.primitive(ot or "")).ref()
            has_rows = bool(self.facts.get(role_ref["fact_type"]))
            observed = (self._count_scalar(
                self.m.where(self.pattern(role_ref["fact_type"], {role_ref["role"]: member}))
                .select(count(member))) if has_rows else 0)
        else:
            return "unsupported", "cardinality-scope-unknown"
        minimum, maximum = bounds.get("min"), bounds.get("max")
        breached = ((minimum is not None and observed < minimum)
                    or (maximum is not None and observed > maximum))
        if breached:
            return "violated", [[observed]]
        return "satisfied", []

    def _subtype_partition(self, constraint: dict[str, Any],
                           ft_id: str | None) -> tuple[str, Any]:
        from relationalai.semantics import not_

        supertype = constraint.get("supertype")
        subtypes = constraint.get("subtypes", [])
        if not supertype or not subtypes:
            return "unsupported", "partition-shape"
        if not (constraint.get("exclusive") or constraint.get("exhaustive")):
            return "unsupported", "partition-asserts-nothing"
        # A subtype whose membership exists only behind an opaque derivation rule
        # is not decidable from an ASSERTED population: absent members mean
        # "not stated", not "empty". Deciding here would report a violation on a
        # population that states nothing — so decline instead. This reads the
        # population/model format, not the production checker's branch: the
        # oracle says it cannot evaluate the shape, and adopts no GND policy.
        for subtype in subtypes:
            declaration = self.model.object_types.get(subtype) or {}
            if (not self.universe_values(subtype)
                    and declaration.get("derivation") == "derived"):
                return "unsupported", "subtype-membership-derivation-only"
        super_rel, concept = self.universe(supertype)
        member = concept.ref()
        sub_rels = [self.universe(sub)[0] for sub in subtypes]
        queries = []
        if constraint.get("exclusive"):
            for i in range(len(sub_rels)):
                for j in range(i + 1, len(sub_rels)):
                    queries.append(self.m.where(sub_rels[i](member), sub_rels[j](member))
                                   .select(member))
        if constraint.get("exhaustive"):
            absences = [not_(rel(member)) for rel in sub_rels]
            queries.append(self.m.where(super_rel(member), *absences).select(member))
        return self._decide(self._witnesses(*queries))


def _constraint_entries(model: ModelIndex) -> list[tuple[str, dict[str, Any], str | None]]:
    """(constraint_ref, constraint, enclosing fact type id) in checker order."""
    entries: list[tuple[str, dict[str, Any], str | None]] = []
    for ft_id, fact_type in model.fact_types.items():
        for index, constraint in enumerate(fact_type.get("constraints", [])):
            entries.append((f"fact_types[{ft_id}].constraints[{index}]", constraint, ft_id))
    for index, constraint in enumerate(model.doc.get("constraints", [])):
        entries.append((f"constraints[{index}]", constraint, None))
    return entries



class ExportInputError(ValueError):
    """Malformed input to the independent export reader/compiler."""


class _UsageParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        self.print_usage(sys.stderr)
        self.exit(64, f"{self.prog}: error: {message}\n")


def _read_text(path: Path, *, max_bytes: int = 16_777_216) -> str:
    if not stat.S_ISREG(path.stat().st_mode):
        raise ExportInputError(f"not a regular input file: {path}")
    with path.open("rb") as handle:
        data = handle.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise ExportInputError(f"input exceeds {max_bytes} bytes: {path}")
    try:
        return data.decode("utf-8")
    except UnicodeError as error:
        raise ExportInputError(f"input is not UTF-8: {path}") from error


def _parse_document(text: str) -> dict[str, Any]:
    try:
        document = YAML(typ="safe").load(text)
        if not isinstance(document, dict):
            raise ExportInputError("document must be a mapping")
        # An iterative walk detects recursive aliases and bounds expanded work.
        stack = [(document, frozenset(), 0)]
        visited = 0
        while stack:
            value, ancestors, depth = stack.pop()
            visited += 1
            if visited > 1_000_000 or depth > 128:
                raise ExportInputError("document nesting or expanded size exceeds limit")
            if isinstance(value, (dict, list)):
                if id(value) in ancestors:
                    raise ExportInputError("recursive aliases are not supported")
                children = value.values() if isinstance(value, dict) else value
                if isinstance(value, dict) and any(not isinstance(k, str) for k in value):
                    raise ExportInputError("mapping keys must be strings")
                chain = ancestors | {id(value)}
                stack.extend((item, chain, depth + 1) for item in children)
            elif isinstance(value, float) and not math.isfinite(value):
                raise ExportInputError("nonfinite numeric value")
            elif isinstance(value, int) and value.bit_length() > 4096:
                raise ExportInputError("integer exceeds supported size")
            elif not isinstance(value, (str, int, float, bool, datetime.date, type(None))):
                raise ExportInputError("unsupported scalar value")
        return document
    except (YAMLError, ValueError, TypeError, RecursionError, OverflowError) as error:
        if isinstance(error, ExportInputError):
            raise
        raise ExportInputError(f"malformed document: {error}") from error


def load_document(path: Path, *, max_bytes: int = 16_777_216) -> dict[str, Any]:
    """Bounded YAML 1.2 admission, independent of production GND loaders.

    Missing files and operational I/O errors remain distinct from malformed data.
    This admits document shapes, not all GND model semantics.
    """
    return _parse_document(_read_text(path, max_bytes=max_bytes))


def _declarations(value: Any, label: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or any(not isinstance(row, dict) for row in value):
        raise ExportInputError(f"{label} must be a list of mappings")
    return value


def _constraints(value: Any, role_names: set[str] | None = None) -> None:
    for constraint in _declarations(value, "constraints"):
        if not isinstance(constraint.get("type"), str):
            raise ExportInputError("constraint type must be a string")
        for key in ("roles", "allowed", "subtypes", "subset_role_seq", "superset_role_seq",
                    "role_sequences", "ranges"):
            if key in constraint and not isinstance(constraint[key], list):
                raise ExportInputError(f"constraint {key} must be a list")
        for key in ("role", "roles"):
            if key not in constraint:
                continue
            names = constraint[key] if key == "roles" else [constraint[key]]
            if any(not isinstance(name, str) or not name or
                   (role_names is not None and name not in role_names) for name in names):
                raise ExportInputError(f"constraint {key} must name existing roles")
        for key in ("bound", "range", "role_ref"):
            if key in constraint and not isinstance(constraint[key], dict):
                raise ExportInputError(f"constraint {key} must be a mapping")


def _admit_model(document: dict[str, Any]) -> ModelIndex:
    """Validate consumed model structure and resolvable single-value identity.

    Unsupported constraint families are retained. This is not GND validate.
    """
    if not isinstance(document, dict):
        raise ExportInputError("model must be a mapping")
    objects = _declarations(document.get("object_types"), "object_types")
    facts = _declarations(document.get("fact_types"), "fact_types")
    for rows, label in ((objects, "object_types"), (facts, "fact_types")):
        ids = [row.get("id") for row in rows]
        if any(not isinstance(oid, str) or not oid for oid in ids) or len(set(ids)) != len(ids):
            raise ExportInputError(f"{label} ids must be unique nonempty strings")
    index = ModelIndex(document)
    primitives = {"String", "Date", "DateTime", "Binary", "Integer", "Float", "Number", "Boolean"}
    for obj in objects:
        if obj.get("kind") not in {"entity", "value"}:
            raise ExportInputError("object kind must be entity or value")
        if obj.get("kind") == "value" and obj.get("primitive") not in primitives:
            raise ExportInputError(f"unsupported primitive: {obj.get('primitive')}")
        supers = obj.get("subtype_of", [])
        if not isinstance(supers, list) or any(
            not isinstance(s, str) or s not in index.object_types for s in supers
        ):
            raise ExportInputError("invalid subtype references")
        if "reference" in obj and not isinstance(obj["reference"], dict):
            raise ExportInputError("reference must be a mapping")
        reference = obj.get("reference", {})
        if reference and (reference.get("mode") not in {"popular", "unit-based", "general", "external"} or
                          set(reference) - {"mode", "value_type"} or
                          (reference.get("mode") != "external" and
                           reference.get("value_type") not in index.object_types)):
            raise ExportInputError("unsupported or unresolved reference scheme")
    # Resolve references once with cycle detection and memoization; ModelIndex's
    # inherited transcription is retained only after this boundary is checked.
    resolved: dict[str, str | None] = {}
    active: set[str] = set()

    def resolve(oid: str) -> str | None:
        if oid in active:
            raise ExportInputError("cyclic reference inheritance")
        if oid in resolved:
            return resolved[oid]
        active.add(oid)
        obj = index.object_types[oid]
        value_type = None
        if obj["kind"] == "value":
            value_type = oid
        elif obj.get("reference", {}).get("mode") == "external":
            value_type = ""  # supplied opaque identity; do not synthesize a compound key
        elif obj.get("reference"):
            value_type = obj["reference"].get("value_type")
            if not value_type or index.object_types[value_type]["kind"] != "value":
                raise ExportInputError("entity reference must name a value type")
        elif obj.get("inherits_reference") is True:
            candidates = {resolve(sup) for sup in obj.get("subtype_of", [])}
            if len(candidates) == 1:
                value_type = candidates.pop()
        if value_type is None:
            raise ExportInputError(f"unrepresentable reference identity: {oid}")
        active.remove(oid)
        resolved[oid] = value_type
        return value_type

    try:
        for oid in index.object_types:
            resolve(oid)
    except RecursionError as error:
        raise ExportInputError("reference inheritance exceeds supported depth") from error
    for fact in facts:
        roles = _declarations(fact.get("roles"), "roles")
        names = [r.get("role_name") for r in roles]
        if not roles or any(not isinstance(n, str) or not n for n in names):
            raise ExportInputError("fact roles must have nonempty names")
        if len(set(names)) != len(names) or "gnd_ord" in names:
            raise ExportInputError("duplicate or reserved role name")
        if any(r.get("object_type") not in index.object_types for r in roles):
            raise ExportInputError("unknown role object type")
        _constraints(fact.get("constraints", []), set(names))
    _constraints(document.get("constraints", []))
    return index


def admit_model(document: dict[str, Any]) -> ModelIndex:
    try:
        return _admit_model(document)
    except (TypeError, KeyError, ValueError, RecursionError) as error:
        if isinstance(error, ExportInputError):
            raise
        raise ExportInputError(f"malformed model structure: {error}") from error


def admit_population(document: dict[str, Any], model: ModelIndex) -> None:
    if not isinstance(document, dict):
        raise ExportInputError("population must be a mapping")
    for field in ("facts", "instances"):
        if not isinstance(document.get(field, {}), dict):
            raise ExportInputError(f"population {field} must be a mapping")
    for ft_id, rows in document.get("facts", {}).items():
        if ft_id not in model.fact_types:
            raise ExportInputError(f"unknown fact type: {ft_id}")
        for row in _declarations(rows, "facts"):
            roles = model.roles(ft_id)
            if set(row) != {r["role_name"] for r in roles}:
                raise ExportInputError(f"missing or extra roles in {ft_id}")
            for role in roles:
                _admit_scalar(row[role["role_name"]], model.primitive(role["object_type"]))
    for oid, values in document.get("instances", {}).items():
        if oid not in model.object_types or not isinstance(values, list):
            raise ExportInputError("invalid instance roster")
        for value in values:
            _admit_scalar(value, model.primitive(oid))


def _valid_temporal(value: Any, primitive: str) -> bool:
    # Independent implementation of the population format's ISO scalar grammar.
    # Keep strings canonical for the compiler's lexical Date comparisons.
    pattern = (r"\d{4}-\d{2}-\d{2}" if primitive == "Date" else
               r'[0-9]{4}-[0-9]{2}-[0-9]{2}T(?:[01][0-9]|2[0-3]):[0-5][0-9](?::[0-5][0-9](?:\.[0-9]{1,6})?)?(?:Z|[+-](?:[01][0-9]|2[0-3]):[0-5][0-9])?')
    if not isinstance(value, str) or re.fullmatch(pattern, value) is None:
        return False
    try:
        if primitive == "Date":
            datetime.date.fromisoformat(value)
        else:
            datetime.datetime.fromisoformat(value[:-1] + "+00:00" if value[-1:] in ("Z", "z") else value)
    except ValueError:
        return False
    return True


def _admit_scalar(value: Any, primitive: str | None) -> None:
    valid = {
        "Integer": type(value) is int,
        "Float": type(value) in (int, float), "Number": type(value) in (int, float),
        "Boolean": type(value) is bool,
        "String": isinstance(value, str), "Binary": isinstance(value, str),
        "Date": _valid_temporal(value, "Date"),
        "DateTime": _valid_temporal(value, "DateTime"),
        None: type(value) in (str, int, float, bool),
    }.get(primitive, False)
    if not valid or (isinstance(value, float) and not math.isfinite(value)):
        raise ExportInputError(f"invalid scalar for {primitive}")


def local_config(path: str = ":memory:") -> dict[str, Any]:
    return {"connections": {"local": {"type": "duckdb", "path": path}},
            "default_connection": "local",
            "deployment": {"schema": "gnd_oracle", "auto_deploy": True}}


def evaluate_document(model: dict[str, Any], population: dict[str, Any], *,
                      mode: str, config: dict[str, Any]) -> list[dict[str, Any]]:
    index = admit_model(model)
    admit_population(population, index)
    if mode not in {"select", "require"}:
        raise ExportInputError(f"unknown mode: {mode}")
    if "RAI_BUILD_DIR" not in os.environ:
        os.environ.setdefault("RAI_BUILD_DIR", tempfile.mkdtemp(prefix="gnd-pyrel-build-"))
    oracle = PyrelOracle(index, population, config=config) if mode == "select" else None
    verdicts = []
    for ref, constraint, ft_id in _constraint_entries(index):
        entry = {"constraint_ref": ref, "constraint_type": constraint["type"]}
        if mode == "require":
            entry.update(status="unsupported", reason="require-mode-needs-lqp-runtime")
        else:
            try:
                status, payload = oracle.evaluate(constraint, ft_id)
                entry["status"] = status
                if status == "violated":
                    entry["witnesses"] = payload
                elif status == "unsupported":
                    entry["reason"] = payload
            except Exception as error:  # noqa: BLE001 -- preserve per-constraint failure
                entry.update(status="error", reason=f"{type(error).__name__}: {error}"[:300])
        verdicts.append(entry)
    return verdicts


def report_document(model: dict[str, Any], population: dict[str, Any], *, mode: str,
                    config: dict[str, Any], model_name: str, population_name: str) -> dict[str, Any]:
    verdicts = evaluate_document(model, population, mode=mode, config=config)
    package_version = "1.30.1"  # declared dependency only when require is reserved
    if mode == "select":
        from importlib.metadata import version
        package_version = version("relationalai")
    return {"schema_version": SCHEMA_VERSION, "oracle": "pyrel",
            "package": {"name": "relationalai", "version": package_version},
            "backend": "duckdb-local", "mode": mode, "model": model_name,
            "population": population_name, "verdicts": verdicts}


def run(model_path: Path, population_path: Path, mode: str) -> dict[str, Any]:
    return report_document(load_document(model_path), load_document(population_path), mode=mode,
                           config=local_config(), model_name=str(model_path),
                           population_name=str(population_path))


def write_new(path: Path, text: str) -> None:
    """Create one artifact exclusively; remove only our own partial inode on error."""
    handle = path.open("x", encoding="utf-8")
    identity = os.fstat(handle.fileno())
    try:
        with handle:
            handle.write(text)
    except BaseException:
        try:
            current = path.lstat()
            if (current.st_dev, current.st_ino) == (identity.st_dev, identity.st_ino):
                path.unlink()
        except OSError:
            pass
        raise


# applications-v1 is opt-in; legacy report/evaluator semantics above stay frozen.
PROFILE = 'applications-v1'
PROFILE_BYTES = 1_048_576
PROFILE_ROWS = 1000
PROFILE_WORK = 100_000
PROFILE_RESULTS = 10_000


class ProfileRefusal(Exception):
    """An honest unsupported/coverage/work boundary, never a policy violation."""


def _profile_literal(value: Any, primitive: str) -> None:
    try:
        _admit_scalar(value, primitive)
    except ExportInputError as error:
        raise ProfileRefusal('literal-type:' + primitive) from error
    if type(value) is int and abs(value) > 2**53 - 1:
        raise ProfileRefusal('integer-profile-limit')


def _profile_guard(index: ModelIndex, constraint: dict[str, Any]) -> dict[str, str]:
    atoms = constraint.get('antecedent')
    consequent = constraint.get('consequent')
    if not isinstance(atoms, list) or not 1 <= len(atoms) <= 8:
        raise ProfileRefusal('guarded-antecedent-shape')
    if not isinstance(consequent, dict) or len(consequent) != 1:
        raise ProfileRefusal('guarded-consequent-shape')
    variables: dict[str, str] = {}

    def atom_shape(atom: Any, positive: bool) -> None:
        if not isinstance(atom, dict) or set(atom) != {'fact_type', 'bind'}:
            raise ProfileRefusal('guarded-atom-shape')
        name, bindings = atom['fact_type'], atom['bind']
        if not isinstance(name, str):
            raise ProfileRefusal('guarded-fact-name')
        try:
            roles = {r['role_name']: r for r in index.roles(name)}
        except KeyError as error:
            raise ProfileRefusal('guarded-unknown-fact') from error
        if not isinstance(bindings, dict) or set(bindings) - set(roles):
            raise ProfileRefusal('guarded-unknown-role')
        for role, term in bindings.items():
            primitive = index.primitive(roles[role]['object_type'])
            if isinstance(term, str) and term.startswith('$') and len(term) > 1:
                if term in variables and variables[term] != primitive:
                    raise ProfileRefusal('guarded-variable-type')
                if not positive and term not in variables:
                    raise ProfileRefusal('guarded-unbound-variable')
                variables[term] = primitive
            else:
                _profile_literal(term, primitive)

    for atom in atoms:
        atom_shape(atom, True)
    kind = next(iter(consequent))
    payload = consequent[kind]
    if kind in {'atom', 'absence'}:
        atom_shape(payload, False)
    elif kind == 'comparison':
        if not isinstance(payload, dict) or set(payload) != {'operator', 'left', 'right'}:
            raise ProfileRefusal('guarded-comparison-shape')
        operator = payload['operator']
        if not isinstance(operator, str) or operator not in _NEGATED_OP:
            raise ProfileRefusal('guarded-comparison-operator')
        primitives = []
        for term in [payload['left'], payload['right']]:
            if isinstance(term, str) and term.startswith('$') and len(term) > 1:
                if term not in variables:
                    raise ProfileRefusal('guarded-unbound-variable')
                primitives.append(variables[term])
            else:
                primitive = {str: 'String', int: 'Integer', bool: 'Boolean'}.get(type(term))
                if primitive is None:
                    raise ProfileRefusal('guarded-comparison-literal')
                _profile_literal(term, primitive)
                primitives.append(primitive)
        if primitives[0] != primitives[1]:
            raise ProfileRefusal('guarded-comparison-type')
        if primitives[0] != 'Integer' and operator not in {'=', '==', '!=', '<>'}:
            raise ProfileRefusal('guarded-nonnumeric-order')
    else:
        raise ProfileRefusal('guarded-consequent-unsupported')
    return variables


def _profile_admit(index: ModelIndex, population: dict[str, Any]) -> None:
    facts = index.fact_types
    entries = _constraint_entries(index)
    if type(index.doc.get('version')) is not int or index.doc['version'] not in {1, 2}:
        raise ProfileRefusal('model-version-not-in-application-profile')
    if set(index.doc) - {'version', 'model_id', 'source', 'object_types', 'fact_types', 'constraints'}:
        raise ProfileRefusal('model-declarations-outside-application-profile')
    if len(index.object_types) > 64 or len(facts) > 32 or len(entries) > 64:
        raise ProfileRefusal('declaration-limit')
    for document in [index.doc, population]:
        try:
            size = len(json.dumps(document, ensure_ascii=False, allow_nan=False).encode('utf-8'))
        except (TypeError, ValueError, RecursionError) as error:
            raise ExportInputError('profile requires finite JSON data') from error
        if size > PROFILE_BYTES:
            raise ProfileRefusal('document-profile-limit')
    metadata = population.get('population', {})
    if not isinstance(metadata, dict):
        raise ExportInputError('population metadata must be a mapping')
    if metadata.get('model_id') is not None and metadata['model_id'] != index.doc.get('model_id'):
        raise ExportInputError('population model_id differs from selected model')
    covers = metadata.get('covers')
    if not isinstance(covers, list) or any(not isinstance(x, str) for x in covers):
        raise ProfileRefusal('coverage-not-declared')
    rows = population.get('facts', {})
    if any(name not in covers or name not in rows for name in facts):
        raise ProfileRefusal('relation-not-covered-or-listed')
    count = sum(len(values) for values in rows.values())
    count += sum(len(values) for values in population.get('instances', {}).values())
    if count > PROFILE_ROWS:
        raise ProfileRefusal('population-row-limit')
    for declaration in index.object_types.values():
        if set(declaration) - {'id', 'name', 'kind', 'primitive', 'reference', 'inherits_reference',
                               'subtype_of', 'description'}:
            raise ProfileRefusal('object-declarations-outside-application-profile')
        primitive = index.primitive(declaration['id'])
        if primitive not in {'String', 'Integer', 'Boolean'}:
            raise ProfileRefusal('primitive-not-in-application-profile')
    for name, declaration in facts.items():
        if set(declaration) - {'id', 'reading', 'roles', 'constraints', 'derivation', 'storage', 'derivation_rule'}:
            raise ProfileRefusal('fact-declarations-outside-application-profile')
        roles = index.roles(name)
        if len(roles) > 8:
            raise ProfileRefusal('role-limit')
        if any(set(role) - {'role_name', 'object_type'} for role in roles):
            raise ProfileRefusal('role-declarations-outside-application-profile')
        if declaration.get('derivation') not in (None, 'asserted') or 'derivation_rule' in declaration:
            raise ProfileRefusal('derivation-not-yet-in-application-profile')
        if declaration.get('storage') not in (None, 'stored'):
            raise ProfileRefusal('storage-not-in-application-profile')
        for row in rows[name]:
            for role in roles:
                _profile_literal(row[role['role_name']], index.primitive(role['object_type']))
    for oid, values in population.get('instances', {}).items():
        for value in values:
            _profile_literal(value, index.primitive(oid))
    for _, constraint, ft_id in entries:
        family = constraint['type']
        common = {'type', 'id', 'source', 'status', 'modality', 'provenance', 'rationale', 'scope'}
        fields = {'guarded': {'antecedent', 'consequent'}, 'uniqueness': {'roles'},
                  'mandatory': {'role'}, 'value': {'object_type', 'allowed'},
                  'subset': {'subset_role_seq', 'superset_role_seq'}}
        if family not in fields or set(constraint) - common - fields[family]:
            raise ProfileRefusal('constraint-shape-outside-application-profile')
        if 'id' in constraint and (not isinstance(constraint['id'], str) or not constraint['id']):
            raise ProfileRefusal('constraint-label-not-string')
        if constraint.get('scope') not in (None, 'inline', 'internal'):
            raise ProfileRefusal('constraint-scope-outside-application-profile')
        if constraint.get('modality', 'alethic') not in ('alethic', 'deontic'):
            raise ProfileRefusal('unsupported-modality')
        if family == 'guarded':
            if ft_id is not None:
                raise ProfileRefusal('only-top-level-guarded')
            _profile_guard(index, constraint)
            work = 1
            for atom in constraint['antecedent']:
                work *= len(rows[atom['fact_type']])
                if work > PROFILE_WORK:
                    raise ProfileRefusal('guarded-join-work-limit')
            consequent = constraint['consequent']
            kind = next(iter(consequent))
            if kind in {'atom', 'absence'}:
                work *= max(1, len(rows[consequent[kind]['fact_type']]))
                if work > PROFILE_WORK:
                    raise ProfileRefusal('guarded-join-work-limit')
        elif family in {'uniqueness', 'mandatory'}:
            if ft_id is None or constraint.get('scope') == 'external':
                raise ProfileRefusal('only-inline-key-and-mandatory')
            if family == 'uniqueness' and not constraint.get('roles'):
                raise ProfileRefusal('uniqueness-needs-key-roles')
            if family == 'mandatory' and not isinstance(constraint.get('role'), str):
                raise ExportInputError('mandatory requires a role string')
        elif family == 'value':
            if not isinstance(constraint.get('object_type'), str):
                raise ExportInputError('value requires an object_type string')
            if ft_id is not None:
                raise ProfileRefusal('only-top-level-object-value-enum')
            if constraint.get('object_type') not in index.object_types or not isinstance(constraint.get('allowed'), list):
                raise ProfileRefusal('only-object-value-enum')
            for term in constraint['allowed']:
                _profile_literal(term, index.primitive(constraint['object_type']))
        elif family == 'subset':
            if ft_id is not None:
                raise ProfileRefusal('only-top-level-unary-subset')
            for key in ['subset_role_seq', 'superset_role_seq']:
                sequence = constraint.get(key)
                if not isinstance(sequence, list) or len(sequence) != 1 or not isinstance(sequence[0], dict):
                    raise ProfileRefusal('only-unary-projected-subset')
                ref = sequence[0]
                if not isinstance(ref.get('role'), str) or not isinstance(ref.get('fact_type'), str):
                    raise ExportInputError('subset reference requires fact_type and role strings')
                try:
                    roles = {r['role_name'] for r in index.roles(ref.get('fact_type'))}
                except (KeyError, TypeError) as error:
                    raise ProfileRefusal('subset-unknown-fact') from error
                if ref.get('role') not in roles:
                    raise ProfileRefusal('subset-unknown-role')
            sub = constraint['subset_role_seq'][0]
            sup = constraint['superset_role_seq'][0]
            if index.role_object_type(sub['fact_type'], sub['role']) != index.role_object_type(sup['fact_type'], sup['role']):
                raise ProfileRefusal('subset-role-types-outside-application-profile')
        else:
            raise ProfileRefusal('family-not-in-application-profile:' + family)


class ApplicationOracle(PyrelOracle):
    """Native policy execution for the bounded, explicitly selected profile."""

    def _mandatory(self, constraint: dict[str, Any], ft_id: str | None) -> tuple[str, Any]:
        role_name = constraint['role']
        ot = self.model.role_object_type(ft_id, role_name)
        relation, concept = self.universe(ot)
        member = concept.ref()
        query = self.m.where(relation(member), self.m.not_(self.pattern(ft_id, {role_name: member}))).select(member)
        return self._decide(self._witnesses(query))

    def _subset(self, constraint: dict[str, Any], ft_id: str | None) -> tuple[str, Any]:
        return self._one_direction(constraint['subset_role_seq'], constraint['superset_role_seq'], self.m.not_)

    def _rows(self, fragment: Any) -> list[list[Any]]:
        rows = super()._rows(fragment)
        if len(rows) > PROFILE_RESULTS:
            raise ProfileRefusal('native-result-tuple-limit')
        return rows

    def guarded(self, constraint: dict[str, Any]) -> tuple[str, Any]:
        from relationalai.semantics import Int
        from relationalai.semantics.frontend.base import Field

        primitives = _profile_guard(self.model, constraint)
        variables = {name: self._concept_for(primitive).ref() for name, primitive in primitives.items()}
        names = sorted(variables)

        def atom(pattern: dict[str, Any]) -> Any:
            bindings = {role: variables[term] if isinstance(term, str) and term in variables else term
                        for role, term in pattern['bind'].items()}
            return self.pattern(pattern['fact_type'], bindings)

        positive = [atom(pattern) for pattern in constraint['antecedent']]
        if any(not self.facts[pattern['fact_type']] for pattern in constraint['antecedent']):
            return 'vacuous', []
        selected = [variables[name] for name in names]
        if not selected:
            marker = self.m.Relationship(fields=[Field('token', Int)], short_name='profile_marker')
            self.m.define(marker(0))
            token = Int.ref()
            positive.append(marker(token))
            selected = [token]
        if not self._rows(self.m.where(*positive).select(*selected)):
            return 'satisfied', []
        kind = next(iter(constraint['consequent']))
        payload = constraint['consequent'][kind]
        extra = []
        if kind == 'atom':
            breach = self.m.not_(atom(payload))
        elif kind == 'absence':
            breach = atom(payload)
        else:
            def operand(term: Any) -> Any:
                if isinstance(term, str) and term in variables:
                    return variables[term]
                primitive = {str: 'String', int: 'Integer', bool: 'Boolean'}[type(term)]
                concept = self._concept_for(primitive)
                relation = self.m.Relationship(fields=[Field('value', concept)],
                                               short_name=f'profile_literal_{len(extra)}')
                self.m.define(relation(term))
                reference = concept.ref()
                extra.append(relation(reference))
                return reference

            left, right = operand(payload['left']), operand(payload['right'])
            operator = _NEGATED_OP[payload['operator']]
            if operator in {'=', '=='}:
                breach = left == right
            elif operator in {'!=', '<>'}:
                breach = left != right
            elif operator == '<':
                breach = left < right
            elif operator == '<=':
                breach = left <= right
            elif operator == '>':
                breach = left > right
            else:
                breach = left >= right
        rows = self._rows(self.m.where(*positive, *extra, breach).select(*selected))
        witnesses = {json.dumps(dict(zip(names, row, strict=True)) if names else {},
                                sort_keys=True, separators=(',', ':')) for row in rows}
        return ('violated', [json.loads(row) for row in sorted(witnesses)]) if witnesses else ('satisfied', [])

    def profile_evaluate(self, constraint: dict[str, Any], ft_id: str | None) -> tuple[str, Any]:
        family = constraint['type']
        if family == 'guarded':
            return self.guarded(constraint)
        if family == 'uniqueness' and not self.facts[ft_id]:
            return 'vacuous', []
        if family == 'mandatory':
            if not self.facts[ft_id]:
                return 'vacuous', []
            role = next(r for r in self.model.roles(ft_id) if r['role_name'] == constraint['role'])
            if not self.universe_values(role['object_type']):
                return 'vacuous', []
        if family == 'value' and not self.universe_values(constraint['object_type']):
            return 'vacuous', []
        if family == 'subset':
            refs = constraint['subset_role_seq'] + constraint['superset_role_seq']
            if all(not self.facts[ref['fact_type']] for ref in refs):
                return 'vacuous', []
        return self.evaluate(constraint, ft_id)


def acceptance_document(model: dict[str, Any], population: dict[str, Any], *,
                        model_sha256: str, population_sha256: str,
                        execution_refusal: str | None = None) -> dict[str, Any]:
    """Explicit acceptance; supplied hashes bind caller-owned exact input reads.

    Malformed input raises ExportInputError (the standalone CLI maps it to 3).
    Unknown coverage/shape/work and native failures return nonaccepted reports.
    """
    import uuid
    from importlib.metadata import version

    if any(not isinstance(digest, str) or re.fullmatch('[0-9a-f]{64}', digest) is None
           for digest in [model_sha256, population_sha256]):
        raise ExportInputError('bindings require lowercase SHA-256 hex')
    index = admit_model(model)
    admit_population(population, index)
    entries = _constraint_entries(index)
    verdicts = [{'constraint_ref': ref, 'id': c.get('id', ref), 'constraint_type': c['type'],
                 'modality': c.get('modality', 'alethic'), 'status': 'incomplete',
                 'witnesses': [], 'reason': None} for ref, c, _ in entries]
    report = {'schema_version': 1, 'profile': PROFILE, 'backend': 'duckdb-local',
              'status': 'incomplete', 'exit_code': 2, 'accepted': False,
              'binding': {'model_sha256': model_sha256, 'population_sha256': population_sha256},
              'verdicts': verdicts, 'derivations': []}
    try:
        _profile_admit(index, population)
        if execution_refusal is not None:
            if not isinstance(execution_refusal, str) or not execution_refusal:
                raise ExportInputError('execution refusal must be a nonempty string')
            raise ProfileRefusal(execution_refusal)
    except ProfileRefusal as error:
        for row in verdicts:
            row['reason'] = str(error)
        return report
    try:
        if version('relationalai') != '1.30.1' or version('duckdb') != '1.5.5':
            raise RuntimeError('applications-v1 requires PyRel 1.30.1/DuckDB 1.5.5')
        if 'RAI_BUILD_DIR' not in os.environ:
            os.environ['RAI_BUILD_DIR'] = tempfile.mkdtemp(prefix='gnd-application-build-')
        config = local_config()
        config['deployment']['schema'] = 'gnd_application_' + uuid.uuid4().hex
        oracle = ApplicationOracle(index, population, config=config)
        for row, (_, constraint, ft_id) in zip(verdicts, entries, strict=True):
            try:
                status, payload = oracle.profile_evaluate(constraint, ft_id)
                if status not in {'satisfied', 'violated', 'unsupported', 'vacuous', 'incomplete', 'error'}:
                    raise ProfileRefusal('unexpected-native-status')
                row['status'] = 'warning' if status == 'violated' and row['modality'] == 'deontic' else status
                if status == 'violated':
                    row['witnesses'] = payload
                elif status == 'unsupported':
                    row['reason'] = payload
            except ProfileRefusal as error:
                row.update(status='incomplete', reason=str(error))
            except Exception as error:  # noqa: BLE001 -- explicit native failure verdict
                row.update(status='error', reason=f'{type(error).__name__}: {error}'[:300])
    except Exception as error:  # noqa: BLE001 -- optional backend construction boundary
        for row in verdicts:
            row.update(status='error', reason=f'{type(error).__name__}: {error}'[:300])
        report.update(status='runtime_failure', exit_code=70)
        return report
    statuses = {row['status'] for row in verdicts}
    if 'error' in statuses:
        report.update(status='runtime_failure', exit_code=70)
    elif statuses & {'unsupported', 'incomplete', 'vacuous'}:
        report.update(status='incomplete', exit_code=2)
    elif 'violated' in statuses:
        report.update(status='rejected', exit_code=1)
    elif statuses <= {'satisfied', 'warning'}:
        report.update(status='accepted_with_warnings' if 'warning' in statuses else 'accepted',
                      exit_code=0, accepted=True)
    return report


def program_main(argv: list[str] | None = None) -> int:
    parser = _UsageParser(description="Run exported PyRel constraints; exit 0 means report completion.")
    parser.add_argument("population", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--mode", choices=("select", "require"), default="select")
    parser.add_argument("--config", type=Path)
    parser.add_argument("--accept", action="store_true", help="Require applications-v1 policy acceptance")
    args = parser.parse_args(argv)
    try:
        if args.accept:
            import hashlib
            if len(MODEL_TEXT.encode('utf-8')) > PROFILE_BYTES:
                raise ProfileRefusal('embedded model exceeds application-profile byte cap')
            try:
                text = _read_text(args.population, max_bytes=PROFILE_BYTES)
            except ExportInputError as error:
                if str(error).startswith(f'input exceeds {PROFILE_BYTES} bytes:'):
                    raise ProfileRefusal(str(error)) from error
                raise
            model = _parse_document(MODEL_TEXT)
            population = _parse_document(text)
            context_refusal = None
            if (args.mode != 'select' or args.config is not None or EXPORT_CONFIG['connection'] is not None
                    or EXPORT_CONFIG['duckdb_path'] != ':memory:'):
                context_refusal = 'applications-v1 requires in-memory local select execution'
            report = acceptance_document(model, population,
                                         model_sha256=hashlib.sha256(MODEL_TEXT.encode('utf-8')).hexdigest(),
                                         population_sha256=hashlib.sha256(text.encode('utf-8')).hexdigest(),
                                         execution_refusal=context_refusal)
            try:
                write_new(args.out, json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + '\n')
            except FileNotFoundError as error:
                print(f'output failure: {error}', file=sys.stderr)
                return 70
            return report['exit_code']
        model = _parse_document(MODEL_TEXT)
        population = load_document(args.population)
        index = admit_model(model)
        admit_population(population, index)
        config = local_config(EXPORT_CONFIG["duckdb_path"])
        if args.mode == "select" and EXPORT_CONFIG["connection"] is not None:
            if args.config is None:
                raise FileNotFoundError("named connection requires --config PATH")
            load_document(args.config)
            print("named connection execution needs the Phase 4 runtime adapter", file=sys.stderr)
            return 64
        report = report_document(model, population, mode=args.mode, config=config,
                                 model_name=MODEL_NAME, population_name=str(args.population))
        try:
            write_new(args.out, json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n")
        except FileNotFoundError as error:
            print(f"output failure: {error}", file=sys.stderr)
            return 70
        return 70 if any(row["status"] == "error" for row in report["verdicts"]) else 0
    except ProfileRefusal as error:
        print(f'application refusal: {error}', file=sys.stderr)
        return 2
    except FileExistsError as error:
        print(f"output exists: {error}", file=sys.stderr)
        return 11
    except FileNotFoundError as error:
        print(f"missing input: {error}", file=sys.stderr)
        return 66
    except ExportInputError as error:
        print(f"invalid input: {error}", file=sys.stderr)
        return 3
    except Exception as error:  # noqa: BLE001 -- standalone command operational boundary
        print(f"PyRel execution failed: {type(error).__name__}: {error}", file=sys.stderr)
        return 70
