# OB4 spec gate

**Owner approval, 2026-11-24.** `auto=false`.

The owner was asked "How do you want to rule G1–G18: all as proposed, or ask
the reporter first?" and answered:

> All as proposed

| Item | Value |
|---|---|
| Approved spec | [OB4 spec r1](notes/phase-OB4-spec.md) |
| SHA-256 | `f79b3979d9670b3599148e095d5903b5101386ff680087d8bfef9c47fdc67b8a` |
| Under | plan r2 (`52d946a4…6e1d`), approved at the [plan gate](002-plan-gate.md) |
| Review state | not reviewed by a panel or a reviewer |

## Rulings

G1–G18 are ruled as the spec's §7 proposes them. The ones with effects
outside the reader:

| ID | Ruling |
|---|---|
| G1 | The GND-owned format is defined now, from the issue's prose. The reporter is asked in parallel (D10, each outside step still confirmed with the owner first). |
| G2, G3, G4 | `references` sits on the column. `tables` and `columns` are objects keyed by name. A `table.column` string is resolved by lookup, and an ambiguous one is refused. |
| G7 | `extension_roles` are checked and listed, and produce no link mapping. |
| G11 | Caller names are written as given and quoted and uppercased in expressions; names equal after uppercasing are refused. |
| G13 | Three reasons are added for a binding run: `unbound`, `extension-role`, `not-in-binding`. |
| G16 | Implementation starts on a branch cut from main after PR #271 merges. |
| G18 | Corpus first. |

## Effect

- **Corpus authoring may start.** The valid cases, their stories and the
  refusal table are committed before any reader code and gated by the owner.
- **No reader code yet** (G16).
