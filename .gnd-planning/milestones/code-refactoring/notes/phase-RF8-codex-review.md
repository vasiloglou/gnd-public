# RF8 independent Codex review

Retained verbatim except absolute worktree/home paths replaced by <worktree>/<home>.
Reviewed production commit:6a0875097ae3547bf829c3818606487cc63b4060.
Provider transmission explicitly authorized by owner reply approved,2026-10-06.

One reviewer is one reviewer. I found two reproducible gaps in the RF8 claims.

1. **The v7 shim loses an existing binding.** `_HIDDEN` was defined in `session_v7` on the base commit and now lives in [session_replay.py](<worktree>/src/gnd/exp/session_replay.py:161), but [session_v7.py](<worktree>/src/gnd/exp/session_v7.py:50) does not reexport it. A bytecode-disabled probe confirmed `hasattr(session_v7, "_HIDDEN")` is false while the replay module has it. Thus a previously valid `from gnd.exp.session_v7 import _HIDDEN` raises `ImportError`. Reexport the same sentinel object and include original top-level definitions in the binding control, alongside the 47 imports.

2. **An empty reconstruction can leave the public best identity stale.** The no-contract, no-attempt path in [session_replay.py](<worktree>/src/gnd/exp/session_replay.py:270) returns before updating the caches set at line 499. In a read-only probe, a store with a previously cached best identity and now-empty attempts and launches returned a `ResumeState` with no best, while [best_identity()](<worktree>/src/gnd/exp/session_store.py:1693) still returned the old identity. This can occur if evidence is cleared while the same store object remains in use. Clear `_best_identity` and `_v7_best` on that successful empty-state return.

I read the RF8 spec and amendments, the bounded source and test diff, and the permitted small predecessor controls. Source comparison and small probes supported the profile version table, valid-version copy refresh, schema exclusion, and absence of an import cycle among 14 inspected session modules. I did not rerun the reported replay or consumer suites, so their pass counts remain reported evidence rather than independently verified results. No files were edited.
## Reproduction and disposition

Both findings are blocking: R1 violates SM2 import compatibility; R2 violates the new public best accessor contract. Before repairs, review-red exits1 with3failed (sentinel and cache versions7/8). No other findings were accepted.
