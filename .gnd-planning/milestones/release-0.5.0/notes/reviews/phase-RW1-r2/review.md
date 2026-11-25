<!-- Edited by review_tool.py sanitize: 1 absolute path(s) replaced with <repo> or <home>. The reviewer's words are otherwise unchanged; run.json holds the SHA-256 of the original. -->
1. **F1 — The new refusal statement is too broad (P2).** [docs/release-notes.md:77](<repo>/docs/release-notes.md:77) says export refuses a model that “writes an `Integer` value into a `Float` or `Number` role.” Integer `count` results are explicitly allowed by `_refuse_inexact_head`.

   **Reproduction:** Call `gnd.export.pyrel_rules.render` on `tests/fixtures/pyrel-rules-coverage/rp3/count-into-number.orm.json` with each target, `duckdb` and `lqp`. Both successfully render programs. Changing its destination primitive to `Float` also succeeds with both current and `v0.4.0` exporter source.

   **Consequence:** The notes tell users that supported count exports will fail. Qualify the sentence to preserve the count exception.

2. **Checked and found true.**

   - All 11 pinned SHA-256 hashes match. The supplied patch matches `git diff cc8cdb65 HEAD` byte for byte.
   - The repaired block includes every inexact-number export refusal listed on the runtime page. Its specific historical claim about Integer `sum`, `min` and `max` results entering Float roles matches the retained evidence and source probes: six formerly successful exports now return exit 3.
   - Twenty additional numeric refusal checks passed across both targets.
   - C2 holds: the original four Ossie bullets remain unchanged and occur once each in the selected section.
   - Both changed tests pass. In-memory mutations removing either exit constant, corrupting exit numbers, or removing the byte bound cause the corresponding test to fail.
   - Standing matcher checks: `markdown_section` handled CRLF, fenced heading decoys, Unicode content, and sibling/parent boundaries; the bound’s whitespace normalization handled line breaks, tabs and Unicode spaces. The unchanged `exit_numbers` matcher caught incorrect numbers. No new matcher was introduced.

3. **Could not check.**

   Full pytest and engine execution were not run. Historical exports were exercised from `v0.4.0` source with current dependencies, rather than an isolated installed 0.4.0 package; the retained installed-package evidence was inspected. All probes remained read-only.

VERDICT: CHANGES_REQUESTED