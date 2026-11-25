# Findings ledger: phase-OB5-r1

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
| F1 | The oracle test compares with the validator's own uppercasing, so it hides that a letter such as U+1C8A uppercases differently under the exporter's Python 3.14 and the validator's 3.11. | yes (`"\u1c8a".upper()` differs by version) | hardening | fixed as a stated limit; open for the owner (OB5-Q1) | `7a6ccfe9` | The test now asserts the limit is confined to non-ASCII names. The normative text states it. The exporter is unchanged: it cannot know a reader's Unicode tables. |
| F2 | `normalized()` in the corpus checker took 24 ASCII control characters for punctuation and disagreed with the exporter. | yes (24 code points) | blocking (the independent checker was wrong) | fixed | `7a6ccfe9` | `test_r1_f2_the_corpus_checkers_normalizer_agrees_with_the_exporter_on_every_character`, failed before the fix. |
| F3 | T4a did not check unmapped reasons on a page; a misspelled reason passed. | yes | blocking (approved obligation T4a) | fixed | `7a6ccfe9` | `test_every_reason_on_a_page_is_one_the_code_gives`, `test_r1_f3_a_misspelled_reason_is_caught`. |
| F4 | T5 matched exit numbers by substring: 111 passed for 11, and one wrong mention passed beside a right one. | yes | blocking (approved obligation T5) | fixed | `7a6ccfe9` | `exit_numbers` reads every number before a constant; `test_r1_f4_every_exit_number_in_the_release_note_is_checked`. |
| F5 | The explanation said `uniqueness-not-confirmed` means "not yet confirmed"; a confirmed deontic rule gets it too. | yes (by the normative rule) | blocking (a false sentence) | fixed | `7a6ccfe9` | Reworded to confirmed and alethic. No test can hold prose meaning; named in the record's boundary. |
| F6 | The release note implied a 10 MiB lower bound and exit 64 below it; the range is 1 byte to 256 MiB, and `--max-output-bytes 1` exits 3. | yes (exit 3) | blocking (a false sentence) | fixed | `7a6ccfe9` | `test_r1_f6_the_release_note_states_the_bound_as_the_cli_takes_it`, failed before the fix. |
| F7 | The how-to said each refund has one requesting customer; the model says at most one. | yes (the column is nullable) | blocking (a false sentence) | fixed | `7a6ccfe9` | Both pages now say "at most one". |
