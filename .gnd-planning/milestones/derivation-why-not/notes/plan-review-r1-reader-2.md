# Reader 2 -- implementability, pins and homes

Retained text of the reader's returned report. No local edits.

Both digests matched: plan `77928fb2…cc70`, WN1 spec `cbc99f26…f03` (`shasum -a 256`). Worktree HEAD is `fb03739`.

**Verdict: approve-with-fixes**

**Scope.** I read both subjects in full, plus issue #66 and the spec-note contract. I checked them against `src/gnd/witness/*`, `extensions.py` (lines 454, 629–1000 and 1469–1800), `terms.py`, `values.py`, `model/_validation.py:2845`, `cli.py`, `commands/witness.py`, `tools/gnd_layers.json`, `tools/gnd_entrypoints.json`, and every test that pins the surfaces the plan touches. I ran `uv run pytest -q tests/test_rf6_query_policy.py tests/test_rf1_layering.py`: 43 passed. I wrote nothing in the repository.

Several things check out:
- Every line anchor the plan cites is correct: `api.py:119` (eleven names), `extensions.py:454/683/921`, `_validation.py:2845`, and the witness lane at 1,395 lines.
- Every helper the spec names exists. `_joined_atom_candidates(atom, facts, *, variable_of, work)` is at `extensions.py:629` and is re-exported by `gnd.checker`. `_identity_key` is in `gnd.values`. `compare_terms(op, l, r, binding, *, limits, bound_cross_product)` and `evaluate_term(term, binding, *, limits, temporal_work)` are in `gnd.terms`. `_apply_negation` requires a non-None `_JoinWork`.
- The proposed home is legal. `lanes` (rank 4) importing `checking` (rank 2) is downward. Private imports from a new module are counted only for the RF3/RF4 baseline cohorts (`test_rf4_peripheral.py:44`, `test_rf3_core.py:40`), so a new module is not ratcheted. `witness.producer` already reads `checker._evaluate_stratified_extensions`.

## Findings

**R2-F1 — blocking (the phase fails its gates as written), high confidence. The RF6 live query policy rejects any new model read in `why_not.py`.**
- **Where:** plan §3 and WN-R7; spec §6.1, §6.7 and T16.
- **What is wrong:** `tests/test_rf6_query_policy.py::test_exact_live_query_policy` counts every `model.fact_types`, `.get('roles')`, `['roles']` and `['fact_types']` read under `src/gnd`, and requires exact equality with the approved rows. The kernel needs head roles, clause roles and derivation kinds. Any direct read, even `fact_type.get("roles")` as `_relation_roles` does, fails the test. AGENTS.md says to prefer the `gnd.model_index.ModelIndex` snapshot. The plan and spec never mention this policy.
- **How I verified:** the policy file `.gnd-planning/milestones/code-refactoring/evidence/RF9-repair/query-allow-list.json` has ceiling 365, baseline 375 and a row sum of 354. The witness rows are counted one by one (for example `src/gnd/witness/io.py roster model.fact_types`). Successors chain through `QUERY_SUCCESSORS` in `tests/support/pyrel_application_successors.py:10`.
- **Fix:** spec §6.7 should require role and derivation lookups through `ModelIndex` or the already-counted `witness.io.roster`. If a new read is unavoidable, it needs an authenticated `evidence/WN1/query-successor.json` registered in `QUERY_SUCCESSORS`. Add `test_rf6_query_policy.py` to WN1's gate (T16).

**R2-F2 — blocking for WN2, high confidence. The CLI pins and the command registration home are missing.**
- **Where:** plan §3 "Service, CLI, view", WN2-C3 and §9.
- **What is wrong:** adding `why-not` changes these exact pins:
  - `tests/test_rf1_cli_pins.py`: `EXPECTED_PARSERS = 56`; the `cli/tree.json` golden; the `gnd` help goldens `gnd.py311/313/314.json`; new `cli-help/gnd_why-not` and `cli-exit/gnd_why-not` goldens; and `goldens.sha256`. These are captured with `tools/rf1_pins.py capture`, and the per-interpreter goldens need all three Python minors.
  - `tests/test_rf5_commands.py:118`: `len(parsers) == 56`.
  - `tests/fixtures/rf5-handlers/cases.json`: needs a `why-not` handler case.
  - Registration also needs an edit to `src/gnd/commands/witness.py`. Its `_register_witness` dict and `handle` set are hard-coded to `witness`, `replay` and `witness-view`, and the plan does not list that file.
  - `witness.cli` must keep importing `gnd.witness.service`, not `gnd.api`. The pair `("gnd.witness.cli", "gnd.api")` is asserted absent in `test_rf1_layering.py`.
- **How I verified:** `grep -n EXPECTED_PARSERS tests/test_rf1_cli_pins.py`, `sed -n 110,125p tests/test_rf5_commands.py`, `cat src/gnd/commands/witness.py`, and `ls tests/fixtures/rf1-pins/goldens/cli-help`.
- **Fix:** list these pins and `src/gnd/commands/witness.py` in WN2-C3 and §3.

**R2-F3 — hardening, high confidence. The API pin list is incomplete.**
- **Where:** WN2-C3.
- **What is wrong:** the exact `__all__` tuple is also pinned in `tests/test_v61_phase2_api.py:38`, which the plan omits. `tests/test_public_runtime.py:52` is a `distribution`-marked probe with a stale ten-name tuple. That file is named in WN2-C3, but its literal currently omits `EvaluationSession`. Editing it to eleven or twelve names should be a deliberate choice, recorded in the spec. `test_public_reference_signatures.py` pins no witness signature, so the plan needs a new signature case, not an edit.
- **Fix:** name all four files and add a `why_not` keyword-only signature pin.

**R2-F4 — hardening, high confidence. The output schema inventory is not named.**
- **Where:** plan §3 "Output schema".
- **What is wrong:** `src/gnd/why-not.schema.json` fits the root output-contract convention, which is a good choice. But `tests/test_public_built_inventory.py::VENDORED_SCHEMAS` (line 248) must gain `gnd/why-not.schema.json` so the wheel is required to carry it. The witness lane's own schemas live in `src/gnd/schema/witness-result.schema.json`. The plan should say why it does not follow its own lane, so a reviewer does not "fix" it.
- **Fix:** add the inventory edit to WN2-C2 and state the home rationale.

**R2-F5 — hardening, high confidence. "As witness" is wrong for the API's redaction.**
- **Where:** plan WN-R5, §2 and WN-D4; spec WN-R5.
- **What is wrong:**
  - `api.witness` has no `raw` parameter and returns raw values. Only `witness.cli.run` applies `result_view` without `--raw`, and `python-api.md:273` says so explicitly.
  - The other public functions spell the redaction switch `unredacted=False`, which `test_public_api.py:15` pins for validate, check and transition.
  - `raw=False` on `why_not` is therefore a new convention, not reuse.
- **Fix:** rule on `raw` versus `unredacted` (or returning raw like `witness`). Record it in WN-D4, and state where the redacted view lives (`witness/view.py`).

**R2-F6 — hardening, high confidence. The `--fact-type` / `--targets` contract and the kernel `row` type are unspecified.**
- **Where:** plan §2; spec §5 and §6.2.
- **What is wrong:**
  - `witness.io.load_targets` takes `{"version":1,"targets":[{"fact_type","tuple":[typed…]}]}`, with 1 to 256 targets, each naming its own fact type.
  - The plan has a separate `--fact-type` flag, but does not say what happens with multiple targets or a mismatched `fact_type`.
  - `explain(model, relations, fact_type_id, *, row=None, …)` takes a single row of unstated type. It could be typed cells or production scalars; witness matches by canonical typed-cell JSON, while the spec says `_identity_key`.
  - The spec also does not say whether `relations` are base relations (`checker._base_relations` of the reference-bound population, as `produce_witness` builds them) with derived extensions computed inside, or are pre-evaluated.
- **Fix:** add a WN2 rule. Either targets must all name `--fact-type` with each target explained (exit 3 on mismatch), or the flag is dropped in favour of targets. Pin `row`'s type and the `relations` precondition in spec §5.

**R2-F7 — hardening, medium confidence. Production's unavailable relations have no defined outcome.**
- **Where:** spec §6.2 steps 4–5 and §6.3; T8.
- **What is wrong:**
  - Production marks the *whole relation* unavailable on an unavailable comparison, an unavailable head term, or `materialize_scalar` "term:head-non-integral" (`extensions.py` ~1700–1745). It carries this out of band in `_ExactExtensions.unavailable`, and propagates it to dependents (`exact-origin-propagated`).
  - The spec covers only an unavailable comparison, and maps it to `blocked`.
  - It gives no outcome for an unavailable head term, an unavailable derived body relation, or an unavailable target relation.
  - T8's "derived iff in exact extension" then has no defined answer for those cases.
- **Fix:** add these rows to the §6.1 and §6.2 tables, with a status (for example `unavailable`, mapped to exit 2) and T cases.

**R2-F8 — completeness, high confidence. The WN2 docs work is under-listed.**
- **What is wrong:**
  - Python blocks in `python-api.md` marked `<!-- gnd-run expect=0 -->` are executed by `tools/run_tutorials.py:205`. A `why_not` example there needs a runnable fixture.
  - Every `| \`gnd …\`` row in `cli.md` is probed with `--help` by `tests/test_documentation_tutorials.py::test_reference_command_routes_exist`.
  - The new reference page needs a nav entry in the root `zensical.toml` (line 27). No test enforces this, so the page would be silently orphaned.
  - For WN3, `tools/check_installed_docs.py:58` keeps a list of packaged example domains, which the new example should join.
- **Fix:** add these to WN2-C4 and WN3-C1.

**R2-F9 — completeness, high confidence. Focused gates can be named now.**
- **Where:** plan §9 says the gates are "unresolved"; spec §8 lists cases but no command.
- **Fix:** name them.
  - WN1: `uv run pytest -q tests/test_why_not_kernel.py tests/test_why_not_oracle.py tests/test_rf1_layering.py tests/test_rf6_query_policy.py tests/test_rf4_peripheral.py tests/test_gnd_arch.py` plus the existing witness tests. `test_rf4_peripheral` asserts that the layer-map modules equal the discovered modules, so it, not `test_rf1_layering`, is what catches a missing map entry.
  - WN2 adds: `test_public_api.py`, `test_v61_phase2_api.py`, `test_public_reference_signatures.py`, `test_rf1_cli_pins.py`, `test_rf5_commands.py`, `test_rf5_handler_pins.py`, `test_documentation_tutorials.py`, and `test_public_built_inventory.py` (distribution, owner-selected).

**R2-F10 — completeness, medium confidence (judgement, not measured). The size estimates are low.**
- **Where:** spec §10.
- **What is wrong:** 300 source lines must cover the support policy, a step loop with five step kinds, the head-bind seed, descent with three stop reasons, two error types, result types and charging. For comparison, `producer.py` is 267 lines with no descent. 450 test lines must cover 17 cases with exact payloads, plus an independent oracle and a seeded corpus generator.
- **Fix:** estimate about 400–500 source lines and 700 or more test lines, and record the actual figures in the phase record.
