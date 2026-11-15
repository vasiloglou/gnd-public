---
milestone: literature-identity
station: phase-LI2-corpus-gate
skill: "n/a -- repository development under process-phase, not a gnd-solve station over a domain model"
scope: phase-LI2-corpus-gate
date: 2026-11-15
gate:
  command: "ruling: owner approved the LI2 corpus at commit 3ef46384, tree src/gnd/examples/literature f6d7844b744e42f94d6cff7dffbe6407f8cf6434"
  exit: "n/a -- ruling"
evidence:
  - path: src/gnd/examples/literature/resolution/cases.json
    sha256: 97b9c0e88071cb66d5431e2e23f65266ed8be303b734ba9624dc60e0483789bc
  - path: src/gnd/examples/literature/resolution/README.md
    sha256: fcf69caf03e4b5208176b4a11cad66fd55ad455af762712d8b60140499748b89
  - path: src/gnd/examples/literature/resolution/baseline.json
    sha256: b94ab5f5e615b12f753a84b5c58547c420de760bc13b5e6ca64313ccad17ac31
  - path: src/gnd/examples/literature/resolution/li1-reference.resolution.json
    sha256: 62c7847ae1f2097c71fa88aecdf1261847c3c499603b7ce5b958f387d6891ea9
  - path: src/gnd/examples/literature/resolution/model.orm.yaml
    sha256: b5120440ad128f3853109f247ab928434e59d7ef74cce55edd935f886348f5a4
  - path: src/gnd/examples/literature/expected/M1-drop-all.expected.json
    sha256: 37fe1ec25c1cabc3f1f6e82fc3199300affc16062f90e081092610e94048582d
  - path: src/gnd/examples/literature/expected/M2-drop-one.expected.json
    sha256: 64d3d266eed98f7a8ec68dfb00b32e73a6395cabb1a308459ab2eef7514ebcdb
  - path: src/gnd/examples/literature/expected/M3-stale.expected.json
    sha256: 7288eb1c357972d0d5dd6701972ff54b07c569bc601f7092316e1834a3ddf98b
  - path: src/gnd/examples/literature/expected/M4-false-derived.expected.json
    sha256: 4a6ecfdfbb3d61ab94cfb5d39ec7d22f085071dc53814b7619b4dcf8f35b94f4
  - path: src/gnd/examples/literature/expected/M5-invalid-population.expected.json
    sha256: b56bc9b88cb6ca13c3324956ae455257a2b3b1276a3c02d86e87ded8ce110821
  - path: src/gnd/examples/literature/expected/M6-shifted-span.expected.json
    sha256: c3279f88975316426d105556e09fe8ce2cf9839d644b1e181e504eb9d59db87a
  - path: src/gnd/examples/literature/expected/M7-false-merge.expected.json
    sha256: 667791272df2ecd436ed42a98b248b0a5d2d44d5156660aa9e84cf6008830dc6
  - path: src/gnd/examples/literature/expected/X1-abstain-6.expected.json
    sha256: 8b67885188bfe478c76d7e6e9c497a282f4e943d98846f9ca552e7a54e211f81
  - path: src/gnd/examples/literature/expected/X2-consistent-shift.expected.json
    sha256: ccf98a3a8eef1ac6eb3082cb77ad7c49a48d0932864795cb5278796ef95e7cad
  - path: src/gnd/examples/literature/expected/reference.expected.json
    sha256: 36c0cfe52f312988ea9affe2c5c370d48f34dd49720022ecd03efde23856d72d
  - path: tests/test_li2_resolution.py
    sha256: 3aa3ca158f6a87bedc7c8d50642dc01d2a2907ec3a637a0b6a4b18edb6ecd0d7
  - path: tests/test_li1_assurance_report.py
    sha256: d5c08be0fdb8aad9181c45822d2ee8ace1af6198c75d2596a776c2ed07a6e6b3
  - path: tools/build_resolution_fixtures.py
    sha256: e861d944d042722b8ed9e1d4a282db845fb67f92844104dd008feed7486eb49f
  - path: tools/build_literature_example.py
    sha256: ee709f719f97b8cc08620bf34ece76182ab58975b059ec8f6de46110cd595633
---

# Claim

The owner approved the LI2 corpus as committed in `3ef46384`:
- the 20 resolution cases, with their exits and exact refusal messages;
- the mention fixture;
- the T16 baseline;
- the LI1 reference decisions;
- the amended LI1 expected outcomes, including M7.

The owner ruled amendments B1–B4 (spec §13) as proposed, and asked for the
gate to be recorded. Implementation waits for a separate go-ahead.

## Gate output (verbatim)

    Owner answers, 2026-11-15, in chat:
      LI2 corpus gate:  "Approve the corpus (Recommended)"
      B1–B4:            "Accept all four (Recommended)"
      Go-ahead:         "Record and stop (Recommended)"

## Rulings `(o)`, 2026-11-15

| ID | Ruling |
|---|---|
| Corpus | Approved as committed. The amended LI1 expected outcomes replace the ones approved at the LI1 corpus gate (005). A later change to any approved outcome returns it to the owner |
| B1 | Identity keys and evidence come only from asserted fact types, never `derived` or `semiderived` ones |
| B2 | `check_coverage(keys, decisions)` raises `CompositionError`. A key is `{source, object_type, value, outcome, coordinate}`, with the coordinate written `<source> <fact_type>#<index>.<role>` at the key's first asserted occurrence |
| B3 | The messages are exactly those in `cases.json`. When several rules fail, the first is reported in this order: step 3 (rule 6, then evidence), then decisions in index order (rule 5, then 3, then 4), then joined groups (rule 1), then spelling groups (rule 2) |
| B4 | With a resolution present, a renaming that cites no decision is refused at step 1 with `renaming <i> cites no decision` |

## Boundary -- what this result did NOT establish

- **No implementation.** No composition or harness code changed. The 42 LI2
  and 22 LI1 red cases are red because composition does not yet accept a
  `resolution` entry, which is what this gate approves.
- **Designed, not measured.** The M7 outcome and the amended LI1 numbers
  come from the spec's rules applied to the corpus. Only the T16 baseline,
  the flat whale witness and the mention check were measured.
- **Further authority.** No merge, publication or push is authorized.

## Open questions

- None surfaced by this gate.
