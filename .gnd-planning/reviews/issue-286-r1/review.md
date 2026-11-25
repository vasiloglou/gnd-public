<!-- Edited by review_tool.py sanitize: 1 absolute path(s) replaced with <repo> or <home>. The reviewer's words are otherwise unchanged; run.json holds the SHA-256 of the original. -->
All SHA-256 hashes match the brief.

1. **F1 — Role-map detection also matches ordinary metadata.** At [src/gnd/terms.py:100](<repo>/src/gnd/terms.py:100), classification uses the holding key without checking its schema location. Description extras can legally contain those same keys.

   Reproduce in memory with:

   ```json
   {
     "version": 3,
     "object_types": [{
       "id": "label",
       "kind": "value",
       "primitive": "String",
       "description": {
         "summary": "A label",
         "extra": {
           "head": {"source": {"date": "2026-07-07"}}
         }
       }
     }],
     "fact_types": [],
     "constraints": []
   }
   ```

   This passes the schema. With the base walker, `semantic_validate` returns no issues. With the new walker, it returns `semantic:temporal-site` at `$.object_types[0].description.extra.head.source`. Replacing `head` with `bind` produces the same regression: previously accepted metadata is refused.

   The reverse also occurs. Replace the description with:

   ```json
   {
     "summary": "A label",
     "sample_population": [{"date": "2026-07-07"}]
   }
   ```

   The base walker yields the date map; the new walker omits it. `uses_temporal` changes from `true` to `false`, and its temporal validation error disappears.

   These executed counterexamples contain no actual role-keyed maps. They disprove C2’s node-preservation claim and C3’s unchanged traversal claim. Classification needs to distinguish schema locations from matching keys in arbitrary metadata.

2. **Checked and found true**

   - C1 passed 99 container/role/term combinations, including roles named `source`, `provenance`, `rejected_proposals`, `bind`, `head`, and `sample_population`. Containers were omitted while temporal values and nested operands remained visible.
   - Twenty-two sample-row models passed schema and semantic validation without being classified as temporal.
   - All five schema references to bindings or derivation heads use the handled keys; sample rows are the remaining role-map location.
   - Exact node order matched the base walker for 100 ordinary documents without role maps or misleading container keys.
   - Both release-note behaviors were reproduced, including previously accepted date literals under head roles `source` and `provenance`.
   - The tag-only preparation is complete: version fields agree, `TAGGED` includes `0.5.1`, paragraphs and install command match the procedure, and install pins remain `0.5.0`. `tools/release_text.py check` passed.
   - **34 read-only tests passed.** The changed production matchers examined were `_ROLE_MAPS`, `_ROLE_ROWS`, and `_NOT_SYNTAX`; the inputs above cover their successful and failing cases.

3. **Not checked**

   Tests requiring temporary files and an actual install from the tag were not run under the read-only restriction. The post-merge annotated tag and remote publication state were not verified. The finding was reproduced through schema validation, walker execution, and in-memory semantic validation.

VERDICT: CHANGES_REQUESTED