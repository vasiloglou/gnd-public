"""Small public reporting and approval CLI over submission facts."""
import argparse
import json
import sys
from pathlib import Path


def main(argv=None):
    parser = argparse.ArgumentParser()
    subcommands = parser.add_subparsers(dest="command", required=True)
    report = subcommands.add_parser("report")
    report.add_argument("--population", required=True)
    approve = subcommands.add_parser("approve")
    approve.add_argument("--population", required=True)
    approve.add_argument("--expense", required=True, type=int)
    approve.add_argument("--chain", required=True)
    args = parser.parse_args(argv)
    path = Path(args.population)
    document = json.loads(path.read_text())
    facts = document["facts"]
    submitted = {row["expense"] for row in facts["expense_submitted_by_employee"]}
    if args.command == "report":
        amounts = {row["expense"]: row["amount"] for row in facts["expense_has_amount"]}
        print(json.dumps({"submitted": len(submitted), "total": sum(amounts[e] for e in submitted)}))
        return 0
    if args.expense not in submitted:
        print("unknown expense: no submission fact", file=sys.stderr)
        return 1
    if args.expense in {row["expense"] for row in facts["expense_is_approved"]}:
        print("already approved", file=sys.stderr)
        return 1
    facts["expense_is_approved"].append({"expense": args.expense})
    facts["expense_approved_by_chain"].append({"expense": args.expense, "chain": args.chain})
    path.write_text(json.dumps(document))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
