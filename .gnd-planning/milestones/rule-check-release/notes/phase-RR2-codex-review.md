# Codex review of the RR2 spec, draft r1

Reviewer: Codex (`gpt-6-sol`, `model_reasoning_effort=xhigh`, `--sandbox read-only`, prompt on stdin), 2026-11-08. Reviewed bytes: `notes/phase-RR2-spec.md` at commit `a789d16c`, sha256 `f9b58fedcf0aa66ecb04583cd951d5ab52031af6ece3f275938fe1e52657fdd7`. Dispositions are in the spec, §12. Verbatim output follows.

```text
DISPOSITION: revise

ID: S1  
SEVERITY: blocking  
LOCATION: .gnd-planning/milestones/rule-check-release/notes/phase-RR2-spec.md:194  
QUOTE: “one cycle, `[[api, auth, api]]` (O-e)”  
PROBLEM: The cited reference says version 7 reports a single cycle, but does not give that exact row. O-e measured the current tree, which is the candidate behavior under test. The P5 mutant’s exact `jsonschema:const` expectation at line 197 likewise comes from O-e; the cited population format promises refusal, not that issue ID. These expectations do not meet the spec’s independent-source claim.  
FIX: Ground the exact version-7 row in the published 0.1.0 control, and ground the P5 issue shape in an independent contract or an explicitly justified assertion. Label any observation of candidate output as an observation, not an expected value.

ID: S2  
SEVERITY: blocking  
LOCATION: .gnd-planning/milestones/rule-check-release/notes/phase-RR2-spec.md:248  
QUOTE: “`C` on the PR 125 branch”  
PROBLEM: The recommended build uses an unmerged branch commit. Approved RR2-C1 requires `git archive` of a named **main** commit, and the milestone completion predicate requires the installed candidate to come from one. A later merge that makes `C` an ancestor of main does not make `C` a main commit at build time.  
FIX: Build and accept a named main commit after the owner-authorized merge, or obtain an explicit plan amendment for a branch candidate and its later identity check.

ID: S3  
SEVERITY: blocking  
LOCATION: .gnd-planning/milestones/rule-check-release/notes/phase-RR2-spec.md:190  
QUOTE: “`fixed` against `base` … with `--allow-vacuous` exit 0”  
PROBLEM: Every P3 candidate run has no new must-hold violation. A broken implementation that returns 0 whenever `--allow-vacuous` is present passes these checks. The reference says the flag changes exit 2 to 0 *and nothing else*.  
FIX: Add `head --baseline base --allow-vacuous`, expecting exit 1, alongside the existing 2-to-0 case.

ID: S4  
SEVERITY: blocking  
LOCATION: .gnd-planning/milestones/rule-check-release/notes/phase-RR2-spec.md:250  
QUOTE: “Exactly two”  
PROBLEM: Approved RL-D8 and conflict C1 select the release-acceptance file as the one `addopts` override; they say nothing else overrides it. D4 recommends a second override for `tests/test_public_distribution.py` without identifying this as a change to that ruling.  
FIX: Obtain an explicit amendment to RL-D8 before selecting V6, or use a separately authorized gate that preserves the existing lane boundary.

ID: S5  
SEVERITY: blocking  
LOCATION: .gnd-planning/milestones/rule-check-release/notes/phase-RR2-spec.md:310  
QUOTE: “`-o addopts='' tests/test_public_distribution.py` … exit 0”  
PROBLEM: Clearing `addopts` also runs that file’s `@pytest.mark.evidence` cases. Its historical B3 tests compare the current tree and package with the B3 manifest: `audit_tree(ROOT)` rejects paths absent from that manifest, and `audit_payload` checks old source digests. The RR2 spec path is absent from the manifest, and its recorded `src/gnd/population.py` digest already differs from the current file. This command cannot meet its stated exit on the candidate. Excluding `evidence` would also leave one of the four claimed `VERSION` sites unrun.  
FIX: Design a targeted, current-version check for all four sites without invoking the historical B3 assertions; state the selected test nodes and lane explicitly.

ID: S6  
SEVERITY: hardening  
LOCATION: .gnd-planning/milestones/rule-check-release/notes/phase-RR2-spec.md:182  
QUOTE: “`remedy` of `no_import_loops`”  
PROBLEM: P1 checks a remedy for only one of four rules. The other three have remedies in the shipped model and how-to; deleting or corrupting them could leave T1 green despite the plan’s requirement that each verdict carry its own expected fields. P2 similarly specifies row novelty only for the loop verdict.  
FIX: Assert the expected remedy for each rule and the row novelty of the legacy and owner violations.

ID: S7  
SEVERITY: hardening  
LOCATION: .gnd-planning/milestones/rule-check-release/notes/phase-RR2-spec.md:219  
QUOTE: “`git -C <repo> archive C | tar -x -C src`”  
PROBLEM: In the stated fresh directory, `src` has not been created, so the literal command fails. The claim at line 228 that these are the workflow’s prepare steps with only three differences also omits the workflow’s artifact upload; that omission is required by this milestone’s preparation-only boundary.  
FIX: Create the extraction directory before `tar`, and describe M3 as the local build and identity portion of `prepare`, explicitly naming the omitted upload.

ID: S8  
SEVERITY: completeness  
LOCATION: .gnd-planning/milestones/rule-check-release/notes/phase-RR2-spec.md:40  
QUOTE: “RR1 open question / RL-D8”  
PROBLEM: The harvest routes RR1’s distribution question but not its deferred version-fixture refactor or the two load-sensitive timing tests. It also leaves the plan §10 question about adding RR2’s observed profile to `docs/support.md` without a decision or destination. The spec-note contract requires inherited open items to be discharged or routed.  
FIX: Add rows that assign each item to RR2, RR3, close, or a named later milestone, with the intended disposition.

ID: S9  
SEVERITY: hardening  
LOCATION: .gnd-planning/milestones/rule-check-release/notes/phase-RR2-spec.md:205  
QUOTE: “exit 64”  
PROBLEM: Exit 64 is plausible and agrees with 0.1.0’s argument parser, but approved plan §2 says the 0.1.0 option-refusal control exits 2. The draft silently changes a stated plan expectation.  
FIX: Record the plan’s exit-2 statement as a refuted premise and amend it to 64 with the tag evidence.

CHECKED AND FOUND TRUE

- The shipped base population’s SHA-256 matches T1’s `d816…5fcd` value and the how-to.
- The 0.1.0 tag lacks the three flags, `remedy`, and the `tool-output`/`producer` schema fields. Section 3.1’s reported refusals are plausible; the stripped-input default comparison is a fair comparison of the shared version-7 path.
- FU2’s source diff adds the stated `model_copy` producer check and preserves `label` when combining populations. `git diff 1e63aeb5 df5753bf -- src` is empty.
- V4’s clean worktree at `C` would make the existing acceptance fixture’s `git archive HEAD` archive `C`. The proposed new installed-wheel calls use that fixture’s macOS sandbox prefix.

COULD NOT DO

- Build or install artifacts, run the acceptance suite, or verify live PyPI and GitHub state in this read-only review.
codex exit=0
```
