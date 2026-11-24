# OB2 D5 gate

**Owner ruling, 2026-11-24.** `auto=false`.

The owner was shown the variant measurement and asked "Which D5 variant
should OB3 use: HALPIN or ALTERNATE? Either answer would also accept IF5 and
RR1." After asking for the decision in business terms, the owner answered:

> go with Halpin

| Item | Value |
|---|---|
| Measurement read at the gate | [OB2-variant-measurement.md](notes/OB2-variant-measurement.md), sha256 `90d7d0d39feb384c427b59911245d16fadb2a6d2d7109f39e909179a270ab36d` |
| Code measured | `src/gnd/rmap.py` at commit `4b50f740`, sha256 `414a891733d63d1b5ef4040fc2552e0ab0f04110e89e0f1a79c70d752adbc67e` |
| Review state of that code | review round 1 found F1–F9, all repaired; the repaired bytes are not re-reviewed |

## Rulings

| Item | Ruling |
|---|---|
| D5 | **HALPIN.** OB3 maps with `RmapVariant.HALPIN`: subtypes are absorbed into their supertype's table, and a symmetric 1:1 goes toward the player whose id sorts first. `ALTERNATE` stays implemented and tested behind the internal switch, with no CLI surface. |
| IF5 | **Accepted.** Rules 1–5 give the entity a table. This refines S7 and A4. |
| RR1 | **Accepted.** The Rmap selects composite identification itself (confirmed, alethic, `preferred`, smallest sorted role references on a tie) and does not use `refscheme.reference_identity`. This departs from the spec's §6 reuse table. |

## What the measurement showed

- 62 of 66 models map identically under both variants.
- The 4 that differ are corpus cases 07, 08 and 15, and the census model
  `library_with_subtypes`: 1 table and 4 nullable columns under HALPIN,
  against 3 tables and 1 nullable column under ALTERNATE.
- Totals, HALPIN / ALTERNATE: 195 / 196 tables, 35 / 35 unmapped fact types,
  93 / 94 foreign keys, 58 / 55 nullable columns.

## Effect

- OB2 may be recorded.
- Changing the default variant later changes OB3's output for the models
  above, and returns to the owner.
