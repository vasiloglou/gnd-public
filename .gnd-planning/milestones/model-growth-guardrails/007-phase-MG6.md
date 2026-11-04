---
milestone: model-growth-guardrails
station: "phase-MG6"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-MG6
date: 2026-11-04
gate:
  command: "uv run python tools/run_tutorials.py && uv run --group docs zensical build --strict && uv run python tools/check_docs.py site && uv run pytest -q tests/test_growth_example.py tests/test_development_scaffold.py tests/test_disclosure_docs.py tests/test_skill_prose_sync.py tests/test_public_binding_prose.py tests/test_packaged_skills.py"
  exit: 0
  output: "267 tutorial blocks passed; Build finished, no issues; 13393 local links/assets/anchors checked; 127 passed, 1 deselected"
  note: "The plan's section 9 MG6 row plus the docs-adjacent pins. No Python source under src/gnd changed."
evidence:
  - path: .gnd-planning/milestones/model-growth-guardrails/notes/phase-MG6-spec.md
    sha256: 318a63b0647899e38d60a8c92d54f5acc78d11f682d3ed2065b174de3b9d959c
  - path: .gnd-planning/milestones/model-growth-guardrails/notes/phase-MG6-claude-review.md
    sha256: 4eb6101b17722cff4fc1448e7a1382da78f54ac11a543f9669aaa79b3124f374
  - path: docs/how-to/grow-a-model.md
    sha256: ce7d6295166cf753462adfe67def063215163c17c81fc5c627a4df3e30e03eeb
  - path: .gnd-planning/milestones/model-growth-guardrails/checkpoints/DC2/docs/how-to/grow-a-model.md
    sha256: ce7d6295166cf753462adfe67def063215163c17c81fc5c627a4df3e30e03eeb
  - path: src/gnd/examples/growth/model.orm.yaml
    sha256: 100474ee44f3e3dfcb8b3e2d223921a18dc853341b78e9fc91c5bf9134269e55
  - path: src/gnd/examples/growth/round-1.proposal.json
    sha256: 5677b683f163fc600a3103a8b4896306ff5971baf266e2d7007abd3a7756f415
  - path: src/gnd/examples/growth/round-2.proposal.json
    sha256: 5e8c18616da78a7dc19fc3965b1210605b944ef9222f419a00d7ce955d8dd830
  - path: tools/build_growth_example.py
    sha256: 8e62656795e66acff8286ec06dd88cd9cf69f6b86f7cc2d1cf8ebaf5cb06438e
  - path: tests/test_growth_example.py
    sha256: 6c2f0ffc45c6dc5e3e08c30f5306329c8121cc31a6bd4195c9450148d140d027
  - path: docs/release-notes.md
    sha256: 6e9ae020425b5b8274f4f5fe95bce2b54fd27e8bebf782382ce3a78878778004
---

# Phase MG6: documentation

**Claim.** One executed how-to, [Grow a model by additions](../../../docs/how-to/grow-a-model.md),
walks a refused non-additive round, a shape report, an apply that repeats the
policy, extraction guidelines and rule read-back over the packaged
`growth` example; the docs runner executes its 10 blocks with their exits
and shown output. Every page naming the milestone's surfaces has a
disposition, the five phase notes are one Unreleased entry, and the docs
gates exit 0.

**Authority.** Plan r3 `(a1)`. Spec r1 under **delegated approval
(auto=true)** `(d1)` over SHA-256 `a2c20f5a539a3c52cc6e5ba9eec9c5d81d4e6a7603d5bdd8819828911a9f0925`; an agent ruling, not the
owner's reading. Owner viewing of the DC2 checkpoint is **pending**.

## What shipped

- `src/gnd/examples/growth/` (model, two proposals, README) and
  `tools/build_growth_example.py`; `tests/test_growth_example.py` rebuilds the
  proposals byte-identically.
- `docs/how-to/grow-a-model.md`, its nav entry and runner group `growth`.
- Pointers in the evolution guide, the evolve-policy reference and three
  agent pages; the consolidated release note.
- DC2 checkpoint copy `checkpoints/DC2/docs/how-to/grow-a-model.md`,
  registered in `tests/test_development_scaffold.py`.

## Gate

| Command | Result |
|---|---|
| `uv run python tools/run_tutorials.py` | `267 tutorial blocks passed`, exit 0 (the `growth` group: 10) |
| `uv run --group docs zensical build --strict` | no issues |
| `uv run python tools/check_docs.py site` | `13393 local links/assets/anchors checked`, exit 0 |
| pytest (front matter) | `127 passed, 1 deselected`, exit 0 |
| `git diff --stat 7961119 -- src/gnd` Python files | none |
| anonymity scan | 0 matches |

## Disposition table

In the spec ([phase-MG6-spec.md](notes/phase-MG6-spec.md), "Disposition
table"), completed after review R-F6.

## Checkpoints

DC1 (illustrative drafts after plan approval) did not happen: MG1 to MG5 ran
without it. That is recorded as missed (spec D2), not as satisfied. DC2 is the
executed page, retained under `checkpoints/DC2/`; showing it to the owner is
a human step this delegation does not cover.

## Adversarial review

One reviewer is one reviewer:
[phase-MG6-claude-review.md](notes/phase-MG6-claude-review.md). Verdict
approve-with-fixes; two blocking findings (R-F1 the one-line JSON claim,
R-F2 the missing `--populated`) and five others, all fixed; see the spec.

## Refactoring review

**None needed:** MG6 changed pages, one packaged example and one tool.

## Refuted premises

- Plan O22 ("`apply` rewrites the model as one-line JSON, dropping
  comments", inherited from the IK close): `apply` publishes the proposal's
  candidate text as given. The one-line JSON comes from the canonical
  candidate writer that built the proposal.

## Open questions

| ID | Question | Target |
|---|---|---|
| MG6-Q1 | The CSDP header template in `verbalization-patterns.md` lists `guided\|one-shot` only | milestone close |

## Boundary

- One reviewer is one reviewer. DC1 missed; DC2 owner viewing pending.
- No push, pull request, merge, release or publication is claimed by this record.
