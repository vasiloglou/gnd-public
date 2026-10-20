# Plan review — round 1 disposition

2026-10-19. Owner-selected instrument: **four local reviewer agents**, as in
the preceding milestone. The owner selected the instrument in reply to the
review question; that selection is recorded as plan D6. It is not approval of
plan/spec bytes or authorization to implement.

## Subjects and limits

Reviewed plan r1 SHA-256:
`34b1004e9d7e5e60f3162dae423e78b3d42bf98678edcccc0ad358517f086de1`.
Supporting IE0 spec SHA-256:
`d49a5bcc4f06b5f1b500bd231637d54dcedc2bd9778976ba5817edb6a9ba19da`.
Inspection HEAD: `058874965c54c19c4a4c34855cc9ca1b789394bf`.

Retained exact snapshots: [plan](../evidence/plan-review-r1/incremental-evaluation-plan.md)
and [IE0 spec](../evidence/plan-review-r1/phase-IE0-spec.md).
Their relative links and line citations retain the original `notes/` context;
they are evidence copies, not competing canonical plans.
[Manifest](../evidence/plan-review-r1/manifest.json) records snapshot, current
amended artifact and reader-note digests.

Each reviewer started with fresh context, received the named subject/digests
and a different lens, and inspected the complete plan/spec and relevant sources.
Readers 1–3 ran concurrently; reader 4 followed when a slot became free.
All four were local model-agent readers, not humans or a provider panel. This
is the explicitly selected advisory plan instrument, not the different-harness
adversarial phase-diff review required during implementation. No tests,
benchmarks, credentials, paid tools or native lanes were used. These are static
opinions on specified bytes, not proof of runtime performance or correctness.

## Opinions

| Reader | Lens | Verdict | Blocking | Hardening | Completeness |
|---|---|---|---|---|---|
| [1](plan-review-r1-reader-1.md) | semantics, invalidation and CR-01 | approve | 0 | 0 | 0 |
| [2](plan-review-r1-reader-2.md) | implementability and dependency homes | approve | 0 | 0 | 0 |
| [3](plan-review-r1-reader-3.md) | protocol, authority and privacy | approve | 0 | 0 | 1 |
| [4](plan-review-r1-reader-4.md) | measurement and reproducibility | approve-with-fixes | 0 | 1 | 0 |

Reader notes retain the returned substantive text; Markdown titles and section
formatting were added for local navigation. Reviewer citations refer to the
retained reviewed snapshots, not shifting line numbers in amended files.

## Findings and coordinator checks

| Finding | Class / severity | Reproduction from reviewed bytes | Disposition |
|---|---|---|---|
| R3-F1 | completeness / low | Plan line 387 calls D6 pending while lines 391–401 explicitly record owner selection. The coordinator independently read those lines. | Fixed in r2, tagged `(p1)`. Leaving contradictory authority status would invite an unnecessary second selection request at the imminent owner gate, so this completeness correction did not wait for close. Only the scheduling decision and artifact approvals remain pending. |
| R4-F1 | hardening / medium | IE0 spec declares three arms at lines 166–169, a two-arm AB/BA/AB schedule, accepts repeat 1..7 at lines 99–100, and tests the two-arm schedule at line 218. The coordinator checked that all four clauses coexist. This is a document contradiction; no runtime experiment is needed to establish it. | Fixed in the draft spec, tagged `(p1)`. Named A=full stateless, B=receipt-only, C=independent fresh full. Round i uses `(ABC, BCA, CAB)[i % 3]`, one replay per arm per round. Defined N=1..7 behavior, positional-imbalance reporting, isolated inputs, all-arm sample counts and instrumentation absence in T7. Renamed tool-only `measure_pair` to `measure_modes` to match its three-arm contract. |

The timing repair changes the planned instrument's reproducibility, not a
product API, runtime outcome, performance target or already-approved contract.
No benchmark has run and no measured ceiling was moved. Neighbour checks covered
the signature, CLI repeat meaning, schedule, budget wording and T7; no obsolete
two-arm schedule remains in the canonical spec.

## Convergence and current status

| Round | Seats | Per-seat counts | Self-inflicted / total | Blocking / total | Severity ceiling | Verdicts |
|---|---|---|---|---|---|---|
| 1, plan r1 with IE0 draft | 4 | 0 / 0 / 1 / 1 | n/a: first round | 0 / 2 | medium | 3 approve; 1 approve-with-fixes |

The declared round budget permits a bounded confirmation of reproduced blocking
findings. There are no blocking findings to confirm, so no second round runs.
No convergence trend is inferred from one round. Further review requires a
concrete reason and remains subject to the process-phase convergence reference.

**Repaired bytes carry no review opinion of their own.** Current plan r2 SHA-256:
`b7503db4af6ab7ab5916e0c0fa8a6f7bbcbe6aab5464e9fdd99422fe53e160b1`.
Current IE0 draft SHA-256:
`13b240404813e2bc5bb6389c9b92ee8a524b8ffbcc9e1708e01977b883fce963`.
The two repairs and review status are disclosed for the owner's disposition;
the three approval opinions do not silently transfer to these new digests.

Plan decisions other than review instrument D6 remain open. Plan approval,
IE0's concrete spec gate, its approved-spec commit and explicit execution
workflow selection remain pending. Implementation, PR merge, publication,
certification and milestone closure have not occurred. The selected four-reader
instrument also applies to the eventual close; no close review runs now.
