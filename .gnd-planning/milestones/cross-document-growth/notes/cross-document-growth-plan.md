# Cross-document model growth

Revision 2, 2026-11-28. The owner delegated milestone rulings and selected the light panel. All six reviewers assessed revision 1. The changes below carry the coordinator’s disposition of those findings. Completion requires the phase results below and a separate milestone-close ruling.

## 0. Binding design rules

Document and check every new sample span against the cited document before CAS. Count duplicate evidence separately from distinct rows. Use existing loaders, ModelIndex for model queries and the defining component for policy. State validation order at each public boundary and test both sides of every refusal.

## 1. Scope, sources and authority

Issue requirements come from [#338](https://github.com/vasiloglou/gnd-public/issues/338), [#339](https://github.com/vasiloglou/gnd-public/issues/339), including their proposed changes and reproduction examples. Implementation baseline 83cd4170. The [predecessor close](../../compact-growth-context/004-milestone-close.md) records the inherited capability and the limits of its evidence. These are framework features; a domain experiment census cannot establish API or evaluator behavior.

## 2. Proposed behavior

Append located rows to a locally owned fact under additive preview and apply. Keep prior rows and spans intact and validate the extended population.

Index singleton types, role-player and reading shapes, name similarity, units and counted nouns. Emit stable candidate IDs, evidence locations and scores. Reordering declarations must preserve groups.

Review one group at a time against source spans. Preview row moves and role rewrites together, record merge, demotion, subtype or leave, recompute candidates after apply and stop at the configured threshold.

## 3. Dependencies and artifact homes

CG1 provides the canonical evidence representation for CG2 and CG3. Candidate discovery may read a model before CG1 ships, but the closure replay must exercise two documents and an accepted merge. Start with [src/gnd/evolve/policy.py](../../../../src/gnd/evolve/policy.py). The component index identifies `evolve.policy`, `evolve.population_check`, `evolve.service`, `evolve.round_summary`. Its November 27 review flagged 105 descriptions older than their source; resolve contract details against code and tests.

## 4. Obligations and completion criteria

| Phase | Issue and deliverable | Observable exit criterion |
|---|---|---|
| CG1 | [#338](https://github.com/vasiloglou/gnd-public/issues/338) Located additions | Append located rows to a locally owned fact under additive preview and apply. Keep prior rows and spans intact and validate the extended population. |
| CG2 | [#339](https://github.com/vasiloglou/gnd-public/issues/339) Candidate discovery | Index singleton types, role-player and reading shapes, name similarity, units and counted nouns. Emit stable candidate IDs, evidence locations and scores. Reordering declarations must preserve groups. |
| CG3 | [#339](https://github.com/vasiloglou/gnd-public/issues/339) Reviewed consolidation loop | Review one group at a time against source spans. Preview row moves and role rewrites together, record merge, demotion, subtype or leave, recompute candidates after apply and stop at the configured threshold. |

The [first draft spec](phase-CG1-spec.md) expands CG1. Later specs follow the preceding decisions. Carry the predecessor’s documented limits into each new public claim.

## 5. Documentation and compatibility

Growth policy currently directs later rows to open questions. Changing that public guidance belongs to CG1. CG3 owns the packaged consolidation skill and its installed example. Start from [docs/reference/evolve-policy.md](../../../../docs/reference/evolve-policy.md). Run existing examples and compare the observable result for a caller using the previous interface.

## 6. Risks and controls

Document and check every new sample span against the cited document before CAS. Count duplicate evidence separately from distinct rows. Vary identifiers, declaration order and input cardinality in the acceptance fixtures. Record work counters and the first refusal where limits apply.

## 7. Outside this milestone

Paid grower effectiveness and cross-model alignment. Release scheduling belongs to the owner.

## 8. Execution and review

Each phase needs its own spec and owner ruling, implementation, focused tests, independent diff review, refactoring review and numbered record. Plan and close require the project’s four-reviewer bar, recorded against the reviewed bytes. The owner selects the panel. Merge and release have separate authority.

## 9. Verification and baseline

Observed at intake: Existing guidance sends later rows to open questions. The compact inventory identifies vocabulary but omits sample rows. The corpus counts in #338 and #339 come from the reporter.

Run the first spec’s focused selection and retain its verbatim pytest summary. For each later phase, use the issue reproduction and the criterion in §4 as an acceptance pair, pin the old behavior on unextended inputs and record the public entry point and result. Milestone closure requires a replay across phases, a disposition for each issue and an inventory of unverified claims. Native backend claims require native execution.

CG2: shuffle model declaration order and compare candidate group IDs and cited spans. Include two similarly named types with incompatible role players; the suggestion must carry evidence for review. CG3: accept one group, decline another, restart from the decision log and verify that the declined group is not offered again unless its evidence changes. After a rename or deletion validate all role references and locate every transferred row’s original source.

## 10. Open decisions

The delegated decision adopts append-only samples for root-owned facts. Included definitions stay owned by their source. A host may record evidence for an included fact as an open question. The earlier alternative of a separate growth population remains in revision 1 at ecb01fa9.

## Amendment after plan review

1. CG1 uses an explicit document input. A caller supplies source bytes for appended spans at preview and apply. Validate authored root ownership, preserve every old row and span, check declared document identity and excerpt against supplied bytes, then validate the candidate samples with the ordinary population reader and checker. An affected constraint must return pass. Any missing coverage, warning, violation, or evaluator inability refuses the operation. Retain ordinary CAS validation and the original model on failure. Exercise root and included targets and a deontic uniqueness warning. Provide the public guidance and the fallback for sources lacking sufficient evidence.
2. Treat an indexed sample as an observation. An additional document may support an identical tuple; preserve the located observation and evaluate the distinct typed facts. A repeated identical tuple and source occurrence adds no evidence and is refused as redundant. An existing preview applied again follows the existing transaction recovery contract. Test differing excerpts and differing documents separately.
3. CG2 owns deterministic candidate discovery. Define stable identity from the signal, root-owned member kind and sorted member IDs. Hash the sorted evidence (including source digests and locations) separately so a newly supported group can be reconsidered without changing its identity. Include one true candidate and one control for singleton entities, role-player signatures, reading shapes, similar names, units and counted nouns. Include cross-document and renamed fixtures. Discovery is advisory and never applies a candidate. Charge indexed items and examined candidate pairs, return incomplete on budget exhaustion, and test exact-budget and one-less boundaries.
4. CG3 reviews candidates with one of four decisions: leave, demote to row, merge or link subtype. Bind each decision to group and evidence hashes and the reviewed model digest. A leave suppresses only the same evidence. A mutation uses one digest-bound proposal for the entire group, including row moves and role rewrites. Check constraint conflicts and dangling references before applying. Persist proposal and decision identity before publishing, and complete the existing transaction on recovery. Demonstrate failed rewrites leave both rows and references intact and restart after publication completes the ledger once. Bound the loop by maximum decisions and discovery work. Terminate when no eligible unresolved group meets the selected minimum score, the budget expires, or a decision needs input. Record the reason explicitly.
5. Milestone closure replays two source documents, a duplicate observation, one accepted group, one declined group and an interrupted restart. Compare the final model digest, surviving references, located evidence, decision identities, counters and terminal reason between uninterrupted and resumed runs. Preserve origin spans during transfers and refuse conflicting constraints. Put the replay and exact results in the milestone close record.

The [first panel report](plan-review-r1.md) preserves every agreed and divergent finding. The runtime homes and baseline discrepancy are checked in [execution intake](execution-intake.md). The five amendment clauses supersede shorthand in the phase table. One plan round was budgeted before implementation; use focused code tests to settle runtime behavior.
