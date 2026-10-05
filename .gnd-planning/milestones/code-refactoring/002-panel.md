---
milestone: code-refactoring
station: "plan-review-r2"
skill: gnd-review-panel-light
scope: panel
date: 2026-10-05
gate:
  command: "uv run gnd review finalize .gnd-planning/milestones/code-refactoring/evidence/plan-review-r2/panel-run .gnd-planning/milestones/code-refactoring/evidence/plan-review-r2/synthesis.json --out .gnd-planning/milestones/code-refactoring/evidence/plan-review-r2/PANEL-REVIEW.md"
  exit: 0
  panel_command: "uv run python tools/run_gnd_review_panel.py --light .gnd-planning/milestones/code-refactoring/evidence/plan-review-r2/review-request.json --out .gnd-planning/milestones/code-refactoring/evidence/plan-review-r2/panel-run --effort high --reviewer-timeout 600 --overall-timeout 900"
  panel_exit: 0
  note: "Final plan-review round under the bound declared 2026-10-05. Run in a disposable detached worktree at 145ce956aa31869d185fba5dc41b2672dd740451; gnd resolved inside that tree; evidence copied here afterwards."
evidence:
  - path: .gnd-planning/milestones/code-refactoring/notes/code-refactoring-plan.md
    sha256: 52bc1f5faa931ca5b411bc5e47b61c6fb8c9df9a3df9d601b5fc3133d9498966
  - path: .gnd-planning/milestones/code-refactoring/evidence/plan-review-r2/review-request.json
    sha256: f1775815975f5a28e7f03088daa8996f25e3d9757e29f1b36ee5bc95d35f1f2e
  - path: .gnd-planning/milestones/code-refactoring/evidence/plan-review-r2/panel-run/run.json
    sha256: e18303cfbaf3dd6d521dd9f4779f482b8fd5b139c61a2b3827059589a5bef683
  - path: .gnd-planning/milestones/code-refactoring/evidence/plan-review-r2/synthesis.json
    sha256: 650db2ac6795618fa875ffbfd562ca7ace1b2e4e7eda1e6f0e118bec8954c42c
  - path: .gnd-planning/milestones/code-refactoring/evidence/plan-review-r2/PANEL-REVIEW.md
    sha256: 566813e16b6353f8e416e2bd07705280f649e885ca6cc4b4198541f75acaee67
---

# Claim

The light panel at high effort over plan candidate r2 (commit 145ce95)
exited 0 with six of six reviewers successful, all with disposition revise,
and finalization exited 0 with 12 agreed concern groups, 7 divergent views
and 12 prioritized fixes.

## Gate output (verbatim)

Panel (stderr, then stdout):

    review credential names loaded (not yet authenticated): OPENROUTER_API_KEY from OPENROUTER_API_KEY, ZAI_API_KEY from ZAI_API_KEY
    OpenRouter authentication preflight passed
    {"advisory":true,"attempted_reviewer_ids":["claude","codex","qwen","gemini","kimi","glm"],"command":"review panel-light","gnd_version":"0.1.0","outcome":"quorum-established","quorum_met":true,"request_kind":"plan","request_sha256":"8ca3b15f39c833dfbc52c8b2784542cba8a5e16c0151722c556a6c9a1674a5c4","required_successes":3,"reviewed_artifacts_unchanged":true,"reviewer_effort":"high","reviewer_statuses":[{"reviewer_id":"claude","status":"success"},{"reviewer_id":"codex","status":"success"},{"reviewer_id":"qwen","status":"success"},{"reviewer_id":"gemini","status":"success"},{"reviewer_id":"kimi","status":"success"},{"reviewer_id":"glm","status":"success"}],"run_directory":".gnd-planning/milestones/code-refactoring/evidence/plan-review-r2/panel-run","run_sha256":"e18303cfbaf3dd6d521dd9f4779f482b8fd5b139c61a2b3827059589a5bef683","schema_version":1,"successful_reviewer_ids":["claude","codex","qwen","gemini","kimi","glm"],"tool":"gnd"}
    exit=0

Finalize:

    {"advisory":true,"agreed_concern_count":12,"command":"review finalize","divergent_concern_count":7,"gnd_version":"0.1.0","outcome":"quorum-established","prioritized_fix_count":12,"quorum_met":true,"report_path":".gnd-planning/milestones/code-refactoring/evidence/plan-review-r2/PANEL-REVIEW.md","required_successes":3,"run_sha256":"e18303cfbaf3dd6d521dd9f4779f482b8fd5b139c61a2b3827059589a5bef683","schema_version":1,"successful_reviewer_ids":["claude","codex","qwen","gemini","kimi","glm"],"synthesis_sha256":"aebb08c0743038cf6442a9548cdf1a5e41dc77324104c6ef60837eac1c563888","tool":"gnd"}
    exit=0

Evidence anchoring: claude 12/12, codex 2/2, qwen 18/18, gemini 1/2,
kimi 1/1, glm 1/5.

## Boundary -- what this result did NOT establish

- A panel result is advisory and nothing more. It is not approval of the
  plan and not the owner plan gate.
- The opinions cover the r2 bytes at the digest above only.
- Grouping is the driving agent's semantic judgment; finalization proves
  only that supporters are real and that no concern was dropped or counted
  twice.
- Effort high was bound per run only for the Claude and Codex seats. The
  Claude and GLM seats share one CLI codebase. GLM's evidence was anchored
  for 1 of 5 concerns, so its engagement with the bytes is weakly
  established.
- GND does not sandbox reviewer CLIs; the run tree showed no change outside
  the evidence directory afterwards, which is detection, not containment.

## Open questions

Under the bound declared on 2026-10-05, no further plan round runs. Each
group or view is routed to the gate that must settle it. The routing is a
proposal, ruled at the owner plan gate.

| Concern (report fix or divergent id) | Routed to |
|---|---|
| F1 (A) RF-R1 exception contradiction; F11 (D) five-of-six count; F12 (C) dangling RF5-C5 | Owner plan gate: text-only erratum, proposed below |
| F2 (B) strict xfail semantics and clean-layer declaration | RF0 and RF1 spec gates |
| F3 (H) RF-D2 gate naming and stall route | Owner plan gate (ruling); curated-manifest failure: public-launch |
| F4 (I) tool size and co-change metrics; RF0/RF1 budgets | RF0 spec gate; RF4 parts limit at the RF4 spec gate |
| F5 (G) full monkeypatch inventory; stale-patch scan | RF0 spec gate (inventory); every move phase (scan test) |
| F6 (K) helper-family classification and definition of identical | RF0 spec gate; RF2 re-routes at the RF2 spec gate |
| F7 (L) cycle-to-phase assignment; allow-list bound; RF3 vs RF6b | RF0 spec gate; RF3 spec gate |
| F8 (E) unmarked audit claims | RF0 spec gate; dead-assignment claim at the RF8 spec gate |
| F9 (F) missed-target semantics | Owner plan gate (ruling) |
| F10 (J) move-unit definition | RF2 spec gate (first move phase), then inherited |
| claude/late-pins-anchor-drift; qwen/qwen-r2-rf1-c1-mutation-evidence | RF1 spec gate |
| qwen/qwen-r2-rf0-c4-skills-exclusion; qwen/qwen-r2-rf-r7-reachability-hatch | RF0 spec gate |
| qwen/qwen-r2-predicate4-cli-imports-unbound | RF5 spec gate |
| claude/modelindex-cache-key-digest-unspecified; gemini/missing-rf6-rename | RF6a spec gate |

Proposed text-only erratum (A, C, D): remove the owner-exception clause
from RF-R1 and predicate 1, so that an observable change requires a plan
revision; repoint RF5-C5 to RF5-C2 in predicate 4 and the RF0 body; change
"five of the six divergent views" to "all six".

## Refuted premises

- Reviewer claude reported that RF0/RF1 commits made before public-launch
  sign-off would turn the curated-manifest audit red. The mechanism is
  confirmed (audit_tree in tests/test_public_distribution.py refuses
  unlisted paths), but the premise that the lane is currently green is
  refuted: tests/test_public_distribution.py::test_curated_manifest_and_source_owned_ledger
  already failed at the pre-milestone commit 7e08e1e with 55 unlisted
  paths, including public-launch's own Phase 4 files (run 2026-10-05 in a
  detached worktree, 1 failed). The repair belongs to public-launch.
- r2's status paragraph claimed five of six divergent views were repaired;
  all six were (the RF-D2 view was adopted on the owner's ruling).
