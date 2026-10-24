# Induced knowledge

Planning opened, 2026-10-23, from [issue #34](https://github.com/vasiloglou/gnd-public/issues/34).
Draft plan r4 and IK1 spec r4: r3's owner-directed repairs plus the owner's 2026-10-24 rulings on D1–D6 and D14. r3 and r4 bytes carry no review opinion. No owner approval, no implementation.

- [Canonical plan (r4)](notes/induced-knowledge-plan.md)
- [IK1 draft spec (r4)](notes/phase-IK1-spec.md)
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

Request 2 (role-scoped value verbalization) is proposed in
[PR #35](https://github.com/vasiloglou/gnd-public/pull/35), which is open; IK1
is its fallback owner.

Pending:
- plan approval;
- then explicit selection of `process-phase IK1 induced-knowledge`, at whose
  gate base commit B is named.
