# Close review, reader 1: correctness against production semantics

Retained text of the reader's returned report (one of four local close
readers, WN-D8). Local edits: scratch paths read `<scratch>`.

**Scope.** I read `src/gnd/witness/why_not.py` in full, plus the why-not diffs in `service.py`, `cli.py`, `view.py` and `api.py`. I read `docs/reference/why-not.md`, and the status-first, blocking-step and exit sections of the plan. On the production side I read `_evaluate_stratified_extensions`, `_evaluate_derivations_dispatch`, `_python_extension_calculator`, `_clause_bindings`/`_apply_negation`/`_joined_atom_candidates`, `iter_derivation_clauses`, `derivation_dependencies`, `bind_population` and `checker.check`'s partial-opaque switch.

I wrote and ran these probes under `<scratch>/close-r1/`:
- `fuzz.py`: a differential fuzz of random two-layer models. It covers constants, repeated variables, negation, comparisons, computed `add` heads, multiple clauses, semiderived with asserted rows, rule and every row mode. It ran 3,200 iterations over 5 seeds, giving about 4,800 explain calls against the production extension.
- `opaque.py`, `datehead.py`, `agg.py`.

I did not run the full suite, the v71 corpus or docs builds. No repository files were touched.

**Verdict: request-changes.** There is one blocking crash.

## Claims checked and found true
- **Fuzz agreement.** Status agreed with the production extension in every fuzz case: about 3,960 blocked, 380 derived and 0 disagreements. There were no `WhyNotInternalError` and no other exceptions.
- **Clause semantics match production.** Negation happens after all positive atoms, and production's "unresolvable binding survives" cannot arise because the validator rejects unbound negation variables. Comparisons are filtered in sequence, which is equivalent to production's per-binding short-circuit. The root `where` comes before the clause `where`, as `iter_derivation_clauses` presents it. Head values pass through `evaluate_term` and `materialize_scalar`. Identity follows `_identity_key`/`_identity_token`, and 1 and 1.0 count as one value.
- **Grounded atoms and disconnected components** reduce to the same product that production's `_component_product` builds.
- **Opaque handling matches check.** Opaque values only in asserted rows of a semiderived dependency give `unsupported` from both why-not and check's `opaque-value` verdict. Opaque values outside the closure give the same status as check (derived, blocked, derived). The closure test is equivalent to check's `affected` set. Default `check` does not take the partial path, and why-not's stripping mirrors that.
- **Engine choice does not matter.** Check's legacy, non-exact calculator and the stratified exact calculator agree on every model the validator admits. Date-literal heads are refused by validation ("temporal terms are supported only in guarded comparison operands").
- **References.** `bind_population` refusals are `ReferenceInputError(ValueError)`, so they become exit 3. The CLI binds from `--reference-root`, or from the model's directory by default, exactly as witness and check do.
- **Unavailability.** It propagates per clause to every dependent, so a descent can never reach an unavailable relation while the parent is available.

## C1-1 — Descent into an aggregate-ruled fact type crashes with `WhyNotInternalError` (blocking, high)

**Where.** In `src/gnd/witness/why_not.py`, `_atom_blocker` labels any dict-ruled fact type `derived`/`semiderived`, and `_descend` then calls `_Walk.explain` on it. `_Walk.explain` and `_clause` never look at `aggregate`; only the top-level `explain()` scans for it, and only in the target's own clauses. `src/gnd/witness/service.py` `why_not` does not catch `RuntimeError`.

**What is wrong.** When a blocker atom names an aggregate-derived fact type and its row is ground, the nested row-mode walk ignores the aggregate:
- the seed binds `$n` from the claimed row;
- the body joins;
- the head reproduces the claimed row.

The walk therefore "walks to a non-empty end" and raises `WhyNotInternalError`. Through the CLI and `gnd.api.why_not` this is an uncaught traceback with exit 1, on a valid model where `gnd check` decides cleanly. The reference page promises descent for "a derived or semiderived fact type with a structured rule", which includes aggregates, and the schema's `descent_stopped` enum has no value for this case. Golden g5 only covers an aggregate in the target itself.

**Reproduction.** Run `PYTHONDONTWRITEBYTECODE=1 uv run python -I <scratch>/close-r1/agg.py <scratch>/close-r1/agg`. The model is:
- `tally(person, n)`: aggregate `count` of `$w` over `wrote(work: $w, person: $p)`;
- `prolific(person)`: body `member(person: $p)`, `tally(person: $p, n: 3)`;
- facts: `wrote(w1, ann)` and `member(ann)`.

Output:
```
check: blocked
why-not raised: WhyNotInternalError clause 0 of 'tally' walks to a non-empty end although production did not derive the target
```
On the CLI, `uv run python -I -m gnd why-not agg/model.orm.json agg/pop.json --fact-type prolific` gives `exit=1` and a traceback ending in `gnd.witness.why_not.WhyNotInternalError: clause 0 of 'tally' walks to a non-empty end although production did not derive the target`. `gnd check` on the same files reports `[pass] derivation:prolific`.

**Fix.** In `_descend`, or when `_atom_blocker` sets `derivation`, stop when any clause of the blocker's rule has a dict `aggregate`, with `descent_stopped: "aggregate"`. Add that value to `why-not.schema.json`, list it in the reference page's descent-stop list, and add a kernel test plus a golden for it. The alternative is to treat aggregate fact types like prose rules for descent. Either way, `WhyNotInternalError` stays reserved for genuine evaluator disagreement.

## C1-2 — Reference page says the walk can "hold 400,000 binding cells", but the counter is cumulative (hardening, high)

**Where.** The Limits section of `docs/reference/why-not.md`, against `_Budget`/`_store` in `why_not.py`.

**What is wrong.** `binding_cells` adds `len(binding)` for every newly stored binding. It accumulates across steps, clauses and descent levels and is never released, so it is not a bound on cells held at one time. A walk can be refused with `work-limit` even though no more than a few thousand cells were live at any moment. This is precisely located but not reproduced as a separate probe; the code path is direct.

**Fix.** Reword the page to "may store 400,000 binding cells in total", or count live cells instead.
