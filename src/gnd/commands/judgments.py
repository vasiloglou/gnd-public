from __future__ import annotations


def _register_judgments(subparsers):
    judgment_parser = subparsers.add_parser("judgments", help="evaluate saved external opinions")
    judgment_sub = judgment_parser.add_subparsers(dest="judgment_command", required=True)
    judgment_check = judgment_sub.add_parser(
        "check", help="check saved receipts and confidence floors"
    )
    judgment_check.add_argument("model")
    judgment_check.add_argument("population")
    for name in ("policy", "receipts", "trusted-root"):
        judgment_check.add_argument("--" + name, required=True)
    judgment_check.add_argument("--reference-root")
    judgment_check.add_argument("--unredacted", action="store_true")
    judgment_check.add_argument("--format", choices=("json", "text"), default="text")

    return {'judgment_check': judgment_check, 'judgment_parser': judgment_parser}


def add_parsers(subparsers, *, command: str | None = None):
    parsers = {}
    if command is None or command == 'judgments':
        selected = _register_judgments(subparsers)
        parsers.update(selected)
        selected['judgment_parser'].set_defaults(handler=lambda args, selected=selected: handle(args, selected))
    if not parsers:
        raise ValueError(f"unsupported command: {command}")
    return parsers


def handle(args, parsers) -> int:
    if args.command == "judgments":
        from gnd.api import judgments
        from gnd.artifacts import canonical_json_bytes

        result = judgments(
            args.model,
            args.population,
            args.policy,
            args.receipts,
            trusted_root=args.trusted_root,
            reference_root=args.reference_root,
            unredacted=args.unredacted,
        )
        print(
            canonical_json_bytes(result, exact_numbers=True).decode()
            if args.format == "json"
            else "saved judgment outcome: " + str(result["outcome"])
        )
        return result["outcome"]

    raise ValueError(f"unsupported command: {args.command}")

