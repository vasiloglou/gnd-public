<!-- Edited by review_tool.py sanitize: 2 absolute path(s) replaced with <repo> or <home>. The reviewer's words are otherwise unchanged; run.json holds the SHA-256 of the original. -->
All ten SHA-256 hashes match the brief. I found two correctness issues.

1. **F1 — Invalid rule values pass validation.**  
   [assertion_admission.py:135](<repo>/src/gnd/examples/literature/assertion_admission.py:135) normalizes values without checking that they are JSON scalars. The same issue affects reason values at line 141.

   Reproduce by copying `DEFAULT_RULES`, setting the first requirement’s `admissible` to `[{}]` or `[[]]`, and passing it to packaged `admit()`. Both reach judgments and `publish_directory_once`, although §6.2 requires refusal. Setting it to `[float("inf")]` reaches judgments, then raises a raw `ValueError` during digest serialization.

   Executed with publication intercepted in memory; no files were published.

2. **F2 — Optional reasons are required.**  
   [assertion_admission.py:128](<repo>/src/gnd/examples/literature/assertion_admission.py:128) requires every requirement to contain `reasons`. The spec’s obligation table explicitly makes reasons optional.

   Reproduce by deleting `reasons` from an otherwise valid requirement and calling `admit()`. I observed `Refusal("rules:invalid")` before judgments. A valid requirement therefore cannot use the declared fallback to its ID without supplying an empty list.

What I checked and found true:

- The packaged four output bytes, captured in memory using a real judgment report, match all four H18 digest prefixes.
- Explicit default rules preserve admitted bytes, reasons and order, with the required `policy-refused` status changes.
- Shaped evaluation handles mixed admissible/inadmissible rows, missing rows, first-failure ordering, declared reasons and ID fallbacks.
- Scalar matching distinguishes strings, numbers and booleans while equating `1` and `1.0`.
- Existing malformed-rule cases and invalid or lowered target caps refuse before judgments and publication.
- Changing shape, rules, target cap or row cap changes the corresponding `/2` field and record digest.
- The new regex passed token-boundary probes. No additional structured-text parsing issue was found by inspection.
- Direct projection of 65,536 rows with 64 requirements completed in 0.62 seconds. Focused Ruff checks passed.

I did not run the full pytest or tutorial lanes because they create files. Publication, temporary snapshot handling and full admission timing remain unchecked; write-producing seams were replaced with in-memory spies. No files were changed.

VERDICT: CHANGES_REQUESTED