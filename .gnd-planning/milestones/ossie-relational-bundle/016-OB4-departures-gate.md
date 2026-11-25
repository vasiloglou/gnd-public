# OB4 departures gate

**Owner ruling, 2026-11-25.** `auto=false`.

The owner was shown the two rules that the [OB4 record](015-phase-OB4.md)
put forward as OB4-Q1 and asked "Do you accept both added rules, or would you
like them explained first?" The owner answered:

> Accept both

| Item | Value |
|---|---|
| Record read at the gate | [015-phase-OB4.md](015-phase-OB4.md), sha256 `25ebff9e9bac3ca27b9d876b9e5b8ef69f1cd9ccf107f0756976dfab63e1166e` |
| Code | commit `527cf956` (the review repairs); recorded at `45bde294` |
| Review state | one Codex round; the repairs are not re-reviewed |

## Rulings

| Item | Ruling |
|---|---|
| OB4-Q1, K5 refined (IF1) | **Accepted.** For `binding:incompatible-keys`, two object types are compatible when they are related by subtyping or one is part of the other's identifier, at any depth. A column may therefore hold an entity and a component of that entity's identifier, as approved case V3 does. |
| OB4-Q1, the 8-level identifier limit (RR2) | **Accepted.** An identifier nested more than 8 entities deep is not followed. The entity is treated as one the ontology does not identify: its roles' column counts are not checked, and fact types through it are listed as `identification-differs`. |

## Still open

- **OB3-Q3:** the opt-in oracle lane (OB3 T11, OB4 T13) has not been requested or run.
- **OB4-Q2:** no second review round has been requested.
- **OB4-Q3:** the reporter has not been asked whether their schema uses surrogate keys (D10).
- The OB4 branch is not pushed and has no pull request.
