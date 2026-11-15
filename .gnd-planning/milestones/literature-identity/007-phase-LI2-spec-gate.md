---
milestone: literature-identity
station: phase-LI2-spec-gate
skill: "n/a -- repository development under process-phase, not a gnd-solve station over a domain model"
scope: phase-LI2-spec-gate
date: 2026-11-15
gate:
  command: "ruling: owner approved .gnd-planning/milestones/literature-identity/notes/phase-LI2-spec.md sha256 64e756b7974fc6bff77777e5c9909857f1b0cecc406ea0286a724badc72caa8a"
  exit: "n/a -- ruling"
evidence:
  - path: .gnd-planning/milestones/literature-identity/notes/phase-LI2-spec.md
    sha256: 64e756b7974fc6bff77777e5c9909857f1b0cecc406ea0286a724badc72caa8a
---

# Claim

The owner approved LI2 spec r1 at the SHA-256 above (commit `b4f4cdb4`,
before its gate edits). The owner ruled D1–D11 as proposed and chose the
corpus-first approval instrument, so a corpus gate comes before any
composition code.

## Gate output (verbatim)

    Owner answers, 2026-11-15, in chat:
      LI2 spec gate:        "Approve r1 (Recommended)"
      D1–D11:               "Accept all proposals (Recommended)"
      Approval instrument:  "Corpus-first (Recommended)"

## Rulings `(o)`, 2026-11-15

| ID | Ruling |
|---|---|
| D1 | Keep `gnd-composition-manifest/1` and `gnd-composition/1`. The new fields are optional and paired, and without `resolution` the bytes equal the baseline. This settles the plan-gate open question on LI2's schema ids |
| D2 | The coverage set covers the object types the resolution record lists, each declared by the model |
| D3 | The manifest's renamings cite decisions, and GND verifies them. Renaming stays the only way a value changes, including `unresolved` placeholders |
| D4 | A `same` decision whose keys are not joined is refused |
| D5 | Corpus-first |
| D6 | A new module `gnd.composition_resolution` at layer `model`, called by `compose` |
| D7 | The harness reads the `same`-connectivity of the run's resolution, as verified by R4 |
| D8 | The approved LI1 expectations are amended (reference resolution, M7, and the changed failing sets). The amended outcomes return to the owner at the corpus gate |
| D9 | A mention id is `<document>@<start>-<end>`, a string value of a `Mention` value type |
| D10 | Exactly two keys per decision, with at least one evidence coordinate per key |
| D11 | No spec review |

## Boundary -- what this result did NOT establish

- **No corpus or implementation.** No fixture, golden or code exists under
  this gate, and the corpus gate must clear before composition code.
- **The approved LI1 outcomes stand.** They are unchanged until the owner
  approves their amendment at the corpus gate (D8).
- **No review.** No review opinion covers the spec bytes (D11).
- **Further authority.** No merge, publication, release or push is
  authorized.

## Open questions

- None surfaced by this gate.
