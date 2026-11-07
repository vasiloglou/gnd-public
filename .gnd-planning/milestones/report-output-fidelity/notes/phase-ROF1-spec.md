# Phase ROF1: projected text for `check` and `validate` (issue 112)

## 1. Status

**Draft r3 (2026-11-07). Awaiting owner review at the spec gate.** Plan r3 was
approved at the plan gate on 2026-11-07 ([record](../001-plan.md)). The
approval corpus (section 11) is authored and committed; it fails (20 cases
red) until the phase lands. Not implementable before the owner's approval of
the corpus and this spec. `auto=false`.

## 2. Provenance

- Plan r3 §4 ROF1, completion predicate 1; design rules 1-5. Plan r3 is the
  governing plan; r2 was the plan the Codex review read.
- Issue 112; rule-check-adoption RC1 open questions; FD2 of
  rule-check-followups ("the JSON-only text is a deliberate no-leak design;
  rendering verdict lines from the projected tree needs its own design and a
  leak review").
- Base: main `12daa5b7`.
- Codex reviewed r1 bytes of this spec (sha256 `f576b349…`, commit f5ad4290)
  together with plan r2: `block`, findings P5-P8 and P10 concern this spec
  ([plan-review-r2](../evidence/plan-review-r2/)). **This r2 is repaired
  bytes: it carries no review opinion of its own.** Marks: `(r1)` a repair
  applied for that review, `(r3)` a correction made while authoring the
  corpus (an observation refuted an expectation), `(o)` an owner decision.

## 3. Obligations (step 0 harvest)

| Source | Obligation | Discharged by |
|---|---|---|
| plan ROF1-C1 | verdict lines, no JSON, exits unchanged, four combinations | T1-T4 |
| plan ROF1-C2 | leak canary | T5 |
| plan ROF1-C3 | plain text byte-identical; one shared row renderer | T6, T7 |
| plan ROF1-C4 | changed goldens listed before code | section 11, M5 |
| plan rule 5 | render the verdict body from the projected tree only; state the boundary for `--trace`/`--document` (r1) | M1, section 6 boundary, T8, T13, T14 |
| plan D2 (ruled (o) 2026-11-07: omit the empty header) | temporal-only header | D2 here, T3 |
| `output.py:113` docstring | "render only the already-projected tree on declaration-bearing routes" | M1, T8 |
| issue 112 | with or without `--rule-ids` | T4 |
| AGENTS.md | `tools/gnd_layers.json` homes; model-query/family rules | V4 |
| components skill | `infra.text_output` | section 6 reuse table |

## 4. The standing rules, bound to this phase

| Rule | Binding |
|---|---|
| 1 Totality | `render_check_rows` consumes a payload that may be a failure envelope (exit 3/70): `verdicts` null or missing, `derivations: null`, `coverage: {}`. T9 feeds arbitrary mappings (missing keys, wrong types) and asserts a bounded text, not a traceback; the issues list is capped by `report_module.MAX_POPULATION_ISSUES` exactly as `_print_issues` is. |
| 2 Algorithm bound | the renderer is linear in verdict rows; T10 time-bounds it on a payload with 50,000 verdict rows. |
| 3 Validation order | text selection stays `exit decided → payload built → projected → rendered`; the order is untouched. No new refusal. Inapplicable beyond that. |
| 4 One walk | one row renderer for plain and projected check text (M2). `_print_report` becomes an adapter. T7 asserts by source that `_print_report` calls `render_check_rows`. |
| 5 One home | the layout of check text has one home, `render_check_rows`. The header has one home, `redaction.render_text_header`. |
| 6 Measure | the leak property is measured with a canary (T5), not argued. |
| plan 0.1 Frozen | JSON output is untouched (T11 pins `--format json` bytes). The plain-text bytes are untouched (T6). Only text that today is JSON changes (section 11 lists it). |
| Failure classes | *A rule made unfalsifiable by fixtures*: T5's canary sits in a role that is redacted **and** one that is not, so "redact everything" and "redact nothing" both fail. *Schema vs implementation spelling*: verdict values are read as the payload spells them (`pass|fail|warning|unchecked|vacuous`). |

## 5. Goal

`gnd check MODEL POP --format text` and `gnd validate MODEL --format text`
print the BLOCKING / ADVISORY / DERIVATIONS / count / COVERAGE layout, or the
`ERROR at …` issue lines, for a model with an active redaction policy or
temporal terms, in `applied` and `unredacted` mode, with and without
`--rule-ids`; exit codes are those of the same invocation today (0, 1, 2, 3,
4, 70 as the payload says); `--format json` bytes are unchanged; the plain
route's text bytes are unchanged; no line contains a value the projection
removed.

## 6. Design

**Reuse table** (searched 2026-11-07 at `12daa5b7`:
`components_index.py search "text report renderer verdict lines"`,
`"redaction projected payload"`, plus `git grep _print_projected_text`).

| Capability | Found | Decision |
|---|---|---|
| verdict-line formatting | `output._constraint_verdict_line`, `_identified_verdict_lines`, `_derivation_verdict_lines` (component `infra.text_output`) | **adapt**: they read attributes of verdict objects; they become readers of rows (mappings) |
| redaction header | `redaction.render_text_header` | **reuse** (one change: D2) |
| issue lines | `output._print_issues` | **reuse** |
| projected tree | `checking_service._project_result`, `redaction.project_output` | **reuse**, unchanged; the renderer is downstream of it |
| a generic payload-to-text renderer | none (`fidelity.report.render_fidelity` and `measure.report.render_measurement` are for other payloads) | **new** `render_check_rows` |

**M1. `src/gnd/output.py`, about 100 lines.** (r1: a new entry point; the
shared `_print_projected_text` is **not** changed in this phase.)

```python
def render_check_rows(payload: Mapping[str, Any]) -> list[str]:
    # Lines of check text from a payload's rows. Total over any mapping.

def _print_projected_check_text(payload: dict[str, Any]) -> None:
    # Header (if any), then render_check_rows(payload). check/validate only.
```

`_print_projected_text` stays exactly as it is for `transition`, `check
--admission`'s transition body and the export verification route (ROF2
owns them; Codex P5: they have PRE-STATE/STEP/FRAME/POST-STATE sections and an
extraction line a snapshot row renderer cannot reproduce).
`render_check_rows` reads only `payload["verdicts"]`, `["derivations"]`,
`["counts"]`, `["coverage"]`, `["issues"]`, `["warnings"]`, `["error"]` and
`["exit_code"]`, and never imports or receives a `CheckReport`. Layout:

1. warnings: `WARNING at {path}: {message} [{rule_id}]`;
2. if `issues`: `ERROR at {path}: {message} [{rule_id}]` lines (capped by
   `report_module.MAX_POPULATION_ISSUES`, with the elision line `_print_issues`
   prints) and stop;
3. `error` set and no issues: `ERROR: {error}` or `INTERNAL ERROR: {error}`
   when `exit_code` is 70 (the `_cmd_validate` rule);
4. **validate success** (command `validate`, exit 0, no verdict rows):
   `OK: {model} is a valid GND ORM model` (r1, Codex P6: a validate payload
   has empty verdicts/counts, so the check layout does not apply);
5. otherwise, check layout, as `_print_report` prints it: `BLOCKING
   (alethic)` / `ADVISORY (deontic)` / `DERIVATIONS (alethic)` / `pass=…
   fail=… warning=… unchecked=… vacuous=…` / `COVERAGE`.

**Boundary for routes that print from the model (r1, Codex P10).** The claim
"rendered from the projected tree only" covers the verdict body. Two
pre-existing paths print from other sources and are **unchanged and
explicitly outside it**: `validate --trace` prints the model's structure
(operations, derivations, frame modalities, from `_print_trace(result.model)`)
before the projected text, and `validate --document` can return early and
print `result.warnings` and newly built span issues without a projected
payload. Neither prints a population value; T13 and T14 pin that with
canaries rather than the source assertion T8, which covers only the
projected branches.

**M2. `_print_report(report, declared)`** becomes an adapter: build the rows
from the `CheckReport` (`verdict.model_dump()` per row, `counts()`, coverage as
`{id: {declared, facts}}`) and call `render_check_rows`. The `declared`
(`--rule-ids`) lines are kept: the row dict gains optional `address`,
`remedy`, `novelty`, `rule_message` keys that only the plain route sets
(`--rule-ids` is refused on every projected route, so the projected rows never
carry them). Plain bytes unchanged (T6).

**M3. `src/gnd/commands/checking.py`.** Two call sites change, `_cmd_check`
and `_cmd_validate`, from `_print_projected_text` to
`_print_projected_check_text` (the `--trace` block before the latter is kept).
`_cmd_transition` and the export verification service still call
`_print_projected_text`. `_print_admission_text` and `_print_lineage` follow
unchanged for `--admission`.

**M4. `src/gnd/redaction.py` `render_text_header` (D2, ruled).** Returns
`None` when `declarations` is empty; `_print_projected_check_text` then prints
no header. The old `_print_projected_text` is unchanged, so on the routes
ROF2 owns the empty-header behaviour is unchanged until ROF2 (a header
returning `None` there would otherwise raise its existing `ValueError`; ROF2
resolves it).

**M5. Goldens.** Section 11's list, regenerated from the reports.

Estimated: about 130 source lines (M1 100, M2 20, M3 6, M4 4), 300 test lines.

### Normative order and home

Layout: `render_check_rows` is the one home; `docs/reference/` text examples
cite it. The header grammar `REDACTION <mode>: <fact_type.role>, …`
stays in `render_text_header`.

## 7. Decisions

| D | Question | Readings and cost |
|---|---|---|
| D1 | Approval instrument | **corpus-first**: one model/population/expected-text triple per case (section 11). Alternative: prose-only, which cannot be re-read blind. Proposed: corpus **Open** |
| D2 | Header on the temporal-only route | **Ruled (o, 2026-11-07), at plan level: omit the empty header** ("Approve as proposed", answering "How do you rule on RF-D0 and D1–D6 in the plan?"). Changes the 4 `rf1-pins` goldens' first line as well as their body; no exit-code difference. (r1, Codex P8: the spec's row carries the plan's ruling.) |
| D3 | Under `--unredacted`, the header says `unredacted`; the verdict lines are the projected `unredacted`-mode tree (the actual values). Print them? | yes: that is what `--unredacted` asks for and what the JSON route prints; the canary test T5b pins the values appear **only** in unredacted mode **Open** |
| D4 | Review over the spec bytes | none, per the pattern of rule-check-followups D3; the diff review covers the leak surface (plan §8) **Open** |

## 8. Tests

Expected exits are the exit of the same invocation's `--format json` run at
`12daa5b7`; the numbers below are the band the corpus answer key pins, read
from the report, not from an implementation.

| T | File | Case | Expected |
|---|---|---|---|
| T1 | `tests/test_rof1_projected_text.py` | `src/gnd/examples/disclosure`, `check --format text` | exit 1; first line `REDACTION applied: has_email.email`; `BLOCKING (alethic)` with one `[fail] fact_types[has_email].constraints[0]: [REDACTED INSTANCE DETAIL]` line; `ADVISORY (deontic)` shows `(none)`; no line starts with `{` |
| T2 | same | same, `--unredacted` | exit 1; header `REDACTION unredacted: has_email.email`; verdict lines; the fact value appears in the lines the unprojected route would print it (D3) |
| T3 | same | temporal model + valid population (corpus), `check --format text` | exit 0 (all pass); no header (D2); `BLOCKING (alethic)`/`(none)`, `pass=N fail=0 …`, `COVERAGE` |
| T3b | same | temporal model + population violating a deontic constraint (corpus `temporal-advisory`) | **exit 0** (r3: r2 said 2; the report's own exit for a deontic shortfall is 0, "accepted"); `ADVISORY (deontic)` lists one `[warning]` line |
| T3c | same | temporal model + population whose derivation is unchecked (corpus `temporal-derivation`) | exit 4; `DERIVATIONS (alethic)` lists the `[unchecked]` rows; `unchecked=5` (r3: this corpus's derivations carry no finding lines; a `[finding]` line has no corpus case and is covered by T9-style payload rows) |
| T4 | same | disclosure model, `check --rule-ids` | exit 3; one `ERROR at …` line ending `[check:rule-ids-unsupported]` (path read from the report); no JSON line; no `BLOCKING` header |
| T4b | same | disclosure model with a population that fails load (type mismatch) | exit 3; `ERROR at …` lines; no verdict sections |
| T4c | same | **payload level** (r3): a hand-built check payload with one `warnings` row and passing verdicts | the `WARNING at …` line precedes `BLOCKING`. No fixture model here produces a model warning, so the corpus cannot carry this branch |
| T5a | same | a canary secret in a redacted role and a different canary in an unredacted role, `applied` | exit 1; the redacted canary appears in no stdout line; the other appears where the plain route would print it |
| T5b | same | same population, `--unredacted` | exit 1; **both** canaries appear (D3) |
| T6 | same + existing golden suites | every plain-route check/validate text golden | byte-identical; exit as before |
| T7 | same | source assertion | `_print_report` calls `render_check_rows`; `render_check_rows` has no `CheckReport` parameter or import |
| T8 | same | source assertion | the projected branches of `_cmd_check` and `_cmd_validate` call only `_print_projected_check_text`, which reads only the payload |
| T9 | same | hostile payloads: `verdicts: null`, missing keys, non-string messages, 1,000 issues | bounded output, no traceback; the issue elision line appears |
| T10 | same | 50,000 verdict rows | under a ceiling measured on the dev machine with a 6x margin, recorded in the spec before it runs |
| T11 | existing JSON suites | `--format json` for the disclosure and temporal cases | byte-identical; exits as before |
| T12 | `tests/test_rf1_helper_pins.py` et al. | the changed goldens (section 11) | equal the corpus's new text |
| T13 | same | `validate --trace` on a redaction-bearing model with a canary in a population | exit 0; trace block present; canary absent (the trace never sees a population); `OK:` line last |
| T14 | same | `validate --document` with a span-hash failure on a redaction-bearing model | exit 3; `ERROR` lines from the early return; canary absent |
| T15 | same | `validate --format text`, redaction-bearing model, valid | exit 0; `OK: … is a valid GND ORM model`; no JSON line |
| T16 | same | `validate --format text`, a redaction-bearing model that does not load (corpus `validate-invalid`) | exit 3; the plain `ERROR at …` line, unchanged (r3: a model that fails to load has no policy, so the projected route is unreachable; this is a control that must keep passing) |
| T17 | same | `transition` and export verification, redaction-bearing | unchanged from today (still JSON text); pins that ROF1 did not touch ROF2's routes |

Every declared layout branch (warnings, issues, error, validate success,
blocking, advisory, derivations, counts, coverage; applied, unredacted,
temporal-only, refusal) has a case that fails it: T4c warnings, T4/T4b
issues, T1 blocking, T3b advisory, T3c derivations, T3 counts and coverage,
T15 validate success, T9 error-only envelope.

## 9. Out of scope for this phase

`transition`, `check --admission`'s transition body, and the export
verification route (ROF2: their PRE-STATE/STEP/FRAME/POST-STATE sections and
extraction line); any change to what is redacted; `--format json`;
`validate --trace` content and `validate --document` behaviour (boundary only,
section 6); issue 111.

## 10. Size

Estimate: about 130 source and 300 test lines, plus the corpus. Stop at 1.5x.

## 11. Approval instrument

A fixture corpus, authored first and committed (r3): `tests/fixtures/rof1-projected-text/`,
entry point `README.md` (stories and commands only), answer key split out in
`expected/` (with `README.md` saying how it was derived), runner
`tests/test_rof1_projected_text.py`. Each answer is derived from the **report**
(`--format json`) at `12daa5b7`, rendered with the plain route's own renderer
over the report's rows (`expected/derive_answers.py`), not from an
implementation.

Twelve cases: `redacted-fail`, `redacted-fail-unredacted`, `redacted-pass`,
`redacted-rule-ids`, `redacted-ill-formed`, `temporal-pass`,
`temporal-advisory`, `temporal-derivation`, `validate-redacted`,
`validate-redacted-unredacted`, and the controls `validate-temporal` and
`validate-invalid`. They map to T1-T5, T3-T3c, T4/T4b, T15, T16.

State at commit: 37 corpus tests, **20 red** (10 answer-key cases and 10
no-JSON-line cases, for the ten projected-route text cases), 17 green (the 12
JSON-bytes pins, the two controls, the applied-mode canary, the unredacted
canary, the corpus-lists-itself check). The canaries pass today because the
JSON text holds the redaction; they are regression guards for the phase.

Changed-bytes list (rule 1; still to be completed before implementation):
the four `tests/fixtures/rf1-pins/goldens/sem-check/ex_{dispatch,release}_…json`
stdout bodies; `tests/fixtures/public-emitter21/answers.json`
`exact_text_prefixes` (confirm the prefix `REDACTION applied: optional_code.code\n`
still prefixes the new text); any `tests/test_public_redaction_reports.py`
expectation that parses the JSON line out of stdout (to be enumerated by
running the suite against a mutant renderer, per rule 6). The corpus's own
fixtures are new and move no recorded byte.

## Verification ledger

| # | Obligation | Disposition | Command or evidence |
|---|---|---|---|
| V1 | merge-base record | run before any edit | focused files at `12daa5b7`; full suite sharded on beast-3 |
| V2 | focused gate | run | `uv run pytest -q tests/test_rof1_projected_text.py tests/test_rf1_helper_pins.py tests/test_public_emitter21_controls.py tests/test_public_redaction_reports.py tests/test_public_report_redaction_metadata.py --tb=short` (**unresolved until the corpus fixes the file list**) |
| V3 | lint | run | `uv run ruff check` on touched files |
| V4 | layers and homes | run | `tools/gnd_layers.json` import check; allowance count stays zero |
| V5 | full suite vs base | run on beast-3 | failure set equal to the base's |
| V6 | component index | run at record time | `python3 scripts/components_index.py changed --base 12daa5b7 --strict` |
