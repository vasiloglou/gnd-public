# Round 2, reader 4 -- measurability and the end-to-end demonstration

Retained text of the reader's returned report. Local edits: scratch paths read
`<scratch>`; headings demoted one level.

**Digest check:** both match.
- `evidence/plan-review-r2/induction-skill-plan.md.snapshot` = 7329cbd2…3dc
- `evidence/plan-review-r2/phase-IS1-spec.md.snapshot` = f81590b0…938

Line numbers below refer to these snapshots.

**Verdict: approve-with-fixes.** No finding blocks plan approval. The IS1 spec is approvable. Every new finding is in IS2's outline or in IS1's red-control bookkeeping, and each can be fixed by naming an edit. Seven of my nine new findings are self-inflicted, which is more than half, so the declared stop rule applies. These items should move into the IS1 and IS2 spec gates, not into a third plan round.

**What I did** (only in `<scratch>`, with the repo's `.venv/bin/gnd`; the recorder was not run, no network):
- Walked the commands page over a copy of refunds up to step 6. The outputs reproduced: measure 2/4, searched 40, support 4/4, `EMITTED 10`, SUPPRESSED 1/3, `breaking: false`, apply exit 0.
- Ran `gnd check MODEL POP` without the grep, on every batch before and after the apply, and with bad inputs.
- Ran plain `gnd measure` and plain `gnd evolve preview`.
- Ran T3's `ABSOLUTE` patterns over the 12 committed course `turn-*.jsonl` files.

## Re-check intent (`gnd check MODEL POP`) against step 6

- **It reproduces step 6.** After the apply, plain `gnd check model.orm.yaml batches/market.yaml` exits 0. Its output contains both lines the commands page greps for: `ADVISORY (deontic)` and `[warning] constraints[1]: … {'$v_v0': '601', '$v_v1': '750'}`. So the `TUTORIAL_CLAIMS` pair for 601/750 shows up in plain output, and the keep rule keeps it because the command has no pipe.
- **The reactions fit the real exits.** The step-6 result is a deontic warning at exit 0, so the "report" reaction applies. A missing population, or labels.json passed as the population, exits 3, which matches "report the refusal verbatim and stop". Per `docs/reference/cli.md:94`, check can also exit 1 (alethic failure), 2 (vacuous) or 4 (indeterminate). These fall under "any other non-zero → report verbatim and stop", which is acceptable.
- **The exit citation is wrong** (see N2). `gnd check --help` documents no exit meanings except the usage error 64.

## Round-1 status

| ID | Status | Evidence |
|---|---|---|
| R4-F1 recorder cannot record | **partially resolved** | All six edits are named, plus the `kept_stream` test and the piped-gnd statement (plan l.286-293). Two gaps remain: "per-skill `done`" is the wrong granularity (N6), and nothing carries state between conversations (N5). |
| R4-F2 `test_replays.py` rejects refunds | **resolved** | Plan l.304-306: generalized to an example and skill map, red first. Naming collisions remain (N6). |
| R4-F3 step 6 check has no skill | **resolved in design** | D18 (o); the intent row (l.175); predicate 2 (l.62-64); spec l.121. It is not tested (N1), and its exit citation is wrong (N2). |
| R4-F4 numbers and recordings untied | **partially resolved** | Done: "every number listed in `TUTORIAL_CLAIMS`" (l.67-69), a recording column, the said-equality test, and the 5/2/3 row deferred to the IS2 gate (l.311-316). Gap 1: one pair can never appear in a single kept output, and the divergence escape cannot be checked (N3). Gap 2: the said test compares the page with `replays.json` `said`, which is entered by hand. Stream-json carries no user prompt: `/gnd:gnd-model-from-text rules.md` does not appear in its own turn-01.jsonl. The tie to the recorder's declared turn (`results.json` `turn_log[].user`) that my fix asked for was dropped. |
| R4-F5 residual overclaims | **mostly resolved** | IS1 residual narrowed (l.280-282); spec honest limit (l.267-270); adversarial turns named and uncovered branches become residuals (l.300-303). Still missing: a pass/fail predicate in `results.json` for each adversarial turn, and the absent-learner turn cannot show absence (N7). |
| R4-F6 Popper unproven | **resolved** | Plan l.208-213; spec l.150 and l.329. |
| R4-F7 red-first contradiction | **resolved** | Spec l.87-94 now has two controls. Bookkeeping slips remain (N8). |
| R4-F8 no page test; IS-R7 conflict | **resolved** | IS2-C5 (l.317-319); IS-R7 exception (l.89). The current page has "There is no skill for this step" at l.94, and again split across lines 192-193, so the C5 test needs whitespace-normalized matching to catch both. |
| R4-F9 learn spans steps 2 and 3 | **resolved** | Plan l.174; spec l.120; C0 decides (spec l.326-327). |

## New findings

**R4-N1** (hardening, high, **self-inflicted**): **The C5 page-structure test cannot fail when step 6's re-check stays a plain request.**
- **Where:** plan l.62-64 ("step 6's re-check included") and IS2-C5 l.317-319.
- **Evidence:** C5 checks for a `/gnd:` prompt in each step and a skill on every summary row. Step 6 already has `/gnd:gnd-model-evolve …` (tutorial l.220), and its row already names `gnd-model-evolve` (l.270). So a rewrite that leaves "Check batches/market.yaml against the model again." as a plain prompt passes C5. The D18 clause of predicate 2 has no failing case.
- **Fix:** C5 also asserts that the "You type" fence immediately before the Before/After table starts with `/gnd:gnd-induce`, and that row 6 names both skills.

**R4-N2** (hardening, high, **self-inflicted**): **For `gnd check`, "The meaning of each exit is in that command's `--help`" is false.**
- **Where:** spec l.122; plan IS-R3 l.85 and the reactions paragraph l.186-189.
- **Evidence:**
  - `gnd check --help` states no exit band except 64.
  - The bands (0 pass, 1 alethic failure, 2 vacuous, 3 invalid input, 4 indeterminate) live in `docs/reference/cli.md:94`.
  - IS-R3's home list (`measure-labels`, `discover`, `ilp-bridge`) omits that file.
  - A packaged skill cannot link `docs/` (plan l.414).
  - T7 only checks that options exist, so it stays green.
- **Fix:** add `docs/reference/cli.md` "Interpret exits" to IS-R3's homes. Have the skill name the check bands' home in words, without a link. Optionally add one sentence saying that exits 1 and 2 are check results, not command failures. An alternative is an owner-scoped follow-up to add an exit line to `gnd check --help`, outside this milestone's "no CLI change" scope.

**R4-N3** (hardening, high, **self-inflicted**, from IS2-C4's new test): **One `TUTORIAL_CLAIMS` pair can never appear in a kept tool output, and the escape clause has no testable form.**
- **Where:** plan l.312-315; `tests/test_ik6_walk.py:180-181`.
- **Evidence:**
  - The pair `"  breaking: false\n  breaking: false"` is two separate `gnd evolve preview … | grep breaking` outputs joined together.
  - A plain preview, measured, prints `breaking: false` once among seven lines (PREVIEW, proposal, before, candidate, blast-radius, breaking, affected). Two previews are two tool results, so the joined string appears in no single kept output.
  - The pair `then $v_v1 is at most 500.` comes from `grep -o … model.verbalization.txt | sed …`. It appears only if the agent happens to Read that file.
  - "Or the page explains the divergence beside the replay" has no form a test can check.
- **Fix:** give each pair a recording-side string of its own (here `breaking: false`, found in each preview's output). For divergence, require a marker a test can find, for example an admonition beside the replay that names the pair.

**R4-N4** (hardening, high, pre-existing; the recording home was chosen in r1): **Recordings kept under `src/gnd/examples/refunds/` will fail T3's path scan, after money has been spent.**
- **Where:** plan l.236 and l.305-306.
- **Evidence:**
  - `_public_texts()` scans every file under the example with `ABSOLUTE`, including the drive-letter pattern `\b[A-Za-z]:[\\/]`.
  - Run over the 12 committed course turn files, 2 match it falsely: `claude-default/run-2/turn-01.jsonl` and `skill-sessions-evolve/claude-haiku/run-1/turn-01.jsonl`. In both, Python's `as f:` is followed by an escaped newline (`f:\n`).
  - The recorder's leak gate (`record_skill_sessions.py:179-185`) does not check the patterns `/tmp/`, `/opt/` or `~/`, so a recording can pass it and still fail T3.
  - Side effect: the commands page's `copytree` (l.23) would also copy the recordings into the reader's walk folder.
- **Fix:** run T3's `ABSOLUTE` patterns in the recorder's leak gate before keeping a recording. Have T3 match decoded JSON strings, not raw jsonl. Add `skill-sessions` to the commands page's `ignore_patterns`.

**R4-N5** (hardening, medium, pre-existing): **Nothing carries state between recorded conversations.**
- **Where:** IS2-C1 l.286-303; the sweep row l.417 ("IS2-C1 names the edits").
- **Evidence:**
  - Each run copies only `plan["files"]` from the example into a fresh temporary workspace (`record_skill_sessions.py:125-132`).
  - Steps 3 and 4, which import, need `ilp/` and `learned/` or `faulty/`.
  - Step 6's evolve conversation needs `learned.proposal.json` and `discovered.json`.
  - Step 6's re-check needs the applied model.
  - None of these files is committed in refunds. One conversation spanning every step does not fit `MAX_TURNS = 6` or the stop rule.
- **Fix:** name a seeding edit for each conversation, for example running the commands-page blocks up to step N in the workspace before the first turn, with the seed's digests recorded in the manifest. Or declare one conversation that spans several skills, with its own turn bound.

**R4-N6** (hardening, medium, **self-inflicted**; it comes from the wording of my own R4-F1 fix): **Recorder parts keyed per skill are the wrong granularity.**
- **Where:** l.290-292 ("a per-skill `done` predicate"), l.236 (`skill-sessions/<model>/run-N/`), and IS2-C2.
- **Evidence:**
  - At least six gnd-induce conversations share one skill but need different predicates: score; learn stopping after the learner; learn and import; the faulty import; discover; re-check; plus the three adversarial turns.
  - `SKILLS` is keyed by skill, with one turns list.
  - `done(model)` receives only the model path (l.161), so it cannot test "proposal exists" or "exited 3".
  - `results.json` records one skill.
  - Both the home `<model>/run-N` and the replay name `course-<skill>-<model>-run-N` would collide.
- **Fix:** key the recorder by conversation id. Give the `done` predicate the workspace and the kept stream. Put the conversation id into the home path and into the generalized replay-name regex.

**R4-N7** (hardening, medium, **self-inflicted**; the adversarial turns were added in r2): **The "use popper" turn cannot show a real absence.**
- **Where:** l.300-301; spec l.143-146.
- **Evidence:**
  - `TOOLS` (`record_skill_sessions.py:57`) allows no absence probe (`command -v popper`, `which popper`, `popper --help`). Any probe is denied by permission, and `kept_stream` replaces its result with "[N bytes of output not kept]". So a recorded stop cannot be told apart from a permission denial.
  - The exact `python stand_in_learner.py *` entry denies `python3 …` or `./stand_in_learner.py` too.
- **Fix:**
  - Declare one probe command in the allowlist and in the keep rule.
  - Put the exact learner invocation in the user turn.
  - Give each adversarial turn a pass/fail predicate in `results.json`: the named stop, a new path after exit 11, and no clause edited after exit 3.

**R4-N8** (completeness, low, **self-inflicted**): **The red-control labels do not match their definitions.**
- **Where:** spec l.90-94 versus l.254 and l.264.
- **Evidence:**
  - T17 (new, in `test_induce_skill.py`) is marked "control 2 red", but control 2 is defined as only the *unchanged* T5 and T9.
  - T7's "control 1 red" holds for `test_public_packaged_invocation_guards.py` (per-skill count) but not for `test_public_packaged_command_help.py`. That file is unedited and passes on the pre-IS1 tree.
- **Fix:** state each control per file, and either add T17 to control 2's definition or relabel it.

**R4-N9** (completeness, low, **self-inflicted**): **The "Before" column of step 6's table has no source.**
- **Where:** tutorial l.249-252; the re-check intent l.175.
- **Evidence:** the written rule "quiet" on market before the apply comes from no commands-page block and no `TUTORIAL_CLAIMS` pair. I measured it in scratch: before the apply, check exits 0 with ADVISORY `(none)`. A re-check recorded only after the apply cannot show it.
- **Fix:** either record a pre-apply re-check turn and pair it, or have the rewrite derive "Before" from step 1 and say so.

**Round-2 tally for reader 4:** 9 findings (0 blocking, 7 hardening, 2 completeness); 7 of 9 self-inflicted. Round 1 was 9 findings with 4 blocking. The count is flat while severity fell, so both of the declared stop conditions are met.
