# Findings ledger: phase-OB4-r1

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
| F1 | An escaped lone surrogate in any string of the binding ended in `UnicodeEncodeError`, exit 70 | yes (R1-F1 red, four positions) | blocking | fixed | the OB4 review-repair commit | `test_r1_f1_a_lone_surrogate_anywhere_is_a_syntax_refusal`. A string that is not Unicode text is `binding:syntax`. |
| F2 | A chain of 1,100 entities identified through one another made `bind` raise `RecursionError`, even with nothing bound | yes (R1-F2 red) | blocking | fixed | the OB4 review-repair commit | `test_r1_f2_a_deep_identifier_chain_is_listed_not_followed`, `test_r1_f2_the_depth_limit_itself_is_mapped`. The identification shape is computed with an explicit stack, and an identifier nested more than 8 deep is not followed. The limit is new, so the owner sees it with the record. |
| F3 | An external uniqueness took the `spans-tables` reason of a referenced fact type although its own roles sat in one table | yes (R1-F3 red) | blocking | fixed | the OB4 review-repair commit | `test_r1_f3_an_external_uniqueness_is_placed_by_its_own_roles`. Placed by the columns of the roles it names; the derived unique key follows. |
| F4 | Which foreign-key group a refusal named depended on the columns' member order | yes (R1-F4 red, one order; the other passed) | hardening | fixed | the OB4 review-repair commit | `test_r1_f4_the_reported_foreign_key_does_not_depend_on_member_order`. Groups are checked in sorted order. |
| F5 | The SQL type lexer accepted a word directly after the parenthesized list (`double(2)precision`) | yes (R1-F5 red, two inputs; two already absent) | hardening | fixed | the OB4 review-repair commit | `test_r1_f5_a_word_after_the_list_needs_a_space` |
| F6 | A schema refusal's pointer did not escape `/` and `~`, so it mis-located and mis-sorted | yes (R1-F6 red) | hardening | fixed | the OB4 review-repair commit | `test_r1_f6_a_schema_refusal_names_an_escaped_pointer_in_sorted_order` |

