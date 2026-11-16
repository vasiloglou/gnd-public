---
milestone: literature-depth
station: phase-LD4
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-LD4
date: 2026-11-16
gates:
  - command: "uv run --no-sync pytest -q tests/test_ld4_revision.py tests/test_ld3_reading_workflow.py tests/test_rule_edition_comparison.py --tb=short"
    exit: 0
    output: "62 passed in 259.53s (0:04:19)"
  - command: "uv run --no-sync pytest -q tests/test_ld4_revision.py -k additive_refusal_must_identify --tb=short"
    exit: 0
    output: "1 passed, 15 deselected in 54.36s"
  - command: "uv run --no-sync pytest -q tests/test_rf5_commands.py tests/test_rf5_review_regressions.py tests/test_rf6_query_policy.py tests/test_rf7_structure.py tests/test_rf8_structure.py tests/test_rf9_repairs.py tests/test_rof4_accept_identities.py tests/test_disclosure_mode.py tests/test_disclosure_docs.py tests/test_packaged_skills.py tests/test_conformance_payload.py tests/test_development_scaffold.py --tb=short"
    exit: 0
    output: "679 passed, 2 deselected in 303.91s (0:05:03)"
  - command: "uv run --no-sync pytest -q tests/test_li2_resolution.py tests/test_li4_assertions.py tests/test_li5_lineage.py tests/test_rule_edition_comparison.py tests/test_evolve_loading.py tests/test_evolve_additive_policy.py tests/test_witness_composition.py tests/test_ld3_reading_workflow.py --tb=short"
    exit: 1
    output: "2 failed, 315 passed in 316.79s (0:05:16)"
  - command: "python -m pytest -q tests/test_evolve_loading.py::test_h3_every_homes_outcome_is_unchanged[replay/changed] tests/test_evolve_loading.py::test_h3_every_homes_outcome_is_unchanged[witness/changed] --tb=short at 0d35a0b0"
    exit: 1
    output: "2 failed in 2.95s"
  - command: ".venv/bin/ruff check --output-format=json"
    exit: 1
    output: "188 exact inherited diagnostics; changed Python files pass"
  - command: "python3 scripts/components_index.py changed --base 0d35a0b0 --strict"
    exit: 0
    output: "0 to fix, 0 warning(s), 0 to reread"
  - command: "uv build --offline --wheel --out-dir <scratch>/dist"
    exit: 0
    output: "installed in a standalone scratch virtualenv"
  - command: "python -m gnd.examples.literature.revision run reading --out release"
    exit: 0
    output: "five before proofs, two after; two current supports"
  - command: "python -m gnd.examples.literature.revision status release/after"
    exit: 0
    output: "current"
  - command: "python -m gnd.examples.literature.revision replay release"
    exit: 0
    output: "fresh and replay bytes identical"
  - command: "python -m gnd.examples.literature.revision replay release --snapshot before"
    exit: 0
    output: "same original witness digest"
  - command: "claude -p --model opus --permission-mode plan --add-dir <review-dir> -- '<brief-path prompt>'"
    exit: 0
    output: "VERDICT: CHANGES_REQUESTED"
slow_cadence:
  command: 'uv run pytest -q -m "evidence or census"'
  trigger: explicit owner or CI selection
  reason: affected current routes use ordinary focused and installed gates
evidence:
  - path: .gnd-planning/milestones/literature-depth/010-phase-LD4-spec-gate.md
    sha256: 8e1007f5d45eb758915b307822a1af805067287b346df0103dc19739f84356e9
  - path: .gnd-planning/milestones/literature-depth/notes/phase-LD4-spec.md
    sha256: 9cd15da06777a3d5edf63302a9313249c07089159319fbbc7f7a5a9d21dfcf3b
  - path: .gnd-planning/milestones/literature-depth/evidence/LD4/installed-observation.json
    sha256: 06227fb624d738f2719b4d01c77f9b3a85c37b4ab910fc5e70e6265b27547b7a
  - path: .gnd-planning/milestones/literature-depth/notes/reviews/phase-LD4-r1/BRIEF.md
    sha256: 030412bb3d90eea3a4efb338cfa64bf4722a9a3fdfb8d52bf7394a89fb676fea
  - path: .gnd-planning/milestones/literature-depth/notes/reviews/phase-LD4-r1/FINDINGS.md
    sha256: 285042618d5f4fc5c7afc94ea1fde228e96a90c338b4dafc000f91f1ea980e74
  - path: .gnd-planning/milestones/literature-depth/notes/reviews/phase-LD4-r1/brief.json
    sha256: 294a555d61c07eac80a155864141eaf1dad3754676636340fb4fbd6631d03712
  - path: .gnd-planning/milestones/literature-depth/notes/reviews/phase-LD4-r1/diff.patch
    sha256: 389e0c5dbc2631478f0a65d4a2ea0372b8b8721aa0381953c491d3e2e1efda57
  - path: .gnd-planning/milestones/literature-depth/notes/reviews/phase-LD4-r1/review.log
    sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
  - path: .gnd-planning/milestones/literature-depth/notes/reviews/phase-LD4-r1/review.md
    sha256: 2ba83b164e9e989802df6cc154e0dc1e0bf5ec070e41bee3d6a2a3e97291bddb
  - path: .gnd-planning/milestones/literature-depth/notes/reviews/phase-LD4-r1/run.json
    sha256: 2b155f40c38e06c283c82885c5c4cd39a5963a162501803eabb65c38ed8693e7
  - path: src/gnd/examples/literature/revision.py
    sha256: 888b812f9dd45c31371384989d311c5774b1758cbeaf435b9a22149f32435a3f
  - path: src/gnd/examples/literature/revision_manifest.py
    sha256: 9ca7699f78a1886dfed25ce64fb3299b21d7889b2a2e668f3ea338f95d4c603a
  - path: src/gnd/examples/literature/reading.py
    sha256: 9182a7430774416fd2bc727ec316fb89a445b735f8d3e906644418e6f8ac3dbc
  - path: src/gnd/examples/literature/revision_fixture/release-policy.json
    sha256: af44dfee16ca94f20c560c5e82bb00e59bb86f53c53c7219b30fb6da3ad8bc65
  - path: tests/test_ld4_revision.py
    sha256: 60061d3a9179c6baa4559714824c9d7a0d94690b86f22bf9536a359d35b128c3
---

# LD4 completion

The installed semantic revision example publishes independently replayable
snapshots. It checks the assertion anchors and independently proves
lineage through public witness and replay. Exact support, model, policy,
source and publication identities are retained.

| Criterion | Observed result |
|---|---|
| Before and after | Three false lineage paths disappear. OpenCap Monocular→WHAM and VampNet→DMD are preserved. Original witness replay uses its own prior population, source notes and semantic inputs. |
| Dependencies | An independently pinned policy fixes the exact roster. Resolution and proposal mutations reach their actual consumers. The after manifest binds the prior composition and population. Candidate coverage omission, duplicates and empty rosters refuse. |
| Migration | Composition occurrences retain exact original coordinates and update the whale-b values. A source-free WHAM occurrence carries two candidates for rereading. The scoped absence stales only for the changed predicate. The unrelated denial remains current. |
| Semantic review | Additive preview names and rejects the exact reading edit. The reviewed preview and apply pass. The old occurrence review stales while a separately bound replacement admits the same source and roles. A rehashed interpretation change cannot transfer a saved approval. |
| Rule and support editions | The separate same-vocabulary value-rule comparison shows one head-only finding. A different-vocabulary control refuses. Two certificates independently prove the same target, including when the other certificate's source is removed. |

## Independent review

The owner authorized a single Claude Code Opus review at `05546dc0`.
The reviewer checked 32 brief hashes and passed the nine original direct
tests. The review verified the query outcomes, old snapshot, evolved
review and separate support coordinates. Its verdict was changes requested.
The [findings ledger](notes/reviews/phase-LD4-r1/FINDINGS.md) records five
repairs and the existing public vocabulary guard. The author also
reproduced accepted interpretation-policy rebinding and prior replay's
dependency on packaged reading bytes. The repair authenticates saved
opinion policy and retains the exact reading sources and vocabulary.

The installed, structure, component and lint evidence covers the repair.
The repair bytes are listed separately from the original reviewed hashes.
The expanded affected run on the reviewed candidate passed 315 tests.
Two changed-reference tests expected `ReferenceInputError` and received
`ReferenceHashMismatch`. The same two failures reproduced on the
pre-LD4 source at `0d35a0b0`. The focused repair recurrence includes
the affected LD3 reader and rule comparison.

## Refactoring review

Refactors EXECUTED. Raw staleness and migration impact share the dependency
walk. Resolution status follows actual consumers of the source decision
and independent proofs reuse the exact edition without loading another
support's source. Historical replay supplies retained raw inputs through
the existing LD3 reader.

## Boundary

One reviewer checked the original candidate. The after release is a
bounded worked example over the fixed reviewed source and definition
editions. Public check reports the anchored assertions while the
proof routes cover the selected lineage. Both supports are synthetic
source controls. Historical and census lanes retain their ordinary
explicit selection.

## Open questions

- LD5 uses the two independent support certificates and the observed
  same-occurrence review transition.
- The CLI positional prompt separator stays with the review-helper
  maintainer's next sync.
- Part 10 remains deferred.
