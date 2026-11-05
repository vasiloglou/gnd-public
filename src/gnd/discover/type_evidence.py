"""The fact-type family's evidence file, ``gnd-type-evidence/1`` (TS1).

The family decides nothing semantic: it groups generic rows and counts. This
file states, per group, what it counted and which fact types the group's
entity type already plays, so a judgement skill can decide what a duplicate
or a multi-valued attribute is. It never says "duplicate". Schema:
``src/gnd/type-evidence.schema.json``. The disclosure decisions arrive from
the caller; no population value is emitted unless ``show_values`` and no
attribute digest unless ``show_digests``.
"""

from __future__ import annotations

import json
import re
from typing import Any

from gnd.artifacts import canonical_json_bytes
from gnd.discover import types
from gnd.discover.support import PopulationView, identity
from gnd.model_index import ModelIndex
from gnd.refscheme import role_player_signature

FORMAT = "gnd-type-evidence/1"
MAX_EVIDENCE_BYTES = 10 * 1024 * 1024
_DIGEST = re.compile(r"[0-9a-f]{64}")
_ORIGIN_KEYS = {"generic", "attribute_sha256"}


class TypeEvidenceError(ValueError):
    """A malformed ``provenance.induced_from`` (exit 3)."""


class TypeEvidenceOverflow(RuntimeError):
    """The groups alone exceed the evidence cap (an internal defect, exit 70)."""


def origins(view: PopulationView) -> dict[str, dict[str, str] | None]:
    """Every fact type's ``provenance.induced_from``, refusing a malformed one."""
    found: dict[str, dict[str, str] | None] = {}
    for fact_type in ModelIndex.for_model(view.model).iter_fact_types_shared():
        fact_id = str(fact_type.get("id"))
        provenance = fact_type.get("provenance")
        if not isinstance(provenance, dict) or "induced_from" not in provenance:
            found[fact_id] = None
            continue
        origin = provenance["induced_from"]
        if (not isinstance(origin, dict) or set(origin) != _ORIGIN_KEYS
                or not all(isinstance(origin[key], str) for key in _ORIGIN_KEYS)
                or _DIGEST.fullmatch(origin["attribute_sha256"]) is None):
            raise TypeEvidenceError(f"fact type {fact_id}: invalid induced_from")
        found[fact_id] = {key: origin[key] for key in _ORIGIN_KEYS}
    return found


def _pairs_comparable(facts: dict[str, Any], kind: str | None) -> bool:
    """The candidate's value cells have the group's identity kind (D2).

    Judged by the kinds its cells actually hold, since a declared primitive
    and a cell's identity kind need not share a name (a DateTime cell held as
    a JSON string is ``string``, review F3); by the declared primitive only
    when the candidate has no cells.
    """
    if kind is None or facts["pairs"] is None:
        return False
    if facts["kinds"]:
        return facts["kinds"] == {kind}
    return types.primitive_kind(facts["value_primitive"]) == kind


def _candidate_facts(view: PopulationView, fact_id: str, object_type: str,
                     redacted: frozenset[tuple[str, str]]) -> dict[str, Any]:
    """One candidate's model text and its population sets, built once."""
    index = ModelIndex.for_model(view.model)
    fact_type = index.fact_type(fact_id) or {}
    roles = view.roles[fact_id]
    rows = view.rows(fact_id)
    own = [role for role in roles if role.object_type == object_type]
    entities = {key for role in own for row in rows if role.name in row
                for key in [identity(row[role.name], role.primitive)] if key is not None}
    pairs, kinds, primitive = None, set(), None
    other = [role for role in roles if role.object_type != object_type]
    # A redacted value role gets no pair count: it would say how many hidden
    # values equal the group's (review F4).
    if len(roles) == 2 and len(own) == 1 and (fact_id, other[0].name) not in redacted:
        pairs, primitive = set(), other[0].primitive
        for row in rows:
            entity = identity(row.get(own[0].name), own[0].primitive)
            value = identity(row.get(other[0].name), other[0].primitive)
            if entity is not None and value is not None:
                pairs.add((entity, value))
                kinds.add(value[0])
    readings = [str(fact_type[key]) for key in ("reading", "inverse_reading") if fact_type.get(key)]
    return {
        "readings": readings,
        "players": [{"name": role.name, "object_type": role.object_type} for role in roles],
        "signature": list(role_player_signature({role.name: role.object_type for role in roles})),
        "rows": len(rows),
        "entities": entities,
        "pairs": pairs,
        "kinds": kinds,
        "value_primitive": primitive,
    }


def _size(value: Any) -> int:
    # Canonical bytes carry one trailing newline, which pays for the comma.
    return len(canonical_json_bytes(value))


def build_evidence(
    view: PopulationView,
    proposals: types.TypeProposals,
    *,
    model_sha256: str,
    population_sha256: str,
    min_support: int,
    show_values: bool,
    show_digests: bool,
    redacted_generics: list[str],
    redacted_roles: frozenset[tuple[str, str]] = frozenset(),
) -> dict[str, Any]:
    """The evidence document for the groups ``proposals`` holds, statuses final.

    Built within the cap (standing rule 2): every group's own entry first, in
    order, then candidates in order until the remaining bytes run out. So work
    and memory follow the cap, not groups times candidates; what does not fit
    is counted in ``truncated_groups`` and ``truncated`` (review F1, F2).
    """
    induced = origins(view)
    played: dict[str, list[str]] = {}
    for fact_id, players in ModelIndex.for_model(view.model).role_object_types().items():
        for object_type in set(players.values()):
            played.setdefault(object_type, []).append(fact_id)
    document: dict[str, Any] = {
        "format": FORMAT,
        "model_sha256": model_sha256,
        "population_sha256": population_sha256,
        "min_support": min_support,
        "show_values": show_values,
        "show_digests": show_digests,
        "groups": [],
        "redacted_generics": list(redacted_generics),
        "truncated": 0,
        "truncated_groups": 0,
    }
    # Headroom for the two counts' digits.
    budget = MAX_EVIDENCE_BYTES - _size(document) - 64
    kept: list[tuple[types.GroupRecord, dict[str, Any]]] = []
    for number, record in enumerate(proposals.groups):
        group: dict[str, Any] = {
            "group": f"g{number}",
            "generic": record.generic,
            "status": record.status,
            "fact_type": record.fact_type,
            "signature": record.signature,
            "value_primitive": record.value_primitive,
            "entity_object_type": record.entity_object_type,
            "support": record.support,
            "rows": record.rows,
            "multi": {"entities": record.multi_entities, "max": record.multi_max},
            "exact_repeats": record.exact_repeats,
            "row_ids": list(record.row_ids),
            "candidates": [],
        }
        if show_digests:
            group["attribute_sha256"] = record.attribute_sha256
        if show_values:
            group["value"] = record.attribute
        size = _size(group)
        if size > budget:
            document["truncated_groups"] = len(proposals.groups) - number
            break
        budget -= size
        kept.append((record, group))
    # Pair sets per candidate are built once, not per group: each group then
    # costs its own rows.
    cache: dict[tuple[str, str], dict[str, Any]] = {}
    full = False
    for record, group in kept:
        document["groups"].append(group)
        candidates = [fact_id for fact_id in played.get(record.entity_object_type, [])
                      if fact_id != record.generic]
        if full:
            document["truncated"] += len(candidates)
            continue
        kinds = {value[0] for _, value in record.pairs}
        kind = next(iter(kinds)) if len(kinds) == 1 else None
        own_entities = {entity for entity, _ in record.pairs}
        own_signature = None if record.signature is None else json.loads(record.signature)
        for position, fact_id in enumerate(candidates):
            key = (fact_id, record.entity_object_type)
            if key not in cache:
                cache[key] = _candidate_facts(view, fact_id, record.entity_object_type, redacted_roles)
            facts = cache[key]
            entry: dict[str, Any] = {
                "fact_type": fact_id,
                "readings": facts["readings"],
                "roles": facts["players"],
                "signature_equal": own_signature == facts["signature"],
                "rows": facts["rows"],
                "overlap": {
                    "entities": len(own_entities & facts["entities"]),
                    "pairs": len(record.pairs & facts["pairs"]) if _pairs_comparable(facts, kind) else None,
                },
                "origin": None,
            }
            origin = induced.get(fact_id)
            if origin is not None:
                entry["origin"] = {
                    "generic": origin["generic"],
                    "same_attribute": origin["attribute_sha256"] == record.attribute_sha256,
                    **({"attribute_sha256": origin["attribute_sha256"]} if show_digests else {}),
                }
            size = _size(entry)
            if size > budget:
                full = True
                document["truncated"] += len(candidates) - position
                break
            budget -= size
            group["candidates"].append(entry)
    return document


def evidence_bytes(document: dict[str, Any], *, cap: int | None = None) -> bytes:
    """Canonical bytes; drops candidates, then groups, from the tail if still over the cap.

    A fallback: ``build_evidence`` already fills within the cap. Each pass
    frees at least the excess before serialising again, so a few passes do.
    """
    cap = MAX_EVIDENCE_BYTES if cap is None else cap
    raw = canonical_json_bytes(document)
    groups = document["groups"]
    while len(raw) > cap:
        excess, freed = len(raw) - cap, 0
        index = len(groups) - 1
        while freed < excess and index >= 0:
            if groups[index]["candidates"]:
                freed += _size(groups[index]["candidates"].pop())
                document["truncated"] += 1
            else:
                index -= 1
        while freed < excess and groups:
            freed += _size(groups.pop())
            document["truncated_groups"] += 1
        if freed == 0:
            raise TypeEvidenceOverflow("the type evidence header exceeds the evidence cap")
        raw = canonical_json_bytes(document)
    return raw
