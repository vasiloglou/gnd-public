# GC1 candidate verification

The GC1 candidate implements the delegated [spec and corpus gate](../002-phase-GC1-spec-gate.md).
The independent phase-diff review and completion record are pending.

| Gate | Exit | Observed result |
|---|---:|---|
| Focused membership, schema, guarded evaluation, derivation, synthesis and verbalization | 0 | 326 passed in 93.32s (0:01:33) |
| Focused PyRel, Lean, Ossie and Soufflé exporter gate | 0 | 159 passed, 93 deselected in 12.74s |
| Issue #171 guards and layer checks | 0 | 679 passed, 2 deselected in 140.15s (0:02:20) |
| Ruff | 0 | All checks passed! |
| Component check against main | 0 | 0 to fix, 0 warnings, 11 entries to reread |
| git diff --check | 0 | Empty output |

The first exporter run's fake-executable file-mode test reproduced its failure
on the pre-change commit. A direct chmod probe showed the sandbox cleared the
requested mode bit. The exporter table records the complete rerun in the runner
that preserved the fixture mode. The two new fact-type scans caught by the
first guard run were converted to ModelIndex lookups before the successful
rerun. The RF6 direct-query allowance count stayed at its prior level. The
counted dynamic-inventory [successor](../evidence/GC1/dynamic-query-successor.json)
accounts for the changed syntax selectors.

The component check's reread entries cover reconstruction's verbalization
dependency, the PyRel, Lean and Soufflé exporters, extension calculation,
snapshot decision, verbalization, snapshot IR, adaptation, reference semantics,
and the temporal guard path. Their declared capabilities remain accurate.
Catalog generation also refreshed an inherited stale tool inventory.

The data comparisons use the existing guarded and derivation validation
entry points. The new reason IDs identify membership problems at those
entries, preserving the relative ordering of the old type checks. The
runtime separates explicit membership identity from the old equality
operators, including Boolean and temporal cases.
