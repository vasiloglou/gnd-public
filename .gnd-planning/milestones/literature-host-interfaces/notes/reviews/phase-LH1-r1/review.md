<!-- Edited by review_tool.py sanitize: 6 absolute path(s) replaced with <repo> or <home>. The reviewer's words are otherwise unchanged; run.json holds the SHA-256 of the original. -->
All files named in the brief matched their SHA-256 digests. I found four functional issues.

1. **F1 — P1: The retained-file cap is not an upper bound.**  
   [reading.py:803](<repo>/src/gnd/examples/literature/reading.py:803) assumes 1 KiB of overhead per row, while roster strings have no corresponding bound.

   Reproduce with the caller fixture: set `survey-a`’s version to `"v" * 200000`, use `ReadingLimits(roster=7, input_bytes=1<<20, response_bytes=1024)`, and return empty responses. The run records a **131,072-byte cap**, but serializes `payload-3.json` to **401,064 bytes**.

   Saved tables also escape the estimate: padding a valid `responses.json` with 2 MiB of whitespace produces a **2,097,464-byte** retained table under a **1,184,771-byte** cap. These runs would retain files that cannot be read under their recorded cap. Both cases were reproduced in memory.

2. **F2 — P1: Serialization exceptions escape `run()`.**  
   [reading.py:457](<repo>/src/gnd/examples/literature/reading.py:457), also [reading.py:525](<repo>/src/gnd/examples/literature/reading.py:525).

   `_plain` permits values that the serializer subsequently rejects, without translating that failure into `ExampleError` or `ArtifactError`.

   Reproduce by returning an otherwise valid accepted response containing `{"title": chr(0xd800)}` or `{"paper": 10**5000}`. `run()` raises raw **`UnicodeEncodeError`** and **`ValueError`**, respectively. A reviewer returning `{"decision": "supported", "basis": chr(0xd800)}` also leaks `UnicodeEncodeError`. All three were reproduced through `run()` with no output writes.

3. **F3 — P1: Structurally invalid saved reviews are checked after producer calls.**  
   [reading.py:333](<repo>/src/gnd/examples/literature/reading.py:333), [reading.py:513](<repo>/src/gnd/examples/literature/reading.py:513).

   Loading `reviews.json` checks only that it decodes to an object. Receipt validation waits until both extraction passes finish.

   Reproduce with `review: true`, no live reviewer, `reviews.json` containing `{"a-opening":[]}`, and a producer returning valid accepted responses. The run makes **five producer calls** before refusing with `stale semantic reading review`. The malformed receipt could have been rejected during preflight. No output was written, but C2’s call-order guarantee fails.

4. **F4 — P2: Cross-source supersession assigns required questions to the wrong source.**  
   [reading.py:818](<repo>/src/gnd/examples/literature/reading.py:818).

   Required questions are reduced to terminal successors before `_stops` determines their source, losing the originating source.

   Reproduce with the caller fixture: make only `a-title` required, make it superseded by non-required `b-title`, and return empty responses. The report says `survey-a` has completed required coverage, while `survey-b` has exhausted available evidence—even though **`survey-b` has no required question**. This contradicts the specified per-source rule. Reproduced through `run()`.

What I checked and found true:

- Regenerating the packaged loop with recorded public-route outputs matched **all 23 files** in each of the three configurations, including all three P3 manifest digests.
- All 17 existing malformed-response examples and ten limit-refusal cases behaved as expected.
- The per-document budget omitted `a-methods` and continued to the smaller `a-results`.
- The unedited legacy repeated-inspection test passed.
- Roster validation and successor resolution handled 4,096 chained questions in approximately 0.008 seconds.
- The bounded process captured 16 MiB without truncation; a one-second timeout completed in approximately 1.013 seconds.
- Whole-repository `ruff check --no-cache` passed. The three frozen legacy test files are unchanged.

What I could not check:

- I did not run the complete workflow suites or fresh `extract`, `verify`, `check`, and `fidelity` workflows because they create files, which the brief forbids.
- Run-level probes replaced temporary storage and public-route execution with in-memory substitutes. They exercised the actual validation, loop, serialization, reporting, and output orchestration; they do not establish fresh verifier results or whole-run timing at every ceiling.

VERDICT: CHANGES_REQUESTED