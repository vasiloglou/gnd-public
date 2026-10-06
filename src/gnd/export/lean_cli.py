"""Thin routes for separately selected Lean export, verify and compile claims."""

import json

from gnd.export import service as api


def add_parsers(targets):
    for name in ["lean", "lean-verify", "lean-compile"]:
        p = targets.add_parser(name, help="finite Lean definitions; explicit unproved obligations")
        p.add_argument("--json", action="store_true")
        if name == "lean":
            p.add_argument("model")
            p.add_argument("population")
            p.add_argument("--toolchain", required=True)
            p.add_argument("--reference-root")
            p.add_argument("--out")
            p.add_argument("--raw", action="store_true")
        else:
            p.add_argument("bundle")
        if name == "lean-compile":
            p.add_argument("--executable", default="lake")
            p.add_argument("--elaborate-stubs", action="store_true")


def dispatch(args):
    if args.export_target == "lean":
        result = api.export_lean(
            args.model,
            args.population,
            toolchain=args.toolchain,
            reference_root=args.reference_root,
            out=args.out,
            raw=args.raw,
        )
    elif args.export_target == "lean-verify":
        result = api.verify_lean(args.bundle)
    else:
        result = api.compile_lean(
            args.bundle, executable=args.executable, elaborate_stubs=args.elaborate_stubs
        )
    print(json.dumps(result, ensure_ascii=False, allow_nan=False))
    return result["exit_code"]
