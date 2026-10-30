# IH0: review of the ilp-learners source changes

**Status:** r2 draft (p1), awaiting the plan gate and then this phase's
owner gate. `auto=false`. Nothing below is approved. r1 (`269663b5…db81`)
had one reader's opinion ([plan review r1](plan-review-r1-reader-1.md),
findings 1, 12, 13); **r2 bytes carry no review opinion.**

## Provenance

- Plan: `ilp-import-hardening-plan.md` r2, §4 "IH0", §9 IH0 row, §10
  IH-D2 and IH-D4. The plan has no approval.
- Source of the obligation (p1): the owner's answer of 2026-10-29 (o), "yes",
  to the plan whose first phase is the diff review. `../ilp-learners/009-milestone-close.md`
  left the review to "the owner's call at acceptance", and
  `../ilp-learners/010-owner-acceptance.md` ("Boundary") records that none ran.
- Earlier reviews of parts of the range, which IH0 does not replace:
  - IL1 to IL6 phase reviews, `../ilp-learners/notes/phase-IL<n>-agent-review.md`;
  - the close review, `../ilp-learners/notes/phase-IL-close-agent-review.md`;
  - the predicate-7 review, `../ilp-learners/notes/phase-IL-close-p7-review.md`.
  Each covered only its own commits; none read the range as one diff.

## Obligations

| Obligation | Source | Discharged in |
|---|---|---|
| Review IL's source changes as one change | plan §4 IH0; the owner, 2026-10-29 (o) (p1) | §Design 1–3 |
| Re-read commits that already had a phase or predicate-7 review, not skip them (p1) | plan §4 IH0 | §Design 3 (the brief) |
| Reproduce every finding before believing it | plan §4 IH0; process-phase step 4 | §Design 4 |
| Carry a finding that needs a learner run, never run one | IH-R1 | §Design 4 |
| Fix blocking findings with a regression shown red against the fix's parent commit (p1) | plan §4 IH0 | §Design 5; §Tests |
| Residual, copied forward (p1): "a review is a disagreement locator, not a proof. Tests, docs and evidence are out of its scope unless the owner widens it (IH-D2)." | plan §4 IH0 | §Out of scope; the record's boundary |
| Assign every other finding to IH1, IH2 or a carried row | plan §4 IH0 | §Design 5 |
| Focused gate for every touched module | plan §9 IH0 row | §Tests |
| Refusal order has one home | IH-R4 | §Standing rules |

## Standing rules, bound to this phase

- **IK-R1 to IK-R12, IL-R1 to IL-R11:** bind any fix IH0 makes; a fix that
  touches a wire, a golden or an adapter version names it and returns to the
  owner gate (IL-R7).
- **IH-R1:** readers run no learner, solver or model; they may run the test
  suite and the committed replays.
- **IH-R2:** does not bind IH0's fixes, which may change behaviour; any
  moved golden is named in the record.
- **IH-R3:** binds the close, not IH0.
- **IH-R4:** a fix that adds a refusal name places it in the tuple and in
  the documented order in the same commit.
- **Subagent outputs** are confined to the session scratch directory; the
  retained copy under `notes/` is sanitized of home paths and usernames
  (IL-R10).

## Goal

Every finding over IL's merges in the scope IH-D2 fixes is reproduced,
triaged and disposed of; each blocking fix has a regression test that exits
non-zero against the fix's parent commit and zero after the fix (p1); the focused
gate of each touched module exits 0.

## Design

1. **The subject (p1).** IL's own first-parent merges, each read as
   `git diff m^1 m -- src tools`: `65fd6df` (#56), `426bd80` (#57),
   `75a397f` (#58), `e30eec8` (#59), `70266b5` (#60), `860e651` (#61),
   `a75b328` (#62), `7818be1` (#63), `fb03739` (#64). 37 files, +3,187/−161,
   judged at `fb03739` (proposed IH-D2). The merges #47, #50, #52 and #53 in
   the same range belong to other milestones and are out of scope. Readers
   get each merge's commit list (`git log --oneline m^1..m^2`) to attribute
   each finding to its originating commit.
2. **The readers** (IH-D4). Each reader gets the same brief and reads the
   whole range independently; none sees another's report. Each judges code
   at `fb03739`.
3. **The brief**, given verbatim to each reader:
   > Review the ilp-learners milestone's source changes in this repository:
   > the merges 65fd6df, 426bd80, 75a397f, e30eec8, 70266b5, 860e651,
   > a75b328, 7818be1 and fb03739, each read as `git diff m^1 m -- src tools`.
   > The milestone added learner adapters for ILASP, RIPPER, AMIE and an LLM
   > to the ILP bridge. Other merges between them (#47, #50, #52, #53) belong
   > to other milestones: do not review them. Earlier reviews each covered
   > one phase's commits; read IL's changes as one change, including commits
   > that already had a review.
   > Look for: wrong exits or refusal names, refusals in the wrong order,
   > inputs a reader accepts that its writer never writes (and the reverse),
   > duplicated logic that has already drifted, private names used across
   > modules, unbounded work, and anything that admits a rule GND has not
   > re-checked. For each finding give: class (blocking, hardening,
   > completeness), originating commit, file and line, a reproduction you
   > ran, expected versus actual. Run no learner, solver or model. Write
   > only under `<scratch>/IH0/<reader>/`. Edit no repository file.
4. **Reproduction.** The author reruns each reader's reproduction at
   `fb03739` before believing it. A finding that cannot be reproduced is
   recorded as "not reproduced" with the reason; one that needs a learner,
   solver or model run is carried with a target (IH-R1).
5. **Triage and disposition**, per finding:
   - **blocking** (a wrong admission, a crash, a wrong exit on valid input):
     fixed in IH0, with a regression test in `tests/test_ih0_review.py`
     shown red against the fix's parent commit in `evidence/IH0/red.txt` (p1);
   - **hardening**: fixed in IH0 if it is local and small, or assigned to
     IH1 or IH2 by name if it is in the counting path they rewrite;
   - **completeness**: deferred by default, as a carried row with a target.
   A finding several readers report is one row, with every reader named.
6. **Outputs.**
   - `notes/phase-IH0-review-<n>.md`: each reader's report verbatim,
     sanitized;
   - `notes/phase-IH0-triage.md`: the triage table, reproduction notes and
     dispositions;
   - `evidence/IH0/red.txt` and `evidence/IH0/gate.txt`;
   - the phase record `NNN-phase-IH0.md` with the refactoring review.
   The fixes' own diff gets one further reviewer (process-phase step 4).

## Decisions

| ID | Question | Readings and cost | Proposed |
|---|---|---|---|
| IH0-D1 (plan IH-D2) | Scope (p1) | IL's merges in `src/` + `tools/` (37 files, about 3,350 changed lines); adding the other milestones' merges (64 files); adding `tests/` (about 14,000 lines) finds weak or vacuous tests but multiplies reading time about four times | IL's merges, `src/` + `tools/` |
| IH0-D2 (plan IH-D4) | Instrument | four local readers; the maintained panel (parent credentials required); one reader | four local readers |
| IH0-D3 | Hardening findings in the counting path | fix in IH0, or assign to IH1 so the code moves once | assign to IH1 |
| IH0-D4 | A fix that moves a golden or bumps an adapter version | stop for the owner per fix, or batch them into one ruling after triage | batch after triage |

## Tests

| Test | Expected |
|---|---|
| `tests/test_ih0_review.py::test_f<n>_…`, one per fixed finding | exit non-zero at the fix's parent commit (retained in `evidence/IH0/red.txt`), exit 0 after the fix (p1) |
| the focused tests of every module a fix touches, named in the record | exit 0 |
| `tests/test_ilp_learners.py::test_t8_the_milestone_directory_is_private_clean`, widened to this milestone's directory | exit 0 |

The test list for the fixes cannot be fixed before the review runs. The
record lists every test added, with its red output.

## Out of scope for this phase

- Fixing anything IH1 or IH2 owns, unless blocking.
- Tests, docs and evidence, unless IH0-D1 widens the scope.
- The source changes of #47, #50, #52 and #53 (p1).
- **Residual:** a review is a disagreement locator, not a proof (p1).
- Any learner, solver or model run.

## Size

Review: four readers over about 3,350 changed lines (p1). Fixes: unknown until triage.
The record measures both.

## Approval instrument

This prose. A fixture corpus does not fit a review phase: the cases are the
findings, which do not exist before the review.
