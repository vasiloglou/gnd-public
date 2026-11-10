---
milestone: model-composition
station: "MC4-draft owner-feedback revision"
skill: "n/a -- repository development checkpoint, not a gnd-solve station"
scope: MC4-draft-revision
date: 2026-11-10
gates:
  - command: ".venv/bin/python .gnd-planning/milestones/model-composition/evidence/MC4-draft/run.py /tmp/mc4-revised-receipt-final.json"
    exit: 0
    output: "11 tutorial blocks passed"
  - command: ".venv/bin/pytest -q tests/test_plan_app_docs.py -k 'share-a-vocabulary or shared-component-vocabulary' --tb=short"
    exit: 0
    output: "7 passed, 72 deselected in 0.08s"
  - command: ".venv/bin/zensical build -f .mc4-draft-zensical.toml"
    exit: 0
    output: "Build finished in 0.53s; No issues found"
  - command: ".venv/bin/pytest -q tests/test_mc1_guards.py::test_R30_examples_do_not_declare_includes --tb=short"
    exit: 1
    output: "1 failed in 0.14s"
    note: "Retained temporary blanket-guard integration failure; this checkpoint remains draft and unmerged."
  - command: "python3 scripts/components_index.py --no-cache changed --base origin/main --strict"
    exit: 0
    note: "0 to fix,0 warnings,0 rereads; no runtime component changed."
  - command: "git diff --check"
    exit: 0
evidence:
  - path: .gnd-planning/milestones/model-composition/011-MC4-draft.md
    sha256: 382bd71ad20dae8b5e9535e99b09ea9f58006132d91f08f955d1160de584888f
  - path: .gnd-planning/milestones/model-composition/notes/phase-MC4-spec.md
    sha256: ef566a7a4df1940c026b501cb128064dd0577df133857a35c19d4ff7346cba2e
  - path: .gnd-planning/milestones/model-composition/evidence/MC4-draft/owner-reaction.json
    sha256: aad136fc1b86aaa355b4f3908f5f37d8b3c8fef65acca669819a6e78b8f6b735
  - path: .gnd-planning/milestones/model-composition/evidence/MC4-draft/revision-manifest.json
    sha256: 82b64f5b619d56a3697aca6ae273f3da0133a7aaedc21e0ef9755b88b8f26d37
---

# Claim

The revised documentation checkpoint's eleven command blocks exit as narrated and compare their displayed output. Seven focused prose checks exit0, and the rendered copy builds without issues. The original owner's actual reaction is recorded verbatim; reaction to this new business-level page remains pending.

## Owner reaction and disposition

The owner answered the first PR155 how-to checkpoint:

> I want it more higher level like the rest of the documentation with a real example, maybe you can borrrow an exisiting or expand it to demonstrate the value of the functionality you implemented

This is feedback, not merge or byte approval. Delegated ruling (auto=true),2026-11-10, selects the higher-level business page in MD17(a) and its owner reaction round; the driving Codex agent authors it instead of the open proposal's Fable authorship. No extra reviewer or author agent is selected. The draft final MC4 spec records this actual reply and separates this already-authorized checkpoint from the final phase, whose spec gate still follows MC3.

## What changed

The main page expands the existing rule_check example's twelve-component catalog into two projects sharing identical vocabulary bytes. Checkout owns its original blocking no-import-loops rule. Platform owns its original advisory ownership rule. The diagram, results table, plain requests, findings and author-supplied remedies show what each team gets. Two loops disappear in checkout's repaired facts; platform's metrics ownership warning disappears after adding its owner. A warning is not falsely presented as a blocking failure.

The supporting how-to holds the project files, validation and before/after command output. Eleven blocks run through the unchanged tutorial runner. Separate JSON observations independently check the narrated exit/count branches and unchanged vocabulary hash512e10fb. Model files contain no copied vocabulary object/fact definitions. The new files run on this docs branch's merged MC1 source; they do not depend on the unmerged MC2 implementation. The earlier small example and record011 remain retained; the new pages use the expanded checkout/platform data.

The first prose selection found two missing Files on GitHub boxes (2 failed,5 passed). Adding the required source links made all7 selected checks pass. Links point to the existing draft branch until final integration; MC4 must change them to main at integration. R30's blanket no-include example scan still exits1, as first observed in011. Final MC4 owes its exact rooted successor and retained legacy controls before this PR can merge.

## Gate output (verbatim)

    share-a-vocabulary.md: selected executable blocks passed
    11 tutorial blocks passed

    7 passed, 72 deselected in 0.08s

    Build started
    Build finished in 0.53s
    No issues found

    1 failed in 0.14s

The example-scan failure output is retained in revision-example-scan-red.json, with local paths sanitized. No full default suite or final strict-site/skill suite is claimed. A temporary project-local render config/output was copied to the localhost preview and removed; the retained config captures the exact build inputs. Playwright inspected the generated business page and its complete diagram. Screenshot/HTML hashes are recorded as outside-history artifacts, whose persistence is weaker than the committed source/run evidence.

## Boundary

This is a documentation checkpoint, not completed MC4 or a personal owner reading of the revised page. No independent checkpoint review was selected. The re-pin half remains visibly unfinished until MC3 implements it. The PR remains draft and unmerged because final evolution story, R30 successor, skill citations, nav/release/runner registration and final docs gates remain owed. No production publisher, certification, milestone close or issue closure is authorized or claimed.

## Open questions

- Owner: react to the revised business-level page; record the actual answer in the final MC4 spec without inferring merge or byte approval.
- MC3: deliver the pinned vocabulary update, named broken-rule analysis and valid combined publication needed to finish this example.
- MC4: finish all named plan criteria, integrate exact R30 successor, change draft GitHub links to main, and run its complete selected checks after the final spec gate.
- Close: retain both owner reactions, the checkpoint integration refusal and the actual final main-branch predicates.
