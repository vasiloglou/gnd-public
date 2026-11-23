# Pins and the review check

Plan r1, 2026-11-23: **approved by the owner** on 2026-11-23 with D1–D5 as
proposed ([plan gate](001-plan.md)); no review has read it. It covers the
work left undone by
[PR 235](https://github.com/vasiloglou/gnd-public/pull/235),
[PR 246](https://github.com/vasiloglou/gnd-public/pull/246) and
[PR 247](https://github.com/vasiloglou/gnd-public/pull/247). No issue was
filed for it.

| Phase | Deliverable | State |
|---|---|---|
| PF1 | the packaged-skill inventory defined once; the install, uninstall and verification-fix tests import it and join the guard block. Repairs `tests/test_verification_fixes.py`, red on `main` (5 failed) | done on `claude/pf1-inventory-pin`: [002-phase-PF1.md](002-phase-PF1.md); [spec r1](notes/phase-PF1-spec.md) owner-approved; pull request open, not merged |
| PF2 | a recorded calibration of the standing "code fitted to its examples" review check, over planted and control diffs | outline in the plan |

[Plan](notes/pins-and-review-check-plan.md).

Rulings (plan §10), all as proposed: D1 one baseline run on beast-3, D2
`codex` over about eight diffs, D3 one reviewer in a different tool for
plan, phase and close (panel waived for this milestone), D4 one pull request
per phase, D5 the distribution-lane pin stays as a named exception.

Next action: the owner rules on PF1's open questions (OQ1 keeps or drops the out-of-spec commit) and merges its pull request; then PF2's spec.
