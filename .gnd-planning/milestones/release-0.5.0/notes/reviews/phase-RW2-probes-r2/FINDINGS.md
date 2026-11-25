# Findings ledger: phase-RW2-probes-r2

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
| F1 | `shlex` with comments reads an unquoted `#` inside a word as a comment, so `population.json#BROKEN` was accepted | yes | hardening | fixed | 9f853be4 | Self-inflicted: the text was written by round 1's repair. The helper no longer reads a line as shell: one `sh` or `bash` block of the README must equal the probe's commands as text. Regression: `tests/test_acceptance_controls.py::test_readme_commands_refuses_a_command_the_readme_no_longer_documents[glued-comment]` on both READMEs, in the default lane |
| F2 | the contents of a here-document inside the shell fence counted as commands | yes | hardening | fixed | 9f853be4 | Self-inflicted: the text was written by round 1's repair. The helper no longer reads a line as shell: one `sh` or `bash` block of the README must equal the probe's commands as text. Regression: `tests/test_acceptance_controls.py::test_readme_commands_refuses_a_command_the_readme_no_longer_documents[here-document]` on both READMEs, in the default lane |
| F3 | the Markdown reader's `splitlines()` splits at U+2028, which the shell reads as part of a word, so `other<U+2028>gnd ...` was accepted | yes | hardening | fixed | 9f853be4 | Self-inflicted: the text was written by round 1's repair. The helper no longer reads a line as shell: one `sh` or `bash` block of the README must equal the probe's commands as text. Regression: `tests/test_acceptance_controls.py::test_readme_commands_refuses_a_command_the_readme_no_longer_documents[line-separator]` on both READMEs, in the default lane. `markdown_blocks` still splits at U+2028; that is the reader other tests use and it is not changed here. With the whole-block comparison the split makes the block differ, so the input is refused |
