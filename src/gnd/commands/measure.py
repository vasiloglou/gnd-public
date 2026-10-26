from __future__ import annotations

import gnd.measure.service as _handler_measure_service
from gnd.commands._arguments import _add_format_argument, _add_unredacted_argument


def _register_measure(subparsers):
    measure_parser = subparsers.add_parser(
        "measure",
        help="measure per-constraint false-pass/false-fail/undecided rates (VER-03)",
        description=(
            "Measure the checker's per-constraint false-pass, false-fail and "
            "undecided rates over labelled synthetic populations. Reads the "
            "populations `gnd synth` wrote and their provenance sidecars, verifies "
            "the C6 sidecar binding before scoring, and emits a per-constraint "
            "report — three rates, each with its numerator AND its conditional "
            "denominator (C2), never a blended accuracy number (D-01). Computed "
            "OFFLINE from committed artifacts: no timestamp, so two runs over one "
            "corpus reproduce byte-for-byte. Exits 3 on a sidecar-binding "
            "mismatch, 5 on a population that fails to load, 6 on a checker defect "
            "(C9), 64 on a corpus mixing models or pool sources (C4)."
        ),
    )
    measure_parser.add_argument("model", help="path to the model file")
    measure_parser.add_argument(
        "--promote",
        default=None,
        metavar="DIR",
        help=(
            "D-14: copy each defect-revealing population and its model into DIR (the "
            "adversarial corpus root) and PRINT manifest rows in the locked record "
            "shape. The append itself stays a reviewed act — this never edits "
            "manifest.yaml"
        ),
    )
    # Exactly one of --populations / --labels, enforced in handle(): an argparse
    # mutually exclusive group renders its usage differently across Python minors.
    measure_parser.add_argument(
        "--populations",
        default=None,
        help="output root of a `gnd synth` run (the directory holding index.json)",
    )
    measure_parser.add_argument(
        "--labels",
        default=None,
        metavar="MANIFEST",
        help=(
            "IK3: a gnd-labels/1 manifest of host-labelled populations, instead of "
            "--populations. Expected-state mode emits report schema 4 (exit 6 on a "
            "checker defect); class mode emits schema 5 agreement cells (exit 0). "
            "See docs/reference/measure-labels.md"
        ),
    )
    measure_parser.add_argument(
        "--out", default=None, help="write the JSON payload to this path (default: stdout)"
    )
    _add_format_argument(measure_parser)
    _add_unredacted_argument(measure_parser)

    return {'measure_parser': measure_parser}


def add_parsers(subparsers, *, command: str | None = None):
    parsers = {}
    if command is None or command == 'measure':
        selected = _register_measure(subparsers)
        parsers.update(selected)
        selected['measure_parser'].set_defaults(handler=lambda args, selected=selected: handle(args, selected))
    if not parsers:
        raise ValueError(f"unsupported command: {command}")
    return parsers


def handle(args, parsers) -> int:
    if args.command == "measure":
        if (args.labels is None) == (args.populations is None):
            parsers["measure_parser"].error("exactly one of --populations or --labels is required")
        if args.labels is not None and args.promote is not None:
            parsers["measure_parser"].error("--promote needs --populations: host labels have no sidecars")
        if args.labels is not None:
            return _handler_measure_service._measure_labels(
                args.model, args.labels, args.format, args.out, unredacted=args.unredacted
            )
        return _handler_measure_service._cmd_measure(
            args.model,
            args.populations,
            args.format,
            args.out,
            args.promote,
            unredacted=args.unredacted,
        )

    raise ValueError(f"unsupported command: {args.command}")

