# ilp-learners close plan

r1, 2026-10-29. **Approved by the owner, 2026-10-29:** "The close plan is
approved. Draft the IL-close repair spec and stop at its owner gate." The
approval was given over SHA-256 `e636b452…d3d7d`, the bytes before this status line.

Baseline: `a75b328` (main, after PR #62, the IL6 merge). All six phases are
recorded: `002` to `007`.

The plan's §8 close has four parts: four-reviewer evidence, a question sweep,
a PR, and separately recorded owner acceptance. The owner chose to fix four
questions at close instead of deferring them, so the close has a repair part
first. That part is phase-shaped work, and it runs under process-phase.

| Part | What | Instrument | Record |
|---|---|---|---|
| A | **Close repairs**: the code fixes ruled below | spec, owner gate, one reviewer, refactoring review (process-phase) | `notes/phase-IL-close-spec.md`, `008-close-repairs.md` |
| B | **Plan repairs**: wording fixes at the owner's direction, without review (plan §8, p2) | owner direction | listed in the close record |
| C | **Question sweep**: every row from `002` to `008` gets a disposition | this plan's ruling table | the close record |
| D | **Close review**: four reviewers over the whole milestone | the maintained panel | `notes/close-review-*.md` |
| E | **Close record and PR**, then owner acceptance recorded on its own | AGENTS.md | `009-milestone-close.md` |

Commits use the `IL-close` scope, which the IL6 census test already accepts.

## Owner rulings on the open questions (2026-10-29)

Ruled through two question rounds in this session. The answers are quoted, and
each option's text appears with it.

| Row | Question | Ruling | Part |
|---|---|---|---|
| IL4-Q1 | AMIE joins through a subtype count as never holding | **"Fix it now"**: spell entities by a shared root type so the count agrees with the checker | A |
| IL4-Q2 | `gnd-mined-run/1` does not bind the export digest | **"Bind it now"**: re-derive the retained `reported.json` for both AMIE runs | A |
| IL6-Q2 | `hold()` silently counts an unmappable rule as not holding | **"Fail loudly"** | A |
| IL1-Q1, IL2-Q3 | Infix comparisons in check 9b; the export's thresholds handed to the ASP reader | **"Do both now"** | A |
| IL1-Q4 | `extract_program` truncates without saying so | **fix** (author fixes, all four selected) | A |
| IL1-Q5, IL6-Q1 | Missing tests: T5c pair count, a `type_closures` subtype test, refusal names per adapter section | **fix** | A |
| IL2-Q1 | The Popper reader reads a bare `true` as a string | **fix** | A |
| IL3-Q2, IL4-Q3 | `ilp_popper._threshold_rows` and `ilp._value` made public | **fix** | A |
| IL3-Q1 | The RF6 scanner cannot see the rules adapter's module-key read | **"Census row enough"**: no code; closed | C |
| IL5-Q5, IL5-Q6 | Verbalization structural lines; recording the agent's version | **"Defer both"** to the milestones that own verbalization and `gnd.agents` | C |
| IL1-Q6, IL2-Q2, IL3-Q3, IL6-Q3 | Reproducibility, an ILASP bias amendment and rerun, one outcome schema | **"Later eval milestone"**: carried rows; no learner runs at close | C |

Rows needing no ruling, for the sweep: IL1-Q2 (discharged by IL4 and IL5),
IL1-Q3 (discharged in IL2), IL4-Q4 (discharged in IL6), IL5-Q1 to IL5-Q3
(ruled and closed), IL5-Q4 (discharged in IL3 by `live_common`), IL2-Q4 and
the plan-wording rows (Part B).

## Part A: what the repair spec must decide

These are design questions for the spec's owner gate. None is decided here.

1. **IL4-Q1, the shared root type.** Which root spells a value whose type has
   several supertypes? Candidates: refuse that join by name, use the
   lexicographically first root, or use the set of roots. The spec states
   which IK and IL goldens move. The AMIE run-of-record outcomes must not
   change: neither staffing run joins through a subtype. That is a test.
2. **IL4-Q2, the binding.** Choices: add `export_sha256` within
   `gnd-mined-run/1` as a required field (every retained `reported.json` is
   re-derived and IL6's shipped `staffing/learners/*/reported.json` and its
   walk goldens move), or bump to `/2` and keep a `/1` reader. The ruled
   re-derivation is mechanical: the digest is already recorded in each run's
   `outcome.json`. No learner run.
3. **IL1-Q1.** The IK5 goldens that move are listed, with each refusal it
   adds. An infix comparison on a variable of the wrong type becomes
   `type-confused-join`.
4. **IL2-Q3.** An off-threshold constant becomes a named refusal from the ASP
   reader. ILASP's retained run is unchanged: its refusal,
   `empty-antecedent`, comes first.
5. **IL6-Q2.** `tools/ilp_comparison.py` exits non-zero and names the rule.
   This needs a test with a planted unmappable rule.
6. **The comparison stays true.** After Part A, `tools/ilp_comparison.py`
   still reproduces `comparison.json` and the walk page still passes 12
   blocks, or the spec names every row or digest that moves, and why.

Gate: IL6's gate files plus the new tests; T9 (both wheel origins) once,
because shipped files may move under IL4-Q2.

## Part B: plan repairs (proposed wording)

The plan file is `notes/ilp-learners-plan.md`. Each repair is a wording change
that records what happened. None changes an approved criterion's intent.

| Row | Where | Now | Proposed |
|---|---|---|---|
| IL3-Q4 | §1, line 43 | "Boolean rule sets (integer-programming or certifiable rule-set learners)" | "Boolean rule sets (a sequential-covering learner, RIPPER, IL3-D1 (a); integer-programming and certifiable learners were not integrated)" |
| IL4-Q5 | §4 IL6, line 104 | the walk "runs the IK6 refunds example through" every adapter | labelled adapters on the refunds example; `amie` on the committed staffing fixture, which has the relations a miner needs |
| IL4-Q5 | §4 IL4, line 358 | "the miner's positive-example count" | "the miner's support, its count of distinct head pairs" (AMIE prints no positive examples; IL4-F4) |
| IL2-Q4 | §0 IL-R9 | "the learner's own timeout below the wall clock" | add: "where the learner has one; ILASP 4.4.1 and the agent CLIs have none, so `learner-timeout` is unreachable there and the wall clock is the bound" |
| IL1-Q7 | §9 IL1 row, line 660 | "goldens unchanged except listed C2 cases" | "goldens unchanged except the C2 cases and the IK5 goldens named by the owner-recorded amendments" |
| IL6 refuted premise 2 | §5, line 583 | "the two pin sites" | "the pin sites: gnd-export, gnd-model-evolve, and gnd-solve's Station 6 (IL6 review R3)" |
| Plan status line | line 3 | "Draft; awaiting owner approval" | approved as recorded in `001-plan-gate.md` (approval was recorded there, not in the plan) |

## Part D: the close review

The four-reviewer bar (plan §8). Run through the maintained panel, which
needs the parent credentials; the launcher is
`uv run python tools/run_gnd_review_panel.py`. The input is the close bundle:
the plan with its repairs, records `002` to `008`, the close record draft, and
the milestone diff `07f4d45^..HEAD`. The stop rule in
`process-phase/references/review-convergence.md` bounds the number of rounds.

## Order

A (spec, then STOP for the owner gate, implement, review, record) → B → C →
D → E. B and C can be written while A is in review. They are recorded only
once A's record exists, because A changes some rows' dispositions.
