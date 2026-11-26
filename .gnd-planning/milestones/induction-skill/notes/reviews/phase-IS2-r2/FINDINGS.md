# Findings ledger: phase-IS2-r2

One row per finding the review returned, under the reviewer's own id. Fill every cell:

- Reproduced: yes or no. A finding is believed only once it is reproduced against the bytes.
- Class: blocking, hardening or completeness, assigned here, not by the reviewer
  (review-convergence.md).
- Disposition: fixed, deferred, rejected or open.
- Repaired at: for a fixed finding, the commit or tag that holds the repaired bytes. Those
  bytes are unreviewed until a later round reads them; `review_tool.py status` says which.
- Notes: the regression test for a fixed finding, the target for a deferred one, the reason
  for a rejected one.

If the review returned no findings, replace the table with the line: No findings.

| Id | Finding | Reproduced | Class | Disposition | Repaired at | Notes |
|---|---|---|---|---|---|---|
| F1 | an interrupted run keeps host data in its turn file and partial results.json; the CLI reads `checks` from it | no (not probed) | hardening | deferred | | self-inflicted (round 1's per-turn write); no further recording is authorized; carried to the milestone close |
| F2 | finish()'s JSON read drops duplicate keys | no (not probed) | hardening | deferred | | self-inflicted (round 1's finish); same class as round 1 F13, which the T3 reader now handles |
| F3 | the scrubber omits the git email's local part | no (not probed) | hardening | deferred | | self-inflicted (round 1's scrub) |
| F4 | a JSON line split at U+2028 loses a turn's cost and a replay message | yes (two pieces from one line) | hardening | fixed | 8d76814f | earlier code; `test_review_r2_f4_*`, `test_a_line_separator_inside_a_message_keeps_the_message` |
| F5 | quoted punctuation and comments mis-split segments | yes (`printf '%s' ';' gnd evolve apply`; a comment before a newline) | hardening | deferred | | self-inflicted (round 1's `segments()`) |
| F6 | climbing paths inside a word, parentheses in a path, a sed program, a workspace-prefix sibling | yes (all three probed) | hardening | deferred | | self-inflicted (round 1's `outside_words()` and `PATH_WORD`) |
| F7 | an unspaced redirect into a learner artifact; a quoted `>`; a partial Edit of a proposal | yes (unspaced redirect passed) | hardening | deferred | | self-inflicted (round 1's redirect rule) |
| F8 | a whole Bash call's result attributed to a command inside it (`Exit code 30`, `false && gnd check`) | yes (both passed) | hardening | deferred | | self-inflicted (round 1's predicates); the kept runs' published results are unaffected (reviewer reproduced them) |
| F9 | learn, absent-learner and existing-output accept contrary evidence | yes (learn and absent-learner probed) | hardening | deferred | | self-inflicted (round 1's predicates); `timeout`-prefixed learner calls are F10 of section 16 |
| F10 | keep rule drops a quoted `;` and keeps `mygnd`; live and recheck checks can differ | yes (both) | hardening | deferred | | self-inflicted (round 1's word compare); published results come from `recheck()` |
| F11 | a denial in one turn marks a reused id refused in another | yes | hardening | fixed | 8d76814f | `test_a_denial_marks_only_its_own_turns_call` |
| F12 | gate front matter split at an indented `---` | no (not probed) | hardening | deferred | | self-inflicted (round 1's `gate_ok`); both real records pass |
| F13 | page tests miss a swapped prompt, a second review prompt, a spaced command in prose | no (not probed) | completeness | deferred | | self-inflicted (round 1's page tests); the current page was checked by hand against its recordings |
| F14 | the page misstated the permission list and missed the turn-1 writes of score and learn | yes (`shasum` in recheck turn 1; a `cd && gnd export && ls` chain in learn turn 1) | blocking | fixed | 8d76814f | Fable's correction; `test_plan_app_docs.py` and the page tests pass |
