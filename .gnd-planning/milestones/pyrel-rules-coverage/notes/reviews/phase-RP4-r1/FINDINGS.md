# Findings ledger: phase-RP4-r1

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
| F1 | A range helper's universe (`<type>_any`), rendered for role-scoped rules, was not in the name-collision check, so a fact type of that name was overwritten | yes by reading `_refuse_name_collisions`; the regression test confirms the refusal | blocking | fixed | RP4 phase commit | range universes join the generated names; `test_a_fact_type_named_like_a_range_universe_is_refused` |
| F2 | Admitting `value` in the fact-scoped dispatch changed Ossie's output for a fact-scoped value rule without `role_ref` (plan §0: Ossie unchanged) | yes: Codex's comparison against `f02c58d8`; the digests now equal those bytes | blocking | fixed | RP4 phase commit | Ossie keeps fact-scoped value rules as extensions; Ossie pin for `rp4/fact-plain` (digests at `f02c58d8`) |
| F3 | Two cumulative tests failed: a range rule's `<id>_allowed` type lookup read allowed lists only (`StopIteration`), and RP2's quantity-fixture test still expected the RP4 refusal | yes: the focused lane failed the same two | blocking | fixed | RP4 phase commit | `_Model.value_rules` resolves any value rule; RP2's test now asserts the fixture renders and lists its anchored rule |
