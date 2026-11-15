---
milestone: literature-identity
station: renewed-close-panel-retry
skill: "gnd-review-panel"
scope: panel
date: 2026-11-15
gates:
  - command: "uv run --no-sync python tools/run_gnd_review_panel.py .gnd-planning/milestones/literature-identity/evidence/close/renewed-request.json --out <scratch>/panel-run --reviewer-timeout 600 --overall-timeout 900"
    exit: 0
  - command: "uv run --no-sync gnd review finalize ../panel-run ../renewed-synthesis.json --out ../renewed-panel.md"
    exit: 0
evidence:
  - path: .gnd-planning/milestones/literature-identity/evidence/close/renewed-request.json
    sha256: 97277e0bee2225d8100ec4b7a35d5d41ed90448430b3378d9b7ae2201a777f80
  - path: .gnd-planning/milestones/literature-identity/evidence/close/retry-summary.json
    sha256: 5ea3f47eed03d88f1aa421d465ceb9384921bcbfb8e59cf0ecd913e832b233a5
  - path: .gnd-planning/milestones/literature-identity/evidence/close/retry-synthesis.json
    sha256: 6fdd2fec683758016a6556b9e9532a1626d82967d10de861921a54287aac6cdf
  - path: .gnd-planning/milestones/literature-identity/evidence/close/retry-panel.md
    sha256: bf32488e29f4c4799a69a377274817261616274ba16b7f1ec6136cc0c8b335b0
---

# Renewed close panel retry

The owner approved one further paid round after [033](033-panel.md).
The maintained panel reviewed the same three artifact digests in a
clean clone at `ff7ce094`, whose tree matched `main` at `92646ab2`.
Qwen used its native sandbox. The clone had no reserved ref.

## Gate output

The runner exited 0 with `quorum-established` and
`reviewed_artifacts_unchanged: true`. All six reviewers returned
schema-valid responses, meeting the project requirement of four.
Codex approved. Claude, Qwen, Kimi and GLM asked for revisions.
Gemini returned block. Kimi retained both concerns and one preamble
line made its response incomplete. No concerns were dropped.
Claude anchored 5/5 concerns, Qwen 6/6, Gemini 0/2, Kimi 2/2 and GLM
2/2. Codex raised no concerns. Claude and GLM share a CLI executable.

Finalization exited 0 with three agreed groups, eight divergent
concerns and four prioritized fixes. The
[report](evidence/close/retry-panel.md),
[synthesis](evidence/close/retry-synthesis.json) and
[summary](evidence/close/retry-summary.json) retain the findings and
run binding. The raw run directory remains local outside Git.

## Findings and dispositions

| Support | Finding | Disposition |
|---|---|---|
| Claude, Qwen, Gemini, GLM | Plan §11 describes the earlier close only | Append the first executable fresh score and its separately approved corpus to the plan chronology. Retain the original C6 freeze and prior outcomes. |
| Claude, Qwen, Kimi | Aggregate omits some execution inputs | 027 binds the model, policy, runner and rubric. 028 binds the key and 030 binds the composed input. The private rubric copy matches 027. The renewed close records the exact bindings together. |
| Claude, Qwen | Prove and rule the decision-only correction | Compare the exact objects against the actual admission subset. The one omitted `same` decision could never bind. The close records the scope and accepts the pre-score recovery. |
| Claude | False-path exclusion does not isolate path-policy causation | Both false targets lacked a required admitted directed edge. The fresh measurement tests end-to-end exclusion. The development negative control in 024 tests that a wrong accepted path lowers the score. |
| Claude | Internal provenance labels name the corpus author | The frozen example writes corpus-author producer and judge labels. Those are internal assembly labels. Record the actual Astra annotation and separate Codex custody in the close, with the production bytes kept fixed. |
| Qwen | Recorded read-only flag does not establish isolation | The abbreviated 030 entry lists the inner CLI flag. The original invocation was wrapped by an OS sandbox from a separate directory. Reapplying that profile allowed source reads and denied repository and both key reads. The close binds the profile and transcript hashes. |
| Qwen | Fresh result omits the development score | Cite 024 with the separate 3/3 supported and 5/5 excluded development result. |
| Qwen | Gate output in 030 is not attributed | The statement-equality line came from the driver comparison. The JSON exit line came from the assembler. Record the distinction in the renewed close. |
| Gemini | The first assembly refusal undermines reliance on the recovered input | Retain the refusal and the dissent. The approved predicate measures supported and false paths, and the single score used the first executable blind input. The driver had verified the only removed reference was unadmitted and kept every statement and valid decision fixed. The renewed claim leaves zero-shot assembly unmeasured. |
| Kimi | A substitute corpus is distinct from repeating the original | The 026 open condition called for an independent measurement under an approved corpus. The 027–028 owner rulings establish the fresh corpus. The original first result remains 0/1. The renewed close states the scope explicitly. |
| GLM | Format-only wording obscures a removed data item | Call it removal of one inadmissible resolution reference before scoring. The first assembly refusal and all comparisons remain explicit. |

The request and reviewed artifact bytes were identical to the previous
round. The retry addresses the prior non-starting sandbox and seat
shortfall. It was the only additional paid round authorized.

## Boundary

The panel is advisory. The project reviewer count is satisfied.
The policy acceptance and status are recorded separately in
[035](035-milestone-close.md).

## Open questions

- The remaining milestone residuals and the renewed ruling are in 035.
