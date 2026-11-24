# Findings ledger: phase-OB1-r1

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
| F1 | Default arguments capture `input_policy.MAX_BYTES`, so four RF7 controls that lower it regress | yes (4 failed in `tests/test_rf7_input_policy.py`) | blocking | fixed | the phase-OB1 commit | Defaults are `None` and resolve `MAX_BYTES` per call. The regression tests are `test_json_byte_cap_before_decode[*]` and `test_stream_read_is_bounded`, shown failing before the fix. |
| F2 | The normative "Ossie interchange" text still states fixed 10 MiB limits, and the help text does not cite it | yes (the paragraph at `representation-format.md:2132`) | completeness | fixed | the phase-OB1 commit | The normative paragraph now states both flags, the default, the ceiling, exit 64 and the kept model-size cap. The help-text citation part is rejected: CLI help in this repository states defaults and never cites a docs section, and the help is a summary, not a second normative home. |
