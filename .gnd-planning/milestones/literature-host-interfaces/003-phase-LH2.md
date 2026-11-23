---
milestone: literature-host-interfaces
station: "phase-LH2"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-LH2
date: 2026-11-23
gates:
  - command: "ruling: delegated (auto=true) approved .gnd-planning/milestones/literature-host-interfaces/notes/phase-LH2-spec.md sha256 2e15cb11bdf2d9106acfe5b2beaa4572d86ba68dbb94889fc54a08c60dcd4ef8"
    exit: "n/a -- ruling"
  - command: "uv run pytest -q tests/test_lh2_reading_replay.py tests/test_lh1_reading_host.py tests/test_ld3_reading_workflow.py tests/test_ld4_revision.py tests/test_ld5_verdict.py tests/test_li1_assurance_report.py tests/test_ld1_competency_examples.py --tb=short"
    exit: 0
    output: "281 passed in 508.98s (0:08:28)"
    note: "plan §9 LH2 row plus tests/test_ld1_competency_examples.py (depth.py, LH1 finding 9)"
  - command: "uv run python tools/run_tutorials.py --group literature"
    exit: 0
    output: "15 tutorial blocks passed"
  - command: "the project.md structure and inventory guard block (12 files)"
    exit: 0
    output: "679 passed, 2 deselected in 106.53s (0:01:46)"
  - command: "uv run ruff check"
    exit: 0
    output: "All checks passed!"
  - command: "python3 scripts/components_index.py changed --base 0c23f30c --strict"
    exit: 0
    output: "changed against 0c23f30c (0c23f30): 19 file(s) differ; 0 to fix, 0 warning(s), 0 to reread"
slow_cadence:
  command: "uv run pytest -q -m \"evidence or census\""
  trigger: "explicit owner request or separately scoped CI selection"
  reason: "the broad controls are outside this phase's impact closure"
evidence:
  - path: .gnd-planning/milestones/literature-host-interfaces/notes/phase-LH2-spec.md
    sha256: ec41cccdf7bb099e1129e11fb141126b35b4b2e60887ac8996e3abfadbaed647
  - path: src/gnd/examples/literature/reading.py
    sha256: cad2bea4aa679310e154f98bcdad3e85e89cba581812ba703f059d737246d8b6
  - path: src/gnd/examples/literature/assurance_report.py
    sha256: eb5bf73f97b9a7f400ae4c68348334fd8dfba932ceea5b585341f74da3d56078
  - path: src/gnd/examples/literature/reading_fixture/README.md
    sha256: 797c060777fd392dee286322c38b45ac4faf79df08847f50dbe46acf449c57c7
  - path: tests/test_lh2_reading_replay.py
    sha256: 84f9895071d52affdceff71defc02d8ff75f8c7cb6136d27832cd067ed8d7983
  - path: tests/test_lh1_reading_host.py
    sha256: c0db56071a7f2f5c17ff521949c748b3aaf7f5b2656950b698741ff1b19cc5fe
  - path: docs/literature/commands.md
    sha256: 9d7f3d092c276124d8df27689abbad397d912922f7d34ee8f7b3c72a60470181
  - path: docs/release-notes.md
    sha256: 3fde981b1b7c920b17cae776352b7bdda18a358df90b40b37e601e4270a3f62e
  - path: .gnd-planning/milestones/literature-host-interfaces/notes/reviews/phase-LH2-r1/review.md
    sha256: 066aed2030be6d523d8d0df9a083bde32cda16f12559400cb80ac2ce9530ea3a
  - path: .gnd-planning/milestones/literature-host-interfaces/notes/reviews/phase-LH2-r1/FINDINGS.md
    sha256: 5736726aaeffba3890039819e20712b559e644fe7d8cbe7d6aab2890f63da674
---

# Phase LH2: replay of a caller run

## Claim

`replay(folder, fixture=root)` re-derives a `literature-reading-run/2`
folder from its own files and the caller root, with no producer and no
reviewer, and refuses every changed file, changed input, malformed manifest
and out-of-ceiling setting. Criteria and their tests in
`tests/test_lh2_reading_replay.py`:

| Criterion | Tests |
|---|---|
| LH2-C1 | T1 (a plain live run and a declared run with a live reviewer, replayed byte-identical with zero calls) |
| LH2-C2 | T2 (one changed byte in the response table and in a receipt; a consistently rewritten folder with and without the expected digest) |
| LH2-C3 | T3 (lowered and raised limits with a document budget; the 9-section run at the response ceiling within 60 s; `route_seconds` 601) |
| LH2-C4 | T4 (source, profile, model and include each refuse "stale reading input") |
| LH2-C5 | `test_ld3`, `test_ld4`, `test_ld5` unedited, in the focused lane |
| LH2-C6 | T6 |
| LH2-C7 | T7 |
| spec §6.1 | T8: a `/2` folder under the packaged root and a `/1` folder under a caller root each refuse by name |
| rule 1, rule 3 | T9 (seven malformed manifests refuse before any run file; every run file read under the recorded cap; saved and empty live runs replay), R1 to R3 |

## Gate

Delegated approval (auto=true), 2026-11-23, under the owner's
`/process-milestone literature-host-interfaces auto`, of the spec at sha256
`2e15cb11…4ef8` (commit `33fe059b`), LH2-D1 and LH2-D2 as proposed. The
spec has since been appended only. The milestone coordinator's GO for LH2
concerned file order with literature-reading-reference and approved
nothing.

## Review

One reviewer is one reviewer: Codex in the other harness, read-only,
through `review_tool.py`, one round over the LH2 diff (base `33fe059b`).
Three findings, all reproduced, one blocking and two hardening, none
self-inflicted; all fixed at `9df661c8` with regression tests that failed
before the fix. The convergence rules did not call for a second round, so
the repairs carry no review opinion. The retained review was sanitized of
this machine's paths, as its header says.

## Refactoring review

Refactors EXECUTED, behavior-preserving behind the unedited `test_ld3`,
`test_ld4`, `test_ld5`: the stage-chain and file reading of a run moved into
one helper, `_retained_files`, shared by the `/1` and `/2` readers, and now
decodes each file under the cap it was read with. Deferred: none.

## Refuted premises

**Plan D4's 64 MiB retained-file ceiling.** Every JSON reader in the
repository goes through `gnd.input_policy`, which refuses JSON over 10 MiB
(`MAX_BYTES`). LH1's run at the response ceiling (63 sections, a 63 MiB
payload) completed and could not be read back, contradicting LH1-C14 and
LH2-C3. Repaired in this phase by delegated approval: the ceiling is
`gnd.input_policy.MAX_BYTES`, imported, and the ceiling runs use 9 sections
(spec finding 1). The plan text is repaired at milestone close (open
question Q1).

## Open questions

| ID | Question | Owner | Target |
|---|---|---|---|
| Q1 | Plan §10 D4 and §2 LH1 still say the retained-file ceiling is 64 MiB; the shipped ceiling is the JSON read cap, 10 MiB | milestone close | plan repair at close |

## Boundary

- **The reading pair ends here.** LH1 and LH2 are delivered as the first of
  two pull requests (README, deviation from plan §8).
- **No review reads `9df661c8`'s repairs.**
- **A consistently rewritten folder replays** unless the host passes the
  digest `run()` returned; the README says so.
- **Out of scope.** No command-line flag for a caller root; `revision.py`'s
  packaged replay is unchanged.
