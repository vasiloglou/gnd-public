# Rule-check adoption

r2, 2026-11-06. **Draft, awaiting the owner's plan gate. No plan review has
run over these bytes** (§8 names the bar; whether to run it or waive it is
RC-D0). Milestone: `rule-check-adoption`. Phase prefix `RC`.
Sources: five owner-filed requests from 2026-11-06, GR-D1, GR-D2, GR-D3, GR-D5
and GR-D6 (GitHub issues 92, 93, 94, 96 and 97). GR-D4 (issue 95, model
composition) is excluded by the owner's selection relayed to this planning
session on 2026-11-06 ("Plan a milestone" on a proposal that put D1, D2, D3,
D5 and D6 in one milestone and D4 in its own). It approves no bytes.
Inspection baseline: main at `33d1db49`. PR 99 (open) repairs 24 failing
tests on main; RC1's focused gate runs after that PR merges or names the
pre-existing failures it inherits (RC-D1).
Plan authorship is not approval. No phase has a spec approval; no code is
written. `auto=false`.

**Revision history and owner rulings.**

- **r1:** first draft. No review has run over it.
- **r2:** after merging `origin/main` 8bfbe417 (PR 100, the component index
  and the project rule that requires searching it). Reuse findings O16-O17;
  version-15 verdicts carry `address` + `addressing` (existing census scheme)
  instead of a bare `constraint_id`; RC-D4 is answered by that scheme. No
  review has run over r2.

## Problem and completion predicates

A development tool (a caller outside this repository) exports a project's
component catalog and import graph as a population and runs `gnd check`
against rules the project owner writes. On its first project (209
components, 2,047 import edges) the check ran in 2.5 seconds. Five things
stop it from being a CI gate a project can switch on:

1. A verdict names its rule by position (`constraints[3]`), never by the
   `id` the author wrote, and carries no author text saying what to do.
2. An existing project starts with violations (791 and 18 on that project),
   and there is no way to fail only on the ones a change adds.
3. `ring` `variant: acyclic` reports one cycle; the same facts hold 8 groups of
   mutually reachable components (sizes 90, 19, 13, 7, 3, 3, 2, 2). Which
   cycle is named depends on traversal order, so two runs cannot be compared.
4. A rule shipped ahead of the data it will judge is `vacuous` and the run
   exits 2, so the caller stops trusting the exit band.
5. A population read from source code by a deterministic tool must call
   itself `fixture`.

The milestone is complete when, on the main branch after merge:

1. `gnd check MODEL POP --rule-ids --format json` emits report version 15,
   whose verdicts carry `address`, `addressing` and `remedy` (RC1). Version 7 bytes
   are unchanged for every existing input.
2. Under version 15, an `acyclic` failure lists every fact that lies inside a
   strongly connected group, independent of traversal order (RC2).
3. `gnd check MODEL HEAD --baseline BASE` marks every offending row `new` or
   `standing`, decides the band from new rows only, and refuses to claim "no
   new violations" when either run is ill-formed or undecided (RC3).
4. `gnd check ... --allow-vacuous` exits 0 when the only shortfall is vacuous
   verdicts, and still lists them (RC4).
5. A population may declare a source for deterministic tool output (RC5).
6. The rule-check workflow is documented end to end, with a worked example
   that runs (RC6).
7. Each phase has an approved spec, a record with verbatim focused-gate
   output, and an independent review; the close record disposes every open
   question.

## 0. Binding design rules

The project's six standing design rules
([project.md](../../../../.codex/skills/process-phase/references/project.md))
bind every phase. Bound to this milestone:

1. **Totality.** `--baseline` reads a second untrusted population; its loader
   is the existing population loader with its caps, never a new reader (RC3).
   `remedy` is untrusted model text and reaches the payload only through
   `json.dumps` (RC1).
2. **Input cap bounds the algorithm.** RC2's group computation is linear
   (Tarjan or Kosaraju over the pairs); RC3's comparison is a set difference
   over canonical keys, linear in rows. Each ships a time-bound test.
3. **Validation order.** With `--baseline`, the order is: arguments (64),
   model load (3), head population load (3), base population load (3, naming
   the base), then evaluation. Pinned by a source-order test (RC3).
4. **One walk.** Declared identity is attached by one walk over the model's
   constraints (`ModelIndex.iter_constraints()`) keyed by `constraint_ref`, not by threading a field through the
   seven `ConstraintVerdict(...)` construction sites (RC1). The baseline key
   is one function over every family's offending row (RC3).
5. **One home.** The version-15 shape has one home, `src/gnd/report.schema.json`;
   the `remedy` field has one home, `orm-meta.schema.json` and its sync-pinned
   skill copy; the population source enum has three spellings today (schema,
   `population.py` `Literal`, `extract/projection.py`) and RC5 makes one yield.
6. **Measure contested questions.** RC2's row shape (group vs edge) and RC3's
   key are settled on the 209-component data shape reproduced as a synthetic
   fixture, not by argument.

Milestone-specific rule:

7. **Frozen variants stay frozen.** Version 7 and every other existing report
   variant keep their bytes. New meaning goes in version 15 only. A golden
   that moves outside version 15 is a defect.

## 1. Scope, sources and authority

| Source | What it gives |
|---|---|
| Issue 92 (GR-D1) | rule id and author message in each verdict |
| Issue 93 (GR-D2) | baseline comparison, band from new violations |
| Issue 94 (GR-D3) | full extent of an acyclic violation |
| Issue 96 (GR-D5) | accept vacuous verdicts |
| Issue 97 (GR-D6) | population source value for tool-extracted facts |
| Owner selection 2026-11-06 | D4 excluded; this milestone plans the other five |

### Obligations harvested

Observed = read or run at `33d1db49` during planning. Claim = stated by the
requester and not reproduced here.

| # | Obligation | Evidence | Kind | Phase |
|---|---|---|---|---|
| O1 | verdict carries declared constraint `id` | probe: v7 verdict has only `constraint_ref: "fact_types[component_uses_component].constraints[0]"` for a constraint declared `id: no_import_loops` | observed | RC1 |
| O2 | author-written fix text copied into the verdict | `constraint_common` in `src/gnd/schema/orm-meta.schema.json` has `rationale`, no field for what to do; unknown keys are refused (`unevaluatedProperties`) | observed | RC1 |
| O3 | v7 verdict shape is closed | `$defs.verdict` in `src/gnd/report.schema.json`: `additionalProperties: false`, nine required keys | observed | RC1 |
| O4 | ids are a stable key | `gnd validate` refuses a duplicate constraint id across the model (`semantic:id-unique`), probe | observed | RC1, RC3 |
| O5 | acyclic reports one cycle | `_ring_component_violations`, `src/gnd/checker/_core.py:1376-1378`; probe with a 2-cycle and a 3-cycle reported only `['a','b','a']` | observed | RC2 |
| O6 | other ring variants list every offender | same function, lines 1340-1375 | observed | RC2 |
| O7 | new/standing per offending binding, keyed by rule and values | issue 93 | claim | RC3 |
| O8 | band from new violations only | issue 93 | claim | RC3 |
| O9 | stated outcome when either run is ill-formed or undecided | issue 93 | claim | RC3 |
| O10 | v7 offending rows hold values; later versions name `{fact_type, index}` | `fact_ref_v10` in report schema; issue 93 | observed (schema) | RC3 |
| O11 | vacuous exits 2 | `band()`, `src/gnd/checker/_reports.py:146-168` | observed | RC4 |
| O12 | vacuous acceptance reported, not hidden | issue 96 | claim | RC4 |
| O13 | source enum is `agent-output`, `synthetic`, `fixture` | `src/gnd/schema/population.schema.json:18`, `src/gnd/population.py:131`, `src/gnd/extract/projection.py:278` | observed | RC5 |
| O14 | optional note naming tool and revision | issue 97 | claim | RC5 |
| O16 | declared-id-else-positional addressing already exists | `model.address` (`Addressing`, `constraint_address`, `src/gnd/address.py`); `coverage._constraint_address` (`src/gnd/coverage.py:735`); `ModelIndex.iter_constraints()` (`src/gnd/model_index.py:279`) | observed (index search) | RC1 |
| O17 | no strongly-connected-group or two-report comparison exists | index searches `strongly connected graph cycle`, `compare two check reports baseline`, `diff violations between populations`: only `model.diff` (two models, not two populations) | observed (index search) | RC2, RC3 (new) |
| O15 | 2,047 edges / 209 components checked in 2.5 s | issue 94/92 | claim | RC2, RC3 time bounds |

## 2. Contract proposal and product behavior

### 2.1 Declared identity: report version 15 (RC1)

- New optional constraint field `remedy` (string) in `constraint_common`.
  It is author text saying what to do; `rationale` stays the reason the rule
  exists.
- New report version 15: the version-7 snapshot shape, with three more
  required verdict keys: `address` (`constraint:<id>`, else the positional
  ref), `addressing` (`declared-id` or `positional`, the census's existing
  spelling) and `remedy` (string or null). Selected by `--rule-ids` on the plain snapshot arm.
- Text output under `--rule-ids` prints the id before the positional ref.
- Models with an active redaction policy or temporal terms re-project to
  versions 10/13 (`_project_result` in `src/gnd/checking_service.py`);
  `--rule-ids` refuses them in this milestone (RC1 D3).
- `--rule-ids` with `--populations`, `--pre/--steps/--post`, `--anchors`,
  `--composition` or `--admission` exits 64 in this milestone.

### 2.2 Acyclic extent (RC2)

Under version 15 only, a failing `acyclic` verdict's `offending_facts` lists
every pair that lies inside a strongly connected group, sorted, and its
message names the number of groups and their sizes. Version 7 keeps the
single cycle (rule 7). Row shape is RC-D3.

### 2.3 Baseline (RC3)

`gnd check MODEL HEAD --baseline BASE` (implies `--rule-ids`). Both
populations are judged under MODEL. A violation key is
`(address, canonical JSON of the offending row)`; a positional address is
flagged by its `addressing`.
Each version-15 verdict gains an aligned `novelty` list (`new` or
`standing`); a top-level block names the baseline and counts new, standing
and resolved rows. Band 1 needs a new alethic row. Exact band and outcome
when only standing violations remain, and when either run is undecided,
are RC-D5 and RC-D6.

### 2.4 Vacuous acceptance (RC4)

`--allow-vacuous` (run-wide) moves band 2 to 0 when vacuous verdicts are the
only shortfall. Verdicts and counts are unchanged; the payload records that
the option was used. Per-constraint control is RC-D7.

### 2.5 Source for tool output (RC5)

A fourth `population.source` value for facts a deterministic program
produced, with an optional note. Spelling is RC-D8: `extracted` collides
with `gnd extract`, whose outputs are `agent-output`.

## 3. Dependencies and artifact homes

```
RC1 ──> RC2 ──> RC3 ──> RC6 ──> close
RC4 ─────────────────────^
RC5 ─────────────────────^
```

RC2 needs version 15 to put a new meaning somewhere (rule 7). RC3 needs
stable ids (RC1) and order-independent acyclic rows (RC2). RC4 and RC5 are
independent and may run in any order.

| Artifact | Home |
|---|---|
| `remedy` field | `src/gnd/schema/orm-meta.schema.json` + sync-pinned copy in `src/gnd/skills/gnd-orm-core/references/` |
| version-15 shape | `src/gnd/report.schema.json` |
| declared address | `src/gnd/address.py` (`declared_constraint_address`, moved from `coverage.py`) |
| group computation | `src/gnd/checker/_core.py`, beside `_find_cycle` |
| baseline comparison | new module under `src/gnd/checker/` (RC3 spec), layered per `tools/gnd_layers.json` |
| CLI flags | `src/gnd/commands/checking.py` |
| population source | `src/gnd/schema/population.schema.json` (+ skill copy), `src/gnd/population.py` |

## 4. Phases, deliverables, named criteria and inherited residuals

### RC1: Declared identity, report version 15 (about 180 source, 350 test lines)

- RC1-C1: `remedy` accepted by `gnd validate`; non-string refused (exit 3).
- RC1-C2: `--rule-ids` emits v15; every verdict has `address`,
  `addressing` and `remedy` (null when undeclared); fact-type and top-level constraints both
  covered.
- RC1-C3: without `--rule-ids`, output bytes for the rf1 sem-check goldens are
  unchanged.
- RC1-C4: `--rule-ids` with any other arm exits 64.
- RC1-C5: the v15 payload validates against `report.schema.json`.

### RC2: Acyclic extent (about 60 source, 200 test lines)

- RC2-C1: two disjoint cycles both appear; a pair outside every group does
  not.
- RC2-C2: rows are identical under permuted fact order.
- RC2-C3: version 7 output for the same input is unchanged.
- RC2-C4: time bound over 2,000+ edges.

### RC3: Baseline (about 300 source, 500 test lines)

- RC3-C1: a violation in both runs is `standing`; only in head is `new`;
  only in base is counted resolved.
- RC3-C2: the band follows the RC-D5 ruling; standing-only does not exit 1.
- RC3-C3: base ill-formed exits 3 naming the base; an undecided alethic
  verdict in either run never yields "no new violations".
- RC3-C4: key survives inserting a rule above another and inserting a fact
  above another.
- RC3-C5: validation order pinned; time bound over 2,000+ rows.
- Harvest item for the RC3 spec: survey every snapshot family's v7
  offending-row shape and confirm each is values only.

### RC4: Vacuous acceptance (about 50 source, 150 test lines)

- RC4-C1: vacuous-only run exits 0 with the option, 2 without.
- RC4-C2: a fail or alethic unchecked still decides the band.
- RC4-C3: the payload records the option; vacuous verdicts still listed.

### RC5: Tool-output source (about 30 source, 80 test lines)

- RC5-C1: the new value loads; the optional note is a bounded string.
- RC5-C2: the three spellings of the enum reduce to one home (rule 5).

### RC6: Documentation (docs only)

Constraint reference (`remedy`), report reference (version 15, `novelty`),
population format (source), CLI help, and a how-to: adopting rules on
existing data with `--baseline`, worked on a synthetic component graph that
runs under `tests/test_documentation_tutorials.py` (exact gate unresolved until the RC6 spec).

### Milestone close (not a feature phase)

Close record under the milestone record format; question sweep; plan-review
bar per §8.

### Obligation-to-phase map

O1-O4, O16 → RC1; O17 → RC2, RC3; O5-O6 → RC2; O7-O10 → RC3; O11-O12 → RC4; O13-O14 → RC5;
O15 → RC2 and RC3 time bounds. Every row has an owner.

## 5. Documentation, skill and compatibility surfaces

- Report versions 3-14 keep their bytes (rule 7).
- `gnd-orm-core` references: constraint reference, population format and the
  two sync-pinned schemas.
- `gnd-extract` keeps writing `agent-output`; RC5 does not change it.
- CLI help for `check` gains three flags.

## 6. Risks and required controls

| Risk | Control |
|---|---|
| A v7 golden moves | RC1-C3 / RC2-C3 byte checks over the rf1 sem-check goldens |
| Baseline key unstable for some family | RC3 family survey; RC3-C4 |
| "No new violations" read from a run that did not judge | RC3-C3 and RC-D6 |
| Band rule duplicated in a new caller | RC3/RC4 extend `band()`, the one implementation |
| Allow-vacuous hides a rule that should bite | RC4-C3; option recorded in payload |
| Enum spellings diverge | RC5-C2 |
| Redacted values make a baseline key meaningless | `--rule-ids` (and so `--baseline`) refuses redaction-policy models |

## 7. Out of scope

- GR-D4 model composition (issue 95): its own milestone.
- Version-15 variants for batch, transition, anchors, composition, admission,
  redaction-policy and temporal models.
- Per-constraint vacuous control, unless RC-D7 rules it in.
- Changing `gnd extract` or any packaged skill's workflow.

## 8. Execution, approval and review protocol

`auto=false`. Each phase: spec, owner gate, implementation, focused gate,
one independent reviewer in a different tool, refactoring review, record,
commit on a topic branch, PR. Merge is the owner's. The plan-review bar is
the maintained panel (project.md); it has not run over r1 (RC-D0).

## 9. Per-phase verification story

| Phase | Focused gate (exact files fixed in each spec) | Affected consumers |
|---|---|---|
| RC1 | `uv run pytest -q tests/test_rc1_*.py tests/test_schema_sync.py tests/test_checker_families.py tests/test_rf1_semantic_pins.py` | 28 rf1 sem-check goldens, report schema tests |
| RC2 | RC2 tests + `tests/test_ring_frozen.py tests/test_v6_phase2_ring.py` | pyrel ring expected.json (must not move) |
| RC3 | RC3 tests + RC1/RC2 tests | `tests/test_exp_bands.py` |
| RC4 | RC4 tests + band tests | assurance decision tests |
| RC5 | RC5 tests + `tests/test_schema_sync.py` | extract projection tests |
| RC6 | unresolved; candidate `tests/test_documentation_tutorials.py` | — |

### Implementability sweep (author inspection, not review)

- Every input exists at `33d1db49`; nothing waits on another milestone.
- No new dependency: SCC is stdlib-implementable.
- Report version 15 is free (schema enumerates 3-14).
- All exit outcomes are measurable on synthetic fixtures; no paid tool, no
  reserved lane.

## 10. Owner decisions and open questions

All are proposals until ruled.

| ID | Question | Proposal |
|---|---|---|
| RC-D0 | Run the panel over r1, or waive it as for type-induction-skills? | owner's call |
| RC-D1 | RC1 gate before or after PR 99 merges? | after; otherwise name the 24 inherited failures |
| RC-D2 | New version 15 behind a flag, or put the new keys in v7? | v15 behind `--rule-ids`; v7 is closed and frozen |
| RC-D3 | Acyclic rows: one per group, or one per in-group edge? | per edge: matches other ring variants and gives a finer baseline key; groups go in the message |
| RC-D4 | Constraint without an id under `--baseline` | answered by the reused scheme: key by positional address, `addressing: positional` tells the caller it is unstable |
| RC-D5 | Band and outcome when only standing violations remain | exit 0, outcome `accepted`, `acceptance_ready: false`, counts show standing |
| RC-D6 | Outcome when either run leaves an alethic constraint unchecked | exit 4; no novelty claim for that constraint |
| RC-D7 | Vacuous control: run-wide flag, per-constraint field, or both | flag only: a CI adoption choice, not a domain fact |
| RC-D8 | Spelling of the new source value | `tool-output`, with optional `producer` note; avoid `extracted` |
