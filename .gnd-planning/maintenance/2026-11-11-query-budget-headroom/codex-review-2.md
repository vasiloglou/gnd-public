# Second diff review (Codex), retained verbatim

- Instrument: one reviewer in a different tool. One reviewer is one reviewer.
- Command: `codex exec --ephemeral --config model_reasoning_effort="xhigh" --sandbox read-only --color never --skip-git-repo-check -`, prompt on stdin, exit 0. Model: the tool's configured default.
- Reviewed bytes: `git diff 793618f1 bbe4d3c3`. The changes made in answer to R3 to R5 (the test file and this directory's README and spec) were not reviewed.
- The output below is unedited (it contains no home-directory path); the trailing "codex exit" line is the driver's.

## Reviewer output (verbatim)

DISPOSITION: revise

ID: R3  
SEVERITY: medium  
LOCATION: src/gnd/diff.py:289  
QUOTE: `return any(fact.get("derivation_rule") for fact in ModelIndex.for_model(model).iter_fact_types_shared())`  
PROBLEM: Refutes C3 for programmatically constructed Models. With a zero-field dataclass instance as `derivation_rule`, the Model constructor retains that instance, but `model_dump()` converts it to `{}`. I reproduced `_structured(model)` returning `True` at base and `False` at head. This input is outside the loaded-fixture corpus; I found no repository caller supplying it.  
FIX: Preserve live-value semantics for accepted constructed Models, or explicitly narrow the supported input contract. Add a baseline comparison containing serializer-altered values.

ID: R4  
SEVERITY: medium  
LOCATION: tests/test_query_budget_headroom.py:117  
QUOTE: `expected = {0, 1} if name == 'render_skill_document' else {1}`  
PROBLEM: Refutes C9. `LARGEST` contains no structured derivation, so this test never executes the converted skill-document read. An injected implementation that indexes once per fact in that branch still passes. The test also counts `iter_fact_types_shared()`, not index construction: I injected 19 additional `ModelIndex.for_model()` calls into `_build_projection`, and it still passed. Only five readers are exercised.  
FIX: Count the indexing operation, exercise structured and nonstructured branches, and cover all ten sites with appropriate per-call or per-distinct-model expectations. Include negative controls that demonstrate repeated indexing fails.

ID: R5  
SEVERITY: low  
LOCATION: .gnd-planning/maintenance/2026-11-11-query-budget-headroom/README.md:43  
QUOTE: `On the final working tree over 793618f1, uncommitted when run:`  
PROBLEM: Refutes C10. The recorded G1 result is `368 passed`, while the exact command currently collects 369 tests. The added frequency test postdates that evidence. README line 37 also says a frequency control “were not added,” although one now exists.  
FIX: Bind historical results to their tested commit, update the current test description, and record checks covering the final bytes.

Could not check full G1/G2, write-dependent workflows, external callers, or representative large-model performance. The read-only focused selection passed 48 tests.

I reproduced all 1,350 retained output digests at both base and head. That comparison covers six functions across 225 loaded models, including seven projection errors. It covers no empty-fact-type model, constructed-model inputs, or outputs from `_run_transition_raw`, `read_session_contract`, `evaluate_judgments`, and `build_measurement_report`. Its sorted JSON hashes also cannot establish dictionary insertion order, mutation/escape safety, or indexing frequency.
codex exit 0
