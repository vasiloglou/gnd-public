# OB3 departures gate

**Owner ruling, 2026-11-24.** `auto=false`.

The owner was shown the four departures of the [OB3 record](011-phase-OB3.md)
and asked "Do you accept all four departures, or would you like them
explained first?" The owner answered:

> Accept all four

| Item | Value |
|---|---|
| Record read at the gate | [011-phase-OB3.md](011-phase-OB3.md), sha256 `61c9ebed389d7b476ee9cfb58f02a2e8dd303300f158c55ac1519d1c1303c44a` |
| Code | commit `110f805a` (the review repairs); recorded at `c794e2f4` |
| Review state | one Codex round; the repairs are not re-reviewed |

## Rulings

| Item | Ruling |
|---|---|
| OB3-Q1 (IF1, review F5) | **Accepted.** A model that maps to no table writes the ontology's three files, prints a note on standard error and exits 0. Its fact types and constraints are then listed in no relational file. |
| OB3-Q2, `unmapped_links` (IF2) | **Accepted.** The mapping's `GND` extension carries the list when it is not empty. |
| OB3-Q2, the 32-role limit (RR2) | **Accepted.** A fact type with more than 32 roles keeps its table and is listed as `arity-over-limit`. |
| OB3-Q2, foreign-key names (RR3) | **Accepted.** Names are unique in the whole schema. This amends OB2's A11. |

## Still open

- **OB3-Q3:** the opt-in oracle lane (T11) has not been requested or run.
- **OB3-Q4:** no second review round has been requested.
- The OB3 branch is not pushed and has no pull request.
