---
milestone: model-composition
station: "Actual main verification and close-review readiness"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: main-verification
date: 2026-11-10
gates:
  - command: 'GitHub SHA-guarded merge PR157c6dad88d then PR155396f86f3'
    exit: 0
    result: 'merged ed091709 then a9b67d8b, explicit current owner authorization'
  - command: 'compare actual main tracked tree and all nonplanning paths/modes to measured1ca2379f'
    exit: 0
    result: 'main tree equals MC4;4698paths;exactly four test guards and one skill prose follow-up remain'
  - command: 'PYTHONPATH=MAIN_ARCHIVE/src GIT_DIR=REPO/.git python -m pytest -q tests/test_mc1_model_includes.py tests/test_mc3_evolution.py tests/test_mc4_expense.py --tb=short'
    exit: 0
    result: '229 passed in 23.49s'
  - command: 'ruling: delegated (auto=true) approve append-only plan actual-merge amendment, sha256 7a6925ff75b082f05718f511a23789c0d70e9a37e9bcb67c4f9cbd5d2208655a'
    exit: 'n/a -- main verification and review readiness only'
evidence:
  - path: .gnd-planning/milestones/model-composition/evidence/close/main/manifest.json
    sha256: a0bcf1f662931df6a85f9abfd74dc6d7a147a5dc9f7030132c5da4d22698079a
  - path: .gnd-planning/milestones/model-composition/notes/model-composition-plan.md
    sha256: 7a6925ff75b082f05718f511a23789c0d70e9a37e9bcb67c4f9cbd5d2208655a
---

# Claim

The owner explicitly approved MC3#157c6dad88d then MC4#155396f86f3 and requested main verification and Codex CLI close review. Exact live heads, empty review lists/threads and mergeability were checked; SHA-guarded merges completed in order: ed091709dcccc92e6316684b62e4a00c3998315a then a9b67d8b3a507dffd219c146c7cb4d5953100a0c. Fetched actual main's complete tree equals the MC4 approved head. All4698nonplanning tracked paths/modes were compared with final measured1ca2379f. Exactly five differ: four compatibility/metadata test guards and one offline model-evolve skill prose repair already gated by027/028. Runtime Python, schemas, examples, commands, docs, configuration and goldens are identical. These pending follow-ups belong to PR158; its base is nowmain.

## Actual main smoke and setup correction

The initial archive invocation resolved gnd through the editable installation and lacked Git history;1failed/228passed in19.45s is INVALID for a main claim. The exact frozen-runtime assertion failed with Git128, not a product mismatch. The corrected invocation explicitly sets PYTHONPATH to the isolated main archive/src, verifies gnd.__file__ there, and supplies the original Git object store only for the selected historical git-show assertion. The three selected modules contain no Git mutations. It exits0:229 passed in23.49s on existing Python3.11.15. This is fresh focused main runtime evidence; it does not relabel the beast-3 Python3.11.18 candidate full/default or census as main outcomes.

## Delegated amendment and review readiness

Delegated approval (auto=true),2026-11-10, authority original named milestone delegation and current continue request, accepts exact appended plan §18 after implementability/impact sweep. Original bytes and all earlier records remain preserved. No product/source/test edit arises from this verification. The current question sweep and review bundle distinguish four local completed phases, actual main runtime predicates, and candidate follow-ups. Original specs/corpora,008/013/023/025,027–029and actual-main manifest supply review inputs.

Separate close budget from026 remains maximum2 CLI calls: one first opinion plus at most one narrowly scoped confirmation. Selected instrument one Codex CLI reviewer, existing authentication, read-only, prompt on stdin; no panel/subagent/env-file read. No call has yet been made. Phase review opinions do not cover close repairs. Current reference/frontmatter checks are owed before invoking review and again after final record authoring.

## Boundary and remaining gates

No new broad/native/external suite, certification, publisher or successor is selected. The final full comparison remains1ca2379f:18795passes plus exactly six baseline failures, exit1;13baseline lint findings remain. Four test repairs and offline skill prose still await PR158's separate fixed-head owner merge authority. The independent close opinion, final delegated close ruling, final main tree equality and issue95closure remain pending. Existing157/155approval does not authorize158. Local readiness never fabricates completion on main.

## Refactoring review

None needed: this work observes Git tree identities and executes existing focused tests; no runtime module or query/dispatch path changes. The actual existing structure still supplies one composition loader and authored-only writers. Delivered hook/index contradiction remains a repository-owner maintenance residual in the current sweep.

Current-context reference/twins check exits0:2 passed in0.32s; frontmatter validates118citations, retaining001’s two original path-only entries. Setup-probe limitations are retained in metadata-setup.txt; none are called passing gates. These outputs are bound by the main manifest.
