from __future__ import annotations

import gnd.evolve.cli_service as _handler_evolve_cli_service
from gnd.commands._arguments import _add_format_argument


def _register_evolve(subparsers):
    evolve_parser = subparsers.add_parser(
        "evolve",
        help="preview, apply, and finalize one digest-bound model evolution",
        description=(
            "Run the staged offline evolution protocol over explicit files. "
            "Preview validates without mutation; apply revalidates the exact "
            "reviewed preview, performs the model CAS, and completes the live "
            "conformance recheck in one invocation; finalize completes a "
            "pending state left behind by an interrupted apply. The CLI does "
            "not propose changes, repair projects, or select a runtime."
        ),
    )
    evolve_subparsers = evolve_parser.add_subparsers(
        dest="evolve_command",
        required=True,
    )
    evolve_preview_parser = evolve_subparsers.add_parser(
        "preview",
        help="validate a proposal and publish one immutable review claim",
        description=(
            "Read MODEL and PROPOSAL beneath the authoritative workspace, "
            "validate the candidate and blast radius, and write the complete "
            "digest-bound preview to PREVIEW without changing the model, "
            "verbalization, records, or linked projects."
        ),
    )
    evolve_preview_parser.add_argument("model", help="current model file beneath ROOT")
    evolve_preview_parser.add_argument(
        "proposal", help="closed evolution proposal JSON beneath ROOT"
    )
    evolve_preview_parser.add_argument(
        "--workspace",
        required=True,
        help="authoritative existing workspace ROOT",
    )
    evolve_preview_parser.add_argument(
        "--records",
        required=True,
        help="authoritative immutable evidence DIR",
    )
    evolve_preview_parser.add_argument(
        "--out",
        required=True,
        help="write-once PREVIEW JSON path beneath ROOT",
    )
    _add_format_argument(evolve_preview_parser)

    evolve_apply_parser = evolve_subparsers.add_parser(
        "apply",
        help="revalidate an exact preview and complete the whole evolution",
        description=(
            "Require PROPOSAL and PREVIEW to reproduce the current exact "
            "preview, obtain the exact blast-radius digest for a breaking "
            "proposal, publish the candidate model CAS and durable "
            "pending-finalization evidence, then complete the verbalization, "
            "live linked-project conformance, and final record in the same "
            "invocation. The exit is the raw aggregate conformance exit, so "
            "linked drift returns 13 with the model published and no rollback."
        ),
    )
    evolve_apply_parser.add_argument("model", help="current model file beneath ROOT")
    evolve_apply_parser.add_argument("proposal", help="closed evolution proposal JSON beneath ROOT")
    evolve_apply_parser.add_argument(
        "--preview",
        required=True,
        help="exact reviewed PREVIEW JSON beneath ROOT",
    )
    evolve_apply_parser.add_argument(
        "--workspace",
        required=True,
        help="authoritative existing workspace ROOT",
    )
    evolve_apply_parser.add_argument(
        "--records",
        required=True,
        help="authoritative immutable evidence DIR",
    )
    _add_format_argument(evolve_apply_parser)

    evolve_finalize_parser = evolve_subparsers.add_parser(
        "finalize",
        help="complete exact pending leaves and publish the final record last",
        description=(
            "Load one immutable PENDING identity, finish its exact "
            "verbalization and linked-project conformance leaves, and publish "
            "the final evolution record last. Linked drift remains exit 13 "
            "with its raw evidence; no rollback or regeneration occurs."
        ),
    )
    evolve_finalize_parser.add_argument("model", help="published model file beneath ROOT")
    evolve_finalize_parser.add_argument(
        "pending", help="immutable pending-finalization JSON beneath ROOT"
    )
    evolve_finalize_parser.add_argument(
        "--workspace",
        required=True,
        help="authoritative existing workspace ROOT",
    )
    evolve_finalize_parser.add_argument(
        "--records",
        required=True,
        help="authoritative immutable evidence DIR",
    )
    _add_format_argument(evolve_finalize_parser)

    return {'evolve_apply_parser': evolve_apply_parser, 'evolve_finalize_parser': evolve_finalize_parser, 'evolve_parser': evolve_parser, 'evolve_preview_parser': evolve_preview_parser}


def add_parsers(subparsers, *, command: str | None = None):
    parsers = {}
    if command is None or command == 'evolve':
        selected = _register_evolve(subparsers)
        parsers.update(selected)
        selected['evolve_parser'].set_defaults(handler=lambda args, selected=selected: handle(args, selected))
    if not parsers:
        raise ValueError(f"unsupported command: {command}")
    return parsers


def handle(args, parsers) -> int:
    if args.command == "evolve":
        if args.evolve_command == "preview":
            return _handler_evolve_cli_service._cmd_evolve_preview(
                args.model,
                args.proposal,
                args.workspace,
                args.records,
                args.out,
                args.format,
            )
        if args.evolve_command == "apply":
            return _handler_evolve_cli_service._cmd_evolve_apply(
                args.model,
                args.proposal,
                args.preview,
                args.workspace,
                args.records,
                args.format,
            )
        return _handler_evolve_cli_service._cmd_evolve_finalize(
            args.model,
            args.pending,
            args.workspace,
            args.records,
            args.format,
        )

    raise ValueError(f"unsupported command: {args.command}")

