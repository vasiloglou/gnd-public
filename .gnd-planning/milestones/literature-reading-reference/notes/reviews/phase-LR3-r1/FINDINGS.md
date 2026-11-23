# Findings ledger: phase-LR3-r1

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
| codex-1 | Wrong predicate counted a same-fact-type row with reversed roles | yes (the reviewer's reversed builds-on row gave wrong_predicate 1) | blocking | fixed | aec93739 | wrong predicate now needs another fact type; T4 asserts the reversed row is neither found nor wrong predicate. The recorded run's two wrong-predicate rows both have another fact type, so the figures are unchanged |
| codex-2 | Sequential prompt substitution rewrites a model reading that spells a field name | yes (T9 with a reading "{section} introduces {Method}") | hardening | fixed | aec93739 | one-pass fill; test_t9_prompt_fields_are_filled_once. The new fill gives byte-identical prompts for all 46 recorded sections, so the run stands |
| codex-3 | A non-object response or a non-string section escapes as a traceback | yes (both shapes raised AttributeError and TypeError) | hardening | fixed | aec93739 | both shapes refuse with ExampleError; two T8 cases |
| codex-4 | T2 does not enforce zero producer calls | yes (by reading T2) | hardening | fixed | aec93739 | T2 replaces reading.ProducerCall with a raiser during replay |
| codex-5 | The README and the reply predict beyond the measured run | yes (by reading) | completeness | fixed | aec93739 | both now say the run measures this set only and attributes no gap |
