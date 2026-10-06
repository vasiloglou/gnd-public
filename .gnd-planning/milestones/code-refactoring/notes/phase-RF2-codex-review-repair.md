# RF2 bounded repair review

2026-10-05. One reviewer is one reviewer. Findings below retained verbatim except absolute worktree paths replaced with `<worktree>`; this sanitization is the only edit. Same owner-authorized RF2 review destination, gpt-6-sol/xhigh/read-only, no test suite run.

## Findings

1. **The v1 successor pins fail on Python 3.11 and 3.13.** [assert_successor](<<worktree>/tests/support/rf2_session_pins.py:154>) selects the interpreter’s original golden, but [session-successors.json](<<worktree>/tests/fixtures/rf2-pins/session-successors.json>) stores the Python 3.14 SHA-256 for both v1 cases. The retained 3.11/3.13 goldens have different hashes, so those nodes fail before comparing behavior. Generate and test successors for each supported interpreter while keeping each original golden bound.

2. **The closed exit allocation guard still has a false-green path.** [test_rf2_helpers.py:152](<<worktree>/tests/test_rf2_helpers.py:152>) skips every assignment whose value is an AST `Name`. In a read-only, in-memory reproduction, adding `NEW_CODE = 19; EXIT_EXTRA = NEW_CODE` outside `exits.py` left the guard green. Trace aliases to known `exits` allocations or check the resulting namespace union; retain this declaration as a failing regression.

3. **RF2 capture does not always enforce the original-golden comparison.** [assert_successor:160](<<worktree>/tests/support/rf2_session_pins.py:160>) calls `assert_golden` before writing a successor, but `assert_golden` switches to write-only capture when `GND_RF1_CAPTURE` is also set. An altered observation could therefore be captured without passing the original answer. Reject that environment combination or compare directly with the historical bytes; test the dual-capture case.

4. **The new declared-input JSON branch loses byte identity.** [project_input:111](<<worktree>/tests/support/rf2_session_pins.py:111>) parses valid JSON before comparison. Two byte-distinct inputs differing only in whitespace produce the same projection, as a read-only call confirmed. All four current successors use its text branch, so this has not hidden a difference in those cases; the JSON branch is unexercised and does not meet the stated byte-pin contract. Compare token-normalized raw text or retain a byte digest, with a whitespace mutation control.

## Confirmed scope and limits

The original RF1 goldens and manifest are unchanged. For each of the four successors, I compared its observation with the original golden: they match after exactly the two declared execution-identity substitutions. The mint hook captures the encoder input, independently checks its bytes and digest, and checks the producer identity. The 16 retargeted mutation rows retain their IDs and `expect_red` sets; the recorded run killed all 16 through failing call nodes. The two actual `is_sha256_hex` consumers retain acceptance of `None`; the predicate itself returns false for `None`.

The prior provenance lookups now use the renamed function. The scan control observes actual scan visits, and annotated and computed exit assignments are covered; finding 2 is a remaining alias-form gap. Final recorded G1, G3, G4, and G5 exits are 0. The direct controls report 57 passed. The budget file still calls for a **post-commit comparison**, so it is not a completed G6 claim. Source-base capture and replay each report four passed, but their terse output does not independently establish the checkout identity or capture environment.

I made no modifications, ran no test suite or provider tool, and performed no certification. **One reviewer is one reviewer.**