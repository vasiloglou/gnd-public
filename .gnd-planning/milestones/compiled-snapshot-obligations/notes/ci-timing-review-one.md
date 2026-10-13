# Bounded local guarded-timing review one

Read the test-only diff in tests/test_guarded_corpus.py and the new deterministic
batch controls. No production edit or broad test run. **No blocking finding.**

## Observations

The loop runs 100 checker calls: ten pair iterations, two workloads and five
calls per workload. Every call validates its result and binding count and must
finish below the unchanged two-second individual ceiling. The unchanged
45-second deadline covers the complete loop, including warmup and assertions.
The ten warmup calls retain the existing exclusion from returned statistical
samples; their individual result and duration checks still run. The remaining
90 observations each contribute exactly once to the 18 fixed batch means.

There is no retry, sample-dependent batching, outlier filter, GC suppression or
conditional sample selection. Each workload retains nine samples and the
existing alternating pair order. Numerical thresholds remain unchanged:
relative MAD at most 10%, and the existing max(2.2 * smaller median, 0.2s)
scaling bound. The test has always included the 0.2-second floor; it is not a
new relaxation.

The statistical unit does change from individual calls to fixed five-call
means. This deliberately smooths scheduling/GC variability and can reduce MAD;
record it as a measurement-method change rather than claiming identical
statistical sensitivity. The unchanged individual ceiling prevents averaging
from hiding a call over two seconds. The new aggregate still measures all
non-warmup observations without discarding outliers.

## Focused verification and hardening suggestion

Ran only tests/test_guarded_timing_batches.py through the isolated Python 3.11
environment. Result: **2 passed in 0.09s**, exit 0. The call-count assertion pins
100 checker executions; the slow-call control demonstrates that even a warmup
spike cannot hide inside an average.

Low-severity test hardening: the current sequence [0.1,0.2,0.3,0.4,0.5] is
symmetric, so its mean and median both equal 0.3. Change to an asymmetric finite
sequence, such as [0.1,0.2,0.3,0.4,0.9], and assert mean 0.38. That would make
accidental replacement of the mean with a median or symmetric trimming fail.
Source inspection confirms the current code uses all five durations correctly;
this suggestion is not a reproduced implementation defect.

## Limits

One same-model advisory reading, limited to timing-method preservation and the
new deterministic controls. Real guarded workload runs on both interpreters
remain the root's evidence. This review establishes no full CI/platform claim,
certification, or proof of runtime performance under every host load.

## Bounded follow-up

The averaging fixture now uses [0.1,0.1,0.1,0.1,0.9] and expects mean 0.26;
median substitution or dropping the high observation would fail. This
discharges the low-severity aggregation-test suggestion. The existing ordering
control now expects each of its original alternating workload entries repeated
five times, preserving the warmup and pair sequence across all 100 calls.
Invalid report verdicts and binding counts are exercised at call 0, call 10
(first measured call) and call 99 (last call); none can escape checking.

Ran only the two batch controls and the repaired ordering/report control:

```text
UV_CACHE_DIR=/tmp/gnd-review-one-uv UV_PROJECT_ENVIRONMENT=/private/tmp/gnd-issue16-audit/venv uv run --no-sync --python 3.11 pytest -q tests/test_guarded_timing_batches.py tests/test_guarded_corpus.py::test_guarded_measurement_pairs_and_checks_every_report --tb=short
```

Result: **3 passed in 0.10s**, exit 0.

No remaining blocker or hardening request from this reader. These are test-only
repairs; numerical timing thresholds and real-workload scope remain unchanged.
Final real guarded group results are retained separately by the root.
