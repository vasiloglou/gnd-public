"""Bound the indexed subset layer on unchanged supplied native mirror relations."""
import hashlib
import json
import signal
import sys
from pathlib import Path
from time import perf_counter

from gnd import semantic_rows, semantic_spec
from gnd.model import load_model
from gnd.population import load_population
from gnd.semantic_adapter import adapt_snapshot


def measure_identity_work(operation):
    calls = [0]
    original = semantic_rows.scalar_identity
    def count(value):
        calls[0] += 1
        return original(value)
    semantic_rows.scalar_identity = count
    started = perf_counter()
    try:
        result = operation()
    finally:
        elapsed = perf_counter() - started
        semantic_rows.scalar_identity = original
    return result, elapsed, calls[0]


def main(root):
    model = load_model(root / "plan.orm.json")
    population = load_population(root / "state0.pop.json", model=model)
    snapshot = adapt_snapshot(model, population)
    mirrors = {f"constraints[{i}]": row["id"] for i,row in enumerate(model.constraints)
               if row.get("id") in {"mirror_plan_role_functional", "mirror_role_functional"}}
    assert len(mirrors) == 2
    results = []
    for constraint in snapshot.constraints:
        if constraint.ref not in mirrors:
            continue
        expected = semantic_spec.verdict_of(constraint, snapshot)
        def deadline(*args):
            raise TimeoutError("indexed subset layer exceeded15s")
        signal.signal(signal.SIGALRM, deadline)
        signal.setitimer(signal.ITIMER_REAL, 15)
        try:
            actual, elapsed, calls = measure_identity_work(
                lambda: semantic_rows.indexed_subset_verdict(constraint, snapshot))
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)
        assert actual == expected
        projected = [semantic_spec.role_sequence_rows(sequence, snapshot)[1]
                     for sequence in constraint.sequences]
        scalar_count = sum(len(row) for rows in projected for row in rows)
        assert calls <= 2 * scalar_count
        results.append({"constraint":mirrors[constraint.ref],
                        "rows":[len(rows) for rows in projected], "seconds":elapsed,
                        "identity_calls":calls, "linear_bound":2*scalar_count,
                        "oracle_identical":True, "verdict":actual[0]})
    assert len(results) == 2
    print(json.dumps({"mirrors_retained":True, "results":results,
                      "inputs":{p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in (root/"plan.orm.json",root/"state0.pop.json")}}, sort_keys=True))


if __name__ == "__main__":
    main(Path(sys.argv[1]))
