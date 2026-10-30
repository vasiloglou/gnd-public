# ILP import hardening

r1, 2026-10-29. Planning only. **No plan or spec approval exists.**
Milestone: `ilp-import-hardening`. `auto=false`.
Inspection baseline: `fb03739` (main, after PR #64, which marked ilp-learners
closed and repaired three tests that PR #63 left red).

**Change tags:**
- `(o)` marks an owner answer or ruling, quoted where the owner's words exist.
- Untagged text is the author's r1 proposal.
- Planning authorship is not approval.

## Goal, status and completion predicates

The ilp-learners milestone (IL) closed on 2026-10-29 and carried the debt
in its mined-rule import (`gnd import mined-rules`) to "the next milestone
that changes the mined import" (`../ilp-learners/009-milestone-close.md`,
"Carried forward"). Its diff was never reviewed as a whole: the owner chose
at acceptance not to have one first (`../ilp-learners/010-owner-acceptance.md`).

This milestone:
- reviews IL's whole diff, so that the debt it fixes is the debt that is
  actually there;
- gives the mined import one public counting entry and one rendering pass;
- settles IL4-Q1's remainder: a join through an own-reference subtype is
  either counted as the checker counts it or refused by its own name;
- runs no learner. Every test reads committed fixtures or retained outputs.

The owner asked for this plan on 2026-10-29 (o), in answer to "Should I
draft that milestone plan with `start-milestone`?": "yes". The plan it
answered: "start the hardening milestone with the diff review as its first
phase". The request is planning authority only.

Completion requires:

1. **IH0, the diff review:**
   - one review opinion per reader over `07f4d45^..fb03739` restricted to
     `src/` and `tools/` (64 files, about 3,600 added lines), with every
     finding reproduced before it is believed;
   - every finding triaged blocking, hardening or completeness, and given a
     disposition: fixed in IH0 with a regression test shown red, assigned to
     IH1 or IH2 by name, or carried with a target.
2. **IH1, one counting entry:**
   - a public `count_mined_rules` entry that `gnd import mined-rules` and
     `tools/ilp_comparison.hold()` both call; no module outside
     `gnd.export.ilp_service` imports `_mined_inputs`;
   - the mined facts are rendered once per import, and `facts-mismatch` and
     the count read that one rendering (IL-close-Q1);
   - the per-rule provenance builder lives in `gnd.export.ilp_amie`
     (IL4-Q3 remainder);
   - behaviour preserved: every IL4 and IL-close golden, the retained AMIE
     replays and the committed comparison table are byte-identical.
3. **IH2, own-reference subtype joins (IL4-Q1 remainder):** a join through
   an own-reference subtype either counts as the checker counts it, or is
   refused by a refusal name of its own before any count, per IH-D1. A
   regression test reproduces today's false `support-mismatch` first.
4. **Every phase has:** approval, focused checks, one independent diff
   review, a refactoring review and a record.
5. **Close has:** a question sweep, **the full local CI matrix on the PR
   head** (IH-R3), a PR, and owner acceptance recorded separately.

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
| IH-R2 | **Refactors preserve bytes.** IH1 is behaviour-preserving: every golden, retained replay and the comparison table stay byte-identical, and the AMIE `adapter_version` stays 2. A change that moves a golden is not a refactor and returns to the owner gate. |
| IH-R3 | **The close gate is the full local CI.** Before the close PR merges, the development workflow's three jobs (candidate, regression with the full suite, installed) run on the PR head under Python 3.13 and 3.11 and exit 0. Focused gates remain the per-phase gate. This answers IL's close, whose focused gate let three failing tests reach main. |
| IH-R4 | **Refusals keep their order.** A new refusal name enters `MAPPING_REFUSALS` or `COUNT_REFUSALS` (`gnd.export.ilp_amie`) at one named position. The documented order in `docs/reference/ilp-bridge.md` is its one home, and a test pins the tuple against it. |

## 1. Scope, sources and authority

### Sources

| Source | What it assigns |
|---|---|
| `../ilp-learners/009-milestone-close.md`, "Carried forward" | IL4-Q3 remainder, IL-close-Q1, the `hold()` import, IL4-Q1 own-reference subtypes; the whole-diff review left to the owner |
| `../ilp-learners/010-owner-acceptance.md`, "Boundary" | "The milestone diff as a whole has had no review" |
| `../ilp-learners/notes/phase-IL-close-spec.md` §6.1, ILC-F8 | the family spelling and why an own-reference subtype was split out |
| `../ilp-learners/notes/phase-IL4-agent-review.md`, finding 2 | the original subtype-join defect |
| `../ilp-learners/007-phase-IL6.md`, refactoring review | the deferred `hold()` private import |
| this session's local CI on PR #64 (2026-10-29) | three tests on main failed after IL's focused close gate; IH-R3 |

### Harvested obligations

| Obligation | Source | Owner phase / gate |
|---|---|---|
| Review IL's whole diff | 009 "Carried forward", last row; 010 "Boundary" | IH0 |
| One public "count mined rules" entry; `hold()` stops importing `_mined_inputs` | 009, `007` refactoring deferral row | IH1 |
| One rendering pass for `facts-mismatch` and the count | 009, IL-close-Q1 | IH1 |
| Per-rule provenance moves into `ilp_amie` | 009, IL4-Q3 (remainder) | IH1 |
| Count an own-reference subtype join, or refuse it by name | 009, IL4-Q1 (own-reference subtypes) | IH2 (IH-D1) |
| Close gate runs the full local CI | IH-R3 | close |

### Not harvested (carried elsewhere by IL's close)

IL1-Q6, IL2-Q2, IL3-Q3 and IL-close-Q2 need learner or clingo runs and go to
a later evaluation milestone. IL5-Q5 and IL5-Q6 change verbalization and
`gnd.agents`, which other milestones own. IL6-Q3 (one outcome schema) is
offered at IH-D3.

## 2. Contract proposal and product behaviour

**No wire changes in IH0 or IH1.** `gnd-mined-run/1`, `gnd-ilp-import/1`
and the AMIE export tree are unchanged; `gnd import mined-rules` keeps its
arguments, exits and refusal order.

### The counting entry (IH1)

```python
# gnd.export.ilp_service
@dataclass(frozen=True)
class MinedCount:
    inputs: MinedInputs          # today's _Mined, made public
    facts_sha256: str            # the digest of the one rendering of amie/facts.tsv
    rules: tuple[MinedRule, ...]
    counts: tuple[Counts, ...]

def load_mined_inputs(model_path: Path, population_path: Path) -> MinedInputs: ...
def count_mined_rules(inputs: MinedInputs, parsed: list[dict[str, Any]]) -> MinedCount: ...
```

`count_mined_rules` renders once, then maps and counts each rule in
`MAPPING_REFUSALS` then `COUNT_REFUSALS` order, raising `IlpError` with the
name it raises today. The import compares `facts_sha256` with the run record
after the call. `hold()` calls the same two functions.

**Order constraint.** Today `facts-mismatch` is raised before any mapping
refusal. If the rendering moves into `count_mined_rules`, a record with
wrong facts and an unmappable rule would refuse by the mapping name. The IH1
spec keeps the current order: the import calls the rendering step first and
passes it in, or `count_mined_rules` returns before mapping. The spec fixes
which, with a test pinning `facts-mismatch` ahead of every mapping refusal.

### Own-reference subtype joins (IH2)

Today `ilp_amie.family` puts an own-reference subtype in a family of its own,
so `manager:1` never meets `staff:1`. The checker compares raw values, so
where both raw values are equal and of one primitive, the checker joins
them and GND's count does not: a false `support-mismatch`
(`tests/test_il_close.py::test_r1_an_own_reference_subtype_is_its_own_family`
pins the refusal for differing primitives). IH-D1 chooses the repair.

## 3. Dependencies and artifact homes

| Artifact | Home |
|---|---|
| Plan, specs, reviews | `.gnd-planning/milestones/ilp-import-hardening/notes/` |
| Phase and close records | `.gnd-planning/milestones/ilp-import-hardening/NNN-*.md` |
| Red/green and gate evidence | `.gnd-planning/milestones/ilp-import-hardening/evidence/IH<n>/` |
| Code | `src/gnd/export/ilp_service.py`, `src/gnd/export/ilp_amie.py`, `tools/ilp_comparison.py` |
| Tests | `tests/test_ih_*.py`; fixtures under `tests/fixtures/ilp_learners/` |
| Docs | `docs/reference/ilp-bridge.md` (refusal order, mined import) |

Dependencies are linear: IH0 → IH1 → IH2 → close. IH1 needs IH0's findings,
because a finding in the counting path changes what IH1 moves. IH2 needs
IH1's counting entry, because its refusal or spelling enters there. No phase
is optional.

`tools/gnd_layers.json` must assign any new home; IH1 adds none, because it
moves names within `gnd.export`.

## 4. Phases, criteria and residuals

### IH0: review of IL's whole diff

**Deliverables:** the review opinions retained verbatim under `notes/`, a
triage table, and fixes for blocking findings.

**Criteria:**
- the reviewed range is `07f4d45^..fb03739`, paths `src/` and `tools/`; the
  commits that already had a phase or predicate-7 review are re-read, not
  skipped;
- each finding is reproduced before it is believed; one that cannot be
  reproduced without a learner run is carried (IH-R1);
- each **blocking** finding is fixed in IH0 with a regression test shown red
  against `fb03739`; each hardening or completeness finding is fixed, or
  assigned to IH1 or IH2 by name, or carried with a target;
- the focused gate for every touched module exits 0.

**Residual:** a review is a disagreement locator, not a proof. Tests, docs
and evidence in the range are out of its scope unless the owner widens it
(IH-D2).

### IH1: one counting entry

**Criteria:**
- `count_mined_rules` and `load_mined_inputs` are public in
  `gnd.export.ilp_service`; `grep -rn "_mined_inputs" src tools` finds only
  `ilp_service`, or nothing;
- the import renders `amie/facts.tsv` once (a test counts the calls to
  `ilp_amie.render` per import: exactly 1);
- the per-rule provenance builder is `ilp_amie.provenance(...)`;
- IH-R2: the IL4 and IL-close goldens, the retained AMIE replays and the
  comparison golden `tests/fixtures/ilp_learners/il6/comparison.json` are
  byte-identical; the AMIE `adapter_version` stays 2;
- `facts-mismatch` still precedes every mapping refusal (a test pins it);
- RF6 census and `tools/gnd_layers.json` checks exit 0.

### IH2: own-reference subtype joins

**Criteria:**
- a fixture with an own-reference subtype whose raw values equal its
  supertype's, of one primitive, reproduces today's false `support-mismatch`
  (red at IH1's head);
- per IH-D1, either (a) the join counts as the checker counts it and the
  import admits the rule, or (b) the import refuses it by a new name before
  any count;
- `test_r1_an_own_reference_subtype_is_its_own_family` (differing
  primitives) still refuses, never exits 70;
- under (a) the AMIE `adapter_version` becomes 3 and every moved golden is
  named; under (b) no golden moves.

### Close

A question sweep over every row, the full local CI matrix on the PR head
(IH-R3), a close review per IH-D4, a PR, and owner acceptance recorded
separately.

## 5. Documentation, skill and compatibility surfaces

| Surface | Phase | Change |
|---|---|---|
| `docs/reference/ilp-bridge.md`, mined import and refusal order | IH2 | the new refusal or spelling |
| `docs/release-notes.md` | IH2, close | one bullet for an exit change |
| `gnd.export.ilp_service` public names | IH1 | two new public names; RF6 census rows regenerated |
| Skills | none | no skill names the mined import's internals |

## 6. Risks and required controls

| Risk | Control |
|---|---|
| A "refactor" that changes an exit or a byte | IH-R2; golden and replay tests run unchanged |
| Moving the rendering reorders refusals | §2 order constraint; a pinned test |
| A review finding that needs a learner run | IH-R1; carried, never reproduced live |
| Another red main after a focused close gate | IH-R3 |
| IH2 (a) changes how AMIE reads facts, while the retained runs read the old spelling | the retained IL4 runs are not re-run; their replays stay on adapter 2 inputs, and the spec names how |

## 7. Out of scope

- Any learner, solver or model run (IH-R1); IL1-Q6, IL2-Q2, IL3-Q3,
  IL-close-Q2.
- IL5-Q5, IL5-Q6: verbalization and `gnd.agents` changes.
- New learners, FastLAS, an integer-programming learner.
- Repository settings, such as making cloud CI a required check. IH-R3 binds
  this milestone's own close; a repository rule is the owner's separate act.

## 8. Execution, approval and review protocol

`auto=false`. Each phase follows process-phase: harvest, spec, owner gate,
implement and verify, one adversarial reviewer ("one reviewer is one
reviewer"), refactoring review, record and commit. IH0 is a review phase:
its "implementation" is the review and the fixes it forces; its own diff
(the fixes) gets a separate one-reviewer pass.

The plan's review instrument is IH-D5. Merge, publication and
certification keep their separate owner authorization.

## 9. Verification story and affected consumers

| Phase | Gate | Affected consumers |
|---|---|---|
| IH0 | the regression tests for each fixed finding, shown red then green; the focused tests of each touched module | per finding |
| IH1 | `tests/test_ilp_amie.py`, `tests/test_il_close.py`, `tests/test_il6_walk.py` (the comparison golden), RF6 and layer checks | `tools/ilp_comparison.py`, the IL6 walk, docs replay of the comparison |
| IH2 | the new fixture's red/green tests; R1 and R2 in `tests/test_il_close.py`; the mined-import docs replay | `docs/reference/ilp-bridge.md` |
| Close | the full local CI matrix, Python 3.13 and 3.11 (IH-R3) | everything |

Exact test node lists are fixed in each phase spec; they are not invented here.

### Implementability sweep (author inspection, not review)

- IH0's range exists: `07f4d45` is IL's first commit, `fb03739` is main.
- IH1's names exist today: `_mined_inputs`, `_Mined`, `ilp_amie.render`,
  `mapped`, `count`, `Counts`, `MinedRule`; `hold()` repeats the
  import's map-and-count loop at `tools/ilp_comparison.py:123`.
- IH2's fixture shape exists: `tests/fixtures/ilp_learners/close/ownref.orm.yaml`
  differs from the needed case only in `manager_no`'s primitive.
- IH-R3's commands exist in `.github/workflows/development.yml` and ran
  locally on 2026-10-29.

## 10. Owner decisions and open questions

| ID | Question | Readings and cost | Proposed |
|---|---|---|---|
| IH-D1 | An own-reference subtype join: count it or refuse it? | (a) **count**: spell the whole subtype component as one family and tag values with their primitive, so equal raw values of one primitive meet as in the checker; AMIE adapter 3, export goldens move for models with own-reference subtypes, and a rule that is refused today is admitted. (b) **refuse by name**: a new mapping refusal, `own-reference-join`, before any count; no golden moves; exit stays 3, only the name changes | (b): smaller and honest; (a) can follow if a real model needs it |
| IH-D2 | IH0's scope: `src/` and `tools/` only, or tests, docs and evidence too? | The source diff is about 3,600 lines over 64 files; with tests about 14,000 lines over 168 files; the whole range is 539 files | `src/` and `tools/` |
| IH-D3 | Include IL6-Q3, one outcome schema across live-run records? | It touches every adapter's evidence scripts and their retained outcomes; the retained runs are not re-run, so the schema would be applied to existing records | No: leave it with the evaluation milestone |
| IH-D4 | IH0's review instrument | (a) four local readers, each over the whole source range, as IL's plan review; (b) the maintained six-seat panel (needs parent credentials); (c) one reader | (a) |
| IH-D5 | This plan's review instrument | (a) none; the owner reads it; (b) one reader; (c) four readers, the repository's plan bar | (b): a small plan whose largest step is itself a review |
