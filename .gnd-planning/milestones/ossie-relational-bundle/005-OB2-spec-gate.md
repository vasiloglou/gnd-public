# OB2 spec gate

**Owner approval, 2026-11-24.** `auto=false`.

The owner was asked "How do you want to rule S1–S11?" and answered:

> All as proposed

| Item | Value |
|---|---|
| Approved spec | [OB2 spec r1](notes/phase-OB2-spec.md) |
| SHA-256 | `6bcca4ed157ec84b674fb2b2fb955ad470f5f17c33e3c72e8dac68625c2cb972` |
| Under | plan r2 (`52d946a4…6e1d`), approved at the [plan gate](002-plan-gate.md) |
| Review state | not reviewed by a panel or a reviewer |

## Rulings

S1–S11 are ruled as the spec's §7 proposes them:

| ID | Ruling |
|---|---|
| S1 | A fact type with no uniqueness takes the implied spanning uniqueness. |
| S2 | Only confirmed alethic uniqueness drives placement and keys. |
| S3 | Derived and computed fact types are unmapped. Stored and semiderived ones are placed. |
| S4 | The explicit reference fact type is carried as the key column. |
| S5 | Grouping happens on a single-role uniqueness only. A compound uniqueness gets its own table. This corrects plan §2.3 rule 2. |
| S6 | A unary is a Boolean column. |
| S7 | Tables go to entities with placements, independent entities, objectifications, and determining value types. |
| S8 | The objectification key is the fact type's effective uniqueness. |
| S9 | A unit-based reference is the column `<id>_value`, typed Number. |
| S10 | Column names follow §6.3. |
| S11 | **Corpus first.** |

## What happens next

1. **Corpus first, under S11.** The 25 cases, their stories and the split
   answer keys are authored and committed **before any `rmap.py` code**.
2. **Second gate.** The owner then gates on the stories. Implementation
   starts only after that gate.
3. **D5.** D5 is ruled later, at the internal gate after T5.

**Not selected:** no opt-in gate, no panel, and no oracle lane. Merge stays
the owner's decision.
