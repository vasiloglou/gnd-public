---
milestone: code-refactoring
station: milestone-close
scope: milestone-close
date: 2026-11-25
source_base: 99cf3df2aeb8663d27a7028d6f8bfd24a8ddfdf9
milestone_end: a390599c1a8fe8bdf13596e2f71805b6a94e109d
gates:
  - command: "bash .gnd-planning/milestones/release-0.5.0/evidence/RW1/e1-shards.sh 99cf3df2aeb8663d27a7028d6f8bfd24a8ddfdf9 base   # on beast-3"
    exit: "0 (shard 0 exit 1 for the two RC-02 errors)"
    output: "22,057 passed, 0 failed, 2 errors, 13 skipped"
  - command: "uv run pytest -q -p no:cacheprovider tests/test_rf1_*.py tests/test_rf5_commands.py tests/test_gnd_arch.py"
    exit: 0
    output: "758 passed"
  - command: "uv run python tools/run_gnd_review_panel.py --light .gnd-planning/milestones/code-refactoring/evidence/close-panel/review-request.json --out <scratch>/panel-run --effort high --reviewer-timeout 600 --overall-timeout 900"
    exit: 0
    output: "quorum-established: 4 of 6 seats (claude, codex, qwen, glm), all revise; gemini malformed, kimi nonzero"
  - command: "ruling: the owner closed code-refactoring on candidate r2 sha256 ca1e7f0e680c7293cac887d2805906ba7ce3b61c69078e32dcde28d587c0f172, plan sha256 80a5804a34ec498e3a53a00ffedfa19d656f6741a76561eb0dd2385ff4a14380"
    exit: "n/a -- owner ruling"
    output: "closed, with C-D1 to C-D5 as ruled"
evidence:
  - path: .gnd-planning/milestones/code-refactoring/018-close-candidate.md
    sha256: ca1e7f0e680c7293cac887d2805906ba7ce3b61c69078e32dcde28d587c0f172
  - path: .gnd-planning/milestones/code-refactoring/notes/code-refactoring-plan.md
    sha256: 80a5804a34ec498e3a53a00ffedfa19d656f6741a76561eb0dd2385ff4a14380
  - path: .gnd-planning/milestones/code-refactoring/notes/close-results.md
    sha256: 1278ebb651bf608ecedd0eaaa4df62a22a51451934e1484cac708ee3e3003bdb
  - path: .gnd-planning/milestones/code-refactoring/notes/close-question-sweep.md
    sha256: 7a61a36e4ff58f4028af7811edb3d3ed7f9ddc862288cf1ca95c8a77057c980d
  - path: .gnd-planning/milestones/code-refactoring/evidence/close/owner-statements.txt
    sha256: 95a03d3a9c9f4a50610ee1ace22e7e4bc68ccf3d846b77f01961b44a96f84d89
  - path: .gnd-planning/milestones/code-refactoring/evidence/close/default-lane.txt
    sha256: e570801744d5bf533bbbac0d53af96218a7000784d4db4cd63fb125aa41ef6bc
  - path: .gnd-planning/milestones/code-refactoring/evidence/close-panel/PANEL-REVIEW.md
    sha256: 6467affd5da80b8b8beb80047a330f6e061bc4fb66b09bc5dff41225fc1b2941
  - path: .gnd-planning/milestones/code-refactoring/evidence/close-panel/disposition.md
    sha256: 25c43d250173b50495da3b1d09cc863907564b3c953697605e308e56309cd7f9
  - path: .gnd-planning/milestones/code-refactoring/evidence/close-panel/synthesis.json
    sha256: cd8c670fb2452236903128c8855dfbb3b9c118a9ea74eb79b0ee058ac1272453
  - path: .gnd-planning/milestones/code-refactoring/evidence/close-panel/review-request.json
    sha256: 2b6243655988d5ba91bfa7f9e96a5e7a05500fef23c213436af50190c34d5530
---

# code-refactoring milestone close

**Closed by the owner on 2026-11-25**, on close candidate
[018](018-close-candidate.md) r2 and the plan as amended by its close repairs.
The ruling is the owner's own, given in answers quoted whole in
[owner-statements.txt](evidence/close/owner-statements.txt); it is not a
delegated ruling.

## Result

All ten phases (RF0 to RF9) have records; the last phase commit is
`a390599c`. At that commit and on main `99cf3df2`:

| # | Predicate | Result |
|---|---|---|
| 1 | RF1 pins | holds at `a390599c` under CR2 (RF7's nineteen successors bound apart) |
| 2 | layering | holds on the RF0 import graph; the seven package-initializer cycles are carried (C-D1) |
| 3 | one home per identical family; diverged variants kept | **not met** for five groups whose RF1 pins agree and that keep several definitions, accepted as residuals (C-D2); the diverged-variant sentence is superseded for RF7's three merged families (C-D5) |
| 4 | thin CLI | holds: `cli.py` 667 lines at `a390599c`, 733 on main; 0 entry-point violations |
| 5 | measurements | holds: the before/after table and fourteen missed-original rows; the ten delegated re-targets and the RF5 re-plan are ratified as owner-ruled values (C-D4) |

Measured at the RF0 base, the milestone end and main: runtime import cycles
5 to 0 to 0; wrong-way layer edges 27 to 0 to 0; clean layers 2 to 6 to 6;
`cli.py` 9,088 to 667 to 733 lines; private cross-module imports 242 to 680
to 804 ([close-results.md](notes/close-results.md)).

Full default lane at main on beast-3: 22,057 passed, 0 failed, the two RC-02
errors, 13 `GND_PYREL_PYTHON` skips.

## Review

The light GND panel read candidate r1 (four of six seats, all "revise").
Its thirteen fixes are disposed in
[disposition.md](evidence/close-panel/disposition.md); none was rejected.
The largest: predicate 3 was not met as r1 claimed, which the pin-agreement
measurement showed and r2 reports. One round; r2 has no review opinion.

## Owner rulings at this close

| ID | Ruling |
|---|---|
| route | full close for code-refactoring; analytics-m3-repairs and induction-skill left open |
| C-D1 | predicate 2 holds on the RF0 graph; the package-initializer cycles are carried |
| C-D2 | the five groups with agreeing pins are residuals; `_rate` and `_sorted_set`/`_canonical` carried |
| C-D3 | the residuals and carried items of the sweep's section F are accepted |
| C-D4 | the ten delegated re-targets and the RF5 re-plan are ratified |
| C-D5 | RF7's merges of JSON intake, datetime and the file-digest reader supersede RF-D11 for those families |

## Carried

Named in [close-question-sweep.md](notes/close-question-sweep.md), section F:
shim retirement (RF-D5's trigger has passed; it needs its own approved
phase); the RF7 remainder; the session-controller, session-portability,
media-type, model-query and input-boundary successors; RF1-OQ7; the
untracked items Q2, Q3, the Souffle setuid node and the pool `ValueError`;
the primitive-ownership guard; the source-owned questions; the
package-initializer cycles; `_rate` and `_sorted_set`/`_canonical`. None
names a successor milestone; tracking issues can be filed on the owner's
word.

## Boundary

- Lanes ran on macOS only; no Linux, installed-wheel, certification or
  release claim.
- Later milestones' 32 pin re-recordings and their effect on the layering are
  not reviewed here; main still measures clean on the RF0 graph.
- The raw panel streams are in scratch and not in history; the request,
  synthesis, report and disposition are.
