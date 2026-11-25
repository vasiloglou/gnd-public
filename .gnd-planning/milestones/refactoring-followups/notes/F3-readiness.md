# F3 architecture and model-query baseline

At the F1/F2 boundary the ordinary runtime graph and module-only graph both contain zero strongly connected components of size greater than one. The package-initializer graph contains seven. The three core groups have **only implicit edges back to the parent**. The graph builder in tools/gnd_arch.py adds a parent edge for every dotted sibling import, including lazy imports. Rewriting these calls to import siblings is already represented by the measured graph.

| Group | Source of the return edge |
|---|---|
| gnd.assurance | gnd.assurance.core:16, gnd.assurance.core:421, gnd.assurance.core:556 |
| gnd.checker | gnd.checker._composed:12, gnd.checker._composed:14, gnd.checker._core:52, gnd.compiled_obligations:77 |
| gnd.model | gnd.model._includes:18, gnd.model._includes:19, gnd.model._operations:8, gnd.model._validation:46, gnd.model._validation:47, gnd.model._validation:48, gnd.model._validation:65, gnd.model._validation:78, gnd.model._validation:84, gnd.model._validation:116 |

The remaining groups are gnd.evolve, gnd.recovery, gnd.review and gnd.synth.oracle. The test_rf6_query_policy.effective_policy() inventory has 294 distinct rows and a ceiling of 365. Each row identifies a path, owner, expression, multiplicity and reason. An architectural move must preserve the existing patch lookup, layer assignments, init execution and import identities. Standalone exports cannot start importing GND. Keep raw/IR selectors separate from ModelIndex snapshot semantics, including missing-key behavior, ordering and detached versus shared objects.

These are phase-preparation measurements. No phase gate or migration is claimed.
