"""The VG1 scaling sweep (spec, "An experiment, recorded before it runs").

Run from a checkout: python vg1_sweep.py BUILT OUT.jsonl. Each run is a fresh
process; a run that exceeds 120 s is recorded as over 120 s, is not repeated,
and the larger sizes of that series are not run.
"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LIMIT = 120
SERIES = (
    [(shape, "check", (0, 250, 500, 1000, 2000)) for shape in ("values", "entities", "shared", "tree", "both")]
    + [("values", "judgments", (0, 250, 500, 1000)), ("values", "verify", (0, 1000)),
       ("chain", "chain", (200, 400, 800))]
)


def once(built, shape, n, route):
    try:
        done = subprocess.run([sys.executable, str(HERE / "vg1_once.py"), built, shape, str(n), route],
                              capture_output=True, text=True, timeout=LIMIT)
    except subprocess.TimeoutExpired:
        return {"shape": shape, "n": n, "route": route, "over": LIMIT}
    if done.returncode != 0:
        return {"shape": shape, "n": n, "route": route, "error": done.stderr[-400:]}
    return json.loads(done.stdout.strip().splitlines()[-1])


def main():
    built, out = sys.argv[1], Path(sys.argv[2])
    with out.open("a") as sink:
        for shape, route, sizes in SERIES:
            for n in sizes:
                runs = []
                for _ in range(3):
                    row = once(built, shape, n, route)
                    runs.append(row)
                    if "seconds" not in row:
                        break
                seconds = [r["seconds"] for r in runs if "seconds" in r]
                summary = {"shape": shape, "route": route, "n": n, "runs": runs,
                           "min_seconds": min(seconds) if len(seconds) == len(runs) else None}
                sink.write(json.dumps(summary) + "\n")
                sink.flush()
                if summary["min_seconds"] is None:
                    break


if __name__ == "__main__":
    main()
