---
milestone: code-refactoring
station: "phase-RF0"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-RF0
date: 2026-10-05
gate:
  command: "uv run pytest -q tests/test_gnd_arch.py"
  exit: 0
  output: "46 passed"
  base: "19b131b (branch merged with main cbb9783; owner amendment 1 in the RF0 spec)"
selection:
  - {obligation: "direct tool behavior", disposition: run, command: "uv run pytest -q tests/test_gnd_arch.py", exit: 0}
  - {obligation: "lint", disposition: run, command: "uv run ruff check tools/gnd_arch.py tests/test_gnd_arch.py", exit: 0}
  - {obligation: "RF-R1 and RF-R7: no src/gnd or public-launch change", disposition: run, command: "git diff --quiet 19b131b HEAD -- src/gnd .gnd-planning/milestones/public-launch", exit: 0}
  - {obligation: "planning links (amended D11)", disposition: run, command: "uv run pytest -q tests/test_development_scaffold.py", exit: 0}
  - {obligation: "RF0-C1 determinism", disposition: run, command: "two measure runs compared with cmp, and with the committed metrics", exit: 0}
  - {obligation: "distribution lane", disposition: cadence, note: "fixed separately in vasiloglou/gnd-public#8 (D4)"}
  - {obligation: "full default lane", disposition: cadence, note: "not selected: RF0 changes no imported code"}
evidence:
  - path: tools/gnd_arch.py
    sha256: f7b92b206a199b49e615cadb3c3f4add01283d4d25349feb051e0bc3ef3438fc
  - path: tools/gnd_layers.json
    sha256: 405e2b0dc9edfb5daed7a446a51241c739ba6bb60f8ce6e86ecb7962da840b3a
  - path: tests/test_gnd_arch.py
    sha256: 3aa37f721d5f47bc99084d58358dc32f6fa9c284aaafe807249288d3eff2c50f
  - path: .gnd-planning/milestones/code-refactoring/evidence/metrics-RF0.json
    sha256: fdecd3715518437831c009ecd7af4b8ac32b4f1cf3d5eeb20188b4e235b4fc80
  - path: .gnd-planning/milestones/code-refactoring/evidence/phase-RF0/review-regressions-red.txt
    sha256: c72e95bd8f23916e5f4ad4be4cd4b757f338cf3ad4190ceff9798de964d55c49
  - path: .gnd-planning/milestones/code-refactoring/notes/phase-RF0-spec.md
    sha256: efafb32b116a39bc780a25ece12fffb732dd8aa6a9d5976ab23e99546c88da9e
  - path: .gnd-planning/milestones/code-refactoring/notes/rf0-baseline.md
    sha256: 1c383e20012d9b9d7d644a7d34ed63396cf09f19f55f40e191cfbdb721176099
  - path: .gnd-planning/milestones/code-refactoring/notes/helper-families.md
    sha256: a09a5da453f5e69914e323f56e956d273063c9a6158f517c93f847b7cf113a05
  - path: .gnd-planning/milestones/code-refactoring/notes/phase-RF0-codex-review.md
    sha256: d44ed2bca48917bc3a90cde0d39348e4756b0edc7d82009bea0de67f6ab11648
---

# Claim

At base `19b131b`, `uv run pytest -q tests/test_gnd_arch.py` exited 0
(46 passed), and every other run row of the selection ledger exited 0. RF0's
measurement tool, layer map, baseline notes and helper-family
classification are committed, and no `src/gnd` or public-launch byte
changed.

## Gate output (verbatim)

    $ uv run pytest -q tests/test_gnd_arch.py
    46 passed in 4.52s
    $ uv run ruff check tools/gnd_arch.py tests/test_gnd_arch.py
    All checks passed!
    $ git diff --quiet 19b131b HEAD -- src/gnd .gnd-planning/milestones/public-launch
    (exit 0)
    $ uv run pytest -q tests/test_development_scaffold.py
    14 passed, 1 deselected in 2.95s
    $ uv run python tools/gnd_arch.py measure --out d1.json   (and again to d2.json)
    $ cmp d1.json d2.json && cmp d1.json .gnd-planning/milestones/code-refactoring/evidence/metrics-RF0.json
    (exit 0)

## Criteria

| Criterion | Result |
|---|---|
| RF0-C1 deterministic output | Met: byte-identical runs (T1, gate row 5) |
| RF0-C2 cycles confirmed, refuted or new, with edges | Met: [rf0-baseline.md](notes/rf0-baseline.md) cycle register. The core cycle is 14 modules (one dynamic edge, checked at `semantic_spec.py:1613`); `agent_cli ↔ exp` is refuted; no new SCC |
| RF0-C3 audit rows marked with measured values | Met with D2's third status: 19 rows (A1–A19). The confirmed rows are A1, A4, A12 (three meanings), A17, A18 and A19; refuted, partly confirmed and unverifiable rows are as listed in the note |
| RF0-C4 map coverage test that can fail | Met: T7d, with T7e proving it fails |
| RF0-C5 inventories counted at execution | Met: pin-site inventory and helper families come from the tool |
| RF0-C6 handoff statement and RF-D3 ruling | Met: see *Authority handoff* below; RF-D3 = D4 (b), ruled 2026-10-05 |

## Authority handoff (RF-D1, RF-R7)

The `runtime` and `test-acceptance` units are developed in `gnd-public` from
this record's commit forward, by owner ruling RF-D1. The owner's stated
intent in public-launch's `009-milestone-close.md` (archive the source
repository and develop only in gnd-public) agrees. The public-launch ledger
`units.json` is not edited by this milestone. Under RF-R7 and D8, the
source-side control rests on owner attestation; no source remote was
supplied.

## Budgets (D9)

| Item | Estimate | Ceiling | Measured |
|---|---|---|---|
| `tools/gnd_arch.py` | 750 | 900 | 858 |
| `tools/gnd_layers.json` | 200 | 250 | 168 |
| `tests/test_gnd_arch.py` | 500 | 650, re-targeted to 700 | 666. The original 650 was missed (13 review-regression tests added 161 lines). Owner ruling under RF-D13, 2026-10-05: re-target to 700; the miss stays listed in the close table |
| RF0 notes | 450 | 600 | 183 (`rf0-baseline.md` 132 + `helper-families.md` 51) |

## Review

One reviewer is one reviewer. A single Codex review (gpt-6-sol, xhigh,
read-only sandbox, prompt on stdin) reported 13 findings and could not run
pytest in its sandbox. Nine were reproduced red by regression tests
(evidence: 9 failed, 4 passed) and are now fixed. Three were note
corrections made in place. One part of RF0-09 (patches of non-`gnd` targets)
is kept by design. The dispositions are in
[phase-RF0-codex-review.md](notes/phase-RF0-codex-review.md).

## Boundary — what this result did NOT establish

- The tool measures imports and names. It establishes nothing about runtime
  behavior, and AST identity is not behavioral identity: D7 requires RF1
  byte pins before any merge.
- AST hashes are comparable only under Python 3.14.
- Commit counts and co-change cannot be measured here (D3).
- The patch inventory leaves out targets bound to non-`gnd` imports, and
  records 71 targets that cannot be resolved statically as
  `resolved: false`. Test-file alias bindings are file-wide, not scoped.
- One reviewer's reading, without a test run, is not a panel.
- No `src/gnd` code was refactored; RF0 only measures.

## Refactoring review

**None executed; one deferred.** RF0 added tooling and changed no product
code. One thing seen in the tool itself: `_ModuleVisitor` and
`_TestVisitor` each implement import-alias resolution, and after RF0-08 only
the module visitor is lexically scoped. That is a second answer to the same
question, which can drift. **Deferred** to RF1 (the next consumer of the
patch inventory) as an open question, not executed here, because changing
the test visitor's binding semantics would shift the counts this record
cites.

## Open questions

- **RF0-OQ1 (closed):** the tests ceiling of 650 was missed (666). Owner
  ruling 2026-10-05: re-target to 700. Carried to the close table as an
  original target that was missed.
- **RF0-OQ2 → RF1:** unify the two alias resolvers in `tools/gnd_arch.py`
  (refactoring review above).
- **RF0-OQ3 → RF1:** RF1's per-edge strict xfail list is the 27 wrong-way
  edges in `metrics-RF0.json`; `declared_clean` = entry, infrastructure.
- **RF0-OQ4 → RF2 spec gate:** under D7, the audit's identical
  canonical-JSON helpers are all diverged (F2). Accept, or rule an
  additional normalized view.
- **RF0-OQ5 → RF3 spec gate:** the dynamic `__import__` at
  `semantic_spec.py:1613` is the edge that puts `semantic_spec` in the core
  cycle (F3).
- **RF0-OQ6 → RF8 spec gate and milestone close:** the first
  `SESSION_CONTRACT_VERSION` assignment is live (F1). RF-D8's removal is
  withdrawn, and the plan text is repaired at close.
- **RF0-OQ7 → milestone close:** repair the plan's predicate 5 (co-change,
  D3) and RF-D2 (tag condition, owner amendment 2) text.

## Refuted premises

- Plan RF-D8: "remove the dead first assignment of
  `SESSION_CONTRACT_VERSION`". It is not dead (`exp/session_contract.py:482`
  captures it); see `rf0-baseline.md` A13.
- Plan predicate 5's co-change column is measurable in this repository: it
  is not (D3).
- The audit's "11 identical canonical-bytes sites": none of them is
  AST-identical to another (A6).
