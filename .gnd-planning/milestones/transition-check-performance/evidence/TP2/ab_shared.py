"""In-process A/B of TP2 on the reporter replay (evidence, not a gate).

Run from the repository root: uv run python <this file>. It alternates the shared
fact-type accessor with a copying stand-in (the TP1 behaviour), 3 runs each, in one process.
"""
import statistics
import sys
import time
from copy import deepcopy

sys.path.insert(0, "tools")
import measure_transition_cost as tool  # noqa: E402

from gnd.model_index import ModelIndex  # noqa: E402

run = tool.replay("reporter")
run()
shared = ModelIndex.iter_fact_types_shared


def copying(self):
    return iter(tuple(deepcopy(self._document.get("fact_types") or [])))


samples = {"shared": [], "copying": []}
for i in range(6):
    mode = "shared" if i % 2 == 0 else "copying"
    ModelIndex.iter_fact_types_shared = shared if mode == "shared" else copying
    start = time.perf_counter()
    run()
    samples[mode].append(time.perf_counter() - start)
ModelIndex.iter_fact_types_shared = shared
print({k: [round(x, 3) for x in v] for k, v in samples.items()})
print({k: round(statistics.median(v), 3) for k, v in samples.items()})
