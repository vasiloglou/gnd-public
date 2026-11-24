# OB3 corpus gate

**Owner approval, 2026-11-24.** `auto=false`.

The owner was asked "Do you approve the corpus and amendment r1.1, or would
you rather I push the branch so you can read it on GitHub first?" and
answered:

> Approve corpus, r1.1

| Item | Value |
|---|---|
| Spec, with amendment r1.1 (§14, B1–B14) | [phase-OB3-spec.md](notes/phase-OB3-spec.md), sha256 `0b8c85f542a93b6a5db7a97d6895ea988011dd8894a5c1136b741b9014c7ec4c` |
| Corpus | [tests/fixtures/ossie_relational](../../../tests/fixtures/ossie_relational/README.md) at commit `68511ff8`: 7 cases with stories |
| Expected files | 21 files (7 semantic models, 7 mappings, 7 extension copies), hand-derived. sha256 of their concatenation, in the order semantic models, mappings, extensions, each sorted by case: `f4926423d727483e7028c5d5cf1d13b4092fcfaa372547b90af63601ef5477b2` |
| Review state | not reviewed; the upstream validator (opt-in oracle lane) was not run |

## Effect

- **The approved expected files are fixed.** Changing one returns it to the
  owner, and the earlier file is kept. Cases added during implementation get
  ids of their own.
- **Implementation waits (E1).** It starts on a branch cut from main after
  PRs #264, #266 and #270 merge. The harness then lands red first, and each
  implementation commit names the cases it turns green.
