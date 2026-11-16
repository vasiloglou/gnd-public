All 24 hashes in the brief match, so I reviewed the exact bytes it names. I changed nothing in the repository. My scratch files are in `/private/tmp/ld2-review-*`, and the one required plan file holds only a summary.

## 1. Findings

**F1: the time selector accepts inverse time (rates).** `src/gnd/anchors.py:47` and `:384`
- The compound-unit guard only catches the ASCII characters `/ ^ *` and `·`. Two common ways papers write a rate get through:
  - the Unicode minus: `fs−1`
  - superscripts: `fs⁻¹`
- **What you'd observe:** a document saying "The decay rate is 2 fs⁻¹." (or "2 fs−1.") with an anchor on `2 fs` passes `gnd check` (exit 0, anchored `pass`). A frequency is admitted as a time step of 2 fs. That breaks C1's "refuses wrong dimensions."
- **How I showed it:** I ran the public `gnd check` on the packaged fixture copy (`/private/tmp/ld2-review-scripts/probe.py`). The same text through `recognition_index` gives `{2: [(0, 4)]}`. `2 fs²` is correctly refused, because `²` counts as a word character.

**F2: part of a valid quantity is admitted as the whole amount.** `src/gnd/anchors.py:416`, the left boundary check that `time-fs` reuses
- The check only rejects a number preceded by a word character or `+`/`-`. So characters like `^`, `/`, `:` or an en dash can sit right before the number.
- **What you'd observe:** `gnd check` exits 0 with anchored `pass` in these cases:
  - "0.5x10^2 fs" (really 50 fs) anchored as `2 fs`, coefficient 2
  - "4/2 fs" anchored as `2 fs`
- With the index alone, "x 10^-3 ps" gives −3000 fs, and "1.5x10^3 fs" gives 3 fs.
- The `integer` and `decimal` selectors already had this weakness. For a time selector, though, it produces a wrong amount from a span that looks complete. That goes against C1's "malformed quantities" and the spec's "left token boundary." I reproduced it the same way as F1.

**F3: control T7 has no test.** `.gnd-planning/milestones/literature-depth/notes/phase-LD2-spec.md`, Verification table row T7
- The spec places "Fresh installed wheel executes the same public check/witness/replay route" in `tests/test_ld2_quantities.py`. Neither that file nor any test marked as a distribution test runs it, and I found no record of it being run.
- **What you'd observe:** nothing yet shows the packaged `quantity_fixture` works from an installed wheel. The example does sit under `src/gnd/`, so it should ship.

**F4 (style): the replay mutation test only checks that the exit code is not 0.** `tests/test_ld2_quantities.py:116`
- It doesn't check the reason or the scale/unit mutations, so a malformed-input failure (exit 3) would also pass it.
- In my runs, changing places to 4, the unit to `fs`, or the coefficient to 3 in the proof each gave exit 1 with `proof-invalid`. The behaviour is right; the test is just weak. The `unit` proof-cell mutation the spec mentions isn't tested.

## 2. What I checked and found true
- `tests/test_ld2_quantities.py`: 27 passed.
- 536 affected tests passed: RF6 query policy, index and registry, anchor sidecar v2 and other anchor suites, LD1 competency examples, schema sync, the LI0 witness-wire, public replay-admission and v71 witness-corpus tests, `test_replays`, and the LX1–LX4 and layering tests.
- `test_rf2_pre_move_pins.py::test_measure_output_bytes` fails, but it fails identically at base `cdb6b48b` (64283 vs 64085 bytes), so LD2 didn't cause it.
- **C1:**
  - `2 fs`, `0.002 ps` and `0.000002 ns` count as occurrences 0, 1 and 2 of one value, and their spans include the unit.
  - `2 eV`, `0.0001 ps`, `3 fs` and the bare `2` are refused.
  - The listed malformed tokens are refused, and so are no-break and thin spaces, `fsec`, `2-3 fs` and `2 fs/`.
  - The 18-character limit counts the sign, as the sidecar parser's `strict_json` does.
  - Converting units by shifting the decimal exponent is exact; `0.0020 ps` lands in the same bucket as 2.
- **C2:** witness and replay of `(2, 3, "ps")` exit 0, and every altered proof cell fails replay. Population mutations of places and unit fail the value constraints. The Float and Number controls check cleanly, then witness exits 2 with `fragment-unsupported`.
- **C3:**
  - The new selector is the only change to model admission (Integer only), and the String case fails `validate` at exit 3.
  - The capped prefix and the 40,000-repeat document finish inside the timeout.
  - The RF6 successor JSON is registered and the guard passes.
  - No other module lists the selector kinds (checked with grep), so no other contract is affected.

## 3. What I couldn't check
- I didn't build or install a wheel (F3).
- I didn't run the full historical, evidence and census lanes or a whole-tree Ruff pass.
- The replay checks the tuple against the population, not against the document. The tie between "0.002 ps" in the source and the tuple rests on the check plus the fixed `places = 3` and `ps` constraints. That only holds in this fixture because the ps scale is 3. I'm reporting that as stated by the README, not as a defect.

VERDICT: CHANGES_REQUESTED
