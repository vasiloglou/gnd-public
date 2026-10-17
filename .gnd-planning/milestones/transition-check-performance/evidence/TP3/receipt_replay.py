"""TP3 evidence: counters and digests of the reporter replay with and without receipts.

Run from the repository root: uv run python <this file> OUT.json
"""
import json
import statistics
import sys
import time

sys.path.insert(0, "tools")
import measure_transition_cost as tool  # noqa: E402

out = {}
for name in ("reporter", "reporter-receipts"):
    run = tool.replay(name)
    run()
    with tool.counting() as counts:
        payloads = run()
    samples = []
    for _ in range(3):
        start = time.perf_counter()
        run()
        samples.append(time.perf_counter() - start)
    out[name] = {"counters": dict(counts),
                 "payload_digests": [tool.normalized_digest(p) for p in payloads],
                 "median_s": statistics.median(samples)}
out["payloads_identical"] = out["reporter"]["payload_digests"] == out["reporter-receipts"]["payload_digests"]
with open(sys.argv[1], "w") as handle:
    json.dump(out, handle, indent=2, sort_keys=True)
print({k: (v["counters"]["checker_runs"], round(v["median_s"], 3)) for k, v in out.items() if isinstance(v, dict)},
      "identical:", out["payloads_identical"])
