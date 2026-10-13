"""Developer-owned expense CLI; policy is evaluated by the GND model."""

from __future__ import annotations

import argparse
import copy
import json
import sys
import tempfile
from pathlib import Path

from cli.reporting import summarize

from gnd.api import check


def _accepted(model: Path, population: Path) -> tuple[bool, dict]:
    report = check(model, population)
    return report["exit_code"] == 0, report


def _refusal(report: dict) -> int:
    print(json.dumps({
        "message": "GND withheld acceptance; no approval output was published",
        "exit_code": report["exit_code"],
        "findings": [
            {"constraint": row["constraint_ref"], "verdict": row["verdict"]}
            for row in report["verdicts"] if row["verdict"] != "pass"
        ],
    }), file=sys.stderr)
    return report["exit_code"]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    subcommands = parser.add_subparsers(dest="command", required=True)
    for name in ("report", "approve"):
        sub = subcommands.add_parser(name)
        sub.add_argument("--model", required=True, type=Path)
        sub.add_argument("--population", required=True, type=Path)
        sub.add_argument("--backend", choices=["gnd", "pyrel"], default="gnd")
        sub.add_argument("--pyrel-python", type=Path)
        if name == "approve":
            sub.add_argument("--expense", required=True, type=int)
            sub.add_argument("--chain", required=True)
            sub.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    if args.backend == "pyrel":
        from gnd.export.applications import execute_application

        if args.pyrel_python is None:
            parser.error("--backend pyrel requires --pyrel-python")
        with tempfile.TemporaryDirectory(prefix="expense-native-report-") as directory:
            output = args.output if args.command == "approve" else Path(directory) / "checked.json"
            result = execute_application(
                args.model, args.population, output, native_python=args.pyrel_python,
                query_script=Path(__file__).with_name("native_query.py"),
                query_args=(args.command, str(args.expense) if args.command == "approve" else "",
                            args.chain if args.command == "approve" else ""),
                owned_relations=("expense_is_approved", "expense_approved_by_chain") if args.command == "approve" else (),
                allowed_guard_kinds=("unknown-expense", "already-approved", "unsupported-currency"),
            )
        if result["accepted"] and args.command == "report":
            result["report"] = result["calculation"]["report"]
            result["published"] = False  # the private checked snapshot has been removed
        # Failed calculations are evidence in the library result, never a
        # successful business report in the CLI response.
        result.pop("calculation", None)
        print(json.dumps(result, sort_keys=True))
        return result["exit_code"]
    accepted, report = _accepted(args.model, args.population)
    if not accepted:
        return _refusal(report)
    document = json.loads(args.population.read_text(encoding="utf-8"))
    facts = document["facts"]
    if args.command == "report":
        print(json.dumps(summarize(facts), sort_keys=True))
        return 0
    submitted = {row["expense"] for row in facts["expense_submitted_by_employee"]}
    approved = {row["expense"] for row in facts["expense_is_approved"]}
    if args.expense not in submitted:
        print("unknown expense: no submission fact", file=sys.stderr)
        return 1
    if args.expense in approved:
        print("already approved", file=sys.stderr)
        return 1
    if args.output.resolve() == args.population.resolve():
        parser.error("output must be a separate file so the input checkpoint is preserved")
    candidate = copy.deepcopy(document)
    candidate["facts"]["expense_is_approved"].append({"expense": args.expense})
    candidate["facts"]["expense_approved_by_chain"].append({
        "expense": args.expense, "chain": args.chain,
    })
    # A temporary candidate gives the stable path-based API the exact bytes that
    # would be published. The same file is moved only after a clean check.
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", suffix=".json", dir=args.output.parent, delete=False
    ) as stream:
        staged = Path(stream.name)
        json.dump(candidate, stream, indent=2)
        stream.write("\n")
    try:
        accepted, report = _accepted(args.model, staged)
        if not accepted:
            return _refusal(report)
        staged.replace(args.output)
    finally:
        staged.unlink(missing_ok=True)
    print(json.dumps({"approved": args.expense, "chain": args.chain,
                      "output": str(args.output)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
