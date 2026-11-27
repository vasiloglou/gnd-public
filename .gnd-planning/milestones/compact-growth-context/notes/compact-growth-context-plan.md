# Compact growth context for issue 295

## 0. Design rules
GND supplies a complete read-only inventory of the resolved model. The coding agent chooses how to investigate it, including alternative paths, retries and deferral. Existing additive evolution gates govern writes.

## 1. Requirements and evidence
Issue 295 asks for compact prompt context, stable identifiers and explicit guidance when a host supplies a subset. Earlier passage-selection experiments missed reusable mentions even with graph neighbors. They motivate retry and deferral. They establish no product-level accuracy or cost improvement. The earlier five-phase proposal is archived in historical-fable-draft.md. The owner selected this two-phase scope.

## 2. Product contract
Version 1 is canonical UTF-8 JSON with a trailing newline. Expose object IDs and reference modes, fact IDs, readings and ordered named role players, direct subtype links and registered constraint signatures. Preserve meaningful order and use deterministic ordering elsewhere. Exclude author evidence, samples, notes and rationale. Use a view digest for replay. Check original root bytes and verified pins for every directly declared include before applying evolution because evidence-only changes can preserve the view digest.

## 3. Dependencies and ownership
Use the composed loader, ModelIndex, family semantics and existing verbalization module. Both public surfaces call the same renderer. The packaged unattended-growth guide owns the host protocol. The host owns passage selection, search strategy and prompt budgeting.

## 4. Phases
GC1 delivers the projection and its internal tests. Verify complete identifiers on fixtures, role order, guarded and anchored signatures, deterministic bytes, included elements, empty models, unresolved includes and evidence-only edits. Compare compact versus ordinary review bytes on the same populated schema fixture.

GC2 adds the opt-in API keyword and CLI flag, packaged guidance and runnable include-backed example. Verify unchanged default output, CLI/API byte parity from an installed wheel, direct reuse, a first miss followed by successful lookup of an included fact via its role players, and ambiguous deferral. Check the role-specific occurrence before reusing a fact.

## 5. Documentation and compatibility
Document the flag and keyword on existing CLI and Python reference pages. The host records actual prompt scope, full or partial status, exact view digest, queries, inspected IDs, chosen action and source occurrence. A subset miss requires broader investigation or deferral before asserting novelty. The agent may choose a different search route each round.

## 6. Risks and controls
Loader checks protect composed ID identity. Field allowlists and evidence sentinels check disclosure. Ordered role-player signatures preserve direction. Existing evolution preview and apply perform stale-state checks. Measure actual UTF-8 bytes and confine comparisons to the measured fixture.

## 7. Scope
Search indexes, ranking algorithms, hosted inference, new databases, empirical recall claims and release publication are outside these two phases.

## 8. Execution and review
The implementation predates formal review. The owner delegated this milestone in auto mode and selected a full plan and close panel and independent Claude phase diff reviews. Record current decisions and exact artifacts. Resolve blocking findings before advancing.

## 9. Verification and closure
Phase records must link implementation, independent opinions and regression results. At close run repository-prescribed checks, component and layer checks, wheel installation, CLI/API parity, and the packaged host example. Record measured sizes and any limitations. Submit changes through a topic PR.

## 10. Decisions
The owner chose agent-directed search and authorized implementation. The coordinator may accept the plan, specs and milestone after the respective gates. Merge and release require separate owner decisions.

## Acceptance details following the first panel

GC1 returns the exact object, fact and authored constraint IDs supplied by the loader, including the seed's IDs, with no generated aliases. For each registered family check the signature against the family's expected operands and host, including their order. Assert equality of the fixture's authored IDs before and after reordering and an evidence-only edit. Check nested evidence sentinel strings are absent. Family registration growth must cause the coverage test to fail until a signature case exists. Unresolved includes refuse before output. Nested includes are rejected by the existing loader.

The top-level format field is exactly gnd-growth-view-v1. Serialize with sorted JSON keys, separators comma and colon without padding, unescaped Unicode, and a single final LF. SHA-256 covers all resulting UTF-8 bytes. Sort object and fact records by ID, subtype pairs by endpoints, constraints by canonical signature. Retain authored role order and asymmetric operand sides, including when two named roles share a player. A compact rendering must be strictly smaller in UTF-8 bytes than both the original full_vocabulary.orm.yaml fixture and the ordinary review rendering of that same model. Report all three counts. No cross-corpus threshold is claimed.

GC2 exposes gnd verbalize model MODEL --for-growth and gnd.api.verbalize_model(MODEL, for_growth=True). Verify the default against repository verbalization snapshots and the independent CLI grammar. On identical source bytes authenticate included IDs and compare a direct lookup against the resolved fact definition. Check reversed role bindings are ineligible for reuse. Verify a stale include fails and raw root identity changes after an evidence-only edit even when the view digest stays equal.

The renderer always emits the complete view. A host presenting a subset shows the agent a partial flag, the full view digest and the exact selected rows at each search. The runnable example retains these along with the source span and decision in a host JSON record. Check that the first search yields zero rows, the next finds the known included fact, and ambiguous evidence yields defer with no added fact. Any number of partial misses alone is insufficient to propose novelty. Before proposing new schema inspect the complete inventory for that shape and check meaning and direction against the source, or defer. A host can change search route freely. A digest of the view cannot authorize mutation. Bind expected_model_sha256 to the root bytes from which the view was loaded and reauthenticate pins through the existing evolution workflow.

At close reconcile each of these criteria with its actual test or installed example. The historical draft lives beside this plan. A schema registry, a prescribed search algorithm and a second model mutation API would exceed the selected scope.

Review budget: at most two plan rounds. After the second, disposition concrete blockers and verify repairs through tests. Stop prose iteration when findings concern presentation or completeness, or the same seat repeats issues without new failing behavior. Unresolved issues that change product scope go to the owner.
