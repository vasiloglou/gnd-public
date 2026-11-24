# Findings ledger: close-repairs-r1

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
| codex-F1 | the close record is cited but does not exist; close-results still quotes no close measurement | yes | completeness | fixed | close commit | written at close: `006-milestone-close.md`, and close-results.md now quotes the close commit's gates and the packaged digests. The review ran before the record by design |
| codex-F2 | close-results says the close panel read every unread repair, though the Qwen seat read no code | yes | completeness | fixed | close commit | close-results.md's review section names the seats that read code (Codex, Gemini, Kimi) and Qwen's scope |

The runtime repair (empty fact lists) found no counterexample in a 36-case
matrix. One round; no further round: both findings are close documents.
