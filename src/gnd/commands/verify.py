from __future__ import annotations

import gnd.export.verification_service as _handler_export_verification_service
from gnd.commands._arguments import _add_format_argument, _add_unredacted_argument


def _register_verify(subparsers):
    verify_parser = subparsers.add_parser(
        "verify",
        help="run the full derived verifier over a pre-extracted population (VER-01, VER-02)",
        description=(
            "Run the full derived verifier: popvalidate then check over a "
            "PRE-EXTRACTED population file. This command never calls a model "
            "and never orchestrates extraction (R-03''): the executing agent "
            "running the gnd-extract skill writes the population and its "
            "<population>.extraction.json sidecar, and verify validates the "
            "handoff before composing the checker. Exit bands are REUSED "
            "unchanged with precedence 3 > 1 > 4 > 2 > 0: 3 ill-formed "
            "(including an ill-formed extraction handoff), 1 alethic fail, 4 "
            "indeterminate, 2 vacuous, 0 pass. The payload's extraction block "
            "carries the machine-readable state (ran | skipped | failed + "
            "reason); a missing sidecar is extraction:sidecar-missing, a "
            "malformed one extraction:sidecar-invalid, and a digest that does "
            "not match the file bytes extraction:binding-mismatch — all exit "
            "3, state failed. skipped is written ONLY by --no-extraction. "
            "Never a fidelity rate in this payload: a checker pass over an "
            "uncalibrated extraction is checker acceptance, not proof of "
            "faithfulness."
        ),
    )
    verify_parser.add_argument("model", help="path to the model file")
    verify_parser.add_argument(
        "population", help="path to the PRE-EXTRACTED population file (YAML or JSON)"
    )
    verify_parser.add_argument(
        "--sidecar",
        default=None,
        help=(
            "path to the extraction sidecar (default: the population path with "
            "an .extraction.json suffix, beside the population)"
        ),
    )
    verify_parser.add_argument(
        "--artifacts",
        default=None,
        help=(
            "directory containing the model's extraction bundle; required on "
            "the extraction path so projection_sha256 is verified"
        ),
    )
    verify_parser.add_argument(
        "--no-extraction",
        dest="no_extraction",
        action="store_true",
        help=(
            "the INTENTIONAL opt-out: check a population that was not produced "
            "by an extraction; records extraction.state=skipped with the reason"
        ),
    )
    verify_parser.add_argument(
        "--out",
        default=None,
        help="also write the JSON payload to this path (from argv only)",
    )
    _add_format_argument(verify_parser)
    _add_unredacted_argument(verify_parser)

    return {'verify_parser': verify_parser}


def add_parsers(subparsers, *, command: str | None = None):
    parsers = {}
    if command is None or command == 'verify':
        selected = _register_verify(subparsers)
        parsers.update(selected)
        selected['verify_parser'].set_defaults(handler=lambda args, selected=selected: handle(args, selected))
    if not parsers:
        raise ValueError(f"unsupported command: {command}")
    return parsers


def handle(args, parsers) -> int:
    verify_parser = parsers.get('verify_parser')
    if args.command == "verify":
        if args.no_extraction and args.sidecar is not None:
            # A usage contradiction, not a verdict: --sidecar names a handoff
            # to validate while --no-extraction opts out of extraction
            # entirely. Routed through the parser so it exits 64 with no
            # payload, exactly like every other malformed invocation (WR-03).
            verify_parser.error(
                "--sidecar and --no-extraction are contradictory: --sidecar "
                "names an extraction handoff to validate, --no-extraction "
                "declares there was none"
            )
        return _handler_export_verification_service._cmd_verify(
            args.model,
            args.population,
            args.sidecar,
            args.artifacts,
            args.no_extraction,
            args.out,
            args.format,
            unredacted=args.unredacted,
        )

    raise ValueError(f"unsupported command: {args.command}")

