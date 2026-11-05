# type-induction-skills

Planning opened 2026-11-04 for the owner's rulings on CT-close-Q1 and
CT-close-Q2 from the
[composition-and-type-induction close](../composition-and-type-induction/007-milestone-close.md):
duplicate detection and multi-valued modelling for the `fact-type` discover
family move to skills; the CLI stays deterministic and supplies evidence.

**Status: plan r1 and TS1 spec r1 are drafts awaiting the owner's plan
gate.** No review has run, nothing is approved, no code is written.
`auto=false`. Inspection baseline `549ebb9`, the tip of
`claude/process-milestone-composition` (PR #86, open). TS1 waits for PR #86
to merge and then rebases onto it (TS-D1).

- [Canonical plan (r1, draft)](notes/type-induction-skills-plan.md)
- [TS1 spec (r1, draft, blocked on PR #86)](notes/phase-TS1-spec.md)

Phases:
- TS1: type evidence (`--type-evidence`);
- TS2: judgement files and rendering, including many-to-many with a spanning
  uniqueness;
- TS3: packaged skill `gnd-judge-fact-types` (semantic duplicate judge);
- TS4: packaged skill `gnd-model-multivalued` (variant of the
  `rai-orm-from-schema` dialect conventions);
- TS5: documentation and a how-to;
- close.

Pending at the plan gate: TS-D0 (quote the owner's rulings), TS-D1 to
TS-D11, and the plan review instrument (TS-D2 proposes four local readers).

Next action: the owner reads the plan and TS1 spec, rules §10, and selects a
review instrument for plan review.
