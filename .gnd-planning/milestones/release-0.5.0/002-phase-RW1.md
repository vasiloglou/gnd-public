---
milestone: release-0.5.0
station: "phase-RW1"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-RW1
date: 2026-11-25
implementation_commit: 4a73af2eafe18bc7556dc8607b37dfe5a1fe65e3
gates:
  - command: "ruling: delegated (auto=true) approved .gnd-planning/milestones/release-0.5.0/notes/phase-RW1-spec.md sha256 a56efcc9ea2f3f38b81b929fd5e8d7a661f6192e0d04705a63733cca192e847e"
    exit: "n/a -- ruling"
    output: "first ruling, renewed at the resumed base: spec r6 approved for the E1 measurement only (commit b25bb2d8)"
  - command: "ruling: owner chose 'Ossie relational files' as the block that leads the 0.5.0 notes (spec D4), among the four readings of D4, 2026-11-25"
    exit: "n/a -- ruling"
    output: "the owner chose among one-line descriptions; the owner has not read the spec"
  - command: "ruling: delegated (auto=true) approved .gnd-planning/milestones/release-0.5.0/notes/phase-RW1-spec.md sha256 c2f7efed1d26e52209e87ace093fae15bc896f7856393e08f0cc3613b3c6ea6d"
    exit: "n/a -- ruling"
    output: "second ruling: spec r7 approved for implementation with the handling list of its section 13 (commit 4d2d8325)"
  - command: "e1-shards.sh 4968631ec93ad7e74936c5569bf7657a5b088d94 base, and the same with bumped (beast-3, six shards each)"
    exit: "base 0, 0, 0, 1, 0, 1; bumped 0, 0, 0, 1, 1, 1"
    output: "base 21,994 passed, 1 failed, 2 errors, 13 skipped; bumped 21,989 passed, 6 failed, 2 errors, 13 skipped"
    note: "E1. The five failures the bump adds are all in tests/test_release_version.py"
  - command: "uv lock --check"
    exit: 0
    output: "Resolved 32 packages"
  - command: "uv run pytest -q tests/test_release_version.py tests/test_recorded_version.py tests/test_release_text.py tests/test_marketplace_plugins.py tests/test_release_docs.py tests/test_release_preparation.py tests/test_package_description.py tests/test_ossie_docs.py tests/test_plan_app_docs.py tests/test_il6_walk.py --tb=line -p no:cacheprovider"
    exit: 0
    output: "263 passed, 1 deselected in 12.83s"
    note: "at 4a73af2e. The spec's seven focused files, plus the three other test files that read the notes or the how-to pages"
  - command: "uv run python tools/release_text.py check"
    exit: 0
    output: "0.5.0 is not in RELEASED: nothing to check before publication"
  - command: "the project.md structure and inventory guard block (16 files)"
    exit: 1
    output: "1 failed, 865 passed, 2 deselected in 125.45s (0:02:05)"
    note: "the one failure, tests/test_development_scaffold.py::test_reference_closure_and_declared_bootstrap, comes from an untracked skill mirror in this checkout; the same test passes in all three clean-clone lanes below"
  - command: "uv run ruff check"
    exit: 0
    output: "All checks passed!"
  - command: "python3 scripts/components_index.py changed --base origin/main --strict"
    exit: 0
    output: "changed against origin/main (3998d37): 54 file(s) differ; 0 to fix, 0 warning(s), 0 to reread"
  - command: "uv run --group docs zensical build --strict"
    exit: 0
    output: "No issues found"
  - command: "uv run python tools/check_docs.py site"
    exit: 0
    output: "19539 local links/assets/anchors checked"
  - command: "e1-shards.sh cc8cdb6594cc75a2ee42fe7db89281bc344b3abc base (beast-3, six shards)"
    exit: "1, 0, 0, 1, 0, 1"
    output: "21,992 passed, 3 failed, 2 errors, 13 skipped"
    note: "the first RW1 commit. Two failures the E1 base lacks, both in tests/test_ossie_docs.py; repaired at 1d8536de"
  - command: "e1-shards.sh 1d8536deb8318d1de17174055551a95d0331ec70 base (beast-3, six shards)"
    exit: "0, 0, 0, 1, 0, 1"
    output: "21,994 passed, 1 failed, 2 errors, 13 skipped"
    note: "the same failing ids as the E1 base run"
  - command: "e1-shards.sh 4a73af2eafe18bc7556dc8607b37dfe5a1fe65e3 base (beast-3, six shards)"
    exit: "0, 0, 0, 0, 0, 1"
    output: "21,998 passed, 0 failed, 2 errors, 13 skipped"
    note: "T7 at the implementation commit, which has main 3998d371 merged. The two errors are the RC-02 setup errors of tests/test_public_optional.py"
  - command: "python3 .claude/skills/process-phase/scripts/review_tool.py run .gnd-planning/milestones/release-0.5.0/notes/reviews/phase-RW1-r1"
    exit: 0
    output: "codex, effort high, read-only: 1 finding, VERDICT: CHANGES_REQUESTED"
  - command: "python3 .claude/skills/process-phase/scripts/review_tool.py run .gnd-planning/milestones/release-0.5.0/notes/reviews/phase-RW1-r2 --wait"
    exit: 0
    output: "codex, effort high, read-only: 1 finding, VERDICT: CHANGES_REQUESTED"
  - command: "python3 .claude/skills/process-phase/scripts/review_tool.py status .gnd-planning/milestones/release-0.5.0/notes/reviews"
    exit: 1
    output: "both rounds done, ledgers complete; unreviewed: docs/release-notes.md, evidence/RW1/old-version-probes.md, evidence/RW1/notes-reconciliation.md (changed after the round that read them)"
slow_cadence:
  command: "uv run pytest -q -m \"evidence or census\""
  trigger: "not run"
  reason: "spec D3: opt-in lanes are excluded from RW1. pyrel_oracle is RW2's, on the owner's selection of 2026-11-23; ossie_oracle is asked at the RW2 spec (plan section 14)"
evidence:
  - path: .gnd-planning/milestones/release-0.5.0/notes/phase-RW1-spec.md
    sha256: aac415c539b5c79a567ae5775c2d92863be621933cc923b3a82d2fc4429458ce
    note: "r7 with the second ruling appended; the rulings name the bytes they approved"
  - path: .gnd-planning/milestones/release-0.5.0/notes/release-0.5.0-plan.md
    sha256: ceaecc0aa48ddcf74d6eeb38f4ba7032e5fa057e2d6bcd5c9b38dbb7170da206
    note: "r5: section 14 and its later addendum"
  - path: .gnd-planning/milestones/release-0.5.0/evidence/RW1/e1-shards.sh
    sha256: 7b9e7634d1b518c585876078664f5f5d19d84ad8247d4b8006d05c640b286ff4
  - path: .gnd-planning/milestones/release-0.5.0/evidence/RW1/e1-summary.md
    sha256: 8b2bef0619c07767a5f5bd6c475d4e4c98c3a8e052116ec4a694b74c16139d09
  - path: .gnd-planning/milestones/release-0.5.0/evidence/RW1/t7-lanes.md
    sha256: f93061addf66110278cc09d89310fb3c965e2f8bd39a45383cfc0d2c30a6df59
  - path: .gnd-planning/milestones/release-0.5.0/evidence/RW1/notes-reconciliation.md
    sha256: 67f8258908dcf0f053ff1856b8c8ad428159e5ca4a78e55eb6122936924575fa
  - path: .gnd-planning/milestones/release-0.5.0/evidence/RW1/old-version-probes.md
    sha256: 18e6931fcacc56fe53b5cda47c52bc790e1022418467db07b62e7f8fc9479342
  - path: .gnd-planning/milestones/release-0.5.0/notes/reviews/phase-RW1-r1/review.md
    sha256: 1fb549ac6c59c059b70b2175cc8015eaaf55172fe5743b3f9266f7d8ce44fb39
    note: "sanitized; run.json binds the original"
  - path: .gnd-planning/milestones/release-0.5.0/notes/reviews/phase-RW1-r1/run.json
    sha256: 69ae4b0787c665e7f4b66e133c7c1ec997e4b728e595df2ea779d4eef348c59d
  - path: .gnd-planning/milestones/release-0.5.0/notes/reviews/phase-RW1-r1/FINDINGS.md
    sha256: 28576fa81da233c17bd90c21842c64fdc35b7a4c912263294779f3cf9b9eef4e
  - path: .gnd-planning/milestones/release-0.5.0/notes/reviews/phase-RW1-r2/review.md
    sha256: e8a5e41fa8babfead00d82670253626f3dd9775479536334c3d301a0a621835a
    note: "sanitized; run.json binds the original"
  - path: .gnd-planning/milestones/release-0.5.0/notes/reviews/phase-RW1-r2/run.json
    sha256: 5ff0de74167e9ae8f75fe86eabcce2d7c6751f5862875c326561f0aaa66bcfc6
  - path: .gnd-planning/milestones/release-0.5.0/notes/reviews/phase-RW1-r2/FINDINGS.md
    sha256: fdf1088fb6b5515c217d6148469bace0a933321dc9c88b08bb8f9b30fc20c4cb
  - path: pyproject.toml
    sha256: 031acf62df8f7a8aa074eeca4976fa56396e61aa53c4f30a71dbdd61e4c7a4a2
  - path: uv.lock
    sha256: e96d80125673b6b3dbd6203caedcda1e5871ed47da45bd4b2ab3c35804f9496f
  - path: .claude-plugin/plugin.json
    sha256: 2b021b3206ceca1778fd8011e9997f9ae7d7b2fc6437e669082309301ce3a85d
  - path: .codex-plugin/plugin.json
    sha256: 21c44d7a1e8cd88cf5b8f3259574a7709cd325925f9df171e0b2cea2f115df48
  - path: .claude-plugin/marketplace.json
    sha256: f0724655e0e373311f65c5ef102a11f41ad493c1d3c8f5156aad752f9d9b2c1e
  - path: docs/release-notes.md
    sha256: dac2bb66da8b4ec6858f0fdd8f23538ff338ba9fdb0cfc9f49c561aa5f95968e
  - path: docs/compatibility.md
    sha256: ee61db381c81252795befebc1abc04033dd16b65a195a654f82a3b991e82c66b
  - path: docs/support.md
    sha256: af5e248dee386a23418111f7717115b7a735dbb3da704b2e625ab19d41824c3d
  - path: docs/marketplace-plugins.md
    sha256: a760dac10f89ccd4ce93c99f771cca57f90e92e9ac039cf81995b2f79336c8f7
  - path: tests/test_release_version.py
    sha256: a09670902e2756ba37ae2a074fc776d30915f54b22fb2efa29dc42ec8c6ad00c
  - path: tests/test_ossie_docs.py
    sha256: 6635a3d9069a2025df7650593adf69488323e950cc7c02e66bd3e121e065657d
---

# Claim

At `4a73af2e` the declared version is 0.5.0 in `pyproject.toml`, the lock
entry and the three plugin manifests; `tests/test_release_version.py` exited
0 inside the focused gate; `uv lock --check`, `tools/release_text.py check`,
`uv run ruff check`, the component-index check, the strict docs build and
the site link check exited 0; and the six-shard default lane on a clean
clone reported 21,998 passed, no failure and the two RC-02 setup errors.
Nothing was built, uploaded, tagged or released.

## What the phase did

- **Version (M1 to M3).** Five lines: `pyproject.toml`, the editable
  `get-nick-done` line of `uv.lock` edited by hand, and the three manifests.
- **Notes (M6).** The five `Unreleased:` sections of `docs/release-notes.md`
  became one `## 0.5.0 (prepared, not published)` section of seven blocks.
  The 26 bullets main held moved with their wording and links unchanged;
  the first review round checked that each occurs exactly once. Fourteen
  bullets are new: six in the PyRel block, two in the Ossie block, two for
  the COUNT certificates and four under "Other changes".
- **Headline (M4, D4).** The owner chose "Ossie relational files". The
  section opens with that block, and `HEADLINE_BLOCK["0.5.0"]` pins it with
  its link to `explanation/ossie.md`. Control: with the PyRel block first,
  `assert_notes_name_the_headline_change` raised `AssertionError: the 0.5.0
  notes do not open with '### Ossie relational files'`.
- **Status pages (M7 to M9).** The compatibility, support and plugin pages
  say 0.5.0 is prepared and not published. The package index was read on
  2026-11-25: it lists 0.1.0 to 0.4.0 and no 0.5.0. The install pins stay at
  0.4.0.
- **A consumer E1 could not show (M5).** Two tests in
  `tests/test_ossie_docs.py` read the notes by the heading the rewrite
  removed. They now read `### Ossie relational files`, named once in that
  file. See "Refuted premises".

Size: about 106 new or changed lines outside planning, against the second
ruling's 86 and its pause point of 129. The notes file shows 143 lines added
and 53 removed.

## Spec obligations

| Row | Result |
|---|---|
| RW1-C1 | done; `test_lock_manifests_and_notes_agree_with_pyproject` in the focused gate; reviewer's C1 |
| RW1-C2 | E1 ran twice before code; the handling list is spec §13. The list was incomplete by two test ids (below) |
| RW1-C3 | one 0.5.0 section, no `Unreleased:` section left. [notes-reconciliation.md](evidence/RW1/notes-reconciliation.md) places all 140 shipped files that differ from `v0.4.0`. "Every user-visible change" is shown by that table and the review, not proved by a test |
| RW1-C4 | done; the pins are unchanged (`test_install_pins_name_a_published_version` in the focused gate) |
| RW1-C5 | exit 0, both |
| RW1-C6 | at `4a73af2e` the lane has no failure. At `cc8cdb65` it had two the base lacked; they are repaired |
| RW1-C7 | `uv run ruff check` exit 0 |
| structure guards | 865 passed, 1 failed locally; the failure is this checkout's untracked skill mirror and does not occur in a clean clone |
| component index | 0 to fix |
| W15, R10 | the PyRel block's last bullet says no RelationalAI engine ran the programs; reviewer's C5 found nothing that reads otherwise |
| R3 | main will say 0.5.0 before PyPI once this merges; the heading and three pages say "not published" |
| RR1 finding | the lock line was edited by hand; `uv lock --check` exit 0; the diff of `uv.lock` is one line |

## Review

One reviewer in a different tool, Codex at effort high, read-only, through
the review helper. Two rounds.

| Round | Seats | Per-seat counts | Self-inflicted / total | Blocking / total | Severity ceiling | Verdicts |
|---|---|---|---|---|---|---|
| r1, the RW1 diff at `cc8cdb65` | codex | 1 | 0 / 1 | 0 / 1 | P2 | changes requested |
| r2, the repairs at `1d8536de` | codex | 1 | 1 / 1 | 0 / 1 | P2 | changes requested |

- **r1 F1, reproduced, fixed at `1d8536de`.** The PyRel block did not say
  that a model writing an Integer `min` or `max` into a `Float` role is
  refused at export, where 0.4.0 exported it. Reproduced with 0.4.0 from
  the package index against this tree, for `sum` as well: exit 0 against
  exit 3 in both modes
  ([old-version-probes.md](evidence/RW1/old-version-probes.md)).
- **r2 F1, reproduced, fixed at `5faddf3d`.** The repaired sentence refused
  too much: an Integer count written into such a role is accepted.
  The sentence now follows `_refuse_inexact_head`.
- **Why there is no round 3.** Round 2's one finding attacked text that
  round 1's repair wrote, so the self-inflicted ratio is above one half,
  which is the stop rule of `review-convergence.md`. The round budget was
  not written down before round 2, as that page asks; the stop rule was
  applied after it.
- **What r1 checked and found true:** the digests, the version agreement,
  the 26 moved bullets, the 140-file reconciliation, the "not published"
  and no-engine wording, and probes of the COUNT commands, the Ossie export
  and the numeric refusals.
- **What neither round ran:** the full lane, the strict docs build, an
  installed 0.4.0 package (r2 used 0.4.0's source), a RelationalAI engine.

The helper's `status` exits 1: three files changed after the round that
read them. The last sentence of the PyRel refusal bullet, the count probe
and the reconciliation's paragraph about pull request 275 carry no review
opinion. The lane and the probes cover them.

## Gate output (verbatim)

    Resolved 32 packages in 17ms
    263 passed, 1 deselected in 12.83s
    0.5.0 is not in RELEASED: nothing to check before publication
    FAILED tests/test_development_scaffold.py::test_reference_closure_and_declared_bootstrap
    1 failed, 865 passed, 2 deselected in 125.45s (0:02:05)
    All checks passed!
    changed against origin/main (3998d37): 54 file(s) differ; 0 to fix, 0 warning(s), 0 to reread
    No issues found
    19539 local links/assets/anchors checked

    4a73af2eafe18bc7556dc8607b37dfe5a1fe65e3
    Shard 0 exit 0
    4322 passed, 49 deselected in 681.34s (0:11:21)
    Shard 1 exit 0
    2849 passed, 238 deselected in 693.03s (0:11:33)
    Shard 2 exit 0
    4204 passed, 219 deselected, 1 warning in 743.70s (0:12:23)
    Shard 3 exit 0
    3649 passed, 13 skipped, 104 deselected in 1008.86s (0:16:48)
    Shard 4 exit 0
    3778 passed, 256 deselected in 564.60s (0:09:24)
    Shard 5 exit 1
    ERROR tests/test_public_optional.py::test_base_wheel_refuses_missing_synth_extra_and_still_checks
    ERROR tests/test_public_optional.py::test_declared_synth_extra_is_seeded_and_loader_valid
    3196 passed, 174 deselected, 2 errors in 740.02s (0:12:20)

The other lanes are in [t7-lanes.md](evidence/RW1/t7-lanes.md) and
[e1-summary.md](evidence/RW1/e1-summary.md).

## Refuted premises

- **"The ids E1 lists are every consumer the phase must handle" (spec §6
  and §13, plan W8).** E1 changes the version fields only. The notes rewrite
  has its own consumers, and E1 cannot see them: two tests of
  `tests/test_ossie_docs.py` failed at `cc8cdb65`
  ([t7-lanes.md](evidence/RW1/t7-lanes.md), sha256 `f93061ad…df59`). The
  focused gate of the spec did not hold them either. The full lane found
  them. Plan repair for the close: E1's design names the notes' readers as
  a second measured set, found by searching the tests for the notes' path.
- **"The base run has no failure, or the scaffold guard" (spec r6, §6).**
  The base at `4968631e` had one failure, in a how-to page of the Ossie
  milestone, and the scaffold guard passed
  ([e1-summary.md](evidence/RW1/e1-summary.md), sha256 `8b2bef06…9d09`).
  Pull request 275 repaired it on main.

## Refactoring review

None needed. Outside planning the phase changed five version fields, four
docs pages and four lines in two test files. The one structural choice was
to name the notes heading once in `tests/test_ossie_docs.py`, where two
tests had each spelled it. No production code changed.

## Open questions

- **Issue links for the Ossie bullets.** The session that ran
  ossie-relational-bundle filed issues 276 to 280 after its bullets were
  written. The moved bullets keep their wording (D6), so they link none.
  Owner's choice whether RW2-C0 adds them.
- **The scaffold guard in this checkout.** An untracked, locally excluded
  skill mirror makes one guard test fail here and nowhere else. It is this
  machine's state, not the repository's; the Ossie close record lists the
  same test as a known red. Target: the owner, or whoever maintains that
  mirror.
- **For the RW2 spec (plan §14):** whether `ossie_oracle` runs at the freeze
  commit, and a fifth installed probe for the five-file export.
- **For the close:** the plan repair named under "Refuted premises"; the
  round budget that was not declared before review round 2.

## Boundary -- what this result did NOT establish

- That 0.5.0 builds, installs or passes release acceptance. No wheel or
  sdist was built; that is RW2, which needs this phase merged.
- That the notes are complete. The reconciliation table was built from
  which pull request changed each file; most diffs were not read line by
  line, and one reviewer is one reviewer.
- That the final wording of the PyRel refusal bullet is right. It was
  changed after the round that read it.
- Anything about opt-in lanes, a RelationalAI engine, or what 0.4.0 did
  with the export-time refusals the probes did not run.
- The owner's reading of the spec. Both spec rulings are delegated; the
  owner ruled D4 from a one-line description of each choice.
- Publication. The pins, `RELEASED`, the upload, the tag and the GitHub
  release are untouched and each waits for the owner's request.
