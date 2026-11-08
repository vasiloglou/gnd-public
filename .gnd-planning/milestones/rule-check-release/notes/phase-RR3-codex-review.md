# Codex review of the RR3 spec, draft r1

Reviewer: Codex (`gpt-6-sol`, `model_reasoning_effort=xhigh`, `--sandbox read-only`, prompt on stdin), 2026-11-08. Reviewed bytes: `notes/phase-RR3-spec.md` at commit `fd4cb5e4`, sha256 `2bd704397849c6603d8d868db92b6e94e20f50b417567ef4dd8d46894d158125`. Dispositions are in the spec, §12. Verbatim output follows.

```text
DISPOSITION: revise

ID: Q1 — The inventory misses stale release-state text  
SEVERITY: blocking  
LOCATION: .gnd-planning/milestones/rule-check-release/notes/phase-RR3-spec.md:117  
QUOTE: “heading and opening”  
PROBLEM: The row does not explicitly cover `docs/release-notes.md:4-7`, including “Until it is published, install commands … name 0.1.0.” Section 6.2 also omits the versionless “first PyPI release” wording in `docs/releasing.md:9`, although M3 proposes to repair it. The stated 23 hits count only `0.1.0`; the stated version and phrase search returns 29 lines outside release notes.  
FIX: Classify the opening paragraph and versionless release wording explicitly. State the search and exclusions precisely, then require the patch to remove every stale clause.

ID: Q2 — F1 asserts a byte difference the workflow does not prove  
SEVERITY: hardening  
LOCATION: .gnd-planning/milestones/rule-check-release/notes/phase-RR3-spec.md:48  
QUOTE: “a new candidate with new bytes”  
PROBLEM: `release.yml` proves that dispatch builds and uploads that run’s artifacts from its checked-out main commit. It does not prove their hashes differ from the retained files. The changes from `7c0f4d0e` to `25f58b5e` are tests and planning files, so identical package bytes remain possible.  
FIX: Say the workflow creates a new build tied to its own source commit and acceptance run. Leave byte identity to a hash comparison.

ID: Q3 — Required prepublication actions are absent from M1  
SEVERITY: blocking  
LOCATION: .gnd-planning/milestones/rule-check-release/notes/phase-RR3-spec.md:148  
QUOTE: “Owner actions before and at publication”  
PROBLEM: The numbered actions omit O8’s repository visibility, content and history review and target-only release authority. They also omit O15’s check that breaking changes and migration instructions are recorded, and its prohibition on overwriting released files. Thus RR3-C2 can appear complete while required owner actions have no entry or dated open evidence.  
FIX: Add each action and its current evidence to M1 §D, with route-specific publisher and environment checks.

ID: Q4 — D6 introduces unchecked version copies  
SEVERITY: blocking  
LOCATION: .gnd-planning/milestones/rule-check-release/notes/phase-RR3-spec.md:207  
QUOTE: “with no version: ‘Install GND 0.2.0 or later’”  
PROBLEM: That sentence names `0.2.0`. Repeating it across seven pages creates version literals outside `PIN_FILES` and outside the proposed version-consistency check, contrary to plan rule 0.2.  
FIX: Use genuinely versionless text linking to the installation page, or add every literal-bearing page to a test tied to the declared version.

ID: Q5 — T5 has no failure condition  
SEVERITY: blocking  
LOCATION: .gnd-planning/milestones/rule-check-release/notes/phase-RR3-spec.md:218  
QUOTE: “recorded output”  
PROBLEM: A grep still exits successfully when it finds stale text. T5 specifies neither an allowed historical-hit list nor an assertion against unexpected hits, so an incomplete patch can pass its stated gate.  
FIX: Compare the post-patch results with an explicit historical allowlist and require a nonzero exit for any unmatched hit, including versionless release-state wording.

ID: Q6 — V3 cannot establish predicate 6 at milestone close  
SEVERITY: blocking  
LOCATION: .gnd-planning/milestones/rule-check-release/notes/phase-RR3-spec.md:248  
QUOTE: “git diff origin/main -- .github is empty”  
PROBLEM: After merge, a diff against `origin/main` can be empty even if the milestone changed `.github/`. V3 also omits the plan’s required procedure-step comparison for `docs/releasing.md` and gives no baseline comparison or expected result for its remote listings.  
FIX: Audit against the fixed pre-milestone base, account for the approved `releasing.md` edits, and compare dated remote results with O3/O5’s baseline. State that PyPI account-side publisher registration remains unaudited.

ID: Q7 — D4 joins two independent publication choices  
SEVERITY: completeness  
LOCATION: .gnd-planning/milestones/rule-check-release/notes/phase-RR3-spec.md:205  
QUOTE: “applied only if the owner creates the tag … and attaches the files”  
PROBLEM: A tag can exist without GitHub release attachments. The spec’s own inventory marks the tag wording stale on tag creation, yet the combined patch is withheld unless files are attached. Its inventory also names `7c0f4d0e` for the tag case, while M1 permits a workflow-built commit.  
FIX: Give tag wording and attached-file instructions separate conditions or independently applicable hunks, keyed to the published commit.

ID: Q8 — T6 does not check M3’s procedure meaning  
SEVERITY: hardening  
LOCATION: .gnd-planning/milestones/rule-check-release/notes/phase-RR3-spec.md:219  
QUOTE: “tests/test_release_docs.py tests/test_release_preparation.py”  
PROBLEM: `test_release_docs.py` checks links, and `test_release_preparation.py` checks the frozen workflow. Neither would fail if `docs/releasing.md` still described Trusted Publishing as the sole route or retained “After Phase 3 accepts.”  
FIX: Add a focused assertion for the intended route conditions and removed stale wording, or make an explicit reviewed text check part of the gate.

CHECKED AND FOUND TRUE

- `release.yml` prepares from the dispatch’s main ref and publishes artifacts retained by that same run.
- Without the `RELEASED` hunk, new `0.2.0` install pins fail the existing `assert_pins_name_published_versions` check; T3’s predicted failure is real.
- T3b and T4 describe checks that can be added to `tests/test_release_version.py`. The current test file does not yet contain them.
- M1 identifies the retained candidate, its measured profile and principal unmeasured cases. D1’s proposed edit is within RR3-C4’s owner gate.

COULD NOT DO

- Execute T1–T4 or inspect the proposed patch contents: neither RR3 patch file exists yet.
- Verify live GitHub or PyPI state from this read-only review.
codex exit=0
```
