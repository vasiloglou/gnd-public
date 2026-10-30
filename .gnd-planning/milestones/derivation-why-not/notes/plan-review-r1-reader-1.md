# Reader 1 -- correctness against production semantics

Retained text of the reader's returned report. Local edits: scratch paths read
`<scratch>`.

Both digests matched: plan `77928fb2...cc70`, WN1 spec `cbc99f26...1f03`.

**Verdict: request-changes**

**Scope.** I read the plan and the WN1 spec in full, and issue #66. In `src/gnd/extensions.py` I read `_joined_atom_candidates`, `_joined_bindings`, `_component_atoms`/`_component_product`, `_apply_negation`, `_clause_bindings`, `_python_extension_calculator`, `_exact_extension_calculator` (lines 1813-1990), `_evaluate_stratified_extensions` (lines 1469-1811), `_exact_derivation_obligation` and `_evaluate_derivations_dispatch` (lines 2618-2750). I also read `values._identity_key`, `iter_derivation_clauses`, the validation rules for unbound negated and head variables, `witness/io.support_closure`, `witness/producer.produce_witness` and `WitnessLimits`. I ran two probes with `uv run python`. Both are under `<scratch>/reader1/`: `probe_unavail.py` and `probe_dep.py`.

**What holds.** If no term is unavailable, the declared-order walk yields the same set of bindings as production's component-reordered join. Joins are commutative, so after all positive atoms the bindings are the same. Negation runs before `where` in both. The `where` comparisons short-circuit per binding in production, which equals filtering them in sequence. Walking a recursive clause over the final fixpoint gives exactly that fixpoint. Seeding head variables in row mode filters the same bindings that the final head projection would filter. Within that fragment, "blocked" and "derived" agree with `check`. The findings below fall outside it.

## Findings

### R1-F1 -- blocking, high confidence. An unavailable term makes why-not say "derived" (or "blocked") when `check` derives nothing

**Where:** spec §6.2 step 4 (lines 124-127); §6.3 status rule (lines 168-170); §7 D6; plan §2 line 197; spec §5 Goal.

**What is wrong.** In production an unavailable result is a property of the whole relation. When `compare_terms` or `evaluate_term` is unavailable for *any* binding, or `materialize_scalar` fails (`term:head-non-integral`), `_exact_extension_calculator` and `_evaluate_stratified_extensions` drop the whole head relation into `unavailable`. That happens even when other bindings or other clauses would derive rows. `check` then reports the verdict `unchecked` (band 4). The spec's status rules diverge in three ways:

- **Rule mode, several clauses.** The spec reports `derived` if any clause is derived. Production derives no extension at all.
- **Row mode.** Seeding the head variables means the binding that fails is never generated, so the spec reports `derived` for the claimed row. Production has no extension.
- **Rule mode, one clause.** The spec reports `blocked` (exit 0, "explanation produced") and names the comparison as the blocker. Production says the answer is *unknown*, not missing. The host would go off and extract a fact that does not exist.

The head step (§6.2 step 5) says nothing about unavailable or non-integral head terms.

**Reproduced.** `probe_unavail.py` uses `price(x,1.0)` and `price(y,0.0)`, with `ok(i) :- price(i,a), div(1,a) > 0`. It runs it as a single clause, and as two clauses where the first clause has no `where`:

```
single-clause ok unchecked term:div-zero
two-clause ok unchecked term:div-zero
two-clause extension ok: None unavailable: {'ok': RelationUnavailable(... 'term:div-zero', binding={'i':'y','a':0.0})}
```

Under spec §6.3:

- the two-clause rule is `derived`, because clause 0 derives `ok(x)` and `ok(y)`;
- the row claim `ok(x)` is `derived`, because the seeded binding `a=1.0` passes;
- `check` reports `unchecked` for both.

This breaks WN-R2, WN1-C2, and the §5 statement "`derived` exactly when check's extension contains the row".

**Fix.** Add a top-level status `unavailable`, mapped to exit 2 with a reason, as an amendment to WN-D5. Decide it *before* any walk: run the production exact evaluation over the target's closure. If the target head is in `extensions.unavailable`, return `unavailable` with that `RelationUnavailable`'s reason, binding and `source_relation`, in both rule and row mode. Also decide `derived` from production's extension: row mode checks identity membership, rule mode checks non-empty. Walk only when production says "not derived and available". Then assert that every clause reaches a zero step, and treat a mismatch as an internal defect. With this ordering, "derived when check does not" and "blocked when check derives" become impossible by construction instead of something T8 has to sample for. Replace D6 accordingly. Drop clause status `unavailable`, or keep it only as a diagnostic under a top-level `unavailable`.

### R1-F2 -- blocking, high confidence. An unavailable dependency silently becomes an empty relation

**Where:** spec §6.2 steps 2-3; WN-R2 (spec line 42, "Derived body relations come from `_evaluate_stratified_extensions(..., exact=True)`"); §6.4.

**What is wrong.** Suppose a body or negated predicate is unavailable. Production propagates that to the head (`exact-origin-propagated`, lines 1592-1601 and 1856-1874), and the predicate is *absent* from the returned extensions mapping. The spec does not handle that absence:

- **Positive atom.** The walk sees an empty relation and reports `blocked` at that atom with `derivation: derived`, then descends.
- **Negated atom.** The walk removes nothing and may report `derived`.

**Reproduced.** `probe_dep.py` adds `top(i) :- price(i,a), not ok(i)`, with `ok` as in R1-F1:

```
ok unchecked term:div-zero
top unchecked term:div-zero
extensions keys: [] unavailable: ['ok', 'top']
```

A walk over `top` would find `ok` missing. Its negation would keep both bindings, so it would report `derived`, while `check` reports `unchecked`.

**Fix.** This is covered by R1-F1's pre-check, because the target's own `unavailable` entry already carries `source_relation`. Also state the rule outright: a relation in `unavailable` is never read as empty. Add a T8 case for each of positive dependency, negated dependency and descent target.

### R1-F3 -- blocking, medium-high confidence. Opaque-value support is not transitive

**Where:** spec §6.1, row "opaque (dict) values in a relation the clause reads".

**What is wrong.** `_evaluate_derivations_dispatch` (lines 2690-2725) computes the *transitive* set of heads downstream of any opaque source and reports each one as `unchecked` / `opaque-value`. The witness lane does the same through `trace.opaque & scope` over the closure, reporting "unknown". Opaque cells can also sit in a base relation that only a derived body predicate reads. In that case the clause reads a derived extension built from rows with the opaque ones removed: in partial mode `_evaluate_stratified_extensions` keeps only rows without opaque values in `state`. Why-not would then report `blocked` at that derived atom, where `check` says `unchecked`. Separately, any opaque cell *anywhere* switches `_evaluate_stratified_extensions` into its partial path for every rule. That is not the path `check` takes, which re-evaluates a population with the opaque rows removed.

**Verified** by reading the code; not probed.

**Fix.** Return `unsupported` / `opaque-value` when any relation in the target's dependency closure (`derivation_dependencies`, transitive) contains an opaque cell. Reuse the closure loop from the dispatch, and add a T14 case with an opaque value two strata upstream.

### R1-F4 -- hardening, high confidence. Production evaluation of derived body relations is not charged

**Where:** spec WN-R1 (line 38, "does not set `_WITNESS_TRACE`"), WN-R2, §6.6; plan WN-R4 and completion predicate 5.

**What is wrong.** Witness bounds its call to `_evaluate_stratified_extensions` through `_WITNESS_TRACE` (`_witness_charge` in `_joined_bindings` and `_component_product`). The spec disables that trace and charges only its own step loop. The exact fixpoint, which can contain cross products and recursion, then runs against untrusted input with no limit, and T13 covers only the walk. A blow-up there would hang rather than exit 4.

**Fix.** Either install a charging trace that records no rows and only charges (a sibling context variable, or a trace object whose row hook is a no-op), or name the production pre-evaluation as bounded only as `check` is bounded, and say so in the WN-R4 argument. Extend T13 to a derived body predicate with a large intermediate join.

### R1-F5 -- hardening, high confidence. Descent's cycle key and grounding rule defeat its purpose

**Where:** spec §6.4 lines 174-179; plan §2 lines 179-183.

**What is wrong.**

- **Cycle key.** Stopping on "predicate already visited on this path" ends descent at the first step of every recursive predicate, such as `anc(x,z) :- parent(x,y), anc(y,z)`, even though the row is different. Depth 8 already bounds the recursion.
- **Grounding rule.** Descent needs a sample that grounds *every* role. In declared order, a blocking atom that introduces a new variable is never ground, and that is exactly the issue's own payload sketch (`bound_roles: ["work"], free_roles: ["person"]`). So when the blocking predicate is derived, the case the issue cares about ends at `not-ground`.
- **Plan wording.** The plan text, "if every earlier binding grounds that atom's arguments the same way for at least one sample binding", is self-contradictory and differs from the spec.

**Fix.** Key cycles on (predicate, canonical row). Either specify partially bound descent, explaining "no row of P with the bound roles equal to ...", or state plainly that descent covers only ground atoms and that a host asks again otherwise. Align the plan sentence with the spec.

### R1-F6 -- hardening, medium confidence. The oracle's independence is under-specified

**Where:** spec §6.5; plan §6, risk row "oracle ... no import from `extensions` join helpers".

**What is wrong.** Forbidding imports from `gnd.extensions` still lets the oracle import `gnd.terms.compare_terms`/`evaluate_term` and `gnd.values._identity_key`, so it would share both comparison and identity semantics with the kernel. The spec also does not say whether the oracle computes the extensions of derived body predicates itself, or reads the same production `relations`. If it reads them, derived-predicate cases are not independent. The oracle also re-implements the same declared-order *definition*. Agreement with production is tested only by T8, and T8's corpus omits unavailable terms, dependencies, opaque values upstream, and the boolean-vs-integer and `1` vs `1.0` identity cases.

**Fix.** Make the oracle:

- implement identity itself (separate boolean and number domains, `int == float`);
- compute derived-predicate extensions by naive fixpoint;
- use only comparisons with literal operators (no function terms), or say explicitly which helpers it may import.

Extend T8 to rule mode ("non-empty and available") and to the cases listed in R1-F1 to R1-F3.

### R1-F7 -- completeness, high confidence. Smaller definitional gaps

- **Unreachable negation clause.** §6.2 step 3, "a not-fully-bound negated atom keeps the binding", cannot be reached in an admitted model: `semantic:derivation-negate-unbound` (`_validation.py:4330`) and `semantic:derivation-head-unbound` (`:4306`) refuse it. Say so, so that a test does not pin an unreachable branch as behavior.
- **Clause presentation.** Name `iter_derivation_clauses` as the clause source. In it, a clause body *replaces* the shared body, and root `where` comparisons come before clause-local ones (`_validation.py:2845-2868`). That defines the "declaration order" of comparisons.
- **Identity.** Name the identity used for "distinct" and for head-row equality: `_identity_token` on `materialize_scalar(evaluate_term(...))`, which is the production row key.
- **Body predicate with a string (opaque) rule.** Production reads its asserted rows as base (`_base_relations`, line 826). Its blocker should report `derivation: base` as production treats it, not descend and refuse as `rule-opaque`.
- **Fragment wider than witness.** The why-not fragment (negation, semiderived predicates, function terms, float values) is much wider than witness's `support_closure`. "The same call witness makes" therefore covers inputs witness never runs. R1-F1 to R1-F3 are the consequences.
