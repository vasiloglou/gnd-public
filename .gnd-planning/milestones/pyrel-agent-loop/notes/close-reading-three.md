# Close reading THREE: evidence and honesty (pyrel-agent-loop @ 1c30525)

## Blocking

B1. A username is committed in the evolve recordings. The string `user:<user>` (redacted here) (the owner's handle) is the proposal `audit.actor_id` in
`src/gnd/examples/plan_apps/skill-sessions-evolve/claude-haiku/run-1/turn-01.jsonl:107,167,214` and `run-2/turn-01.jsonl:99,105,168,261`.
The leak search missed it because its needles are only `home.name` (`nikolaosvasiloglou`), path prefixes, key prefixes and temp-dir parts (`tools/record_skill_sessions.py:179-183`).
The README (`skill-sessions-evolve/README.md`, "What was kept") implies the redaction is complete. The handle is not in docs/ or the replay assets.
Fix: redact it to `<user>` (the manifest records the change, as `rebound` does), add the git/email local part to the needles, and disclose the redaction.

No other claim I checked was false.

## Hardening

H1. Record 021's evidence is stale for its own phase. All four changed paths match df4de9f, not HEAD: course-planner.md, clinic-refills.md, render_replay.py and replays.json (`021-phase-PL18.md:27-32`).
They were then changed by 26af6fb, 7346f72, d6f8084 and a1d9452. Those commits are described in the record's later "Owner feedback" sections, but the evidence block was never re-hashed.
New files are not bound at all: `skill-sessions-evolve/manifest.json`, `docs/explanation/what-is-pyrel.md`, and the new tests.

H2. Later edits are not re-recorded:
- `src/gnd/examples/plan_apps/core.py` and `tests/test_plan_apps.py` (017:25,27) were changed in 05eedd7 (PL17), but 020's evidence (`020-phase-PL17.md:24-30`) does not list them.
- `tools/record_plan_apps.py` (020:27) and `tests/test_pyrel_rules_derivations.py` (014:22) were changed in PL18 (df4de9f, 6dcc4d9) without a new hash.

Every other mismatch is explained by a later record: pyrel_rules.py and pyrel.md by 017, test_pyrel_rules_families by 015, test_pyrel_rules by 016. Of 50 entries in 013-021, 21 do not match HEAD, and every one matches the bytes at its own phase commit.

H3. Gate 018 has no amendment for its two discarded launches. Together they made 275 paid calls over 135 runs, against the 125 runs authorized (`018-recording-gate-PL17.md:27,31`).
They are disclosed in `recordings/README.md:47-53` and CAVEATS.md, but gate 019 recorded its own discards as amendments and 018 did not.

H4. The PL4 recording reached outside gate 005. The gate says "this run reads no key" and that hosted keys are not authorized (`005-recording-gate.md:27-28`).
Even so, a key-bearing Claude call was attempted, and the permission classifier refused it (`006-phase-PL4.md:59`). It is disclosed, but it was not authorized.

H5. The evolve README overstates one point. It says both runs read "the approvals example's model" (`skill-sessions-evolve/README.md:41`), but only run-1 did (a Read call); run-2 read only `models.py`.
The README also leaves out three things:
- run-1 grepped `<home>/.claude/...`, outside the workspace;
- both runs wrote scripts to `<tmp>`;
- the Read and Grep tools could still reach `<repo>`, including the shipped proposal, despite the plugin copy (amendment 3).
Neither run used the shipped proposal.

H6. The `declined` outcome hides earlier failed attempts. claude-haiku/access runs 1-2 gave an unusable answer before declining, but the table shows "5 declined" (README:19). `model-runs.md:47` says the Claude models "planned within the rules at the first attempt".

H7. The bytes behind the PL17 recording are not in git. The recorded `plan_app_bot.py` digest (186bbfd…) matches no commit. The drift is declared, but those bytes cannot be checked from git.

## Verified (no finding)

- **Manifests.** All 386, 19 and 7 file digests match, with no files missing or unlisted. Source drift is all declared: recordings `drift`, and skill-sessions README "Sources changed".
- **Path and key search.** No other local paths or keys in the three recording directories.
- **Results table.** `readme_table(results.runs)` is byte-equal to the README table block.
- **Recordings README figures** all match the recording:
  - outcomes: 40 first, 9 repaired-rule, 11 repaired-format, 12 declined, 53 refused;
  - Claude cost $0.6249 and OpenRouter cost $0.0135;
  - host counts: Novita 26, DeepInfra 34, Parasail 68, DeepInfra 3, Parasail 69;
  - four Haiku clinic runs show 2026-10-14;
  - at most 459 completion tokens per call, under the 2000 cap.
- **Skill-session READMEs.** Costs (0.19, 0.15, 2.46, 17.41; 0.24, 0.22), denial counts (3 and 7) and turn counts match the result events. 84 of 87 and 51 of 51 thinking blocks are empty, and none has a signature.
- **Gates.** Model, run and turn limits were respected: 5×5×5 with at most 3 attempts; 2 per model and at most 6 turns; Haiku ×2 for evolve. The skill-sessions caveat discloses the beyond-`Bash(gnd *)` reads.
- **Docs spot-checks (15), all true:**
  - clinic: ten first, nine refilled one drug on 2024-03-10, and haiku run-3 used two drugs on 2026-10-14 (`clinic-refills.md:179`);
  - `llama-3.2-3b/course/run-2` is the only course run refused on a rule and then accepted, and it repaired with MATH220 alone;
  - Claude course runs: all ten mention MATH220, STAT210 and CS340 (`course-planner.md:340`);
  - claude-default lease: all five wrote "1450" and ran exit 3 then 0 (`lease-schedule.md:57`);
  - access: all ten Claude runs declined (`access-requests.md:85`);
  - only small models were repaired after a rule refusal;
  - "many" = 82 of 180 attempts were unusable;
  - four chained-command denials and the verbatim `semantic:reading-placeholders` errors (`course-planner.md:129-157`);
  - evolve: three refusals (two chained, one Python), the media-type refusal, and the cap at 6 (`course-planner.md:435-441`).
- **Local CI (021:236-240).** I ran these on HEAD and on a clean `--shared` clone at a9a2f08. The same seven fail on both:
  - `test_rf1_pin_harness::test_mutation_table_rows_of_their_own`
  - `test_rf7_structure::test_complete_routing_and_dirty_controls`
  - `test_rf6_query_policy::test_dynamic_candidate_inventory_is_complete_and_live`
  - `test_rf6_query_policy::test_dynamic_duplicate_inventory_row_is_refused`
  - `test_rf6_packages::test_original_definition_body_is_verbatim[gnd.checker.check]`
  - `test_rf4_peripheral::test_moved_algorithm_preserves_base_body[gnd.api:_run_check_raw]`
  - `test_rf4_peripheral::test_current_successor_body_and_import_controls_are_live`

  The two files fixed in 6dcc4d9 pass in a clean clone of 1c30525 (45 passed, without GND_PYREL_PYTHON). In the main checkout, `test_reference_closure_and_declared_bootstrap` still fails only on the untracked `.claude/worktrees/rf1-code-refactoring-225109`, as disclosed.

## Completeness

C1. 021 says "the five known inherited failures plus test_rf4_peripheral ×2" but names no node IDs. The list above should go in the record.
C2. Gate 018 and record 020 do not record which plan_app_bot bytes produced the run; see H7.
