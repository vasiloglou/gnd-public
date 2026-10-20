Retained output edited only to replace the machine-specific repository root with <REPO>. One CLI reader, not a panel.

Four static concerns warrant reproduction before IE2 acceptance. None below was executed.

1. **Helper changes can leave stale exact results cached.** [extensions.py:1024](<REPO>/src/gnd/extensions.py:1024) fingerprints callable globals at that module, but imported functions retain dependencies in their defining module. Replacing `gnd.terms._too_wide` leaves the identities and code of `extensions.evaluate_term` and `compare_terms` unchanged.

   **Minimal repro:** warm `_exact_extension_calculator` using the existing exact-terms fixture; patch `gnd.terms._too_wide` to return `True`; compare fresh and transactional calculations. Fresh evaluation should report `term:exact-value-too-wide`, while reuse can retain the previous unavailable reason and binding. This challenges the approved helper-policy invalidation claim.

2. **Opaque dictionary subclasses bypass fallback and lose possible rows.** [extensions.py:1014](<REPO>/src/gnd/extensions.py:1014) excludes only `type(value) is dict`; the original evaluator recognizes opaque values using `isinstance(value, dict)`. A subclass therefore enters component evaluation. [extensions.py:1057](<REPO>/src/gnd/extensions.py:1057) discards `possible`, and the final reconstruction cannot restore it. IE1 declining to cache the unsupported value does not prevent this loss.

   **Minimal repro:** repeat the existing opaque fallback test with `class Opaque(dict): pass` and `Opaque({"$opaque": "unknown"})`. Compare `.possible` outside and inside a transaction, for both `exact` values.

3. **Warm exact hits can suppress an existing shape refusal.** The component hook precedes `_relation_facts`; cache hits skip that materialization entirely. Signatures cover dependencies, so a malformed unrelated relation can escape the original evaluator’s strict row-width check.

   **Minimal repro:** warm the exact-terms fixture, then replace the unused `ticket_status` relation with a three-cell row while retaining its two roles. Fresh calculation should raise `ValueError` from strict `zip`; warm component reuse can return successfully. This challenges conservative refusal parity at the requested calculator boundary.

4. **The differential oracle cannot establish complete typed-envelope parity.** [test_incremental_extensions.py:12](<REPO>/tests/test_incremental_extensions.py:12) delegates to a projection that omits relation `fact_type`, roles and codec version. Direct Python equality also conflates numeric values such as `True` and `1`.

   **Minimal negative controls:** alter only an output relation’s roles or codec, then separately replace a Boolean cell with an integer. The current envelope comparison can remain equal. Include the omitted metadata and use a discriminating scalar comparison. This is an IE2 verification concern; it does not require expanding into IE3.

Static inspection supported these claims:

- Dirty recursive SCCs reset their heads and use the original fixed-point implementation.
- Direct signatures retain ordered rows, roles, lineage, codec and upstream unavailability; ordinary counters sum, and current exact maximum fields combine by maximum.
- Per-unit branches are captured and replayed into enclosing captures.
- IE1 cloning, generation rollback and accounting remain in use; IE2 supplies dependency-input plus output row counts.
- The direct work controls run without a preparation scope, so existing per-call preparation does not explain their no-op savings.
- The dynamic successor chains after IE1 with the matching predecessor digest; no raw-query waiver was added. RF3 extension body pins remain historical.

This was one read-only reviewer, not a panel. I ran no tests, agents, providers or network operations and changed no files. The supplied focused-pass results and **179 versus 4878** smoke counts remain reported evidence; payload-only smoke does not establish complete trace acceptance. Sessions, constraints and receipt repair remain IE3’s scope.