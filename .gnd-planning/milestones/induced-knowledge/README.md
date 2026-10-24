# Induced knowledge

Planning opened, 2026-10-23, from [issue #34](https://github.com/vasiloglou/gnd-public/issues/34).
Plan r4 and IK1 spec r4 **approved by the owner 2026-10-24** (bytes bound in the IK1 spec §12). r3 and r4 bytes carry no review opinion. IK1 base commit B = `1d6eee0`; IK1-D6 ruled exit 3 with a schema amendment.

- [Canonical plan (r4)](notes/induced-knowledge-plan.md)
- [IK1 draft spec (r4)](notes/phase-IK1-spec.md)
- [IK2 spec (r1)](notes/phase-IK2-spec.md): approved 2026-10-24, with its approval corpus
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
  focused gate 4003 passed; one local reviewer, R1 (blocking) fixed; IK2-Q1
  (archived induced proposals) and IK2-Q4 (confirm in place) await owner
  rulings.

Next: IK3 (measure over host-labelled populations) or IK4 (constraint
discovery), each needing its own spec and owner gate.
