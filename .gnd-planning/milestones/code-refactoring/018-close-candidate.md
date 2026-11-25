---
milestone: code-refactoring
station: close-candidate
scope: close-candidate
date: 2026-11-25
revision: r2
reviewed_revision: "r1, sha256 3ba5796b84093e329fc0b20c04d372caa74dadd066c6894b4856e38b57fc6dde, commit efe9ea8a"
measurement_points:
  rf0_base: 19b131b
  milestone_end: a390599c1a8fe8bdf13596e2f71805b6a94e109d
  main: 99cf3df2aeb8663d27a7028d6f8bfd24a8ddfdf9
evidence:
  - path: .gnd-planning/milestones/code-refactoring/notes/code-refactoring-plan.md
    sha256: 80a5804a34ec498e3a53a00ffedfa19d656f6741a76561eb0dd2385ff4a14380
  - path: .gnd-planning/milestones/code-refactoring/notes/RF7-plan-amendment.md
    sha256: 93a2575df51e4b28df9d9e58b43acc186446ed20e8086ed6d5135dd4ebb83bab
  - path: .gnd-planning/milestones/code-refactoring/notes/close-results.md
    sha256: 1278ebb651bf608ecedd0eaaa4df62a22a51451934e1484cac708ee3e3003bdb
  - path: .gnd-planning/milestones/code-refactoring/notes/close-question-sweep.md
    sha256: 7a61a36e4ff58f4028af7811edb3d3ed7f9ddc862288cf1ca95c8a77057c980d
  - path: .gnd-planning/milestones/code-refactoring/notes/close-families.md
    sha256: 6a47c54f541c6ff55488489f67fd22fd5c1b6268d07f28d48139e80570737b26
  - path: .gnd-planning/milestones/code-refactoring/evidence/close/close-table.txt
    sha256: e25a9baf0333deded5fcb057be6028c751621ca2c42bcc6e16fa6cc7600dd452
  - path: .gnd-planning/milestones/code-refactoring/evidence/close/close-table.py
    sha256: 8317acf81976332869fbfa14fec76b4b5b5f08361a812c2f85e4dcfe496a5cb8
  - path: .gnd-planning/milestones/code-refactoring/evidence/close/metrics-a390599c.json
    sha256: 2a075d05bfd208b5ad547b36ce2cee7bb5d0f87b11431ad166c285060840082a
  - path: .gnd-planning/milestones/code-refactoring/evidence/close/metrics-close.json
    sha256: ee21a5353cc9b082d02d153de9a5c20ade1baa7cd0bd16bea71485c7825cdd84
  - path: .gnd-planning/milestones/code-refactoring/evidence/close/pin-history.txt
    sha256: c2a6a2013b7cb3e9b7a9fcd66ec3f1aadfa5ff63f6488150c4af2c376a868f64
  - path: .gnd-planning/milestones/code-refactoring/evidence/close/pin-agreement.py
    sha256: de57ed4019474ecfdc3688be41a069ceef9c6782c1a81b16e362976fcf482c6b
  - path: .gnd-planning/milestones/code-refactoring/evidence/close/pin-agreement.txt
    sha256: f981c3232b447afb58ebd2068c0aec42402de02d12fa849c7f75eae385bbabf1
  - path: .gnd-planning/milestones/code-refactoring/evidence/close/predicates-focused.txt
    sha256: 584f44f08273e3e5d5a1f2dd712ad7295ee8b84a5091c640bff94b5e0eb4da47
  - path: .gnd-planning/milestones/code-refactoring/evidence/close/default-lane.txt
    sha256: e570801744d5bf533bbbac0d53af96218a7000784d4db4cd63fb125aa41ef6bc
  - path: .gnd-planning/milestones/code-refactoring/evidence/close/owner-statements.txt
    sha256: 2a955cbb84fe8bca9e615358bce0c48dbbd54e64dac1a32ef52ee5d43e61b1de
  - path: .gnd-planning/milestones/code-refactoring/evidence/close-panel/review-request.json
    sha256: 2b6243655988d5ba91bfa7f9e96a5e7a05500fef23c213436af50190c34d5530
  - path: .gnd-planning/milestones/code-refactoring/evidence/close-panel/synthesis.json
    sha256: cd8c670fb2452236903128c8855dfbb3b9c118a9ea74eb79b0ee058ac1272453
  - path: .gnd-planning/milestones/code-refactoring/evidence/close-panel/PANEL-REVIEW.md
    sha256: 6467affd5da80b8b8beb80047a330f6e061bc4fb66b09bc5dff41225fc1b2941
  - path: .gnd-planning/milestones/code-refactoring/evidence/close-panel/disposition.md
    sha256: 25c43d250173b50495da3b1d09cc863907564b3c953697605e308e56309cd7f9
  - path: .gnd-planning/milestones/code-refactoring/017-phase-RF9-ci-repair.md
    sha256: 8dcbb36783c60c2deb11b948316c3e239441193de4c0244eaa7b5586105c01eb
---

# code-refactoring close candidate

**r2, after the light close panel.** The panel (four of six seats, all
"revise") read r1; r2 applies its thirteen fixes
([disposition](evidence/close-panel/disposition.md)). No review has read r2.

The owner asked on 2026-11-25 to check which old milestones are finished and
close them, and chose a full close for this one: the five predicates measured
on main, the full lane on beast-3, the light GND panel over this candidate,
and the owner's close ruling ([owner statements](evidence/close/owner-statements.txt)).
The plan's default is `auto=false` (plan §8); phases ran with their own
per-phase `auto` selections, and no delegation covers the close. The close
ruling is the owner's.

## What the milestone delivered

A layered `src/gnd` with no multi-module cycle on the import graph RF0
measured, a thin CLI, and one home for the five helper groups RF2 promoted,
through behavior-preserving moves (RF2 to RF6, RF8), the owner-directed
restrictions of RF7, and the RF9 cumulative review and its two repairs. Its
last phase commit is `a390599c` (2026-10-06).

| Records | Phases |
|---|---|
| 001 to 003, 005 | two light plan panels, the plan gate, erratum e1 |
| 004, 006 | RF0 baseline and tool; RF1 characterization pins |
| 007 to 012 | RF2 helpers; RF3 core cycle; RF4 peripheral layers; RF5 CLI groups; RF6a model queries and family registry; RF6b model and checker packages |
| 013 | RF7, the restrictions pulled forward by the owner ([amendment](notes/RF7-plan-amendment.md)) |
| 014 | RF8 session profile and the v7 merge |
| 015 to 017 | RF9 cumulative review, its repair and its CI repair |

## The predicates

[close-results.md](notes/close-results.md) judges them at three points: the
RF0 base `19b131b`, the milestone end `a390599c` and main `99cf3df2`.

| # | Predicate | Judgement | Evidence |
|---|---|---|---|
| 1 | RF1 pins green; no expected value changed | **holds** at `a390599c` under CR2: the RF1 golden files are unchanged from capture to milestone end, apart from mutation targets; RF7's nineteen restriction successors are bound apart and unchanged since | [pin-history.txt](evidence/close/pin-history.txt); record 017's full suite; main's 758-test run is a regression check only ([predicates-focused.txt](evidence/close/predicates-focused.txt)) |
| 2 | layer map complete; layering test without xfail; no multi-module SCC in the core layers | **holds on the RF0 import graph** (CR4): 0 unmapped modules, no xfail marker, 0 SCCs, 0 wrong-way edges, 6 of 6 clean layers, at `a390599c` and on main. On RF9's package-initializer graph it does not: seven package-internal cycles, three in the core layers. Carried by the owner's ruling C-D1 | [metrics-a390599c.json](evidence/close/metrics-a390599c.json), [metrics-close.json](evidence/close/metrics-close.json), [close-table.txt](evidence/close/close-table.txt), [predicates-focused.txt](evidence/close/predicates-focused.txt) |
| 3 | one home per identical family; diverged variants kept | **not met as written** for five groups whose RF1 pins agree and that keep several definitions (three kept apart by phase rulings, two never ruled): C-D2. The diverged-variant sentence holds only if the owner ratifies RF7's three merges: C-D5 | [pin-agreement.txt](evidence/close/pin-agreement.txt), [close-families.md](notes/close-families.md) |
| 4 | `cli.py` at most 2,500 lines; no entry-point violation | **holds**: 667 lines at `a390599c`, 733 on main; 0 violations | close-table.txt |
| 5 | before/after table; every missed original listed; each target met against its final owner-ruled value | the table and the fourteen missed-original rows are complete; ten were re-targeted by delegated phase rulings and are owner-ruled only if ratified: C-D4 | close-results.md, "Original targets missed" |

## Plan repairs

| Repair | Touches | Kind |
|---|---|---|
| CR1 | RF7's status in §1, §3, §4, §7, §9, RF-D7 | records 013 and the RF9 amendment |
| CR2 | predicate 1 | applies the RF7 amendment's own reading |
| CR3 | RF-D11, predicate 3's second sentence | **reframes**; for the owner (C-D5) |
| CR4 | predicate 2's graph | reframes the graph after RF9 widened the tool; the owner ruled the consequence (C-D1) |
| CR5 | predicate 3's "identical" | **withdrawn** after the panel |
| CR6 | §4 RF2's canonical premise | records RF2-OQ1 |
| CR7 | RF-D3 | records RF0 D4(b) and RF2 D7 |
| CR8 | §4 RF3's SCC prose | records RF0 D10 and RF3 A5 |
| CR9 | §4 RF4's filesystem "move" | records RF4 D2 and design F |
| CR10 | predicate 4's entry rule; the RF5 re-plan | records RF5; the re-plan goes to C-D4 |
| CR11 | §4 RF6's facade target | records RF6b A1 |
| CR12 | §10 statuses of RF-D5, RF-D6, RF-D8, RF-D9 | records the rulings and RF7 |
| CR13 | risk row "and co-change" | records erratum e1 |

## Owner decisions

| ID | Question | Proposal | Alternative and cost | State |
|---|---|---|---|---|
| C-D1 | the package-initializer cycles | carry them; predicate 2 holds on the RF0 graph | a repair phase before the close | **ruled by the owner: the proposal** |
| C-D2 | five groups with agreeing pins and several definitions | accept as residuals; carry `_rate` and `c4e1c0f8` | a small repair phase: merge `_rate`; rule `c4e1c0f8` | ruled on r1's wrong premise; **asked again** |
| C-D3 | the residuals and carried items of the sweep, section F | accept | reopen rows as work | open |
| C-D4 | ten delegated re-targets and the RF5 re-plan | ratify as final owner-ruled values | predicate 5 unmet for those rows | open |
| C-D5 | CR3, RF7's merges against RF-D11 | ratify | predicate 3's second sentence unmet for three families | open |

## The close's own evidence

- **Full default lane** at main `99cf3df2`, six shards on beast-3:
  [22,057 passed, 0 failed, 2 errors, 13 skipped](evidence/close/default-lane.txt).
  Pass condition: 0 failed; errors limited to the two RC-02 nodes in
  `tests/test_public_optional.py`; skips limited to `GND_PYREL_PYTHON`. Met.
- **Question sweep** ([sweep](notes/close-question-sweep.md)): 86 rows from
  plan §10 and records 003 to 017; eleven rows where records disagree and one
  possible conflict (C63); section F disposes of every open, untracked or
  conflicting row.
- **Close panel** over r1: [review](evidence/close-panel/PANEL-REVIEW.md),
  [synthesis](evidence/close-panel/synthesis.json),
  [disposition](evidence/close-panel/disposition.md).

## Separation of authority

- The owner's rulings: the plan gate (003), erratum e1 (005), the RF-D rulings
  named in the plan, the RF7 instruction ("yes implement RF7"), the RF9
  registration and repair approvals (016, 017), and at this close C-D1 and the
  close route (owner-statements.txt).
- Delegated phase rulings: the ten re-targets and the RF5 re-plan, listed as
  delegated until C-D4.
- This candidate, its measurements and the sweep are the author's; the panel
  is advisory.

## What the close does not establish

- Behavior on Linux or from an installed wheel; the lanes ran on macOS.
- That later milestones kept the layering by design: main measures clean, but
  this close does not review their diffs or their 32 pin re-recordings.
- Shim retirement: RF-D5's release trigger has passed; retirement needs its
  own approved phase.
- Any certification or release claim.
