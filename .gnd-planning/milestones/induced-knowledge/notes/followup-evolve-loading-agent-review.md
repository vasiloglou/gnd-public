# Evolve-loading follow-up — adversarial review of the diff

**Reviewer:** one local reviewer agent, 2026-10-27, over the working-tree diff
after commit `f2507ca` (the red tests) with the fix applied. It was given the
spec and the code, not the author's conclusions. **One reviewer is one
reviewer.** It edited no repository file; its scratch work stayed outside the
repository.

## Report (condensed by the author: reproduction folders and run counts trimmed; claims and wording otherwise kept)

> I found two blocking regressions and one hardening gap; the completeness check found nothing.
>
> **B1. `gnd discover` now crashes on any valid model with a timezone-aware timestamp (base exits 0).**
> - Cause: `_parse_model_text` calls `_json_document(..., refuse=False)`. Its fallback returns ruamel's round-trip `TimeStamp` object as it is, where the old safe reader returned a plain `datetime`. Discover's block-YAML writer cannot represent a `TimeStamp` that carries a timezone.
> - Reproduce: the staff fixture with `  created: 2024-01-01T10:00:00+02:00` under `source:`; `gnd discover … --families uniqueness`. Change: traceback ending `ruamel.yaml.representer.RepresenterError: cannot represent an object: TimeStamp(2024, 1, 1, 10, 0, tzinfo=...+02:00)`, rc=1. Base: rc=0.
> - Scope: `gnd validate` exits 0 on this model. `...T10:00:00Z` (and lowercase `t`) fails the same way. Naive timestamps still work.
> - Possibly also ILP: ILP import builds its candidate through the same path. I did not reproduce that.
> - Fix: in non-refuse mode, turn `TimeStamp` back into a plain `datetime`, as the safe reader did. Test gap: E1/D5 cover only a date and a tag.
>
> **B2. The YAML guard now runs outside the `YAMLError` handler, so valid JSON input can exit 70 (previously-3 case now 70).**
> - Cause: in `_load_model_document`, `_rf7_input.guard_yaml(data)` runs after the `try`, and only `ValueError` is caught. Strict JSON that YAML cannot scan escapes as a raw `YAMLError` and maps to EXIT_INTERNAL, e.g. a flow-mapping key longer than 1024 characters inside a free-form `description` map.
> - YAML model with that key: change `(70): while parsing a flow mapping ...`; base `(3): candidate model is not valid YAML at line 1, column 1315`. `gnd validate` exits 0.
> - `.json` model with the same key: `gnd validate` exits 0, preview gives 70; base was also 70 ("current model is not" matches no CLI marker). Not new, but the spec's "never 70" is still broken.
> - Fix: catch `YAMLError` around the guard and turn it into a "validation failed" refusal; better, skip the YAML guard for input that took the strict JSON branch.
> - Related latent issue: `_yaml_refusal` with any label other than "candidate model" produces a message no CLI marker matches, so it exits 70.
>
> **H1. Remaining exit-70 paths and unused tag information.**
> - The guard's `ValueError` messages ("YAML alias refused", "YAML depth cap exceeded", …) are wrapped as a plain `EvolutionError(str(error))` with no malformed marker, so they would exit 70. Not reachable through a validate-accepted model; no test covers the branch.
> - The strict walk accepts a core tag on the wrong node kind: `a: !!str {b: 1}` passes as a plain mapping. The old safe reader refused it.
> - Kind names are uneven: `!!value` and `!!merge` read `tag tag:yaml.org,2002:value`. Cosmetic.
>
> **Completeness: checked, no defect found.** Old vs new parse for JSON-domain documents (ints in every base, `ScalarFloat` forms, big ints, block scalars, trailing whitespace, BOM, CRLF, comments, flow mappings starting with `{`, merge keys, anchored scalars, keep-mode YAML-only values, explicit core tags) gave no differences. Escaped surrogate pairs differ in the new code's favour. Anchored booleans become 1/0, but `gnd validate` already refuses them. Apply's reordering keeps every previously tested exit (selected suites: 200 and 241 passed). `.json` strictness reaches apply and finalize. Reference exits 66/74/3 come through. Side note: each model is parsed twice plus a guard pass; a cost, not a correctness issue.

## Disposition

Each finding was reproduced before it was believed. Regressions RV1..RV4 in
`tests/test_evolve_loading.py` fail on the reviewed code
(`evidence/evolve-loading/regressions-red.txt`: 7 failed, both RV2 cases at
exit 70) and pass after the fix.

| Finding | Triage | Disposition |
|---|---|---|
| B1 | blocking (a base exit 0 became a traceback) | **Fixed.** Keep mode returns a plain `datetime` with its zone, equal to the safe reader's. RV1 (`+02:00`, `Z`): discover 0, preview 3 naming the timestamp |
| B2 | blocking (a base 3 became 70; "never 70" broken) | **Fixed.** `_guard_yaml_document` runs the YAML guard only on documents the YAML reader built; a strict-JSON document is not re-read as YAML. RV2: both the YAML model with a JSON candidate and the `.json` model now preview 0 |
| B2 latent, `_yaml_refusal` labels | hardening | **Fixed.** One CLI marker, "is not valid YAML", maps every model's YAML refusal to 3 (RF5 successor for `_evolve_service_exit`). RV3 |
| H1 guard messages | hardening | **Fixed.** Guard and loader refusals in the parse carry `{label} validation failed:`. RV3 |
| H1 core tag on a collection | hardening | **Fixed.** Only a collection's own core tag passes the strict walk. RV4 (`!!str {b: 1}`, `!!str [1]`); the round-trip reader itself refuses the other core scalar tags on collections |
| H1 kind names | cosmetic | **Fixed** with RV4's change: `tag:yaml.org,2002:` prints as `!!` |
| ILP via the same path | — | Covered by the B1 fix (one function); the IK5 suite is in the gate. Not separately reproduced |
| Double parse cost | — | Kept; recorded in the record's refactoring review |

---

# Round 2 — amendment r2's diff

**Reviewer:** one local reviewer agent, 2026-10-27, over the r2 working-tree
diff after `d594717` (the r2 red tests), given the spec and the code. **One
reviewer is one reviewer.** It edited no repository file. To get "before"
behaviour it ran the same code with the new guards replaced by no-ops.

## Report (condensed by the author: reproduction script names trimmed)

> **B1 — blocking: recovery verify and the verbalizer now refuse valid models that verified before.** `!!omap` and `!!pairs` values pass `gnd validate`, and the old `render_model_verbalization` rendered them, because `json.dumps` writes a tuple or ordered map as JSON. `verify.py`'s walk refuses both ("tag !!omap", "tag !!pairs"); the verbalizer guard refuses pairs (a list of tuples after `model_dump`) and passes omap, so the two guards disagree. This contradicts r2.2 and F13. Reproduced: omap and pairs bundles, old ok=True, new ok=False.
>
> **H1 — hardening: the new refusal now pre-empts `invalid-model-origin`.** A model with `source: {kind: text-conversation, created: 2024-01-01}` used to fail `invalid-model-origin` and now fails `invalid-model-value`. Exit 3 either way; the error code changes.
>
> **C1 — completeness: the verbalizer still leaks `TypeError` for an explicit `!!str` tag.** `provenance: {user_note: !!str 5}` loads as a ruamel `TaggedScalar`; the guard turns it into a string and passes it, and `_canonical` then raises `TypeError`. Not a regression.
>
> **C2 — completeness: `gnd import ilp-rules` changed outcome, untested and unrecorded.** It shares `candidate_text`. On the IK5 corpus with `source.x: .nan` (digests rebound): before, a traceback (exit 1); after, exit 0 with a YAML candidate. Consistent with D7 and with dates, but a second command whose exit moved.
>
> **Checked, no defect:**
> - **Reference homes (D6):** every adopted site behaves as before. `gnd.references.bind_references` is the same object; `reference_root` defaults and check-then-bind order are kept; the exception tuples see the same types; `attach` is set only where it was (evolve, discover, session_contract); monkeypatches still take effect. A mutant dropping session_contract's `attach` failed an existing phase-4 branch test.
> - **The verbalizer over 171 valid models:** 0 output or error differences; render time 0.03s before, 0.04s after.
> - **Constructed values:** dates, sets, nan, inf and binary now give `VerbalizationError` instead of `TypeError`/`ValueError`. Core tags and big integers render as before.
> - **Discover with `.nan`:** population values cannot be non-finite, so the reload shares the model's own nan.

## Disposition

Each finding was reproduced before it was believed (B1 and H1 with the
reviewer's script; C1 and C2 by the regressions below). RV5..RV7 fail on the
reviewed code (`evidence/evolve-loading/r2-regressions-red.txt`, 5 failed).
RV8 pins D7's writer change, already applied, and passes by design.

| Finding | Triage | Disposition |
|---|---|---|
| B1 | blocking (a base 0 became 3) | **Fixed.** `json_document(..., encodable=True)` refuses exactly what `json.dumps` cannot write: a tuple and an ordered map pass, and so does a tagged collection (author's extra case, `!foo {a: 1}`, also refused by the reviewed code). Recovery verify and the verbalizer both use it. Evolve keeps the strict mode. RV5: omap, pairs and a tagged mapping verify, 0 |
| H1 | hardening | **Fixed.** The recovery refusal runs after the origin check. RV6 |
| C1 | completeness (pre-existing `TypeError`) | **Fixed.** In encodable mode a tagged scalar of any tag is refused by name. RV7 |
| C2 | completeness | **Recorded and pinned.** RV8 checks `candidate_text` round-trips `inf`, `-inf` and `nan` for both callers; record 014 names `gnd import ilp-rules` beside discover. No end-to-end ILP case was added |
