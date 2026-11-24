# Findings ledger: phase-LR1-r1

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
| codex-1 | The guide says offending_facts are always row objects; a mandatory failure lists a bare instance | yes (skeleton population.bad.yaml: offending_facts [3]) | blocking | fixed | 910b8c2b | step 2 names three witness shapes; test_t10_a_mandatory_failure_lists_bare_instance_witnesses; T7 pins the new sentence |
| codex-2 | The runnable block's output is not compared, and the test reimplements the filter | yes (no output=stdout; the text block is not compared) | blocking | fixed | 910b8c2b | output=stdout; listing is the page's own failed() read by the runner's block reader and ast. Mutations: no constraints printed fails the tutorial node; dropped derivation filter fails T8 |
| codex-3 | T3 checks a listed subset, not every documented field | yes (by reading) | hardening | fixed (code), deferred (prose) | 910b8c2b | T3 now requires the set of keys the page's code reads to equal the listed set; a bogus key read fails T3 (mutation run). A field named only in prose stays unchecked: no Markdown parser in the default environment. Residual in the phase record |
| codex-4 | T5 does not assert the redaction markers | yes (by reading) | hardening | fixed | 910b8c2b | T5 asserts message equals gnd.redaction.INSTANCE_DETAIL and one marker object with redacted true and subject_label roles |
| codex-5 | The section reader splits on a heading prefix and misreads a fenced block | yes (by reading the split) | hardening | fixed | 910b8c2b | the splitter is removed; nothing reads the section by text any more |
