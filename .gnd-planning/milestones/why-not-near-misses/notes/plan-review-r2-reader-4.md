# Confirmation round (round 2), reader 4 -- test design, falsifiability

Retained text of the reader's returned report, lightly edited for layout.
Scratch paths read `<scratch>`.

Both digests matched: plan r2 `211d9e01…490a665de`, NM1 spec r2 `1b739a57…5087de1d72`.

**Verdict:** approve-with-fixes

**Scope.** Both r2 snapshots in full, diffed against r1; checked against
`why_not.py`, `extensions._joined_atom_candidates` (629-680),
`tests/why_not_oracle.py`, the generator, kernel limit tests and
`inspect.signature` over `gnd.api.__all__`. Implemented the r2 Design literally
as a runtime patch and an independent brute-force oracle (`unicodedata` and the
oracle's own `identity` only). Probes in `<scratch>/nm-review2/reader4/`
(`nm2impl.py`, `cases.py`, `gen.py`), Python 3.14.3, Unicode 16.0.0. Nothing
written in the repository.

**Measured.** T1 all pairs reproduce (incl. `ACME-CORP`→`acmecorp` ≠
`ACME CORP`; `...`, `－－` → `None`). T2: count 1, `roles == ["k"]`, 2
inspections. T10: count 0, no exception; T10b 1; T10c one pair, both roles.
T11b, T11c: 1 each. T12 bracket: full count 4 at `m=5`; truncated, count 2 at
`m−1`. T12b: 200/400/800 inspections, counts 10,000/40,000/160,000. T12c: 1,024
inspections, count 262,144, not truncated, probes 1,536. T16 raises. SPELLING
over 200 seeds: 200 valid, 202 atom blockers, 175 with `B` non-empty, **46
non-zero** (floor 20 holds), 0 kernel exceptions, 0 oracle disagreements, **0
truncated, 0 with count > 5**.

## Theme status

| Theme | Status | Basis |
|---|---|---|
| A | repaired | spec:101-110, plan:199-207; T10 no longer raises; invariant sound by argument |
| B | repaired | `near_misses=False` default; `service.py:138-156` cannot pass it |
| C | repaired, with test gaps | keyed counting 1,024 inspections for 262,144 pairs; own counter; see C4-F3, F4 |
| D | repaired | plan:127, 279-282; NM2-C1, C3 |
| E | repaired | ruled (a): plan:262-267, 550 |
| F | partly repaired | mechanical discovery misses raw-by-default API functions; `api.why_not` has no row (C4-F5) |
| G | repaired | plan:269-273; NM2-C3 identical bytes; ruling cited |
| P | mostly repaired | remaining: C4-F1, F2, F3, F6, F7 |

## Findings

### C4-F1 -- Oracle cannot agree on truncated reports (hardening, self-inflicted)

- **Where:** spec:152-159, 209 (T17 covers T12 `m−1`, T16), 141-142; plan:95-98, 334-337.
- **What is wrong:** the brute-force oracle always returns the full count; making
  it mimic truncation would copy the kernel's row order. T16, T19, T20 cannot be
  oracle-compared.
- **Reproduction:** `gen.py <scratch> 3` (cap 3): 120 truncated, 40
  disagreements (seed 5: kernel 0 vs oracle 2).
- **Fix:** T17/T18 exact agreement only when untruncated; truncated: kernel
  count ≤ oracle and pairs a subset; exact truncated values as kernel literals;
  drop T16, T19, T20 from T17.

### C4-F2 -- Plan says the corpus produces truncated reports; it never does (hardening, self-inflicted)

- **Where:** plan:96, 336-337 vs spec:163-168, T18.
- **Reproduction:** `gen.py`: truncated 0, count > 5: 0, non-zero 46.
- **Fix:** drop "and truncated" or add a lowered-cap pass under the C4-F1
  relation; add a floor on count > 5 (bigger SPELLING or more rows).

### C4-F3 -- Counter tests cannot catch per-pair enumeration within a key (hardening, pre-existing)

- **Where:** T12b, T12c; NM-R3.
- **What is wrong:** an implementation charging one inspection per row and
  binding but building all S×R pairs passes T12b and T12c in under a second.
  Sorting is n log n.
- **Fix:** count pair constructions in T12c (≤ 25 per key, 25 total), or run
  4,096×4,096 under a wall cap like `test_review_r5_t13b_wall_cap`.

### C4-F4 -- Truncation is unreachable with default limits (low, self-inflicted)

- **What is wrong:** a search runs only when `B` is non-empty, i.e. when
  production's `shared` is non-empty, after `_candidates` charged
  `probes += len(facts)` and `_join` one probe per binding (why_not.py:419,
  439-441). Inspections ≤ probes ≤ 200,000 = default cap, and the check runs
  before an inspection, so `near_miss_truncated` is always false on any request
  that does not exit 4.
- **Reproduction:** probes > inspections in every probe (T12b 300 > 200; T12c
  1,536 > 1,024).
- **Fix:** state that the cap guards lowered limits; tests lower it; or default
  it below `probes` if a reachable flag is wanted.

### C4-F5 -- Discovery cannot see raw-by-default API functions; `api.why_not` lacks a row (hardening, self-inflicted)

- **Where:** plan:348-357 vs plan:262, 107-108.
- **What is wrong:** `api.why_not`, `api.witness`, `api.replay` take neither
  `raw` nor `unredacted`; the "site without a row fails" guarantee misses them;
  `api.why_not` was not added by hand and gets no customer leak test. The five
  `unredacted` API functions are discovered but not named.
- **Fix:** add `api.why_not` to the known rows and NM2-C3; a fourth channel:
  every `gnd.api.__all__` callable has a row or is on an explicit
  no-population-values list; name the five.

### C4-F6 -- Inconsistent inspection wording; counter not observable (low, self-inflicted)

- **What is wrong:** plan:222-223 and NM-R3 say "eligible rows", spec:125 says
  "each row"; the counter lives on `_Walk`, not returned, not in `work`.
- **Fix:** "every row of the fact type" throughout; observe by bracketing the cap
  (2n untruncated, 2n−1 truncated); pin T12b/T12c fixtures with rows spelled
  differently from bindings (identical variants make the target derived).

### C4-F7 -- Smaller discrimination gaps (low; T1, T4 pre-existing; T11, T19, representatives self-inflicted)

- (a) T1 passes punctuation-before-NFKC and casefold-before-NFKC variants; add
  `℅` → `co` (`c/o` under punctuation-first).
- (b) T4 has no literal values and the oracle does not descend; pin count and
  pairs.
- (c) T11 should span two keys with interleaved canonical order.
- (d) T19 needs a named `_eligible_rows(atom, bound)` helper (step 1 returns
  before eligibility when `B` is empty) and a projection rule.
- (e) the representative of identity-equal values (`1`, `1.0`) is unspecified;
  row order changes the reported candidate. Pick first-seen or smallest
  canonical, same rule in the oracle, or compare by identity.
