<!-- Edited by review_tool.py sanitize: 1 absolute path(s) replaced with <repo> or <home>. The reviewer's words are otherwise unchanged; run.json holds the SHA-256 of the original. -->
All SHA-256 hashes match the brief.

1. **F1 — C2 remains false: container detection also matches nested sample data.** At [src/gnd/terms.py:101](<repo>/src/gnd/terms.py:101), `head` and `bind` select role-map behavior regardless of schema location. Sample-row values permit arbitrary objects, so the description exclusion leaves another instance of the same confusion.

   Reproduce with this model:

   ```json
   {
     "version": 3,
     "object_types": [
       {"id": "label", "kind": "value", "primitive": "String"}
     ],
     "fact_types": [{
       "id": "labels",
       "reading": "{label}",
       "roles": [{"role_name": "label", "object_type": "label"}],
       "sample_population": [{
         "label": {"head": {"source": {"date": "2026-07-07"}}}
       }]
     }],
     "constraints": []
   }
   ```

   **Executed result:** layer 1 reports no issues. With the pre-issue walker (`102110b2`), semantic validation reports no issues and `uses_temporal` returns `false`. Current code returns `true` and reports `semantic:temporal-site` at `$.fact_types[0].sample_population[0].label.head.source`.

   Replacing `head` with `bind` reproduces the rejection. These nested maps are sample data, not derivation heads or atom bindings. A previously accepted model is consequently refused. Classification still needs to account for schema location.

2. **Checked and found true**

   - The description exclusion fixes the round-1 examples. Six in-memory metadata cases passed layer 1 and semantic validation without counting as temporal, including date functions and `primitive: Duration`.
   - C1’s intended safety property holds for the cases examined: the schema’s only explicitly declared `description` property is object-type metadata. Roles named `description` still expose their values through the role-map branch.
   - **81 container/role/term combinations passed**, including roles named `description`, `source`, `provenance`, `bind`, `head`, and `sample_population`.
   - C3’s release-note bullet accurately describes the tested description behavior.
   - Standing matcher check: tested `_NOT_SYNTAX`, `_ROLE_MAPS`, and `_ROLE_ROWS` with description extras, colliding role names, and nested sample objects. The nested sample inputs expose F1. No new regular expression, split, or slice was introduced.
   - **33 selected tests passed** with bytecode, pytest caching, and file-based output capture disabled.

3. **Could not check**

   Tests requiring temporary files, including the new end-to-end description tests, were not run under the read-only restriction. Their description cases were exercised through in-memory schema and semantic validation instead.

VERDICT: CHANGES_REQUESTED