# OB2 corpus gate

**Owner approval, 2026-11-24.** `auto=false`.

The owner was asked "Approve the corpus stories and amendment r1.1?" and
answered:

> Approve corpus and r1.1

| Item | Value |
|---|---|
| Spec, with amendment r1.1 (§12, A1–A14) | [phase-OB2-spec.md](notes/phase-OB2-spec.md), sha256 `7b38ddbd67fec77e091b578ba869be27a28cf9ebe249deb49c64fb784990b26b` |
| Corpus | [tests/fixtures/rmap](../../../tests/fixtures/rmap/README.md) at commit `fadd1d7b`: 25 cases with stories |
| Answer keys | 28 files in `tests/fixtures/rmap/answers/`, hand-derived. sha256 of their sorted concatenation: `7a4e6ee6116f0e327252abfc8a7d5d9fcb387d187d849154d50ae7acf7fb78e0` |

## Effect

- **Implementation may start.** Per the spec's §11, the harness lands red
  first, and each implementation commit names the cases it turns green.
- **The approved answers are fixed.** Changing an approved expected answer
  returns that answer to the owner, and the earlier answer is kept.
  Regression cases added during implementation get ids of their own.
- **D5** is still ruled at its own gate, after T5.
