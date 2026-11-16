---
milestone: literature-interop
station: plan-review-r2
skill: gnd-review-panel
scope: panel
date: 2026-11-15
gates:
  - command: "uv run --no-sync python tools/run_gnd_review_panel.py .gnd-planning/milestones/literature-interop/evidence/plan-r2-request.json --out ../panel-run --reviewer-timeout 600 --overall-timeout 900"
    exit: 0
  - command: "uv run --no-sync gnd review finalize ../panel-run ../synthesis.json --out ../PANEL-REVIEW.md"
    exit: 0
evidence:
  - path: .gnd-planning/milestones/literature-interop/evidence/plan-r2-request.json
    sha256: 6b49a11a1bee20da6b812e39202b97bd3dbf2a5a721f41e2b91f07930447fcfe
  - path: .gnd-planning/milestones/literature-interop/evidence/plan-r2/PANEL-REVIEW.md
    sha256: 23a7d25934082935b99774c97ea7d3dfc65b9b598b03bcd19e5dbce8396c80bf
  - path: .gnd-planning/milestones/literature-interop/evidence/plan-r2/attribution.json
    sha256: 3e4f5363c40a4fa6a6c3ea0c9a1549ba9da503aa68188644d59543a213e82a05
  - path: .gnd-planning/milestones/literature-interop/evidence/plan-r2/reviewed-plan.txt
    sha256: 0d7b4b18ea96f8f942dbafdaae144d5cc6490a17efcd4e39bcb869f3ddbb915e
  - path: .gnd-planning/milestones/literature-interop/evidence/plan-r2/summary.json
    sha256: 447aa1aa18b9bc65dee5a1b0c214db904be62a761e7eab015ddd174211f3040a
  - path: .gnd-planning/milestones/literature-interop/evidence/plan-r2/synthesis.json
    sha256: 7126b7b07b661fcc29e4350f7fa087d22146d87389383775029eeeda1fd6e35d
---

# Claim

The standard panel exited 0 on plan r3 and returned six valid responses.
Finalization exited 0 with four agreed groups and fifteen divergent concerns.

## Gate output

- Panel: `quorum-established`, `reviewed_artifacts_unchanged: true`, six valid responses.
- Finalize: `agreed_concern_count: 4`, `divergent_concern_count: 15`,
  `prioritized_fix_count: 19`.

The owner authorized the second and final round in the milestone chat on
2026-11-15. The panel ran in an isolated shallow clone of
`ef1fc9e5c69323108d76906fd4582da4481ffd19`. The active source matched
that commit and its loaded module resolved within the clone. The dependency
environment identifies its installed metadata as 0.2.0 in the CLI output.
The run used the clone's source. The raw run stays local outside Git,
bound by the canonical digest in the [summary](evidence/plan-r2/summary.json).

All six responses were complete. Codex approved, Gemini blocked, and
Claude, Qwen, Kimi and GLM requested revisions. Claude anchored 9/9
concerns, Qwen 9/9, Gemini 0/5, Kimi 1/1 and GLM 2/2. Codex raised
none. Qwen reviewed the inline plan and did not read the round-one record.
Claude and GLM share a CLI. The [finalized report](evidence/plan-r2/PANEL-REVIEW.md)
contains every opinion.

## Reproduction and dispositions

| Topic | Disposition |
|---|---|
| Rebind, composition and the check/witness roots | The r3 rebind described an ambiguous handoff. R4 rebinds source populations before composition and uses one checking root from composition through replay. The example manifest verifies each source provenance and downstream output. |
| Date input, sequencing, edge selection and precision | LI5's public lineage contracts do not carry dates. Use fixture-side publication dates keyed by work ID, separate from graph and checking inputs. Run a named optional report after composition and bind date and candidate-edge bytes. Keep the known false PINN candidate out of admitted lineage. |
| Catalog check, stale control and replay | The current composed-check API separates caller-provided references from composition. LX3 uses the composition route's own bound context and tests a catalog-dependent constraint. Test a forged composition catalog binding with a valid root pin, and differing valid catalog declarations at LX4. Name replay in the LX3 contract. |
| Flat handoff and two origin axes | Pin the substituted flat input control. Independently alter model and fact provenance, then test both LX3 fact-origin swaps and catalog-binding forgery. |
| Guards and temporal admission | LX1 continues temporal refusal at the current extraction admission boundary. LX4 repeats the control. Exercise guarded direct include-byte entry and the retained explicit-context override refusal. |
| Raw document evidence in composition | Decline the proposed removal. The existing composition source loader binds a document and anchor sidecar for each source. Retain that provenance and keep it separate from the fact merge. |
| Companion advisory timing | Use the post-composition step. The r2 wording about running beside extraction meant a single example, and r4 makes the sequence explicit. |
| Compatibility and history | Specify absent fields on legacy wires. The replay kernel already uses `binding-stale`. Retain the r2 and r3 exact snapshots by digest. |

## Convergence

The [classification ledger](evidence/plan-r2/attribution.json) marks 19 of
26 concerns as attacking r3 repair wording or controls. The driver compared
r2 and r3, counted the retained concerns even where the proposed remedy was
declined, and conservatively counted ambiguities already visible in r2
as carried. The ratio is 19/26, above one half. Same-seat counts were
Claude 15 to 9, Codex 4 to 0, Qwen 14 to 9, Kimi 0 to 1 and GLM 6 to 2.
Gemini had no valid round-one response. The convergence rule and final
authorized budget both stop further plan review.

## Boundary

Round 2 binds r3 only. The amended r4 plan has a distinct delegated ruling.
Phase evidence must establish the proposed behaviors.

## Open questions

- LX2 and LX3 specify the exact producer and replay refusal diagnostics.
- LX4 specifies the example manifest, dated-work fixture rows and measured
  evidence layout.
