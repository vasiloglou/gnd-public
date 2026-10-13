# Astra/high phase11 review, round 2

Retained reviewer response; edited only to sanitize absolute workspace paths.

**Round 2: no new demonstrated blocking or hardening findings.** The original **1 blocking + 2 hardening** findings are repaired by source inspection and retained regression evidence. I found no new output or refusal change.

- **Blocking—aggregate fingerprint budget: repaired.** [extension_preparation.py:113](<GND_WORKTREE>/src/gnd/extension_preparation.py:113) uses remaining scope allowances, bypasses exhausted/full scopes before snapshot construction, and charges hits and failed attempts. Accounting now completes **before** fallback evaluation at line 129, closing the retained `nodes=4` versus `3` nesting failure. [extensions.py:1301](<GND_WORKTREE>/src/gnd/extensions.py:1301) freezes model fields and relation contents incrementally, without an eager dump or complete relation copy.
- **Hardening—helper invalidation: repaired.** [extensions.py:1316](<GND_WORKTREE>/src/gnd/extensions.py:1316) includes callable lookup-home values and Python code identities, `math.isfinite`, and frozen `DEFAULT_LIMITS` fields. The retained warm-`derivation_strata` regression demonstrates the original stale-result failure.
- **Hardening—public sharing control: repaired.** [test_m3_extension_preparation.py:253](<GND_WORKTREE>/tests/test_m3_extension_preparation.py:253) reaches compiled composition, asserts shared evaluator/checker/compose ownership and fresh successive owners. Both owner mutants were retained RED. The additional [real calculation control:279](<GND_WORKTREE>/tests/test_m3_extension_preparation.py:279) requires fewer body calls and equality of the **complete** disabled/prepared public report.

Other claims verified by source inspection:

- Scalar distinctions, finite float representation, integer storage charging, YAML containers, Pydantic fields and Enum values are handled under bounded traversal; unsupported, cyclic and excessive-depth shapes bypass preparation.
- Compatible owners join; different owners restore the outer context; exceptions restore scope and branch capture and do not cache results.
- For evaluator-produced shapes, mapping wrappers, unavailable bindings and work counters are isolated; immutable rows, lineage and possible metadata remain intact. Cached branch IDs replay through `record_branch`.
- Exact/partial policies remain separated. Selective, prior-state, observer, witness and reference-work routes retain fallback. Public admission checks and fresh compiled work budgets remain outside cached calculations.
- No persistent/global result cache or public signature change was introduced.

The amended spec, tests and both implementation hashes match the review ruling. Retained evidence reports [15 direct passes](<GND_WORKTREE>/.gnd-planning/milestones/analytics-m3-repairs/evidence/phase-11-review-green.txt:2), [159 focused passes](<GND_WORKTREE>/.gnd-planning/milestones/analytics-m3-repairs/evidence/phase-11-focused.txt:4), and lint green. I read these results; I did not execute them.

**Acceptance remains pending:** the retained native summary’s implementation hashes differ from the reviewed bytes, so its timing/parity results do not establish current-byte performance. Native 6+6 and app90 repeats remain owed. The original 109-development agreement and successful held-out median ≤15 seconds gates remain unmet; isolated timing does not close M3.

**One reviewer is one reviewer.** This was a read-only review against `098ec68`, including the untracked module. No tests, mutations, credentials or provider tools were used. No completeness-only work or further review round is requested.
