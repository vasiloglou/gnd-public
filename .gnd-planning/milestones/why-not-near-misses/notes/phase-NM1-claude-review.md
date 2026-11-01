<!-- Retained review of the NM1 diff, 2026-11-01: one reviewer (a Claude subagent,
general-purpose, run from this session), full repository read access plus the
ability to run tests. EDITED: absolute machine paths were replaced with
<scratch>/ and <worktree>/; the body is otherwise verbatim. The disposition
follows the review. -->

# NM1 adversarial review (single reviewer)

Subject: the working-tree diff on `claude/issue-70-near-miss-plan` against `33c260e`
(src/gnd/witness/why_not.py, tests/why_not_oracle.py, tests/test_why_not_kernel.py,
tests/test_why_not_oracle.py, tests/support/pyrel_application_successors.py, and the untracked
evidence/NM1/dynamic-query-successor.json). Spec: notes/phase-NM1-spec.md r3 (approved).

Scratch dir (all outputs): `<scratch>/nm1-review/` (below: `$S`).
Every script runs from the worktree root as `PYTHONPATH=$PWD uv run python $S/<script>`.

**Bottom line: I found no blocking defect in the kernel.** The algorithm matches the spec, and
the exactness invariant, count semantics and global top-5 hold under proof and fuzzing. Every
finding is a test hole that lets a spec rule regress without notice, or a gap in the spec or record.

Gate status, measured: plan §9 NM1 row (`test_why_not_kernel`, `test_why_not_oracle`,
`test_public_why_not`, `test_why_not_anonymity`, `test_rf1_layering`, `test_rf6_query_policy`,
`test_gnd_arch`) all pass (119 + 171). The affected-consumers row passes (430). Unicode
database under `uv run`: 16.0.0 (Python 3.14.3).

---

## Findings

### R1 — hardening — tests/test_why_not_kernel.py (T12 at :938) / src/gnd/witness/why_not.py:293
**Claim.** Nothing tests standing rule "one counter serves every clause and descent level"
(Design, gate sweep). Mutant `reset_counter` resets `self.near_miss_inspections = 0` at every
`_near_misses` call, which turns the counter into one per blocker. All 45 NM1 tests still pass.
Every capped test (T12, T12b, T17b, T18b) has one atom blocker per walk. T18b runs only in rule
mode over single-clause generated rules.
**Repro.** `$S/mutants.py reset_counter` → `$S/mutants.out`: `45 passed`.
**Fix.** Add a literal test with two clauses, or a descent, both with atom blockers and a cap the
first blocker exhausts exactly. Expect the second blocker to report `near_miss_truncated: True,
near_miss_count: 0`. The T4 shape with `near_miss_inspections` = the top-level inspections works.

### R2 — hardening — tests (T11 :926, T12b in T17, T12c :961) / why_not.py:650
**Claim.** Nothing tests the sample side of the per-key "first 5 by canonical" selection.
Mutant `first_seen_top5` takes `list(group.values())[:5]` (insertion order) for samples and
survives. The only keys with more than 5 samples are in `spelled(n)`. Its bindings
`"acme"+"."*i` are inserted in canonical order already (`'"' < '.'`), so first-seen equals
canonical. The rows side is caught, because `"ACME!"` sorts before `"ACME"`. T12c asserts only
`len == 5`, not which pairs.
**Repro.** `$S/mutants.py first_seen_top5` → `45 passed`. The rows mutant
`first_seen_top5_rows` → fails at `T17[T12b]` (contrast).
**Fix.** Insert T12b's bindings in non-canonical order (e.g. reverse, or `"acme"+"!"*i`), or pin
T12c's 5 pairs as literals.

### R3 — hardening — tests/test_why_not_oracle.py:254 (`strip_near`), :270 (`compare_near`)
**Claim.** No test covers "Non-atom blockers ... are unchanged" with the flag on. `strip_near`
removes the three keys at every depth. `compare_near` asserts the keys are present on atom
blockers but never absent on negated, comparison or head blockers. Mutant: add the three keys
to every non-atom blocker when the flag is set. All 45 NM1 tests pass, although T18 visits
negated and comparison blockers. `$S/mutant_nonatom_check.py` confirms the mutant is live:
a negated blocker carries `near_miss_count`, `near_miss_truncated` and `near_misses`.
**Repro.** `$S/mutant_nonatom.py` → `$S/mutant_nonatom.out`: `45 passed`, then the live check line.
**Fix.** In `compare_near` (and T9), assert `not set(NEAR) & set(blocker)` for every non-atom
blocker. Better, strip only from atom blockers instead of at every depth.

### R4 — hardening — tests/test_why_not_oracle.py:347 (T18b), :250 floor
**Claim.** T18b's comparison rule never runs on content. At cap 3, all 15 truncated reports have
count 0 and no pairs, so `count ≤` and `pairs ⊆` hold trivially. The test admits this (F2) and
defers to T17b. T17b covers two hand-written fixtures only. Other caps over the same corpus
produce truncated reports with content.
**Repro.** `$S/coverage.py` → `$S/coverage.out`:
`cap 3 {'truncated': 15, 'truncated_with_pairs': 0}`, `cap 4/5/6 … 'truncated_with_pairs': 1`.
`$S/fuzz.py` (Unicode domain, caps 1..13, 1500 seeds) produced 182 truncated-with-pairs reports,
all within the rule.
**Fix.** Sweep caps (e.g. 3..8) in T18b, and add a floor on truncated reports with a non-zero
count. Note the spec text fixes cap 3, so record this as an implementation finding.

### R5 — hardening — tests/test_why_not_oracle.py:358 (T9)
**Claim.** T9 runs flag-on against flag-off only on the generated corpus and on the NM1 `CASES`.
It never runs on the WN1 named discriminators: multi-clause, derived/recursive descent,
identity duplicates, boolean/number constants, budget cases. It also never runs on the WN2
golden corpus (`tests/fixtures/why_not/cases.json`). Descent, multi-clause and row mode with
derived bodies therefore have no flag-on invariance check. No defect hides there: I measured
the full surface.
**Repro.** `$S/t9_everywhere.py` wraps `explain` so every existing call also runs with the flag
on. It compares modulo the three keys and requires the same exception type and text. Run over
the kernel, oracle, public why-not and repair-loop suites → `$S/t9_everywhere.out`:
`STATS {'calls': 2246, 'atom_blockers': 905, 'nonzero': 86, 'truncated': 17, 'mismatch': 0}`.
The one pytest failure is an artifact of the wrapper: it doubles a call-count assertion.
**Fix.** Run the T9 comparison over the named WN1 cases and the WN2 corpus. A thin parametrized
helper reusing `case()` and `cases.json` is enough.

### R6 — completeness — tests/test_why_not_oracle.py:299 (T17)
**Claim.** T17's exception list is "T12 at m-1, T16, T19, T19b, T20". The implementation also
leaves out T12c (512), T12b at n=200/400, and the T4 nested blocker. `compare_near` compares only
top-level clauses, and the generator never puts a derived atom in a body. The kernel agrees on
all of them, so this is coverage only.
**Repro.** `$S/coverage.py` → `spelled 200/400/512 … oracle-agrees`,
`T4 nested: kernel 1 True oracle 1`.
**Fix.** Add these to T17. Brute force at 512×512 takes a few seconds. Alternatively, record the
narrowing as an implementation finding.

### R7 — completeness — src/gnd/witness/why_not.py:598, :638
**Claim.** The spec diverges from the code, with no record. The spec says step 4 tests membership
"in `_eligible_rows`" and that "`_eligible_rows` is called for every atom blocker, including `B`
empty". The code never calls `_eligible_rows`, which only tests use (T19, T19b). `_near_misses`
calls the `_eligible` predicate and returns early when `B` is empty. The two are equivalent,
because `_eligible_rows` wraps the same predicate. Mutant `no_b_empty_return` also survives
(`$S/mutants.out`), so spec step 1, "no inspections" when `B` is empty, is untested. Removing
the early return would count inspections that no probe pays for. That breaks the "inspections ≤
charged probes" argument, because the join charges no per-binding probe when `shared` is empty.
**Repro.** `$S/mutants.py no_b_empty_return` → `45 passed`. Grep shows no non-test call of
`_eligible_rows`.
**Fix.** Record this in Implementation findings. Add a literal check: a walk whose only atom
blocker has `B` empty leaves `near_miss_inspections == 0`.

### R8 — completeness — notes/phase-NM1-spec.md "Implementation findings" / "Recorded at implementation"
**Claim.** The test code cites "NM1 finding F1" (canonical-minimum byte order picks `1.0`) and
"F2" (T18b carries no pairs). It also says the floors are "recorded in the NM1 phase record".
The spec's Implementation findings section is still empty, and no phase record exists in the
milestone directory. `unicodedata.unidata_version` (16.0.0 here) and the T18/T18b floors (46/15)
are also unrecorded, although the spec requires them.
**Repro.** `find .gnd-planning/milestones/why-not-near-misses -type f` shows no NM1 record. The
spec section reads "(recorded as found)".
**Fix.** Record F1, F2, R7's divergence, the floors and the Unicode version before close.

### R9 — completeness (owner note before NM3) — why_not.py:521 (`_samples`) vs :617 (`add`)
**Claim.** One blocker can show one binding group two ways. `samples` keeps the first-seen
representative (pre-existing `_samples`, order-dependent). `near_misses[].sample` keeps the
canonical minimum (D5). With bindings `n=1` then `n=1.0`, `samples` shows `{"n":1}` and the
near-miss sample shows `{"n":1.0}`. The spec allows this, but NM3 fixes the wire form and will
show both side by side.
**Repro.** `$S/coverage.py` → `samples: [{"m":"Acme","n":1}]`, `near_misses sample: {"m":"Acme","n":1.0}`.
**Fix.** No NM1 code change. Raise it for NM3, or document it.

---

## Categories checked with no defect found

1. **Spec conformance of `_near_misses`.** Checked:
   - Bindings are inspected before rows.
   - The cap is checked (`==`) before each inspection, and every row counts as an inspection,
     eligible or not.
   - The counter lives on `_Walk` and is shared through `self.explain` in descent; only the
     tests miss it (R1).
   - A truncation during bindings skips rows, so the count is 0 (D4a).
   - The count is |distinct identity groups| × |distinct identity groups| per key.
   - At most 5×5 pairs are formed per key, then sorted globally by
     `(canonical(sample), canonical(candidate))` and cut to 5.
   - `roles` lists the differing bound roles in sorted order; a repeated bound variable gives one
     component per role.

   **Global top-5 proof:** suppose a pair (s, c) is globally in the top 5, but s is 6th or later
   in its key. Then the 5 smaller samples s1..s5 of that key pair with c, giving 5 strictly
   smaller pairs: a contradiction. The same argument holds for c. Strictness holds because a
   canonical encoding identifies an identity group (1 and 1.0, or -0.0 and 0, are one group).
   The work is linear: at most 25·(#keys) pairs, with #keys ≤ min(#sample groups, #row groups).
2. **Exactness invariant.** Proof: a row that passes `_eligible` and equals a binding by identity
   at every bound role also passes production's in-row check for repeated bound variables. It
   is therefore a production candidate whose `shared` key matches, so the join would not be
   empty. `self.facts` is the same object the join used, and `bound` and `shared` derive from
   `previous[0]` in both. Probed with 1 vs 1.0, `True`, strings whose normalized form is `None`,
   row-mode head seeds, and a mix of repeated bound variable, constant and repeated free
   variable (`$S/exactness.py` → `$S/exactness.out`; all agree with the oracle, none raise).
   Fuzzing gave no `WhyNotInternalError`: 1500 seeds over a Unicode domain (`…`, full-width,
   `ß`, `℅`, combining vs precomposed, `Å` vs `Å`), both modes, caps 1..13, 12,439 blockers
   (`$S/fuzz.out`). Opaque values are refused before the walk (`why_not.py:252-258`).
   Derived-row values are wire scalars (`terms.materialize_scalar`), so `_canonical` cannot
   raise on them.
3. **Keys vs the pair definition.** Key equality ⇔ near on every role. `("x", id)` keys are equal
   only when identities are equal. `("n", N)` keys are equal only when N is equal and not None.
   A string with N = None and a non-string never share a key with an `"n"` key. `True` gives
   `("x", ("boolean", True))`, which differs from `1`. 1 and 1.0 hash and compare equal inside
   the identity tuple. The oracle's `near()` is the same predicate, stated without keys.
4. **Flag-on/off.** Over 2246 existing calls, including the WN2 goldens through the service,
   flag-on equals flag-off modulo the three keys, with zero exception mismatches (R5 numbers).
   `_near_misses` never calls `budget.charge`, so `work` and `WhyNotWorkError` cannot change. At
   default limits, inspections ≤ probes ≤ 200000 = cap, and `charge` raises above the limit, so
   truncation at default limits is unreachable. With the flag off, the only change is the
   `_Walk` keyword; the golden suites pass unedited.
5. **Test weaknesses.** See R1–R4 and R6. T16 and the D3 test are real negative tests through a
   bare `_Walk`. T19 does compare `_eligible` (through `_eligible_rows`) with production,
   with ≥300 atoms.
6. **Oracle independence.** `tests/why_not_oracle.py` imports only `json`, `unicodedata` and
   `fractions`. Its pair condition is a per-role brute force with `near()`, not keys. Its
   eligibility, identity (`Fraction`-based) and canonical encoding are its own. It restates the
   spec's representative rule (canonical minimum), which is unavoidable. It never sees
   truncation, so it cannot mirror the kernel's cap logic.
7. **Evidence file.** `predecessor_sha256` matches the WN-merge file
   (`bdc3ebd6…aa2df1`), and `tests/test_rf6_query_policy.py` passes with it.

## Disposition (phase author, 2026-11-01)

Each finding was reproduced in this session before disposition. The reviewer's
mutation harness was rerun against the pre-fix tests. `reset_counter`,
`first_seen_top5` and `no_b_empty_return` passed all 45 NM1 tests, and the
non-atom mutant was live. No finding is blocking, and no source line changed.

| Finding | Triage | Disposition | Regression test, observed red against its mutant |
|---|---|---|---|
| R1 | hardening | fixed (test) | `test_nm1_review_r1_one_counter_serves_the_whole_walk`, red under `reset_counter` |
| R2 | hardening | fixed (test) | `test_nm1_review_r2_samples_shown_are_the_canonical_first_five`, red under `first_seen_top5` and `top1_samples` |
| R3 | hardening | fixed (test) | `test_nm1_review_r3_non_atom_blockers_are_unchanged` (negated, comparison, head-bind), plus a misplaced-key assertion in `compare_near` and T9; 7 tests red under the non-atom mutant |
| R4 | hardening | fixed (test) | `test_nm1_review_r4_truncated_reports_with_content_are_subsets`, caps 4 to 6, floor 3 (measured 3 on the SPELLING corpus). T18b is kept as approved. T17b already covered hand-written content (F2). |
| R5 | hardening | fixed for the WN1 named cases | `test_nm1_review_r5_flag_is_inert_on_the_wn1_named_cases` over `AGREEMENT` and `_more_agreement()`, covering descent, recursion, multi-clause and refusals. The WN2 golden corpus is not added. NM3 replaces those payloads with schema 2 and re-pins them, so a flag-on census there belongs to NM3. |
| R6 | completeness | partly fixed | `test_nm1_review_r6_larger_spelled_cases_agree` (n = 200, 400). T12c (512) is left out of the oracle run because of cost. The nested T4 blocker is pinned as a kernel literal, and the oracle has no descent. |
| R7 | completeness | fixed (test) plus record | `test_nm1_review_r7_unbound_blocker_inspects_nothing`, red under `no_b_empty_return`. The spec's "uses `_eligible_rows`" is met by one shared predicate, `_Walk._eligible`, that both `_eligible_rows` (T19) and the search call. Recorded as finding F4. |
| R8 | completeness | already resolved | Findings F1 to F3 and the recorded values were appended to the spec while the review ran; the phase record follows. |
| R9 | completeness, NM3 | deferred | Open question for NM3: `samples` keeps the first-seen value and `near_misses` keeps the canonical minimum, so one blocker can show `1` and `1.0` for the same group. NM3 decides whether the view aligns them. |

One reviewer is one reviewer.
