---
milestone: pyrel-applications
station: plan-amendment
skill: process-milestone
scope: plan-amendment
date: 2026-10-13
---
# Delegated approval (auto=true) of tutorial amendment A2

Owner request, 2026-10-13: after reviewing the shipped PA5 chapters, the owner
asked for junior-friendly tutorials that present GND as the way PyRel users get
from rules to checked agentic apps, with Snowflake teams in mind. In chat the
owner ruled O1 messaging-only Snowflake, O2 the scripted producer framed as the
agent slot, O3 a public query seam, and O4 approval under the existing
whole-milestone auto=true delegation with four local amendment readers.

Adopt A2 r3 (64777d5a3d4f75ac70e0238d39c5ea63a8d704b10fe72b5e814ed424a2d1fb6e). Effective plan becomes r1 + A1 + A2.
Original r1 and A1 are unchanged. This is a delegated ruling, not the owner's
personal reading of these bytes.

A2 inserts phase PA5R (PA5 → PA5R → PA6). It rewrites both native chapters and
adds an overview page. It fixes existing Snowflake overclaims (D0), adds a
public query seam inside the emitted PyRel program (D1, a delegated relocation
of O3 because `gnd` cannot be imported in the native interpreter), adds
checked-output tutorial blocks (D3) and a readability/claim gate (D7). PA5-C1..C6
must be re-satisfied in full. PA6 receives a new delegated spec gate after PA5R
and uses its one remaining repair-review slot.

## Convergence

- Round one (r1): four readings. Seven blocking findings across readings two
  (1, 2, 6), three (1, 2) and four (1). All reproduced against the cited lines.
- Repair round (r2): readers two, three and four. All seven blockers resolved.
  One new small blocker: README.md:16-18 and docs/index.md:259 were missing
  from D0 (reproduced). Non-blocking: D7 Snowflake-rule scope and wording;
  `--proposal` lane behavior; chapter 3 converting expense-project to the
  currency model (reproduced at docs/expense/03-evolution.md:164-185); the
  re-gated PA6 review budget.
- r3 applies exactly those repairs. Per the budget, no third round. r3's
  convergence edits have no independent reading. The PA5R phase review and the
  four close readers will see the resulting bytes.

Dispositions of non-blocking round-one findings: adopted in r2 except review
one finding 6's "layout-independent import", superseded by a base-model
project built with chapter 2's own steps; and review four finding 4, resolved by
using gnd evolve on a reader-local copy (no shipped sixth model). The PA5R spec
must confirm or refute that the evolve path supports the comparison-value change.

## Evidence

- notes/plan-amendment-a2.md (r3): 64777d5a3d4f75ac70e0238d39c5ea63a8d704b10fe72b5e814ed424a2d1fb6e
- notes/plan-amendment-a2-r2.md: 827fbedf138aac2dc531b6d7071e20dc8e8c1de296c2b1711590052474a797fe
- notes/plan-amendment-a2-r1.md: 555a0e76ed41364bb05c9db34897727c85a556640171de01e363b07b6589c3d1
- notes/plan-amendment-a2-review-one.md: 3c52ab9821ca871ebb2f32ff189407d5c3aa8e1dc1477ac0af96187335abacce
- notes/plan-amendment-a2-review-two.md: f5cca2d80985249cc270ccd89aa50abce847b0c6955b9a43150ede690ec8d3bf
- notes/plan-amendment-a2-review-three.md: 7b67683375d125e56268d5a962dec13e778fb2540593ca9778a60b4e7a580a2a
- notes/plan-amendment-a2-review-four.md: 129d58e33bf2b700194843e851e026a3a591a6f35f92b116c670711f8ca1747f
- notes/plan-amendment-a2-repair-review-two.md: 28639aa7a33d308b4510b21ce7d8328a49858b618d6287afa50d10ed2e590760
- notes/plan-amendment-a2-repair-review-three.md: ca1943db6156ffd44d849d4b39ecc52f19fff6258e3d5753fa2a129e4e0294ea
- notes/plan-amendment-a2-repair-review-four.md: dcbd9f22f0b07f6504b359f21313c7a406502e12967a37d84f8e4b3291318dfc

## Boundary and open questions

Review files are condensed by the orchestrator from each reader's
returned report; the reports' findings and cited lines are preserved.
No PA5R spec, implementation, PA6 completion, certificate, release or merge.
Uncommitted PA6 evidence under evidence/PA6/ is superseded but retained.
Next: process-phase PA5R pyrel-applications (auto=true) to write its spec.
