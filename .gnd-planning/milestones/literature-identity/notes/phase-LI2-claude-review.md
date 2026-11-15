# LI2 Claude Code diff review

Claude Code 2.1.322, one read-only reviewer, high effort, prompt on stdin.
The prompt and bundled diff SHA-256 is `379c414623fe1694c7816a45f8723fe09b07196f69371189326d359ffc0ae06d`.
The phase started at `457baeb3`. This review covered the first implementation
snapshot. The phase record describes subsequent repairs and their gates.
The following output is retained verbatim with host paths sanitized if present.

---

I found one actionable defect of medium-to-high severity and several low ones. I traced every R1–R7 path in the code without finding a contradiction. I ran nothing: no pytest, compose or builder. Everything below comes from reading the spec, the 008 ruling, the diff and the code it touches. I did not open the reserved held-out ref or any credentials.

## Findings

### F1 · Medium–High · An `anchored` constraint without `role` crashes compose
**Where:** `src/gnd/composition_resolution.py:164-165`

`ResolutionEvidence.__init__` reads `rule["role"]` and `rule["type"]` directly. A fact-level `anchored` constraint with no `role` is a valid "all roles" variant:
- the checker handles it at `checker/_core.py:1873,1882,1897` and `checker/_composed.py:50`;
- `popvalidate.py:533-534` treats it as covering every declared role;
- `tests/test_tp3_check_receipts.py:144` builds one.

**Effects:**
- **The crash.** With a `resolution` present, compose raises an uncaught `KeyError`. `api.compose` catches only `CompositionError` (`api.py:1005`), so the result is a traceback or internal error, not exit 3. That breaks the totality rule, and `gnd check --composition` goes through the same path.
- **If the key were present as `role: null`:** the role would silently count as unanchored. A span-less coordinate would then pass, and a correct span would be refused with "names a span for an unanchored role".
- **A related fragility:** `fact.get("constraints", ())` raises `TypeError` on `constraints: null`. Other readers use `or []`.

**Reproduction:**
1. Copy `resolution/model.orm.yaml`.
2. Replace the two `anchored` constraints on `method_builds_on_method` with one `- type: anchored` that has no `role`.
3. Run `gnd compose <model'> src/gnd/examples/literature/resolution/cases/A-alias --out … --record …`.

No sidecar needs rebinding, because `vocabulary_digest` excludes `constraints` (`anchors.py:214`). Expected: exit 0 or a clean exit 3. Actual: `KeyError: 'role'`.

**Fix:** use `rule.get("type")`, expand a `None` role to all the fact type's roles, and use `fact.get("constraints") or []`.

### F2 · Low–Medium · Placeholders are checked against keys only, not every composed value
**Where:** `composition_resolution.py:285`

Spec §6.2 says placeholders must be "distinct from every composed value of that object type". The shared-placeholder check only counts coverage keys, which come from asserted roles. Two kinds of composed value escape it:
- instance-only values;
- values in claimed derived rows.

The docs (`composition.md`, "Other keys of that object type…") match the code, not the spec.

**Reproduction:**
1. Take H-unresolved.
2. In `hom-b`, add an instance-only `method` value equal to `TRACE#1`, if the model admits instance listings for `method`.
3. Rebind the sidecar, the `input_sha256` and the manifest digest.
4. Compose. It exits 0, and hom-a's unresolved placeholder becomes the same composed entity as hom-b's listed instance.

This needs an owner call: narrow the spec sentence, or extend the check.

### F3 · Low · The report still lists `identity_pairs` as unscored
**Where:** `assurance_report.py:834`

`unscored_labels` still includes `identity_pairs` with owner `LI2`, even though the stage now scores them. The report contradicts itself. The gate-approved test pins this at `tests/test_li1_assurance_report.py:199`, so changing it returns to the owner.

### F4 · Low · T20 doesn't time what spec §4.2 describes
**Where:** `tests/test_li2_resolution.py:298-311`

- The spec says T20 "composes" 200 × 200 × 20,000. The test calls only `check_coverage`, with 19,900 decisions.
- It refuses inside the joined-group pass. So the spelling pass, the `different` and `unresolved` branches, `bind` and `keys_and_lineage` are never timed.

Reading the code, all of them are linear, with no pairwise product. The bound most likely holds, but this test doesn't show it. The test is gate-approved.

### F5 · Low · The "one walk" source scan is shallow
**Where:** `tests/test_li2_resolution.py:259`

`glob("*.py")` doesn't recurse. `assurance_report.py:556,558` compares `decision["decision"] == "unresolved"` and `"same"`, and has its own union-find. D7 allows the harness reading, but the pin is weaker than the spec's "no other module compares the decision kinds".

### F6 · Low · A typo'd fact type gets a misleading refusal
**Where:** `composition.py:251-253` vs `:261`

With a resolution present, rule 6 runs before the step-4 check "names a fact type or role the model does not declare". A misspelled `fact_type` gets `role_object_type → None` and is refused as "cites decision N, which does not name its key". That respects the validation order, but the message points at the wrong cause.

### F7 · Low (structural) · `CompositionError` moved home with no recorded alias
**Where:** `composition_resolution.py:21`

`CompositionError` is now defined here and re-exported from `gnd.composition`. Identity is preserved, but `__module__` changed. No identity-alias or shim entry records the move, which the AGENTS.md refactoring convention asks for. `_row_key`, `_scalar`, `_keys` and `_json` were also dropped; I found no references to them.

## Claims checked and supported (static tracing)
- **R1:** the W-resolved path is structurally sound.
- **R2:** MV-joined-no-same goes through rule 1. Coverage is skipped within one source (`:294`).
- **R3:** A-alias, H-no-decision and H-different each reach the expected rule.
- **R4:** every approved R-case message in `cases.json` matches a code template character for character: `_pair_refusal`, the rule-6 messages, B4, connected, evidence (holds key / anchor), stale input, digest, not joined, placeholder. The digest refusal comes before the uncovered pair, and evidence comes before coverage.
- **R5:**
  - a changed decision trips the digest check, or `manifest_sha256` once the manifest is rebound;
  - `verify_composition` compares `resolution_sha256` and `facts`;
  - `parse_record` requires the two fields together.
- **R6:** with M7, the `same` connectivity gives 3/4 precision, with no `different` in its way.
- **R7:** H-unresolved goes through rule 4 with distinct placeholders.
- **Legacy behavior:** without `resolution`, the field sets, refusal messages and order are unchanged. The added `isinstance(str)` guards give the same messages. Records without the new fields go through the old checks.
- **Validation order:** manifest, then digest, then parse, then rule 6, then load, then input digests and evidence, then step 4, then coverage. This matches §6.4 and B3–B4.
- **Totality of `parse_resolution` and `parse_manifest`:** every field is type-guarded before membership or comparison. The 4 MiB cap is on the read.
- **Decision evidence:** the source and object type match, the row and role hold the value (exact type and repr), the role is asserted (B1), the span exactly matches a bound anchor, and spans are refused on unanchored roles. Echoed identifiers are model or manifest ids only, checked before echoing (`:185-187`).
- **Coverage logic:**
  - B2's key shape and coordinate order are as ruled;
  - rule 5 means `same` components can't leave a joined group;
  - the counting form of rule 2 is exact, because separated partners always have different outcomes and a set removes duplicates.
- **Harness:**
  - floors as approved;
  - no resolution → not-measured, owner `run`;
  - R4 refused → `route_refused`;
  - no composed output → owner `run`;
  - an empty denominator fails;
  - `DOCUMENT_CAP` equals the 4 MiB resolution cap;
  - the approved `.expected.json` files are untouched, and only `.report.json` files changed.

## Could not verify
- **B3 tie-break:** "decisions in index order (rule 5, then 3, then 4)" could mean decision-first or rule-first. The code is decision-first. No approved case has faults on two decisions; for example, decision 0 `different` ending joined plus decision 1 `same` not applied.
- **Anything that needs running:** T16 baseline bytes, the T1 witness exits, the actual T20 timing, the measured M7 derivation recall of 7/8, and whether the reference run's `resolution.json` is byte-identical to `li1-reference.resolution.json`.
- **Value-freeness of `strict_json` error text** on hostile input. T18 checks only the prefix.

## Broader structural concern
Two things are design consequences, not defects:
- D2 and B1 put coverage under host control. A resolution can list an unrelated type (or `[]`) and leave joins of every other type unchecked. B1 also skips the asserted rows of semiderived types.
- With a resolution present, every renaming must cite a decision about a covered key. So you can't normalize uncovered types, such as dates, alongside one.

The harness then scores only what the run chose to cover, and fails closed, at 0/0, only when nothing is covered. It may be worth requiring `object_types` to include the answer key's object type before the stage counts as measured.
