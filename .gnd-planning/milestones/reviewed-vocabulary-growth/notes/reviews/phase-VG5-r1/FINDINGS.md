# Findings ledger: phase-VG5-r1

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
| codex-F1 | the include route list omits `gnd discover`, which resolves an include root, while saying every unlisted route refuses | yes | completeness | fixed | 0fc30381 | Reproduced: `discover` over the MC1 include fixture and over the grown example root returns proposals. Completeness: the guidance was wrong, no behaviour. Test `test_R1_F1_the_route_list_names_discover_which_resolves_an_include_root`, failed before 0fc30381 |
| codex-F2 | T4 cut each reply at the next literal `"\n## "`, so a heading inside a fenced block ended a section | yes | hardening | fixed | 0fc30381 | Reproduced with the reviewer's fenced example. Test `test_R1_F2_a_fenced_heading_inside_a_reply_does_not_end_its_section`, failed before 0fc30381. The fence-aware reader moved from VG2's test to `tests/support/markdown_sections.py`; T4 and VG2's T3 use it |
