# LI3 Claude Code diff review

One read-only Claude Code reviewer, Sonnet high effort, prompt on stdin. The phase base is 4735730d. An earlier transport attempt exited 0 but returned literal tool invocations without a review. It carried no review opinion. The technical retry returned the review below.

First prompt SHA-256: `d56789ee1b1a8a2b0d3073fdc4ffe00a33cc78ab04e26333b9b3fe78e83f143b`. Retry prompt SHA-256: `9a855e759972eff2aea0a7d0e28f888238d48cb7ab3c9df2e8cf2c3627691db8`. Output retained verbatim with host paths sanitized if present.

---

# LI3 phase-diff review (read-only, nothing executed)

This review is by reading only. I did not run any command or test, and I did not touch the heldout ref. I did read the LI2 reader (`src/gnd/composition_resolution.py`) and `diagnostics/cases.json`. Predicted outputs below are hand-traced from the code, not observed.

## Defects

### D1. "families" bypasses the generic-word exclusion
- **Anchor:** `name_diagnostics.py:30` (`GENERIC_TOKENS`) and `:80-83` (`_tokenize`).
- **Cause:** The plural stripper turns `families` into `familie`, and only `family`, `method` and `variant` are excluded. `methods` and `variants` are caught after stripping; `families` is not.
- **Reproduction:** Take four rows from distinct works with no introducing works, valued `AlphaFold families`, `Boltz families`, `OpenCap families` and `VampNet families`. Give them distinct sources and disjoint contexts.
- **Expected:** `diagnose` returns `[]`, as the amendment intends.
- **Predicted:** `familie` is shared by 4 works, so it qualifies at k=4, and all 6 pairs come out as `family` at 0.9.
- **Test gap:** `test_a_generic_family_word_alone_is_not_a_name` only covers the singular.
- **Related:** The same carrier-noun problem remains for `model`, `network`, `learning` and similar words. The amendment is reactive to this corpus, so the family precision figure applies to this corpus only.
- **Severity:** Medium.

### D2. The "acronym casing" predicate is too broad, and its branch is untested
- **Anchor:** `name_diagnostics.py:~105`, where `acronym` means a compact ASCII name with at least 2 uppercase letters. It is used at `:158`.
- **Cause:** CamelCase names count as acronyms.
- **Reproduction:** Two rows with `AlphaFold` and `Alphafold`, distinct sources, overlapping contexts and no introducing works.
- **Predicted:** The folded values are equal, the origins are disjoint, and the spellings differ with one acronym. That gives `homonym` at 1.0 for what is plainly a casing variant.
- **Alternative:** Requiring a run of two or more consecutive capitals would still accept `WhAM`, `WHAM` and `VAMPnet`. It would reject `AlphaFold`, `OpenCap` and `VampNet`.
- **Test gap:** In `cases.json` both required homonym pairs have disjoint contexts (`kinetics`/`music`, `bioacoustics`/`pose`). They pass through the `not context_overlap` arm. The case-variant arm at `:158` has no positive or negative test.
- **Severity:** Medium. The spec wording "acronym casing" is ambiguous.

### D3. The N1 synonym result depends on the N2 fixture
- **Where:** `cases.json`.
- **How:**
  - `flows-review` and `sbi-frontier` share the token `flow` with `flow-density` and `flow-motion`. That is 4 works, exactly k.
  - Family is suppressed only because the two Flow Matching rows carry `introducing_works`. `_families` (`:139-150`) marks a token as introduced if any row containing it has origins.
  - The required synonym therefore survives by coincidence.
- **Prediction:** In the T2 control, which clears the origins on the last two rows, `flow` becomes a family token. The pair `flows-review`/`sbi-frontier` would then flip to `family`, because family precedes synonym. The test only asserts the flow-matching pair, so it would not notice.
- **Design question:** One introduced occurrence suppresses the token corpus-wide. That follows the spec's "no introducing assertion for the token", but it is a coupling you should know about.
- **Severity:** Low to medium.

### D4. Test weaknesses

**T4 (`tests/test_li3_diagnostics.py`)**
- The `over-limit` case never asserts `reason`.
  - The fixture has 12 rows, so 12 × 50 = 600 does trip the occurrence cap first.
  - If the cap were removed, duplicate ids would still give exit 3, so the test would still pass.
  - 500 accepted and 501 refused are not tested.
- Cases the spec lists that are not covered:
  - unknown fields
  - bad coordinates (span order, source mismatch)
  - duplicate ids
  - per-source digest conflicts
  - NaN
  - deep nesting
  - invalid UTF-8
  - a file over 4 MiB
  - a missing path
  - a wrong schema string

**T5**
- `test_high_occurrence_count_is_bounded` uses disjoint contexts, so `context_overlap and _one_edit` (`:162`) short-circuits and `_one_edit` is never reached.
- The dense TRACE test aborts after about 8,001 pairs. Nothing walks all 124,750 pairs on a path that does the real classification work.
- The 8,000/8,001 boundary is untested.
- The candidate-limit refusal is tested only at `diagnose`, not through the CLI exit.

**T6**
- The assertions restate the implementation: `row["evidence"] | {"key": n}`.
- The decisions are never passed through `composition_resolution.parse_resolution` or `check_coverage`.
- "No file changes" is not tested. Only an in-memory `data == before` is checked.

**T3 (`diagnostic_measurement.py`)**
- The liveness control only uses all-wrong labels.
  - There is no wrong-kind label.
  - There is no case at exactly 1/5; `:59` uses `5 * wrong <= denominator`.
  - There is no case just over 1/5.
- `main` and `_labels` are untested.
- No test pins the SHA-256 of `measurement.json` or `labels.json` to the premeasurement record. A post-hoc edit would pass the suite.

### D5. Smaller issues
- **Output field:** The measurement output has no explicit fraction, only counts. The spec asks for "false positives and fraction".
- **Docstring:** `diagnose` says "ranked", but the output is sorted by ids.
- **Tokenization:**
  - Digit-only words of 4 or more characters, such as `2024`, count as tokens.
  - The stripper strips the `s` from `class` and `stress`. It does so consistently on both sides, so equality still holds.
- **Output encoding:** `print(json.dumps(..., ensure_ascii=False))` sits outside the `try`. A non-UTF-8 stdout with a non-ASCII spelling would raise a traceback instead of exit 3. This depends on the environment and I could not establish it.
- **Special files:** `read_capped` on a FIFO would block. That is an edge case.
- **Dedup versus labels:**
  - Dedup keeps the first highest-score occurrence pair per key pair.
  - Labels are keyed by occurrence pair, and a mismatch counts as a false discovery (`diagnostic_measurement.py:50`).
  - This only matters if the 300-row corpus has repeated keys, which I did not check.
- **Mixed-context mentions:** A key mentioned in several contexts can get `homonym` from one disjoint mention pair even when another pair shares a context. This follows the spec but is worth a sentence in the README.

## Claims confirmed from the code and fixtures

**N1**
- All four required pairs are produced from the original spellings, and each id pair is already in id order.
  - `VAMPnet`/`VampNet` and `WhAM`/`WHAM` give `homonym` via disjoint contexts with empty origins.
  - `normalizing flow`/`normalizing flows` gives `synonym` through context `inference` and one insertion. This holds only given D3.
  - `$PINN`/`PINNs` gives `family`. The token `pinn` appears in exactly 4 works (`apinn`, `pinn-failure-modes`, `pinn-transfer`, `pinn-workshop`), none introduced. `family` and `methods` are excluded.
- Precedence is homonym, then family, then synonym, in one function (`_classify`, `:155`).

**N2**
- `flow-density`/`flow-motion` has equal folded text and shared origin `flow-origin`, so homonym is suppressed.
  - `_one_edit` returns False for equal strings.
  - Its tokens are introduced, so family cannot fire.
  - Its contexts are disjoint, so synonym cannot fire.
  - The result is no candidate.
- The control with origins cleared does emit `homonym`.

**N3 sampling arithmetic**
- With emissions family 144, homonym 36 and synonym 36 (total 216, so no census):
  - Floors are 20 each, leaving 40 slots.
  - Largest remainder over capacities 124/16/16 gives 31/4/4, fractions 124/16/16, and one leftover slot to family.
  - The result is 52/24/24, which matches the reported 3/52, 1/24 and 2/24.
- Tie-breaking is by kind, and draws run in sorted kind order from one `Random(193)`.
- I traced that the allocation cannot divide by zero or over-allocate: capacity is positive whenever the total is at least 100, and a leftover slot never exceeds a stratum's room.
- All three strata have at least 20 observations, and 5·wrong ≤ denominator holds for each, so the status is pass.

**N4**
- The read is capped before decoding (`read_capped` reads cap+1 bytes).
- JSON parsing rejects duplicate keys, constants, deep nesting and oversized integers.
- `RecursionError` and `ValueError` are caught.
- The full input is validated before any classification.
- A refusal leaves `candidates` empty. It is assigned only after `diagnose` returns.
- Bool-as-int is rejected. `_shape` handles dict-keys set comparison correctly. The `[[]]` case is short-circuited, so there is no `TypeError`.
- The occurrence cap (500) is checked before per-row work.
- The caps are enforced: 8 list items, 64-character ids, 96-character values.
- The candidate cap (8,000) is enforced during dedup.
- Pair enumeration is at most 124,750 pairs, and the cost per pair is small.
- Output order is by ids, so it is deterministic.

**Unresolved decisions are structurally valid against LI2 (`composition_resolution.py:97-150`)**
- The field set is exactly right, and every producer, digest and coordinate field matches `exact_fields` and `_parse_coordinate`.
- Keys come from distinct sources with one object type.
- Evidence indices are exactly {0, 1}.
- Placeholders are two distinct strings of the same type as the key values.
- The per-key placeholder (a hash of source, type and spelling) is stable across candidates. That matters because `check_coverage` (`:336-340`) requires each key to take exactly its placeholder.
- The tool only reads and prints, with no write path.

## What cannot be established without running
- Whether the 81 focused tests and 679 structure tests pass, and whether the predicted outputs for D1 to D3 are right.
- That the committed `cases.json`, `measurement.json` and `labels.json` match the digests in the premeasurement record. No test pins them.
- Whether any candidate passes `ResolutionEvidence`, which checks coordinates against the model and sources. I read the parser, not the evidence-checking path.
- Whether the committed ledger's three-stratum numbers, and the 3, 1 and 2 false discoveries, are correct. They depend on `labels.json`, which I did not audit.
- Whether `measurement.json` contains repeated keys that make the dedup versus label-pair issue real.
- Wall-clock behaviour: the T5 timings, and the stdout-encoding and FIFO edge cases.

## Methodological caveats
- The ledger is declared `independent: false`, and `_labels` rejects `true`. The labeller is the corpus author, who also wrote the classifier and amended it after inspecting the corpus. The spec's "independently authored" wording overstates this.
- The pass is judged on the sample point estimate, with no interval. For example, 2 false discoveries in 24 is consistent with a true rate above 1/5. The result supports only "among sampled synthetic emissions", as the preregistration says.
