# Findings ledger: phase-GO4-r1

Reviewer: codex (review helper, `--subject phase`, base `f7ec03b4`, reviewed
commit `038f64dc`). One reviewer is one reviewer. A first attempt of this round
did not start: its brief pinned a file another round was still writing. The
round was briefed again and run in a clean scratch checkout of `038f64dc`; its
folder was copied back and its log's machine paths replaced. The reviewer could
not run pytest (no project environment in its sandbox) and ran the guard's
functions in memory.

| Reviewer | # | Finding | Reproduced | Class | Disposition | Repaired at | Notes |
|---|---|---|---|---|---|---|---|
| codex | F1 | The guard passes a reversed or deleted rule ("are not an `open_questions` entry", both id-only sentences removed, "its own or included" removed, "Rows for any fact type") | yes: the old guard returns `[]` for each | blocking | fixed | the GO2–GO5 commit after `9bf8bf3e` | GO4-C2 was false. The guard now requires each rule as a whole statement, compared with whitespace collapsed; any edit to one is a missing statement. The four edits are T2 cases (`reversed`, `id-only-deleted`, `own-or-included-deleted`, `any-fact-type`); each fails with the old guard |
| codex | F2 | The guard read Markdown by exact lines and string splits: a rule inside an HTML comment counted, and an unpadded table, a closed heading (`## … ##`), a `~~~` fence or a reflowed sentence broke it | yes | hardening | fixed | as above | `tests/support/markdown_sections.py` (the repository's own reader) gains `markdown_blocks` and `section_blocks`: ATX headings with closing runs, fences of either marker, tables with or without outer pipes and padding, HTML comments dropped, paragraphs with whitespace collapsed. `test_go4_r1_f2_hidden_rules_are_missing_and_equivalent_markdown_is_read`, which fails with the old guard |
| codex | F3 | "Acting on a shape match" told the host to write the dropped fact type's facts against the existing one, which the additive policy refuses (`fact_types.modify`) | yes: the policy's diff of that change is `changed outside the admitted keys: sample_population` | blocking | fixed | as above | The page contradicted the new rows rule. The bullet now names the existing id and makes the rows an `open_questions` entry; the guard requires that sentence and refuses the old wording (`reuse-bullet` case) |

Three findings are blocking, so the phase's budget gives a second round. It
is not run separately: GO4's repaired bytes are read by the milestone's close
review, which reads the whole GO2–GO5 diff (recorded in the phase record).
