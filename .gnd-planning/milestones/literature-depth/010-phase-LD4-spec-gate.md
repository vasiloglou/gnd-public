---
milestone: literature-depth
station: phase-LD4-spec-gate
skill: "n/a -- repository development under process-phase"
scope: phase-LD4-spec-gate
date: 2026-11-16
gates:
  - command: "uv run --no-sync pytest -q tests/test_ld4_revision.py --tb=short"
    exit: 1
    output: "6 errors in 0.26s"
  - command: "ruling: delegated (auto=true) approved .gnd-planning/milestones/literature-depth/notes/phase-LD4-spec.md sha256 b2a9f38c23b5acd3d1ea71a08d93181739b18aec589c0d66bf2aff90253fb638"
    exit: "n/a -- ruling"
evidence:
  - path: .gnd-planning/milestones/literature-depth/009-phase-LD3.md
    sha256: 3637fe884e8a8e08eccb1c0538ed87152d840e5ad0c1b83d0f85cd13b064a9b4
  - path: .gnd-planning/milestones/literature-depth/notes/phase-LD4-spec.md
    sha256: b2a9f38c23b5acd3d1ea71a08d93181739b18aec589c0d66bf2aff90253fb638
  - path: tests/test_ld4_revision.py
    sha256: bd1d2faaba12d33a5fd5d01737164071d6d127e23f1a080c4f824373ed3a3726
  - path: tests/fixtures/ld4-revision/expected.json
    sha256: 1d2a9464cb0596e86e73ba3d15753bdecb60efef3ddee4fb3819cafa847b7230
  - path: src/gnd/examples/literature/revision_fixture/comparison/base.orm.json
    sha256: d74953014d1cb2b202d07fed18fafc15babda733f7d949fe4f57dd4b1c1cab4c
  - path: src/gnd/examples/literature/revision_fixture/comparison/head.orm.json
    sha256: 59102aa094e725ca4c524993d705e379596937729de82382fba44b796cb155cb
  - path: src/gnd/examples/literature/revision_fixture/comparison/population.json
    sha256: 84b100fd6802d4bc00d7e02bcca9536457d0283bb3b779fb3eb984eef65cc3e2
  - path: src/gnd/examples/literature/revision_fixture/corroboration/document.txt
    sha256: 7e3da2ebdbb88d3905d1da82fb5623e4ed7b02b0f1fb8abc80bb4583db95a9ee
  - path: src/gnd/examples/literature/revision_fixture/corroboration/population.json
    sha256: 83b0ef3d28f7f49df0c4fd0b65ccea850ce63764c18cf9ea6fe461178243c151
  - path: src/gnd/examples/literature/revision_fixture/corroboration/population.json.anchors.json
    sha256: 3b65999e2ff302464ffbe79ba5fefd7a591c5df1430a59317d9e7e1c1113a1fc
  - path: src/gnd/examples/literature/revision_fixture/interpretation.json
    sha256: d2e1dd6af05fa046be827eb2ab314bb1049c546f33c9c12a4db4199598630a59
  - path: src/gnd/examples/literature/revision_fixture/proposal.json
    sha256: b0adaf0d29a613732eaead5cb60f9c10295520131907dcecfb0827570407f673
  - path: src/gnd/examples/literature/revision_fixture/release-policy.json
    sha256: 555e00b93fde50eae2dc7e9077c9f1a255e2ff169e9916c5b43ce38c0d194df9
  - path: src/gnd/examples/literature/revision_fixture/review-inputs.json
    sha256: 426c65553c3f5de4049ee7f6eea0321957ad6eae939410c182ca9a46d45c4568
  - path: src/gnd/examples/literature/revision_fixture/support-targets.json
    sha256: 633422d3770d8c26319804621c44575da86146b82d2d85710829011c63e86bf4
  - path: src/gnd/examples/literature/revision_fixture/targets.json
    sha256: 4e3ffa7df198388f17520ab7bf1303e44b36624031c1693d51cd3314d31b4a5f
---

# LD4 spec and corpus gate

The owner's `process-milestone literature-depth auto` invocation delegates
approval of the semantic revision fixture and its in-scope decisions.
The frozen corpus establishes exact outcomes before the public example
exists. All six selected controls stopped at the absent revision module.
The separate policy defines the dependency inventory. The consumer-pinned
review fixture binds named occurrences to exact source, fact and model
bytes. The two source supports are synthetic controls with distinct
evidence. Public route feasibility was measured in scratch fixtures.
The sole further external review for this phase is the independent diff
review after local verification and separate authorization.
