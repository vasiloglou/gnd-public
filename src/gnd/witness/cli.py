"""CLI boundary for explicit finite-witness export and read-only replay."""

import json
import os

from gnd.artifacts import canonical_json_bytes
from gnd.witness import service as api
from gnd.witness.io import load_certificate
from gnd.witness.view import result_view, why_not_view, witness_view


def add_parsers(subparsers):
    p = subparsers.add_parser("witness", help="produce a finite grounded derivation witness")
    p.add_argument("model")
    p.add_argument("population")
    p.add_argument("--targets", required=True)
    p.add_argument("--reference-root")
    p.add_argument("--raw", action="store_true", help="explicitly expose replayable raw values")
    p.add_argument("--out", help="create a new raw certificate; requires --raw")
    p = subparsers.add_parser("replay", help="independently replay a finite derivation witness")
    p.add_argument("model")
    p.add_argument("population")
    p.add_argument("certificate")
    p.add_argument("--reference-root")
    p.add_argument("--json", action="store_true")
    p.add_argument("--raw", action="store_true", help="explicitly expose target values")
    p = subparsers.add_parser("witness-view", help="view a witness with default value redaction")
    p.add_argument("certificate")
    p.add_argument("--raw", action="store_true")
    p.add_argument("--expand", action="store_true")
    p.add_argument("--json", action="store_true")
    p = subparsers.add_parser(
        "why-not", help="explain why a derived fact type or row is not derived"
    )
    p.add_argument("model")
    p.add_argument("population")
    p.add_argument("--fact-type", required=True)
    p.add_argument("--row", help="a witness request holding the one claimed row")
    p.add_argument("--reference-root")
    p.add_argument("--raw", action="store_true", help="explicitly expose population values")


def run(args):
    try:
        if args.command == "why-not":
            result = api.why_not(
                args.model,
                args.population,
                args.fact_type,
                row_path=args.row,
                reference_root=args.reference_root,
            )
            view = {**result, "view": "raw"} if args.raw else {
                **why_not_view(result), "view": "redacted"
            }
            print(json.dumps(view, ensure_ascii=False, sort_keys=True))
            return result["exit_code"]
        if args.command == "replay":
            result = api.replay(
                args.model, args.population, args.certificate, reference_root=args.reference_root
            )
        elif args.command == "witness-view":
            result = witness_view(
                load_certificate(args.certificate), raw=args.raw, expand=args.expand
            )
        else:
            if args.out and not args.raw:
                raise ValueError("--out requires --raw")
            result = api.witness(
                args.model, args.population, args.targets, reference_root=args.reference_root
            )
            certificate = result["certificate"]
            if args.out and certificate is not None:
                # O_EXCL protects existing files, including symlinks, at the write.
                fd = os.open(args.out, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
                with os.fdopen(fd, "wb") as stream:
                    stream.write(canonical_json_bytes(certificate))
        if args.command in {"witness", "replay"} and not args.raw:
            result = result_view(result)
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return result["exit_code"]
    except (ValueError, OSError, TypeError):
        print(json.dumps({"exit_code": 3, "reason": "input-invalid"}))
        return 3
