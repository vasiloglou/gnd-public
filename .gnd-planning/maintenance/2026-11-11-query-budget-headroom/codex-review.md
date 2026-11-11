# Diff review (Codex), retained verbatim

- Instrument: one reviewer in a different tool. One reviewer is one reviewer.
- Command: `codex exec --ephemeral --config model_reasoning_effort="xhigh" --sandbox read-only --color never --skip-git-repo-check -`, prompt on stdin, exit 0. Model: the tool's configured default.
- Reviewed bytes: the uncommitted working tree over `793618f1` as it stood after the first two sites were replaced (ten conversions, including `extraction_scope.fact_type_scope` and `checking_service._run_check_raw`). The later changes (README, "Dispositions") were not reviewed.
- The output below is unedited (it contains no home-directory path); the trailing "codex exit" line is the driver's.

## Reviewer output (verbatim)

DISPOSITION: revise

ID: R1  
SEVERITY: high  
LOCATION: src/gnd/extraction_scope.py:28  
QUOTE: `for fact_type in ModelIndex.for_model(model).iter_fact_types_shared()`  
PROBLEM: Refutes C2 and C3. An existing caller passes a `SimpleNamespace`: `tests/test_extract_applicable.py:22–26` → `applicable_set()` → `fact_type_scope()`. This previously returned the applicability result; it now raises `TypeError: ModelIndex requires a Model`. I reproduced the existing test against both implementations: base passes, working tree fails.  
FIX: Preserve the accepted duck-typed input behavior, or retain this direct read and select another conversion site. Update the successor inventory accordingly.

ID: R2  
SEVERITY: medium  
LOCATION: tests/test_query_budget_headroom.py:40  
QUOTE: `def test_t2_converted_functions_keep_their_values(models):`  
PROBLEM: T2 exercises only `_structured`, `fact_type_scope`, and `frontier_codes_for`, despite the spec requiring controls for all ten functions. It checks partial results for the latter two and records no baseline output bytes. The test at line 66 also expects `TypeError` for a dictionary, whereas the base raises `AttributeError`, thereby accepting an exception change.

Within this new test file:

- C1’s exact ten conversions, C3’s real caller types, C4’s mutation/escape guarantees, C5’s invocation frequency, C6’s policy chain, and C8’s layering/cycles have no assertions.
- C2 has partial coverage; seven functions and output-byte compatibility are untested.
- T5 measures isolated index calls, so it cannot detect repeated indexing introduced into a caller’s loop.

The new tests all pass despite R1. Existing policy and layering guards passed; the combined focused run returned **51 passed, 1 failed**.  
FIX: Complete the specified baseline controls for every converted function, include the existing `SimpleNamespace` caller, preserve baseline exceptions, and add controls for cache mutation and indexing frequency.

Could not check:

- Full G1/G2 and workflows requiring filesystem writes in this read-only environment.
- Every command’s output bytes; additional base comparisons covered skill-document rendering and coverage elements across 225 fixture models.
- Representative large-workload performance or callers outside this repository.
codex exit 0
