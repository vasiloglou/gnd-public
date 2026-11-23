---
milestone: literature-host-interfaces
station: "phase-LH1"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-LH1
date: 2026-11-23
gates:
  - command: "ruling: delegated (auto=true) approved .gnd-planning/milestones/literature-host-interfaces/notes/phase-LH1-spec.md sha256 93cd0f95314cdd027900475bb4ea0e1558fa3e0a04efae357302ba3e38c90e12"
    exit: "n/a -- ruling"
  - command: "uv run pytest -q tests/test_lh1_reading_host.py tests/test_ld3_reading_workflow.py tests/test_ld4_revision.py tests/test_ld5_verdict.py tests/test_li1_assurance_report.py tests/test_ld1_competency_examples.py --tb=short"
    exit: 0
    output: "251 passed in 379.01s (0:06:19)"
    note: "plan §9 LH1 row plus tests/test_ld1_competency_examples.py, added because depth.py changed (spec finding 9)"
  - command: "the project.md structure and inventory guard block (12 files)"
    exit: 0
    output: "679 passed, 2 deselected in 120.93s (0:02:00)"
  - command: "uv run ruff check"
    exit: 0
    output: "All checks passed!"
  - command: "python3 scripts/components_index.py changed --base 78934ee3 --strict"
    exit: 0
    output: "changed against 78934ee3 (78934ee): 114 file(s) differ; 0 to fix, 0 warning(s), 1 to reread"
    note: "the reread line names examples.literature_depth: depth.py gained two keyword arguments whose defaults are today's values; its entry is still accurate"
slow_cadence:
  command: "uv run pytest -q -m \"evidence or census\""
  trigger: "explicit owner request or separately scoped CI selection"
  reason: "the broad controls are outside this phase's impact closure"
evidence:
  - path: .gnd-planning/milestones/literature-host-interfaces/notes/phase-LH1-spec.md
    sha256: b9e48c65cef90190afb05d7d262cbd06635b56a7fc58b238a612c309f236f25f
  - path: src/gnd/examples/literature/reading.py
    sha256: 679c10561d839745d66ce8c1aa1760f2b720c5e2e55dd2d385073fda44f7684f
  - path: src/gnd/examples/literature/depth.py
    sha256: f50ff0cbd22f73cf151b5985eb207828111e0cbde06cd4213e7c9211b4a798f7
  - path: src/gnd/examples/literature/reading_fixture/README.md
    sha256: 046790deff8f792fcbdd7c66b603d5d7383f241c92b4aa91e958c8f493e8dd90
  - path: tests/test_lh1_reading_host.py
    sha256: b4974946ba1f1ed9f2d56c1c68cd30218148ad09c825e4681de7aa34755770b7
  - path: .gnd-planning/milestones/literature-host-interfaces/notes/reviews/phase-LH1-r1/review.md
    sha256: 402e117938f29a690a0b415442adc31ee11248714815cd53a35fc8fee70ab4e8
  - path: .gnd-planning/milestones/literature-host-interfaces/notes/reviews/phase-LH1-r1/FINDINGS.md
    sha256: ac9b4f12c47d966b651df467dd710c4a4642b5abbaa757635595cc467f7519ec
  - path: .gnd-planning/milestones/literature-host-interfaces/notes/reviews/phase-LH1-r2/review.md
    sha256: bb1d287477545ce37c7b1ff68071e7082793b771c9b8ec959656849c08086579
  - path: .gnd-planning/milestones/literature-host-interfaces/notes/reviews/phase-LH1-r2/FINDINGS.md
    sha256: fd788e05f04bd7afd19844ecdfc9043e95a41401b819607200284ea8b16a1989
  - path: dev/components/COMPONENTS.md
    sha256: 8243162ca04ce32a39a90b79c62c9b243aae3d2280c1a600ed022b264e09e7cc
---

# Phase LH1: a live producer over a caller root

## Claim

`reading.run()` takes a producer object over a root that holds
`profile.json` and writes a `literature-reading-run/2` folder. Every LH1
criterion has a test in `tests/test_lh1_reading_host.py` (the spec's T1 to
T20, plus regressions R1 to R8 from review):

| Criterion | Tests |
|---|---|
| LH1-C1 | T1 |
| LH1-C2 | T2 |
| LH1-C3 | T3 |
| LH1-C4 | T4, T5, T6, T19 |
| LH1-C5 | T7 (three cases, including D6's continuation) |
| LH1-C6 | T8 |
| LH1-C7 | T9 (17 malformed answers), R2 |
| LH1-C8 | T10 |
| LH1-C9 | T11, and `test_ld3`, `test_ld4`, `test_ld5` unedited |
| LH1-C10 | T12 (roster, input, response, budget, timeout and route-output ceilings), T20 (retained ceiling) |
| LH1-C11 | T13 |
| LH1-C12 | T14 |
| LH1-C13 | T15: exits 2, 1 and 4 through real caller models; any other exit refuses |
| LH1-C14 | T20, R1, R5 |

The three packaged run configurations equal the trees recorded at
`78934ee3` before any edit (`389adcdc`), file for file, and their `run.json`
digests are P3's.

## Gate

Delegated approval (auto=true), 2026-11-23, under the owner's
`/process-milestone literature-host-interfaces auto`. It covered the spec at
sha256 `93cd0f95…0e12` (commit `c0068c27`), with LH1-D1 to LH1-D5 as
proposed. The spec has since been appended only, with its implementation
findings; the current bytes are the evidence row above. The owner's
`/process-milestone … auto` supersedes the plan gate's D15 ruling (phase by
phase) for this milestone.

## Review

One reviewer is one reviewer. Codex ran in the other harness, read-only,
through `review_tool.py` (plan D13), for two rounds:

| Round | Read | Findings | Blocking | Self-inflicted |
|---|---|---|---|---|
| r1 | the LH1 diff, base `c5fbaf58` | 4 | 4 | 0 |
| r2 | the r1 repair, base `83de2846` | 4 | 2 | 2 |

Every finding was reproduced before it was fixed, and each fix has a
regression test that failed on the code before it (the ledgers name them).
Round 2 was declared the last round in r1's ledger before it ran; its
repairs (`59fd62f0`) are not read by any reviewer. Both retained reviews
were sanitized of this machine's paths by `review_tool.py sanitize`, as
their headers say.

## Refactoring review

Refactors EXECUTED, each behavior-preserving behind T11's byte comparison
and the unedited `test_ld3`, `test_ld4`, `test_ld5`:

- The packaged constants (model and include names, label, producer label,
  calibration literals, conflict fact, step switches, route exits) became one
  data object, `PACKAGED_PROFILE`, read by the same loop as a caller's
  profile (R0.4).
- `gnd extract` moved out of `_public_results` into `_extract`, which runs
  before the first producer call for both roots.
- One row validator (`_fact_rows`) and one serializer for untrusted values
  (`_canonical`) replaced checks spread across the loop.

Deferred: none. `assurance_report._coverage_units` re-checks the coverage
row shape that `reading._outcomes` writes; it predates this phase and is
outside its homes, and it stays as an independent reader by design.

## Refuted premises and findings

- **Size.** `reading.py` grew from 610 to 1,146 lines (+695, -159 with
  `depth.py`), past the 400-line split threshold of plan §6 and spec §10.
  Splitting into LH1a and LH1b was ruled out by delegated approval (spec
  finding 1). The estimate of 300 to 380 lines was low by roughly half,
  most of it in the review repairs.
- The spec's retained bound ("roster cap times 1 KiB") did not bound
  roster strings or saved files; it is now a measured bound per file (r1-F1,
  r2-F1).
- Spec findings 2 to 9 record the other departures from the spec's letter.

## Open questions

None opened by this phase.

## Boundary

- **Replay of a caller run** is LH2's. `replay()` refuses a `/2` folder.
- **No review reads `59fd62f0`'s repairs.** The round budget was two, and
  round 2 read only the round-1 repair.
- **Speed.** The time bounds are measured on this machine (Apple silicon,
  2026-11-23); T12 and T20 hold them, but other machines are not measured.
- **Packaged steps on new arguments.** The packaged root refuses every new
  argument (LH1-D1); a host gets the new behavior only through a profile.
- **Out of scope.** No change to any stable command, to `revision.py` or to
  `assurance_report.py`; no command-line flag.
