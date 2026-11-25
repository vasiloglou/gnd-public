---
milestone: code-refactoring
station: close-candidate
scope: close-candidate
date: 2026-11-25
source_base: 99cf3df2aeb8663d27a7028d6f8bfd24a8ddfdf9
milestone_end: a390599c
evidence:
  - path: .gnd-planning/milestones/code-refactoring/notes/code-refactoring-plan.md
    sha256: b983a2c96dfc01df31bbc234e705cde1c62d84f042a0b6b42a7478bbc5c1132e
    note: "r2 with erratum e1, the RF9 amendment and the close repairs CR1 to CR13"
  - path: .gnd-planning/milestones/code-refactoring/notes/RF7-plan-amendment.md
    sha256: 93a2575df51e4b28df9d9e58b43acc186446ed20e8086ed6d5135dd4ebb83bab
  - path: .gnd-planning/milestones/code-refactoring/notes/close-results.md
    sha256: 1c8f2cd3382f133e1cc2b2b84423fa2122a0eec3c2d859f25b24628b5258fb23
  - path: .gnd-planning/milestones/code-refactoring/notes/close-question-sweep.md
    sha256: 2e48b47a093883832749fb95ec20487a8b8cc1568ff922900314ca4b6cd4b4c0
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
    sha256: 6969aff914823a434d4cc969ba5abe7e66c8c3ad0fc076fc7d6bf3098eb75730
  - path: .gnd-planning/milestones/code-refactoring/evidence/close/predicates-focused.txt
    sha256: 584f44f08273e3e5d5a1f2dd712ad7295ee8b84a5091c640bff94b5e0eb4da47
  - path: .gnd-planning/milestones/code-refactoring/evidence/close/default-lane.txt
    sha256: e570801744d5bf533bbbac0d53af96218a7000784d4db4cd63fb125aa41ef6bc
  - path: .gnd-planning/milestones/code-refactoring/017-phase-RF9-ci-repair.md
    sha256: 8dcbb36783c60c2deb11b948316c3e239441193de4c0244eaa7b5586105c01eb
---

# code-refactoring close candidate

This is the review subject of the close. The owner asked on 2026-11-25 to check
which old milestones are finished and close them, and chose a full close for
this one: the five predicates measured on main, the full lane on beast-3, the
light GND panel over this candidate, and the owner's close ruling. The plan
gives this milestone no delegation (`auto=false`, plan §8), so the close
ruling is the owner's.

## What the milestone delivered

A layered `src/gnd` with no import cycle, a thin CLI and one home for each
shared helper that RF1's pins showed identical, through behavior-preserving
moves (RF2 to RF6, RF8), the owner-directed restrictions of RF7, and the RF9
cumulative review and its two repairs. Its last phase commit is `a390599c`
(2026-10-06).

| Records | Phases |
|---|---|
| 001 to 003, 005 | two light plan panels, the plan gate, erratum e1 |
| 004, 006 | RF0 baseline and tool; RF1 characterization pins |
| 007 to 012 | RF2 helpers; RF3 core cycle; RF4 peripheral layers; RF5 CLI groups; RF6a model queries and family registry; RF6b model and checker packages |
| 013 | RF7, the restrictions pulled forward by the owner ([amendment](notes/RF7-plan-amendment.md)) |
| 014 | RF8 session profile and the v7 merge |
| 015 to 017 | RF9 cumulative review, its repair and its CI repair |

## The predicates

[close-results.md](notes/close-results.md) judges the five predicates, read
through the plan's close repairs CR1 to CR13. In short:

| # | Predicate | Judgement |
|---|---|---|
| 1 | RF1 pins green; no expected value changed | holds at `a390599c` under CR2: expected values unchanged through the milestone except RF7's nineteen named restriction successors; 758 pin, layering and tool tests pass on main. 32 later commits from other milestones re-recorded pin values after the milestone |
| 2 | layer map complete; layering test without xfail; no multi-module SCC in the core layers | holds on the RF0 graph (CR4): 0 SCCs, 0 wrong-way edges, 6 of 6 layers clean, 0 allowances, at `a390599c` and on main. The package-initializer graph RF9 added has seven package-internal cycles, three in the core layers: **owner decision C-D1** |
| 3 | one home per identical family; diverged variants kept | holds under CR3 and CR5: the five promoted groups have one home; RF7 merged three diverged families under its amendment; four candidate groups were never promoted or ruled: **owner decision C-D2** |
| 4 | `cli.py` at most 2,500 lines; no entry-point violation | holds: 667 lines at `a390599c`, 733 on main; 0 violations |
| 5 | before/after table; every missed original target listed | holds: close-results.md lists thirteen missed originals, most re-targeted by delegated phase rulings |

## The close's own evidence

- **Full default lane** at main `99cf3df2`, six shards on beast-3:
  [22,057 passed, 0 failed, 2 errors, 13 skipped](evidence/close/default-lane.txt).
  The two errors are `tests/test_public_optional.py` (RC-02 of the
  release-0.5.0 close); the skips need `GND_PYREL_PYTHON`.
- **Measurements** with the milestone's own tool at three points:
  [close-table.txt](evidence/close/close-table.txt).
- **Pin history** across and after the milestone:
  [pin-history.txt](evidence/close/pin-history.txt).
- **Question sweep** ([sweep](notes/close-question-sweep.md)): 86 rows from
  plan §10 and records 003 to 017, twelve of them records that disagree; its
  section F gives a disposition to every row the records left open, untracked
  or in conflict.
- **Plan repairs** CR1 to CR13 (plan, "Close repairs"), each citing the
  record that raised it; prior wording kept.

## Separation of authority

- The owner's rulings are the plan gate (003), erratum e1 (005), the RF-D
  rulings named in the plan, the RF7 instruction ("yes implement RF7"), the
  RF9 registration and the RF9 repair approvals (016, 017).
- From RF3 on, many targets were re-targeted by delegated phase rulings, not
  by the owner (close-results.md, "Original targets missed"); the close lists
  them as delegated.
- This candidate, its measurements and the sweep are the author's; the
  panel is advisory; the close ruling, C-D1 to C-D3 included, is the owner's.

## What the close does not establish

- Behavior on Linux or from an installed wheel; the lanes ran on macOS.
- That every later milestone kept the layering by design: main still
  measures clean, but this close does not review their diffs.
- Shim retirement: RF-D5's release trigger has passed, and retirement still
  needs its own approved phase.
- Any certification or release claim.
