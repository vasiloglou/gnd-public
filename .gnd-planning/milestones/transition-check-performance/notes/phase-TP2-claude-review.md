# TP2 independent diff review (transition-check-performance)

- Branch: claude/transition-check-performance-tp2 (uncommitted working-tree diff over 834ee88)
- SHA-256 src/gnd/model_index.py: c820a107ee8591e561c05745c863af9afcc6c095eeced5913e3027ea6ea8f540
- SHA-256 tests/test_tp2_shared_fact_types.py: 04ce7f5135bbe3e46b5d365bb342687969b1b0540ab36fad4d4e04f00c18b6c8
- Method: the 8 readers were read by hand. Mutants ran in a scratch copy (scratchpad/tp2-review/wt, with PYTHONPATH pointing at the copy's src). No repository file was edited. After each mutant the copy's src was diffed against the repo and matched.
- Baseline in the copy: all 5 TP2 tests passed (73 s).

## Data-flow audit of the 8 readers

| Reader | What escapes the loop | Verdict |
|---|---|---|
| check_legacy coverage | `str(fact_type["id"])` keys and CoverageEntry(ints/strings) | read-only, no escape |
| _record_aggregate_guarded_outcomes | set of id strings; `rule` is only tested with isinstance/get | read-only |
| _partial_constraint_report guard (`any(...)`) | bool | read-only |
| _partial_constraint_report by_ref | a local dict of (constraint, fact_type) refs, used only for get(), constraint_variant, _scope_fact_types (which returns `[str(id)]` when fact_type is set) and the roles/keys lists built from `possible`. The new ConstraintVerdict carries only strings. The dict dies with the call | read-only, no escape |
| _check_dispatch | passes refs to _scope_fact_types and _term_unavailable_constraint_verdict, which builds the verdict from `str(...)` of constraint fields plus constraint_variant (read-only) | read-only, no escape |
| _anchored_verdicts obligations | a local list. `recognisers_by_role[...]` copies elements via set.update; `tuple(recognisers)` copies too. `offending_facts` holds population rows, not model rows. Verdict fields are str() values | read-only, no escape |
| compiled_obligations.compose | `str(fact['id'])` goes into the `unavailable` set | read-only |
| universe._instance_values_of | role_name strings; the appended values come from population facts | read-only |

- Shared rows are not aliases of `model.fact_types`, because model_dump copies them. Two separately loaded models with equal content get the same cached ModelIndex (checked: `for_model(m2) is for_model(m1)`). So a stray write would corrupt other callers, which makes the read-only audit above the load-bearing guarantee.
- Public detachment (O5): `fact_types` and `iter_fact_types` still deepcopy. The only new public method is `iter_fact_types_shared`. Its docstring marks it internal, but it has no leading underscore, so any caller can reach it. No public API returns a shared row from any of the 8 sites.

## Mutants tried

| # | Mutant (in the scratch copy) | Run | Outcome |
|---|---|---|---|
| M0 | Switch all 8 sites back to iter_fact_types | T1 | KILLED: the deepcopy bound fails |
| M1 | check_legacy: `fact_type.update(_mut=1)` | T2 | KILLED |
| M2 | compose: `fact['_mut']=1` | T2 | KILLED |
| M3 | universe: `roles.sort(...)` | T2 | KILLED |
| M4 | _check_dispatch: `constraint['_mut']=1` | T2 | KILLED |
| M5 | aggregate: `rule.setdefault('_mut',1)` | T2 | KILLED |
| M6 | _partial_constraint_report: `constraint['_mut']=1` | T2 | SURVIVED (T2's workloads never reach this path) |
| M6' | same | freeze plugin + test_v70_phase4_constraints etc. | KILLED |
| M7 | _anchored_verdicts: `fact_type.update(_mut=1)` | T2 | SURVIVED (the workloads have no anchored constraints) |
| M7' | same | freeze plugin + test_rf1_semantic_pins etc. | KILLED (test_check_anchored) |
| M7'' | same | same suites without the plugin | SURVIVED: a harmless extra key changes no output |
| M8 | check_legacy: `dict.__setitem__(fact_type,'derivation','derived')` (bypasses the guard) | T2 | SURVIVED (the write goes to a discarded frozen copy) |
| M8' | same | T4 (unfrozen parity) | KILLED |
| M8'' | same | freeze plugin + compiled_snapshot suite | KILLED (test_opt_in_single_and_batch). Not reproduced: why this fails under the plugin |

Note: the guard's TypeError shows up in T2 as a digest AssertionError, not as a TypeError, because gnd turns the exception into a different payload or exit. The test still fails, so this does not matter.

## Findings

| ID | Class | Severity | Finding |
|---|---|---|---|
| F1 | completeness | low | T2's own workloads (reporter and course) never reach 2 of the 8 readers: `_partial_constraint_report` (PARTIAL_OPAQUE) and `_anchored_verdicts`. Write mutants there survive T2 (M6, M7). They are caught only by the out-of-tree evidence plugin `tp2_freeze_all.py` run across the suites. Fix: either record in the phase evidence that the plugin run is the coverage for those two readers, or add a small T2 case that drives one anchored constraint and one partial-opaque model with the frozen accessor. |
| F2 | hardening | low | The frozen guard is copy-based. It hands out a fresh frozen copy each time, so (a) `dict.__setitem__` / `list.append` called directly on the class bypasses it, and (b) even a caught write would never have reached the real cached row. So T2 detects write attempts, not corruption. M8 shows that unfrozen parity (T4) does catch a meaningful bypassing write. No current reader does any such write. Side effect: deepcopy or copy of a frozen row raises, because reconstruction calls `__setitem__`. That would be a false positive, but no reader copies a row (756 passed under the plugin). JSON round-trips are unaffected. This is acceptable as is. |
| F3 | hardening | info | The name `iter_fact_types_shared` is public by convention. Only its docstring limits it to internal readers. An underscore prefix, or a source-scan test that only allowlisted modules call it, would make the O5 boundary checkable. It is not required by the spec. |

No blocking finding survived. No reader mutates a shared row or anything reachable from it. by_ref, obligations and check_legacy keep no reference past the call. Reports and verdicts hold only derived strings and ints.

## Verdict

ACCEPT, with no blocking findings. T1 fails when the change is undone (M0). T2's guard catches writes in the 6 readers its workloads reach (5 tried, all killed). The other 2 readers are covered only by the freeze-plugin evidence (F1).
