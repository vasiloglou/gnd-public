"""Compose several anchored populations into one population with lineage (CT2).

A composition directory holds ``manifest.json`` and, for each source id,
``<id>/population.json``, its adjacent sidecar and ``<id>/document.txt``.
The manifest lists every change composition makes; nothing is inferred. The
record written beside the composed population is value-free: digests, ids
and indexes only.
"""

from __future__ import annotations

import hashlib
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from gnd.anchors import (
    MAX_DOCUMENT_BYTES,
    AnchorError,
    AnchorSidecar,
    bind_anchors,
    parse_anchor_sidecar,
    read_regular_path,
    strict_json,
)
from gnd.artifacts import canonical_json_bytes
from gnd.model import MAX_ENTRIES, Model
from gnd.model_index import ModelIndex
from gnd.population import (
    MAX_POPULATION_BYTES,
    Population,
    PopulationLoadError,
    load_population_bytes,
)

MANIFEST_SCHEMA = "gnd-composition-manifest/1"
RECORD_SCHEMA = "gnd-composition/1"
MAX_MANIFEST_BYTES = 1 << 20
MAX_RECORD_BYTES = 16 << 20
_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
_HEX = re.compile(r"^[0-9a-f]{64}$")
# The per-fact-type row index; a test substitutes a counting mapping (T6).
_positions_factory = dict


class CompositionError(ValueError):
    """A bounded, value-free composition refusal (exit 3)."""

    def __init__(self, message: str) -> None:
        super().__init__(f"composition:invalid: {message}")


@dataclass(frozen=True)
class Manifest:
    sources: tuple[str, ...]
    renamings: tuple[dict[str, Any], ...]
    scope_tags: tuple[dict[str, str], ...]


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


def _row_key(row: dict[str, Any]) -> tuple[Any, ...]:
    return tuple((name, type(value).__name__, repr(value)) for name, value in sorted(row.items()))


def _scalar(value: Any) -> bool:
    return isinstance(value, (str, bool, int)) or (isinstance(value, float) and math.isfinite(value))


def _keys(value: Any, keys: set[str], what: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != keys:
        raise CompositionError(f"{what} has missing or unexpected fields")
    return value


def _json(raw: bytes, *, max_bytes: int, what: str) -> Any:
    try:
        return strict_json(raw, max_bytes=max_bytes, too_large=f"{what} exceeds its size cap")
    except (ValueError, TypeError, UnicodeError, RecursionError) as error:
        raise CompositionError(f"{what}: {error}") from error


def parse_manifest(raw: bytes) -> Manifest:
    data = _keys(_json(raw, max_bytes=MAX_MANIFEST_BYTES, what="manifest"),
                 {"schema", "sources", "renamings", "deduplications", "scope_tags"}, "manifest")
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
    for index, renaming in enumerate(data["renamings"]):
        _keys(renaming, {"source", "fact_type", "role", "from", "to"}, f"renaming {index}")
        if renaming["source"] not in sources:
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
        if tag["source"] not in sources:
            raise CompositionError(f"scope tag {index} names an unknown source")
        if not isinstance(tag["tag"], str) or not 0 < len(tag["tag"]) <= 128:
            raise CompositionError(f"scope tag {index} must be 1 to 128 characters")
    return Manifest(tuple(sources), tuple(data["renamings"]), tuple(data["scope_tags"]))


def _lineage_entry(value: Any, what: str) -> dict[str, Any]:
    _keys(value, {"source", "fact_type", "fact_index"}, what)
    if (not isinstance(value["source"], str) or not isinstance(value["fact_type"], str)
            or type(value["fact_index"]) is not int or value["fact_index"] < 0):
        raise CompositionError(f"{what} is invalid")
    return value


def parse_record(raw: bytes) -> dict[str, Any]:
    data = _keys(_json(raw, max_bytes=MAX_RECORD_BYTES, what="record"),
                 {"schema", "model_sha256", "manifest_sha256", "population_sha256", "sources", "scope_tags", "facts"},
                 "record")
    if data["schema"] != RECORD_SCHEMA:
        raise CompositionError("record schema is not gnd-composition/1")
    for key in ("model_sha256", "manifest_sha256", "population_sha256"):
        if not isinstance(data[key], str) or not _HEX.fullmatch(data[key]):
            raise CompositionError(f"record {key} is not a SHA-256 digest")
    if not isinstance(data["sources"], list) or not data["sources"]:
        raise CompositionError("record sources must be a non-empty list")
    for index, source in enumerate(data["sources"]):
        _keys(source, {"id", "population_sha256", "sidecar_sha256", "document_sha256"}, f"record source {index}")
        if not isinstance(source["id"], str) or not _ID.fullmatch(source["id"]):
            raise CompositionError(f"record source {index} has an invalid id")
        if not all(isinstance(source[key], str) and _HEX.fullmatch(source[key])
                   for key in ("population_sha256", "sidecar_sha256", "document_sha256")):
            raise CompositionError(f"record source {index} has an invalid digest")
    if not isinstance(data["scope_tags"], list):
        raise CompositionError("record scope_tags must be a list")
    for index, tag in enumerate(data["scope_tags"]):
        _keys(tag, {"source", "tag"}, f"record scope tag {index}")
        if not isinstance(tag["source"], str) or not isinstance(tag["tag"], str):
            raise CompositionError(f"record scope tag {index} is invalid")
    if not isinstance(data["facts"], list):
        raise CompositionError("record facts must be a list")
    for index, fact in enumerate(data["facts"]):
        _keys(fact, {"fact_type", "index", "sources", "renamings"}, f"record fact {index}")
        if not isinstance(fact["fact_type"], str) or type(fact["index"]) is not int or fact["index"] < 0:
            raise CompositionError(f"record fact {index} is invalid")
        if not isinstance(fact["sources"], list) or not fact["sources"]:
            raise CompositionError(f"record fact {index} needs at least one source fact")
        for position, entry in enumerate(fact["sources"]):
            _lineage_entry(entry, f"record fact {index} source {position}")
        if not isinstance(fact["renamings"], list) or not all(type(item) is int and item >= 0 for item in fact["renamings"]):
            raise CompositionError(f"record fact {index} renamings must be manifest indexes")
    # One record, one identity (close review): the check reports the canonical
    # digest and a witness binds the raw one, so only canonical bytes are read.
    if raw != canonical_json_bytes(data):
        raise CompositionError("record is not in the canonical form gnd compose writes")
    return data


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
    directory = Path(directory)
    if model.reference_populations:
        raise CompositionError("composition with reference populations is unsupported")
    manifest_raw = _read(directory / "manifest.json", label="composition manifest", max_bytes=MAX_MANIFEST_BYTES)
    manifest = parse_manifest(manifest_raw)
    index_ = ModelIndex.for_model(model)
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
    record_bytes = canonical_json_bytes(record)
    if len(record_bytes) > MAX_RECORD_BYTES:
        raise CompositionError("the composition record would exceed its 16 MiB cap")
    return Composition(population_bytes, record, record_bytes, sources)


def verify_composition(
    model: Model, model_raw: bytes, population_raw: bytes, record: dict[str, Any], directory: str | Path,
) -> Composition:
    """Re-derive a composition from its inputs and compare it with the record."""
    if record["model_sha256"] != _sha(model_raw):
        raise CompositionError("the model differs from the record's model digest")
    if record["population_sha256"] != _sha(population_raw):
        raise CompositionError("the composed population differs from the record's digest")
    derived = compose(model, model_raw, directory)
    for key in ("manifest_sha256", "sources", "scope_tags", "facts"):
        if derived.record[key] != record[key]:
            raise CompositionError(f"re-derived composition differs from the record at {key}")
    if derived.population_bytes != population_raw:
        raise CompositionError("re-derived composed population bytes differ")
    return derived


def lineage_index(record: dict[str, Any]) -> dict[tuple[str, int], list[dict[str, Any]]]:
    return {(fact["fact_type"], fact["index"]): fact["sources"] for fact in record["facts"]}
