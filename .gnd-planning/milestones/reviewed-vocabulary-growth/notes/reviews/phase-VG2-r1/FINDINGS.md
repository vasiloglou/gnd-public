# Findings ledger: phase-VG2-r1

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
| codex-F1 | the new D-12 refusal is not in the CLI's exit classifier, so `gnd evolve preview` exits 70 | yes | blocking | fixed | 53280cba | Reproduced: `_evolve_service_exit` returned 70 for the message; six CLI cases printed `REFUSED (70)`. Blocking: VG2-C2 says exit 3. Test `test_R1_F1_the_refusal_exits_3_at_the_command_line` (6 cases), failed before 53280cba. The marker is registered as an RF5 successor (`evidence/VG2/source-successors.json`) |
| codex-F2 | a changed `sample` or `common-sense` constraint that stays `proposed`/`deontic` is now admitted, against the brief's claim that changed constraints are judged as before | yes | completeness | rejected | n/a | Reproduced as described. Not a defect: D-12's home opens "admits a constraint that is new or changed … only under these rules", the code judges both alike as it does for `llm-inferred`, and the contract sentence VG2 edited says so. The claim in the brief was wrong; it is corrected in the record. Pinned by `test_R1_F2_a_changed_sample_or_common_sense_constraint_is_judged_as_a_new_one` |
| codex-F3 | on an unattended model a `confirmed` or `alethic` new constraint is refused by U2 or U8 first, not by the named D-12 refusal | yes | completeness | rejected | n/a | Reproduced. Not a defect: candidate validation precedes D-12 (evolution contract, "Order"), and the exit is 3 either way. The brief's "on any model" overclaimed; the record states VG2-C2 as the D-12 refusal on a model without the mode and exit 3 on any model. T4 holds the U8 order |
| codex-F4 | the documentation guard selects sections by substring, so a heading inside a fenced example is read as the section | yes | hardening | fixed | 53280cba | Reproduced in memory. Test `test_R1_F4_a_fenced_copy_of_a_section_is_not_read_as_the_section`, failed before 53280cba. Sections are read outside fenced blocks, up to the next heading of the same level or above |
