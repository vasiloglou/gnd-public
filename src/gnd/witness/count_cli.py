"""Public commands for bounded COUNT membership evidence."""

import json
from pathlib import Path

from gnd.artifacts import ArtifactError, canonical_json_bytes, publish_leaf_atomic


def add_parsers(subparsers):
    for name, help_message in (
        ("witness-count", "produce a bounded COUNT membership certificate"),
        ("replay-count", "independently replay a COUNT membership certificate"),
    ):
        parser = subparsers.add_parser(name, help=help_message)
        parser.add_argument("model")
        parser.add_argument("population")
        parser.add_argument("--request", required=True, help="expected COUNT group request")
        parser.add_argument("--raw", action="store_true", help="explicitly reveal bound values")
        if name == "witness-count":
            parser.add_argument("--out", help="create a new certificate file; requires --raw")
        else:
            parser.add_argument("certificate")
        parser.set_defaults(handler=run)


def run(args):
    if args.command == "witness-count":
        from gnd.witness.count_producer import produce_count
        if args.out and not args.raw:
            result = {"exit_code": 3, "reason": "input-invalid"}
        else:
            result = produce_count(args.model, args.population, args.request)
            if args.out and "certificate" in result:
                output = Path(args.out).absolute()
                try:
                    publish_leaf_atomic(
                        output.parent, output.name, canonical_json_bytes(result["certificate"]), mode=0o600
                    )
                except (ArtifactError, OSError):
                    result = {"exit_code": 3, "reason": "input-invalid"}
    else:
        from gnd.witness.count_replay import replay_count
        result = replay_count(args.model, args.population, args.certificate, args.request)
    if not args.raw:
        for key in ("certificate", "request", "count"):
            result.pop(key, None)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return result["exit_code"]
