# WN1 diff review

Retained text of the single reviewer's returned report (one local reviewer
agent; one reviewer is one reviewer). Local edits: scratch paths read
`<scratch>`.

**Scope.** I read all of `src/gnd/witness/why_not.py`, the five new test and support files, the evidence JSON, the tracked diffs, and spec §§1-11 plus the appended gate. On the production side I read `_joined_bindings`, `_joined_atom_candidates`, `_apply_negation`, `_evaluate_derivations_dispatch` (including the legacy and exact split) and `values._identity_key`. I ran the focused suite: the why_not tests plus rf1, rf4 and rf6 gave 1012 passed in 157 s. I ran 13 probes and a mutation harness that loads mutated copies of the module from scratch, under `<scratch>/wn1-review/` (`p1_samples.py` … `p9_trace.py`, `mutrun.py`, `mut/`). Probes ran with `PYTHONDONTWRITEBYTECODE=1 uv run python -I <probe>`. I wrote nothing in the repository. Not done: the T15 parity files, the broad suite, and any test with references.

## Claims checked and found true
- **Status always agrees.** `p4_agree.py 0 600` covers 1894 cases: the T9 generator, plus a semiderived `m` with asserted rows, plus negation over derived `m`, each in rule and row mode. Result: 0 mismatches against `check_status` (which covers both the legacy and exact paths), 0 against the oracle, 0 raises.
- **Opaque values.** An opaque value in a negated base gives `unsupported`, and `check` agrees.
- **Comparison order (`p7_guard.py`).** I tried guard-then-div orders: clause-local, root div with a clause guard, root guard with a clause div, and negate before div. Status matches `check`, and the walk never raises `WhyNotInternalError`.
- **Trace isolation (`p9_trace.py`).** The charge-only trace is reset, and the walk phase sends nothing to an outer trace (blocked target, computed head, descent).
- **T13 figures.** They reproduce exactly, and 96,722 probes decomposes correctly.
- **Identity.** A kernel without binding dedup is caught (M4). A `_binding_key` that used Python `==` cannot be told apart on any input validation lets through, because Boolean/Number variable sharing is refused.
- **The oracle is independent.** It has no `gnd` import and its own Fraction identity.
- **Layer and RF6 tests pass.** No forbidden `"roles"` or `"fact_types"` subscript appears.
- **Other mutants killed:** cycle disabled, unsorted samples, `sample_count`, cell charge, stop order, non-atom reads and samples.

## Findings

### WN1-R1 — walk work is not bounded by the charged counters (blocking, high confidence)
**Where:** `why_not.py:379-384` (product path) and `:390-396` (indexed path).

**What is wrong:** Each inner-loop pair is charged only when `_store` sees a new binding key. Populations may hold duplicate rows (the corpus uses `[1, 1.0, 1, 2]`). With a duplicate-heavy disconnected or bucketed atom, the walk runs P×D Python iterations but charges only P joins. Production charges every probed pair (`extensions.py:404`, `:763`), so the bridge keeps the pre-evaluation cheap. This breaks standing rule 2 and §6.7.

**Reproduction:** `p2_dups.py N D`. Body `a1(x), a3(z), a4(x,z)`, where `a1` has N distinct rows, `a3` has D copies of `{"z":"k"}`, and `a4` is empty.
- `1000 1000` gives `work {'pre_joins': 1000, 'joins': 2000, 'probes': 3000, 'binding_cells': 3000}` in 2.98 s.
- `3000 3000` gives `joins 6000, probes 9000` in 26.03 s.
- So 30000×30000 stays far below every ceiling (60k joins, 90k probes) but needs about 9e8 iterations, roughly 40+ minutes. I stopped that run.

**Fix:** Dedupe candidates under `_binding_key` after the charged scan in `_candidates`. Then every pair in both paths yields a distinct stored binding, which is charged. Alternatively, charge `probes` per pair. Add a T13 case with duplicate rows.

### WN1-R2 — samples are deduplicated by canonical JSON, not identity; the oracle disagrees (hardening, high)
**Where:** `why_not.py:465-470`.

**What is wrong:** `{v:1}` and `{v:1.0}` are one identity but two canonical keys. They take two of the five sample slots and can also change `grounded[0]`. The oracle deduplicates by identity, so T9's "full blocker record equals the oracle's" fails on a valid input. The corpus never generates floats, which is why this escaped.

**Reproduction:** `p1_samples.py` with `r(v,k)` rows `{1,"a"}, {1.0,"b"}` and `s` empty prints `kernel samples: [{'v': 1.0}, {'v': 1}] sample_count 2`, then `ORACLE DISAGREES`.

**Fix:** Key `seen` by the identity of the projected sample and sort by canonical JSON. Add a Number-domain generator or discriminator with mixed `1`/`1.0`.

### WN1-R3 — totality: non-finite row values raise a bare ValueError (hardening, high)
**Where:** `why_not.py:276` (`_identity_row` on the claimed row). `validate_targets` accepts NaN and inf.

**Reproduction:** `p3_edges.py` prints:
- `row nan -> RAISES ValueError non-finite values have no identity token`
- `row inf -> RAISES ValueError non-finite values have no identity token`

Python's `json.loads` accepts `NaN`, so a JSON input can carry these values.

**Fix:** Refuse non-finite row values as `WhyNotInputError("malformed row")` during row validation, and add the case to T14.

### WN1-R4 — depth precedence is off by one against §6.5 (hardening, high)
**Where:** `why_not.py:533-536`.

**What is wrong:** §6.5 says `proof_depth` "can only breach when a caller lowers it below 8". At `proof_depth=8` the depth-8 stop should be recorded, but the code raises.

**Reproduction:** `p6_depth.py` on `chain(10)` prints `8 RAISES WhyNotWorkError proof_depth ceiling` and `9 completes`.

**Fix:** Test `MAX_DESCENT` before `proof_depth`, or use `>=` semantics consistent with the spec, and pin `proof_depth=8` in T12.

### WN1-R5 — branch tests that cannot fail (completeness, high)
These mutants survive the kernel and oracle suites (`mutrun.py`, 51 passed each):
- **M1:** sample cap 5 changed to 6. No test has more than 5 distinct samples.
- **M2:** descent from `grounded[-1]` instead of the first grounded row in canonical order.
- **M6:** `asserted_not_read` true whenever any asserted row exists. Only the positive case is tested, and T9 excludes this key.
- **M7:** the per-binding negation probe charge removed.
- **M11:** opaque-row stripping removed. This mutant appears equivalent; the evaluation does not need the strip, so T14 "outside" does not pin it.

Also missing from the tests:
- T8 does not run the T9, T10 or T14 cases against `check`, as the spec requires (R-claim 1 holds only by my probe).
- T15b covers only a `derived` target, so the walk phase never runs under an outer trace.
- T12 asserts `> limit`, not `limit + 1`.
- The T13 10 s wall cap is never asserted.
- For non-atom blockers the oracle compares only kind, index and count, not `reads` or `samples`. It also never emits `head` steps.
- The "declared order differs" census reimplements the evaluator's rule instead of computing it from production, as §6.6 allows.

**Fix:** Add the missing cases.

### WN1-R6 — the anonymity scan matches whole tokens only (hardening, medium)
**Where:** `tests/test_why_not_anonymity.py:28-31`.

**What is wrong:** Compounds of a forbidden name escape. With the planted control:
- `zz-planted-name-v2` → False
- `zz-planted-name_fork` → False
- `ZzPlantedName` → False
- `zz-planted-name.git` → True

The negative control also exercises `_digests` only, not `_added_files`.

**Fix:** Also test digests of every hyphen/underscore-delimited sub-run of each token, and of the punctuation-stripped form. Plant the control through the same file-listing path.

### WN1-R7 — model read outside the §6.8 list (completeness, low)
**Where:** `why_not.py:141`, `model.model_dump()` passed to `derivation_dependencies`.

**What is wrong:** §6.8 lists the only allowed model reads, and this is not one. The rf6 tests do not flag it.

**Fix:** Build the dependency document from `ModelIndex.iter_fact_types_shared()`, as `_build_incremental_context` does, or amend the spec append-only.
