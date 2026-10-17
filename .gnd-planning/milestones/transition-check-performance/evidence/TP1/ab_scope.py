"""In-process A/B of the TP1 index scope on the reporter replay (evidence, not a gate).

Run from the repository root: uv run python <this file>. The replay alternates between the
real index_scope and a no-op scope, 3 runs each, in one process, so machine drift between
separately launched runs does not enter the comparison.
"""
import contextlib
import statistics
import sys
import time

sys.path.insert(0, "tools")
import measure_transition_cost as tool  # noqa: E402

from gnd import model_index  # noqa: E402

run = tool.replay("reporter")
run()
real = model_index.index_scope


@contextlib.contextmanager
def no_scope():
    yield


samples = {"scope": [], "no_scope": []}
for i in range(6):
    mode = "scope" if i % 2 == 0 else "no_scope"
    model_index.index_scope = real if mode == "scope" else no_scope
    start = time.perf_counter()
    run()
    samples[mode].append(time.perf_counter() - start)
model_index.index_scope = real
print({k: [round(x, 3) for x in v] for k, v in samples.items()})
print({k: round(statistics.median(v), 3) for k, v in samples.items()})
