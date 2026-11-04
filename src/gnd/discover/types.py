"""The opt-in ``fact-type`` discover family: binary fact types from generic rows (CT4).

A fact type is generic only when its provenance declares
``generic: {entity, attribute, value}``. Its rows are grouped by the attribute
role's value; a group whose distinct entities reach the support threshold and
whose values share one primitive becomes an ADD of a binary fact type with an
opaque id and a placeholder reading, plus an induced deontic uniqueness on the
entity role. No population value enters the model: the attribute value is
reported as a SHA-256 and, only when the disclosure mode allows, as text.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

from gnd.discover.support import PopulationView, identity
from gnd.evolve.models import (
    ConstraintLocator,
    ElementLocator,
    EvolutionOperation,
    EvolutionOperationKind,
)
from gnd.model_index import ModelIndex
from gnd.refscheme import role_player_signature

FAMILY = "fact-type"
DEFAULT_MIN_SUPPORT = 20
_GENERIC_KEYS = {"entity", "attribute", "value"}


class GenericDeclarationError(ValueError):
    """An invalid ``provenance.generic`` declaration (exit 3)."""


@dataclass
class TypeProposals:
    operations: list[EvolutionOperation] = field(default_factory=list)
    report: dict[str, Any] = field(default_factory=dict)


def generic_declarations(view: PopulationView) -> dict[str, dict[str, str]]:
    """The declared generic fact types, refusing a malformed declaration."""
    declared = {}
    for fact_type in ModelIndex.for_model(view.model).iter_fact_types_shared():
        provenance = fact_type.get("provenance")
        if not isinstance(provenance, dict) or "generic" not in provenance:
            continue
        fact_id = str(fact_type.get("id"))
        generic = provenance["generic"]
        roles = [role.name for role in view.roles.get(fact_id, [])]
        if (not isinstance(generic, dict) or set(generic) != _GENERIC_KEYS or len(roles) != 3
                or not all(isinstance(generic[key], str) for key in _GENERIC_KEYS)
                or {generic[key] for key in _GENERIC_KEYS} != set(roles)):
            raise GenericDeclarationError(f"fact type {fact_id}: invalid generic declaration")
        declared[fact_id] = {key: generic[key] for key in _GENERIC_KEYS}
    return declared


def _value_digest(value: Any) -> str:
    return hashlib.sha256(repr((type(value).__name__, value)).encode("utf-8")).hexdigest()


def propose(
    view: PopulationView,
    eligible: list[str],
    *,
    min_support: int,
    show_values: bool,
    redacted: frozenset[tuple[str, str]],
    envelope: dict[str, Any],
    budget: int | None = None,
) -> TypeProposals:
    """Group each eligible generic fact type's rows and propose a fact type per group.

    ``envelope`` is the other families' induction provenance without its
    per-candidate fields; ``show_values`` is already decided by the caller's
    disclosure mode.
    """
    index = ModelIndex.for_model(view.model)
    declared = {ft: spec for ft, spec in generic_declarations(view).items() if ft in eligible}
    objects = index.object_types_by_id()
    existing = {}
    for fact_id, players in index.role_object_types().items():
        existing.setdefault(role_player_signature(players), fact_id)
    result = TypeProposals()
    proposed, shape_matches = [], []
    skipped = {"redacted_attribute_roles": 0, "mixed_type_groups": 0, "below_support": 0,
               "multi_valued": 0, "over_budget": 0}
    visits = 0
    taken = set(index.role_object_types()) | set(objects)
    used = 0
    for generic_id, spec in declared.items():
        if (generic_id, spec["attribute"]) in redacted:
            skipped["redacted_attribute_roles"] += 1
            continue
        roles = {role.name: role for role in view.roles[generic_id]}
        entity_role, value_role = roles[spec["entity"]], roles[spec["value"]]
        attribute_role = roles[spec["attribute"]]
        groups: dict[Any, dict[str, Any]] = {}
        for row_index, row in enumerate(view.rows(generic_id)):
            visits += 1
            key = identity(row.get(spec["attribute"]), attribute_role.primitive)
            entity = identity(row.get(spec["entity"]), entity_role.primitive)
            value = identity(row.get(spec["value"]), value_role.primitive)
            if key is None or entity is None or value is None:
                continue
            group = groups.setdefault(key, {"attribute": row[spec["attribute"]], "rows": [],
                                            "entities": {}, "kinds": set()})
            group["rows"].append(view.fact_id(generic_id, row_index))
            group["entities"].setdefault(entity, []).append(view.fact_id(generic_id, row_index))
            group["kinds"].add(value[0])
        for number, group in enumerate(groups.values()):
            digest = _value_digest(group["attribute"])
            support = len(group["entities"])
            if len(group["kinds"]) != 1:
                skipped["mixed_type_groups"] += 1
                continue
            if support < min_support:
                skipped["below_support"] += 1
                continue
            if any(len(ids) > 1 for ids in group["entities"].values()):
                # D5: an entity with several values breaks the uniqueness the
                # envelope sits on, so the group is counted, not proposed.
                skipped["multi_valued"] += 1
                continue
            # Never reuse an id the model already holds (review F1): a clash
            # takes the next free suffix.
            new_id, clash = f"{generic_id}_induced_{number}", 0
            while {new_id, f"{new_id}_value"} & taken:
                clash += 1
                new_id = f"{generic_id}_induced_{number}_{clash}"
            value_type = value_role.object_type
            primitive = _primitive_of(view, group, spec, generic_id)
            if value_role.primitive != primitive:
                value_type = f"{new_id}_value"
            players = {"entity": entity_role.object_type, "value": value_type}
            match = existing.get(role_player_signature(players))
            if match is not None:
                shape_matches.append({"generic": generic_id, "attribute_sha256": digest, "existing": match})
                continue
            single = [ids[0] for ids in group["entities"].values() if len(ids) == 1]
            multiple = [ids[0] for ids in group["entities"].values() if len(ids) > 1]
            operations = []
            if value_type != value_role.object_type:
                operations.append(("object_types", value_type, {
                    "id": value_type, "name": _name(value_type), "kind": "value", "primitive": primitive,
                }))
            entity_name = str(objects[entity_role.object_type].get("name") or entity_role.object_type)
            value_name = _name(value_type) if value_type != value_role.object_type else str(
                objects[value_type].get("name") or value_type)
            operations.append(("fact_types", new_id, {
                "id": new_id,
                "reading": f"{{{entity_name}}} has induced attribute {number} {{{value_name}}}",
                # A redacted generic role stays redacted in the new fact type (review F4).
                "roles": [{"object_type": entity_role.object_type, "role_name": "entity",
                           **({"redact": True} if (generic_id, spec["entity"]) in redacted else {})},
                          {"object_type": value_type, "role_name": "value",
                           **({"redact": True} if (generic_id, spec["value"]) in redacted else {})}],
            }))
            induction = {**envelope, "examples": single[:256], "counterexamples": multiple[:32],
                         "support": {"numerator": len(single), "denominator": support}}
            constraint = {"type": "uniqueness", "roles": ["entity"], "source": "induced",
                          "status": "proposed", "modality": "deontic",
                          "provenance": {"induction": induction}}
            # The proposal carries each addition about three times (review F2).
            cost = 3 * sum(len(json.dumps(after, ensure_ascii=False)) for _, _, after in operations)
            cost += 3 * len(json.dumps(constraint, ensure_ascii=False))
            if budget is not None and used + cost > budget:
                skipped["over_budget"] += 1
                continue
            used += cost
            taken.update({new_id, f"{new_id}_value"})
            for collection, element_id, after in operations:
                result.operations.append(EvolutionOperation(
                    operation_id=f"discover-type-{len(result.operations):04d}", kind=EvolutionOperationKind.ADD,
                    locator=ElementLocator(collection=collection, element_id=element_id), after=after))
            result.operations.append(EvolutionOperation(
                operation_id=f"discover-type-{len(result.operations):04d}", kind=EvolutionOperationKind.ADD,
                locator=ConstraintLocator(host="fact_type", host_id=new_id, family="uniqueness"),
                after=constraint))
            entry = {"fact_type": new_id, "generic": generic_id, "attribute_sha256": digest,
                     "support": induction["support"], "rows": group["rows"]}
            if show_values:
                entry["value"] = group["attribute"]
            proposed.append(entry)
    result.report = {"min_support": min_support, "proposed": proposed, "shape_matches": shape_matches,
                     "skipped": skipped, "row_visits": visits}
    return result


def _primitive_of(view: PopulationView, group: dict[str, Any], spec: dict[str, str], generic_id: str) -> str:
    kind = next(iter(group["kinds"]))
    value_role = next(role for role in view.roles[generic_id] if role.name == spec["value"])
    # The checker's identity kind names the primitive family; keep the declared
    # primitive when it agrees, otherwise the kind's own primitive.
    return value_role.primitive if _kind(value_role.primitive) == kind else _PRIMITIVE_FOR_KIND.get(kind, "String")


_PRIMITIVE_FOR_KIND = {"string": "String", "number": "Number", "boolean": "Boolean", "date": "Date",
                       "datetime": "DateTime"}


def _kind(primitive: str | None) -> str | None:
    return {"String": "string", "Integer": "number", "Number": "number", "Float": "number",
            "Boolean": "boolean", "Date": "date", "DateTime": "datetime"}.get(primitive or "")


def _name(object_type_id: str) -> str:
    return "".join(part.capitalize() for part in object_type_id.split("_"))
