---
milestone: literature-interop
station: phase-LX3-spec-gate
skill: "n/a -- repository development under process-phase"
scope: phase-LX3-spec-gate
date: 2026-11-15
gates:
  - command: "ruling: delegated (auto=true) approved .gnd-planning/milestones/literature-interop/notes/phase-LX3-spec.md sha256 48984c60c2309663304d9c2dd28a0e9aa45eb275b77344cac6f31fdf00c98e12"
    exit: "n/a -- ruling"
  - command: "uv run pytest -q tests/test_lx3_catalog_composition.py --tb=short"
    exit: 1
    output: "17 failed, 1 passed in 6.07s"
evidence:
  - path: .gnd-planning/milestones/literature-interop/notes/phase-LX3-spec.md
    sha256: 48984c60c2309663304d9c2dd28a0e9aa45eb275b77344cac6f31fdf00c98e12
  - path: tests/test_lx3_catalog_composition.py
    sha256: 8b145b1cc15ea1d71f5c67c3b8e963ba6a140a347a4b50dbed1c75dbc1e13c57
  - path: tests/fixtures/lx3-catalog-composition/expected.json
    sha256: c75609385917971e76a6833a7653221f21c8a70f3feb1fd4912cfd4a48445b8e
  - path: tests/fixtures/lx3-catalog-composition/README.md
    sha256: 2da0ca163798174cd1babd9c956d6dea11b96fd485f897811b0495ee881b2d83
---

# Claim

The owner delegated milestone and phase rulings with
`process-milestone literature-interop auto`. Approve LX3 decisions D1–D4
and the corpus at the exact digests above. The independent phase diff
review has its own gate.

## Implementability

Rooted dispatch check distinguished the pinned catalog from the same
candidate without it. The rooted proof verified candidate and catalog
base facts using the existing evaluator. Both fixture roots load and
authenticate their catalogs. The reference-free route at `6d2ecece`
produced the two hashes in the expected file. The catalog fixture obtains
its source anchors from the original asserted spellings. The LI2 control
retains the original resolution and candidate identities.

## Gate output

    17 failed, 1 passed in 6.07s

The catalog route is refused by the phase-base implementation. The
reference-free wire control passes.

## Boundary

The corpus records expected results and selected consumers. The LX3
phase record owns implementation verification.

## Open questions

- None at the spec gate.
