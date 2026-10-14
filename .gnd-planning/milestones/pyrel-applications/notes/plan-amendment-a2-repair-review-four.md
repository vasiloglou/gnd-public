# Amendment A2 repair review four — plan and repository compatibility

Date: 2026-10-13
Instrument: owner-selected independent local reviewer (repair round, read-only)
Subject: `notes/plan-amendment-a2.md` r2, SHA-256 `827fbedf138aac2dc531b6d7071e20dc8e8c1de296c2b1711590052474a797fe`

**Verdict: pass with findings** (no blocking).

| # | First-round finding | Status |
|---|---|---|
| 1 (blocking) | PA6 harness pins tutorial shape | Resolved: every pin named (accept_pyrel_applications_install.py:67,179-180; test_pyrel_applications_install.py:35,44,61-62; phase-PA6-spec.md:3,77; plan §3) |
| 2–8 | non-blocking | Addressed, not made worse |

D1 seam: no conflict (layer map :437, RF1 pins :401,455 preserved, digest change recorded separately,
O3 relocation labeled, corpus untouched).

- N1 (medium). Chapter 3 converts `expense-project` to the currency model
  (03-evolution.md:164,177-185), so "chapter 4 continues in expense-project" breaks the base-model
  baseline, meal-cap exercise and figure checkpoints. Choose: start from currency state, or a
  base-model copy for chapter 4; record the choice.
- N2 (low-medium). Re-gated PA6 review budget unstated; PA6 used its initial Claude review.

No other conflicts with r1/A1, AGENTS.md, or 001/003 records.

Orchestrator reproduction 2026-10-13: N1 checked at 03-evolution.md:160-186.
