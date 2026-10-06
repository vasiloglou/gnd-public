from __future__ import annotations

import argparse
import math
import sys

from gnd.exits import EXIT_USAGE

OUTPUT_FORMATS = ("text", "json")

class _BandSafeParser(argparse.ArgumentParser):
    """Usage errors exit 64 (EX_USAGE), not argparse's default 2 — exit 2 is
    the normative "vacuous population" band (WR-03)."""

    def error(self, message: str) -> None:  # type: ignore[override]
        self.print_usage(sys.stderr)
        print(f"{self.prog}: error: {message}", file=sys.stderr)
        raise SystemExit(EXIT_USAGE)

class _StoreOnce(argparse.Action):
    """Refuse a second occurrence of a single-valued flag.

    argparse's default is last-wins, which lets a user believe a bound was set
    that never was. A second occurrence is a user error, never a silent
    overwrite -- and it reaches 64 through _BandSafeParser.error like every other
    usage refusal.
    """

    def __call__(self, parser, namespace, values, option_string=None):  # type: ignore[no-untyped-def]
        if getattr(namespace, f"_seen_{self.dest}", False):
            parser.error(f"{option_string} may be given at most once")
        setattr(namespace, f"_seen_{self.dest}", True)
        setattr(namespace, self.dest, values)

def _positive_int(value: str) -> int:
    """Argparse converter for counts that must be strictly positive."""
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return parsed

def _positive_finite_float(value: str) -> float:
    """Argparse converter for positive finite wall-clock tightenings."""

    parsed = float(value)
    if parsed <= 0 or not math.isfinite(parsed):
        raise argparse.ArgumentTypeError("must be finite and greater than zero")
    return parsed

def _add_format_argument(parser: argparse.ArgumentParser) -> None:
    """--format on BOTH subcommands (D-10). An invalid choice is an argparse
    usage error, so _BandSafeParser routes it to exit 64 with no payload."""
    parser.add_argument(
        "--format",
        choices=OUTPUT_FORMATS,
        default="text",
        help="output rendering: human-readable text (default) or one JSON payload",
    )

def _add_unredacted_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--unredacted",
        action="store_true",
        help=argparse.SUPPRESS,
    )

_BandSafeParser.__module__ = "gnd.cli"
_StoreOnce.__module__ = "gnd.cli"
_positive_int.__module__ = "gnd.cli"
_positive_finite_float.__module__ = "gnd.cli"
_add_format_argument.__module__ = "gnd.cli"
_add_unredacted_argument.__module__ = "gnd.cli"
