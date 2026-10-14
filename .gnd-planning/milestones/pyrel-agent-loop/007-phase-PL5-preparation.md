---
milestone: pyrel-agent-loop
station: phase-PL5-preparation
skill: process-phase
scope: phase-PL5-preparation
date: 2026-10-14
source_base: 1495ba2f61eb5f8524b35589b14dc5cd07707b21
status: preparation-complete-review-pending
gate:
  command: ".venv/bin/python -m pytest -q -p no:cacheprovider tests/test_pyrel_learning_path.py tests/test_tutorial_output_blocks.py tests/test_pyrel_tutorial_experience.py tests/test_documentation_tutorials.py tests/test_pyrel_applications_install.py tests/test_recording_tools.py tests/test_pyrel_recordings.py tests/test_pyrel_stand_in_sessions.py"
  exit: 0
  output: "201 passed, 4 deselected in 61.38s (0:01:01)"
slow_cadence:
  command: uv run pytest -q
  trigger: explicit owner request or separately selected CI
  reason: prior run is classified below; repaired docs use focused current-byte gates
evidence:
  - path: .gnd-planning/milestones/pyrel-agent-loop/notes/phase-PL5-spec.md
    sha256: 6849374ac2befaa195e3ed18a2101103f41d317ca16b818068a897fd9fa23d83
  - path: .gnd-planning/milestones/pyrel-agent-loop/notes/phase-PL6-spec.md
    sha256: 9b43c1c858b40c95c0f78b1c469babaf8c1df70162390c8e8c5965a919811476
  - path: .gnd-planning/milestones/pyrel-agent-loop/evidence/PL5/resume-source-identity.json
    sha256: 41c35fba179509d0e47cba3608f39105aacc9748f848a4ada8c734ffd96f40ba
  - path: .gnd-planning/milestones/pyrel-agent-loop/evidence/PL5/resume-candidate-classification.txt
    sha256: 9080f98a23415988a3d35f2f71db5320c3f8575e6dcb6dfc48df45bf6b7a55ed
  - path: .gnd-planning/milestones/pyrel-agent-loop/evidence/PL5/resume-clean-checkout.txt
    sha256: 3730d6eadf73a72726567ad670e1dc647fee8e46ec44ce0222a88e5d43e59476
  - path: .gnd-planning/milestones/pyrel-agent-loop/evidence/PL5/resume-excerpts-green.txt
    sha256: 5c4d1886a9995b2db881f19b17dcb62562b3e931b8e440ae2020038b26ed1830
  - path: .gnd-planning/milestones/pyrel-agent-loop/evidence/PL5/resume-excerpts-red.txt
    sha256: 2fa41ddb996d772bf9cd1fbde283ceec964e6a42879dde85e10b2ba1cddb568c
  - path: .gnd-planning/milestones/pyrel-agent-loop/evidence/PL5/resume-focused.txt
    sha256: e80d732c0c10393d4d4e2a8c4601c14acf2eca392ac5374bdf39cf9ed594ce27
  - path: .gnd-planning/milestones/pyrel-agent-loop/evidence/PL5/resume-main-classification.txt
    sha256: c53ac13837fd498fa5f7f898d0ef5bfd1d9451308f845adc2947dbecf01ad36f
  - path: .gnd-planning/milestones/pyrel-agent-loop/evidence/PL5/resume-prior-full-suite.txt
    sha256: 5115fdd1b5c7f9bd2fbade53e1437fe514b023b62c8bcf6d23c1a06b3cee9493
  - path: .gnd-planning/milestones/pyrel-agent-loop/evidence/PL5/resume-site-build.txt
    sha256: de311ecdbe3c014be964489437542b93103fe4c660113beab39d9ed1c4de3a80
---
# PL5 preparation resumed; independent review remains pending

Resumed Claude session fd814110-b392-4c16-8294-2db75ff438c9 on the existing
codex/pyrel-agent-loop branch, under 001's recorded phase delegation. The user
requested continuation in Codex. This is a preparation checkpoint, not a phase
completion or milestone close.

## What shipped

- The overview and BookRec/Expense chapters show rule provenance, verbalization,
  ORM and equivalent hand-written PyRel; runnable assistant feedback loops;
  prompts for the packaged skills; model evolution; readable app commands.
  Agent-section pointers and navigation titles lead to the new material.
- The Expense meal-cap helper creates a digest-bound evolution proposal. Its
  tutorial drives preview/apply and observes the changed rule's refusal.
- On resume, task, candidate and feedback excerpts gained byte checks. Historical
  recording bytes/manifests were preserved. Task hashes are pinned in page code
  because those files were absent from the original session manifest.
- Assistant messages print in full; shortened commands carry a visible ellipsis.
- BookRec's coverage wording now says the floor counts all recommendations,
  including Ben's. Both chapters distinguish generic session acceptance from
  task-specific completion and preservation of input facts.
- Expense reports on the actual accepted stand-in candidate through PyRel,
  instead of only using a separately reconstructed snapshot.
- Block counts remain BookRec 71 total / 10 native and Expense 57 / 11. The
  install harness and its controls carry these measured pins.

## Gate output (verbatim)

Focused command in frontmatter: exit 0.

    201 passed, 4 deselected in 61.38s (0:01:01)

Excerpt tamper controls, before repair:

    .venv/bin/python -m pytest -q -p no:cacheprovider tests/test_pyrel_learning_path.py -k recorded_excerpt
    6 failed, 2 passed, 28 deselected in 1.67s

After repair (prose and output controls):

    .venv/bin/python -m pytest -q -p no:cacheprovider tests/test_pyrel_learning_path.py tests/test_tutorial_output_blocks.py
    47 passed in 0.32s

Lint command:

    .venv/bin/ruff check tests/test_pyrel_learning_path.py tests/test_pyrel_applications_install.py tests/test_rf7_structure.py src/gnd/examples/expense/prepare_meal_cap.py tools/accept_pyrel_applications_install.py
    All checks passed!

Site commands, both exit 0:

    .venv/bin/zensical build --strict
    Build finished in 0.44s
    .venv/bin/python tools/check_docs.py site
    8284 local links/assets/anchors checked

Clean candidate worktree controls (development scaffold, install controls and
RF7): exit 1 solely for the inherited RF7 failure.

    1 failed, 40 passed, 1 deselected in 11.73s

The same failed node occurs on main. The clean candidate's reference-closure
check passes; the root checkout fails it because it descends into an old nested
Claude worktree. No stale-worktree files or reference-check policy were edited.

## Verification selection and inherited evidence

Run: focused test command, eight executable tamper controls, lint, strict site,
links, and actual installed tutorial paths. Inputs and changed file hashes are
in resume-source-identity.json; changed page/runtime bytes invalidate these
claims. Native installed acceptance is recorded separately when complete.

Inherit with limits: the previous session's full default run reported
8 failed, 14643 passed, 521 deselected, 1 warning. Its wrapper returned zero and
lost pytest's exit code; no successful broad result is claimed. The eight failed
nodes were rerun on clean main a9a2f08: seven refactoring failures and reference
closure passing. On the clean candidate the same seven failures reproduce;
reference closure passes. The eighth failure in the original checkout is local
nested-worktree contamination. Evidence logs retain all failed node names.

Cadence: full/broad historical lanes require explicit owner or selected CI;
no further broad replay was launched during this continuation.

## Rendered reading

Fresh screenshots at 1440x1000 and 390x1000, light and dark, cover each chapter's
recorded-session region. Author inspected rendered views: prose fits, headings
and colors are readable, code blocks scroll horizontally without widening the
page. These are author checks, not independent reader evidence. Earlier-session
screenshots of the rule/diagram/refusal regions are retained as historical views.

## Review and convergence

The original PL5 Claude reviewer failed at the session limit and returned no
opinion. A Codex CLI attempt with its configured gpt-6.1-sol default failed
before review because that model was unsupported by the installed CLI account.
Automatic approval review then rejected gpt-6-sol because the command would send
unpublished repository contents to an external reviewer. Explicit authorization
was requested; it has not been received. No successful independent review ran.
One reviewer is one reviewer; author self-checks are not a substitute. No second
review round or four-reader close panel is claimed.

## Refactoring review

None needed in the resumed implementation: the byte checks follow the existing
recording-manifest layout, the model-change helper uses EvolutionProposal and
canonical_sha256, and no core algorithm or normative skill was duplicated.
A reusable recording-display helper could reduce page plumbing but is deferred
as completeness work to GND maintainers' tutorial-maintenance backlog, preserving
this phase's runnable blocks and recording authenticity controls.

## Boundary

Local preparation and measured checks only. PL5 awaits independent review; PL6
and milestone close remain incomplete. Claude Code was not recorded: completion
predicate 4's literal Claude requirement remains unmet, despite the eight real
Codex recordings. Seven main-inherited refactoring failures remain open to their
existing follow-up. The primary-three-page readability tests do not establish
all old prose on every linked agents page satisfies the same style constraints.
No merge, release, site publication, certification or new live recording occurred.

## Open questions

| ID | Question | Owner / target |
|---|---|---|
| PL5-Q1 | Authorize and complete the independent phase review | owner; explicit gpt-6-sol payload/destination permission pending |
| PL6-Q1 | Four-reader close review including PL4 recorder/wrapper | close-review instrument after PL5 review |
| PL4-Q1 | Record Claude Code or explicitly accept Codex-only scope | owner; 005 live-recording gate remains separate |
| PL6-Q2 | Seven main-inherited failures | GND maintainers; existing refactoring follow-up |
| PL5-Q2 | Readability gate scope on agents pages and inherited long paragraphs | independent PL5 review / tutorial maintenance; no whole-page style compliance claim |

## Refuted premises

- An accepted session with a floor of two recommendations proves two for Ada:
  false; the generic floor counts Ben too. Corrected in the page itself.
- Every displayed artifact was verified: false before repair; six tamper cases
  failed before the byte checks and pass after them.
- The prior full-suite wrapper's exit zero meant pytest passed: false; eight
  failures are retained and classified against main.
