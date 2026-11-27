| Id | Finding | Reproduced | Class | Disposition | Repaired at | Notes |
|---|---|---|---|---|---|---|
| F1 | Invalid nested mutation reaches renderer | yes | blocking | fixed | c4da7347 | test_loaded_growth_model_refuses_invalid_role_player failed before repair. Validate an in-memory snapshot through the model loader before projection. |
| F2 | Direct lookup and ambiguous passage absent from host example | yes | blocking | fixed | c4da7347 | The packaged example now runs a direct lookup and defers a separate document with both IDs and no directed relation. The public test checks the resulting record and document digest. |
