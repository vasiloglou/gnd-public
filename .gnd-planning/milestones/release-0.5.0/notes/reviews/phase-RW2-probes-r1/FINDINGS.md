# Findings ledger: phase-RW2-probes-r1

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
| F1 | `readme_commands` accepts a command the README no longer documents: another executable before it, a shell comment, or a copy kept only in an HTML comment | yes | hardening | fixed | 423ab44f | Reproduced with both packaged READMEs. The helper now reads the README's Markdown blocks with the existing `markdown_blocks` and each line of a `sh` or `bash` fence with `shlex`; it adds no pattern. Regression: `tests/test_acceptance_controls.py::test_readme_commands_refuses_a_command_the_readme_no_longer_documents` (five changes on two READMEs) and `test_readme_commands_accepts_the_packaged_readmes`, in the default lane |
