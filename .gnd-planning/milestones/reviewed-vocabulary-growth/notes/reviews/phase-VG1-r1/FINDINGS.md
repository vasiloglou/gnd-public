# Findings ledger: phase-VG1-r1

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
| codex-F1 | a code-built model with a str-enum `kind` and a plain loaded model share a cache key; the cached tables answer from the first model's rows, so `_kind_of` returns `K.VALUE` for the plain model and a range check reads `vacuous` for `fail` | yes | blocking | fixed | 7e235d4a | Reproduced: `_kind_of` returned `K.VALUE` for the plain model after the enum model warmed the cache; the digests are equal. Blocking because C1 claims every loadable model. Test `test_R1_F1_a_cached_index_never_answers_for_a_model_whose_values_differ`, failed before 7e235d4a. The tables are built from the canonical JSON form the key is a digest of. The collision itself is older than VG1 and still reaches the index's other readers (record, open questions) |
| codex-F2 | the table resolves every type before removing covered ones, so a code-built model whose `reference` is a string raises `AttributeError` where the base returned `set()` | yes | hardening | fixed | 7e235d4a | Reproduced: `_denoting_types({"v", "e"}, model)` raised `AttributeError`. Hardening: only a model built in code can hold that shape. Test `test_R1_F2_a_malformed_reference_in_a_code_built_model_does_not_raise`, failed before 7e235d4a. Such a type resolves to None |
