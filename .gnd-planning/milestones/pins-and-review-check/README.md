# Pins and the review check

Plan r1 (owner-approved, [plan gate](001-plan.md)), amended at close (c1).
**Closed locally on 2026-11-23** by delegated ruling under the owner's
`process-milestone pins-and-review-check auto`
([close record](004-close.md)). Nothing is merged. It covers the work left
undone by [PR 235](https://github.com/vasiloglou/gnd-public/pull/235),
[PR 246](https://github.com/vasiloglou/gnd-public/pull/246) and
[PR 247](https://github.com/vasiloglou/gnd-public/pull/247).

| Phase | Deliverable | State |
|---|---|---|
| PF1 | the packaged-skill inventory defined once, guarded over every binding; the install, uninstall and verification-fix tests import it and join the guard block; `tests/test_verification_fixes.py`, red on `main`, repaired | [record](002-phase-PF1.md); [PR 250](https://github.com/vasiloglou/gnd-public/pull/250), not merged |
| PF2 | the standing fitted-code review check on eight blind runs: 4 of 4 planted defects found, 0 false findings on controls | [record](003-phase-PF2.md), [grading](evidence/PF2/GRADING.md); [PR 253](https://github.com/vasiloglou/gnd-public/pull/253), not merged |

[Plan](notes/pins-and-review-check-plan.md). Merge order: PR 248 (plan), then
250, then 253.

After the close: OQ2 (inline count copies outside any name guard) fixed by
the [maintenance pass](../../maintenance/2026-11-23-inline-inventory-counts/README.md);
OQ4 (the frontmatter fence defect) fixed by
[PR 255](https://github.com/vasiloglou/gnd-public/pull/255), merged.
