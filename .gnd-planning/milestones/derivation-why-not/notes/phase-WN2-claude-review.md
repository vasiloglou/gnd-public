# WN2 diff review

Retained text of the single reviewer's returned report (one local reviewer
agent; one reviewer is one reviewer). Local edits: scratch paths read
`<scratch>`.

**Scope.** I read the whole WN2 spec, including the gate section and sweep S1–S7, and plan §2, §4 (WN2-C1 to C6) and WN-R5. I read the diff from `26e36c8` to the working tree for `service.py`, `view.py`, `witness/cli.py`, `commands/witness.py` and `api.py`. I also read the schema, `tests/test_public_why_not.py`, the corpus `cases.json` and its goldens, every pin edit, the RF6 successor, the docs and the nav entry. I wrote 8 probes under `<scratch>/wn2-review/` and ran them. I also ran 9 test files: `test_public_why_not`, `test_public_api`, `test_v61_phase2_api`, `test_public_reference_signatures`, `test_rf1_cli_pins`, `test_rf5_commands`, `test_rf5_handler_pins`, `test_rf1_pin_harness` (588 passed together) and `test_rf6_query_policy` (17 passed). I did not run the v71 witness corpus, the full suite, the distribution lanes (`test_public_runtime`, `test_public_built_inventory`) or `test_documentation_tutorials`. The `gnd-run` block in `python-api.md` was checked against the G9 raw golden, not executed. I wrote nothing in the repository.

## Claims checked and found true
- **Totality.** No probe got any exception out of `api.why_not`:
  - p3: 24 hostile inputs, including non-str, bytes and None paths, a NUL path, directories, a missing population, malformed YAML, an unknown fact type in the population, missing, int and bytes reference roots, a tampered reference file, and row files with opaque, short, long, bad-primitive, int, list or non-JSON content. All 24 gave 3 `refused input-invalid`.
  - p6: 500 random mutations of the model, population and row gave `Counter()` escapes.
- **Validation order.** G13 refuses a malformed aggregate row (3) before reporting unsupported. The service checks the row file before the model, while spec §4 rule 3 lists it after; the exit is the same either way.
- **Exit bands** match spec §6.3 for every corpus case through both the CLI and the API.
- **Schema accepts every payload kind the kernel can emit** (p4: extended claims model, both views):
  - a `negated` blocker with `reads ['$w']`;
  - a `comparison` blocker with `['$a']`;
  - a `head` blocker with `['$a','$w']`;
  - a `head-bind:constant` blocker;
  - an atom blocker with a constant role.
- **Redaction.** For those same payloads, none of `val-w1`, `val-w2`, `1004`, `val-const-head`, `val-const-atom`, `val-other`, `9999` or `1005` appears in redacted output. The view is a closed selection by key name; the recursive descent and the unavailable binding are covered, and `reason` values are fixed `term:*` strings.
- **Intake limits.** The projection matches the spec. The digit ceiling really applies: with intake disabled (p2), 129 and 200 digits give exit 0; with it enabled (p1), 128 gives 0 and 129 gives 3. The 1,000-target row file stops at the count check.
- **Pins.** All three `__all__` literals and the runtime tuple, the `why_not` signature assertions, `EXPECTED_PARSERS` 57 in both files, the rf1 goldens (exit-golden diffs are only the command list) and the manifest digest, the rf5 case and answer, `VENDORED_SCHEMAS`, and the RF6 successor (passes).
- **Docs.** `python-api.md` says "nine functions", which matches its own list. The bands, limits, descent stops (`MAX_DESCENT` 8) and the redaction description in `why-not.md` match the code. The python-api example's sample values match the G9 raw golden.

## Findings

### WN2-R1 — The schema does not enforce the band/reason pairing or the redacted view (hardening, high)
**Where:** `src/gnd/why-not.schema.json` (the `allOf` block and `$defs/blocker`, `role` and `unavailable`).

**What is wrong:**
- §6.3 ties `input-invalid` to exit 3 and `work-limit` to exit 4, and requires a refusal to have null `fact_type`, `mode` and `order`. The schema only allows reason ∈ {both} and exit ∈ {3, 4} independently, and leaves the other fields free.
- `view: "redacted"` is not tied to redacted fields, so a raw payload labelled `redacted` validates. Each field accepts a raw value or `"redacted"` independently.
- T2 only refuses six samples, which is a `maxItems` case, not a redaction case.

**Reproduction (p5_schema.py):**
```
raw values labelled view=redacted valid: True
refused/work-limit with exit 3 valid: True
refused/input-invalid with exit 4 valid: True
blocked with no clauses valid: True
refused carrying fact_type/mode/order valid: True
unavailable with null unavailable/reason valid: True
```

**Fix:**
- Split the `refused` condition by reason: `input-invalid` → exit 3 and `work` with `maxProperties: 0`; `work-limit` → exit 4.
- For `refused`, require `fact_type`, `mode`, `order` and `unavailable` to be null.
- For `unavailable`, require an object and `reason` matching `^term:`.
- For `blocked`, require `clauses` with `minItems: 1`.
- Add `if view = redacted then` a redacted variant of the clause, blocker, role and unavailable definitions in which `samples`, `constant` and `binding` are `const: "redacted"`.
- Add negative T2 cases for each of these.

### WN2-R2 — The `nan` and `deep` cases in G12 pass even with intake removed (hardening, high)
**Where:** `tests/test_public_why_not.py`, `_hostile_inputs` and `test_g12_hostile_inputs_exit_3`.

**What is wrong:**
- The NaN goes into a `code` role and the nesting into `population.note`. The population loader refuses both for shape, at any depth and for any number.
- So neither case exercises the depth or nonfinite ceiling that §6.1 and WN2-C1 claim. Only `long-int` depends on the service's intake.
- A deep term in the model is also refused by the loader at depth 40, so the depth-64 ceiling seems unreachable from files. It works as defence in depth but cannot be observed through these inputs.

**Reproduction:**
- p1_hostile_controls.py, controls under the ceiling: `deep-header-3 3 refused`, `deep-fact-3 3 refused`, `listed-number-control 3 refused`.
- p7_mutants.py with `io.intake` disabled: `1 failed, 3 passed`. Only `[long-int]` fails.
- p8: model term depth 40 with intake off → `3 refused`.

**Fix:**
- Give each hostile case a passing control (just under the ceiling, otherwise valid).
- Call `gnd.witness.io.intake(..., limits=_why_not_intake_limits())` directly on depth-65 and NaN documents. That pins the ceilings in code, rather than through the loaders.
- Or say in the test that the loaders refuse first.

### WN2-R3 — No test exercises the constant-role, `reads` or head-bind parts of the redacted view (hardening, high)
**Where:** `src/gnd/witness/view.py`, `_why_not_role`, and the `reads` branch of `_why_not_clause`. The corpus goldens contain only atom blockers with variable roles: `grep constant goldens/*` matches nothing, and no golden has a negated, comparison or head blocker.

**What is wrong:**
- Spec §6.4 requires rule constants to be redacted.
- Changing `_why_not_role` to copy the constant is not caught.

**Reproduction:** p7_mutants.py `leak-constant`, with `view._why_not_role = lambda spec: dict(spec)`, gives `44 passed`. The current code does redact correctly (p4 shows no leaks).

**Fix:**
- Add a corpus case with a constant in a body atom. The p4 `pinned` rule in the probe file is one: `wrote(work:$w, person:"val-const-atom")`.
- Add one negated, one comparison and one head blocker case, with goldens in both views.
- Add the constants to the T4 leak value set.

### WN2-R4 — Two pages still give an old API count (completeness, high)
**Where:**
- `docs/bookrec/06-evolution.md:186`: "the seven stable application API functions".
- `docs/runtimes/decision.md:93`: "The seven stable Python functions".

**What is wrong:** WN2-C4 and standing rule 5 make `python-api.md` the one home of the count, and it now says "nine functions". These two pages still state a different number. The count was already stale at eight before WN2. Spec §6.7 only named `tour.md` and `cli.md`.

**Reproduction:** a `grep -rniE "seven[- ]function|seven stable"` over the docs finds only these two lines.

**Fix:** Change both to "the stable [Python API](../../../../docs/reference/python-api.md)" with no number.

No blocking defects found: totality, redaction of what the code emits, the exit bands, intake and the pins all hold under the probes.
