"""Stable in-process access to GND validation and checking reports."""

from __future__ import annotations

import copy
import json
import os
from collections.abc import Callable, Mapping
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

from gnd import checker as checker_module
from gnd import model as model_module
from gnd import redaction as redaction_module
from gnd import report as report_module
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
from gnd.population import (
    Population,
    PopulationLoadError,
    PopulationValidationError,
    load_population,
)
from gnd.references import BoundReferenceContext
from gnd.semantic_registry import capture_branches
from gnd.terms import uses_temporal

__all__ = ("validate", "check", "transition", "verbalize", "diff", "witness", "replay")  # noqa: RUF022 - approved stable order


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


def _check_model_input(value: object) -> None:
    if not isinstance(value, Model):
        _path(value, name="model")


def _check_population_input(value: object, *, name: str) -> None:
    if not isinstance(value, Population):
        _path(value, name=name)


def _check_steps_input(value: object) -> None:
    if not isinstance(value, Mapping):
        _path(value, name="steps")


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


def _run_validate_raw(
    model_input: str | os.PathLike[str] | Model, *, references: BoundReferenceContext | None = None
) -> _RunResult:
    coordinate = None if isinstance(model_input, Model) else _path(model_input, name="model")
    schema_version = report_module.BASE_PAYLOAD_SCHEMA_VERSION
    model = None

    def build(
        exit_code: int,
        *,
        issues: list[ValidationIssue] | None = None,
        warnings: list[ValidationIssue] | None = None,
        error: BaseException | None = None,
    ) -> dict[str, Any]:
        return report_module.build_validate_payload(
            exit_code,
            coordinate,
            schema_version=schema_version,
            issues=issues,
            warnings=warnings,
            error=error,
        )

    try:
        model, _ = _resolve_model(model_input)
        if model.reference_populations:
            from gnd.references import resolve_context

            model._references = resolve_context(model, references)
        if coordinate is None:
            document = model.model_dump(exclude={"warnings"})
            issues = model_module.semantic_validate(document)
            errors = [issue for issue in issues if issue.severity == "error"]
            if errors:
                raise ModelValidationError(
                    errors,
                    [issue for issue in issues if issue.severity == "warning"],
                )
    except ModelValidationError as error:
        return _finalize(
            build(3, issues=error.issues, warnings=error.warnings),
            exit_code=3,
            fallback=lambda failure: build(EXIT_INTERNAL, error=failure),
            warnings=tuple(error.warnings),
            issues=tuple(error.issues),
            model=model or getattr(error, "model", None),
            error=error,
        )
    except Exception as error:  # noqa: BLE001 - loader failures are report data
        return _finalize(
            build(3, error=error),
            exit_code=3,
            fallback=lambda failure: build(EXIT_INTERNAL, error=failure),
            model=model or getattr(error, "model", None),
            error=error,
        )

    schema_version = report_module.payload_schema_version(model)
    payload = build(0, warnings=model.warnings)
    return _finalize(
        payload,
        exit_code=0,
        fallback=lambda failure: build(EXIT_INTERNAL, error=failure),
        model=model,
        warnings=tuple(model.warnings),
    )


def _run_check_raw(
    model_input: str | os.PathLike[str] | Model,
    population_input: str | os.PathLike[str] | Population,
    *,
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
    except Exception as error:  # noqa: BLE001
        return _finalize(
            build(3, error=error),
            exit_code=3,
            fallback=lambda failure: build(EXIT_INTERNAL, error=failure),
            model=getattr(error, "model", None),
            error=error,
        )

    structured = bool(structured_derivation_ids(model))
    try:
        model_digest = transition_module.model_digest(model)
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
    except Exception as error:  # noqa: BLE001
        return _finalize(
            build(3, error=error),
            exit_code=3,
            fallback=lambda failure: build(EXIT_INTERNAL, error=failure),
            model=model,
            error=error,
        )

    try:
        with capture_branches() as semantic_trace:
            from gnd.extract.anchors import (
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
    except Exception as error:  # noqa: BLE001 - evaluator bugs are exit 70
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
    assurance, execution = _certify_assurance(
        model,
        [population],
        checked,
        exit_code,
        semantic_trace | projection_trace,
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


def _run_transition_raw(
    model_input: str | os.PathLike[str] | Model,
    pre_input: str | os.PathLike[str] | Population,
    steps_input: str | os.PathLike[str] | Mapping[str, Any],
    post_input: str | os.PathLike[str] | Population | None = None,
    *,
    references: BoundReferenceContext | None = None,
) -> _RunResult:
    plan_mode = post_input is None
    model_coordinate = None if isinstance(model_input, Model) else _path(model_input, name="model")
    model: Model | None = None
    populations: dict[str, Population] = {}
    model_digest: str | None = None
    structured = False

    def build(
        exit_code: int,
        *,
        evaluated: bool = False,
        supplied: dict[str, Any] | None = None,
        transition_report: Any = None,
        issues: list[ValidationIssue] | None = None,
        warnings: list[ValidationIssue] | None = None,
        error: BaseException | None = None,
    ) -> dict[str, Any]:
        if plan_mode:
            planned = (
                transition_report
                if isinstance(transition_report, transition_module.ComputedTransition)
                else None
            )
            return report_module.build_plan_transition_payload(
                exit_code,
                model_coordinate,
                evaluated=evaluated,
                model_digest=model_digest,
                structured=structured,
                supplied_digests=supplied,
                transition_report=planned.report if planned is not None else None,
                computed_post=planned.computed_post if planned is not None else None,
                post_snapshot_evaluated=planned is None or planned.post is not None,
                issues=issues,
                warnings=warnings,
                error=error,
            )
        return report_module.build_transition_payload(
            exit_code,
            model_coordinate,
            evaluated=evaluated,
            schema_version=7,
            model_digest=model_digest,
            structured=structured,
            supplied_digests=supplied,
            transition_report=transition_report,
            issues=issues,
            warnings=warnings,
            error=error,
        )

    try:
        model, _ = _resolve_model(model_input)
        if model.reference_populations:
            from gnd.references import resolve_context

            model._references = resolve_context(model, references)
    except ModelValidationError as error:
        return _finalize(
            build(3, issues=error.issues, warnings=error.warnings),
            exit_code=3,
            fallback=lambda failure: build(EXIT_INTERNAL, error=failure),
            warnings=tuple(error.warnings),
            issues=tuple(error.issues),
            error=error,
        )
    except Exception as error:  # noqa: BLE001
        return _finalize(
            build(3, error=error),
            exit_code=3,
            fallback=lambda failure: build(EXIT_INTERNAL, error=failure),
            model=getattr(error, "model", None),
            error=error,
        )

    model_digest = transition_module.model_digest(model)
    structured = bool(structured_derivation_ids(model))
    try:
        populations["pre"], pre_coordinate = _resolve_population(pre_input, model=model, name="pre")
        if post_input is not None:
            populations["post"], _ = _resolve_population(post_input, model=model, name="post")
        if model.reference_populations:
            from gnd.references import bind_population

            for population in populations.values():
                bind_population(model, population, references=model._references)
    except PopulationValidationError as error:
        warnings = [*model.warnings, *error.warnings]
        return _finalize(
            build(3, issues=error.issues, warnings=warnings),
            exit_code=3,
            fallback=lambda failure: build(EXIT_INTERNAL, error=failure),
            model=model,
            populations=tuple(populations.values()),
            warnings=tuple(warnings),
            issues=tuple(error.issues),
            error=error,
        )
    except Exception as error:  # noqa: BLE001
        return _finalize(
            build(3, error=error),
            exit_code=3,
            fallback=lambda failure: build(EXIT_INTERNAL, error=failure),
            model=model,
            populations=tuple(populations.values()),
            error=error,
        )

    try:
        if isinstance(steps_input, Mapping):
            document = transition_module.validate_steps_document(steps_input)
        else:
            document = transition_module.read_steps_document(_path(steps_input, name="steps"))
        transition_module.verify_digests(document, model, pre_coordinate)
        steps = transition_module.validate_steps(document, model)
        multi_clause = any(
            isinstance(rule := fact_type.get("derivation_rule"), dict)
            and "clauses" in rule
            for fact_type in model.fact_types
        )
        if multi_clause:
            transition_module.assert_dynamic_derivation_coverage(
                model, steps, populations, transition_module._supplied_digests(document)
            )
        transition_module.assert_frame_coverage(
            transition_module.touched_fact_types(model, steps),
            populations,
            transition_module._supplied_digests(document),
        )
        transition_module.assert_static_derivation_coverage(
            model,
            steps,
            populations,
            transition_module._supplied_digests(document),
        )
        if not multi_clause:
            transition_module.assert_dynamic_derivation_coverage(
                model, steps, populations, transition_module._supplied_digests(document)
            )
    except transition_module.TransitionLoadError as error:
        return _finalize(
            build(3, supplied=error.supplied, issues=error.issues, warnings=model.warnings),
            exit_code=3,
            fallback=lambda failure: build(EXIT_INTERNAL, error=failure),
            model=model,
            populations=tuple(populations.values()),
            warnings=tuple(model.warnings),
            issues=tuple(error.issues),
            error=error,
        )

    try:
        with capture_branches() as semantic_trace:
            if plan_mode:
                planned = transition_module.evaluate_plan(model, populations["pre"], steps)
                walk = planned.report
            else:
                planned = None
                walk = transition_module.evaluate(
                    model, populations["pre"], populations["post"], steps
                )
            exit_code = transition_module.band(walk)
    except Exception as error:  # noqa: BLE001
        return _finalize(
            build(EXIT_INTERNAL, error=error),
            exit_code=EXIT_INTERNAL,
            fallback=lambda failure: build(EXIT_INTERNAL, error=failure),
            model=model,
            populations=tuple(populations.values()),
            error=error,
        )

    supplied = transition_module._supplied_digests(document)
    with capture_branches() as projection_trace:
        payload = build(
            exit_code,
            evaluated=True,
            supplied=supplied,
            transition_report=planned or walk,
            warnings=model.warnings,
        )
    if planned is not None:
        if planned.post is not None:
            populations["post"] = planned.post
        _, execution = _certify_assurance(
            model,
            [populations["pre"], *([planned.post] if planned.post is not None else [])],
            walk,
            exit_code,
            semantic_trace | projection_trace,
            steps=steps,
        )
        return _finalize(
            payload,
            exit_code=exit_code,
            fallback=lambda failure: build(EXIT_INTERNAL, error=failure),
            model=model,
            populations=(
                (populations["pre"], planned.post)
                if planned.post is not None
                else (populations["pre"],)
            ),
            report=walk,
            warnings=tuple(model.warnings),
            steps=tuple(steps),
            execution=execution,
        )
    assurance, execution = _certify_assurance(
        model,
        [populations["pre"], populations["post"]],
        walk,
        exit_code,
        semantic_trace | projection_trace,
        steps=steps,
    )
    payload["assurance"] = assurance.as_dict()
    return _finalize(
        payload,
        exit_code=exit_code,
        fallback=lambda failure: build(EXIT_INTERNAL, error=failure),
        model=model,
        populations=(populations["pre"], populations["post"]),
        report=walk,
        warnings=tuple(model.warnings),
        steps=tuple(steps),
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
    digest = transition_module.model_digest(model)
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
        source["model_digest"] = transition_module.model_digest(result.model)
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
    except Exception as failure:  # noqa: BLE001 - projection is fail-closed
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


def _run_validate(
    model_input: str | os.PathLike[str] | Model,
    *,
    unredacted: bool = False,
    references: BoundReferenceContext | None = None,
) -> _RunResult:
    return _reference_wrap(
        _project_result(
            _run_validate_raw(model_input, references=references), "validate", unredacted=unredacted
        )
    )


def _run_check(
    model_input: str | os.PathLike[str] | Model,
    population_input: str | os.PathLike[str] | Population,
    *,
    unredacted: bool = False,
    evaluator: Callable[[Model, Population], CheckReport] | None = None,
    anchors: Any = None,
    document: bytes | str | os.PathLike[str] | None = None,
    population_bytes: bytes | None = None,
    admission: bool = False,
    references: BoundReferenceContext | None = None,
) -> _RunResult:
    if admission and evaluator is None:
        evaluator = checker_module.check_partial
    result = _run_check_raw(
        model_input,
        population_input,
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
        except Exception as failure:  # noqa: BLE001 - projection fails closed
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


def _run_transition(
    model_input: str | os.PathLike[str] | Model,
    pre_input: str | os.PathLike[str] | Population,
    steps_input: str | os.PathLike[str] | Mapping[str, Any],
    post_input: str | os.PathLike[str] | Population | None = None,
    *,
    unredacted: bool = False,
    references: BoundReferenceContext | None = None,
) -> _RunResult:
    kind: redaction_module.OutputKind = "plan" if post_input is None else "transition"
    return _reference_wrap(
        _project_result(
            _run_transition_raw(
                model_input, pre_input, steps_input, post_input, references=references
            ),
            kind,
            unredacted=unredacted,
        )
    )


def validate(
    model: str | os.PathLike[str] | Model,
    *,
    unredacted: bool = False,
    references: BoundReferenceContext | None = None,
) -> dict[str, Any]:
    """Validate a model path or reuse a loaded model, returning its report."""
    _check_model_input(model)
    return _run_validate(model, unredacted=unredacted, references=references).payload


def check(
    model: str | os.PathLike[str] | Model,
    population: str | os.PathLike[str] | Population,
    *,
    unredacted: bool = False,
    anchors: Any = None,
    document: bytes | str | os.PathLike[str] | None = None,
    population_bytes: bytes | None = None,
    admission: bool = False,
    references: BoundReferenceContext | None = None,
) -> dict[str, Any]:
    """Check one population and return the same payload emitted by the CLI."""
    _check_model_input(model)
    _check_population_input(population, name="population")
    return _run_check(
        model,
        population,
        unredacted=unredacted,
        anchors=anchors,
        document=document,
        population_bytes=population_bytes,
        admission=admission,
        references=references,
    ).payload


def diff(
    model_a: str | os.PathLike[str] | Model,
    model_b: str | os.PathLike[str] | Model,
    *,
    populations: str | os.PathLike[str] | None = None,
    unredacted: bool = False,
    seed: int = 0,
    references: BoundReferenceContext | None = None,
    references_b: BoundReferenceContext | None = None,
) -> dict[str, Any]:
    """Read two models and optionally one directory of population documents."""
    from dataclasses import replace
    from importlib.resources import files

    from jsonschema import Draft202012Validator

    from gnd.diff import DiffError, diff_models
    from gnd.extract.anchors import vocabulary_digest
    from gnd.population import MAX_POPULATION_BYTES
    from gnd.redaction import RedactionPolicy, project_output
    from gnd.verbalize_population import validate_model_object

    _check_model_input(model_a)
    _check_model_input(model_b)
    for value in (model_a, model_b):
        if not isinstance(value, Model):
            path = Path(_path(value, name="model"))
            if any(part.is_symlink() for part in (path, *path.parents)):
                raise DiffError("diff:model-symlink")
    try:
        left, _ = _resolve_model(model_a, safe=True)
        right, _ = _resolve_model(model_b, safe=True)
        from gnd.references import resolve_context

        for bound_model, context in ((left, references), (right, references_b)):
            if bound_model.reference_populations:
                bound_model._references = resolve_context(bound_model, context)
    except OSError:
        raise
    except Exception as error:  # model parser boundary
        raise DiffError(f"diff:invalid-model:{type(error).__name__}") from error
    try:
        validate_model_object(left)
        validate_model_object(right)
    except Exception as error:  # public in-memory model boundary
        raise DiffError(f"diff:invalid-model:{type(error).__name__}") from error
    if vocabulary_digest(left) != vocabulary_digest(right):
        raise DiffError("diff:vocabulary-mismatch")
    provided: list[tuple[str, bytes]] = []
    if populations is not None:
        root = Path(_path(populations, name="populations"))
        if any(part.is_symlink() for part in (root, *root.parents)) or not root.is_dir():
            raise DiffError("diff:population-directory-invalid")
        paths = sorted(root.iterdir(), key=lambda item: item.name)
        if len(paths) > 1024:
            raise DiffError("diff:too-many-populations")
        for path in paths:
            if any(part.is_symlink() for part in (path, *path.parents)) or not path.is_file() or path.suffix.lower() not in {".json", ".yaml", ".yml"}:
                raise DiffError(f"diff:population-entry-invalid:{path.name}")
            if path.stat().st_size > MAX_POPULATION_BYTES:
                raise DiffError(f"diff:population-too-large:{path.name}")
            with path.open("rb") as stream:
                raw = stream.read(MAX_POPULATION_BYTES + 1)
            if len(raw) > MAX_POPULATION_BYTES:
                raise DiffError(f"diff:population-too-large:{path.name}")
            provided.append((path.name, raw))
    report = diff_models(left, right, populations=provided, seed=seed)
    first, second = RedactionPolicy.from_model(left), RedactionPolicy.from_model(right)
    policy = replace(first, declarations=first.declarations + second.declarations,
                     effective_roles=first.effective_roles | second.effective_roles)
    projected = project_output("diff", report, policy=policy,
                               mode="unredacted" if unredacted else "applied",
                               emitter_id="api-diff")
    schema = json.loads((files("gnd") / "diff.schema.json").read_text(encoding="utf-8"))
    Draft202012Validator(schema).validate(projected)
    if left.reference_populations or right.reference_populations:
        from gnd.references import reference_model_digest, resolve_context

        context = resolve_context(left) if left.reference_populations else None
        return {
            "schema_version": 12,
            "command": "diff",
            "outcome": "accepted",
            "exit_code": 0,
            "model_digest": reference_model_digest(left),
            "reference_binding": {
                "identity_version": 1,
                "references": [
                    {"id": origin.id, "sha256": origin.raw_sha256}
                    for origin, _path, _raw in (context._snapshots if context else ())
                ],
            },
            "report": projected,
            "occurrence_origins": [],
        }
    return projected


def _run_verbalize(
    model: str | os.PathLike[str] | Model,
    population: str | os.PathLike[str] | Population,
    *,
    anchors: Any = None,
    document: bytes | str | os.PathLike[str] | None = None,
    population_bytes: bytes | None = None,
    unredacted: bool = False,
    emitter_id: str = "api-population-verbalization",
) -> dict[str, Any]:
    """Return projected fact sentences without running a checker or a model."""
    from gnd.extract.anchors import (
        MAX_DOCUMENT_BYTES,
        AnchorError,
        AnchorSidecar,
        read_anchor_sidecar,
        read_regular_path,
        validate_anchor_sidecar,
    )
    from gnd.population import PopulationLoadError
    from gnd.redaction import RedactionProjectionError
    from gnd.verbalize_population import (
        PopulationVerbalizationError,
        validate_model_object,
        verbalize_population,
    )

    def failure(exit_code: int, kind: str, message: str) -> dict[str, Any]:
        return {"rows": [], "exit_code": exit_code, "error": {"kind": kind, "message": message}}

    try:
        _check_model_input(model)
        _check_population_input(population, name="population")
        if (anchors is None) != (document is None):
            raise ValueError("anchors and document must be supplied together")
        selected_model, _ = _resolve_model(model)
        if isinstance(model, Model):
            validate_model_object(selected_model)
        selected_population, population_path = _resolve_population(
            population, model=selected_model, name="population",
        )
        if not selected_population.matches_validation_marker(selected_model):
            raise ValueError("population validation marker is stale")
        if isinstance(anchors, (str, os.PathLike)):
            selected_anchors = read_anchor_sidecar(anchors)
        elif isinstance(anchors, AnchorSidecar):
            selected_anchors = validate_anchor_sidecar(anchors)
        elif anchors is None:
            selected_anchors = None
        else:
            raise ValueError("invalid anchor sidecar")
        if selected_anchors is not None:
            if population_bytes is None and population_path is not None:
                population_bytes = read_regular_path(
                    population_path, label="anchor population", max_bytes=MAX_DOCUMENT_BYTES,
                )
            if isinstance(document, (str, os.PathLike)):
                document_bytes = read_regular_path(
                    document, label="anchor document", max_bytes=MAX_DOCUMENT_BYTES,
                )
            elif isinstance(document, bytes):
                document_bytes = document
            else:
                raise ValueError("invalid document")
        else:
            document_bytes = None
        rows = verbalize_population(
            selected_model, selected_population,
            anchors=selected_anchors, population_bytes=population_bytes,
            document_bytes=document_bytes, unredacted=unredacted,
            emitter_id=emitter_id,
        )
        return {"rows": list(rows), "exit_code": 0, "error": None}
    except RedactionProjectionError:
        return failure(70, "projection", "projection failed")
    except (
        AnchorError, ModelValidationError, model_module.ModelLoadError,
        PopulationLoadError, PopulationVerbalizationError,
        ValueError, TypeError, OSError,
    ):
        return failure(3, "input", "invalid model, population, anchors, or document")
    except Exception:  # noqa: BLE001 - unclassified runtime fault, without leaking bytes
        return failure(70, "projection", "projection failed")


def verbalize(
    model: str | os.PathLike[str] | Model,
    population: str | os.PathLike[str] | Population,
    *,
    anchors: Any = None,
    document: bytes | str | os.PathLike[str] | None = None,
    population_bytes: bytes | None = None,
    unredacted: bool = False,
) -> dict[str, Any]:
    """Public population sentence view; applied redaction is the default."""
    return _run_verbalize(
        model, population, anchors=anchors, document=document,
        population_bytes=population_bytes, unredacted=unredacted,
    )


def transition(
    model: str | os.PathLike[str] | Model,
    pre: str | os.PathLike[str] | Population,
    steps: str | os.PathLike[str] | Mapping[str, Any],
    post: str | os.PathLike[str] | Population | None = None,
    *,
    unredacted: bool = False,
    references: BoundReferenceContext | None = None,
) -> dict[str, Any]:
    """Audit a declared post, or compute it when ``post`` is omitted."""
    _check_model_input(model)
    _check_population_input(pre, name="pre")
    _check_steps_input(steps)
    if post is not None:
        _check_population_input(post, name="post")
    return _run_transition(
        model, pre, steps, post, unredacted=unredacted, references=references
    ).payload


def _witness_inputs(model_path, population_path, reference_root):
    """Load witness inputs without introducing a new checking claim."""
    from pathlib import Path

    from gnd.model import load_model_bytes
    from gnd.population import _parse_document_bytes, load_population_bytes
    from gnd.references import bind_references
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
    context = (
        bind_references(
            model, root=reference_root if reference_root is not None else Path(model_path).parent
        )
        if model.reference_populations
        else None
    )
    try:
        md = json.loads(mr)
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


def judgments(
    model_path,
    population_path,
    policy_path,
    receipts_path,
    *,
    trusted_root,
    reference_root=None,
    unredacted=False,
):
    """Evaluate saved opinions without obtaining any external judgment."""
    from pathlib import Path

    from gnd.artifacts import ArtifactError, read_regular_bounded
    from gnd.judgments import (
        JudgmentInputError,
        evaluate_judgments,
        read_judgment_policy,
        read_judgment_receipts,
        redact_policy,
    )
    from gnd.model import ModelLoadError, ModelValidationError, load_model_bytes
    from gnd.population import PopulationLoadError, load_population_bytes
    from gnd.references import bind_references

    result = {
        "schema_version": 15,
        "command": "judgments",
        "outcome": 3,
        "error": None,
        "mechanical_report": None,
        "judgment_policy": None,
    }

    def read(path, maximum):
        path = Path(path).absolute()
        try:
            return read_regular_bounded(path.parent, path.name, max_bytes=maximum)[0]
        except ArtifactError as error:
            raise JudgmentInputError(
                "limit" if any(w in str(error) for w in ("cap", "over", "exceed")) else "binding",
                "input unavailable or unstable",
            ) from error

    try:
        policy = read_judgment_policy(read(policy_path, 1024 * 1024))
        receipts = read_judgment_receipts(read(receipts_path, 10 * 1024 * 1024))
        mr, pr = read(model_path, 10 * 1024 * 1024), read(population_path, 10 * 1024 * 1024)
        model = load_model_bytes(mr, source=model_path)
        candidate = load_population_bytes(pr, source=population_path, model=model)
        refs = (
            bind_references(model, root=reference_root or Path(model_path).parent)
            if model.reference_populations
            else None
        )
        raw_mechanical = check(model, candidate, admission=True, references=refs, unredacted=True)
        result["mechanical_report"] = (
            raw_mechanical
            if unredacted
            else check(model, candidate, admission=True, references=refs, unredacted=False)
        )
        for payload in (raw_mechanical, result["mechanical_report"]):
            inner = payload.get("report", payload)
            inner["model"], inner["population"] = str(model_path), str(population_path)
        decision = evaluate_judgments(
            policy,
            receipts,
            model=model,
            candidate=candidate,
            mechanical_report=raw_mechanical,
            model_bytes=mr,
            population_bytes=pr,
            trusted_root=trusted_root,
            references=refs,
        )
        result["outcome"] = 0 if decision["admission"] else 1
        result["judgment_policy"] = decision if unredacted else redact_policy(decision)
    except JudgmentInputError as error:
        result.update(
            outcome=4 if error.reason in {"limit", "io"} else 3,
            error={"reason": error.reason, "message": str(error)},
        )
    except (
        ValueError,
        TypeError,
        OSError,
        ModelLoadError,
        ModelValidationError,
        PopulationLoadError,
    ):
        result.update(error={"reason": "binding", "message": "invalid bound judgment input"})
    return result


def export_souffle(model_path, population_path, *, reference_root=None, out=None, raw=False):
    """Render/publish the explicit standalone Souffle derivation fragment."""
    from gnd.export.souffle_io import export_souffle as export

    return export(
        model_path, population_path, reference_root=reference_root, out=out, raw=raw
    ).model_dump()


def verify_souffle(bundle_path):
    """Verify retained bytes and reproduce their deterministic emission."""
    from gnd.export.souffle_io import verify_souffle_bundle

    return verify_souffle_bundle(bundle_path).model_dump()


def run_souffle(bundle_path, *, executable="souffle", raw=False):
    """Run only an explicitly selected, checked foreign derivation program."""
    from gnd.export.souffle_runtime import run_souffle as run

    result = run(bundle_path, executable=executable)
    if not raw:
        result["extensions"] = None
        if result["tool"]:
            result["tool"].update(path=None, sha256=None)
    return result


def souffle_witness(bundle_path, targets_path, *, executable="souffle", raw=False, out=None):
    """Map native positive provenance and independently replay before publication."""
    from gnd import artifacts
    from gnd.export.souffle import INPUT_ERRORS, wire
    from gnd.export.souffle_io import read_file
    from gnd.export.souffle_runtime import native_witness
    from gnd.witness.io import parse_wire
    from gnd.witness.types import WitnessResult

    try:
        if out is not None and not raw:
            return WitnessResult(3, reason="input-invalid").model_dump()
        targets = parse_wire(read_file(targets_path, 10485760))
        result = native_witness(bundle_path, targets, executable=executable)
        if result.exit_code == 0 and out is not None:
            from pathlib import Path

            p = Path(out)
            artifacts.publish_leaf_atomic(p.parent, p.name, wire(result.certificate))
        report = result.model_dump()
        if not raw:
            report["certificate"] = None
            report["results"] = [
                {k: v for k, v in r.items() if k != "target"} for r in report["results"]
            ]
        return report
    except (artifacts.ArtifactError, *INPUT_ERRORS):
        return WitnessResult(3, reason="input-invalid").model_dump()


def export_lean(
    model_path, population_path, *, toolchain, reference_root=None, out=None, raw=False
):
    """Export finite definitions; no theorem or snapshot-equivalence claim."""
    from gnd.export.lean_io import export_lean as export

    return export(
        model_path,
        population_path,
        toolchain=toolchain,
        reference_root=reference_root,
        out=out,
        raw=raw,
    ).model_dump()


def verify_lean(bundle_path):
    """Verify exact deterministic reconstruction of a raw Lean bundle."""
    from gnd.export.lean_io import verify_lean_bundle

    return verify_lean_bundle(bundle_path).model_dump()


def compile_lean(bundle_path, *, executable="lake", elaborate_stubs=False):
    """Explicit compiler work; all theorem obligations remain unproved."""
    from gnd.export.lean_runtime import compile_lean as compile_bundle

    return compile_bundle(
        bundle_path, executable=executable, elaborate_stubs=elaborate_stubs
    ).model_dump()
