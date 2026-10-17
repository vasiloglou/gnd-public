"""Stable in-process access to GND validation and checking reports."""

from __future__ import annotations

import copy  # noqa: F401 -- historical compatibility binding
import json  # noqa: F401 -- historical compatibility binding
import os
from collections.abc import Callable, Mapping  # noqa: F401 -- historical compatibility binding
from dataclasses import (  # noqa: F401 -- historical compatibility binding  # noqa: F401 -- historical compatibility binding
    dataclass,
    replace,
)
from pathlib import Path
from typing import Any

from gnd import checker as checker_module  # noqa: F401 -- historical compatibility binding
from gnd import input_policy as _rf7_input
from gnd import model as model_module
from gnd import redaction as redaction_module
from gnd import report as report_module
from gnd import transition as transition_module
from gnd.assurance import (
    AssuranceBlockV1,  # noqa: F401 -- historical compatibility binding
    _mint_execution,  # noqa: F401 -- historical compatibility binding
    certify_result,  # noqa: F401 -- historical compatibility binding
    derive_assurance_scope,  # noqa: F401 -- historical compatibility binding
    semantic_decision_for_band,  # noqa: F401 -- historical compatibility binding
)
from gnd.assurance_evidence import (
    load_assurance_evidence,  # noqa: F401 -- historical compatibility binding
)
from gnd.checker import CheckReport  # noqa: F401 -- historical compatibility binding
from gnd.checking_service import (
    RunResult as _RunResult,
)
from gnd.checking_service import (
    certify_assurance as _certify_assurance,
)
from gnd.checking_service import (
    finalize as _finalize,
)
from gnd.checking_service import (
    path as _path,
)
from gnd.checking_service import (
    project_result as _project_result,
)
from gnd.checking_service import (
    projection_failure_base as _projection_failure_base,  # noqa: F401 -- historical helper import
)
from gnd.checking_service import (
    reference_wrap as _reference_wrap,
)
from gnd.checking_service import (
    resolve_model as _resolve_model,
)
from gnd.checking_service import (
    resolve_population as _resolve_population,
)
from gnd.checking_service import (
    run_check as _run_check,
)
from gnd.checking_service import (
    run_check_raw as _run_check_raw,  # noqa: F401 -- historical helper import
)
from gnd.exits import EXIT_INTERNAL
from gnd.export.service import (
    compile_lean as compile_lean,  # noqa: PLC0414 -- compatibility surface
)
from gnd.export.service import (
    export_lean as export_lean,  # noqa: PLC0414 -- compatibility surface
)
from gnd.export.service import (
    export_souffle as export_souffle,  # noqa: PLC0414 -- compatibility surface
)
from gnd.export.service import (
    run_souffle as run_souffle,  # noqa: PLC0414 -- compatibility surface
)
from gnd.export.service import (
    souffle_witness as souffle_witness,  # noqa: PLC0414 -- compatibility surface
)
from gnd.export.service import (
    verify_lean as verify_lean,  # noqa: PLC0414 -- compatibility surface
)
from gnd.export.service import (
    verify_souffle as verify_souffle,  # noqa: PLC0414 -- compatibility surface
)
from gnd.model import (
    Model,
    ModelValidationError,
    ValidationIssue,
    load_model,  # noqa: F401 -- historical compatibility binding
    structured_derivation_ids,
)
from gnd.model_index import scoped as _index_scoped
from gnd.population import (
    Population,
    PopulationLoadError,  # noqa: F401 -- historical compatibility binding
    PopulationValidationError,
    load_population,  # noqa: F401 -- historical compatibility binding
)
from gnd.references import BoundReferenceContext
from gnd.semantic_registry import capture_branches
from gnd.terms import uses_temporal  # noqa: F401 -- historical compatibility binding
from gnd.witness.service import (
    replay as replay,  # noqa: PLC0414 -- compatibility surface
)
from gnd.witness.service import (
    witness as witness,  # noqa: PLC0414 -- compatibility surface
)
from gnd.witness.service import (
    witness_inputs as _witness_inputs,  # noqa: F401 -- compatibility surface
)

__all__ = ("validate", "check", "transition", "verbalize", "diff", "witness", "replay")  # noqa: RUF022 - approved stable order






def _check_model_input(value: object) -> None:
    if not isinstance(value, Model):
        _path(value, name="model")


def _check_population_input(value: object, *, name: str) -> None:
    if not isinstance(value, Population):
        _path(value, name=name)


def _check_steps_input(value: object) -> None:
    if not isinstance(value, Mapping):
        _path(value, name="steps")










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
    except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
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
    except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
        return _finalize(
            build(3, error=error),
            exit_code=3,
            fallback=lambda failure: build(EXIT_INTERNAL, error=failure),
            model=getattr(error, "model", None),
            error=error,
        )

    model_digest = transition_module.transition_model_identity(model)
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
    except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
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
    except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
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




@_index_scoped
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
    compiled_operations: bool = False,
    unredacted: bool = False,
    anchors: Any = None,
    document: bytes | str | os.PathLike[str] | None = None,
    population_bytes: bytes | None = None,
    admission: bool = False,
    references: BoundReferenceContext | None = None,
) -> dict[str, Any]:
    """Check one population and return the same payload emitted by the CLI."""
    if not isinstance(compiled_operations, bool):
        raise TypeError('compiled_operations must be a boolean')
    if compiled_operations and admission:
        raise ValueError('compiled_operations cannot be combined with admission')
    _check_model_input(model)
    _check_population_input(population, name="population")
    return _run_check(
        model,
        population,
        compiled_operations=compiled_operations,
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
    from dataclasses import replace  # noqa: F811 -- historical compatibility binding
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
    schema = _rf7_input.loads((files("gnd") / "diff.schema.json").read_text(encoding="utf-8"))
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
    from gnd.population import PopulationLoadError  # noqa: F811 -- local compatibility binding
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
    except Exception:  # noqa: BLE001 -- preserve predecessor refusal contract
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
    from gnd.population import (  # noqa: F811 -- local compatibility binding
        PopulationLoadError,
        load_population_bytes,
    )
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
