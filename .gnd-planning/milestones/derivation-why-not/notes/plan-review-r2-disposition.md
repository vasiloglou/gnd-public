# Plan review -- round 2 (confirmation) disposition

2026-10-30. Instrument: four local reviewer agents (WN-D8 `(o)`). The round ran
at the owner's direction after round 1, quoted: "I accept the round-1
disposition's repair themes A-K. Apply them as r2, take the proposed answers
where a decision is re-argued, and run the one confirmation round over the
blocking themes." The direction does not approve plan or spec bytes.

## Subjects and limits

| Subject | SHA-256 | Retained snapshot |
|---|---|---|
| plan r2 | `b0308e35e0e088d7264b24c0f34de0bec2f676e7d83cc325bd90bbfa1514630e` | `evidence/plan-review-r2/derivation-why-not-plan.md.snapshot` |
| WN1 spec r2 | `d1c87cb1315341e453debb6fd7088abc0b8f5a4dc831dd2a4ac33abdf44f6f69` | `evidence/plan-review-r2/phase-WN1-spec.md.snapshot` |

The [manifest](../evidence/plan-review-r2/manifest.json) records the snapshot and
reader-note digests. All four readers verified both digests. Each received its
round-1 lens and was asked to (1) rule on each of its own round-1 findings and
(2) look for new defects in the repaired text of the blocking themes, tagging
each as self-inflicted or original. Readers 1 and 4 wrote probe scripts in the
session scratchpad; reader 2 ran focused tests (1,383 passed) and probes; reader
3 only read. No reader wrote to the repository. No network, credentials or paid
tools were used.

## Opinions

| Reader | Lens | Verdict | New | Blocking | Self-inflicted |
|---|---|---|---|---|---|
| [1](plan-review-r2-reader-1.md) | correctness against production semantics | request-changes | 5 | 2 | 5 |
| [2](plan-review-r2-reader-2.md) | implementability, pins and homes | approve-with-fixes | 8 | 1 | 8 |
| [3](plan-review-r2-reader-3.md) | protocol, authority, compatibility, privacy | approve-with-fixes | 7 | 0 | 5 |
| [4](plan-review-r2-reader-4.md) | test design, falsifiability, demonstration | request-changes | 7 | 3 | 7 |

Total: 27 new findings, 6 blocking, 25 self-inflicted. R1-2-F1, R2-2-F1 and
R4-2-F1 are the same defect, so there are **4 distinct blocking findings**, all
self-inflicted.

Round-1 findings: of 35, the readers marked 24 resolved and 11 partly resolved
(R1-F3, F4, F7; R2-F3; R3-F5, F8, F10; R4-F2, F3, F4, F6). None was marked not
resolved. Every "partly" is carried by a round-2 finding listed below.

## Coordinator reproduction

| Finding | Check | Result |
|---|---|---|
| R1-2-F1, R2-2-F1, R4-2-F1 (shared budget) | reader 1 probed (`probe_t13.py`); readers 2 and 4 derived the same figures independently | pre-evaluation charges 88,791 (17 rows) and 111,204 (18 rows); T13(a)/(b) as written cannot test the walk |
| R4-2-F3 (T8 circular) | spec §6.2 vs T8 | T8 compares the status with the call it was copied from: confirmed by reading |
| R4-2-F2 (T13c self-referential) | spec T13c | confirmed by reading |
| R1-2-F2 (opaque scan) | reader 1's `probe_b`; `branches.py:786` maps opaque to `unchecked` | confirmed by reading; probe not re-run |
| R1-2-F4 (semiderived) | `extensions.py:2496` reports surplus only when `derivation == "derived"` | confirmed |
| R2-2-F2 (API pins) | `test_public_api.py:15-27` asserts `unredacted` for every listed name; `tools/run_public_acceptance.py:373` pins `__all__` | confirmed |
| R2-2-F4 (limits) | `witness/types.py:33` requires `isinstance(limits, WitnessLimits)` | confirmed |
| R2-2-F6 (schema rationale) | `test_schema_sync.py:27` syncs only `orm-meta`, `population`, `steps` | confirmed |

## Convergence ledger

| Round | Subject | Findings | Blocking (distinct) | Self-inflicted | Ratio |
|---|---|---|---|---|---|
| 1 | r1 | 35 | 10 (8) | 0 | 0 |
| 2 | r2 | 27 | 6 (4) | 25 | 0.93 |

**Stop rule** (`review-convergence.md`): stop when the self-inflicted ratio
exceeds one half. Round 2's ratio is 0.93, so review stops. The plan's §8 budget
also allows no third round without a new owner request. The repairs below are
therefore proposed as r3 **without a further review round**; r3 bytes would carry
no review opinion, and the owner decides plan approval over them.

## Proposed repairs for r3

Proposals only; nothing is applied until the owner accepts them.

- **L. Separate budgets, recomputed tests.** Two counters: `pre` (the production
  pre-evaluation, charged through the charge-only trace in bindings only, as
  `witness` is) and `walk` (bindings, probes, cells). Each has its own ceiling in
  `WhyNotLimits`. WN-R4 and spec §4 rule 2 say plainly that pre-evaluation probe
  work is bounded only by the input ceilings, as in `check` and `witness`.
  T13 is rebuilt on fixtures where production does not enumerate what the walk
  does (atoms 1 and 2 disconnected, atom 3 bridging, a trailing empty atom), with
  literal expected values for both counters on both sides of each ceiling, and
  T13c with a fixed |R| (300) and literal `probes` and `walk` values that a
  nested-loop implementation would exceed. A test hook (`work` on the raised
  `WhyNotWorkError`) exposes the counters on a breach. The `work` key is renamed
  `joins` to match the limit field. (R1-2-F1, R2-2-F1, R4-2-F1, R4-2-F2, R1-2-F3,
  R2-2-F8)
- **M. Agreement with `check`, not with itself.** T8 compares why-not's status
  with the `gnd check` derivation verdict (via `_evaluate_derivations_dispatch`),
  with the map written out: `pass` with the row present (or a non-empty
  extension) → `derived`; `unchecked` with a `term:` reason → `unavailable`;
  `unchecked`/`opaque-value` and `rule-opaque` → `unsupported`; otherwise
  `blocked`. The oracle also computes derivability by its own fixpoint and runs
  on derived cases. `unchecked-not-covered` is stated: why-not ignores `covers`.
  (R4-2-F3, R1-2-F5)
- **N. Opaque scan over the facts check reads.** The opaque scan reads
  `population.facts` and reference facts for every fact type in the closure,
  target included, as `_evaluate_derivations_dispatch` does; opaque rows outside
  the closure are stripped before relations are built, so the pre-evaluation
  takes the exact path. Opaque is exit 2 `unsupported` (following `witness`'s
  band, not `check`'s band 4), and "opaque" is removed from the exit-4 row; T8's
  map says so. `heads=closure` includes the target. (R1-2-F2, R1-F3 remainder,
  R3-2-F2, R1-2-F5)
- **O. Reachable branches only.** Drop clause status `derived`; raise
  `WhyNotInternalError` when **any** walked clause ends non-zero; add a case for
  the descent-returns-derived raise; state that descent depth 8 is recorded and
  `proof_depth` (128) can only breach with a lowered limit, with T12's fixture
  value. Descent excludes string-rule predicates, whose blockers say
  `derivation: base`. (R4-2-F5, R4-2-F6, R4-F4 item 7, R1-2-F5)
- **P. Semiderived truth.** Correct D6: `check` reports no unsound surplus for
  semiderived types, and dependents never read asserted semiderived rows. The
  WN2 doc says so; a T8/T10 fixture pins it; the blocker carries
  `asserted_not_read: true` when the absent row is asserted. (R1-2-F4)
- **Q. A stronger oracle and repair loop.** Replace the unbuildable `True`/`1`/`"1"`
  case with a buildable boolean-vs-number case or a marked direct-relation case;
  extend the oracle import ban to `gnd.checker` and `gnd.witness`, enforced by an
  AST import test; the census asserts each discriminator's property (for example,
  that declared order differs from `_joined_bindings` order). WN3-C2: each gap
  has at least one bound role taken from raw samples; the extracted table holds
  only free roles (disjointness asserted); gap 1 is at index ≥ 1; "unchanged"
  means (kind, index, fact_type); the expected `check` variant is named.
  (R4-2-F4, R4-2-F7)
- **R. Pins and homes, exactly.** List all three `__all__` literals
  (`test_public_api.py:16`, `test_v61_phase2_api.py:38`,
  `tools/run_public_acceptance.py:373`); a separate `why_not` signature assertion;
  `answers.json` beside `cases.json`; every RF1 golden that embeds the command
  list is regenerated by `rf1_pins.py capture`; the permitted model accessors are
  named (`ModelIndex.fact_type(id)`, `iter_fact_types_shared()`, `roster(model)`,
  `relation.roles`; never `.fact_types`); the service projects `WhyNotLimits` to a
  `WitnessLimits` for input loading, with a test; the schema-home reason is
  reworded to "root-level output contracts are what `VENDORED_SCHEMAS`
  enumerates"; the check-contract test files T15 relies on join the WN1 gate.
  (R2-2-F2..F7)
- **S. Protocol honesty.** WN-D3, D4 and D5 relabelled "proposed under the
  owner's direction of 2026-10-30; the owner confirms at the plan gate", kept in
  every blocked-on list, with spec D2's readings and costs restored; README tense
  fixed; the validation-order change becomes its own proposed decision (sibling
  parity with `witness`, which refuses malformed targets before reporting
  unsupported) without the `(p1-E)` tag; T17 uses committed SHA-256 digests of
  normalized forbidden tokens over files added since `fb03739`, with a negative
  control, and fails rather than skips; completion predicate 4 and WN2-C1 are
  conditional on WN-D10 and WN-D11; the README's release-note phase is fixed;
  §8 states the stop-rule outcome. (R3-2-F1, F3..F7)

## Next action

The owner accepts, amends or rejects themes L-S. If accepted, they are applied as
r3 with no further review round, and the owner then decides plan approval over
r3 together with the pending rulings (WN-D1, D2, D6, D7, D9..D13 and confirmation
of D3, D4, D5).
