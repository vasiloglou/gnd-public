---
milestone: literature-interop
station: close-candidate
skill: "n/a -- repository development under process-milestone"
scope: close-candidate
date: 2026-11-15
evidence:
  - path: .gnd-planning/milestones/literature-interop/003-plan-gate.md
    sha256: db8fc47587e79b86bc8693cff1479c023896f7ba0d558a6271c284236b2f377e
  - path: .gnd-planning/milestones/literature-interop/005-phase-LX1.md
    sha256: 42a68ecde3c670cf706abe932a35e61e7a34ef0c93ca3c430690ac5082c0bebb
  - path: .gnd-planning/milestones/literature-interop/007-phase-LX2.md
    sha256: 04881624cdf820ca16f54ecd7f37065792fbe48ce20c4c70041d21e3f946cf61
  - path: .gnd-planning/milestones/literature-interop/009-phase-LX3.md
    sha256: 78d13149683a5d74f61b94cd60468a5333fa3a7be91645abf0ba9235b87affc0
  - path: .gnd-planning/milestones/literature-interop/011-phase-LX4.md
    sha256: ea02cf9e9068c1302edc4f6eb42f77337a499b6ac56ede735f975d73fbad5ee1
  - path: .gnd-planning/milestones/literature-interop/notes/literature-interop-plan.md
    sha256: 0b0b8be165233078e7048948eef45266f007165df557fbdd3c629cd106ae5454
  - path: .gnd-planning/milestones/literature-interop/evidence/LX4/installed-observation.json
    sha256: 5dd61435b73a58f558ed3613fbfbe1ed176671354d74e399e9b6c863142390a5
---

# Literature interoperability close candidate

The [approved plan](notes/literature-interop-plan.md) covers issue #193 part 5
and the dates step of part 4. The topic is draft PR #202. The phase records
identify the exact reviewed candidates, changes that followed review and
verification results for the current implementation.

## Exit predicates

| Criterion | Evidence |
|---|---|
| LX1.a and LX1.b | [005](005-phase-LX1.md) records extraction under two pinned includes and replay of each element address. The public verifier refuses altered root, include, flat model or record bytes, including a jointly re-pinned flat bundle that differs from resolution. It also re-derives the projection schema. |
| LX1.c | The selected include-free artifacts retain the phase-base bytes. |
| LX2.a and LX2.b | [007](007-phase-LX2.md) records rooted version 3 production and independent replay. Model origin, fact occurrence and source lineage have separate controls. Stale include/artifact input is refused. Legacy versions 1 and 2 and streamed include-free inputs have compatibility controls. |
| LX3.a and LX3.b | [009](009-phase-LX3.md) records a catalog-dependent subset, one combined checking view, alias renaming and unchanged reference-free bytes. It binds independent reference, manifest, candidate and record controls. Catalog keys and candidate independence have explicit refusal tests. LI2's unjustified cross-source join still refuses. |
| LX3.c | The version 4 proof contains candidate and catalog base facts. Replay independently refuses both origin swaps, stale catalog identity and forged model origin. |
| LX4.a | [011](011-phase-LX4.md) records the separate extraction and checking roots. Both retain the same two include pins and catalog binding. Each source rebind retains its input and output provenance. Changing a temporal allowance causes a real checking violation; temporal extraction stays in its declared refusal band. |
| LX4.b | The public advisory uses the LI5 chainable relation policy and separate work-date evidence. The report gives two passes, one PINN advisory and five unresolved proposals. Omitting advice gives byte-identical checking and proof outputs. |
| LX4.c | The installed example authenticates the two original extractions, rebinds them, composes with an explicit identity decision, checks and replays the witness on the checking root, and verifies the manifest. Both fidelity cases run over the original evidence. The two shared source folders have two additional document copies and zero additional original population or extraction sidecar copies. |

## Cross-phase evidence

At runtime candidate `a3463627`, the focused union passed 669 tests
with three deselected. The structural gate passed 679 tests with two
deselected. These are the exact commands and outputs in the
[LX4 record](011-phase-LX4.md). Changed-file lint and the strict component
gate passed. Whole-tree Ruff retained the same 188 inherited diagnostics,
compared by file, line, code and message. The wheel ran with existing
locked dependencies. The [installed result](evidence/LX4/installed-observation.json)
binds check counts, stage-byte comparisons, rebinds and the physical
layout census.
The fixture uses saved extractor responses over the packaged documents and
runs the local projection, verification, checking, witness and fidelity
commands. No live extraction service is required by these controls.

## Questions and refactoring

| Question | Proposed disposition |
|---|---|
| Pin observable wires, refusal bands, and legacy bytes (001, 002, 003) | Closed by the LX1–LX4 spec gates and executable controls. |
| Shared fidelity/composition evidence layout (001, 002, LI1, LI5) | Closed for the example by the LX4 run and measured counts. |
| Example manifest, dated-work rows, timing and layout (002) | Closed by the LX4 corpus and the optional-mode comparison. |
| Claude CLI separator in the synchronized phase-review helper (005, 007, 009 and 011) | Carry to the dev-tools maintainer, target the next review-helper sync. The four runs bind the explicit argument separator. |
| Generic strict-reader symlink behavior and serializer consolidation (LI1 and literature-identity close) | Retain the existing maintenance and refactoring targets. LX2's explicit caller path repair is evidence for that specific route. |

Each phase record inventories the refactors made or deferred. The byte-exact
phase review artifacts remain attached to the candidate each reader saw.
The review helper reported four finished rounds, zero unresolved ledger
problems, 73 reviewed entries and 21 updated entries. The repaired bytes
are established by the recorded local regressions and cross-phase gates.

## Boundary

The closure concerns this feature and public fixture on the reviewed topic.
Broader reserved evidence, certification and merge each have their own
authorization rules. The close panel will evaluate this candidate. Its
judgments are advisory evidence in the ruling.
