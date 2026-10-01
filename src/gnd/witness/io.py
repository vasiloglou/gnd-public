"""Bounded wire intake, structural validation and byte-bound input identities.

This module has no derivation evaluator or comparison semantics. Both sides may
share its structural reader; replay never trusts producer validation markers.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from datetime import date
from pathlib import Path

from gnd.artifacts import canonical_json_bytes
from gnd.model import iter_derivation_clauses, load_model_bytes
from gnd.population import _build_population, _parse_document_bytes, load_population_bytes
from gnd.popvalidate import resolve_primitive
from gnd.references import (
    MAX_ENTRIES,
    MAX_SET_BYTES,
    reference_model_digest,
    resolve_context,
    validate_declarations,
    validate_reference_structure,
)
from gnd.witness.types import DEFAULT_LIMITS, WitnessInputError, checked_limits


def validate_witness_structure(document: object, *, limits=DEFAULT_LIMITS) -> int:
    limits = checked_limits(limits)

    def children(value, depth):
        if type(value) is dict:
            for key, child in value.items():
                if type(key) is not str:
                    raise WitnessInputError("object keys must be strings")
                yield key, depth
                yield child, depth
        else:
            for child in value:
                yield child, depth

    stack = [iter(((document, 0),))]
    visits = 0
    while stack:
        try:
            value, parent = next(stack[-1])
        except StopIteration:
            stack.pop()
            continue
        visits += 1
        if visits > limits.bytes:
            raise WitnessInputError("container work exceeds intake ceiling")
        if type(value) in (dict, list):
            depth = parent + 1
            if depth > limits.container_depth:
                raise WitnessInputError("container depth exceeds ceiling")
            stack.append(children(value, depth))
        elif type(value) is str:
            if len(value.encode("utf-8")) > limits.scalar_bytes:
                raise WitnessInputError("scalar bytes exceed ceiling")
        elif type(value) is int:
            if len(str(abs(value))) > limits.numeric_digits:
                raise WitnessInputError("numeric digits exceed ceiling")
        elif type(value) is float:
            if not math.isfinite(value):
                raise WitnessInputError("nonfinite number")
        elif value is not None and type(value) is not bool:
            raise WitnessInputError("non-JSON value")

    # Stream the wire representation: in-memory callers have the same byte
    # ceiling as file callers, without allocating a second full document.
    size = 0
    encoder = json.JSONEncoder(ensure_ascii=False, allow_nan=False, separators=(",", ":"))
    for chunk in encoder.iterencode(document):
        size += len(chunk.encode("utf-8"))
        if size > limits.bytes:
            raise WitnessInputError("wire bytes exceed ceiling")
    return size


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise WitnessInputError("duplicate object key")
        result[key] = value
    return result


def parse_wire(raw: bytes, *, limits=DEFAULT_LIMITS):
    checked_limits(limits)
    if len(raw) > limits.bytes:
        raise WitnessInputError("wire bytes exceed ceiling")
    try:
        doc = json.loads(
            raw,
            object_pairs_hook=_pairs,
            parse_constant=lambda _: (_ for _ in ()).throw(WitnessInputError("nonfinite")),
        )
        validate_witness_structure(doc, limits=limits)
        return doc
    except (ValueError, RecursionError, UnicodeError) as error:
        raise WitnessInputError("invalid JSON wire") from error


def read_wire(path, *, limits=DEFAULT_LIMITS):
    checked_limits(limits)
    with Path(path).open("rb") as stream:
        return parse_wire(stream.read(limits.bytes + 1), limits=limits)


def record(value, keys):
    if type(value) is not dict or set(value) != set(keys.split()):
        raise WitnessInputError("closed record shape violated")


def integer(value):
    if type(value) is not int or value < 0:
        raise WitnessInputError("expected nonnegative integer")


def typed(value):
    record(value, "primitive value")
    p, v = value["primitive"], value["value"]
    good = p in {"String", "Date", "DateTime", "Boolean", "Integer", "Number", "Float"} and type(
        v
    ) in (str, bool, int, float)
    if not good:
        raise WitnessInputError("invalid typed scalar")


def target_shape(t):
    record(t, "fact_type tuple")
    if type(t["fact_type"]) is not str or type(t["tuple"]) is not list:
        raise WitnessInputError("invalid target")
    for v in t["tuple"]:
        typed(v)


def load_targets(path, *, limits=DEFAULT_LIMITS):
    doc = read_wire(path, limits=limits)
    record(doc, "version targets")
    if type(doc["version"]) is not int or doc["version"] != 1:
        raise WitnessInputError("unknown request version")
    if type(doc["targets"]) is not list or not 1 <= len(doc["targets"]) <= limits.targets:
        raise WitnessInputError("target count outside ceiling")
    for t in doc["targets"]:
        target_shape(t)
    return tuple(doc["targets"])


def certificate_shape(doc, *, limits=DEFAULT_LIMITS):
    validate_witness_structure(doc, limits=limits)
    record(doc, "version kind binding results nodes")
    if (
        type(doc["version"]) is not int
        or doc["version"] != 1
        or doc["kind"] != "derivation-witness"
    ):
        raise WitnessInputError("unknown certificate kind/version")
    b = doc["binding"]
    record(b, "model_digest candidate_digest references")
    for k in ("model_digest", "candidate_digest"):
        if type(b[k]) is not str or not re.fullmatch(r"sha256:[0-9a-f]{64}", b[k]):
            raise WitnessInputError("invalid digest")
    if type(b["references"]) is not list:
        raise WitnessInputError("invalid reference identity roster")
    ids = []
    for ref in b["references"]:
        record(ref, "id raw_sha256")
        if (
            type(ref["id"]) is not str
            or type(ref["raw_sha256"]) is not str
            or not re.fullmatch(r"[0-9a-f]{64}", ref["raw_sha256"])
        ):
            raise WitnessInputError("invalid reference identity")
        ids.append(ref["id"])
    if ids != sorted(set(ids)):
        raise WitnessInputError("reference identities must be sorted and unique")
    if (
        type(doc["results"]) is not list
        or not 1 <= len(doc["results"]) <= limits.targets
        or type(doc["nodes"]) is not list
    ):
        raise WitnessInputError("invalid result/node array")
    from gnd.witness.types import STATUS

    for i, r in enumerate(doc["results"]):
        record(r, "request_index target status reason root")
        integer(r["request_index"])
        target_shape(r["target"])
        if (
            r["request_index"] != i
            or r["status"] not in STATUS
            or r["reason"] != STATUS[r["status"]][1]
        ):
            raise WitnessInputError("incomplete or inconsistent result roster")
        if r["status"] == "proved":
            integer(r["root"])
            if r["root"] >= len(doc["nodes"]):
                raise WitnessInputError("root out of range")
        elif r["root"] is not None:
            raise WitnessInputError("non-success root")
    for i, n in enumerate(doc["nodes"]):
        kind = n.get("kind") if type(n) is dict else None
        keys = {
            "base": "id kind fact_type tuple origin",
            "rule": "id kind fact_type clause_index tuple bindings premises",
            "comparison": "id kind rule_fact_type clause_index where_index bindings premises",
        }
        if kind not in keys:
            raise WitnessInputError("unknown node kind")
        record(n, keys[kind])
        integer(n["id"])
        if n["id"] != i:
            raise WitnessInputError("node ids must be consecutive")
        if kind != "comparison":
            target_shape({"fact_type": n["fact_type"], "tuple": n["tuple"]})
        if kind == "base":
            record(n["origin"], "kind reference_id fact_index")
            integer(n["origin"]["fact_index"])
            origin = n["origin"]
            if (
                origin["kind"] not in {"candidate", "reference"}
                or (origin["kind"] == "candidate" and origin["reference_id"] is not None)
                or (origin["kind"] == "reference" and type(origin["reference_id"]) is not str)
            ):
                raise WitnessInputError("invalid base origin")
        else:
            integer(n["clause_index"])
            if kind == "comparison":
                integer(n["where_index"])
                if type(n["rule_fact_type"]) is not str:
                    raise WitnessInputError("invalid comparison owner")
            if type(n["bindings"]) is not dict or type(n["premises"]) is not list:
                raise WitnessInputError("invalid bindings/premises")
            for k, v in n["bindings"].items():
                if not k or k.startswith("$"):
                    raise WitnessInputError("invalid binding variable")
                typed(v)
            for edge in n["premises"]:
                integer(edge)
                if edge >= len(doc["nodes"]):
                    raise WitnessInputError("premise out of range")


def load_certificate(path, *, limits=DEFAULT_LIMITS):
    doc = read_wire(path, limits=limits)
    certificate_shape(doc, limits=limits)
    return doc


def witness_input_identity(model, candidate, *, references=None):
    refs = resolve_context(model, references)._snapshots if model.reference_populations else ()
    return identity(model, candidate, [(o.id, raw) for o, _, raw in refs])


def identity(model, candidate, refs):
    return {
        "model_digest": reference_model_digest(model),
        "candidate_digest": "sha256:"
        + hashlib.sha256(canonical_json_bytes(candidate.model_dump(mode="json"))).hexdigest(),
        "references": sorted(
            [{"id": k, "raw_sha256": hashlib.sha256(v).hexdigest()} for k, v in refs],
            key=lambda r: r["id"],
        ),
    }


def intake(model_document, candidate_document, reference_inputs, *, limits=DEFAULT_LIMITS):
    validate_witness_structure(model_document, limits=limits)
    validate_witness_structure(candidate_document, limits=limits)
    model = load_model_bytes(
        json.dumps(model_document, ensure_ascii=False, allow_nan=False).encode("utf-8"),
        source="model.orm.json",
    )
    candidate = load_population_bytes(
        canonical_json_bytes(candidate_document), source="candidate.pop.json", model=model
    )
    owners = validate_declarations(model)
    if any(ft in owners for ft in candidate.facts):
        raise WitnessInputError("candidate mentions reference-owned relation")
    if len(reference_inputs) != len(model.reference_populations) or len(
        {r[0] for r in reference_inputs}
    ) != len(reference_inputs):
        raise WitnessInputError("reference roster mismatch")
    supplied = dict(reference_inputs)
    refs = {}
    total = 0
    for d in model.reference_populations:
        raw = supplied.get(d["id"])
        if (
            type(raw) is not bytes
            or len(raw) > limits.bytes
            or hashlib.sha256(raw).hexdigest() != d["sha256"]
        ):
            raise WitnessInputError("reference bytes/hash mismatch")
        total += len(raw)
        if total > MAX_SET_BYTES:
            raise WitnessInputError("reference set byte ceiling")
        doc = _parse_document_bytes(raw, suffix=Path(d["path"]).suffix, source=d["path"])
        validate_reference_structure(doc)
        validate_witness_structure(doc, limits=limits)
        pop = _build_population(doc, model=model, deduplicate_shape_rows=True)
        if any(ft not in d["fact_types"] for ft in pop.facts):
            raise WitnessInputError("reference asserts unowned relation")
        refs[d["id"]] = pop
    for section in ("facts", "instances"):
        if (
            sum(
                len(rows)
                for pop in (candidate, *refs.values())
                for rows in getattr(pop, section).values()
            )
            > MAX_ENTRIES
        ):
            raise WitnessInputError("combined entry ceiling")
    return model, candidate, refs


def roster(model):
    return {
        ft["id"]: [
            (r["role_name"], resolve_primitive(r["object_type"], model)) for r in ft["roles"]
        ]
        for ft in model.fact_types
    }


def validate_targets(targets, model):
    roles = roster(model)
    for t in targets:
        target_shape(t)
        if t["fact_type"] not in roles or [v["primitive"] for v in t["tuple"]] != [
            p for _, p in roles[t["fact_type"]]
        ]:
            raise WitnessInputError("target fact/arity/primitive mismatch")
        for cell in t["tuple"]:
            primitive, value = cell["primitive"], cell["value"]
            valid = (
                (primitive in {"String", "Date", "DateTime"} and type(value) is str)
                or (primitive == "Boolean" and type(value) is bool)
                or (primitive == "Integer" and type(value) is int)
                or (primitive in {"Number", "Float"} and type(value) in (int, float))
            )
            if not valid:
                raise WitnessInputError("malformed typed target")
            if primitive == "Date":
                try:
                    if date.fromisoformat(value).isoformat() != value:
                        raise ValueError
                except ValueError:
                    raise WitnessInputError("target Date must be canonical ISO") from None


def support_closure(model, targets):
    """Conservative syntactic classifier; no tuple or comparison evaluation."""
    types = {ft["id"]: ft for ft in model.fact_types}
    roles = roster(model)
    closure, pending = set(), [t["fact_type"] for t in targets]
    supported = True
    while pending:
        fid = pending.pop()
        if fid in closure:
            continue
        closure.add(fid)
        ft = types[fid]
        if any(p not in {"String", "Boolean", "Integer", "Number", "Date"} for _, p in roles[fid]):
            supported = False
        rule = ft.get("derivation_rule")
        if ft.get("derivation") == "semiderived" or isinstance(rule, str):
            supported = False
        for c in iter_derivation_clauses(rule):
            if (
                c.get("negate")
                or c.get("aggregate")
                or any(isinstance(v, (dict, list)) for v in c["head"].values())
            ):
                supported = False
            variable_types = {}
            for a in c.get("body", []):
                pending.append(a["fact_type"])
                for role, p in roles[a["fact_type"]]:
                    term = a.get("bind", {}).get(role)
                    if isinstance(term, str) and term.startswith("$"):
                        variable_types[term] = p
                    elif isinstance(term, (dict, list)):
                        supported = False
            for w in c.get("where", []):
                operands = (w["left"], w["right"])
                if any(isinstance(v, (dict, list)) for v in operands):
                    supported = False
                ps = {
                    variable_types[v]
                    if isinstance(v, str) and v in variable_types
                    else "Boolean"
                    if type(v) is bool
                    else "String"
                    if type(v) is str
                    else "Integer"
                    if type(v) is int
                    else None
                    for v in operands
                }
                if w["operator"] not in {"=", "!=", "<", "<=", ">", ">="} or (
                    ps & {"String", "Boolean"} and w["operator"] not in {"=", "!="}
                ):
                    supported = False
    return supported, closure


def population_wire(pop):
    metadata = {
        k: getattr(pop, k)
        for k in ("model", "model_id", "source", "label", "covers")
        if getattr(pop, k) is not None
    }
    return {
        "format_version": pop.format_version,
        "population": metadata,
        "instances": pop.instances,
        "facts": pop.facts,
    }


def classify_targets(model, targets, populations):
    """Classify each request independently, caching only within this call."""
    roles, cache = roster(model), {}
    flags, scopes, selected = [], [], set()
    for target in targets:
        fid = target["fact_type"]
        if fid not in cache:
            supported, scope = support_closure(model, (target,))
            if supported and any(
                p == "Number" and type(row[role]) is float
                for pop in populations
                for relation in scope
                for row in pop.facts.get(relation, ())
                for role, p in roles[relation]
            ):
                supported = False
            cache[fid] = supported, scope
        supported, scope = cache[fid]
        supported = supported and not any(
            cell["primitive"] == "Number" and type(cell["value"]) is float
            for cell in target["tuple"]
        )
        flags.append(supported)
        scopes.append(scope)
        if supported:
            selected.update(scope)
    return flags, scopes, selected
