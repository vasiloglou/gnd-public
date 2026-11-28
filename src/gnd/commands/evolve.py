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
    evolve_preview_parser.add_argument(
        "--policy",
        choices=("additive",),
        default=None,
        help="refuse operations outside the additive policy (see the evolution contract)",
    )
    evolve_preview_parser.add_argument(
        "--populated",
        action="append",
        default=None,
        metavar="FACT_TYPE",
        help="treat FACT_TYPE as populated under --policy additive; repeatable",
    )
    evolve_preview_parser.add_argument(
        "--shape-report",
        action="store_true",
        help="list existing fact types with the same role players as each added one (advice only)",
    )
    evolve_preview_parser.add_argument(
        "--operation-outcomes",
        action="store_true",
        help="name an outcome for every operation of the proposal (admitted, refused and why, or unassessed)",
    )
    evolve_preview_parser.add_argument(
        "--outcome-report",
        default=None,
        metavar="FILE",
        help="when the preview is refused, write every operation's outcome to FILE beneath ROOT; requires --operation-outcomes",
    )
    evolve_preview_parser.add_argument(
        "--check-population",
        default=None,
        metavar="FILE",
        help="check new or strengthened proposed deontic constraints on populated fact types against the population in FILE beneath ROOT; requires --policy additive",
    )
    evolve_preview_parser.add_argument(
        '--previous-include', action='append', default=None, metavar='ID=PATH',
        help='authenticate old bytes for a repinned include from PATH beneath ROOT; repeatable',
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
    evolve_apply_parser.add_argument(
        "--policy",
        choices=("additive",),
        default=None,
        help="refuse operations outside the additive policy (see the evolution contract)",
    )
    evolve_apply_parser.add_argument(
        "--populated",
        action="append",
        default=None,
        metavar="FACT_TYPE",
        help="treat FACT_TYPE as populated under --policy additive; repeatable",
    )
    evolve_apply_parser.add_argument(
        "--check-population",
        default=None,
        metavar="FILE",
        help="repeat the reviewed preview's --check-population FILE beneath ROOT",
    )
    for parser in (evolve_preview_parser, evolve_apply_parser):
        parser.add_argument("--sample-document", action="append", metavar="FILE",
                            help="verify newly appended sample rows against this workspace document; repeatable")
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

    evolve_summary_parser = evolve_subparsers.add_parser(
        "summary",
        help="print one JSON summary of a growth round",
        description=(
            "Read the host's ROUND_FILE and, when the round produced them, its "
            "proposal, its preview or outcome report, and the evolution record "
            "of the applied round; print one gnd-round-summary JSON document. "
            "Each artifact must bind the one before it. Writes no file."
        ),
    )
    evolve_summary_parser.add_argument("round_file", metavar="ROUND_FILE", help="the host's gnd-round JSON file")
    evolve_summary_parser.add_argument("--proposal", metavar="FILE", help="the round's evolution proposal")
    evolve_summary_artifact = evolve_summary_parser.add_mutually_exclusive_group()
    evolve_summary_artifact.add_argument("--preview", metavar="FILE", help="the round's preview")
    evolve_summary_artifact.add_argument(
        "--outcome-report", metavar="FILE", help="the outcome report of the round's refused preview"
    )
    evolve_summary_parser.add_argument(
        "--record", metavar="FILE", help="the evolution record of the applied round; requires --preview"
    )

    return {'evolve_apply_parser': evolve_apply_parser, 'evolve_finalize_parser': evolve_finalize_parser, 'evolve_parser': evolve_parser, 'evolve_preview_parser': evolve_preview_parser, 'evolve_summary_parser': evolve_summary_parser}


def add_parsers(subparsers, *, command: str | None = None):
    parsers = {}
    if command is None or command == 'evolve':
        selected = _register_evolve(subparsers)
        parsers.update(selected)
        selected['evolve_parser'].set_defaults(handler=lambda args, selected=selected: handle(args, selected))
    if not parsers:
        raise ValueError(f"unsupported command: {command}")
    return parsers


@_handler_evolve_cli_service.parse_scoped  # GO1 (#228): one command parses each model text once per reader
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
                policy=args.policy,
                populated=args.populated,
                shape_report=args.shape_report,
                check_population=args.check_population,
                sample_documents=args.sample_document or (),
                previous_include=args.previous_include,
                operation_outcomes=args.operation_outcomes,
                outcome_report=args.outcome_report,
            )
        if args.evolve_command == "apply":
            return _handler_evolve_cli_service._cmd_evolve_apply(
                args.model,
                args.proposal,
                args.preview,
                args.workspace,
                args.records,
                args.format,
                policy=args.policy,
                populated=args.populated,
                check_population=args.check_population,
                sample_documents=args.sample_document or (),
            )
        if args.evolve_command == "summary":
            return _handler_evolve_cli_service._cmd_evolve_summary(
                args.round_file,
                proposal=args.proposal,
                preview=args.preview,
                outcome_report=args.outcome_report,
                record=args.record,
            )
        return _handler_evolve_cli_service._cmd_evolve_finalize(
            args.model,
            args.pending,
            args.workspace,
            args.records,
            args.format,
        )

    raise ValueError(f"unsupported command: {args.command}")

