# GC2 · Guarded antecedent filters · draft r1

GC2 follows the accepted GC1 phase. The [milestone plan](guarded-rule-clauses-plan.md)
binds N1–N4, D3, and the issue #195 shipped-order exception.

## Obligations and decisions

| Criterion | Contract | Evidence |
|---|---|---|
| N1 | Optional nonempty `negate` (atoms) and `where` (term comparisons) sit beside `antecedent`. Negative and comparison variables must be introduced by positive antecedent atoms. Ground negative atoms are permitted. Existing positive connection checks keep their precedence. | GND validation fixtures cover legal variable and ground negation, bad shapes and references, an unbound variable on either side of a comparison, and unbound or disconnected positive graphs. |
| N2 | Negative atoms read the effective constraint relation. Asserted and fully derived relations must be covered for an absence proof. A fully derived relation uses its covered claim and the derivation check independently judges consistency. A semiderived relation uses its available calculated rows. | Asserted covered empty, present, and uncovered negative relations. Covered consistent and inconsistent fully derived claims and uncovered derived relations. Existing stratification refusal on a negative dependency cycle. |
| N3 | For a positive binding, a true negative match or false comparison excludes it. An unavailable comparison or absence over unavailable or uncovered rows makes a binding unknown when no filter definitely excludes it. Any outstanding unknown makes the guard unchecked. Otherwise filter-only emptiness is vacuous. Diagnostics count definite survivors and keep the first-empty index tied to the positive join. | Public check and reference/indexed evaluator controls, plus a fixed-seed helper differential over 200 covered, decidable inputs with both pass and fail. Filter-only vacuity and unresolved filters have distinct outcomes. |
| N4 | Render the filters in the rule sentence. Existing rule-id feedback identifies the original rule. Guarded synthesis emits both verdicts over reachable filter cases. A passing negation example keeps an active satisfying binding and excludes a second binding whose consequent would fail. | Expected CNL and `--rule-ids` output, guarded-cases v1 pair and checked populations. Confirm the excluded binding participates in an otherwise identical control with the negative filter removed. |

Negative references do not create a derivation graph edge because a guard
has no output relation. A missing or unavailable relation cannot support an
absence claim. A known matching row can prove exclusion even if the other
filters are unavailable. The no-filter guard retains its report bytes.

## Design and work bounds

1. **Totality.** New array shapes, comparisons and atomic bindings are
   validated without trusting an earlier reader. Type probes distinguish
   malformed arrays, members, unknown operators and incompatible operands.
2. **Cap the algorithm.** Compile each filter once. Index the needed columns
   of each negative relation by typed row identity and charge each index row
   and binding probe to the same bounded operation. An exhausted budget
   returns an unchecked verdict. The reference path can scan rows, while the
   production path remains indexed. Pin work and elapsed time for a wide
   covered negative relation over 10,000 potential bindings.
3. **Validation order.** Membership remains in its original comparison
   rules. New guarded atom references and role claims join the existing atom
   walk. Filter binding and comparison checks follow those claims. Source
   order tests pin the boundary.
4. **One walk.** Expose filter atoms and comparison operands through the
   shared guarded walks. Keep the positive-only join graph and the filter
   read set separate because they drive different behavior.
5. **One home.** Document the semantics in the Guarded constraints section
   of representation-format. Public report docs explain counts for the new
   shapes within v16. Other references link those homes.
6. **Measure.** Compare helper and native guards only on covered, definite
   outcomes and project offending bindings to the shared variables. Direct
   expected-outcome tests cover undefined terms and missing coverage.

Reuse the registered guarded family, the existing atom and term adapters,
GC1 membership filters, the effective constraint view, runtime diagnostic
observation, and guarded case generator. The exact preparation and evaluation
boundaries must preserve the temporal guard's work limit. For intermediate
releases, each exporter that cannot represent the new filters refuses them
explicitly.

## Proposed verification

Run the new filter corpus, guarded comparison and reference evaluator tests,
guarded diagnostics and temporal controls, derivation and synthesis tests,
the affected exporters, the issue #171 guard list, Ruff, and the component
index checks. Finalize the exact ledger and delegated corpus/spec gate after
GC1 acceptance and before changing runtime code for GC2.

Independent diff review uses Claude Code under the owner's GC1–GC4 selection.

## Selected gates

- `uv run pytest -q tests/test_guarded_antecedent_filters.py --tb=short`
  on the initial corpus before implementation, then on the expanded corpus.
- `uv run pytest -q tests/test_guarded_antecedent_filters.py tests/test_guarded_membership.py tests/test_model_guarded.py tests/test_public_semantic_guarded.py tests/test_guarded_diagnostics.py tests/test_v71_phase1_dates.py tests/test_derivation_rule.py tests/test_synth_guarded_cases.py tests/test_rule_verbalization.py tests/test_schema_sync.py --tb=short`.
- The same explicit affected exporter and issue #171 commands used for GC1,
  plus Ruff and `python3 scripts/components_index.py changed --base main --strict`.

Component consult for “indexed negation anti join” and “guarded coverage
term filters” found `check.snapshot_decision`, `semantics.temporal_guards`
and the existing extension anti-join and comparison helpers. Adapt the
existing registered guard and typed-identity representation. The extension
anti-join establishes the indexing pattern; its closed-world absence policy
does not carry to the guarded filter. External components were absent.
