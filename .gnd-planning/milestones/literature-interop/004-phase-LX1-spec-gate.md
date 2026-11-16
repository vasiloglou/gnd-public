---
milestone: literature-interop
station: phase-LX1-spec-gate
skill: "n/a -- repository development under process-phase"
scope: phase-LX1-spec-gate
date: 2026-11-15
gates:
  - command: "ruling: delegated (auto=true) approved .gnd-planning/milestones/literature-interop/notes/phase-LX1-spec.md sha256 ae928cb6fb3caf2e8174812b386868c60b0517ab0ebf7829e5bc63d0f9ef823a"
    exit: "n/a -- ruling"
  - command: "python -m pytest -q -p no:cacheprovider tests/test_lx1_flattening.py --tb=short"
    exit: 1
evidence:
  - path: .gnd-planning/milestones/literature-interop/notes/phase-LX1-spec.md
    sha256: ae928cb6fb3caf2e8174812b386868c60b0517ab0ebf7829e5bc63d0f9ef823a
  - path: tests/test_lx1_flattening.py
    sha256: 8f9b592c7e6b12a7ccf93f226faae6e2ee5b45196d6fd67d1a7ee95d0c7063be
  - path: tests/fixtures/lx1-flattening/README.md
    sha256: 81cf195c66f34617cb6d1e0fdf7a158f94bb7ef6efd15ce38d731074518132c4
  - path: tests/fixtures/lx1-flattening/components.orm.json
    sha256: c1b7802153351c2aa2dc827a191f14a4870d59ec30fbcfcd8fa9f53eb2f67320
  - path: tests/fixtures/lx1-flattening/document.txt
    sha256: 953221e526b6a2f6eac34a62dfde4a09056b078725bb8b3ee3dc32ddc3a1f8d1
  - path: tests/fixtures/lx1-flattening/expected.json
    sha256: d3838579e32af331aa4f25bff242d3d21a534180fd60f293dc529e016acc6d09
  - path: tests/fixtures/lx1-flattening/facts.json
    sha256: e0e135cac1f5b567258994e136aebf5820279ea95850ea59dda6e76a435c0484
  - path: tests/fixtures/lx1-flattening/project.orm.json
    sha256: 9e7a9e7a5b5f76f6f253a3fc965d386db667b97468737169b93d4320fe99e4bb
  - path: tests/fixtures/lx1-flattening/topics.orm.json
    sha256: 7f09b19990e17cf9b6f368150538eab65d22b21e534268711f8b0c4c10a51178
---

# Claim

The LX1 delegated gate approves the spec and the corpus bound above. The
corpus establishes a red predecessor for include-backed extraction.

## Ruling and implementability

ruling: delegated (auto=true) approved .gnd-planning/milestones/literature-interop/notes/phase-LX1-spec.md sha256 ae928cb6fb3caf2e8174812b386868c60b0517ab0ebf7829e5bc63d0f9ef823a

**Delegated approval (auto=true), 2026-11-15.** The owner's
`process-milestone literature-interop auto` instruction authorizes the spec
and corpus decisions D1–D4. The approval instrument is corpus-first.
All test and fixture bytes above are bound to this ruling. The spec sets
the required focused, structural and lint gates. The selected post-change
review is the project phase-diff instrument, with its own execution
authorization. No spec panel was selected.

The loaded two-include fixture has nine resolver origins, including the
anonymous constraint and both root attachments. The model-loader probe
showed the underlying projection can round-trip. The test harness drives
the actual extract and verify commands, rewrites bound bytes independently,
and has a same-root coordinated forgery arm. It captures pre-change
include-free bytes with the package version pinned to 0.3.1.

## Gate output

Run with the host's existing dev dependencies and this worktree's source
on the import path. The phase base is `183972ea`.

    8 failed, 1 passed, 13 errors in 3.57s

The predecessor extract route returns `include:unsupported-route`. Tests
that require its bundle stop at setup. The flattening layer is absent.
The include-free exact-byte control exits 0.

## Boundary

The red corpus binds expected transitions under LX1. Runtime implementation,
focused verification, independent review and phase closure are separate gates.

## Open questions

- None at the spec gate.
