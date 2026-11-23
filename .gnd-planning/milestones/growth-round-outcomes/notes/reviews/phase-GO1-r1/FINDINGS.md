# Findings ledger: phase-GO1-r1

Reviewer: codex (review helper, `--subject phase`, base `2814d9be`, reviewed
commit `84c8df0b`). One reviewer is one reviewer.

| Reviewer | # | Finding | Reproduced | Class | Disposition | Repaired at | Notes |
|---|---|---|---|---|---|---|---|
| codex | F1 | The write check misses a change of only a mapping tag or a key's type (`1` to `true`) | yes: both mutations passed scope close at `84c8df0b` | hardening | fixed | the GO1 repair commit after `84c8df0b` | No evolve path writes into a parsed document (the lane passes with the check on), so no wrong output today; the check, the control of GO1-C3, was blind to these writes. The snapshot is now the round-trip YAML writer's text. `test_t3_r1_the_check_sees_a_tag_or_key_type_change[tag, key-type]`, both fail at `84c8df0b` |
| codex | F2 | An unchanged anchored tagged scalar (`x: &a !foo abc`) fails the write check | yes: AssertionError with no write at `84c8df0b` | hardening | fixed | the GO1 repair commit after `84c8df0b` | Test-only false positive (the check is off outside tests); it would replace a named refusal with AssertionError in a test. Same repair as F1. `test_t3_r1_an_unchanged_anchored_or_tagged_node_is_not_a_write[x: &a !foo abc, x: &a [1, 2]]` fail at `84c8df0b`; the `!!set` case passes on both |
| codex | F3 | A context copied while a scope was open keeps reusing its documents after the scope closes | yes: `saved.run(second)` returned the stale, written document at `84c8df0b` | hardening | fixed | the GO1 repair commit after `84c8df0b` | No evolve path copies a context; a library caller could. Each scope now carries an `open` flag cleared on exit, and its documents are dropped. `test_t6_r1_a_context_copied_from_a_closed_scope_does_not_reuse_it`, fails at `84c8df0b`. While a scope is open, a context copied from it (`asyncio.to_thread`) does share it; the spec's "does not cross threads" is restated in §13 |
| codex | (note) | The `.json` count test had no scope-off control | yes | completeness | fixed | the GO1 repair commit after `84c8df0b` | `test_t1_a_json_workspace_stays_within_the_bound` now runs both and requires the scope-off counts to be larger |

No finding was blocking, so the phase's review budget (a second round only if
the first blocks) ends here. The repaired bytes of `src/gnd/model/_parsing.py`
and the new tests carry no review opinion.
