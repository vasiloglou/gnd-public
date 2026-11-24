# Findings ledger: phase-OB2-r2

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
| F1 | An objectification whose composite identification does not resolve crashed rule 2 (`AttributeError`) | yes (R2-F1 red, both variants) | blocking | fixed | the round-2 repair commit | `test_r2_f1_unresolved_objectification_identification_falls_back`. The A5 fallback key is O's key everywhere; identification facts then fall to later rules. |
| F2 | A tie on sorted role references let declaration order pick the identifier | yes (R2-F2 red) | blocking | fixed | the round-2 repair commit | `test_r2_f2_tied_identifiers_ignore_declaration_order`. Ties break on the `role_refs` sequence; any external uniqueness over the identifier's roles is the `primary_key`. |
| F3 | Duplicate external uniqueness with reversed `role_refs` gave two keys and two dispositions | yes (R2-F3 red) | blocking | fixed | the round-2 repair commit | `test_r2_f3_duplicate_external_uniqueness_is_one_key`. Columns in table order; one key per column set. R4's pinned column order changed with it. |
| F4 | ALTERNATE could not inherit a composite identifier | yes (R2-F4 red) | blocking | fixed | the round-2 repair commit | `test_r2_f4_alternate_subtype_inherits_a_composite_identifier` |
| F5 | A value component of a composite key got no foreign key to its tabled value type | yes (R2-F5 red) | hardening | fixed | the round-2 repair commit | `test_r2_f5_a_tabled_value_component_of_a_composite_key_is_a_foreign_key` |
| F6 | An identification over a computed fact type stayed the primary key | yes (R2-F6 red) | blocking | fixed | the round-2 repair commit | `test_r2_f6_identification_over_a_computed_fact_type_takes_its_reason`. Such a uniqueness identifies nothing and takes `derived-computed`. |
| F7 | External uniqueness over unary roles keyed the Boolean flags | yes (R2-F7 red) | blocking | fixed | the round-2 repair commit | `test_r2_f7_external_uniqueness_over_unary_roles_is_not_a_flag_key`. A unary role is held by the key columns. |
| F8 | External unique-key deduplication was quadratic | yes (R2-F8 red: ratio 6.6 at 4x) | blocking | fixed | the round-2 repair commit | `test_r2_f8_external_unique_keys_are_not_quadratic`. Keys are indexed by column set. |
