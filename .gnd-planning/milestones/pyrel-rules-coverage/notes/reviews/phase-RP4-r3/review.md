<!-- Edited by review_tool.py sanitize: 1 absolute path(s) replaced with <repo> or <home>. The reviewer's words are otherwise unchanged; run.json holds the SHA-256 of the original. -->
All supplied SHA-256 hashes match.

1. **F1 — Valid `_any` fact names can still prevent export (medium).** [pyrel_rules.py:1078](<repo>/src/gnd/export/pyrel_rules.py:1078) treats a used relation named `<object_type>_any` as a generated universe, even when it is the source fact relation and no universe is needed.

   **Reproduce:** In `rp4/top.orm.json`, rename `has_grade` to `grade_any`, update `role_ref.fact_type`, and rename the population’s fact and coverage entries accordingly. Keep the allowed list. The model validates; GND returns **1**, **0**, and **2** for `deny`, `other-role`, and `empty-role`. Both exporters instead raise `ExportInputError`, claiming `grade_any` collides with a generated relation. The fact-scoped form fails identically. Reproduced with validated in-memory inputs.

2. **Checked and found true:**

   - **98 read-only tests passed**, including query-policy guards; focused Ruff checks passed.
   - The supplied `assessed_any` regression fixture renders and parses under both targets.
   - Twenty-eight variants covering `_any`, `_allowed`, `_reverse`, `_derived`, `_claimed`, `_closure`, and `_plays` render and parse.
   - Top-level, fact-scoped, range, and quantity fixtures render under both targets.
   - All seven RP4/quantity Ossie bundles match the pre-phase lowerer byte-for-byte; all four pinned digest sets match.

3. **Limits:** Full native agreement and live LQP enforcement were not rerun. Two initial tests required prohibited temporary files; the subsequent read-only selection passed. Historical logs were hash-verified and their conclusions inspected, but their complete nested transcripts were not fully reviewed. No files were changed.

VERDICT: CHANGES_REQUESTED