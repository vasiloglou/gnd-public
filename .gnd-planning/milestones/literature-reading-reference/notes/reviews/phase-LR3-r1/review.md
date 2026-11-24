<!-- Edited by review_tool.py sanitize: 5 absolute path(s) replaced with <repo> or <home>. The reviewer's words are otherwise unchanged; run.json holds the SHA-256 of the original. -->
All 165 SHA-256 hashes match the brief.

1. **F1 — Wrong-predicate scoring includes unchanged predicates.** [reference_set.py:170](<repo>/src/gnd/examples/literature/reference_set.py:170)  
   The fallback compares value multisets without requiring a different fact type. In `vampnet-p2`, producing `method_builds_on_method` with `method="bidirectional transformer"` and `base_method="VampNet"` returns `wrong_predicate: 1`. The predicate is unchanged; its roles are reversed. Under the README’s rule, this should be an unmatched row with `wrong_predicate: 0`. Reproduced through the scorer with in-memory payloads.

2. **F2 — Prompt substitution corrupts legal model readings.** [record_lr3_reference_run.py:111](<repo>/tools/record_lr3_reference_run.py:111)  
   Sequential replacements also modify the vocabulary inserted earlier. Reproduce by changing the `work` object’s display name to `section` and its reading to `{section} introduces {Method}`. This model passes complete model validation. Producing for `vampnet-p1` sends the vocabulary reading `"vampnet-p1 introduces {Method}"`, changing its meaning. Reproduced with a captured prompt and no CLI call. Substitute template fields once while preserving inserted vocabulary.

3. **F3 — Malformed payloads escape as tracebacks.** [reference_set.py:154](<repo>/src/gnd/examples/literature/reference_set.py:154)  
   A payload containing `{"attempts":[{"section":"vampnet-p2","response":[1]}]}` raises `AttributeError`. An attempt with `section: []` raises `TypeError` during section lookup. Both escape `main()` instead of producing the promised controlled refusal. Reproduced through `main(["score", ...])` using injected file bytes. T8 omits both shapes; validate response and section types before using them.

4. **F4 — T2 does not enforce zero producer calls.** [test_lr3_reference_set.py:60](<repo>/tests/test_lr3_reference_set.py:60)  
   T2 checks only the evidence digest and read denominator. I injected a replay-evaluator mutation that supplies a counting `SavedProducer` over the retained responses. It invoked `produce()` **46 times**, preserved the evidence, and T2 still passed. This reproduction substituted the write-producing extraction/verification routes with retained outcomes. Assert zero reported producer calls and guard the producer invocation boundary.

5. **F5 — The README extrapolates beyond the measured run.** [reference_fixture/README.md:77](<repo>/src/gnd/examples/literature/reference_fixture/README.md:77)  
   “Expect lower figures” on real papers predicts performance on unmeasured corpora, despite the stated one-run limitation. The issue reply similarly suggests the reference run can determine how much of another corpus’s gap comes from prompts versus papers. This run supplies no such attribution. Inspection only: narrow these statements to the observed reference-set results.

What I checked and found true:

- The committed score is byte-identical to the scorer’s output: broad recall **9/31**, precision **9/10**; cumulative targeted recall **27/31**, targeted precision **18/23**, with two rows classified as wrong predicate.
- All generated overlay files match `build()`. The original corpus, answers and expected outputs have no diff against `origin/main`.
- The 31 labels have the stated per-type counts and a shared provenance/licence note.
- Manifest, retained-artifact and prompt hashes agree. The record identifies the producer, settings, budget and 46 calls.
- Removing gold anchors leaves the roster unchanged.
- In-memory changes to a retained response, source byte and section span each cause replay refusal before evaluation.
- T1, T3 and T5 pass unchanged. T9’s assertions pass with an in-memory CLI substitute.
- Matcher probes covered multi-digit passage IDs, Unicode byte offsets, decomposed accents, case folding, nonbreaking whitespace, literal braces in excerpts and the 500-character diagnostic slice. The legal vocabulary-placeholder collision is F2.

I could not run the complete unmodified replay or the full test file: they create temporary files, which the brief forbids. Read-only reconstruction reproduced the recorded evidence digest with extraction/verification routes substituted; this does not independently validate those routes. No producer calls, credential reads or repository writes were made.

VERDICT: CHANGES_REQUESTED