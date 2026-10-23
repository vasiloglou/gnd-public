# Induced knowledge

Planning opened, 2026-10-23, from [issue #34](https://github.com/vasiloglou/gnd-public/issues/34).
Draft plan r3 and IK1 spec r3 (owner-directed repairs after review; r3 bytes carry no review opinion). No owner approval, no implementation.

- [Canonical plan (r3)](notes/induced-knowledge-plan.md)
- [IK1 draft spec (r3)](notes/phase-IK1-spec.md)
- [Plan review round 1 disposition](notes/plan-review-r1-disposition.md):
  three request-changes, one approve-with-fixes, 12 reproduced blocking findings.
- [Plan review round 2 (confirmation) disposition](notes/plan-review-r2-disposition.md):
  - three approve-with-fixes, one request-changes;
  - 10 of 12 round-1 blockers resolved;
  - self-inflicted ratio 0.95, so review stopped by the declared rule.

Review instrument: four local reviewer agents, owner-selected (D7, 2026-10-23).
The owner accepted the round-1 repairs and the proposed D8–D13 answers on
2026-10-23. D12's reading was owner-confirmed after round 2, and the owner directed repairs P-1..P-9 as r3 with no further review round.

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
- D1–D6;
- plan approval;
- then explicit selection of `process-phase IK1 induced-knowledge`, at whose
  gate base commit B is named.
