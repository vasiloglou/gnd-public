"""Thin explicit command surface for the optional Souffle lane."""

import json

from gnd import api


def add_parsers(targets):
    for name in ("souffle", "souffle-verify", "souffle-run", "souffle-witness"):
        p = targets.add_parser(name, help="bounded standalone Souffle derivation claim")
        if name == "souffle":
            p.add_argument("model")
            p.add_argument("population")
            p.add_argument("--reference-root")
        else:
            p.add_argument("bundle")
        p.add_argument("--json", action="store_true")
        if name != "souffle-verify":
            p.add_argument("--raw", action="store_true")
        if name in ("souffle", "souffle-witness"):
            p.add_argument("--out")
        if name in ("souffle-run", "souffle-witness"):
            p.add_argument("--executable", default="souffle")
        if name == "souffle-witness":
            p.add_argument("--targets", required=True)


def dispatch(args):
    name = args.export_target
    if name == "souffle":
        result = api.export_souffle(
            args.model,
            args.population,
            reference_root=args.reference_root,
            out=args.out,
            raw=args.raw,
        )
    elif name == "souffle-verify":
        result = api.verify_souffle(args.bundle)
    elif name == "souffle-run":
        result = api.run_souffle(args.bundle, executable=args.executable, raw=args.raw)
    else:
        result = api.souffle_witness(
            args.bundle, args.targets, executable=args.executable, raw=args.raw, out=args.out
        )
    print(json.dumps(result, ensure_ascii=False, allow_nan=False))
    return result["exit_code"]
