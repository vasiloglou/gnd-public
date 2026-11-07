# Rule-check adoption

r6, 2026-11-06. **Draft, awaiting the owner's plan gate. r6 has not been
reviewed.** r2 (SHA-256 `526d2ff1…610d631f`) was reviewed by the full panel
([record](../001-panel.md)); r3 (`f00ffcf3…a59e`) by one reviewer, Codex
([record](../002-review.md)), per the owner's RC-D0 ruling; r4
(`a69e3d3b…15f2`) re-checked by Codex ([record](../003-review.md)) per
RC-D14; r5 (`e8a3a154…0a31`) re-checked by Codex
([record](../004-review.md)) per RC-D15. r6 repairs r5 and carries no
review opinion. Milestone: `rule-check-adoption`.
Phase prefix `RC`.
Sources: five owner-filed requests from 2026-11-06, GR-D1, GR-D2, GR-D3, GR-D5
and GR-D6 (GitHub issues 92, 93, 94, 96 and 97). GR-D4 (issue 95, model
composition) is excluded by the owner's selection relayed to this planning
session on 2026-11-06 ("Plan a milestone" on a proposal that put D1, D2, D3,
D5 and D6 in one milestone and D4 in its own). It approves no bytes.
Inspection baseline: main at `33d1db49`, re-read after merging `origin/main`
8bfbe417. PR 99 (open) repairs 24 failing tests on main; RC1's focused gate
runs after that PR merges or names the pre-existing failures it inherits
(RC-D1), recorded at the merge base before any RC1 change (§8).
Plan authorship is not approval. No phase has a spec approval; no code is
written. `auto=false`.

**Revision history and owner rulings.**

- **r1:** first draft. Not reviewed.
- **r2:** after merging `origin/main` 8bfbe417 (PR 100, the component index
  and the project rule that requires searching it). Reuse findings O16-O17;
  version-15 verdicts carry `address` + `addressing` (existing census scheme)
  instead of a bare `constraint_id`. Reviewed by the full panel, six of six
  (three `block`, three `revise`).
- **r3:** repairs r2 from the panel's 22 fixes (F1-F22 in
  [PANEL-REVIEW.md](../evidence/plan-review-r2/PANEL-REVIEW.md)). Main
  changes: the version-15 shape is fixed whole in RC1 (F12); RC4 follows RC3
  and records itself in version 15 only (F3, F5); RC3-C4 split by addressing
  (F1); refusal of redaction/temporal models given a criterion and the right
  versions, 9 and 11 (F2); RC-D5 keeps D-08 (F6); numeric time bounds from a
  fixture measured here, and a stop rule (F7); RC2 reuses existing SCC code
  (F16); new decisions RC-D9 to RC-D13. Each fix's disposition is in §11.
  Reviewed by one reviewer (Codex, `block`, 13 findings, all reproduced).
- **r4:** repairs r3 from the 13 findings R1-R13 (dispositions in §12).
  Main changes: version-15 verdict and derivation shapes are separate closed
  definitions (R1); reference-population models are refused too, which also
  removes the only modality-independent band-4 route (R2, R7); novelty is
  split into a verdict-level label and a row-aligned list, and derivations
  get both (R3, R4); the identity walk does not copy (R8); RC2 moves both
  existing SCC callers to the shared home as a criterion (R11). Owner ruling
  recorded: **RC-D0, 2026-11-06, "One reviewer on r3"**. Re-checked by
  Codex (`block`, 4 findings S1-S4, all reproduced; 11 of 13 R findings
  confirmed resolved).
- **r5:** repairs r4 from S1-S4 (dispositions in §13). Owner ruling
  recorded: **RC-D14, 2026-11-06, "Codex re-check r4"**; and on
  2026-11-06, choosing "Commit, r5 with refusal", the owner selected the
  narrower fix for S1: `--baseline` refuses models with structured
  derivations instead of comparing derivation findings (RC-D11). Version-15
  derivations therefore keep the existing `derivation_verdict` definition
  unchanged, which also resolves S2. `producer` is retained by the loader
  (S3); `undecided` counts obligations, not rows (S4). This brings the plan
  back toward the requests: the requester's models have no derivations.
  Re-checked by Codex (`block`, 2 findings T1-T2, both reproduced).
- **r6:** repairs r5 from T1-T2 (dispositions in §14). Owner ruling
  recorded: **RC-D15, 2026-11-06, "Codex re-check r5"**. Version-15
  derivations get their own closed definition again, without novelty
  fields: the version-7 properties and conditional rules, with the
  `reason_code` set widened to every reason the checker emits (T1). While
  reproducing T1 the driving agent found that today's version-7 report
  already fails its own schema for such a model (O29); that is a
  pre-existing defect outside this milestone (rule 7), recorded for the
  owner.

## Problem and completion predicates

A development tool (a caller outside this repository) exports a project's
component catalog and import graph as a population and runs `gnd check`
against rules the project owner writes. On its first project (209
components, 2,047 import edges) the check ran in 2.5 seconds (claim, issue
94). Five things stop it from being a CI gate a project can switch on:

1. A verdict names its rule by position (`constraints[3]`), never by the
   `id` the author wrote, and carries no author text saying what to do
   (issue 92).
2. An existing project starts with violations (791 and 18 on that project,
   claim), and there is no way to fail only on the ones a change adds
   (issue 93).
3. `ring` `variant: acyclic` reports one cycle; the same facts hold 8 groups of
   mutually reachable components (sizes 90, 19, 13, 7, 3, 3, 2, 2; claim,
   issue 94). For one fact set the named cycle is already deterministic
   (`_find_cycle` sorts the pairs, `src/gnd/checker/_core.py:1377`); what
   breaks comparison is that adding or removing an edge anywhere can change
   which cycle is named, so a fix in one group can look like a new violation
   in another.
4. A rule shipped ahead of the data it will judge is `vacuous` and the run
   exits 2, so the caller stops trusting the exit band (issue 96).
5. A population read from source code by a deterministic tool must call
   itself `fixture` (issue 97).

The milestone is complete when, on the main branch after merge:

1. For a model whose plain check report is version 7 and unwrapped (no
   temporal terms, no active redaction policy, no reference populations),
   `gnd check MODEL POP --rule-ids --format json`
   emits report version 15, whose verdicts carry `address`, `addressing` and
   `remedy` (RC1). Other models are refused with a named rule id. Existing
   report variants keep their bytes as far as the full test suite pins them
   (§5).
2. Under version 15, an `acyclic` failure lists every pair that lies inside a
   strongly connected group, and adding a disjoint cycle leaves the existing
   rows unchanged (RC2).
3. `gnd check MODEL HEAD --baseline BASE` marks every offending row, every
   failing verdict `new` or `standing`, decides the band from new ones only,
   and refuses to claim "no new violations" when either run is ill-formed or
   leaves an alethic constraint undecided (RC3). Models with structured
   derivations are refused under `--baseline` with a named rule id.
4. `gnd check ... --allow-vacuous` exits 0 when the only shortfall is vacuous
   verdicts, still lists them, and records the option in version 15 (RC4).
5. A population may declare a source for deterministic tool output (RC5).
6. The rule-check workflow is documented end to end, with a worked example
   that runs under a named test (RC6).
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
   (Tarjan over the pairs); RC3's comparison is a set difference over
   canonical keys, linear in rows; RC1's identity walk copies nothing, so it
   is linear in constraints. Each ships a test with the numbers in §4.
3. **Validation order.** With `--rule-ids` or `--baseline`, the order is:
   arguments (64), model load (3), model refusal `check:rule-ids-unsupported`
   (3; temporal, redaction-policy or reference-population models), with
   `--baseline` only the refusal `check:baseline-unsupported` (3; models
   with structured derivations), head
   population load (3), base population load (3, naming the base),
   then evaluation. Pinned by a source-order test (RC1 for the first four
   steps, RC3 for the base).
4. **One walk.** Declared identity is attached by one walk over the model's
   constraints keyed by `constraint_ref`, through a non-copying sibling of
   `ModelIndex.iter_constraints()` (`iter_constraints_shared()`, same
   contract as the existing `iter_fact_types_shared()`),
   not by threading a field through the seven `ConstraintVerdict(...)`
   construction sites (RC1). The baseline key is one function over every
   family's offending row (RC3).
5. **One home.** The version-15 shape has one home, `src/gnd/report.schema.json`,
   fixed whole in RC1; the `remedy` field has one home, `orm-meta.schema.json`
   and its sync-pinned skill copy; the population source enum has three
   spellings today (schema, `population.py` `Literal`, `extract/projection.py`)
   and RC5 makes the schema normative and the other two derive from it or be
   pinned to it by test. Strongly connected groups get one shared home rather
   than a third copy (RC2, RC-D10).
6. **Measure contested questions.** RC2's row shape (group vs edge) and RC3's
   key are settled on the synthetic 209-component fixture (§9), not by
   argument.

Milestone-specific rules:

7. **Frozen variants stay frozen.** Every existing report variant (versions
   3-14) keeps its bytes. New meaning goes in version 15 only. A golden or
   pinned test that moves outside version 15 is a defect. Gate: RC1, RC2,
   RC3 and RC4 each run the full suite and compare it with the merge-base
   record (§8).
8. **Stop rule.** A phase returns to its owner gate, with work paused, when
   its source or test lines pass 1.5 times the §4 estimate, when a harvest
   survey contradicts an assumption of this plan (for example RC3's family
   survey finds a v7 offending row that is not values only), or when a time
   bound in §4 fails and cannot be met without a design change.

## 1. Scope, sources and authority

| Source | What it gives |
|---|---|
| Issue 92 (GR-D1) | rule id and author message in each verdict |
| Issue 93 (GR-D2) | baseline comparison, band from new violations |
| Issue 94 (GR-D3) | full extent of an acyclic violation |
| Issue 96 (GR-D5) | accept vacuous verdicts |
| Issue 97 (GR-D6) | population source value for tool-extracted facts |
| Owner selection 2026-11-06 | D4 excluded; this milestone plans the other five |
| Panel over r2 | 22 advisory fixes; dispositions in §11 |

### Obligations harvested

Observed = read or run during planning at `33d1db49` / 8bfbe417. Claim =
stated by the requester and not reproduced here.

| # | Obligation | Evidence | Kind | Phase |
|---|---|---|---|---|
| O1 | verdict carries declared constraint `id` (issue 92) | probe: v7 verdict has only `constraint_ref: "fact_types[component_uses_component].constraints[0]"` for a constraint declared `id: no_import_loops` | observed | RC1 |
| O2 | author-written fix text copied into the verdict (issue 92) | `constraint_common` in `src/gnd/schema/orm-meta.schema.json` has `rationale`, no field for what to do; unknown keys are refused (`unevaluatedProperties`) | observed | RC1 |
| O3 | v7 verdict shape is closed (issue 92) | `$defs.verdict` in `src/gnd/report.schema.json`: `additionalProperties: false`, nine required keys | observed | RC1 |
| O4 | ids are a stable key (issues 92, 93) | `gnd validate` refuses a duplicate constraint id across the model (`semantic:id-unique`), probe | observed | RC1, RC3 |
| O5 | acyclic reports one cycle (issue 94) | `_ring_component_violations`, `src/gnd/checker/_core.py:1376-1378`; probe with a 2-cycle and a 3-cycle reported only `['a','b','a']` | observed | RC2 |
| O6 | other ring variants list every offender (issue 94) | same function, lines 1340-1375 | observed | RC2 |
| O7 | new/standing per offending binding, keyed by rule and values | issue 93 | claim | RC3 |
| O8 | band from new violations only | issue 93 | claim | RC3 |
| O9 | stated outcome when either run is ill-formed or undecided | issue 93 | claim | RC3 |
| O10 | v7 offending rows hold values; later versions name `{fact_type, index}` | `fact_ref_v10` in report schema; issue 93 | observed (schema) | RC3 |
| O11 | vacuous exits 2 | `band()`, `src/gnd/checker/_reports.py:146-168` | observed | RC4 |
| O12 | vacuous acceptance reported, not hidden | issue 96 | claim | RC4 |
| O13 | source enum is `agent-output`, `synthetic`, `fixture` | `src/gnd/schema/population.schema.json:18`, `src/gnd/population.py:131`, `src/gnd/extract/projection.py:278` | observed | RC5 |
| O14 | optional note naming tool and revision | issue 97 | claim | RC5 |
| O15 | 2,047 edges / 209 components checked in 2.5 s | issues 92, 94 | claim | RC2, RC3 time bounds |
| O16 | the pieces of declared-id-else-positional addressing exist, unjoined | `src/gnd/address.py`: `Addressing` and `constraint_address(id) -> "constraint:<id>"` (no fallback); `coverage._constraint_address` (`src/gnd/coverage.py:735`, private): declared address, else positional; `ModelIndex.iter_constraints()` (`src/gnd/model_index.py:279`): the walk yielding positional refs. No public function joins them | observed (index search, read) | RC1 |
| O17 | no two-population comparison exists; strongly connected components are computed twice already | index searches `compare two check reports baseline`, `diff violations between populations`: only `model.diff` (two models). SCC: iterative Tarjan in `src/gnd/model/_validation.py:4499` and `src/gnd/export/pyrel_rules.py:688` | observed (index search, read) | RC2 (reuse), RC3 (new) |
| O18 | report-version gates that a new version must pass | `ReportSchemaVersion = Literal[3, …, 11, 13]` (`src/gnd/payloads.py:76`); `schema_version in {7, 8}` branches in `payloads.py`; `coverage._accepted_schema_versions` (`src/gnd/coverage.py:436`) accepts 7, 9, 10 for check evidence | observed | RC1 |
| O19 | `acceptance_ready` is true exactly when exit code is 0 (D-08) | `report.schema.json` description; `payloads.py` sets `exit_code == 0` | observed | RC3 |
| O20 | derivation failures decide band 1 alongside alethic verdicts | `has_alethic_fail`, `src/gnd/checker/_reports.py:110-113` | observed | RC3 (refused, RC-D11) |
| O26 | a derivation reports only its first missing and first surplus row | `src/gnd/extensions.py:2465-2505` | observed (Codex S1, reproduced) | RC3 (refused, RC-D11) |
| O27 | `Population` has no `producer` field; both constructors drop unknown header values | `src/gnd/population.py:123-139`, `453-464`, `485-495` | observed (Codex S3, reproduced) | RC5 |
| O28 | a deontic `opaque-value` unchecked verdict has no rows | `src/gnd/correspondence.py:927-928` | observed (Codex S4, reproduced) | RC3 |
| O29 | today's version-7 report fails its own schema when a derivation is unchecked with a `term:*` reason: the v7 branch types derivations as `derivation_verdict`, whose `reason_code` admits three values | probe 2026-11-06: `tests/fixtures/v62-phase3/models/exact-terms.orm.yaml` with `redact: true` removed, `gnd check --format json` → schema_version 7, exit 4, `term:mod-zero` derivations, 1 validation error, gone when those reasons are replaced | observed (Codex T1, reproduced) | out of scope (rule 7); RC1 avoids it in v15 |
| O22 | reference-population models wrap the check report as version 12 (14 for admission), whose `report` admits only existing report shapes | `_reference_wrap`, `src/gnd/checking_service.py:594-663`; `report.schema.json:85-93` | observed (Codex R2, reproduced) | RC1 |
| O23 | band 4 for `reference-join-work-limit` regardless of modality; reachable only with reference populations | `src/gnd/checker/_reports.py:159-163`; `src/gnd/checker/_core.py:2379` | observed (Codex R7, reproduced) | RC1 (refusal), RC3 |
| O24 | `iter_constraints()` deep-copies the fact type per constraint | `src/gnd/model_index.py:279-285` | observed (Codex R8, reproduced) | RC1 |
| O25 | text output renders the internal `CheckReport`, not the payload | `src/gnd/commands/checking.py:273-276` → `_print_report`, `src/gnd/output.py:167` | observed (Codex R10, reproduced) | RC1 |
| O21 | measured size: the synthetic fixture (§9) checks in 0.89-1.15 s wall clock, 3 runs, including interpreter start | `gnd check` on the planning machine, 2026-11-06 | observed | RC2, RC3 time bounds |

## 2. Contract proposal and product behavior

### 2.1 Declared identity: report version 15 (RC1)

- New optional constraint field `remedy` (string, 1-2000 chars) in
  `constraint_common`. It is author text saying what to do; `rationale` stays
  the reason the rule exists. A constraint without `remedy` yields
  `remedy: null`; `rationale` is not copied in its place (RC-D12).
- New report version 15: the version-7 snapshot shape, fixed whole in RC1 so
  no later phase changes a closed shape (F12). Its verdicts use a new
  closed definition, `verdict_v15`, that restates the version-7 properties,
  as `verdict_v10` does, rather than referencing the closed version-7
  object (R1). Its derivations use `derivation_verdict_v15`: the
  version-7 `derivation_verdict` properties and pass/fail/unchecked
  conditional rules restated, with `reason_code` admitting every reason the
  checker emits (`DerivationReason`, `src/gnd/extensions.py:55-67`; the
  same set `derivation_verdict_v10` admits), and no novelty field
  (RC-D11, S2, T1). Each verdict gains
  `address` (`constraint:<id>`, else the positional ref), `addressing`
  (`declared-id` or `positional`, the census's existing spelling), `remedy`
  (string or null), `novelty` (verdict label: `new`, `standing` or null)
  and `row_novelty` (null, or a list aligned one-to-one with
  `offending_facts`) (R3). The top
  level gains `baseline` (`null` without `--baseline`) and `allow_vacuous`
  (boolean). Without `--baseline` every novelty field is null. RC3 and RC4
  fill values; they add no key.
- Selected by `--rule-ids` on the plain snapshot arm. `--baseline` and
  `--allow-vacuous` imply it.
- Text output under `--rule-ids` prints the address before the positional
  ref and, when present, the remedy on an indented line. The text renderer
  (`_print_report`, `src/gnd/output.py`) receives the identity map; its
  output without the flag is pinned unchanged (R10).
- `--rule-ids` refuses, at exit 3 with issue rule id
  `check:rule-ids-unsupported`, any model whose plain report is not an
  unwrapped version 7: a model using temporal terms (version 11) or with an
  active redaction policy (version 9), as selected by
  `current_payload_schema_version` (`src/gnd/payloads.py:735`), or a model
  with reference populations, whose report is wrapped as version 12 (O22).
  The refusal comes after model load and before population load (rule 3).
  It also makes `reference-join-work-limit` unreachable under version 15
  (O23).
- `--rule-ids` with `--populations`, `--pre/--steps/--post`, `--anchors`,
  `--document`, `--composition`, `--sources` or `--admission` exits 64
  (admission's versions 10 and 13 are reached only through that arm).
- `gnd coverage` does not accept version-15 check reports in this milestone;
  it refuses them through its existing version check (O18), pinned by test.

### 2.2 Acyclic extent (RC2)

Under version 15 only, a failing `acyclic` verdict's `offending_facts` lists
every pair that lies inside a strongly connected group, sorted, and its
message names the number of groups and their sizes. Version 7 keeps the
single cycle (rule 7). Mechanism: the checker's verdict is unchanged; the
version-15 builder computes the extent through one separate function over
the same pairs, so no version-7 code path reads it. Row shape is RC-D3; the
SCC home is RC-D10.

### 2.3 Baseline (RC3)

`gnd check MODEL HEAD --baseline BASE` (implies `--rule-ids`). Both
populations are judged under MODEL. A violation key is
`(address, canonical JSON of the offending row)`.

- **Row novelty.** Each offending row is `new` or `standing`; the verdict's
  `row_novelty` lists them aligned one-to-one with `offending_facts` (empty
  when there are no rows).
- **Verdict novelty (F10, R3).** A failing verdict's `novelty` is `new` when
  any of its rows is new, or, for a failing verdict with no offending rows
  (for example a cardinality minimum over an empty universe), when the same
  address did not fail in base; otherwise `standing`. A verdict with mixed
  rows is therefore `new`. Passing verdicts carry `novelty: null`.
- **Derivations (F13, R4, S1).** `--baseline` refuses a model with
  structured derivations (`structured_derivation_ids(model)` non-empty,
  `src/gnd/documents.py:85`) at exit 3 with `check:baseline-unsupported`,
  after model load and before either population load (RC-D11). A derivation
  reports only its first missing and first surplus row (O26), so comparing
  findings could call a grown violation standing.
- **Band.** Band 1 needs a failing alethic verdict whose `novelty` is
  `new`. Standing-only: RC-D5.
- **Undecided.** An alethic constraint unchecked in either run: RC-D6.
  Deontic unchecked: RC-D13.
- **Vacuous (F5).** Vacuity is judged on head. A head verdict that is
  vacuous keeps band 2 under `--baseline` unless `--allow-vacuous` is given
  (RC4); base vacuous contributes no rows; base fail with head vacuous
  counts the base rows as resolved and the band is 2 (0 with
  `--allow-vacuous`).
- **Id-less constraints (F1).** Their address is positional, so their key
  is stable within one model revision but moves when a constraint is
  inserted above them. RC-D9 decides refuse vs warn.
- The top-level `baseline` block names the base population and its digest
  and counts new, standing, resolved and positional-keyed rows, and
  `undecided` obligations: verdicts unchecked in either run, whatever their
  modality and whether or not they carry rows (S4). Shape fixed in RC1.

### 2.4 Vacuous acceptance (RC4)

`--allow-vacuous` (run-wide, implies `--rule-ids`) moves band 2 to 0 when
vacuous verdicts are the only shortfall. Verdicts and counts are unchanged;
`allow_vacuous: true` in version 15 records it, so no existing variant
changes (F3). Per-constraint control is RC-D7.

### 2.5 Source for tool output (RC5)

A fourth `population.source` value for facts a deterministic program
produced, with an optional note. Spelling is RC-D8: `extracted` collides
with `gnd extract`, whose outputs are `agent-output`.

## 3. Dependencies and artifact homes

```
RC1 ──> RC2 ──> RC3 ──> RC4 ──> RC6 ──> close
RC5 ────────────────────────────^
```

RC2 needs version 15 to put a new meaning somewhere (rule 7). RC3 needs
stable ids (RC1) and edge-stable acyclic rows (RC2). RC4 needs version 15
to record itself (RC1) and follows RC3 because both extend `band()` and the
combined `--baseline --allow-vacuous` outcomes are RC4's tests (F3, F5).
RC5 is independent.

| Artifact | Home |
|---|---|
| `remedy` field | `src/gnd/schema/orm-meta.schema.json` + sync-pinned copy in `src/gnd/skills/gnd-orm-core/references/` |
| version-15 shape (whole) | `src/gnd/report.schema.json` (`verdict_v15`, `derivation_verdict_v15`, `baseline_v15`); `ReportSchemaVersion` and version gates in `src/gnd/payloads.py` |
| identity walk | `ModelIndex.iter_constraints_shared()`, `src/gnd/model_index.py` |
| text rendering | `_print_report`, `src/gnd/output.py` |
| declared address | `src/gnd/address.py`: a new public `declared_constraint_address`, which absorbs the private `coverage._constraint_address` (coverage calls it) and builds on the existing `constraint_address` |
| group computation | shared SCC home per RC-D10 (`tools/gnd_layers.json`), called by the version-15 builder |
| baseline comparison | new module under `src/gnd/checker/` (RC3 spec), layered per `tools/gnd_layers.json` |
| band | `band()`, `src/gnd/checker/_reports.py`, extended by RC3 then RC4 |
| CLI flags | `src/gnd/commands/checking.py` |
| population source | normative `src/gnd/schema/population.schema.json` (+ skill copy); `src/gnd/population.py` `Literal`; `src/gnd/extract/projection.py:278` |

## 4. Phases, deliverables, named criteria and inherited residuals

Time bounds are measured in-process on the synthetic fixture (§9), on the
gate machine, with the bound at about five times the planning measurement.

### RC1: Declared identity, report version 15 (about 230 source, 480 test lines)

- RC1-C1: `remedy` accepted by `gnd validate`; non-string, empty and
  2001-char values refused (exit 3).
- RC1-C2: `--rule-ids` emits v15; every verdict has `address`,
  `addressing`, `remedy` (null when undeclared), `novelty: null` and
  `row_novelty: null`; derivations of a structured model serialize as in
  version 7 and validate against `derivation_verdict_v15`, including an
  unchecked derivation with reason `term:mod-zero`; the top level has
  `baseline: null` and `allow_vacuous: false`; fact-type and top-level
  constraints both covered.
- RC1-C3: without `--rule-ids`, the full suite matches the merge-base record
  (rule 7); the rf1 sem-check goldens are byte-identical.
- RC1-C4: `--rule-ids` with any other arm exits 64 before model load.
- RC1-C5: the v15 payload validates against `report.schema.json`; a v7
  payload with `address` added fails.
- RC1-C6: a temporal model, a redaction-policy model and a
  reference-population model with `--rule-ids` each exit 3 with
  `check:rule-ids-unsupported`, before population load.
- RC1-C7: text output under the flag prints the address and the remedy
  (substring checks on real output); without the flag the text output is
  unchanged.
- RC1-C9: the identity walk over a model with 2,000 constraints in one fact
  type takes under 0.5 s and deep-copies no fact type (a patched
  `deepcopy` is never called).
- RC1-C8: `gnd coverage` census addresses are unchanged after the move, and
  `gnd coverage` refuses a version-15 report with its existing message.

### RC2: Acyclic extent (about 120 source, 280 test lines)

- RC2-C1: two disjoint cycles both appear; a self-loop on one node appears
  as its own edge; a pair outside every group does not.
- RC2-C2: adding a disjoint cycle leaves the existing group's rows
  byte-identical (today's single-cycle report fails this).
- RC2-C3: version 7 output for the same input is unchanged; full suite
  matches the merge-base record.
- RC2-C4: the group computation over the fixture's 2,047 edges takes under
  0.5 s.
- RC2-C5: the message names the group count and sizes (90, 19, 13, 7, 3, 3,
  2, 2 on the fixture).
- RC2-C6: the two existing SCC callers (`src/gnd/model/_validation.py`,
  `src/gnd/export/pyrel_rules.py`) call the shared home and keep no Tarjan
  of their own (source scan); their existing tests pass unchanged (R11).

### RC3: Baseline (about 320 source, 550 test lines)

- RC3-C1: a violation in both runs is `standing`; only in head is `new`;
  only in base is counted resolved.
- RC3-C2: standing-only exits 0 with `acceptance_ready: true` and outcome
  per RC-D5, counts showing the standing rows.
- RC3-C3a: `--baseline` with a temporal, redaction-policy or
  reference-population model exits 3 with `check:rule-ids-unsupported`
  before either population loads (R13).
- RC3-C3b: `--baseline` with a model that has a structured derivation exits
  3 with `check:baseline-unsupported` before either population loads; the
  same model with `--rule-ids` alone is accepted (RC-D11).
- RC3-C3: base ill-formed exits 3 naming the base; an alethic verdict
  unchecked in either run never yields "no new violations" (RC-D6); a
  deontic `opaque-value` unchecked verdict with no rows leaves the band
  unchanged and makes `undecided` 1 (RC-D13, S4).
- RC3-C4a: within one model revision, the key survives inserting and
  reordering facts in either population.
- RC3-C4b: across model revisions, a declared-id key survives inserting a
  constraint above it; a test shows a positional key moves, and RC-D9's
  behavior applies.
- RC3-C5: validation order pinned; comparison over 2,000 rows a side takes
  under 0.5 s.
- RC3-C6: a row-less alethic failure new in head exits 1 with
  `novelty: new` and `row_novelty: []`; a verdict with one standing and one
  new row has `novelty: new`; a verdict with only standing rows has
  `novelty: standing` and does not exit 1.
- Harvest item for the RC3 spec: survey every snapshot family's v7
  offending-row shape and confirm each is values only (rule 8 applies).

### RC4: Vacuous acceptance (about 60 source, 200 test lines)

- RC4-C1: vacuous-only run exits 0 with the option, 2 without.
- RC4-C2: a fail or alethic unchecked still decides the band.
- RC4-C3: `allow_vacuous: true` appears in v15; vacuous verdicts still
  listed; without `--rule-ids` the option implies it, and no existing
  variant's bytes change.
- RC4-C4: with `--baseline`: vacuous head (2, or 0 with the option), vacuous
  base (no rows contributed), base fail and head vacuous (rows resolved; 2,
  or 0 with the option).

### RC5: Tool-output source (about 30 source, 80 test lines)

- RC5-C1: the new value loads; the optional `producer` field (string,
  1-200 characters, naming tool and revision) is a retained `Population`
  field, passed through both constructors (O27), and its value is asserted
  after loading; an empty or 201-character `producer`, or `producer` on
  another source, is refused (exit 3).
- RC5-C2: the schema is the one normative spelling; a test fails if
  `population.py` or `extract/projection.py` disagrees with it.

### RC6: Documentation (about 400 doc lines, 60 test lines)

Constraint reference (`remedy`), report reference (version 15, `novelty`,
`baseline`, `allow_vacuous`), population format (source), CLI help, and a
how-to: adopting rules on existing data with `--baseline`, worked on a
synthetic component graph. Gate: `uv run pytest -q
tests/test_documentation_tutorials.py` runs the how-to's commands and
compares their exit codes and key output lines.

### Milestone close (not a feature phase; about 100 record lines)

Close record under the milestone record format; question sweep; full suite
against the merge-base record; plan-review bar per §8.

### Obligation-to-phase map

O1-O4, O16, O18, O22, O24, O25 → RC1; O23 → RC1 (refusal) and RC3; O5-O6, O17 (SCC) → RC2; O7-O10, O17 (comparison),
O19, O20 → RC3; O11-O12 → RC4; O13-O14 → RC5; O15, O21 → RC2 and RC3 time
bounds. Every row has an owner.

## 5. Documentation, skill and compatibility surfaces

- Report versions 3-14 keep their bytes as far as the full suite pins them
  (rule 7). The suite holds dedicated tests for each, among them
  `tests/test_report_json.py` and the rf1 goldens (7),
  `tests/test_v70_phase3_wire.py` (10), `tests/test_v71_phase1_successors.py`
  (11), `tests/test_public_v72_status.py` (13), `tests/test_ring_frozen.py`
  (ring rows).
- `gnd-orm-core` references: constraint reference, population format and the
  two sync-pinned schemas.
- `gnd-extract` keeps writing `agent-output`; RC5 does not change it.
- CLI help for `check` gains three flags.
- `gnd coverage` keeps its accepted versions; v15 is refused (RC1-C8).

## 6. Risks and required controls

| Risk | Control |
|---|---|
| An existing variant moves | rule 7: full suite against the merge-base record in RC1, RC2, RC3, RC4 and close |
| Baseline key unstable for some family | RC3 family survey; RC3-C4a/b; rule 8 |
| Id-less constraints give unstable keys across revisions | RC-D9; `addressing` in each verdict; count in the baseline block |
| "No new violations" read from a run that did not judge | RC3-C3, RC-D6, RC-D13 |
| A grown derivation violation read as standing | `--baseline` refuses derivation models (RC3-C3b, RC-D11) |
| Band rule duplicated in a new caller | RC3 then RC4 extend `band()`, the one implementation, in that order |
| Allow-vacuous hides a rule that should bite | RC4-C3; option recorded in v15 |
| Enum spellings diverge | RC5-C2 |
| Redacted, temporal or reference-wrapped reports make a baseline key meaningless | `--rule-ids` (and so `--baseline`) refuses those models (RC1-C6, RC3-C3a) |
| A third SCC copy | RC-D10 |
| A phase grows past its estimate | rule 8 |

## 7. Out of scope

- GR-D4 model composition (issue 95): its own milestone.
- Version-15 variants for batch, transition, anchors, composition, admission,
  redaction-policy, temporal and reference-population models.
- `--baseline` over models with structured derivations (RC-D11); `--rule-ids`
  alone still covers them.
- `gnd coverage` intake of version-15 reports.
- Per-constraint vacuous control, unless RC-D7 rules it in.
- Changing `gnd extract` or any packaged skill's workflow.

## 8. Execution, approval and review protocol

`auto=false`. Each phase: spec, owner gate, implementation, focused gate,
one independent reviewer in a different tool, refactoring review, record,
commit on a topic branch, PR. Merge is the owner's. Before RC1 changes any
source, the existing-suite part of its gate (`uv run pytest -q
tests/test_schema_sync.py tests/test_checker_families.py
tests/test_rf1_semantic_pins.py tests/test_address.py
tests/test_coverage_payload.py tests/test_report_json.py`) and the full suite
are run at the merge base and recorded verbatim, so inherited failures are
told apart from regressions (RC-D1, R6). The new `tests/test_rc1_*.py` runs
only after RC1 adds it. The plan-review bar is the maintained panel
(project.md); it ran over r2. The owner waived it for r3 in favour of one
reviewer (RC-D0); Codex re-checked r4 (RC-D14) and r5 (RC-D15); r6 is
unreviewed.

## 9. Per-phase verification story

**Fixture.** A synthetic component graph reproducing the request's shape:
209 components, 2,047 `uses` edges, strongly connected groups of sizes 90,
19, 13, 7, 3, 3, 2, 2, the rest acyclic; seeded generator (seed 209)
committed with RC2's tests. Measured during planning (O21): plain `gnd
check` 0.89-1.15 s, exit 1.

| Phase | Focused gate (exact files fixed in each spec) | Affected consumers |
|---|---|---|
| RC1 | `uv run pytest -q tests/test_rc1_*.py tests/test_schema_sync.py tests/test_checker_families.py tests/test_rf1_semantic_pins.py tests/test_address.py tests/test_coverage_payload.py tests/test_report_json.py`; full suite vs merge-base record | rf1 goldens, report schema tests, coverage census |
| RC2 | RC2 tests + `tests/test_ring_frozen.py tests/test_v6_phase2_ring.py`; full suite | pyrel ring expected.json (must not move); the SCC callers under RC-D10 |
| RC3 | RC3 tests + RC1/RC2 tests + `tests/test_exp_bands.py`; full suite | band consumers |
| RC4 | RC4 tests + RC3 tests + band tests; full suite | assurance decision tests |
| RC5 | RC5 tests + `tests/test_schema_sync.py` + extract projection tests | `gnd extract` |
| RC6 | `uv run pytest -q tests/test_documentation_tutorials.py` | — |
| close | full suite vs merge-base record | — |

### Implementability sweep (author inspection, not review)

- Every input exists at 8bfbe417; nothing waits on another milestone.
- No new dependency: SCC code exists twice (O17).
- Report version 15 is free (the schema enumerates 3-14).
- All exit outcomes are measurable on synthetic fixtures; no paid tool, no
  reserved lane.

## 10. Owner decisions and open questions

All are proposals until ruled.

| ID | Question | Proposal |
|---|---|---|
| RC-D0 | Review r3 again (panel or one reviewer), or gate on r2's panel plus these repairs? | **ruled 2026-11-06: "One reviewer on r3"** (done, [002-review](../002-review.md)). Whether r4 is reviewed is RC-D14 |
| RC-D1 | RC1 gate before or after PR 99 merges? | after; otherwise the merge-base record names the inherited failures |
| RC-D2 | New version 15 behind a flag, or put the new keys in v7? | v15 behind `--rule-ids`; v7 is closed and frozen |
| RC-D3 | Acyclic rows: one per group, or one per in-group edge? | per edge: matches other ring variants and gives a finer baseline key; groups go in the message |
| RC-D4 | Constraint without an id under `--baseline` | key by positional address; stability across revisions is RC-D9 |
| RC-D5 | Band and outcome when only standing violations remain | exit 0, `acceptance_ready: true` (D-08 kept), outcome `accepted`; the `baseline` block counts standing rows. A caller wanting zero violations runs without `--baseline` |
| RC-D6 | Outcome when either run leaves an alethic constraint unchecked | exit 4; no novelty claim for that constraint |
| RC-D7 | Vacuous control: run-wide flag, per-constraint field, or both | flag only: a CI adoption choice, not a domain fact |
| RC-D8 | Spelling of the new source value | `tool-output`, with an optional `producer` string (1-200 characters, naming tool and revision) allowed only with it; avoid `extracted` |
| RC-D9 | `--baseline` over a model with id-less constraints | proceed; mark each row's `addressing`, count positional-keyed rows in the `baseline` block, and print a warning in text output. Alternative: refuse at exit 3 |
| RC-D10 | Home for strongly connected groups | lift one existing iterative Tarjan into a shared lower-layer home; RC2 moves both existing callers onto it (RC2-C6), so one implementation remains |
| RC-D11 | Derivation failures under `--baseline` | **owner selected 2026-11-06 ("Commit, r5 with refusal")**: refuse models with structured derivations at exit 3, `check:baseline-unsupported`. Comparing findings would need every offending derivation row (O26); that is follow-up work if a caller needs it |
| RC-D12 | `remedy: null` when undeclared, or fall back to `rationale`? | null: `rationale` says why the rule exists, not what to do; copying it would put the wrong text in the field |
| RC-D13 | Does a deontic unchecked verdict block "no new violations"? | no, matching `band()` for every route version 15 can reach: deontic unchecked affects the band only through `reference-join-work-limit` (O23), which needs reference populations, and those models are refused (RC1-C6). The `baseline` block counts it in `undecided`, an obligation count (S4) |
| RC-D14 | Review r4 before the plan gate? | **ruled 2026-11-06: "Codex re-check r4"** (done, [003-review](../003-review.md)) |
| RC-D15 | Review r5 before the plan gate? | **ruled 2026-11-06: "Codex re-check r5"** (done, [004-review](../004-review.md)) |
| RC-D16 | Review r6 before the plan gate? | owner's call; r6's changes are confined to T1-T2 (§14) |
| RC-D17 | The pre-existing version-7 schema defect (O29) | file it as its own issue; fixing it changes the frozen version-7 contract, so it is not part of this milestone |

## 11. Panel fix dispositions (r2 → r3)

| Fix | Disposition |
|---|---|
| F1 key stability for id-less | applied: RC3-C4a/b, RC-D9, §2.3 |
| F2 redaction/temporal refusal | applied: §2.1 by model property, versions 9/11, RC1-C6, rule 3, predicate 1 |
| F3 allow-vacuous record | applied: v15 `allow_vacuous`, implies `--rule-ids`, RC1 → RC4 |
| F4 freeze gated only by v7 | applied: rule 7 full-suite gate, §5 suites named, claim narrowed to what the suite pins |
| F5 baseline × vacuous | applied: §2.3, RC4 after RC3, RC4-C4 |
| F6 RC-D5 vs D-08 | applied: RC-D5 keeps D-08, RC3-C2 |
| F7 time bounds, budgets, stop rule | applied: O21 fixture measured here, RC2-C4, RC3-C5, RC6/close budgets, rule 8 |
| F8 O16 and address row | applied: O16 and §3 reworded |
| F9 RC5 homes | applied: §3 row, RC5-C2 |
| F10 verdict-level novelty | applied: §2.3, RC3-C6 |
| F11 deontic unchecked | applied: RC-D13 |
| F12 full v15 shape in RC1 | applied: §2.1, RC1-C2 |
| F13 derivations | applied: RC-D11, RC3-C7, O20 (r5: superseded by the refusal, RC3-C3b) |
| F14 version gates and coverage | applied: O18, §2.1, RC1-C8, §7 |
| F15 RC2-C2 | applied: problem item 3, RC2-C2 |
| F16 existing Tarjan | applied: O17, RC-D10 |
| F17 merge-base gate record | applied: header, §8 |
| F18 coverage/address suites | applied: §9 RC1 gate |
| F19 text and message criteria | applied: RC1-C7, RC2-C5 |
| F20 remedy null | applied: RC-D12 |
| F21 issue numbers | applied: O1-O6 |
| F22 stale r1 references | applied: §8, RC-D0 |

## 12. Single-review dispositions (r3 → r4)

| Finding | Disposition |
|---|---|
| R1 `allOf` over closed verdict | applied: §2.1 separate closed `verdict_v15` / `derivation_verdict_v15`; RC1 spec M2 (r5: derivations reuse `derivation_verdict`) |
| R2 reference-population wrapper | applied: §2.1 refusal, O22, rule 3, RC1-C6, predicate 1 |
| R3 verdict-level novelty | applied: §2.1 `novelty` + `row_novelty`, §2.3, RC3-C6 |
| R4 derivation novelty | applied: §2.1 derivation fields, RC-D11, RC3-C7 (r5: replaced by the refusal; S1) |
| R5 RC3 full suite | applied: rule 7, §6, §9 |
| R6 merge-base command | applied: §8 existing-suite command; RC1 spec §8 |
| R7 work-limit band route | applied: O23, RC-D13 (unreachable under the R2 refusal) |
| R8 quadratic copy | applied: rule 2, rule 4, O24, `iter_constraints_shared()`, RC1-C9 |
| R9 RC5 note bound | applied: RC5-C1, RC-D8 |
| R10 text renderer | applied: §2.1, O25, §3, RC1-C7; RC1 spec M6 |
| R11 SCC migration criterion | applied: RC2-C6, RC-D10 |
| R12 self-loop | applied: RC2-C1 |
| R13 RC3 refusal criterion | applied: RC3-C3a |

## 13. Re-check dispositions (r4 → r5)

| Finding | Disposition |
|---|---|
| S1 first-row-only derivation findings | applied by refusal (owner's selection): RC-D11, §2.3, O26, RC3-C3b, §7; derivation novelty fields removed |
| S2 derivation conditional rules | resolved by S1's fix: v15 derivations reuse `derivation_verdict` unchanged; RC1 spec M2, T4b (r6: own definition keeping the rules, T1) |
| S3 `producer` loader | applied: O27, RC5-C1 |
| S4 `undecided` unit | applied: §2.3 obligation count, O28, RC3-C3, RC-D13 |

## 14. Re-check dispositions (r5 → r6)

| Finding | Disposition |
|---|---|
| T1 v15 derivation reasons too narrow | applied: §2.1 `derivation_verdict_v15` (v7 properties and conditional rules, full reason set), RC1-C2, O29, RC-D17; RC1 spec M2, T4c |
| T2 stale labels | applied: §8; RC1 spec §1 |

## 15. Close amendments (2026-11-06)

Plan repairs owed by phase records, applied at the milestone close
([012-milestone-close.md](../012-milestone-close.md)) under its ruling. Each
keeps the prior wording; the sections above are not edited.

| Clause | Prior wording | Amended | Raised by |
|---|---|---|---|
| O17 | "strongly connected components are computed twice already" | three implementations existed; RC2 moved all three onto `gnd.graphs` | [007-phase-RC2.md](../007-phase-RC2.md), refuted premise |
| Implementability sweep, "No new dependency" | "SCC code exists twice (O17)" | three times; see O17 above | [007-phase-RC2.md](../007-phase-RC2.md), refuted premise |
| §3, baseline comparison | "new module under `src/gnd/checker/` (RC3 spec)" | `src/gnd/baseline.py`: a guard pins `src/gnd/checker/` to four files | [008-phase-RC3.md](../008-phase-RC3.md), refuted premise |
| RC5-C2 | "a test fails if `population.py` or `extract/projection.py` disagrees with it" | `population.py` equals the schema enum; the extraction projection is a pinned subset, since its bytes are hashed into recorded `projection_sha256` values and its output is always `agent-output` (RC5 D2) | [010-phase-RC5.md](../010-phase-RC5.md), refuted premise |
