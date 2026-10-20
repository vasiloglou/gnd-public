Retention annotation: final reviewer response verbatim except repository root replaced with <REPO>. Original final response SHA256 119eaebc9c4b9ac390741211785d22211f85b063b02dcf2a00059494787fcda2. Full transient CLI transcript retained outside Git /private/tmp/ie6-cli-review.txt. Read-only Astra xhigh, one reviewer is one reviewer; static only.

Three findings survived this **initial, single-reviewer static review**.

1. **Blocking — prepared policies lose live hashability validation.** At [incremental_state.py:438](<REPO>/src/gnd/incremental_state.py:438), prepared keys bypass hashing after preparation, but borrowed classes can change hashability.

   Exact reproducer: the newly added [test_prepared_policy_rechecks_live_hashability](<REPO>/tests/test_incremental_performance.py:195). Prepare `(PolicyClass,)`, cache one result, set its metaclass’s `__hash__ = None`, and reuse the same unit. The reviewed implementation returns cached `1` instead of fresh `2`, with no bypass. At `e897967`, hashing the signature rejects this now-unsupported policy and calculates fresh.

   Preserve per-lookup validation for hash-sensitive class handles, while retaining one-time validation for handles whose hashability cannot change.

2. **Hardening — the “exact builtin” fast path uses equality rather than identity.** [incremental_state.py:100](<REPO>/src/gnd/incremental_state.py:100) permits a custom metaclass to suppress a dataclass’s dictionary charge.

   Exact reproducer, provided but **not executed**:

   ```python
   import sys
   from dataclasses import dataclass
   from gnd.incremental_state import _measure

   class Meta(type):
       __hash__ = type.__hash__

       def __eq__(cls, other):
           return cls is other or other is type(None)

   @dataclass
   class Record(metaclass=Meta):
       values: list

   Record.__module__ = "gnd.test"
   value = Record([])
   minimum = sum(sys.getsizeof(x)
                 for x in (value, value.__dict__, value.values))
   assert _measure(value, minimum - 1) is None
   ```

   Static consequence: that assertion fails because tuple membership invokes metaclass equality, skipping `value.__dict__`. The previous implementation charges it. Use identity comparisons for this fast path and add this negative control. Full retained-size comparisons using the same `_measure` implementation cannot independently detect this omission.

3. **Completeness — traversal assertions permit repeated descendant walks.** The [prepared-policy counter](<REPO>/tests/test_incremental_performance.py:20) counts only the normalized root; the [raw-policy counter](<REPO>/tests/test_incremental_performance.py:176) selects tuples of length 160.

   Exact regression mutation: insert this after resolving `policy_key` on every lookup:

   ```python
   for child in policy_key:
       _measure(child, self._max_bytes)
   ```

   Both traversal-count assertions remain unchanged despite 160 extra subtree walks per lookup. They observe the real `_children` traversal, but do not bound total policy work. Count descendant visits too, including prepared warm hits and changed-snapshot misses.

**Checked claims:** No additional counterexample survived for conservative subtree-summary accounting itself: storage, node counts and relative depth are charged; sharing with outer content can overcount. Full-source `_measure` controls and actual private-clone measurement remain. `_Footprint` stays outside retained entries. Structural signature equality remains collision-safe; current calculator/snapshot hashing, authority checks, function-code guards and mutable-configuration checks remain. Clone behavior, both-generation accounting and atomic publication are unchanged. Fresh evaluator calls remain outside setup catches, without a new retry path.

**Static limits:** No tests, benchmarks, providers, credentials or edits. Reproducer outcomes above are source-derived. Files changed during inspection; this review ends at runtime SHA-256 `15e545f80a3421229b58fdfab80b3c6b7bdba4335f0c65d48dc1ca29e3ecf10d` and test SHA-256 `7aa0a79d7e4170cd8b2f4ff78f21f2a6703f59ab0a71ca246066a53b1b7c3b1a`. Approval010 and the effective spec were checked; 008/009 execution results remain historical. No elapsed improvement or current-suite acceptance is established.
