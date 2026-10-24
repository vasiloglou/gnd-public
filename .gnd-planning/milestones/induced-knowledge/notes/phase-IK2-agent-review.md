# IK2 adversarial review

**One reviewer is one reviewer.** One local general-purpose agent reviewed
`git diff ef39b1a a35d8fe`, the IK2 implementation on top of the approved
corpus. It wrote only to a session scratch directory. It is not a panel, and
nothing here carries panel weight.

Every finding below was reproduced by the author before anything was fixed.
Each fix has a regression test that failed on `a35d8fe` and passes after the
fix.

## Disposition

| ID | Class | Reproduced by author | Disposition | Regression test |
|---|---|---|---|---|
| R1 | blocking | yes: `support {10.0, 1.0}` with 10 examples loads `OK` | **fixed:** `_rule_induced_provenance` refuses non-`int` counts | `test_r1_float_support_counts_are_refused` (2 cases), red before the fix |
| R2 | hardening | yes: an `llm-inferred` provenance with `induction: {conf: .nan}` is refused at HEAD and valid at B | **fixed:** the screen applies only under `source: induced` constraints, as IK2-D3 rules | `test_r2_induction_key_under_another_source_validates_as_at_base`, red before the fix |
| R3 | hardening | yes: a confirmation that moves P to another fact type is admitted by the gate | **fixed:** claimable predecessors are keyed by host fact type (top level = `None`). This tightens the spec §6 sentence "matching is location-insensitive" for the status-change path only; exact matching is unchanged. See finding F6 | `test_r3_confirmation_cannot_move_the_rule` (2 cases), red before the fix; `test_r3_confirmation_in_place_is_still_admitted` |
| R4 | hardening | not separately reproduced; the reviewer's reproduction is recorded | **deferred:** open question IK2-Q1. `rejected_proposals` is schema-light; checking archived induced proposals changes that contract for models valid at B | none |
| R5 | completeness | 8 surviving mutants rerun | **fixed:** tests added. Each kills its mutant (8 of 8), and the unmutated control copy passes them all (8 passed) | `test_r5_*` (8 tests) |
| R5 (schema) | completeness | yes: `induced: []` validated | **fixed:** `minItems: 1` on `induced` | `test_r5_coverage_schema_refuses_an_empty_induced_list`, red before the fix |
| R6 | completeness (docs) | not needed | **recorded:** spec §5 over-states `..` refusal. The grammar refuses `..` *segments* (`../x`, `a/../b`), not every `..` (`a..b`). The approved grammar stands; finding F7 | none |
| spec note | doc | yes: §6 has a stale IK2-D4 sentence | **recorded:** finding F5; the code follows the D4 ruling | none |

## Reviewer report (verbatim)

The reviewer's final message, unedited except that its headings are demoted one
level.

### IK2 adversarial review: `git diff ef39b1a a35d8fe`

**1. Verdict:** Not ready to certify. One blocking defect: float support counts skip the support-arithmetic check, which breaks C1. There are also three hardening defects and several declared branches that no test can fail. The gate's main paths, refusal order, CLI mapping, coverage versioning and v3/v4 byte identity all held under attack.

I wrote nothing under the repo. All scratch files are in `/private/tmp/claude-501/-Users-nikolaosvasiloglou-github-repos-gnd-public--claude-worktrees-recent-commits-95fa1c/16650214-feb5-484f-a716-975b7f732cdd/scratchpad/ik2-review/` (called `$S` below): the extracted B tree in `$S/base`, the mutants in `$S/mut/<name>`, the probe scripts `$S/p1.py`–`$S/p7.py`, `$S/gate.py`, `$S/preview.py` and the mutant runner `$S/mutate.sh`. `tests/test_induced_provenance.py` passes at HEAD (141 tests).

### 2. Findings

**R1 — blocking — breaks C1 (the "support arithmetic is inconsistent → exit 3" item in spec §5).**
- **Cause:** JSON Schema 2020-12 treats `10.0` as an `integer`, so the schema accepts float support counts. `_rule_induced_provenance` (`src/gnd/model/_induction.py`) then runs `if not (type(numerator) is int and type(denominator) is int): continue`. That line silently skips all three count checks.
- **Reproduction:** `uv run python $S/p1.py $S $S/models` builds a model with an L01 constraint where `support: {numerator: 10.0, denominator: 1.0}` and `examples` holds 10 ids.
  - `uv run gnd validate $S/models/float_support.json` prints `OK: … is a valid GND ORM model`, exit 0.
  - Through preview (`$S/p6.py`) the same constraint gives `(0, '')`. The integer control `10/1` gives `(3, '…support numerator 10 exceeds denominator 1')`.
  - `gnd coverage` emits `schema_version 5` with `support {'numerator': 10.0, 'denominator': 1.0}`, prints `support=10.0/1.0` in the text view, and validates against `coverage.schema.json`.
  - This also contradicts the "`support` | integers" row in `provenance-and-modality.md`.
- **Fix:** in `_rule_induced_provenance`, emit a `semantic:induced-provenance` issue when either count is not an exact `int` (`type(x) is not int`), instead of `continue`. Alternatively, screen floats at the induction `support` paths in layer 1.
- **Regression test:** loader cases `numerator: 10.0, denominator: 1.0` and `numerator: 2.0, denominator: 3` must exit 3 with `[semantic:induced-provenance]`. Both exit 0 today.

**R2 — hardening — contradicts IK2-D3 ("`gnd validate` is unchanged … any existing model stays valid") and IK-R3.**
- **Cause:** the new path in `_JSON_FORM_SCREENED_PATHS` matches `provenance.induction` under any source, not just `induced`.
- **Reproduction (`$S/p2.py`):** an `llm-inferred`/proposed/deontic constraint with `provenance: {rationale_world_fact: …, induction: {conf: .nan}}`.
  - HEAD: `ERROR at $.fact_types[0].constraints[1].provenance.induction.conf: nan is a non-finite number … [jsonschema:type]`, exit 3.
  - B (`PYTHONPATH=$S/base/src`): `OK … valid`, exit 0.
  - Control `{conf: 0.5}` exits 0 at both.
- **Fix:** apply the screen only when the owning constraint has `source: induced`. Or keep the stricter screen and record an owner amendment to D3.
- **Regression test:** the B-valid `llm-inferred` model above must still exit 0.

**R3 — hardening — breaks the intent of C2 / IK-R1 (confirmation "differing only in status, modality, reviewed_in").**
- **Cause:** the reviewed status change matches location-insensitively, so one proposal can confirm a proposed induced rule and move it onto a different fact type, or to top level. The rule that comes out confirmed and alethic was never induced on that fact type. The spec's "location-insensitive" sentence permits this, but it defeats the review.
- **Reproduction (`$S/gate.py`, `$S/preview.py`):**
  - Gate, P in `work_item_has_title` → C in a second fact type `work_item_has_alt_title` with the same role name: `G1 … ADMITTED`.
  - Gate, P → top-level `constraints`: `G2 … ADMITTED`.
  - Full `EvolutionService.preview`, modifying both fact types: `G1 preview confirm+move (0, '')`.
- **Fix:** key `claimable` by `(host fact-type id or None, canonical strip)`, and look the candidate up with its own location.
- **Regression test:** proposed P in FT1 and confirmed C in FT2 must give R-I3 at the gate and preview exit 3.

**R4 — hardening — IK-R11 ("`provenance.induction` … never carry host filesystem paths or raw population values").**
- **Cause:** `rejected_proposals` is schema-light, so an archived `source: induced` proposal can persist a host path, a raw value and float support. Nothing checks it: not the loader, not D-12, not coverage.
- **Reproduction (`$S/p5.py`):** `examples: ["/home/alice/secret.csv", "Jane Doe"]` in a rejected induced proposal. `gnd validate` prints `OK`. Coverage stays at v3 with no `induced` key.
- **Fix:** when an archived proposal has `source: induced`, apply `$defs/induction` to its `provenance.induction` (or a semantic rule that does the same).
- **Regression test:** the model above must exit 3.

**R5 — completeness — declared branches no test can fail.** Each mutant below leaves `tests/test_induced_provenance.py` at "141 passed". For each one I confirmed separately that the real product behaves correctly:
- **Whitespace check, `_induction_strings`:**
  - Dropping `inducer.name`/`version` (`M_inducer_ws`), `method` (`M_method_ws`) or `counterexamples` (`M_cex_ws`) is not caught.
  - The product correctly refuses `"gnd-discover\n"` as inducer name or method, and `"case-1\n"` as a counterexample, all with `semantic:induced-provenance`.
  - Without the rule the schema `$` lets them through (S1).
  - Add loader cases for a trailing newline in name, version, method and counterexample, plus a raw counterexample `Jane Doe`.
- **Gate `claimable` filter, `item.get("status") == "proposed"`** (`M_confirmed_reclaim`): not caught. With the filter, re-confirming an already-confirmed induced rule under a new `reviewed_in` gives R-I3 (`$S/p3.py`). Without it, that path is admitted. Add an admission case: confirmed K with `r1` → K with `r2` → R-I3.
- **Layer-1 screen on top-level constraints** (`M_screen_ft_only`, regex forced to `fact_types[..]` only): not caught. The product refuses `$.constraints[0].provenance.induction.confidence.value: nan`; the mutant prints `OK` (`$S/p4.py`). Add a top-level `.nan` case.
- **Coverage row fields:** hard-coding `"status": "proposed"` (`M_cov_status`) or always using the positional address (`M_cov_positional`) is not caught. T11 has only one proposed/deontic, id-less, fact-type row. Running `$S/p7.py` correctly gives `constraint:ik_title confirmed alethic` and `constraints[0] proposed deontic`. Add a multi-row expected list: confirmed/alethic with an id, plus a top-level row.
- **`_VerifierVerdictV1` literal:** removing `"induced"` (`M_v1_literal`) is not caught. T12 checks only `VerifierVerdict`'s annotation string. The mutant raises `ValidationError` on `_VerifierVerdictV1(source="induced", …)`, so a schema-v1 session over an induced model fails. Add a test that builds the V1 verdict.
- **Coverage schema accepts `induced: []`:** a v5 payload with an empty list gives 0 schema errors, though the product never emits it (IK2-D8). Add `minItems: 1`, and a schema test that refuses an empty list.

**R6 — completeness (docs) — spec §5 says an example, counterexample or evidence ref containing `..` exits 3.** The approved §6 grammars accept `a..b` as an example id and `a..b/c..` as an evidence ref: `$S/models/dotdot.json` validates. The traversal cases `../x` and `a/../b` are refused, so this is a §5 over-statement rather than a hole. Either reword §5 to "a `..` segment", or tighten the grammar by amendment.

### 3. Confirmed (tried to refute; held)
- **Gate behaviour:**
  - Two candidates claiming one predecessor are refused. So is a kept predecessor next to a confirmed copy.
  - An id change during confirmation is refused (G3).
  - Blank `reviewed_in` values (`"  "`, `\xa0`, `　`) are refused.
  - Hostile `provenance` (None, list, string, int, `{induction: None}`, non-string `reviewed_in`) and hostile `status` (None, list, dict) raise only `EvolutionError`. The non-dict constraint and fact-type crashes (G8, G9) are identical at B, and preview validates the candidate before the gate anyway.
  - The audit check still precedes R-I1, and the in-order refusal is kept.
  - The mutants for decrement removal, `claimable` from all of `before`, the R-I1 branch, the `strip` and string guards on `reviewed_in`, and modality stripping are all caught.
- **Gate call sites and CLI mapping:**
  - `_enforce_d12` runs unchanged at preview, apply and finalize (`service.py` lines 1217, 1522, 1835).
  - Removing either new marker from `cli_service.py` is caught by T4/T6.
- **Coverage:**
  - For 7 fixture models plus one model carrying `induction` under `llm-inferred`, JSON and text output at HEAD equal B byte for byte, apart from `gnd_version`.
  - The v6 and renderer evidence-line mutants are caught.
  - `test_schema_sync`, the four coverage test files, `test_object_type_description`, `test_skill_prose_sync` and `test_rf6_packages` pass.
- **Schema:** the twin schemas are byte-identical. The only places constraints can live are fact-type constraints and top-level `constraints`, and the screen regex covers both. `source: induced` appears in only the four `source_kind` sites; operation, precondition and dynamic rule refuse it.
- **Other consumers:** the `rai_import` D-03 rows are correct (T13 catches a revert). The modality-policy message bytes are unchanged.
- **Spec note:** §6's sentence "Under IK2-D4 = keep-deontic, modality is not stripped" contradicts the approved ruling D4 = yes. The code follows the ruling and strips `modality`.

### 4. Could not check
- `​` and `﻿` as `reviewed_in` pass both the gate and validate, because Python `.strip()` does not treat them as whitespace. This matches `imported`'s existing rule, and they are not Unicode whitespace, so it meets the spec as worded. I did not count it as a defect.
- I did not drive real apply and finalize runs with an induced proposal. I only confirmed the gate is called there.
- I did not run the RF6b body-pin, census or layering suites beyond `test_rf6_packages`, nor the exp-session or report-schema impact suites.
- I did not check whether real learner output fits the induction block (the residual the spec carries to IK5).
- The worktree has uncommitted edits to `evidence/IK2/build_dynamic_successor.py` and `update_source_successors.py` that are outside the reviewed diff. I did not review them.
