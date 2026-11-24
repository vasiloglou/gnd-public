---
milestone: literature-reading-reference
station: ruling
scope: ruling-D3
date: 2026-11-23
skill: "process-milestone (auto=true); an owner ruling, not a delegated one"
gates:
  - command: "ruling: owner, D3 (LR3 producer and budget)"
    exit: "n/a -- ruling"
---

# Ruling D3: LR3's producer and budget

Date: 2026-11-23. Ruled by the owner in this session, in reply to "Which
producer and budget should LR3's one recorded run use (D3)?":

> sonnet 50$

| Field | Ruling |
|---|---|
| Producer | Claude Sonnet, the current model in that family at run time (`claude-sonnet-5-5` on 2026-11-23); LR3's spec names the exact model id it calls |
| Budget | USD 50, a ceiling for the one recorded live run, all calls included |
| Scope | the single live run of plan §2 LR3, recorded once and replayed after (R0.5). Gates replay; they call no model |

This completes the plan gate's open row: [001-plan-gate.md](001-plan-gate.md)
left D3 to the owner. The ruling does not supply a credential. The run uses
a provider key from the owner's trusted environment by name, never from a
repository `.env`, and stops before the first call if the key is absent.

LR3 still waits for literature-host-interfaces LH1 and LH2 (PR 241) on
`main`. On 2026-11-23 PR 241 is open.
