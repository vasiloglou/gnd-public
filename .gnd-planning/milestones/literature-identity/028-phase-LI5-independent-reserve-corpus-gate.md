---
milestone: literature-identity
station: phase-LI5-independent-reserve-corpus-gate
skill: "n/a -- repository development under process-phase"
scope: phase-LI5-independent-reserve-corpus-gate
date: 2026-11-15
gate:
  command: "ruling: owner approved sealed corpus v1 approval-manifest.json sha256 dcfd45ea22f14647128c0de658e04d7f8a6c712685af4c75e50b4c8ff8ceec7d"
  exit: "n/a -- ruling"
evidence:
  - path: .gnd-planning/milestones/literature-identity/notes/phase-LI5-independent-reserve-spec.md
    sha256: 3684f86cb30f69ae8048e76dea7cd9ed2dbc0bfd50c94b260f2ac54f87d34cec
---

# Claim

The owner approved sealed corpus v1 for the source-only Astra run. The
corpus manifest, its four source members, and the private key hashes
were verified before annotation. The answer key contains one supported
chain and two distinct false chains. The scorer and rule pins remain
as recorded in [027](027-phase-LI5-independent-reserve-spec-gate.md).

## Gate output (verbatim)

    2026-11-15, responding to the sealed corpus manifest submitted in chat:
    approved

The private approval manifest binds these local artifacts.

| Artifact | SHA-256 |
|---|---|
| Approval manifest | `dcfd45ea22f14647128c0de658e04d7f8a6c712685af4c75e50b4c8ff8ceec7d` |
| Source manifest | `be19aef5dc7258d1751e3c38601600f2877e1628e5feaaeb7534a893c0a86f00` |
| Answer key | `6f510056d22ffb6b11c4c94a2ea71ebaef3a38b3e6897518105621a19bde4929` |
| Case rationales | `08efd5b1ae9b5f72f338ec10c588c0bf7f4457985fed83cca57b97d86cfd6032` |
| Source-only prompt | `9c628f6697b6e1f0450d1d38ca50a306e286a07873a115d32c97b75a1ef637ad` |
| Annotation response schema | `f446f62db07664eddee5639760a10455789075c8703efb234f3a885bbf3efe37` |

The target and key bytes are in the custodian directory outside Git.
The prompt contains the source paragraphs, source provenance, exact
byte coordinates and the predeclared annotation instructions. The
response schema carries only the input structure. Astra runs in
an isolated session with neither the key nor repository access.

## Boundary

This is the corpus approval. The first annotation, assembly and score
have separate outcomes. The original close ruling remains recorded in
[026](026-milestone-close.md).

## Open questions

- Retain the first submitted annotation and score outcome.
