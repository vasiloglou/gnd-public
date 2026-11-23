"""Bounded intake and exact source enumeration for a selected COUNT group."""

from __future__ import annotations

import os
from pathlib import Path

from ruamel.yaml.error import YAMLError

from gnd.artifacts import canonical_json_bytes, is_sha256_hex, sha256_hex
from gnd.errors import ModelLoadError, ModelValidationError, PopulationLoadError
from gnd.input_policy import guard_yaml
from gnd.model import iter_derivation_clauses, load_model_bytes
from gnd.model_index import ModelIndex
from gnd.population import load_population_bytes
from gnd.safefs import open_regular
from gnd.witness.io import integer, parse_wire, record, validate_witness_structure
from gnd.witness.types import WitnessInputError, checked_limits

KIND = "count-membership"
PRIMITIVES = {"String": str, "Boolean": bool, "Integer": int}
BINDING_KEYS = ("model_sha256", "population_sha256", "request_sha256")
INPUT_ERRORS = (OSError, ValueError, TypeError, KeyError, RecursionError, OverflowError, YAMLError,
                ModelLoadError, ModelValidationError, PopulationLoadError)


class CountRefusal(ValueError):
    def __init__(self, exit_code: int, reason: str):
        super().__init__(reason)
        self.exit_code = exit_code
        self.reason = reason


def refused(error: Exception) -> dict:
    if isinstance(error, CountRefusal):
        return {"exit_code": error.exit_code, "reason": error.reason}
    return {"exit_code": 3, "reason": "input-invalid"}


def _version(value):
    if type(value) is not int or value != 1:
        raise WitnessInputError("invalid COUNT membership wire version")


def _cell(wire):
    record(wire, "primitive value")
    name = wire["primitive"]
    if type(name) is not str or type(wire["value"]) is not PRIMITIVES.get(name):
        raise WitnessInputError("invalid COUNT membership scalar")


def request_shape(doc):
    record(doc, "version fact_type group")
    _version(doc["version"])
    if type(doc["fact_type"]) is not str or not doc["fact_type"] or type(doc["group"]) is not dict:
        raise WitnessInputError("invalid COUNT group selector")
    for cell in doc["group"].values():
        _cell(cell)


def certificate_shape(doc, limits):
    record(doc, "version kind binding request count status members")
    _version(doc["version"])
    if doc["kind"] != KIND or doc["status"] not in ("complete", "empty-group"):
        raise WitnessInputError("invalid COUNT certificate")
    binding = doc["binding"]
    record(binding, " ".join(BINDING_KEYS))
    if not all(is_sha256_hex(value) for value in binding.values()):
        raise WitnessInputError("invalid COUNT certificate binding")
    request_shape(doc["request"])
    integer(doc["count"])
    members = doc["members"]
    if type(members) is not list or len(members) > limits.nodes:
        raise WitnessInputError("invalid COUNT membership roster")
    for member in members:
        record(member, "over of fact_index")
        integer(member["fact_index"])
        _cell(member["of"])
        if type(member["over"]) is not list or not member["over"]:
            raise WitnessInputError("invalid COUNT contribution key")
        for cell in member["over"]:
            _cell(cell)


def read_bytes(path, limits, *, snapshot=False):
    with os.fdopen(open_regular(path), "rb") as stream:
        data = stream.read(limits.bytes + 1)
    if len(data) > limits.bytes:
        raise CountRefusal(4, "work-limit") if snapshot else WitnessInputError("wire byte ceiling")
    return data


def read_request(path, limits):
    raw = read_bytes(path, limits)
    request = parse_wire(raw, limits=limits)
    request_shape(request)
    return request, sha256_hex(raw)


def read_snapshot(model, population, request_digest, limits):
    checked_limits(limits)
    raw_model = read_bytes(model, limits, snapshot=True)
    raw_population = read_bytes(population, limits, snapshot=True)
    binding = dict(zip(BINDING_KEYS, (sha256_hex(raw_model), sha256_hex(raw_population), request_digest), strict=True))
    return raw_model, raw_population, binding


def _is_variable(value):
    return type(value) is str and value.startswith("$")


def _role_primitives(index, player_types):
    return {role: index.primitive(player, variant="strict") for role, player in player_types.items()}


def _declared_rule(model, request):
    index = ModelIndex.for_model(model)
    fact = index.fact_type(request["fact_type"])
    if fact is None:
        raise WitnessInputError("unknown COUNT fact type")
    rules = tuple(iter_derivation_clauses(fact.get("derivation_rule")))
    if fact.get("derivation") != "derived" or len(rules) != 1:
        raise CountRefusal(2, "fragment-unsupported")
    clause = rules[0]
    agg = clause.get("aggregate")
    if (
        not isinstance(agg, dict) or agg["fn"] != "count" or len(clause["body"]) != 1
        or clause.get("where") or clause.get("negate")
    ):
        raise CountRefusal(2, "fragment-unsupported")
    body = clause["body"][0]
    source = index.fact_type(body["fact_type"])
    slots = body["bind"]
    if (
        source is None or source.get("derivation") not in (None, "asserted")
        or source.get("derivation_rule") is not None
        or not all(_is_variable(value) for value in slots.values())
        or len(set(slots.values())) != len(slots)
    ):
        raise CountRefusal(2, "fragment-unsupported")
    inverse = {value: role for role, value in slots.items()}
    head = clause["head"]
    role_players = index.role_object_types()
    types = _role_primitives(index, role_players[request["fact_type"]])
    inputs = _role_primitives(index, role_players[body["fact_type"]])
    fresh = agg["as"]
    groups = {role: value for role, value in head.items() if value != fresh}
    count_roles = [role for role, value in head.items() if value == fresh]
    over = agg["over"]
    of = agg["of"]
    if (
        not groups or len(count_roles) != 1 or types[count_roles[0]] != "Integer"
        or not all(_is_variable(value) and value in inverse for value in groups.values())
        or len(set(groups.values())) != len(groups)
        or not over or not _is_variable(of) or of not in inverse
        or any(var not in inverse for var in over)
        or any(primitive not in PRIMITIVES for primitive in (*inputs.values(), *types.values()))
        or any(types[role] != inputs[inverse[var]] for role, var in groups.items())
    ):
        raise CountRefusal(2, "fragment-unsupported")

    selected = request["group"]
    if selected.keys() != groups.keys() or any(cell["primitive"] != types[role] for role, cell in selected.items()):
        raise WitnessInputError("COUNT group does not match the model")
    filters = {inverse[var]: selected[role]["value"] for role, var in groups.items()}
    over_roles = [(inverse[var], inputs[inverse[var]]) for var in over]
    of_role = (inverse[of], inputs[inverse[of]])
    return body["fact_type"], len(inputs), filters, over_roles, of_role


def _guard_yaml_snapshot(raw, path, limits):
    if Path(path).suffix != ".json":
        guard_yaml(raw, max_bytes=limits.bytes, max_depth=limits.container_depth)


def members_from_snapshot(model_path, population_path, snapshot, request, limits):
    raw_model, raw_population, _ = snapshot
    _guard_yaml_snapshot(raw_model, model_path, limits)
    model = load_model_bytes(raw_model, source=model_path)
    if model.reference_populations:
        raise CountRefusal(2, "fragment-unsupported")
    source, body_width, filters, over_roles, of_role = _declared_rule(model, request)
    _guard_yaml_snapshot(raw_population, population_path, limits)
    population = load_population_bytes(raw_population, source=population_path, model=model)
    if source not in population.covers:
        raise CountRefusal(2, "coverage-undeclared")
    rows = population.facts.get(source, ())
    cells_per_row = body_width + len(filters) + len(over_roles) + 1
    if len(rows) > limits.joins or len(rows) * cells_per_row > limits.binding_cells:
        raise CountRefusal(4, "work-limit")

    members = {}
    output_bytes = 0
    for fact_index, row in enumerate(rows):
        # A redacted row can hide a group key or contribution.
        if any(isinstance(value, dict) for value in row.values()):
            raise CountRefusal(2, "opaque-value")
        if any(row[role] != value for role, value in filters.items()):
            continue
        over = [{"primitive": primitive, "value": row[role]} for role, primitive in over_roles]
        role, primitive = of_role
        of = {"primitive": primitive, "value": row[role]}
        # These admitted primitive domains have exact typed JSON equality.
        key = canonical_json_bytes([over, of])
        if key in members:
            continue
        if len(members) == limits.nodes:
            raise CountRefusal(4, "work-limit")
        member = {"over": over, "of": of, "fact_index": fact_index}
        output_bytes += len(canonical_json_bytes(member)) + 1
        if output_bytes > limits.bytes:
            raise CountRefusal(4, "work-limit")
        try:
            validate_witness_structure(member, limits=limits)
        except WitnessInputError as error:
            raise CountRefusal(4, "work-limit") from error
        members[key] = member
    return [members[key] for key in sorted(members)]


def make_document(binding, request, members):
    return {"version": 1, "kind": KIND, "binding": binding, "request": request,
            "count": len(members), "status": "complete" if members else "empty-group", "members": members}


def check_result_bound(document, limits):
    try:
        validate_witness_structure(document, limits=limits)
        if len(canonical_json_bytes(document)) > limits.bytes:
            raise WitnessInputError("canonical certificate byte ceiling")
    except WitnessInputError as error:
        raise CountRefusal(4, "work-limit") from error


def success(document, *, include_certificate=False):
    result = {"exit_code": 0, "reason": None, "status": document["status"],
              "count": document["count"], "request": document["request"]}
    if include_certificate:
        result["certificate"] = document
    return result
