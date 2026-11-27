# Compact growth context for issue 295

## 0. Design rules
GND supplies a complete read-only inventory of the resolved model. The coding agent chooses how to investigate it, including alternative paths, retries and deferral. Existing additive evolution gates govern writes.

## 1. Requirements and evidence
Issue 295 asks for compact prompt context, stable identifiers and explicit guidance when a host supplies a subset. Earlier passage-selection experiments missed reusable mentions even with graph neighbors. They motivate retry and deferral. They establish no product-level accuracy or cost improvement. The earlier five-phase proposal is archived in historical-fable-draft.md. The owner selected this two-phase scope.

## 2. Product contract
Version 1 is canonical UTF-8 JSON with a trailing newline. Expose object IDs and reference modes, fact IDs, readings and ordered named role players, direct subtype links and registered constraint signatures. Preserve meaningful order and use deterministic ordering elsewhere. Exclude author evidence, samples, notes and rationale. Use a view digest for replay. Check original root bytes and verified transitive include pins before applying evolution because evidence-only changes can preserve the view digest.

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
