from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

from gnd import api as api_module
from gnd import report as report_module
from gnd import resolve_version, verbalize
from gnd.checker import check
from gnd.commands._output import (
    _print_admission_text,
    _print_issues,
    _print_projected_text,
    _print_report,
    _print_trace,
    _print_transition,
)
from gnd.exits import EXIT_COLLISION, EXIT_INTERNAL, EXIT_IO, EXIT_NO_INPUT, EXIT_USAGE
from gnd.model import ModelValidationError, load_model

_DEFAULT_CHECK = check

def _cmd_validate(
    model_path: str,
    output_format: str,
    *,
    trace: bool = False,
    unredacted: bool = False,
) -> int:
    result = api_module._run_validate(model_path, unredacted=unredacted)
    if output_format == "json":
        try:
            report_module.emit(result.payload)
        except report_module.NonJsonValueError as error:
            fallback = report_module.build_validate_payload(
                EXIT_INTERNAL,
                model_path,
                schema_version=result.payload["schema_version"],
                error=error,
            )
            report_module.emit(fallback)
            return EXIT_INTERNAL
        return result.exit_code
    mechanical_payload = result.payload.get("report", result.payload)
    if "redaction" in mechanical_payload:
        if trace and result.model is not None and not result.issues and result.error is None:
            _print_trace(result.model, model_path)
        _print_projected_text(mechanical_payload)
        return result.exit_code
    for warning in result.warnings:
        print(f"WARNING at {warning.path}: {warning.message} [{warning.rule_id}]")
    if result.issues:
        _print_issues(list(result.issues))
        return result.exit_code
    if result.error is not None:
        prefix = "INTERNAL ERROR" if result.exit_code == EXIT_INTERNAL else "ERROR"
        print(f"{prefix}: {result.error}")
        return result.exit_code
    if trace:
        _print_trace(result.model, model_path)
    print(f"OK: {model_path} is a valid GND ORM model")
    return result.exit_code

def _cmd_coverage(
    model_path: str,
    experiments: list[str],
    check_sources: list[str],
    verify_sources: list[str],
    conformance_sources: list[str],
    transition_sources: list[str],
    output_format: str,
) -> int:
    """Compute the read-only element roadmap; never write an artifact."""

    from gnd.coverage import (
        CoverageInputError,
        CoverageMissingError,
        CoveragePathError,
        build_coverage,
        build_payload,
        canonical_payload,
        guard_named_source,
        render_coverage,
    )

    model_file = Path(model_path)
    try:
        guard_named_source(model_file, directory=False)
        model = load_model(model_file)
    except CoverageMissingError as error:
        print(f"MISSING: {error}")
        return EXIT_NO_INPUT
    except CoveragePathError as error:
        print(f"IO ERROR: {error}")
        return EXIT_IO
    except ModelValidationError as error:
        _print_issues(error.issues)
        return 3
    except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
        print(f"ERROR: {error}")
        return 3

    try:
        result = build_coverage(
            model,
            model_path=model_path,
            experiments=[Path(path) for path in experiments],
            check=[Path(path) for path in check_sources],
            verify=[Path(path) for path in verify_sources],
            conformance=[Path(path) for path in conformance_sources],
            transition=[Path(path) for path in transition_sources],
        )
    except CoverageMissingError as error:
        print(f"MISSING: {error}")
        return EXIT_NO_INPUT
    except CoveragePathError as error:
        print(f"IO ERROR: {error}")
        return EXIT_IO
    except CoverageInputError as error:
        print(f"ERROR: {error}")
        return 3

    payload = build_payload(result, gnd_version=resolve_version())
    if output_format == "json":
        print(canonical_payload(payload))
    else:
        print(render_coverage(payload), end="")
    return 0

def _cmd_transition(
    model_path: str,
    pre_path: str,
    steps_path: str,
    post_path: str | None,
    output_format: str,
    *,
    unredacted: bool = False,
) -> int:
    result = api_module._run_transition(
        model_path,
        pre_path,
        steps_path,
        post_path,
        unredacted=unredacted,
    )
    if output_format == "json":
        if result.execution is not None:
            from gnd.assurance_transport import prepare_execution

            prepare_execution(result.execution)
        report_module.emit(result.payload)
        return result.exit_code
    mechanical_payload = result.payload.get("report", result.payload)
    if "redaction" in mechanical_payload:
        _print_projected_text(mechanical_payload)
        return result.exit_code
    if result.report is not None:
        _print_transition(
            result.report,
            list(result.warnings),
            computed_post=(
                result.payload["transition"]["computed_post"] if post_path is None else None
            ),
        )
        return result.exit_code
    for warning in result.warnings:
        print(f"WARNING at {warning.path}: {warning.message} [{warning.rule_id}]")
    if result.issues:
        _print_issues(list(result.issues))
    elif result.error is not None:
        prefix = "INTERNAL ERROR" if result.exit_code == EXIT_INTERNAL else "ERROR"
        print(f"{prefix}: {result.error}")
    return result.exit_code

def _cmd_check(
    model_path: str,
    population_path: str,
    output_format: str,
    *,
    unredacted: bool = False,
    anchors_path: str | None = None,
    document_path: str | None = None,
    admission: bool = False,
) -> int:
    result = api_module._run_check(
        model_path,
        population_path,
        unredacted=unredacted,
        evaluator=check if check is not _DEFAULT_CHECK else None,
        anchors=anchors_path,
        document=document_path,
        admission=admission,
    )
    if output_format == "json":
        if result.execution is not None:
            from gnd.assurance_transport import prepare_execution

            prepare_execution(result.execution)
        report_module.emit(result.payload)
        return result.exit_code
    mechanical_payload = result.payload.get("report", result.payload)
    if "redaction" in mechanical_payload:
        _print_projected_text(mechanical_payload)
        if admission:
            _print_admission_text(result.payload.get("report", result.payload))
        return result.exit_code
    if result.report is not None:
        for warning in result.warnings:
            print(f"WARNING at {warning.path}: {warning.message} [{warning.rule_id}]")
        _print_report(result.report)
        if admission:
            _print_admission_text(result.payload.get("report", result.payload))
        return result.exit_code
    for warning in result.warnings:
        print(f"WARNING at {warning.path}: {warning.message} [{warning.rule_id}]")
    if result.issues:
        _print_issues(list(result.issues))
    elif result.error is not None:
        prefix = "INTERNAL ERROR" if result.exit_code == EXIT_INTERNAL else "ERROR"
        print(f"{prefix}: {result.error}")
    return result.exit_code

def _cmd_verbalize_population(
    model_path: str, population_path: str, output_format: str, *,
    anchors_path: str | None = None, document_path: str | None = None,
    unredacted: bool = False,
) -> int:
    emitter_id = f"cli-population-verbalization-{output_format}"
    result = api_module._run_verbalize(
        model_path, population_path, anchors=anchors_path, document=document_path,
        unredacted=unredacted, emitter_id=emitter_id,
    )
    if result["exit_code"]:
        print(result["error"]["message"], file=sys.stderr)
        return result["exit_code"]
    for row in result["rows"]:
        if output_format == "jsonl":
            print(json.dumps(row, ensure_ascii=False, separators=(",", ":")))
            continue
        ref = row["fact_ref"]
        suffix = f" | excerpt: {row['excerpt']}" if "excerpt" in row else ""
        print(f"FACT {verbalize.path_segment(ref['fact_type'])}[{ref['index']}]: {row['sentence']}{suffix}")
    return 0

def _cmd_diff(
    model_a: str, model_b: str, populations: str | None, output_format: str,
    unredacted: bool, seed: int,
) -> int:
    from gnd.diff import DiffError

    try:
        payload = api_module.diff(model_a, model_b, populations=populations,
                                  unredacted=unredacted, seed=seed)
    except (DiffError, ModelValidationError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 3
    except OSError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return EXIT_IO
    except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
        print(f"INTERNAL ERROR: {error}", file=sys.stderr)
        return EXIT_INTERNAL
    if output_format == "json":
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    else:
        payload = payload["report"] if payload.get("schema_version") == 12 else payload
        print(f"DIFF {payload['model_a_digest']} {payload['model_b_digest']}")
        print(f"Entailment rows: {len(payload['entailment'])}")
        for row in payload["entailment"]:
            print(f"  {row['from_model']}->{row['to_model']} {row['left_ref']} {row['result']}")
        for row in payload["populations"]:
            print(f"POPULATION {row['population_ref']}: A={row['a'].get('band')} B={row['b'].get('band')}")
            for direction in ("a_to_b", "b_to_a"):
                for gap in row[direction]:
                    print(f"  {direction} {gap['target_ref']} {gap['verdict']} {gap['witness_sentence'] or ''}")
        for row in payload["not_derivable"]:
            print(f"NOT DERIVABLE {row['source']}: {row['reason']}")
    return 0

def _cmd_rai_import(
    model_path: str,
    output_dir: str,
    source_artifact: str,
    source_commit: str | None,
) -> int:
    """Import one admitted RAI ORM document and publish its evidence pair."""

    from gnd.rai_import import (
        RaiImportCollision,
        RaiImportError,
        RaiImportIO,
        RaiImportMissing,
        RaiImportRequest,
        plan_rai_import,
        publish_rai_import,
    )

    request = RaiImportRequest(Path(model_path), Path(output_dir), source_artifact, source_commit)
    try:
        result = plan_rai_import(request)
        publish_rai_import(request, result)
    except RaiImportCollision as error:
        print(error, file=sys.stderr)
        return EXIT_COLLISION
    except RaiImportMissing as error:
        print(error, file=sys.stderr)
        return EXIT_NO_INPUT
    except RaiImportIO as error:
        print(error, file=sys.stderr)
        return EXIT_IO
    except RaiImportError as error:
        print(error, file=sys.stderr)
        return 3
    except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
        print(f"INTERNAL ERROR: {type(error).__name__}: {error}", file=sys.stderr)
        return EXIT_INTERNAL
    print(f"IMPORTED {model_path} -> {output_dir}")
    return 0

def _cmd_check_batch(model_path: str, populations_dir: str, *, unredacted: bool = False) -> int:
    """Emit the canonical one-model/many-population matrix."""

    from importlib.resources import files

    from gnd.batch import (
        BatchInternalError,
        BatchIOError,
        BatchMissingError,
        BatchUsageError,
        build_batch_payload,
        canonical_batch_bytes,
        check_population_directory,
    )

    try:
        result = check_population_directory(Path(model_path), Path(populations_dir))
        payload = build_batch_payload(result)
        try:
            batch_model = load_model(model_path)
        except Exception:  # noqa: BLE001 -- preserve predecessor refusal contract
            batch_model = None
        if batch_model is not None:
            from gnd.redaction import RedactionPolicy, project_output

            policy = RedactionPolicy.from_model(batch_model)
            payload = project_output(
                "batch",
                payload,
                policy=policy,
                mode="unredacted" if unredacted else "applied",
                emitter_id="cli-batch-json",
            )
        schema = json.loads(
            files("gnd").joinpath("batch-report.schema.json").read_text(encoding="utf-8")
        )
        Draft202012Validator(schema).validate(payload)
        sys.stdout.buffer.write(canonical_batch_bytes(payload))
        return result.aggregate_exit
    except BatchUsageError as error:
        print(f"gnd check: error: {error}", file=sys.stderr)
        return EXIT_USAGE
    except BatchMissingError as error:
        print(f"gnd check: error: {error}", file=sys.stderr)
        return EXIT_NO_INPUT
    except BatchIOError as error:
        print(f"gnd check: error: {error}", file=sys.stderr)
        return EXIT_IO
    except BatchInternalError as error:
        print(f"INTERNAL ERROR: {error}", file=sys.stderr)
        return EXIT_INTERNAL
    except Exception as error:  # noqa: BLE001 -- preserve predecessor refusal contract
        print(f"INTERNAL ERROR: {type(error).__name__}: {error}", file=sys.stderr)
        return EXIT_INTERNAL

_cmd_validate.__module__ = "gnd.cli"
_cmd_coverage.__module__ = "gnd.cli"
_cmd_transition.__module__ = "gnd.cli"
_cmd_check.__module__ = "gnd.cli"
_cmd_verbalize_population.__module__ = "gnd.cli"
_cmd_diff.__module__ = "gnd.cli"
_cmd_rai_import.__module__ = "gnd.cli"
_cmd_check_batch.__module__ = "gnd.cli"
