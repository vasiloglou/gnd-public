All 26 files match the SHA-256 values in the brief, so this review covers the exact bytes it names. I made no changes to the repository. The commands I ran wrote only to throwaway folders under `/private/tmp`, which I deleted afterwards, and pytest ran with `-p no:cacheprovider` so it left no cache.

## 1. Findings

**F1: The percent check's result is hard-coded, so it can never flip (C3).** `src/gnd/examples/literature/depth.py:256-257`
- **What's wrong:** `opens_ld2` for `percent-versus-points` is the constant `False`. It does not depend on `recognized_percentages`.
- **Spec gap:** D3 asks the probe to compare "an absolute difference between percentages with a relative change". The probe text contains no relative change, so that comparison never happens.
- **What I ran:** I fed the existing recognizer `"…absolute change of 5 percentage points and a relative change of 12.5%. Also 5% better."` It returned `['12.5%']` for 12.5 and `['5%']` for 5. It only sees the `%` sign and cannot tell an absolute change from a relative one.
- **Consequence:** If the recognizer counted "5 percentage points" as 5%, or the fixture used a relative change, the report would still say `opens_ld2: false`. The test at `tests/test_ld1_competency_examples.py:171-172` passes either way. The "no new percent recognizer" decision in the spec's implementation findings is asserted, not measured.

**F2: The exact-decimal probe measures that Float is unsupported, not decimal exactness (C3).** `depth_fixture/decimal.orm.json:11`, `decimal.targets.json:8`, `depth.py:240-245`
- **What's wrong:** `witness/kernel.py:42-63` refuses every `Float` value ("primitive outside fragment"). The decimal-relevant path is `Number`, which refuses with "only exact integral JSON numbers".
- **What I ran** (in a scratch folder):

  | Target | Exit | Result |
  |---|---|---|
  | Float 0.002 | 2 | `fragment-unsupported` |
  | Float 0.5 (exact in binary) | 2 | `fragment-unsupported` (identical) |
  | Integer 2 | 0 | `proved` |

- **Consequence:** The observation would look the same whether or not the route could handle exact decimals. The probe never tries `Number` with 0.002, which is the "native decimal numeric proof" D3 names. The conclusion to open LD2 may well be right, but this check does not establish it.

**F3: The dimension probe has no compatible-unit control (C3).** `depth.py:233-236, 254`
- **Spec gap:** D3 asks to compare the reported step with "a compatible time unit and incompatible energy unit". The text has only `2 fs` and `2 eV`. Nothing like `0.002 ps` is checked.
- **Construction issue:** `unit_phrases` is built by slicing three characters past each integer span (`end + 3`). The unit is attached by the example, not recognized.
- **Consequence:** The LD2 requirement ("validate a time-step anchor without accepting the same magnitude in energy units") also implies accepting an equivalent time value. Nothing measures whether the existing route accepts one.

**F4: Detecting a substituted citation depends only on the support-file digest (C2).** `depth.py:91-96`; test at `tests/test_ld1_competency_examples.py:85-86, 101`
- **What's wrong:** The `citation` mutation fails only because `SUPPORT_SHA` no longer matches. The spec says "Check reviewed data against a separately frozen case evidence inventory", and there is no such inventory: `cases.json` carries no source locators.
- **What I ran:** I rewrote `dynamics.rows[0].primary.url` to `https://example.invalid/fabricated` and the version to `fabricated v9`, then updated `SUPPORT_SHA` to the new digest. `build` succeeded and reported `supported https://example.invalid/fabricated fabricated v9`.
- **Consequence:** Anyone who updates the digest (the same step the `span` mutation test does) can swap a citation without any check failing. The span and document checks stay independent of the digest; the citation check does not.

**F5: The identity and relationship tests cannot fail (C2, partly style).** `tests/test_ld1_competency_examples.py:135-136, 59-60`
- `changed["subject"]` always comes from `cases.json` (`depth.py:287`) and never from the population, so `subject == old subject` is true by construction.
- The question rows never include labels, so `questions == old questions` is also always true.
- The spec's "retaining an occurrence reference" has no counterpart anywhere in the code or report.
- "Three relation predicates remain distinguishable" is checked only by those two relationship keys existing. `subject_influenced_by` appears only in the synthetic population. No test would notice a component reported as a specialization.

**F6: Missing-score comparison has no fixture control (low).** `depth_fixture/comparison.json`
- **What's wrong:** The spec says "Score cases include a control for each field recognized by comparison". `score` is one of those fields (`depth.py:188`), but no pair is missing a score.
- **What I ran:** `compare_scores` directly returns `('unknown', ['score'])`, so the code is correct; only the coverage is missing.

**F7: The decimal observation hard-codes `checked_value: "0.002"` (style/low).** `depth.py:245, 249`
- The value is a literal, not read from the population or the witness output. If the fixture value changes, the report still says 0.002.

## 2. What I checked and found true

- **Tests:** `uv run pytest -q -p no:cacheprovider tests/test_ld1_competency_examples.py` gives 20 passed.
- **C1, rooted extraction:** Each case root includes `vocabulary.orm.json` by digest, and extract → verify → check all run, ending `accepted`.
- **C1, unknowns:** The three scope limitations stay `unknown`. The required facts `conservation`, `validity` and `runtime` exist in the root models, so these questions could be answered with new reviewed evidence; they are not unknown by construction.
- **C1, reported equation:** `claim_kind: reported-equation` is kept separate from any judgement of scientific correctness.
- **Span and source checks:** A changed document, an altered span (after updating the digest) and a fabricated fact value each refuse. A fact for a scope-limitation question also refuses, because the reviewed facts there are `{}`.
- **Bound qualifiers:** Removing `assumptions` or `cost_model` yields `unknown` naming the missing fact.
- **Comparison order:** Known differences are checked before missing fields. `metric-changed-and-missing-conditions` → incompatible (`metric`); `missing-conditions` → unknown (`conditions`); each of the five context fields changed alone → incompatible.
- **Duplicate experiment fields** are refused before any GND call.
- **Label uniqueness:** `subject_has_one_label` is the only uniqueness constraint, and a duplicate label fails it through the public checker.
- **Input refusals:** Malformed, duplicate-key, NaN and oversized `cases.json` refuse before any GND call and before the output folder is created. An existing output folder is preserved (exit 3).
- **Witness output:** `witness --raw --out` prints JSON on stdout even on exit 0, so the code's exit-0/replay branch is reachable.
- **Algorithms source:** The complexity statement matches the arXiv 0909.4061 abstract as I know it: O(mn log k) flops for dense input.

## 3. What I could not check

- I did not run the installed-wheel rebuild (spec Q10). The test file has no wheel run, only a second in-tree `build`. The fixture should ship because it sits under `src/gnd/`, but I did not confirm that.
- I did not fetch the primary sources, so these are unverified: the PMC12243082 content (OPES-eABF, ff14SB, 2 fs, 300 K) and the Clawpack gallery details (extrapolation boundaries, van Leer limiter, 500 cells).
- I did not run whole-tree Ruff, the strict component gate, or the other three test files the spec selects.

VERDICT: CHANGES_REQUESTED
