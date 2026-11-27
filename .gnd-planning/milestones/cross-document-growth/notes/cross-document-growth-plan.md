# Cross-document model growth

Draft r1, 2026-11-27 · awaiting plan review and owner decisions · auto=false. The owner requested planning. No panel was selected or run. Completion requires the phase results below and a separate milestone-close ruling.

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

Choose append-only in-model storage or the external population requested in #338. The external option changes the atomic publication and summary contract and requires revising CG1. These are proposals for the owner. Resolve the first-phase decision before implementation; later choices may remain open through earlier phases.
