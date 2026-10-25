from __future__ import annotations

import argparse
from datetime import datetime

import gnd.discover.service as _handler_discover_service
from gnd.commands._arguments import _add_format_argument

FAMILIES = _handler_discover_service.FAMILIES


def _families(text: str) -> tuple[str, ...]:
    names = tuple(name.strip() for name in text.split(",") if name.strip())
    unknown = sorted(set(names) - set(FAMILIES))
    if not names or unknown:
        raise argparse.ArgumentTypeError(
            f"unknown families {unknown}; choose from {', '.join(FAMILIES)}"
        )
    return tuple(family for family in FAMILIES if family in names)


def _at_least(minimum: int):
    def parse(text: str) -> int:
        try:
            value = int(text)
        except ValueError as error:
            raise argparse.ArgumentTypeError(f"{text!r} is not an integer") from error
        if value < minimum:
            raise argparse.ArgumentTypeError(f"must be at least {minimum}")
        return value

    return parse


def _actor(text: str) -> str:
    if not text.strip():
        raise argparse.ArgumentTypeError("--actor must name who requests the proposal")
    return text


def _requested_at(text: str) -> datetime:
    try:
        value = datetime.fromisoformat(text)
    except ValueError as error:
        raise argparse.ArgumentTypeError(f"{text!r} is not an ISO-8601 time") from error
    if value.tzinfo is None or value.utcoffset() is None:
        raise argparse.ArgumentTypeError("--requested-at needs a UTC offset")
    return value


def _register_discover(subparsers):
    discover_parser = subparsers.add_parser(
        "discover",
        help="propose induced constraints observed in one population (IK4)",
        description=(
            "Propose candidate constraints of seven families (uniqueness, mandatory, "
            "value, frequency, subset, equality, exclusion) that hold in one "
            "population. A candidate is kept only when `gnd check` passes it with "
            "support > 0 and the model neither declares nor entails it. Writes a "
            "discovery report and, when anything is emitted, a `gnd evolve` "
            "proposal of induced, proposed, deontic constraints: admission stays a "
            "reviewed act. Exits 0 on success (also with nothing emitted), 3 on an "
            "invalid model or population, 11 when --out already exists (nothing "
            "written), 64 on a usage error, 66 on a missing input, 70 on an "
            "internal defect, 74 on a refused output path."
        ),
    )
    discover_parser.add_argument("model", help="path to the model file")
    discover_parser.add_argument("population", help="path to the population file")
    discover_parser.add_argument("--out", required=True, help="write the evolve proposal here")
    discover_parser.add_argument("--report", required=True, help="write the discovery report here")
    discover_parser.add_argument(
        "--actor", required=True, type=_actor,
        help="who requests the proposal (its audit actor_id)",
    )
    discover_parser.add_argument(
        "--requested-at", required=True, type=_requested_at,
        help="when, as ISO-8601 with a UTC offset (the audit time; keeps output reproducible)",
    )
    discover_parser.add_argument(
        "--families", type=_families, default=FAMILIES,
        help="comma-separated subset of the seven families (default: all)",
    )
    discover_parser.add_argument(
        "--max-values", type=_at_least(1), default=20,
        help="largest distinct-value count for a value candidate (default 20)",
    )
    discover_parser.add_argument(
        "--max-pairs", type=_at_least(0), default=256,
        help="most unordered role pairs compared for subset/equality/exclusion (default 256)",
    )
    _add_format_argument(discover_parser)
    return {"discover_parser": discover_parser}


def add_parsers(subparsers, *, command: str | None = None):
    parsers = {}
    if command is None or command == "discover":
        selected = _register_discover(subparsers)
        parsers.update(selected)
        selected["discover_parser"].set_defaults(
            handler=lambda args, selected=selected: handle(args, selected)
        )
    if not parsers:
        raise ValueError(f"unsupported command: {command}")
    return parsers


def handle(args, parsers) -> int:
    if args.command == "discover":
        return _handler_discover_service._cmd_discover(
            args.model,
            args.population,
            out=args.out,
            report=args.report,
            actor=args.actor,
            requested_at=args.requested_at,
            families=args.families,
            max_values=args.max_values,
            max_pairs=args.max_pairs,
            output_format=args.format,
        )

    raise ValueError(f"unsupported command: {args.command}")
