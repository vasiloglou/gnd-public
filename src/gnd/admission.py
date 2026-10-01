"""Read-only occurrence admission projection for a completed check report."""

from __future__ import annotations

from collections import defaultdict, deque
from typing import Any

from gnd.checker import CheckReport
from gnd.model import Model
from gnd.population import Population
from gnd.popvalidate import resolve_primitive, resolve_reference_value_type
from gnd.semantic_adapter import canonical_scalar
from gnd.semantic_ir import Opaque

Coordinate = tuple[str, int]
TypedKey = tuple[str, str, str]
OpaqueLocation = tuple[str, int, str]
GroupKey = tuple[str, str, TypedKey]


def _fact_ref(node: Coordinate) -> dict[str, Any]:
    return {"fact_type": node[0], "index": node[1]}


def _typed_key(
    value: Any, object_type: str, model: Model, reference_value_types: set[str],
) -> TypedKey | None:
    value_type = resolve_reference_value_type(object_type, model)
    if value_type is None or value_type not in reference_value_types:
        return None
    scalar = canonical_scalar(value, resolve_primitive(value_type, model))
    if scalar is None or isinstance(scalar, Opaque):
        return None
    return value_type, scalar.identity_kind, scalar.token


def _verdict_refs(
    report: CheckReport, population: Population, model: Model,
) -> list[tuple[Any, list[dict[str, Any]]]]:
    projection = report.snapshot_projection or report.admission_projection
    if projection is None:
        raise ValueError("admission requires internal occurrence provenance")
    derived_types = {
        str(row["id"])
        for row in model.fact_types
        if row.get("derivation") in {"derived", "semiderived"}
    }
    paired: list[tuple[Any, list[dict[str, Any]]]] = []
    for verdict, finding in zip(report.verdicts, projection.findings, strict=True):
        refs = (
            verdict.fact_refs
            if verdict.constraint_type == "anchored"
            else [_fact_ref(node) for node in finding.fact_refs]
        )
        paired.append((verdict, [
            ref for ref in refs
            if str(ref["fact_type"]) in population.facts
            and 0 <= int(ref["index"]) < len(population.facts[str(ref["fact_type"])])
            and (
                verdict.constraint_type == "anchored"
                or str(ref["fact_type"]) not in derived_types
            )
        ]))
    return paired


def build_admission(
    model: Model,
    population: Population,
    report: CheckReport,
    *,
    max_cells: int | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """Partition asserted occurrences using typed joins and completed verdicts."""
    fact_types = {str(row["id"]): row for row in model.fact_types}
    reference_value_types = {
        str(row["reference"]["value_type"])
        for row in model.object_types
        if isinstance(row.get("reference"), dict) and row["reference"].get("value_type") is not None
    }
    nodes = sorted(
        (fact_type_id, index)
        for fact_type_id, rows in population.facts.items()
        for index in range(len(rows))
    )
    keys: dict[Coordinate, set[TypedKey]] = {}
    own_opaque: dict[Coordinate, set[OpaqueLocation]] = {}
    typed_index: dict[tuple[str, TypedKey], set[Coordinate]] = defaultdict(set)
    value_index: dict[TypedKey, set[Coordinate]] = defaultdict(set)
    entity_keys: dict[Coordinate, set[TypedKey]] = defaultdict(set)
    for node in nodes:
        fact_type_id, index = node
        fact_type = fact_types.get(fact_type_id)
        if fact_type is None:
            continue
        fact = population.facts[fact_type_id][index]
        node_keys: set[TypedKey] = set()
        opaque: set[OpaqueLocation] = set()
        for role in fact_type.get("roles") or []:
            role_name = str(role["role_name"])
            object_type = str(role["object_type"])
            value = fact.get(role_name)
            if isinstance(value, dict) and set(value) == {"$opaque"}:
                opaque.add((fact_type_id, index, role_name))
                continue
            key = _typed_key(value, object_type, model, reference_value_types)
            if key is None:
                continue
            node_keys.add(key)
            if key[0] == object_type:
                value_index[key].add(node)
            else:
                entity_keys[node].add(key)
        keys[node] = node_keys
        own_opaque[node] = opaque
        for key in node_keys:
            typed_index[(fact_type_id, key)].add(node)

    target_groups: dict[GroupKey, set[Coordinate]] = defaultdict(set)
    for node in nodes:
        fact_type = fact_types.get(node[0])
        if fact_type is None:
            continue
        for source_type in fact_type.get("depends_on") or []:
            for key in keys.get(node, ()):
                target_groups[("explicit", source_type, key)].add(node)
        for key in entity_keys.get(node, ()):
            target_groups[("implicit", "", key)].add(node)
    source_groups: dict[Coordinate, set[GroupKey]] = defaultdict(set)
    for group in target_groups:
        kind, source_type, key = group
        sources = (
            typed_index.get((source_type, key), ())
            if kind == "explicit"
            else value_index.get(key, ())
        )
        for source in sources:
            source_groups[source].add(group)

    blockers: dict[Coordinate, set[str]] = {node: set() for node in nodes}
    opaque_deps = {node: set(own_opaque.get(node, ())) for node in nodes}
    for verdict, refs in _verdict_refs(report, population, model):
        if verdict.verdict not in {"fail", "unchecked"}:
            continue
        if verdict.verdict == "fail" and verdict.modality != "alethic":
            continue
        for ref in refs:
            node = (str(ref["fact_type"]), int(ref["index"]))
            if node in blockers:
                blockers[node].add(verdict.constraint_ref)

    cells = sum(len(v) for v in blockers.values()) + sum(len(v) for v in opaque_deps.values())
    if max_cells is not None and cells > max_cells:
        raise ValueError("admission propagation exceeds cell cap")
    queue = deque(nodes)
    queued = set(nodes)
    group_blockers: dict[GroupKey, set[str]] = defaultdict(set)
    group_opaque: dict[GroupKey, set[OpaqueLocation]] = defaultdict(set)
    while queue:
        source = queue.popleft()
        queued.discard(source)
        for group in source_groups.get(source, ()):
            fresh_blockers = blockers[source] - group_blockers[group]
            fresh_opaque = opaque_deps[source] - group_opaque[group]
            if not fresh_blockers and not fresh_opaque:
                continue
            group_blockers[group].update(fresh_blockers)
            group_opaque[group].update(fresh_opaque)
            for target in target_groups[group]:
                added_blockers = fresh_blockers - blockers[target]
                added_opaque = fresh_opaque - opaque_deps[target]
                if added_blockers or added_opaque:
                    cells += len(added_blockers) + len(added_opaque)
                    if max_cells is not None and cells > max_cells:
                        raise ValueError("admission propagation exceeds cell cap")
                    blockers[target].update(added_blockers)
                    opaque_deps[target].update(added_opaque)
                    if target not in queued:
                        queue.append(target)
                        queued.add(target)

    admitted: list[dict[str, Any]] = []
    blocked: list[dict[str, Any]] = []
    for node in nodes:
        if blockers[node]:
            blocked.append(
                {
                    "fact_ref": _fact_ref(node),
                    "blocked_by": sorted(blockers[node]),
                }
            )
        else:
            admitted.append(
                {
                    "fact_ref": _fact_ref(node),
                    "opaque_deps": [
                        {"fact_ref": _fact_ref((fact_type_id, index)), "role": role}
                        for fact_type_id, index, role in sorted(opaque_deps[node])
                    ],
                }
            )
    return {"admitted": admitted, "blocked": blocked}


def wire_verdicts(
    payload: dict[str, Any], report: CheckReport, population: Population, model: Model,
) -> None:
    """Put typed occurrence addresses on v10 without touching old report rows."""
    for row, (verdict, refs) in zip(
        payload["verdicts"], _verdict_refs(report, population, model), strict=True,
    ):
        row["witnesses"] = row["offending_facts"]
        row["offending_facts"] = refs if verdict.verdict in {"fail", "warning"} else []
        row["refused_facts"] = refs if verdict.verdict == "unchecked" else []
