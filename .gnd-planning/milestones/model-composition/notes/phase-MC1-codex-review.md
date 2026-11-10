# MC1 independent Codex CLI review

One reviewer is one reviewer. Codex CLI gpt-6.1-sol, xhigh, read-only, prompt on stdin; exit 0. Operator home/repository paths in links sanitized to <HOME>/<REPO>; otherwise retained verbatim. No broad/native/provider tests were run by the reviewer.

DISPOSITION: revise

Nine reproduced findings. No files were modified.

1. **MC1-R1 — blocking — Batch refusal becomes exit 70.**  
   [batch.py:157](<REPO>/src/gnd/batch.py:157) returns a refusal with `model_digest=None`, which the public report schema rejects.

   Reproducer:
   ```text
   .venv/bin/python -B -m gnd check tests/fixtures/mc1-includes/project.orm.yaml --populations tests/fixtures/mc1-includes --format json
   ```
   Observed: exit **70**, `None is not of type 'string'` at `model.sha256`.

   **Fix/control:** after detecting the refusal, populate its metadata from the captured bytes’ authentic digest. Preserve guard-first ordering and avoid the adapter’s subsequent model reload. Test the public CLI, including schema validation. This independently confirms the newly recorded self-audit finding.

2. **MC1-R2 — blocking — Composition checks leak the guard exception.**  
   The guard at [checking_service.py:165](<REPO>/src/gnd/checking_service.py:165) raises `ModelValidationError`, but its caller catches only `CompositionError`.

   Reproducer: call `api.check(project_fixture, clean_population_fixture, composition="absent", sources="absent")`. Both this API call and equivalent CLI `main()` invocation raise `ModelValidationError`; neither returns the required band-3 report.

   **Fix/control:** guard this route before model loading and adapt the refusal into its normal band-3 issue payload. Add API and text/JSON CLI regressions; the existing helper-only test misses this escape.

3. **MC1-R3 — blocking — Include-free export refusal spelling changes.**  
   [lean_io.py:72](<REPO>/src/gnd/export/lean_io.py:72) and [souffle_io.py:125](<REPO>/src/gnd/export/souffle_io.py:125) now expose every `ModelValidationError`’s first rule.

   Using the same bounded input, `{"version":4,"object_types":[],"fact_types":[],"unknown":1}`, the preparation adapters return `(3, "input-invalid")`; current adapters return `(3, "jsonschema:additionalProperties")`.

   **Fix/control:** special-case the new include refusal while preserving the historical adapter result for other validation failures. Pin both include-free and include-bearing cases.

4. **MC1-R4 — blocking — `compose` is not total over hostile direct input.**  
   [\_includes.py:104](<REPO>/src/gnd/model/_includes.py:104) performs an unprotected recursive `deepcopy`.

   Read-only reproducer: parse the committed project fixture, replace its `source` with 500 nested `{"nested": ...}` mappings, and call `compose` using a valid retained fixture-root descriptor. Structural validation returns **zero issues**, then execution raises `RecursionError` through `compose:187 → _merge:104 → deepcopy`.

   **Fix/control:** make this path return a documented refusal or use bounded copying. Extend direct-call depth controls beyond the current 200-level parser case.

5. **MC1-R5 — blocking — Include ID `model` corrupts ownership provenance.**  
   [\_includes.py:116](<REPO>/src/gnd/model/_includes.py:116) stores the include ID as the origin; [line 211](<REPO>/src/gnd/model/_includes.py:211) interprets `"model"` as project ownership. That ID is valid under both declaration validators.

   Reproduced with valid included warning constraints: ID `components` reports `includes[components]:$.fact_types[id=...].constraints[0]`; changing only the ID to `model` reports `$.fact_types[0].constraints[0]`. The provenance table also labels included elements as `"model"`.

   **Fix/control:** distinguish ownership kind from include ID. Add the valid ID `model` to ownership, warning, and error regressions.

6. **MC1-R6 — completeness — Direct raw exporters discard the include reason.**  
   [lean.py:954](<REPO>/src/gnd/export/lean.py:954) and [souffle.py:397](<REPO>/src/gnd/export/souffle.py:397) absorb the new witness-intake refusal into `input-invalid`.

   Calling `render_lean` and `render_souffle` directly with the committed project/population bytes returns `(3, "input-invalid")`. Instrumentation confirmed that the actual intake guard first raised **`include:unsupported-route`**—the fixture did not fail for another reason.

   **Fix/control:** preserve that specific reason in both raw adapters, retaining historical behavior otherwise. Test these direct entry points separately from path exports.

7. **MC1-R7 — completeness — Some guards run after competing work.**  
   [session.py:301](<REPO>/src/gnd/exp/session.py:301), its `_case_models` path, and [session_replay.py:66](<REPO>/src/gnd/exp/session_replay.py:66) hash before guarding. With valid include bytes and a stale declared digest, copy/replay helpers raise generic “model changed” errors.

   Separately, [emit.py:26](<REPO>/src/gnd/export/emit.py:26) checks temporal features before guarding. A version-5 includer with an own `Duration` type—which successfully loads through the composed loader—receives the temporal refusal instead of `include:unsupported-route`.

   **Fix/control:** move detection before digest and feature checks, after bounded intake. Add compound-fault controls that assert the competing work was not called.

8. **MC1-R8 — completeness — Own selector-addressed diagnostics change spelling.**  
   [\_includes.py:213](<REPO>/src/gnd/model/_includes.py:213) restores selectors only for included origins.

   For an includer’s own fact type with a valid proposed constraint, semantic validation emits `$.fact_types[id=own_uses].constraints[0]`; the loaded warning becomes `$.fact_types[0].constraints[0]`. This contradicts the promised unchanged own-element paths.

   **Fix/control:** preserve own selectors while retaining attachment remapping to `fact_type_constraints`. Test own, included, and attached constraints together.

9. **MC1-R9 — completeness — Schema/parser digest parity is incomplete.**  
   [orm-meta.schema.json:139](<REPO>/src/gnd/schema/orm-meta.schema.json:139) accepts a digest containing 64 lowercase hexadecimal characters **plus a final newline**. `Draft202012Validator.is_valid` returns true; `parse_declarations` refuses it.

   **Fix/control:** enforce exact length in both schema copies and add this case to parity tests.

I checked and could not refute:

- Committed composed/twin dumps, all three identity functions—including attachments—and clean/cycle/self checker equality, with bands **0/1/1**.
- Runtime import acyclicity, moved-home source visitation—including `errors`—alias identity, pickle/metadata preservation, and the named RF6/RF8 successor pins.
- Exact live query policy and counted dynamic-syntax successor controls.
- Frozen PyRel runtime bytes and the independently retained baseline program digest.

Verification was bounded and read-only: no credentials, network/provider/native calls, reviewer subagents, whole suite, or marked census. The focused log now ends with **995 passed, 3 deselected**; that does not establish the remaining default-suite or census gates. The historical invalid-warning fixture was not used as regression evidence. No additional plan-review round is requested.