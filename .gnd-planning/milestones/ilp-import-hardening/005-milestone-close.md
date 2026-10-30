---
milestone: ilp-import-hardening
station: milestone-close
skill: "n/a -- repository development via process-milestone, not a gnd-solve station over a domain model"
scope: IH-close
date: 2026-10-30
source_base: fb03739
gate:
  command: "<scratch>/ci/ci.sh PYTHON CLONE, the steps of .github/workflows/development.yml, on clean clones of d132003 (IH-R3)"
  exit: 0
  output: "CI RESULT python 3.13: PASS; CI RESULT python 3.11: PASS; full suite 16435 passed on each"
  note: >-
    Python 3.13 and 3.11, macOS, each on its own clean clone of the pushed PR
    head, with uv 0.10.10, the version the build profile pins. Both ran on a
    second macOS host, at the same time. The Linux leg of the workflow is not
    reproduced (IH-R3). In evidence/close/ci-run.txt, filtered for size as its header states.
evidence:
  - path: .gnd-planning/milestones/ilp-import-hardening/notes/close-review.md
    sha256: 2a779db4b5772a2c535130ca57b292a6c92f96cd53ef5c80c617a8f12cc0e755
  - path: .gnd-planning/milestones/ilp-import-hardening/evidence/close/red.txt
    sha256: cc2014de6534a708361e9d331d666c14bec12f2b2b314a3bc383201c482c15b1
  - path: .gnd-planning/milestones/ilp-import-hardening/evidence/close/repair-gate.txt
    sha256: 95fe0b192417318c14aad957d92ccdfee26662875998dabe1f0cdf1ffea81e1a
  - path: .gnd-planning/milestones/ilp-import-hardening/evidence/close/ci-run.txt
    sha256: ea719ab7ff150578db64e7b57032273808e2c75fdd4ee784142e20791f5c0d26
  - path: tests/test_ih_close.py
    sha256: 0da9991963e7ebc8d4c19cd0829034b48decb0bd7da6fb4fbb5200f670e56fcb
---

# ILP import hardening -- milestone close

**Status: closed and accepted by the owner on 2026-10-30, with the merge authorized (see Owner acceptance at the end).** All three
phases have records. The close review ran, and its findings were fixed or
carried. The close CI ran on the PR head on both Pythons. The close ruling
below is a **delegated close ruling (auto=true)**, not owner acceptance.
Merging PR #65 is the owner's act, and its record follows separately.

## The delegated close ruling (auto=true)

- **Authorization:** the owner's `process-milestone ilp-import-hardening
  auto`, 2026-10-30. It covers spec, plan and close rulings within this
  milestone, and not merge, publication, paid calls or certification.
- **Ruling:** the milestone's completion predicates 1 to 4 are met, and
  predicate 5 is met except for the owner acceptance it names. Every question
  row is dispositioned below.
- **Instrument:** four readers over the whole milestone (IH-D6 (a)), then the
  CI run (IH-R3).
- **Budget:** no paid call; no learner, solver or model run (IH-R1).
- **Not established:** the close review's repairs were read by no one after
  them (see "Boundary").

## Phase records

| Phase | Record | Commit | Result |
|---|---|---|---|
| plan gate | [001-plan-gate.md](001-plan-gate.md) | `cbc97b2` | plan r2 approved by the owner, with its proposed rulings |
| IH0 | [002-phase-IH0.md](002-phase-IH0.md) | `60792cf`, `35cdc63` | four readers over IL's merges; 13 findings, none blocking; five fixed, three assigned to IH1, three carried |
| IH1 | [003-phase-IH1.md](003-phase-IH1.md) | `4389b61` | one public counting entry, built once; IH1-D3 to D5 (o) |
| IH2 | [004-phase-IH2.md](004-phase-IH2.md) | `faceb67` | `own-reference-join`, under a delegated gate |
| close repairs | this record | `d132003` | the comparison tool and docs repairs from the close review |

## Completion predicates

| Predicate (plan, "Completion requires") | Result |
|---|---|
| 1. IH0: one opinion per reader over IL's merges; findings reproduced, triaged, and fixed, assigned or carried | met: 002, its triage and four reviews |
| 2. IH1: public `count_mined_rules` used by the import and `hold()`; no `_mined_inputs` outside `ilp_service`; build once; provenance in `ilp_amie` with no discover edge; refusal order pinned; goldens and replays byte-identical | met: 003, T1 to T13. Two owner-approved error-path changes, IH1-D4 and D5 |
| 3. IH2: refused by its own name before any count, per IH-D1 (b); the false `support-mismatch` reproduced first | met: 004, T1 to T11. The rule was settled by the close review (below) |
| 4. Every phase: approval, focused checks, one independent diff review, a refactoring review and a record | met for IH0, IH1 and IH2. IH0's approval was "Start IH0", recorded as such; IH2's gate was delegated |
| 5. Close: a question sweep; the local CI run on the PR head; a close review per IH-D6; a PR; owner acceptance, recorded separately | the sweep, CI and review are below. The PR is vasiloglou/gnd-public#65. **Owner acceptance: given 2026-10-30** (below) |

## Gate output (summary of the log)

From [evidence/close/ci-run.txt](evidence/close/ci-run.txt):

```
python 3.13 (clone of d132003, uv 0.10.10)
== uv build (release, comparison) and sha256 check: exit 0, exit 0, exit 0
== uv sync --locked / gnd install / gnd doctor / collect-only: exit 0 each; 16435/17229 tests collected (794 deselected)
== timing and guarded lane: 160 passed, 1 deselected -- exit 0
== uv run pytest -q -ra --tb=short: 16435 passed, 794 deselected, 1 warning in 2188.61s -- exit 0
== installed: candidate commit = HEAD -- exit 0
== release acceptance: 1806 passed / 91 passed (release); 1806 passed / 91 passed (comparison); 10 passed -- exit 0
== CI RESULT python 3.13: PASS

python 3.11 (clone of d132003, uv 0.10.10)
== uv build (release, comparison) and sha256 check: exit 0, exit 0, exit 0
== uv sync --locked / gnd install / gnd doctor / collect-only: exit 0 each; 16435/17229 tests collected (794 deselected)
== timing and guarded lane: 160 passed, 1 deselected -- exit 0
== uv run pytest -q -ra --tb=short: 16435 passed, 794 deselected, 1 warning in 2084.85s -- exit 0
== installed: candidate commit = HEAD -- exit 0
== release acceptance: 1806 passed / 91 passed (release); 1806 passed / 91 passed (comparison); 10 passed -- exit 0
== CI RESULT python 3.11: PASS
```

**The close repairs' focused gate** ([repair-gate.txt](evidence/close/repair-gate.txt)),
on the bytes committed as `d132003`: 742 passed, 8 skipped, exit 0. The
comparison tool exits 0, and ruff is clean. The CI run above covers the same
bytes.

## Close review (IH-D6 (a))

Four readers read the whole milestone, `git diff fb03739`, on `4389b61` with
IH2's uncommitted work. Each had its own emphasis: the import's end-to-end
correctness; IH0's fixes and the comparison tool; tests and evidence; the
plan and the docs. Their reports are retained verbatim
([close-review.md](notes/close-review.md)). Each finding was reproduced by
the author before repair, except where the table says otherwise.

| Reader, finding | Class | Disposition |
|---|---|---|
| 1, finding 1: a variable over a type under two references (the diamond's `director`) holding `1` and `"1"` exits 70, after reader 4's H1 repair | blocking | fixed in IH2 (`faceb67`): refuse a variable whose types' references, taken together, span more than one kind of value. T9 is red at IH1's head and against the H1 repair |
| 1, finding 2: the same exit 70 through two unrelated top types, with no own-reference subtype | hardening | fixed by the same rule: T11, red at IH1's head. The refusal name says own-reference though no subtype here has its own scheme; the docs row names the case |
| 1, finding 3: the primitive-name union refused an Integer and Number diamond that `fb03739` admitted | hardening | fixed: kinds of value, not names (`_kind`, reusing `gnd.terms.NUMERIC_PRIMITIVES`). T10 |
| 1, finding 4: siblings and value-type subtypes declared not to inherit are refused by this name too | completeness | fixed in the docs row |
| 2, finding 1: an LLM answer that is valid JSON but no clauses document crashes the comparison tool with exit 1 | hardening | fixed (`d132003`): exit 2 naming the directory, or a reader-refusal row. `tests/test_ih_close.py`, red at `4389b61` ([red.txt](evidence/close/red.txt)) |
| 2, finding 2: the Popper and ILASP readers' schema-size limits (more than 64 arguments, names over 64 characters) are refused with no refusal name | completeness | carried: IH-close-Q1 |
| 2, finding 3: the import summary's rules bullet was broader than `check_columns` | completeness | fixed (`d132003`) |
| 2, suspected: other exit-1 escapes in the tool; `_BEFORE_ANY_CLAUSE` hard-coded; an unnamed nesting refusal | — | carried, not reproduced: IH-close-Q2 |
| 3, C1: the IH2 draft named a full-suite file not yet written | completeness | resolved: written and sanitized before IH2's commit |
| 3, H1 and 4, C5: a private host name in planning text | hardening | fixed (`d132003`); the IH2 record names no host |
| 4, H1: the F1 repair refuses a variable over `director` alone, which IH1's head admitted | hardening | **overruled** by reader 1's finding 1. `director` may hold `1` and `"1"`; the refusal is disclosed in the docs, the release note and IH2's boundary |
| 4, C1: IH0's "invalid model" suspicion had no row | completeness | carried: IH1-Q2 |
| 4, C2 and C3: the release note and docs row overstated or understated the cases | completeness | fixed in IH2 |
| 4, C4: the test and fixture homes depart from the plan's §3 | completeness | recorded here: the tests are `tests/test_ih0_review.py`, `test_ih1_counting.py`, `test_ih2_ownref.py` and `test_ih_close.py`, and the fixtures are under `tests/fixtures/ilp_import_hardening/`. The plan is not edited |

**Convergence.** The close review was the milestone's last instrument for
IH2's rule. Each repair round opened the next round's findings: F1 led to
H1, H1 to reader 1's finding 1, and the per-name union to finding 3. The
final rule was checked against every model the readers built, by the
author, and by no reader after it.

## Question sweep

Every record in this directory was re-read, together with the questions this
milestone harvested from IL's close.

| Row | Source | Disposition |
|---|---|---|
| IL4-Q1 remainder: own-reference subtype joins | IL 009 | **closed** by IH2 (004): refused by name (IH-D1 (b)) |
| IL-close-Q1: one rendering pass | IL 009 | **closed** by IH1 (003), T2 |
| IL4-Q3 remainder: provenance home | IL 009 | **closed** by IH1, T6 |
| `hold()`'s private import | IL 009 | **closed** by IH1, T1 |
| IL's diff "as a whole" | IL 009, 010 | **retired as an accepted residual**: IH0 read IL's `src` and `tools` (IH-D2 (o)); IL's tests and docs were not reviewed |
| IH-D3 / IL6-Q3; IL1-Q6, IL2-Q2, IL3-Q3, IL-close-Q2 | plan §1, §7 | **carried** to the evaluation milestone, as IL's close recorded; they need learner or clingo runs |
| IH0-Q1: Popper and ILASP name a negated off-threshold literal differently (G) | 002 | **retired as an accepted residual**: both exit 3 by name |
| IH0-Q2: the export's work report omits threshold rendering (K); reader 3's `p6` not rerun | 002 | **carried** to the next milestone that changes the ILP export's bounds |
| IH0-Q3: the `llm` entry's `adapter_version` is never read (L) | 002 | **carried** to the next milestone that changes the LLM adapter |
| IH0-Q4: one home for the threshold check | 002 | **closed** by IH0-D4 (o) |
| IH0-D4's held fixes: the LLM threshold check; Popper's binary and infix spellings | 002 | **retired as an owner-ruled residual** ("Keep both held"), stated in the docs' Import step 2 |
| FR1's reverse subtype case, not run | 002 boundary | **closed**: reader 2 ran it (`f_refund_fee__2__3__gt_t_amount__450` refused) |
| IH1-Q1: the mined learner check ignores the tuple form | 003 | **carried** to the next milestone that changes the mined import |
| IH1-Q2 (new): a mapped rule that fails whole-model validation is reported "invalid model" with no rule index | IH0 triage; close reader 4, C1 | **carried** to the next milestone that changes the mined import |
| IH1: counting every rule before any check is slower on refused sets, not measured | 003 | **retired as an accepted residual**: bounded per rule (IL4-D7), owner-ruled IH1-D4 |
| IH2-Q1: spell a type under two references apart (IH-D1 (a), adapter version 3) instead of refusing | 004 | **carried** to the milestone that needs such rules admitted |
| IH2: `reference_primitives` cost on lattices; other family-mixing paths | 004 | **retired as an accepted residual**: reader 1 measured about 15% over `fb03739`'s already exponential baseline on a 20-level lattice |
| IH-close-Q1 (new): schema-size limits in the Popper and ILASP readers have no refusal name | close reader 2 | **carried** to the next milestone that changes the ILP readers |
| IH-close-Q2 (new): the comparison tool's other exit-1 escapes, the hard-coded `_BEFORE_ANY_CLAUSE`, and an unnamed nesting refusal | close reader 2, suspected | **carried**, not reproduced, to the next milestone that changes `tools/ilp_comparison.py` |

**Refactoring review.** Every deferred refactor has a row:
- IH0's shared threshold home is IH0-Q4, closed;
- IH0's `hold()` copy is closed by IH1;
- IH1's tuple check is IH1-Q1;
- IH2's spelling is IH2-Q1, and its resolver cost is a residual.

The close executed no refactor: its repairs are a tool guard and docs.

## Refuted premises

- **IH2 spec r1, Design 1 and 3:** a cross-family check catches every join the
  count cannot meet. False for a type under two references (004).
- **Reader 4's H1,** that a variable over one type alone joins nothing, so
  cannot be miscounted. False: such a type may hold `1` and `"1"` (reader 1,
  finding 1; T9).
- **IL's close record** listed Popper's unrendered thresholds as fixed (002).

## Boundary -- what this close does NOT establish

- **Owner acceptance and merge are not recorded.** This is a delegated close
  ruling.
- **The close review's repairs carry no review opinion.** The readers judged
  `4389b61` plus IH2's work in progress, and reader 1 judged it while it
  changed. The final IH2 rule and the tool guard were checked by the author's
  tests and by the readers' own models, run by the author.
- **The CI ran on macOS only,** on a second host; the workflow's Linux leg
  is not reproduced (IH-R3).
- **IL's tests and docs were never reviewed as a whole** (IH-D2 (o)).
- **The checker's equality across kinds of value** was observed on the
  readers' models, not proved; the refusal is conservative where it is not
  needed.
- **No learner, solver or model ran** (IH-R1).

## Next action

The owner reviews PR vasiloglou/gnd-public#65 and accepts or amends. A merge
is the owner's act; its record follows.

## Owner acceptance

2026-10-30, by the owner, in the session that ran this close: "Accept and
merge", in answer to "Do you accept the milestone close and authorize merging
PR #65?". This acceptance is the owner's own, distinct from the delegated close
ruling above, and covers the bytes of this record's commit and the PR head that
carries it. It authorizes merging vasiloglou/gnd-public#65; it does not start a
successor milestone, publish, or certify anything.
