# OS4 candidate 4c9416ce: independent diff review

**Decision: conditional accept.** I found no defect in the gate's pass/fail logic, and it can serve as a regression boundary. Three small changes are needed before OS4 closes: the "dropped requires" label, a reconciliation guard in the extractor, and the offline-guard claim. I read all of this and ran nothing, so none of the passes, hashes or timings below are re-measured. I read only the diff and the named sources.

## Claims I checked

- **All intact exports are attempted.** The loop covers every `CENSUS` line except the three `INCLUDE_ROOTS`, and `assert len(cases) == 38` pins the count. The evidence file has exactly 38 case rows.
  - Converter results are collected before any assertion, and the JSON is written before the asserts run.
  - The pass counts in 018 (49 deselected, then 48 deselected) are consistent with a 41-line census plus 8 other oracle tests.
- **A new mismatch fails the gate.**
  - `failures` is every row with a nonzero exit or a non-empty difference, and the test asserts that set equals the two known cases.
  - A new refusal, a new mismatch, or a known case that stops failing all break the gate.
  - Each known case also needs a diagnostic substring match. The isolation controls and the requires control must be exit 0 with an empty difference.
  - Timeout (124) and invalid source (3) are nonzero, so they fail too.
- **Declaration comparison is accurate for what it compares.**
  - The direction of `difference` is right: missing is expected minus observed, extra is observed minus expected.
  - The static test's expected dict matches what the altered source implies for parent, relationship and identifier.
  - Variable renames (`Model_2`) resolve through `bindings`, and `Property` and `Relationship` are merged consistently.
  - The evidence is internally consistent. Cases sharing an `ontology_sha256` share a `pyrel_sha256` (bookrec, expense, course/haiku). The requires counts per case match the `formulas` lists.
- **The two refusals are pinned specifically.** The composition diagnostic is `type-membership Lookup`, and the library diagnostic is `[Invalid identify_by] Property LibraryItem.gnd_reference`. The isolation pointers recorded in the evidence match what the test removes (`/ontology/0/relationships/1/derived_by`, `/ontology/1` and `/ontology/2/identify_by`).
- **The companion LQP numbers match 018.** The formula corpus gives 12 `require` calls, and four of the 38 models are refused. The refusal reasons come from the renderer's own `ExportInputError`.
- **The evidence file has no machine paths and no timestamps.**

## Concerns

1. **"converter-dropped-requires" is stronger than the evidence.**
   - The only observation is zero `.require` calls in `to_pyrel(model.base_model().to_metamodel())`.
   - The label is attached to every `requires` formula whenever that count is 0. The check `len(limitations) == len(formulas)` therefore passes by construction.
   - The converter may hold requires outside `base_model()`, or codegen may not print them.
   - The OR/EXISTS controls support the label. An `OR` in `requires` converts, while an `OR` in `derived_by` is refused, so requires bodies appear not to be translated at all. That is still inference.
   - Reword the label to something like `no-require-in-emitted-source`, or confirm it in the converter's handling of `requires`. That source is outside my scope.
   - Partial emission is also unflagged. If a future pin emits 3 of 8 requires, no limitation is recorded and nothing fails.
   - `calls` records only six call names. Add `where` and any negation or constraint calls so "emitted requirements" can be judged.

2. **The AST extractor can hide extra declarations.**
   - `_assignments` sees only top-level `x = m.Attr(...)`. An unassigned `m.Concept("Rogue")`, a nested one, or a name-call is ignored. Missing declarations still surface, but extras do not.
   - Evidence already records `calls` per case, and the gate never reconciles it with the declaration counts.
   - Add `sum(concepts) == calls["Concept"]`, `sum(relationships) == calls["Property"] + calls["Relationship"]`, and the number of concepts with an identifier equal to `calls["identify_by"]`.
   - Add a static negative control for an extra unassigned concept and for a concept-name mismatch. The `concepts` branch of `difference` has no control.

3. **The offline guard is weaker than the wording in 018.**
   - It is an in-process audit hook on `socket.connect` and `socket.getaddrinfo` only.
   - `sendto`, `gethostbyname`, `getnameinfo`, `subprocess` and `ctypes` are not covered.
   - The self-test exercises `getaddrinfo` only. It never exercises `connect`, the call that actually matters.
   - Hook events are neither logged nor asserted to be zero. If the converter swallowed the `RuntimeError`, the run would pass silently, so "the converter subprocess refused socket access" cannot be shown from the evidence.
   - Have the hook write a marker and assert zero events, or reword the claim to "guard active; no refusal diagnostics observed". Label it a guard, not a sandbox.

4. **Pin gaps.**
   - `check_pins` uses `git diff --quiet HEAD`, which ignores untracked files. `sys.path[:0]` puts `checkout/*/src` ahead of site-packages, so a stray untracked module could shadow the pinned code. Add an untracked-files check (`git status --porcelain`).
   - The wheel digest is verified on the file in scratch. The subprocess only asserts `importlib.metadata.version == "1.39.0"`. Nothing ties env `c` to that wheel.
   - The `raiconfig.yaml` hash is checked from the same checkout the subprocess reads, which is fine.

## Limits to state

- **The library refusal is export-induced.** `_inherit_identifiers` (`ossie.py:243-255`) deliberately copies the parent's identifier onto the child, and the converter rejects that shape. "consumer-inherited-identifier" is accurate, but it should say the GND export choice triggers it. A variant that omits the child `identify_by` is an open question for the owner.
- **No derivation is observed to convert.** `define` is 0 in every successful case and isolation.
  - Both refusals involve chains, and the OR/EXISTS controls fail earlier.
  - A single-atom `derived_by` control (for example `Account.account_active` on `account_flagged`) would show whether any derivation converts. Without it, "derivation unsupported" rests on three failure shapes.
  - The record already says the chain premise was refuted.
- **Comparison is names and edges only.** It does not compare relationship target types or readings, multiplicity, concept kind, or the `Property`/`Relationship` distinction. "36 matched" means identity agreement, not semantic equivalence. Constraints are not covered at all: all 36 emitted sources have 0 requires.
- **The LQP companion is informational.**
  - Only `corpus > 0` is asserted. The four renderer refusals and the counts are recorded but not pinned.
  - The counts are raw `.require` calls, not comparable one-to-one with Ossie formula counts. Models with 0 rules (staffing, type_judgements) still convert.
  - The amendment's claim that LQP "emits the `require` calls being counted" is true, but the `duckdb` target prints the same `require` shape, so LQP is not the only choice.
- **Isolation controls** show that the removed fields are sufficient for the converter to proceed, not that each removal is necessary. The two library removals were not tried separately.
- **Minor:**
  - `render_ossie` errors abort the loop and skip the evidence write (fail-fast, not collect-all).
  - `RecursionError` or `MemoryError` from `ast.parse` is uncaught.
  - The ordinary test `test_os0_refund_snapshot_is_compared_without_a_converter` reads `.gnd-planning/...`. That path is tracked here, but it couples the default suite to planning files.

## Reproduction leads (read-only first)

1. Recompute SHA-256 of `consumer-limitations.json` (expect `a1cd2ad3…9d4b`) and the amendment hash (expect `681a15fd…cb52`).
2. From the JSON, check these invariants:
   - 38 cases.
   - Exactly the two exit-1 cases.
   - Every exit-0 `declaration_difference` is empty.
   - `calls.require` is 0 everywhere.
   - `limitations` count equals the requires formula count in every exit-0 case.
3. Opt-in lane: rerun with `GND_OSSIE_CONSUMER_OUTPUT` and diff the output against the committed JSON. It should be byte-identical apart from timing flakiness near the 30s cap.
4. Mutation checks:
   - Add an unassigned `m.Concept("Rogue")` to a static source. The current extractor reports no difference, which demonstrates concern 2.
   - Swap a `Property` target concept in the static source. The comparison stays silent, which demonstrates the limit on target types.
5. Offline guard: temporarily add an `AF_INET` `sendto` or `gethostbyname("example.invalid")` to the converter script. The current hook does not trip, which demonstrates concern 3.
6. Library variant: strip only the child `identify_by` and convert. Then strip only `PeriodicalItem`'s. This settles necessity and the export-versus-consumer attribution.
7. Add a one-atom `derived_by` to the corpus-minus-chain control and check whether `define > 0`.

## Required before closure

- Relabel or substantiate "converter-dropped-requires" (concern 1).
- Add the count reconciliation and the two static negative controls (concern 2).
- Either log and assert zero hook events, or soften the offline claim in 018 (concern 3).

The remaining items (the library attribution, the missing positive derivation control, and the untracked-files and wheel pin gaps) can be recorded as documented limits in the closure note.
