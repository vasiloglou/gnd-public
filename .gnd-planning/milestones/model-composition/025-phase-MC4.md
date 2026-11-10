---
milestone: model-composition
station: MC4 documentation and skills
skill: n/a -- repository development, not a gnd-solve station over a domain
  model
scope: phase-MC4
date: '2026-11-10'
gates:
- command: uv run pytest -q tests/test_documentation_tutorials.py --tb=short
  exit: 0
  result: 96 passed in 62.26s (0:01:02)
- command: uv run python tools/run_tutorials.py
  exit: 0
  result: 338 tutorial blocks passed; optional native lanes skipped, not claimed
    executed
- command: uv run pytest -q tests/test_skill_prose_sync.py
    tests/test_packaged_skills.py tests/test_plan_app_docs.py
    tests/test_mc1_guards.py tests/test_mc4_expense.py --tb=short
  exit: 1
  result: 1 failed, 196 passed in 1.99s; exactly inherited grow-a-model prose
    failure
- command: uv run pytest -q tests/test_mc4_expense.py
    tests/test_packaged_skills.py tests/test_skill_prose_sync.py
    tests/test_mc1_guards.py --tb=short
  exit: 0
  result: 111 passed in 1.71s
- command: .venv/bin/zensical build --strict
  exit: 0
  result: No issues found; rerun after source-link repair
- command: .venv/bin/python tools/check_docs.py site
  exit: 0
  result: 16018 local links/assets/anchors checked
- command: uv run python scripts/components_index.py --check --strict
  exit: 0
  result: generated index current
- command: uv run python scripts/components_index.py changed --base 30e91079
    --strict
  exit: 0
  result: 'changed against 30e91079 (30e9107): 84 file(s) differ; 0 to fix, 0 warning(s),
    0 to reread'
- command: uv run ruff check src tests --output-format json
  exit: 1
  result: same13 inherited findings, exact five-line checkpoint location offset
- command: git diff --check c6dad88d..HEAD -- docs src tests tools dev
    zensical.toml
  exit: 0
  result: source delta clean
- command: git diff --check c6dad88d..HEAD
  exit: 2
  result: four trailing-space lines in retained historical logs, explicit
    delegated residual
slow_cadence:
  command: uv run pytest -q -m "evidence or census"
  disposition: Not selected wholesale; named final beast-3 census/default
    selected separately and running
evidence:
- path: .gnd-planning/milestones/model-composition/notes/phase-MC4-spec.md
  sha256: edd5bee311efbc886b3d91b0f3e7f3b69be26e2af0cfbee7c8b1c41913761113
- path: .gnd-planning/milestones/model-composition/024-MC4-gate.md
  sha256: 553439186d70b3c7bd1e1b55485e050a39ee1dcad2df35a72a71fc0ce70e5dc2
- path:
    .gnd-planning/milestones/model-composition/evidence/MC4/completion-source-manifest.json
  sha256: 63330264b258764f7d7f9231cd8801d18c1e355e2da8535d103e863c647dd612
- path:
    .gnd-planning/milestones/model-composition/evidence/MC4/completion-evidence-manifest.json
  sha256: fe146340e7dd381de2d9414d304449bf639d1387c9190fd5c6af4450abebf556
- path:
    .gnd-planning/milestones/model-composition/notes/phase-MC4-codex-review.md
  sha256: 28bb34cda0af44fa0c86e30569ccc244eef53d84241d15e851869a4115d48116
- path:
    .gnd-planning/milestones/model-composition/notes/phase-MC4-codex-confirmation.md
  sha256: db3c3755ad0f57e08f14e689d84def6e150e132dcc4de287c2c847e5de960e0b
- path:
    .gnd-planning/milestones/model-composition/evidence/MC4/review-repair-size.json
  sha256: 8367394acbf1278825c288b7e9cd04da8af5a3ed792e4cce8a454c0faa988e75
---

# Claim

MC4 is complete locally at reviewed source6de7189a47dfc11a385dd60de0f0ebb942dfa452. Delegated acceptance (auto=true),2026-11-10, under the owner's named milestone request accepts the phase with explicit inherited failure and historical-log boundaries. This is agent acceptance under delegation, not the owner's personal byte review or merge authorization.

## Criteria and measured coverage

| Criterion | Evidence |
|---|---|
| C1 single home/citations | Includes grammar stays in representation-format.md; three skills and CLI cite it. Existing evolution grammar remains its one home. Frozen238 routing edges plus MC3one plus MC4two cross-skill citations; exact sets and dirty remove/wrong-anchor controls retained. ORM-core same-directory link is outside that cross-skill regex. |
| C2 shipping contract | Command walkthrough demonstrates retained versioned files, exact raw pins, project-specific re-pin, authored-only publication and historical-file route; no external fact generator implemented. |
| C3 doc-sync/skill structure | Current focused selection196passes; sole failure is the unchanged grow-a-model paragraph (141words vs90). Original bytes independently equal at c6dad88d/current. No waiver, xfail or unrelated edit. |
| C4 whole update story | Accepted Fable expense story shows Finance edition2, receipt_required affected, six caps unaffected, valid combined update and final checks. Original MC3 component corpus remains unchanged. |
| C5 runnable shipped example | 28 expense blocks in existing runner; mandated whole offline runner338blocks exits0; mandated tutorial tests96pass. Later repairs change only two redirect URLs and a regression; canonical pages, commands, runner and data remain identical. |
| C6 figure | Before/after SVG with complete alt and named shipped source; rendered figure inspected, images loaded, no page overflow. Screenshot retained in visualization workspace, not committed. |
| C7 site integration | Both navigation entries and unreleased release note; strict build and local site checker rerun after repair exit0. Source links now target eventual main; this record does not claim merge/publication. |
| C8/MD17 reaction | Actual Fable authorship retained in019/020; two earlier rejections preserved. Owner answered “Yes, this explains it” to expense story. Feedback accepts direction, not bytes. |

Commands measure edition-only invalid preview3 and named own rule; valid preview0 and exact acceptance; apply/finalize0; supported Sales expenses0 and missing document1; unchanged Engineering0. The authored Sales output exactly equals shipped candidate, retains all six caps, and copies no shared definitions; both shared editions and Engineering remain byte-identical. Tampered vocabulary3, dinner/approval team contrasts0/1 and missing receipt warning/violation0/1 remain exercised. New byte/path-only semantically unchanged re-pin test proves breaking classification, unaccepted apply refusal and exact accepted preview. This is not multi-file atomicity or generated-app conformance.

R30 now admits exactly three named rooted expense examples and retains the prohibition for every other example. Isolated actual-predicate controls pass current set and reject deleting the expected sales-v2 file or adding an unexpected include root. The400-original compatibility comparison belongs to separate close evidence, not this focused phase claim.

## Review and repairs

One reviewer is one reviewer. Codex CLI0.163.0, gpt-6.1-sol/xhigh, ephemeral read-only, one first opinion plus one bounded confirmation. First review's completeness-labelled finding was triaged as a mandatory source-link fidelity repair: retained redirect pages selected draft source. The added regression failed before the two-URL fix; focused repair gate111passed afterward. Confirmation approves exact9f3d22f7..6de7189a scope, independently verifies old fails/new passes/either reverted page fails, thirteen neighboring local links/anchors, thirteen main source paths within the snapshot and all three repair hashes. Remote URL availability was not tested.

First reviewer independently ran70pass/1skip/7deselected selected checks, ten population outcomes and read-only invalid/valid previews; initial temporary-capture/fixture setup errors are not passes. Confirmation's initial heredoc and overly strict link assertion failures likewise remain disclosed. Neither reviewer re-executed full publication/rendering/default/census/native lanes. Parent runtime runner/build/browser gates supply those narrower observations. Two review invocations exhaust the phase budget; no further phase reviewer is selected.

## Refactoring review

None needed. The phase changes documentation, example data and exact integration controls. It reuses the canonical loader/evolution services, tutorial executor, site checker, packaged link inventory and component generator; one runner registry entry introduces no alternate executor. No module, ModelIndex waiver, family hook, layer allowance or discovery link changed. The generated tools component page was refreshed for shifted runner positions; strict changed check reports zero failures/warnings/rereads. No structural debt was exposed beyond previously recorded close repairs.

## Findings and fidelity

Gate024 binds the preimplementation prose spec; its immutable Git snapshot preserves approved bytes, later findings append only. Checkpoint history preserves earlier driver-authorship ruling superseded by the owner's actual Fable request. JSON-compatible proposal text still uses existing application/yaml media type; new rule follows D-12 user-supplied/confirmed metadata. Initial wrong media type, missing --records, out-of-workspace output and unresolved macOS temp alias were developer probe refusals, not successful examples. Old six caps retain original provenance.

Conservative final size:0 production Python,759 added prose/SVG against effective700estimate/1050stop,114 test/support Python including36 checkpoint-wrapper lines against80estimate/120stop. Shipped JSON and retained execution outputs are separate data/evidence, bound by manifests; they are not hidden as Python. Original450doc heading plus MD17's selected250line cost remains preserved for close plan repair. No other phase's size exception transferred.

## Boundary

All mandatory phase work is completed locally, with196 current focused passes and exactlyone inherited prose failure; lint retains13 baseline findings with the declared five-line checkpoint shift. Unrestricted committed whitespace check exits2 on four retained historical log lines; source-scoped check exits0. Delegated acceptance preserves those verbatim logs as explicit artifact-only residual, matching record009's policy. This record does not rewrite old evidence or call a red gate green.

No phase completion is a merge, release, certification, issue closure or milestone close. PR157's fixed MC3 merge authorization remains pending; PR155 will carry final MC4. The authorized final beast-3 census and full default comparison run at6de7189a separately; actual main-branch predicates, independent close review and canonical plan/question repair remain owed. Unsupported linked-project/codegen/conformance includes routes remain refused. No optional native or excluded historical lane is reported complete.

## Open questions and carryovers

| Subject | Owner/target |
|---|---|
| MC3/MC4 merges | Owner explicit fixed-head authorization; coordinator verifies heads and review threads before merging. |
| Final comparison | Coordinator close: retain beast-3 candidate outputs, compare original400 and disposition23 new models; exact six full-default failure names against baseline. |
| Plan/question repair | Coordinator milestone close: all prior phase repairs plus selected Fable expense story, actual reactions, effective MD17 size and R30 successor; retain prior wording. |
| Independent close | One explicitly selected Codex CLI reviewer under owner panel override; phase reviews do not substitute. |
| Existing six default failures/13lint findings | Repository maintenance owner; explicit unchanged residuals, no broad waiver. |
