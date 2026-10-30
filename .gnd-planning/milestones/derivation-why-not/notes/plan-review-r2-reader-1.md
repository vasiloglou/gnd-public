# Round 2 reader 1 -- correctness against production semantics

Retained text of the reader's returned report. Local edits: scratch paths read
`<scratch>`.

Digests: plan `b0308e35…630e` and WN1 spec `d1c87cb1…6f69` both match.

**Verdict: request-changes**

**Scope.** I read the r2 spec in full, the plan's p1-A/B/C passages, the r1 disposition and my round-1 note. In `src/gnd/extensions.py` I re-read:
- `_evaluate_stratified_extensions`: the partial path, the exact clause loop, and the propagation and unavailable sites (1640-1760);
- `_prepared_stratified`, `_joined_bindings`, `_component_product` and every `_witness_charge`/`_WITNESS_TRACE` site;
- `_base_relations`, `_derivation_obligation`, `_exact_derivation_obligation`, `_evaluate_derivations_dispatch` and `constraint_view_legacy`.

I also read `witness/producer.produce_witness` and `witness/io.support_closure`. Probes ran with `uv run python -I`. The scripts are in `<scratch>/r2-reader1/`: `probe_a.py`, `probe_b.py`, `probe_c.py` and `probe_t13.py`.

**Your specific questions.**
- **Does the trace change results?** No. `probe_a` gives identical extensions and unavailable entries with and without a charge-only trace, on both the exact and the partial path. Setting the trace only bypasses the scope cache and incremental reuse.
- **Does the pre-evaluation classify like check?** It reproduces check's `unavailable` classification, including through propagation. The two exceptions are R1-2-F2 and R1-F3 below.
- **Is a descent returning `derived` really an internal defect?** Yes, I found no counterexample. A zero count at a ground atom means that row is absent from P's production extension under `_identity_key`. Descent re-evaluates P's sub-closure, which reaches the same stratified fixpoint. One caveat: P with a string rule returns `unsupported`, not `derived` (see F5).

## Round-1 findings

| ID | Status | Evidence |
|---|---|---|
| R1-F1 | resolved | §6.2 steps 3-4 take `unavailable` and `derived` from production in both modes; T1 cases (a)-(e) plus the two-clause case |
| R1-F2 | resolved | Propagation fixes the target's `unavailable` entry before any walk, and step 5 says no relation is read as empty |
| R1-F3 | partly | Closure-wide `opaque-value` was added, but two gaps remain. (1) The scan misses asserted opaque cells (R1-2-F2). (2) An opaque cell outside the closure still switches the pre-evaluation to the partial path: `probe_a` returns `_PartialExtensions` and 8 charges against 2 for the identical clean case. Check instead strips opaque rows and takes the exact path. |
| R1-F4 | partly | A charge-only trace was added, but it charges bindings only, and the shared budget breaks T13 (R1-2-F1, R1-2-F3) |
| R1-F5 | resolved | Cycles are keyed on (predicate, row); descent is ground-only; plan lines 217-223 now agree with §6.5 |
| R1-F6 | resolved | The §6.6 oracle owns its identity, computes derived predicates by naive fixpoint, imports no `extensions`/`terms`/`values`, and uses literal operators only |
| R1-F7 | partly | The unreachable negation branch, `iter_derivation_clauses` and the identity are now named. The string-rule body predicate is read as base in §6.1, but §6.5 still descends into it (R1-2-F5). |

## New findings

### R1-2-F1 -- blocking, high, self-inflicted. T13(a)/(b) contradict the shared budget

**Where:** §6.7 ("adds to the shared budget"); §8 T13(a), (b); D1.

**What is wrong.** T13 assumes the walk alone fills the `joins` budget, but the pre-evaluation already does production's full product. `probe_t13` uses four disconnected one-role atoms and a `where` that removes every binding:

| Rows per atom | Pre-evaluation charges | Walk bindings |
|---|---|---|
| 17 | 88,791 | 88,740 |
| 18 | 111,204 | 111,150 |

- **T13(b):** the 17-row twin totals about 177.5k under a shared budget, so it breaches. It cannot "complete with the exact product".
- **T13(a):** the 18-row breach happens inside the pre-evaluation, so the case never tests the walk's counter.
- **D1:** its cost argument ("declared order … exit 4 sooner") ignores that production enumerates the product first.

**Fix.** Use separate ceilings for the pre-evaluation and the walk, or define the budget as their sum and recompute every T13 figure from measured values. Name which counter the pre-evaluation charges.

### R1-2-F2 -- blocking, medium-high, self-inflicted. The opaque scan reads the wrong relations

**Where:** §6.1, last row; §6.2 step 1; plan line 197.

**What is wrong.** Check builds its opaque sources from `population.facts`, which includes the asserted rows of derived fact types. `_base_relations` drops the asserted rows of every structured-rule fact type. A scan over "relations in the closure" therefore misses opaque claimed rows.

**How verified.** `probe_b` has a derived `ok` with the claim `{"amount": {"$opaque": …}}`:
- check returns `ok unchecked opaque-value`;
- `_base_relations` contains no opaque cell;
- the pre-evaluation derives `ok(x, 1.0)`, so why-not would answer `derived`.

**Fix.** Scan `population.facts` (and reference facts) for every fact type in the closure, the target included, exactly as `_evaluate_derivations_dispatch` does. Add a T14 case. This is also the natural point to strip opaque rows outside the closure before building relations, which closes R1-F3's partial-path remainder.

### R1-2-F3 -- hardening, high, self-inflicted. Pre-evaluation charging is overstated

**Where:** spec §4 rule 2; plan WN-R4 ("bindings, probes and cells … including the pre-evaluation").

**What is wrong.** `_witness_charge` is called only at four sites: `extensions.py:404`, `:737`, `:763` and `:872`. Those cover bindings in joins, products and partial joins. Candidate scans, negation index builds and probes, `where` evaluation and head cells inside the pre-evaluation are never charged.

**Fix.** Say the pre-evaluation is bounded in bindings only, as `witness` is. Drop "probes and cells" for that stage.

### R1-2-F4 -- hardening, high, self-inflicted. D6 misstates check for semiderived targets

**Where:** §7 D6.

**What is wrong.** Unsound surplus is reported only when `derivation == "derived"` (`extensions.py:2496`).
- `probe_a`: a semiderived `ok` with an asserted, underived row `z` passes check with no findings. It is not `derived-extension-unsound`.
- `probe_c`: dependents never read asserted semiderived rows, because `_base_relations` drops them. `q :- p` with `p(z)` asserted gives `q(z)` unsound. Why-not will then block at `p` with sample `z` and descend into `p`'s rule, even though the population asserts `p(z)`.

**Fix.** Correct D6. State in the WN2 doc that asserted semiderived rows are invisible to dependent rules. Add that fixture to T8/T10, and optionally flag "asserted but not read" on the blocker.

### R1-2-F5 -- completeness, high, self-inflicted. Wrong `covers` premise; closure and descent edges

**Where:** T8; §6.1; §6.2 step 2; §6.5.

- **The T8 `covers` fixture rests on a false premise.** "A derived body predicate read from asserted rows" never happens in derivation evaluation: `_base_relations` drops those rows whatever `covers` says. The covers-dependent read exists only in `constraint_view_legacy`. Separately, an uncovered unavailable target is `unchecked-not-covered` in check (`:2633`), while why-not answers `unavailable`. State that why-not ignores `covers`.
- **The closure may omit the target.** `heads=closure` must include the target, as witness's `support_closure` does. A non-recursive target's transitive dependencies do not include the target itself.
- **Descent ignores the string-rule rule.** §6.5's trigger, "derived or semiderived predicate", still descends into a string-rule predicate that §6.1 reads as base. That descent returns `unsupported rule-opaque`. Exclude it and set `derivation: base` on its blocker.

**Fix:** reword T8 and §6.1/§6.2 as above, and exclude string-rule predicates from the §6.5 trigger.
