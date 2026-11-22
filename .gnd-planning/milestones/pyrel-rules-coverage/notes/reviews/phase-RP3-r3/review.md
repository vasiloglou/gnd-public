<!-- Edited by review_tool.py sanitize: 2 absolute path(s) replaced with <repo> or <home>. The reviewer's words are otherwise unchanged; run.json holds the SHA-256 of the original. -->
All 49 supplied SHA-256 hashes match.

**F1 — Aggregate results escape the Float/Number head guard (high).** [pyrel_rules.py:1472](<repo>/src/gnd/export/pyrel_rules.py:1472) collects binary-context variables only from the body. An aggregate result assigned to a Float/Number head is omitted. The [head check at line 1404](<repo>/src/gnd/export/pyrel_rules.py:1404) also cannot bound a plain result variable.

Reproduce from `head-beyond.orm.json`:

- Give the source score role a new Integer object type; update its reading and remove `one_score`.
- Set the derived head’s score to `$total`, retaining its Number type.
- Add `aggregate: {"fn":"sum","of":"$s","over":["$s"],"as":"$total"}`.
- Add the comparison `$total < add(9007199254740992, 2)`.
- Supply source scores `9007199254740992` and `1` for run `"a"`, and claim derived score `9007199254740992`. Cover both fact types.

The validated model exports under both targets. **GND returns 1**, reporting missing score `9007199254740993` and extra score `9007199254740992`. The generated DuckDB queries report **OK and return 0** after rounding the aggregate result. Reproduced through an in-memory PyRel compiler/DuckDB adapter, for both Number and Float heads. Removing the comparison still produces the false pass; oversized comparison literals also escape refusal.

**Checked and found true:** The supplied round-two reproductions now receive named refusals under both targets. All seven refusal fixtures reject correctly. Integer arithmetic still renders under both targets. **43 selected tests passed**, including the existing derivation refusal tests.

**Limits:** Fixture-writing oracle suites and live LQP enforcement were not run under the read-only restriction. Historical logs were hash-verified and their conclusions inspected; their complete nested transcripts were not reviewed. No files were changed.

VERDICT: CHANGES_REQUESTED