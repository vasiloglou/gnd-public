I'm requesting changes for one reason: a deeply nested YAML model makes the new COUNT commands hang. Everything else I tested matched what the author claims.

All 37 file hashes in the brief match, so I reviewed the right bytes. The affected test files pass (555 tests). My extra checks ran in a scratch folder under `/private/tmp`, and I changed nothing in the repository.

## Findings

**F1 (medium; the slow path is older than AC1). Nothing limits how deeply the model file can be nested before it is parsed.**
- **Where:** `src/gnd/witness/count_membership.py:98-103` and `:170-175`. `read_snapshot` checks only the file size, then `load_model_bytes` parses the YAML with no depth limit.
- **What you'd see:** a model file that is just `a: [[[ … ]]]` (deeply nested empty lists), run through `gnd witness-count`:

  | Nesting depth | File size | Time | Result |
  |---|---|---|---|
  | 1,000 | small | 3.7 s | exit 3 |
  | 4,000 | small | 13 s | exit 3 |
  | 16,000 | 32 KB | 44 s | exit 3 |
  | 50,000 | ~100 KB | over 120 s | I killed it |

  The size cap is 10 MiB, so a file far deeper than these is allowed.
- **Why it counts against AC1:** `gnd validate` slows down the same way, so the slow parse is in the existing loader. But the phase spec says nesting must be capped before parsing (its standing rules and test T6), and AC1 adds no such cap. The bounded-input claim (C3) holds for file sizes but not for nesting in the model and population.
- **Population:** a deeply nested JSON population is refused quickly with exit 3. A YAML population goes through the same parser as the model, so it is probably affected too; I did not run that case.
- **Fix:** add a depth check on the raw model and population bytes in `read_snapshot`, or record this explicitly as a carryover.

**F2 (style only, nothing observable).** Replay never imports the producer or the main evaluator, but both producer and replay call the same scan function, `members_from_snapshot`. A bug in that scan would show up on both sides and still certify. The only check against the main evaluator is one test covering the fixture's 2 groups. The spec allows this design.

## Checked and found true
- **C1 (replay checks everything):**
  - Replay checks in this order: certificate shape, the caller's request file, the model and population bytes, then all three digests plus the parsed request. A mismatch there exits 3 as `binding-stale`.
  - It then rebuilds the full roster and compares the whole certificate exactly; any difference exits 1. Count, status, order, contributions and the first supporting row are all covered.
  - Type checks stop `true`/`1`/`1.0` from passing as each other.
  - Members are told apart the same way the main evaluator does it. A test with two different Unicode encodings of "é" gave a count of 2 from both the certificate and `gnd check`.
- **C2 (empty groups and coverage):**
  - An empty covered group certifies zero.
  - Population rows with the wrong value type are rejected when the population loads.
  - Missing coverage exits 2, hidden (opaque) values exit 2, and models that include other files are refused.
  - Ordinary aggregate witnesses are still refused as before.
- **C3 (limits, except F1):** an oversized certificate or request exits 3. An oversized model or population exits 4. The row, cell, member and output-size limits all exit 4. The model and population loaders cap files at the same 10 MiB.
- **C4 (disclosure and output files):**
  - `--out` without `--raw` exits 3 and writes no file.
  - An existing `--out` file is refused and left byte-for-byte unchanged. New certificates are created with owner-only permissions (0600).
  - `--raw` is refused in customer disclosure mode and turned on automatically in internal mode.
  - The default output shows only the status.

## Not checked
- The installed-wheel path in test T8: I ran everything from the source tree.
- How long a deeply nested YAML population takes (inferred above, not run).

VERDICT: CHANGES_REQUESTED
