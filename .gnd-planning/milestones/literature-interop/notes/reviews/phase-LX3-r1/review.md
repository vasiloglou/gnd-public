All 32 SHA-256 values in the brief matched, so this review covers the exact bytes it names. I only read and ran things: I made no repository edits. My probes ran the repo's own test helpers in scratch directories under `/private/tmp/lx3probe`. Plan mode was on, and the tool for ending it isn't available in this session, so this answer is the result. A copy of the findings is in the plan file.

## 1. Findings

**F1 (medium, C2): an equality constraint lets a catalog depend on candidate rows without being refused.** `src/gnd/composition.py:230-234`
- **What's wrong:** `catalog_roster` only counts a constraint as candidate dependence when its type is `subset`. An `equality` constraint between a filled catalog relation and a candidate relation contains the same forbidden catalog→candidate direction, but nothing checks it.
- **What you'd see:** I put the test's catalog and candidate warehouse roles into an equality, using `setup()` from `tests/test_lx3_catalog_composition.py` and re-anchoring the vocabulary digest.
  - `gnd compose` exits 0 and writes a `gnd-composition/2` record.
  - With a malformed manifest, compose exits 3 with the manifest error (`manifest has missing or unexpected fields`). The catalog-dependency refusal never fires before it.
  - The subset form of the same model refuses with `reference catalog depends on candidate rows`.
- **Why it matters:** C2 says candidate dependence is refused in a set order. That only holds for the subset spelling. The docs (`docs/reference/composition.md`) and the spec only mention subset, so either the check or the stated scope needs widening.

**F2 (low, C2/C3): a correctly pinned but invalid catalog is reported as `binding-stale`.** `src/gnd/witness/service.py:316` and `:356`
- **What's wrong:** Both composed witness routes turn every `ReferenceInputError` into `binding-stale`, not just a changed catalog.
- **What you'd see:** I made the catalog assert a fact type it doesn't own and re-pinned its hash in the model.
  - Composed witness: exit 3, `binding-stale`.
  - Plain witness on the same inputs: exit 3, `input-invalid`.
  - Compose: `reference catalog could not be bound`.
- **Why it matters:** The spec and the witness contract say `binding-stale` means changed catalog bytes or a mismatched roster. Here the catalog is current but invalid, so the reason code is wrong. The exit band (3) is right.

**F3 (style, not reproduced): the ambiguous-match skip may hide candidate lineage.** `src/gnd/checking_service.py:214-216`
- **What's wrong:** When a verdict that isn't tied to one fact type has a row matching both a catalog row and a candidate row, the code skips the candidate's lineage too. The `(fact_type, index) in lineage` filter already keeps catalog rows out, so the skip only removes real candidate offenders.
- **Why it's only style:** I couldn't trigger it. Model-level subset and exclusion verdicts emit rows as lists, which this function skips anyway, so `lineage` was `[]` with and without a catalog row.

## 2. Checked and found true
- **Tests:** `tests/test_lx3_catalog_composition.py`, `test_witness_composition.py` and `test_composition.py` all pass (103 passed).
- **Reference-free bytes:** I re-ran the predecessor source (`git archive 6d2ecece`). The reference-free population and record digests match `legacy_*_sha256` exactly, so the claim of unchanged reference-free bytes holds.
- **Include-free catalog check:** CLI and API check both exit 0 with 4 passes. The spec's tests didn't cover this case for check.
- **Downgrade attempt:** stripping `references` and relabelling the record as `gnd-composition/1` gives exit 3 with a roster mismatch on check, and `binding-stale` on witness.
- **Roster ordering:** `_bind_at` sorts by reference id, so the roster compose writes always passes the reader's sorted-and-distinct check.
- **Row indexes:** `bind_population` keeps candidate row indexes when it combines candidate and catalog, so lineage positions stay correct.
- **Version fence in the replay kernel:**
  - It refuses a mismatch between catalog version and reference inputs.
  - Any v4 certificate must carry a composition digest and a non-empty roster.
  - A base node's `sources` must be empty for reference origins and non-empty for candidate origins (enforced by both `io.certificate_shape` and the schema).
  - Rooted reference-free certificates are still stamped v3, because `bind_declared_references` returns `None` when there are no references.
- **Composition schema:** its v2 `if/then/else` requires `references` for v2 and forbids it otherwise.

## 3. Not checked
- **Full verification gates:** I didn't run the structure suites, Ruff or the component gate.
- **F3 path:** I didn't search the checker for a verdict family that emits row dicts without an owning fact type, so F3 stays unconfirmed.
- **Other constraints:** I didn't probe whether external uniqueness or mandatory constraints spanning catalog and candidate relations should also be refused when the catalog is admitted.

VERDICT: CHANGES_REQUESTED
