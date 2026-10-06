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
