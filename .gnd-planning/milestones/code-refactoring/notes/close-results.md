# code-refactoring close results

Judged on 2026-11-25. The milestone's last phase commit is `a390599c` (record
017, `source_subject`). Main is `99cf3df2`. The plan's close repairs CR1 to
CR13 (plan, "Close repairs") set how each predicate is read. Measurements:
[close-table.txt](../evidence/close/close-table.txt), from
`tools/gnd_arch.py measure` at the RF0 baseline (`19b131b`), at `a390599c`
(from `git archive`) and at main.

## Predicates

| # | Predicate | At `a390599c` | At main `99cf3df2` | Judgement |
|---|---|---|---|---|
| 1 | RF1 suite green; no expected value changed | RF1 expected values unchanged from the RF1 capture (`5f56f5f6`) to `a390599c`; only `mutations.json` was retargeted to moved code ([pin-history.txt](../evidence/close/pin-history.txt)). RF7's nineteen restriction successors are the amendment's named exceptions (CR2). Full suite at `a390599c`: 13,944 passed, 400 deselected (017) | 758 passed for `tests/test_rf1_*.py`, `tests/test_rf5_commands.py`, `tests/test_gnd_arch.py` ([predicates-focused.txt](../evidence/close/predicates-focused.txt)). 84 pin files changed after the milestone, in 32 commits of later milestones, each under its own review | **holds** under CR2, at the milestone's end |
| 2 | every module mapped; layering test with no xfail; no multi-module SCC in model, population, checking or semantics | 228 modules, 0 unmapped; 0 runtime and 0 module-only SCCs; 0 wrong-way edges; 6 of 6 layers clean; 0 allowances | 296 modules, 0 unmapped; the same zeros; `tests/test_rf1_layering.py` has no xfail marker | **holds** on the RF0 graph (CR4). The package-initializer graph has seven package-internal cycles, three in the named layers: owner decision C-D1 |
| 3 | one home per identical family; diverged variants kept | 5 promoted groups merged into `gnd.artifacts`; see the group table below | same | **holds** under CR3 and CR5, with eight candidate groups that were never promoted listed below |
| 4 | `cli.py` at most 2,500 lines; no entry-point violation | 667 lines; 0 violations | 733 lines; 0 violations | **holds** |
| 5 | before/after table committed; every missed original target listed | the table below and close-table.txt | | **holds** with this file |

## Before and after

| Measure | RF0 `19b131b` | End `a390599c` | Main `99cf3df2` |
|---|---|---|---|
| Modules / lines | 148 / 104,094 | 228 / 111,580 | 296 / 143,456 |
| Runtime SCCs over one module (largest) | 5 (14) | 0 | 0 |
| Wrong-way layer edges | 27 | 0 | 0 |
| Clean layers | 2 of 6 | 6 of 6 | 6 of 6 |
| Cross-lane edges | 54 | 153 | 190 |
| Private cross-module imports | 242 | 680 | 804 |
| AST-identical groups | 15 | 12 | 22 |
| Largest module | `cli` 9,088 | `model._validation` 4,890 | `model._validation` 4,989 |
| `cli.py` | 9,088 | 667 | 733 |

Private imports rose, as RF5 (010:178) and RF9 (015:98) said: moved private
names kept compatibility aliases. The plan set no target on them. Main's
later growth (cross-lane, identical groups) comes from later milestones and is
not this milestone's result.

## The candidate groups of `helper-families.md`

From [close-families.md](close-families.md):

| State | Groups |
|---|---|
| promoted and merged (one home in `gnd.artifacts`) | `f4d89086`, `2f5a20a1`, `5bebc70e`, `d9f0cf8e`, `dcbdd645` |
| algorithm in `ModelIndex`; one-line wrappers kept for old import paths | `22614c42` (3 wrappers), `c9b00e5d` (2) |
| kept separate by RF4's ruling (spec D2, design F) | `0f1cc1a7`, `3d106ff9` |
| never promoted or ruled | `ccbb68bd` (`_rate`), `c4e1c0f8` (needs an RF-D10 rename ruling first), `73ae047d` and `5153de62` (RF8 moved them, did not merge) |
| not a family (constructors) | `cf363396`, `cd3b7244` |

Owner decision C-D2 is whether the four never-ruled groups are carried or
accepted as they are.

## Original targets missed (RF-D13)

| Phase | Original | Measured / re-target | Ruling | Source |
|---|---|---|---|---|
| RF0 | `tests/test_gnd_arch.py` 650 lines | 666; 700 | owner | 004:90 |
| RF1 | `mutations.json` estimate 700 | 1,705 | owner accepted | 006:132 |
| RF1 | `test_rf1_helper_pins.py` estimate 350 | 535 | owner accepted | 006:133 |
| RF3 | non-relocated added 700 | 1,987; 2,200 | delegated A6 | 008:362 |
| RF4 | non-relocated 2,200 | 3,971; 4,200 | delegated A6 | 009:311 |
| RF4 | tests and data 1,800 | 3,515; 3,600 | delegated A9 | 009:311 |
| RF4 | touched 130, docs 180 | 250, 800 | delegated A5 | 009:311 |
| RF6b | model facade 400 | 758; 900 | delegated A1 | 012:366 |
| RF7 | touched 180 | 183; 210 | delegated | 013:358 |
| RF8 | touched 90 | 120, then 140 | delegated A4, A6 | 014:193 |
| RF8 | non-relocated 650 | 1,005; 1,100 | delegated A5 | 014:191 |
| RF8 | `session_v7` estimate 937 | 976 at base (goal of at most 60 met: 58) | estimate error | 014:191 |
| RF9-ci-repair | touched 80 | over; 90 | delegated | 017:112 |

From RF3 on, the re-targets are delegated rulings under the phase's `auto`
selection, where RF-D13 says the owner may re-target.

## Lanes

Full default lane at main `99cf3df2`, six shards on beast-3:
[default-lane.txt](../evidence/close/default-lane.txt): **22,057 passed, 0 failed, 2
errors, 13 skipped** (uv 0.13.7, Python 3.13.18, macOS 27.0.1). The two errors are
`tests/test_public_optional.py`, carried as RC-02 by the release-0.5.0 close; the
13 skips are `tests/test_guarded_clause_exports.py` without `GND_PYREL_PYTHON`.
The milestone's own full-suite gate at `a390599c` is record 017's (13,944 passed,
400 deselected, on two Python minors).

## Owner decisions for the close ruling

- **C-D1 (predicate 2).** The seven package-internal cycles (a package's
  `__init__` re-exports a submodule that imports its parent package):
  three in the named layers (`gnd.model`, `gnd.checker`, `gnd.assurance`
  with their own submodules). Proposed: predicate 2 holds on the RF0 graph,
  and the cycles are carried to a successor as RF9 recorded them
  ("diagnostic, not a zero-cycle claim", 016:343). Alternative: predicate 2
  fails and a repair phase precedes the close.
- **C-D2 (predicate 3).** The four never-ruled candidate groups. Proposed:
  carried with the residuals below; none blocks the close.
- **C-D3.** Accept the residuals and carried items in
  [close-question-sweep.md](close-question-sweep.md), "Close dispositions".
