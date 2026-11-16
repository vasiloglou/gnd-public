---
milestone: literature-interop
station: plan-review-r1
skill: gnd-review-panel
scope: panel
date: 2026-11-15
gates:
  - command: "uv run --no-sync python tools/run_gnd_review_panel.py .gnd-planning/milestones/literature-interop/evidence/plan-r1-request.json --out ../panel-run --reviewer-timeout 600 --overall-timeout 900"
    exit: 0
  - command: "uv run --no-sync gnd review finalize ../panel-run ../synthesis.json --out ../plan-round-1.md"
    exit: 3
  - command: "uv run --no-sync gnd review finalize ../panel-run ../synthesis.json --out ../plan-round-1.md"
    exit: 0
evidence:
  - path: .gnd-planning/milestones/literature-interop/evidence/plan-r1/PANEL-REVIEW.md
    sha256: 3a9f69f696f99d3bedab7c5b179002c9374562f7c944317ed7fc30bfd6b0a2de
  - path: .gnd-planning/milestones/literature-interop/evidence/plan-r1/request.json
    sha256: 4ccdcb6c51231901b70ea976a8f4d0dab610f4e420536190afd1591dd7d29c86
  - path: .gnd-planning/milestones/literature-interop/evidence/plan-r1/reviewed-plan.txt
    sha256: dc0b3fd0f1dfea5f6a299fc6a12e8cf2d0d77452c6e67a0c46761515c1d14573
  - path: .gnd-planning/milestones/literature-interop/evidence/plan-r1/summary.json
    sha256: 2fe981dc9da7e0c3219dafbb98a6c83d13cad96ca7f1d272b0d0a048ecf7c10f
  - path: .gnd-planning/milestones/literature-interop/evidence/plan-r1/synthesis.json
    sha256: c82ff14a1d83b9d2d950cdef0544bdb0fb2ee02cb9f13b0a2ca377086695bf3b
---

# Claim

The maintained standard panel reviewed r2. Five valid responses meet the
project's four-reviewer plan review requirement.

## Run and gate output

The owner approved round 1 in the milestone chat on 2026-11-15. The panel
ran in a dedicated shallow clone of `befea8f1f3f438e1cc86239c259941218aaae91f`
with the exact approved r2 draft overlaid at its canonical path. The active
panel source matched the base commit, and the imported module resolved inside
the clone. The dependency environment's installed metadata reports 0.2.0 in
the CLI output. The panel code was loaded from the clone's source tree.

The panel command exited 0 with `quorum-established` and
`reviewed_artifacts_unchanged: true`. Claude, Codex, Qwen and GLM requested
revisions. Kimi approved. All five valid responses were complete and their
39 concerns were anchored. Gemini was malformed. Its recorded validation
message ends with `output contains no JSON object`. Claude and GLM share a CLI.
The exact reviewed snapshot is retained as text so its relative Markdown links
resolve only from the original review path. The raw run stays outside the branch. Its canonical SHA-256 is in the
[summary](evidence/plan-r1/summary.json).

The first finalization exited 3 with `ERROR: agreed concern supporting reviewers are forged or incomplete`.
The synthesis listed supporters in alphabetical order. Reordering by the
panel's roster fixed the validation error. The same command then exited 0
with 12 agreed groups, six divergent concerns and 18 proposed fixes. The
[finalized report](evidence/plan-r1/PANEL-REVIEW.md) retains every concern.

## Dispositions

| Report topic | Plan action |
|---|---|
| Integrated fixture and chain | Require all stages on one fixture and record one mutation control per trust boundary in §4. Each phase spec pins concrete wire fields and diagnostics. |
| Model versus fact provenance | LX2 verifies model origin with a reference-free composition. LX3 depends on LX2 and owns mixed fact provenance. Both origin swaps refuse on replay. |
| Catalog and source staleness | Verify the catalog at compose, check, witness and replay with candidate bytes fixed. Add separate source and record controls in the consumers that receive them. |
| Rebinding | Bind extraction and checking inputs, shared vocabulary, extraction index and the population. Verify each mutation before evaluation. |
| Advisory and lineage | Use the public LI5 route. Evaluate publication dates on candidate builds-on edges and keep the rejected PINN edge out of accepted lineage. Assert unchanged check outcome and witness on advisory findings. |
| Unsupported and confined inputs | Add the refusal table and discriminating path, standalone-validity, nested, reference-in-include, unattended and temporal extraction controls. |
| Validation order | Each spec identifies its own boundary and checks two defects. Catalog validation is isolated from candidate validation. |
| Legacy controls | Verify selected predecessor bundle, certificate and composition bytes and replay older certificates. |
| Evidence layout | Run fidelity and composition on the same evidence, count copies and record the LX4 decision. |
| Source inventory and consumers | Cite current symbols and identify direct verification for LX4 and the existing LI0 controls. Assign normative homes to the rebind and advisory report. |

## Boundary

The panel opinion binds r2 only. Product claims require phase verification.
Paid review authorization covered round 1. The raw run directory is retained
locally outside Git.

## Open questions

- Each phase spec pins its wire and refusal contracts and tests their order.
- LX4 decides the fidelity and composition fixture layout from measured copies.
