Retained text of the reader's report. Local paths read `<repo>`, `<scratch>`.

# Close reader 4 of 4: protocol, evidence and records (unattended-model-growth)

Subject: `<repo>/.gnd-planning/milestones/unattended-model-growth/` at HEAD `dd3c35a5` (= main, after PR 151). Read only; no repository file was edited. Scratch scripts and outputs are under `<scratch>/close-r4/` (`dig.py`, `digests.txt`, `scan.py`, `msgs.txt`, `q.txt`).

## Verdict: approve-with-fixes

The phase records exist and their evidence digests verify. There are three blocking items, and all three can be fixed in the close record and README without rewriting history:
1. The README's status is stale.
2. The tracker state the records claim is false. Issues 74, 75 and 76 have been closed since 2026-11-08.
3. One implementation commit landed before its approval was recorded.

The hardening and completeness items below should be dispositioned in the close record.

## Findings

### R4-F1 (blocking): the README status does not match what merged
- Where: `README.md:15`, `:38`, `:40-43`, `:52-54`.
- Check: `gh pr view 151` returned `MERGED dd3c35a5 claude/ug4-spec`. `git log --first-parent HEAD -4` shows `dd3c35a5 Merge pull request #151`.
- Observed:
  - `:15` says UG4 is "recorded on branch `claude/ug4-spec` ... not merged; the milestone close remains". `:38` says "not merged".
  - `:52` says "Next action. The owner reviews the UG4 pull request and decides whether to merge it".
  - `:53` says "Until then no code is written".
  - `:40-43` still says UG2 and UG3 "need[s] its own spec gate".
  - `:54` says "neither blocks UG1".
- Fix: rewrite the status and next-action lines. They should say: UG4 merged in PR 151 (`dd3c35a5`), the close is the only remaining step, and the phase-list sentence and the "no code is written" sentence are history.

### R4-F2 (blocking): issues 74, 75 and 76 are closed, and the records say no issue is closed
- Where:
  - `README.md:15` ("No issue is closed").
  - `notes/ug1-issue-dispositions.md:13-14` ("No issue was closed").
  - `notes/ug4-issue-followups.md:12-15` treats #74 and #76 as open and drafts follow-ups for them.
  - `004-phase-UG3a.md:110` ("Issue 74 is not commented on or closed").
- Check: `gh issue view N --json state,closedAt`, then `gh api repos/.../issues/74/events`.
- Observed:
  - 74, 75 and 76 are `CLOSED` (reason COMPLETED) at 2026-11-08T14:44:50Z, :53Z and :55Z. The closing actor is the owner's account, and no commit is attached.
  - 104 is `OPEN`.
  - The UG1 dispositions were posted at 2026-11-08T17:59Z, three hours after the closures. The commit marking them posted (`3cbd31d5`) still wrote "No issue was closed".
- Fix: the close record states the real tracker state with the timestamps and corrects the dispositions note's sentence. Under the append-only rule that correction is a new record, not an edit of `002`. The follow-ups for #74 and #76 are re-scoped as comments on closed issues, or retired. UG-D0 for 104 remains the owner's.

### R4-F3 (blocking, disclosure required): implementation was committed before its approval was recorded
- Where: `notes/phase-UG3-spec.md` status line at `747c1ba5`.
- Check: `git show <c>:notes/phase-UG*-spec.md | sed -n 3,6p` and `git show --stat` for each commit in the four PRs.
- Observed:
  - **UG3, the clear case.** `747c1ba5 feat(phase-UG3a)` (17:32 -0500) changes `src/gnd/commands/checking.py`, `src/gnd/model/_unattended.py` and `src/gnd/model/__init__.py`. At that commit the spec status still reads "Corpus authored and red ... waiting for the owner's corpus approval". The corpus approval ("Approve the corpus") is first recorded in `2dea8a81`, the UG3b implementation commit.
  - **Same-commit cases.** In three phases the ruling was recorded in the same commit as the code, so git cannot show which came first:
    - UG1: spec gate and the test file, both in `ffacc133`.
    - UG2: corpus approval and the `src/gnd/evolve` changes, both in `2518e8fe`.
    - UG4: the spec ruling "Approve all as proposed" and the docs/skill/test edits, both in `ff49a713`. `478ea2a2` holds only the draft.
  - Only the UG2 and UG3 spec-gate rulings precede code in separate commits (`c635ef9d`, `e881e521`; neither touches `src/`).
- Fix: the close record says this plainly ("no code before recorded spec approval" holds for UG2 and UG3 spec gates only; UG3a code preceded its recorded corpus approval). It does not claim the ordering was kept. For future milestones, commit the ruling before the first implementation edit.

### R4-F4 (hardening): append-only and section rules broken in 001 and 002
- Where: `002-phase-UG1.md`, `001-plan.md:60-68`.
- Check: `git log -- 00*.md` showed `002-phase-UG1.md: 15ca986b 1b8540d5`; every other record has one commit. Then `grep -n '^## '` over each record.
- Observed:
  - `002` was rewritten after its commit by `15ca986b`. The T-anon row went from not-run to run, and a new "Anonymity scan" section was added. This happened before the PR merged, but after the record's own commit.
  - `002` has no `## Open questions` section. UG-Q6 and UG-Q7 sit in its Boundary at `:130-131`.
  - `001` has no `## Open questions` section; its open questions are under "What it does not cover".
- Fix: the close sweep treats `002`'s Boundary bullets and `001:62-65` as the open-question sources. The close record notes the in-place edit. Later records get a correction record instead of an edit.

### R4-F5 (hardening): commit-message grammar
- Check: a loop over all 21 commits of PRs 123, 139, 147, 149 and 151 (`git log --format=%B`), counting backticks, em-dashes, Co-Authored-By lines and record-path lines. Then `git log --format='%(trailers:key=Co-Authored-By,valueonly)'`.
- Observed:
  - **Scope token.** The six plan/UG1 commits (`5d9d8ba1`, `314dc019`, `b3a4fda4`, `ffacc133`, `1b8540d5`, `15ca986b`) and `3cbd31d5` use `unattended-model-growth`. The contract wants `plan` and `phase-UG1`, and `002` itself says `scope: phase-UG1`.
  - **Missing body and record path.** `1b8540d5`, the commit that introduced `002`, has no body and no record path. `b3a4fda4` names its record mid-body rather than on its own closing line.
  - **Co-Authored-By not parsed.** In `8e7819a1`, `a06d1f6f` and `c56781b6` the record path follows the Co-Authored-By line. Git does not parse Co-Authored-By as a trailer there; the trailer query returns empty, so the attribution does not register.
  - **Subject length.**
    - `ff49a713` has a 71-character description, over 65 by any reading.
    - Counting the type(scope) prefix, 12 subjects exceed 65: `15ca986b`, `1b8540d5`, `ffacc133`, `b3a4fda4`, `314dc019`, `3cbd31d5`, `bff83562`, `c635ef9d`, `2518e8fe`, `747c1ba5`, `e881e521`, `ff49a713`.
  - **Feat/doc commits without a record path.** `747c1ba5`, `2dea8a81`, `478ea2a2` and `ff49a713` carry no record path. The rule binds record commits, so this is minor.
  - **No problem found:**
    - backticks: 0 in all 21 commits;
    - em-dashes: 0;
    - Co-Authored-By: present in all 21.
- Fix: record these as known deviations in the close record. In the close commit, put the record path before the Co-Authored-By trailer, as `e0e6790c` does, and use scope `close` (or `milestone-close`, see R4-F14).

### R4-F6 (hardening): gate commands are not verbatim
- Where: `003-phase-UG2.md:8`, `004-phase-UG3a.md:8`, `005-phase-UG3b.md:8`.
- Observed:
  - **Elided commands.** The gate command elides its module list as "<43 modules: ...>" and "<99 modules: ...>", so it cannot be re-run from the record. All three also carry `<scratch>` placeholders.
  - **Gate output is summaries.** No phase record has a "Gate output (verbatim)" section; each gives summary lines. `005:15` says lint, components and anonymity were "as in 004" rather than giving its own exits.
  - **Junit digests.** These are declared "scratch, not committed" (`002:26`, `003:29`, `004:31`, `005:27`), but no record states that the claim is correspondingly weaker. `006` cites no junit digest at all.
- Fix: the close record's union gate lists every module explicitly (or commits the selection file) and records its verbatim summary. It also states that the phase junit digests are not checkable from history.

### R4-F7 (hardening): evidence does not cover the claims
- Observed:
  - **`006` evidence.** The front matter cites 5 paths, but `ff49a713`/`c56781b6` changed 11 non-planning files. Missing are:
    - `docs/agents/evolve.md`;
    - `docs/agents/model-from-text.md`;
    - `docs/how-to/grow-a-model.md`;
    - `docs/reference/evolve-policy.md`;
    - `docs/release-notes.md`;
    - `src/gnd/skills/gnd-model-evolve/SKILL.md`;
    - `src/gnd/skills/gnd-model-evolve/references/evolution-contract.md`;
    - `src/gnd/skills/gnd-model-from-text/SKILL.md`.
    The UG4-C5 row (`006:55`) cites line numbers in several of them, with no digest.
  - **Merge after the record.** `ab6beff7` ("Merge main (PR 150) into the UG4 branch") came after the record and the review. It resolved a conflict in `src/gnd/skills/gnd-model-from-text/SKILL.md`, a UG4-touched file. No gate or review is recorded over the merged bytes.
  - **`001` evidence.**
    - The snapshot entry (`001-plan.md:17-18`) has no sha256. Recomputed, it is `b2678c57...`, which matches the r1.1 digest in the body.
    - The UG1 spec snapshot (`e7523244...`, matches) is not cited at all.
- Fix: the close record cites the UG4 docs files by digest at `dd3c35a5`. It also includes the packaged-skill and docs gates in its union gate over the merged bytes, which covers the merge resolution.

### R4-F8 (completeness): cited digests that no longer match main
- Check: `<scratch>/close-r4/dig.py` recomputes each cited digest at the record's introducing commit, its merge commit and HEAD.
- Observed: every cited committed path matches at its record's introducing commit and its merge. On main, four differ:
  - `001`: the plan file. `f099eb2a...` matches only at `314dc019`; at `b3a4fda4` and later it is `fa2679af...`. This is declared: status-only edits, and the record's `commit:` field pins `314dc019`.
  - `002`: `tests/test_unattended_model_growth_acceptance.py`. Now `28822fc8...`, changed by `2dea8a81` (UG3b F-i4, a comment-only change to T12 (a)).
  - `002`: `notes/ug1-issue-dispositions.md`. Now `5077aae5...`, changed by `3cbd31d5` (marked posted).
  - `004`: `src/gnd/model/_unattended.py`. Now `380a9f06...`, changed by `42a34aca` through PR 150 (`39246a93`), the U5 induced-constraint exception.
- Fix: the close parity table lists these four with their cause. The current-byte claims for the acceptance replay and `_unattended.py` rest on the close's own union gate, not on the phase digests.

### R4-F9 (hardening): placement of "one reviewer is one reviewer", and what the reviewer could not do
- Check: grep across the records and the review notes.
- Observed:
  - All five phase records state "One reviewer is one reviewer" (`002:107`, `003:68`, `004:61`, `005:57`, `006:60`). All of them put it in Review, while `review-and-record.md` says "The record says so in its boundary section".
  - `004`, `005` and `006` do not say what the reviewer could not do. The review notes do say it.
- Fix: the close record's boundary repeats the one-reviewer statement for every phase diff. It states that the plan review was four local readers, not the maintained panel (UG-D1).

### R4-F10 (hardening): fixes without a regression test proven to fail before the fix
- Check: the dispositions tables in `notes/phase-UG*-codex-review.md`.
- Observed:
  - UG1 finding 2: "by reading". UG1 finding 3: "n/a".
  - UG4 findings 3, 4 and 5: "prose". UG4 finding 1: prose plus one guard case.
  - UG3 finding 6 fails before the fix only because "the counted seams do not exist", so it fails structurally, not behaviorally.
  - UG2 finding 9 passes before the fix; this is declared.
  - `005:57-58` says each part B finding was "fixed with a regression test", without the finding 6 caveat. `006:61` does not say that 3 of its 5 fixes have no executable regression.
- Fix: the close record lists these exceptions.

### R4-F11 (hardening): a deferred refactor has no named target
- Where: `002-phase-UG1.md:118-123` ("deferred to the owner's choice") and `003-phase-UG2.md:132` (UG2-Q3, target "owner's choice").
- Observed: the protocol wants a named target milestone and the reason the refactor is blocked.
- Fix: the close sweep gives UG2-Q3 a target milestone, or retires it with a reason.

### R4-F12 (hardening): a selected gate exited non-zero without a recorded owner stop
- Where: `006-phase-UG4.md:17`.
- Observed: `uv run gnd doctor --project` exited 11, a G-skills check in the approved spec ledger. The record contract says a record that departs from the approved spec (a selected gate that exited non-zero) needs a separate stop. None is recorded; it is carried as UG4-Q1 "owner, local".
- Fix: the close runs doctor in a fresh adopted worktree, or records the owner's acceptance of the exit 11.

### R4-F13 (completeness): plan-text departures have no refuted-premise or plan-repair rows
- Check: `grep -n -i 'refut|depart|plan'` over the records and spec findings.
- Observed: no record has a "Refuted premises" section. Several owner-ruled departures from plan text were recorded only as spec decisions or findings (rows S10 to S17 below). The plan's own status paragraph (`notes/unattended-model-growth-plan.md:17-19`: "No phase has a spec approval. No code is written") and `:492` ("UG-D1 asks again") are stale.
- Fix: the close repairs the plan (or records why not) for each row S10 to S17. The protocol says the plan is repaired at close.

### R4-F14 (completeness): the close record's name and the component-index statement are unsettled
- Observed:
  - `project.md` names the close `NNN-milestone-close.md`, scope `milestone-close`, and notes that this "awaits the owner's confirmation". The shared contract says `NNN-close.md`, scope `close`.
  - `001-plan.md:90-93` followed the shared contract name for the plan.
  - UG-Q6, the `project.md` contradiction ("There is no component index" against the `dev/components/` section), is still open. UG2 to UG4 ran `components_index.py changed --strict` anyway.
- Fix: the close names its choice (consistency with `001` points to `007-close.md`, scope `close`) and carries UG-Q6 to the owner.

### R4-F15 (completeness): the UG1 record's skill field
- Where: `002-phase-UG1.md:4`.
- Observed: it reads `"process-phase (repository development, ...)"`. The string `project.md` prescribes, which `003` to `006` use, is `"n/a -- repository development, not a gnd-solve station over a domain model"`.
- Fix: note it in the close; do not edit `002`.

### R4-F16 (completeness): the close evidence is untracked
- Observed: `git status` shows `?? .gnd-planning/milestones/unattended-model-growth/evidence/close/`, which holds `capture_parity.py`. A digest of an uncommitted file is not a citation. Scanned: 0 absolute paths, 0 forbidden-name digest hits.
- Fix: commit it with the close record, staged by explicit path.

### No finding: absolute local paths and downstream names
- Checks:
  - `git grep` for home, `/private/tmp` and `/var/folders` patterns under the milestone directory: 0 hits.
  - `<scratch>/close-r4/scan.py` over all 115 files changed by the five UG merges and every commit message since `12daa5b7`, using the committed digest set (`tests/test_why_not_anonymity.py` FORBIDDEN, sha256 `33d12db5...`): 0 name hits, 0 absolute-path hits, positive control found.
- Outside this lens: 7 committed files elsewhere in the repository contain a home path. They are 5 files in other milestones' `evidence`/`notes`, `why-not-near-misses/evidence/close/close-gate.txt` and `tests/test_development_scaffold.py`. None was touched by UG PRs.

### No finding: review-finding dispositions
Every finding in the four `notes/phase-UG*-codex-review.md` files and in `notes/plan-review-r1-disposition.md` has a disposition, and none is undispositioned. The exceptions to the regression-test rule are in R4-F10.

## Questions the close sweep must disposition

| ID | Source path | Summary | Target named by its source |
|---|---|---|---|
| UG-Q1 | notes/unattended-model-growth-plan.md §10 | Can the evolve lane call the checker with zero allowances | answered; confirmed in the UG2 spec (G-layers, G-arch) |
| UG-Q2 | plan §10 | Option and flag names | UG2/UG3 specs (UG2-D3, UG3-D2: ruled) |
| UG-Q3 | plan §10 | How the population arrives; one file or several | UG2 spec (UG2-D1, D2: ruled) |
| UG-Q4 | plan §10 | Does a census pin the tests/ listing | answered |
| UG-Q5 | plan §10 | Which proposal schema versions carry the locator | UG3 (i) spec (UG3-D10: ruled) |
| UG-Q6 | plan §10; 001-plan.md:62; 002:130; 003:133; 004:120; 005:116; 006:108; README:53 | project.md both denies and locates a component index | owner / maintainer |
| UG-Q7 | plan §10; same sites | Downstream tracker labels on the issues | owner |
| O15 / MG3-Q2 | plan §1 table, §4 "Carried, not owned"; phase-UG3-spec.md:67 | ADD/DELETE-only proposal fails BlastRadiusReport | carried, not owned |
| MG-close-Q3, Q4, other MG rows | plan §4 "Carried, not owned" | model-growth-guardrails sweep rows | the owners that close assigned |
| O16 / UG-D4 | plan §1, §4 map | Subtype links carry no status/modality | UG-D4 (a); UG4-C1 (stated) |
| PR1-D1 | notes/plan-review-r1-disposition.md:109-112 | Exit (3 or 11) of a changed population at the same path | UG2 spec (pinned: 11, R5) |
| PR1-D2 | plan-review-r1-disposition.md:109-112 | Strict flag no-op on a model without the mode | UG3 spec (pinned: no-op) |
| PR1-H5 | plan-review-r1-disposition.md:90 (R3-H5 D) | Plan-gate record must carry the verbatim message and re-confirm UG-D2/D3/D9 | 001-plan.md (re-confirmed only by approval of the revision; owner did not re-state) |
| PR1-C7 | plan-review-r1-disposition.md:105 (R4-C7 P) | UG4-C4 has no executable result | stays "inspected", stated |
| PR1-SR | plan-review-r1-disposition.md:114-121; 001-plan.md:66-68 | No confirmation round; r1.2 has no review opinion | owner (close review instrument per UG-D1) |
| UG1-REF | 002-phase-UG1.md:118-123 | UG1 test file imports private helpers from two test modules | "deferred to the owner's choice" (becomes UG2-Q3) |
| UG2-Q1 | 003-phase-UG2.md:130 | popvalidate.py raises OverflowError on a huge integer for a Float role | a maintenance fix or the milestone close sweep |
| UG2-Q2 | 003-phase-UG2.md:131; 005:115 | _evolve_service_exit maps refusals by message substring | the milestone close sweep (refactoring candidate) |
| UG2-Q3 | 003-phase-UG2.md:132 | UG1 private-helper coupling | owner's choice (no named milestone: R4-F11) |
| UG3-Q1 | 004-phase-UG3a.md:118 | Unreadable --document on a redacted/reference model emits MG5's unprojected payload | the milestone close sweep |
| UG3-Q2 | 005-phase-UG3b.md:114; phase-UG4-spec.md:202 (UG4-D5 (a)) | Layer one accepts a digest declared twice | owner; UG4 or the close. UG4-D5 left it to the close sweep |
| UG3-Q3 | 004-phase-UG3a.md:119 | validate --document walks spans twice | refactoring candidate, the milestone close sweep |
| UG4-Q1 | 006-phase-UG4.md:107 | Worktree discovery-link receipts stale (doctor exit 11) | owner, local |
| UG4-FU | notes/ug4-issue-followups.md:1-15, :34, :41, :57 | Follow-ups drafted, not posted; "this phase's PR" placeholder (now PR 151); #74/#76 already closed | owner (UG-D0, UG4-D2 (a)) |
| UG-D0 | plan §10; README:50; 001:88-89 | Owner closes 74, 75, 76, 104 | owner. 74, 75 and 76 have been closed since 2026-11-08; 104 is open (R4-F2) |
| S10 | phase-UG1-spec.md:272-282 (plan-reading note) | Plan UG1-C1 "over all three documents" read as four documents | plan text, not edited ("approved bytes stand") |
| S11 | 002-phase-UG1.md:86-94 | T-anon method deviation from spec §8 (pattern file absent), owner-approved | recorded; no target |
| S12 | phase-UG2-spec.md:401 (UG2-D8) | Departs from plan §2.2 "count only" wording | ruled (o); plan text unrepaired |
| S13 | phase-UG2-spec.md:554 (F-i4); plan :446, :461 | RF1 successor fixture instead of re-pinned goldens (plan §4 UG2, §5, §6) | ruled; plan text unrepaired |
| S14 | phase-UG3-spec.md:287 (UG3-D13) | Same re-pin departure for UG3 | ruled (o); plan text unrepaired |
| S15 | phase-UG3-spec.md:447 (F-c3) | Plan UG1-C8 "may" pin golden proposals; UG1 did not; B9 captured them | recorded; none |
| S16 | 003-phase-UG2.md:97-104 | Source size about 2.5 times the estimate, above plan's 400 to 650 | "a finding about the estimate"; none |
| S17 | plan :17-19, :492; plan §9 UG4 row vs phase-UG4-spec.md:218 | Plan status says no spec approval and no code; "UG-D1 asks again"; §9 names the full run_tutorials.py, the spec selected --group growth | close (plan repaired at close per protocol) |
| S18 | project.md record-names paragraph; 001-plan.md:90-93 | NNN-milestone-close.md against NNN-close.md; "awaits the owner's confirmation" | owner; the close must choose (R4-F14) |
| S19 | 006-phase-UG4.md:97-98; plan §4 "Milestone close" | Close record, question sweep, close review, union gate, parity table, PR | the close |

## Claims checked and found true
- **Spec-gate digests.** Each spec gate's approved-bytes digest matches the spec at the cited commit:
  - UG1 `30835b56...` at `b3a4fda4`;
  - UG2 `7164d48b...` at `bff83562`;
  - UG3 `6c65d9f5...` at `e3b95610`;
  - UG4 `f475810e...` at `478ea2a2`.
  Each status line quotes the owner's reply with a 2026-11-07 or 2026-11-09 date.
- **Answer keys.** The UG2 and UG3 answer keys are unchanged since approval: `622a47a6...` at `c635ef9d` and `a46dc7dc...` at `e881e521` both match HEAD.
- **Phase evidence.** Every committed path cited in `002` to `006` matches its digest at the record's introducing commit and its merge commit; only the four main-side drifts in R4-F8 differ.
- **Plan gate.** The plan digest `f099eb2a...` matches at `314dc019`, as `001` pins. The plan-review snapshots match `b2678c57...` and `e7523244...`. The disposition note matches `4270b596...` at HEAD.
- **UG2 and UG3 spec gates came first.** Both rulings were committed in commits with no `src/` change (`c635ef9d`, `e881e521`), before the first source edit.
- **Append-only, apart from `002`.** Records `001` and `003` to `006` were never edited after their commit.
- **Review notes.** All four say "one reviewer, not a panel", declare in their header that they were sanitized, and carry a "Claims checked and found true" list.
- **Commit messages.** No backticks and no em-dashes in any of the 21. Every one has a Co-Authored-By line, with the parsing caveat in R4-F5.
- **Merges.** PRs 123, 139, 147, 149 and 151 are `MERGED` at `b5fda4fd`, `dd330157`, `5c6a0c5f`, `ad454305` and `dd3c35a5`. The README's PR 147 and PR 149 SHAs are correct.
- **Anonymity.** The T-anon digest-set file is unchanged (`33d12db5...` at `15ca986b` and at HEAD).
- **Paths and names.** 0 absolute paths and 0 downstream-name hits in the milestone directory, in the files changed by the UG PRs and in the UG commit messages.
