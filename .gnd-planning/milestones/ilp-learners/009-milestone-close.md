---
milestone: ilp-learners
station: milestone-close
skill: "n/a -- repository development under the approved close plan (notes/close-plan.md), not a gnd-solve station"
scope: IL-close
date: 2026-10-29
source_base: a75b328
gate:
  command: "uv run pytest -q -p no:randomly <evidence/IL-close/gate-files.txt>"
  exit: 0
  output: "1281 passed, 24 deselected in 273.13s (0:04:33)"
  note: >-
    The part A gate (008), on the final code bytes: IL6's 23-file gate, which
    is cumulative over IL1 to IL6, plus tests/test_il_close.py. T9 on the same
    bytes: both wheel origins, 229 tutorial blocks each. Parts B and C change
    planning text only.
slow_cadence:
  command: "uv run pytest -q"
  trigger: "explicit owner selection or separately configured CI"
  reason: "outside the milestone's impact closure; the reduced v6.3 selection was run"
---

# ILP learners -- milestone close

**Status: draft for the close review (part D).** Owner acceptance is recorded
separately, after the PR; this record does not claim it.

The close follows the [close plan](notes/close-plan.md), approved by the owner
on 2026-10-29: A repairs, B plan repairs, C the question sweep, D the close
review, E this record and the PR.

## What the milestone shipped

Five learners on one bridge, each run for real, with every result re-checked
by GND (`002` to `008`, PRs #56, #57, #58, #60, #61, #62 and this close):

| Adapter | Learner | Runs | Outcome of the run of record |
|---|---|---|---|
| `popper` | Popper 5.0.1 | 3 (2 and 3 owner-ruled) | `rendering-rejected`; invocation 3 admitted |
| `ilasp` | ILASP 4.4.1 | 1 | refused `empty-antecedent` (recorded as is, IL2-F7) |
| `llm` | the `claude` agent | 1 | admitted |
| `rules` | wittgenstein RIPPER | 1 | admitted, support 4/5 |
| `amie` | AMIE 4.0.0 | 2 (2 owner-ruled) | refused `does-not-hold`; invocation 2 admitted |

- **One learner registry** (IL1), with the join check 9b and SWI octal escapes.
- **ILASP** export and closed ASP reader (IL2); **rule sets** feature export and
  reader (IL3); **AMIE** typed triples, `gnd import mined-rules` and GND's own
  head-pair count (IL4); the **LLM proposer** (IL5).
- **The comparison** (IL6): `tools/ilp_comparison.py`, the table in
  `docs/reference/ilp-bridge.md`, and `docs/how-to/compare-ilp-learners.md`,
  which replays every run from committed outputs.
- **The close repairs** (`008`): subtype joins counted by family; the mined
  run record binds the facts the miner read; infix comparison joins; ILASP
  `off-threshold`; the Popper extractor and booleans; public names; the
  comparison tool fails loudly.

## Completion predicates (plan, "Goal, status and completion predicates")

| # | Predicate | Verdict | Where |
|---|---|---|---|
| 1 | IL1: one registry; IK5/IK6/RF1 goldens byte-identical except D12/D13 refusals; join check; octal escapes; one real Popper run, replayed | MET WITH RESIDUAL: the owner-recorded amendments moved named IK5 goldens (IL1-Q7, plan repaired) | `002` |
| 2 | IL2: ILASP task golden under two seeds; learned rules through the shared checker; one run replayed | MET (FastLAS not kept, IL2-D1) | `003` |
| 3 | IL3: thresholded feature export; positive single-feature conjuncts; refusals by name; all-or-nothing; one run replayed | MET; one run read as the rule-set result although RIPPER is not deterministic under its seed (IL3-F5, carried) | `005` |
| 4 | IL4: typed relations; `guarded` import; GND support and confidence; `support-mismatch`; holds only; one run replayed | MET; subtype joins were false refusals until `008` | `006`, `008` |
| 5 | IL5: `llm` entry; JSON through the shared re-check; one run after D8 | MET | `004` |
| 6 | IL6: the walk exits as recorded; the comparison table; docs, skills, entry points with census checks | MET; the walk's wording repaired (IL4-Q5) | `007` |
| 7 | Every phase: approval, focused checks, one reviewer, refactoring review, a record | MET | `002`–`008` |
| 7 | Close: four-reviewer evidence; question sweep; PR; owner acceptance recorded separately | sweep below; review in part D; PR and acceptance pending | this record |

## Plan repairs (part B)

Applied to `notes/ilp-learners-plan.md` at the owner's direction without
review (plan §8, p2), each tagged `(c)`:

| Row | Repair |
|---|---|
| IL3-Q4 | §1 names RIPPER, a sequential-covering learner; integer-programming and certifiable learners were not integrated |
| IL4-Q5 | IL6's walk: labelled adapters on refunds, `amie` on the staffing fixture |
| IL4-Q5 | §4 IL4: "the miner's support, its count of distinct head pairs" |
| IL2-Q4 | IL-R9: the learner's own timeout "where the learner has one" |
| IL1-Q7 | §9 IL1 row: the IK5 goldens moved by owner-recorded amendments |
| IL6 refuted premise 2 | §5: the pin sites include gnd-solve's Station 6 |
| Status | The header records the approval in `001-plan-gate.md`; "No approval exists" and "Planning only … awaits approval" are replaced by pointers to the records |

## Question sweep (part C)

Every open-question row from `002` to `008`.

| Row | Disposition |
|---|---|
| IL1-Q1 | **fixed** in `008` (C4) |
| IL1-Q2 | **discharged**: IL5 added `binds`, and `contract` varies by entry (IL4) |
| IL1-Q3 | **discharged** in IL2 |
| IL1-Q4 | **fixed** in `008` (C6) |
| IL1-Q5 | **fixed** in `008` (C8a, C8b) |
| IL1-Q6 | **carried**: reproducibility and a larger domain, to a later evaluation milestone (owner, 2026-10-29) |
| IL1-Q7 | **plan repaired** (part B) |
| IL2-Q1 | **fixed** in `008` (C7); ILC-F5 accepted |
| IL2-Q2 | **carried**: the ILASP bias amendment and a rerun, to a later evaluation milestone |
| IL2-Q3 | **fixed** in `008` (C5) |
| IL2-Q4 | **plan repaired** (part B) |
| IL5-Q1, IL5-Q2, IL5-Q3 | **closed**: ruled 2026-10-28 |
| IL5-Q4 | **discharged** in IL3 (`live_common`) |
| IL5-Q5 | **carried**: to the milestone that owns verbalization (owner: "Defer both") |
| IL5-Q6 | **carried**: to the milestone that owns `gnd.agents` |
| IL3-Q1 | **closed**: the census row is enough (owner) |
| IL3-Q2 | **fixed** in `008` (C9) |
| IL3-Q3 | **carried**: RIPPER's run-to-run variation, to a later evaluation milestone |
| IL3-Q4 | **plan repaired** (part B) |
| IL4-Q1 | **fixed** in `008` (C1, R1, R2) |
| IL4-Q2 | **fixed** in `008` (C2, R4, R6) |
| IL4-Q3 | **partly fixed**: `ilp.export_value` is public (C9). Moving the per-rule provenance into `ilp_amie` was not in the ruled scope; **carried** with IL-close-Q1 |
| IL4-Q4 | **discharged** in IL6: invocation 2 ran and was admitted |
| IL4-Q5 | **plan repaired** (part B) |
| IL6-Q1 | **fixed** in `008` (C8c) |
| IL6-Q2 | **fixed** in `008` (C3, R5) |
| IL6-Q3 | **carried**: one outcome schema across live-run records, to a later milestone |
| `007` refactoring deferral | `tools/ilp_comparison.hold()` imports the private `ilp_service._mined_inputs`. **Carried** with IL-close-Q1: a public "count mined rules" entry serves the tool and the import |
| ILC-F5, ILC-F6 | **accepted** by the owner, 2026-10-29 |
| IL-close-Q1 | **carried**: one rendering pass for `facts-mismatch` and the count |

**Carried forward, for the successor:**

| Row | Target |
|---|---|
| IL1-Q6, IL2-Q2, IL3-Q3, IL6-Q3 | a later evaluation milestone: reproducibility, the ILASP bias rerun, RIPPER's variation, one outcome schema |
| IL5-Q5 | the milestone that owns verbalization |
| IL5-Q6 | the milestone that owns `gnd.agents` |
| IL4-Q3 (remainder), IL-close-Q1, the `hold()` import | the next milestone that changes the mined import: one public counting entry, one rendering pass |

## Close review (part D)

Pending: the maintained panel over the plan (spec), this record (results) and
the close plan (delta).

## Boundary -- what the milestone does NOT establish

- **Which learner is better.** Each row is one run on one small example.
- **Reproducibility.** No run was repeated to measure it.
- **Any learner in CI.** Tests replay committed outputs; nothing installs or
  runs a learner.
- **That an own-reference subtype's joins are counted.** They are refused,
  never admitted (`008`, ILC-F8).
- **Acceptance.** The owner's acceptance is a separate record.
