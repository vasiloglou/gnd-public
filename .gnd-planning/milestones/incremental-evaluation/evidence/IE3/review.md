Retained output; edited only to replace machine repository/user paths.
Original SHA256: 5ccb9e251313d995f063aa31c0050635602120b49598f9046e31ccc522f8277b

Two findings from the static review:

1. **[P2] Callable hook defaults are absent from the constraint policy key.** [correspondence.py:999](<REPO>/src/gnd/correspondence.py:999) includes registry hooks, but [_policy:147](<REPO>/src/gnd/incremental_state.py:147) records only function identity and code.

   Unexecuted minimal counterexample: install a frequency evaluator `def evaluator(c, s, state=1): return state, []`, warm a session, then set `evaluator.__defaults__ = (0,)`. The snapshot, function identity, code and registry entry remain unchanged. Fresh evaluation returns failure; the session can replay its cached pass. Bind supported hook configuration through bounded keys, or fall back for hooks whose configuration is unsupported.

2. **[P2] The approved integration corpus still lacks discriminating controls.** [test_incremental_sessions.py:82](<REPO>/tests/test_incremental_sessions.py:82) names declared and computed walks, but both iterations omit `post`. Every reporter session transition also omits it. A mutation that drops the facade’s supplied `post` argument would survive these controls. The reference control additionally removes `references` before calling the real API, so it establishes disabled caching without exercising reference binding. These leave declared S7/S8 obligations uncovered; the supplied passing counts cannot establish those claims.

Source inspection otherwise supports these claims:

- The facade is explicit and loaded-input-only, calls existing API orchestration, and retains transaction lifetime/refusal handling. Root, compiled-root, intermediate and declared/computed-post check sites remain present.
- Normal exits `0/1/2` may publish; error/uncheckable exits discard candidates. Exceptions retain IE1 rollback.
- Inline uniqueness keys complete selected fact metadata and ordered relation rows, including non-key cells; other eligible constraints key the complete snapshot. Aliases are included. Reference work, guarded/anchored constraints and clock operands take fresh paths. Aggregation, projection and report counts remain fresh.
- Trusted dataclass fingerprints include class identity and every field under existing bounds and cycle guards. Finding storage charges input rows plus witness rows.
- Receipt minting and consumption make separate deep copies. Mint-copy failure disables reuse; consume-copy failure checks fresh. The failed-mint repair forwards the original exception and branches through the normal builder without a second checker invocation.
- `checking_service.py` and layer allowances are unchanged. Both export assertions add `EvaluationSession`. Successor predecessor hashes match; the query delta describes typed IR reads and retains `308 < 310`.

No tests, agents, network/providers or writes were used. Counterexamples above are static predictions requiring reproduction. The reported fourteen direct passes, reporter reduction below `4878`, and final repair checks remain unverified here. No elapsed-time gain or installed-result claim is established.

The tree changed during inspection; the final session-test blob reviewed was `ee932c3`, with correspondence `d687100`.