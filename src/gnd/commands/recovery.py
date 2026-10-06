from __future__ import annotations

import gnd.recovery.service as _handler_recovery_service
from gnd.commands._arguments import _positive_int


def _register_recovery(subparsers):
    recovery_parser = subparsers.add_parser(
        "recovery",
        help="inventory static code evidence and verify one recovered model bundle",
        description=(
            "Run the one-time, execution-free recovery boundary. Inventory reads only "
            "explicit categorized roots under ROOT with closed byte/file limits and "
            "writes one immutable JSON census. Verify re-resolves the canonical model, "
            "full verbalization, report, evidence digests, typed locators, and exact "
            "selected-path census. Neither command imports or executes repository code, "
            "launches an agent, invokes conformance, or generates code. Exits 3 for an "
            "ill-formed inventory/report or failed digest/locator claim, 66 when a "
            "required input is missing, and 74 for refused or unreadable paths and I/O."
        ),
    )
    recovery_subparsers = recovery_parser.add_subparsers(
        dest="recovery_command",
        required=True,
    )
    recovery_inventory_parser = recovery_subparsers.add_parser(
        "inventory",
        help="write one bounded closed census of explicit static repository roots",
        description=(
            "Read explicitly selected source, test, documentation, configuration, and "
            "schema roots as inert bytes. Every selected path is classified as parsed, "
            "excluded, ambiguous, or frontier; source text is never copied into the "
            "inventory. --exclude uses REASON=PATH where REASON is dependency, vendored, "
            "generated, cache, build, or sensitive-tree. The output is write-once. "
            "Exits 3 for an empty/malformed scope, 66 for a missing root, and 74 for an "
            "unsafe/unreadable path or refused output."
        ),
    )
    recovery_inventory_parser.add_argument(
        "root",
        metavar="ROOT",
        help="authoritative existing repository root",
    )
    for option, destination, label in (
        ("--source", "sources", "source"),
        ("--tests", "tests", "test"),
        ("--docs", "docs", "documentation"),
        ("--config", "configs", "configuration"),
        ("--schema", "schemas", "schema"),
    ):
        recovery_inventory_parser.add_argument(
            option,
            dest=destination,
            action="append",
            default=[],
            metavar="PATH",
            help=f"repository-relative {label} root (repeatable)",
        )
    recovery_inventory_parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        metavar="REASON=PATH",
        help="closed exclusion reason and repository-relative path (repeatable)",
    )
    recovery_inventory_parser.add_argument(
        "--max-file-bytes",
        type=_positive_int,
        default=2 * 1024 * 1024,
        help="maximum bytes read from one selected file (default: 2097152)",
    )
    recovery_inventory_parser.add_argument(
        "--max-total-bytes",
        type=_positive_int,
        default=32 * 1024 * 1024,
        help="maximum aggregate bytes read from selected files (default: 33554432)",
    )
    recovery_inventory_parser.add_argument(
        "--max-files",
        type=_positive_int,
        default=10_000,
        help="maximum selected file observations (default: 10000)",
    )
    recovery_inventory_parser.add_argument(
        "--out",
        required=True,
        metavar="INVENTORY.json",
        help="write-once inventory JSON destination beneath ROOT",
    )

    recovery_verify_parser = recovery_subparsers.add_parser(
        "verify",
        help="verify the canonical three-artifact recovery bundle and every claim",
        description=(
            "Verify REPORT beneath authoritative ROOT, together with its explicit "
            "canonical sibling model and full verbalization. All leaves are no-follow "
            "regular files; the runtime reloads the model, reproduces the complete "
            "verbalization, resolves every evidence locator, and re-inventories the "
            "selected roots. Exits 3 for malformed/stale evidence, 66 for a missing "
            "artifact, and 74 for unsafe/unreadable paths or I/O."
        ),
    )
    recovery_verify_parser.add_argument(
        "root",
        metavar="ROOT",
        help="authoritative existing recovery bundle/repository root",
    )
    recovery_verify_parser.add_argument(
        "report",
        metavar="REPORT",
        help="explicit canonical model.recovery.json beneath ROOT",
    )
    recovery_verify_parser.add_argument(
        "--model",
        default="model.orm.yaml",
        metavar="MODEL",
        help="explicit recovered model sibling (default: model.orm.yaml)",
    )
    recovery_verify_parser.add_argument(
        "--verbalization",
        default="model.verbalization.txt",
        metavar="VERBALIZATION",
        help="explicit full verbalization sibling (default: model.verbalization.txt)",
    )

    return {'recovery_inventory_parser': recovery_inventory_parser, 'recovery_parser': recovery_parser, 'recovery_verify_parser': recovery_verify_parser}


def add_parsers(subparsers, *, command: str | None = None):
    parsers = {}
    if command is None or command == 'recovery':
        selected = _register_recovery(subparsers)
        parsers.update(selected)
        selected['recovery_parser'].set_defaults(handler=lambda args, selected=selected: handle(args, selected))
    if not parsers:
        raise ValueError(f"unsupported command: {command}")
    return parsers


def handle(args, parsers) -> int:
    if args.command == "recovery":
        if args.recovery_command == "inventory":
            return _handler_recovery_service._cmd_recovery_inventory(
                args.root,
                args.sources,
                args.tests,
                args.docs,
                args.configs,
                args.schemas,
                args.exclude,
                args.max_file_bytes,
                args.max_total_bytes,
                args.max_files,
                args.out,
            )
        return _handler_recovery_service._cmd_recovery_verify(
            args.root,
            args.report,
            args.model,
            args.verbalization,
        )

    raise ValueError(f"unsupported command: {args.command}")

