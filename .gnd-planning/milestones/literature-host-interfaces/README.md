# Literature host interfaces

Plan r6, 2026-11-23, from [issue #216](https://github.com/vasiloglou/gnd-public/issues/216)
and [issue #215](https://github.com/vasiloglou/gnd-public/issues/215).
**Closed on 2026-11-23** ([close record](006-milestone-close.md)): all four
phases recorded, the full GND panel ran on the close, and the plan is r6
with close amendments A1 to A4. Pull requests #241 and #245 are open; merging
is the owner's. Plan approved by the owner on 2026-11-23
([plan-gate record](001-plan-gate.md), r6 sha256 `2dc760e5…1528`), with every
decision ruled. The full panel
reviewed r4 and r5; r6 answers the second round and is not itself reviewed.
Nothing is implemented, and no phase spec is approved.

| Phase | Deliverable | State |
|---|---|---|
| LH1 | A public producer protocol in the reading example; a caller's producer drives the six stages over a caller's root, with a budget per document, caps as parameters and optional steps recorded as skipped | done: [record](002-phase-LH1.md), [spec](notes/phase-LH1-spec.md) |
| LH2 | `replay()` of a live run from its own folder and the caller's root, with zero producer calls and its settings read from the run | done: [record](003-phase-LH2.md), [spec](notes/phase-LH2-spec.md) |
| LH3 | Admission over a caller-named assertion entity, identified by its own handle: every attached fact row kept, the facts of followed entities kept with them, include roots admitted | done: [record](004-phase-LH3.md), [spec](notes/phase-LH3-spec.md) |
| LH4 | Admission rules as data, the status `policy-refused`, and `max_targets` as an argument up to 1,024 | done: [record](005-phase-LH4.md), [spec](notes/phase-LH4-spec.md) |

[Plan](notes/literature-host-interfaces-plan.md). Third in the
[roadmap after 0.4.0](../../PROJECT.md#roadmap-after-040--planned-2026-11-21):
the reporter has working workarounds for both issues.

Three things the plan found that the outline did not say:

- The reading loop completes only when `gnd verify` and `gnd check` exit 0.
  A caller model with a constraint over a fact type not yet read exits 2, so
  the loop as written cannot finish on such a model (plan H23, decision D16).
- `gnd judgments check` itself stops at 1,024 targets per policy. A
  `MAX_TARGETS` parameter cannot admit more than that in one call (plan H13,
  decision D11).
- The checker does not join an objectified fact type to its entity (plan
  H14). The owner ruled that admission identifies an assertion by its own
  handle and refuses an entity that objectifies a fact type (D10).

Owner rulings so far: D6 as proposed (a budget and a stop reason per
document; no early end at required coverage); D9, follow entities outward
from an admitted assertion; D10, own handle only; D17, as proposed (the host
lists the entity types to follow, and nothing else is followed).

Plan review: the owner selected the full GND panel (D14) on 2026-11-23. It
ran over plan r4 (sha256 `6cadaa91…7cb6`): four of six reviewers succeeded,
all asking for revision, with two blocking concerns and twelve ranked fixes
([panel record](../../reviews/literature-host-interfaces-r4-panel/README.md)).
Plan r5 applies all twelve (plan §11). For the lint conflict the owner had
the dev-tools scripts fixed upstream (dev-tools PR 34, merged as `a29562a`),
and gnd-public is re-synced, so the whole-repository lint exits 0 again. The
LH1 spec is brought to r5. r5's own bytes are not reviewed; r5 is not
approved. Plan r5 adds one proposed decision, D18 (the admission row bound).

Second round: the owner asked for it on 2026-11-23. It ran over r5
(sha256 `c1a83237…2c9b`), and five of six reviewers succeeded:

- Gemini approved.
- Claude, Codex, Kimi and GLM asked for revision.
- Qwen timed out.

Three concerns reached agreement:

- LH1-C14's run at the response and roster ceilings cannot fit the retained-file ceiling.
- §3 starts LH1 at `4ad0d216`, before the lint re-sync.
- LH1-C10 misses two of the seven ceilings.

One blocking concern came from a single reviewer (Claude): under D4's
defaults, the retained-file bound refuses the packaged runs. Seven fixes are
ranked in the
[round-two record](../../reviews/literature-host-interfaces-r5-panel/README.md),
and plan r6 applies all seven (plan §11, tagged `(p2)`). The main change:
the retained-file bound applies only to new-format (`/2`) runs, whose default
cap is derived from their own bounds, so today's runs keep their path and
bytes. The LH1 spec is brought to r6. r6 adds no decision. This was the last
panel round the convergence rules allow.

Plan gate, 2026-11-23: the owner ruled the other thirteen decisions as
proposed ("All as proposed"), with D15 phase by phase (`auto=false`).

Next action, the owner's: commit the planning work (the plan's §3 start
commit is the merge that lands it with the dev-tools re-sync); then review and
gate the LH1 spec, which also rules LH1-D1 to LH1-D5; then select
`process-phase LH1 literature-host-interfaces`.

Execution: the owner delegated the milestone on 2026-11-23
(`/process-milestone literature-host-interfaces auto`), which supersedes D15's
phase-by-phase ruling. Branch `claude/literature-host-interfaces`.

**Deviation from plan §8, two pull requests.** Plan §8 delivers the milestone
as one pull request. It is delivered as two: the reading pair (LH1 and LH2),
then the admission pair (LH3 and LH4), so that literature-reading-reference's
LR3, which needs LH1 and LH2 on `main`, need not wait for LH4. The
milestone-coordinator session (local_0bf324b1) relayed the owner's answer to
"Accept splitting literature-host-interfaces into two PRs?" as "Accept the
split". This session did not receive those words from the owner directly; it
records the split as a delegated amendment (auto=true) under the owner's
milestone delegation, with the relayed words as their source. Merging each
pull request stays with the owner.
