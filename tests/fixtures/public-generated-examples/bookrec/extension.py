"""Small public recommender over explicit rating and catalogue facts."""
import argparse
import json
import sys
from pathlib import Path

from gnd.checker import band, check
from gnd.model import load_model
from gnd.population import load_population


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["recommend"])
    parser.add_argument("--model", required=True)
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--user", required=True)
    parser.add_argument("--limit", type=int, required=True)
    args = parser.parse_args(argv)
    document = json.loads(Path(args.input).read_text())
    ratings = document["facts"]["user_rated_book"]
    if args.user not in {row["user"] for row in ratings}:
        print("unknown user", file=sys.stderr)
        return 3
    if args.limit <= 0:
        print("limit must be positive", file=sys.stderr)
        return 2
    read = {row["book"] for row in ratings if row["user"] == args.user}
    books = sorted({row["book"] for row in document["facts"]["book_has_title"]} - read)
    document["facts"]["recommendation"] = [
        {"user": args.user, "book": book} for book in books[:args.limit]
    ]
    output = Path(args.output)
    candidate = output.with_suffix(".candidate.json")
    candidate.write_text(json.dumps(document))
    model = load_model(args.model)
    report = check(model, load_population(candidate, model=model))
    status = band(report)
    if status == 0:
        candidate.replace(output)
    else:
        candidate.unlink()
    return status


if __name__ == "__main__":
    raise SystemExit(main())
