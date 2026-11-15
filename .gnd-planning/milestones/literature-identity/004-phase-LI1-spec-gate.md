---
milestone: literature-identity
station: phase-LI1-spec-gate
skill: "n/a -- repository development under process-phase, not a gnd-solve station over a domain model"
scope: phase-LI1-spec-gate
date: 2026-11-15
gate:
  command: "ruling: owner approved .gnd-planning/milestones/literature-identity/notes/phase-LI1-spec.md sha256 d6836087374ddb1c3b97532c372036160cb8ba4b98938b6b8a38d3c210e39adf"
  exit: "n/a -- ruling"
evidence:
  - path: .gnd-planning/milestones/literature-identity/notes/phase-LI1-spec.md
    sha256: d6836087374ddb1c3b97532c372036160cb8ba4b98938b6b8a38d3c210e39adf
---

# Claim

The owner approved LI1 spec r1 at the SHA-256 above (commit `c53d7d56`,
before its gate edits). The owner ruled D1–D10 as proposed and chose the
corpus-first approval instrument. Under that instrument, a second owner gate
on the authored corpus comes before any harness code.

## Gate output (verbatim)

    Owner answers, 2026-11-15, in chat:
      LI1 spec gate:        "Approve r1 (Recommended)"
      D1–D10:               "Accept all proposals (Recommended)"
      Approval instrument:  "Corpus-first (Recommended)"

## Rulings `(o)`, 2026-11-15

| ID | Ruling |
|---|---|
| D1 | `semantic-support` is scored through `gnd fidelity` (R3). The harness assembles the case directories, and each document has a `gnd-render-doc` renderer manifest |
| D2 | Corpus-first: this gate, then a corpus gate on the authored corpus, the narrated stories and the golden reports, committed red |
| D3 | Floors as in spec §6.5: P = R = 1.0 for validity, source binding, derivation and freshness. Semantic support needs P ≥ 0.9, R ≥ 0.9 and abstention ≤ 0.2. Derivation abstention is 0. Comparisons are inclusive, over exact rationals |
| D4 | The held-out answer key sits on a local branch `literature-heldout`, and its digest is committed on the LI1 branch. It is pushed only with a later explicit authorization |
| D5 | The held-out set is additional documents and chains: 1 supported and 2 false. The five named false chains stay in dev |
| D6 | Routes are read where a stage consumes them. `gnd judgments` stays unread until LI4 |
| D7 | The business-facing docs page is deferred to LI5. LI1 ships the example README only |
| D8 | Schema ids: `literature-corpus/1`, `literature-answer-key/1`, `literature-run/1`, `literature-assurance-report/1` |
| D9 | A route refusal is a scored failure (exit 1). Only the harness's own inputs exit 3 |
| D10 | No spec review |

## Boundary -- what this result did NOT establish

- **No corpus or implementation.** No corpus byte, harness file or test exists
  under this gate. The corpus gate must clear before harness code.
- **No review.** No review opinion covers the spec bytes (D10).
- **The reference run's exit 0.** The spec's sweep (§12) leaves one detail to
  corpus authoring: whether every single-source population can exit 0 under
  `gnd check`.
- **Further authority.** No merge, publication, release or certification is
  authorized. Pushing the `literature-heldout` branch is not authorized.

## Open questions

- None surfaced by this gate.
