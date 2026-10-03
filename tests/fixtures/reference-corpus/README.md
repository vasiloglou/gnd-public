# v7.1 Phase 2 reference corpus

Status: proposed exact bytes awaiting the corpus owner mark. The design was approved on 2026-09-29; that did not approve these uncreated answers.

Read the dispatch/release base models, candidate files and fixed catalogs, then `inputs.json` for each narrated scenario. The expected outcomes are split into `answers.json`; `manifest.json` binds every corpus file. There are no wall-clock rules or external services.

Each model requests two candidate facts to form a pair; the immutable catalog owns the allowed-pair fact type. The guarded existential rule requires the requested pair in that catalog. Neither reference file must independently satisfy candidate-dependent domain constraints. Additional context-only scenarios prove that nonvacuous domain evaluation is distinct from candidate production credit.

The executable instrument is `tests/test_v71_phase2_references.py`. Every feature case first demonstrates that the unmodified v4 reference control validates and checks at zero, so an absent lane cannot make negative refusals accidentally pass. That shared control is deliberately RED before implementation. Runtime branch observations remain unproved until the final instrument executes them; a shared-control failure is not a test of their eventual semantics.

The tests materialize narrated edits and bounded scaling documents in private temporary directories. They never derive expected answers from production output. Path-swap cases accept only the approved descriptor snapshot or input refusal, with an additional fresh-invocation stale-hash refusal. Corpus integrity checks include known-dirty input/answer/inventory controls.

Fixture location follows the existing exact Phase 0 registry at `tests/fixtures/v71/phase2`, correcting the draft's prospective `v71-phase2` spelling without changing case meanings.

Corpus clarification: the existing v10 partition has exactly `admitted` and `blocked` arrays, not contested/withheld terminology. The candidate-only exhaustive set is unchanged; the fixture instrument uses the actual frozen field spellings. Parser depth is measured by a direct new `validate_reference_structure(document)` guard: root container is level one, scalar leaves add no container depth. It accepts 64 levels and raises `ReferenceInputError` at 65. Typed population validation is still a subsequent distinct stage.

Legacy identity and report projection fields in `answers.json` were captured from the unchanged pre-Phase-2 producer at source `31abfdd3b0187291cc8a66eb0a5d88e2e61294ca`. They freeze compatibility observations, not expected answers from a new reference implementation. The newly authored domain/refusal answers remain independent of implementation. Model replacement cases allow exactly 0 (approved bytes consumed) or 3 (safe refusal), never success under substituted bytes.
