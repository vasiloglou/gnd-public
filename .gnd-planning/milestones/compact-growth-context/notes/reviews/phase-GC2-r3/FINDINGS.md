| Id | Finding | Reproduced | Class | Disposition | Repaired at | Notes |
|---|---|---|---|---|---|---|
| F1 | Canonical reference digest rejects legal free-form nonfinite metadata during load | yes | blocking | fixed | 8bd28b16 | test_composed_snapshot_accepts_nonfinite_source_metadata reproduced ValueError before repair. Vocabulary provenance now uses the existing non-JSON-compatible positional digest independently of reference identity. |
