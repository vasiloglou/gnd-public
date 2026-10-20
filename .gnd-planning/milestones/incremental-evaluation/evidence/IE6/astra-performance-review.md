# Astra incremental evaluation performance review

Subject: d0ffd9a720bb92b56f1f5c1636b06b477b27070f, branch codex/incremental-evaluation.
Reviewer: independent gpt-6-astra agent, high effort. One reviewer is one reviewer.
This is the coordinating agent's summary of Astra's findings and bounded experiments, not a verbatim transcript. Production files and PR were unchanged.

## Ranked findings

1. **Repeated full-policy accounting dominates cache misses.** In src/gnd/incremental_state.py:431 and :445, every miss measures key, complete signature, value and branches twice. Signatures contain large normalized policy trees that preparation already measures at :374. Astra's reporter profile attributed 2.349s cumulative to _measure, including 1.886s from reuse and .376s from prepare_policy. The course profile attributed 2.012s to measurement from reuse. First try exact-builtin fast paths. Next consider bounded, precomputed size/node metadata for immutable policy descriptions, conservatively charging each retained entry. Continue measuring the actual private clone: reconstruction can change its size. Preserve node/depth/cycle/finite checks, proxy backing-dictionary accounting, changed-binding retention, row/byte limits and atomic rollback.

2. **Reduce repeated fingerprint allocation and complete signature hashing on hits.** src/gnd/incremental_state.py:391-408 measures a snapshot, separately freezes it, freezes mutable policy, and hashes the complete signature. Actual dictionary lookup uses namespace and unit key; signatures are compared for equality. Astra's reporter profile attributed 1.518s to fingerprinting from reuse and .333s to 4,485 explicit signature hashes. Experiment with prevalidated prepared-policy hashability, while preserving validation of current calculation identity and snapshot shape. A combined measurement/freeze pass could save traversal but must preserve distinct semantics: retained bytes deduplicate shared objects; ordered fingerprint occurrences do not. Preserve duplicate rows, ordering, types, lineage, codec and refusal behavior. Keep live mutable-configuration and code checks at every allowed reuse boundary; once-per-transaction checks are insufficient.

3. **Prepare guarded constraint policy per bounded evaluation context.** src/gnd/correspondence.py:1006-1047 rebuilds callable namespaces, imported homes, registry and hook configuration per eligible constraint and sends raw policy through normalization again. Course _constraint_reuse consumes 2.335s over 75 calls, with 45 eligible calls. Reporter guarded routes all remain fresh, and its 684 _constraint_reuse calls cost only .114s including evaluation. This optimization targets course/localized rather than directly fixing reporter. Preserve live registry/function/default/closure/namespace changes, conservative external-hook fallback and single execution of evaluator failures outside setup catches.

4. **Reuse bounded extension dependency planning and policy setup.** src/gnd/extensions.py:1038-1076 repeatedly obtains fact declarations, strata, classifications, dependencies and policy; :1083 reconstructs component dependency lists. Astra's reporter profile attributes 1.173s to 69 context builds, including .639s policy preparation. Experiment with a bounded transaction-local plan bound to the freshly established ModelIndex and relevant current helper policy. Preserve independent model content validation, helper/default/ModelIndex patch invalidation and _relation_facts validation of unrelated malformed rows even on warm hits.

Do not prioritize clone weakening: clone cost was only .211s in Astra's reporter profile. Candidate dictionary reconstruction/accounting was not a material hotspot. Do not expand cache eligibility without new semantic justification.

Profiler cumulative durations overlap and are diagnostic only; they are not additive costs or predicted wall-time savings.

## Bounded experiment

The coordinating agent tested a process-only variant of _measure that skips dataclasses.is_dataclass for exact builtin None/str/int/bool/float/dict/tuple/list/frozenset/MappingProxyType values. No repository source was edited.

Course C, warmed, three alternating original/trial pairs, no profiler or tracemalloc:

- Original seconds: 1.7602225421, 1.6036847502, 1.6104495411; median 1.6104495411.
- Trial seconds: 1.6467087502, 1.5575687499, 1.5053309998; median 1.5575687499.
- Median decreased about 3.28%; shared host, small sample. This does not establish a reliable improvement across workloads or superiority to full evaluation.
- Process-patched focused tests: test_incremental_state.py, test_incremental_state_review.py, test_incremental_prepared_policy.py: **37 passed in 1.09s**.

The larger recommendations remain unimplemented and their wall-time gains are unproven.

## Diagnostic profiles

- /private/tmp/gnd-astra-course-B.prof
- /private/tmp/gnd-astra-course-C.prof
- /private/tmp/gnd-astra-reporter-B.prof
- /private/tmp/gnd-astra-reporter-C.prof
- /private/tmp/gnd-astra-review-reporter-C.prof (Astra's independent run)

Each used credential-free cProfile around measure_incremental_evaluation.replay_full with receipts=True and incremental=False/True as appropriate. Astra's independent reporter C run recorded 56,742,063 total calls, 11.339s profiler total and 4,485 reuse calls consuming 4.533s cumulative. Timing runs were separate from all profiler runs.

## Validation for a follow-up implementation

Use existing mutation, private-clone accounting, bounds, fallback and cancellation controls. Compare B/full receipts versus C/session receipts with the existing complete payload, exit, branch and ordered calculation oracle in tools/measure_evaluation_sessions.py. Then measure course, reporter and localized through the existing balanced uninstrumented schedule. Add diagnostic work counters for measurement nodes, policy builds and guard checks; derivation counts alone do not capture the present bottleneck.

No production edits, broad suites, credentials, network operations, new downstream workload, merge or publication occurred in this review pass.
