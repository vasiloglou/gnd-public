# PyRel rules coverage · plan r4

**Status: r4, 2026-11-21. Not approved.** Written by `start-milestone`
from the r1 outline (`0cf94434`; its text is in git history at this path).
Two rounds of the full GND panel (xhigh, owner-selected on 2026-11-21):
round 1 over r2 (`a2a69608`, sha256 `f2296905…3dbf`; repairs `(p1)`, in
r3) and round 2 over r3 (`5b1df6fb`, sha256 `077871ed…4179`; repairs
`(p2)`, in r4). Dispositions: [round 1](../evidence/plan-review-r1/disposition.md),
[round 2](../evidence/plan-review-r2/disposition.md). The stop rule fired
after round 2 and the budget was two rounds. **r4 has not been reviewed**;
its `(p2)` text carries no review opinion.

This plan covers items 2–4 of [#214](https://github.com/vasiloglou/gnd-public/issues/214)
and the value constraints that stop its quantity-fixture case. Item 1
(include roots) was delivered by [include-root-routes](../../include-root-routes/README.md)
IR3, merged to `main` in PR 220 (`8c909013`). Every code citation below was
read at `8c909013`.

## Goal and completion predicates

A model built with the literature-depth features exports as a PyRel rules
program (`gnd export pyrel --rules duckdb|lqp`) for RelationalAI. Each
constraint is either compiled to a `require`, or listed in the program by
id as not checked, which is what `gnd check` reports for it when it is run
without an anchor sidecar `(p1)`. No supported literature model is refused
on the first construct it meets. The default (checker) export and the Ossie
export are unchanged `(p1)`.

- **RP1.** A top-level external uniqueness constraint compiles to a
  requirement over the shared-entity join that GND's checker uses
  (`checker/_core.py:1099-1150`). A disconnected join is reported as GND
  reports it: vacuous when every referenced fact list is empty, otherwise
  not checked with GND's reason `(p1)` `(p2)`. An ambiguous join is refused
  at model load, as GND refuses it (exit 3) `(p2)`. An entity
  whose reference mode is `external` gets the column type `String` (D4). Both
  packaged models that use the construct, `assertions/model.orm.yaml` and
  `lineage/model.orm.yaml`, export.
- **RP2.** An `anchored` constraint is listed in the program as not checked,
  with its id, and is never compiled. GND's checker reports it the same way
  (D1). The rest of the model exports.
- **RP3.** `primitive: Number` is typed like `Float` in both programs (D2).
  An integer the program cannot hold exactly as a float is refused by name
  (D6) `(p1)`, in a population cell or in a model constant `(p2)`.
- **RP4.** A value constraint scoped to a role (`role_ref`) compiles, both
  written on a fact type and written at the top level (D3).
- **RP5.** Every packaged literature model in §1's acceptance table exports
  under both `--rules duckdb` and `--rules lqp`, exit 0. On every population
  that table names, the DuckDB program agrees with GND `(p1)`.

"Agrees with GND" in this plan has one meaning: the DuckDB program's exit
code and its non-OK finding set equal `gnd check`'s (run without an anchor
sidecar), as `test_duckdb_program_agrees_with_gnd` compares them
(`tests/test_pyrel_rules.py:106-127`). `(p1)` That comparator cannot yet
represent a not-checked rule: `_findings` calls `json.loads` on the text
after the status (`:62-73`), and `_gnd` turns an `unchecked` verdict with no
offending facts into no finding (`:83-102`). RP2 extends both sides to
`(rule, 'not checked', null)`, with a negative control (RP2-C6), before any
criterion relies on it.

## 0. Binding design rules

- **No silent loss.** Whatever a program does not enforce is listed in it by
  constraint id, with the reason, and printed on every run. The export's
  success line counts the listed rules.
- **Same verdict as GND.** On every input a program accepts, it reports a
  rule as not checked exactly where `gnd check` (without an anchor sidecar)
  does. A program that enforces less than GND checks is a defect; one that
  enforces more is a defect too. `(p1)` An input the program cannot represent
  exactly is refused by name with exit 3, before PyRel sees it, as repeated
  facts and opaque values already are (`pyrel_rules.py:2532-2533`,
  `:2545`). Each such refusal is a stated difference from GND, listed on
  the runtime page, and has a test that pins both exits.
- **Default export unchanged.** The default (checker) export already exits
  0 on these models; its bytes stay the same. `tests/test_pyrel_export.py`
  and `tests/test_pyrel_export_boundaries.py` hold it.
- **Ossie export unchanged** `(p1)`. `gnd export ossie` calls the same
  lowering (`export/ossie_formulas.py:272`, `:293`) and treats an
  `ExportInputError` as "not projected" (`:295`), so a refusal this
  milestone lifts can turn into a new Ossie projection. Its committed tests
  (`tests/test_ossie_formulas.py`, `tests/test_ossie_export.py`) run in every
  phase's lane. A phase whose change would alter an Ossie output keeps the
  Ossie path refusing that shape, unless its spec rules otherwise and names
  the moved bytes.
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
| `assertions/model.orm.yaml` | `constraints_0: external uniqueness is a later phase` (`:882`, one line that raises for external uniqueness and external frequency alike `(p2)`); then `object type 'assertion' has no primitive or reference value type` (`:187`) | RP1 |
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

### Populations for the agreement criteria `(p1)`

Measured on 2026-11-21 with `gnd check MODEL POPULATION` (no sidecar).

| Model | Populations | `gnd check` exit |
|---|---|---|
| `model.orm.yaml` | the twelve `answers/gold/*.population.json` | 4 each (four anchored rules unchecked) |
| `assertions/model.orm.yaml` | `assertions/raw.population.json` | 0 |
| `resolution/model.orm.yaml` | the 41 `resolution/cases/*/*/population.json` `(p2)` | 4 (first case measured; the rest are measured by the RP5 test itself) |
| `quantity_fixture/time.orm.yaml` | `quantity_fixture/time.population.json` | 4 |
| `depth_fixture/decimal.orm.json` | `depth_fixture/decimal.population.json` | 0 |
| `lineage/model.orm.yaml`, both interop models | none in the population format (`lineage/*-input.json` and `interop_fixture/*.gold.json` are other formats) | — |

### What GND itself does with each construct (measured)

- **Anchored.** `gnd check quantity_fixture/time.orm.yaml
  quantity_fixture/time.population.json` reports `[unchecked]
  fact_types[time_step].constraints[0]: Source anchor unchecked` and exits
  4; so does `gnd check model.orm.yaml answers/gold/apinn.population.json`
  (four anchored rules unchecked). The family's evaluator is
  `_family_result_unknown` (`constraint_families.py:36`,
  `semantic_spec.py:3064-3065`). `(p1)` Given a sidecar, `gnd check
  --anchors SIDECAR --document DOC` decides them
  (`commands/checking.py:890-891`; the quantity fixture's README runs it).
  The programs read no sidecar.
- **External uniqueness.** `gnd check` joins the referenced fact types on
  their shared anchor object types and counts each joined tuple of
  referenced values; a tuple seen more than once is a violation
  (`checker/_core.py:1099-1150`, `:2071-2074`). The constraint is vacuous
  when the join is empty (`_core.py:893-899`, `:983-986`), not when one fact
  list is empty. `(p1)` `(p2)` Measured on scratch models on 2026-11-21: a
  **disconnected** join (two fact types sharing no anchor object type) is
  vacuous, exit 2, when both referenced fact lists are empty, and
  **unchecked**, exit 4, otherwise ("Role references span fact types ...
  that share no anchor object type"; `semantic_spec.py:2895-2933` applies
  empty-subject vacuity before `join_refusal_of`). An **ambiguous** join (one
  referenced fact type with two non-referenced roles of one object type)
  never reaches a verdict: `gnd validate` and `gnd check` refuse the model
  with `semantic:join-anchor-ambiguous`, exit 3, and the rules export already
  refuses it as `invalid model` (exit 3). (r2 said both were refused; r3 said
  both were unchecked. Each was half wrong.) On `assertions/raw.population.json`, `gnd check` exits 0; with one
  repeated (passage, work) pair, exit 1 and witness
  `[["p01", "working-notes"]]`; with an empty join, exit 2 (vacuous).
- **External reference mode.** An entity with `reference: {mode: external}`
  has no resolvable primitive. GND skips the type check on its values and
  admits any scalar (`_core.py:1275-1278`). The packaged populations use
  strings (`assertions/raw.population.json`: `"working-notes#p01"`).
- **Number.** GND admits a finite integer or float, not a boolean, with the
  same identity token as `Float` (`src/gnd/skills/gnd-orm-core/references/representation-format.md:1309`) `(p1)`.
  The default (checker) export already types `Number` as `Float`
  (`pyrel_runtime.py:172`). GND does not check `precision` or `scale`.
  `(p1)` GND keeps an integer's exact ratio (`values.py:392-399`); a binary
  float cannot tell 9007199254740992 from 9007199254740993, so the programs
  cannot hold every integer GND admits in a `Number` or `Float` role.
  `(p2)` A boolean in a `Number` role: `gnd check` exits 3
  (`population:type-mismatch`). No packaged population under
  `src/gnd/examples/literature/` holds an integer beyond 2**53 (scan of every
  `*.population.json`).
- **Anchored, empty subject** `(p2)`. With `time_step` empty, declared in
  `covers` or not, `gnd check` still reports the anchored rule unchecked
  (exit 4): the family's scope hook returns no subject fact types
  (`_family_scope_empty`), so empty-subject vacuity never applies.
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

All four phases change `src/gnd/export/pyrel_rules.py`, plus tests and
fixtures. `(p1)` RP2 also changes `src/gnd/commands/export.py` (the success
line) and `docs/explanation/rules-as-pyrel.md`; each phase edits
`docs/runtimes/pyrel.md`.

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
- `(p1)` `(p2)` Before lowering, the join is classified as GND classifies
  it. A disconnected join compiles to no requirement; the program decides at
  run time, in GND's order: vacuous when every referenced fact list is
  empty, otherwise not checked with GND's reason, through RP2's mechanism
  (RP2's not-checked rows therefore carry an optional vacuity condition). An
  ambiguous join never gets here: model load refuses it (exit 3), as GND
  does. RP1 runs after RP2 (§3).
- `(p2)` The `:882` line raises for both external families. RP1 splits it:
  external uniqueness lowers, external frequency keeps its message.
- `(p2)` Join arity. The join may span any number of referenced fact types;
  "two copies" means two copies of the whole join, with per-copy anchor
  variables, and `same` over every anchor pair. RP1's spec adds a
  three-fact-type case.
- Vacuity follows GND: vacuous when the join is empty. The program lists the
  join's rows (a listing part, as `cardinality` lists its members) and the
  report reads that listing. The exact part name is fixed at the RP1 spec.
- `raw_primitive` gives an entity with reference mode `external` the type
  `String` (D4). `check_cell` then refuses a non-string cell in that role
  with exit 3, naming the entity and saying GND would accept it. This is a
  stated input refusal under §0 `(p1)`, listed on the runtime page.
- `(p1)` Anchor equality is the program's equality on the anchor's type.
  With string anchors it equals GND's identity; RP1-C8 measures a numeric
  anchor (`1` and `1.0` in a `Float`-identified entity). If the program does
  not agree with GND there, that anchor type becomes a by-name input refusal
  under §0 `(p2)`.
- External frequency keeps its refusal (`:860`, `:882`).
- The fact-scoped external-uniqueness guard at `:855` stays as a defensive
  refusal: the schema admits no fact-scoped form
  (`representation-format.md:76`), so no valid model reaches it.

### RP2 — anchored constraints

- `constraint_requirements` handles family `anchored` like `textual`: it
  appends a row to `model.unchecked` and returns no requirement. The row
  gains a `reason` field, and the report line prints it:
  `<id>  not checked  (<reason>)`. `(p1)` The textual row's reason is
  `textual rule: <expression>`, so a textual rule's printed line stays
  byte-identical. The anchored row's reason says the rule needs a source
  anchor sidecar, which `gnd check --anchors --document` reads and the
  programs do not. Exact strings are fixed at the RP2 spec.
- `(p2)` An anchored rule is not checked whether or not its fact list is
  empty, as measured (§1); the RP2 spec pins the empty-subject case against
  GND in the oracle lane. A deontic not-checked rule does not move the exit
  band in either program, as GND's `deontic-unchecked-keeps-band` rule
  says.
- Both the fact-scoped form (`:864`) and the top-level form (`:886`) are
  handled. Measured: a top-level anchored constraint carrying `role` or
  `recognise` fails `gnd validate` (exit 3, `unevaluatedProperties`);
  `anchored` is an inline family (`representation-format.md:9`). The RP2
  spec tests whether a bare top-level form validates.
- The DuckDB program then prints `<id>  not checked  (<reason>)` and exits
  4 for an alethic anchored rule, as `gnd check` does
  (`pyrel_rules.py:1647-1649`, band at `:1584-1585`).
- The LQP program prints the same not-checked lines before it reports the
  engine's result, and with `--compile` too `(p1)`. Its exit code when a
  must-rule is listed is decision D5. The lines and the exit come from one
  function the main calls, which RP2-C7 runs with the engine call stubbed,
  in the oracle lane's interpreter `(p2)` (the default lane executes no
  program, §0).
- `(p1)` The oracle comparator learns not-checked lines on both sides
  (Goal), with a negative control: a program with one anchored id removed
  from `UNCHECKED` must fail the comparison.
- The export's success line names the count of listed rules, for example
  `... to OUT; 4 rules are not checked (listed in the program)`. `(p2)` Only
  the rules path changes (`_cmd_export_pyrel_rules`,
  `commands/export.py:40-65`); the checker export's success line keeps its
  bytes.

### RP3 — `Number`

- `_TYPES` maps `Number` to `Float`; `check_cell` admits for `Number` what it
  admits for `Float`. Everything that refuses arithmetic or ordering on
  `Float` (`_refuse_inexact`, `pyrel_rules.py:1257`) refuses it on `Number`
  too, by name.
- `(p1)` `check_cell` refuses, with exit 3 and by name, an integer in a
  `Number` or `Float` role whose magnitude exceeds 2**53, the largest range
  in which every integer is exact as a binary float (D6). This is a stated
  input refusal under §0.
- `(p2)` The same bound applies to the model's own numeric constants in a
  `Number` or `Float` context (`allowed` values, range bounds, comparison
  literals): the export refuses such a model by name, exit 3, since a
  `Float`-typed helper such as `_allowed`'s cannot hold them exactly.

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

- `(p1)` RP1 needs RP2's not-checked reason (for disconnected and
  ambiguous joins). RP3 and RP4 need nothing from the others. All four edit
  `pyrel_rules.py`, so they run one at a time on one branch, in the order
  **RP2, RP1, RP3, RP4**, then RP5, which needs all four. Phase IDs are
  unchanged.
- Start condition met: include-root-routes is closed and merged
  (`8c909013`), so this milestone is the only writer of `pyrel_rules.py`.
- RP5 exports packaged models only and uses no literature-host-interfaces
  deliverable.
- Affected consumer `(p1)`: `src/gnd/export/ossie_formulas.py`, which calls
  `constraint_context` and `constraint_requirements` (§0).
- Homes: code in `src/gnd/export/pyrel_rules.py` and, for the success line,
  `src/gnd/commands/export.py`; tests in `tests/test_pyrel_rules.py`,
  `tests/test_pyrel_rules_families.py` and one new file per phase,
  `tests/test_rp<N>_*.py`; this milestone's fixtures in
  `tests/fixtures/pyrel-rules-coverage/rp<N>/` `(p2)`, the existing review
  fixtures staying in `tests/fixtures/pyrel-rules-families/review/`; the
  user-facing list in `docs/runtimes/pyrel.md`.
- `(p2)` Ossie pins. A phase that makes a shape newly lowerable (RP1's
  external uniqueness and `String` entity, RP3's `Number`, RP4's role-scoped
  and fact-scoped value) adds a test that `gnd export ossie` on a model with
  that shape gives the bytes it gave at `8c909013`, because the committed
  Ossie tests cover none of them.
- Populations used by the oracle tests are the packaged ones (§1) plus small
  fixtures each spec writes for the discriminating cases.

## 4. Phases

| Phase | Criteria |
|---|---|
| RP2 (runs first) | **RP2-C1** the flat literature model, `resolution/`, both interop models and the quantity fixture's anchored constraint pass the anchored step (the quantity fixture still stops on RP4's refusal until RP4). **RP2-C2** every anchored id appears in `UNCHECKED` and in no requirement. **RP2-C3** (oracle) on the twelve gold populations of the flat literature model, the DuckDB program agrees with GND (exit 4, each anchored id not checked). **RP2-C4** in the DuckDB program, a textual rule's printed line is byte-identical to `8c909013`'s `(p1)` `(p2)`. **RP2-C5** the rules success line counts the listed rules, and the checker export's success line is unchanged `(p2)`. **RP2-C8** `(p2)` (oracle) an anchored rule over an empty fact list is not checked, and the program agrees with GND (exit 4). **RP2-C6** `(p1)` the comparator represents not-checked rules on both sides, and the negative control (one anchored id dropped from `UNCHECKED`) fails it. **RP2-C7** `(p1)` (oracle `(p2)`) the LQP program's report function, run with the engine stubbed, prints the not-checked lines and returns D5's exit; `--compile` prints them too |
| RP1 | **RP1-C1** `assertions/` and `lineage/` render under both targets, exit 0. **RP1-C2** the default lane checks that both programs state the (work, passage) requirement from one `Requirement` (`test_both_programs_state_each_rule_from_one_requirement`'s rule). **RP1-C3** (oracle) the DuckDB program agrees with GND on `assertions/raw.population.json` (exit 0), on a population with one duplicate (passage, work) pair (exit 1, the same witness), and on one whose join is empty while both fact lists are not (exit 2, vacuous). **RP1-C4** (oracle) a non-string `assertion` value is refused with exit 3 by name, while `gnd check` exits 0 on it (both pinned). **RP1-C5** `refuse-external-uniqueness.orm.json` (`tests/test_pyrel_rules_families.py:98`) renders; the external-frequency refusal stays. **RP1-C6** `(p1)` `(p2)` (oracle) a disconnected external join agrees with GND on a population with facts (not checked, exit 4) and on one with every referenced list empty (vacuous, exit 2). **RP1-C7** `(p2)` an ambiguous join is refused at export with exit 3, as `gnd check` refuses the model (both pinned). **RP1-C8** `(p2)` (oracle) a numeric-anchor population (`1` and `1.0`) agrees with GND, or the anchor type is refused by name under §0. **RP1-C9** `(p2)` an external uniqueness over three referenced fact types renders and (oracle) agrees with GND on a duplicate |
| RP3 | **RP3-C1** #214's six-line model and `depth_fixture/decimal.orm.json` render under both targets. **RP3-C2** (oracle) the DuckDB program agrees with GND on `depth_fixture/decimal.population.json`, and refuses a boolean in a `Number` role with exit 3, as `gnd check` does (measured, §1) `(p2)`. **RP3-C3** arithmetic on a `Number` value in a derivation is refused by name, as on `Float`. **RP3-C4** `(p1)` (oracle) the integer 9007199254740993 in a `Number` role, and in a `Float` role, is refused with exit 3 by name, while `gnd check` decides it (both pinned). **RP3-C5** `(p2)` a model whose `allowed` list holds 9007199254740993 for a `Number` object type is refused at export by name, exit 3 |
| RP4 | **RP4-C1** a role-scoped value constraint renders in both branches. **RP4-C2** (oracle) a population with a disallowed value in that role is denied (exit 1, GND's witness) and one with the same value only in another role of the object type is not; an empty role is vacuous, as GND. **RP4-C3** `quantity_fixture/time.orm.yaml` renders under both targets |
| RP5 | **RP5-C1** `(p2)` these eleven packaged models render under both targets, exit 0: `model.orm.yaml`, `assertions/model.orm.yaml`, `lineage/model.orm.yaml`, `resolution/model.orm.yaml`, `quantity_fixture/time.orm.yaml`, `interop_fixture/extraction.orm.json`, `interop_fixture/checking.orm.json`, and `depth_fixture/{algorithms,decimal,dynamics,molecular,vocabulary}.orm.json` (the last four already render and are held). #214's six-line model belongs to RP3-C1; `reading_fixture/reading.orm.json` is excluded (§1). **RP5-C2** (oracle) on each population named in §1's population table `(p1)`, the DuckDB program agrees with GND, with the GND exit that table records. **RP5-C3** `docs/runtimes/pyrel.md` lists what the programs check, what they list as not checked, and what they refuse. `(p2)` A default-lane test asserts that every not-checked reason and every refusal message the programs can print for the constructs this milestone touches appears on that page; the phase's reviewer reads the rest of the page against the code |

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
  `(p1)` A program newly generated for a model that already exported prints
  the same report lines (the textual line is unchanged, RP2-C4); its source
  text changes where `UNCHECKED` rows gain `reason` and where D6's bound
  enters `check_cell`. The export's success line gains its count. Each
  phase's spec lists the golden files and pinned strings that move,
  measured, not guessed. Ossie output is unchanged (§0).

## 6. Risks and required controls

| Risk | Control |
|---|---|
| A program listing anchored rules is read as full enforcement | the not-checked lines print on every run, the DuckDB program exits 4 as GND does, and the success line counts them |
| External uniqueness compiled over the wrong join (a Cartesian product, or anchors matched by role name instead of object type) | RP1-C3's duplicate case and empty-join case run against GND in the oracle lane |
| A rule checked as vacuous when GND decides it, or the reverse | each phase has one oracle case at the vacuity boundary (RP1 empty join, RP4 empty role) |
| `String` for an external entity refuses input GND accepts | the refusal is by name, exit 3, and listed on the runtime page as a difference from GND (D4) |
| A fixture that cannot tell two readings apart (project.md failure class) | RP4-C2's "same value in another role" case separates role scope from object-type scope |
| The structure and inventory guards go red unnoticed | every phase runs the guard block (§9) |
| `(p1)` A lifted refusal silently changes `gnd export ossie` | the Ossie tests run in every phase's lane; §0 "Ossie export unchanged" |
| `(p1)` A rule GND leaves unchecked (disconnected join, anchored) is compiled, or one GND refuses (ambiguous join) is exported `(p2)` | RP1-C6, RP1-C7, RP2-C2, RP2-C8, and the comparator's negative control RP2-C6 |

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
  `(p1)` Round 1 over r2 returned blocking concerns: 6 of 19 by the
  disposition's triage (four of six seats; Qwen and Gemini malformed). Round
  2 runs over r3 and is the last.
  `(p2)` Round 2 over r3: four of six seats (Claude and Gemini failed), Kimi
  approved, 19 concerns; 12 attack `(p1)` text, so the self-inflicted ratio
  is 12/19 and the stop rule fires. r4 goes to the plan gate unreviewed
  (`evidence/plan-review-r2/disposition.md`).
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

`(p1)` Every focused lane below also runs `tests/test_ossie_formulas.py
tests/test_ossie_export.py` (§0, Ossie export unchanged). Order of execution:
RP2, RP1, RP3, RP4, RP5 (§3). `(p2)` Lanes are cumulative: each phase's
lane, default and oracle, runs every earlier phase's new test file too.

| Phase | Focused lane (default) | Oracle lane (opted in) | Expected |
|---|---|---|---|
| RP2 | `uv run pytest -q tests/test_rp2_anchored.py tests/test_pyrel_rules.py tests/test_pyrel_rules_families.py tests/test_pyrel_rules_derivations.py tests/test_rules_in_pyrel.py tests/test_pyrel_export.py tests/test_pyrel_export_boundaries.py tests/test_ossie_formulas.py tests/test_ossie_export.py --tb=short` | `uv run pytest -q -m pyrel_oracle tests/test_rp2_anchored.py tests/test_pyrel_rules.py tests/test_pyrel_rules_families.py` | exit 0 |
| RP1 | the same with `tests/test_rp1_external_uniqueness.py` in place of the RP2 file, plus `tests/test_rp2_anchored.py` | the same files under `-m pyrel_oracle` | exit 0 |
| RP3 | the same with `tests/test_rp3_number.py` added | the same under `-m pyrel_oracle` | exit 0 |
| RP4 | the same with `tests/test_rp4_role_value.py` added | the same under `-m pyrel_oracle` | exit 0 |
| RP5 | the same with `tests/test_rp5_literature_rules.py` added | the same under `-m pyrel_oracle` | exit 0 |
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
| D4 | RP1: how the programs type an entity identified only by an external uniqueness, such as `assertion` | the type of the identifier its population rows carry | `String`, decided from the model, never from a population. GND admits any scalar there (§1); a non-string value is refused by name with exit 3, a stated input refusal under §0 `(p1)` |
| D5 | RP2: when the LQP program lists a must-rule as not checked and the engine reports no violation, does it exit 0 or 4 | (new in r2) | 4, as the DuckDB program and `gnd check` do; fixed at the RP2 spec and tested by RP2-C7 `(p1)`. A deontic not-checked rule keeps the band `(p2)` |
| D6 `(p1)` | RP3: integers beyond 2**53 in a `Number` or `Float` role, which a binary float cannot hold exactly | (new in r3) | refuse by name with exit 3, for `Float` as well as `Number`: the `Float` gap predates this milestone and the same bound closes both. `(p2)` The model's own constants in those types are refused at export the same way |

Open questions carried into the phases:

| Question | Owner |
|---|---|
| Exact part name and witness shape for the external-uniqueness join listing | RP1 spec |
| `(p1)` GND's exact reason text for disconnected and ambiguous joins, and the anchored reason text | RP2 and RP1 specs, measured |
| Which program-text goldens and pinned strings move when the not-checked line changes | RP2 spec, measured |
| Whether a bare top-level `anchored` constraint validates; whether GND scopes a fact-scoped value constraint without `role_ref` to the object type | RP2 and RP4 specs, by test |
| The lqp program gives textual rules no not-checked line today (`_LQP_MAIN`, `pyrel_rules.py:2057-2126`); RP2 fixes it for both kinds | RP2 |

## 11. Close amendments (2026-11-22)

Plan repairs deferred to the close. Each names the record that raised it; the
r4 wording above is kept as written.

| # | Section, prior wording kept | Amendment | Raised by |
|---|---|---|---|
| A1 | §2 RP1, "anchors matched by object type" | across fact types, by object type; within one fact type, by role, because GND projects one fact type (`semantic_spec.role_sequence_rows`) | `003-phase-RP1.md`, implementation finding 1; spec `(p3)` |
| A2 | §1 and RP1-C6, disconnected join "vacuous when its lists are empty" | vacuous only when **every** referenced list is empty; one empty list still gives unchecked (exit 4). The DuckDB version reads the computed view of semiderived types; the LQP version always lists it as not checked | `003-phase-RP1.md` (finding 1, review r1-F2, boundary) |
| A3 | §0 "Same verdict on accepted inputs" | repeated facts include rows equal by GND's numeric identity (`1`, `1.0`), refused like other repeats; a non-finite number is refused in every cell, roster and plan binding; an LQP program returns 3 for a population it cannot read | `003-phase-RP1.md`, review r1-F1, r1-F3, r2-F2, r3-F1 |
| A4 | §10 D6, "integers beyond 2**53 in a Number or Float role … model constants" | the bound also covers reference facts, constants at any depth, arithmetic next to a Float or Number value (refused), and what a derivation writes into a Float or Number head (a sum over or into one is refused; an Integer value written into one is refused) | `004-phase-RP3.md`, review r1–r5 |
| A5 | §0 "Ossie export unchanged" | holds; RP4 needed one Ossie line to keep it (fact-scoped value rules stay extensions) | `005-phase-RP4.md`, review r1-F2 |
| A6 | §2 RP4 | universes (`<type>_any`) are recorded where the lowering creates them, plan creates included, so a fact type named like one is read as itself or refused by name | `005-phase-RP4.md`, review r2–r4 |
| A7 | §5, the runtime page | several older statements were narrowed to match the code: DuckDB-only reporting, plans on DuckDB only, exclusive-or over multi-role sequences, disconnected guarded antecedents, exit 4 when no rule is violated | `006-phase-RP5.md`, review r1–r3 |

Open questions of §10, swept:

| Question | Disposition |
|---|---|
| Part name and witness shape for the join listing | resolved (RP1 spec §6.1): part `join`; witness the distinct referenced tuples in `role_refs` order |
| GND's reason texts (disconnected, ambiguous, anchored) | resolved: ambiguous is an invalid model at load (exit 3); disconnected and anchored reasons as printed in `docs/runtimes/pyrel.md` |
| Program-text goldens moved by the not-checked line | resolved (RP2): textual lines byte-identical; RP4's comparison shows 573 accepted programs unchanged |
| Bare top-level `anchored`; fact-scoped value without `role_ref` | resolved: the first does not validate (RP2 spec); the second covers the universe, as GND (RP4) |
| LQP textual rules had no not-checked line | resolved (RP2, `not_checked()`) |
