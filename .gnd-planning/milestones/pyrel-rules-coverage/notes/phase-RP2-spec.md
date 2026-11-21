# Phase RP2 — anchored constraints listed as not checked · spec

## 1. Status

owner-decided (2026-11-21) by **delegated approval (auto=true)**: see §7 and
§12. Base commit `92cd5c9b`.

## 2. Provenance

Derived from plan r4 (sha256 `9a93f4c2…9434`, approved in
`001-plan-gate.md`), §2 RP2, §4 RP2-C1…C8, §9 row RP2, §10 D1 and D5. The
plan's review rounds ran over r2 and r3; this spec has had no review. All
citations read at `92cd5c9b` (code equal to `8c909013`).

## 3. Obligations

| Source | Obligation | Discharged in |
|---|---|---|
| RP2-C1 | flat, `resolution/`, both interop models pass the anchored step; the quantity fixture's anchored constraint passes (it still stops on RP4's value refusal) | T1, T2 |
| RP2-C2 | every anchored id is in `UNCHECKED` and in no requirement | T3 |
| RP2-C3 | (oracle) the twelve gold populations of the flat model agree with GND, exit 4 | T9 |
| RP2-C4 | DuckDB textual line byte-identical | T4, T10 |
| RP2-C5 | rules success line counts listed rules; checker success line unchanged | T5, T6 |
| RP2-C6 | comparator learns not-checked; negative control fails it | T9, T11 |
| RP2-C7 | (oracle) LQP report function prints the lines and returns D5's exit; `--compile` prints them | T12, T13 |
| RP2-C8 | (oracle) anchored over an empty fact list: not checked, exit 4, agrees | T14 |
| §2 RP2 deontic | a deontic not-checked rule keeps the band | T15 |
| §0 Ossie unchanged | `anchored` is not in Ossie's `_SUPPORTED` (`ossie_formulas.py:40-42`), so `place` returns before lowering; lane runs the Ossie tests | lane |
| §0 Default export unchanged | lane runs `test_pyrel_export*.py` | lane |
| §5 docs | runtime page and `rules-as-pyrel.md` say anchored rules are listed as not checked | T7 |
| §10 open question | a bare top-level `anchored` validates? | measured: no, `gnd validate` exit 3 (`oneOf`); the top-level branch keeps its generic refusal, unreachable by a valid model |

## 4. Standing rules

1. **Totality.** The new branch reads `c["id"]` and `c["modality"]`, which
   `constraint_requirements` already requires of every constraint; it adds
   no new input read. The LQP report function reads only `UNCHECKED`, a
   constant the program itself embeds. Argued inapplicable beyond that.
2. **Cap bounds the algorithm.** The branch is O(1) per constraint. Inapplicable.
3. **Validation order.** The anchored branch sits in the fact-scoped family
   walk; model-wide refusals still run first. A model with an anchored
   constraint and a later refused construct still refuses on the latter
   (T8 pins it with the quantity fixture's value refusal).
4. **One walk.** Handled inside `constraint_requirements`; the one report
   loop over `UNCHECKED` prints both kinds (no second loop).
5. **One home.** The not-checked reason text has one home: the `reason`
   field written at lowering time; both programs print it from there.
   `docs/runtimes/pyrel.md` yields its list.
6. **Measurement.** Every GND exit in T9–T15 was measured (plan §1).

## 5. Goal

`gnd export pyrel MODEL --rules duckdb|lqp` exits 0 for the flat model,
`resolution/`, and both interop models. On the twelve gold populations the
DuckDB program exits 4 and its finding set, now including not-checked
rules, equals `gnd check`'s.

## 6. Design

### `src/gnd/export/pyrel_rules.py` (~40 lines)

- `_Model.unchecked` rows become `{"id", "modality", "reason"}` plus
  `"expression"` for textual rows. Textual: `reason = f"textual rule:
  {expression}"`. Anchored:

      reason = "source anchor: gnd check decides it with --anchors and --document; the rules programs read no sidecar"

- `constraint_requirements`, fact-scoped branch: `if family == "anchored":
  model.unchecked.append({...}); return []`, before the generic refusal.
- DuckDB `state_lines`: `print(f"{rule['id']}  not checked  ({rule['reason']})")`.
  For textual rows this prints the same bytes as `8c909013`.
- New program function, both targets:

      def not_checked():
          """Print each rule listed as not checked; True when a must-rule is among them."""

  The DuckDB `state_lines` keeps its own loop (it collects lines rather
  than printing); the LQP program calls `not_checked()`.
- `_LQP_MAIN`: `lqp_report(problems)` prints the not-checked lines, then the
  violation lines and count, and returns `1 if problems else 4 if
  must_unchecked else 0` (D5). `main` returns `lqp_report(problems)`.
  `compile_only` calls `not_checked()` before compiling.
- `render_report(model_path, target) -> tuple[str, list[str]]`: the program
  and the listed ids. `render` returns `render_report(...)[0]`.

### `src/gnd/commands/export.py` and `export/emit.py`

`_cmd_export_pyrel_rules` uses a new `emit.render_pyrel_rules_report`.
When the list is non-empty, it appends `; N rule(s) are not checked
(listed in the program)` to its success line; with none, the line is the
`8c909013` bytes. `_cmd_export_pyrel` (the checker) is untouched.

### Tests support

`tests/test_pyrel_rules.py`: `_findings` maps `rule  not checked  (...)` to
`(rule, 'not checked', 'null')`; `_gnd` maps an `unchecked` verdict to the
same tuple, before the offending-facts loop.

### Docs

`docs/runtimes/pyrel.md:156`: "Textual rules and anchored rules are listed
as not checked, as GND lists them without a sidecar." One sentence says
`gnd check --anchors --document` decides anchored rules. Line 79-80 example
output unchanged (its model has none). `docs/explanation/rules-as-pyrel.md`:
the judgement bullet adds anchored rules.

## 7. Decisions

| ID | Question | Ruling (delegated, 2026-11-21) |
|---|---|---|
| RP2-D1 | Success line with zero listed rules | keep the `8c909013` bytes; the count appears only when non-zero, so the docs' example output stays true |
| RP2-D2 | The anchored reason text | as in §6; it names the route that does decide it |
| RP2-D3 | Approval instrument | prose plus GND as oracle (§11) |

## 8. Tests

New `tests/test_rp2_anchored.py`, fixtures in `tests/fixtures/pyrel-rules-coverage/rp2/`.

| # | Case | Lane | Expected |
|---|---|---|---|
| T1 | render flat, `resolution/`, interop extraction and checking, both targets | default | no exception |
| T2 | quantity fixture refuses with `time_step#1: family 'value'`, not anchored | default | `ExportInputError` |
| T3 | flat model: `UNCHECKED` ids equal the four anchored ids; no `RULES` row has them | default | equal |
| T4 | `textual.orm.json`: DuckDB program contains `not checked  ({rule['reason']})` and the textual reason string `textual rule: <expr>` | default | pass |
| T5 | CLI export of the flat model prints `; 4 rule(s) are not checked` | default | exit 0 |
| T6 | CLI export of bookrec prints the `8c909013` line exactly; the checker export line unchanged | default | exit 0 |
| T7 | runtime page mentions anchored rules and `--anchors` | default | pass |
| T8 | order: the quantity fixture refuses on value after passing anchored | default | as T2 |
| T9 | (oracle) twelve gold populations agree with GND through the extended comparator | oracle | exit 4 both |
| T10 | (oracle) `textual` review case still agrees (existing `REVIEW_CASES`) | oracle | unchanged |
| T11 | (oracle) negative control: the program with one anchored id dropped from `UNCHECKED` does not agree | oracle | comparison fails |
| T12 | (oracle) LQP program, `lqp_report([])` on the flat model: prints four not-checked lines, returns 4 | oracle | 4 |
| T13 | (oracle) LQP `--compile` on the flat model prints the not-checked lines | oracle | exit 0 |
| T14 | (oracle) quantity-shaped model without the value rules (`rp2/anchored-only.orm.json`), empty `time_step` | oracle | exit 4 both |
| T15 | (oracle) `rp2/anchored-deontic.orm.json`: deontic anchored rule only | oracle | GND's exit, both equal (measured at test time and pinned) |

Verification ledger: plan §9 row RP2 (focused, oracle), the guard block,
`uv run ruff check`. Broad lanes not selected.

## 9. Out of scope

External uniqueness (RP1), `Number` (RP3), role-scoped value (RP4); reading
an anchor sidecar in a program.

## 10. Size

Estimate ~60 source lines, ~180 test lines, 2 fixtures.

## 11. Approval instrument

Prose; the answer key for every oracle case is `gnd check` itself, with
the measured exits written literally in the tests.

## 12. Gate

Delegated approval (auto=true), 2026-11-21, under the owner's
`/process-milestone pyrel-rules-coverage auto`; instrument: this prose;
budget: one Codex review round over the diff. Spec bytes: the SHA-256 is
recorded in the phase record (this line would move it).
