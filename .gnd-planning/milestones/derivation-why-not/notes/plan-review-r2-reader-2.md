# Round 2 reader 2 -- implementability, pins and homes

Retained text of the reader's returned report. No local edits.

Digests checked with `shasum -a 256`: the plan is `b0308e35…630e` and the WN1 spec is `d1c87cb1…6f69`. Both match. Nothing was written to the repository, and no probe files were created.

**Verdict: approve-with-fixes**

**Scope.** I read r2 of the plan and the WN1 spec, the round-1 disposition and my round-1 note. I checked the theme I and theme C text against the code, `tools/gnd_layers.json`, the RF6 allow-list, the RF1 and RF5 pin fixtures, and the API pin tests.

- **Tests run:** `uv run pytest -q tests/test_rf6_query_policy.py tests/test_rf1_layering.py tests/test_rf4_peripheral.py tests/test_rf5_commands.py tests/test_rf1_cli_pins.py tests/test_gnd_arch.py` gave 1383 passed.
- **Probes:** I ran `uv run python -I` probes to check signatures, alias identity and `checked_limits` behaviour.
- **What the probes confirmed:**
  - `checker._WITNESS_TRACE` and `checker._relation_facts` are the same objects as the ones in `extensions`.
  - The witness lane may import `checking`, because that is a downward import.
  - `_evaluate_stratified_extensions(model, relations, *, heads=, …, exact=)` has the assumed signature and returns `_ExactExtensionResult.extensions.unavailable`.
  - `bind_population(model, candidate, *, references)`, `ModelIndex.for_model(model)` and `roster(model)` exist with the assumed signatures. `derivation_dependencies(doc)` and `materialize_scalar` are re-exported by `checker`.
  - The spec's line 1026 statement is accurate: a set trace disables `_build_incremental_context`, and line 1441 bypasses the scope cache.
  - A `_ChargeOnlyTrace` set on `checker._WITNESS_TRACE` is legal. Production calls only `charge` and `row` on a trace, and it catches nothing broader than `_PartialTermFailure` there, so a `ValueError`-based work error propagates out.
  - `EXPECTED_PARSERS` going from 56 to 57 is right, because `why-not` has no subparsers.
- **Kernel model reads:** the kernel can avoid direct `fact_types`/`roles` reads. Role names can come from `roster(model)`, `relation.roles` (an attribute, not counted) or `_relation_facts`. Clauses can come from `iter_derivation_clauses`. One accessor trap is listed in F3.
- **Size:** the new estimate of 450 source and 800 test lines is plausible.
- **Named files:** every test file and tool the plan names exists, except the new why-not files, which are meant to be created.

## Round-1 findings

| ID | Status | Evidence |
|---|---|---|
| R2-F1 | resolved | WN-R7, spec §6.8 and T16 route model reads through `ModelIndex` or `roster`, and `test_rf6_query_policy.py` is in the WN1 gate. There is one accessor trap (F3). |
| R2-F2 | resolved, with a small residual (F5) | WN2-C3 lists `EXPECTED_PARSERS`, `tree.json`, the three-interpreter help goldens, `rf5_commands:118`, `cases.json` and `commands/witness.py`. |
| R2-F3 | partly | The new signature case and WN-D13 are present. But the `test_public_api.py` "signature row" does not work as written, and two `__all__` pins are missing (F2). |
| R2-F4 | resolved | `VENDORED_SCHEMAS` is in WN2-C2, and WN-D12 states the home. The stated rationale is inaccurate (F6). |
| R2-F5 | resolved | WN-D4 (a) is adopted, and `witness/view.py` is named in WN2-C2. |
| R2-F6 | resolved | Spec §5 pins the `row` type (typed cells) and the `relations` precondition (§6.2 step 1). WN-D11 allows exactly one target matching `--fact-type`. |
| R2-F7 | resolved | Status is taken from production (§6.2 step 3), and T1 covers cases (a) to (e). |
| R2-F8 | resolved | WN2-C4 covers the runnable `gnd-run` block, the route probe and the `zensical.toml` entry; WN3-C1 adds the installed-docs list. |
| R2-F9 | resolved | Plan §9 and spec §8 name the commands, with one gap (F7). |
| R2-F10 | resolved | The spec §10 estimate is now 450 source and 800 test lines. |

## New findings

**R2-2-F1 — blocking for the WN1 gate, high confidence, self-inflicted (p1-C). T13(b) cannot pass under a shared budget.**
- **Where:** spec §6.7 ("`charge(n)` adds to the shared budget") and §8 T13(a)/(b).
- **What is wrong:**
  - The walk runs only when production reports the target not derived, so the T13 fixture must block after the four-way product.
  - Production computes that product in full, with no short-circuit. `_component_product` charges once per merged pair for each component after the first, and `_joined_bindings` charges `len(bindings)` per component (`extensions.py:737`, `:872`).
  - For 17 rows, the pre-evaluation charges about 68 + 289 + 4,913 + 83,521 = 88,791.
  - The walk's prefixes then store 17 + 289 + 4,913 + 83,521 = 88,740 bindings.
  - Against one shared `joins` budget of 100,000, the 17-row twin breaches instead of completing. For 18 rows, the breach happens during the pre-evaluation, not in the walk that (a) describes.
- **How I verified:** read `_clause_bindings`, `_component_product` and `GroundedTrace.charge` (`producer.py:95`), then did the arithmetic. Not executed.
- **Fix:** keep separate pre-evaluation and walk counters, or one budget with T13's numbers recomputed. State which counter each T13 case asserts.

**R2-2-F2 — hardening, high confidence, self-inflicted (p1-I). The API pins are wrong or missing.**
- **Where:** plan WN2-C3, the API bullet.
- **What is wrong:**
  - The `expected` loop in `test_public_api.py:17-27` asserts that every listed function has a keyword-only `unredacted=False` parameter. Under WN-D4 (a), `why_not` has none, so adding a "signature row" there fails. It needs a separate assertion.
  - The same file pins the full `__all__` tuple at line 16; the plan cites only `test_v61_phase2_api.py:38`.
  - `tools/run_public_acceptance.py:373` also pins `__all__` exactly, and it is unlisted. It is exercised by `tests/test_public_acceptance_runner.py`.
- **Fix:** list all three `__all__` literals, and make the `why_not` signature check its own assertion, matching `api.witness`'s `(model_path, population_path, …, *, reference_root=None)`.

**R2-2-F3 — hardening, high confidence, self-inflicted (p1-I). The RF6 counter is triggered by the natural `ModelIndex` spelling.**
- **Where:** spec §6.8 and WN-R7.
- **What is wrong:**
  - The scanner counts any `.fact_types` attribute load (`test_rf6_query_policy.py:29`). `ModelIndex.fact_types` is a property (`model_index.py:198`), so `ModelIndex.for_model(m).fact_types` adds a row.
  - The scanner also counts any `.get('roles')` or `['roles']`, whatever the receiver, so a `ModelIndex.fact_type(id)["roles"]` lookup is counted too.
- **Fix:** name the permitted accessors: `ModelIndex.fact_type(id)` and `iter_fact_types_shared()` (never `.fact_types`), `roster(model)` for roles, and `relation.roles` / `checker._relation_facts` for rows.

**R2-2-F4 — hardening, high confidence (probed), self-inflicted (p1-C). `WhyNotLimits` cannot flow through the witness input lane.**
- **Where:** plan WN-D6, spec §6.7, plan WN2-C1.
- **What is wrong:**
  - `read_wire`, `parse_wire` and `intake` call `checked_limits`, which requires `isinstance(limits, WitnessLimits)` (`types.py:33`).
  - The probe showed that a sibling dataclass is refused with `WitnessInputError("limits cannot raise the fixed ceilings")`, a misleading exit 3. A subclass raises `AttributeError: probes`.
- **Fix:** state that the service projects `WhyNotLimits` to a `WitnessLimits` for input loading, and add a test.

**R2-2-F5 — completeness, high confidence, self-inflicted (p1-I). Some pin fixtures are not listed.**
- **What is wrong:**
  - A new `cases.json` case needs a paired `tests/fixtures/rf5-handlers/answers.json` entry, or `test_rf5_handler_pins.py:42` raises `KeyError`. It also needs a `target` for the disabling control.
  - The root and `install`/`doctor`/`uninstall` exit goldens for py311, py313 and py314 also embed the command list. I found "witness-view" in them.
- **Fix:** add `answers.json`, and state that `rf1_pins.py capture` regenerates every golden containing the choices list.

**R2-2-F6 — completeness, high confidence, self-inflicted (p1-I). The WN-D12 rationale is inaccurate.**
- **Where:** plan §3, the "Output schema" row.
- **What is wrong:** the row says `src/gnd/schema/` "holds interchange schemas synced with canonical references (`test_schema_sync.py`)". But `SCHEMA_PAIRS` syncs only `orm-meta`, `population` and `steps`. `witness-result.schema.json`, an output schema, sits in `src/gnd/schema/` unsynced.
- **Fix:** reword the reason, for example "root-level output contracts are what `VENDORED_SCHEMAS` enumerates". The choice itself is fine.

**R2-2-F7 — completeness, medium confidence, self-inflicted (p1-K). The WN1 gate omits the check-contract tests T15 relies on.**
- **What is wrong:** T15 asserts that the "check contract tests [are] unchanged", but the focused gate lists only the witness corpora.
- **Fix:** name the check-contract file or files in the gate.

**R2-2-F8 — hardening, high confidence, self-inflicted (p1-C). WN-R4's claim about the pre-evaluation is not implementable.**
- **What is wrong:**
  - WN-R4 says candidates probed and cells stored are charged "including work inside the production pre-evaluation".
  - The only hook is `_witness_charge`, which is called per merged binding. A zero-output indexed join charges nothing in production (`extensions.py:760-763`).
  - §6.8 forbids editing `extensions.py`.
- **Fix:** restrict the claim to bindings for the pre-evaluation, and note that its probe work is bounded by the input ceilings.

All eight findings are self-inflicted. No original-text defect was found in this lens.
