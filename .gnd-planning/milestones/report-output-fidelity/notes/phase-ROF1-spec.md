# Phase ROF1: projected text for `check` and `validate` (issue 112)

## 1. Status

**Draft r1 (2026-11-07). Blocked on the plan gate** (the plan is proposed, not
approved) **and awaiting owner review.** Not implementable. The approval
instrument (a corpus, section 11) is not yet authored. `auto=false`.

## 2. Provenance

- Plan r1 §4 ROF1, completion predicate 1; design rules 1-5.
- Issue 112; rule-check-adoption RC1 open questions; FD2 of
  rule-check-followups ("the JSON-only text is a deliberate no-leak design;
  rendering verdict lines from the projected tree needs its own design and a
  leak review").
- Base: main `12daa5b7`.
- No review has run over these bytes. Nothing in this spec carries a review
  opinion.

## 3. Obligations (step 0 harvest)

| Source | Obligation | Discharged by |
|---|---|---|
| plan ROF1-C1 | verdict lines, no JSON, exits unchanged, four combinations | T1-T4 |
| plan ROF1-C2 | leak canary | T5 |
| plan ROF1-C3 | plain text byte-identical; one shared row renderer | T6, T7 |
| plan ROF1-C4 | changed goldens listed before code | section 11, M5 |
| plan rule 5 | render from the projected tree only | M1, T8 |
| plan D2 | temporal-only header | D2 here, T3 |
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

**M1. `src/gnd/output.py`, about 90 lines.**

```python
def render_check_rows(payload: Mapping[str, Any]) -> list[str]:
    """Lines of check text from a payload's rows. Total over any mapping."""

def _print_projected_text(payload: dict[str, Any]) -> None:
    """Header (if any), STEP summaries (unchanged), then render_check_rows(payload)."""
```

`render_check_rows` reads only `payload["verdicts"]`, `["derivations"]`,
`["counts"]`, `["coverage"]`, `["issues"]`, `["warnings"]`, `["error"]`,
and never imports or receives a `CheckReport`. Layout, in order:

1. warnings: `WARNING at {path}: {message} [{rule_id}]` (as `_cmd_check`
   prints them today for the plain route);
2. if `issues`: `ERROR at {path}: {message} [{rule_id}]` lines (capped), then
   stop (the plain route returns after issues; counts of an ill-formed run are
   zeros and carry no information);
3. `error` set and no issues: `ERROR: {error}` / `INTERNAL ERROR: {error}`
   by `exit_code` (the `_cmd_validate` rule);
4. `BLOCKING (alethic)` / `ADVISORY (deontic)` / `DERIVATIONS (alethic)` /
   `pass=… fail=… warning=… unchecked=… vacuous=…` / `COVERAGE` exactly as
   `_print_report` prints them.

For a route with a transition block the existing `STEP` summaries stay in
`_print_projected_text` (ROF2 owns the transition body).

**M2. `_print_report(report, declared)`** becomes an adapter: build the rows
from the `CheckReport` (`verdict.model_dump()` per row, `counts()`, coverage as
`{id: {declared, facts}}`) and call `render_check_rows`. The `declared`
(`--rule-ids`) lines are kept: the row dict gains optional `address`,
`remedy`, `novelty`, `rule_message` keys that only the plain route sets
(`--rule-ids` is refused on every projected route, so the projected rows never
carry them). Plain bytes unchanged (T6).

**M3. `src/gnd/commands/checking.py`.** Two call sites change from "print
header then JSON" to the renderer: `_cmd_check` and `_cmd_validate` (the
`--trace` block before it is kept). `_print_admission_text` and
`_print_lineage` follow unchanged for `--admission` (ROF2 verifies them).

**M4. `src/gnd/redaction.py` `render_text_header` (D2).** Returns `None` when
`declarations` is empty; `_print_projected_text` then prints no header (today
it raises `ValueError`; the guard becomes "payload lacks redaction metadata
entirely").

**M5. Goldens.** Section 11's list, regenerated from the reports.

Estimated: about 120 source lines (M1 90, M2 20, M3 6, M4 4), 250 test lines.

### Normative order and home

Layout: `render_check_rows` is the one home; `docs/reference/` text examples
cite it. The header grammar `REDACTION <mode>: <fact_type.role>, …`
stays in `render_text_header`.

## 7. Decisions

| D | Question | Readings and cost |
|---|---|---|
| D1 | Approval instrument | **corpus-first**: one model/population/expected-text triple per case (section 11). Alternative: prose-only, which cannot be re-read blind. Proposed: corpus **Open** |
| D2 | Header on the temporal-only route | (a) omit it: it describes no policy (proposal); changes the 4 `rf1-pins` goldens' first line as well as their body. (b) keep `REDACTION applied: ` (empty list): a line saying nothing, but one fewer byte-class to change. Differs in text only, not in exit code **Open** |
| D3 | Under `--unredacted`, the header says `unredacted`; the verdict lines are the projected `unredacted`-mode tree (the actual values). Print them? | yes: that is what `--unredacted` asks for and what the JSON route prints; the canary test T5b pins the values appear **only** in unredacted mode **Open** |
| D4 | Review over the spec bytes | none, per the pattern of rule-check-followups D3; the diff review covers the leak surface (plan §8) **Open** |

## 8. Tests

| T | File | Case | Expected |
|---|---|---|---|
| T1 | `tests/test_rof1_projected_text.py` | `src/gnd/examples/disclosure` model + population, `check --format text` | exit 1; stdout starts `REDACTION applied: has_email.email`, then `BLOCKING (alethic)` with one `[fail] fact_types[has_email].constraints[0]: [REDACTED INSTANCE DETAIL]` line; no line starts with `{` |
| T2 | same | same with `--unredacted` | exit 1; header `REDACTION unredacted: …`; verdict lines; the fact value appears (D3) |
| T3 | same | temporal model + valid population, `check --format text` | exit 0 or 1 as the report; no JSON line; header per D2 |
| T4 | same | disclosure model + `--rule-ids` | exit 3; an `ERROR at …` line ending `[check:rule-ids-unsupported]` (path read from the report); no JSON line |
| T5a | same | canary secret in a redacted role and a different canary in an unredacted role, `applied` | the redacted canary appears in no stdout line; the other appears wherever the plain route would print it |
| T5b | same | same, `--unredacted` | both canaries may appear |
| T6 | `tests/test_rof1_projected_text.py` + existing golden suites | every plain-route text golden | byte-identical |
| T7 | same | source assertion | `_print_report` calls `render_check_rows`; `render_check_rows` has no `CheckReport` parameter or import |
| T8 | same | source assertion | `_print_projected_text` and `render_check_rows` read only the payload (no `result.report` in the projected branches of `_cmd_check`/`_cmd_validate`) |
| T9 | same | hostile payloads: `verdicts: null`, missing keys, non-string messages, 1,000 issues | bounded output, no traceback |
| T10 | same | 50,000 verdict rows | under a ceiling measured on the dev machine and 6x margin recorded in the spec before it runs |
| T11 | existing JSON suites | `--format json` for the disclosure and temporal cases | byte-identical |
| T12 | `tests/test_rf1_helper_pins.py` et al. | the changed goldens (section 11) | equal the corpus's new text |

Every declared layout branch (warnings, issues, error, blocking, advisory,
derivations, counts, coverage; applied, unredacted, temporal-only, refusal) has
a case that fails it.

## 9. Out of scope for this phase

`transition`, `--admission`, and the export verification route (ROF2); any
change to what is redacted; `--format json`; `validate --trace` content;
issue 111.

## 10. Size

Estimate: about 120 source and 250 test lines, plus the corpus. Stop at 1.5x.

## 11. Approval instrument

A fixture corpus, authored first: `tests/fixtures/rof1-projected-text/`, entry
point `README.md` (cases and commands only), with the answer key in
`expected/` split out, so a later blind pass cannot see answers from the
entry point. Each answer is derived from the **report** (`--format json`) at
`12daa5b7` and the layout in section 6, not from an implementation.

Changed-bytes list (to be completed before the owner gate, rule 1): the four
`tests/fixtures/rf1-pins/goldens/sem-check/ex_{dispatch,release}_…json` stdout
bodies; `tests/fixtures/public-emitter21/answers.json` `exact_text_prefixes`
(the prefix `REDACTION applied: optional_code.code\n` is a prefix of the new
text too; confirm); any `tests/test_public_redaction_reports.py` expectation
that parses the JSON line out of stdout (to be enumerated by running the
suite against a mutant renderer, per rule 6).

## Verification ledger

| # | Obligation | Disposition | Command or evidence |
|---|---|---|---|
| V1 | merge-base record | run before any edit | focused files at `12daa5b7`; full suite sharded on beast-3 |
| V2 | focused gate | run | `uv run pytest -q tests/test_rof1_projected_text.py tests/test_rf1_helper_pins.py tests/test_public_emitter21_controls.py tests/test_public_redaction_reports.py tests/test_public_report_redaction_metadata.py --tb=short` (**unresolved until the corpus fixes the file list**) |
| V3 | lint | run | `uv run ruff check` on touched files |
| V4 | layers and homes | run | `tools/gnd_layers.json` import check; allowance count stays zero |
| V5 | full suite vs base | run on beast-3 | failure set equal to the base's |
| V6 | component index | run at record time | `python3 scripts/components_index.py changed --base 12daa5b7 --strict` |
