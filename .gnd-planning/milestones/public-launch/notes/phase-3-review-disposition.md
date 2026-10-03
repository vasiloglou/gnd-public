# Phase 3 independent review disposition

Two findings reproduced against bb14d18 before repair. The regression run returned
2 failed in 0.15s, exit 1; after repair, 2 passed in 0.09s, exit 0.

F1: blocking, medium severity. Both wheels could omit review-contract.md without
failing the retained payload check. Compare the complete skill resource set to
the existing independently pinned inventory and run all packaged-skill resource
and relative-link controls against each installed wheel. The omitted-resource
mutant exercises the actual payload checker and now fails.

F2: hardening, medium severity; fixed here because the acceptance instrument is
this phase's deliverable. A collect-report skip escaped the runtest-only hook.
The shipped plugin now captures collection skips as well. A passing test plus a
skipped collection report previously yielded an empty skip list; the regression
now requires that report in the list. No existing selected module was shown to
have such a skip; this is a demonstrated instrument gap, not an invented product
failure. Optional marker deselection remains distinct from unexpected skipping.

No product code or expected result changed. Neighbor checks and installed
resources must rerun on repaired acceptance code. A bounded repaired-diff follow-up
is selected after the focused gate; no approval is claimed until it returns.
Refactoring: reuse the existing pinned skill inventory instead of introducing a
second inventory; retain the installed gate in one program with a direct hook
control. No unrelated structural rewrite or hidden deferred refactor is selected.
