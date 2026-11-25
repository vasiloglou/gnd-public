---
milestone: release-0.5.0
station: "phase-RW3"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-RW3
date: 2026-11-25
implementation_commit: 115ae4c10899bd601f326ca34663518ccf6e18b2
candidate_commit: 85d076ba384e67b1f992cfd6b9a596ca01b3d4e7
gates:
  - command: "ruling: owner merged pull request 284 (the RW2 record) on the words 'Merge 284', 2026-11-25; main 44d866df"
    exit: "n/a -- ruling"
  - command: "ruling: delegated (auto=true) approved .gnd-planning/milestones/release-0.5.0/notes/phase-RW3-spec.md sha256 54200c91a402300ebf6df0305ef4271204c70149d12fa49fbd7c44992e7551ea"
    exit: "n/a -- ruling"
    output: "spec r1 approved for implementation (commit 5163686e); D3 and D5 left to the owner at publication; no act of publication covered"
  - command: "ruling: delegated (auto=true) amended .gnd-planning/milestones/release-0.5.0/notes/phase-RW3-spec.md sha256 8bb36bc1c12cf04703a7248350126f172ad09f303e4a7e8dbef313cb3e18f564"
    exit: "n/a -- ruling"
    output: "M2 (c), the paragraph pass, withdrawn; the review search stopped after round 2 as declared"
  - command: "uv run pytest -q tests/test_release_text.py tests/test_release_docs.py tests/test_release_preparation.py tests/test_release_version.py --tb=short -p no:cacheprovider"
    exit: 0
    output: "98 passed, 1 deselected in 0.44s"
  - command: "uv run python tools/release_text.py check"
    exit: 0
    output: "0.5.0 is not in RELEASED: nothing to check before publication"
  - command: "bash rehearse-publication.sh CLONE post-publication-supplement.patch 115ae4c10899bd601f326ca34663518ccf6e18b2 (a disposable clone of the RW3 commit)"
    exit: 0
    output: "tool-only publish exit 1 with seven lines; the patch applies; check exit 0; split-phrase search 0 blocks; 98 passed; strict docs build and site link check exit 0"
    note: "T4. Rehearsal date 2026-11-25; nothing uploaded, tagged or released"
  - command: "the project.md structure and inventory guard block (16 files)"
    exit: 1
    output: "1 failed, 865 passed, 2 deselected in 121.32s (0:02:01)"
    note: "the one failure, tests/test_development_scaffold.py::test_reference_closure_and_declared_bootstrap, comes from an untracked skill mirror in this checkout; it passes in a clean clone (RW1 and RW2 lanes)"
  - command: "uv run ruff check"
    exit: 0
    output: "All checks passed!"
  - command: "python3 scripts/components_index.py changed --base origin/main --strict"
    exit: 0
    output: "changed against origin/main (44d866d): 53 file(s) differ; 0 to fix, 0 warning(s), 0 to reread"
    note: "after `components_index.py write` regenerated dev/components/modules/tools.md"
  - command: "uv run --group docs zensical build --strict"
    exit: 0
    output: "No issues found"
  - command: "uv run python tools/check_docs.py site"
    exit: 0
    output: "19539 local links/assets/anchors checked"
  - command: "git diff --stat 85d076ba HEAD -- src PYPI.md pyproject.toml LICENSE NOTICE"
    exit: 0
    output: "(empty)"
    note: "T6: the candidate is not stale"
  - command: "python3 .claude/skills/process-phase/scripts/review_tool.py run .gnd-planning/milestones/release-0.5.0/notes/reviews/phase-RW3-r1 --wait"
    exit: 0
    output: "codex, effort high, read-only: 5 findings, VERDICT: CHANGES_REQUESTED"
  - command: "python3 .claude/skills/process-phase/scripts/review_tool.py run .gnd-planning/milestones/release-0.5.0/notes/reviews/phase-RW3-r2 --wait"
    exit: 0
    output: "codex, effort high, read-only: 4 findings, VERDICT: CHANGES_REQUESTED"
slow_cadence:
  command: "uv run pytest -q -m \"evidence or census\""
  trigger: "not run"
  reason: "not selected. The full default lane is the close's; no opt-in lane ran in this phase"
evidence:
  - path: .gnd-planning/milestones/release-0.5.0/notes/phase-RW3-spec.md
    sha256: 8bb36bc1c12cf04703a7248350126f172ad09f303e4a7e8dbef313cb3e18f564
  - path: .gnd-planning/milestones/release-0.5.0/evidence/RW3/dossier.md
    sha256: 392b1ca8d38ad5bab93de662ced06d2e67c3521f0603c7efb94c1d63ee1f56c4
  - path: .gnd-planning/milestones/release-0.5.0/evidence/RW3/github-release-notes.md
    sha256: e75450c9e0555894c98823415a5224aaaa6f0f0c110a9599fba19dc8b63046b6
  - path: .gnd-planning/milestones/release-0.5.0/evidence/RW3/pre-publication-state.txt
    sha256: 2b6b2a3a24df87bfd511426f36dd97bdde247128273a54a6667c90e176e6f393
  - path: .gnd-planning/milestones/release-0.5.0/evidence/RW3/rehearse-publication.sh
    sha256: f225c9c8172395324580e4f32f7b293c2005c31c945229b086c8de0695bd5022
  - path: .gnd-planning/milestones/release-0.5.0/evidence/RW3/split-phrase-search.py
    sha256: a02ce17febf56a839bea32e5dcd1b9775adc64c40103c7b4da431e765039dd84
  - path: .gnd-planning/milestones/release-0.5.0/evidence/RW3/tool-only-preview.txt
    sha256: d9d5702a02cf6e56d9268771343473acc40779d45f63bcbab5895487d241b456
  - path: .gnd-planning/milestones/release-0.5.0/evidence/RW3/post-publication-supplement.patch
    sha256: e9a7b4ded7207d412737d5da394053e995754687c82fd39ebe6948aceea920c2
  - path: .gnd-planning/milestones/release-0.5.0/evidence/RW3/scratch-verification.txt
    sha256: a4ef5789dca16293442e8b49797f05e527a3a90ebf2012622f85dce4dcca05a0
  - path: .gnd-planning/milestones/release-0.5.0/notes/reviews/phase-RW3-r1/review.md
    sha256: afe0387e1cae3c2a30e4203feee68a5e4139bc36d07d112654c6a03ec1b273f6
    note: "sanitized; run.json binds the original"
  - path: .gnd-planning/milestones/release-0.5.0/notes/reviews/phase-RW3-r1/run.json
    sha256: fa47b3589801df57eb717dc8f23cf0bdc53123b4b1f66d1a7bd9c3afed0efeb9
  - path: .gnd-planning/milestones/release-0.5.0/notes/reviews/phase-RW3-r1/FINDINGS.md
    sha256: 84780394706db284184687780b913334543026ff82d52d94759386b96e3ea4b2
  - path: .gnd-planning/milestones/release-0.5.0/notes/reviews/phase-RW3-r2/review.md
    sha256: 1bcfe5e4d808664d5914cc9ffcabd93d48108553b531bac5b728ef5cbb594769
    note: "sanitized; run.json binds the original"
  - path: .gnd-planning/milestones/release-0.5.0/notes/reviews/phase-RW3-r2/run.json
    sha256: accd9ee720ba16f459ba7187e581bd47b901a1409f3e140252b1c3de6e0527c4
  - path: .gnd-planning/milestones/release-0.5.0/notes/reviews/phase-RW3-r2/FINDINGS.md
    sha256: e669adce821b2f66025f3ef158ce60a9aafbfa2f0d3ce75ac3efdcbfc073cc6d
  - path: tools/release_text.py
    sha256: d0cf03fa3ea0696ec5d0d037c66f7f5774bdda922435c380b0a306c2fdfbc200
  - path: tests/test_release_text.py
    sha256: d5bd835b68610ad2f55377afa5664877dd53f7d927d725b4758ce865bf3fbf3e
  - path: docs/releasing.md
    sha256: f89ce81a98c984200f2fada0aa04ab0d338915e8ec00890e7e715f25df35075c
---

# Claim

At `115ae4c1` the four release test files exited 0 with 98 passed and
`tools/release_text.py check` exited 0. In a disposable clone of that commit,
`release_text.py publish` for 0.5.0 exited 1 with seven lines left for a
person, the supplemental patch applied, and `check`, the four release test
files, the strict docs build and the site link check then exited 0. The
[dossier](evidence/RW3/dossier.md) names each publication act with its
command and receipt. No act of publication was performed.

## What the phase did

- **The dossier (RW3-C1, C2).** The candidate's identity and results, what
  was not measured, and seven owner acts in the plan's order: the owner's own
  checks and the availability recheck; the upload; the served-file comparison
  and a fresh install; the tag; the GitHub release; the pages pull request;
  the issue comments. Every command block stops at its first failure.
- **The rehearsal (RW3-C3).** The helper changes eight files and leaves seven
  lines on five pages; the [preview](evidence/RW3/tool-only-preview.txt)
  lists them and the
  [supplemental patch](evidence/RW3/post-publication-supplement.patch)
  rewrites them. Five say a feature first shipped in 0.4.0 and become "GND
  0.4.0 and later"; one is the plugin sentence RW1 wrote; one is the
  literature page's "in GND 0.4.0, run for real", where the patch drops the
  version and the dossier leaves the choice to the owner (spec D3).
- **RC-03.** The helper reports two phrases it missed at the 0.4.0
  publication: "not in a published package" (or "any published") and "on
  `main` after" a version. Controls: the receipts note as it stood then, six
  other one-line texts, and standing guidance that must not be reported.
  With the helper as it was on main, all of them failed.
- **RC-06 (RW3-C4).** `docs/releasing.md` names the releases published by
  token upload through 0.4.0. The helper's standing entry for that sentence
  now accepts any list of releases of that form, so the next token release
  edits the page and not the tool; five forms are tested.
- **The remote snapshot (RW3-C5).**
  [pre-publication-state.txt](evidence/RW3/pre-publication-state.txt), taken
  at 17:27 UTC, equals the plan's baseline W4 in every item: five tags with
  the same commits, four GitHub releases, one environment, no `release.yml`
  run, and no 0.5.0 on PyPI.
- **RC-07** is not discharged and cannot be here: the dossier makes the
  owner's account and content checks the first act and says what record they
  need.

Size outside planning: 70 lines added and 5 removed in three files, plus the
regenerated index page for `tools/`.

## Review

One reviewer in a different tool, Codex at effort high, read-only. The
budget was in the spec ruling before round 1: one round, a second only over
a repair, then stop.

| Round | Seats | Per-seat counts | Self-inflicted / total | Blocking / total | Severity ceiling | Verdicts |
|---|---|---|---|---|---|---|
| r1, the RW3 diff | codex | 5 | 0 / 5 | 2 / 5 | not graded by the reviewer | changes requested |
| r2, the repairs | codex | 4 | 3 / 4 | 1 / 4 | not graded by the reviewer | changes requested |

- **Blocking, all in the dossier, all fixed.** r1 F4: the source check ran
  from the retained folder, which is not a repository. r1 F5: the comparison
  block had no failure guard, so a failed comparison would have been
  followed by the install with exit 0. r2 F1: one `&&` line hid a failed
  `mktemp` from the guard. Each was reproduced; every block is now
  `( set -e ... )`, passes `bash -n`, and a guarded block with a failing
  stage was run and exits 1.
- **The paragraph pass, withdrawn.** This phase first added a pass that read
  each paragraph as one line, to report a phrase a line break splits. Round
  1 found three defects in it and round 2 three more in its repair. It was
  removed rather than repaired again (spec amendment). The helper reads
  lines, as before the phase, and its documentation says so.
  [split-phrase-search.py](evidence/RW3/split-phrase-search.py) prints text
  blocks where a line break splits one of the phrases, for a person to read;
  it found none on the prepared tree or on the rehearsed published tree.
- **The stop.** Three of round 2's four findings attacked round 1's repair,
  above one half. There is no round 3. The final helper, the search script
  and the last dossier edit carry no review opinion; the 98 tests and the
  rehearsal are their instrument.
- **What the rounds checked and found true:** the token-route pattern
  against lists of two, four and seven versions and six wrong forms; that
  neither new phrase matches a page line today; the dossier's digests, byte
  sizes, counts, profiles and snapshot against the RW2 evidence and the
  retained files; that the seven patch hunks are the seven preview lines and
  leave no problem; the order of the acts against plan §11.
- **What neither round ran:** the release test files with writes, the docs
  build, the rehearsal, and any publication, install or remote command.

## Gate output (verbatim)

    98 passed, 1 deselected in 0.44s
    0.5.0 is not in RELEASED: nothing to check before publication
    All checks passed!
    changed against origin/main (44d866d): 53 file(s) differ; 0 to fix, 0 warning(s), 0 to reread
    No issues found
    19539 local links/assets/anchors checked
    FAILED tests/test_development_scaffold.py::test_reference_closure_and_declared_bootstrap
    1 failed, 865 passed, 2 deselected in 121.32s (0:02:01)

    Tool-only publish exit: 1
    git apply --check <supplement>: exit 0
    no page describes the state before 0.5.0 was published
    uv run python tools/release_text.py check: exit 0
    split-phrase search: 0 block(s)
    98 passed, 1 deselected in 0.58s
    No issues found
    19539 local links/assets/anchors checked
    Scratch publication diff SHA-256: 8a4a5e831050586fc6451f67976c8ff74c477e26ca87fe5bb88e75d0f43a6e8a

The rehearsal's full output is
[scratch-verification.txt](evidence/RW3/scratch-verification.txt).

## Refuted premises

- **"The helper can read each paragraph as one line" (spec M2 (c)).** Two
  review rounds returned six defects against it and its repair
  ([round 1](notes/reviews/phase-RW3-r1/FINDINGS.md), sha256
  `84780394…a4b2`; [round 2](notes/reviews/phase-RW3-r2/FINDINGS.md), sha256
  `e669adce…cc6d`): what a standing entry covers, how many times a statement
  is reported and where a paragraph ends each need a rule the helper does not
  have. Plan repair for the close: RC-03's successor, if wanted, is a design
  question about the unit the helper judges, not a pattern to add.

## Refactoring review

None needed after the withdrawal. The helper's change is two alternatives in
one pattern, one pattern made general and one expression that collapses a
line's whitespace; `stale_lines` has the shape it had on main. The search
script reuses the helper's own `STALE` and `page_files` and adds no second
copy of either.

## Open questions

- **A phrase split over a line break is not reported by `check`.** Stated in
  the helper's documentation and the dossier; the search script covers it at
  a rehearsal and on publication day. Whether the helper should judge
  paragraphs is the design question above. Target: the owner, as release
  tooling maintenance (it replaces RC-03).
- **The literature page's version (spec D3)** and **the issue comments (spec
  D5)** are the owner's at publication.
- **RC-07** stays the owner's first act.
- Carried from RW2: the `gnd flatten` file names against the notes'
  `<stem>`; `markdown_blocks` splitting at U+2028; the Ossie oracle root's
  origin.

## Boundary -- what this result did NOT establish

- That any command of the dossier works against PyPI or GitHub. None was
  run; the upload, the served-file comparison, the tag and the release are
  written from the 0.4.0 hand-over and the workflow's step, and checked only
  with `bash -n`.
- That the pages will still match the supplemental patch on publication
  day. A page edited before then makes `git apply --check` fail, and the
  seven lines are then rewritten by hand.
- That no page holds prepared-state wording the helper and the search both
  miss. They look for the phrases in the helper's list and for older
  version numbers.
- That the final helper and the search script are free of defects. No
  reviewer read them.
- The owner's reading of the spec. Its approval and its amendment are
  delegated.
- Publication. Nothing is uploaded, tagged or released; the pins and
  `RELEASED` are untouched.
