"""Render a GND model as a pinned Ossie ontology and bound interchange metadata."""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from functools import lru_cache
from graphlib import CycleError, TopologicalSorter
from importlib.resources import files
from io import StringIO
from pathlib import Path

from jsonschema import Draft202012Validator
from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError

from gnd.artifacts import canonical_json_bytes
from gnd.export.ossie_formulas import ProjectedRelation, place_formulas
from gnd.input_policy import MAX_BYTES, guard_yaml
from gnd.model import MAX_MODEL_BYTES, json_document, load_model_bytes, parse_model_document
from gnd.model._documents import ModelValueError
from gnd.model._includes import guard_document
from gnd.model_index import ModelIndex
from gnd.safefs import NotRegularFileError, open_regular
from gnd.values import ModelIdentityError, model_identity

_VERSION = "0.3.0.dev0"
_BUILTINS = frozenset(
    {"Any", "Boolean", "Date", "DateTime", "Decimal", "Float", "Integer", "String"}
)
_ALIAS = re.compile(r"[A-Za-z_][A-Za-z0-9_]*\Z")
_PLACEHOLDER = re.compile(r"\{([^{}]+)\}")
_NATIVE_LITERAL = ("native", "projected-with-source-spelling", None)
_POPULATION_REFUSAL = "population:out-of-scope"


class OssieInputError(ValueError):
    """The source cannot be exported with the selected policy."""


@dataclass(frozen=True)
class OssieArtifacts:
    document: bytes
    sidecar: bytes
    loss_report: bytes


@lru_cache(maxsize=1)
def _schema() -> Draft202012Validator:
    resource = files("gnd").joinpath("schema", "ossie", "ontology.json")
    return Draft202012Validator(json.loads(resource.read_bytes()))


def _read_model(path: Path):
    try:
        descriptor = open_regular(path)
    except NotRegularFileError as error:
        raise OssieInputError("model path is not a regular file") from error
    with open(descriptor, "rb") as stream:
        raw = stream.read(MAX_MODEL_BYTES + 1)
    try:
        if path.suffix != ".json":
            guard_yaml(raw, max_bytes=MAX_MODEL_BYTES)
        doc = parse_model_document(raw, source=path)
    except (YAMLError, ValueError, RecursionError, OverflowError) as error:
        raise OssieInputError("invalid model syntax or input limit exceeded") from error
    guard_document(doc, "export.ossie")
    model = load_model_bytes(raw, source=path)
    try:
        return json_document(doc), model
    except ModelValueError as error:
        raise OssieInputError(str(error)) from error


def _names(objects):
    counts = Counter(obj.get("name", oid) for oid, obj in objects.items())
    names = {
        oid: name
        for oid, obj in objects.items()
        if (name := obj.get("name", oid)) not in _BUILTINS
        and counts[name] == 1
        and _ALIAS.fullmatch(name)
    }
    used = set(names.values()) | _BUILTINS
    for oid in objects:
        if oid not in names:
            alias = f"gnd_{oid}"
            while alias in used:
                alias = "_" + alias
            names[oid] = alias
            used.add(alias)
    return names


def _pointers(*path) -> str:
    return "".join("/" + str(part).replace("~", "~0").replace("/", "~1") for part in path)


def _copy(target):
    return "native", "projection", target


def _role_order(fact):
    roles = tuple(role["role_name"] for role in fact["roles"])
    determinant_constraints = defaultdict(list)
    for i, constraint in enumerate(fact.get("constraints", ())):
        if (
            constraint["type"] == "uniqueness"
            and constraint.get("scope", "internal") == "internal"
            and constraint.get("modality") == "alethic"
            and constraint.get("status") == "confirmed"
        ):
            determinant_constraints[frozenset(constraint["roles"])].append(i)
    if len(roles) < 2:
        return roles, None, ()
    if len(roles) == 2 and all(frozenset({role}) in determinant_constraints for role in roles):
        return (
            roles,
            "OneToOne",
            tuple(i for role in roles for i in determinant_constraints[frozenset({role})]),
        )
    role_set = frozenset(roles)
    by_omitted = {
        next(iter(role_set - determinant)): indexes
        for determinant, indexes in determinant_constraints.items()
        if len(determinant) == len(roles) - 1 and determinant <= role_set
    }
    for omitted in reversed(roles):
        if selected := by_omitted.get(omitted):
            prefix = tuple(role for role in roles if role != omitted)
            return (*prefix, omitted), "ManyToOne", selected
    return roles, None, ()


def _verbalizes(fact, role_tokens):
    roles = [role["role_name"] for role in fact["roles"]]
    forward = iter(roles)
    readings = [_PLACEHOLDER.sub(lambda _match: role_tokens[next(forward)], fact["reading"])]
    inverse = fact.get("inverse_reading")
    if not inverse:
        return readings, False
    matches = list(_PLACEHOLDER.finditer(inverse))
    if not matches and len(roles) == 2:
        return [*readings, f"{role_tokens[roles[1]]} {inverse} {role_tokens[roles[0]]}"], True
    inverse_roles = [match[1].partition(":")[2].strip() for match in matches]
    if len(inverse_roles) == len(roles) and set(inverse_roles) == set(roles):
        readings.append(
            _PLACEHOLDER.sub(lambda match: role_tokens[match[1].partition(":")[2].strip()], inverse)
        )
        return readings, True
    return readings, False


def _relationship(fact, names, order):
    by_role = {role["role_name"]: names[role["object_type"]] for role in fact["roles"]}
    first, *additional = order
    roles = [{"concept": by_role[role], "name": role} for role in additional]
    tokens = {first: "{" + by_role[first] + "}"}
    tokens.update({role: f"{{{by_role[role]}:{role}}}" for role in additional})
    readings, inverse = _verbalizes(fact, tokens)
    result = {"name": fact["id"], "verbalizes": readings}
    if roles:
        result["roles"] = roles
    return result, inverse


def _add_references(objects, components, names, functional_links, constraints, mapped, indexes):
    # Pre-index composite UC candidates by their shared identifying entity.
    composite = {}
    for i, constraint in enumerate(constraints):
        if (
            constraint.get("type") != "uniqueness"
            or constraint.get("scope") != "external"
            or constraint.get("modality") != "alethic"
            or constraint.get("status") != "confirmed"
        ):
            continue
        links = []
        entity = None
        for ref in constraint.get("role_refs", ()):
            fact_id = ref["fact_type"]
            link = functional_links.get(fact_id)
            if link is None:
                break
            owner, dependent_role = link
            if dependent_role != ref["role"]:
                break
            if entity is not None and owner != entity:
                break
            entity = owner
            links.append(fact_id)
        else:
            if entity is not None and links:
                priority = bool(constraint.get("preferred"))
                previous = composite.get(entity)
                if previous is None or (priority and not previous[0]):
                    composite[entity] = (priority, i, links)

    for oid, obj in objects.items():
        ref = obj.get("reference") or {}
        component = components[oid]
        mode = ref.get("mode")
        path = ("object_types", indexes[oid], "reference")
        if mode in {"popular", "general"}:
            value_type = ref["value_type"]
            rels = component.setdefault("relationships", [])
            used = {r["name"] for r in rels}
            key = "gnd_reference"
            while key in used:
                key = "_" + key
            rels.append(
                {
                    "name": key,
                    "roles": [{"concept": names[value_type]}],
                    "verbalizes": [f"{{{names[oid]}}} is identified by {{{names[value_type]}}}"],
                    "multiplicity": "OneToOne",
                }
            )
            component["identify_by"] = [key]
            mapped[path] = _NATIVE_LITERAL
            mapped[(*path, "value_type")] = _NATIVE_LITERAL
        elif mode == "external" and oid in composite:
            _, index, links = composite[oid]
            component["identify_by"] = links
            mapped[path] = _NATIVE_LITERAL
            mapped[("constraints", index)] = _NATIVE_LITERAL


def _inherit_identifiers(objects, components, indexes, mapped):
    parents = {oid: tuple(obj.get("subtype_of") or ()) for oid, obj in objects.items()}
    try:
        order = list(TopologicalSorter(parents).static_order())
    except CycleError as error:
        raise OssieInputError("ossie:cyclic-subtypes") from error
    direct = {
        oid
        for oid, obj in objects.items()
        if (obj.get("reference") or {}).get("mode") in {"popular", "general"}
    }
    for oid in order:
        if not objects[oid].get("inherits_reference") or len(parents[oid]) != 1:
            continue
        parent = parents[oid][0]
        if parent not in direct:
            continue
        child = components[oid]
        inherited = components[parent]["identify_by"]
        own_names = {relationship["name"] for relationship in child.get("relationships", ())}
        if inherited and not child.get("identify_by") and own_names.isdisjoint(inherited):
            child["identify_by"] = list(inherited)
            direct.add(oid)
            mapped[("object_types", indexes[oid], "inherits_reference")] = _NATIVE_LITERAL


def _ontology(document, model):
    objects = ModelIndex.for_model(model).object_types_by_id()
    names = _names(objects)
    if not names:
        raise OssieInputError("an Ossie ontology requires at least one concept")
    indexes = {obj["id"]: i for i, obj in enumerate(document.get("object_types", ()))}
    components = {}
    mapped = {}
    for oid, i in indexes.items():
        obj = objects[oid]
        component = {
            "concept": names[oid],
            "type": "EntityType" if obj["kind"] == "entity" else "ValueType",
        }
        source = ("object_types", i)
        target = ("ontology", i)
        mapped[source] = _NATIVE_LITERAL
        mapped[(*source, "kind")] = _NATIVE_LITERAL
        if names[oid] == obj.get("name"):
            mapped[(*source, "name")] = _copy((*target, "concept"))
        parents = obj.get("subtype_of") or ()
        if parents:
            component["extends"] = [names[parent] for parent in parents]
            mapped[(*source, "subtype_of")] = _NATIVE_LITERAL
            for index in range(len(parents)):
                mapped[(*source, "subtype_of", index)] = _NATIVE_LITERAL
        primitive = obj.get("primitive")
        if primitive and not parents:
            base = {"Duration": "Integer", "Number": "Decimal"}.get(primitive, primitive)
            if base in _BUILTINS:
                component["extends"] = [base]
                if primitive == base:
                    mapped[(*source, "primitive")] = _copy((*target, "extends", 0))
        if obj.get("description"):
            component["description"] = obj["description"]["summary"]
            mapped[(*source, "description", "summary")] = _copy((*target, "description"))
        components[oid] = component

    functional_links = {}
    projected_relations = {}
    for i, fact in enumerate(document.get("fact_types", ())):
        order, multiplicity, constraints = _role_order(fact)
        role_source = {role["role_name"]: role for role in fact["roles"]}
        owner = role_source[order[0]]["object_type"]
        relationship, inverse = _relationship(fact, names, order)
        if multiplicity:
            relationship["multiplicity"] = multiplicity
        rels = components[owner].setdefault("relationships", [])
        target = ("ontology", indexes[owner], "relationships", len(rels))
        rels.append(relationship)
        projected_relations[fact["id"]] = ProjectedRelation(
            names[owner],
            tuple(role_source),
            order,
            {name: role["object_type"] for name, role in role_source.items()},
            relationship,
        )
        source = ("fact_types", i)
        for path in (source, (*source, "reading"), (*source, "roles")):
            mapped[path] = _NATIVE_LITERAL
        mapped[(*source, "id")] = _copy((*target, "name"))
        if inverse:
            mapped[(*source, "inverse_reading")] = _NATIVE_LITERAL
        role_positions = {role: index for index, role in enumerate(order)}
        for j, role in enumerate(fact["roles"]):
            projected_index = role_positions[role["role_name"]]
            path = (*source, "roles", j)
            mapped[path] = _NATIVE_LITERAL
            mapped[(*path, "object_type")] = _NATIVE_LITERAL
            if projected_index:
                mapped[(*path, "role_name")] = _copy(
                    (*target, "roles", projected_index - 1, "name")
                )
        for j in constraints:
            cpath = (*source, "constraints", j)
            constraint = fact["constraints"][j]
            for path in (cpath, (*cpath, "type"), (*cpath, "roles"), (*cpath, "scope")):
                mapped[path] = _NATIVE_LITERAL
            for k in range(len(constraint["roles"])):
                mapped[(*cpath, "roles", k)] = _NATIVE_LITERAL
        if len(order) == 2 and multiplicity:
            functional_links[fact["id"]] = (owner, order[1])
    _add_references(
        objects,
        components,
        names,
        functional_links,
        document.get("constraints", ()),
        mapped,
        indexes,
    )

    _inherit_identifiers(objects, components, indexes, mapped)

    ontology = {
        "version": _VERSION,
        "name": document.get("model_id") or "gnd_model",
        "ontology": list(components.values()),
    }
    if document.get("model_id"):
        mapped[("model_id",)] = _copy(("name",))
    place_formulas(document, ontology, components, projected_relations, mapped)
    return ontology, mapped


def _metadata(document, mapped):
    rows = []
    elements = defaultdict(dict)
    refused = False

    def visit(value, path=(), owner="", refusal=False, formula=False):
        nonlocal refused
        population = path == ("reference_populations",) or (
            len(path) == 3 and path[0] == "fact_types" and path[2] == "sample_population"
        )
        refusal = refusal or (population and bool(value))
        if isinstance(value, dict) and isinstance(value.get("id"), str):
            owner = value["id"]
        pointer = _pointers(*path)
        children = (
            value.items()
            if isinstance(value, dict)
            else enumerate(value)
            if isinstance(value, list)
            else ()
        )
        if refusal:
            refused = True
            disposition, reason = "refused", _POPULATION_REFUSAL
        else:
            fallback = (
                ("requires", "formula", None) if formula else ("extension", "gnd-source", None)
            )
            disposition, reason, target = mapped.get(path, fallback)
            if isinstance(value, dict):
                entry = {"kind": "object"}
            elif isinstance(value, list):
                entry = {"kind": "array"}
            elif target is not None:
                entry = {"kind": "copy", "from": _pointers(*target)}
            else:
                entry = {"kind": "literal", "value": value}
            elements[owner][pointer] = entry
        rows.append({"pointer": pointer, "disposition": disposition, "reason": reason})
        for key, child in children:
            visit(child, (*path, key), owner, refusal, disposition == "requires")

    visit(document)
    return rows, dict(elements), refused


def render_ossie(model_path: Path, *, output_format: str, strict: bool = False) -> OssieArtifacts:
    """Render three deterministic artifacts from one bounded, admitted model read."""
    document, model = _read_model(model_path)
    ontology, mapped = _ontology(document, model)
    _schema().validate(ontology)
    rows, elements, refused = _metadata(document, mapped)
    if strict and refused:
        raise OssieInputError(_POPULATION_REFUSAL)
    if output_format == "json":
        data = canonical_json_bytes(ontology)
    elif output_format == "yaml":
        yaml = YAML(typ="safe", pure=True)
        yaml.version = (1, 1)
        yaml.default_flow_style = False
        yaml.sort_base_mapping_type_on_output = False
        stream = StringIO()
        yaml.dump(ontology, stream)
        data = stream.getvalue().encode("utf-8")
    else:
        raise OssieInputError("unsupported Ossie output format")
    try:
        identity = model_identity(model)
        binding = {"model_identity": identity, "document_sha256": hashlib.sha256(data).hexdigest()}
        report = canonical_json_bytes(
            {"schema": "gnd-ossie-loss/1", **binding, "dispositions": rows}
        )
        sidecar = canonical_json_bytes(
            {"schema": "gnd-ossie-sidecar/1", **binding, "elements": elements}
        )
    except (ModelIdentityError, UnicodeEncodeError, ValueError) as error:
        raise OssieInputError("model has no encodable interchange identity") from error
    if max(len(data), len(sidecar), len(report)) > MAX_BYTES:
        raise OssieInputError("ossie:output-size")
    return OssieArtifacts(data, sidecar, report)
