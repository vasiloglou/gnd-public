"""Invocation-bound fixed populations and their candidate-only projections."""

from __future__ import annotations

import hashlib
import os
import re
import weakref
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

from gnd import artifacts

if TYPE_CHECKING:
    from gnd.model import Model
    from gnd.population import Population

MAX_BYTES = 10 * 1024 * 1024
MAX_SET_BYTES = 32 * 1024 * 1024
MAX_ENTRIES = 100_000
_TOKEN = object()
_BOUND = weakref.WeakValueDictionary()
_COMBINED = weakref.WeakValueDictionary()


class ReferenceInputError(ValueError):
    """A reference boundary refused its input before domain evaluation."""

    def __init__(self, message: str, *, model: Model | None = None):
        super().__init__(message)
        self.model = model


@dataclass(frozen=True)
class ReferenceOrigin:
    id: str
    raw_sha256: str


@dataclass(frozen=True)
class OccurrenceOrigin:
    kind: Literal["candidate", "reference"]
    reference_id: str | None


@dataclass(frozen=True)
class BoundReferenceContext:
    _model: Model
    _digest: str
    _snapshots: tuple[tuple[ReferenceOrigin, str, bytes], ...]
    _owners: tuple[tuple[str, str], ...]
    _populations: tuple[Population, ...]
    _token: object


@dataclass(frozen=True)
class BoundPopulationView:
    combined: Population
    candidate: Population
    occurrence_origins: tuple[dict[str, Any], ...]
    references: BoundReferenceContext


def validate_reference_structure(document: object) -> None:
    stack = [(document, 0)]
    while stack:
        node, parent_depth = stack.pop()
        if isinstance(node, (list, dict)):
            depth = parent_depth + 1
            if depth > 64:
                raise ReferenceInputError("reference container depth exceeds 64")
            stack.extend((v, depth) for v in (node.values() if isinstance(node, dict) else node))


def _relative(path: object) -> str:
    if not isinstance(path, str) or not path or len(path) > 4096:
        raise ReferenceInputError("reference path is empty or exceeds 4096 characters")
    parts = path.split("/")
    if len(parts) > 32 or any(p in {"", ".", ".."} for p in parts):
        raise ReferenceInputError(
            "reference path must have at most 32 nonempty relative components"
        )
    if "\\" in path or "\x00" in path or re.match(r"^[A-Za-z]:", path):
        raise ReferenceInputError("reference path is not a confined POSIX relative path")
    return path


@contextmanager
def retained_root(root: str | Path):
    """Open every lexical ancestor without following a symlink."""
    if not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_DIRECTORY"):
        raise ReferenceInputError("safe reference descriptor traversal is unavailable")
    absolute = Path(root)
    if not absolute.is_absolute():
        absolute = Path.cwd() / absolute
    descriptor = os.open(absolute.anchor, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for part in absolute.parts[1:]:
            next_fd = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = next_fd
        yield descriptor
    finally:
        os.close(descriptor)


def validate_declarations(model: Model) -> dict[str, str]:
    declarations = model.reference_populations
    if declarations:
        from gnd.model import _layer1_structural, semantic_validate

        document = model.model_dump(exclude={"warnings"})
        if _layer1_structural(document) or any(
            i.severity == "error" for i in semantic_validate(document)
        ):
            raise ReferenceInputError("reference-bearing model structure or semantics are invalid")
    if declarations and model.version != 4:
        raise ReferenceInputError("reference_populations requires model version 4")
    if len(declarations) > 32:
        raise ReferenceInputError("reference file count exceeds 32")
    ids: set[str] = set()
    owners: dict[str, str] = {}
    types = {ft["id"]: ft for ft in model.fact_types}
    for d in declarations:
        if set(d) != {"id", "path", "sha256", "fact_types"}:
            raise ReferenceInputError("reference declaration has missing or extra fields")
        identifier = d["id"]
        if not isinstance(identifier, str) or not 1 <= len(identifier) <= 128 or identifier in ids:
            raise ReferenceInputError("reference id must be unique and 1..128 characters")
        ids.add(identifier)
        _relative(d["path"])
        if not isinstance(d["sha256"], str) or not re.fullmatch("[0-9a-f]{64}", d["sha256"]):
            raise ReferenceInputError("reference sha256 must be 64 lowercase hexadecimal digits")
        claimed = d["fact_types"]
        if not isinstance(claimed, list) or not claimed:
            raise ReferenceInputError("reference fact_types must be a nonempty list")
        for ft in claimed:
            if not isinstance(ft, str) or ft not in types or ft in owners:
                raise ReferenceInputError(
                    "reference fact ownership is unknown, duplicated or overlapping"
                )
            if types[ft].get("derivation", "base") not in {"base", None}:
                raise ReferenceInputError("references may own only base fact types")
            owners[ft] = identifier
    for operation in model.operations:
        for effect in operation.get("effects", []):
            for action in ("assert", "retract"):
                if effect.get(action, {}).get("fact_type") in owners:
                    raise ReferenceInputError(
                        "operation effects cannot write a reference-owned fact type"
                    )
    return owners


def reference_model_digest(model: Model) -> str:
    from gnd.population import _model_digest
    from gnd.transition import _canonical

    if not model.reference_populations:
        return "sha256:" + _model_digest(model)
    document = model.model_dump(exclude={"warnings", "reference_populations"})
    declarations = [
        dict(d, fact_types=sorted(d["fact_types"])) for d in model.reference_populations
    ]
    payload = {
        "identity_version": 1,
        "model": _canonical(document, "$"),
        "reference_populations": sorted(declarations, key=lambda d: d["id"]),
    }
    return "sha256:" + hashlib.sha256(artifacts.canonical_json_bytes(payload)).hexdigest()


def _bind_at(model: Model, descriptor: int) -> BoundReferenceContext:
    from gnd.population import PopulationLoadError, _build_population, _parse_document_bytes

    owners = validate_declarations(model)
    snapshots = []
    populations = []
    fact_entries = instance_entries = 0
    total = 0
    for d in sorted(model.reference_populations, key=lambda d: d["id"]):
        raw, _leaf = artifacts.read_regular_bounded_at(descriptor, d["path"], max_bytes=MAX_BYTES)
        total += len(raw)
        if total > MAX_SET_BYTES:
            raise ReferenceInputError("reference set exceeds 32 MiB")
        digest = hashlib.sha256(raw).hexdigest()
        if digest != d["sha256"]:
            raise ReferenceInputError("reference raw hash does not match declared sha256")
        doc = _parse_document_bytes(raw, suffix=Path(d["path"]).suffix, source=d["path"])
        validate_reference_structure(doc)
        if isinstance(doc, dict):
            for section in ("facts", "instances"):
                entries = doc.get(section, {})
                if (
                    isinstance(entries, dict)
                    and sum(len(rows) for rows in entries.values() if isinstance(rows, list))
                    > MAX_ENTRIES
                ):
                    raise ReferenceInputError("reference entries exceed 100000")
        try:
            pop = _build_population(doc, model=model, deduplicate_shape_rows=True)
        except PopulationLoadError as error:
            raise ReferenceInputError(
                "reference population structure or types are invalid"
            ) from error
        if any(ft not in d["fact_types"] for ft in pop.facts):
            raise ReferenceInputError("reference asserts an unowned fact type")
        fact_entries += sum(map(len, pop.facts.values()))
        instance_entries += sum(map(len, pop.instances.values()))
        if fact_entries > MAX_ENTRIES or instance_entries > MAX_ENTRIES:
            raise ReferenceInputError("reference fact or instance entry count exceeds 100000")
        snapshots.append((ReferenceOrigin(d["id"], digest), d["path"], raw))
        populations.append(pop)
    context = BoundReferenceContext(
        model,
        reference_model_digest(model),
        tuple(snapshots),
        tuple(sorted(owners.items())),
        tuple(populations),
        _TOKEN,
    )
    _BOUND[id(context)] = context
    return context


def bind_references(model: Model, *, root: str | Path) -> BoundReferenceContext:
    validate_declarations(model)
    with retained_root(root) as descriptor:
        return _bind_at(model, descriptor)


def resolve_context(
    model: Model, references: BoundReferenceContext | None = None
) -> BoundReferenceContext:
    context = references if references is not None else model._references
    if (
        not isinstance(context, BoundReferenceContext)
        or context._token is not _TOKEN
        or _BOUND.get(id(context)) is not context
    ):
        raise ReferenceInputError("reference-bearing model requires a bound reference context")
    if context._model is not model or context._digest != reference_model_digest(model):
        raise ReferenceInputError("reference context does not match this model's current identity")
    owners = validate_declarations(model)
    expected = {d["id"]: d for d in model.reference_populations}
    if tuple(sorted(owners.items())) != context._owners or len(expected) != len(context._snapshots):
        raise ReferenceInputError("reference context ownership or snapshot roster changed")
    if len(context._populations) != len(context._snapshots) or any(
        not pop.matches_validation_marker(model) for pop in context._populations
    ):
        raise ReferenceInputError("reference context validated population changed")
    for origin, path, raw in context._snapshots:
        declaration = expected.get(origin.id)
        if (
            declaration is None
            or path != declaration["path"]
            or origin.raw_sha256 != declaration["sha256"]
            or hashlib.sha256(raw).hexdigest() != origin.raw_sha256
        ):
            raise ReferenceInputError("reference context snapshot identity changed")
    return context


def bind_population(
    model: Model, candidate: Population, *, references: BoundReferenceContext
) -> BoundPopulationView:
    from gnd.checker import _identity_key
    from gnd.population import _combine_validated_populations

    context = resolve_context(model, references)
    owners = dict(context._owners)
    if any(ft in owners for ft in candidate.facts):
        raise ReferenceInputError("candidate cannot mention a reference-owned fact type")
    if not candidate.matches_validation_marker(model):
        raise ReferenceInputError("candidate population is not validated against the current model")
    facts = {ft: [dict(row) for row in rows] for ft, rows in candidate.facts.items()}
    instances = {ot: list(values) for ot, values in candidate.instances.items()}
    covers = list(candidate.covers)
    format_version = candidate.format_version
    origins = [
        {"origin": {"kind": "candidate", "reference_id": None}, "fact_type": ft, "index": i}
        for ft, rows in candidate.facts.items()
        for i in range(len(rows))
    ]
    for (origin, _path, _raw), pop in zip(context._snapshots, context._populations, strict=True):
        format_version = max(format_version, pop.format_version)
        for ot, values in pop.instances.items():
            instances.setdefault(ot, []).extend(values)
        for ft, rows in pop.facts.items():
            facts[ft] = [dict(row) for row in rows]
            origins.extend(
                {
                    "origin": {"kind": "reference", "reference_id": origin.id},
                    "fact_type": ft,
                    "index": i,
                }
                for i in range(len(rows))
            )
        covers.extend(ft for ft in pop.covers if ft not in covers)
    if (
        sum(map(len, facts.values())) > MAX_ENTRIES
        or sum(map(len, instances.values())) > MAX_ENTRIES
    ):
        raise ReferenceInputError("combined fact or instance entry count exceeds 100000")
    instances = {
        ot: list({_identity_key(value): value for value in values}.values())
        for ot, values in instances.items()
    }
    combined = _combine_validated_populations(
        model,
        (candidate, *context._populations),
        {
            "format_version": format_version,
            "population": {
                "model": candidate.model,
                "model_id": candidate.model_id,
                "source": candidate.source,
                "covers": covers,
            },
            "facts": facts,
            "instances": instances,
        },
    )
    combined._reference_combined = True
    combined._reference_context = context
    _COMBINED[id(combined)] = combined
    origins.sort(
        key=lambda row: (
            row["origin"]["kind"],
            row["origin"]["reference_id"] or "",
            row["fact_type"],
            row["index"],
        )
    )
    return BoundPopulationView(combined, candidate, tuple(origins), context)


def candidate_fact_count(view: BoundPopulationView) -> int:
    return sum(map(len, view.candidate.facts.values()))


def is_bound_population(
    model: Model, population: Population, context: BoundReferenceContext
) -> bool:
    """Recognize only a current combined population created by this binder."""
    return (
        _COMBINED.get(id(population)) is population
        and population._reference_context is context
        and population.matches_validation_marker(model)
    )
