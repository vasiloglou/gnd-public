"""Compose several anchored populations into one population with lineage (CT2).

A composition directory holds ``manifest.json`` and, for each source id,
``<id>/population.json``, its adjacent sidecar and ``<id>/document.txt``.
The manifest lists every change composition makes; nothing is inferred. The
record written beside the composed population is value-free: digests, ids
and indexes only.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from itertools import pairwise
from pathlib import Path
from typing import Any

from gnd.anchors import (
    MAX_DOCUMENT_BYTES,
    AnchorError,
    AnchorSidecar,
    bind_anchors,
    parse_anchor_sidecar,
    read_regular_path,
)
from gnd.artifacts import canonical_json_bytes
from gnd.composition_resolution import (
    MAX_RESOLUTION_BYTES,
    CompositionError,
    ResolutionEvidence,
    check_coverage,
    parse_resolution,
)
from gnd.composition_resolution import exact_fields as _keys
from gnd.composition_resolution import read_json as _json
from gnd.composition_resolution import row_key as _row_key
from gnd.composition_resolution import scalar as _scalar
from gnd.model import MAX_ENTRIES, Model, ReferenceInputError, resolve_context
from gnd.model_index import ModelIndex
from gnd.population import (
    MAX_POPULATION_BYTES,
    Population,
    PopulationLoadError,
    load_population_bytes,
)
from gnd.values import identity_key

MANIFEST_SCHEMA = "gnd-composition-manifest/1"
RECORD_SCHEMA = "gnd-composition/1"
CATALOG_RECORD_SCHEMA = "gnd-composition/2"
MAX_MANIFEST_BYTES = 1 << 20
MAX_RECORD_BYTES = 16 << 20
_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
_HEX = re.compile(r"^[0-9a-f]{64}$")
# The per-fact-type row index; a test substitutes a counting mapping (T6).
_positions_factory = dict


@dataclass(frozen=True)
class Manifest:
    sources: tuple[str, ...]
    renamings: tuple[dict[str, Any], ...]
    scope_tags: tuple[dict[str, str], ...]
    resolution: dict[str, str] | None = None


@dataclass(frozen=True)
class Source:
    id: str
    population: Population
    sidecar: AnchorSidecar
    document_bytes: bytes
    digests: dict[str, str]


@dataclass(frozen=True)
class Composition:
    population_bytes: bytes
    record: dict[str, Any]
    record_bytes: bytes
    sources: tuple[Source, ...]


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def parse_manifest(raw: bytes) -> Manifest:
    data = _json(raw, max_bytes=MAX_MANIFEST_BYTES, what="manifest")
    fields = {"schema", "sources", "renamings", "deduplications", "scope_tags"}
    has_resolution = isinstance(data, dict) and "resolution" in data
    if has_resolution:
        fields.add("resolution")
    _keys(data, fields, "manifest")
    resolution = data.get("resolution")
    if has_resolution:
        _keys(resolution, {"path", "sha256"}, "manifest resolution")
        path, digest = resolution["path"], resolution["sha256"]
        if not isinstance(path, str) or not path.endswith(".json") or not _ID.fullmatch(path[:-5]):
            raise CompositionError("manifest resolution path must be a single JSON filename")
        if not isinstance(digest, str) or not _HEX.fullmatch(digest):
            raise CompositionError("manifest resolution sha256 is not a SHA-256 digest")
    if data["schema"] != MANIFEST_SCHEMA:
        raise CompositionError("manifest schema is not gnd-composition-manifest/1")
    sources = data["sources"]
    if (not isinstance(sources, list) or not sources
            or not all(isinstance(item, str) and _ID.fullmatch(item) for item in sources)
            or len({item.casefold() for item in sources}) != len(sources)):
        # Case-folded: on a case-insensitive filesystem two ids that differ
        # only in case would open one folder twice (close review).
        raise CompositionError("manifest sources must be distinct ids")
    if data["deduplications"] != "identical-rows":
        raise CompositionError("manifest deduplications must be identical-rows")
    if not isinstance(data["renamings"], list) or not isinstance(data["scope_tags"], list):
        raise CompositionError("manifest renamings and scope_tags must be lists")
    seen = set()
    source_ids = set(sources)
    for index, renaming in enumerate(data["renamings"]):
        fields = {"source", "fact_type", "role", "from", "to"}
        if has_resolution:
            if isinstance(renaming, dict) and set(renaming) == fields:
                raise CompositionError(f"renaming {index} cites no decision")
            fields.add("decision")
        _keys(renaming, fields, f"renaming {index}")
        if has_resolution and (type(renaming["decision"]) is not int or renaming["decision"] < 0):
            raise CompositionError(f"renaming {index} decision must be a nonnegative index")
        if not isinstance(renaming["source"], str) or renaming["source"] not in source_ids:
            raise CompositionError(f"renaming {index} names an unknown source")
        if not all(isinstance(renaming[key], str) and renaming[key] for key in ("fact_type", "role")):
            raise CompositionError(f"renaming {index} has an invalid fact type or role")
        if not (_scalar(renaming["from"]) and _scalar(renaming["to"]) and type(renaming["from"]) is type(renaming["to"])):
            raise CompositionError(f"renaming {index} must map a scalar to a scalar of the same type")
        identity = (renaming["source"], renaming["fact_type"], renaming["role"],
                    type(renaming["from"]).__name__, repr(renaming["from"]))
        if identity in seen:
            raise CompositionError(f"renaming {index} repeats an earlier renaming")
        seen.add(identity)
    for index, tag in enumerate(data["scope_tags"]):
        _keys(tag, {"source", "tag"}, f"scope tag {index}")
        if not isinstance(tag["source"], str) or tag["source"] not in source_ids:
            raise CompositionError(f"scope tag {index} names an unknown source")
        if not isinstance(tag["tag"], str) or not 0 < len(tag["tag"]) <= 128:
            raise CompositionError(f"scope tag {index} must be 1 to 128 characters")
    return Manifest(tuple(sources), tuple(data["renamings"]), tuple(data["scope_tags"]), resolution)


def _lineage_entry(value: Any, what: str) -> dict[str, Any]:
    _keys(value, {"source", "fact_type", "fact_index"}, what)
    if (not isinstance(value["source"], str) or not isinstance(value["fact_type"], str)
            or type(value["fact_index"]) is not int or value["fact_index"] < 0):
        raise CompositionError(f"{what} is invalid")
    return value


def parse_record(raw: bytes) -> dict[str, Any]:
    data = _json(raw, max_bytes=MAX_RECORD_BYTES, what="record")
    digests = ["model_sha256", "manifest_sha256", "population_sha256"]
    has_resolution = isinstance(data, dict) and "resolution_sha256" in data
    if has_resolution:
        digests.append("resolution_sha256")
    catalog = isinstance(data, dict) and data.get("schema") == CATALOG_RECORD_SCHEMA
    fields = {"schema", "sources", "scope_tags", "facts"} | set(digests)
    _keys(data, fields | {"references"} if catalog else fields, "record")
    if not catalog and data["schema"] != RECORD_SCHEMA:
        raise CompositionError("record schema is not gnd-composition/1")
    if catalog:
        _parse_catalog_roster(data["references"])
    for key in digests:
        if not isinstance(data[key], str) or not _HEX.fullmatch(data[key]):
            raise CompositionError(f"record {key} is not a SHA-256 digest")
    if not isinstance(data["sources"], list) or not data["sources"]:
        raise CompositionError("record sources must be a non-empty list")
    source_ids = set()
    for index, source in enumerate(data["sources"]):
        _keys(source, {"id", "population_sha256", "sidecar_sha256", "document_sha256"}, f"record source {index}")
        if not isinstance(source["id"], str) or not _ID.fullmatch(source["id"]):
            raise CompositionError(f"record source {index} has an invalid id")
        if not all(isinstance(source[key], str) and _HEX.fullmatch(source[key])
                   for key in ("population_sha256", "sidecar_sha256", "document_sha256")):
            raise CompositionError(f"record source {index} has an invalid digest")
        if catalog:
            identifier = source["id"]
            if identifier in source_ids:
                raise CompositionError("record candidate source ids must be distinct")
            source_ids.add(identifier)
    if not isinstance(data["scope_tags"], list):
        raise CompositionError("record scope_tags must be a list")
    for index, tag in enumerate(data["scope_tags"]):
        _keys(tag, {"source", "tag"}, f"record scope tag {index}")
        if not isinstance(tag["source"], str) or not isinstance(tag["tag"], str):
            raise CompositionError(f"record scope tag {index} is invalid")
    if not isinstance(data["facts"], list):
        raise CompositionError("record facts must be a list")
    fields = {"fact_type", "index", "sources", "renamings"}
    if has_resolution:
        fields.add("decisions")
    fact_coordinates = set()
    for index, fact in enumerate(data["facts"]):
        _keys(fact, fields, f"record fact {index}")
        if has_resolution:
            decisions = fact["decisions"]
            if (not isinstance(decisions, list) or not all(type(i) is int and i >= 0 for i in decisions)
                    or any(a >= b for a, b in pairwise(decisions))):
                raise CompositionError(f"record fact {index} decisions must be sorted distinct indexes")
        if not isinstance(fact["fact_type"], str) or type(fact["index"]) is not int or fact["index"] < 0:
            raise CompositionError(f"record fact {index} is invalid")
        if catalog:
            coordinate = fact["fact_type"], fact["index"]
            if coordinate in fact_coordinates:
                raise CompositionError(f"record fact {index} duplicates a candidate coordinate")
            fact_coordinates.add(coordinate)
        if not isinstance(fact["sources"], list) or not fact["sources"]:
            raise CompositionError(f"record fact {index} needs at least one source fact")
        for position, entry in enumerate(fact["sources"]):
            _lineage_entry(entry, f"record fact {index} source {position}")
            if catalog and entry["source"] not in source_ids:
                raise CompositionError(f"record fact {index} names an unknown candidate source")
        if not isinstance(fact["renamings"], list) or not all(type(item) is int and item >= 0 for item in fact["renamings"]):
            raise CompositionError(f"record fact {index} renamings must be manifest indexes")
    # One record, one identity (close review): the check reports the canonical
    # digest and a witness binds the raw one, so only canonical bytes are read.
    if raw != canonical_json_bytes(data):
        raise CompositionError("record is not in the canonical form gnd compose writes")
    return data


def _parse_catalog_roster(roster: object) -> None:
    if not isinstance(roster, list) or not 1 <= len(roster) <= 32:
        raise CompositionError("record references needs 1 to 32 entries")
    ids = []
    for entry in roster:
        _keys(entry, {"id", "raw_sha256"}, "record reference")
        identifier, digest = entry["id"], entry["raw_sha256"]
        if not isinstance(identifier, str) or not 1 <= len(identifier) <= 128:
            raise CompositionError("record reference id must be 1 to 128 characters")
        if not isinstance(digest, str) or not _HEX.fullmatch(digest):
            raise CompositionError("record reference digest is invalid")
        ids.append(identifier)
    if any(left >= right for left, right in pairwise(ids)):
        raise CompositionError("record reference ids must be sorted and distinct")


def catalog_roster(model: Model, *, references=None) -> list[dict[str, str]]:
    """Validate fixed catalog keys and admission before using candidate evidence."""
    if not model.reference_populations:
        return []
    try:
        context = resolve_context(model, references)
    except ReferenceInputError as error:
        raise CompositionError("reference populations require a current bound catalog context") from error
    owners = dict(context._owners)
    rows = {fact_type: facts for pop in context._populations for fact_type, facts in pop.facts.items()}
    directions = {
        "subset": (("subset_role_seq", "superset_role_seq"),),
        "equality": (("role_seq_a", "role_seq_b"), ("role_seq_b", "role_seq_a")),
    }
    for _, constraint, fact_type in ModelIndex.for_model(model).iter_constraints_shared():
        if constraint.get("status") != "confirmed" or constraint.get("modality", "alethic") != "alethic":
            continue
        if (constraint.get("type") == "uniqueness" and fact_type is not None
                and constraint.get("scope", "internal") == "internal"):
            fact_id = fact_type.get("id")
            roles = ModelIndex.constraint_roles(constraint)
            facts = rows.get(fact_id, ())
            if facts and len({tuple(identity_key(row[role]) for role in roles) for row in facts}) != len(facts):
                raise CompositionError(f"reference catalog key conflict for {fact_id}")
        for antecedent, consequent in directions.get(constraint.get("type"), ()):
            left = {role.get("fact_type") for role in constraint.get(antecedent, ())}
            right = {role.get("fact_type") for role in constraint.get(consequent, ())}
            if left and all(rows.get(fact_id) for fact_id in left) and right.difference(owners):
                raise CompositionError("reference catalog depends on candidate rows")
    return [{"id": origin.id, "raw_sha256": origin.raw_sha256} for origin, _, _ in context._snapshots]


def _read(path: Path, *, label: str, max_bytes: int) -> bytes:
    try:
        return read_regular_path(path, label=label, max_bytes=max_bytes)
    except Exception as error:
        raise CompositionError(f"{label} could not be read safely") from error


def _load_source(model: Model, directory: Path, source_id: str) -> Source:
    folder = directory / source_id
    population_raw = _read(folder / "population.json", label=f"source {source_id} population", max_bytes=MAX_POPULATION_BYTES)
    sidecar_raw = _read(folder / "population.json.anchors.json", label=f"source {source_id} sidecar", max_bytes=MAX_DOCUMENT_BYTES)
    document_raw = _read(folder / "document.txt", label=f"source {source_id} document", max_bytes=MAX_DOCUMENT_BYTES)
    try:
        population = load_population_bytes(population_raw, source=folder / "population.json", model=model)
    except PopulationLoadError as error:
        # Population messages can quote values; the refusal names the source only.
        raise CompositionError(f"source {source_id} population does not validate against the model") from error
    if model.reference_populations and any(ft in population.facts for ft, _ in model._references._owners):
        raise CompositionError(f"source {source_id} mentions a reference-owned fact type")
    try:
        sidecar = parse_anchor_sidecar(sidecar_raw)
        bind_anchors(sidecar, model, population_raw, document_raw, population)
    except AnchorError as error:
        raise CompositionError(f"source {source_id}: {error}") from error
    return Source(source_id, population, sidecar, document_raw, {
        "population_sha256": _sha(population_raw),
        "sidecar_sha256": _sha(sidecar_raw),
        "document_sha256": _sha(document_raw),
    })


def compose(model: Model, model_raw: bytes, directory: str | Path) -> Composition:
    """Compose the sources a manifest names; refuse instead of guessing."""
    return _compose(model, model_raw, directory, catalog_roster(model))


def _compose(model, model_raw, directory, references):
    directory = Path(directory)
    manifest_raw = _read(directory / "manifest.json", label="composition manifest", max_bytes=MAX_MANIFEST_BYTES)
    manifest = parse_manifest(manifest_raw)
    index_ = ModelIndex.for_model(model)
    evidence = None
    if manifest.resolution is not None:
        raw = _read(directory / manifest.resolution["path"], label="resolution", max_bytes=MAX_RESOLUTION_BYTES)
        if _sha(raw) != manifest.resolution["sha256"]:
            raise CompositionError("resolution digest differs from the manifest")
        resolution = parse_resolution(raw, index_, manifest.sources)
        for number, renaming in enumerate(manifest.renamings):
            object_type = index_.role_object_type(renaming["fact_type"], renaming["role"])
            resolution.check_renaming(number, renaming, object_type)
        sources = tuple(_load_source(model, directory, source_id) for source_id in manifest.sources)
        evidence = ResolutionEvidence(index_, sources, resolution)
        evidence.bind()
    roles = index_.fact_type_roles()
    renamings: dict[tuple[Any, ...], tuple[int, Any]] = {}
    instance_renamings: dict[tuple[Any, ...], tuple[int, Any]] = {}
    for index, renaming in enumerate(manifest.renamings):
        if renaming["role"] not in roles.get(renaming["fact_type"], set()):
            raise CompositionError(f"renaming {index} names a fact type or role the model does not declare")
        key = (renaming["source"], renaming["fact_type"], renaming["role"],
               type(renaming["from"]).__name__, repr(renaming["from"]))
        renamings[key] = (index, renaming["to"])
        # The same value listed as an instance of the role's object type in
        # that source is the same entity, so the renaming rewrites it too.
        object_type = index_.role_object_type(renaming["fact_type"], renaming["role"])
        if object_type is not None:
            instance_key = (renaming["source"], object_type, type(renaming["from"]).__name__, repr(renaming["from"]))
            first = instance_renamings.setdefault(instance_key, (index, renaming["to"]))
            target = (type(renaming["to"]).__name__, repr(renaming["to"]))
            # One entity cannot become two (close review): renamings of one
            # source value of one object type must agree on the new value.
            if (type(first[1]).__name__, repr(first[1])) != target:
                raise CompositionError(f"renamings {first[0]} and {index} rename one value to different values")
    if evidence is None:
        sources = tuple(_load_source(model, directory, source_id) for source_id in manifest.sources)
    if sum(len(rows) for source in sources for rows in source.population.facts.values()) > MAX_ENTRIES:
        raise CompositionError(f"composed fact count exceeds {MAX_ENTRIES}")

    facts: dict[str, list[dict[str, Any]]] = {}
    positions: dict[str, dict[tuple[Any, ...], int]] = {}
    lineage: dict[tuple[str, int], dict[str, Any]] = {}
    used: set[int] = set()
    kept: dict[tuple[Any, ...], tuple[str, str]] = {}
    instances: dict[str, dict[tuple[str, str], Any]] = {}
    covers: list[str] = []
    for source in sources:
        changed: dict[tuple[Any, ...], int] = {}
        for fact_type, rows in source.population.facts.items():
            composed = facts.setdefault(fact_type, [])
            index = positions.get(fact_type)
            if index is None:
                index = positions[fact_type] = _positions_factory()
            for fact_index, row in enumerate(rows):
                renamed, applied = dict(row), []
                for role, value in row.items():
                    hit = renamings.get((source.id, fact_type, role, type(value).__name__, repr(value)))
                    object_type = index_.role_object_type(fact_type, role)
                    entity = (source.id, object_type, type(value).__name__, repr(value))
                    if hit is not None:
                        renamed[role] = hit[1]
                        applied.append(hit[0])
                        changed.setdefault(entity, hit[0])
                        continue
                    if object_type is not None:
                        kept.setdefault(entity, (fact_type, role))
                key = _row_key(renamed)
                position = index.get(key)
                if position is None:
                    position = index[key] = len(composed)
                    composed.append(renamed)
                entry = lineage.setdefault((fact_type, position), {"sources": [], "renamings": set()})
                entry["sources"].append({"source": source.id, "fact_type": fact_type, "fact_index": fact_index})
                entry["renamings"].update(applied)
                used.update(applied)
        # One value of one object type is one entity in its source (owner
        # ruling after the close): renaming it in one role and keeping it in
        # another would split it, so the manifest must rename every use.
        for entity, renaming_index in changed.items():
            if entity in kept:
                fact_type, role = kept[entity]
                raise CompositionError(
                    f"renaming {renaming_index} splits a value of source {source.id}: "
                    f"{fact_type}.{role} still uses the old value; rename it there too")
        for object_type, values in source.population.instances.items():
            bucket = instances.setdefault(object_type, {})
            for value in values:
                instance_key = (source.id, object_type, type(value).__name__, repr(value))
                hit = instance_renamings.get(instance_key)
                if hit is not None:
                    # A fact row still using the old value would split the
                    # entity in two (close review), so refuse instead.
                    if instance_key in kept:
                        raise CompositionError(
                            f"renaming {hit[0]} renames an instance that another role of that source still uses unrenamed")
                    value = hit[1]
                bucket.setdefault((type(value).__name__, repr(value)), value)
        covers.extend(item for item in source.population.covers if item not in covers)
    unused = sorted(set(range(len(manifest.renamings))) - used)
    if unused:
        raise CompositionError(f"renaming {unused[0]} matches no row")

    first = sources[0].population
    header: dict[str, Any] = {"model": first.model, "source": first.source, "covers": covers}
    if first.model_id is not None:
        header["model_id"] = first.model_id
    if first.producer is not None:
        header["producer"] = first.producer
    document: dict[str, Any] = {
        "population": header,
        "instances": {key: list(bucket.values()) for key, bucket in instances.items()},
        "facts": facts,
    }
    format_version = max(source.population.format_version for source in sources)
    if format_version != 1:
        document["format_version"] = format_version
    population_bytes = canonical_json_bytes(document)
    try:
        load_population_bytes(population_bytes, source="composed.population.json", model=model)
    except PopulationLoadError as error:
        raise CompositionError("the composed population does not validate against the model") from error

    record = {
        "schema": RECORD_SCHEMA,
        "model_sha256": _sha(model_raw),
        "manifest_sha256": _sha(manifest_raw),
        "population_sha256": _sha(population_bytes),
        "sources": [{"id": source.id, **source.digests} for source in sources],
        "scope_tags": [dict(tag) for tag in manifest.scope_tags],
        "facts": [
            {"fact_type": fact_type, "index": position,
             "sources": lineage[(fact_type, position)]["sources"],
             "renamings": sorted(lineage[(fact_type, position)]["renamings"])}
            for fact_type in sorted(facts) for position in range(len(facts[fact_type]))
        ],
    }
    if references:
        record.update(schema=CATALOG_RECORD_SCHEMA, references=references)
    if evidence is not None:
        keys = evidence.collect_keys(instance_renamings)
        check_coverage(list(keys.values()), evidence.resolution.decisions,
                       other_outcomes=evidence.other_outcomes(keys, kept, instance_renamings))
        record["resolution_sha256"] = manifest.resolution["sha256"]
        evidence.stamp_lineage(record["facts"], MAX_RECORD_BYTES)
    record_bytes = canonical_json_bytes(record)
    if len(record_bytes) > MAX_RECORD_BYTES:
        raise CompositionError("the composition record would exceed its 16 MiB cap")
    return Composition(population_bytes, record, record_bytes, sources)


def verify_composition(
    model: Model, model_raw: bytes, population_raw: bytes, record: dict[str, Any], directory: str | Path,
) -> Composition:
    """Re-derive a composition from its inputs and compare it with the record."""
    references = catalog_roster(model)
    if record.get("references", []) != references:
        raise CompositionError("reference roster differs from the record")
    if record["model_sha256"] != _sha(model_raw):
        raise CompositionError("the model differs from the record's model digest")
    if record["population_sha256"] != _sha(population_raw):
        raise CompositionError("the composed population differs from the record's digest")
    derived = _compose(model, model_raw, directory, references)
    for key in ("manifest_sha256", "sources", "scope_tags", "resolution_sha256", "facts"):
        if derived.record.get(key) != record.get(key):
            raise CompositionError(f"re-derived composition differs from the record at {key}")
    if derived.population_bytes != population_raw:
        raise CompositionError("re-derived composed population bytes differ")
    return derived


def lineage_index(record: dict[str, Any]) -> dict[tuple[str, int], list[dict[str, Any]]]:
    return {(fact["fact_type"], fact["index"]): fact["sources"] for fact in record["facts"]}
