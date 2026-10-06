from __future__ import annotations

import argparse
import sys
from pathlib import Path

from gnd import exits as exits_module
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

from gnd.commands._arguments import _StoreOnce


def _register_solve(subparsers):
    solve_station_order = ", ".join(station.name for station in solve.STATIONS)
    solve_exit_map = ", ".join(
        f"{code} {meaning}" for code, meaning in exits_module.SOLVE_CONTROL_PLANE_EXITS
    )

    solve_parser = subparsers.add_parser(
        "solve",
        help="walk the CLI-pure GND stations in order, gating each, and log the walk",
        description=(
            f"Walk the CLI-pure GND stations in locked order -- {solve_station_order} "
            "-- blocking for an authorization "
            "before each one and appending an authorization record to a walk log "
            "before the station is spawned.\n"
            "\n"
            "WHAT THIS GUARANTEES: sequence, gating and logging FOR WALKS THAT GO "
            "THROUGH IT. Nothing more.\n"
            "\n"
            "WHAT IT DOES NOT GUARANTEE: the process in general. Running the "
            "stations a la carte stays legal and is not a violation of anything -- "
            "a harness that could not be bypassed would be routed around, and a "
            "bypassed harness is worse than none, because its log's existence "
            "would falsely imply the walk is where work happens.\n"
            "\n"
            "IT DOES NOT JUDGE STATION-INTERNAL AGENT WORK. The guarantee's "
            "perimeter is the walk log's perimeter.\n"
            "\n"
            "A STATION'S OWN EXIT IS IN THE LOG, NOT IN THIS COMMAND'S EXIT CODE. "
            f"The exit code is a control plane: {solve_exit_map}. "
            "A caller scripting this command reads the code "
            "and then reads the log; a station exiting 11 does not make gnd solve "
            "claim a collision about itself.\n"
            "\n"
            "THE BROWNFIELD PROFILE ASSUMES RECOVERY ALREADY COMPLETED. "
            "--skip synth --skip codegen --skip conformance leaves gnd validate; a "
            "recovered model's gate is gnd recovery verify, which runs BEFORE this "
            "harness is entered, not inside it.\n"
            "\n"
            "THE WALK LOG RECORDS WHAT THIS HARNESS DID; IT IS NOT PROOF THAT IT "
            "DID IT. A log that satisfies the walk predicate is a self-consistent "
            "document, and a file authored by hand can be self-consistent too. It "
            "attests no spawn, no executed argv, no existing artifact and no human "
            "presence.\n"
            "\n"
            "THE OUTER STATION TIMEOUT IS NOT THE CONTRACT'S INNER --wall-seconds "
            "BOUND. --station-timeout bounds the child process; this harness passes "
            "no --wall-seconds to gnd exp run, because a contract's own wall bound "
            "is the contract's business."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    solve_parser.add_argument("model", help="path to the model file")
    solve_parser.add_argument(
        "--workspace",
        required=True,
        action=_StoreOnce,
        help=(
            "the directory every station writes into. Required: a walk that wrote "
            "five artifacts into whatever directory the caller happened to be "
            "standing in is the accident this argument exists to prevent"
        ),
    )
    solve_parser.add_argument(
        "--experiment",
        action=_StoreOnce,
        help=(
            "the data-driven experiment directory for the exp-run station, which "
            "must resolve strictly inside --workspace. Mandatory when exp-run is "
            "selected and refused when it is not"
        ),
    )
    solve_parser.add_argument(
        "--from",
        dest="from_station",
        action=_StoreOnce,
        help="first station to run, inclusive",
    )
    solve_parser.add_argument("--until", action=_StoreOnce, help="last station to run, inclusive")
    solve_parser.add_argument(
        "--skip",
        action="append",
        default=[],
        metavar="NAME",
        help="omit a station; repeatable, and repeating one name is not an error",
    )
    solve_parser.add_argument(
        "--auto",
        action="store_true",
        help=(
            "authorize every gate without blocking. The log is NOT byte-identical "
            "to a gated walk: flags.auto is true and every authorization carries "
            "the auto source token"
        ),
    )
    solve_parser.add_argument(
        "--adapter",
        action=_StoreOnce,
        choices=("claude", "codex"),
        help="terminal-agent adapter for the exp-run station; resolves to claude",
    )
    solve_parser.add_argument(
        "--adapter-policy",
        action=_StoreOnce,
        help="trusted local declared-adapter policy for a schema-v6 exp-run station",
    )
    solve_parser.add_argument(
        "--test-argv",
        dest="test_argv",
        action="append",
        default=[],
        metavar="WORD",
        help="forwarded to the exp-run station verbatim, in the order given",
    )
    solve_parser.add_argument(
        "--station-timeout",
        dest="station_timeout",
        action="append",
        default=[],
        metavar="NAME=SECONDS",
        help=(
            "override one station's outer timeout. SECONDS is a positive integer "
            f"no greater than {solve.MAX_STATION_TIMEOUT_S}: an unbounded override "
            "is an unbounded child wearing a flag"
        ),
    )

    return {'solve_parser': solve_parser}


def add_parsers(subparsers, *, command: str | None = None):
    parsers = {}
    if command is None or command == 'solve':
        selected = _register_solve(subparsers)
        parsers.update(selected)
        selected['solve_parser'].set_defaults(handler=lambda args, selected=selected: handle(args, selected))
    if not parsers:
        raise ValueError(f"unsupported command: {command}")
    return parsers


def handle(args, parsers) -> int:
    if args.command == "solve":
        return _cmd_solve(args)

    raise ValueError(f"unsupported command: {args.command}")

