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

from gnd.artifacts import canonical_json_bytes
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
class GroupRecord:
    """One group as the family left it, for the type evidence (TS1).

    ``attribute`` and ``pairs`` are population data held in memory; the
    evidence writer decides what of them is emitted.
    """

    generic: str
    attribute_sha256: str
    status: str  # proposed, shape_match, multi_valued, below_support, mixed_type, over_budget
    signature: str | None  # canonical JSON of the role players; None before typing
    value_primitive: str | None  # None for a mixed-type group
    entity_object_type: str
    support: int
    rows: int
    multi_entities: int
    multi_max: int
    exact_repeats: int
    row_ids: tuple[str, ...]  # first ROW_IDS_MAX
    attribute: Any
    pairs: frozenset[tuple[Any, Any]]  # typed (entity, value) identities
    fact_type: str | None = None  # the proposed id, when status is proposed
    values: frozenset[str] = frozenset()  # the value cells' text, for the rationale scan (TS2)


ROW_IDS_MAX = 32


@dataclass
class TypeProposals:
    operations: list[EvolutionOperation] = field(default_factory=list)
    report: dict[str, Any] = field(default_factory=dict)
    # Operations per proposed group, in order, so a caller can drop whole
    # groups from the tail when the written proposal is over its cap.
    group_sizes: list[int] = field(default_factory=list)
    # Every group formed, in order; the proposed ones also in ``_proposed``.
    groups: list[GroupRecord] = field(default_factory=list)
    redacted_generics: list[str] = field(default_factory=list)
    _proposed: list[GroupRecord] = field(default_factory=list)

    def drop_last(self, count: int) -> None:
        for _ in range(min(count, len(self.group_sizes))):
            del self.operations[len(self.operations) - self.group_sizes.pop():]
            self.report["proposed"].pop()
            self.report["skipped"]["over_budget"] += 1
            dropped = self._proposed.pop()
            dropped.status, dropped.fact_type = "over_budget", None


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
    # The repository's one canonical form, so a reader can recompute it (close review).
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def propose(
    view: PopulationView,
    eligible: list[str],
    *,
    min_support: int,
    show_values: bool,
    show_digests: bool = True,
    redacted: frozenset[tuple[str, str]],
    envelope: dict[str, Any],
    budget: int | None = None,
    verdicts: dict[int, Any] | None = None,
    judgement: dict[str, Any] | None = None,
) -> TypeProposals:
    """Group each eligible generic fact type's rows and propose a fact type per group.

    ``envelope`` is the other families' induction provenance without its
    per-candidate fields; ``show_values`` is already decided by the caller's
    disclosure mode, and so is ``show_digests``: a short attribute name can be
    recovered from its unsalted digest, so customer mode omits it (owner
    ruling after the close).

    ``verdicts`` (TS2) maps a group's position, its evidence ``g<n>``, to a
    checked verdict; ``judgement`` names the files they came from. A judged
    group is rendered as its verdict says, not by the signature match.
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
               "multi_valued": 0, "over_budget": 0, **({} if verdicts is None else {"judged_skip": 0})}
    visits = 0
    taken = set(index.role_object_types()) | set(objects)
    used = 0
    for generic_id, spec in declared.items():
        if (generic_id, spec["attribute"]) in redacted:
            skipped["redacted_attribute_roles"] += 1
            result.redacted_generics.append(generic_id)
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
                                            "entities": {}, "values": {}, "kinds": set(), "pairs": {},
                                            "repeats": [], "texts": set()})
            fact = view.fact_id(generic_id, row_index)
            group["rows"].append(fact)
            group["entities"].setdefault(entity, []).append(fact)
            # Distinct values, not rows: an exact repeated row is one value (close review).
            group["values"].setdefault(entity, set()).add(value)
            group["kinds"].add(value[0])
            # Each pair's first row, and the rows that repeat one (TS2 many-to-many).
            if (entity, value) in group["pairs"]:
                group["repeats"].append(fact)
            else:
                group["pairs"][entity, value] = fact
            group["texts"].add(cell_text(row[spec["value"]]))
        for number, group in enumerate(groups.values()):
            position = len(result.groups)
            verdict = None if verdicts is None else verdicts.get(position)
            digest = _value_digest(group["attribute"])
            support = len(group["entities"])
            counts = [len(values) for values in group["values"].values()]
            record = GroupRecord(
                generic=generic_id, attribute_sha256=digest, status="", signature=None,
                value_primitive=(_primitive_of(view, group, spec, generic_id)
                                 if len(group["kinds"]) == 1 else None),
                entity_object_type=entity_role.object_type, support=support, rows=len(group["rows"]),
                multi_entities=sum(1 for count in counts if count > 1), multi_max=max(counts),
                exact_repeats=len(group["rows"]) - len(group["pairs"]),
                row_ids=tuple(group["rows"][:ROW_IDS_MAX]), attribute=group["attribute"],
                pairs=frozenset(group["pairs"]), values=frozenset(group["texts"]))
            result.groups.append(record)
            if len(group["kinds"]) != 1:
                skipped["mixed_type_groups"] += 1
                record.status = "mixed_type"
                continue
            if support < min_support:
                skipped["below_support"] += 1
                record.status = "below_support"
                continue
            many = False
            if any(len(values) > 1 for values in group["values"].values()):
                # D5: an entity with several values breaks the uniqueness the
                # envelope sits on, so the group is counted, not proposed,
                # unless a shape verdict judged it many-to-many (TS2).
                record.status = "multi_valued"
                if verdict is None:
                    skipped["multi_valued"] += 1
                    continue
                if verdict.verdict == "skip":
                    skipped["judged_skip"] += 1
                    continue
                many = True
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
            record.signature = canonical_json_bytes(list(role_player_signature(players))).decode("utf-8").strip()
            if verdict is not None and verdict.verdict == "duplicate":
                record.status = "shape_match"
                shape_matches.append({"generic": generic_id, "existing": verdict.of, "judged": True,
                                      **({"attribute_sha256": digest} if show_digests else {})})
                continue
            if match is not None and verdict is None:
                record.status = "shape_match"
                shape_matches.append({"generic": generic_id, "existing": match,
                                      **({"attribute_sha256": digest} if show_digests else {})})
                continue
            if many:
                # The uniqueness spans both roles: each pair once (TS2-C5).
                single, multiple = list(group["pairs"].values()), group["repeats"]
                numerator, denominator, spanned = len(group["pairs"]), len(group["rows"]), ["entity", "value"]
            else:
                single, multiple = [ids[0] for ids in group["entities"].values()], []
                numerator, denominator, spanned = len(single), support, ["entity"]
            operations = []
            if value_type != value_role.object_type:
                operations.append(("object_types", value_type, {
                    "id": value_type, "name": _name(value_type), "kind": "value", "primitive": primitive,
                }))
            fact_provenance = {} if verdict is None else {"provenance": {
                # D3: no attribute digest enters the model under customer.
                **({"induced_from": {"generic": generic_id, "attribute_sha256": digest}} if show_digests else {}),
                "judgement": {"evidence_sha256": judgement["evidence_sha256"],
                              "judgements_sha256": judgement[verdict.kind]["sha256"], "kind": verdict.kind,
                              "verdict": verdict.verdict, "skill": judgement[verdict.kind]["skill"]},
            }}
            entity_name = str(objects[entity_role.object_type].get("name") or entity_role.object_type)
            value_name = _name(value_type) if value_type != value_role.object_type else str(
                objects[value_type].get("name") or value_type)
            # A judged group may take a clashing id where a signature match
            # stopped it before, so its reading names the suffix too (review F4).
            label = new_id.removeprefix(f"{generic_id}_induced_") if verdict is not None else number
            operations.append(("fact_types", new_id, {
                "id": new_id,
                # The generic id keeps readings from two generic fact types apart (close review).
                "reading": f"{{{entity_name}}} has induced {generic_id} attribute {label} {{{value_name}}}",
                # A redacted generic role stays redacted in the new fact type (review F4).
                "roles": [{"object_type": entity_role.object_type, "role_name": "entity",
                           **({"redact": True} if (generic_id, spec["entity"]) in redacted else {})},
                          {"object_type": value_type, "role_name": "value",
                           **({"redact": True} if (generic_id, spec["value"]) in redacted else {})}],
                **fact_provenance,
            }))
            induction = {**envelope, "examples": single[:256], "counterexamples": multiple[:32],
                         "support": {"numerator": numerator, "denominator": denominator}}
            constraint = {"type": "uniqueness", "roles": spanned, "source": "induced",
                          "status": "proposed", "modality": "deontic",
                          "provenance": {"induction": induction}}
            # The proposal carries each addition about three times (review F2).
            cost = 3 * sum(len(json.dumps(after, ensure_ascii=False)) for _, _, after in operations)
            cost += 3 * len(json.dumps(constraint, ensure_ascii=False))
            if budget is not None and used + cost > budget:
                skipped["over_budget"] += 1
                record.status = "over_budget"
                continue
            used += cost
            taken.update({new_id, f"{new_id}_value"})
            result.group_sizes.append(len(operations) + 1)
            for collection, element_id, after in operations:
                result.operations.append(EvolutionOperation(
                    operation_id=f"discover-type-{len(result.operations):04d}", kind=EvolutionOperationKind.ADD,
                    locator=ElementLocator(collection=collection, element_id=element_id), after=after))
            result.operations.append(EvolutionOperation(
                operation_id=f"discover-type-{len(result.operations):04d}", kind=EvolutionOperationKind.ADD,
                locator=ConstraintLocator(host="fact_type", host_id=new_id, family="uniqueness"),
                after=constraint))
            entry = {"fact_type": new_id, "generic": generic_id, "support": induction["support"],
                     "rows": group["rows"]}
            if show_digests:
                entry["attribute_sha256"] = digest
            if show_values:
                entry["value"] = group["attribute"]
            if verdict is not None:
                entry["judged"] = True
                if many:
                    entry["shape"] = "many-to-many"
            proposed.append(entry)
            record.status, record.fact_type = "proposed", new_id
            result._proposed.append(record)
    result.report = {"min_support": min_support, "proposed": proposed, "shape_matches": shape_matches,
                     "skipped": skipped, "row_visits": visits}
    if verdicts is not None:
        result.report["judgements"] = {
            "evidence_sha256": judgement["evidence_sha256"],
            **{f"{kind}_sha256": (None if judgement[kind] is None else judgement[kind]["sha256"])
               for kind in ("duplicates", "shapes")},
        }
    return result


def cell_text(value: Any) -> str:
    # A cell's text as a rationale would quote it: a string as itself, else its JSON.
    return value if isinstance(value, str) else canonical_json_bytes(value).decode("utf-8").strip()


def _primitive_of(view: PopulationView, group: dict[str, Any], spec: dict[str, str], generic_id: str) -> str:
    kind = next(iter(group["kinds"]))
    value_role = next(role for role in view.roles[generic_id] if role.name == spec["value"])
    # The checker's identity kind names the primitive family; keep the declared
    # primitive when it agrees, otherwise the kind's own primitive.
    return value_role.primitive if primitive_kind(value_role.primitive) == kind else PRIMITIVE_FOR_KIND.get(kind, "String")


# The kind vocabulary (TS2 D9): a declared primitive's family, as the
# checker's identity kinds name it, and back.
PRIMITIVE_FOR_KIND = {"string": "String", "number": "Number", "boolean": "Boolean", "date": "Date",
                       "datetime": "DateTime"}


def primitive_kind(primitive: str | None) -> str | None:
    return {"String": "string", "Integer": "number", "Number": "number", "Float": "number",
            "Boolean": "boolean", "Date": "date", "DateTime": "datetime"}.get(primitive or "")


def _name(object_type_id: str) -> str:
    return "".join(part.capitalize() for part in object_type_id.split("_"))
