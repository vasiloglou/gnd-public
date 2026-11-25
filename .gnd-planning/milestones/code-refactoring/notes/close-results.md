# code-refactoring close results

Judged on 2026-11-25; r2 after the light close panel
([review](../evidence/close-panel/PANEL-REVIEW.md),
[disposition](../evidence/close-panel/disposition.md)). Three measurement
points: the RF0 baseline `19b131b`, the milestone's last phase commit
`a390599c1a8fe8bdf13596e2f71805b6a94e109d` (record 017,
`source_subject`), and main `99cf3df2`. The plan's close repairs CR1 to
CR13 (plan, "Close repairs") set how each predicate is read. Measurements:
[close-table.txt](../evidence/close/close-table.txt), from
`tools/gnd_arch.py measure` at the RF0 baseline (`19b131b`), at `a390599c`
(from `git archive`) and at main.

## Predicates

| # | Predicate | At `a390599c` | At main `99cf3df2` | Judgement |
|---|---|---|---|---|
| 1 | RF1 suite green; no expected value changed | the file diff of `tests/fixtures/rf1-pins` without `mutations.json`, from the RF1 capture `5f56f5f6` to `a390599c`, is empty; the seven commits in that range changed only mutation targets ([pin-history.txt](../evidence/close/pin-history.txt)). RF7's nineteen restriction successors are bound apart, in `tests/fixtures/rf7-restrictions/successors.json` (19 rows, unchanged since) (CR2). Full suite at `a390599c`: 13,944 passed, 400 deselected (017) | regression check only: 758 passed for `tests/test_rf1_*.py`, `tests/test_rf5_commands.py`, `tests/test_gnd_arch.py` ([predicates-focused.txt](../evidence/close/predicates-focused.txt)), against values that 32 later commits re-recorded (84 files); this close does not review those commits | **holds** under CR2, judged at `a390599c` |
| 2 | every module mapped; layering test with no xfail; no multi-module SCC in model, population, checking or semantics | 228 modules, 0 unmapped ([metrics-a390599c.json](../evidence/close/metrics-a390599c.json)); 0 runtime and 0 module-only SCCs; 0 wrong-way edges; 6 of 6 layers clean; 0 allowances | 296 modules, 0 unmapped ([metrics-close.json](../evidence/close/metrics-close.json)); the same zeros; `tests/test_rf1_layering.py` has no xfail marker (its one "xfail" is in the docstring) and passes ([predicates-focused.txt](../evidence/close/predicates-focused.txt)) | **holds on the RF0 import graph** (CR4). On the package-initializer graph RF9 added it does not: seven package-internal cycles, three in the named layers (`gnd.model`, `gnd.checker`, `gnd.assurance` with their own submodules). The owner ruled C-D1: carried |
| 3 | one home per identical family; diverged variants kept | 5 promoted groups merged into `gnd.artifacts`. RF1's pins agree for five more groups that keep several definitions ([pin-agreement.txt](../evidence/close/pin-agreement.txt)); RF7 merged three diverged families | same | **not met as written** for those five groups, and the diverged-variant sentence is superseded for RF7's three only if the owner ratifies CR3: owner decisions C-D2 and C-D5 |
| 4 | `cli.py` at most 2,500 lines; no entry-point violation | 667 lines; 0 violations | 733 lines; 0 violations | **holds** |
| 5 | before/after table committed; every missed original target listed; every target met against its final owner-ruled value | the table below and close-table.txt; fourteen missed originals: three re-targeted or accepted by the owner, ten by delegated phase rulings, one an estimate error | | the table and list are complete; "owner-ruled" holds for the ten delegated values only if the owner ratifies them: owner decision C-D4 |

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

From [close-families.md](close-families.md), with RF1 pin agreement measured
from the helper goldens ([pin-agreement.txt](../evidence/close/pin-agreement.txt);
those golden files are unchanged since `a390599c`). Under RF0 D7 a candidate
"becomes identical ... only when RF1's byte pins agree on every pinned input".

| Group | RF1 pins | Definitions now | Ruling in the records |
|---|---|---|---|
| `f4d89086`, `2f5a20a1`, `5bebc70e`, `d9f0cf8e`, `dcbdd645` | agreed (RF2) | one each, in `gnd.artifacts` | merged in RF2 |
| `22614c42` object types by id | agree (3 of 3) | 3 one-line wrappers over `ModelIndex.object_map` | RF6a A3/A4: algorithm in `ModelIndex`, wrappers kept for old import paths |
| `c9b00e5d` role to object type | agree (2 of 2) | 2 one-line wrappers over `ModelIndex.role_map` | same |
| `0f1cc1a7` safe coordinate | agree (2 of 2) | 2 | RF4 spec D2 and design F: no variant merge |
| `ccbb68bd` `_rate` | agree (2 of 2) | 2 | none ("recorded, no action proposed", helper-families.md) |
| `c4e1c0f8` `_sorted_set` / `_canonical` | agree (2 of 2) | 2 | none; helper-families.md requires an RF-D10 rename ruling first, never given |
| `3d106ff9` directory identity | one site pinned; the other was nested (owed to RF4, which pinned its refusal) | 2 | RF4 design F: no merge |
| `73ae047d`, `5153de62` (session) | pinned through the session replays, not per site | 3 and 2 | RF8 moved them, no merge ruling |
| `cf363396`, `cd3b7244` | not a family (constructors) | | |

So predicate 3's first sentence is not met for five groups whose pins agree.
Three of them have phase rulings that kept them apart (RF6a's wrappers,
RF4's no-merge); `_rate` and `c4e1c0f8` have none. r1's CR5, which read
"marks identical" as "promoted", is withdrawn: the panel showed it changed the
predicate's meaning. The four never-ruled groups of r1 are, measured, two
with agreeing pins and two pinned only through session replays.

## Original targets missed (RF-D13)

| Phase | Original | Measured / re-target | Ruling | Source |
|---|---|---|---|---|
| RF0 | `tests/test_gnd_arch.py` 650 lines | 666; 700 | owner | 004:90 |
| RF1 | `mutations.json` estimate 700 | 1,705 | owner accepted | 006:132 |
| RF1 | `test_rf1_helper_pins.py` estimate 350 | 535 | owner accepted | 006:133 |
| RF3 | non-relocated added 700 | 1,987; 2,200 | delegated A6 | 008:362 |
| RF4 | non-relocated 2,200 | 3,971; 4,200 | delegated A6 | 009:311 |
| RF4 | tests and data 1,800 | 3,515; 3,600 | delegated A9 | 009:311 |
| RF4 | touched files 130 | 249; 250 | delegated A5 | 009:311; RF4-final-budget.json |
| RF4 | documentation 180 lines | 578; 800 | delegated A5 | 009:311; RF4-final-budget.json |
| RF6b | model facade 400 | 758; 900 | delegated A1 | 012:366 |
| RF7 | touched 180 | 183; 210 | delegated | 013:358 |
| RF8 | touched files 90 | 136; 120, then 140 | delegated A4, A6 | 014:193; RF8/budget.json |
| RF8 | non-relocated 650 | 1,005; 1,100 | delegated A5 | 014:191 |
| RF8 | `session_v7` estimate 937 | 976 at base (goal of at most 60 met: 58) | estimate error | 014:191 |
| RF9-ci-repair | touched paths 80 | 84; 90 | delegated | 017:112; RF9-ci-repair/budget.json |

Fourteen rows (RF4's touched and documentation ceilings are two rows): three
originals re-targeted or accepted by the owner (RF0, both RF1 estimates); ten
by delegated phase rulings under each phase's `auto` selection (RF3, RF4 three
times, RF6b, RF7, RF8 twice, RF9-ci-repair); one estimate error (RF8
`session_v7`, whose goal was met). RF-D13 says the owner may re-target, so the
delegated values need the owner's ratification (C-D4).

## Lanes

Full default lane at main `99cf3df2`, six shards on beast-3:
[default-lane.txt](../evidence/close/default-lane.txt): **22,057 passed, 0 failed, 2
errors, 13 skipped** (uv 0.13.7, Python 3.13.18, macOS 27.0.1). The two errors are
`tests/test_public_optional.py`, carried as RC-02 by the release-0.5.0 close; the
13 skips are `tests/test_guarded_clause_exports.py` without `GND_PYREL_PYTHON`.
The milestone's own full-suite gate at `a390599c` is record 017's (13,944 passed,
400 deselected, on two Python minors). The pass condition this close applies:
0 failed; errors limited to the two RC-02 nodes; skips limited to the
`GND_PYREL_PYTHON` gate. The lane meets it.

## Owner decisions for the close ruling

| ID | Question | Proposal | Alternative and its cost | Owner |
|---|---|---|---|---|
| C-D1 | the seven package-internal cycles of the package-initializer graph (predicate 2) | predicate 2 holds on the RF0 graph; the cycles are carried to a successor, as RF9 recorded them ("diagnostic, not a zero-cycle claim", 016:343) | a repair phase that breaks the three core-layer cycles before the close | **ruled 2026-11-25: the proposal** ([owner-statements.txt](../evidence/close/owner-statements.txt)) |
| C-D2 | the five groups whose RF1 pins agree but keep several definitions (predicate 3) | accept them as residuals: three are kept apart by phase rulings (RF6a wrappers for old import paths; RF4 no-merge), `_rate` and `c4e1c0f8` are carried; predicate 3 is recorded as not met for them | a small repair phase before the close: merge `_rate`, and give `c4e1c0f8` its RF-D10 rename ruling or record it diverged by meaning | ruled 2026-11-25 on r1's premise that pin agreement was unknown; **to be put again** with the measurement |
| C-D3 | the residuals and carried items of [close-question-sweep.md](close-question-sweep.md), section F | accept them | reopen named rows as work before the close | open |
| C-D4 | the ten delegated re-targets and the delegated RF5 re-plan (predicate 5) | ratify them as the final owner-ruled values | record predicate 5 as unmet for those rows | open |
| C-D5 | CR3: RF7's merges of the JSON intake, datetime and file-digest families supersede RF-D11 and predicate 3's second sentence | ratify, as the RF7 amendment did for RF-R1 | record predicate 3's second sentence as unmet for those three families | open |

Carried items name no successor milestone. Tracking issues for C-D1's three
core-layer cycles, `_rate`, `c4e1c0f8` and the session groups can be filed on
the owner's word.
