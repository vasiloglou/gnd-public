---
milestone: literature-host-interfaces
station: "phase-LH3"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-LH3
date: 2026-11-23
gates:
  - command: "ruling: delegated (auto=true) approved .gnd-planning/milestones/literature-host-interfaces/notes/phase-LH3-spec.md sha256 7de038c63cec4c1cb8a6358e2815947d4ae37cdd0e5c7df1810f1ef56ad72922"
    exit: "n/a -- ruling"
  - command: "uv run pytest -q tests/test_lh3_admission_shape.py tests/test_li4_assertions.py tests/test_li5_lineage.py --tb=short"
    exit: 0
    output: "68 passed in 46.35s"
  - command: "the project.md structure and inventory guard block (12 files)"
    exit: 0
    output: "679 passed, 2 deselected in 96.27s (0:01:36)"
  - command: "uv run ruff check"
    exit: 0
    output: "All checks passed!"
  - command: "python3 scripts/components_index.py changed --base f82490cb --strict"
    exit: 0
    output: "changed against f82490cb (f82490c): 25 file(s) differ; 0 to fix, 0 warning(s), 0 to reread"
slow_cadence:
  command: "uv run pytest -q -m \"evidence or census\""
  trigger: "explicit owner request or separately scoped CI selection"
  reason: "the broad controls are outside this phase's impact closure"
evidence:
  - path: .gnd-planning/milestones/literature-host-interfaces/notes/phase-LH3-spec.md
    sha256: f5823c57c5fb585c7677f5cb0a110f8ee70e1dc2dfc5770d4cfa706c299cadc4
  - path: src/gnd/examples/literature/assertion_admission.py
    sha256: 805535e66257aca50126cf2ea06a44efa99e5fbfe332190149380da7120c9ca4
  - path: src/gnd/examples/literature/README.md
    sha256: 2dfd3fcfa1bcae9a17009a55e7b67a4c9b9abc44ef644d55e3e8987e2e567807
  - path: tests/test_lh3_admission_shape.py
    sha256: e0573b8e59b79cf6485efb525268df3dde8366e9d39a680f268a28f2f4f65324
  - path: tests/fixtures/lh3-admission/claims.orm.json
    sha256: 1518e043a6cb9ae8e5ccac823ca14c8988f04116e2e1153c7888e86811887e15
  - path: tests/fixtures/lh3-admission/terms.orm.json
    sha256: 05996ed42c345362ba99884466a7872bbfc11152f7290948c801c87e7dde3370
  - path: .gnd-planning/milestones/literature-host-interfaces/notes/reviews/phase-LH3-r1/review.md
    sha256: aab6cc702b70aff9b4276bfc664ccb41add101465ddddd585dea4bf94b268662
  - path: .gnd-planning/milestones/literature-host-interfaces/notes/reviews/phase-LH3-r1/FINDINGS.md
    sha256: cf70e90666253ab1d7a4cc7b61f0eab04d5ba3a261be90f69819a634801e8f05
  - path: .gnd-planning/milestones/literature-host-interfaces/notes/reviews/phase-LH3-r2/review.md
    sha256: 2573fdbbc32b6b159439c6a92de82c34738191727ce0381592aa98e8f7b7b958
  - path: .gnd-planning/milestones/literature-host-interfaces/notes/reviews/phase-LH3-r2/FINDINGS.md
    sha256: 2173c132d95e41ad885f7e4bd71899c59298baca18dc62419532002532bb5cb1
  - path: dev/components/COMPONENTS.md
    sha256: 60995a6849e00449cfe040e88b03ebb4fef01938ae11039ff1bfe3eae69596c4
---

# Phase LH3: admission over a caller-named assertion entity

## Claim

`admit(..., shape=SHAPE)` admits the instances of a caller-named entity
type, identified by their own handle, with every attached row and the rows
of followed entities, and writes `literature-assertion-admission/2`. The
packaged call keeps its four H18 digests. Criteria and tests in
`tests/test_lh3_admission_shape.py`:

| Criterion | Tests |
|---|---|
| LH3-C1 | T1 (shared passage, two actors and no object, three conditions, a quantity with its rows; `gnd check` on the admitted population exits 0), T1 covers |
| LH3-C2 | T2 (the packaged `assertion` refuses `shape:objectified-assertion`) |
| LH3-C3 | T3 |
| LH3-C4 | T4 |
| LH3-C5 | T5 (include root bound; an edited include refuses through the judgment route) |
| LH3-C6 | T6 (eight shape refusals, a target outside the shape, an include path with `..`, three bad `max_rows`, `max_rows` without a shape), R2, R5 |
| LH3-C7 | T7, R3 |
| LH3-C8 | T8 (all four H18 digests and the packaged reasons); `test_li4`, `test_li5` unedited |
| LH3-C9 | T9 (1,024 claims and 65,536 rows within 60 s; one row over refuses `input:row-cap`) |
| LH3-C10 | T10 (a shared quantity kept once, the rejected claim's rows not kept, `paper` not followed; an empty follow list follows nothing) |

## Gate

Delegated approval (auto=true), 2026-11-23, under the owner's
`/process-milestone literature-host-interfaces auto`, of the spec at sha256
`7de038c6…2922` (commit `fe46095e`), LH3-D1 to LH3-D3 as proposed. The spec
has since been appended only. The coordinator's GO for LH3 approved nothing.

## Review

One reviewer is one reviewer: Codex in the other harness, read-only,
through `review_tool.py`.

| Round | Read | Findings | Blocking | Self-inflicted |
|---|---|---|---|---|
| r1 | the LH3 diff, base `fe46095e` | 4 | 2 | 0 |
| r2 | the r1 repair, base `dcd3a61c` | 1 | 0 | 0 |

All five were reproduced and fixed with regression tests that failed before
their fix. Round 2 was declared the last before it ran; its repair
(`f718b572`) carries no review opinion.
Both retained reviews were sanitized of this machine's paths, as their
headers say.

## Refactoring review

Refactors EXECUTED, behavior-preserving behind T8 and the unedited
`test_li4`, `test_li5`: the target half of `_support` became
`_target_reason`, shared by the packaged and generic projections (R0.4).
Deferred: none. The packaged projection keeps its own path, as D10
requires.

## Refuted premises and findings

None refuted. Spec findings 1 to 5 record the departures from the letter:
include paths read with the model parser, cases built in the test module,
the `venue` entity, T9's 60 s bound, and T8's four digests. Review found
that handles must be keyed as the checker keys them
(`gnd.synth.identity.scalar_identity`), not as Python keys.

## Open questions

None opened by this phase.

## Boundary

- **Rules, `policy-refused` and `max_targets` are LH4's.** A shaped call
  without rules admits every supported assertion.
- **Nested includes are not copied.** An include root whose include
  declares includes refuses through the judgment route.
- **`instances` is `{}`** in the admitted population (LH3-D3).
- **No review reads round 2's repair.**
- **Out of scope.** No command-line flag; no change to `gnd judgments
  check`.
