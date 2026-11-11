# OS6 — Prepare an upstream Ossie requires contribution

Plan r3 predicate 9 and OS6-C1 to C3 govern this phase. The
[OS4 record](../021-phase-OS4.md) establishes that the pinned converter
emits no PyRel requirements and records the full source and isolation
results. The upstream contribution starts at
`83ddc294c8840f5f497a2bdbec2348a128fc2254` and uses RelationalAI
1.39.0. It remains a separate local topic branch.

| Obligation | Evidence |
|---|---|
| OS6-C1 | Convert parsed requires through the upstream formula visitor and emit scoped PyRel requirements. Preserve existing derivations. Run the upstream RelationalAI tests and update only affected snapshots, beginning with Flights. |
| OS6-C2 | Replay the OS4 comparison against the local commit and isolate each emitted GND family. Record per-case calls, the supported scope, and any unsupported formula shape. Preserve the original OS4 report and pins. |
| OS6-C3 | Prepare the exact upstream PR title and body. Record the owner's publication decision and either the opened PR's state or the retained local branch. |

Reuse the existing parser, resolved formula AST, variable references and
PyRel expressions. Scope concept requirements to instances and
relationship requirements to matching tuples. Ontology requirements use
an empty outer scope. Emit a requirement only after its body has lowered
successfully. Leave unsupported forms visible as warnings with the
formula scope and a reproducible reason. Measure which families the SDK
actually emits. The contribution should preserve the converter's
independent treatment of derivations and the legacy path for raw
formulas outside the parser's validated subset.

The code accepts typed parser objects and does not introduce a new
reader. Reuse the existing declaration and formula traversals. Check
scope and unsupported shape before building the requirement. The native
test config and socket guard own the offline boundary. No PyRel engine
or warehouse run is selected. The OS4 comparison uses a separate
checkout and records that commit, with the original pin unchanged.

The public upstream diff needs an independent review. The upstream
suite and OS4 replay are opt-in. Publication requires a separate
decision over the local branch and exact PR text.
