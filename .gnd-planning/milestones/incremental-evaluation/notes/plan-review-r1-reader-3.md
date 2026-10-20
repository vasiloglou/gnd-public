# Reader 3 — protocol, authority and privacy

Reader 3 verdict: **approve** for this advisory planning review. No blocking or hardening finding survived. One completeness correction can be deferred without delaying owner disposition.

Reviewed plan SHA-256: `34b1004e9d7e5e60f3162dae423e78b3d42bf98678edcccc0ad358517f086de1`.

Supporting IE0 draft SHA-256: `d49a5bcc4f06b5f1b500bd231637d54dcedc2bd9778976ba5817edb6a9ba19da`.

Lens: planning protocol, scope and authority, carryover harvesting, privacy, approvals, compatibility ownership and verification selection. This was a fresh-context local reader’s advisory review, not phase diff review, execution approval or certification. I read AGENTS.md, start-milestone and relevant process-phase references, CONTRIBUTING.md, PROJECT.md, the question register, the complete plan and IE0 draft, and the preceding milestone close and applicable boundaries. I made no edits, ran no tests or benchmarks, invoked no providers and read no credentials.

## R3-F1 — Stale review-instrument status in implementability sweep

- Class: completeness.
- Severity: low.
- Location: `.gnd-planning/milestones/incremental-evaluation/notes/incremental-evaluation-plan.md:387`.
- Evidence: this row says “D6 and D5 remain pending.” The canonical decision section explicitly excepts D6 from the open decisions at lines 391–392 and records the owner’s selection at line 401. Section 8 also recognizes that selection at lines 324–329.
- Observable consequence: a reader using the implementability sweep receives a contradictory readiness summary and may unnecessarily request the already-selected review instrument again. This does not authorize execution or compromise a runtime result.
- Minimal remedy: change the sweep row to identify D5 as pending and cite D6’s recorded selection. Keep artifact approval pending. No additional review round is warranted for this correction.

The approval and authority boundaries are sound. The plan distinguishes proposed milestone rules from independently binding repository obligations at lines 67–68; preserves `auto=false`; and places review, plan approval, the concrete phase gate and approved-spec commit before implementation at lines 324–336. The selected four-reader instrument does not imply plan/spec approval. Separate PR, merge, publication and certification authority remains explicit at lines 346–349. The IE0 draft likewise remains blocked on decisions and approval at lines 252–265. These pending rulings are appropriate draft state, not defects or implied consent.

Carryover coverage is adequate for planning. The obligation table assigns the inherited compatibility and protocol corrections, including current-content mutation checks, mandatory transition checks, mutable receipts, affected policy/pin selection, spec-before-code and privacy. The residual table at plan lines 264–286 explicitly dispositions all 18 prior close rows rather than silently closing them. Later exact signatures, accounting and verification commands remain explicitly unresolved until their owning specs.

Privacy and verification selection are appropriately bounded. IE0 excludes private imports, limits work to existing public fixtures and synthetic controls, and requires an amended spec before admitting another import path. The plan preserves downstream acceptance as conditional and avoids extrapolating local measurements to the 547-program census. Focused gates retain default lane exclusions, historical results are not inherited onto changed bytes, runtime policy/layer consumers have named ownership, and broad/provider/native/certification lanes require separate selection.

The IE0 prose instrument remains an owner decision with an explicit rationale and mandatory negative controls. Its presence here does not constitute acceptance of that exception.

No additional protocol correction is required before the owner considers the plan and its open decisions.
