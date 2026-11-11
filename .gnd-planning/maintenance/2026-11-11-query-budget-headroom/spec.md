# Query-budget headroom -- spec r1

## 1. Status

**Owner-decided (2026-11-11): approved with D1 to D4 as proposed ("Approve as
proposed") (o).** Implemented; see "Implementation findings" at the end. No
review ran over the spec; the diff review is recorded in the README.

## 2. Provenance

- Issue 170 ("Both query-policy budgets are full"), carried at the
  release-0.3.0 close (`milestones/release-0.3.0/007-milestone-close.md`) from
  the RN0 record (`milestones/release-0.3.0/002-phase-RN0.md`, "Refactoring
  review") and `milestones/release-0.3.0/evidence/RN0/query-successor.json`.
- Owner ruling, 2026-11-11: "Move reads" (o). The alternative, raising the
  ceilings, was offered and not chosen.
- Probes below ran on `main` at `793618f1`, on branch
  `claude/issues-169-177-explanation-e4e2b0`.
- Home: a maintenance note, following
  `maintenance/2026-10-27-carried-defects`. It is one phase of
  behavior-preserving work with no product change, so it has no milestone plan
  (D4).

## 3. Obligations

| # | Source | Obligation | Discharged in |
|---|---|---|---|
| O1 | issue 170 | make room in both budgets before the next milestone that adds source code | §5, §6.1 |
| O2 | owner ruling 2026-11-11 | by moving reads behind `gnd.model_index.ModelIndex`, not by raising a ceiling | §6.1, §6.3; T3 |
| O3 | AGENTS.md "Model queries and family dispatch" | prefer the read-only `ModelIndex` snapshot; exceptions stay exact, counted rows | §6.2 |
| O4 | AGENTS.md "Refactoring dependency homes" | `tools/gnd_layers.json` stays the source of module homes; allowance count stays zero | §6.4; T4 |
| O5 | `tests/test_rf6_query_policy.py` | found reads equal the approved rows exactly; the 310/320 literal is unchanged | §6.2; T3 |
| O6 | `tests/support/pyrel_application_successors.py` | a budget change is an authenticated successor chained to its predecessor by SHA-256 | §6.2 |
| O7 | project.md "Test and gate commands" | focused gate under the default lane filter; lint gate recorded | §8 |
| O8 | project.md "Component index" | `scripts/components_index.py changed --base main --strict` before the PR | §8 |
| O9 | issue 171 (open) | the structure guards are in no gate; this work runs them anyway | §8 gate G1 |

## 4. Standing rules, bound to this work

1. **Totality belongs to the function.** No new consumer of document shapes
   is added. `ModelIndex.for_model` refuses a non-`Model` with `TypeError`;
   every converted site is one whose callers pass a `Model` (§6.1, checked
   per site, T2).
2. **A cap bounds the document, not the algorithm.** Outside an index scope
   `ModelIndex.for_model` dumps and hashes the model on each call. Only sites
   reached once per command are converted; sites reached once per constraint
   are excluded (§6.1, "Excluded"). T5 bounds the added cost.
3. **Validation order.** Inapplicable: no check is added or reordered.
4. **One walk over N kinds.** Inapplicable: no policy is added.
5. **One home for normative prose.** Inapplicable: no normative document
   changes. The policy's home remains the successor chain.
6. **Measure, don't argue.** Equivalence of the two reads is measured over
   the fixture models (T1) before any site is converted.

Failure classes: "a declared branch with no case that can fail it" is
answered by T1 and T2, which fail if the index's rows differ from the
model's; the guard itself (T3) fails in each direction already
(`test_policy_rejects_each_direction`).

## 5. Goal

After the change, `uv run pytest -q tests/test_rf6_query_policy.py` exits 0
with the exact policy at **355 of 365** occurrences and the original metric
at **300 of 310**, both ceilings and the `(310, 320)` literal unchanged. No
command's output bytes change.

## 6. Design

### 6.1 The reads

Observed: the 365 counted reads include 134 `model.fact_types` or
`self.model.fact_types` reads in 44 modules. Each conversion below replaces
one such read with
`ModelIndex.for_model(model).iter_fact_types_shared()` (D1) and removes one
occurrence from both metrics.

**Primary set, 10 reads.** Each was read at `793618f1`: the loop only reads
rows, no row leaves the function, and the function runs once per command.

| # | Site | Use |
|---|---|---|
| 1 | `src/gnd/diff.py` `_structured` | `any(...)` over derivation rules |
| 2 | `src/gnd/extraction_scope.py` `fact_type_scope` | builds an id-to-reason map |
| 3 | `src/gnd/synth/frontier.py` `frontier_codes_for` | `any(...)` over constraint types |
| 4 | `src/gnd/measure/report.py` `build_measurement_report` | `any(...)` over rule operands |
| 5 | `src/gnd/measure/service.py` `_cmd_measure` | builds disclosure tuples of strings |
| 6 | `src/gnd/judgments.py` `evaluate_judgments` | set of supplied fact-type ids |
| 7 | `src/gnd/coverage.py` `_element_universe` | builds address tuples |
| 8 | `src/gnd/checking_service.py` `_run_check_raw` | `any(...)` over constraint types |
| 9 | `src/gnd/api.py` `_run_transition_raw` | `any(...)` over rule clauses |
| 10 | `src/gnd/synth/service.py` `_cmd_synth` (the `any(...)` read) | `any(...)` over rule clauses |

Not yet checked for these ten: that every caller passes a `Model` (T2
decides it), and that `gnd.extraction_scope`, which is in the `model` layer
beside `gnd.model_index`, can import it without a cycle. A site that fails
either check is dropped and replaced from the reserve; the record names it.

**Reserve, up to 4 reads**, converted only to replace a dropped primary site
or by D2: `src/gnd/extract/projection.py` `_build_projection`,
`src/gnd/vocabulary.py` `render_verbalization`,
`src/gnd/codegen/emit.py` `render_skill_document`,
`src/gnd/exp/session_contract.py` `read_session_contract`. Their signatures
take `model: Any`; none was read beyond the one line.

**Excluded, with the reason:**

- rows leave the function, so a shared row could be mutated by a caller:
  `diff._constraints`, `measure/truth.resolve_constraint_ref`,
  `refscheme._fact_types_by_id`, `codegen/emit._constructor_fact_types`,
  the second `_cmd_synth` read (it stores `derivation_rule` values);
- reached once per constraint: `synth/boundary._value_target` and
  `_reference_targets`, the three `synth/oracle/mutations` helpers;
- `documents.structured_derivation_ids` is re-homed as `gnd.model` and is
  imported by the model layer itself;
- the 95 `.get('roles')` reads, the snapshot-IR reads and the standalone
  runtimes keep the reasons their rows already record.

### 6.2 The policy successor

One new file,
`.gnd-planning/maintenance/2026-11-11-query-budget-headroom/query-successor.json`,
appended to `QUERY_SUCCESSORS` in
`tests/support/pyrel_application_successors.py`:

```json
{
  "schema_version": 1,
  "predecessor": ".gnd-planning/milestones/release-0.3.0/evidence/RN0/query-successor.json",
  "predecessor_sha256": "<sha256 of that file>",
  "reason": "...",
  "removed": [["src/gnd/diff.py", "_structured", "model.fact_types", 1], "..."],
  "added": [],
  "result_distinct_rows": "<297 minus the rows that reach zero>",
  "result_occurrences": 355,
  "original_metric_current": 300
}
```

The dynamic-query inventory is expected not to move:
`ModelIndex.for_model(model)` is neither a non-constant subscript nor a
non-constant `.get`/`getattr`. If it moves, a dynamic successor is added in
the same directory and the record says so.

### 6.3 What does not change

`tests/test_rf6_query_policy.py` (no line), both ceilings, both baselines,
`src/gnd/model_index.py`, every CLI output and every recorded fixture.

### 6.4 Size and homes

About 10 changed source lines and up to 6 added import lines in 9 modules
(`coverage`, `api` and `checking_service` already import `ModelIndex`). No new
module, so no new row in `tools/gnd_layers.json`. Importing `gnd.model_index`
(layer `model`) from the `model`, `semantics`, `lanes` and `entry` layers
needs no allowance.

## 7. Decisions

| # | Question | Readings and cost | Proposed |
|---|---|---|---|
| D1 | Which accessor? | `iter_fact_types_shared()` yields the index's own rows with no copy; its docstring restricts it to internal readers that never mutate a row. `iter_fact_types()` deep-copies every fact type on each call, which is safe against mutation and costs a full copy per read. Neither changes an exit code. | shared, since every primary site only reads. **Ruled as proposed (o), 2026-11-11** |
| D2 | How much room? | 10 reads leaves 10 free in each budget. Adding the 4 reserve sites leaves 14, at the cost of four less-inspected conversions. | 10; reserve only as replacements. **Ruled as proposed (o), 2026-11-11** |
| D3 | Gate breadth? | The change touches 9 modules whose consumers span most of the suite (over 100 test files name `measure`, `synth` or `coverage`). A focused list would be long and easy to under-select; the default lane run once covers it. Project.md's rule is the focused selection. | G1 focused guards, plus G2 the default lane once as the affected-consumer selection. **Ruled as proposed (o), 2026-11-11** |
| D4 | Home and review bar? | As maintenance: this spec, one independent diff reviewer in a different tool, a README record. As a milestone: a plan, a plan gate and the four-reviewer panel at plan review and close. | maintenance. **Ruled as proposed (o), 2026-11-11** |

## 8. Tests and gates

New file `tests/test_query_budget_headroom.py` (default lane):

| # | Case | Expected |
|---|---|---|
| T1 | for each model fixture the suite already loads for `ModelIndex` tests, `list(ModelIndex.for_model(m).iter_fact_types_shared()) == list(m.fact_types or [])` | pass; fails if the dump and the live rows ever differ |
| T2 | each converted function, called on one fixture model, returns the value recorded from `793618f1` before the edit | pass; a non-`Model` caller would raise `TypeError` here or in G2 |
| T5 | `ModelIndex.for_model` on the largest fixture model outside an index scope, 10 calls, under a stated bound measured first on `main` | pass |

Existing tests that judge the change:

| # | Case | Expected |
|---|---|---|
| T3 | `tests/test_rf6_query_policy.py` (17 tests; 17 passed at `793618f1`) | exit 0 at 355 and 300 |
| T4 | `tests/test_rf1_layering.py` | exit 0, allowance count zero |

Gates, recorded verbatim:

- **G1** `uv run pytest -q tests/test_query_budget_headroom.py tests/test_rf6_query_policy.py tests/test_rf1_layering.py tests/test_rf5_commands.py tests/test_rf5_review_regressions.py tests/test_rf7_structure.py tests/test_rf8_structure.py tests/test_rf9_repairs.py --tb=short -p no:cacheprovider`
- **G2** (D3) `uv run pytest -q --tb=short -p no:cacheprovider`
- **G3** `uv run ruff check` over the changed source and test files
- **G4** `python3 scripts/components_index.py changed --base main --strict`

T1's fixture list is unresolved until implementation: it is taken from the
existing `ModelIndex` tests, not invented here.

## 9. Out of scope

- Any ceiling, baseline or guard-code change.
- The `.get('roles')` reads, the remaining 124 `model.fact_types` reads and
  any new `ModelIndex` method.
- Putting the structure guards in a phase gate (issue 171) and the
  repository-wide lint (issue 177).
- Closing issue 170: the owner closes it at merge.

## 10. Size

Estimate: 16 source lines, 70 test lines, one successor file of about 30
lines, one line in `tests/support/pyrel_application_successors.py`. Stop for
the owner past 1.5 times this.

## 11. Approval instrument

This prose. Approval of the spec and D1 to D4 precedes any source edit. Merge
keeps its separate owner authorization.

## Implementation findings, recorded as they were found

1. **Two primary sites are pinned by an existing guard and were dropped.**
   `tests/test_rf5_commands.py::test_relocated_algorithm_and_qualification_are_unchanged`
   pins the syntax tree of `_cmd_measure` and `_cmd_synth`. Converting their
   reads turned that test red (2 failed, 365 passed in G1). Both edits were
   reverted, not the pins. §6.1 did not foresee this: it named only the
   `Model`-caller and import-cycle checks as reasons to drop a site.
2. **Two reserve sites replaced them** (§6.1, D2):
   `codegen/emit.render_skill_document` and
   `exp/session_contract.read_session_contract`. Both were read before
   conversion: each only reads rows and builds strings or a set of ids. The
   second runs once per distinct model path in a contract, not once per
   command. The other two reserve sites are unconverted.
3. **Result as measured:** 10 reads removed, none added; 355 of 365 and 300 of
   310; 287 distinct rows (§6.2 left this figure open). The dynamic-query
   inventory did not move.
4. **T1 measured:** 225 models under `examples/` and `tests/fixtures/` load and
   all 225 give equal rows; 60 further `.orm.yaml` fixtures are deliberately
   invalid and are skipped. The test requires at least 200.
5. **T2 is narrower than written.** It calls three converted functions
   directly (`diff._structured`, `fact_type_scope`, `frontier_codes_for`) and
   compares each with a recomputation from the model's own rows, with both
   branches of each predicate present. The other seven sit inside commands and
   are judged by G2 only.
6. **T5 is a loose bound.** Ten unscoped calls on the largest fixture (19 fact
   types) took 0.003 s; the test allows 1.0 s. It would catch a gross
   regression, not a small one.
7. **G4 needed a regenerated component index**
   (`scripts/components_index.py write`): seven generated files under
   `dev/components/` changed. It then reports 0 to fix and 14 entries to
   reread, which is advisory.
8. **Size:** 16 source lines changed or added in 10 modules, 77 test lines, one
   line in `tests/support/pyrel_application_successors.py`; within the estimate.
9. **A third primary site is pinned and was dropped (found by G2).**
   `tests/test_rf4_peripheral.py` pins the body of `_run_check_raw`
   (2 failed in the first full run). The edit was reverted, not the pin.
   Findings 1 and 9 together: three of the ten primary sites were command
   bodies whose syntax an RF4 or RF5 guard pins. The spec's site selection
   did not look for body pins.
10. **A fourth primary site was dropped on review finding R1 (reproduced).**
    `extraction_scope.fact_type_scope` is reached through
    `refscheme.applicable_set(model: Any)`, and
    `tests/test_extract_applicable.py` passes a `SimpleNamespace`. The
    conversion raised `TypeError` there; the edit was reverted. This is the
    `Model`-caller check §6.1 left to the tests, and the new tests did not
    catch it; the reviewer and the full lane did.
11. **All four reserve sites are now used**, replacing the four dropped
    primary sites: `codegen/emit.render_skill_document`,
    `exp/session_contract.read_session_contract`,
    `vocabulary.render_verbalization` and
    `extract/projection._build_projection`. The last two take `model: Any`
    and were not read beyond their loops before conversion; the full lane is
    what judges their callers. `extract/projection.py` had no module-level
    `gnd` import before; it now imports `gnd.model_index`.
12. **Final converted set (10):** `api._run_transition_raw`,
    `codegen/emit.render_skill_document`, `coverage._element_universe`,
    `diff._structured`, `exp/session_contract.read_session_contract`,
    `extract/projection._build_projection`, `judgments.evaluate_judgments`,
    `measure/report.build_measurement_report`,
    `synth/frontier.frontier_codes_for`, `vocabulary.render_verbalization`.
    Finding 3's figures stand: 355 of 365, 300 of 310, 287 distinct rows.
13. **A behaviour change to know:** a converted function given a non-`Model`
    now raises `TypeError: ModelIndex requires a Model`, where it raised
    `AttributeError` (or, for a duck-typed object with `fact_types`, worked).
    No caller in `src/` or the default lane does this at the ten final sites.
    Pinned by `test_a_non_model_now_raises_type_error`.
14. **T2 after review (R2):** it now calls two converted functions directly
    (`_structured`, `frontier_codes_for`); a new test checks that three
    converted readers leave the shared rows equal. The other converted
    functions are judged by the full lane only. R2's request for recorded
    baseline bytes for all ten, and for a per-caller indexing-frequency
    control, was not done.
15. **R2's remainder was applied after the first PR push.**
    `evidence/compare_outputs.py` digests the outputs of six converted
    functions over the 225 loadable models, once importing the source tree of
    `793618f1` and once the head tree; the 1,350 digests are equal
    (`evidence/outputs-head.json`). A frequency test counts reads of the fact
    types per call, with a negative control.
16. **Second review, R3 (reproduced): the index reads a dump, not the live
    rows.** For a `Model` built in code whose rows hold a value that
    `model_dump()` alters (the reviewer's case: a zero-field dataclass as
    `derivation_rule`), `_structured` returned `True` at base and returns
    `False` at head. T1 could not see this: every fixture is loaded from YAML,
    where the dump equals the rows. This holds for every `ModelIndex` read in
    the repository, not only these ten. It is recorded as a limit, not
    repaired: the supported input is a model whose rows are plain JSON
    values, which is what `load_model` produces.
17. **R4 applied in part.** The frequency test now uses a model with a
    structured rule, so the skill-document read runs, covers six readers and
    has a negative control. It counts reads of the fact types, not
    constructions of the index, and does not cover the four readers that sit
    inside commands.
18. **R5 applied:** the README binds each gate result to the commit it ran on.
