<!-- Edited by review_tool.py sanitize: 5 absolute path(s) replaced with <repo> or <home>. The reviewer's words are otherwise unchanged; run.json holds the SHA-256 of the original. -->
All named files match their SHA-256 digests. The original round-1 reproducers are repaired, but broader cases still violate C1–C3.

1. **F1 — P1: Saved reviews still defeat the retained-file bound.**  
   [reading.py:846](<repo>/src/gnd/examples/literature/reading.py:846)

   The bound assumes receipts obey `response_bytes`, but saved receipts have no such check. Measuring `reviews.json` separately also misses its contents being embedded alongside coverage in `payload-4.json`.

   Reproduced with the caller fixture, `review=true`, `ReadingLimits(roster=7, input_bytes=1<<20, response_bytes=1024)`, and one correctly pinned saved receipt whose basis is `"b"*200000`. Return an accepted title for `a-opening` and empty answers elsewhere. The run completes with a **200,216-byte cap**, while **`payload-4.json` is 201,534 bytes**. C1 remains false.

2. **F2 — P1: Saved-review preflight still accepts fields whose invalidity is already knowable.**  
   [reading.py:347](<repo>/src/gnd/examples/literature/reading.py:347)

   Preflight checks only keys and string types. Empty bases and malformed excerpt digests pass, although both can be rejected from caller files alone.

   Reproduced using a saved `a-opening` receipt with correct remaining fields and either `basis=""` or `excerpt_sha256="not-a-digest"`. With `a-opening` accepted and other answers empty, the run makes **five producer calls** before raising `ExampleError("stale semantic reading review")`. No output is written, but C3 remains false.

3. **F3 — P2: Source decoding leaks `UnicodeDecodeError`.**  
   [reading.py:363](<repo>/src/gnd/examples/literature/reading.py:363), [reading.py:380](<repo>/src/gnd/examples/literature/reading.py:380)

   Replace the first source byte with `0xff` and update its roster digest. `run()` raises raw `UnicodeDecodeError`. An otherwise valid UTF-8 source beginning with `é`, paired with span `[0,1]`, leaks the same exception when the span splits the character.

   Both were reproduced before any producer call or output write. This predates the repair but disproves C2’s broader caller-file guarantee.

4. **F4 — P2: Missing roster fields leak `KeyError`.**  
   [reading.py:388](<repo>/src/gnd/examples/literature/reading.py:388)

   Validation treats a missing `superseded_by` as `None`, then indexes the absent key at line 402. Delete that field from `a-title` to reproduce raw `KeyError("superseded_by")`. Removing `selection` from the unavailable `b-appendix` similarly leaks `KeyError("selection")`.

   Both occur before calls or writes. These also predate the repair and remain C2 failures.

What I checked and found true:

- Long source versions and whitespace-padded saved response tables now fit their recorded caps.
- Surrogate and 5,000-digit integer answers, and surrogate reviewer answers, now raise `ExampleError`.
- The original list-valued saved review refuses before any producer call.
- Cross-source supersession preserves the required question’s originating source, with both unresolved and resolved successors.
- Packaged regeneration using recorded route outputs matched all **23 files in each configuration**, including the three expected manifest digests.
- The repair adds no regex or string split; its new span indexing uses validated two-element lists.
- Ruff passed for both changed Python files. The three frozen legacy test files are unchanged.

What I could not check:

- Fresh public-route workflows and complete test suites create files, which the brief forbids.
- Run-level probes therefore used in-memory file overrides, intercepted writes, and substituted extraction/public-route results. They exercised actual validation, loop, serialization, cap calculation, and reporting, but do not establish fresh verifier outcomes or ceiling timings.
- I read the entire LH2 draft; its proposed replay behavior remains unimplemented and untested here.

VERDICT: CHANGES_REQUESTED