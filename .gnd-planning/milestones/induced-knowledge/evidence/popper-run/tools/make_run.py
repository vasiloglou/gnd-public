"""Build a gnd-ilp-run/1 record from a CLAUSES file and coverage.pl output.

Usage: python make_run.py EXPORT_JSON CLAUSES COVERAGE_JSONL VERSION OUT
"""
import hashlib
import json
import sys

export_json, clauses, coverage, version, out = sys.argv[1:]


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


with open(coverage) as f:
    rows = [json.loads(line) for line in f if line.startswith("{")]
record = {
    "schema_version": "gnd-ilp-run/1",
    "learner": {"name": "popper", "version": version},
    "export_sha256": sha(export_json),
    "clauses_sha256": sha(clauses),
    "coverage": rows,
}
with open(out, "w") as f:
    json.dump(record, f, indent=2)
    f.write("\n")
print(json.dumps(record))
