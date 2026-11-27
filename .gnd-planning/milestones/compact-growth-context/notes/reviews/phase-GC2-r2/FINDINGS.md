| Id | Finding | Reproduced | Class | Disposition | Repaired at | Notes |
|---|---|---|---|---|---|---|
| F1 | Mutating an included row leaves positional origin metadata stale | yes | blocking | fixed | 0b0fa734 | test_changed_included_row_requires_reload produced DID NOT RAISE before repair. Loader captures the validated vocabulary digest; the loaded growth route checks it before using the origin map. |
