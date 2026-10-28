from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

from gnd import api as api_module
from gnd import input_policy as _rf7_input
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
    compiled_operations: bool = False,
) -> int:
    result = api_module._run_check(
        model_path,
        population_path,
        unredacted=unredacted,
        evaluator=check if check is not _DEFAULT_CHECK else None,
        anchors=anchors_path,
        document=document_path,
        admission=admission,
        **({"compiled_operations": True} if compiled_operations else {}),
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
        # IK1-Q2: description changes, as escaped canonical JSON so untrusted
        # text cannot forge a line (IK-R5).
        for row in payload.get("annotations", ()):
            print(f"ANNOTATION {row['object_type']} description")
            for side in ("before", "after"):
                value = json.dumps(row[side], ensure_ascii=True, sort_keys=True, separators=(",", ":"))
                print(f"  {side} {value}")
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

def _cmd_check_batch(model_path: str, populations_dir: str, *, unredacted: bool = False,
                     compiled_operations: bool = False) -> int:
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
        result = check_population_directory(
            Path(model_path), Path(populations_dir),
            **({"compiled_operations": True} if compiled_operations else {}),
        )
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
        schema = _rf7_input.loads(
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

from pathlib import PurePosixPath, PureWindowsPath

from gnd.commands._arguments import _add_format_argument, _add_unredacted_argument


def _register_import(subparsers):
    import_parser = subparsers.add_parser(
        "import", help="import a supported foreign ORM dialect create-once"
    )
    import_subparsers = import_parser.add_subparsers(dest="import_command", required=True)
    rai_import_parser = import_subparsers.add_parser(
        "rai-orm",
        help="import the bounded rai-orm-from-schema dialect",
    )
    rai_import_parser.add_argument("model", help="path to the source RAI ORM YAML file")
    rai_import_parser.add_argument(
        "--out", required=True, help="new directory for model.orm.yaml and aliases.json"
    )
    rai_import_parser.add_argument(
        "--source-artifact",
        help="stable relative POSIX source path recorded in provenance",
    )
    rai_import_parser.add_argument(
        "--source-commit",
        help="source repository commit required when provenance must be synthesized",
    )

    ilp_import_parser = import_subparsers.add_parser(
        "ilp-rules",
        help="admit learned ILP clauses as induced guarded constraints (IK5)",
        description=(
            "Rewrite each learned clause wrong(X) :- B1, ..., Bn in the declared fragment "
            "into one guarded constraint (source induced, status proposed, modality "
            "deontic), re-run the checker over the manifest's populations, and write an "
            "evolve proposal only if, for every clause, the set of example ids GND covers "
            "equals the set the run record reports. Admission is all-or-nothing. Exits 0 "
            "when the proposal is written, 3 on any refusal (a construct outside the "
            "fragment, a binding or coverage mismatch, invalid input), 5 when a population "
            "fails to load, 11 when --out exists, 64 on a usage error, 66 on a missing "
            "input, 70 on an internal defect, 74 on a refused path."
        ),
    )
    ilp_import_parser.add_argument("model", help="path to the model file")
    ilp_import_parser.add_argument(
        "clauses", help="learned clauses: Popper's printed program, or gnd-ilp-clauses/1 JSON"
    )
    ilp_import_parser.add_argument("--labels", required=True, help="the class-mode label manifest")
    ilp_import_parser.add_argument(
        "--reported-coverage", required=True, help="the learner run record (gnd-ilp-run/1)"
    )
    ilp_import_parser.add_argument(
        "--target", required=True, choices=("popper", "neutral", "ilasp", "llm", "rules"), help="the adapter CLAUSES is in"
    )
    ilp_import_parser.add_argument("--out", required=True, help="write the evolve proposal here")
    ilp_import_parser.add_argument(
        "--actor", type=_ilp_actor, default="gnd import ilp-rules",
        help="who requests the proposal (its audit actor_id)",
    )
    ilp_import_parser.add_argument(
        "--requested-at", type=_ilp_requested_at, default=None,
        help="the audit time, ISO-8601 with a UTC offset (default: now); fix it for reproducible output",
    )
    _add_format_argument(ilp_import_parser)

    return {'import_parser': import_parser, 'rai_import_parser': rai_import_parser,
            'ilp_import_parser': ilp_import_parser}


def _ilp_actor(text: str) -> str:
    import argparse

    if not text.strip():
        raise argparse.ArgumentTypeError("--actor must name who requests the proposal")
    return text


def _ilp_requested_at(text: str):
    import argparse
    from datetime import datetime

    try:
        value = datetime.fromisoformat(text)
    except ValueError as error:
        raise argparse.ArgumentTypeError(f"{text!r} is not an ISO-8601 time") from error
    if value.tzinfo is None or value.utcoffset() is None:
        raise argparse.ArgumentTypeError("--requested-at needs a UTC offset")
    return value


def _register_validate(subparsers):
    validate_parser = subparsers.add_parser(
        "validate",
        help="validate a model and bind declared fixed reference populations",
        description="Validate the model; version-4 references bind beneath its parent with disjoint fixed ownership and exact raw hashes.",
    )
    validate_parser.add_argument("model", help="path to the model file")
    validate_parser.add_argument(
        "--trace",
        action="store_true",
        help=(
            "report what a transition run would evaluate, WITHOUT evaluating "
            "anything: the two digests every steps.json must carry, which "
            "preconditions compile to standing obligations and which are "
            "retained per-step and why, and the frame modality each fact type "
            "would be graded with. Reports; never decides, never reads a "
            "population. This is the only shipped producer of "
            "operations_digest, which every steps.json is required to carry"
        ),
    )
    _add_format_argument(validate_parser)
    _add_unredacted_argument(validate_parser)

    return {'validate_parser': validate_parser}


def _register_diff(subparsers):
    diff_parser = subparsers.add_parser("diff", help="compare two models over one vocabulary")
    diff_parser.add_argument("model_a")
    diff_parser.add_argument("model_b")
    diff_parser.add_argument("--populations", metavar="DIR")
    diff_parser.add_argument("--seed", type=int, default=0)
    _add_format_argument(diff_parser)
    _add_unredacted_argument(diff_parser)

    return {'diff_parser': diff_parser}


def _register_coverage(subparsers):
    coverage_parser = subparsers.add_parser(
        "coverage",
        help="report claims and cited evidence for every addressable model element",
    )
    coverage_parser.add_argument("model", help="path to the model file")
    coverage_parser.add_argument("--experiments", action="append", default=[], metavar="DIR")
    coverage_parser.add_argument("--check", action="append", default=[], metavar="PATH")
    coverage_parser.add_argument("--verify", action="append", default=[], metavar="PATH")
    coverage_parser.add_argument("--conformance", action="append", default=[], metavar="PATH")
    coverage_parser.add_argument("--transition", action="append", default=[], metavar="PATH")
    _add_format_argument(coverage_parser)

    return {'coverage_parser': coverage_parser}


def _register_check(subparsers):
    check_parser = subparsers.add_parser(
        "check",
        help="check a population against a model, or a walk between two populations",
        description=(
            "Two arms, and exactly one runs. SNAPSHOT: a positional population is "
            "checked against the model's constraints. TRANSITION: --pre, --steps "
            "and --post audit a WALK -- the operation invocations claimed to have "
            "carried the pre-population to the post-population -- reporting failed "
            "preconditions, undeclared side effects and illegal intermediate "
            "states. Mixing the two, or supplying part of the transition triple, "
            "is a usage error at 64: they answer different questions, and "
            "silently preferring one would make the other's arguments decorative. "
            "Model version 3 supports guarded Date plus/minus Duration calendar-day "
            "terms (date_add/date_sub), selecting report v11; --admission selects temporal report v13."
        ),
    )
    check_parser.add_argument(
        "model",
        help="path to the model file",
    )
    # nargs="?" so the transition arm can omit it. The parser therefore cannot
    # enforce "one arm or the other" itself -- that check lives in the dispatch,
    # routed back through parser.error so it exits 64 with no payload like every
    # other malformed invocation.
    check_parser.add_argument(
        "population",
        nargs="?",
        help="path to the population file (YAML or JSON) -- the snapshot arm",
    )
    check_parser.add_argument(
        "--populations",
        help="batch arm: directory of sorted .json/.yaml/.yml population projections",
    )
    check_parser.add_argument(
        "--pre",
        help="transition arm: the population the walk starts from",
    )
    check_parser.add_argument(
        "--steps",
        help="transition arm: the steps.json document describing the walk",
    )
    check_parser.add_argument(
        "--post",
        help="transition arm: the population the walk is claimed to end in",
    )
    check_parser.add_argument(
        '--compiled-operations', action='store_true',
        help='check eligible compiled standing subsets; excludes step/frame obligations',
    )
    check_parser.add_argument("--anchors", help="bound source anchor sidecar for snapshot checks")
    check_parser.add_argument("--document", help="source document for anchor spans")
    check_parser.add_argument(
        "--admission",
        action="store_true",
        help="include the occurrence admission partition in the check report",
    )
    _add_format_argument(check_parser)
    _add_unredacted_argument(check_parser)

    return {'check_parser': check_parser}


def _register_verbalize(subparsers):
    verbalize_parser = subparsers.add_parser(
        "verbalize",
        help="render supplied facts as deterministic sentences",
    )
    verbalize_targets = verbalize_parser.add_subparsers(dest="verbalize_target", required=True)
    verbalize_population_parser = verbalize_targets.add_parser(
        "population",
        help="render one population in text or JSONL",
    )
    verbalize_population_parser.add_argument("model")
    verbalize_population_parser.add_argument("population")
    verbalize_population_parser.add_argument("--anchors")
    verbalize_population_parser.add_argument("--document")
    verbalize_population_parser.add_argument("--format", choices=("text", "jsonl"), default="text")
    _add_unredacted_argument(verbalize_population_parser)

    return {'verbalize_parser': verbalize_parser, 'verbalize_population_parser': verbalize_population_parser}


def add_parsers(subparsers, *, command: str | None = None):
    parsers = {}
    if command is None or command == 'import':
        selected = _register_import(subparsers)
        parsers.update(selected)
        selected['import_parser'].set_defaults(handler=lambda args, selected=selected: handle(args, selected))
    if command is None or command == 'validate':
        selected = _register_validate(subparsers)
        parsers.update(selected)
        selected['validate_parser'].set_defaults(handler=lambda args, selected=selected: handle(args, selected))
    if command is None or command == 'diff':
        selected = _register_diff(subparsers)
        parsers.update(selected)
        selected['diff_parser'].set_defaults(handler=lambda args, selected=selected: handle(args, selected))
    if command is None or command == 'coverage':
        selected = _register_coverage(subparsers)
        parsers.update(selected)
        selected['coverage_parser'].set_defaults(handler=lambda args, selected=selected: handle(args, selected))
    if command is None or command == 'check':
        selected = _register_check(subparsers)
        parsers.update(selected)
        selected['check_parser'].set_defaults(handler=lambda args, selected=selected: handle(args, selected))
    if command is None or command == 'verbalize':
        selected = _register_verbalize(subparsers)
        parsers.update(selected)
        selected['verbalize_parser'].set_defaults(handler=lambda args, selected=selected: handle(args, selected))
    if not parsers:
        raise ValueError(f"unsupported command: {command}")
    return parsers


def handle(args, parsers) -> int:
    check_parser = parsers.get('check_parser')
    rai_import_parser = parsers.get('rai_import_parser')
    verbalize_population_parser = parsers.get('verbalize_population_parser')
    if args.command == "diff":
        return _cmd_diff(
            args.model_a, args.model_b, args.populations, args.format, args.unredacted, args.seed
        )

    if args.command == "import" and args.import_command == "ilp-rules":
        from gnd.export.ilp_service import _cmd_import_ilp_rules

        return _cmd_import_ilp_rules(
            args.model, args.clauses, args.labels, args.reported_coverage,
            target=args.target, out=args.out, actor=args.actor,
            requested_at=args.requested_at, output_format=args.format,
        )

    if args.command == "import":
        source_artifact = args.source_artifact
        if source_artifact is None:
            supplied = args.model
            candidate = PurePosixPath(supplied)
            if (
                Path(supplied).is_absolute()
                or PureWindowsPath(supplied).is_absolute()
                or "\\" in supplied
                or any(part in {"", ".", ".."} for part in supplied.split("/"))
            ):
                rai_import_parser.error(
                    "an absolute or unstable MODEL path requires --source-artifact"
                )
            source_artifact = candidate.as_posix()
        return _cmd_rai_import(args.model, args.out, source_artifact, args.source_commit)

    if args.command == "verbalize":
        if (args.anchors is None) != (args.document is None):
            verbalize_population_parser.error("--anchors and --document must be supplied together")
        return _cmd_verbalize_population(
            args.model,
            args.population,
            args.format,
            anchors_path=args.anchors,
            document_path=args.document,
            unredacted=args.unredacted,
        )

    if args.command == "check":
        if (args.anchors is None) != (args.document is None):
            check_parser.error("--anchors and --document must be supplied together")
        if (args.anchors is not None or args.document is not None) and (
            args.populations is not None
            or args.pre is not None
            or args.steps is not None
            or args.post is not None
        ):
            check_parser.error("--anchors and --document apply only to snapshot checks")
        if args.compiled_operations and (args.admission or any(
            value is not None for value in (args.pre, args.steps, args.post)
        )):
            check_parser.error('--compiled-operations cannot be combined with admission or a walk')
        transition_arm = {"--pre": args.pre, "--steps": args.steps, "--post": args.post}
        supplied = {flag for flag, value in transition_arm.items() if value is not None}
        if args.populations is not None:
            if args.admission:
                check_parser.error("--admission applies only to snapshot checks")
            if args.population is not None or supplied:
                check_parser.error(
                    "--populations is a distinct batch arm; do not combine it with "
                    "a positional population or --pre/--steps/--post"
                )
            if args.format != "json":
                check_parser.error("--populations requires --format json")
            return _cmd_check_batch(args.model, args.populations, unredacted=args.unredacted,
                                    compiled_operations=args.compiled_operations)
        if supplied and args.population is not None:
            # Not a precedence question. A caller who wrote both asked two
            # questions in one command and is owed the error, not a guess.
            check_parser.error(
                "a positional population and the transition arm (--pre/--steps/--post) "
                "are different questions; supply one or the other"
            )
        plan_arm = supplied == {"--pre", "--steps"}
        if supplied and len(supplied) != len(transition_arm) and not plan_arm:
            missing = sorted(set(transition_arm) - supplied)
            check_parser.error(
                f"the transition arm needs --pre, --steps and --post; missing "
                f"{', '.join(missing)}. A partial triple is a typo, not a mode"
            )
        if not supplied and args.population is None:
            check_parser.error(
                "supply a population to check, or --pre/--steps/--post to audit a walk"
            )
        if supplied:
            if args.admission:
                check_parser.error("--admission applies only to snapshot checks")
            return _cmd_transition(
                args.model,
                args.pre,
                args.steps,
                args.post,
                args.format,
                unredacted=args.unredacted,
            )

    if args.command == "validate":
        return _cmd_validate(
            args.model,
            args.format,
            trace=args.trace,
            unredacted=args.unredacted,
        )

    if args.command == "coverage":
        return _cmd_coverage(
            args.model,
            args.experiments,
            args.check,
            args.verify,
            args.conformance,
            args.transition,
            args.format,
        )

    return _cmd_check(
        args.model,
        args.population,
        args.format,
        unredacted=args.unredacted,
        anchors_path=args.anchors,
        document_path=args.document,
        admission=args.admission,
        compiled_operations=args.compiled_operations,
    )

