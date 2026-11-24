---
milestone: pins-and-review-check
station: "milestone close"
skill: "n/a -- repository development; process-milestone auto=true"
scope: close
date: 2026-11-23
gate:
  command: "ruling: delegated (auto=true) approved .gnd-planning/milestones/pins-and-review-check/notes/pins-and-review-check-plan.md sha256 3ebf67e281d32ab3ebba03428cf5aa3c68a0546b1512c41957482d298d8b5859"
  exit: "n/a -- ruling"
gates:
  - {name: "PF1 focused lane", command: "uv run pytest -q -p no:cacheprovider tests/test_inventory_pin_home.py tests/test_packaged_skills.py tests/test_install.py tests/test_doctor_uninstall.py tests/test_verification_fixes.py tests/test_gate_guard_list.py --tb=short", exit: 0, output: "241 passed in 39.16s"}
  - {name: "structure and inventory guards (project.md block)", command: "the guard command of project.md, with -p no:cacheprovider", exit: 0, output: "866 passed, 2 deselected in 195.01s (0:03:15)"}
  - {name: "lint, plan form", command: "uv run ruff check src tests tools", exit: 0, output: "All checks passed!"}
  - {name: "lint, whole repository", command: "uv run ruff check", exit: 0, output: "All checks passed!"}
  - {name: "component index", command: "python3 scripts/components_index.py changed --base origin/main --strict", exit: 0, output: "changed against origin/main (a027059): 108 file(s) differ; 0 to fix, 0 warning(s), 0 to reread"}
  - {name: "distribution lane, recorded", command: "uv run pytest -q -p no:cacheprovider -m distribution tests/test_public_built_inventory.py", exit: 0, output: "17 passed in 18.97s"}
  - {name: "PF2 key fixed before the runs", command: "cd evidence/PF2 && shasum -a 256 -c KEY-SHA256SUMS", exit: 0, output: "5 OK"}
base: "b140554b (claude/pf2-review-calibration, stacked on PR 250 and PR 248)"
evidence:
  - {path: .gnd-planning/milestones/pins-and-review-check/notes/pins-and-review-check-plan.md, sha256: 3ebf67e281d32ab3ebba03428cf5aa3c68a0546b1512c41957482d298d8b5859}
  - {path: .gnd-planning/milestones/pins-and-review-check/001-plan.md}
  - {path: .gnd-planning/milestones/pins-and-review-check/002-phase-PF1.md}
  - {path: .gnd-planning/milestones/pins-and-review-check/003-phase-PF2.md}
---

# Claim

Both phases of pins-and-review-check have their records, and the
milestone's exit gates are green at `b140554b`. The packaged-skill inventory
has one home with a guard, and `tests/test_verification_fixes.py`, red on
`main`, passes. The standing fitted-code review check has a first
measurement: 4 of 4 planted defects found, 0 false findings, on eight runs.
Nothing is merged: PRs 248, 250 and 253 wait for the owner.

## Exit predicates (plan, Goal)

| Predicate | Result |
|---|---|
| each phase has its record | PF1 `002-phase-PF1.md`; PF2 `003-phase-PF2.md` |
| green focused gates | PF1 lane 241 passed; PF2's checks E1–E5 (its record) |
| the guard block | 866 passed (it now includes the four PF1 files) |
| `uv run ruff check` | both forms pass |
| the component-index check | 0 to fix |
| a close review on the D3 instrument | below |

## Phases

| Phase | Record | PR | Result |
|---|---|---|---|
| PF1 | `002-phase-PF1.md` | [250](https://github.com/vasiloglou/gnd-public/pull/250) | inventory defined once in `tests/test_packaged_skills.py`; three files import it; a guard over every binding of the three names; four files in the guard block; one red file on `main` repaired, and the distribution lane's inline counts too (a1). Two review rounds: every finding reproduced; round 1 F1–F3 and round 2's three fixed, round 1 F4 (two inline `18`s) carried as OQ2. The close review's two guard misses were fixed after the record (its addendum) |
| PF2 | `003-phase-PF2.md` | [253](https://github.com/vasiloglou/gnd-public/pull/253) | 4 of 4 planted found, 0 missed, 0 false findings, 2 true findings on controls (one a defect on `main`). One review round; three evidence repairs, no grade changed |

## Refuted premises and plan repairs

Plan amendment c1 (`notes/pins-and-review-check-plan.md`, sha256
`3ebf67e2…5859`) records five repairs with their raising records and prior
wording: C1 the deliberate duplication, C2 PF1's added home, C3 the guard's
true scope, C4 inline counts outside any name guard, C5 blindness by
arrangement only.

## Open-questions sweep

| Source | Question | Disposition |
|---|---|---|
| plan §10, PF1 | none beyond D1 and D5 | closed: both ruled at the plan gate and applied |
| plan §10, PF2 | the corpus and the wording that counts as "names a breaking input" | closed: PF2 spec §6 Corpus and Grading |
| PF1 OQ1 | keep `c1ecb8c1`? | closed: kept, delegated ruling, PF1 spec amendment a1 |
| PF1 OQ2 | inline `== 18` in `tests/test_development_scaffold.py:200` and `tests/test_marketplace_plugins.py:25`; PR 254 shows one more copy, the recorded install output `placed 71 file(s)` in `tests/fixtures/rf5-handlers/answers.json` | **carried** to the owner: a maintenance pass (plan C4). No name guard sees a literal in a test or a fixture |
| PF1 OQ3 | 14 default-lane tests red on `main` in five files | **closed outside this milestone**: [PR 254](https://github.com/vasiloglou/gnd-public/pull/254), merged on `main` on 2026-11-23, repaired all 19 (these 14 and the 5 inventory ones). PF1's branch merged `main` and keeps its import over PR 254's literal 71 in `tests/test_verification_fixes.py` and `tests/test_public_built_inventory.py`; gates green on the merge (`4ac609d6`) |
| PF2 OQ4 | `gnd.exp.frontmatter._split` takes an indented `---` as the closing fence | **carried**: a separate session started at the owner's request on 2026-11-23 fixes it with a regression test in its own pull request |
| PF1 refuted premise | the duplication was deliberate | closed: plan C1 |
| PF1 and PF2 reviews | repaired bytes with no review opinion (PF1 round-2 repair; PF2 evidence repairs) | closed: read by the close review below |
| close review F1, F2 | the guard missed a star import and a function-scope bare annotation | closed: fixed in `49de26cb` with cases that fail on the previous guard; **this repair carries no review opinion** (accepted residual) |
| close review F3 | this record said every PF1 finding was fixed | closed: the phase row now separates the fixed findings from F4 (OQ2) |
| plan D3 | the panel bar waived for this milestone | **accepted residual**: plan, phase and close reviews are one reviewer each, not a panel |
| PF2 limits | eight runs, one author, one reviewer | **accepted residual**: no rate is claimed |

## Close review

Instrument: the review helper, one reviewer in a different tool (Codex,
read-only, reasoning high), plan D3. **One reviewer is one reviewer; this is
not a panel** (D3 waived the panel bar for this milestone). Brief
`notes/reviews/close-r1/` over this record's draft, the plan, both phase
records and specs, `GRADING.md` and the guard, asking it to refute the exit
predicates, the sweep, the plan repairs and the unreviewed bytes.

CHANGES_REQUESTED, three findings, each reproduced before it was believed:

- **F1:** `from test_public_distribution_runtime import *` binds a 59-file
  inventory and the guard returned nothing.
- **F2:** a bare annotation inside a function makes the name local; the guard
  exempted it.
- **F3:** the phase table said every PF1 finding was fixed, while round 1 F4
  was carried.

All three repaired (F1, F2 in `49de26cb` on PR 250, merged forward; F3 in the
phase table above). Plan repair C3 now states the guard's final rule. The
reviewer reproduced all 64 PF2 grading rows and the 15-of-71 count, found the
key's checksums good and the carried questions honestly described. One
round, the close budget; **the F1/F2 repair carries no review opinion**.

## Close ruling

**Delegated approval (auto=true), 2026-11-23.** Authorization: the owner's
`process-milestone pins-and-review-check auto` of 2026-11-23, this milestone
only; an agent ruling under that delegation, not the owner's reading. The
milestone is **closed locally**: both phases are recorded, the exit gates are
green at `b140554b`, the close review ran and its findings are repaired, and
the plan as amended (c1, sha256 `3ebf67e2…5859`) is approved. Carried to the
owner: OQ2 and OQ4; OQ3 was closed on `main` by PR 254. Not covered by the delegation and still the owner's:
merging PRs 248, 250 and 253, in that order.

## Boundary -- what this result did NOT establish

- A detection rate for the standing check; how it does with another reviewer
  or subtler fitted code.
- That no test restates the inventory: inline literals are outside any name
  guard (OQ2).
- A fix for OQ4 (a separate session owns it); OQ3's repair is PR 254's, not this milestone's.
- Merge, release or publication.

## After the close (2026-11-23)

OQ2 was fixed at the owner's request by a maintenance pass,
[2026-11-23-inline-inventory-counts](../../maintenance/2026-11-23-inline-inventory-counts/README.md).
OQ4 was fixed by [PR 255](https://github.com/vasiloglou/gnd-public/pull/255),
merged on `main`.
