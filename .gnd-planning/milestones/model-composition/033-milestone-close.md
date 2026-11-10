---
milestone: model-composition
station: "Milestone local close; final merge pending"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: milestone-close
date: 2026-11-10
gates:
  - command: 'uv tool run --from uv==0.10.10 uv run pytest -q --tb=short'
    exit: 1
    result: '6 failed, 18801 passed, 801 deselected, 1 warning in 2545.10s (0:42:25)'
  - command: 'uv tool run --from uv==0.10.10 uv run pytest -q -s -m "evidence or census" tests/test_mc1_census.py --tb=short'
    exit: 0
    result: '2 passed in 15.80s;400originalobservations unchanged/23dispositioned additions'
  - command: 'affected witness/composition/model tests after reproduced fixes'
    exit: 0
    result: '466 passed, 11 deselected in 275.41s (0:04:35)'
  - command: 'source/architecture/helper pins'
    exit: 0
    result: '125 passed in 25.82s'
  - command: 'actual direct repair and clean-order controls'
    exit: 0
    result: '7 passed in 0.38s'
  - command: 'ruff check src tests --output-format json'
    exit: 1
    result: 'exact13baseline findings; existing declared checkpoint offset only'
  - command: 'components_index.py --no-cache changed --base origin/main --strict'
    exit: 0
    result: '0 to fix,0 warnings; witness subsystem reread disposition031'
  - command: 'one independent Codex CLI close review plus bounded confirmation'
    exit: 0
    result: 'REVISE2findings; reproduced/fixed; confirmationAPPROVE at86ad71f1, budget2/2consumed'
  - command: 'historical manifest audit at original snapshots'
    exit: 0
    result: '16manifests/1598bindings/0mismatches'
  - command: 'ruling: delegated approval (auto=true), exact amended plan sha256 c3a510c720fb8918487450beddd1a02ff250b4b720753e134a31bad739c79bb4, final sweep sha256 b0693934df84517587d931517a2e64d1f68e0f8b593111070e0f95a96839360c'
    exit: 'n/a -- local close only; PR158/main/issue95 external gates pending'
evidence:
  - path: .gnd-planning/milestones/model-composition/notes/model-composition-plan.md
    sha256: c3a510c720fb8918487450beddd1a02ff250b4b720753e134a31bad739c79bb4
  - path: .gnd-planning/milestones/model-composition/notes/close-final-question-sweep.md
    sha256: b0693934df84517587d931517a2e64d1f68e0f8b593111070e0f95a96839360c
  - path: .gnd-planning/milestones/model-composition/evidence/close/final/manifest.json
    sha256: bd6d8ee8f6af9d6dc9a8fb97afe262c246b9a55d30fab8ba3ad23c7e2147a465
  - path: .gnd-planning/milestones/model-composition/032-candidate-confirmation-input.md
    sha256: 59e45ce6cc5ea8eed94c50717cb2be8f5f7570172b8d03330509f6f3e905c2c8
---

# Local milestone close with final merge pending

All four mandatory phases MC1–MC4 are locally accepted, their phase PRs merged under explicit owner authority. Corrected close sourceb7da04b1ead8dbc72e27ac0b3bf945cc7d970244 has completed current compatibility evidence and independent conditional local close approval. Delegated approval (auto=true),2026-11-10, under the original named milestone instruction and current continue request accepts the exact amended plan and final question sweep hashed above for **local close only**. This is the coordinator’s ruling, not the owner’s personal reading. PR158's explicit final fixed-head merge, final main equality and issue95closure remain unsatisfied external gates. The milestone is not declared complete on main.

## Phase and predicate audit

| Phase | Gate/completion evidence | Acceptance and merge |
|---|---|---|
| MC1 |002–008 exact spec/repairs; loader/twin/inline rules/refusals/scaling/census;008completion |Owner-raised1100/1900stop respected; PR154d5ca5d9a |
| MC2 |010/012/013 exact corpus and complete32-row admission matrix; model verbalization and explicit refusals |PR156720053ff; later027–032adaptations remain separately attributed |
| MC3 |015–023 exact16-case corpus, ownership/re-pin/snapshots/CAS/recovery/writers;1365primary and1820impact passes overlap |Owner1400/1400stop; explicit fixedc6dad88d PR157mergeded091709 |
| MC4 |024/025approved final story/commands/figures/skills/nav/release;338selectedofflineblocks,96tutorialtests, strictbuild/site/component gates |Explicit fixed396f86f3 PR155mergeda9b67d8b afterMC3 |

Predicates1–3 are supplied by008's actual composition/twin/refusal/inline controls and later rooted consumers. Predicate4 retains400original per-observable census rows, current six-failure full comparison and the new adapter controls that discriminate a previously missed legacy refusal. Predicate5 has every32-row admission decision plus exact later ILP/discover/evolve/example successors. Predicates6–7 use023's actual authored-only re-pin publication/component scenario and025's independent expense update. Predicate8 has one normative format home, existing evolution grammar, three skill citations, runnable expense story/command page and actual owner reaction. Predicate9 has approved phase gates, all completion records, this final question disposition and independent close opinion; its actual on-main/issue95completion component remains pending the final external gate. No activity count substitutes for that gate.

## Verbatim gate outcomes and attribution

The completed named beast-3 result is `6 failed, 18801 passed, 801 deselected, 1 warning in 2545.10s (0:42:25)`, exit1. Exact six failed node identities equal immutable459ca8d2; no added/removed failure, error, skip,xfail orxpass. Both tracked statuses are empty. Marked census is `2 passed in 15.80s`, exit0; new423-row producer bytes exactly equal the retained artifact. Original400observations are unchanged;23additions have separate dispositions. Actual module origin and Python3.11.18 are bound. Local focused work used Python3.11.15 and is not conflated with that execution. No full suite is called green.

032binds all new raw summaries/exits/source/runtime/status and preserves older1caresult, rejected8e5fourteenfail output and incomplete6de separately.031binds actual pre-fix4fail/2pass, baselineadapter2pass, post-fix7pass,466affectedpasses/11deselected,125pins and exactly13lint positions. Focused selections overlap and are not summed. MC4's strict build/site and tutorial results remain bound to their unchanged documentation bytes, with phase reviews correctly limited to their snapshots. Final bookkeeping receives its own focused metadata check; its record bytes are not retroactively called reviewed.

## Independent review and convergence

One selected Codex CLI reviewer (explicit owner override of maintained panel),0.163.0/gpt-6.1-sol/xhigh/read-only/stdin, existing authentication only. First close opinion atb89747d6 REVISE found one blocking include-free composed witness/replay refusal defect and one hardening guard gap. Both reproduced and gained real controls observed red before fixes. Witness adapters now forward only include:* reasons, preserving legacy input-invalid; the guard binds the actual first candidate argument. The initial included hash-mismatch oracle was refuted and corrected before production edits to preserve unsupported-route order.

The sole confirmation at86ad71f1 APPROVE finds no unresolved scoped finding. It executed fresh actual-adapter/baseline/dirty-guard probes, checked46evidencebindings/fivesourcebindings, all4698nonplanning paths/modes, budgets and uncached13-position lint. Its unfiltered reference scan encountered an ignored nested worktree; tracked Markdown/twins/modes passed. It did not rerun broad/native/external suites or real publication/race fixtures. Prior phase reviewers remain distinct scoped opinions. No panel or subagent was invoked.

| Round | Seats | Findings | Blocking / total | Self-inflicted / total | Verdict |
|---|---|---|---|---|---|
| First close |1CodexCLI|2:1blocking,1hardening|1/2|n/a first close opinion|REVISE |
| Narrow confirmation |same1seat|0unresolved|0/0(n/a)|n/a no findings|APPROVEconditional local close |

Declared026budget is2calls and now2/2consumed. Same-seat counts2→0 fall; no further round is selected. Later ruling/navigation metadata has only focused current checks, not an invented third opinion.

## Plan repair, refuted premises and questions

All original plan/record/review bytes remain preserved at their snapshots. Effective amendments13–20 retain exact raising records/dates/prior wording: census additions versus original400, intake metadata versus positive currency, actual serial overlap/new model verbalize route, same-phase normative seams, conservative breaking re-pins, authenticated history/live CAS ordering, corpus newline locators, component hook contradiction, owner-selected Fable story, exact examples, retained draft home, offline guidance and API/order/inventory guards, actual merges and the two reproduced close findings.031/032do not relabel either first review REVISE or the old wrong included answer as success. The final sweep resolves inherited/new technical questions or names explicit residual owners.

## Open questions

Open questions are only the final owner merge gate and subsequent coordinator main/issue verification, plus accepted repository-owner maintenance residuals: six baseline default failures,13lint findings, exact historical-output formatting and the delivered component-hook contradiction. These residuals never waive pending merge/main/issue gates. No successor work is started.

## Refactoring review

No additional runtime refactor is needed at close. The phase work retains one canonical composition loader, existing descriptor/path seams, explicit identity aliases, public effective-view/ModelIndex variants and registered family dispatch. The close repair reuses the established neighboring adapter fallback and existing regex support; witness.service and generated component documentation are updated in its commit. New homes/allowances are not added. MC2conservative110source/585tests are under375/600; MC3source1109/test1239 under1400/1400; MC4test120/120unchanged. Combined post-MC3 support163=120+22+21, four production additions separate, no cap transfer. The subsystem reread remains correctly described; the delivered hook contradiction stays repository-owner maintenance.

## Boundary — final external gate

Actual maina9b67d8b exactly equals approved MC4 and has229fresh focused main passes, with invalid initial archive/editable attempt separately recorded030. It is still9nonplanning files behind correctedcandidate, including the restored witness refusals. These new passing candidate outcomes are not called main outcomes. After explicit owner authorization for PR158's final fixed head, verify head/reviews/threads, SHA-guarded merge, fetch main and assert all4698nonplanning tracked paths/modes/blobs equal measuredb7. Unexpected relevant changes invalidate affected observations. Only then close issue95and report actual main SHA; the GitHub merge/issue events supply the post-record external disposition.

Finite gates and one reviewer do not prove universal behavior. Excluded historical/native/proof/external lanes were not executed; no multi-file atomicity, nested/remote includes, include-bearing generated-app/conformance or linked-project evolution support is claimed. No publication, certification, owner personal byte reading or successor milestone is authorized. This record's local acceptance never invents final merge authority.

Final current-context reference/twin verification exits0: `2 passed in 0.14s`. Frontmatter validates126citations, retaining only001’s two original path-only entries. All nonplanning working bytes remain measuredb7; final manifest binds navigation, sweep, opinion, audit, current controls and original phase/result records. Final authored whitespace must remain clean; exact raw-output residuals remain separately enumerated in their original records.
