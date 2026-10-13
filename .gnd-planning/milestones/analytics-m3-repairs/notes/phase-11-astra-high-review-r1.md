Retained reviewer text; edited only worktree paths to <GND_WORKTREE>.

Phase11 review found **one blocking contract gap and two hardening gaps** against baseline `098ec68`, including the untracked preparation module. These are source-traced findings; I ran no tests or reproductions.

1. **Blocking — the aggregate fingerprint-work bound is not enforced.**  
   [extension_preparation.py:90](<GND_WORKTREE>/src/gnd/extension_preparation.py:90) creates a fresh fingerprint budget on every call. Hits return before accounting; counters increase only when storing a result at line 111. Thus repeated hits each walk the full snapshot while the scope records only the first walk’s cost. Rejected/unsupported attempts are also uncharged, and entry-cap checks happen after fingerprinting. Additionally, [extensions.py:1302](<GND_WORKTREE>/src/gnd/extensions.py:1302) builds the complete model dump and relation tuple before any fingerprint limit applies.

   This contradicts the approved **aggregate fingerprint-work** limit in [phase-11-spec.md:25](<GND_WORKTREE>/.gnd-planning/milestones/analytics-m3-repairs/notes/phase-11-spec.md:25). The implementation bounds retained fingerprint accounting, not total preparation work. Charge every attempt against the remaining scope budget and bound snapshot construction; add a focused control covering repeated hits and exhausted-budget bypass.

2. **Hardening — changing an existing calculation helper can reuse stale results.**  
   The key at [extensions.py:1311](<GND_WORKTREE>/src/gnd/extensions.py:1311) omits `derivation_strata`, `compare_terms`, and other live dependencies. A concrete source-level counterexample is: warm the existing chain fixture’s stratified result, replace `extensions.derivation_strata` with a function returning `[]`, then repeat within the same scope. The key remains identical, so the cached nonempty result returns; the uncached body at [extensions.py:1336](<GND_WORKTREE>/src/gnd/extensions.py:1336) would iterate no strata and return empty extensions.

   `derivation_strata` is already a patch seam exercised by [test_public_derivation_cost_mutations.py:127](<GND_WORKTREE>/tests/test_public_derivation_cost_mutations.py:127). Preserve these seams through complete dependency tracking or conservative bypass, with a warm-cache regression.

3. **Hardening — the scope test cannot detect loss of evaluator/compose sharing.**  
   [test_m3_extension_preparation.py:144](<GND_WORKTREE>/tests/test_m3_extension_preparation.py:144) checks only that observed scopes are non-null. Its fixture has no operations, so [compiled_obligations.py:81](<GND_WORKTREE>/src/gnd/compiled_obligations.py:81) returns before calculating extensions. Removing the service scope would still leave the checker-owned scope satisfying these assertions. Disabling compatible-owner joining would likewise escape detection.

   Use an existing fixture that reaches stratified evaluation and compiled composition; assert the same owner spans both, actual calculation reuse occurs, and successive public calls receive different owners.

Other claims checked by source inspection:

- Fingerprinting distinguishes scalar types, finite float spellings, container kinds and order; unsupported/cyclic/deep shapes fall back.
- Model/population identity governs scope joining; different owners nest with token restoration. Failed calculations are not stored.
- Exact/partial policy and `DEFAULT_LIMITS` enter the key; selective, prior, observer, witness and reference-work routes bypass.
- For evaluator-produced shapes, mappings, unavailable bindings and work counters are isolated; immutable rows and possible metadata are preserved. Branch IDs replay through `record_branch`.
- Service scope currently encloses evaluator plus separate compose; direct checker joins compatible ownership. Marker validation and fresh compiled budgets remain outside cached calculations.
- Ordinary DAG dispatch, compatibility aliases and public signatures remain intact; no persistent result cache was added.

The spec, original RED and successor-test hashes match their rulings. The successor corrects frozen-field assignment without weakening the expectation. Retained evidence reports **153 focused passes**, lint green and successor baseline **8 failures/2 passes**; I did not independently execute those checks.

No completeness-only findings. Native timing/report parity and app controls remain pending acceptance evidence. The pre-repair complete answer still hit **120 seconds**; the original **109-question agreement and successful held-out median ≤15 seconds** gates remain unchanged.

**One reviewer is one reviewer.** No mutations, tests, credentials or provider tools were used; this is not certification or final acceptance.