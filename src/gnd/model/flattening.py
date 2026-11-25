"""Canonical re-entry bytes and provenance for a resolved model include root."""

from __future__ import annotations

from dataclasses import asdict, dataclass

from gnd.artifacts import canonical_json_bytes, sha256_hex
from gnd.documents import Model
from gnd.errors import ModelLoadError, ModelValidationError, ReferenceInputError, ValidationIssue
from gnd.model import _finish_model, _model_warnings, parse_model_document
from gnd.model._documents import model_wire
from gnd.model._validation import MAX_MODEL_BYTES


class FlatteningError(ValueError):
    """A resolved model cannot be represented within the flat wire contract."""


@dataclass(frozen=True)
class FlattenedModel:
    model_bytes: bytes
    record_bytes: bytes
    model: Model


def flatten_model(model: Model) -> FlattenedModel:
    """Serialize an include snapshot made by the model loader."""
    includes = [
        {"id": item.id, "path": item.path, "sha256": item.sha256}
        for item in model._included
    ]
    if not includes or includes != model.includes or model._authored_sha256 is None:
        raise FlatteningError("flattening requires a resolved include root")

    wire = model_wire(model)
    wire.pop("includes")
    wire.pop("fact_type_constraints", None)
    flat_bytes = canonical_json_bytes(wire)
    if len(flat_bytes) > MAX_MODEL_BYTES:
        raise FlatteningError("flattening: flat model exceeds the model byte limit")

    try:
        reopened = _load_projection(flat_bytes, model)
    except ModelValidationError as error:
        issue = ValidationIssue(path="$", rule_id="flattening:re-entry", message="Flat model failed validation")
        raise ModelValidationError([issue, *error.issues], error.warnings) from error
    except (ModelLoadError, ReferenceInputError) as error:
        raise FlatteningError(f"flattening:re-entry: {error}") from error
    original = model.model_dump(exclude={"warnings", "includes", "fact_type_constraints"})
    if original != reopened.model_dump(exclude={"warnings"}):
        raise FlatteningError("flattening would change model values on re-entry")

    record = canonical_json_bytes({
        "format": "gnd-flattening/1",
        "root_sha256": model._authored_sha256,
        "includes": includes,
        "flat_model_sha256": sha256_hex(flat_bytes),
        "origins": [asdict(origin) for origin in sorted(
            model._provenance, key=lambda item: item.composed_address
        )],
    })
    if len(record) > MAX_MODEL_BYTES:
        raise FlatteningError("flattening: record exceeds the model byte limit")
    return FlattenedModel(flat_bytes, record, reopened)


def _load_projection(data: bytes, root: Model) -> Model:
    document = parse_model_document(data, source="flat.orm.json")
    warnings = _model_warnings(document, root._provenance, flat_root=True)
    return _finish_model(document, _warnings=warnings)
