# Include-root routes

Plan r6, 2026-11-21, from [issue #217](https://github.com/vasiloglou/gnd-public/issues/217)
and item 1 of [issue #214](https://github.com/vasiloglou/gnd-public/issues/214).
Plan reviewed twice by the GND panel light and approved by delegated ruling
([plan gate](001-plan-gate.md)). **Closed locally** by delegated ruling after
a panel-light close review ([close record](005-milestone-close.md)); not merged. Run with
`process-milestone include-root-routes auto`.

| Phase | Deliverable | State |
|---|---|---|
| IR1 | `gnd judgments check` judges a version-5 include root directly | [record](002-phase-IR1.md): focused lane exit 0 |
| IR2 | `gnd flatten`: a recorded flattening route that accepts temporal models | [record](003-phase-IR2.md): focused lane exit 0 |
| IR3 | `gnd export pyrel` (all modes) accepts an include root through its recorded flattened model | [record](004-phase-IR3.md): focused lane exit 0 |

[Plan](notes/include-root-routes-plan.md). It is first in the
[roadmap after 0.4.0](../../PROJECT.md#roadmap-after-040--planned-2026-11-21):
#217 has no workaround today.

Next action, the owner's: review and merge the pull request; post the
[issue replies](notes/issue-replies.md); file the checker-scaling issue.
