# Reader 3 -- protocol, authority, compatibility and privacy

Retained text of the reader's returned report. Local edits: none beyond this
header.

Reviewed plan SHA-256 526ab075473ab60cf2e8090fe7c0f177aa54e4a82b7fce83af1cb50d1919c411 and spec SHA-256 0510b5275622f8b38aff8865500d40601c9ea4e3ce3b2e58ed2fcf5b9363515a: both **match**. The snapshots are byte-identical to the working copies in `notes/`.

**Verdict: request-changes**

**Scope.** I read both subjects in full. I also read AGENTS.md, CONTRIBUTING.md (grep pass), the start-milestone SKILL.md, the process-phase SKILL.md, and these process-phase references: spec-note-contract, standing-rules, review-convergence and verification-selection (the ledger part).

From the induced-knowledge milestone I read README.md, the relevant rows of 010, 012 and 014, and the census test with its `skill-census.md`. I read the recorder, renderer and replay files: `tools/record_skill_sessions.py`, `tools/render_replay.py` (header), `tests/test_replays.py`, `docs/assets/replays/replays.json`, `docs/agents/recorded-sessions.md` (the gate and credential sections), the `skill-sessions-evolve` layout, README and manifest, `tests/test_plan_app_docs.py` and the PL18 gate record 019. I spot-checked the pinned tests: `test_solve_successors.py`, `test_packaged_skills.py:67`, `test_public_packaged_invocation_guards.py:131`, `test_ik6_walk.py`, `pyproject.toml:73` and `test_public_distribution_runtime.py`.

I compared the baseline `077f46e` with `origin/main` and with the local sibling branches, using git read-only. No tests were run, and the recorder was not run. Every claim about a test result below comes from reading the code.

What holds up:
- `auto=false` is stated.
- D13 is quoted, and the plan says the selection covers the instrument only.
- Contributions go through a PR only (plan 299-300).
- The installer generates the links (IS-R8; spec 157-159).
- The C0 checkpoint is labelled a mockup, and the tutorial does not use it (spec 228-232).
- The plan does not edit any FROZEN skill.
- No station number changes.
- No absolute paths or downstream names appear anywhere in the milestone directory (grep came back clean).
- The cited sources are accurate: 010:69, 010:174, 012:151-152, `test_packaged_skills.py:67`, `test_ik6_skill_census.py:45` and `GROUPED_COMMANDS` at :131.

## Findings

- **R3-F1** (blocking, medium): **An approved sibling milestone that changes the same contract and files is not handled.**
  - *Where:* plan IS-O16 (line 124), §3 prerequisites (187-189), §6 sibling row (271), and "Not owned here" (127-129). That section points to "the ILP-bridge follow-up" without naming it.
  - *Evidence:* `origin/main` (PR #48, after the `077f46e` baseline) carries the approved `ilp-learners` milestone: plan r3, approved 2026-10-27. Its approved plan says IL1:
    - adds a learner registry;
    - adds the `type-confused-join` refusal and a `learner-mismatch` refusal for neutral run records;
    - adds a real Popper run over the refunds export.

    Its §5 says IL2–IL5 add `--target` values and a new `gnd import mined-rules`. It also says IL "inspects and edits" the skill pin sites that name `gnd export ilp`, which are `gnd-export` and `gnd-dev-session`, the files IS1 edits. Its IL6 runs the refunds example and updates docs, skill surfaces and "the skill census".

    The IS plan's control for sibling work ("IS1 edits no docs page those sessions own; IS2 rebases after they merge") does not cover any of this. IS2's recordings of the learn step would be made against an import contract that IL1 changes.
  - *Fix:*
    - Name `ilp-learners` as a concurrent dependency in §1, §3 and §6.
    - Read its approved plan into the harvest.
    - Say whether IS2 records before or after IL1 merges, and pin the commit the recordings bind to.
    - Coordinate the shared edits to `gnd-export` and `gnd-dev-session`, and IL6's census edit.
    - Re-baseline on current main, or state why `077f46e` stays the baseline.

- **R3-F2** (blocking, medium): **The proposed D8 census pin conflicts with a pending sibling edit to the same closed record.**
  - *Where:* plan D8 (336), spec §6.3 last row (155) and T9 (192).
  - *Evidence:* sibling branch commit `33827e2` (the "docs(IK-close)" reader-four docs gaps, which plan §6 expects to land) edits two things:
    - a packaged skill file, `gnd-orm-core/references/representation-format.md`;
    - its census row in `induced-knowledge/skill-census.md`, which becomes `IK1, IK2, IK-close`.

    The census test reads `skill-census.md` from the working tree, but under D8 it would compute `git_phases` from `log ...077f46e` (`test_ik6_skill_census.py:59-74`). That gives {IK1, IK2} for this file. So `test_t4_each_changed_cell_names_the_phases_git_records` goes red whichever PR merges second.

    This also shows the IK census is still being edited after close, so `077f46e` is not its end commit.
  - *Fix:* either pin to the merge commit of the last IK-scoped change and name it at the IS1 gate, or read `skill-census.md` at the same pinned commit (`git show`). Add a D8 row that covers later IK-close-scoped edits, and coordinate with that sibling.

- **R3-F3** (blocking, medium): **The IS1 gate breaks the verification-selection protocol.**
  - *Where:* spec §8 proposed gate (205-210) and T16 (199).
  - *Evidence:*
    - `verification-selection.md:39-50` requires a selection ledger (`run`/`inherit`/`cadence`, input boundary, invalidation) "before the owner gate". The spec has none.
    - `verification-selection.md:29-30` says not to use `-m` to bring the `distribution` lane into an ordinary gate, but the second gate command does exactly that.
    - The first command lists `tests/test_public_distribution_runtime.py`, whose `pytestmark = pytest.mark.distribution` (line 14) is deselected by `addopts` (`pyproject.toml:73`). The gate therefore names a test it never runs.
  - *Fix:* add the ledger. Either turn the distribution-lane rows into an explicit owner-selected decision row or give them a `cadence` disposition. Drop the deselected file from the ordinary command, or move it into the selected lane.

- **R3-F4** (hardening, medium): **IS-R9 rests on a test that cannot fail on a committed edit.**
  - *Where:* plan IS-R9 (75) and the implementability row (320); spec T13 (196).
  - *Evidence:* `test_solve_successors.py:33` computes `FROZEN_SKILL_BASELINE` from the current tree when the module is imported. `test_t16` (79-81) then compares the current tree against that same value, so an edit to a frozen skill committed in IS1 passes. This is the standing-rules "declared branch with no case that can fail it" class.
  - *Fix:* make T13 check `git diff --quiet <IS1 base> -- src/gnd/skills/<frozen>` for each frozen skill, with a seeded negative control. Do this in `test_induce_skill.py` and leave the closed test alone.

- **R3-F5** (hardening, medium): **The IS2 recording authority and paid-run protocol is left unsaid, and reusing PL18's gate would transfer another milestone's authorization.**
  - *Where:* plan IS2-C1 (221-223), the §9 sweep row (318), the §6 cost row (274) and D11 (339).
  - *Evidence:*
    - `record_skill_sessions.py:233-235` only accepts a gate record containing `phase-PL18-skill-recording`. That record (019:5, 18-19) is scoped to course recordings with Haiku and 2 runs.
    - The tool hard-codes the course example: `EXAMPLE` at :29, `sources` at :203-205, and `"example": "course"` at :241.
    - start-milestone:74-75 says "never transfer another milestone's delegation".
    - The recorder also strips `ANTHROPIC_`/`OPENROUTER_` variables (:123) and relies on Claude Code's own login. The plan's "credentials from a trusted environment" does not say that. `recorded-sessions.md:240-243` records an earlier session where the owner did not allow an env-file wrapper.
    - D11 sets no spend ceiling, and start-milestone:104 asks for relevant budgets.
  - *Fix:* state in the IS2 outline and D11 that:
    - a new IS-scoped gate record will exist;
    - the recorder's scope check changes to accept it (a named edit);
    - the credential path is Claude Code's own login with no env import;
    - user turns are declared before any run (as in precedent);
    - there is a run bound and a cost ceiling.

- **R3-F6** (hardening, medium): **The proposed actor instruction invites the git-identity leak that has happened before, and the existing guard would not cover the new recordings.**
  - *Where:* spec §6.1 "Fix the inputs first" (82: "`--actor` (the user)"); plan §2 inputs (144-146); plan §3 recordings home (182).
  - *Evidence:*
    - The `skill-sessions-evolve/manifest.json` "rebound" entry records that Claude Code filled audit fields from git, and the email had to be redacted later.
    - The email check, `test_plan_app_docs.py:216-221`, only scans `plan_apps/` folders, not `src/gnd/examples/refunds/`.
    - The recorder's leak needles (`record_skill_sessions.py:180-189`) cover the email and its handle but not `git config user.name`.
    - The commands page uses a synthetic `--actor reader` (`learn-rules-commands.md:128`).
  - *Fix:*
    - Have the skill ask the user for an actor id, never derive one from git or the environment.
    - Use a synthetic actor in IS2's scripted turns.
    - Extend the email and name scan to the refunds recording home.
    - Add `user.name` to the recorder's needles.

- **R3-F7** (hardening, medium): **Two existing replay pins block the IS2 recordings, and the plan names neither edit.**
  - *Where:* plan §3 (182-183) and IS2-C1.
  - *Evidence:* `test_replays.py:60-73` (a pin from the closed PL18 work) requires two things:
    - skill-session sources must match `src/gnd/examples/plan_apps/skill-sessions(-evolve)?/claude-*/run-N/turn-01.jsonl`;
    - replay names must be `course-<skill>-...`.

    Recordings under `src/gnd/examples/refunds/skill-sessions/` with `refunds-*` names fail both. Separately, `test_ik6_walk.py:73-75` scans every file under the refunds example. That is a useful backstop, but it is an IK test the plan says stays unedited.
  - *Fix:* name the `test_replays.py` naming-rule edit, and a red-first case for it, in the IS2 outline. Also state that the refunds recordings are covered by the `test_ik6_walk` T3 scan.

- **R3-F8** (hardening, low): **The red-first claim for T9 cannot be met as written.**
  - *Where:* plan predicate 1 (43-44), spec §5 (61-62), the red-first note (179-180) and T9 (192).
  - *Evidence:* the pinned census test is green on the pre-IS1 tree by design, since the tree has 65 files at the pin. "Each moved pin (T2..T7, T9) exits 1 on the pre-IS1 tree" is therefore false for T9. Also, "red before the skill exists" (179) and "with the new skill present" (61) are two different controls.
  - *Fix:* state T9's real control: the old HEAD-reading test goes red with the skill present, and the pinned version goes green. Use one consistent definition of "pre-IS1 tree".

- **R3-F9** (hardening, low): **Two different byte sets are both called "r1".**
  - *Where:* plan line 3.
  - *Evidence:* commit `3b3dc36` holds r1 with D13 as "ask the owner". The reviewed snapshot, which is uncommitted, is also called r1 but records D13 (o) and has 14 changed lines in §8 and §10. A plan gate citing "r1" would be ambiguous.
  - *Fix:* bind the round-1 subject by SHA-256 in the disposition (as `ilp-learners` did with `manifest.json`), commit the snapshot, and give the next amendment a distinct label.

- **R3-F10** (hardening, low): **Owner statements are cited without a source or date.**
  - *Where:* plan 102 ("The owner asked for every carried item to be taken care of"), IS-O6 (114), IS-O13 (121) and D12 (340).
  - *Evidence:* these lines carry no repository record, quote or date. The `ilp-learners` README quotes each owner answer. These statements should not be mistaken for rulings.
  - *Fix:* quote each one with its date, or label it as recorded only in the owner's conversation. Keep the "(o)" tag for dated rulings only.

- **R3-F11** (completeness, low): **Spec §4 binds the standing rules but not the plan's own §0 rules.**
  - *Where:* spec §4 (38-56).
  - *Evidence:* spec-note-contract:38-44 requires each of the plan's §0 rules to be bound by name or argued inapplicable. IS-R1, IS-R6 and IS-R7 are not bound anywhere in the IS1 spec, and IS-R7 bears on C0.
  - *Fix:* bind IS-R1..IS-R9 by name, or give each a one-line inapplicability argument.

- **R3-F12** (completeness, low): **Stale wording and one misplaced citation.**
  - *Where:* plan 293-295 and plan 31-32.
  - *Evidence:* lines 293-295 still say "Once one is chosen" after D13 was chosen. Line 31-32 attributes "four of the six steps" to "record 010, Boundary, F8", but the phrase is in the IK6-Q1 open-questions row (010:181). F8 is at 010:174. Also, review-convergence:57-58 asks for the round budget "in the artifact's own bytes", while the plan defers it to the disposition (IK precedent).
  - *Fix:* reword line 293, fix the citation, and either declare the round budget in the plan or note the IK precedent.
