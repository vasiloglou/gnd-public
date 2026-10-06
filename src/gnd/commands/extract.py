from __future__ import annotations

import gnd.extract.service as _handler_extract_service


def _register_extract(subparsers):
    extract_parser = subparsers.add_parser(
        "extract",
        help="emit the per-model extraction artifact bundle (VER-01, DATA-02)",
        description=(
            "Derive the per-model extraction artifacts OFFLINE from "
            "model.orm.yaml: <stem>.projection.schema.json (the closed, "
            "shape-only structured-output projection, gated by a recursive "
            "allowlist that fails closed on unlisted keywords), "
            "<stem>.verbalization.txt (the constraint-blind rendering seed), "
            "<stem>.applicable.json (the three-path reference-scheme "
            "applicable set) and <stem>.artifacts.json (sha256 digests plus "
            "the header_template the executing skill copies verbatim). No "
            "provider is called and no network is touched — the executing "
            "agent running the gnd-extract skill is the only place a model "
            "is ever called. Exits 0 when the bundle is emitted, 3 when the "
            "model is invalid, 64 on usage errors, 70 when the projection "
            "gate refuses gnd's own emitter (an internal invariant breach), "
            "74 when the output path is refused or unwritable."
        ),
    )
    extract_parser.add_argument("model", help="path to the model file")
    extract_parser.add_argument(
        "--out", required=True, help="output directory for the four-file bundle"
    )

    return {'extract_parser': extract_parser}


def add_parsers(subparsers, *, command: str | None = None):
    parsers = {}
    if command is None or command == 'extract':
        selected = _register_extract(subparsers)
        parsers.update(selected)
        selected['extract_parser'].set_defaults(handler=lambda args, selected=selected: handle(args, selected))
    if not parsers:
        raise ValueError(f"unsupported command: {command}")
    return parsers


def handle(args, parsers) -> int:
    if args.command == "extract":
        return _handler_extract_service._cmd_extract(args.model, args.out)

    raise ValueError(f"unsupported command: {args.command}")

