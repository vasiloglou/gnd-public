---
milestone: release-0.4.0
station: plan-gate
scope: plan-gate
date: 2026-11-17
skill: "n/a -- repository development under process-milestone"
gates:
  - command: "uv run python tools/run_gnd_review_panel.py review-request.json --out panel-run --reviewer-timeout 600 --overall-timeout 900 --max-output-bytes 8388608"
    exit: 0
  - command: "uv run gnd review finalize panel-run synthesis.json --out PANEL-REVIEW.md"
    exit: 0
  - command: "ruling: delegated (auto=true) approved .gnd-planning/milestones/release-0.4.0/notes/release-0.4.0-plan.md sha256 e9828d47fcf6429f85a9869e29972d75e8efb706dd5d2e0d0f0fb6062b3be7ed"
    exit: "n/a -- ruling"
evidence:
  - path: .gnd-planning/milestones/release-0.4.0/evidence/plan-r1/PANEL-REVIEW.md
    sha256: cd1afe957dd90d7394b3af2b2c78db2a42de2213750c8b8082e72b9495ca697c
---

# Claim

The standard GND panel reviewed the r1 plan from commit `9458c0a1`, SHA-256
`6eb1f3a6146d69de3a587cd94ab213133c9f0e61ba499d0f962b001a8fc5b338`.
All six reviewers produced validated responses. Qwen's response had one
schema-invalid line dropped at position 11. Claude had two unanchored
concerns and Codex had one. Verified those findings directly against the
freeze gate, publication tag instructions and packaged receipts example.

## Review disposition and implementability

The [panel report](evidence/plan-r1/PANEL-REVIEW.md) retains all 34 concerns in
six agreed groups and 18 divergent views. [Plan r2 §11](notes/release-0.4.0-plan.md#11-amendments-after-the-standard-panel-2026-11-17)
binds the fixes. The existing acceptance test verifies a 0.3.0 candidate and
the old-release test pins 0.2.0. The RV2 edit and pre-freeze merge therefore
precede the acceptance run. The prior RN2 script provides the pinned uv setup
and checksum verification. The receipts example test provides source-grounded
expected findings and the missing-decision control. The existing literature
fixture and catalog tests provide concrete inputs for the two literature
probes. E1 remains an unrun diagnostic with a separate spec gate before edits.

The conditional tag-only reading is closed by selecting the PyPI route.
A conditional extra probe for PR 204 is deferred to the RV2 fixture decision
and named as a coverage boundary if omitted. Receipt availability tests the
actual packaged resource. The previous release's docs and records provide
the full control digest, earlier tag target and expected evidence locations.
The two rejected finalization drafts used an incorrect ordering of reviewer
IDs. The retained synthesis uses the fixed roster order and finalization
exited 0.

| Stage | Prerequisite | Current gate | Next action |
|---|---|---|---|
| RV1 | Plan gate | Draft spec | Rule on E1 diagnostic, then measure |
| RV2 | RV1 on main | Pending | Prepare the acceptance spec |
| RV3 | RV2 accepted candidate | Pending | Prepare hand-over |
| Close | Recorded publication and phase evidence | Pending | Standard panel and delegated close ruling |

## Gate output (verbatim)

    panel: exit 0
    {"advisory":true,"attempted_reviewer_ids":["claude","codex","qwen","gemini","kimi","glm"],"command":"review panel","gnd_version":"0.3.1","outcome":"quorum-established","quorum_met":true,"request_kind":"plan","request_sha256":"4ec61bf16e8df9c91ce91594b0bc5075b00eeae9fa3b5d6ac17b853f497b74c1","required_successes":3,"reviewed_artifacts_unchanged":true,"reviewer_effort":"xhigh","reviewer_statuses":[{"reviewer_id":"claude","status":"success"},{"reviewer_id":"codex","status":"success"},{"reviewer_id":"qwen","status":"success"},{"reviewer_id":"gemini","status":"success"},{"reviewer_id":"kimi","status":"success"},{"reviewer_id":"glm","status":"success"}],"run_directory":"panel-run","run_sha256":"820f4ea576145074c49ada1a286cb42d95cf5abd0c61438d8a2847e9b7fa3fcc","schema_version":1,"successful_reviewer_ids":["claude","codex","qwen","gemini","kimi","glm"],"tool":"gnd"}
    finalize: exit 0
    {"advisory":true,"agreed_concern_count":6,"command":"review finalize","divergent_concern_count":18,"gnd_version":"0.3.1","outcome":"quorum-established","prioritized_fix_count":10,"quorum_met":true,"report_path":"PANEL-REVIEW.md","required_successes":3,"run_sha256":"820f4ea576145074c49ada1a286cb42d95cf5abd0c61438d8a2847e9b7fa3fcc","schema_version":1,"successful_reviewer_ids":["claude","codex","qwen","gemini","kimi","glm"],"synthesis_sha256":"f26e5d371042c75ed65eca8d4ca91d28daf86ce32a1d2764dfe72f39830d70c2","tool":"gnd"}

> Delegated approval (auto=true), 2026-11-17. Approved the release-0.4.0
> plan r2 at SHA-256
> e9828d47fcf6429f85a9869e29972d75e8efb706dd5d2e0d0f0fb6062b3be7ed.
> Source: the owner's explicit milestone invocation with auto and subsequent
> "gnd standard" instrument selection. Scope: plan decisions RV-D0 through
> RV-D10 as amended, with phase and close rulings to be recorded separately.
> Review budget: one standard panel round, six fixed reviewer attempts,
> 600 seconds per seat and 900 overall, 8 MiB output limit per invocation.
> The reviewed r1 and the approved r2 have distinct digests. The amendment
> corrects implementation and evidence ordering with existing controls.
> Phase size limits and separate owner merge and publication gates apply.

## Boundary

Immutable raw panel streams and the run manifest are retained outside Git
history in the local `gnd-release-040-plan-r1-evidence.tar.gz` archive,
SHA-256 `4d8d8f316e0b920f6da380ccdba54fc1ebe7c1b04132c6673a875c41e5156f8e`.
The manifest SHA-256 appears in the tool receipts above. Raw audit is
available to the archive holder. The repository retains the request,
normalized synthesis and finalized report.

The review is advisory and binds r1. The amended plan r2 received the
delegated implementability ruling above. Build, acceptance and publication
remain downstream. The six seats used five executables. Capability probes
verify the documented invocation flags. GND asks reviewers to preserve the
tree and checks the artifact digest, while reviewer tools retain their own
execution permissions.

## Open questions

- RV1 owns E1's measured outcomes and classification review.
- RV2 owns the exact installed probes and execution profile.
- RV3 owns the hand-over snapshot and exact publication commands.
