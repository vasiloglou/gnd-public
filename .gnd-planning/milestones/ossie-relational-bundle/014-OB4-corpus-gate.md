# OB4 corpus gate

**Owner approval, 2026-11-24.** `auto=false`.

The owner was asked "Do you approve the corpus, schema and amendment r1.1,
or would you rather discuss surrogate keys first?" and answered:

> Approve corpus, r1.1

| Item | Value |
|---|---|
| Spec, with amendment r1.1 (§13, K1–K13) | [phase-OB4-spec.md](notes/phase-OB4-spec.md), sha256 `9de68ee2323e9a62d7f328612cf5738ae93ad086213bb46e55fdbeedc86f9b44` |
| Corpus | [tests/fixtures/physical_binding](../../../tests/fixtures/physical_binding/README.md) at commit `204c04d0` when approved, `ecb323e1` after the branch was rebased onto main (same bytes): 7 valid cases with stories, and 50 refusal rows |
| Corpus files | 29 files, hand-written. sha256 of their concatenation, in the order bindings, semantic models, mappings, extensions (each sorted by case), then `refusals.json`: `d8377d48dbb9ba301ccf4938573463a8accea3b4615d092081a40e00ad7054ed` |
| Format | [physical-binding.schema.json](../../../src/gnd/schema/physical-binding.schema.json), sha256 `5640b691db86a4a197a0832de83207ab5f78f15053f35be6d225e1263eac9066` |
| Review state | not reviewed |

## Effect

- **The approved files are fixed.** Changing a binding, an expected file, a
  refusal row or the schema returns it to the owner, and the earlier file is
  kept. Cases added during implementation get ids of their own.
- **K13 is accepted as a known limit.** A role held only through a surrogate
  key cannot be bound. D10 asks the reporter whether their schema uses them.
- **Implementation waits (G16).** It starts on a branch cut from main after
  PR #271 merges. The harness then lands red first, and each implementation
  commit names the cases it turns green.
- **G16's condition is met.** Asked "Should I merge #271 and start OB4, or run
  a second review of OB3 first?", the owner answered "Merge 271, start OB4".
  PR #271 merged as `165fa7c7`. Main had not moved since the OB3 branch was
  gated, so main's tree (`5718e427`) is the tree that passed OB3's gate. This
  also rules **OB3-Q4**: no second review round runs over the OB3 repairs;
  OB4's tests are the next instrument over that code. This branch was then
  rebased onto main.
