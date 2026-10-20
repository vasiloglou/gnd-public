Retained reviewer output; edited only to replace the machine-specific repository root with <REPO>. One CLI reviewer, not a panel.

Four blocking findings and one hardening finding survived static review.

1. **Blocking — copied contexts retain transaction authority.** [incremental_state.py:247](<REPO>/src/gnd/incremental_state.py:247) checks only `_ACTIVE is self`. A context copied during a transaction remains accepted after exit and can access a later transaction’s candidate or call `discard()`. It also retains the old ModelIndex scope. **Regression:** save `copy_context()` in transaction A; after A exits, invoke `reuse()` through it, then repeat during transaction B. Both stale-context calls should refuse.

2. **Blocking — options fingerprints escape the byte budget.** [incremental_state.py:217](<REPO>/src/gnd/incremental_state.py:217) constructs the options fingerprint, and line 230 retains it without accounting against `max_bytes`. `close()` also leaves `_binding` retained. **Regression:** use a tiny byte cap and a large string inside `options`; complete an empty transaction and close the state. Currently substantial fingerprint storage survives while reported cache bytes remain zero.

3. **Blocking — container accounting omits owned backing storage.** [incremental_state.py:72](<REPO>/src/gnd/incremental_state.py:72) counts a `MappingProxyType` wrapper and its contents but omits the backing dictionary created by `_clone`. Ordinary dataclass instance dictionaries are similarly omitted. The fixed per-entry allowance cannot cover arbitrarily many such containers. **Regression:** cache a proxy containing 10,000 integer keys, with a cap between the measured projection and the backing-inclusive size; storage should bypass instead of exceeding the cap.

4. **Blocking — policy expansion lacks a cumulative bound.** [incremental_state.py:131](<REPO>/src/gnd/incremental_state.py:131) limits tuple width and depth independently, without a node budget or memoization. Repeated shared tuples expand exponentially before signature measurement or evaluation. **Regression:** start with `(0,)` and wrap it three times as `(previous,) * 1000`; this compact input should bypass within a bounded walk.

5. **Hardening — malformed dependency shapes can produce a clean selection.** [incremental_state.py:165](<REPO>/src/gnd/incremental_state.py:165) trusts a parser that silently ignores malformed bodies. The conservative fallback checks unknown changed identifiers, not graph completeness. **Regression:** replace `left_copy`’s body with a mapping and change `left`; require conservative invalidation or explicit refusal, rather than an empty result. This currently affects diagnostic selection; no evaluator consumes it.

Verified by inspection:

- Fresh independent index lookup includes operations and restores the outer scope.
- Escaping exceptions/cancellation discard candidates; normal publication, overlap refusal, and closed → busy → foreign-model ordering are present.
- The reverse worklist closes transitive dependencies and SCCs represented by valid parser edges, including negative and aggregate dependencies.
- Layer allowances remain zero; the only new assignment is `gnd.incremental_state` to checking. No model-query waiver or runtime evaluator skipping was added.

All supplied hashes initially matched. During review, the successor helper changed to `4249acfb…`. The later version includes IE1; static AST/JSON inspection confirmed its seven additions, predecessor hash, and resulting counts.

Limits: one read-only reviewer; no runtime, tests, benchmarks, credentials, agents, providers, or network invoked. Regression cases above are proposed, not executed; no passing-gate claim is made.