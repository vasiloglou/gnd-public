# PyRel rules coverage · plan r2

**Status: r2, 2026-11-21. Not reviewed. Not approved.** Written by
`start-milestone` from the r1 outline (`0cf94434`; its text is in git
history at this path). The plan review has not run. The owner selected the
full GND panel (xhigh) for the plan review and the close on 2026-11-21. This
status line changes when the review has run and when the plan gate is
recorded in `001-plan-gate.md`.

This plan covers items 2–4 of [#214](https://github.com/vasiloglou/gnd-public/issues/214)
and the value constraints that stop its quantity-fixture case. Item 1
(include roots) was delivered by [include-root-routes](../../include-root-routes/README.md)
IR3, merged to `main` in PR 220 (`8c909013`). Every code citation below was
read at `8c909013`.

## Goal and completion predicates

A model built with the literature-depth features exports as a PyRel rules
program (`gnd export pyrel --rules duckdb|lqp`) for RelationalAI. Each
constraint is either compiled to a `require`, or listed in the program by
id as not checked, which is what `gnd check` reports for it. No supported
literature model is refused on the first construct it meets. The default
(checker) export is unchanged.

- **RP1.** A top-level external uniqueness constraint compiles to a
  requirement over the shared-entity join that GND's checker uses
  (`checker/_core.py:1099-1150`). An entity whose reference mode is
  `external` gets the column type `String` (D4). Both packaged models that
  use the construct, `assertions/model.orm.yaml` and
  `lineage/model.orm.yaml`, export.
- **RP2.** An `anchored` constraint is listed in the program as not checked,
  with its id, and is never compiled. GND's checker reports it the same way
  (D1). The rest of the model exports.
- **RP3.** `primitive: Number` is typed like `Float` in both programs (D2).
- **RP4.** A value constraint scoped to a role (`role_ref`) compiles, both
  written on a fact type and written at the top level (D3).
- **RP5.** Every packaged literature model in §1's acceptance table exports
  under both `--rules duckdb` and `--rules lqp`, exit 0. Where a packaged
  population exists for it, the DuckDB program's verdicts equal `gnd check`'s
  on that population.

"Agrees with GND" in this plan has one meaning: the DuckDB program's exit
code and its non-OK finding set equal `gnd check`'s, as
`test_duckdb_program_agrees_with_gnd` compares them
(`tests/test_pyrel_rules.py:106-127`).

## 0. Binding design rules

- **No silent loss.** Whatever a program does not enforce is listed in it by
  constraint id, with the reason, and printed on every run. The export's
  success line counts the listed rules.
- **Same verdict as GND.** A program reports a rule as not checked exactly
  where `gnd check` does. A program that enforces less than GND checks is a
  defect; one that enforces more is a defect too.
- **Default export unchanged.** The default (checker) export already exits
  0 on these models; its bytes stay the same. `tests/test_pyrel_export.py`
  and `tests/test_pyrel_export_boundaries.py` hold it.
- **Families stay registered.** No new constraint family is introduced. A
  new lowering lives in `export/pyrel_rules.py` beside the family it
  extends, under the one family walk of `constraint_requirements`
  (`pyrel_rules.py:845-886`). `gnd.constraint_families.FAMILIES` is not
  edited (AGENTS.md, model queries and family dispatch).
- **Say what each test proves.** The default lane only reads program text
  and the requirement IR; it executes no program. Execution is the opt-in
  `pyrel_oracle` lane, which the owner selected for this milestone on
  2026-11-21 (§8). Offline, the `lqp` program is compile-only and DuckDB
  does not enforce `require` (`tests/test_pyrel_rules.py:290-293`,
  `pyrel_rules.py:2461-2466`). Enforcement on a RelationalAI engine is
  shown only by a named opt-in live run, which this plan does not schedule.

## 1. Scope, sources and authority

### Observed refusals

Each row was measured on 2026-11-21 at `8c909013`: first with
`uv run gnd export pyrel MODEL --rules lqp --out X`, then with a scratch
probe that turns each rules-program refusal into a skip and keeps going, so
the table lists every refusal a model meets, not only the first one.

| Model (`src/gnd/examples/literature/`) | Refusals, in the order met | Phase |
|---|---|---|
| `model.orm.yaml` (flat literature model) | `work_introduces_method#0`, `method_builds_on_method#0`, `#1`, `method_is_used_in_field#0`: `family 'anchored' is a later phase` (`pyrel_rules.py:864`) | RP2 |
| `assertions/model.orm.yaml` | `constraints_0: external uniqueness is a later phase` (`:882`); then `object type 'assertion' has no primitive or reference value type` (`:187`) | RP1 |
| `lineage/model.orm.yaml` | the same two as `assertions/` | RP1 |
| `resolution/model.orm.yaml` | `method_builds_on_method#0`, `#1`, `mention_has_surface_text#0`: anchored (`:864`) | RP2 |
| `quantity_fixture/time.orm.yaml` | `time_step#0`: anchored (`:864`); then `time_step#1`, `#2`: `family 'value' is a later phase` (`:864`) | RP2, RP4 |
| `interop_fixture/extraction.orm.json` | `paper_names_parent_method#0`: anchored (`:864`) | RP2 |
| `interop_fixture/checking.orm.json` (include root; exports its flat model since IR3) | `paper_names_parent_method#0`: anchored (`:864`) | RP2 |
| `depth_fixture/decimal.orm.json` | `primitive 'Number' is not supported by the rules programs yet` (`:190`) | RP3 |
| #214's six-line `Number` model | the same `:190` refusal (the issue's own reproduction) | RP3 |

`depth_fixture/algorithms`, `dynamics`, `molecular` and `vocabulary` already
render. `reading_fixture/reading.orm.json` stops on `include:unreadable`
because it includes files that are not shipped beside it. That refusal is
correct and out of scope.

### What GND itself does with each construct (measured)

- **Anchored.** `gnd check quantity_fixture/time.orm.yaml
  quantity_fixture/time.population.json` reports `[unchecked]
  fact_types[time_step].constraints[0]: Source anchor unchecked` and exits
  4. The family's evaluator is `_family_result_unknown`
  (`constraint_families.py:36`, `semantic_spec.py:3064-3065`). The anchor is
  checked by `gnd verify` against the source document, not by `gnd check`.
- **External uniqueness.** `gnd check` joins the referenced fact types on
  their shared anchor object types and counts each joined tuple of
  referenced values; a tuple seen more than once is a violation
  (`checker/_core.py:1099-1150`, `:2071-2074`). The constraint is vacuous
  when the join is empty (`_core.py:893-899`, `:983-986`), not when one fact
  list is empty. A disconnected join is refused (`_require_joinable`,
  `:1156`). On `assertions/raw.population.json`, `gnd check` exits 0.
- **External reference mode.** An entity with `reference: {mode: external}`
  has no resolvable primitive. GND skips the type check on its values and
  admits any scalar (`_core.py:1275-1278`). The packaged populations use
  strings (`assertions/raw.population.json`: `"working-notes#p01"`).
- **Number.** GND admits a finite integer or float, not a boolean, with the
  same identity token as `Float` (`gnd-orm-core/references/representation-format.md:1309`).
  The default (checker) export already types `Number` as `Float`
  (`pyrel_runtime.py:172`). GND does not check `precision` or `scale`.
- **Role-scoped value.** GND evaluates only the values in the named role,
  and the constraint is vacuous when that role has no facts
  (`semantic_spec.py:2583-2593`); the object type's other roles and its
  instances roster do not count.

### Sources

| Source | Obligation | Phase |
|---|---|---|
| #214 item 2 | external uniqueness in the rules programs; the assertions example uses it | RP1 |
| #214 item 3 | an explicit, recorded projection for anchored constraints | RP2 |
| #214 item 4 | `Number`, or a documented Integer / Decimal route | RP3 |
| #214 reproduction table, `quantity_fixture/time.orm.yaml` row | its value constraints with `role_ref` | RP4 |
| #214 reproduction table | the packaged models are the acceptance cases | RP5 |
| r1 outline D1–D4 | the four owner decisions, re-argued in §10 on what was measured | RP1–RP4 |
| [docs/runtimes/pyrel.md:156-161](../../../../docs/runtimes/pyrel.md) | the one home of the list of what the rules programs refuse | RP1–RP4 |

### Issue requests and the phases that discharge them

| Request | Phase |
|---|---|
| #214 item 1: include roots | done: include-root-routes IR3 (PR 220) |
| #214 item 2: external uniqueness in the rules programs | RP1 |
| #214 item 3: an explicit, recorded projection for anchored constraints | RP2 |
| #214 item 4: `Number`, or a documented Integer / Decimal route | RP3 |
| #214 reproduction table: every packaged literature case exports | RP4, RP5 |

## 2. Contract proposal and product behavior

All four phases change `src/gnd/export/pyrel_rules.py` only, plus tests,
fixtures and the PyRel runtime page.

### RP1 — external uniqueness

- `_external_uniqueness(model, c)` lowers a top-level `uniqueness` with
  `scope: external` to one `Requirement` of family `uniqueness`. It builds
  two copies of the join: one atom per referenced fact type, the referenced
  roles bound to shared variables, the anchor roles bound to per-copy
  variables keyed by object type (`$<object type>_1`, `$<object type>_2`),
  exactly as `_join_rows` merges anchors. The check is `same` over the anchor
  pairs: two joined rows with equal referenced values must have equal
  anchors. This is the shape `_uniqueness` already uses for one fact type
  (`pyrel_rules.py:686-699`).
- A join that GND would refuse as disconnected is refused by name, before
  lowering.
- Vacuity follows GND: vacuous when the join is empty. The program lists the
  join's rows (a listing part, as `cardinality` lists its members) and the
  report reads that listing. The exact part name is fixed at the RP1 spec.
- `raw_primitive` gives an entity with reference mode `external` the type
  `String` (D4). `check_cell` then refuses a non-string cell in that role
  with exit 3, naming the entity and saying GND would accept it. This is a
  stated difference from GND, listed on the runtime page.
- External frequency keeps its refusal (`:860`, `:882`).
- The fact-scoped external-uniqueness guard at `:855` stays as a defensive
  refusal: the schema admits no fact-scoped form
  (`representation-format.md:76`), so no valid model reaches it.

### RP2 — anchored constraints

- `constraint_requirements` handles family `anchored` like `textual`: it
  appends a row to `model.unchecked` and returns no requirement. The row
  gains a `reason` field; the textual row's reason is its expression, the
  anchored row's is that the source anchor is checked by `gnd verify`
  against the document. The report line changes from the hard-coded
  `textual rule:` text to the row's reason. Exact strings are fixed at the
  RP2 spec.
- Both the fact-scoped form (`:864`) and the top-level form (`:886`) are
  handled. Measured: a top-level anchored constraint carrying `role` or
  `recognise` fails `gnd validate` (exit 3, `unevaluatedProperties`);
  `anchored` is an inline family (`representation-format.md:9`). The RP2
  spec tests whether a bare top-level form validates.
- The DuckDB program then prints `<id>  not checked  (<reason>)` and exits
  4 for an alethic anchored rule, as `gnd check` does
  (`pyrel_rules.py:1647-1649`, band at `:1584-1585`).
- The LQP program prints the same not-checked lines before it reports the
  engine's result. Its exit code when a must-rule is listed is decision D5.
- The export's success line names the count of listed rules, for example
  `... to OUT; 4 rules are not checked (listed in the program)`.

### RP3 — `Number`

- `_TYPES` maps `Number` to `Float`; `check_cell` admits for `Number` what it
  admits for `Float`. Everything that refuses arithmetic or ordering on
  `Float` (`_refuse_inexact`, `pyrel_rules.py:1257`) refuses it on `Number`
  too, by name.

### RP4 — role-scoped value constraints

- `_value` with `role_ref` compiles a requirement whose domain is the values
  in that one role (an atom over the role's fact type), not the object
  type's universe. Its vacuity is the role's fact list being empty; the
  instances roster does not count.
- The fact-scoped branch (`:864`) admits family `value` and lowers it the
  same way. Measured: a fact-scoped value constraint without `role_ref`
  passes `gnd validate`; it is lowered like the top-level form without
  `role_ref` (the object type's universe), and the RP4 spec confirms
  against `gnd check` that GND scopes it the same way.

## 3. Dependencies and artifact homes

- RP1–RP4 are independent of one another in what they need, and all four
  edit `pyrel_rules.py`. They run one at a time, in the order RP1, RP2, RP3,
  RP4, on one branch. RP5 needs all four.
- Start condition met: include-root-routes is closed and merged
  (`8c909013`), so this milestone is the only writer of `pyrel_rules.py`.
- RP5 exports packaged models only and uses no literature-host-interfaces
  deliverable.
- Homes: code in `src/gnd/export/pyrel_rules.py` and, for the success line,
  `src/gnd/commands/export.py`; tests in `tests/test_pyrel_rules.py`,
  `tests/test_pyrel_rules_families.py` and one new file per phase,
  `tests/test_rp<N>_*.py`; review fixtures in
  `tests/fixtures/pyrel-rules-families/review/`; the user-facing list in
  `docs/runtimes/pyrel.md`.
- Populations used by the oracle tests are the packaged ones (§1) plus small
  fixtures each spec writes for the discriminating cases.

## 4. Phases

| Phase | Criteria |
|---|---|
| RP1 | **RP1-C1** `assertions/` and `lineage/` render under both targets, exit 0. **RP1-C2** the default lane checks that both programs state the (work, passage) requirement from one `Requirement` (`test_both_programs_state_each_rule_from_one_requirement`'s rule). **RP1-C3** (oracle) the DuckDB program agrees with GND on `assertions/raw.population.json` (exit 0), on a population with one duplicate (work, passage) pair (exit 1, the same witness), and on one whose join is empty while both fact lists are not (vacuous, as GND). **RP1-C4** (oracle) a non-string `assertion` value is refused with exit 3 by name. **RP1-C5** `refuse-external-uniqueness.orm.json` (`tests/test_pyrel_rules_families.py:98`) renders; the external-frequency refusal stays. **RP1-C6** a disconnected external join is refused by name |
| RP2 | **RP2-C1** the flat literature model, `resolution/`, both interop models and the quantity fixture's anchored constraint pass the anchored step (the quantity fixture still stops on RP4's refusal until RP4). **RP2-C2** every anchored id appears in `UNCHECKED` and in no requirement. **RP2-C3** (oracle) on the gold populations of the flat literature model, the DuckDB program agrees with GND (exit 4, each anchored id not checked). **RP2-C4** a textual rule's line is unchanged. **RP2-C5** the success line counts the listed rules |
| RP3 | **RP3-C1** #214's six-line model and `depth_fixture/decimal.orm.json` render under both targets. **RP3-C2** (oracle) the DuckDB program agrees with GND on `depth_fixture/decimal.population.json`, and refuses a boolean in a `Number` role with exit 3 as GND does. **RP3-C3** arithmetic on a `Number` value in a derivation is refused by name, as on `Float` |
| RP4 | **RP4-C1** a role-scoped value constraint renders in both branches. **RP4-C2** (oracle) a population with a disallowed value in that role is denied (exit 1, GND's witness) and one with the same value only in another role of the object type is not; an empty role is vacuous, as GND. **RP4-C3** `quantity_fixture/time.orm.yaml` renders under both targets |
| RP5 | **RP5-C1** every model in §1's table except `reading.orm.json` renders under both targets, exit 0. **RP5-C2** (oracle) for each with a packaged population, the DuckDB program agrees with GND. **RP5-C3** `docs/runtimes/pyrel.md` lists what the programs check, what they list as not checked, and what they refuse, and no line of it contradicts the code |

"(oracle)" marks a criterion discharged in the `pyrel_oracle` lane (§9).

## 5. Documentation, skill and compatibility surfaces

- `docs/runtimes/pyrel.md:156-161` is the one home of the refusal list.
  RP1–RP4 each edit it in the commit that changes the behavior. RP5 reads it
  whole against the code.
- `docs/explanation/rules-as-pyrel.md:69-70` says a textual rule is
  "reported as not checked on every run"; RP2 adds anchored rules to that
  sentence or cites the runtime page.
- The packaged `gnd-export` skill does not describe the rules programs'
  coverage (`src/gnd/skills/gnd-export/`, read at `8c909013`); no skill edit.
- Compatibility: a program generated before this milestone keeps its bytes.
  A newly generated program for a model that used to export changes only
  where RP2's report line changes (`textual rule:` → the row's reason) and
  where the success line gains its count. RP2's spec lists the golden files
  and pinned strings that move, measured, not guessed.

## 6. Risks and required controls

| Risk | Control |
|---|---|
| A program listing anchored rules is read as full enforcement | the not-checked lines print on every run, the DuckDB program exits 4 as GND does, and the success line counts them |
| External uniqueness compiled over the wrong join (a Cartesian product, or anchors matched by role name instead of object type) | RP1-C3's duplicate case and empty-join case run against GND in the oracle lane |
| A rule checked as vacuous when GND decides it, or the reverse | each phase has one oracle case at the vacuity boundary (RP1 empty join, RP4 empty role) |
| `String` for an external entity refuses input GND accepts | the refusal is by name, exit 3, and listed on the runtime page as a difference from GND (D4) |
| A fixture that cannot tell two readings apart (project.md failure class) | RP4-C2's "same value in another role" case separates role scope from object-type scope |
| The structure and inventory guards go red unnoticed | every phase runs the guard block (§9) |

## 7. Out of scope

External frequency (`:596`, `:860`, `:882`); exact averages (`:745`);
temporal models in the default export; `DateTime`; subtypes; checking
source anchors in a program (that is `gnd verify`'s job); a live RelationalAI
run; posting to #214; release, tag and publication.

## 8. Execution, approval and review protocol

- `process-milestone pyrel-rules-coverage auto`, invoked by the owner on
  2026-11-21, with the project rules in
  `.codex/skills/process-phase/references/project.md`.
- Plan review and close review: the full GND panel (xhigh), owner-selected
  on 2026-11-21, run with `uv run python tools/run_gnd_review_panel.py
  REQUEST --out DIR` from a disposable worktree at the reviewed commit.
  Budget: at most two plan-review rounds. A second round runs only if the
  first returns a blocking concern. The stop rule of the review-convergence
  reference applies after round 2; there is no round 3. One close round.
- The delegated plan gate (`auto=true`) is recorded in `001-plan-gate.md`
  after the review's findings are dispositioned.
- Each phase: spec, delegated spec gate, code, focused gates, one
  independent reviewer over the diff (the review helper with Codex,
  read-only; one reviewer is one reviewer), refactoring review, record,
  commit.
- The `pyrel_oracle` lane is opted in by the owner for this milestone's
  phase and close gates (2026-11-21). It runs with
  `tutorials/runtimes/.venv`, built in the worktree with `uv sync --frozen
  --group tutorial-runtimes`. Baseline at `8c909013`: `uv run pytest -q -m
  pyrel_oracle tests/test_pyrel_rules.py tests/test_pyrel_rules_families.py`
  gave `110 passed, 21 deselected`.
- Pull request: one PR from `claude/pyrel-rules-coverage` to `main`. Merge
  stays with the owner.
- No component index exists in this repository (`project.md`); no index
  step runs.

## 9. Per-phase verification

| Phase | Focused lane (default) | Oracle lane (opted in) | Expected |
|---|---|---|---|
| RP1 | `uv run pytest -q tests/test_rp1_external_uniqueness.py tests/test_pyrel_rules.py tests/test_pyrel_rules_families.py tests/test_pyrel_export.py tests/test_pyrel_export_boundaries.py --tb=short` | `uv run pytest -q -m pyrel_oracle tests/test_rp1_external_uniqueness.py tests/test_pyrel_rules.py tests/test_pyrel_rules_families.py` | exit 0 |
| RP2 | the same with `tests/test_rp2_anchored.py`, plus `tests/test_rules_in_pyrel.py` and `tests/test_pyrel_rules_derivations.py` (pinned program text) | the same files under `-m pyrel_oracle` | exit 0 |
| RP3 | the same with `tests/test_rp3_number.py` | the same under `-m pyrel_oracle` | exit 0 |
| RP4 | the same with `tests/test_rp4_role_value.py` | the same under `-m pyrel_oracle` | exit 0 |
| RP5 | the same with `tests/test_rp5_literature_rules.py` | the same under `-m pyrel_oracle` | exit 0 |
| all | the structure and inventory guard block of `project.md`, and `uv run ruff check` | — | exit 0 |

Affected consumers named here are read at each spec and may be widened
there; a spec that finds another file pinning program text adds it. No
broad lane (`-m "evidence or census"`) is selected.

## 10. Owner decisions and open questions

| ID | Question | r1 proposal | r2 proposal, on what was measured |
|---|---|---|---|
| D1 | RP2: skip anchored constraints with a loss report, or carry them as non-enforced metadata | loss report, as `gnd export ossie` | list them in the program as not checked (the `UNCHECKED` table textual rules use), with a reason, and count them in the success line. Measured: `gnd check` reports an anchored constraint as unchecked and exits 4 (§1). A separate loss file that only drops them would make the DuckDB program exit 0 where GND exits 4, breaking "Same verdict as GND" |
| D2 | RP3: support `Number`, or document Integer / scaled Decimal as the route | support it if RelationalAI has an exact numeric type; otherwise document | type it as `Float`. Measured: GND's own `Number` admits the same values with the same identity as `Float` and checks no scale (§1), and the default export already maps it to `Float`. An exact decimal type would be stricter than GND |
| D3 | RP4: take role-scoped value constraints in, or drop the quantity fixture from RP5 | take them in | unchanged: take them in |
| D4 | RP1: how the programs type an entity identified only by an external uniqueness, such as `assertion` | the type of the identifier its population rows carry | `String`, decided from the model, never from a population. GND admits any scalar there (§1); a non-string value is refused by name with exit 3, a stated difference |
| D5 | RP2: when the LQP program lists a must-rule as not checked and the engine reports no violation, does it exit 0 or 4 | (new in r2) | 4, as the DuckDB program and `gnd check` do; fixed at the RP2 spec |

Open questions carried into the phases:

| Question | Owner |
|---|---|
| Exact part name and witness shape for the external-uniqueness join listing | RP1 spec |
| Which program-text goldens and pinned strings move when the not-checked line changes | RP2 spec, measured |
| Whether a bare top-level `anchored` constraint validates; whether GND scopes a fact-scoped value constraint without `role_ref` to the object type | RP2 and RP4 specs, by test |
| The lqp program gives textual rules no not-checked line today (`_LQP_MAIN`, `pyrel_rules.py:2057-2126`); RP2 fixes it for both kinds | RP2 |
