---
milestone: incremental-evaluation
station: plan-gate
skill: start-milestone
scope: plan and proposed milestone decisions
date: 2026-10-19
---

# Owner approval of plan r2

The owner answered **“approved”** after the plan explanation and the four-reader
review outcome. The preceding explanation explicitly identified approval of
the plan's scope and direction as the next decision and retained IE0's separate
concrete spec gate. This records owner approval with `auto=false`, not delegated
approval or authorization to execute the whole milestone.

Approved subject: `notes/incremental-evaluation-plan.md`, r2, before the
approval-status annotation, SHA-256
`b7503db4af6ab7ab5916e0c0fa8a6f7bbcbe6aab5464e9fdd99422fe53e160b1`.
The [exact approved snapshot](evidence/plan-approval/incremental-evaluation-plan.md)
is retained; its relative links retain the original `notes/` context.

## Milestone decisions

Plan §10's proposed direction is accepted within its stated bounds:

| Decision | Owner ruling, 2026-10-19 |
|---|---|
| D1 | Opt-in, in-process evaluation session; existing stateless defaults remain. Exact public signatures await IE3's spec. |
| D2 | Cross-call selective evaluation is permitted under IE-R1..R4, preserving all admission and intermediate/post check obligations. |
| D3 | Start with the old public workload and synthetic controls; new-workload acceptance remains conditional on its supply and admission. |
| D4 | Include the two carried observation/feedback requests in IE4. Detailed host API, wire/version and ordering decisions remain its concrete spec work. |
| D5 | No delivery-date commitment now; scheduling follows IE0's estimate and risk evidence. |
| D6 | Four local reviewer agents for plan and close, as previously explicitly selected. |
| D7 | Use the plan's counted gates; freeze exact replay counts in IE0 before optimization. Timing remains evidence, not a gate. |
| D8 | Accept IE-R8's provisional bounds; exact accounting is finalized in the prescribed IE1/IE2 specs before reuse implementation. |
| D9 | Accept the proposed IE0 prose instrument and later corpus-first default for validation/wire work. Approval of the IE0 instrument does not approve the concrete IE0 spec or waive its gate. |

## Review basis and boundary

The [review disposition](notes/plan-review-r1-disposition.md) records four local
reader opinions on r1: three approve and one approve-with-fixes, no blocking
findings. The timing-schedule repair in the supporting spec and the plan status
correction were disclosed. The owner's approval applies to r2 as amended; it
does not claim new reviewer opinions on those bytes.

**Not approved here:** the concrete IE0 spec, phase execution, `auto=true`,
later exact API/schema/verification details, PR merge, publication,
certification or milestone closure. No implementation has started. Next:
explicitly select `process-phase IE0 incremental-evaluation` for the concrete
spec gate; commit its approved spec before implementation.
