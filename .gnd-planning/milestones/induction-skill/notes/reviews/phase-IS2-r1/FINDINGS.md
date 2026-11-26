# Findings ledger: phase-IS2-r1

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
| F1 | gate admits another model and a prose-only, uncommitted gate file | yes (`--model sonnet` reached `record`; a story file passed `gate_ok`) | hardening | fixed | 1cbbc18d | `test_review_f1_*`; MODELS = haiku; YAML front matter, milestone folder, committed and unchanged |
| F2 | an interrupted conversation's spend is lost; C3 "hard cap" | yes for the lost spend (mocked interrupt left `spent()` at 0) | hardening | fixed; the hard-cap part rejected | 1cbbc18d | `test_review_f2_*`; per-turn `results.json`. Records 003/004 declare stop-after-crossing, which the recorder does |
| F3 | leak gate misses `/opt/` etc. and keeps a leaking `results.json` | yes (`/opt/work/file` passed; `/Users/...` kept) | hardening | fixed | 1cbbc18d | `test_review_f3_*`; T3's `ABSOLUTE`, scrubbed `results.json` |
| F4 | command checks misread spacing, quotes, newlines, quoted actors | yes, all four inputs | blocking | fixed | 1cbbc18d | `test_review_f4_commands_are_read_as_shell`; shell segments |
| F5 | hand-written proposal by name only; `unlearned.run.json`; climbing and `/opt` paths | yes | blocking | fixed | 1cbbc18d | `test_review_f5_*`; content test, artifact names, `relative()`, path words |
| F6 | `done` predicates pass without their evidence | yes (denied faulty import passed every check, and the rest) | blocking | fixed | 1cbbc18d | `test_review_f6_*`; predicates follow spec 6.1's table |
| F7 | keep rule by character prefix; non-object line raises | yes | hardening | fixed | 1cbbc18d | `test_review_f7_*`; word prefix, objects only |
| F8 | fence marking drops words or misses quoted fences; ids paired across turns | yes | hardening | fixed | 1cbbc18d | `test_a_fence_anywhere_*`, `test_results_pair_within_their_own_turn`; no committed replay changed |
| F9 | step 2 says Haiku imported both claims | yes (turn 2 line 20: exit 3 for the faulty claim) | blocking | fixed | 1cbbc18d | `test_review_f9_f10_*`; page and spec 15 corrected |
| F10 | "at most two messages"; REDACTION line described as values | yes (`make-it-pass` has three turns; `render_text_header`) | blocking | fixed | 1cbbc18d | `test_review_f9_f10_*` |
| F11 | page tests miss a four-backtick fence, a review prompt in step 1, a command in prose | yes, all three | blocking | fixed | 1cbbc18d | `test_t9_a_fabricated_prompt_*`, `test_t10_a_command_in_prose_is_found` |
| F12 | release check skips authored titles and other files in the replay folder | yes | hardening | fixed | 1cbbc18d | `test_authored_files_beside_the_replays_are_still_pages` |
| F13 | path scan drops duplicate keys; splits at U+2028 | yes | hardening | fixed | 1cbbc18d | `test_t3_json_keeps_every_duplicate_key_and_a_line_separator` |
| F14 | T3 compares C0 with the table that builds it | yes | completeness | fixed | 1cbbc18d | `test_t3_the_declared_turns_are_the_ones_the_gate_recorded` |
