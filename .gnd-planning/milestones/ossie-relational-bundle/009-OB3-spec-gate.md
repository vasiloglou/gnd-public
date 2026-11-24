# OB3 spec gate

**Owner approval, 2026-11-24.** `auto=false`.

The owner was asked "How do you want to rule E1–E16?" and answered:

> All as proposed

| Item | Value |
|---|---|
| Approved spec | [OB3 spec r1](notes/phase-OB3-spec.md) |
| SHA-256 | `fa034f27c81394f4a69a7e230d008a3b7121f7ed72bd1df0d5192d0feb619484` |
| Under | plan r2 (`52d946a4…6e1d`), approved at the [plan gate](002-plan-gate.md) |
| Review state | not reviewed by a panel or a reviewer |

## Rulings

E1–E16 are ruled as the spec's §7 proposes them. The ones with effects
outside the renderer:

| ID | Ruling |
|---|---|
| E1 | Implementation starts on a branch cut from main after PRs #264, #266 and #270 merge. The spec and its corpus are prepared now. |
| E2 | Corpus first: seven cases with hand-derived expected files, approved before any renderer code. |
| E3 | (a) The Rmap requires every component binary of a composite identifier to be functional on the entity; this amends an OB2 rule. (b) A remaining difference from the ontology's `identify_by` is listed as `identification-differs`. |
| E4 | `RelationalSchema` gains the public field `roles`. |
| E5 | SQL identifiers in expressions are quoted and uppercased. |
| E8, E9 | A NULL yields no object and no link; unary flags map through `CASE WHEN`; absorbed subtypes get no object mapping (`subtype-absorbed`). E8 is a recorded residual. |
| E15 | OB2-Q1 goes to the close sweep. |
| E16 | No rename of identifiers over 128 characters; a recorded residual. |

## Effect

- **Corpus authoring may start.** Per §11, the stories and expected files
  are committed before any renderer code and gated by the owner.
- **No renderer code yet.** Per E1, implementation waits for the three PRs
  to merge.
