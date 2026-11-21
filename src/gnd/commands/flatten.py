from __future__ import annotations


def _register_flatten(subparsers):
    flatten_parser = subparsers.add_parser(
        "flatten",
        help="write an include root's flat model and its record",
        description=(
            "Resolve a version-5 model's includes, as gnd check does, and write "
            "<stem>.flat.orm.json and <stem>.flattening.json (gnd-flattening/1) "
            "into --out, both files or neither. Temporal models are accepted. "
            "Reference paths in the flat model stay relative to the root model's "
            "directory. Exits 0 when both files are written, 3 when the model is "
            "invalid, declares no includes or an include is refused, 11 when "
            "either output file already exists (nothing is written), 64 on usage "
            "errors, 66 when the model is missing, 74 when the output path is "
            "refused or unwritable."
        ),
    )
    flatten_parser.add_argument("model", help="path to the include root")
    flatten_parser.add_argument("--out", required=True, help="output directory")
    flatten_parser.add_argument("--format", choices=("text", "json"), default="text")
    return {"flatten_parser": flatten_parser}


def add_parsers(subparsers, *, command: str | None = None):
    parsers = {}
    if command is None or command == "flatten":
        selected = _register_flatten(subparsers)
        parsers.update(selected)
        selected["flatten_parser"].set_defaults(
            handler=lambda args, selected=selected: handle(args, selected))
    if not parsers:
        raise ValueError(f"unsupported command: {command}")
    return parsers


def handle(args, parsers) -> int:
    if args.command == "flatten":
        from gnd.extract.flatten_service import flatten_to

        return flatten_to(args.model, args.out, output_format=args.format)
    raise ValueError(f"unsupported command: {args.command}")
