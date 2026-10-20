Retained output; edited only to replace machine repository/user paths.
Original SHA256: f076d520d4d7ef301649b26df05259bc5335568698346bc7eb619e436551ce9c

Three actionable **static finding candidates**; none was reproduced because tests and execution were prohibited.

1. **[P1] Cancellation can consume an unreturned attempt.** [api.py:1018](<REPO>/src/gnd/api.py:1018) advances `_feedback_attempt` before the transaction exits. A cancellation immediately afterward discards cache staging without restoring the counter.

   **Falsifier:** warm a session, inject `KeyboardInterrupt` at `_call`’s line 1020, then retry the same attempt. Generation/cache should remain unchanged and the retry should succeed; current code predicts an “attempt” refusal. Counter advancement needs transactional rollback.

2. **[P2] The reader invents missing wire discriminators.** [evaluation_feedback.py:54](<REPO>/src/gnd/evaluation_feedback.py:54) defaults `kind`, `schema_version`, and `operation`. Missing tags therefore become valid version-1 feedback.

   **Falsifier:** remove each tag independently from emitted JSON and call `SessionFeedback.model_validate_json`. The strict wire reader should reject each document; current declarations supply defaults instead.

3. **[P2] Encoded feedback bypasses duplicate-key rejection.** [evaluation_feedback.py:64](<REPO>/src/gnd/evaluation_feedback.py:64) passes bytes directly to Pydantic, bypassing the repository’s shared duplicate-key policy.

   **Falsifier:** replace `"schema_version":1` in valid feedback with `"schema_version":2,"schema_version":1`. Expected: rejection. Predicted current behavior: acceptance as version 1 after duplicate-key collapse. Apply duplicate rejection before schema validation.

The remaining inspected paths support these claims:

- Observation composition uses fresh serialized bytes and the normal loader, preserving ordered replacements, duplicates, omitted relations, and detached containers. Observation staging is discarded.
- Normal rejection and feedback-construction exceptions preserve committed cache state and attempt numbering. Reset preserves lifetime numbering. Valid exit-4 feedback still discards staging.
- The builder enforces 128 rows, 256 identifier characters, 16 KiB canonical UTF-8 including the newline, and count maximum `2147483647`. Available-empty, unavailable, not-evaluated, and overflow remain distinct.
- Persistent contract implementations are unchanged. The helper has a checking-layer entry, source-scan coverage, no API/experiment-runtime import, and no added allowance.
- The approved spec matches the amendment hash. I read the no-op, multibyte-bound, rollback, and two-attempt course payload/branch/feedback controls; their structure does not replace runtime verification.

One reviewer is one reviewer. No files were written, tests run, agents spawned, network/providers contacted, or credentials/`.env` read. This establishes no installed-artifact, performance, publication, or certification claim.