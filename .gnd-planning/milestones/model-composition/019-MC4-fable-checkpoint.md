---
milestone: model-composition
station: "MC4-draft Claude Fable expense checkpoint"
skill: "n/a -- repository development checkpoint, not a gnd-solve station"
scope: MC4-fable-checkpoint
date: 2026-11-10
gates:
  - command: ".venv/bin/python .gnd-planning/milestones/model-composition/evidence/MC4-draft/run-expense.py /tmp/mc4-expense-receipt-final.json"
    exit: 0
    output: "19 tutorial blocks passed"
  - command: ".venv/bin/pytest -q tests/test_plan_app_docs.py -k 'shared-expense-policies or shared-component-vocabulary or share-a-vocabulary' --tb=short"
    exit: 0
    output: "14 passed, 72 deselected in 0.07s"
  - command: ".venv/bin/zensical build -f .mc4-draft-zensical.toml"
    exit: 0
    output: "Build finished in 0.50s; No issues found"
  - command: "python3 scripts/components_index.py --no-cache changed --base origin/main --strict"
    exit: 0
    note: "Base720053ff;0 to fix,0 warnings,0 rereads."
  - command: ".venv/bin/pytest -q tests/test_mc1_guards.py::test_R30_examples_do_not_declare_includes --tb=short"
    exit: 1
    output: "1 failed in 0.28s"
    note: "Known temporary include-example integration assertion remains; this is a draft, not merge-ready MC4."
  - command: "git diff --check"
    exit: 0
evidence:
  - path: .gnd-planning/milestones/model-composition/014-MC4-draft-revision.md
    sha256: 9c90accdcfd2cb80f43998f66a6703fb4eaea649ee74f692acfffe370a187083
  - path: .gnd-planning/milestones/model-composition/evidence/MC4-draft/fable-owner-reaction.json
    sha256: 615c2c9d77a1ae0a7f0d0a02ce4e0244a91826b856d8725573016a1d1d4cd9f0
  - path: .gnd-planning/milestones/model-composition/evidence/MC4-draft/fable-manifest.json
    sha256: 6af50ad5cfd0565dec6e2643b2a5f7d82e2c7cfdde0673935070ad55be51cfc5
  - path: .gnd-planning/milestones/model-composition/notes/phase-MC4-fable-draft.md
    sha256: 4a3cdd3d4cb802fc91eaa7ebb75ef3f9374c5391eae5a747483eb789b3b05ea7
---

# Claim

Claude Fable authored the replacement expense story; its current-demo results were then verified through19 runnable blocks, eight independently checked JSON outcomes and14 focused prose checks. The site builds without issues. The owner has not yet reacted to this replacement page, and its update half remains planned.

## Owner direction and actual delegation

The owner rejected the revised scanner page: “no it doesn't I don't understand what you mean by the scanner? ask fable from claude to do this task for you. Explain what you want to demonstrate, and ask it to pick an existing demo example, like the expense report or the bookrec or anything else and extend it to show the functionality in the same high level manner”. This explicit authorship/example selection supersedes record014's driving-agent writing choice and the scanner framing; it is not merge or byte approval.

One Claude CLI request on stdin used --model fable, high effort, read-only Read/Glob/Grep, dontAsk permissions, no session persistence, no MCP, and existing authentication. No repository environment file, network research, other agent or file mutation was permitted. The returned result is success/is_error:false and actual canonical model claude-fable-5-2. The exact request/response and full draft/handoff are retained with path sanitization. This is a writing delegation, not an independent review or a Fable claim that commands ran.

Fable chose the existing expense demo over bookrec: teams already have a familiar reason to apply different spending/approval limits to the same expense facts. It proposed the receipt relation explicitly as new data. The driver verified the actual original20 rules split into14 shared rules and6 team limits, then added shared receipt uniqueness and each team's owned mandatory receipt rule. That yields15 common and7 team rules,22 total. Original expense/app Python files remain unchanged.

## What the reader sees

Engineering and Sales use one shared expense definition. Engineering's original limits are75 EUR for meals and100 EUR for team-lead approval; Sales's proposed limits are120/1000. The actual same90 EUR dinner and800 EUR team-lead approval fail Engineering and pass Sales. With expense102's receipt absent, Engineering reports21 pass/1 warning and exit0; Sales reports21 pass/1 fail and exit1. Both clean seeds report22 pass/exit0. The team receipt remedies appear in the real output. Equal facts across the paired model-bound population files are asserted.

The main page keeps file/hash/command plumbing on the supporting how-to. Its requests are suggestions, not invented agent recordings. The driver replaces expected labels only for measured Part1, corrects Fable's placeholder normative link and makes the source-file grouping explicit: the renderer supplies the complete text/header, not per-sentence owner labels. Two complete read-backs are checked for shared receipt and correct own policy. The tamper check runs in a scratch copy and refuses include:hash-mismatch. Part2 visibly describes unfinished MC3; edition2 data is standalone-valid, but no preview/publication result is claimed.

The rejected scanner pages become pointers to the new story. Only this PR's rejected scanner data/figures are removed; their exact historical bytes and records011/014 remain in Git/evidence. The new receipt rules use explicit fictional requirements with their quoted team sentences, rather than implying an actual employee policy approval. This remains a synthetic demo.

## Gate output (verbatim)

    shared-expense-policies-commands.md: selected executable blocks passed
    19 tutorial blocks passed

    14 passed, 72 deselected in 0.07s

    Build started
    Build finished in 0.50s
    No issues found

    1 failed in 0.28s

The first focused prose selection was2 failed/5 passed because a blanket technical-word ban also banned ordinary expense “receipt” prose. The scoped successor permits that domain word on exactly the two new pages, while still refusing execution/validation/verification/evidence receipts there. Other pages and all other banned terms retain their checks. This is recorded scope, not a fix to the unrelated known grow-a-model failure. Final14 focused checks pass.

Build uses a temporary project-local config/output copied to the localhost review site; both local temporary paths were removed. Playwright inspected the rendered page and captured the view. The manifest marks screenshot/HTML persistence as weaker outside-history evidence. Catalog strict0 has no changed runtime member. R30 still exits1 on the new include example; final MC4 must replace its temporary blanket assertion with the exact rooted expense-example successor and keep every old raw-example guard control.

## Boundary

This checkpoint is not final MC4, a personal owner reading or an independent review opinion. No codegen/conformance/current generated-app claim is made for include models. No update/publication command from the planned half was run. Nav/release/runner registration, final skill changes, R30 integration, strict final site/doc gates and required phase diff review remain owed. PR155 stays draft and unmerged. MC2 was merged under separate explicit authority at720053ff; partial MC3 is saved on its own branch/stash and resumes under the owner1400/1400 stop. No milestone close, issue closure, certification or production publication is claimed.

## Open questions

- Owner: react to Fable's rendered expense story; record the actual answer in the final MC4 spec without inferring merge approval.
- MC3: deliver update analysis, exact acceptance, authored publication and recovery so the planned receipt-to-document half can become measured.
- MC4: finish all gates/citations/integration and change draft-branch source links to main. Close repairs the component-example literal in the plan using the owner's explicit familiar-demo replacement instruction.
