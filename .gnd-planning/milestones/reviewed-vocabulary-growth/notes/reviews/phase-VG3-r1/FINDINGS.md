# Findings ledger: phase-VG3-r1

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
| codex-F1 | U7 read `provenance.sample_spans` on included object types and constraints; a malformed one there refused a root 0.4.0 accepts, and a well-formed one was not counted | yes | blocking | fixed | 01b76996 | Reproduced: the reviewer's case exits 3 with U7 at `702496c8` and 0 at the base. Blocking because VG3-C10 claims every root 0.4.0 validates. Test `test_R1_F1_sample_spans_are_read_on_included_fact_types_only`, failed before 01b76996 |
| codex-F2 | the `[id=…]` selector pattern `(.*?)` stops at a newline, so an issue on an included object type whose id holds one loses `includes[ID]:` | yes | hardening | fixed | 01b76996 | Reproduced: the excerpt-mismatch path had no prefix. Hardening: an id holding a newline validates but no shipped model has one. Tests `test_R1_F2_an_identifier_with_a_newline_keeps_its_include_prefix` and `test_R1_F2_remap_matches_the_whole_declared_identifier[x[id=y]]`, failed before 01b76996. The selector is now matched as whole text, longest first |
