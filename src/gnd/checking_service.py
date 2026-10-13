"""Shared checking, admission and report orchestration below entry points."""
from __future__ import annotations

import copy
import os
from collections.abc import Callable
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

from gnd import checker as checker_module
from gnd import model as model_module
from gnd import payloads as report_module
from gnd import redaction as redaction_module
from gnd import transition as transition_module
from gnd.assurance import (
    AssuranceBlockV1,
    _mint_execution,
    certify_result,
    derive_assurance_scope,
    semantic_decision_for_band,
)
from gnd.assurance_evidence import load_assurance_evidence
from gnd.checker import CheckReport
from gnd.exits import EXIT_INTERNAL
from gnd.model import (
    Model,
    ModelValidationError,
    ValidationIssue,
    load_model,
    structured_derivation_ids,
)
from gnd.population import Population, PopulationValidationError, load_population
from gnd.references import BoundReferenceContext
from gnd.semantic_registry import capture_branches
from gnd.terms import uses_temporal


@dataclass(frozen=True)
class _RunResult:
    payload: dict[str, Any]
    json_text: str
    exit_code: int
    model: Model | None = None
    populations: tuple[Population, ...] = ()
    report: Any = None
    warnings: tuple[ValidationIssue, ...] = ()
    issues: tuple[ValidationIssue, ...] = ()
    error: BaseException | None = None
    steps: tuple[dict[str, Any], ...] = ()
    execution: Any = None


def _path(value: object, *, name: str) -> str:
    if not isinstance(value, (str, os.PathLike)):
        raise TypeError(f"{name} must be a path or loaded GND object")
    coordinate = os.fspath(value)
    if not isinstance(coordinate, str):
        raise TypeError(f"{name} path must resolve to str, not bytes")
    return coordinate


def _resolve_model(
    value: str | os.PathLike[str] | Model, *, safe: bool = False
) -> tuple[Model, str | None]:
    if isinstance(value, Model):
        return value, None
    coordinate = _path(value, name="model")
    return (
        model_module._load_model_no_follow(Path(coordinate)) if safe else load_model(coordinate)
    ), coordinate


def _resolve_population(
    value: str | os.PathLike[str] | Population,
    *,
    model: Model,
    name: str,
) -> tuple[Population, str | None]:
    if isinstance(value, Population):
        return value, None
    coordinate = _path(value, name=name)
    return load_population(coordinate, model=model), coordinate


def _finalize(
    payload: dict[str, Any],
    *,
    exit_code: int,
    fallback,
    **result: Any,
) -> _RunResult:
    try:
        rendered = report_module.render_json(payload)
    except report_module.NonJsonValueError as failure:
        payload = fallback(failure)
        rendered = report_module.render_json(payload)
        exit_code = EXIT_INTERNAL
        result["error"] = failure
    return _RunResult(
        payload=payload,
        json_text=rendered + "\n",
        exit_code=exit_code,
        **result,
    )


def _certify_assurance(
    model: Model,
    populations: list[Population],
    result: Any,
    band: int,
    trace: set[str],
    *,
    steps: list[dict[str, Any]] | None = None,
    extraction_route: str = "not-applicable",
) -> tuple[AssuranceBlockV1, Any]:
    """Authenticate installed evidence without preparing a receipt emission."""
    try:
        execution = _mint_execution(
            model,
            populations,
            result,
            band,
            trace,
            steps=steps,
            extraction_route=extraction_route,
        )
        scope = derive_assurance_scope(execution, consumer="report")
        block = certify_result(execution, scope=scope, evidence=load_assurance_evidence())
        return block, execution
    except (ValueError, TypeError, OverflowError):
        return AssuranceBlockV1(semantic_decision_for_band(band)), None


def _run_check_raw(
    model_input: str | os.PathLike[str] | Model,
    population_input: str | os.PathLike[str] | Population,
    *,
    compiled_operations: bool = False,
    evaluator: Callable[[Model, Population], CheckReport] | None = None,
    anchors: Any = None,
    document: bytes | str | os.PathLike[str] | None = None,
    population_bytes: bytes | None = None,
    admission: bool = False,
    references: BoundReferenceContext | None = None,
) -> _RunResult:
    model_coordinate = None if isinstance(model_input, Model) else _path(model_input, name="model")
    population_coordinate = (
        None
        if isinstance(population_input, Population)
        else _path(population_input, name="population")
    )
    model: Model | None = None
    population: Population | None = None
    model_digest: str | None = None
    structured = False

    def build(
        exit_code: int,
        *,
        report: CheckReport | None = None,
        issues: list[ValidationIssue] | None = None,
        warnings: list[ValidationIssue] | None = None,
        error: BaseException | None = None,
    ) -> dict[str, Any]:
        return report_module.build_check_payload(
            exit_code,
            model_coordinate,
            population_coordinate,
            schema_version=7,
            model_digest=model_digest,
            structured=structured,
            report=report,
            issues=issues,
            warnings=warnings,
            error=error,
        )

    try:
        model, _ = _resolve_model(model_input)
    except ModelValidationError as error:
        return _finalize(
            build(3, issues=error.issues, warnings=error.warnings),
            exit_code=3,
            fallback=lambda failure: build(EXIT_INTERNAL, error=failure),
            warnings=tuple(error.warnings),
            issues=tuple(error.issues),
            error=error,
        )
    except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
        return _finalize(
            build(3, error=error),
            exit_code=3,
            fallback=lambda failure: build(EXIT_INTERNAL, error=failure),
            model=getattr(error, "model", None),
            error=error,
        )

    structured = bool(structured_derivation_ids(model))
    try:
        model_digest = transition_module.transition_model_identity(model)
    except Exception as error:
        if not model.reference_populations:
            raise
        return _finalize(
            build(3, error=ValueError("reference model identity is invalid")),
            exit_code=3,
            fallback=lambda failure: build(EXIT_INTERNAL, error=failure),
            model=model,
            error=error,
        )
    try:
        if model.reference_populations:
            from gnd.references import bind_population, resolve_context

            context = resolve_context(model, references)
            model._references = context
        population, _ = _resolve_population(population_input, model=model, name="population")
        if model.reference_populations:
            if anchors is not None:
                raise ValueError("reference sidecar combinations are unsupported")
            population = bind_population(model, population, references=context).combined
    except PopulationValidationError as error:
        warnings = [*model.warnings, *error.warnings]
        return _finalize(
            build(3, issues=error.issues, warnings=warnings),
            exit_code=3,
            fallback=lambda failure: build(EXIT_INTERNAL, error=failure),
            model=model,
            warnings=tuple(warnings),
            issues=tuple(error.issues),
            error=error,
        )
    except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
        return _finalize(
            build(3, error=error),
            exit_code=3,
            fallback=lambda failure: build(EXIT_INTERNAL, error=failure),
            model=model,
            error=error,
        )

    try:
        with capture_branches() as semantic_trace:
            from gnd.anchors import (
                MAX_DOCUMENT_BYTES,
                AnchorError,
                AnchorSidecar,
                bind_anchors,
                read_anchor_sidecar,
                read_regular_path,
                validate_anchor_sidecar,
            )

            selected_anchors = (
                read_anchor_sidecar(anchors) if isinstance(anchors, (str, os.PathLike)) else anchors
            )
            if selected_anchors is not None and not isinstance(selected_anchors, AnchorSidecar):
                raise AnchorError(
                    "anchor:sidecar-invalid: expected a sidecar path or AnchorSidecar"
                )
            if isinstance(selected_anchors, AnchorSidecar):
                selected_anchors = validate_anchor_sidecar(selected_anchors)
            if isinstance(document, (str, os.PathLike)):
                document_path = Path(document)
                try:
                    document_raw = read_regular_path(
                        document_path, label="anchor document", max_bytes=MAX_DOCUMENT_BYTES
                    )
                except Exception as error:
                    raise AnchorError(
                        f"anchor:sidecar-invalid: document could not be read safely: {error}"
                    ) from error
            else:
                document_raw = document
            if selected_anchors is not None:
                if population_bytes is None and population_coordinate is not None:
                    path = Path(population_coordinate)
                    try:
                        population_bytes = read_regular_path(
                            path, label="anchor population", max_bytes=MAX_DOCUMENT_BYTES
                        )
                    except Exception as error:
                        raise AnchorError(
                            f"anchor:sidecar-invalid: population could not be read safely: {error}"
                        ) from error
                bind_anchors(selected_anchors, model, population_bytes, document_raw, population)
            if selected_anchors is not None or any(
                c.get("type") == "anchored"
                for ft in model.fact_types
                for c in ft.get("constraints") or []
            ):
                anchored_evaluator = (
                    checker_module.check_with_anchors_partial
                    if evaluator is checker_module.check_partial
                    else checker_module.check_with_anchors
                )
                checked = anchored_evaluator(
                    model,
                    population,
                    anchors=selected_anchors,
                    document_bytes=document_raw,
                )
            else:
                checked = (evaluator or checker_module.check)(model, population)
            if compiled_operations:
                from gnd.compiled_obligations import compose
                checked = compose(model, population, checked)
            exit_code = checker_module.band(checked)
    except AnchorError as error:
        return _finalize(
            build(3, error=error),
            exit_code=3,
            fallback=lambda failure: build(EXIT_INTERNAL, error=failure),
            model=model,
            populations=(population,),
            error=error,
        )
    except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
        return _finalize(
            build(EXIT_INTERNAL, error=error),
            exit_code=EXIT_INTERNAL,
            fallback=lambda failure: build(EXIT_INTERNAL, error=failure),
            model=model,
            populations=(population,),
            error=error,
        )

    warnings = [*model.warnings, *population.warnings]
    with capture_branches() as projection_trace:
        payload = build(exit_code, report=checked, warnings=warnings)
    if compiled_operations:
        assurance = AssuranceBlockV1(semantic_decision_for_band(exit_code))
        execution = None
    else:
        assurance, execution = _certify_assurance(
            model, [population], checked, exit_code, semantic_trace | projection_trace,
        )
    payload["assurance"] = assurance.as_dict()
    return _finalize(
        payload,
        exit_code=exit_code,
        fallback=lambda failure: build(EXIT_INTERNAL, error=failure),
        model=model,
        populations=(population,),
        report=checked,
        warnings=tuple(warnings),
        execution=execution,
    )


def _projection_failure_base(
    result: _RunResult,
    kind: redaction_module.OutputKind,
    failure: BaseException,
) -> dict[str, Any]:
    model = result.model
    if model is None:
        raise ValueError("projection failure requires a loaded model")
    digest = transition_module.transition_model_identity(model)
    structured = bool(structured_derivation_ids(model))
    if kind == "validate":
        payload = report_module.build_validate_payload(
            EXIT_INTERNAL,
            result.payload.get("model"),
            error=failure,
        )
        payload["model_digest"] = digest
        payload["assurance"] = AssuranceBlockV1(semantic_decision_for_band(EXIT_INTERNAL)).as_dict()
        return payload
    if kind in {"transition", "plan"}:
        if kind == "plan":
            return report_module.build_plan_transition_payload(
                EXIT_INTERNAL,
                result.payload.get("model"),
                evaluated=False,
                model_digest=digest,
                structured=structured,
                error=failure,
            )
        return report_module.build_transition_payload(
            EXIT_INTERNAL,
            result.payload.get("model"),
            evaluated=False,
            schema_version=7,
            model_digest=digest,
            structured=structured,
            error=failure,
        )
    payload = report_module.build_check_payload(
        EXIT_INTERNAL,
        result.payload.get("model"),
        result.payload.get("population"),
        schema_version=7,
        model_digest=digest,
        structured=structured,
        error=failure,
    )
    if kind == "admission":
        payload["admission"] = {"admitted": [], "blocked": []}
    return payload


def _project_result(
    result: _RunResult,
    kind: redaction_module.OutputKind,
    *,
    unredacted: bool,
) -> _RunResult:
    if result.model is None:
        return result
    policy = redaction_module.RedactionPolicy.from_model(result.model)
    temporal = uses_temporal(result.model) and kind in {"check", "transition", "plan"}
    if not policy.active and not temporal:
        return result
    mode: redaction_module.RedactionMode = "unredacted" if unredacted else "applied"
    source = dict(result.payload)
    if kind == "validate":
        source["model_digest"] = transition_module.transition_model_identity(result.model)
        source["assurance"] = AssuranceBlockV1(
            semantic_decision_for_band(result.exit_code)
        ).as_dict()
    try:
        if kind == "validate":
            payload = redaction_module.project_output(
                kind,
                source,
                policy=policy,
                mode=mode,
                emitter_id="api-validate",
            )
        elif kind == "check":
            payload = redaction_module.project_output(
                kind,
                source,
                policy=policy,
                mode=mode,
                emitter_id="api-check",
            )
        elif kind == "transition":
            payload = redaction_module.project_output(
                kind,
                source,
                policy=policy,
                mode=mode,
                emitter_id="api-transition-full",
            )
        else:
            payload = redaction_module.project_output(
                kind,
                source,
                policy=policy,
                mode=mode,
                emitter_id="api-transition-plan",
            )
        if temporal:
            redaction_module._select_successor(kind, payload)
            payload["schema_version"] = 11
            payload["redaction"] = policy.metadata(mode)
        rendered = report_module.render_json(payload) + "\n"
        return replace(result, payload=payload, json_text=rendered)
    except Exception as failure:  # noqa: BLE001 -- preserve predecessor refusal contract
        base = _projection_failure_base(result, kind, failure)
        payload = redaction_module.project_failure(kind, base, policy=policy, mode=mode)
        rendered = report_module.render_json(payload) + "\n"
        return replace(
            result,
            payload=payload,
            json_text=rendered,
            exit_code=EXIT_INTERNAL,
            report=None,
            issues=(),
            error=failure,
            execution=None,
        )


def _reference_wrap(result: _RunResult) -> _RunResult:
    model = result.model
    if model is None or not model.reference_populations:
        return result
    from gnd.references import ReferenceInputError, reference_model_digest, resolve_context

    try:
        context = resolve_context(model)
        digest = reference_model_digest(model)
    except (ReferenceInputError, ValueError, TypeError):
        context = None
        digest = None
    owners = dict(context._owners) if context is not None else {}
    payload = copy.deepcopy(result.payload)
    if context is None and "model_digest" in payload:
        payload["model_digest"] = None
    if "admission" in payload:
        for kind in ("admitted", "blocked"):
            payload["admission"][kind] = [
                row
                for row in payload["admission"][kind]
                if row["fact_ref"]["fact_type"] not in owners
            ]
    origins = []
    if result.populations and context is not None and result.exit_code != 3:
        from gnd.references import bind_population, is_bound_population

        population = (
            result.populations[-1] if "transition" in result.payload else result.populations[0]
        )
        if not is_bound_population(model, population, context):
            population = bind_population(model, population, references=context).combined
        for ft, rows in population.facts.items():
            owner = owners.get(ft)
            origins.extend(
                {
                    "origin": {
                        "kind": "reference" if owner else "candidate",
                        "reference_id": owner,
                    },
                    "fact_type": ft,
                    "index": index,
                }
                for index in range(len(rows))
            )
    origins.sort(
        key=lambda row: (
            row["origin"]["kind"],
            row["origin"]["reference_id"] or "",
            row["fact_type"],
            row["index"],
        )
    )
    wrapper = {
        "schema_version": 14 if payload.get("schema_version") == 13 else 12,
        "command": payload["command"],
        "outcome": payload["outcome"],
        "exit_code": payload["exit_code"],
        "model_digest": digest,
        "reference_binding": {
            "identity_version": 1,
            "references": [
                {"id": origin.id, "sha256": origin.raw_sha256}
                for origin, _path, _raw in (context._snapshots if context is not None else ())
            ],
        },
        "report": payload,
        "occurrence_origins": origins,
    }
    return replace(result, payload=wrapper, json_text=report_module.render_json(wrapper) + "\n")


def _run_check(
    model_input: str | os.PathLike[str] | Model,
    population_input: str | os.PathLike[str] | Population,
    *,
    compiled_operations: bool = False,
    unredacted: bool = False,
    evaluator: Callable[[Model, Population], CheckReport] | None = None,
    anchors: Any = None,
    document: bytes | str | os.PathLike[str] | None = None,
    population_bytes: bytes | None = None,
    admission: bool = False,
    references: BoundReferenceContext | None = None,
) -> _RunResult:
    if (admission or compiled_operations) and evaluator is None:
        evaluator = checker_module.check_partial
    if compiled_operations and admission:
        raise ValueError('compiled_operations cannot be combined with admission')
    result = _run_check_raw(
        model_input,
        population_input,
        compiled_operations=compiled_operations,
        evaluator=evaluator,
        anchors=anchors,
        document=document,
        population_bytes=population_bytes,
        admission=admission,
        references=references,
    )
    if admission:
        from gnd.admission import build_admission, wire_verdicts

        try:
            payload = copy.deepcopy(result.payload)
            payload["schema_version"] = report_module.requested_check_schema_version(
                result.model,
                admission=True,
            )
            payload["admission"] = {"admitted": [], "blocked": []}
            if result.model is not None and result.populations and result.report is not None:
                payload["admission"] = build_admission(
                    result.model,
                    result.populations[0],
                    result.report,
                    max_cells=1_000_000,
                )
                wire_verdicts(payload, result.report, result.populations[0], result.model)
            rendered = report_module.render_json(payload) + "\n"
        except Exception as failure:  # noqa: BLE001 -- preserve predecessor refusal contract
            payload = report_module.build_check_payload(
                EXIT_INTERNAL,
                result.payload.get("model"),
                result.payload.get("population"),
                schema_version=7,
                model_digest=result.payload.get("model_digest"),
                structured=bool(result.model and structured_derivation_ids(result.model)),
                error=RuntimeError("admission projection failed"),
            )
            payload["schema_version"] = report_module.requested_check_schema_version(
                result.model, admission=True
            )
            payload["admission"] = {"admitted": [], "blocked": []}
            rendered = report_module.render_json(payload) + "\n"
            result = replace(
                result,
                exit_code=EXIT_INTERNAL,
                report=None,
                error=failure,
                execution=None,
            )
        result = replace(result, payload=payload, json_text=rendered)
    return _reference_wrap(
        _project_result(
            result,
            "admission" if admission else "check",
            unredacted=unredacted,
        )
    )



_RunResult.__module__ = 'gnd.api'
RunResult = _RunResult
_path.__module__ = 'gnd.api'
path = _path
_resolve_model.__module__ = 'gnd.api'
resolve_model = _resolve_model
_resolve_population.__module__ = 'gnd.api'
resolve_population = _resolve_population
_finalize.__module__ = 'gnd.api'
finalize = _finalize
_certify_assurance.__module__ = 'gnd.api'
certify_assurance = _certify_assurance
_run_check_raw.__module__ = 'gnd.api'
run_check_raw = _run_check_raw
_projection_failure_base.__module__ = 'gnd.api'
projection_failure_base = _projection_failure_base
_project_result.__module__ = 'gnd.api'
project_result = _project_result
_reference_wrap.__module__ = 'gnd.api'
reference_wrap = _reference_wrap
_run_check.__module__ = 'gnd.api'
run_check = _run_check
check_report = _run_check

mint_execution = _mint_execution

# Historical lookup name for the unchanged CLI assurance closure.
_certify_assurance = certify_assurance
