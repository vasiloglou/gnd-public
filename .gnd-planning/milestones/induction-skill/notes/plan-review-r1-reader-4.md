# Reader 4 -- measurability and the end-to-end demonstration

Retained text of the reader's returned report. Local edits: scratch paths read
`<scratch>`.

Reviewed plan SHA-256 526ab075473ab60cf2e8090fe7c0f177aa54e4a82b7fce83af1cb50d1919c411 and spec SHA-256 0510b5275622f8b38aff8865500d40601c9ea4e3ce3b2e58ed2fcf5b9363515a. Both match.

**Verdict: request-changes.** The IS1 spec is close to approvable and needs only hardening. Completion predicate 2 (IS2), as written, cannot be demonstrated or measured with the tools and tests the plan names. Four blocking findings follow; each can be fixed by naming edits in the plan.

Scope:
- **Read in full:** both subjects; `docs/tutorials/learn-rules.md`; `docs/how-to/learn-rules-commands.md`; `tests/test_ik6_walk.py`; `tests/test_replays.py`; `tools/record_skill_sessions.py`; the refunds example (README, `stand_in_learner.py`, `labels.json`); `docs/reference/ilp-bridge.md`; `docs/assets/replays/replays.json`.
- **Read in part:** `tools/run_tutorials.py` (the `induced` group); the head of `tools/render_replay.py`; the course-planner replay markup; the IK6 record (Boundary, Open questions, Refuted premises); `tests/test_ik6_skill_census.py`; the `GROUPED_COMMANDS` line of `tests/test_public_packaged_invocation_guards.py`; the `gnd-model-evolve` description.
- **Ran, only in `<scratch>/reader4/walk`:**
  - The commands-page walk, with the repo's `.venv/bin/gnd` against a copy of refunds. Every documented output and exit reproduced: measure 2/4; 40 rules searched; import exit 0 with support 4/4; faulty import exit 3 with `coverage-mismatch ... ['north']`; discover `EMITTED 10` / `SUPPRESSED declared=1 spanning-uniqueness=3`.
  - Discover without `--families`.
  - `gnd export ilp --target popper`.
  - A harness that imports `record_skill_sessions.kept_stream` and feeds it synthetic events.
- **Not run:** `record_skill_sessions.py` itself. No network was used. `popper` is not installed; `swipl` is.

## Findings

- **R4-F1** (blocking, high): **The named recorder cannot record tutorial steps 2 and 4, and its replays would hide the learner's claim.**
  - **Where:** plan IS2-C1 (l.221-223) says only that the recorder is "extended for the refunds example"; §9 sweep l.318.
  - **Evidence:**
    - `tools/record_skill_sessions.py:57`: the `TOOLS` allowlist is `Bash(gnd *),Bash(<repo>/.venv/bin/gnd *),Bash(shasum *),Read,Write,Edit,Glob,Grep`. `python stand_in_learner.py …` is outside it, so Claude Code would deny the learner run in steps 2 and 4.
    - `kept_stream` (l.92-97) keeps tool output only for a plain `gnd` command, or for a target that starts with `<workspace>`. Reproduced by feeding it four tool calls:
      - `python stand_in_learner.py ilp learned` became `[37 bytes of output not kept]`;
      - `gnd measure … | grep fired_on` became `[37 bytes of output not kept]`;
      - `python3 <workspace>/stand_in_learner.py … --also-claim north` became `[37 bytes of output not kept]`;
      - only the plain `gnd import ilp-rules …` kept its output.

      So the line "learned: … V1 > 500 covers harbor, market, airport, station" (step 2's whole result) and the "deliberate mistake" line (step 4) can never appear in a replay. A piped measure loses its numbers too.
    - Further hardcodings:
      - `EXAMPLE` is hardcoded to the course example (l.29);
      - the gate check requires the string `phase-PL18-skill-recording` (l.234);
      - `finish()` lists course sources in the manifest (l.203-205);
      - `results.json` records `"example": "course"` (l.241).
    - The stop rule (l.158-165) breaks once `model_file(workspace)` validates and `done` is true. Refunds ships a valid `model.orm.yaml`, and gnd-induce never edits the model. So without a new `done` predicate every conversation ends after turn 1.
  - **Fix:** name the recorder edits and test them before any paid run:
    - an example parameter;
    - an allowlist entry for exactly `python stand_in_learner.py *`;
    - a keep rule for that command's output;
    - a gate-record parameter;
    - a sources list per example;
    - a per-skill `done` predicate (for example, "the named proposal file exists", or "the faulty import exited 3").

    Add a unit test of `kept_stream` over a learner call. State whether piped `gnd` commands are allowed in a recorded run.

- **R4-F2** (blocking, medium): **`tests/test_replays.py` rejects any refunds replay, but the plan says replays are "pinned by" it with no edit.**
  - **Where:** plan l.49-51, §3 l.182-183 (`src/gnd/examples/refunds/skill-sessions/<model>/run-N/`, `docs/assets/replays/refunds-*.svg`), §9 l.307.
  - **Evidence:** `test_each_replay_is_named_after_the_run_it_replays` (`tests/test_replays.py:59-73`) requires every source to match `src/gnd/examples/plan_apps/recordings/...` or `src/gnd/examples/plan_apps/skill-sessions(-evolve)?/claude-(\w+)/run-(\d)/turn-01\.jsonl`. It also requires the name to be `course-<skill>-<model>-run-N`. A `refunds-*` entry with a refunds source fails the `assert skill, source` line. The source pattern also accepts only `turn-01.jsonl` as the first source. In the refunds layout, sources would come from `refunds/skill-sessions/...`, not `plan_apps/skill-sessions-evolve`.
  - **Fix:** list the `test_replays.py` generalisation (an example and skill map) as a named IS2 edit. Make it red first: a refunds entry fails today, then passes after the edit.

- **R4-F3** (blocking, medium): **Step 6's "check the market week again" is a `gnd check` request that no skill owns, so "a skill prompt at every step and no plain request" (l.47) is unreachable.**
  - **Where:** tutorial l.244-255 (the prompt "Check batches/market.yaml against the model again."); commands page l.170-178 (`gnd check`).
  - **Evidence:** the plan §2 intents table (l.137-142) has score, discover, learn and hand off; there is no check intent. The `gnd-model-evolve` description excludes this explicitly: "Not for … population checking". So this sub-step stays a plain request. The page also loses its only before/after advisory evidence (the "601, for 750" claim pair).
  - **Fix:** do one of the following:
    - add a fifth "re-check a population after apply" intent to gnd-induce (one more fenced `gnd` line, so T7's count of 4 becomes 5);
    - route the check to an existing skill that owns `gnd check`, if one does;
    - or narrow the predicate and label this sub-step as a plain request on purpose.

- **R4-F4** (blocking, medium): **"Every number the page states still has its string pair" (l.52-53) has no test that fails when a number lacks a pair, and it is already false at baseline. Nothing ties a recording's numbers to the pairs either.**
  - **Where:** plan l.52-53 and IS2-C3 l.229-230; `tests/test_ik6_walk.py:173-189`.
  - **Evidence:**
    - `TUTORIAL_CLAIMS` is a hand list of nine pairs. It does not cover numbers the page states, such as the 5/2/3 grouping of discovered rules (l.203-205), "differed by one week, north", the exit 3, or "north's largest refund is 120". The commands page does not print the 5/2/3 split at all.
    - Each pair checks only tutorial prose against the commands page. A recording that shows other numbers still passes everything. Discover without `--families` printed `EMITTED 20` / `SUPPRESSED declared=1 spanning-uniqueness=3 redundant-subset=6 redundant-frequency=5` in the scratch copy, against the page's `EMITTED 10`. An agent that misses the family mapping would record 20, and only human review would notice.
    - No test checks that the prompt the page shows equals the recorded user turn. `replays.json` carries `said`, but `test_every_replay_on_a_page_is_listed_and_followed_by_its_transcript` checks only the title in the aria-label.
  - **Fix:**
    - Replace "every number" with "every number listed in `TUTORIAL_CLAIMS`", and decide the 5/2/3 row explicitly.
    - Add a third column per pair: the recording that shows it. Test that the commands-side string appears in that recording's kept tool output, or that the page explains the divergence beside the replay.
    - Test that each "You type" fence beside a replay equals that replay's `said` (the recorder's declared turn).

- **R4-F5** (hardening, high): **The residual "That evidence is IS2's recordings" overclaims. Most declared branches have no case that can fail them.**
  - **Where:** plan IS1 Residual l.216-217; spec "Honest limit" l.201-203; D10 l.338.
  - **Evidence:** the six tutorial steps exercise intents score, discover, learn and hand off, and reactions exit 0 (steps 1, 3, 5) and exit 3 (step 4). Nothing exercises:
    - exit 11 (existing `--out`);
    - "any other non-zero" (for example, exit 6 in D16 expected-state mode; refunds has no expected-state manifest);
    - the absent-learner stop ("no learner named X is installed", spec l.103);
    - R-b, R-c or R-d as behaviour. A recording only shows whether the agent happened not to retry after the refusal. No turn asks it to "just add north and import again".

    T8 checks sentences only, and spec l.201 says so. The plan then credits the recordings with what they do not cover.
  - **Fix:** list the uncovered branches as residuals by name. Alternatively, script adversarial user turns into the recording conversation. Examples: "use popper", where Popper is absent, should give the named stop; "write to learned.proposal.json again" should give exit 11 and a new path; "make the import pass", after the exit 3, should give a refusal to edit the claim. Give each a `done`/verdict predicate in `results.json`.

- **R4-F6** (hardening, medium): **The Popper path in the learn intent has no evidence it can learn this example's rule. Popper is likely unable to produce a separating rule here.**
  - **Where:** plan §2 l.141 (`--target neutral|popper`); D4 l.332 ("or an installed `popper`"); spec l.101-106.
  - **Evidence:** `gnd export ilp --target popper` (scratch) writes only variable-variable comparisons, `type(gt_t_amount,(t_amount,t_amount))`, plus `magic_value_type(t_amount)`. With no magic-value support, a body can compare only two bound amounts in the same week. Every week, clean or flagged, has at least two distinct amounts, so any such body covers all eight weeks and cannot separate them (my inference; Popper was not run). The sibling note says mainline Popper ignores `magic_value_type`; I could not confirm that offline. `ilp-bridge.md:208-209` already says the rendering "has not been run against a real Popper".
  - **Fix:** in the skill and the tutorial, state that the Popper branch is unproven on this example and is not demonstrated in this milestone. Keep it a named branch with its stop sentence. Do not let C0/C2 prose imply that a real learner could reproduce step 2.

- **R4-F7** (hardening, medium): **The red-first protocol contradicts itself for T5 and T9.**
  - **Where:** spec §5 l.60-62 ("each moved pin (T2..T7, T9) exits 1 on the pre-IS1 tree with the new skill present"); §8 l.179 ("edits are committed before the skill exists"); T5 l.188 ("red with the skill and no row").
  - **Evidence:** T9's pinned census (`tests/test_ik6_skill_census.py:42-45` reads `git ls-files` at HEAD and asserts 65) is green before the skill exists and green after. The failure that D8 fixes appears only when the skill is present and the test is unpinned. T5 likewise needs the skill present. "Before the skill exists" cannot produce either red.
  - **Fix:** state two red reproductions in `regressions-red.txt`:
    - pin edits (T2-T4, T6, T7) over the pre-IS1 tree;
    - the unchanged T5 and T9 over a tree with the skill added, before the AGENTS.md row and the census pin are added.

- **R4-F8** (completeness, medium): **IS2-C3 and IS-R7 have no named test, and IS-R7 conflicts with the replays.**
  - **Where:** IS2-C3 l.227-230; IS-R7 l.73; §9 l.307.
  - **Evidence:**
    - No listed consumer checks that each `## N.` section carries a `/gnd:` prompt, that "There is no skill for this step" is gone, or that the "What you did" table names a skill on every row.
    - IS-R7 says the business page shows "never Python or `gnd` commands". A replay transcript, though, prints the agent's commands: `course-model-evolve-haiku-run-1.txt` has 12 lines containing `gnd `, for example `Bash gnd evolve --help`. Steps 2 and 4 would show `python stand_in_learner.py`.
  - **Fix:**
    - Name a test such as `tests/test_learn_rules_page.py` that checks the three structural conditions and fails on the current page.
    - Amend IS-R7 so that replay transcripts are an explicit exception.

- **R4-F9** (completeness, low): **One "learn" intent covers what the tutorial splits into steps 2 and 3.**
  - **Where:** plan §2 l.141; tutorial l.106-151.
  - **Evidence:** step 2 must stop at the learner's unchecked claim ("Nobody has checked it yet"). Step 3 then imports. A skill that always runs export, learner and import together cannot produce step 2's recording as written.
  - **Fix:** state in the skill that the learn intent can stop after the learner run when asked, or merge steps 2 and 3 in the tutorial rewrite (C0 decides).

The rest held up. The IS1 pins (T1-T4, T6, T7, T10-T16) are concrete, with named files and expected exits. T8's seeded R-c case and T14's seeded absolute path make the sentence tests falsifiable. The commands page reproduces exactly in a scratch copy.
