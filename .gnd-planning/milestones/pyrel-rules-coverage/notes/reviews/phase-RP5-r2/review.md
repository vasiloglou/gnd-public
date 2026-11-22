<!-- Edited by review_tool.py sanitize: 2 absolute path(s) replaced with <repo> or <home>. The reviewer's words are otherwise unchanged; run.json holds the SHA-256 of the original. -->
All 29 pinned hashes match. Round-one F1–F5 are fixed, but two documentation contradictions remain.

1. **F1 — Disconnected derivations are accepted.** [pyrel.md:188](<repo>/docs/runtimes/pyrel.md:188) says disconnected rule bodies are refused at export. That refusal applies to guarded antecedents; derivations can contain disconnected components feeding different head roles.

   **Reproduce:** In `tests/fixtures/pyrel-rules-derivations/orders.orm.json`, give `priority` order/customer roles and a derivation with body `line($o,$s,$q), gold($c)` and head `priority($o,$c)`. The model validates, and both targets successfully render:
   ```python
   m.where(line(o, s, q), gold(c)).define(priority_derived(o, c))
   ```
   I reproduced validation and rendering in memory. Narrow the documented refusal to disconnected guarded antecedents.

2. **F2 — LQP compilation does not return 4 for an unchecked must-rule.** [pyrel.md:159](<repo>/docs/runtimes/pyrel.md:159) says a must-rule listed as not checked gives exit 4. LQP `--compile` prints that listing but returns compilation status.

   **Reproduce:** Render `tests/fixtures/pyrel-rules-coverage/rp2/anchored-only.orm.json` as LQP and invoke `--compile`. It prints `time_step#0  not checked  (source anchor: …)`, then `0 requirements compiled for 0 rules (expected 0)`, and returns **0**. I reproduced this with the installed compiler, suppressing temporary-directory creation and blocking filesystem writes. Qualify exit 4 as an enforcement result and document compilation separately.

**Checked and found true:** C1 is satisfied. The Integer-to-Number refusal is documented and reproduced under both targets; the reason list is correctly scoped; DuckDB/LQP reporting differences and plan support are qualified; single-role exclusive-or exports successfully. Forty focused tests passed, all 24 literature model/target combinations rendered and parsed, and `git diff --check` passed.

**Limits:** Full native DuckDB agreement and live LQP enforcement were not rerun under the read-only restrictions. Historical logs were read programmatically, with conclusions and relevant passages inspected; their complete nested transcripts were not manually reviewed. No files were changed.

VERDICT: CHANGES_REQUESTED