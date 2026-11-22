<!-- Edited by review_tool.py sanitize: 5 absolute path(s) replaced with <repo> or <home>. The reviewer's words are otherwise unchanged; run.json holds the SHA-256 of the original. -->
All 23 pinned SHA-256 hashes match. **C3 is not established.**

1. **F1 — Missing RP3 refusal message.** [test_rp5_literature_rules.py:64](<repo>/tests/test_rp5_literature_rules.py:64) omits the refusal for an Integer aggregate written into a Float/Number head. The page omits it too, so the completeness test passes despite incomplete documentation. Reproduced in memory: change `sum` to `min` in `rp3/sum-into-number.orm.json`; both targets refuse with `$total is an Integer value written into the Float or Number role 'score'; PyRel would round it beyond 2**53…`.

2. **F2 — The not-checked reason list is incomplete.** [pyrel.md:193](<repo>/docs/runtimes/pyrel.md:193) says rules print “one of these reasons,” but omits `no claim: <head> is not in covers`, `term:date-out-of-range`, `term:temporal-work-limit`, guarded-filter coverage, and nonfunctional dynamic-rule reasons. I executed generated reporting functions with the existing uncovered-derivation and nonfunctional-plan fixtures and reproduced two omitted messages; the other branches were verified in source.

3. **F3 — DuckDB reporting behavior is attributed to both targets.** [pyrel.md:143](<repo>/docs/runtimes/pyrel.md:143), also lines 153 and 166, needs target qualifications:
   - LQP does not apply DuckDB’s temporal not-checked classification; its generated header explicitly describes different behavior.
   - LQP lacks the missing-`covers` derivation-reporting branch.
   - LQP always lists disconnected uniqueness as not checked. With the existing empty disconnected fixture, generated reporting returns **4**, while DuckDB reports vacuous and returns **2**.

   The reporting difference was executed directly; temporal enforcement was assessed from source, without a live engine.

4. **F4 — The documented plan command fails for LQP.** [pyrel.md:220](<repo>/docs/runtimes/pyrel.md:220) presents plan execution without restricting it to DuckDB. Reproduced by rendering `pyrel-rules-plans/registrar.orm.json` as LQP and calling its generated `main` with `--pre STATE.json --steps PLAN.steps.json`: argparse exits **2** with unrecognized arguments, before any engine connection.

5. **F5 — Exclusive-or refusal is stated too broadly.** [pyrel.md:185](<repo>/docs/runtimes/pyrel.md:185) says exclusive-or over role sequences is refused. The restriction is to **multi-role** sequences. The existing `pyrel-rules-families/exclusive-or.orm.json` uses single-role sequences and successfully renders under both targets; I verified both.

**Checked and found true:** 38 existing read-only tests passed; focused Ruff and `git diff --check` passed. All 24 literature model/target export-handler cases returned 0 with publication suppressed, and their generated Python parsed. The population table contains exactly 56 cases. GND returned the specified exits: 54 cases returned 4 and two returned 0.

**Limits:** Native DuckDB agreement for those 56 cases and LQP compilation/enforcement were not rerun because their execution creates prohibited build files. Thus C2 remains independently unverified here. Historical logs were read programmatically in full, with conclusions and relevant passages inspected; complete nested transcripts were not manually reviewed. No files were changed.

VERDICT: CHANGES_REQUESTED