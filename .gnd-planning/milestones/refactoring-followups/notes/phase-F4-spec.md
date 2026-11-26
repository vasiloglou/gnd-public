# F4 · Model and population intake and canonical panel output

Delegated approval (auto=true), 2026-11-25. Plan r2 §§0, 4, 6, 9 and 10, issues #301 and #302, and the C20/C24/B4 close rows govern this scope.

## Baseline and decisions

All three direct output calls in gnd.review.service form their payload from strings, enums, counts, booleans and None, including the summary for below quorum. None accepts an arbitrary float. The Python compatibility alias is callable with arbitrary dictionaries. Set allow_nan=False at gnd.output._canonical_payload so nested NaN and both infinities refuse before printing. Preserve finite text including Unicode, separators and ordering. Bind the historical Q2 fixture delta to its original hash.

The public model reader already uses a capped binary read; the population reader checks file kind, fstat size and capped read. F1 covers the pool file. Model and population also pre-scan YAML for alias and event budgets. Both lack a collection-depth check before construction. D1 selects the existing input_policy.MAX_DEPTH (64 collections) for those two public readers. Preserve each existing error class, scanner configuration, alias/event diagnostic and model block scalar handling. Avoid reparsing. The production event-depth policy belongs to input_policy; the reader owns its error wording. Measure legal depth and first crossing, rejection before node construction, and ordinary legal inputs. Run a time-bound finite nested input at the added layer. No new parsing pass or per-element copying.

D2 keeps current media typing for historical session profiles. Injecting a host MIME registration changed the measured candidate MIME type for an unchanged file from application/octet-stream to text/x-local. Pin this as a compatibility dependency and record a future explicit media table/version ruling under #302. D3 retains consumer-specific domain errors and JSON decoder exceptions at existing APIs; inventory the other YAML loader and upstream read paths with their trust boundaries. Keep broader migrations tracked at #302. Domain boundaries: model raises ModelLoadError, population raises PopulationLoadError, pool size raises PoolValidationError, review writer raises ValueError on nonfinite JSON. Scope is these named boundaries.

## Verification and budget

Exercise the public model/population byte loaders and bounded path controls, the three nonfinite output values, exact finite bytes and the three existing review CLI output branches. Verify input_policy, the RF1 helper pin and affected default-lane reader tests. Target 25–60 production lines, 45–85 test lines and one independent Claude diff review. Basis for delegated gate is this prose and the focused exact/crossing examples.
