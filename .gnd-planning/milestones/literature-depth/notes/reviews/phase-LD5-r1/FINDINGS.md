# Findings ledger: phase-LD5-r1

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
| F1 | A support-list update changed the shared claim pin | yes | blocking | fixed | `729111ba` | The shared pin binds the published target and its proof status. The selected support must match its own published record and independently replays. Consistently updating or withdrawing one published support preserves the other. |
| F2 | Missing evidence and changed model bytes returned an unsupported result | yes | blocking | fixed | `729111ba` | The verifier checks the manifest before interpreting release claims, pins model bytes for both editions, and requires revalidation when no approval survives but some evidence is stale. Only verified rejections yield the unsupported result. |
| F3 | Missing independent rule, witness and interpretation controls, plus a duplicated edition binding | yes | hardening | fixed | `729111ba` | The tests cover rule edition, witness, interpretation, the publication's resolution edition, and a symlinked opinion file. The installed public invocation is measured independently. |
| F4 | Renewed support accepted the copied rule through an asymmetric path | yes | hardening | fixed | `729111ba` | The renewed route independently projects the rule from both original and evolved model bytes and compares both projections to the pinned artifact. |
