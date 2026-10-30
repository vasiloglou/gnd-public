# Reader 4 -- test design, falsifiability and the end-to-end demonstration

Retained text of the reader's returned report. No local edits.

Digests matched: plan `77928fb2…cc70` and WN1 spec `cbc99f26…1f03`, both as expected.

**Verdict: request-changes**

**Scope.** I read the whole plan r1 and the whole WN1 spec r1, issue #66, `standing-rules.md` (the time-bound, branch-case, half-class and fixture-falsifiability rules) and `spec-note-contract.md` §8. I checked the spec against the current code: `extensions.py` (join, negation, comparisons, head projection, `_witness_charge`), `values.identity_key`, `witness/producer.py`, `witness/types.py`, the negation-safety validator, and the timing tests (`test_witness_timing_measurement.py`, `test_public_classification_scaling.py`, `test_model_guarded.py`). I ran one small probe with `uv run python`. I wrote nothing in the repository, and my scratch directory holds no files.

## Findings

### R4-F1 -- blocking, high confidence: two work loops are never charged, so T12/T13 cannot catch them
**Where:** spec lines 63-64 (standing rule 2), 191-194 (§6.6), 37-38 and 42-44 (WN-R1/WN-R2); plan line 101 (WN-R4).

**What is wrong.**
- **Probes have no ceiling.** Standing rule 2 says work is "charged per binding produced and per candidate probed". §6.6 only charges bindings produced (against `joins`) and cells stored (against `binding_cells`). `WitnessLimits` (`witness/types.py:15-26`) has no probe field. So a connected join where every probe misses produces 0 bindings and pays 0 charge, while doing |B(k-1)| × |candidates| work. That is the quadratic-under-the-cap case standing rule 2 exists to stop.
- **Derived body predicates are evaluated free.** Their relations come from `_evaluate_stratified_extensions(..., exact=True)`. That function charges work only through `_witness_charge`, which reads `_WITNESS_TRACE` (`extensions.py:457-460`). `witness` sets that trace before it evaluates (`producer.py:211-216`), but WN-R1 says why-not does not set it. So the derived-body evaluation runs with no charge against why-not's budget.

**How verified.** Read the code above.

**Fix.**
- Name the ceiling that probes charge, or require an indexed join so probes are bounded by the bindings produced.
- Charge the stratified evaluation, for example through a charge-only trace object, or say which existing bound covers it.
- Add T13 variants: (a) a large zero-output connected join; (b) a blocker whose cost sits inside a derived body predicate.

### R4-F2 -- blocking, high confidence: T13 cannot fail
**Where:** spec line 235.

**What is wrong.** T13 expects "completes or raises within a fixed wall bound". Either outcome passes, and the bound is never stated. The repository's timing tests lean on deterministic counters:
- `test_public_classification_scaling.py:37-43` asserts a work counter (`<= 8*160`) and keeps only a loose wall bound beside it.
- `test_witness_timing_measurement.py` replaces `time.monotonic` with a tick counter.

**Fix.**
- Pick fixture sizes so the outcome is fixed: e.g. four disconnected atoms of 18 rows each gives 104,976 > `joins=100000`. Assert `WhyNotWorkError` and that the work counter stops at exactly `joins+1`.
- Add a just-under-ceiling twin that completes with counts equal to the exact product.
- Assert the counters grow linearly across two sizes. Keep any wall bound secondary and generous.
- Name the file where the "measured cost recorded" result (standing rule 6) is kept.

### R4-F3 -- blocking, high confidence: the T9 oracle corpus may lack the cases that tell right from wrong
**Where:** spec lines 117-120 and 133-135 (distinct counts), 182-187 (§6.5), 231 (T9); plan lines 75-78 (predicate 1).

**What is wrong.**
- **Bag vs distinct.** The production join returns a bag, not a set; duplicates are removed only at head projection (`extensions.py:952-958`). My probe: `_joined_atom_candidates` over 5 rows `{'a','a',1,1.0,True}` returned 5 candidates, which are 3 distinct bindings under `identity_key`. A naive Python set gives 2, because `True == 1` in Python.
- **Repeated variables cannot cause the difference.** Validation makes every atom bind every role (`_validation.py:4057`). So "rows vs distinct bindings" only differs on identity-duplicate rows (exact duplicates, or `1` vs `1.0`).
- **Ordering.** No named case puts the declared-order blocker somewhere other than where the production reordering (`_joined_bindings`, `extensions.py:710-725`) would put it.
- **Seeds alone may miss all of these.** A seeded corpus can lack every one of these cases, and T9 would still pass.
- **Shared identity code.** §6.5 only bans imports from `gnd.extensions`. The oracle could import `gnd.values.identity_key` and share the kernel's identity rule.
- **Partial comparison.** T9 compares "every count and blocker". It does not say whether `bound_roles`, `free_roles`, `sample_bindings` and their canonical order are compared, and those are what the host acts on.

**Fix.**
- Add named, hand-built discriminators: identity-duplicate rows (`1`/`1.0`, exact duplicates); `True`/`1`/`"1"` in one column; a body where atom 1 and atom 2 are disconnected and atom 3 bridges them (declared and production order differ); a constant role; a repeated variable; a variable reused across atoms.
- Add a census assertion that the generated corpus contains each discriminator.
- Give the oracle its own identity table (bool / number with exact int-float equality / string).
- Compare the full blocker record, samples included.

### R4-F4 -- hardening, high confidence: branches declared with no case that can fail them
**Where:** spec lines 113-131, 168-170, 172-180, 223-244.

**What is wrong.**
1. **Step kind `head`.** With variable heads, row mode binds head values up front, so a `head` step can only reach 0 through a computed head term in row mode. T7 names no such case, but the branch walk credits `head` to T7.
2. **`head-bind`.** It has two sub-branches: two head roles binding one variable to different values, and a constant head term mismatch. T7 covers one.
3. **Top-level status rule** ("`derived` if any clause is `derived`"). No case has one derived clause next to a blocked one, so "any" and "every" read the same on T6.
4. **`unavailable`.** §5 (line 85) says the top status is `blocked` only when every clause has a zero step. §6.3 maps an `unavailable` clause to `blocked` as well. No case covers single-clause `unavailable`, or `unavailable` next to `derived`.
5. **Dead branch.** "A not-fully-bound negated atom keeps the binding" (line 122) cannot happen on a validated model: `_rule_derivation_negate_unbound` (`_validation.py:4330`) rejects it.
6. **Ceilings.** T12 is one case covering three ceilings (`joins`, `binding_cells`, descent depth) plus the budget shared with descent.
7. **Descent returning `derived`.** That would mean the kernel disagrees with itself, and no case checks for it.
8. **Computed head terms in rule mode** are declared supported and have no case.

**Fix.** Add one case per item. Delete item 5, or state it is unreachable and test it on a direct kernel call. Settle the §5 vs §6.3 wording.

### R4-F5 -- hardening, medium confidence: T8's agreement predicate is undefined on three reachable inputs
**Where:** spec line 230 (T8), line 213 (D5).

**What is wrong.**
- **Unavailable comparisons.** In production, one unavailable comparison makes the whole relation `RelationUnavailable` (`extensions.py:1705-1708`). The kernel decides per clause, so "derived iff in the exact extension" has no defined expectation there.
- **Semiderived targets.** D5 explains an asserted-but-underived row as blocked. T8's phrase "in the exact extension" does not say whether asserted rows count.
- **Derived predicates in `covers`.** A derived body predicate the population `covers` is read from its asserted rows, not its rule (`extensions.py:2590-2594`). T8 and T10 need a fixture for that case.

**Fix.** Define T8 as "rule-derived rows", spell out the expectation when the relation is unavailable, and add the `covers` and semiderived fixtures.

### R4-F6 -- blocking, high confidence: WN3 can pass without proving the reporter's outcome
**Where:** plan lines 84-88 (predicate 4), 266-271 (WN3-C1/C2).

**What is wrong.**
- **Hand-written repair.** "adding one fact built from the `--raw` sample" does not stop the test from writing the repair fact by hand. A test that adds the right fact derives the claim whatever why-not said.
- **Free roles.** Nothing says where free-role values come from.
- **No negative controls.** Nothing shows that the named predicate and bound values were what mattered.
- **One gap only.** The reporter loops. A single-gap example never shows that a second gap is named after the first is repaired.

**Fix.** Require that WN3's test:
- builds the fact only from payload fields (`fact_type`, the per-role map and raw values), plus an explicit "extracted" table for free roles only;
- runs in row mode on the claimed row, so head constants ground the blocker;
- asserts the `check` verdict variant and that the row is absent before repair;
- includes negative controls: the same fact on the previous step's predicate, and the right predicate with a wrong bound value, both leaving the claim underived;
- covers a two-gap population, where why-not names gap 2 after gap 1 is repaired and returns `derived` (exit 2) after both;
- ends with `witness` exit 0.

### R4-F7 -- hardening, high confidence: the payload does not yet let the host build the missing fact
**Where:** spec lines 137-143; plan lines 187-194.

**What is wrong.**
- **Samples are keyed wrong for the host.** `sample_bindings` are "restricted to the variables the blocking atom reads", so they are keyed by variable and leave out constant roles.
- **Roles are bare names.** `bound_roles`/`free_roles` give role names only. A host cannot map role to value without re-parsing the model, and with redaction it cannot tell constant from variable.
- **"Done" is ambiguous.** The payload never says that later steps were not computed, so further gaps may remain.

**Fix.**
- Add a per-role term map `{role: {"variable": "$w"} | {"constant": <redacted|raw>}}` and a `ground` flag.
- Key raw samples by role.
- Add `"steps_after_blocker": "not-evaluated"`.
- Test both redacted and `--raw` forms in WN2-C2.

### R4-F8 -- completeness, medium confidence: completion predicates and WN-R1 lack failing gates
**Where:** plan lines 89-90 and 293-295; spec line 237 (T15), lines 36-38.

**What is wrong.**
- **Predicate 5** ("every new loop … has a time-bound test") maps only to WN1-C5. WN2 adds loops too: view rendering, schema validation, target intake.
- **T15** ("existing tests pass unmodified") cannot fail on the WN-R1 promise that the kernel does not set `_WITNESS_TRACE`.
- **Predicate 1** is only falsifiable once R4-F3 is fixed.

**Fix.**
- Map predicate 5 to a WN2 time-bound gate as well.
- Add a T15b: call `explain` under an active trace and assert that its charges and rows are unchanged.

### Not verified
I did not check whether population loading accepts exact-duplicate rows. The `1`/`1.0` duplicate in R4-F3 reaches the bag-vs-distinct case either way.
