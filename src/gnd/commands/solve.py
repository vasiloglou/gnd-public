from __future__ import annotations

import argparse
import sys
from pathlib import Path

from gnd import solve
from gnd.exits import EXIT_USAGE


def _utf8_clean(value: str) -> bool:
    """Is this command-line string valid UTF-8?

    POSIX argv is decoded with surrogateescape, so bytes that were never valid
    UTF-8 survive as lone surrogates. They are refused at stage 1 rather than
    encoded: writing them with surrogatepass produces ill-formed UTF-8, which
    would make the harness emit a log its own reader must reject.
    """
    try:
        value.encode("utf-8")
    except UnicodeEncodeError:
        return False
    return True

def _cmd_solve(args: argparse.Namespace) -> int:
    """``gnd solve MODEL --workspace DIR`` — stage 1, then the walk.

    Stage 1 of the validation matrix lives here because a repeated flag and a
    malformed NAME=SECONDS are only visible at the command line. Stages 2 through
    8 are decidable from the typed arguments and belong to run_walk, which is the
    one home for them.
    """
    strings = [args.model, args.workspace, args.experiment, args.from_station, args.until]
    strings += list(args.skip) + list(args.test_argv) + list(args.station_timeout)
    if args.adapter is not None:
        strings.append(args.adapter)
    if args.adapter_policy is not None:
        strings.append(args.adapter_policy)
    for value in strings:
        if value is not None and not _utf8_clean(value):
            print(
                "gnd solve: error: command-line arguments must be valid UTF-8",
                file=sys.stderr,
            )
            return EXIT_USAGE

    station_timeout: dict[str, int] = {}
    for item in args.station_timeout:
        name, separator, raw = item.partition("=")
        if not separator or not name:
            print(
                f"gnd solve: error: --station-timeout expects NAME=SECONDS, got {item!r}",
                file=sys.stderr,
            )
            return EXIT_USAGE
        if not raw.isascii() or not raw.isdecimal():
            print(
                "gnd solve: error: --station-timeout SECONDS must be a positive ASCII integer",
                file=sys.stderr,
            )
            return EXIT_USAGE
        normalized = raw.lstrip("0") or "0"
        ceiling = str(solve.MAX_STATION_TIMEOUT_S)
        if len(normalized) > len(ceiling) or (
            len(normalized) == len(ceiling) and normalized > ceiling
        ):
            print(
                "gnd solve: error: --station-timeout SECONDS must be between 1 and "
                f"{solve.MAX_STATION_TIMEOUT_S}",
                file=sys.stderr,
            )
            return EXIT_USAGE
        seconds = int(normalized)
        if seconds < 1 or seconds > solve.MAX_STATION_TIMEOUT_S:
            print(
                "gnd solve: error: --station-timeout SECONDS must be between 1 and "
                f"{solve.MAX_STATION_TIMEOUT_S}",
                file=sys.stderr,
            )
            return EXIT_USAGE
        if name in station_timeout:
            # Two values for one station is a contradiction, not a set. --skip
            # repeats are fine for exactly the opposite reason.
            print(
                f"gnd solve: error: --station-timeout given twice for {name!r}",
                file=sys.stderr,
            )
            return EXIT_USAGE
        station_timeout[name] = seconds

    return solve.run_walk(
        Path(args.model),
        workspace=Path(args.workspace),
        experiment=None if args.experiment is None else Path(args.experiment),
        start=args.from_station,
        until=args.until,
        skip=frozenset(args.skip),
        auto=args.auto,
        adapter=args.adapter,
        adapter_policy=(None if args.adapter_policy is None else Path(args.adapter_policy)),
        test_argv=tuple(args.test_argv),
        station_timeout=station_timeout,
    )

_utf8_clean.__module__ = "gnd.cli"
_cmd_solve.__module__ = "gnd.cli"
