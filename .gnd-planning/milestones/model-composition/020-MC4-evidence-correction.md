---
milestone: model-composition
station: "MC4 checkpoint evidence correction"
skill: "n/a -- repository development checkpoint, not a gnd-solve station"
scope: MC4-evidence-correction
date: 2026-11-10
gates:
  - command: ".venv/bin/pytest -q tests/test_plan_app_docs.py -k 'shared-expense-policies or shared-component-vocabulary or share-a-vocabulary' --tb=short"
    exit: 0
    output: "14 passed, 72 deselected in 0.07s"
  - command: ".venv/bin/zensical build -f .mc4-draft-zensical.toml"
    exit: 0
    output: "Build finished in 0.51s; No issues found"
  - command: "assert previous rendered HTML bytes equal new build after whitespace cleanup"
    exit: 1
    note: "The equality assumption was false; the later commit incorrectly proceeded before checking this exit."
evidence:
  - path: .gnd-planning/milestones/model-composition/019-MC4-fable-checkpoint.md
    sha256: ef4c3a9a1df4e2ba6a9eabcd1dc3746b9ff69b44caca16ec169370b5ed8a6cf9
  - path: .gnd-planning/milestones/model-composition/evidence/MC4-draft/020-final-manifest.json
    sha256: 2c9b0f493b688671bb34fb92bef9ca1cc938443c0e8b7fa8a8b04d4662a83a73
  - path: .gnd-planning/milestones/model-composition/evidence/MC4-draft/020-binding-correction.json
    sha256: e9075101389ebfe3ff1bb255b2930032f33d0254fa9a5d49c8353b8f4f9097cd
---

# Claim

The final expense page passes its repeated14 prose checks and site build. This successor corrects record019's stale page/render binding; it does not alter runtime/data behavior or manufacture owner acceptance.

## Correction and cause

Removing Fable's expected labels left three trailing spaces. The staged whitespace check caught them before the checkpoint commit, and they were stripped. Prose and build were repeated successfully. A later assertion that rendered HTML must remain byte-identical failed: the spaces changed HTML bytes even though the visual difference is immaterial. The orchestration printed that failure but incorrectly continued to commit/push019 before refreshing its evidence manifest.

The old manifest therefore retains the pre-cleanup page/render hashes. It remains immutable historical evidence. Current source-file checks identify exactly one source mismatch, the expense tutorial page; all other bound source, data, Fable request/response and19-command tutorial artifacts still match. The successor manifest binds the current page, repeated gate outputs, actual new HTML and a newly captured browser view. It supersedes only current-byte attribution in019, not the authorship, measured expense findings or known R30 boundary.

## Gate output (verbatim)

    14 passed, 72 deselected in 0.07s

    Build started
    Build finished in 0.51s
    No issues found

    AssertionError: rendered content changed

## Boundary

No record or prior evidence was rewritten. The final page remains a review checkpoint, the update half remains planned, R30 integration remains owed, and PR155 stays draft/unmerged. No owner reaction, phase completion, merge, certification, publisher or milestone close is inferred. The source delta here is whitespace only; the nineteen supporting command blocks and expense data are unchanged from019's executed observations.

## Open questions

- Obtain the actual owner reaction to Fable's expense story, then finish the update half after MC3 and all final MC4 integration gates.
- Continue MC3 under the already explicit1400/1400 owner ruling; this correction does not consume or change its independent review budget.
