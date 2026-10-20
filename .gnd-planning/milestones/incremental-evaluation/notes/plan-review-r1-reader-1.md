# Reader 1 — semantics and invalidation

Reviewed plan SHA256: `34b1004e9d7e5e60f3162dae423e78b3d42bf98678edcccc0ad358517f086de1` — matches the requested bytes.

**Verdict: approve** within the semantics/invalidation review lens. No actionable findings survived inspection.

Scope: read-only review of AGENTS.md, the complete plan and IE0 draft spec, relevant runtime dependency/strata, extension refresh, lineage, checker/correspondence, preparation, ModelIndex, admission/reference and receipt paths, plus prior transition-performance and repairs boundaries. No files changed; no tests, benchmarks, providers or credentials used.

Reasons supporting approval:

- CR-01 and admission remain prerequisites, including model operations, population mutation/marker, options, references and caller-held stale scopes. Plan lines 57–59, 123–136, 203–213 and 277 address the actual distinction between content verification and scoped identity reuse in `src/gnd/model_index.py:104`.
- Dirty propagation includes negative/aggregate dependencies, transitive dependents and complete recursive SCCs. Recomputing dirty SCCs from current base state avoids preserving unsupported recursive rows after deletion. Plan lines 129–136 and 217–225 agree with the inspected dependency and strata machinery in `src/gnd/model/_validation.py:3294` and `:3585`.
- The plan explicitly prevents directly treating existing selective-refresh mappings as a complete checker envelope. This addresses the inspected loss of prior lineage in `src/gnd/extensions.py:2026`; plan lines 138–143 and 219–223 require lineage, unavailable/possible state and branch parity before integration.
- Selective constraints preserve current witnesses, refusal precedence, root/intermediate/computed-post/declared-post checks and compiled obligations. Plan lines 58 and 229–237 make these acceptance criteria rather than discretionary optimizations.
- Receipt safety is an explicit integration prerequisite. The mutable report held by `src/gnd/api.py:204` is already a named inherited issue; plan lines 232–234 require reproduction and repair before integrating reuse, while preserving existing eligibility.
- IE0’s oracle requires every semantic surface and rejects missing fields and deliberately corrupted outputs. Its spec lines 85–90, 109–111 and 217 prevent an unavailable lineage/possibility comparison from silently becoming parity.

Limits: this opinion approves the proposed correctness framework, not an implementation, completed dependency census or proven performance result. Later eligibility classifications, exact snapshot identities, resource accounting and per-family reuse require their prescribed specs and evidence. Existing open owner decisions remain gates.

The stale D6 “pending” statement at plan line 387 is a document consistency correction identified by the coordinating reviewer; it does not change this semantic verdict.
