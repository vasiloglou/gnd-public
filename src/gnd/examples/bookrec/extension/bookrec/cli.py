"""Publish only a candidate accepted by the selected GND model."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

from gnd import api

from .library import complete, recommend


def publish(model, document, output):
    """Check a temporary file before an atomic move to a new output path."""
    output = Path(output)
    if output.exists():
        print("output already exists; choose a fresh path", file=sys.stderr)
        return 2
    descriptor, name = tempfile.mkstemp(prefix=".bookrec-", suffix=".json", dir=output.parent)
    candidate = Path(name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(document, stream, indent=2)
            stream.write("\n")
        report = api.check(model, candidate, unredacted=True)
        print(json.dumps(report, indent=2))
        if report["exit_code"] == 0 and report["acceptance_ready"]:
            candidate.replace(output)
        return report["exit_code"]
    finally:
        candidate.unlink(missing_ok=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["recommend", "complete"])
    parser.add_argument("--model", required=True)
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--user")
    parser.add_argument("--limit", type=int, default=2)
    parser.add_argument("--preferred-only", action="store_true")
    parser.add_argument("--backend", choices=["gnd", "pyrel"], default="gnd")
    parser.add_argument("--pyrel-python", type=Path)
    args = parser.parse_args(argv)
    if args.backend == "pyrel":
        from gnd.export.applications import execute_application

        if args.pyrel_python is None:
            parser.error("--backend pyrel requires --pyrel-python")
        result = execute_application(
            args.model, args.input, args.output, native_python=args.pyrel_python,
            query_script=Path(__file__).with_name("native_query.py"),
            owned_relations=("recommendation",),
            query_args=(args.command, args.user or "", str(args.limit),
                        "true" if args.preferred_only else "false"),
        )
        print(json.dumps(result, indent=2))
        return result["exit_code"]
    # Validate source structure through GND before application indexing. A nonzero
    # semantic band is repairable input here; malformed input is not.
    input_report = api.check(args.model, args.input, unredacted=True)
    if input_report["exit_code"] == 3:
        print(json.dumps(input_report, indent=2))
        return 3
    document = json.loads(Path(args.input).read_text(encoding="utf-8"))
    if args.command == "complete":
        candidate = complete(document)
    else:
        if args.limit <= 0:
            print("limit must be positive", file=sys.stderr)
            return 2
        users = {row["user"] for row in document["facts"]["user_prefers_genre"]}
        if args.user not in users:
            print("unknown user", file=sys.stderr)
            return 3
        candidate = recommend(
            document, user=args.user, limit=args.limit, preferred_only=args.preferred_only
        )
    return publish(args.model, candidate, args.output)


if __name__ == "__main__":
    raise SystemExit(main())
