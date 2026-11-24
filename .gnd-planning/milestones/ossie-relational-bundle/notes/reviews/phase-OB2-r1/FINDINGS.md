# Findings ledger: phase-OB2-r1

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
| F1 | The identifying external uniqueness ignored `preferred` and confirmation, and depended on declaration order | yes (R1 red, both variants) | blocking | fixed | the OB2 review-repair commit | `test_r1_identification_uses_the_preferred_confirmed_external_uniqueness`. The Rmap selects the confirmed alethic, preferred external uniqueness, and refscheme is no longer used. |
| F2 | Deduplication kept the first duplicate and lost a later duplicate's `preferred` | yes (R2 red) | blocking | fixed | the same commit | `test_r2_a_preferred_duplicate_keeps_its_preference`. A key is preferred if any duplicate is, and duplicates share one disposition. |
| F3 | `unique_keys` order followed declaration order | yes (R3 red) | blocking | fixed | the same commit | `test_r3_unique_key_order_ignores_declaration_order`. Unique keys are sorted by column position. |
| F4 | An external uniqueness whose columns lie in one table was reported as `spans-tables` | yes (R4 red) | blocking | fixed | the same commit | `test_r4_external_uniqueness_within_one_table_is_a_unique_key` |
| F5 | An objectified uniqueness narrower than the key was reported as `primary_key`, and no unique key was made | yes (R5 red) | blocking | fixed | the same commit | `test_r5_objectified_uniqueness_narrower_than_the_key_is_a_unique_key` |
| F6 | ALTERNATE dropped a subtype's foreign key when its supertype had no table | yes (R6 red) | blocking | fixed | the same commit | `test_r6_alternate_subtype_keeps_its_supertype_foreign_key`. The supertype gets a table. |
| F7 | A role played by a value type with a table got no foreign key | yes (R7 red) | hardening | fixed | the same commit | `test_r7_a_role_played_by_a_tabled_value_type_is_a_foreign_key`. Census foreign-key counts rose; the variant comparison is unchanged (4 of 66). |
| F8 | An absorbed unary column was non-nullable | yes (R8 red) | blocking | fixed | the same commit | `test_r8_an_absorbed_unary_is_nullable` |
| F9 | Composite identification was superlinear: refscheme rebuilt maps on each call | yes (R9 red: ratio above 8 at 4×) | blocking | fixed | the same commit | `test_r9_composite_identification_is_not_superlinear`. Identifiers are indexed once per model. |
