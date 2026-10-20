# IE0 bounded Codex confirmation

Retained response; absolute repository link paths sanitized to relative citations.
No other substantive modification. One reader, not a panel; no tests run by reader.
Hashes matched at start/end; three further acceptance findings reproduced before fixing.

Three blocking acceptance gaps remain by static inspection:

1. **Receipt-mode semantic corruption still passes.** `tools/measure_incremental_evaluation.py:434` compares B’s payloads and branches, but compares complete semantic envelopes only between A and C. B’s extensions, lineage, unavailable and possible traces are unchecked. **Regression:** alter or delete only `receipts.semantic_replay.lineage` in an accepted document; require rejection. The current regression changes `fresh_full`, missing this case.

2. **Measured workloads lack exact expected-exit enforcement.** `tools/measure_incremental_evaluation.py:439` accepts any exit in `(0, 1, 2, 4)`; exact expectations apply only to synthetic parity rows. **Regression:** make course attempt 3 consistently fail across all arms, with matching payload digests; require rejection against the expected `[1, 1, 0]`. Current acceptance permits that wrong outcome.

3. **Deleting a required input identity still passes.** `tools/measure_incremental_evaluation.py:418` requires only a nonempty identity mapping. **Regression:** remove the old driver’s or review test’s identity from otherwise valid emitted evidence; require rejection. Current tests delete the entire mapping, leaving this T9 requirement uncovered.

Verified in source: actual evaluator-return counting replaces finding-label counting; zero/multiple-execution and constant-counter controls exist; acceptance enforces reporter 13/25/19 and positive mandatory counters. Repairs also add actual calculator-return traces, compiled partial-pattern controls, detached mutated models, alternate-support deletion/reference/options controls, partial-join counting, B-arm receipt paths, loading/evaluation timing separation, and consumption of a reusable mutated receipt.

All three supplied hashes matched initially and at completion. These are source-level findings and regression proposals, not executed results. I ran no tests or benchmarks, modified no files, accessed no credentials or networking/providers, and invoked no other agent. Fresh execution evidence and the externally running checks remain unverified by this reader.
