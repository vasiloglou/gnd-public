# MG1 diff review (one local reviewer)

Retained text of the reviewer's returned report. **Edited:** the absolute
scratch path is replaced by `<scratch>`, and layout is lightly adjusted. One
reviewer is one reviewer. It ran with the repository read-only, could run
targeted tests and probes, and did not run the evolve suites or the docs
runner.

**Verdict:** approve-with-fixes.

**Scope.** Read the approved spec with its appended implementation findings
and the full diff of `src/gnd/model_verbalization.py`, `api.py`,
`disclosure.py`, the schema, the new test file, docs, pins and
`zensical.toml`. Ran: the gate subset (`test_rule_verbalization`,
`test_public_api`, `test_v61_phase2_api`, `test_public_runtime`,
`test_why_not_near_misses_public`, `test_disclosure_mode`,
`test_disclosure_docs`, `test_rf1_layering`, `test_rf6_query_policy`,
`test_gnd_arch`, `test_conformance_payload`, `test_public_built_inventory`:
349 passed); `capture_parity.py` in a throwaway `1446f90` worktree and on the
working tree; a seeded differential fuzz (6,000 random terms, atoms and rules,
baseline against new); 16 source mutants via scratch pytest plugins; probes on
in-memory mutated models; a schema sweep over every corpus payload. Scripts
and outputs under `<scratch>/mg1-review/`; the worktree was removed. Not done:
evolve suites and the docs runner (the new doc call was run by hand on
`examples/dispatch`: exit 0, a rendered rule). The successor support file, the
new `evidence/MG1/dynamic-query-successor.json` and the spec's later on-disk
changes appeared during the review and were not reviewed.

## Claims confirmed

- **Claim 1.** The reviewer's own baseline capture is byte-identical to
  `parity-before.json` (`cmp`), and its current capture to
  `parity-after.json`: over 282 models, loaded digests unchanged, every
  non-crashing path digest unchanged, the 23 `AttributeError` path inputs now
  equal the loaded render.
- **Claim 2.** With `fallbacks=None`, the fuzz output of `_guarded_term`,
  `_guarded_atom` and `_derivation_cnl` is identical to `1446f90`, including
  exception class and message (3,641 exceptions: `AttributeError`,
  `ValueError`, `TypeError`; 2,359 renders).
- **Claim 4, largely.** `TypeError` checks precede model loading (the ordering
  mutant is caught by T5); in-memory `Model` re-validation (its removal is
  caught by T4c's well-formed `date_add` case); exit-3 refusals; all 846
  corpus payloads (each model loaded, as `str`, as `Path`) validate against
  the schema, all exit 0.
- T1b, T3c, T4c and T5 ordering each fail under the matching mutant
  (theme-B revert, no `line_text`, each collector branch but one (F2),
  unsorted selection).
- Pins, schema inventories, disclosure row and table, nav, the "ten
  functions" line and release notes are consistent; layering and RF6 pass.

## Findings

**F1 (hardening; refutes claim 3 as stated)** -- `model_verbalization.py:686-728`
(`render_rule_verbalizations`), docstring `:695-697`. The collector covers
only the spec's fallback table. A structured rule mutated in place on a
loaded `Model` and passed directly still returns partial or wrong text as
`rendered`, or raises a non-`VerbalizationError`, contradicting rule 4 and
the docstring. Probe `probe3.py` on bookrec `fact_types[6]`:

| Mutation | Result |
|---|---|
| atom without `fact_type` | `'when None(book = $b) and user_is_minor(...)...'` |
| where item without `operator` | `'... and $u None $b, ...'` |
| where item `{}` | `'... and null None null, ...'` |
| `clauses: "x"` or `clauses: []` | `rendered ''` |
| `clauses: ["x"]` with no body | `'when , derive (book = $b, user = $u)'` |
| empty body | `'when , derive (book = $b, user = $u)'` |
| `{"duration_days": {"a": 1}}` | `"... $u != {'a': 1} calendar days ..."` |
| `head: {1: "$u"}` | `'derive (1 = $u)'` |
| unknown rule key `filter` | silently ignored |
| `{"fn": ["x"], "args": []}` | `TypeError: cannot use 'list' as a set element` |

`api.verbalize_rules` returns exit 3 for every one (re-validation), so the
public payload is safe. Repair: re-validate a `Model` argument once in
`render_rule_verbalizations` (`validate_model_object`), converting failure to
`VerbalizationError`; keep the collector as defence in depth. Or narrow the
docstring and rule-4 claim.

**F2 (completeness)** -- T4c against the collector at
`model_verbalization.py:243-244`. The `unanalyzable-aggregate` branch is
untested: mutant H (`fallbacks.append("unanalyzable-aggregate")` → `pass`)
leaves all 35 tests passing; with H, an in-memory `orders` rule with
`aggregate.fn="bogus"` renders `'...; aggregate bogus of $q distinctly over
($s) as $t, ...'` as `rendered`. Repair: add that mutation to `IN_MEMORY`.

**F3 (completeness)** -- T1, T5 (`tests/test_rule_verbalization.py:85-91`,
`:270-298`). `model_id` is not asserted (mutant R, `"model_id": None`,
survives; the schema allows null), nor rule 1's "id in the message" (mutant T
survives). Repair: assert `model_id` in T1 and the id in T5's messages.

**F4 (completeness, unrecorded deviation)** -- T4b (`:209`). The spec wants the
refusal path to name the mutated element; the test asserts only
`$.fact_types[i].derivation_rule`. Probe `t4b.py`: for 9 of 11 mutations
validation reports only the whole-rule path (a schema `oneOf` failure), so
element-level naming is not achievable. The control/mutant pairing still
isolates the cause. Repair: record it as a finding.

**F5 (completeness, unrecorded deviation)** -- T11 (`:301-327`). The spec
counts fact-type visits; the test counts `_derivation_cnl` calls, so a second
walk over `iter_fact_types_shared()` would go unseen. Repair: count those
iterations too, or record the substitution.

**F6 (hardening, unproved impact)** -- `api.py:930-931`. `except (...,
OSError, ValueError)` maps any rendering `ValueError` to "invalid model"
exit 3, including a future renderer bug. No reachable case for validated
models. Repair: narrow the catch to load-time exceptions around
`_resolve_model`.

No blocking defects found.
