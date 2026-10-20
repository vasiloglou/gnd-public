Retained output; edited only to replace machine repository/user paths.
Original SHA256: 1f3331fabc3fe1f3bce2a9336a6940537fac673bc16726b7202886e356775d9a

One additional **P2 static measurement falsifier needs RED reproduction**:

[public_call:265](<REPO>/tools/measure_incremental_evaluation.py:265) fingerprints the payload while `count_work` remains active. That observer traversal enters both `actual_work.fingerprint_nodes` and the per-call delta, inflating reported evaluator work.

Concrete falsifier: enable `COMPLETE_CALL_SINK`, then run `public_call(lambda: {'exit_code': 0})` inside `count_work()`. The callable performs no runtime fingerprinting, but the observer produces a positive `fingerprint_nodes` count. Exclude or separately account for that diagnostic traversal. This concerns adjacent IE5 measurement code already present before these confirmation repairs; it does **not** invalidate the derivation-body gate or separate uninstrumented timings.

The three original falsifiers withstand static inspection:

- The shared observer tracks outermost calculator returns, including cached stratified-wrapper returns; output preserves order and multiplicity.
- The comparator requires workload identity and every arm’s frozen census/exits: reporter 13/all 2, course 3/`[1,1,0]`, localized 6/all 1.
- `lookups` increments once after ownership checks. Overlapping miss/bypass events are documented; rates expose numerator, denominator and `null` for zero.

I also checked the deletion/duplication/permutation negatives, nested/cached control, balanced preloaded case timings, separate per-call work capture, instrumentation refusals, and source/fixture stability guard. No additional runtime correctness issue surfaced in the inspected neighboring paths.

**One reviewer is one reviewer.** This was static reading only: no tests, writes, agents, network/providers, or credentials. The reported 46 passes were not independently verified. Ordered replay, final measurement, combined repaired gate and rebuilt candidate smoke remain pending. No final acceptance or wall-speed claim follows from this confirmation.