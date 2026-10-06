from __future__ import annotations

import argparse

from gnd.commands._arguments import _positive_finite_float, _positive_int
from gnd.review.service import _repository_relative_path


def _add_review_panel_arguments(parser: argparse.ArgumentParser) -> None:
    """Attach the one shared request/output/bounds surface to a panel command."""

    parser.add_argument(
        "request",
        type=_repository_relative_path,
        help=(
            "repository-relative path to the review request JSON (kind plan, "
            "experiment-outcome, or spec-results-delta), resolved against the "
            "current directory"
        ),
    )
    parser.add_argument(
        "--out",
        required=True,
        help="directory to publish immutable panel evidence into; it must not exist",
    )
    parser.add_argument(
        "--reviewer-timeout",
        type=_positive_finite_float,
        default=600.0,
        help="positive finite per-reviewer wall-clock bound in seconds (default: 600)",
    )
    parser.add_argument(
        "--overall-timeout",
        type=_positive_finite_float,
        default=900.0,
        help="positive finite whole-panel wall-clock bound in seconds (default: 900)",
    )
    parser.add_argument(
        "--max-output-bytes",
        type=_positive_int,
        default=536_870_912,
        help=(
            "positive retained byte cap per reviewer stream; the whole-panel "
            "aggregate is twice this value (default: 536870912 -- effectively "
            "uncapped; pass a smaller value to bound a run)"
        ),
    )

_add_review_panel_arguments.__module__ = "gnd.cli"

import gnd.review.service as _handler_review_service


def _register_review(subparsers):
    review_parser = subparsers.add_parser(
        "review",
        help="run the bounded six-reviewer advisory panel and finalize its synthesis (REV-01)",
        description=(
            "Advisory multi-CLI review over ONE of exactly three input classes — "
            "a plan, an experiment outcome, or a spec/results/delta bundle. GND "
            "attempts six reviewer seats over five installed terminal-agent CLIs "
            "(claude, codex, qwen, gemini, kimi, plus a glm seat that runs the "
            "claude CLI against Z.AI's Anthropic-compatible endpoint) through "
            "fixed Python-owned invocation argv and bounded "
            "prompt transport (stdin for five, one --prompt argv element for Kimi), "
            "keeps one closed envelope "
            "per reviewer including "
            "every timeout, authentication failure, missing executable and "
            "unparseable response, and requires three DISTINCT schema-valid "
            "successes before any panel result may be reported. Every reviewer "
            "must first return substantive help that documents every long flag in "
            "the invocation GND is about to send; an incompatible reviewer is never "
            "invoked. GND does not sandbox reviewer CLIs or enforce read-only "
            "execution. It verifies the reviewed artifacts are unchanged before "
            "publishing a run. The panel ships no provider SDK and sources no "
            "credentials."
        ),
    )
    review_subparsers = review_parser.add_subparsers(dest="review_command", required=True)

    review_panel_parser = review_subparsers.add_parser(
        "panel",
        help="attempt all six reviewers and publish one immutable evidence directory",
        description=(
            "Load and digest-bind a review request, attempt all six reviewers "
            "concurrently under one shared deadline, and publish the normalized "
            "request, four raw streams and one closed envelope per reviewer, "
            "every validated response, and a manifest-last run.json into a "
            "directory that must not already exist. REQUEST and every artifact "
            "it names are repository-relative paths resolved against the "
            "directory you are standing in. Every bound must be strictly "
            "positive and is validated BEFORE any process is spawned; each "
            "reviewer's deadline is the earlier of --reviewer-timeout and the "
            "remaining --overall-timeout. Prints one closed JSON summary and "
            "never a verdict, a rate, or a conformance result. Exits 0 when at "
            "least three distinct reviewers returned schema-valid responses, 16 "
            "when all six attempts completed and fewer than three did, 3 when "
            "the request or a reviewer-cited artifact is ill-formed, 11 when the "
            "output directory already exists (nothing was written and no "
            "reviewer was invoked), 64 on usage errors including a non-positive "
            "bound, 66 when the request or a reviewed artifact is missing, 70 on "
            "an internal defect, 74 on refused or failed path/IO."
        ),
    )
    _add_review_panel_arguments(review_panel_parser)

    review_panel_light_parser = review_subparsers.add_parser(
        "panel-light",
        help="run the same panel at high or medium supported per-run effort",
        description=(
            "Run the same bounded six-reviewer advisory panel and publish the "
            "same immutable evidence as `gnd review panel`, but request a lighter "
            "supported per-run effort from Claude and Codex. The default is high; "
            "--effort medium is the only alternative. Qwen uses persistent effort "
            "configuration, and Gemini, Kimi, and the GLM seat expose no per-run "
            "effort flag, so "
            "their invocation policies and models are unchanged. All request, "
            "quorum, deadline, evidence, exit-band, and no-sandbox rules are "
            "identical to the quality-first panel."
        ),
    )
    _add_review_panel_arguments(review_panel_light_parser)
    review_panel_light_parser.add_argument(
        "--effort",
        choices=("high", "medium"),
        default="high",
        help="supported per-run effort for Claude and Codex (default: high)",
    )

    review_finalize_parser = review_subparsers.add_parser(
        "finalize",
        help="validate a semantic synthesis against immutable run evidence and render it",
        description=(
            "Take one immutable panel RUN directory and one closed SYNTHESIS "
            "document — the semantic grouping an agent authored over the "
            "successful responses — and prove it before rendering: the synthesis "
            "must bind the run by digest, account for every retained concern "
            "exactly once, give every agreed concern at least two DISTINCT "
            "successful supporting reviewers, keep every evidence-backed "
            "singleton under divergent views, and trace every prioritized fix to "
            "the complete supporter and evidence set of each group it touches. "
            "Reviewer quorum (three) and concern agreement (two) are different "
            "thresholds and neither substitutes for the other. Nothing in a "
            "reviewed artifact is ever written, no fix is applied, and an "
            "existing report is never replaced. Exits 0 when the report is "
            "rendered, 16 when the run itself is below quorum, 3 when the run "
            "evidence or the synthesis fails closed validation, 11 when the "
            "report path already exists, 64 on usage errors, 66 when the run "
            "directory or the synthesis is missing, 74 on refused or failed "
            "path/IO."
        ),
    )
    review_finalize_parser.add_argument(
        "run", help="the immutable panel run directory published by gnd review panel"
    )
    review_finalize_parser.add_argument(
        "synthesis", help="the closed semantic synthesis JSON authored over that run"
    )
    review_finalize_parser.add_argument(
        "--out",
        required=True,
        help="path to write PANEL-REVIEW.md; an existing file is never replaced",
    )

    return {'review_finalize_parser': review_finalize_parser, 'review_panel_light_parser': review_panel_light_parser, 'review_panel_parser': review_panel_parser, 'review_parser': review_parser}


def add_parsers(subparsers, *, command: str | None = None):
    parsers = {}
    if command is None or command == 'review':
        selected = _register_review(subparsers)
        parsers.update(selected)
        selected['review_parser'].set_defaults(handler=lambda args, selected=selected: handle(args, selected))
    if not parsers:
        raise ValueError(f"unsupported command: {command}")
    return parsers


def handle(args, parsers) -> int:
    review_panel_light_parser = parsers.get('review_panel_light_parser')
    review_panel_parser = parsers.get('review_panel_parser')
    if args.command == "review":
        if args.review_command in {"panel", "panel-light"}:
            # The aggregate is twice the per-stream cap, so a per-stream request
            # above half the module's hard ceiling is a malformed INVOCATION
            # (64) rather than a runtime failure after five processes have run.
            from gnd.review.runner import MAX_REVIEW_STREAM_BYTES

            if args.max_output_bytes * 2 > MAX_REVIEW_STREAM_BYTES:
                panel_parser = (
                    review_panel_parser
                    if args.review_command == "panel"
                    else review_panel_light_parser
                )
                panel_parser.error(
                    f"--max-output-bytes must be at most "
                    f"{MAX_REVIEW_STREAM_BYTES // 2}; the whole-panel aggregate "
                    f"is twice the per-stream cap and may not exceed "
                    f"{MAX_REVIEW_STREAM_BYTES} bytes"
                )
            return _handler_review_service._cmd_review_panel(
                args.request,
                args.out,
                args.reviewer_timeout,
                args.overall_timeout,
                args.max_output_bytes,
                reviewer_effort=("xhigh" if args.review_command == "panel" else args.effort),
                command_name=f"review {args.review_command}",
            )
        return _handler_review_service._cmd_review_finalize(args.run, args.synthesis, args.out)

    raise ValueError(f"unsupported command: {args.command}")

