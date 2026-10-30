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


def _why_not_intake_limits():
    """Project the why-not input ceilings onto the witness lane's limits class."""
    from dataclasses import replace

    from gnd.witness.types import DEFAULT_LIMITS
    from gnd.witness.why_not import DEFAULT_WHY_NOT_LIMITS as limits

    return replace(
        DEFAULT_LIMITS,
        bytes=limits.bytes,
        container_depth=limits.container_depth,
        scalar_bytes=limits.scalar_bytes,
        numeric_digits=limits.numeric_digits,
        targets=1,
    )


def _why_not_envelope(exit_code, status, reason, *, explanation=None, work=None):
    body = explanation or {
        "fact_type": None, "mode": None, "order": None, "unavailable": None, "clauses": [],
    }
    return {
        "schema_version": "gnd-why-not/1",
        "exit_code": exit_code,
        "status": status,
        "reason": reason,
        "fact_type": body["fact_type"],
        "mode": body["mode"],
        "order": body["order"],
        "unavailable": body["unavailable"],
        "clauses": body["clauses"],
        "work": dict(work if work is not None else body.get("work", {})),
    }


_WHY_NOT_EXITS = {"blocked": 0, "derived": 0, "unsupported": 2, "unavailable": 4}


def why_not(model_path, population_path, fact_type, *, row_path=None, reference_root=None):
    """Explain why a derived fact type, or one claimed row of it, is not derived."""
    from ruamel.yaml.error import YAMLError

    from gnd.witness.io import intake, load_targets, population_wire
    from gnd.witness.why_not import WhyNotWorkError, explain

    refused = _why_not_envelope(3, "refused", "input-invalid", work={})
    try:
        if type(fact_type) is not str:
            return refused
        limits = _why_not_intake_limits()
        row = None
        if row_path is not None:
            (target,) = load_targets(row_path, limits=limits)
            if target["fact_type"] != fact_type:
                return refused
            row = target["tuple"]
        model, candidate, context, _, _ = _witness_inputs(
            model_path, population_path, reference_root
        )
        raw_refs = tuple((o.id, raw) for o, _, raw in context._snapshots) if context else ()
        intake(
            model.model_dump(mode="json", exclude={"warnings"}),
            population_wire(candidate),
            raw_refs,
            limits=limits,
        )
        result = explain(model, candidate, fact_type, row=row, references=context).to_dict()
    except WhyNotWorkError as error:
        return _why_not_envelope(4, "refused", "work-limit", work=error.work)
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
        return refused
    return _why_not_envelope(
        _WHY_NOT_EXITS[result["status"]], result["status"], result["reason"], explanation=result
    )



# Historical qualifications are serialized by existing callers.
_witness_inputs.__module__ = 'gnd.api'
witness.__module__ = 'gnd.api'
replay.__module__ = 'gnd.api'
why_not.__module__ = 'gnd.api'

# Public dependency and compatibility spellings; same predecessor objects.
witness_inputs = _witness_inputs
