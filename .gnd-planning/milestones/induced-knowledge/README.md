# Induced knowledge

Planning opened, 2026-10-23, from [issue #34](https://github.com/vasiloglou/gnd-public/issues/34).
Plan r4 and IK1 spec r4 **approved by the owner 2026-10-24** (bytes bound in the IK1 spec §12). r3 and r4 bytes carry no review opinion. IK1 base commit B = `1d6eee0`; IK1-D6 ruled exit 3 with a schema amendment.

- [Canonical plan (r4)](notes/induced-knowledge-plan.md)
- [IK1 draft spec (r4)](notes/phase-IK1-spec.md)
- [IK2 spec (r1)](notes/phase-IK2-spec.md): approved 2026-10-24, with its approval corpus
- [IK4 spec (r1)](notes/phase-IK4-spec.md): approved 2026-10-24, with its approval corpus
- [IK3 spec (r1)](notes/phase-IK3-spec.md): approved 2026-10-25, with its approval corpus
- [IK5 spec (r1)](notes/phase-IK5-spec.md): approved 2026-10-26, with its approval corpus
- [Plan review round 1 disposition](notes/plan-review-r1-disposition.md):
  three request-changes, one approve-with-fixes, 12 reproduced blocking findings.
- [Plan review round 2 (confirmation) disposition](notes/plan-review-r2-disposition.md):
  - three approve-with-fixes, one request-changes;
  - 10 of 12 round-1 blockers resolved;
  - self-inflicted ratio 0.95, so review stopped by the declared rule.

Review instrument: four local reviewer agents, owner-selected (D7, 2026-10-23).
The owner accepted the round-1 repairs and the proposed D8–D13 answers on
2026-10-23. D12's reading was owner-confirmed after round 2, and the owner directed repairs P-1..P-9 as r3 with no further review round.

Owner rulings, 2026-10-24 (recorded in r4):
- D1: no model version bump.
- D2: induced rules enter as proposed and advisory (deontic).
- D3: source kind `induced` only; a gold-answer origin goes in its `method`.
- D4: IK5 is a tool-neutral bridge with one adapter per learner; Popper first.
- D5: label refs by constraint `id`, position only for id-less constraints.
- D6: default discovery bounds, overridable per run, every skip reported.
- D14: object-type `description` is a JSON object with fixed core keys
  (`summary`, `row`, `source`, `notes`) plus extras carried unchanged.

Six phases:
- IK1 object-type descriptions → IK2 induced provenance and admission → IK4
  constraint discovery;
- IK3 measure over host-labelled populations → IK5 ILP bridge (which also needs
  IK2);
- IK6 end-to-end example and docs.

Close is separate.

Request 2 (role-scoped value verbalization) shipped in
[PR #35](https://github.com/vasiloglou/gnd-public/pull/35), merged as `1d6eee0`.

Records:
- [001 plan gate](001-plan-gate.md): plan r4 and IK1 spec r4 approved 2026-10-24.
- [002 phase IK1](002-phase-IK1.md): object-type descriptions shipped; focused
  gate 2309 passed; one local reviewer, no blocking findings; IK1-Q1 (extras
  nesting cap) awaits an owner ruling.
- [003 phase IK2](003-phase-IK2.md): induced provenance and admission shipped;
  focused gate 4003 passed; one local reviewer, R1 (blocking) fixed; the owner
  approved the review fixes (IK2-Q4 ruled) and ruled IK2-Q1 (no automatic
  checks on archived induced proposals; owner review is the control).
- [004 amendment IK1-Q1](004-amendment-IK1-Q1.md): description nesting capped at 64
  levels (owner ruling 2026-10-24); IK1-Q1 closed.
- IK2 repair (2026-10-24): IK2 left a runtime import cycle between
  `gnd.model._induction` and `_validation` that `tests/test_rf8_structure.py`
  refuses; that test was missing from IK2's gate. Repaired with a registration
  hook; gate in `evidence/IK2-repair/` (4366 passed, every `test_rf*.py`).

- [005 phase IK4](005-phase-IK4.md): `gnd discover` shipped, with indexed
  equality, exclusion and frequency checker paths (owner rulings); one local
  reviewer, seven blocking findings fixed; IK4-Q1..Q5 ruled 2026-10-25
  (Q1 implemented as exit 11; Q2 before IK6; Q3/Q4 at close).

- [006 phase IK3](006-phase-IK3.md): `gnd measure --labels` shipped (report
  schemas 4 and 5); focused gate 4360 passed; one local reviewer, no blocking
  findings, five hardening and completeness fixes; C-F7 ratified by the
  owner 2026-10-26.

- [007 phase IK5](007-phase-IK5.md): the ILP bridge shipped (`gnd export ilp`,
  `gnd import ilp-rules`, Popper adapter). Focused gate 4473 passed. One local
  reviewer: three blocking tracebacks and one hardening defect fixed, and all
  17 of its mutants killed by new tests. No learner ran (D13 (a)). IK5-Q1 (the
  bounds disagree) awaits an owner ruling.
- [008 amendment IK5-Q1](008-amendment-IK5-Q1.md): the export facts bound is
  500,000 (owner ruling 2026-10-26), so it and the 64 MiB file cap each refuse
  at their real values. IK5-Q1 closed.

- [009 phase IK4-Q2](009-phase-IK4-Q2.md): `gnd evolve` works on models with
  reference populations (missing reference 66, linked 74, digest mismatch 3,
  owner ruling 2026-10-26). Focused gate 3162 passed. One local reviewer, no
  blocking findings; three fixed with regressions. IK4-Q2-Q1 and Q2 are open.

- [010 phase IK6](010-phase-IK6.md): the refunds example, a business-level
  tutorial (checkpoint C1, approved at r3), its runnable commands page, goldens,
  the 65-file skill census and three skill edits. Installed candidate passed in
  both wheel origins. One local reviewer, no blocking findings; nine fixed.
  IK6-Q1 (a skill for the induction loop) and IK6-R1 are open.

Next: milestone close.
