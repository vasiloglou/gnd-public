<!-- Edited by review_tool.py sanitize: 1 absolute path(s) replaced with <repo> or <home>. The reviewer's words are otherwise unchanged; run.json holds the SHA-256 of the original. -->
All 39 supplied hashes match. Round-1 F1–F3 are fixed; one additional functional issue remains.

1. **F1 — Valid fact names ending in `_any` prevent export (medium).** [pyrel_rules.py:1272](<repo>/src/gnd/export/pyrel_rules.py:1272) treats every domain relation ending in `_any` as an object-type universe. RP4’s role-scoped domain can instead name an ordinary fact type.

   Reproduce from `rp4/top.orm.json`: rename `has_grade` to `assessed_any`, update its `role_ref`, and rename the population’s fact and coverage entries accordingly. GND accepts the model and returns **1** for `deny`, **0** for `other-role`, and **2** for `empty-role`. Both exporters instead raise **`ExportInputError: unknown object type 'assessed'`**. The fact-scoped form fails identically. Reproduced using validated in-memory inputs. Distinguish generated universes from source fact relations.

2. **Checked and found true:**

   - All three prior findings have passing regression checks.
   - **110 cumulative read-only tests passed**, including query-policy guards; focused Ruff checks passed.
   - All **14 supplied agreement cases** matched GND’s exits and witnesses through the installed PyRel compiler with in-memory DuckDB.
   - Across **158 models**, all **244 previously accepted programs** remained byte-identical.
   - All five RP4 model fixtures and the quantity fixture retained their complete pre-phase Ossie bundles.
   - Supported fixtures render and parse under both targets.

3. **Limits:** Full fixture-writing suites and live LQP enforcement were not run. One additional Ossie replay test was blocked by its temporary-directory requirement. Historical logs were hash-verified and their conclusions inspected; their complete nested transcripts were not fully reviewed. No files were changed.

VERDICT: CHANGES_REQUESTED