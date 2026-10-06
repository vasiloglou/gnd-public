# RF9 reviewer C: state and input

Native Codex gpt-6-sol/xhigh, read-only initial area, successful capacity retry exit0. The first attempt exited1 before a final assessment. Fixed source:d440b2e37449ef46647d18c491c46d9bb8d3e851; base:f5a83186f7c2215ac2b2afb0a010c2294eaa433a.
Prompt SHA-256:63452ec82f52a4ca2c0e9c362c73c2b6b18303b0d236a1dd0954a2ee7d51a7c5.
The return below is verbatim except absolute worktree/home paths replaced by <worktree>/<home>. Primary reproduction and disposition are separate; no repair review ran.

## Area C review of `d440b2e`

**Two current defects survive review. Both were present at the fixed pre-refactor base `f5a8318`; neither is a newly introduced RF2–RF8 regression.** The checks below are advisory and do not certify the rest of the implementation.

1. **P1 — An accepted terminal claim can close over a nonaccepted best attempt.** For a version 7 session contract with no walk floors, a well-formed, eligible attempt can fail acceptance and still become `best.json`. If its `result.json` disposition and reason are changed to `accepted`, the [result validator](<worktree>/src/gnd/exp/session_records.py:788) requires a best identity but does not relate the disposition to its evaluation. [Replay](<worktree>/src/gnd/exp/session_replay.py:478) validates the retained feedback but does not check a version 6 terminal disposition. The [close gate](<worktree>/src/gnd/exp/close.py:953) verifies the best identity, then has no walk-floor rows to test; its [caller](<worktree>/src/gnd/exp/close.py:1185) has already accepted the terminal claim. Expected: refuse a best attempt whose required cases failed. Observed in a focused in-memory probe, with reconstruction represented by a nonaccepted best record: `accepted claim: True` and `close findings: []`. This isolates the gate logic; a full filesystem run was not performed. The same path exists at the fixed base.

2. **P2 — A claimed best attempt with no reconstructed best causes a traceback.** An accepted version 6 result can name a best identity while the run has no eligible attempt or best pointer. Reconstruction permits a `None` best; [close dereferences it](<worktree>/src/gnd/exp/close.py:966) and catches only `OSError` and `ValueError`. Expected: a close finding for mismatched evidence. Observed in a focused in-memory probe: `AttributeError: 'NoneType' object has no attribute 'attempt_index'`. At the fixed base, the corresponding `None` unpack also escaped the same catch.

The earlier hypothesis about falsifying *feedback* disposition did **not** survive: the [feedback validator](<worktree>/src/gnd/exp/session_eval.py:1365) and replay’s regenerated feedback bind it to acceptance. Finding 1 concerns the separate terminal `result.json`.

**Test-only issue:** [An RF6 test](<worktree>/tests/test_rf6_index.py:36) still expects the `truthy` primitive variant to accept `inherits_reference: "yes"`. A direct `.venv` probe returned `None` for both variants, consistent with the approved RF7 literal-`True` rule. This is a stale assertion, not a product regression. A targeted pytest node could not start because the read-only environment had no usable temporary directory.

I inspected focused regions of the requested Area C modules and their close-gate consumer. I did not inspect the full session wire schemas, all legacy replay paths, every checker and synthesis consumer, platform race behavior, or broad suites. No files were changed.