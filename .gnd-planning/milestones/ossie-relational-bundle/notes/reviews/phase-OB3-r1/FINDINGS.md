# Findings ledger: phase-OB3-r1

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
| F1 | A composite identifier's object mapping read the key's original column names, not the table's renamed ones (`code`, `code` instead of `code`, `code_2`) | yes (R1-F1 red) | blocking | fixed | the OB3 review-repair commit | `test_r1_f1_composite_object_mapping_reads_the_renamed_key_columns`. `Identification.columns` are the owning table's own key columns. |
| F2 | A 250-role fact type crashed the default export with `RecursionError` (exit 70), while `--ontology-only` succeeded | yes (R1-F2 red, at 33 and 250 roles) | blocking | fixed | the OB3 review-repair commit | `test_r1_f2_a_high_arity_fact_type_is_listed_not_nested`, `test_r1_f2_the_arity_limit_itself_is_mapped`. A fact type with more than 32 roles keeps its table and is listed as `arity-over-limit`. The reason is new, so the owner sees it with the record. |
| F3 | Two foreign keys from different tables could take one relationship name (`a__b__c`) | yes (R1-F3 red) | blocking | fixed | the OB3 review-repair commit | `test_r1_f3_relationship_names_are_unique_in_the_document`. The Rmap makes foreign-key names unique in the schema, in sorted table order. This amends OB2's A11, so the owner sees it with the record. |
| F4 | `#`, `?` and `%` in the output file name were written unescaped into the mapping's `iri` values | yes (R1-F4 red, three names; two controls passed) | hardening | fixed | the OB3 review-repair commit | `test_r1_f4_references_are_iris_of_the_written_file_names`. The file name is percent-encoded. |
| F5 | A model that maps to no table writes three files, so its fact types and constraints are listed nowhere in the relational layer | yes (it is implementation finding IF1) | completeness | open | — | The pinned core-spec requires a dataset, and a mapping must reference a semantic model, so no valid relational file can hold the list. Whether to accept the three-file run or refuse such an export is the owner's decision, put with the record. `test_no_table_means_no_relational_files` pins the current behaviour. |

