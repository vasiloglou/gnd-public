All 49 SHA-256 hashes match the brief. Six issues reproduced.

1. **F1 — Narrowing trusts row positions without checking operation identities.** `src/gnd/discover/narrow.py:48`  
   Create two independent additions, `op-object` and `op-color`. Supply a normally validated report with matching proposal/before hashes, but rows `(0, op-color, refused-by-validation)` and `(1, op-object, admitted)`, including their corresponding references. Narrowing keeps `op-color` and drops `op-object`. It should refuse the mismatched row identities by name; checking length alone permits both keeping a refused operation and dropping an admitted one.

2. **F2 — Summary accepts incomplete outcomes and miscounts the round.** `src/gnd/evolve/summary.py:142`  
   Give a two-operation proposal a validated, correctly hash-bound report with `operation_outcomes=[]`. The summary returns `proposed.total=2`, `outcomes={}`. The command handler also returns exit **0** with this inconsistent summary. It should refuse incomplete coverage before counting.

3. **F3 — Inline HTML comments still satisfy the guidance guard.** `tests/support/markdown_sections.py:132`  
   Replace `New elements only, in the model's own element shapes;` in its table cell with `<!-- New elements only, in the model's own element shapes; -->`. `_reply_rule_problems` returns `[]`, although the required text is hidden. Prefixing the prose rule with `visible <!--` and closing its comment also passes. Comment handling recognizes only lines starting with `<!--`; table cells bypass it.

4. **F4 — Summary bindings do not identify every artifact read.** `src/gnd/evolve/summary.py:158`  
   Two validated reports differing only in `refusal.message` have different canonical SHA-256 hashes but produce identical bindings: only the proposal hash and report gate appear. A saved summary cannot identify which report was read. By inspection, `record_preview_sha256` similarly identifies the preview rather than the record; the record’s own identity is omitted.

5. **F5 — Host reasons are changed rather than reported verbatim.** `src/gnd/evolve/summary.py:50`  
   Read a round file whose host-drop reason is `"  host reason\n"`. Both the reader and CLI summary produce `"host reason"`. `NonEmptyString` strips whitespace, losing the host’s original text.

6. **F6 — Equivalent tab-separated closed headings break the guard.** `tests/support/markdown_sections.py:93`  
   Change the heading to `## The reply shape\t##`. `_reply_rule_problems` raises `AssertionError: no heading 'The reply shape' outside a fenced block`. This legal equivalent heading should pass; splitting only on spaces leaves the closing hashes attached.

What passed:

- Actual read-only service previews accepted narrowed versions of the validation-refusal and policy-refusal examples. Dependency closure dropped the refused fact type’s constraint and retained unassessed operations.
- Representative proposals without `narrowed_from` retained identical serialized bytes and digests against the baseline under schemas 1–3. Narrowed proposals round-tripped under all three.
- Oversize, NaN, depth-10,000, huge-integer, extra-key, duplicate-key, duplicate-reused and invalid-UTF-8 inputs raised `RoundFileError`; command probes returned 3 with empty stdout. Conflicting options returned 64.
- All 22 directly invoked tests requiring no arguments passed, including the GO2 repairs and timing checks; all 11 GO4 mutation controls passed.
- Matcher trials covered `_ROLE_STEP` with named `region_2` and positional roles; schema walking through nested sample/provenance objects; `_cells` with escaped pipes and omitted outer pipes; fence indentation and unequal closing lengths; whitespace reflow; and heading variants. The failures are recorded above.
- The revised shape-match guidance routes existing fact-type rows to `open_questions`.

I could not run apply/CAS, stale-preview publication, record-writing or the full fixture-based suite: those require filesystem writes prohibited by the brief. Hostile-file CLI probes used mocked byte streams; the incomplete-report CLI probe injected normally validated artifacts. No files were changed.

VERDICT: CHANGES_REQUESTED