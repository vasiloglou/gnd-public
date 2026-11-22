<!-- Edited by review_tool.py sanitize: 3 absolute path(s) replaced with <repo> or <home>. The reviewer's words are otherwise unchanged; run.json holds the SHA-256 of the original. -->
All 25 supplied SHA-256 hashes match.

1. **F1 — Numeric duplicate rows silently pass (high).** [pyrel_rules.py:782](<repo>/src/gnd/export/pyrel_rules.py:782) detects repeated referenced tuples only when their anchors differ. The reader’s JSON-based duplicate guard accepts numerically identical rows written differently.

   Reproduce using `rp1/numeric-anchor.orm.json` with:

   ```json
   {
     "holds": [{"badge": 1, "country": "fr"}, {"badge": 1.0, "country": "fr"}],
     "visits": [{"badge": 1, "city": "paris"}]
   }
   ```

   GND returns **1**, witness `[["fr","paris"]]`. The generated reader accepts this population, but the lowered denial requires `badge_1 != badge_2`, producing no violation under set semantics; its report returns **0**, `eu OK`. I reproduced this with GND, the generated reader/report, and an in-memory IR evaluator. Reject duplicates using GND’s scalar identity before lowering them into sets.

2. **F2 — Disconnected-rule vacuity reads claims instead of computed facts (medium).** [pyrel_rules.py:1751](<repo>/src/gnd/export/pyrel_rules.py:1751) consults raw fact lists, ignoring the effective semiderived relations.

   Reproduce by making `disconnected.orm.json`’s `lives` and `capital` semiderived copies of separate seed relations. Supply empty seeds, retain the nonempty claims from `disconnected-facts.population.json`, and cover all four relations. GND accepts both derivation claims and returns **2**, with `eu` vacuous because both computed relations are empty. The generated reporting function returns **4**, listing `eu` as not checked. I reproduced both reporting outcomes in memory.

3. **F3 — LQP’s external-ID refusal exits 1 instead of 3 (medium).** The new rejection at [pyrel_rules.py:2674](<repo>/src/gnd/export/pyrel_rules.py:2674) raises `ValueError`, which LQP’s `main` leaves uncaught.

   Reproduce by running the assertions LQP program with `assertions-integer-id.population.json --connection unused`. It prints a traceback and exits **1**, before connection setup. DuckDB returns **3**, and GND returns **0**. I reproduced the LQP subprocess exit directly, without credentials.

**Checked and found true:**

- Fourteen focused tests passed.
- Assertions and lineage render as syntactically valid programs for both targets; assertions’ checked requirement comes from the shared IR.
- All ten supplied comparison cases match GND when evaluating the IR and generated reporting in memory.
- Ambiguous joins are refused by both exporters. External frequency remains refused.
- Single-fact anchors retain role identity; renamed and three-way join fixtures agree.
- Both Ossie bundles match their pinned digests.
- Twenty existing generated programs retain their baseline IR, constants, and query/build functions; changes are confined to reporting and type guards.

**Limits:** Native DuckDB execution and LQP compilation were not rerun because they create prohibited build files. Fixture-writing tests were likewise unavailable. The four prior review logs were hash-verified and partially inspected, including their conclusions; their complete nested transcripts were not reviewed because of size and output truncation. No files were changed.

VERDICT: CHANGES_REQUESTED