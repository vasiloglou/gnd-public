"""Canonical re-entry bytes and provenance for a resolved model include root."""

from __future__ import annotations

from dataclasses import asdict, dataclass

from gnd.artifacts import canonical_json_bytes, sha256_hex
from gnd.documents import Model
from gnd.model import load_model_bytes
from gnd.model._documents import model_wire
from gnd.model._validation import MAX_MODEL_BYTES


class FlatteningError(ValueError):
    """A resolved model cannot be represented within the flat wire contract."""


@dataclass(frozen=True)
class FlattenedModel:
    model_bytes: bytes
    record_bytes: bytes


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

    reopened = load_model_bytes(flat_bytes, source="flat.orm.json")
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
    return FlattenedModel(flat_bytes, record)
