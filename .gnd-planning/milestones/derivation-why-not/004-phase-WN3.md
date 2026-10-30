---
milestone: derivation-why-not
station: phase-WN3
skill: "n/a -- repository development via process-phase under process-milestone auto=true, not a gnd-solve station over a domain model"
scope: phase-WN3
date: 2026-10-30
gate:
  command: "uv run pytest -q -p no:cacheprovider <the WN2 gate files> tests/test_why_not_repair_loop.py tests/test_il6_skill_census.py tests/test_packaged_skills.py tests/test_public_workflow_claim_routes.py tests/test_verification_fixes.py tests/test_skill_prose_sync.py"
  exit: 0
  output: "2465 passed, 33 deselected in 337.64s (0:05:37)"
  note: >-
    The gate ran over the tree before the review fixes. The files those fixes
    touch were rerun over the final bytes: 171 passed, and the why-not tutorial
    group passed 7 blocks. The docs site built with zensical build --strict.
    tools/check_docs.py reported one error, an unrendered fence in
    reference/ilp-bridge, a page unchanged since the milestone base. The IK6
    skill census credits uncommitted skill edits to IK-close, so it was run
    after the commit (see below).
slow_cadence:
  command: "uv run python tools/check_installed_docs.py; uv run pytest -q"
  trigger: "explicit owner selection"
  reason: "the installed-docs check builds wheels and venvs; the broad suite is owner-selected"
evidence:
  - path: .gnd-planning/milestones/derivation-why-not/notes/phase-WN3-spec.md
    sha256: 72cad59fcfc1cd9043c76c049606787cef40a58e33230418ab40a8ce29c4d087
  - path: .gnd-planning/milestones/derivation-why-not/notes/phase-WN3-claude-review.md
    sha256: cfaf6dc95336b1d638aeafb149e8bff00db4134747d6e966fc68d628ca696c72
  - path: .gnd-planning/milestones/derivation-why-not/evidence/WN3/build_example.py
    sha256: 15aa7510817db88d306eaa1a6c104a83afe8d9460e360ff5c2173d42210f0d13
  - path: .gnd-planning/milestones/derivation-why-not/evidence/WN3/final-gate.txt
    sha256: d79f150c40a6599e0c2d5e1eab8207e7f6fd8855ed6a9e5c41dc7dc8c377561b
  - path: src/gnd/examples/quoted_claims/model.orm.json
    sha256: bdb0c0f7235e1d6771af4657d341f7a45216f228b72658aec81a44e18cfd7432
  - path: src/gnd/examples/quoted_claims/gap.pop.json
    sha256: fa584181acc9f0be6f48b2d06abf17710fa8186a0c82e8a531b1bec4364ae602
  - path: src/gnd/examples/quoted_claims/claim.json
    sha256: f954610ad3d5ef5178686db6fd5d871fc9f60de38a2baeebfbcdec5592a2dd99
  - path: src/gnd/examples/quoted_claims/extracted.json
    sha256: 51d37910711408549a2869bb2c3a92d7bdb5a44f6e420fa7f479fa2676e3a581
  - path: tests/test_why_not_repair_loop.py
    sha256: 1ea8e2fa73d21174720975383130ec915ad7e97d567f919215c5da6ee81546e2
  - path: docs/how-to/repair-a-missing-claim.md
    sha256: 2d80959882a58588fc8ea316f20be9b21140e95ca40c6f245b176c883c23eb53
  - path: src/gnd/skills/gnd-export/SKILL.md
    sha256: abe960d5d2a6924a7e711ce80215b1d7238997aec70b3fb9a51f18e4f53bade4
---

# Phase WN3 -- the repair loop, end to end

Spec: [phase-WN3-spec.md](notes/phase-WN3-spec.md), r1, with a **delegated
approval (auto=true)** under the owner's `/process-milestone derivation-why-not
auto` request (SHA-256 `df9e3342…3ede5`, sweep S1-S3).

## What shipped

- **`src/gnd/examples/quoted_claims/`**: a certified-answer model.
  `certified(q, p)` derives from `quote(q, w)`, `authored(w, p)` and
  `reviewed(w, r)`. The population has the quotes only, so two base facts are
  missing. The example adds `claim.json` (the claimed row), `extracted.json`
  (the reviewer a source names) and a README. It joins the example domains in
  `tools/check_installed_docs.py` and its unit test.
- **`tests/test_why_not_repair_loop.py`**: before repair, `check` passes and
  `witness` says `missing`. Why-not names `(atom, 1, authored)`, and the fact
  is built from the payload alone. Then it names `(atom, 2, reviewed)` with
  `reviewer` free, filled from the extracted table. Then the row is `derived`,
  `witness` proves it and `replay` replays it. Asserting the derived row
  restores a passing `check`. Two negative controls leave the blocker
  unchanged: the values on the previous predicate, and a wrong bound value.
- **`docs/how-to/repair-a-missing-claim.md`**: seven asserted `gnd-run` blocks,
  a `why-not` tutorial group, and a How-to nav entry.
- **`gnd-export` skill**: one route sentence after the witness step.

## Criteria

| Criterion | Result |
|---|---|
| WN3-C1 example | holds: it validates, ships under `src/gnd/examples/`, and is in the installed-docs example list (the wheel build itself is `slow_cadence`) |
| WN3-C2 loop | holds: every clause of C2, including both negative controls and the witness step; the review traced the controls against broken kernels |
| WN3-C3 how-to | holds: 7 blocks pass; the docs site builds strictly |
| WN3-C4 skill route | holds: one sentence in `gnd-export`; `gnd-dev-session` unchanged; skill sync and packaged tests pass |

## Review

One local reviewer agent read the working-tree diff. Its report is kept as
[phase-WN3-claude-review.md](notes/phase-WN3-claude-review.md). It found no
blocking defect.

| Finding | Severity | Disposition |
|---|---|---|
| WN3-R1 the how-to's "`gnd check` passes" is not run | completeness | fixed: an asserted `gnd check` block |
| WN3-R2 the repaired population fails `check` | hardening | fixed: the how-to and README say why, a block asserts the row and shows `check` passing, and the loop test pins both exits. This pins existing behaviour; no code changed, so no red-first regression applies |
| WN3-R3 the skill sentence can pass a multi-target request | hardening | fixed: it now asks for a one-target request and passes `--reference-root` |

## Refactoring review

Nothing to refactor: the phase adds data, one test, one page and one
sentence. `build_example.py` keeps the example reproducible; the README is
hand-written.

## Boundary -- what this phase does NOT establish

- **One reviewer is one reviewer.** The review covered the pre-fix tree.
- **The installed-docs check did not run.** It builds wheels and venvs; only
  its unit test, which fakes a wheel, ran.
- **The loop uses one synthetic example.** It shows that the payload is
  sufficient here, not for every rule shape. Rules whose blocker has free roles
  need a value from outside the payload, as `reviewer` did.
- **A pre-existing docs defect remains:** `tools/check_docs.py` reports an
  unrendered fence in `reference/ilp-bridge`, a page this milestone did not
  change.

## Open questions

| ID | Question | Origin | Target |
|---|---|---|---|
| WN3-Q1 | The unrendered fence in `docs/reference/ilp-bridge.md` | this phase's link check | its own fix, outside this milestone |
