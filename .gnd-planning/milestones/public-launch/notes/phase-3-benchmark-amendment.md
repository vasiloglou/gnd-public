# Phase 3 benchmark amendment — approved 2026-10-03

The owner said “ok do that” after the recommendation to collect more samples,
assess variability and define a meaningful tolerance before further runtime edits.
This authorizes the benchmark repair and its verification; earlier failures stand.

## Contract before implementation

Use the same 10000/20000-fact populations and unchanged verdict/binding counts.
In one isolated process with normal GC, warm each workload once, then measure
nine pairs, alternating which size runs first. Validate every resulting report.
Retain all raw durations. Every measured check must remain below two seconds.
Use the median duration per size rather than the minimum of three. Reject an
unstable measurement when median absolute deviation exceeds 10% of its median;
never increase the acceptance threshold to accommodate observed noise.
Accept scaling only when median20k <= max(2.2 * median10k, 0.2 seconds).
The 2.2 factor is an explicit engineering tolerance: 10% above ideal doubling,
not a confidence interval or a proof of asymptotic complexity. The existing
0.2-second floor remains. This changes the approved performance predicate;
it does not reclassify any earlier failed run as passing.

Synthetic controls must accept small jitter, reject a stable ratio above 2.2,
reject quadratic-like scaling, absolute slowness, invalid/incomplete samples and
high dispersion. Verify collection ordering/count and per-report correctness;
retain the existing isolated-failure propagation control. No skips or xfails.
A 45-second total measurement deadline and 60-second subprocess ceiling cover
20 checks (warmups included); the individual two-second product bound remains.

Budget for this amendment: at most 160 additional authored implementation/test
lines plus this approval/evidence, focused verification on local Python 3.11 and
3.13, then one additional hosted acceptance attempt. No automatic retry or new
independent reviewer. Existing workflow job ceilings and PR-only policy stand.
Source runtime and target runtime remain unchanged. Phase closure still requires
both full regression profiles and both installed candidate profiles to pass.
