---
milestone: model-composition
station: "Corrected candidate comparison and confirmation input"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: candidate-confirmation-input
date: 2026-11-10
gates:
  - command: 'uv tool run --from uv==0.10.10 uv run pytest -q --tb=short'
    exit: 1
    result: '6 failed, 18801 passed, 801 deselected, 1 warning in 2545.10s (0:42:25)'
  - command: 'uv tool run --from uv==0.10.10 uv run python tools/mc1_model_census.py --out candidate-r3-census.json'
    exit: 0
    result: '423members;400originalobservations unchanged;23dispositioned additions'
  - command: 'uv tool run --from uv==0.10.10 uv run pytest -q -s -m "evidence or census" tests/test_mc1_census.py --tb=short'
    exit: 0
    result: '2 passed in 15.80s'
  - command: 'exact frozen failure identities, complete summary, source/origin, tracked status comparison'
    exit: 0
    result: 'no added/removed failures or errors/skips/xfails/xpasses; statuses empty'
  - command: 'affected MC2/model/witness/composition checks'
    exit: 0
    result: '466 passed, 11 deselected in 275.41s (0:04:35)'
  - command: 'ruling: delegated (auto=true) accept corrected comparison, amended plan sha256 c3a510c720fb8918487450beddd1a02ff250b4b720753e134a31bad739c79bb4'
    exit: 'n/a -- corrected comparison only, not milestone acceptance or merge'
evidence:
  - path: .gnd-planning/milestones/model-composition/evidence/close/candidate-r3-result-manifest.json
    sha256: 7775a89226606bbf0ce00a11e2e35f824967d52a2d0e51a9c390aa540c942849
  - path: .gnd-planning/milestones/model-composition/notes/model-composition-plan.md
    sha256: c3a510c720fb8918487450beddd1a02ff250b4b720753e134a31bad739c79bb4
---

# Claim

Correctedb7da04b1ead8dbc72e27ac0b3bf945cc7d970244 completes the actual named beast-3 comparison: 6 failed, 18801 passed, 801 deselected, 1 warning in 2545.10s (0:42:25), exit1. Exactly the original six459ca8d2failure identities remain, no added/removed failure or error/skip/xfail/xpass. Newmarkedcensus exits0:2passed in15.80s. The producer's423-row bytes exactly equal the retained final-census.json; original400per-observable rows remain identical and23additions separately dispositioned. Both actual tracked before/afterstatuses are empty. ParentSSH returned1 with producer0/census0/default1. This is a measured known-red comparison, not a green full suite.

## Scope, source and corrections

The first close opinion REVISE atb89747d6 remains retained.031's real-byte compatibility controls pass after two include-only fallback repairs, as do two actual dirty first-argument guard controls and original clean guard. Seven direct controls,466affectedchecks/11deselected and125source/architecturepins pass; exactly13lint findings/positions remain. Source and budgets are bound in031: MC2source110/test585,MC3source1109/test1239,MC4test120, combinedsupport163=120+22+21. No cap transfers or output/identity/golden regeneration.

Fresh isolated tracked beast-3 checkout, same pinned uv0.10.10/lockeddev, Python3.11.18 and actual imported module origin in the candidate repository. The harness's local main refd2d6309b is historical test context, not actual GitHubmaina9b67d8b. BundleSHA912b3222e38d0380f635fbdf6ca44d30a8ea860f1774c2aa9360b23c1eb270ab matched remotely; initial git bundle verify lacked a repository, then explicit-C baseline verification completed0 before launch. No envfile or credential value was read/printed. Excluded lanes remain excluded. Prior1ca18795pass/sixfail result, rejected8e5fourteenfail output and incomplete6de remain separate historical executions.

## Delegated comparison ruling and main boundary

Delegated acceptance (auto=true),2026-11-10, authority original named milestone instruction plus current owner continue request, accepts exact corrected comparison and appended plan§20 at the SHA above after impact/implementability sweep. This is not the owner's personal reading or final local close. Later current bookkeeping must receive focused metadata controls; no changed runtime/test byte inherits this result.

Actual main remainsa9b67d8b, already containing owner-approved MC3/MC4 in order. Nine exact nonplanning files differ from correctedcandidate: witnessruntime, five test files, offline skill prose and two component-index files. Source manifests and exact delta bind this boundary; the earlier229-pass main smoke predates the refusal repair. Final fixed-head PR158merge needs separate explicit owner authorization. Only afterward can final main equality satisfy all on-main predicates and permit issue95closure. None of those gates is residual-waived.

## Remaining review and record

One narrowly scoped confirmation is now ready: same selected Codex CLI model/effort/read-only/stdin, existing auth only; first opinion1/2used, maximum2. It checks the two reproduced fixes and corrected evidence/limits, not a new broad review or suite. No third call, panel, subagent, native/external historical replay, publication or certification. Final independent disposition, exact delegated local close record/ruling and owner merge/main/issue95 remain pending. No later record is retroactively called reviewed bytes.

Current metadata verification: reference/twin checks exit0 (2 passed in 0.14s);122well-formed citations retain001’s two historical path-only entries. Exact summary is bound in candidate-r3-current-reference.txt. All nonplanning working bytes still equal measuredb7; no source/test/skill/component change inherits an older full result.
