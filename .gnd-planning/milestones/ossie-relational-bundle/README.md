# ossie-relational-bundle

Planning opened 2026-11-24 from the owner's issue file (three Ossie export
issues, not yet filed on GitHub). **Status: plan r1, draft, not reviewed and
not approved.** Nothing is implemented.

- [Plan r1](notes/ossie-relational-bundle-plan.md)
- [OB1 spec r1 (draft)](notes/phase-OB1-spec.md)

| Phase | Deliverable | State |
|---|---|---|
| OB1 | `--max-output-bytes N` on export (and, per D3, `--max-input-bytes N` on import) | spec drafted; needs plan gate and D3 |
| OB2 | Halpin Rmap library `gnd.rmap` | blocked on D1, D5 |
| OB3 | Semantic model and mapping files, `--ontology-only` | blocked on OB2, D2, D4, D6 |
| OB4 | `--physical-binding FILE` | blocked on OB3, D7, D8 |
| OB5 | Docs and skill | after OB4 |

Next action: the owner rules D1–D10 (plan §10) and selects a plan-review
instrument (D9). Then the plan gate.
