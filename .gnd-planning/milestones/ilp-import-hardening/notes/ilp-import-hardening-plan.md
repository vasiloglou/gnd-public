# ILP import hardening

r2 (p1), 2026-10-29. Planning only. **No plan or spec approval exists.**
Milestone: `ilp-import-hardening`. `auto=false`.
Inspection baseline: `fb03739` (main, after PR #64, which marked ilp-learners
closed and repaired three tests that PR #63 left red, in `a7d6dc0` and
`fe80002`).

**Review status:**
- **Round 1.** r1 (SHA-256 `cbfa12fd…51ce`) received one reader's opinion,
  the instrument the owner selected on 2026-10-29 (o): "One reader". The
  verdict was request-changes, with 14 findings: 3 blocking, 6 hardening and
  5 completeness. The author reproduced all three blocking findings before
  repairing. See [reader 1](plan-review-r1-reader-1.md) and the
  [disposition](plan-review-r1-disposition.md).
- **r2** applies every finding. **r2 bytes carry no review opinion.**
- One reader is below the repository's four-reviewer plan bar (IH-D5).

**Change tags:**
- `(p1)` marks text added or changed in r2 in response to round 1.
- `(o)` marks an owner answer or ruling, quoted where the owner's words exist.
- Untagged text is the author's r1 proposal.
- Planning authorship is not approval.

## Goal, status and completion predicates

The ilp-learners milestone (IL) closed on 2026-10-29. It carried the debt in
its mined-rule import (`gnd import mined-rules`) to "the next milestone that
changes the mined import" (`../ilp-learners/009-milestone-close.md`,
"Carried forward"). Its diff was never reviewed as a whole: the owner chose
at acceptance not to have one first (`../ilp-learners/010-owner-acceptance.md`).

This milestone:
- reviews IL's source changes as one change, so that the debt it fixes is
  the debt that is actually there;
- gives the mined import one public counting entry and builds its relation
  table and spelled pairs once;
- settles IL4-Q1's remainder: a join through an own-reference subtype is
  either counted as the checker counts it or refused by its own name;
- runs no learner. Every test reads committed fixtures or retained outputs.

The owner asked for this plan on 2026-10-29 (o), answering "yes" to "Should I
draft that milestone plan with `start-milestone`?". The plan that question
proposed: "start the hardening milestone with the diff review as its first
phase". The request is planning authority only. **It is also the source of
IH0**: 009 left the whole-diff review to "the owner's call at acceptance",
not to this milestone (p1).

Completion requires:

1. **IH0, the review of IL's source changes (p1):**
   - one opinion per reader over **IL's own merges** (§4 IH0): 37 files in
     `src/` and `tools/`, 3,187 inserted and 161 deleted lines, judged at
     `fb03739`. Every finding is reproduced before it is believed;
   - every finding triaged blocking, hardening or completeness. Each one is
     either fixed in IH0 with a regression test shown red against the fix's
     parent, or assigned to IH1 or IH2 by name, or carried with a target.
2. **IH1, one counting entry:**
   - a public `count_mined_rules` entry that `gnd import mined-rules` and
     `tools/ilp_comparison.hold()` both call. It raises only mapping
     refusals and `too-large`; admission checks stay in the import (p1).
     No module outside `gnd.export.ilp_service` imports `_mined_inputs`;
   - one import builds `relation_table` and `pairs` once each (today twice
     each) (IL-close-Q1) (p1);
   - the per-rule provenance builder lives in `gnd.export.ilp_amie`
     (IL4-Q3 remainder), without a new export → discover edge (p1);
   - the refusal order is pinned against its documented home (IH-R4) (p1);
   - behaviour preserved: the IL4 and IL-close goldens, the retained AMIE
     replays and the comparison golden are byte-identical.
3. **IH2, own-reference subtype joins (IL4-Q1 remainder):** a join through
   an own-reference subtype is either counted as the checker counts it, or
   refused by a refusal name of its own before any count, per IH-D1. A
   regression test reproduces today's false `support-mismatch` first.
4. **Every phase has:** approval, focused checks, one independent diff
   review, a refactoring review and a record.
5. **Close has:**
   - a question sweep;
   - **the local CI run on the PR head** (IH-R3);
   - a close review per IH-D6 (p1);
   - a PR;
   - owner acceptance, recorded separately.

No delivery date is committed.

## 0. Binding design rules

IK-R1 to IK-R12 (`../induced-knowledge/notes/induced-knowledge-plan.md` §0)
and IL-R1 to IL-R11 (`../ilp-learners/notes/ilp-learners-plan.md` §0) bind
every phase unchanged. IL-R2, IL-R5 and IL-R9 (live runs, licences, outcomes
before runs) have nothing to bind here, because no learner runs (IH-R1).
This milestone adds:

| ID | Rule |
|---|---|
| IH-R1 | **No learner runs.** No phase installs, downloads or invokes a learner, solver or model. Evidence is committed fixtures and the retained IL outputs. A finding that needs a learner run is carried, not reproduced by running one. |
| IH-R2 | **Refactors preserve bytes.** IH1 is behaviour-preserving: every golden, retained replay and the comparison golden stay byte-identical, and the AMIE `adapter_version` stays 2. A change that moves a golden is not a refactor and returns to the owner gate. |
| IH-R3 (p1) | **The close gate is the local CI run.** Before the close PR merges, the development workflow's steps run on the PR head, from clean clones, under Python 3.13 and 3.11, and exit 0. Its steps are those of `.github/workflows/development.yml`: <ul><li>**candidate:** `uv build`, the sdist-to-wheel rebuild and the SHA-256 check;</li><li>**regression:** `uv sync --locked --group dev`, `gnd install --symlink --project --force`, `gnd doctor --project`, `pytest --collect-only -q`, the platform-sensitive tests, and `pytest -q -ra --tb=short`;</li><li>**installed:** `GND_CANDIDATE_DIR=… pytest -q -o addopts='' tests/test_release_acceptance.py`.</li></ul> **The workflow's Linux leg is not reproduced:** both runs are macOS; Ubuntu/3.11 runs only if cloud CI runs. The run is retained in `evidence/close/ci-run.txt`. Focused gates remain the per-phase gate. This answers IL's close, whose focused gate let three failing tests reach main (repaired in `a7d6dc0`, `fe80002`). |
| IH-R4 | **Refusals keep their order.** A new refusal name enters `MAPPING_REFUSALS` or `COUNT_REFUSALS` (`gnd.export.ilp_amie`) at one named position. The ordered tables in `docs/reference/ilp-bridge.md` ("Importing mined rules") are its one home. IH1 adds a test pinning both tuples' order against those tables (p1). |

## 1. Scope, sources and authority

### Sources

| Source | What it assigns |
|---|---|
| `../ilp-learners/009-milestone-close.md`, "Carried forward" | IL4-Q3 remainder, IL-close-Q1, the `hold()` import, IL4-Q1 own-reference subtypes |
| the owner, 2026-10-29 (o): "yes" to the plan whose first phase is the diff review | IH0 (p1) |
| `../ilp-learners/010-owner-acceptance.md`, "Boundary" | "The milestone diff as a whole has had no review" |
| `../ilp-learners/notes/phase-IL-close-spec.md` §6.1, ILC-F8 | the family spelling and why an own-reference subtype was split out |
| `../ilp-learners/008-close-repairs.md`, "Refactoring review" | IL-close-Q1 as recorded: the import "builds the relation table and the spelled pairs again" (p1) |
| `../ilp-learners/notes/phase-IL4-agent-review.md`, finding 2 | the original subtype-join defect |
| `../ilp-learners/007-phase-IL6.md`, refactoring review | the deferred `hold()` private import |
| commits `a7d6dc0` and `fe80002` (PR #64) | three tests on main failed after IL's focused close gate; IH-R3 (p1) |

### Harvested obligations

| Obligation | Source | Owner phase / gate |
|---|---|---|
| Review IL's source changes as one change | the owner, 2026-10-29 (o) (p1) | IH0 |
| One public "count mined rules" entry; `hold()` stops importing `_mined_inputs` | 009, `007` refactoring deferral row | IH1 |
| Build the relation table and spelled pairs once | 009, IL-close-Q1; `008` refactoring review (p1) | IH1 |
| Per-rule provenance moves into `ilp_amie` | 009, IL4-Q3 (remainder) | IH1 |
| Pin the refusal order | IH-R4 (p1) | IH1 |
| Count an own-reference subtype join, or refuse it by name | 009, IL4-Q1 (own-reference subtypes) | IH2 (IH-D1) |
| The close gate runs the local CI | IH-R3 | close |

### Not harvested (carried elsewhere by IL's close)

- IL1-Q6, IL2-Q2, IL3-Q3 and IL-close-Q2 need learner or clingo runs. They
  go to a later evaluation milestone.
- IL5-Q5 and IL5-Q6 change verbalization and `gnd.agents`, which other
  milestones own.
- IL6-Q3 (one outcome schema) is offered at IH-D3.

## 2. Contract proposal and product behaviour

**No wire changes in IH0 or IH1.** `gnd-mined-run/1`, `gnd-ilp-import/1`
and the AMIE export tree are unchanged; `gnd import mined-rules` keeps its
arguments, exits and refusal order.

### The counting entry (IH1) (p1)

```python
# gnd.export.ilp_service
@dataclass(frozen=True)
class MinedInputs: ...           # today's _Mined, made public

@dataclass(frozen=True)
class MinedCount:
    relations: dict[str, Relation]
    facts: dict[str, list[tuple[str, str]]]   # the one spelled-pairs table
    rules: tuple[MinedRule, ...]
    counts: tuple[Counts, ...]

def load_mined_inputs(model_path: Path, population_path: Path) -> MinedInputs: ...
def count_mined_rules(inputs: MinedInputs, parsed: list[dict[str, Any]]) -> MinedCount: ...
```

`count_mined_rules` builds `relation_table` and `pairs` once. It maps every
rule in `MAPPING_REFUSALS` order, then counts every rule. **It raises only
the mapping refusals and `too-large`.** `covers-nothing`, `support-mismatch`
and `does-not-hold` stay in the import, as admission checks over
`MinedCount.counts` in their current order. `hold()` needs the counts of
rules that do not hold: the retained AMIE invocation 1 has 6 of 8 such
rules, and the comparison golden records `rules_hold 2`.

**`hold()`'s error order changes.** Today it maps and counts one rule at a
time, so a rule 0 that is `too-large` is reported before a rule 1 that is
unmappable. Through the entry, every mapping refusal comes before any
counting refusal. Only the error path changes: the committed golden has no
error row, so it stays byte-identical. IH1-D2 rules on it.

**The facts digest stays in the import.** Today `facts-mismatch` is raised
before any mapping refusal (`ilp_service.py:619-640`). The import keeps
rendering `amie/facts.tsv` and comparing its digest before it calls
`count_mined_rules`. The entry does not render. IH1-D1 records the
alternative and its cost. A test pins `facts-mismatch` ahead of every
mapping refusal. It passes at `fb03739`, so it is shown red against a
reordering mutant, as IL showed R6.

**The provenance builder.** `ilp_amie.provenance(head, satisfied, rows,
fact_id)` builds one rule's examples. `fact_id` is a callable the import
passes (`PopulationView.fact_id`), so `gnd.export.ilp_amie` gains no import
of `gnd.discover`. It reads the counted pairs, not a second `spell` pass.

**Names (AGENTS.md shims).** `_mined_inputs` and `_Mined` are private, so
AGENTS.md's identity-alias rule for moved public names does not bind them.
IH1 still keeps `_mined_inputs = load_mined_inputs` as an identity alias
until the shim retirement trigger, because `tests/` and the retained
evidence scripts may import it. The IH1 spec lists every importer.

### Own-reference subtype joins (IH2)

Today `ilp_amie.family` puts an own-reference subtype in a family of its
own, so `manager:1` never meets `staff:1`. The checker compares raw values:
two equal values of one primitive join. GND's count does not join them, so
the refusal is a false `support-mismatch`. Reader 1 reproduced this: with
String codes the import exits 3 and GND counts "0 of 2", but with the count
forced to agree, the checker passes the rule (exit 0). With differing
primitives (Integer `1`, String `"1"`) the checker does not join them,
which R1 in `tests/test_il_close.py` pins (p1). IH-D1 chooses the repair.

## 3. Dependencies and artifact homes

| Artifact | Home |
|---|---|
| Plan, specs, reviews | `.gnd-planning/milestones/ilp-import-hardening/notes/` |
| Phase and close records | `.gnd-planning/milestones/ilp-import-hardening/NNN-*.md` |
| Red/green and gate evidence | `.gnd-planning/milestones/ilp-import-hardening/evidence/IH<n>/` |
| RF6 census successor (p1) | `evidence/IH<n>/dynamic-query-successor.json` for each phase that moves query rows, listed in `tests/support/pyrel_application_successors.py` after IL-close's |
| Close CI evidence (p1) | `evidence/close/ci-run.txt` |
| Code | `src/gnd/export/ilp_service.py`, `src/gnd/export/ilp_amie.py`, `tools/ilp_comparison.py` |
| Tests | `tests/test_ih_*.py`; fixtures under `tests/fixtures/ilp_learners/` |
| Docs | `docs/reference/ilp-bridge.md` ("Importing mined rules", its refusal tables) |

The dependencies are linear: IH0 → IH1 → IH2 → close.
- IH1 needs IH0's findings, because a finding in the counting path changes
  what IH1 moves.
- IH2 needs IH1's counting entry, because its refusal or spelling enters
  there.
- No phase is optional.

`tools/gnd_layers.json` needs no new home: IH1 moves names within
`gnd.export`, and the provenance builder takes `fact_id` as a parameter, so
there is no new `export` → `discover` edge (p1).

## 4. Phases, criteria and residuals

### IH0: review of IL's source changes (p1)

**Deliverables:**
- the review opinions, retained verbatim under `notes/`;
- a triage table;
- fixes for blocking findings.

**The subject.** It is the union of IL's own first-parent merges into main,
each read as `git diff m^1 m -- src tools`:

| Merge | PR |
|---|---|
| `65fd6df` | #56 |
| `426bd80` | #57 |
| `75a397f` | #58 |
| `e30eec8` | #59, IL5-Q3's RF1 manifest rehash |
| `70266b5` | #60 |
| `860e651` | #61 |
| `a75b328` | #62 |
| `7818be1` | #63 |
| `fb03739` | #64 |

That is 37 files, +3,187/−161, judged at `fb03739`. The other merges in
`07f4d45^..fb03739` belong to other milestones and are **out of scope**: #47
IK-evolve, #50 IK-close, #52 IKE-Q3 and #53 maintenance. Their `src`
changes were reviewed under those milestones. Including them is IH-D2.

**Criteria:**
- commits that already had a phase or predicate-7 review are re-read, not
  skipped;
- each finding is reproduced before it is believed. One that cannot be
  reproduced without a learner run is carried (IH-R1);
- each **blocking** finding is fixed in IH0, with a regression test shown
  red against the fix's parent commit;
- each hardening or completeness finding is fixed, assigned to IH1 or IH2
  by name, or carried with a target;
- the focused gate of every touched module exits 0.

**Residual:** a review is a disagreement locator, not a proof. Tests, docs
and evidence are out of its scope unless the owner widens it (IH-D2).

### IH1: one counting entry

**Criteria (p1):**
- `count_mined_rules` and `load_mined_inputs` are public in
  `gnd.export.ilp_service`. `grep -rn "_mined_inputs" tools` finds nothing;
  today it finds `hold()`;
- one admitting import calls `ilp_amie.relation_table` once and
  `ilp_amie.pairs` once. A test counts the calls; today each is 2, so the
  test is red first;
- `ilp_amie.provenance` builds each rule's examples from the counted pairs;
  `gnd.export.ilp_amie` imports nothing from `gnd.discover`;
- `count_mined_rules` raises only mapping refusals and `too-large`. A test
  feeds it a rule that does not hold and gets counts back, not a refusal;
- `facts-mismatch` precedes every mapping refusal. The pin test is shown
  red against a reordering mutant;
- the refusal-order test pins `MAPPING_REFUSALS` and `COUNT_REFUSALS`
  against the tables in `docs/reference/ilp-bridge.md`. It is shown red
  against a swapped tuple (IH-R4);
- IH-R2 holds:
  - the IL4 and IL-close goldens, the retained AMIE replays
    (`tests/test_ilp_amie.py::test_t9_the_recorded_run_replays`) and the
    comparison golden `tests/fixtures/ilp_learners/il6/comparison.json` are
    byte-identical;
  - the AMIE `adapter_version` stays 2;
- the RF6 census successor is regenerated and listed. The following exit 0:
  `tests/test_rf6_query_policy.py`, the RF6 successor tests,
  `tests/test_gnd_arch.py` and the layer checks.

### IH2: own-reference subtype joins

**Criteria (p1):**
- a fixture reproduces today's false `support-mismatch`, red at IH1's head.
  It is the own-reference fixture with `manager_no`'s primitive set to
  String, and the population's manager values and `manages` rows changed to
  match;
- per IH-D1, either (a) the join counts as the checker counts it and the
  import admits the rule, or (b) the import refuses it by a new name before
  any count;
- R1 (`test_r1_an_own_reference_subtype_is_its_own_family`, differing
  primitives) still refuses with exit 3, never exit 70. **Under (b) its
  asserted name moves** from `support-mismatch` to the new name, an
  owner-recorded test change. Under (a) it is unchanged;
- under (a), the AMIE `adapter_version` becomes 3, and every moved golden
  and export digest is named. Under (b), no fixture golden moves.

### Close

- a question sweep over every row;
- the local CI run on the PR head (IH-R3);
- a close review per IH-D6 (p1);
- a PR;
- owner acceptance, recorded separately.

## 5. Documentation, skill and compatibility surfaces

| Surface | Phase | Change |
|---|---|---|
| `docs/reference/ilp-bridge.md`, refusal tables | IH2 | the new refusal at its position, or the spelling |
| `docs/release-notes.md` | IH2 | one bullet for the changed refusal or admission |
| `gnd.export.ilp_service` public names | IH1 | `MinedInputs`, `MinedCount`, `load_mined_inputs`, `count_mined_rules`; the identity alias `_mined_inputs`; RF6 successor regenerated |
| `gnd.export.ilp_amie` | IH1 | `provenance` |
| Skills | none | no skill names the mined import's internals |

## 6. Risks and required controls

| Risk | Control |
|---|---|
| A "refactor" changes an exit or a byte | IH-R2; golden and replay tests run unchanged |
| The entry swallows the import's admission checks | §2: only mapping refusals and `too-large` move; a test feeds a rule that does not hold |
| Rendering moves and reorders refusals | §2: the digest stays in the import; a pin test, red against a mutant |
| A review finding needs a learner run | IH-R1: carried, never reproduced live |
| Main goes red again after a focused close gate | IH-R3 |
| IH2 (a) moves export bytes the retained runs read (p1) | Tagging only the components that hold an own-reference subtype leaves `facts.tsv` byte-identical for staffing and north, so the retained run records' `facts_sha256` stays valid. Only `export.json` (`adapter_version`) and the export digests move. The import does not select a spelling by version |

## 7. Out of scope

- Any learner, solver or model run (IH-R1). This covers IL1-Q6, IL2-Q2,
  IL3-Q3 and IL-close-Q2.
- IL5-Q5 and IL5-Q6: changes to verbalization and `gnd.agents`.
- New learners, FastLAS, an integer-programming learner.
- The source changes of #47, #50, #52 and #53, unless IH-D2 widens IH0 (p1).
- Repository settings, such as making cloud CI a required check. IH-R3 binds
  this milestone's own close; a repository rule is the owner's separate act.

## 8. Execution, approval and review protocol

`auto=false`. Each phase follows process-phase:
- harvest;
- spec;
- owner gate;
- implement and verify;
- one adversarial reviewer ("one reviewer is one reviewer");
- refactoring review;
- record and commit.

IH0 is a review phase. Its "implementation" is the review and the fixes it
forces. Its own diff (the fixes) gets a separate one-reviewer pass.

The repository's bar for plan and close review is four reviewers. This plan
was reviewed by one reader (IH-D5 (o)), and the close instrument is IH-D6
(p1). Merge, publication and certification keep their separate owner
authorization.

## 9. Verification story and affected consumers

| Phase | Gate | Affected consumers |
|---|---|---|
| IH0 | the regression test for each fixed finding, red against its parent and then green; the focused tests of each touched module | per finding |
| IH1 | `tests/test_ilp_amie.py`, `tests/test_il_close.py`, `tests/test_il6_walk.py` (the comparison golden), `tests/test_rf6_query_policy.py`, the RF6 successor tests, `tests/test_gnd_arch.py`, and the new `tests/test_ih1_*.py` | `tools/ilp_comparison.py`, the IL6 walk, the docs replay of the comparison |
| IH2 | the new fixture's red/green tests; R1 and R2 in `tests/test_il_close.py`; the mined-import docs replay | `docs/reference/ilp-bridge.md` |
| Close | the local CI run, macOS, Python 3.13 and 3.11 (IH-R3) | everything |

Exact test node lists are fixed in each phase spec; they are not invented
here.

### Implementability sweep (author inspection, then reader 1)

- **IH0's subject exists:** the nine merges above, 37 files (p1).
- **IH1's names exist today:** `_mined_inputs`, `_Mined`,
  `ilp_amie.relation_table`, `pairs`, `mapped`, `count`, `Counts` and
  `MinedRule`.
- **IH1 is red first:** the import calls `relation_table` and `pairs` twice
  each, measured by reader 1 (p1).
- **`hold()` repeats the import's map-and-count loop** at
  `tools/ilp_comparison.py:123`.
- **IH2's case is reproducible** (reader 1, finding 11) (p1).
- **IH-R3's commands exist** in `.github/workflows/development.yml` and ran
  locally on 2026-10-29.

## 10. Owner decisions and open questions

| ID | Question | Readings and cost | Proposed |
|---|---|---|---|
| IH-D1 | An own-reference subtype join: count it or refuse it? | **(a) count:** spell the subtype component as one family and tag values with their primitive, only in components that hold an own-reference subtype, so equal raw values of one primitive meet as in the checker. The AMIE `adapter_version` goes to 3, so **every AMIE `export.json` golden and export digest moves**. `facts.tsv` moves only for models with an own-reference subtype, and a rule refused today is admitted (p1). **(b) refuse by name:** a new mapping refusal, `own-reference-join`, after `type-confused-join` and before any count. No fixture golden moves and the exit stays 3, but R1's asserted name changes from `support-mismatch` (p1) | (b): smaller and honest; (a) can follow if a real model needs it |
| IH-D2 | IH0's scope | IL's merges in `src/` and `tools/`: 37 files, about 3,350 changed lines. Adding the other milestones' merges: 64 files, about 3,800. Adding tests: about 14,000 lines, about 4× the reading (p1) | IL's merges, `src/` and `tools/` |
| IH-D3 | Include IL6-Q3, one outcome schema across live-run records? | It touches every adapter's evidence scripts and their retained outcomes. The retained runs are not re-run, so the schema would be applied to existing records | No: leave it with the evaluation milestone |
| IH-D4 | IH0's review instrument | **(a)** four local readers, each over the whole subject, as IL's plan review; **(b)** the maintained six-seat panel, which needs parent credentials; **(c)** one reader | (a) |
| IH-D5 | This plan's review instrument | **(a)** none; **(b)** one reader; **(c)** four readers, the repository's plan bar. (a) and (b) depart from that bar (p1) | **Ruled (b), 2026-10-29 (o):** "One reader". r2 has no review opinion |
| IH-D6 (p1) | The close review instrument | **(a)** four readers, the repository's close bar; **(b)** one reader, a departure; **(c)** the maintained panel | (a) |
| IH1-D1 (p1) | Where the facts digest is computed | **(a)** the import renders and compares it before calling the entry; the order is unchanged and the entry does not render. **(b)** the entry renders and returns the digest; one fewer step in the import, but `facts-mismatch` would follow mapping refusals unless the entry returns before mapping | (a) |
| IH1-D2 (p1) | `hold()`'s error order through the entry | **(a)** accept: mapping refusals now precede counting refusals; only error paths change, and the golden has none. **(b)** keep per-rule order in `hold()`: the entry loses one caller | (a) |
