# IK1 adversarial diff review (one local reviewer agent)

**One reviewer is one reviewer.** This is a single local reviewer agent's
reading of `git diff 1d6eee0 ad52105`, not a panel. The reviewer was told to
refute IK1-C1..C5 and the T1–T14 tests. It could run targeted commands and
mutants on copies of `src/`, but not the full suite or `evolve apply`/`finalize`.
It modified no repository file.

**Retention.** The reviewer's final report is reproduced verbatim under
"Reviewer report (verbatim)". The reviewer substituted `<repo>` and `<S>` for
the worktree and scratch paths itself. The only edit demotes its headings one
levels to fit this file. The coordinator's reproduction and disposition come
first.

## Disposition (coordinator, 2026-10-24)

Every finding was reproduced before acceptance unless marked otherwise.

| ID | Class | Reproduced | Disposition |
|---|---|---|---|
| R1 lone surrogate crashes renderers | hardening | yes: validate 0; `gnd diff` INTERNAL ERROR; `gnd codegen` UnicodeEncodeError | **fixed**: the IK1-D6 layer-1 screen refuses it inside descriptions. T2 `lone-surrogate` and `nested-lone-surrogate` were red before the fix |
| R2 anchored boolean carried as `1` | hardening | yes: `canonical={"description":{"flag":1,...` | **fixed**: the screen refuses ruamel `ScalarBoolean` inside descriptions (D14 says extras are carried unchanged). T2 `anchored-boolean` was red before the fix. Hex and anchored integers still validate (new test) |
| R3 no declared depth bound on extras | hardening | not reproduced here (reviewer measured depth 242/243 on Python 3.14) | **deferred to the owner**: a new numeric bound needs an owner-recorded amendment (IK-R12). Open question IK1-Q1 |
| R4 core-key order unpinned | completeness | the mutant survived the original tests (reviewer) | **fixed**: `test_t3_core_keys_render_in_one_fixed_order`; fails against the reversed-order mutant |
| R5 summary-only docstring unpinned | completeness | the mutant survived (reviewer) | **fixed**: `test_t4_docstrings_render_summary_only`; fails against the all-keys mutant |
| R6 redaction pass-through vacuous | completeness | the mutant survived (reviewer) | **fixed**: `test_t8_annotations_survive_active_applied_redaction`; fails against the annotation-nulling mutant |
| R7 text-format diff shows no annotations | completeness | not reproduced | **deferred**: outside §5, which requires JSON only. Open question IK1-Q2 |
| note: verbalization-patterns wording | docs | yes | **fixed**: names the population-value neutralizer |
| note: diff.reference.md H1 | docs | yes | **fixed**: lists both versions |
| note: T7 row 4 includes raw `gnd_version` | test boundary | by reading | **recorded**: the spec's row 4 hashes raw bytes; a version bump needs a declared normalization (IK1-Q3) |
| note: T13 cannot fail alone | test boundary | by reading | **accepted**: T5 kills the escape mutant; T13 pins identity only |
| note: runtime `__doc__` line forging | pre-existing at B | not reproduced here | **deferred**: IK1-Q4 |
| note: description can restate a constraint | design boundary | n/a | **recorded** in the record's boundary |

## Reviewer report (verbatim)

### IK1 adversarial review: `git diff 1d6eee0 ad52105`

I found no blocking findings. The code meets the C1–C5 claims for the inputs the spec names. Two hardening findings are pre-existing loader or renderer gaps that IK1 now carries into the new field; R3 is new with IK1's recursive extras schema. Five completeness findings are tests that pass against a wrong implementation, plus one gap in what the text output shows.

Paths: `<repo>` is the worktree root and `<S>` is my scratch directory (`/private/tmp/claude-501/<session>/scratchpad/review`). Scripts used: `<S>/probe.py`, `<S>/mutate.py` and `<S>/evolve_probe.py`. Mutation runs used copies of `src/` under `<S>/mut/<name>/src`, run with `PYTHONPATH`. Base-commit runs used `git archive 1d6eee0 src` extracted to `<S>/base/src`. No repository file was modified.

#### Findings

**R1 — hardening (pre-existing class, now reachable through descriptions). A lone surrogate in a core key passes validation, then crashes four commands.**
- **Claim falsified:** standing rule 1 and Q6 ("any description input that passes validation but crashes").
- **Reproduction:** insert `description: {summary: "a\uD800b"}` under `name: Borrower` in `library.orm.yaml`, then run `uv run python <S>/probe.py <repo> <S>/out1`:
  - `gnd validate` → 0.
  - `render_model_verbalization` → `UnicodeEncodeError ... surrogates not allowed`.
  - `render_verbalization` → the same error.
  - `gnd diff --format json library.orm.yaml M` → exit 70, `INTERNAL ERROR: 'utf-8' codec can't encode character '\ud800'`.
  - `gnd codegen` → exit 1 with a traceback; `gnd extract` → exit 1.
- **At B:** the same holds for an object-type `name: "Borr\uD800ower"` (validate OK, verbalize `UnicodeEncodeError`). So this is not a regression, but the new 4,096-character field gets the same gap.
- **Fix:** refuse lone surrogates (U+D800–U+DFFF) at load, for example in the `_layer1_structural` walk. At minimum scope it to `$.object_types[i].description` with `jsonschema:type`, like the IK1-F1 screen.
- **Regression test:** T2 case `description: {summary: "a\uD800b"}` (and nested in an extra) expects exit 3. It fails today (exit 0).

**R2 — hardening (pre-existing ruamel round-trip behaviour). An anchored boolean extra is silently turned into the number 1, so extras are not "carried unchanged".**
- **Reproduction:** `description: {summary: s, flag: &f true}` → validate 0.
  - The verbalization shows `canonical={"description":{"flag":1,"summary":"s"},...`.
  - `gnd diff --format json library M` gives `annotations: [{'after': {'flag': 1, 'summary': 's'}, ...}]`.
- **Cause:** the `typ="rt"` loader makes an anchored `true` a `ScalarBoolean`, which is an `int` subclass, so the schema's `number` type accepts it.
- **At B:** the same conversion happens inside untyped `provenance` (checked against `<S>/base/src`). Every typed boolean field at B refuses it.
- **Fix:** in the layer-1 walk, refuse ruamel `ScalarBoolean` under the description path (or normalise it to `bool` there).
- **Regression test:** `description: {summary: s, flag: &f true}` expects exit 3, or expects `flag` to load back as `True`.

**R3 — hardening. No declared depth bound on extras; refusal depends on Python's recursion limit and differs between commands.**
- **Validate:** `description_extra` refers to itself, so `jsonschema` recurses once per nesting level.
  - YAML nesting depth 242 → validate 0; diff, codegen, conformance, extract and verbalize all → 0.
  - Depth 243 or more → exit 3 with `ERROR: maximum recursion depth exceeded`. That is a caught `RecursionError`, not a declared rule.
- **Evolve:** a model that validates with an extra nested 40–240 deep cannot go through `evolve preview` as a modify operation. The proposal JSON hits `input_policy.MAX_DEPTH = 64` (`JSON depth exceeds cap`, exit 3). The same description written as a JSON model is refused at depth 64 or more, while YAML accepts it.
- **Reproduction:** `<S>/deep{N}.orm.yaml`, bisected in my run. Evolve: `<S>/evolve_probe.py`, depth-240 case.
- **Fix:** an explicit nesting cap for the description (for example 64, matching `MAX_DEPTH`) in the layer-1 walk, with a declared rule id.
- **Regression test:** a description at depth cap+1 expects exit 3 with that rule id; a description at the cap is accepted by validate and by evolve preview.

**R4 — completeness. The model-verbalization core-key order is not pinned (rule 5: one `DESCRIPTION_CORE_KEYS` order for all three renderers).**
- **Mutation:** `model_verbalization.py` `for key in reversed(DESCRIPTION_CORE_KEYS):`. The whole `test_object_type_description.py` still passes: `49 passed` (SURVIVED).
- **Why:** T3 puts the same text in all four keys and checks with `in`.
- **Regression test:** use distinct `summary`, `row`, `source` and `notes` values. Assert that the borrower sentence ends with `Description: '…'. Row: '…'. Source: '…'. Notes: '…'.` in that order.

**R5 — completeness. "summary only" in codegen docstrings is not pinned.**
- **Mutation:** `_summary_suffix` returns all core keys joined. The whole test file passes (SURVIVED).
- **Why:** T3 uses identical text for every key; T4 sets only `summary`; T5's line count stays the same because everything is appended on one line.
- **Regression test:** `{summary: "S-mark", row: "R-mark", source: "SRC-mark", notes: "N-mark"}`. Assert the docstrings contain `S-mark` and contain none of the other three marks.

**R6 — completeness. T8's "annotations survive applied redaction" check is vacuous.**
- **Mutation:** `redaction.py` nulls `before`/`after` of every annotation when the policy is active. T8 still passes (`4 passed`, SURVIVED).
- **Why:** `library.orm.yaml` declares no `redact`, so `policy.active` is False and the redaction branch never runs.
- **The behaviour itself is correct:** with `fact_types[0].redact: true` plus a description, `gnd diff --format json` keeps the annotation intact in both applied and `--unredacted` modes.
- **Regression test:** the same T8 cases on a copy with `fact_types[0]["redact"] = True`, asserting that the annotations equal the whole objects.

**R7 — completeness. Text-format `gnd diff`, the default format, does not show description annotations.**
- **Reproduction:** the reference-corpus release model `a` against `b`, where `b` adds `description: {summary: "One shipped release."}` to `release_release`. `gnd diff a b` prints exactly what `gnd diff a a` prints, apart from the second model digest. Nothing says a description changed.
- **Scope:** §5 only requires JSON, so this is a gap rather than a broken claim. Suggest one line per annotation (for example `ANNOTATION <object_type> added|modified|removed`), with a test.

**Minor notes (no reproduction needed):**
- `verbalization-patterns.md` says both forms escape the text "like every other model string". In the model verbalization, names are only passed through `line_text`; their quotes are not escaped.
- The `diff.reference.md` H1 still reads "(`gnd-diff/1`)".
- T7 row 4 hashes `.gnd-codegen.json`, which contains an unnormalised `gnd_version`. The test will fail on any version bump, unlike row 5.
- T13 cannot fail on its own: `_neutralize` now calls `neutralize_text`. A mutant that drops backslash escaping passes T13 and the 237 existing neutralizer-related tests; only T5 kills it.
- The runtime `__doc__` of generated tools turns `\n` back into a real newline, so a role line can be forged there; the source text is safe. This is pre-existing at B through a `reading` (reproduced). T5 checks source text only.
- The vocabulary's constraint-blindness is now structural only: a description can restate a constraint in prose, and the docs do not warn about this.

#### Confirmed (tried to refute, held)
- **C1, schema twins:** byte-identical (`cmp`), both mode `-rw-r--r--`. T2 and the IK1-D6 cases pass.
- **C1, extras:**
  - Refused with exit 3: unquoted timestamp or date (top-level and nested), `.nan`, `.inf` and `-.inf` (nested too), `1.0e400`, `!!binary`, a tagged scalar, a non-string key in an extra, and `row: null`.
  - Accepted: `!!omap` and a tagged mapping, both carried as plain objects (the tag is dropped).
- **C1, non-finite screen:** applies to description paths only. The test outside descriptions passes, and an unscoped mutant is caught by it.
- **In-memory models:** mutated `Model` objects with NaN, date, tuple, bytes or string descriptions are refused by `api.diff` (`DiffError diff:invalid-model`).
- **C2, renderers:** mutants for an extras-walking renderer, a capped vocabulary renderer and an unescaped docstring summary are all killed.
- **C2, `_neutralize` identity:** identical to B's `_neutralize` on 20,009 fuzzed inputs (all of U+0000–U+01FF plus separators, BOM, surrogates and astral characters; lengths 0–2000; non-string values).
- **C2, codegen:** a hostile summary (`'''`, `"""`, `\N{…}`, NUL, CR, VT, FF, U+001C, U+0085, U+2028, braces, trailing backslash) produces a `tools.py` that `ast.parse` accepts, and conformance → 0.
- **C2, projection:** `extract/projection.py` is unchanged.
- **C3, digest:** only one digest home exists (`anchors.py`); `extract.anchors` re-exports it. A digest-includes-description mutant is killed.
- **C3, diff versions:**
  - A description-only diff exits like an identical diff; always-v2 and ignore-extras mutants are killed.
  - The two diff schemas are equal modulo `$id`/title.
  - A reference-population diff with an annotation is v2 and its envelope validates against `report.schema.json` (0 errors).
- **C3, RF1 anchor:** `M-SEM-diff-schema` appears once in the source and is still killed (expected-red test fails).
- **C4:** I recomputed T7 rows 1–6 for `library` and `v2_worked_example` from the B sources; all equal `ik1-baseline.json`. HEAD also passes T7. No path renders an undescribed model differently.
- **C5:**
  - Evolve preview lists `object_types[work_item].description` on `annotation` (added) alongside the `object-type` entry, with `breaking: false`.
  - `BlastRadiusEntry` accepts it, and a model without descriptions lists no annotation entry.
  - The evolution contract and representation-format text match the code, apart from the notes above.
- **Coverage:** descriptions with extras on every object type of all four T7 fixtures (entity, subtype, derived subtype, value) → validate, diff, codegen, conformance and extract all 0. PyRel export (registrar, basics, ring) exit codes are unchanged; the description appears only inside the embedded `MODEL_TEXT`.
- **Test run:** `tests/test_object_type_description.py` and `tests/test_schema_sync.py`: 52 passed.

#### What I could not check
- `evolve apply`/`finalize` and a live linked-project conformance after a description change.
- Running exported PyRel programs that embed a description (needs DuckDB or Snowflake).
- A depth cap other than the default recursion limit, or behaviour under other Python builds; R3's threshold of 242 was measured on Python 3.14 here.
- The full test suite, which was out of scope. Unrelated and pre-existing: `gnd export pyrel --rules duckdb` on `tests/fixtures/pyrel-oracle/basics.orm.yaml` exits 70 with `export failed: 'id'`, with or without descriptions.
