"""Bounded witness/replay input orchestration."""
from __future__ import annotations

import json  # noqa: F401 -- historical compatibility binding

from gnd import input_policy as _rf7_input
from gnd import model as model_module
from gnd.errors import ModelValidationError, PopulationLoadError


def _witness_inputs(model_path, population_path, reference_root):
    """Load witness inputs without introducing a new checking claim."""
    from pathlib import Path

    from gnd.model import bind_declared_references, load_model_bytes
    from gnd.population import _parse_document_bytes, load_population_bytes
    from gnd.witness.types import DEFAULT_LIMITS, WitnessInputError

    def read(path):
        with Path(path).open("rb") as stream:
            raw = stream.read(DEFAULT_LIMITS.bytes + 1)
        if len(raw) > DEFAULT_LIMITS.bytes:
            raise WitnessInputError("input byte ceiling")
        return raw

    mr, pr = read(model_path), read(population_path)
    model = load_model_bytes(mr, source=model_path)
    candidate = load_population_bytes(pr, source=population_path, model=model)
    context = bind_declared_references(
        model, root=reference_root if reference_root is not None else Path(model_path).parent
    )
    try:
        md = _rf7_input.loads(mr)
    except ValueError:
        md = _parse_document_bytes(mr, suffix=Path(model_path).suffix, source=str(model_path))
    pd = _parse_document_bytes(pr, suffix=Path(population_path).suffix, source=str(population_path))
    return model, candidate, context, md, pd


def witness(model_path, population_path, targets_path, *, reference_root=None):
    """Produce finite witnesses; exit zero requires every requested tuple proved."""
    from ruamel.yaml.error import YAMLError

    from gnd.witness.io import load_targets
    from gnd.witness.producer import produce_witness
    from gnd.witness.types import WitnessResult

    try:
        targets = load_targets(targets_path)
        model, candidate, context, _, _ = _witness_inputs(
            model_path, population_path, reference_root
        )
        return produce_witness(model, candidate, targets, references=context).model_dump(
            mode="json"
        )
    except (
        ValueError,
        TypeError,
        OSError,
        RecursionError,
        ModelValidationError,
        model_module.ModelLoadError,
        PopulationLoadError,
        YAMLError,
    ):
        return WitnessResult(3, reason="input-invalid").model_dump(mode="json")


def replay(model_path, population_path, certificate_path, *, reference_root=None):
    """Replay a finite proof with an independent local inference kernel."""
    from ruamel.yaml.error import YAMLError

    from gnd.witness.io import load_certificate
    from gnd.witness.kernel import replay_witness
    from gnd.witness.types import WitnessResult

    try:
        certificate = load_certificate(certificate_path)
        _, _, context, md, pd = _witness_inputs(model_path, population_path, reference_root)
        refs = tuple((o.id, raw) for o, _, raw in context._snapshots) if context else ()
        return replay_witness(md, pd, certificate, reference_inputs=refs).model_dump(mode="json")
    except (
        ValueError,
        TypeError,
        OSError,
        RecursionError,
        ModelValidationError,
        model_module.ModelLoadError,
        PopulationLoadError,
        YAMLError,
    ):
        return WitnessResult(3, reason="input-invalid").model_dump(mode="json")



# Historical qualifications are serialized by existing callers.
_witness_inputs.__module__ = 'gnd.api'
witness.__module__ = 'gnd.api'
replay.__module__ = 'gnd.api'

# Public dependency and compatibility spellings; same predecessor objects.
witness_inputs = _witness_inputs
