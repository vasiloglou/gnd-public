# type-induction-skills

Planning opened 2026-11-04 for the owner's rulings on CT-close-Q1 and
CT-close-Q2 from the
[composition-and-type-induction close](../composition-and-type-induction/007-milestone-close.md):
duplicate detection and multi-valued modelling for the `fact-type` discover
family move to skills; the CLI stays deterministic and supplies evidence.

**Status: plan r1 approved by the owner `(a1)` 2026-11-05, without plan
review ([gate record](001-plan-gate.md)). TS1 spec r2 approved by the owner
`(a1)` 2026-11-05 (prose instrument, D1–D7 as proposed). TS1 implemented
and recorded ([record](002-phase-TS1.md)).** `auto=false`. PR #86 merged
(`9f87fa0`); the branch is rebased onto main at `b733b2a` (TS-D1 met).

- [Plan gate record](001-plan-gate.md)
- [Canonical plan (r1, approved)](notes/type-induction-skills-plan.md)
- [TS1 spec (r2, approved)](notes/phase-TS1-spec.md)
- [TS1 record](002-phase-TS1.md)
- [TS2 spec (r1, draft, not approved)](notes/phase-TS2-spec.md)

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

TS1 spec r2 (2026-11-05) re-reads its lines on main `b733b2a`; the CT4-Q1
ruling (008) omits digests under `customer`, so groups are keyed `g<n>`
instead. TS1 shipped `--type-evidence`; its open questions (TS-Q3, the CT4
DateTime kind, plan repairs) are in the record. PR #88 merged as
`7b171bb2`. TS2 spec r1 drafted 2026-11-05 on the owner's relayed "go
ahead"; it records two refuted plan premises (P1, the judgement record
cannot sit on an induced constraint; P2, a `functional` shapes verdict can
never be accepted). Next action: the TS2 owner gate.
