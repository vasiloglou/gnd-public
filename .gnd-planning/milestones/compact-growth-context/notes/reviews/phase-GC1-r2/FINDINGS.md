| Id | Finding | Reproduced | Class | Disposition | Repaired at | Notes |
|---|---|---|---|---|---|---|
| F1 | Derived types lose declared computation metadata | yes | blocking | fixed | 5848faf8 | test_full_inventory_and_size compares declared derivation and storage. Free-text rule bodies stay in the underlying model. |
| F2 | Object independence omitted | yes | hardening | fixed | 5848faf8 | Project authored independence and verify each source object's flags. |
