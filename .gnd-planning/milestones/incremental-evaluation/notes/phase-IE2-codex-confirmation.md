Retained output edited only to replace the machine-specific repository root with <REPO>. One CLI reader, not a panel.

Two remaining static correctness findings:

1. **[P2] `ModelIndex.object_map` is absent from helper-policy invalidation.** The [index policy](<REPO>/src/gnd/extensions.py:1050) binds three methods, but role construction reaches `ModelIndex.object_map` through [primitive resolution](<REPO>/src/gnd/universe.py:56). Its replacement leaves the reuse signature unchanged.

   **Minimal test:** warm the localized ordinary fixture; patch `ModelIndex.object_map` with `staticmethod(lambda model: {})`; retain the original input relations. Fresh output roles become `(('item', None),)`, while warm reuse can retain `(('item', 'String'),)`. Compare complete envelopes and require invalidation.

2. **[P2] Reuse-only index failures escape conservative fallback.** [_incremental_context](<REPO>/src/gnd/extensions.py:1024) calls `ModelIndex.for_model` without an exception boundary. Transaction setup already catches index failures and disables reuse, but this subsequent lookup raises again. The ordinary calculator outside a transaction does not require that lookup.

   **Minimal test:** construct the localized relations, then patch `ModelIndex.for_model` with a classmethod raising `RuntimeError`. Fresh ordinary calculation should succeed; transactional calculation currently reaches the uncaught failure. Require equivalent fresh fallback.

The inspected code supports the specific prior repairs:

- Defining-home replacement of `terms._too_wide` participates in policy binding; live term keyword-default limits are now included.
- Dictionary subclasses select full fallback, preserving possible rows.
- Relation materialization runs before unit hits; caught materialization exceptions return control to the original calculator.
- The diagnostic fingerprint includes relation metadata and distinguishes Boolean/integer cells.
- Dirty SCCs still use the original empty-head calculation; logical counters and branch replay remain intact.

The corrected malformed-row test uses clean term input and an unrelated `unused` relation. The earlier `ticket_status` proposal was unsuitable because it is a negative dependency.

This was one read-only static inspection against `a90e5a3`; neither proposal was executed. The reported eight pre-fix failures and 24 passing tests remain supplied evidence. The tree changed during inspection; I included the added term-default binding and test, with the last observed `extensions.py` blob `42b11f9`. No agents, network, providers, writes, approval, or IE3 integration assessment.