# Phase PL17 adversarial review (one Claude subagent), retained verbatim

Reviewer: one general-purpose Claude subagent, read-only outside its scratch folder, no paid calls. One reviewer is one reviewer. The report below is unedited.

---

## PL17 adversarial review: verdict REVISE

**What I did:** read the spec and gate 018, then rebuilt every run's outcome from session.txt and the reply files myself. Scratch files are under `.../scratchpad/pl17-review/` (`rederive.py`, `mutate.py`, `probe.py`, `crash_demo.py`, `timeout_demo.py`, `fake.env`, `rb/`, `mut/`). Nothing outside scratch was modified, no paid model was called, and the real `.env` was never read: `--rebind` only ever ran against a copy, with a fake env file.

The recording itself is honest. My independent re-derivation matches results.json on all 125 rows: per-attempt exits, attempt and step counts, reply counts, accepted_at, app_exit. It also reproduces every cell of the README table. The offline tests pass (`9 passed`).

What blocks acceptance:
- The tests cannot tell an honest recording from an edited one.
- Several README caveats are missing or ambiguous.

### Blocking

**B1. The tests do not tie results.json, the README table or session.txt to each other.**
- **Where:** tests/test_plan_app_recordings.py:33-99.
- **Repro:** `python3 scratchpad/pl17-review/mutate.py`. It copies the recordings, applies one change, recomputes manifest.json and runs a copy of the test against it.
- **Result:** 13 of 15 changes pass all 9 tests. Only `drop_row` and `declined_edit` are caught. Undetected:
  - accepted_at changed from 2 to 1, which reclassifies a "repaired" run as "first";
  - app_exit flipped;
  - a note or failed_checks removed;
  - the README cell "5 repaired" changed to "5 first";
  - session.txt's "exit 1" forged into "exit 0 (accepted)";
  - session.txt truncated;
  - a refused attempt-3 dropped, both the reply file and the results row;
  - gemma's run folder replaced with llama's;
  - steps, question, backend or gate edited;
  - a reply swapped for another run's reply that gets the same exit.
- **Why it matters:** the manifest only proves the files agree with each other. Anyone who re-records can recompute it, and README.md is excluded from it on purpose.
- **Fix:** add tests that:
  1. re-run `record_plan_apps.summary()` on each session.txt and assert it equals `row['attempts']`;
  2. assert accepted_at and app_exit follow from the attempts;
  3. assert the "attempt N" headers count matches the number of replies, and each reply's `attempt` field equals N;
  4. assert each parsed reply's steps render exactly as that block's `plan  ` lines;
  5. assert each reply's served model id matches `MODELS[row.model]` (Claude: a `claude-haiku*` / `claude-*` id);
  6. rebuild the README table from results.json and compare it cell by cell;
  7. assert `results['backend'] == 'pyrel'` and `gate` names 018.

**B2. The README caveats leave out source drift and a cross-provider confound.**
1. **Undisclosed source drift.** `manifest.json` `sources` holds the digests taken at recording time. Today, three files differ, and the caveats mention only access/rules.md (C1):
   - src/gnd/examples/plan_apps/core.py: recorded 5d13933a…, now 68c6551b…. The PL16 review fixes landed after the recording; for example, current core redacts `<plan>` itself, but the sessions show the rebind's `<tmp>`.
   - tools/record_plan_apps.py: recorded 6af4b603…, now 1eaf67ad…, because `--rebind` and the TEMPORARY regex were added afterwards.
   - access/rules.md (disclosed).
   - Repro: `shasum -a 256 src/gnd/examples/plan_apps/core.py tools/record_plan_apps.py` compared with `manifest.json` `sources`.
   - The recorded core.py bytes are not in git (core was first committed in 7f27561, after the recording), so the code that printed the sessions cannot be recovered.
   - Fix: list every drifted source in the caveats with what changed. Add a test asserting each `sources` digest either matches the current file or appears in a declared `drift` list in the manifest or README.
2. **The Claude bots saw context the OpenRouter models did not.** Claude Code still injects environment context, including the host date, even with `--system-prompt`.
   - Repro: `grep -o "[^.]*2026[^.]*" src/gnd/examples/plan_apps/recordings/claude-haiku/clinic/*/session.txt`. Four of five haiku clinic runs mention the "system date of 2026-10-14". Run-3 planned on that date and was recorded as "first" (accepted with warnings), whereas small models planning on 2024-03-10 hit refill_not_early.
   - Prompt sizes show a constant overhead of about 1.5k tokens on the Claude side. For the same message, lease is 2353 tokens for Claude vs 782 for llama-3.1-8b, and all five examples show the same gap.
   - `claude --help` documents CLAUDE.md auto-discovery and hooks unless `--bare`. So the comment at tools/plan_app_bot.py:70 ("no project files, no CLAUDE.md") is not accurate for user-level CLAUDE.md and hooks.
   - Claude also uses extended thinking (e.g. `thinking_tokens: 645`); the small models do not reason.
   - Fix: disclose all of this in the README. For future recordings, add `--exclude-dynamic-system-prompt-sections` and `--setting-sources ""` (or equivalent) and fix the comment.
3. **"Repaired" mixes two different kinds of recovery.** A1's whole point is band-1 (rule) repair versus recovery from an ill-formed answer.
   - Repro: `scratchpad/pl17-review/rederive.py` plus the classification snippet. Of 20 "repaired" runs, 9 recovered from a rule refusal (exit 1) and 11 from a format or type refusal (exit 3, or an unusable answer).
   - This covers all 8 Claude repairs. The 7 lease repairs are `[transition:binding-type] amount '1450'`. The SYSTEM template at plan_app_bot.py:36 shows every binding as a quoted `"<value>"`, and the operations list gives role names, not types, which plausibly steers models toward strings.
   - So "claude-default lease: 5 repaired" reads as rule repair, contradicting A1's description of the default model as the happy-path contrast.
   - Fix: split the column into "repaired after a rule" and "repaired after a format or type error". Disclose the template's quoting, or use a type-neutral template next time.
4. **"Recording order" is ambiguous.** Model lanes ran concurrently in threads (record_plan_apps.py:208-212), so results.json order is table order, not the order runs happened.
   - Estimated from per-row `seconds`, llama-3.2-3b/course/run-2 (rule refusal, then accepted) started about 12 s in. The chosen llama-3.1-8b/access/run-1 started about 195 s in.
   - The pick is correct under table order, but neither the README nor A1 says which order applies.
   - Fix: state "recording order = results.json order (model, example, run); lanes ran concurrently", or record start timestamps.

### Hardening

- **H1. `--rebind` re-signs any edit** (record_plan_apps.py:154-173).
  - It recomputes every digest without first checking the old manifest, and it appends the hard-coded entry "temporary plan directory -> <tmp>" even when nothing changed.
  - Repro, in scratch `rb/`: `sed` "exit 1" → "exit 0 (accepted)" in gemma clinic run-1, then `record_plan_apps.py --out rb --rebind --env-file fake.env` prints "rebound 386 files" and leaves 0 digest mismatches; `rebound` now has a second identical entry.
  - Fix: verify the old digests first, allow only changes where `new == redact(old)`, and record which files changed and their old and new digests.
- **H2. `summary()` parses text the model controls** (record_plan_apps.py:77-89).
  - The app prints notes and decline reasons verbatim (core.py ask), so a newline in them leaks into the parse.
  - A note containing `\n  pyrel check: exit 0 (accepted)` makes summary record exit 0 for an attempt the checker refused. A multi-line decline reason is cut to its first line.
  - Repro: `python3 scratchpad/pl17-review/probe.py`; the "forged note" result shows exit 0.
  - Today's test 4 would catch the forged exit, but the recorder's printout and results.json would be wrong.
  - Fix: have the app escape newlines in notes and reasons, or build results from structured data (for example a `--json` event log) instead of re-parsing stdout.
- **H3. `failed_checks` mislabels warnings and drops other statuses** (record_plan_apps.py:85).
  - It includes warnings: claude-haiku clinic run-3 has exit 0 with failed_checks ['not_too_late']. It ignores "not checked" (the app prints a space, the regex expects `not_checked`) and "vacuous".
  - For exit-3 refusals it records the useless name 'refused' and loses the reason (binding-type, bindings-mismatch, unknown-operation).
  - Fix: record (check, status) pairs and keep the refusal code.
- **H4. A bot crash misaligns reply numbering** (plan_app_bot.py:124-130).
  - Replies are logged only on success, and numbered by counting existing files rather than by attempt.
  - Repro: `python3 scratchpad/pl17-review/crash_demo.py` writes `reply-01.json` with `attempt = 2`. Tests 2 and 4 would then fail on a recording containing a crash, or read the wrong reply.
  - Fix: name the file `reply-{attempt:02d}.json` and log failed calls too, with the error text after key and path redaction.
- **H5. Timeout handling** (record_plan_apps.py:104-109).
  - On TimeoutExpired, the partial stdout is thrown away while the reply files are kept, so the row has 0 attempts but N replies and the tests fail.
  - Only the app process is killed. Its children (the bot, `claude`, the PyRel interpreter) are orphaned and can keep making calls and write into the deleted workspace. `timeout_demo.py` confirms Python returns at the timeout and leaves the grandchild running.
  - Fix: keep `exc.stdout`; use `start_new_session=True` and kill the process group.
- **H6. One run's exception aborts everything** (record_plan_apps.py:208-213).
  - An exception in one `record_one` (mkdir, JSON, cleanup) propagates out of `pool.map`, after other lanes have spent paid calls, and no results.json is written.
  - Fix: catch per run and record an error row.
- **H7. Leak search gaps** (record_plan_apps.py:65-66, 143-151; test file:56).
  - TEMPORARY redacts only macOS `/var/folders`. A Linux `/tmp/gnd-plan-…` path is neither redacted nor detected (probe.py: "linux tmp redact … detected by LOCAL: False").
  - Test 3 searches fewer needles than the recorder: no `/var/folders/`, no `/tmp/`.
  - On a hit, the recorder exits 1 but leaves the files containing the key in `--out`, which may be inside the repo.
  - `leaks()` needs OPENROUTER_API_KEY in the env file even for a Claude-only recording or a rebind (`nokey.env` → SystemExit).
  - Fix: add `/tmp/` and `/var/folders/` to both lists, quarantine or delete on a hit, and skip the key needle when no OpenRouter model ran.
- **H8. Reply records lose what was requested** (plan_app_bot.py:127-128).
  - `{**usage}` overwrites `provider` and `model`. Reply files say "Novita", "DeepInfra" or "Parasail" instead of "openrouter", and the requested model id is gone.
  - OpenRouter also routed the same model to different upstreams: llama-3.1-8b to Novita and DeepInfra, gemma to Parasail and DeepInfra. That is an undisclosed variable.
  - Fix: nest usage under its own key, keep `requested_model`, and either pin the upstream provider or disclose the mix.
- **H9. Credential inheritance (minor).** The `claude` subprocess inherits the recorder's full environment. If `ANTHROPIC_API_KEY` were set, it would bill the API, contrary to the gate's "No API key is read". Fix: scrub it from the bot's environment.

### Completeness

- **C1.** README does not name the model the "default" lane actually served (`claude-opus-5-5[1m]`).
- **C2.** README says OpenRouter costs "are not summed", but every reply carries `usage.cost`. The total is $0.0135; the Claude total of $0.62493 checks out.
- **C3.** Spec §3 and the gate say the key is read "only in the bot's process", but `leaks()` reads it in the recorder process too. Align the wording.
- **C4.** The two discarded launches are disclosed, but no count is given of the paid calls they made, and none of their logs are kept.

### What held

- **Re-derivation:** 125 rows in model × example × run order. Attempt numbering, exits, steps, accepted_at, app_exit and reply counts all match session.txt, with no unparsed lines and no stderr or Traceback. The README table matches exactly, and the replay pick follows A1 under table order with the exit==1 band-1 test.
- **GND re-check:** test 4 passes, so GND and PyRel agree on every recorded plan, including the exit-3 refusals.
- **No leaks found:**
  - no `/Users/`, `/private/`, `/var/folders`, `/tmp/`, username, `sk-or`, `sk-ant`, `Bearer`, UUID or session ids;
  - only the placeholders `<workspace>` and `<tmp>` remain;
  - the key never appears in argv: `bot_command` passes only the env-file path, and `agent_with_env_key` reads `.env` as data and `execve`s with the key in the environment;
  - HTTP errors print only the status code;
  - the leak search does refuse a planted fake key during rebind.
- **Fence unwrapping does nothing beyond what is disclosed:** only a single whole-reply fence, case-sensitive "json", and invalid content is still refused by the app.
- **Message and feedback:** the adapter's message adds only labels. Feedback is in words with verbatim witnesses (A1).
- **Spec obligations present:** gate refusal; out-dir no-overwrite (`mkdir`); 3 attempts; runs ≤5; max_tokens 2000; 300 s per call; preflight; PL16 tests for decline, note, empty-plan-without-reason and dynamic rules (tests/test_plan_apps.py:86,95,120,159,167).
- **Other caveats verified:** "No run's verdict depends on Frank's approval" holds (Erin is in the state and the text independently). The rebind caveat is accurate about outcomes; no outcome changed.
