# Phase ROF2: projected text for transition, admission and verify (issue 112)

## 1. Status

**Draft r1. Awaiting owner review at the spec gate.** No implementation file
has been created or edited. `auto=false`.

## 2. Provenance

- Plan r3 (approved 2026-11-07, [plan-gate record](../001-plan.md)) §4 ROF2,
  completion predicate 1, design rules 1-6, §9 ROF2 row.
- ROF1 record ([002-phase-ROF1.md](../002-phase-ROF1.md)) and spec
  ([phase-ROF1-spec.md](phase-ROF1-spec.md)): the shared row renderer
  `render_check_rows`, `_projected_check_lines`, `_issue_lines`, `_text`,
  `_rows`, `_row_views`; ROF1-O1 **ruled 2026-11-07: keep the
  `[reason: …]` suffix** on projected rows.
- Base: branch `claude/plan-report-output-fidelity-6d5b5d` at `e1fb6a18`
  (ROF1 plus main `1e63aeb5`, FU2 merged). PR 124 is not merged yet; if it
  merges first, the base becomes main at that merge and nothing below moves.
- No review has read these bytes. Marks: `(o)` an owner decision.

## 3. Obligations (step 0 harvest)

| Source | Obligation | Discharged by |
|---|---|---|
| plan ROF2-C1 | `transition` (full and plan), `check --admission`, export verification print their plain layout for projected payloads, including PRE-STATE, STEP, FRAME, POST-STATE and the extraction line; the existing `STEP` derived-change summary kept, not duplicated | M1-M4; T1-T9 |
| plan ROF2-C2 | the ROF1 canary extended to those routes | T10 |
| plan ROF2-C3 | `validate --trace` on a redaction-bearing model keeps its trace block | already true after ROF1 (`_cmd_validate` prints `_print_trace` before `_print_projected_check_text`); ROF1's T13 (`test_t13_validate_trace_*`) re-runs in the gate (V2) |
| plan completion predicate 1 | with and without `--unredacted`; rendered from the projected tree only | T1-T9 both modes; T12 source assertions |
| plan §9 ROF2 row | new ROF2 tests + `test_public_transition_walks.py`, `test_public_transition_trace.py`, `test_public_emitter_trust_controls.py` and the export verification CLI tests | V2 |
| plan rule 1 (frozen) | `--format json` bytes and plain-route text bytes unchanged | T13, T14 |
| plan rule 4 (one walk) | plain and projected transition text share one renderer | M1 (`_print_transition` becomes an adapter), T12 |
| plan rule 5 (no leak) | render from the projected tree, never the unprojected objects | T10, T12 |
| plan §6 "ROF1 changes routes owned by ROF2" | ROF1 left `_print_projected_text` in place for these routes; ROF2 retires that JSON-as-text body | M5, D2 |
| ROF1 I3 | `render_text_header` unchanged; header omission for a payload with no declarations lives in the printer | M4 (same rule on every projected route) |
| ROF1-O1 ruling (o) | keep the reason suffix | D3 extends it to transition verdict lines |
| ROF1 tests `test_t17_transition_keeps_the_shared_projected_text`, `test_t17_other_projected_routes_still_use_the_shared_json_text`, `test_p1_admission_keeps_the_shared_projected_text_until_its_own_phase`, and the admission line of `test_t8_projected_branches_read_only_the_payload` | pinned that ROF1 did not touch ROF2's routes; they now describe the old behaviour | replaced by named successors (T15); the replacement is listed in section 11 |
| plan §6 risks | leak through a new path; plain bytes move; changed routes outside scope | T10, T13, T12 |
| AGENTS.md | `tools/gnd_layers.json` homes; RF5 relocated-body pins; RF6 dynamic-query successors; component index | V4, V6, section 11 |

## 4. The standing rules, bound to this phase

| Rule | Binding |
|---|---|
| 1 Totality | the transition renderer consumes a payload that may be a refusal envelope: `transition.evaluated: false` with every walk field null (observed, see section 6); `steps: null`; a step that is not a mapping. T11 feeds arbitrary mappings and asserts bounded text, no traceback. The COMPUTED POST line is a `json.dumps` of the projected value; a value that does not serialize prints `<non-text>`. |
| 2 Algorithm bound | linear in rows (snapshot verdicts + steps + step verdicts + frame rows); T16 time-bounds a payload with 10,000 steps × 5 verdict rows, ceiling recorded before it runs. |
| 3 Validation order | `exit decided → payload built → projected → rendered`, unchanged. No new refusal. |
| 4 One walk | one transition renderer for plain and projected (M1); `_print_transition` becomes an adapter, as `_print_report` did in ROF1. Snapshot verdict lines inside a walk go through `_row_views` and `_constraint_verdict_line`, the one line format. |
| 5 One home | transition layout: `render_transition_rows`. Check layout: `render_check_rows` (ROF1). Header: `redaction.render_text_header`. Extraction line: one helper used by plain and projected verify (M3). |
| 6 Measure | the leak property is measured by canaries per route (T10), the bytes that change by a census (section 11), not argued. |
| plan 0.1 Frozen | JSON untouched (T13); plain text untouched (T14, existing goldens). |
| Failure classes | *A rule made unfalsifiable by fixtures*: T10 places one canary in a redacted role and one in an unredacted role on each route, so "redact everything" and "redact nothing" both fail. *Schema vs implementation spelling*: transition verdict rows are read as the payload spells them (`locator`, `verdict`, `message`, `reason_code`; `frame_grading` rows `fact_type`, `modality`, `reason`, `operations`; `post` is `declared` or `computed`). |

## 5. Goal

For a model with an active redaction policy (all three routes) or temporal
terms (transition only; see section 6 for why), `gnd check MODEL --pre PRE
--steps STEPS [--post POST] --format text`, `gnd check MODEL POP --admission
--format text` and `gnd verify MODEL POP --format text` print the layout the
plain route prints, in `applied` and `unredacted` mode, read from the
projected payload only. No line is the JSON report. Exit codes are those of
the same invocation today. `--format json` bytes are unchanged. Plain-route
text bytes are unchanged. No line contains a value the projection removed.

## 6. Design

**Probes (2026-11-07, at `e1fb6a18`, read-only, scratch copies only).**

| Route | Today | Plain layout it should match |
|---|---|---|
| transition, plan (no `--post`), redaction model (`tests/fixtures/v61-phase4/models/role-declaration.orm.yaml`, `transition-pre.yaml`, `steps/binding-only.json`) | `REDACTION applied: optional_code.code` then one JSON line (schema 9) | `PRE-STATE` / `STEP 1 (set_optional_code)` / `COMPUTED POST` + one JSON line of the computed post / `FRAME COMPARISON: not applicable -- post is computed` / `POST-STATE` (observed on a twin with `redact: true` removed and the steps digest re-pinned) |
| transition, full (`--post`) | header + JSON | `PRE-STATE` / `STEP 1 (…)` / `FRAME` / `  optional_code: deontic (deontic-toucher; set_optional_code)` / `  [warning] $.post.facts.optional_code: <message>` / `POST-STATE` |
| transition refusal (steps digest mismatch) | header + JSON; payload `transition.evaluated: false`, every walk field null, one `issues` row | `ERROR at $.model_digest: … [transition:model-digest-mismatch]` |
| transition, temporal (`src/gnd/examples/plan_apps/lease`, its shipped `plans/*.steps.json`) | `REDACTION applied: ` (empty list) then JSON; exit 3 (those files are agent plans, not `steps.json`) | issue lines. A valid temporal walk is feasible: one `schedule_payment` step over the shipped `state.pop.json`, digests from `transition_model_identity` and `operations_digest`, prints `REDACTION applied: ` + JSON (schema 11) and exits 1 (violated); the corpus builds its own copy (section 11) |
| `check --admission`, redaction model | header + JSON (v10) + `ADMITTED`/`BLOCKED` lines | warnings, check layout, then the same `ADMITTED`/`BLOCKED` lines |
| `check --admission`, temporal model | **plain text already**: the admission kind is not in `_project_result`'s temporal set `{check, transition, plan}` | unchanged; not a ROF2 route |
| `verify --no-extraction`, redaction model | header + JSON | warnings, `EXTRACTION: state=skipped (extraction opted out (--no-extraction))`, check layout |
| `verify`, temporal model | **plain text already**: verify is projected only for an active redaction policy | unchanged; not a ROF2 route |
| `verify`, sidecar missing, redaction model | plain `ERROR at …` line: the model is not loaded yet at that refusal, so nothing is projected | unchanged |

What the projected transition block carries (redaction applied): every
snapshot verdict `message` is `[REDACTED INSTANCE DETAIL]` and redacted
`offending_facts`/bindings/computed-post cells are `{"redacted": true, "roles":
[…]}` markers; a frame verdict's message is also replaced. The new text prints
only fields the JSON-as-text prints today, so it can show nothing that today's
output does not already show; it shows less (no digests, no bindings).

**Reuse table** (searched 2026-11-07: `components_index.py search
"transition text walk sections"`, `"verify extraction line report text"`, plus
`git grep _print_projected_text`).

| Capability | Found | Decision |
|---|---|---|
| walk layout | `output._print_transition` (component `infra.text_output`) reads `TransitionReport` objects | **adapt**: becomes an adapter over a new row renderer |
| snapshot verdict line | `_constraint_verdict_line`, `_row_views`, `_with_reason` (ROF1) | **reuse** |
| derived-change summary | `_print_derived_change_summaries` (already reads dicts or objects) | **adapt**: a line-returning twin, the printer calls it |
| preamble (warnings, issues, error) | `_projected_check_lines` (ROF1) | **adapt**: its preamble is split out as `_projected_preamble` and shared |
| admission lines | `_print_admission_text` (reads the payload already) | **reuse**, unchanged |
| extraction line | inline in `verification_service._cmd_verify` | **new** one-line helper `extraction_line(extraction)`, used by both routes |
| header | `redaction.render_text_header` | **reuse**, unchanged; the empty-declarations rule stays in the printer (ROF1 I3) |

**M1. `src/gnd/output.py`, transition renderer, about 70 lines.**

```python
def render_transition_rows(
    block: Mapping[str, Any], *, post: str | None, show_reason: bool = False
) -> list[str]:
    # The walk layout from a payload's ``transition`` block. Total over any mapping.

def _print_transition(walk, warnings, *, computed_post=None) -> None:
    # Adapter: warnings, then render_transition_rows(<walk as rows>, ...). Plain bytes unchanged.
```

Layout, exactly the plain one (`output.py:433-471` at the base):

1. `PRE-STATE`; non-pass rows of `pre_snapshot.verdicts` as
   `  snapshot [<verdict>] <ref>: <message>`; `pre_snapshot_verdicts` as
   `  [<verdict>] <locator>: <message>`;
2. per step: `STEP <index> (<operation>)`; `DERIVED <fact_type>: +<n> -<m>` per
   `derived_changes` row; step `verdicts`; non-pass `intermediate.verdicts` as
   `  intermediate [<verdict>] …`;
3. if `post == "computed"`: `COMPUTED POST`, one `json.dumps(computed_post,
   allow_nan=False)` line, `FRAME COMPARISON: not applicable -- post is
   computed`; else `FRAME`, one `  <fact_type>: <modality> (<reason>;
   <operations>)` line per `frame_grading` row, then `frame_verdicts`;
4. `POST-STATE`; non-pass `post_snapshot.verdicts` as `  snapshot [...]`.

On a projected route each verdict line takes the ROF1 reason suffix (D3).
The derived-change summary is printed once, inside its step; the
pre-ROF2 printer's separate STEP block disappears with the JSON line (C1: "kept,
not duplicated").

**M2. Projected transition text.** `_projected_transition_lines(payload)`:
the shared preamble (warnings; issues → issue lines and stop; error →
`ERROR:`/`INTERNAL ERROR:` and stop), then, if `transition` is a mapping
with `evaluated` true, `render_transition_rows(block, post=payload["post"],
show_reason=True)`. Otherwise nothing more (the plain route prints only the
warnings and issues in that case: `commands/checking.py:230-237`).

**M3. Projected verify text.** `_projected_verify_lines(payload)`: the shared
preamble, then `extraction_line(payload["extraction"])`, then
`render_check_rows(payload, show_reason=True)`. `extraction_line` is the one
home of `EXTRACTION: state=<state>[ (<reason>)]`; the plain verify route
calls it in place of its inline f-string (bytes unchanged).

**M4. Printers and call sites.** One printer per route, each printing the
header only when `redaction.declarations` is non-empty (ROF1's rule, now on
every route, so a temporal-only walk prints no empty `REDACTION applied: `):
`_print_projected_transition_text(payload)`,
`_print_projected_verify_text(payload)`; `check --admission` calls ROF1's
`_print_projected_check_text` and then `_print_admission_text`, unchanged.
Call sites: `commands/checking.py` `_cmd_transition` (line 219) and
`_cmd_check` (line 291), `export/verification_service.py` (line 220).

**M5. `_print_projected_text`** (`gnd.cli` historical binding, re-exported
from `commands/_output.py`). After M4 no command calls it. D2 decides its body:
proposed, it becomes a dispatcher over the three projected renderers (verify
when `command == "verify"`, transition when the payload's `transition` is a
mapping, else check/validate), so the historical name no longer prints
JSON-as-text. Its `ValueError` for a payload without redaction metadata is
kept.

**Boundary.** As in ROF1: `validate --trace` prints from the model (ROF1 T13
pins it); `validate --document`'s early return prints without a projected
payload (ROF1 T14). `verify`'s refusals before the model loads print plain
issue lines and are not projected (probe above); unchanged. Temporal
`--admission` and temporal `verify` are not projected and stay as they are.

Estimated: about 130 source lines (M1 70, M2 15, M3 20, M4 15, M5 10) and
260 test lines, plus the corpus.

### Normative order and home

Walk layout: `render_transition_rows`. Check layout: `render_check_rows`.
Extraction line: `extraction_line`. Header: `render_text_header`. The order of
a projected text is fixed as header → warnings → (issues | error | body) →
route trailer (`ADMITTED`/`BLOCKED`, `lineage`), the plain order.

## 7. Decisions

| D | Question | Readings and cost |
|---|---|---|
| D1 | Approval instrument | **corpus-first**, as ROF1: one model/population/steps/expected-text set per case, answers split out and derived from the base renderer over the report's rows (section 11). Alternative: prose-only. Proposed: corpus. **Open** |
| D2 | Fate of `_print_projected_text` once no command calls it | (a) **dispatcher** (proposed): the historical binding renders the new text, so no caller can get JSON-as-text through it; its RF5 body pin moves (one successor row). (b) leave it unchanged, unused, until shim retirement (RF-D5): no pin moves, but a dead function keeps printing the old layout. No exit-code difference. **Open** |
| D3 | Reason suffix on transition and frame verdict lines | yes (proposed): the ROF1-O1 ruling applied on every projected route, so a redacted walk keeps its cause (`reason_code`) visible; plain bytes unchanged (the suffix is projected-only). No: the transition lines would show `[REDACTED INSTANCE DETAIL]` with no cause. **Open** |
| D4 | The COMPUTED POST line is one JSON line | keep (proposed): it is the plain layout's own line (`json.dumps(computed_post)`), printed from the projected computed post, so its redacted cells are markers. Alternative: render facts as lines, which changes the plain route's bytes too (rule 1). **Open** |
| D5 | Review over the spec bytes | none (proposed), as ROF1 D4; the diff review covers the leak surface (plan §8). **Open** |

## 8. Tests

`tests/test_rof2_projected_text.py` unless named. Expected exits are those of
the same invocation's `--format json` run at the base.

| T | Case | Expected |
|---|---|---|
| T1 | transition plan (computed post), redaction model, `applied` | exit 0; header `REDACTION applied: …`; `PRE-STATE`, `STEP 1 (…)`, `COMPUTED POST`, one JSON line whose redacted cells are markers, `FRAME COMPARISON: not applicable -- post is computed`, `POST-STATE`; no line is the report |
| T2 | same, `--unredacted` | exit 0; header `REDACTION unredacted: …`; the computed-post line carries the bound value |
| T3 | transition full (`--post`), frame delta | exit 0; `FRAME` grading line; one `[warning] $.post.facts.<ft>: [REDACTED INSTANCE DETAIL]` line (applied) |
| T4 | transition with a failing step or intermediate verdict | the band of the report; the step's verdict line and `  intermediate [fail] …` line, message redacted, reason suffix when the row has a code |
| T5 | transition refusal (digest mismatch) | exit 3; one `ERROR at $.model_digest: … [transition:model-digest-mismatch]` line; no `PRE-STATE` |
| T6 | transition on a temporal model (no declarations) with a valid walk | the report's band; no header line; walk layout |
| T6b | a walk whose step has `derived_changes` | the `DERIVED <ft>: +n -m` line appears once, under its `STEP` |
| T7 | `check --admission`, redaction model, `applied` and `unredacted` | exit as today (1 for the failing corpus population); header, check layout, then `ADMITTED`/`BLOCKED` lines exactly as today |
| T8 | `verify --no-extraction`, redaction model, `applied` and `unredacted` | exit 1; header; `EXTRACTION: state=skipped (extraction opted out (--no-extraction))`; check layout |
| T9 | `verify` refusal on a redaction model after the model loads (ill-formed population) | exit 3; issue lines; no `EXTRACTION` line (the plain route prints none there) |
| T10 | canaries: one secret in a redacted role, one public value in an unredacted role, on T1, T3, T7, T8 | applied: the secret in no stdout line, the public value where the plain route prints it; unredacted: both present |
| T11 | hostile payloads: `transition` not a mapping, `steps: null`, a step that is a string, `frame_grading` rows missing keys, a computed post that does not serialize, 1,000 issues | bounded text, no traceback, issue elision line |
| T12 | source assertions | `_print_transition` calls `render_transition_rows`; the projected branches of `_cmd_transition`, `_cmd_check` (admission) and verify call only the projected printers; no projected renderer takes a `TransitionReport`/`CheckReport` |
| T13 | `--format json` for T1-T9 | bytes equal the base's |
| T14 | plain-route text goldens (rf1 pins, `test_public_transition_walks.py`, `test_public_transition_trace.py`) | byte-identical |
| T15 | successors of ROF1's `test_t17_transition_keeps_the_shared_projected_text`, `test_t17_other_projected_routes_still_use_the_shared_json_text`, `test_p1_admission_keeps_the_shared_projected_text_until_its_own_phase` and the admission assertion of `test_t8_projected_branches_read_only_the_payload` | each rewritten to pin the ROF2 behaviour; the old pins are removed in the same commit and named in the record |
| T16 | 10,000 steps × 5 verdict rows | under a ceiling measured before the run (6x the slowest of three runs) |
| T17 | D2 (a): `_print_projected_text` on each route's payload | prints the same lines as the route printer |

Every declared branch has a case that can fail it: pre-state rows (T4),
step verdicts and intermediate (T4), derived changes (T6b), computed post
(T1), declared post / frame grading / frame verdicts (T3), post-state (T4),
refusal (T5), temporal no-header (T6), admission trailer (T7), extraction line
(T8), verify refusal (T9), totality (T11).

## 9. Out of scope for this phase

What is redacted; `--format json`; temporal `--admission` and temporal
`verify`, which are not projected and already print plain text; verify's
refusals before the model loads; `validate` (ROF1); issue 111.

## 10. Size

Estimate: about 130 source and 260 test lines, plus the corpus. Stop at 1.5x
(about 195 source lines).

## 11. Approval instrument

Proposed (D1): a corpus `tests/fixtures/rof2-projected-text/`, entry point
`README.md` (stories and commands only), answers split out in `expected/`
derived from the base renderer (`_print_transition` and `_print_report` over
the report's rows, with the reason suffix rule applied as ROF1 did), runner
`tests/test_rof2_projected_text.py`, red first. Planned cases:
`transition-plan`, `transition-plan-unredacted`, `transition-full`,
`transition-step-fail`, `transition-refused`, `transition-temporal`,
`transition-derived`, `admission`, `admission-unredacted`, `verify`,
`verify-unredacted`, `verify-refused`.

**Changed-bytes census (rule 6), measured before code** (evidence: [evidence/ROF2-census/](../evidence/ROF2-census/)). Method: a scratch
copy of `src/gnd` whose `_print_projected_text` prints a sentinel and exits
99, against an unmodified copy, over the 122 test files that mention
redaction or temporal terms plus the §9 files (`-p no:cacheprovider`,
default selection). Result (2026-11-07, head `e1fb6a18`): base 3492 passed,
0 failed; probe 9 failed, 3483 passed; 0 base-only failures. The nine, and
what each means for ROF2:

| Test | Why it reached the printer | After ROF2 |
|---|---|---|
| `test_carried_defects.py::test_check_refuses_a_fifo_by_name_instead_of_hanging[--pre]`, `[--post]` | asserts the JSON substring `"error": {"type": "PopulationLoadError", "message": "[REDACTED INSTANCE DETAIL]"}` in **text** stdout | **expectation moves**: the text becomes `ERROR: [REDACTED INSTANCE DETAIL]` (exit 3 unchanged). One assertion, two parameters; listed as a changed pin |
| same, `[--steps]` | asserts the issue message and the FIFO path appear | holds: both are in the `issues` row, printed as an `ERROR at` line |
| `test_rof1_projected_text.py::test_t17_transition_keeps_the_shared_projected_text`, `::test_p1_admission_keeps_the_shared_projected_text_until_its_own_phase` | ROF1's own "not yet" pins | replaced (T15) |
| `test_v61_phase4_review_regressions.py::test_malformed_parent_binding_container_is_redacted` | text run asserts exit 3 and canary absent | holds (exit and absence unchanged) |
| `test_v62_phase2_report.py::test_q05_text_summary_is_deterministic_and_value_free` | asserts the `DERIVED …` lines and no canary in them | holds: the lines are printed once, inside their `STEP` |
| `test_v62_phase6_redaction.py::test_exists_where_taint_does_not_leak` (answer E18) | transition text: exit 4, secrets absent, public values present in JSON+text | holds |
| `test_v63_phase2_cache.py::test_unavailable_projection_after_positive_coverage` | **not a text pin**: it fails whenever the bytes of `src/gnd/output.py` differ from the checkout's (rerun alone: red against the probe copy, green against the unmodified copy); the assurance level it reads depends on the source bytes | rerun in the gate (V2) on the implemented bytes |

Not caught by this method (stated limit): source-text assertions that do not
execute the printer (`test_t17_other_projected_routes_still_use_the_shared_json_text`
and the admission line of `test_t8_projected_branches_read_only_the_payload`,
both named in T15), and tests outside the 122 files that reach the printer
without mentioning redaction or temporal terms (the V5 full suite catches those).

## Verification ledger

| # | Obligation | Disposition | Command or evidence |
|---|---|---|---|
| V1 | base record | run before any edit | the census base run (above) |
| V2 | focused gate | run | `.venv/bin/python -m pytest -q tests/test_rof2_projected_text.py tests/test_rof1_projected_text.py tests/test_public_transition_walks.py tests/test_public_transition_trace.py tests/test_public_emitter_trust_controls.py tests/test_public_redaction_reports.py tests/test_v62_phase6_redaction.py tests/test_carried_defects.py tests/test_v61_phase4_review_regressions.py tests/test_v62_phase2_report.py tests/test_v63_phase2_cache.py`, plus the RF5/RF6/RF1 guard suites |
| V3 | lint | run | `ruff check` on touched files |
| V4 | layers and homes | run | `tools/gnd_layers.json` import check; allowance count zero |
| V5 | full default suite vs base | run (sharded) | failure set ⊆ the base's |
| V6 | component index | at record time | `scripts/components_index.py changed --base <base> --strict` |
