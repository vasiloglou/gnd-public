# Findings ledger: phase-LX2-r1

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
| F1 | Include-free streamed models refused | yes | blocking | fixed | 706b9345 | `test_include_free_model_stream_is_consumed_once` covers public production and replay. |
| F2 | Producer lost stale-binding diagnostic | yes | blocking | fixed | 706b9345 | `test_stale_projection_inputs` covers stale include, flat and record on both routes. |
| F3 | Explicit projected paths through symlinked parents refused | yes | hardening | fixed | 706b9345 | `test_explicit_projected_paths_accept_symlinked_parent` covers population and both artifact paths. |
| F4 | Standalone production resolved the model before parsing targets | yes | hardening | fixed | 706b9345 | `test_projected_witness_checks_targets_before_resolving_includes` pairs malformed targets with a missing include. |
