The review found nothing that refutes C1, C2 or C3. I'm approving, with two low-severity findings and one style note. All 13 files match the SHA-256 values in the brief.

## 1. Findings

**F1 (low, the evidence record doesn't match the tests).** The spec's "Preimplementation evidence" (§11) says the base gate exited with `5 failed, 2 passed`, which is 7 tests. `tests/test_si2_reference_identity.py` has 8 tests. Run against the base source, 6 fail and 2 pass. The extra red test, `test_same_role_set_tie_uses_component_sequence` (line 69), is not in the recorded gate or its list of red cases. So the approved spec, under digest `f4b1802e…`, describes a different test file from the one being reviewed. The test is correct; the record understates it.
- Reproduce: `git archive 5699c76a src | tar -x -C /tmp/base && PYTHONPATH=/tmp/base/src .venv/bin/pytest -q tests/test_si2_reference_identity.py`
- Result: the 3 preference cases, the `project_first=True` tie, the same-role-set tie and the timing case fail; the `[False]` tie and the fallback/direct test pass.

**F2 (low, behavior that is neither tested nor documented).** If a qualifying preferred key can't be grounded, the result is `unmatchable`, even when the old first-anchored key would have resolved.
- Location: `src/gnd/refscheme.py:92` and `:164`.
- Input I built (it loads): the task model with a non-preferred project key first, then a preferred confirmed alethic assignment key. Employee is made composite through its own preferred external uniqueness.
- Result: the old code returns `composite` (project). The new code returns `('unmatchable', "…played by 'employee', whose identity is itself composite; nested composite joins are not supported…")`. Fact types played by `task` become inapplicable.
- This is what spec §5 intends ("Both paths continue to report the same failure…"), and it doesn't refute C1, because the fallback only covers the case where no key qualifies. But no test pins it, and neither `representation-format.md:503-510` nor the release note says a preferred key that can't be grounded is not skipped. A reader of the docs could expect it to fall through.

**F3 (style).** `test_many_nonpreferred_constraints_leave_a_bounded_walk` copies one constraint 2000 times and checks a wall-clock time under 5 s. That shows the walk is not pathological, not that it is linear. There is no observable defect.

## 2. What I checked and found true

**C1, preference and fallback:**
- `_select_role_refs` keeps only top-level `uniqueness`/`external` constraints that have non-empty `role_refs` and pass `_anchors_on`.
- Only after that does it apply `preferred` and `is_confirmed_alethic`.
- `first` is the first anchored declaration, exactly as in the old loop.
- The direct resolver still runs first.
- The loader rejects a missing `status` or `modality` and a non-boolean `preferred` (`"true"`, `1`, `"yes"`), so the truthy `.get` checks can't be bypassed.
- The nonpreferred, proposed and deontic cases all fall through to the later qualifying key.

**C2, ties and byte-equivalence:**
- The tie key is the same as Rmap's: both use `(str(fact_type), str(role))` tuples (`rmap.py:277`) and the shared `external_uniqueness_order`.
- `min` is stable for keys that compare equal, and components come back in declared order.
- I reran `census.py` on the working tree. Its output is byte-identical to `candidate.json` (and to `baseline.json`), SHA-256 `5f48cdaa…`.
- The census covers only `*.orm.yaml` and `*.orm.json`, so I also compared old and new `reference_identity` on the other 27 tracked YAML/JSON files that load as models (for example `tests/fixtures/rmap/cases/*/model.yaml`). There were 3 composites and 0 changes.

**C3, query inventories:**
- `test_rf6_query_policy.py`, `test_query_budget_headroom.py` and `test_rf6_index.py` pass: 53 tests, together with the new SI2 tests.
- The new function reads `fact_types` and `roles` only through the existing helpers, so its AST owner keys add no new query site.

**Other checks:**
- Layers: `gnd.refscheme` and `gnd.rmap` are both in the `model` layer, and `test_gnd_arch.py` passes (47 tests).
- `components_index.py --check` exits 0, and `ruff` passes on the changed files.
- The consumer suites pass: 246 tests across extract applicable/guidelines/vocabulary, model verbalization and public applicability.
- `test_rmap.py` plus `test_evolve_shape_matches.py` gave 135 passed and 1 failed: `test_r2_f8_external_unique_keys_are_not_quadratic`. It passes when run alone. It is a timing ratio test, and the diff only moves the existing tie expression into a function, so I read it as machine load rather than a regression.

**Code fitted to its examples.** The diff adds no regular expression, string split or slice. I tried each matcher it does add:
- the `str(type)` and `scope` comparisons, with the built models above;
- `.get("preferred")`, with non-boolean values (the loader rejects them);
- the `sorted()` tuple order, on the same role set in reversed sequence, and in both declaration orders.

None gave a wrong result.

## 3. What I could not check

- **Rmap agreement:** I didn't check whether reference identity and Rmap pick different keys when a preferred key is derived or not functional. The spec puts Rmap out of scope.
- **Other callers:** codegen, fidelity matching and `extract/service` compare against `applicable_set`. I covered them only indirectly, through the result that no tracked model's identity changes; I didn't run their own outputs on the built models.

My test scripts and the copy of the base source are in `/tmp/si2review`; I wrote nothing in the repository.

VERDICT: APPROVE
