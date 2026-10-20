Retained output; edited only to replace machine repository/user paths.
Original SHA256: 50f1e79beb7fb58667f01283c5866dd6706b4d2630c3c7b519583bd827c09f5d

Three static falsifiers need RED reproduction before acceptance. I found no additional runtime correctness failure in the changed policy or hook fallback paths.

1. **P2 — “Complete traces” lose order and multiplicity.** [measure_incremental_evaluation.py:270](<REPO>/tools/measure_incremental_evaluation.py:270) records `sorted(set(calculations))`. Thus B’s `[x, x, y]` and C’s `[y, x]` compare equal, concealing skipped, duplicated or reordered calculations. Observe a consistent logical calculator boundary, then preserve its ordered sequence. Add deletion, duplication and permutation negative controls.

2. **P2 — Matching errors can pass course/localized acceptance.** [measure_evaluation_sessions.py:35](<REPO>/tools/measure_evaluation_sessions.py:35) checks equality and nonempty traces; only reporter receives frozen exit/census checks. Three identical rows with exit `70` and nonempty calculations/branches pass this comparator. Enforce course exits `[1,1,0]`, localized exits `[1]*6`, and their exact call counts. Add an equal-error negative control.

3. **P2 — Unit lookup denominators remain ambiguous.** [python-api.md:393](<REPO>/docs/reference/python-api.md:393) describes lookup events, but one lookup can increment both `misses` and `bypasses`: use `max_rows=0` and `rows=1` with an otherwise cacheable result. Early bypasses increment only `bypasses`, so summing the counters cannot recover lookup count. Document their overlap and supply an explicit lookup denominator before reporting fallback rates.

**Checked by reading:** one prepared normalization at the context construction site; exact active capability, code and mutable-leaf guards; expired/foreign/unsupported fresh fallback; ordinary normalized keys retained in entries; unchanged private entry accounting; fixed diagnostic vocabulary outside payload/feedback; callable/string unknown-hook refusal using actual namespace identity; evaluator invocation outside the setup catch. The shared oracle includes fact/role/codec/rows/lineage/unavailable/possible/logical-work fields. Old timing-arm routing remains intact; session C is explicit and positionally balanced.

One-generation publication, close/capacity/admission controls, documentation limits and successor registration were inspected. The shared-oracle extraction is a useful bounded refactor; no broader rewrite is justified. Localized timing currently remains aggregated across cold/no-op/dirty calls.

This was one initial static reader: **one reviewer is one reviewer**. No tests, writes, agents or external access were used. Reported gates and installed-wheel smoke were not independently verified. Pending gates/replay remain pending; exploratory `4878/179` and its slower C timing establish no final acceptance or speed claim.