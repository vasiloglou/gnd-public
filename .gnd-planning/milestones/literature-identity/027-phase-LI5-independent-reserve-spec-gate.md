---
milestone: literature-identity
station: phase-LI5-independent-reserve-spec-gate
skill: "n/a -- repository development under process-phase"
scope: phase-LI5-independent-reserve-spec-gate
date: 2026-11-15
gate:
  command: "ruling: owner approved .gnd-planning/milestones/literature-identity/notes/phase-LI5-independent-reserve-spec.md sha256 3684f86cb30f69ae8048e76dea7cd9ed2dbc0bfd50c94b260f2ac54f87d34cec"
  exit: "n/a -- ruling"
evidence:
  - path: .gnd-planning/milestones/literature-identity/notes/phase-LI5-independent-reserve-spec.md
    sha256: 3684f86cb30f69ae8048e76dea7cd9ed2dbc0bfd50c94b260f2ac54f87d34cec
  - path: src/gnd/examples/literature/lineage/model.orm.yaml
    sha256: a63b64293edbed71c74d1ded8423c133c328aa4ea02f550bad4fb03c91591279
  - path: src/gnd/examples/literature/lineage/path-policy.json
    sha256: cc27412b17b7cc1ca4f6d5da940b74b80528e45d2aa9d5a78dbee4986274c0b7
  - path: src/gnd/examples/literature/lineage_run.py
    sha256: 15ff3ddc3d483fcdaed71ccfcc059facecb102282a674ce109d967085353706b
  - path: src/gnd/examples/literature/assertions/rubric.json
    sha256: 1c98384795afd57033b0416a6e8dbd6cd3f914a33fadc3510f605394079b0178
---

# Claim

The owner approved the follow-up protocol at the digest above.
The separate sealed-corpus approval precedes the blind annotation run.

## Gate output (verbatim)

    2026-11-15, in the current task, in response to the fresh-reserve protocol:
    approved

The owner selected Astra for the source-only annotation. Codex
prepared and holds the separate sealed corpus. The source-only
session receives the public input shape and approved annotation
instructions. The local isolation probe read a harmless file in its
own directory and refused reads of both the repository and the new
sealed key. The Astra transport returned the requested readiness
token on a data-free prompt. The implementation pins above are from
the frozen checkout `01d9e6c65b9b02b80b07663bdf311554e9081415`.

## Boundary

This gate accepts the follow-up protocol. The original reserved
score and close refusal in [026](026-milestone-close.md) retain their
effect. Corpus approval and fresh evidence remain separate.

## Open questions

- Record the sealed-corpus ruling and first independent measurement
  when available.
