# Moving the milestone skills to the shared dev-tools copies, 2026-11-06

The owner asked for `process-phase`, `start-milestone` and `process-milestone` to be
taken from dev-tools, the repository that now holds the shared form of these skills,
instead of being maintained here by hand. This record says what was replaced, what
happened to every line this repository had written into them, and what the shared
text adds.

Source: dev-tools `2c2b0a137f2329c8d198e312dd7b8e0b0b4feb3b` (tag `v1.0`), clean.
Project at `e8a21f0e`. The change is on branch `claude/adopt-devtools`.

Units replaced: `skills/milestone/process-phase`, `skills/milestone/start-milestone`
and `skills/milestone/process-milestone`, each delivered to `.claude/skills/<name>`
and `.codex/skills/<name>` (six entries in `.devtools.toml`, 26 managed files: 24
replaced and 2 new). No folder was renamed and no old copy was removed.

Left out, because this repository has no counterpart: `skills/components`,
`skills/phase/phase-tests`, `skills/phase/process-phase`, `agents`,
`skills/phase/pytest/phase_selection.py`.

Where this repository's rules now live: `references/project.md` in the
`process-phase` folder of each root (two identical copies, 306 lines). The sync never
writes it. `AGENTS.md` has one new sentence that says so.

## Questions for the owner

Each is answered here with the choice that changes least.

1. **A public repository now takes files from a private one.** dev-tools is private.
   The delivered skills and `project.md` are ordinary files here, so everyone can read
   and use them, but only someone with access to dev-tools can run its `sync.py apply`
   or `check`. `.devtools.toml` and `.devtools-receipt.json` sit at the root.
2. **Two homes for the record contract.** The shared `process-phase` brings
   `references/milestone-record-format.md`, a generalized form of the packaged
   `src/gnd/skills/gnd-orm-core/references/milestone-record-format.md`. The shared
   skills link to it, so it could not be left out. `project.md` says the packaged file
   is the base contract and holds the GND-only parts. Is that the precedence you want?
3. **Record names.** The shared contract names the plan-gate record `NNN-plan.md`
   (scope `plan`) and the close record `NNN-close.md` (scope `close`). The existing
   records use `NNN-plan-gate.md` and `NNN-milestone-close.md`. `project.md` keeps the
   existing names. That line comes from the records, not from the replaced text.
4. **A rule the shared text changes.** The replaced `review-and-record.md` let a phase
   record name one `gate` and "list additional commands in the body". The shared
   contract requires a `gates` list, one entry per gate, when several were selected.
   The shared rule now applies. Existing records are not rewritten.
5. **The measured history behind the review-convergence rules is no longer in the
   skill text** (45 lines: the table of five panel rounds on 2026-08-23 and the
   examples drawn from it). `project.md` keeps one paragraph and the `git show`
   command that prints the old file. Say if the table should be in `project.md`.
6. **A test was edited.** `tests/test_doctor_uninstall.py` pins the file list of
   these skill folders (`LOCAL_SKILL_FILES`). Four paths were added: the two copies of
   `milestone-record-format.md` and of `project.md`. Nothing else in the test changed.
7. **Old digests in records.** `milestones/public-launch/001-phase-1.md` and
   `migration/b1-files.json`, `b2-files.json`, `b3-files.json` cite the SHA-256 of the
   eight replaced `process-phase` files. They are history and stay as written; they
   now describe bytes that are only in Git history.

## Every line this repository had written

The two roots held byte-identical copies before and hold byte-identical copies now, so
the table counts one root. A line is counted when it is in no file the sync delivers.

| File | Lines only here | Stated | Carried | Kept file | Changed | Gap | Candidate | Dropped |
|---|---|---|---|---|---|---|---|---|
| `process-milestone/SKILL.md` | 16 | 5 | 11 | 0 | 0 | 0 | 0 | 0 |
| `process-milestone/agents/openai.yaml` | 2 | 1 | 0 | 0 | 0 | 0 | 0 | 1 |
| `process-phase/SKILL.md` | 80 | 26 | 37 | 0 | 0 | 0 | 0 | 17 |
| `process-phase/references/agent-delegation.md` | 6 | 5 | 1 | 0 | 0 | 0 | 0 | 0 |
| `process-phase/references/architect-overrides.md` | 24 | 13 | 11 | 0 | 0 | 0 | 0 | 0 |
| `process-phase/references/review-and-record.md` | 24 | 6 | 13 | 0 | 1 | 0 | 0 | 4 |
| `process-phase/references/review-convergence.md` | 68 | 13 | 10 | 0 | 0 | 0 | 0 | 45 |
| `process-phase/references/spec-note-contract.md` | 11 | 8 | 3 | 0 | 0 | 0 | 0 | 0 |
| `process-phase/references/standing-rules.md` | 98 | 6 | 64 | 0 | 0 | 0 | 23 | 5 |
| `process-phase/references/verification-selection.md` | 39 | 7 | 28 | 0 | 0 | 0 | 0 | 4 |
| `start-milestone/SKILL.md` | 24 | 7 | 14 | 0 | 0 | 0 | 0 | 3 |
| `start-milestone/agents/openai.yaml` | 3 | 2 | 0 | 0 | 0 | 0 | 0 | 1 |
| **Total** | 395 | 99 | 192 | 0 | 1 | 0 | 23 | 80 |

Line numbers below are lines of the replaced file at the project commit above
(`git show e8a21f0e:.claude/skills/<file>`). `project.md` means
`.claude/skills/process-phase/references/project.md` and its twin under `.codex/skills`.
After the change, `sync.py compare` finds 141 of the 215 carried and candidate lines
word for word in `project.md`; the other 74 were reworded or merged and are accounted
for by the list below.

### Stated

The shared text says the same thing, mostly in the same sentence with "GND", "panel",
"station", "fixture model", "certification" and "this milestone's" replaced by the
general word (review, step, fixtures, opt-in gate, the protocol's).

- `process-phase/SKILL.md`: 3, 10, 21, 25, 56, 93, 112, 131-132, 137, 140, 142-143,
  147, 172, 174, 177-178, 207, 232, 262, 274-277, 282.
- `process-milestone/SKILL.md`: 3, 24, 42, 49, 72.
- `start-milestone/SKILL.md`: 3, 19, 22, 28, 32-33, 137. `AGENTS.md` and
  `CONTRIBUTING.md` are named without a link.
- `agents/openai.yaml` of both skills: the display name and short description
  without "GND".
- `agent-delegation.md`: 58-59, 63, 84-85.
- `architect-overrides.md`: 1, 19, 23-26, 31-32, 38, 43-45, 59.
- `review-and-record.md`: 9, 38, 80-81, 123, 138.
- `review-convergence.md`: 9, 42, 72, 86-87, 92-93, 106, 111, 123, 133, 162, 202.
- `spec-note-contract.md`: 20, 22, 40, 87, 89-90, 114-115.
- `standing-rules.md`: 3, 5, 79, 114, 133, 135.
- `verification-selection.md`: 14, 35, 37, 58, 111-112, 128.

Eighteen of these have no closely worded shared line; each was looked up in the
shared file and found there as a shorter or general statement of the same rule.

### Carried

All in `project.md`, under the heading named.

- "What these skills are here": source-owned skills in both real discovery roots, not
  `gnd` commands or installer-managed (process-milestone 11-12, start-milestone 15);
  `auto=true` is not a gnd CLI flag (process-phase 46); station work belongs to
  `gnd-solve` and its siblings (process-phase 39); the scaffold workflow is
  `gnd-new-project`, and planning or model skills are not invoked automatically
  (start-milestone 40-41, process-milestone 55-56).
- "Plan-review bar": the four-reviewer panel is the bar for plan review and milestone
  close, not per phase (process-phase 33-34, 138-139, 220; process-milestone 66-67;
  start-milestone 134).
- "Review instrument: the maintained panel": the source-provenance precondition, the
  six-seat credential stop, the launcher `tools/run_gnd_review_panel.py` with its
  credential handling, `--check-credentials`, `--check-auth` and `--light`
  (process-phase 149-167); the maintained panel is not activated by using a skill
  (start-milestone 138); the argv transport this project refused (review-and-record
  18-20); the panel's severity axis and the `ReviewResponse` rule
  (review-convergence 163, 185-187, with the stale line numbers `request.py:112` and
  `:327` replaced by the names `ConcernSeverity` and `ReviewResponse`); the `(p2)`
  provenance tag (spec-note-contract 25).
- "Opt-in gates: certification and recertification": the 2026-09-28 owner ruling, the
  stale installed bundle, the installed reader, the v6.3 D10 supersession
  (architect-overrides 3-6, 8, 11-16; verification-selection 8-10); certification keeps
  its own authorization under `auto=true` (process-phase 64; process-milestone 41, 43;
  start-milestone 146).
- "Test and gate commands": the 2026-09-29 ruling and the reduced v6.3 selection
  (verification-selection 16, 26, 71; process-phase 199-202; review-and-record 144);
  no `addopts` override and no `-m` for excluded lanes (verification-selection 29-30);
  missing historical inputs are not green skips (21); native skipped lanes
  (process-milestone 89); the broad-lane command and what `census` and `evidence` are
  for (verification-selection 72, 81-82; review-and-record 127); the lint gate
  (review-and-record 156); `pytest-xdist` (verification-selection 146); the frozen v5.1
  replay (verification-selection 89, 91-98, 101, 104-107, 110).
- "Standing design rules: section 0, the paid-for rules": the six rules with their
  bodies (standing-rules 12, 14, 16-20, 22, 24-32, 34, 36-38, 40, 42, 44-47, 49, 51-52,
  54-56, 58, 60-62, 64-68, 70-71, 73, 75-77; process-phase 293-294) and how a spec
  names them (standing-rules 8-9; spec-note-contract 41-42).
- "Failure classes this project has committed": the interchange field defined in
  Python-only terms, with its three traps (standing-rules 117, 119-121, 123, 125-131);
  fixtures are fixture models, the deontic half (standing-rules 98-99; process-phase
  210-211); the independence bundle carries the model (agent-delegation 93).
- "Review convergence: what this project already mechanized": `gnd exp run` and its
  closed disposition vocabulary (review-convergence 51-56).
- "Record and commit": the packaged record contract is the base contract
  (review-and-record 102-103; process-milestone 118-119; start-milestone 123-124); the
  `skill:` value of a phase record (review-and-record 110, 117); the recorded gate
  command (121); GND commit grammar with `feat(v2-p3)` (180); the host-path guard (47);
  imported historical review results (process-phase 324-325).
- "Planning a milestone": the `gnd coverage MODEL` census and the framework-milestone
  note (start-milestone 46-49); installer links are preserved (44); native acceptance
  lanes (131).

Written into `project.md` without a source line in the replaced text: the first
paragraph (these files are synced, write rules here), "There is no component index in
this repository", the record-names line of question 3, the sentence that no project
instrument is defined for a phase diff, and the pointer of question 5.

### Changed, candidates and dropped lines

Gaps: none. No script was replaced, and no line needed a place only a synced file has.

Changed: `review-and-record.md` 125, "list additional commands in the body", against
the shared `gates` list. Question 4.

Candidates, carried to `project.md` for now, that dev-tools could take:

- "A rule made unfalsifiable by how the fixtures were built" (standing-rules 102,
  104-108): a general failure class the shared `standing-rules.md` lacks.
- "Implementation traps worth a checklist", six traps (standing-rules 138, 140,
  143-157): general lessons, none specific to GND.

Dropped, each read first:

- `process-phase/SKILL.md` 317, 319-323, "Public staging boundary": P1, P2 and P4 of
  the public-launch milestone, which closed with record `010-public-launch-close.md`.
  Its last sentence is carried.
- `process-phase/SKILL.md` 113, 127, 129-130, 141, 208-209, 308-311: how often a defect
  was once found, the corpus-first pilot in the transition phase, the five-round
  measurement. History; the rule each one supports is in the shared text.
- `review-convergence.md` 3-8, 13, 15, 17-21, 23-29, 67-71, 88-91, 103-104, 122,
  129-132, 146-153, 188: the measured record of five panel rounds and the examples
  drawn from it. History. Question 5.
- `standing-rules.md` 83-85, 112-113: "found five times in a single spec draft",
  "five of eight agreed concerns". History.
- `review-and-record.md` 59-61 and 189: what a self-audit once found, and the commit
  once garbled by backticks. History; both rules are in the shared text.
- `verification-selection.md` 19-20, 22-23: what P1 did not import and the P1 scaffold
  command. That phase is closed.
- `start-milestone/SKILL.md` 12-14: where the replaced text had been adapted from. The
  text now comes from dev-tools and the receipt records its origin.
- `agents/openai.yaml` of both skills, line 4: a default prompt naming the
  pyrel-applications milestone, which closed with record `014-milestone-close.md`.

## What the shared text adds

| What arrives | Decision |
|---|---|
| `references/milestone-record-format.md`, a new file | Accepted, because the shared skills link to it. `project.md` names the packaged contract as the base. Question 2 |
| Record names `NNN-plan.md`, `NNN-close.md`, scopes `plan` and `close` | Answered in `project.md`: the existing names stay. Question 3 |
| The `gates` list and the `rulings` field of the record contract | Accepted as shipped for new records. Question 4 |
| Commit example `feat(phase-N)`, `skill:` value and gate command in general words | Answered in `project.md` with GND's grammar, value and `uv run pytest -q` command |
| Provenance tag `(r1)` for a first review round | Answered in `project.md`: `(p2)` and `(o)` stay |
| Default plan-review bar, "one independent reviewer in a different tool" | Answered in `project.md`: the four-reviewer panel |
| Default reviewer for a phase diff, one reviewer in a different tool with the prompt on stdin | Accepted as shipped; `project.md` says no project instrument is defined for a phase diff |
| Component-index steps in `process-phase` (steps 1, 3, 6), `start-milestone` and the spec's Design section | Answered in `project.md`: there is no component index here, skip them |
| The go-ahead for delegating to subagents is asked once at invocation; `auto=true` does not cover it; without it one reader works sequentially | Accepted as shipped |
| A draft spec that `start-milestone` wrote is the starting point of the first phase | Accepted as shipped |
| The known-red proof is owed when the red is first met, normally at step 3 | Accepted as shipped |
| Step 6 has no stop while the commit stays inside what the step 2 gate approved | Accepted as shipped; the packaged contract already has "When a record is due" |
| Four in-place exceptions to the append-only spec (status line, a decision row's ruling, an owner amendment, a corrected argument) | Accepted as shipped |
| Plan repair at milestone close: amend the plan for each refuted premise or open-questions row, and cite the amended plan's SHA-256 in the close record | Accepted as shipped |
| `start-milestone`: until the plan-gate record exists, the plan's status line says whether the plan review ran | Accepted as shipped |
| A three-part format for standing rules (name, what it prevents, how a spec discharges it) | The six carried rules keep the prose they were written in |

The eight replaced reference files and the three skill files were read as lists of the
lines only the shared file has. The new `milestone-record-format.md` was not read line
by line against the packaged contract.

## Checks

- `sync check`: 26 files managed, 0 problems; the `.claude` and `.codex`
  copies of each skill are identical.
- Tests, run on `main` at `e8a21f0e` and on this branch with the same
  interpreter: the 21 test files that read the skill folders, `AGENTS.md`,
  the planning records or the list of tracked files (the skill tests, the
  skill and twin checks, the file-list pins, the release and pull-request
  policy checks). Before: 531 passed, 0 failed. After: 531 passed, 0 failed.
- The milestone records (`.gnd-planning/milestones`) are unchanged.
- Not run: the whole suite and the opt-in lanes. Nothing under `src/`
  changed. A wider set of 83 test files on `main` gave 25 failures in the
  structure tests (`test_rf4` to `test_rf8`, the docs prose check, the
  collection check, one judge-skill test). Those failures were already on
  `main` before this change and are not related to it.
- Not done: a line-by-line read of the new `milestone-record-format.md`
  against the record contract this repository already has.
