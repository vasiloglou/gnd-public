# Include-root routes · plan r4

**Status: r4, 2026-11-21. Plan review ran twice: round 1 over r2 (r3 applied
its 13 fixes, tagged `(p1)`), round 2 over r3 (r4 applies its 4 fixes, tagged
`(p2)`). r4 carries no review opinion of its own; the round budget is spent
(§8).** The owner selected the GND review
panel light (`tools/run_gnd_review_panel.py --light`) for the plan review and
the milestone close in this session on 2026-11-21. The panel read r2 (sha256
`4079c650ad046dcec1087c7cb95b58a71f471743ec511ff670a7426d3027c39b`, commit
`185ccaca`): six of six seats succeeded at high effort; evidence and the
disposition are in `evidence/plan-review-r1/`. Repairs are tagged `(p1)` at
their site. Round 2 read r3 (sha256
`bf150b5b7e40eb92230b5103b012bbb2533e2ce11f0e7b95b3e00b2e832ea45a`, commit
`c1d7219b`): three of six seats succeeded; evidence in
`evidence/plan-review-r2/`. Approval is recorded only in `001-plan-gate.md`. `auto=true`
delegation for this milestone was given on 2026-11-21 (`process-milestone
include-root-routes auto`).

This plan covers [#217](https://github.com/vasiloglou/gnd-public/issues/217)
and item 1 of [#214](https://github.com/vasiloglou/gnd-public/issues/214).
Items 2–4 of #214 belong to
[pyrel-rules-coverage](../../pyrel-rules-coverage/README.md).

**Provenance.** Outline r1 is the previous bytes of this file
(sha256 `c8d81f4b8b4a53e3b2010356fd7032867ac99e3b57fef02b082415f2f887f4a0`,
commit `0cf94434`, merged in PR 219 as `260c4337`). Its phase IDs IR1–IR3 and
decisions D1–D3 are kept. Its reviews, `.gnd-planning/reviews/pr-219-r2/` and
`pr-219-panel/`, read the roadmap outline, not these bytes. Sentences new in
r2 carry no review opinion. r3 repairs, tagged `(p1)`, carry none either.
Every code citation was re-read at `260c4337` on
2026-11-21; `src/` is unchanged since `0f39c392`, where the outline cited it.

## Goal and completion predicates

A version-5 root with includes reaches the routes that refuse it in 0.4.0,
through one recorded composition or flattening, never a silent fallback. Every
combination that stays unsupported refuses with a message naming it.

- **IR1.** `gnd judgments check` accepts an include root, temporal or not, and
  judges the same composed model `gnd check` evaluates. Receipts bind the root
  by its sha256, and the root's pins bind every include (decision D4): every
  include declaration must carry a 64-hex `sha256` or it is refused
  `include:declaration` (`model/_includes.py:61-77`) `(p1)`.
- **IR2.** Any include root, temporal or not, can be written out as a
  `*.flat.orm.json` plus its `gnd-flattening/1` record by `gnd flatten`, a
  command separate from `gnd extract` (D1).
- **IR3.** `gnd export pyrel`, in the default mode and with `--rules lqp` or
  `--rules duckdb`, accepts an include root by exporting its flattened model.
  The program records the flattening record's sha256 and every include's
  sha256 (D5), so an include changed and pinned again in the root gives a
  different recorded digest. An include changed without a new pin already
  refuses at load (`include:hash-mismatch`, `model/_includes.py:217-218`).

The milestone is closed when each phase has its record and the close record
cites green focused gates for IR1–IR3, the structure and inventory guards and
`uv run ruff check`, the replies drafted for #217 and #214, and the panel-light
close review.

## 0. Binding design rules

- **R0.1 Projections are recorded.** Each flattening has a record bound to the
  bytes it consumed: `root_sha256`, each include's pin and the
  `flat_model_sha256` (`model/flattening.py:46-54`, as shipped by LX1).
- **R0.2 Includes stay as they are.** Standalone-valid includes, no nesting,
  confined paths. This milestone opens routes; it does not relax a rule of
  `model/_includes.py:compose`. Nested includes keep
  `include:forbidden-section`.
- **R0.3 One composition.** Every new route composes through the loader that
  `gnd check` uses (`model/__init__.py:_load_model_at`, `compose`) or through
  `flatten_model` over its result. No route parses includes itself.
- **R0.4 Same judgement, either route.** A non-temporal root judged directly
  (IR1) and judged through its flat model must give the same verdicts. A test
  pins it.
- **R0.5 The export modes differ on temporal models, and stay different.** The
  default mode refuses them (`export/emit.py:35-36`). The `--rules` route
  (`render_pyrel_rules`, `emit.py:60-64`) has no temporal refusal: it lowers
  `date_add` / `date_sub` (`pyrel_rules.py:357`, `:409`, `:1654-1668`). Every
  criterion says which mode it means.
- **R0.6 A model without includes is untouched.** Every changed route gives
  byte-identical output for a model that declares no includes. `(p2)` "Declares
  includes" means `declares_includes()` (`model/_includes.py:56-58`): an
  `includes` key or a `fact_type_constraints` key. A version-5 document with
  `fact_type_constraints` and no `includes` takes the composed route and is
  refused `include:declaration` there, where 0.4.0 refused
  `include:unsupported-route` on the routes this milestone opens; each phase
  pins that change. The existing
  tests of each route are the control; for `gnd extract` that includes the
  temporal-refusal goldens in `tests/fixtures/rf1-pins/goldens/sem-extract/`
  (run by `tests/test_rf1_semantic_pins.py`) `(p1)`.

The project's six standing rules (`.codex/skills/process-phase/references/project.md`)
bind every phase; each spec discharges them by name.

## 1. Scope, sources and authority

Harvested obligations. "Observed" means re-read or run on 2026-11-21 at
`260c4337`; "inherited" means claimed by a source and not re-measured.

| # | Source | Obligation | Kind | Phase |
|---|---|---|---|---|
| H1 | #217 "Problem" | `judgments.py:470-471` calls `guard_bytes(..., route="judgments")`; `api.py:1156-1162` refuses first (`guard_path` at `:1157`, `guard_bytes` at `:1162`) and loads with `load_model_bytes` (`:1163`), without includes | observed | IR1 |
| H2 | #217 "Problem" | `require_non_temporal(model, "extract")` at `extract/service.py:191` (and `extract/projection.py:319`) | observed | IR2 |
| H3 | #217 "Request" | either route; the reporter measured that a non-temporal root with reference populations judges through the flat model | inherited | IR1, IR2 |
| H4 | #214 row 5, "What would unblock it" item 1 | `pyrel_rules.py:2415` `guard_bytes(..., route='pyrel_rules:2267')`; default export refuses `include:unsupported-route: export.pyrel` (`emit.py:27-31`) | observed (exit 3 on both fixture roots, all three modes) | IR3 |
| H5 | literature-interop LX1–LX2, closed | `gnd-flattening/1`, `model/flattening.py`, `witness/flattening.py` as shipped | observed | IR2, IR3 |
| H6 | probe, 2026-11-21 | the judgments include refusal writes `error.reason: "include:unsupported-route"` (`api.py:1195-1198`, corrected `(p1)`), outside the closed enum of `judgment.schema.json` `$defs.report.error.reason` (`shape binding trust limit unsupported io`) | observed | IR1 |
| H7 | probe, 2026-11-21 | flattened fixture roots (probe-local names `(p2)`; `gnd flatten` writes `extraction.orm.flat.orm.json` and `checking.orm.flat.orm.json`): `extraction.flat.orm.json` exports in the default mode, exit 0; `checking.flat.orm.json` refuses there with the temporal message, exit 3; under `--rules lqp` and `--rules duckdb` both stop at `paper_names_parent_method#0: family 'anchored'`, exit 3 | observed | IR3 |
| H8 | `tests/test_mc1_guards.py` | `test_R4_judgments`, `test_R5_judgments_api`, `test_direct_refusals[R13-pyrel-rules]`, `test_cli_guards[pyrel]` pin today's refusals; `test_R10_session_judgments` and `test_R21_composition_verify` pin refusals that stay | observed | IR1, IR3 |
| H9 | `tests/test_mc1_review_regressions.py` | `test_R7_guard_precedes_temporal_classification` pins that the include guard runs before temporal classification in the default export | observed | IR3 |
| H10 | PROJECT.md roadmap after 0.4.0 | first milestone; RP5's include-root cases need IR3 merged; two milestones never write the same files at once | inherited | all |
| H11 | `src/gnd/examples/literature/assertion_admission.py:142-165` (path corrected `(p1)`) | copies the model bytes alone into a temporary folder before `judgments check`; an include root would then fail its include read | observed by reading | IR1 (boundary only) |

Out of scope: temporal models in the default PyRel export (`emit.py:36`;
D3), detecting a stale exported program, the `gnd exp` session judgments
(`exp/session_judgments.py:84`), the assertion-admission example (H11; it
belongs to literature-host-interfaces LH3), and #214 items 2–4.

### Issue requests and the phases that discharge them

| Request | Phase |
|---|---|
| #217: `judgments check` judges an include root directly | IR1 |
| #217: a flattening route that accepts temporal models | IR2 |
| #214 item 1: export an include root through its flattened model, or document flattening as the route | IR3 |

This is a framework milestone. An experiment-claim census (`gnd coverage`)
counts claims over a domain model; it says nothing about which CLI routes
accept an include root, so none is read here. The baseline is the probe table
H4–H7.

## 2. Contract proposal and product behavior

### IR1 — `gnd judgments check` on an include root

- `api.judgments` drops `guard_path` and `guard_bytes`. **Only a root that
  declares includes** takes the composed route `(p1)`: its includes are
  composed under the model's directory with the loader `gnd check` uses
  (`_load_model_at` under `retained_root`, R0.3), without binding references
  there. References are then bound exactly as today, by
  `bind_declared_references(model, root=reference_root or model_path.parent)`,
  so `--reference-root` keeps its meaning for include roots. A model without
  includes keeps `load_model_bytes` and today's bytes (R0.6).
- `evaluate_judgments` keeps its include guard for every caller that names no
  root, and skips it when the new keyword `model_root` is given `(p1)`. Its
  raw-subject check (`judgments.py:506-515`) re-derives the model from
  `model_bytes`; for a root that declares includes and a given `model_root`
  it composes the same way. A direct caller without `model_root` keeps
  `include:unsupported-route` (`test_R4_judgments`), so it is never judged
  against a partial model. The `gnd exp` session route calls it without a
  root and keeps its own guard.
- Two digests, by design `(p1)`: the stale-subject check compares each
  receipt's `subject.model_sha256` with the sha256 of the root file's bytes
  (`judgments.py:569`), unchanged. The mechanical report's `model_digest` is
  the composed identity `gnd check` reports, which differs from the root's
  bytes for an include root; for a model without includes it is today's
  value, because that branch does not change. Because composition refuses an
  include whose bytes differ from its pin, the root digest binds every
  include (D4).
- Include refusals map to `error.reason: "binding"` with the include code as
  the message (D6), fixing H6. Outcome stays 3.

### IR2 — `gnd flatten`

- `gnd flatten MODEL --out DIR` loads `MODEL` with `load_model`, calls
  `flatten_model`, and writes `<stem>.flat.orm.json` and
  `<stem>.flattening.json` into `DIR` with the names `gnd extract` uses
  (`extract/service.py:_flattening_names`; the stem strips one suffix, so
  `checking.orm.json` gives `checking.orm.flat.orm.json` `(p2)`). It makes no
  temporal check.
- `(p2)` The flat model keeps the root's `reference_populations` paths,
  relative to the authored root's directory (representation-format.md,
  "Extraction flattening record"). A flat model written elsewhere binds its
  references only where those relative paths resolve. The IR2 spec decides
  whether `gnd flatten` refuses a `DIR` other than the root's directory for a
  model that declares references.
- Exit 0 when both files are written; exit 3 for an invalid model, a model
  without includes, or any include refusal (with its include code); exit 11
  when either output file already exists, with nothing written `(p1)`.
  Output is published once, both files or neither.
- Registered as a top-level command in `src/gnd/cli.py`, where each command
  group's `add_parsers` is called (`cli.py:650-676`), with its module listed
  in `tools/gnd_entrypoints.json` and `tools/gnd_layers.json` `(p1)`.
- `gnd extract` on a temporal **include root** keeps refusing, exit 3, and
  its message adds that `gnd flatten` writes the flat model. A temporal model
  without includes keeps today's message byte for byte (R0.6) `(p1)`.

### IR3 — PyRel export of an include root

- `render_pyrel` (default) and `pyrel_rules.render` (`--rules`) load the root
  with the composed loader, call `flatten_model`, and render the flat model's
  bytes in place of the root's. The temporal refusal of the default mode then
  applies to the flat model.
- Every composition or flattening refusal (`ModelValidationError` with an
  `include:` code, `FlatteningError`) is raised as `ExportInputError`, so
  `commands/export.py` exits 3 with the include code, not `EXIT_INTERNAL`
  (`commands/export.py:15-25`, `:45-55`) `(p1)`.
- The program records the flattening: the default program adds two constants
  after `MODEL_NAME`, and the `--rules` program adds the same two lines to its
  header. Names and spelling are an IR3 spec decision; D5 proposes
  `FLATTENING_RECORD_SHA256` and `MODEL_INCLUDES` (a tuple of
  `(id, path, sha256)`).
- A model without includes renders byte-identically to today (R0.6).

## 3. Dependencies and artifact homes

| Phase | Needs | Homes it changes |
|---|---|---|
| IR1 | nothing | `src/gnd/api.py`, `src/gnd/judgments.py`, `tests/test_mc1_guards.py`, a new `tests/test_ir1_judgments_includes.py`, the includes route list (created), `docs/reference/cli.md`, `docs/release-notes.md` `(p1)` |
| IR2 | nothing | a new `src/gnd/commands/flatten.py`, its registration in `src/gnd/cli.py` `(p1)`, `tools/gnd_entrypoints.json`, `tools/gnd_layers.json`, `src/gnd/extract/service.py` (message for include roots only), a new `tests/test_ir2_flatten.py`, `docs/reference/cli.md`, the representation-format includes section and its route list row, `docs/release-notes.md` `(p1)` |
| IR3 | nothing in code; IR2 for the user to reproduce a recorded digest (D2) | `src/gnd/export/emit.py`, `src/gnd/export/pyrel_rules.py`, `tests/test_mc1_guards.py`, `tests/test_mc1_review_regressions.py`, a new `tests/test_ir3_pyrel_includes.py`, the PyRel export page (`docs/agents/export-and-review.md`), the route list row, `docs/release-notes.md` `(p1)` |

Order: IR1, IR2, IR3, one at a time on the branch `claude/include-root-routes`.
The graph is acyclic; no phase needs another's code. IR3 follows IR2 so the
docs of IR3 can name the command that writes the record. pyrel-rules-coverage
writes `export/pyrel_rules.py` too (H10): IR3 does not start while an RP phase
has unmerged changes to that file. Start condition: `main` at `260c4337`.

The fixture for every phase is the interop example built by
`python -m gnd.examples.literature.interop run --out DIR` (in tests,
`gnd.examples.literature.interop.build(out)`): `checking.orm.json`
(temporal, two includes, one reference population), `extraction.orm.json`
(non-temporal, the same includes) and `composed.population.json` (written
for the checking model). The small two-file case
`tests/test_mc1_model_includes.py:write_case` serves the refusal tests.
`(p1)` Inputs the example does not write are authored by each phase's
tests: policies and receipts (consumer-pinned, bound to the model file the
case judges), a copy of the population relabelled with the extraction
root's `model_id` for IR1-C2, and flat models made in process by
`flatten_model`, which LX1 shipped. No phase needs another phase's output.

## 4. Phases

| Phase | Criteria | Inherited residuals |
|---|---|---|
| IR1 | **IR1-C1** `gnd judgments check checking.orm.json composed.population.json` with a policy and two approving receipts bound to the root, exit 0, `error` null, `admission` true. **IR1-C2** the same policy over `extraction.orm.json` directly and over its in-process flat model, on the relabelled population (receipts rebound to each model's sha256), gives equal `judgment_policy.targets` and `admission`. **IR1-C3** an include edited without a new pin, exit 3, `error.message` `include:hash-mismatch`; an include edited and pinned again, exit 3, `error.message` "stale judgment subject". **IR1-C4** a nested include, exit 3, `include:forbidden-section`. **IR1-C5** every include refusal's report validates against `judgment.schema.json` (H6). **IR1-C6** `test_R5_judgments_api` changes to the new behaviour; `test_R4_judgments` stays as the pin of the refusal for a direct `evaluate_judgments` caller that passes no `model_root`; `test_R10_session_judgments` stays as it is. **IR1-C7** a model without includes gives the byte-identical report it gives today, `model_digest` included. **IR1-C8** `(p1)` an include root whose reference file lives only under a separate `--reference-root` judges, exit 0. **IR1-C9** `(p2)` a version-5 document with `fact_type_constraints` and no `includes`, exit 3, `error.message` `include:declaration` | H11 stays a boundary |
| IR2 | **IR2-C1** `gnd flatten checking.orm.json --out DIR`, exit 0; the two files equal `flatten_model`'s bytes; the record names each element's origin and the flat model keeps `publication_not_before_submission`. **IR2-C2** `gnd check` verdicts over `checking.orm.flat.orm.json`, written into the root's own directory `(p2)`, equal those over `checking.orm.json` on `composed.population.json`; this is check parity for a temporal root, separate from R0.4's judgments parity `(p1)`. **IR2-C3** a model without includes, exit 3; an include refusal, exit 3, with its include code. **IR2-C4** either output file already present, exit 11, nothing written or changed. **IR2-C5** `gnd extract` on `checking.orm.json`, exit 3, message names `gnd flatten`; on an include-free temporal model the rf1 extract goldens stay green `(p1)` | none |
| IR3, default mode | **IR3-C1** `gnd export pyrel extraction.orm.json`, exit 0, and the program equals the export of its flat model (`extraction.orm.flat.orm.json` `(p2)`) except for the added constants and `MODEL_NAME`. **IR3-C2** `checking.orm.json` exits 3 with the temporal message, not an include refusal | none |
| IR3, `--rules lqp` and `--rules duckdb` | **IR3-C3** both roots get past the include refusal and give the same exit and message as their flat models. `(p1)` The expected outcome is fixed at IR3's spec gate from the state of `main` then, with the commit read: at `260c4337` it is `paper_names_parent_method#0: family 'anchored'`, exit 3 (H7); the spec names one outcome, never two | none |
| IR3, all modes | **IR3-C4** the program records the flattening record's sha256 and each include's sha256; an include changed and pinned again changes the recorded digest. Tested in the default mode on `extraction.orm.json` and, for `--rules`, on a small include root with no anchored constraint. **IR3-C5** the refusals pinned for these routes (`test_direct_refusals[R13-pyrel-rules]`, `test_cli_guards[pyrel]`, `test_R7_guard_precedes_temporal_classification`) change to match. **IR3-C6** a model without includes exports byte-identically to today. **IR3-C7** `(p1)` in each mode, an include edited without a new pin exits 3 with `include:hash-mismatch` and a nested include exits 3 with `include:forbidden-section`, never `EXIT_INTERNAL` | none |

Each phase also runs the structure and inventory guards, `uv run ruff check`,
an independent review of its diff, a refactoring review and its record.

## 5. Documentation, skill and compatibility surfaces

- **One home each.** The representation format's includes section
  (`src/gnd/skills/gnd-orm-core/references/representation-format.md`, near
  line 1892) says that `load_model` resolves includes and that unsupported
  consumers refuse `include:unsupported-route`, but it lists no route by
  name. IR1 adds a short list there of the CLI routes that resolve an include
  root, and each later phase adds its row; that list becomes the one home.
  `gnd flatten` (IR2) is described in the same file's "Extraction flattening
  record" subsection, the home of `gnd-flattening/1`. `docs/reference/cli.md`
  gains one row per new command or route and cites the list. The PyRel export
  page, `docs/agents/export-and-review.md`, says nothing about temporal
  models today; IR3 makes it the home of which export mode accepts them.
- **Release notes.** One entry per phase under the unreleased heading of
  `docs/release-notes.md`.
- **Compatibility.** No schema version changes (D4, D6). Error reports of
  include refusals change their `reason` from an include code to `binding`
  (H6); this is a fix to match the schema. Programs exported from include
  roots are new; programs from other models do not change (R0.6).
- **Issue replies.** The close drafts a reply to #217 and to #214 item 1; the
  owner posts them (posting is outside `auto`).

## 6. Risks and required controls

| Risk | Control |
|---|---|
| A direct judgment and a flat-model judgment drift | IR1-C2 parity test (R0.4) |
| `evaluate_judgments` judges a partial model for a direct caller | the `model_root`-less refusal and its test (IR1) |
| A route parses includes on its own and diverges from `gnd check` | R0.3; each spec names the loader call |
| The flattening record and the exported constants disagree | IR3 test compares the constant with `flatten_model(...).record_bytes` |
| Unchanged models get changed output | R0.6 controls in each phase |
| IR3 and pyrel-rules-coverage edit `pyrel_rules.py` together | the dependency rule in §3 |
| A guard test kept as a refusal pin silently stops testing anything | each changed pin is rewritten to the new positive behaviour, never deleted |
| `render_pyrel` promises "one bounded input read; no checker or foreign-runtime import" (`emit.py:21`); composing includes reads more files and imports the model loader | the IR3 spec states the new contract for include roots only and keeps the one-read path for other models; the entry-point import guards (`test_rf5_commands.py`, `test_rf7_structure.py`) run in its gate |

## 7. Out of scope

Temporal models in the default export; stale-program detection; `gnd exp`
session judgments; the assertion-admission example; any include rule change;
#214 items 2–4; release, tag and publication.

## 8. Execution, approval and review protocol

- `process-milestone include-root-routes auto` with the project rules in
  `.codex/skills/process-phase/references/project.md`.
- Plan review and close review: the GND panel light, owner-selected on
  2026-11-21. Convergence follows the bounded rules; one round is planned,
  a second only if the first blocks.
  `(p1)` Round 1 over r2 blocked (5 blocking of 24). Round 2 runs over r3;
  there is no round 3 (`evidence/plan-review-r1/disposition.md`).
  `(p2)` Round 2 over r3: 0 blocking of 5, self-inflicted 3 of 5; the budget
  is spent and the stop rule fires. r4 goes to the plan gate unreviewed
  (`evidence/plan-review-r2/disposition.md`).
- The delegated plan gate (`auto=true`) is recorded in `001-plan-gate.md`
  after the review's findings are dispositioned.
- Each phase: spec, delegated spec gate, code, focused gates, one independent
  reviewer over the diff (D7), refactoring review, record, commit.
- Pull request: one PR from `claude/include-root-routes` to `main`. Merge
  stays with the owner.

## 9. Per-phase verification

| Phase | Focused lane | Expected |
|---|---|---|
| IR1 | `uv run pytest -q tests/test_ir1_judgments_includes.py tests/test_mc1_guards.py tests/test_mc1_review_regressions.py tests/test_mc1_model_includes.py tests/test_public_v71_judgment_successor_guards.py tests/test_public_v71_full_judgments.py --tb=short` | exit 0 |
| IR2 | `uv run pytest -q tests/test_ir2_flatten.py tests/test_lx1_flattening.py tests/test_lx2_witness_flattening.py tests/test_extract_cli.py tests/test_public_extract_boundary.py tests/test_rf1_semantic_pins.py tests/test_mc1_guards.py --tb=short` `(p1)` | exit 0 |
| IR3 | `uv run pytest -q tests/test_ir3_pyrel_includes.py tests/test_pyrel_export.py tests/test_pyrel_export_boundaries.py tests/test_pyrel_rules.py tests/test_pyrel_rules_calendar.py tests/test_mc1_guards.py tests/test_mc1_review_regressions.py --tb=short` | exit 0 |
| all | the structure and inventory guard block of `project.md` (it includes `tests/test_rf5_commands.py` and `tests/test_rf7_structure.py`, the entry-point import guards §6 relies on), and `uv run ruff check` `(p1)` | exit 0 |

Affected consumers named here are read at each spec and may be widened there.
No broad lane (`-m "evidence or census"`) is selected.

## 10. Owner decisions and open questions

All rows are proposals until the plan gate rules them.

| ID | Question | Proposed |
|---|---|---|
| D1 | IR2: a separate `gnd flatten` command, or extend `gnd extract` | `gnd flatten MODEL --out DIR`, so extraction keeps its non-temporal contract. Alternative: `gnd export flat`, a smaller registration change |
| D2 | Is IR2 needed once IR1 lands, given #217 asks for one of the two | Yes. IR3 records a flattening digest; without IR2 no command writes that record for a temporal root, so the user cannot reproduce it or read the flat model that was exported |
| D3 | Temporal models in PyRel export | Default mode: stays out (`emit.py:36`). `--rules`: already accepted; no refusal is added. The reply to #214 says both |
| D4 | IR1: what the receipts and the report bind for an include root | `model_sha256` stays the root's bytes; the pins bind the includes; no schema version change. Alternative: a new `model_binding` field and `schema_version` 16, which every consumer of the report would have to accept |
| D5 | IR3: how the program records the flattening | constants `FLATTENING_RECORD_SHA256` and `MODEL_INCLUDES` in both program kinds, absent for a model without includes |
| D6 | IR1: the `error.reason` of an include refusal (H6) | `binding`, with the include code in `message` |
| D7 | Phase diff reviewer | `(p1)` the review helper (`.claude/skills/process-phase/scripts/review_tool.py`, subject `phase`), which runs Codex read-only: `project.md` names that shared default, one reviewer in a different tool, for a phase diff. r2 proposed a Claude subagent, which is the same tool. One reviewer is one reviewer |
