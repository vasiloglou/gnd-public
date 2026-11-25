"""Rooted include bindings for path-based witness production and replay."""

import re
from dataclasses import asdict, dataclass
from pathlib import Path

from gnd.anchors import read_regular_path
from gnd.artifacts import canonical_json_bytes, sha256_hex
from gnd.errors import ModelValidationError
from gnd.model import load_model
from gnd.model._includes import guard_bytes, include_reason
from gnd.model.flattening import FlattenedModel, flatten_model
from gnd.witness.types import DEFAULT_LIMITS, WitnessInputError, WitnessResult, result_rows


class StaleWitnessBinding(WitnessInputError):
    """The current inputs differ from a rooted witness binding."""


@dataclass(frozen=True)
class WitnessProjection:
    root_sha256: str
    flat: FlattenedModel
    fact_origins: dict[str, dict]

    @property
    def binding(self) -> tuple[str, dict[str, dict]]:
        return sha256_hex(self.flat.record_bytes), self.fact_origins


def read_projected_path(path, *, label):
    """Open an explicit caller path with bounded regular-file checks."""
    return read_regular_path(Path(path).resolve(strict=True), label=label, max_bytes=DEFAULT_LIMITS.bytes)


def resolved_projection(model_path, flat_model=None, flattening_record=None, *, raw=None):
    """Return the authenticated projection when the authored root declares includes."""
    if raw is None:
        raw = read_projected_path(model_path, label="authored model")
    try:
        guard_bytes(raw, source=model_path, route="rooted witness")
    except ModelValidationError as error:
        if include_reason(error) != "include:unsupported-route":
            raise
    else:
        if flat_model is not None or flattening_record is not None:
            raise WitnessInputError("flattening requires an authored include root")
        return None
    if (flat_model is None) != (flattening_record is None):
        raise WitnessInputError("paired flat model and flattening record required")

    try:
        model = load_model(model_path)
    except ModelValidationError as error:
        if include_reason(error) == "include:hash-mismatch":
            raise StaleWitnessBinding("include digest differs from its declaration") from error
        raise
    root_sha256 = sha256_hex(raw)
    if model._authored_sha256 != root_sha256:
        raise StaleWitnessBinding("authored root changed while resolving includes")
    flat = flatten_model(model)
    for path, expected, label in (
        (flat_model, flat.model_bytes, "flat model"),
        (flattening_record, flat.record_bytes, "flattening record"),
    ):
        if path is not None and read_projected_path(path, label=label) != expected:
            raise StaleWitnessBinding(f"{label} differs from the resolved model")
    origins = {
        origin.element_id: asdict(origin)
        for origin in model._provenance
        if origin.element_id is not None and re.fullmatch(r"\$\.fact_types\[\d+\]", origin.composed_address)
    }
    return WitnessProjection(root_sha256, flat, origins)


def node_model_origin(node: dict, origins: dict[str, dict]) -> dict:
    fact_type = node["rule_fact_type"] if node["kind"] == "comparison" else node["fact_type"]
    return origins[fact_type]


def stamp_projection(result: dict, projection: WitnessProjection) -> dict:
    certificate = result["certificate"]
    if certificate is None:
        return result
    if certificate["version"] != 4:
        certificate["version"] = 3
    digest, origins = projection.binding
    certificate["binding"]["flattening_sha256"] = digest
    for node in certificate["nodes"]:
        node["model_origin"] = dict(node_model_origin(node, origins))
    from gnd.witness.io import certificate_shape

    try:
        certificate_shape(certificate, limits=DEFAULT_LIMITS)
        if len(canonical_json_bytes(certificate)) > DEFAULT_LIMITS.bytes:
            raise WitnessInputError("projected certificate exceeds byte ceiling")
    except WitnessInputError:
        targets = tuple(row["target"] for row in certificate["results"])
        return WitnessResult(4, result_rows(targets, "resource-refused"), reason="work-limit").model_dump(mode="json")
    return result


def load_flat_model(projection: WitnessProjection):
    return projection.flat.model
