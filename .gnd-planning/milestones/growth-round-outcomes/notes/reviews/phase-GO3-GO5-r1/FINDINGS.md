# Findings ledger: phase-GO3-GO5-r1

Reviewer: codex (review helper, `--subject phase`, base `9bf8bf3e`, reviewed
commit `b2d67b8e`). One reviewer is one reviewer. One round covers both GO3
and GO5, and the GO2 r2 and GO4 r1 repairs, which share files with them and
were committed together. It ran in a clean scratch checkout of `b2d67b8e`; its
folder was copied back and its logs' machine paths replaced
(`review_tool.py sanitize`, then the scratch prefixes by hand). The reviewer
reports that the GO2 r2 repairs and the eleven GO4 mutation controls held.

Every finding was reproduced by a regression test that fails with
`narrow.py`, `summary.py` and `tests/support/markdown_sections.py` at
`b2d67b8e` and passes on the repair.

| Reviewer | # | Finding | Reproduced | Class | Disposition | Repaired at | Notes |
|---|---|---|---|---|---|---|---|
| codex | F1 | Narrowing checked only the number of rows, so rows in another order kept a refused operation and dropped an admitted one | yes | blocking | fixed | the repair commit after the merge of `origin/main` | Each row must carry its operation's `operation_index`, `operation_id` and `reference`, one per operation in order; otherwise refused by name. `test_r1_f1_rows_must_be_the_proposals_operations_in_order` |
| codex | F2 | The summary counted an outcome list that does not cover the proposal (`[]` for two operations: `outcomes={}`, exit 0) | yes | blocking | fixed | as above | GO5-C1's equality would be false. The same coverage check, refused as `RoundFileError` before anything is counted. `test_r1_f2_outcomes_that_do_not_cover_the_proposal_are_refused` |
| codex | F3 | An inline HTML comment (in a table cell, or opened mid-paragraph) still satisfied the guard | yes | hardening | fixed | as above | Comments are removed wherever they open, across lines, except inside a fence or a code span. `test_go4_r2_inline_comments_hide_a_rule_and_a_tab_closed_heading_reads` |
| codex | F4 | Bindings did not identify the outcome report or the record read | yes | hardening | fixed | as above | Bindings are now `round_file_sha256`, `proposal_sha256`, `preview_sha256` (as `apply` binds them), `outcome_report_sha256` and `record_sha256` (canonical sha256 of the document read). `test_r1_f4_bindings_name_every_artifact_read` |
| codex | F5 | A host's reason (and `kind`, `id`, `document`) was whitespace-stripped | yes | hardening | fixed | as above | The host's text is kept as written (`HostText`: at least one character, never stripped). `test_r1_f5_host_text_is_reported_verbatim` |
| codex | F6 | A heading closed after a tab (`## The reply shape\t##`) was not read as that heading | yes | hardening | fixed | as above | The heading's words are split on any whitespace. Same test as F3 |

Two findings are blocking, so the budget gives a second round. It is not run
separately: the repaired bytes are read by the milestone's close review over
the whole GO2–GO5 diff (recorded in the phase records). **Until then the
repairs carry no review opinion.**
