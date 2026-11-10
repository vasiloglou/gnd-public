---
milestone: model-composition
station: "Close retained-draft metadata repair"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: close-metadata-repair
date: 2026-11-10
gates:
  - command: 'python -m pytest -q tests/test_development_scaffold.py::test_reference_closure_and_declared_bootstrap tests/test_development_scaffold.py::test_twins_modes_and_generated_links --tb=short'
    exit: 1
    result: 'isolated original tracked archive:1failed/1passed, retained Fable draft relative SVG link missing'
  - command: ".venv/bin/pytest -q tests/test_development_scaffold.py -k 'retained_document_origin or retained_external_reference' --tb=short"
    exit: 0
    result: '70 passed, 15 deselected in 0.23s'
  - command: 'python -m pytest -q tests/test_development_scaffold.py::test_reference_closure_and_declared_bootstrap tests/test_development_scaffold.py::test_twins_modes_and_generated_links --tb=short'
    exit: 0
    result: 'isolated tracked archive plus exact source repair:2 passed in 0.33s'
  - command: 'uv run ruff check src tests --output-format json'
    exit: 1
    result: 'same13 inherited findings; existing five-line checkpoint offset only'
  - command: 'ruling: delegated (auto=true) approve appended plan section14 sha256 ca8305a419f053cdba77a2cb7bcb3a1fc139d4e6db6f8bc4205f7afb567e46d7'
    exit: 'n/a -- bounded amendment, not milestone acceptance'
evidence:
  - path: .gnd-planning/milestones/model-composition/evidence/close/metadata-repair-manifest.json
    sha256: a598e2d0cc6fed5f7466a59eb53ec8a992699bebcf56168c57508c7b81131d65
  - path: .gnd-planning/milestones/model-composition/notes/model-composition-plan.md
    sha256: ca8305a419f053cdba77a2cb7bcb3a1fc139d4e6db6f8bc4205f7afb567e46d7
---

# Claim

A real close metadata gap was reproduced in an isolated tracked8efd3409 archive before repair: Fable's immutable draft links needed its original document home. The existing exact origin mapping now binds that draft's SHA and intended home; one exact draft-only historical placeholder exception avoids pretending its proposed page shipped. Real links remain checked. Existing none/changed-snapshot/missing-target controls cover the new origin entry and pass; no runtime, schema, model, population or command block changed.

## Gate and findings

Delegated approval (auto=true),2026-11-10, authority named milestone delegation, bound the prose metadata gate before these edits. All original records/opinions remain preserved. The first live-workspace check failed on an unrelated untracked nested worktree and is not a product reproduction. Isolated original tracked archive reproduced the retained-draft gap. After the six-line table adaptation, focused origin/external controls70pass and isolated reference/twins2pass. The initial first-entry insertion broke the existing synthetic external-reference fixture; moving the new exception to the end preserves that prior order, with its original control passing. Both attempts are retained, not silently discarded.

MC4-attributable Python support is now120lines exactly, including its36 historical wrapper lines; no further growth allowed without a new owner size decision. The same13 lint findings remain, with no new location shift. Production Python0; source/examples/commands remain otherwise byte-identical to6de7189a. This new test metadata repair has no phase-review opinion; the separate close reviewer must inspect it within the already declared close budget.

## Invalidated full run and next candidate

The old full default run at6de7189a was deliberately stopped at an incomplete progress state after this required correction was discovered. Only the exact remote wrapper/descendant process tree was terminated; no unrelated job was selected. The SSH session returned255, not a completed pytest verdict; its partial log is retained and cannot support full-suite acceptance. Do not infer a final failure set or count from progress dots. Earlier completed census2pass and phase results stay bound to their own source.

Restart the already owner-authorized named candidate default/census at the corrected concrete source once focused controls pass. Frozen baseline failure IDs remain fixed before the new outcome; exactly six must remain, with no added or removed failures. This record supplies no merge, current main, independent close opinion, milestone-close acceptance, issue95 closure, certification or publication. PR157/PR155 fixed-head owner merge requests remain pending; PR158 stays draft.

The complete isolated metadata module also exited0:84 passed,1 configured deselection in14.37s. Current milestone frontmatter parsed without defects after the new record. These are metadata controls, not a full-suite or excluded-lane result.

Delegated artifact-retention ruling: preserve the failed first-insertion control log's literal trailing-space E-line12 as an explicit historical-output residual. Its digest remains unchanged. Source whitespace check exits0; staged checking must identify exactly this one new artifact line, not claim unrestricted whitespace clean.
