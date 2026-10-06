# RF8 bounded Codex repair review

Retained verbatim except worktree/home absolute paths replaced by <worktree>/<home>.
Reviewed production:5bd3ea2fcda859c3528d4a419d2fdf487fe39fe7.
This is the one authorized repair review; no third review round selected.

**No reproducible repair blocker or hardening issue found** in this bounded RF8 review.

- The [v7 shim](<worktree>/src/gnd/exp/session_v7.py:54) is 58 lines. A bytecode-disabled probe confirmed all 47 imported bindings, all nine moved definitions, and the `_HIDDEN` same-object alias. `_project` returns that sentinel for an actual hidden set.
- The [empty reconstruction branch](<worktree>/src/gnd/exp/session_replay.py:270) clears both public best caches. In-memory pre-fix probes reproduced stale caches for versions 7 and 8; the repaired path cleared them. Failure and terminal refusals retained their caches. The normal reconstruction path remains outside the edit.
- The [AST observer](<worktree>/tests/support/rf8_sources.py:27) normalized the exact two assignments to the pre-fix body. Probes showed added statements and a dirty tail still change its output. The pre-fix shim lacked the sentinel binding, supporting the third declared regression.

I did not run the exact pytest nodes, the bound-contract normal replay, or the reported 66-pass and native 44-pass matrices. Those counts remain reported results, not independent results from this review. This review made no edits. One reviewer is one reviewer.