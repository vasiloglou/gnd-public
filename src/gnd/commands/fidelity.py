from __future__ import annotations

import gnd.fidelity.service as _handler_fidelity_service
from gnd.commands._arguments import _add_format_argument


def _register_fidelity(subparsers):
    fidelity_parser = subparsers.add_parser(
        "fidelity",
        help="measure extractor fidelity per fact type over committed cases (DATA-02)",
        description=(
            "Measure the EXTRACTOR, per fact type, over committed case "
            "directories. This command emits RATES and never a per-run verdict "
            "— it is the dual of `gnd verify`, which emits verdicts and never a "
            "rate: a checker pass over an uncalibrated extraction is not "
            "evidence of faithfulness. Matching is by the model's own reference "
            "scheme under a LEXICAL-only normalization, multiset (tp per "
            "identity key is min(source_count, extracted_count)), with INCLUSIVE "
            "precision (unresolved and ambiguous extractions stay in the "
            "denominator) and `ambiguous` as an explicit outcome for "
            "normalization collisions and broken composite identities — never "
            "an arbitrary match. Every rate ships with its numerator AND "
            "denominator, no figure blends fact types, and the payload is "
            "schema-REQUIRED to report calibration.state 'uncalibrated' and "
            "publishable false: the round trip measures the round trip, and "
            "while the calibration set is deferred no interval field may exist "
            "at all. Fully offline over committed artifacts. Exits 0 with the "
            "report, 3 on a digest binding mismatch inside a case, 64 on usage "
            "errors or a case set spanning more than one model, 66 when a "
            "required extraction artifact is missing (fail closed — a missing "
            "applicable set must not read as coverage), 70 on an internal "
            "contract breach, 74 when the output path is refused."
        ),
    )
    fidelity_parser.add_argument("model", help="path to the model file")
    fidelity_parser.add_argument(
        "--cases",
        required=True,
        help=(
            "directory of case directories, each carrying source.population.json, "
            "document.md, document.manifest.json, extracted.population.json and "
            "extracted.population.extraction.json (or extraction.skipped.json)"
        ),
    )
    fidelity_parser.add_argument(
        "--artifacts",
        required=True,
        help="the gnd extract bundle directory holding <stem>.applicable.json",
    )
    fidelity_parser.add_argument("--out", help="write the payload to this path")
    _add_format_argument(fidelity_parser)

    return {'fidelity_parser': fidelity_parser}


def add_parsers(subparsers, *, command: str | None = None):
    parsers = {}
    if command is None or command == 'fidelity':
        selected = _register_fidelity(subparsers)
        parsers.update(selected)
        selected['fidelity_parser'].set_defaults(handler=lambda args, selected=selected: handle(args, selected))
    if not parsers:
        raise ValueError(f"unsupported command: {command}")
    return parsers


def handle(args, parsers) -> int:
    if args.command == "fidelity":
        return _handler_fidelity_service._cmd_fidelity(args.model, args.cases, args.artifacts, args.out, args.format)

    raise ValueError(f"unsupported command: {args.command}")

