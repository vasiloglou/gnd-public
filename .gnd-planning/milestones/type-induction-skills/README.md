# type-induction-skills

Planning opened 2026-11-04 for the owner's rulings on CT-close-Q1 and
CT-close-Q2 from the
[composition-and-type-induction close](../composition-and-type-induction/007-milestone-close.md):
duplicate detection and multi-valued modelling for the `fact-type` discover
family move to skills; the CLI stays deterministic and supplies evidence.

**Status: plan r1 approved by the owner `(a1)` 2026-11-05, without plan
review ([gate record](001-plan-gate.md)). TS1 spec r1 is a draft awaiting its
own owner gate.** No code is written. `auto=false`. PR #86 merged
(`9f87fa0`); the branch is rebased onto main at `b733b2a` (TS-D1 met).

- [Plan gate record](001-plan-gate.md)
- [Canonical plan (r1, approved)](notes/type-induction-skills-plan.md)
- [TS1 spec (r1, draft, awaiting its gate)](notes/phase-TS1-spec.md)

Phases:
- TS1: type evidence (`--type-evidence`);
- TS2: judgement files and rendering, including many-to-many with a spanning
  uniqueness;
- TS3: packaged skill `gnd-judge-fact-types` (semantic duplicate judge);
- TS4: packaged skill `gnd-model-multivalued` (variant of the
  `rai-orm-from-schema` dialect conventions);
- TS5: documentation and a how-to;
- close.

Still open: TS-D0 (quote the owner's rulings) and the §10 proposals TS-D2 to
TS-D11, which the approval did not rule.

Next action: an explicit `process-phase TS1 type-induction-skills` selection,
which re-reads the TS1 spec's cited lines on main and stops at its owner gate.
