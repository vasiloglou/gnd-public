"""Bounded, offline import of the pinned Apache Ossie ontology dialect."""

from __future__ import annotations

import hashlib
import json
import re
from collections import defaultdict
from dataclasses import dataclass
from functools import lru_cache
from graphlib import CycleError, TopologicalSorter
from importlib.resources import files
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from referencing.exceptions import Unresolvable
from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError

from gnd.artifacts import canonical_json_bytes
from gnd.errors import ModelLoadError, ModelValidationError
from gnd.input_policy import MAX_BYTES, MAX_DEPTH, guard_yaml, loads
from gnd.model import json_document, load_model_bytes
from gnd.model._documents import ModelValueError
from gnd.safefs import open_regular
from gnd.values import ModelIdentityError, model_identity

_CORE_URI = "https://raw.githubusercontent.com/apache/ossie/main/core-spec/ossie-schema.json"
_SCHEMA_HOME = ("schema", "ossie")
_PRIMITIVES = {
    "Boolean": "Boolean",
    "Date": "Date",
    "DateTime": "DateTime",
    "Decimal": "Number",
    "Float": "Float",
    "Integer": "Integer",
    "String": "String",
}
_BUILTINS = frozenset(_PRIMITIVES) | {"Any"}
_SHA = re.compile(r"[0-9a-f]{64}\Z")
_INDEX = re.compile(r"(?:0|[1-9][0-9]{0,8})\Z")
_POINTER_ESCAPE = re.compile(r"~(?![01])")
_ROLE_TOKEN = re.compile(r"\{([^{}:]+)(?::([^{}]+))?\}")
_FLIGHTS = "821d850f66098b2bb3ed8888e853a287627bb1eec676c2a7a190680d0ca89e87"
_OSSIE_COMMIT = "ee89dbdc2844d8b7d293ed42c8613928bb99505f"


class OssieImportError(ValueError):
    """A value-free refusal at a documented import boundary."""

    def __init__(self, rule: str):
        self.rule_id = f"ossie-import:{rule}"
        super().__init__(self.rule_id)


@dataclass(frozen=True)
class OssieImportResult:
    model: bytes
    loss_report: bytes


def _read(path: Path, rule: str, *, optional: bool = False) -> bytes | None:
    try:
        with open(open_regular(path), "rb") as stream:
            data = stream.read(MAX_BYTES + 1)
    except FileNotFoundError:
        if optional:
            try:
                path.lstat()
            except FileNotFoundError:
                return None
            except OSError:
                pass
        raise OssieImportError(rule) from None
    except (OSError, ValueError):
        raise OssieImportError(rule) from None
    if len(data) > MAX_BYTES:
        raise OssieImportError(f"{rule}-size")
    return data


def _parse(data: bytes, rule: str, *, yaml: bool = False):
    try:
        if yaml:
            guard_yaml(data)
            document = json_document(YAML(typ="safe").load(data))
        else:
            document = loads(data)
        # JSON permits escapes for isolated UTF-16 surrogates. The wire format is UTF-8.
        for part in json.JSONEncoder(ensure_ascii=False).iterencode(document):
            part.encode("utf-8")
        return document
    except (YAMLError, ModelValueError, ValueError, TypeError, RecursionError, OverflowError):
        raise OssieImportError(rule) from None


@lru_cache(maxsize=1)
def _schemas():
    package = files("gnd")
    root = package.joinpath(*_SCHEMA_HOME)
    ontology = json.loads(root.joinpath("ontology.json").read_bytes())
    core = Resource.from_contents(json.loads(root.joinpath("core-spec.json").read_bytes()))
    # Registry() refuses unregistered retrieval. No URI in user input opens a connection.
    registry = Registry().with_resource(_CORE_URI, core)
    report = json.loads(package.joinpath("ossie-loss-report.schema.json").read_bytes())
    return Draft202012Validator(ontology, registry=registry), Draft202012Validator(report)


def _schema_check(document, validator, rule: str) -> None:
    try:
        valid = validator.is_valid(document)
    except (Unresolvable, ValueError, TypeError, RecursionError, OverflowError):
        raise OssieImportError(rule) from None
    if not valid:
        raise OssieImportError(rule)


def _pointer(parts) -> str:
    return "".join("/" + str(part).replace("~", "~0").replace("/", "~1") for part in parts)


def _tokens(pointer) -> tuple[str, ...]:
    if not isinstance(pointer, str) or (pointer and not pointer.startswith("/")):
        raise OssieImportError("sidecar-pointer")
    parts = pointer.split("/")[1:]
    if len(parts) > MAX_DEPTH or any(_POINTER_ESCAPE.search(part) for part in parts):
        raise OssieImportError("sidecar-pointer")
    return tuple(part.replace("~1", "/").replace("~0", "~") for part in parts)


def _scalar(value) -> bool:
    return type(value) in {str, int, float, bool, type(None)}


def _value_at(document, pointer):
    for key in _tokens(pointer):
        if isinstance(document, dict) and key in document:
            document = document[key]
        elif isinstance(document, list) and _INDEX.fullmatch(key) and int(key) < len(document):
            document = document[int(key)]
        else:
            raise OssieImportError("sidecar-pointer")
    if not _scalar(document):
        raise OssieImportError("sidecar-entry")
    return document


class _NameGraph:
    def __init__(self, document):
        components = document["ontology"]
        self.concepts = {item["concept"]: item for item in components}
        if len(self.concepts) != len(components) or self.concepts.keys() & _BUILTINS:
            raise OssieImportError("concept-name")
        declared = self.concepts.keys() | _BUILTINS
        self.parents = {}
        self.relationships = {}
        for name, concept in self.concepts.items():
            self.parents[name] = tuple(concept.get("extends", ()))
            relations = concept.get("relationships", ())
            local = {rel["name"]: rel for rel in relations}
            if len(local) != len(relations):
                raise OssieImportError("relationship-name")
            self.relationships[name] = local
            for target in self.parents[name]:
                if target not in declared:
                    raise OssieImportError("reference")
            for rel in relations:
                if any(role["concept"] not in declared for role in rel.get("roles", ())):
                    raise OssieImportError("reference")
        try:
            self.order = tuple(
                TopologicalSorter(
                    {
                        name: [parent for parent in parents if parent in self.concepts]
                        for name, parents in self.parents.items()
                    }
                ).static_order()
            )
        except CycleError:
            raise OssieImportError("cycle") from None
        self._budget = max(2_048, 32 * (len(components) + sum(map(len, self.parents.values()))))
        self._cache = {}
        for name in self.order:
            for identifier in self.concepts[name].get("identify_by", ()):
                if self.resolve(name, identifier) is None:
                    raise OssieImportError("reference")

    def resolve(self, name, relationship):
        key = (name, relationship)
        if key in self._cache:
            return self._cache[key]
        pending = [name]
        seen = set()
        found = None
        while pending:
            current = pending.pop()
            if current in seen:
                continue
            parents = self.parents.get(current, ())
            self._budget -= 1 + len(parents)
            if self._budget < 0:
                raise OssieImportError("reference-budget")
            seen.add(current)
            cached = (current, relationship)
            if cached in self._cache:
                if self._cache[cached] is not None:
                    found = self._cache[cached]
                    break
                continue
            local = self.relationships.get(current, {})
            if relationship in local:
                found = (current, local[relationship])
                break
            pending.extend(reversed(parents))
        self._cache[key] = found
        return found


def _hex(value):
    return isinstance(value, str) and bool(_SHA.fullmatch(value))


def _identity(value):
    return isinstance(value, str) and value.startswith("sha256:") and _hex(value[7:])


def _binding(sidecar, digest):
    if (
        not isinstance(sidecar, dict)
        or sidecar.keys() != {"schema", "model_identity", "document_sha256", "elements"}
        or sidecar["schema"] != "gnd-ossie-sidecar/1"
        or not _identity(sidecar["model_identity"])
        or not _hex(sidecar["document_sha256"])
    ):
        raise OssieImportError("sidecar-header")
    if sidecar["document_sha256"] != digest:
        raise OssieImportError("binding")


def _restore(sidecar, ontology):
    groups = sidecar["elements"]
    if not isinstance(groups, dict):
        raise OssieImportError("sidecar-entry")
    entries = {}
    pointers = set()
    children = defaultdict(list)
    for group in groups.values():
        if not isinstance(group, dict):
            raise OssieImportError("sidecar-entry")
        for pointer, entry in group.items():
            path = _tokens(pointer)
            if path in entries:
                raise OssieImportError("sidecar-pointer")
            entries[path] = entry
            pointers.add(pointer)
            if path:
                children[path[:-1]].append(path[-1])
    if () not in entries or children.keys() - entries.keys():
        raise OssieImportError("sidecar-pointer")

    def build(path):
        entry = entries[path]
        if not isinstance(entry, dict):
            raise OssieImportError("sidecar-entry")
        kind = entry.get("kind")
        keys = children.get(path, ())
        if kind in ("object", "array") and entry.keys() == {"kind"}:
            if kind == "object":
                return {key: build((*path, key)) for key in keys}
            if set(keys) != {str(i) for i in range(len(keys))}:
                raise OssieImportError("sidecar-pointer")
            return [build((*path, str(i))) for i in range(len(keys))]
        if keys:
            raise OssieImportError("sidecar-pointer")
        if kind == "literal" and entry.keys() == {"kind", "value"} and _scalar(entry["value"]):
            return entry["value"]
        if kind == "copy" and entry.keys() == {"kind", "from"}:
            return _value_at(ontology, entry["from"])
        raise OssieImportError("sidecar-entry")

    return build(()), pointers


def _source_dispositions(report, retained):
    if report is None:
        return [
            {"pointer": p, "disposition": "extension", "reason": "gnd-source"}
            for p in sorted(retained)
        ]
    rows = report["dispositions"]
    seen = set()
    refused = {}
    for row in rows:
        path = row["pointer"]
        parts = _tokens(path)
        is_refused = row["disposition"] == "refused"
        if path in seen or ((path in retained) == is_refused):
            raise OssieImportError("report-pointer")
        seen.add(path)
        if is_refused:
            refused[path] = parts
    if retained - seen:
        raise OssieImportError("report-pointer")
    for path, parts in refused.items():
        population_root = parts == ("reference_populations",) or (
            len(parts) == 3 and parts[0] == "fact_types"
            and _INDEX.fullmatch(parts[1]) and parts[2] == "sample_population"
        )
        parent = path.rsplit("/", 1)[0]
        if parent not in (retained if population_root else refused):
            raise OssieImportError("report-pointer")
    return rows


def _bounded_model(document, source_identity, *, require_identity: bool) -> tuple[bytes, bool]:
    encoder = json.JSONEncoder(
        ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")
    )
    result = bytearray()
    try:
        for part in encoder.iterencode(document):
            data = part.encode("utf-8")
            if len(result) + len(data) >= MAX_BYTES:
                raise OssieImportError("model-size")
            result.extend(data)
    except OssieImportError:
        raise
    except (ValueError, TypeError, RecursionError, OverflowError):
        raise OssieImportError("model") from None
    result.extend(b"\n")
    data = bytes(result)
    try:
        admitted = load_model_bytes(data, source="restored.orm.json")
    except (ModelLoadError, ModelValidationError, ValueError, RecursionError, OverflowError):
        raise OssieImportError("model") from None
    identity_verified = False
    if source_identity is not None:
        try:
            identity_verified = model_identity(admitted) == source_identity
        except ModelIdentityError:
            raise OssieImportError("model-identity") from None
        if require_identity and not identity_verified:
            raise OssieImportError("model-identity")
    return data, identity_verified


class _Identifiers:
    def __init__(self):
        self.used = set()
        self.counters = defaultdict(int)

    def take(self, raw: str) -> str:
        text = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", raw)
        base = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
        if not base or not base[0].isalpha():
            base = "ossie_" + base
        candidate = base
        while candidate in self.used:
            self.counters[base] += 1
            candidate = f"{base}_{self.counters[base]}"
        self.used.add(candidate)
        return candidate


def _walk(value, path=()):
    yield path
    if isinstance(value, dict):
        for key, child in value.items():
            yield from _walk(child, (*path, key))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk(child, (*path, index))


def _foreign_rows(document, projected):
    for path in _walk(document):
        disposition, reason = projected.get(path, ("refused", "foreign:unsupported"))
        yield {"pointer": _pointer(path), "disposition": disposition, "reason": reason}


def _provenance(digest, path):
    result = {
        "origin": "imported",
        "framework": "apache-ossie",
        "sha256": digest,
        "source_pointer": _pointer(path),
    }
    if digest == _FLIGHTS:
        result.update(artifact="examples/flights.ontology.yaml", commit=_OSSIE_COMMIT)
    return result


def _concepts(graph, ids, digest, projected):
    available = {}
    for name in _BUILTINS:
        if name in _PRIMITIVES:
            available[name] = {"kind": "value", "primitive": _PRIMITIVES[name]}
    used_builtins = set()
    positions = {name: i for i, name in enumerate(graph.concepts)}
    for name in graph.order:
        item = graph.concepts[name]
        i = positions[name]
        source = ("ontology", i)
        kind = "entity" if item["type"] == "EntityType" else "value"
        parents = graph.parents[name]
        if kind == "value":
            primitives = {
                available[parent].get("primitive") for parent in parents if parent in available
            }
            if len(primitives) != 1 or None in primitives:
                continue
            (primitive,) = primitives
        obj = {
            "id": ids[name],
            "name": name,
            "kind": kind,
            "provenance": _provenance(digest, source),
        }
        if kind == "value":
            obj["primitive"] = primitive
        for path in (source, (*source, "concept"), (*source, "type")):
            projected[path] = ("native", "projection")
        retained_parents = []
        for j, parent in enumerate(parents):
            if parent not in available or available[parent]["kind"] != kind:
                continue
            if parent == "Decimal":
                projected[(*source, "extends", j)] = ("refused", "foreign:decimal-domain")
                continue
            projected[(*source, "extends", j)] = ("native", "projection")
            if parent not in _PRIMITIVES:
                retained_parents.append(ids[parent])
                if parent in _BUILTINS:
                    used_builtins.add(parent)
        if parents and all(
            projected.get((*source, "extends", j)) == ("native", "projection")
            for j in range(len(parents))
        ):
            projected[(*source, "extends")] = ("native", "projection")
        if retained_parents:
            obj["subtype_of"] = list(dict.fromkeys(retained_parents))
            obj["inherits_reference"] = False
        if item.get("description"):
            obj["description"] = {"summary": item["description"]}
            projected[(*source, "description")] = ("native", "projection")
        available[name] = obj
    return available, used_builtins


def _foreign_reading(readings, source_roles, ids):
    if not readings:
        raise OssieImportError("reading")
    text = readings[0]
    if re.search(r"[{}]", _ROLE_TOKEN.sub("", text)):
        raise OssieImportError("reading")
    positions = defaultdict(list)
    for i, pair in enumerate(source_roles):
        positions[pair].append(i)
    offsets = defaultdict(int)
    order = []

    def replace(match):
        concept = match[1].strip()
        pair = (concept, match[2].strip() if match[2] else None)
        candidates = positions.get(pair, ())
        offset = offsets[pair]
        if offset >= len(candidates):
            raise OssieImportError("reading")
        offsets[pair] += 1
        order.append(candidates[offset])
        return "{" + ids[concept] + "}"

    reading = _ROLE_TOKEN.sub(replace, text)
    if len(order) != len(source_roles):
        raise OssieImportError("reading")
    return reading, order


def _foreign_fact(owner, relationship, ids, available, names, digest, path, projected):
    additional = relationship.get("roles", ())
    source_roles = [(owner, None), *((role["concept"], role.get("name")) for role in additional)]
    if any(concept not in available for concept, _ in source_roles):
        return None
    try:
        reading, order = _foreign_reading(relationship["verbalizes"], source_roles, ids)
    except OssieImportError:
        return None
    roles = _Identifiers()
    authored_roles = [
        {"object_type": ids[player], "role_name": roles.take(label or player)}
        for player, label in source_roles
    ]
    fact = {
        "id": names.take(f"{owner}_{relationship['name']}"),
        "reading": reading,
        "roles": [authored_roles[i] for i in order],
        "provenance": _provenance(digest, path),
    }
    for source in (path, (*path, "name"), (*path, "verbalizes", 0)):
        projected[source] = ("native", "projection")
    if len(relationship["verbalizes"]) == 1:
        projected[(*path, "verbalizes")] = ("native", "projection")
    if "roles" in relationship:
        for child in _walk(relationship["roles"], (*path, "roles")):
            projected[child] = ("native", "projection")

    multiplicity = relationship.get("multiplicity")
    if (
        digest == _FLIGHTS
        and len(authored_roles) > 1
        and (
            multiplicity == "ManyToOne" or (multiplicity == "OneToOne" and len(authored_roles) == 2)
        )
    ):
        role_names = [role["role_name"] for role in authored_roles]
        keys = [role_names[:-1]] if multiplicity == "ManyToOne" else [[r] for r in role_names]
        provenance = _provenance(digest, (*path, "multiplicity"))
        provenance["anchor"] = f"multiplicity: {multiplicity}"
        fact["constraints"] = [
            {
                "type": "uniqueness",
                "roles": key,
                "source": "imported",
                "status": "proposed",
                "modality": "alethic",
                "provenance": provenance,
            }
            for key in keys
        ]
        projected[(*path, "multiplicity")] = ("native", "projection")
    return fact


def _foreign_identifiers(graph, ids, available, projected):
    positions = {name: i for i, name in enumerate(graph.concepts)}
    for name in graph.order:
        if name not in available or available[name]["kind"] != "entity":
            continue
        item = graph.concepts[name]
        i = positions[name]
        obj = available[name]
        retained = []
        for j, parent in enumerate(graph.parents[name]):
            if parent in available and available[parent]["kind"] == "entity":
                retained.append(ids[parent])
            else:
                projected.pop(("ontology", i, "extends", j), None)
                projected.pop(("ontology", i, "extends"), None)
        if retained:
            obj["subtype_of"] = list(dict.fromkeys(retained))
        else:
            obj.pop("subtype_of", None)
            obj.pop("inherits_reference", None)

        identifiers = item.get("identify_by", ())
        if len(identifiers) == 1:
            relationship = graph.relationships[name].get(identifiers[0])
            roles = relationship.get("roles", ()) if relationship is not None else ()
            if len(roles) == 1:
                player = roles[0]["concept"]
                if available.get(player, {}).get("kind") == "value":
                    try:
                        _foreign_reading(
                            relationship["verbalizes"], [(name, None), (player, roles[0].get("name"))], ids
                        )
                    except OssieImportError:
                        pass
                    else:
                        obj["reference"] = {"mode": "general", "value_type": ids[player]}
                        projected[("ontology", i, "identify_by")] = ("native", "projection")
                        projected[("ontology", i, "identify_by", 0)] = ("native", "projection")
        if "reference" not in obj and "subtype_of" not in obj:
            del available[name]
            for path in _walk(item, ("ontology", i)):
                projected.pop(path, None)


def _foreign(document, graph, digest):
    names = _Identifiers()
    ids = {name: names.take(name) for name in (*graph.concepts, *sorted(_BUILTINS))}
    projected = {(): ("native", "projection"), ("ontology",): ("native", "projection")}
    available, used_builtins = _concepts(graph, ids, digest, projected)
    _foreign_identifiers(graph, ids, available, projected)
    facts = []
    for i, (name, concept) in enumerate(graph.concepts.items()):
        if name not in available:
            continue
        relationships = concept.get("relationships", ())
        if "relationships" in concept:
            projected[("ontology", i, "relationships")] = ("native", "projection")
        for j, relationship in enumerate(relationships):
            path = ("ontology", i, "relationships", j)
            fact = _foreign_fact(name, relationship, ids, available, names, digest, path, projected)
            if fact is not None:
                facts.append(fact)
                used_builtins.update(
                    r["concept"] for r in relationship.get("roles", ()) if r["concept"] in _BUILTINS
                )

    objects = [available[name] for name in graph.concepts if name in available]
    for name in sorted(used_builtins):
        objects.append({"id": ids[name], "name": name, **available[name]})
    if not objects:
        raise OssieImportError("foreign-empty")
    source = _provenance(digest, ())
    source.update(ontology_name=document["name"], ontology_version=document["version"])
    projected[("name",)] = projected[("version",)] = ("native", "projection")
    if "description" in document:
        source["ontology_description"] = document["description"]
        projected[("description",)] = ("native", "projection")
    result = {
        "version": 3,
        "model_id": f"urn:gnd:ossie:{digest}",
        "source": source,
        "object_types": objects,
        "fact_types": facts,
    }
    return result, _foreign_rows(document, projected)


def _loss_report_bytes(digest, source_identity, identity_verified, rows) -> bytes:
    # Serialize each row once and cap the total before a foreign tree can
    # amplify to a large report through repeated pointer prefixes.
    empty = canonical_json_bytes({
        "schema": "gnd-ossie-import-loss/1",
        "document_sha256": digest,
        "source_model_identity": source_identity,
        "source_identity_verified": identity_verified,
        "dispositions": [],
    })
    prefix, _, suffix = empty.partition(b'"dispositions":[]')
    result = bytearray(prefix)
    result.extend(b'"dispositions":[')
    for i, row in enumerate(rows):
        data = canonical_json_bytes(row).rstrip()
        if len(result) + len(data) + len(suffix) + 2 > 2 * MAX_BYTES:
            raise OssieImportError("loss-size")
        if i:
            result.extend(b",")
        result.extend(data)
    result.extend(b"]")
    result.extend(suffix)
    return bytes(result)


def plan_ossie_import(path: Path) -> OssieImportResult:
    """Admit one standalone ontology or bound bundle without network access."""
    raw = _read(path, "input")
    assert raw is not None
    ontology = _parse(raw, "syntax", yaml=path.suffix.lower() != ".json")
    _schema_check(ontology, _schemas()[0], "schema")
    graph = _NameGraph(ontology)
    digest = hashlib.sha256(raw).hexdigest()
    sidecar_raw = _read(path.with_name(path.name + ".gnd.json"), "sidecar-input", optional=True)
    source_identity = None
    require_identity = False
    if sidecar_raw is None:
        model, rows = _foreign(ontology, graph, digest)
    else:
        sidecar = _parse(sidecar_raw, "sidecar-syntax")
        _binding(sidecar, digest)
        source_identity = sidecar["model_identity"]
        report_raw = _read(path.with_name(path.name + ".loss.json"), "report-input", optional=True)
        report = _parse(report_raw, "report-syntax") if report_raw is not None else None
        if report_raw is not None:
            _schema_check(report, _schemas()[1], "report-schema")
            if any(report[key] != sidecar[key] for key in ("model_identity", "document_sha256")):
                raise OssieImportError("report-binding")
        model, retained = _restore(sidecar, ontology)
        rows = _source_dispositions(report, retained)
        require_identity = report is not None and all(row["disposition"] != "refused" for row in rows)
    model_bytes, identity_verified = _bounded_model(model, source_identity, require_identity=require_identity)
    return OssieImportResult(
        model_bytes, _loss_report_bytes(digest, source_identity, identity_verified, rows)
    )
