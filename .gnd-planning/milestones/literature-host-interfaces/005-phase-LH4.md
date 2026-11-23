---
milestone: literature-host-interfaces
station: "phase-LH4"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-LH4
date: 2026-11-23
gates:
  - command: "ruling: delegated (auto=true) approved .gnd-planning/milestones/literature-host-interfaces/notes/phase-LH4-spec.md sha256 ed5f1be11ea35c1e3a5615d39ac4023c3686a55b1545fd181a734286983f712c"
    exit: "n/a -- ruling"
  - command: "uv run pytest -q tests/test_lh4_admission_rules.py tests/test_lh3_admission_shape.py tests/test_li4_assertions.py tests/test_li5_lineage.py --tb=short"
    exit: 0
    output: "99 passed in 61.05s (0:01:01)"
  - command: "uv run python tools/run_tutorials.py --group literature"
    exit: 0
    output: "15 tutorial blocks passed"
  - command: "the project.md structure and inventory guard block (12 files)"
    exit: 0
    output: "679 passed, 2 deselected in 99.85s (0:01:39)"
  - command: "uv run ruff check"
    exit: 0
    output: "All checks passed!"
  - command: "python3 scripts/components_index.py changed --base ce8d442a --strict"
    exit: 0
    output: "changed against ce8d442a (ce8d442): 16 file(s) differ; 0 to fix, 0 warning(s), 0 to reread"
slow_cadence:
  command: "uv run pytest -q -m \"evidence or census\""
  trigger: "explicit owner request or separately scoped CI selection"
  reason: "the broad controls are outside this phase's impact closure"
evidence:
  - path: .gnd-planning/milestones/literature-host-interfaces/notes/phase-LH4-spec.md
    sha256: c78f2578899890ba579db643942724a659ac4eb8455ce528aaedd7a4589d6658
  - path: src/gnd/examples/literature/assertion_admission.py
    sha256: bc78375fb84d95f8497e519dce67ca8dd55a376764c0b03ad907b363e37856a6
  - path: src/gnd/examples/literature/README.md
    sha256: 518990cc7568ac9949d2f813b7745a829d7c00b58ed8d07835744bc2de9a0d51
  - path: tests/test_lh4_admission_rules.py
    sha256: 4df73aaec6962b66d79d099cc5606341451132e5a64ffcea3700edc49d259547
  - path: tests/test_lh3_admission_shape.py
    sha256: 8196e84b454028c5cc2fddc5ff13626909e00ccff71642dcb3f2dee4ea80e366
  - path: docs/literature/commands.md
    sha256: 26485303f60ba06c426613f1b275468e6bd7b49b7523e5b9665f50b858252cde
  - path: docs/release-notes.md
    sha256: 1fa3010f9d0b60380e4933508250d3f984ef235a3b861c48b56488a1fe24f3bd
  - path: .gnd-planning/milestones/literature-host-interfaces/notes/reviews/phase-LH4-r1/review.md
    sha256: 3333bd3218376dc8827ab362d4b8330d6ac8b2ec138023533b9e3abe313cb6cd
  - path: .gnd-planning/milestones/literature-host-interfaces/notes/reviews/phase-LH4-r1/FINDINGS.md
    sha256: 70a233ba4a899ec88efbe6fafb00ee39b7a464f9c0131edf3c843b98f0b9d299
---

# Phase LH4: admission rules as data

## Claim

`admit(..., rules=RULES, max_targets=N)`, with or without a shape, admits
the supported assertions that satisfy the rules, records the others as
`policy-refused` with the first failing requirement's reason, and binds
every setting in a `/2` record. The packaged comparison is now
`DEFAULT_RULES`, run by the one evaluator, and the packaged call keeps its
bytes. Criteria and tests in `tests/test_lh4_admission_rules.py`:

| Criterion | Tests |
|---|---|
| LH4-C1 | T1 (two rules files, two admitted sets: `{c1}` and `{c1, c3}`) |
| LH4-C2 | T2 |
| LH4-C3 | T3 (one admissible and one inadmissible row; no row) |
| LH4-C4 | T4 (a cap below the policy, 1,025, 0, `True`; a cap at the policy size admits) |
| LH4-C5 | T5 (ten malformed or unknown-name rules documents and the packaged-shape `assertion_names_work` rule, all before the judgment route), R1 |
| LH4-C6 | T6 (default rules passed explicitly: same reasons, order and admitted bytes, `policy-refused` for statements 3 to 6); LH3's T8 pins the four H18 digests of the call with no argument |
| LH4-C7 | T7 (each of shape, rules, `max_targets`, `max_rows` changes its field; a rules-only call records `packaged`, `null`, `null`) |
| rule 2 | T8 (64 requirements over 65,536 rows within 60 s) |

## Gate

Delegated approval (auto=true), 2026-11-23, under the owner's
`/process-milestone literature-host-interfaces auto`, of the spec at sha256
`ed5f1be1…712c` (commit `8fffc161`), LH4-D1 and LH4-D2 as proposed. The
spec has since been appended only. The coordinator's GO for LH4 approved
nothing.

## Review

One reviewer is one reviewer: Codex in the other harness, read-only,
through `review_tool.py`, one round over the LH4 diff (base `8fffc161`).
Two findings, both reproduced, one blocking and one hardening, none
self-inflicted; both fixed at `4428a24d` with regression tests that failed
before the fix. The convergence rules did not call for a second round; the
repairs carry no review opinion. The retained review was sanitized of this
machine's paths, as its header says.

## Refactoring review

Refactors EXECUTED, behavior-preserving behind LH3's T8, LH4's T6 and the
unedited `test_li4`, `test_li5`: the literal comparison of
`project()` (`(polarity, attribution) != ("asserts", "own-finding")`) became
`DEFAULT_RULES` evaluated by `_evaluate_rules`, the one evaluator of both
projections (R0.4). Deferred: none.

## Refuted premises and findings

None refuted. Spec findings 1 to 4: `reasons` is a list of value and reason
pairs, not a mapping keyed by JSON text; the model loads before the judgment
route, so an edited include refuses `input:model` (LH3's T5 updated); the
`/2` record names the shape kind; `_case` gained `edit_model`.

## Open questions

None opened by this phase.

## Boundary

- **Rules name attached fact types only**, never followed ones.
- **1,024 targets per call** is `gnd judgments check`'s cap; a larger set is
  admitted in several calls the host makes (D11).
- **No review reads `4428a24d`'s repairs.**
- **Out of scope.** No command-line flag; no change to `gnd judgments
  check`.
