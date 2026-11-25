# Findings ledger: phase-RW3-r1

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
| F1 | the paragraph pass reported a wrapped sentence that a standing entry covers when it is on one line | yes | hardening | fixed | 529e3512 | Regression: `tests/test_release_text.py::test_a_standing_statement_stays_standing_when_it_wraps`. The text is this phase's own (written before round 1), not a repair's. |
| F2 | one reported line stopped the paragraph pass, so a second, wrapped statement in the same paragraph was not listed | yes | completeness | fixed | 529e3512 | Regression: `tests/test_release_text.py::test_each_stale_statement_of_a_paragraph_is_reported`. The text is this phase's own (written before round 1), not a repair's. |
| F3 | a phrase written with a double space or a tab between its words was not reported | yes | hardening | fixed | 529e3512 | Regression: `tests/test_release_text.py::test_prepared_install_guidance_is_reported[double-space]`, `[tab]` and `[three-lines]`. The text is this phase's own (written before round 1), not a repair's. |
| F4 | the dossier's source check ran after a `cd` into the retained folder, which is not a repository | yes | blocking | fixed | 529e3512 | Regression: none possible in a test: the block now runs from `git rev-parse --show-toplevel` and was checked with `bash -n`; `git rev-parse` in the retained folder was run and exits 128. |
| F5 | the dossier's comparison block had no failure guard, so a failed comparison was followed by the install and the block exited 0 | yes | blocking | fixed | 529e3512 | Regression: none possible in a test: every command block of the dossier is now `( set -e ... )`; a guarded block with a failing stage was run and exits 1 with no further output. |
